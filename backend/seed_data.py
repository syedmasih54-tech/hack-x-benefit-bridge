import os
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from database import engine, SessionLocal, Base
from models import Citizen, Scheme, Application, ApplicationEvent, DocumentCheck, Grievance
from rules_engine import load_all_scheme_rules

SAMPLE_DOCS_DIR = Path(__file__).resolve().parent / "sample_documents"


def utc_now():
    return datetime.now(timezone.utc)


def generate_sample_document_images():
    """
    Synthesizes realistic sample document images using Pillow.
    Ensures clear printed text so both pytesseract and fallback OCR easily parse them.
    """
    try:
        SAMPLE_DOCS_DIR.mkdir(parents=True, exist_ok=True)

        # 1. Ration Card with Name: Sunita Devi
        ration_path = SAMPLE_DOCS_DIR / "ration_card_name_mismatch.jpg"
        img_rc = Image.new("RGB", (800, 480), color=(248, 246, 240))
        draw_rc = ImageDraw.Draw(img_rc)

        # Draw border
        draw_rc.rectangle([10, 10, 790, 470], outline=(180, 140, 60), width=4)
        draw_rc.rectangle([16, 16, 784, 80], fill=(225, 238, 225))

        # Text
        draw_rc.text((25, 25), "DEPARTMENT OF FOOD & CIVIL SUPPLIES (GOVT OF NCT DELHI)", fill=(20, 50, 20))
        draw_rc.text((25, 50), "NATIONAL FOOD SECURITY ACT (NFSA) - PRIORITY RATION CARD", fill=(60, 90, 60))

        rc_lines = [
            "Card Category: Below Poverty Line (BPL / PHH)",
            "Ration Card No: 0710-4492-9102",
            "Head of Family / Card Holder: Sunita Devi",
            "Date of Birth: 12/04/1959",
            "Gender: Female",
            "Address: Ward 14, Shakurpur, North West Delhi - 110034",
            "FPS Shop Licensee: Delhi Fair Price Shop #410",
            "Issue Date: 14/06/2016"
        ]
        y = 105
        for line in rc_lines:
            draw_rc.text((35, y), line, fill=(30, 30, 30))
            y += 42

        img_rc.save(ration_path, "JPEG", quality=92)
        print(f"[Seed] Created sample document: {ration_path}")

        # 2. Bank Passbook with Name: Sunitha Devi (Intentional 'th' mismatch)
        passbook_path = SAMPLE_DOCS_DIR / "bank_passbook.jpg"
        img_bp = Image.new("RGB", (800, 480), color=(245, 248, 255))
        draw_bp = ImageDraw.Draw(img_bp)

        # Draw border
        draw_bp.rectangle([10, 10, 790, 470], outline=(40, 70, 140), width=4)
        draw_bp.rectangle([16, 16, 784, 80], fill=(215, 230, 250))

        draw_bp.text((25, 25), "STATE BANK OF INDIA - SAVINGS BANK PASSBOOK", fill=(10, 30, 90))
        draw_bp.text((25, 50), "PRADHAN MANTRI JAN DHAN YOJANA (PMJDY / DBT ENABLED)", fill=(40, 60, 110))

        bp_lines = [
            "Account Holder Name: Sunitha Devi",
            "Account No: 30981240981",
            "CIF Number: 84910294812",
            "IFSC Code: SBIN0001234",
            "Branch: Chandni Chowk Main Branch, Delhi - 110006",
            "Date of Birth: 12/04/1959",
            "Mode of Operation: Single",
            "Account Status: Active (DBT Linked)"
        ]
        y = 105
        for line in bp_lines:
            draw_bp.text((35, y), line, fill=(20, 20, 20))
            y += 42

        img_bp.save(passbook_path, "JPEG", quality=92)
        print(f"[Seed] Created sample document: {passbook_path}")
    except Exception as e:
        print(f"[Seed] Notice: Read-only or restricted filesystem ({e}). Using existing document samples.")


def seed_database():
    """Initializes tables and seeds test schemes, citizens, applications, and documents."""
    # Ensure any missing provenance columns in schemes table are added for SQLite
    if engine.dialect.name == "sqlite":
        with engine.connect() as conn:
            cursor_res = conn.exec_driver_sql("PRAGMA table_info(schemes);").fetchall()
            existing_cols = {row[1] for row in cursor_res}
            cols_to_add = {
                "ministry_or_department": "VARCHAR(255) DEFAULT 'Government Authority'",
                "state_or_level": "VARCHAR(64) DEFAULT 'Central'",
                "official_guidelines_url": "VARCHAR(512)",
                "last_synced_at": "DATETIME",
                "is_live_source": "BOOLEAN DEFAULT 1",
                "official_source_name": "VARCHAR(255)",
                "source_gazette_or_guideline_url": "VARCHAR(512)",
                "citizen_charter_clause": "VARCHAR(255)",
                "last_verified_date": "VARCHAR(32)",
                "is_live_data_source": "BOOLEAN DEFAULT 1"
            }
            for col_name, col_type in cols_to_add.items():
                if col_name not in existing_cols:
                    conn.exec_driver_sql(f"ALTER TABLE schemes ADD COLUMN {col_name} {col_type};")
            conn.commit()

    db = SessionLocal()

    try:
        # 1. Seed Schemes from rules directory
        schemes_data = load_all_scheme_rules()
        for scheme_id, data in schemes_data.items():
            # URL Sanitization Guardrail: Normalize any legacy unresolvable nsap.nic.in to nsap.dord.gov.in
            portal_url = str(data["official_portal_url"]).replace("https://nsap.nic.in", "https://nsap.dord.gov.in")
            guideline_url = str(data.get("source_gazette_or_guideline_url", portal_url)).replace("https://nsap.nic.in", "https://nsap.dord.gov.in")
            ministry = data.get("ministry_or_department") or data.get("official_source_name", "Official Government Authority")
            state_lvl = data.get("state_or_level", "Central")
            is_live = bool(data.get("is_live_source", data.get("is_live_data_source", False)))

            existing = db.query(Scheme).filter(Scheme.scheme_id == scheme_id).first()
            if not existing:
                scheme = Scheme(
                    scheme_id=scheme_id,
                    title=data["title"],
                    ministry_or_department=ministry,
                    state_or_level=state_lvl,
                    rule_version=data["rule_version"],
                    processing_deadline_days=data["processing_deadline_days"],
                    official_portal_url=portal_url,
                    official_guidelines_url=guideline_url,
                    citizen_charter_clause=data.get("citizen_charter_clause", "Statutory Citizens Charter Guarantee"),
                    last_synced_at=utc_now(),
                    is_live_source=is_live,
                    # Backward compatibility fields
                    official_source_name=ministry,
                    source_gazette_or_guideline_url=guideline_url,
                    last_verified_date=data.get("last_verified_date"),
                    is_live_data_source=is_live
                )
                db.add(scheme)
                print(f"[Seed] Seeded scheme: {scheme_id} ({data['title']})")
            else:
                existing.title = data["title"]
                existing.ministry_or_department = ministry
                existing.state_or_level = state_lvl
                existing.rule_version = data["rule_version"]
                existing.processing_deadline_days = data["processing_deadline_days"]
                existing.official_portal_url = portal_url
                existing.official_guidelines_url = guideline_url
                existing.citizen_charter_clause = data.get("citizen_charter_clause", existing.citizen_charter_clause)
                existing.last_synced_at = utc_now()
                existing.is_live_source = is_live
                # Backward compatibility fields
                existing.official_source_name = ministry
                existing.source_gazette_or_guideline_url = guideline_url
                existing.last_verified_date = data.get("last_verified_date")
                existing.is_live_data_source = is_live

        db.commit()

        # Safely remove deprecated schemes no longer in rules/ directory
        deprecated = db.query(Scheme).filter(~Scheme.scheme_id.in_(list(schemes_data.keys()))).all()
        for dep in deprecated:
            fallback_scheme = "kisan_yojna" if "kisan_yojna" in schemes_data else list(schemes_data.keys())[0]
            db.query(Application).filter(Application.scheme_id == dep.scheme_id).update({"scheme_id": fallback_scheme})
            db.delete(dep)
            print(f"[Seed] Cleaned up deprecated scheme: {dep.scheme_id}")
        db.commit()

        # 2. Seed Demo Citizens
        # Citizen 1: Sunita Devi (65-year-old widow, no regular income)
        cit_sunita = db.query(Citizen).filter(Citizen.id == "CIT-SUNITA-65").first()
        if not cit_sunita:
            cit_sunita = Citizen(
                id="CIT-SUNITA-65",
                preferred_language="hi",
                consent_given=True,
                age=65,
                gender="female",
                marital_status="widow",
                annual_income=0.0,
                occupation="homemaker",
                created_at=utc_now() - timedelta(days=90)
            )
            db.add(cit_sunita)

        # Citizen 2: Rahul Sharma (20-year-old student)
        cit_rahul = db.query(Citizen).filter(Citizen.id == "CIT-RAHUL-20").first()
        if not cit_rahul:
            cit_rahul = Citizen(
                id="CIT-RAHUL-20",
                preferred_language="en",
                consent_given=True,
                age=20,
                gender="male",
                marital_status="unmarried",
                annual_income=120000.0,
                occupation="student",
                created_at=utc_now() - timedelta(days=20)
            )
            db.add(cit_rahul)
        db.commit()

        # 3. Seed Demo Applications
        # App 1: Active application within timeline (Widow Pension, submitted 5 days ago)
        app_active = db.query(Application).filter(Application.id == "APP-SUNITA-ACTIVE-01").first()
        if not app_active:
            sub_date = utc_now() - timedelta(days=5)
            exp_date = sub_date + timedelta(days=30)
            app_active = Application(
                id="APP-SUNITA-ACTIVE-01",
                citizen_id="CIT-SUNITA-65",
                scheme_id="widow_pension",
                status="under_review",
                submitted_at=sub_date,
                expected_resolution_date=exp_date
            )
            db.add(app_active)
            db.flush()

            db.add(ApplicationEvent(
                application_id=app_active.id,
                event_type="application_created",
                message="Application successfully submitted by citizen Sunita Devi via CSC center.",
                created_at=sub_date
            ))
            db.add(ApplicationEvent(
                application_id=app_active.id,
                event_type="under_review",
                message="Under review by Block Social Welfare Officer (Tehsil North West).",
                created_at=sub_date + timedelta(days=2)
            ))

        # App 2: OVERDUE application (Kisan Yojna, submitted 50 days ago, SLA 30 days -> 20 days overdue)
        app_overdue = db.query(Application).filter(Application.id == "APP-SUNITA-OVERDUE-02").first()
        if not app_overdue:
            sub_date_overdue = utc_now() - timedelta(days=50)
            exp_date_overdue = sub_date_overdue + timedelta(days=30)
            app_overdue = Application(
                id="APP-SUNITA-OVERDUE-02",
                citizen_id="CIT-SUNITA-65",
                scheme_id="kisan_yojna",
                status="under_review",
                submitted_at=sub_date_overdue,
                expected_resolution_date=exp_date_overdue
            )
            db.add(app_overdue)
            db.flush()

            db.add(ApplicationEvent(
                application_id=app_overdue.id,
                event_type="application_created",
                message="Application submitted for Pradhan Mantri Kisan Samman Nidhi (PM-KISAN).",
                created_at=sub_date_overdue
            ))
            db.add(ApplicationEvent(
                application_id=app_overdue.id,
                event_type="under_review",
                message="Forwarded to Agriculture Officer / Tehsil Revenue Inspector.",
                created_at=sub_date_overdue + timedelta(days=10)
            ))
        else:
            if app_overdue.scheme_id != "kisan_yojna":
                app_overdue.scheme_id = "kisan_yojna"

        # App 3: Partial/Pending application (Rahul - Scholarship missing documents)
        app_student = db.query(Application).filter(Application.id == "APP-RAHUL-SCHOLAR-03").first()
        if not app_student:
            sub_date_student = utc_now() - timedelta(days=12)
            exp_date_student = sub_date_student + timedelta(days=60)
            app_student = Application(
                id="APP-RAHUL-SCHOLAR-03",
                citizen_id="CIT-RAHUL-20",
                scheme_id="scholarship",
                status="pending_documents",
                submitted_at=sub_date_student,
                expected_resolution_date=exp_date_student
            )
            db.add(app_student)
            db.flush()

            db.add(ApplicationEvent(
                application_id=app_student.id,
                event_type="application_created",
                message="Scholarship registration initiated.",
                created_at=sub_date_student
            ))
            db.add(ApplicationEvent(
                application_id=app_student.id,
                event_type="pending_documents",
                message="Verification officer requested: Bonafide Student Certificate from College Dean.",
                created_at=sub_date_student + timedelta(days=4)
            ))

        # 4. Seed sample Document Check for Sunita Devi mismatch
        doc_check = db.query(DocumentCheck).filter(DocumentCheck.id == 1).first()
        if not doc_check:
            sample_fields = {
                "full_name_rc": "Sunita Devi",
                "full_name_passbook": "Sunitha Devi",
                "date_of_birth": "12/04/1959",
                "account_number": "30981240981",
                "ifsc_code": "SBIN0001234"
            }
            sample_warnings = [
                "Name spelling variance detected between Ration Card ('Sunita Devi') and Bank Passbook ('Sunitha Devi').",
                "Suggested action: Affidavit or passbook correction to avoid DBT credit rejection."
            ]
            doc_check = DocumentCheck(
                application_id="APP-SUNITA-ACTIVE-01",
                document_type="ration_card_vs_passbook",
                extracted_fields_json=json.dumps(sample_fields),
                mismatch_warnings_json=json.dumps(sample_warnings),
                created_at=utc_now() - timedelta(days=5)
            )
            db.add(doc_check)

        db.commit()
        print("[Seed] Successfully seeded citizens, schemes, applications, and document checks.")

    except Exception as e:
        db.rollback()
        print(f"[Seed] Error seeding database: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    generate_sample_document_images()
    seed_database()
