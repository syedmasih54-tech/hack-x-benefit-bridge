import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from pathlib import Path

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
    Request,
    Response,
    status,
)
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database import engine, Base, get_db
import config
from auth import ensure_citizen_owner, get_current_citizen, issue_access_token
import models
from models import Citizen, Scheme, Application, Grievance, DocumentCheck, VoiceInteractionLog, DigiLockerDocument, utc_now
from schemas import (
    CitizenCreate,
    CitizenResponse,
    SchemeSummary,
    SchemeDetail,
    EligibilityCheckRequest,
    EligibilityCheckResponse,
    DocumentScanResponse,
    DocumentCompareRequest,
    DocumentCompareResponse,
    ApplicationCreateRequest,
    ApplicationDetailResponse,
    CitizenFriendlyStatusResponse,
    MockStatusUpdateRequest,
    GrievanceDraftRequest,
    GrievanceDraftResponse,
    VoiceInteractionLogCreate,
    VoiceInteractionLogResponse,
    VoiceIntakeRequest,
    VoiceIntakeResponse,
    VoiceApplySchemeResponse,
    CitizenProfile,
    DigiLockerLoginResponse,
    DigiLockerAuthResponse,
    DigiLockerCallbackResponse,
    DigiLockerDocumentItem,
    LiveSyncResponse,
)
from sync_gov_data import execute_full_sync
import json
import uuid
from voice_service import (
    extract_intake_from_speech,
    sanitize_speech_transcript,
    transcribe_audio_bytes,
    extract_profile_with_llm,
    generate_voice_confirmation_message,
)
from rules_engine import (
    load_all_scheme_rules,
    get_scheme_by_id,
    evaluate_eligibility,
    simplify_explanation_with_llm,
)
from ocr_service import process_document_image
from mismatch_checker import compare_documents
from tracker_service import (
    create_application,
    get_citizen_friendly_status,
    update_mock_status,
)
from grievance_service import generate_grievance_draft, SUGGESTED_OFFICIAL_CHANNELS
from seed_data import seed_database, generate_sample_document_images
from digilocker_service import (
    get_authorization_url,
    generate_authorization_url,
    exchange_code_for_token,
    fetch_issued_documents,
    parse_document_payload,
    parse_doc_metadata,
    calculate_age_from_dob,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables. Demo records are only seeded in local development.
    Base.metadata.create_all(bind=engine)
    if not config.IS_SERVERLESS and os.getenv("SEED_DEMO_DATA", "true").lower() == "true":
        try:
            generate_sample_document_images()
            seed_database()
        except Exception:
            logging.exception("Local demo data initialization failed")
    yield
    # Shutdown logic if any


# Security Configuration for API Documentation
DOCS_USERNAME = os.getenv("DOCS_USERNAME", "")
DOCS_PASSWORD = os.getenv("DOCS_PASSWORD", "")
security = HTTPBasic()


def verify_docs_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """Secures FastAPI documentation endpoints (/docs, /redoc, /openapi.json) with HTTP Basic Authentication."""
    if not DOCS_USERNAME or not DOCS_PASSWORD:
        raise HTTPException(status_code=404, detail="API documentation is disabled.")
    correct_username = secrets.compare_digest(credentials.username, DOCS_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, DOCS_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password for API documentation.",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def verify_admin_access(request: Request) -> bool:
    """Guard state-changing maintenance/demo operations outside local demo mode."""
    if config.ENABLE_DEMO_INTEGRATIONS and not config.IS_SERVERLESS:
        return True
    expected = os.getenv("ADMIN_API_TOKEN", "")
    supplied = request.headers.get("authorization", "")
    if not expected or not supplied.startswith("Bearer ") or not secrets.compare_digest(supplied[7:], expected):
        raise HTTPException(status_code=401, detail="Admin authorization is required.")
    return True


app = FastAPI(
    title="BenefitBridge - Welfare Navigator Backend",
    description=(
        "Citizen-side welfare navigator for India. "
        "Assists citizens with eligibility discovery, pre-application document mismatch detection, "
        "transparent plain-language tracking, and statutory grievance escalation. "
        "Does NOT replace official government portals or make final determinations."
    ),
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan
)

# CORS Middleware for local frontend (e.g. Vite on 5173, Next.js on 3000) and Vercel deployments
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:8443,http://127.0.0.1:8443,http://localhost:3000,http://127.0.0.1:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- Global Error Shield Exception Handlers ----------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Catches malformed payloads before they crash FastAPI workers.
    Logs full stack trace to the terminal and returns structured JSON 400.
    """
    logging.warning("Request validation failed for %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Bad Request",
            "message": "Invalid request payload format.",
            "details": jsonable_encoder([
                {key: value for key, value in error.items() if key != "input"}
                for error in exc.errors()
            ]),
            "path": str(request.url.path),
        },
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Catches database operational/locking/schema errors safely.
    Logs full stack trace to terminal and returns structured JSON 500 without crashing worker.
    """
    logging.exception("Database error at %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "A database error occurred while processing the request.",
            "details": "Please try again later.",
            "path": str(request.url.path),
        },
    )


STATIC_DIR = Path(__file__).resolve().parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", summary="Citizen Welfare Navigator Web UI", tags=["Frontend"])
@app.get("/portal", summary="Citizen Welfare Navigator Web UI", tags=["Frontend"])
def serve_frontend():
    """Serves the citizen-side BenefitBridge web frontend directly."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "service": "BenefitBridge Welfare Navigator Backend",
        "health": "/health"
    }


# ---------------- Secured API Documentation Endpoints ----------------
@app.get("/docs", include_in_schema=False)
async def get_documentation(_username: str = Depends(verify_docs_credentials)):
    """Secured Swagger UI endpoint protected by HTTP Basic Authentication."""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{app.title} - Swagger UI (Secured)",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )


@app.get("/redoc", include_in_schema=False)
async def get_redoc_documentation(_username: str = Depends(verify_docs_credentials)):
    """Secured ReDoc endpoint protected by HTTP Basic Authentication."""
    return get_redoc_html(
        openapi_url="/openapi.json",
        title=f"{app.title} - ReDoc (Secured)",
        redoc_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )


@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint(_username: str = Depends(verify_docs_credentials)):
    """Secured OpenAPI Schema JSON endpoint protected by HTTP Basic Authentication."""
    return get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )


# ---------------- 1. Health Check ----------------
@app.get("/health", summary="Health check", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": "BenefitBridge Welfare Navigator Backend",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "disclaimer": "Preparatory and assistance layer for Indian citizen welfare schemes."
    }


# ---------------- Citizens (Helper Endpoints) ----------------
@app.post("/citizens", response_model=CitizenResponse, status_code=status.HTTP_201_CREATED, tags=["Citizens"])
def register_citizen(citizen_in: CitizenCreate, db: Session = Depends(get_db)):
    """Registers a citizen profile with explicit consent confirmation and demographic data."""
    if not citizen_in.consent_given:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Citizen consent is strictly required to initialize BenefitBridge navigation assistance."
        )
    citizen = Citizen(
        preferred_language=citizen_in.preferred_language,
        consent_given=citizen_in.consent_given,
        full_name=citizen_in.full_name,
        age=citizen_in.age,
        gender=citizen_in.gender,
        marital_status=citizen_in.marital_status,
        annual_income=citizen_in.annual_income,
        occupation=citizen_in.occupation,
        disability_status=citizen_in.disability_status or "none",
        direct_apply_payload_json=citizen_in.direct_apply_payload_json,
    )
    db.add(citizen)
    db.commit()
    db.refresh(citizen)
    response = CitizenResponse.model_validate(citizen)
    response.access_token = issue_access_token(citizen.id)
    return response


@app.get("/citizens/{citizen_id}", response_model=CitizenResponse, tags=["Citizens"])
def get_citizen(
    citizen_id: str,
    db: Session = Depends(get_db),
    current: Optional[Citizen] = Depends(get_current_citizen),
):
    ensure_citizen_owner(citizen_id, current)
    citizen = db.query(Citizen).filter(Citizen.id == citizen_id).first()
    if not citizen:
        raise HTTPException(status_code=404, detail=f"Citizen with ID '{citizen_id}' not found.")
    return citizen


# ---------------- 2 & 3. Schemes ----------------
@app.post("/schemes/sync-live-data", response_model=LiveSyncResponse, tags=["Schemes"], dependencies=[Depends(verify_admin_access)])
def sync_live_government_data(force_refresh: bool = False, db: Session = Depends(get_db)):
    """
    Triggers live ingestion pipeline across official repositories:
    1. Central Open Government Data Platform (data.gov.in) via OGD API
    2. Ministry of Rural Development NSAP Portal (https://nsap.dord.gov.in)
    3. Ministry of Electronics & IT / Unified Portal (https://www.myscheme.gov.in)
    4. National Scholarship Portal (https://scholarships.gov.in)
    5. Ministry of Agriculture & Farmers Welfare (https://pmkisan.gov.in)

    Maintains immutable SQLite application tracking history and exports rule JSONs.
    """
    res = execute_full_sync(force_refresh=force_refresh, db=db)
    return res


@app.get("/schemes", response_model=List[SchemeSummary], tags=["Schemes"])
def list_schemes(db: Session = Depends(get_db)):
    """Returns all loaded welfare schemes with statutory SLA and authentic government portal provenance."""
    rules_dict = load_all_scheme_rules()
    db_schemes = {s.scheme_id: s for s in db.query(Scheme).all()}

    all_scheme_ids = list(rules_dict.keys())
    for s_id in db_schemes.keys():
        if s_id not in all_scheme_ids:
            all_scheme_ids.append(s_id)

    summaries = []
    for sid in all_scheme_ids:
        rule_data = rules_dict.get(sid, {})
        db_record = db_schemes.get(sid)

        title = (db_record.title if db_record and db_record.title else None) or rule_data.get("title", sid)
        desc = rule_data.get("description", f"Welfare scheme: {title}")
        state_or_level = (getattr(db_record, "state_or_level", None) if db_record else None) or rule_data.get("state_or_level", "Central")
        deadline = (db_record.processing_deadline_days if db_record else None) or rule_data.get("processing_deadline_days", 30)
        portal_url = ((db_record.official_portal_url if db_record and db_record.official_portal_url else None) or rule_data.get("official_portal_url", "")).replace("https://nsap.nic.in", "https://nsap.dord.gov.in")
        rule_ver = (db_record.rule_version if db_record and db_record.rule_version else None) or rule_data.get("rule_version", "v1.0.0")

        # Provenance fields merged from DB and JSON rules engine
        ministry = (
            (getattr(db_record, "ministry_or_department", None) if db_record else None)
            or (getattr(db_record, "official_source_name", None) if db_record else None)
            or rule_data.get("ministry_or_department")
            or rule_data.get("official_source_name")
            or "Official Government Authority"
        )
        guidelines_url = (
            (getattr(db_record, "official_guidelines_url", None) if db_record else None)
            or (getattr(db_record, "source_gazette_or_guideline_url", None) if db_record else None)
            or rule_data.get("official_guidelines_url")
            or rule_data.get("source_gazette_or_guideline_url")
            or portal_url
        ).replace("https://nsap.nic.in", "https://nsap.dord.gov.in")
        charter_clause = (
            (getattr(db_record, "citizen_charter_clause", None) if db_record else None)
            or rule_data.get("citizen_charter_clause")
            or f"Statutory Citizen's Charter Guarantee ({deadline} Days SLA)"
        )
        last_synced = (
            (getattr(db_record, "last_synced_at", None) if db_record else None)
            or rule_data.get("last_synced_at")
            or utc_now()
        )
        last_verified = (
            (getattr(db_record, "last_verified_date", None) if db_record else None)
            or rule_data.get("last_verified_date")
        )
        is_live = (
            (getattr(db_record, "is_live_source", None) if db_record else None)
            or (getattr(db_record, "is_live_data_source", None) if db_record else None)
        )
        if is_live is None:
            is_live = rule_data.get("is_live_source", rule_data.get("is_live_data_source", False))

        summaries.append(
            SchemeSummary(
                scheme_id=sid,
                title=title,
                description=desc,
                state_or_level=state_or_level,
                processing_deadline_days=deadline,
                official_portal_url=portal_url,
                rule_version=rule_ver,
                ministry_or_department=ministry,
                official_guidelines_url=guidelines_url,
                citizen_charter_clause=charter_clause,
                last_synced_at=last_synced,
                is_live_source=bool(is_live),
                official_source_name=ministry,
                source_gazette_or_guideline_url=guidelines_url,
                last_verified_date=last_verified,
                is_live_data_source=bool(is_live)
            )
        )
    return summaries


@app.get("/schemes/{scheme_id}", response_model=SchemeDetail, tags=["Schemes"])
def get_scheme_detail(scheme_id: str, db: Session = Depends(get_db)):
    """Returns complete eligibility rules, mandatory documents, and authentic portal provenance for a specific scheme."""
    rule_data = get_scheme_by_id(scheme_id)
    db_record = db.query(Scheme).filter(Scheme.scheme_id == scheme_id).first()

    if not rule_data and not db_record:
        raise HTTPException(status_code=404, detail=f"Scheme '{scheme_id}' not found.")

    merged = dict(rule_data) if rule_data else {}
    if db_record:
        if db_record.title:
            merged["title"] = db_record.title
        if db_record.processing_deadline_days:
            merged["processing_deadline_days"] = db_record.processing_deadline_days
        if db_record.official_portal_url:
            merged["official_portal_url"] = db_record.official_portal_url
        if db_record.rule_version:
            merged["rule_version"] = db_record.rule_version
        if getattr(db_record, "ministry_or_department", None):
            merged["ministry_or_department"] = db_record.ministry_or_department
            merged["official_source_name"] = db_record.ministry_or_department
        elif getattr(db_record, "official_source_name", None):
            merged["ministry_or_department"] = db_record.official_source_name
            merged["official_source_name"] = db_record.official_source_name
        if getattr(db_record, "state_or_level", None):
            merged["state_or_level"] = db_record.state_or_level
        if getattr(db_record, "official_guidelines_url", None):
            merged["official_guidelines_url"] = db_record.official_guidelines_url
            merged["source_gazette_or_guideline_url"] = db_record.official_guidelines_url
        elif getattr(db_record, "source_gazette_or_guideline_url", None):
            merged["official_guidelines_url"] = db_record.source_gazette_or_guideline_url
            merged["source_gazette_or_guideline_url"] = db_record.source_gazette_or_guideline_url
        if getattr(db_record, "citizen_charter_clause", None):
            merged["citizen_charter_clause"] = db_record.citizen_charter_clause
        if getattr(db_record, "last_synced_at", None):
            merged["last_synced_at"] = db_record.last_synced_at
        if getattr(db_record, "last_verified_date", None):
            merged["last_verified_date"] = db_record.last_verified_date
        if getattr(db_record, "is_live_source", None) is not None:
            merged["is_live_source"] = db_record.is_live_source
            merged["is_live_data_source"] = db_record.is_live_source
        elif getattr(db_record, "is_live_data_source", None) is not None:
            merged["is_live_source"] = db_record.is_live_data_source
            merged["is_live_data_source"] = db_record.is_live_data_source

    ministry = merged.get("ministry_or_department") or merged.get("official_source_name") or "Official Government Authority"
    portal_url = str(merged.get("official_portal_url", "")).replace("https://nsap.nic.in", "https://nsap.dord.gov.in")
    guideline_url = str(merged.get("official_guidelines_url") or merged.get("source_gazette_or_guideline_url") or portal_url).replace("https://nsap.nic.in", "https://nsap.dord.gov.in")

    merged["ministry_or_department"] = ministry
    merged["official_source_name"] = ministry
    merged["official_portal_url"] = portal_url
    merged["official_guidelines_url"] = guideline_url
    merged["source_gazette_or_guideline_url"] = guideline_url
    merged.setdefault("state_or_level", "Central")
    merged.setdefault("citizen_charter_clause", f"Statutory Citizen's Charter Guarantee ({merged.get('processing_deadline_days', 30)} Days SLA)")
    merged.setdefault("last_synced_at", utc_now())
    merged.setdefault("last_verified_date", None)
    merged.setdefault("is_live_source", False)
    merged.setdefault("is_live_data_source", False)

    return SchemeDetail(**merged)


# ---------------- 4. Eligibility Rules Engine ----------------
@app.post("/eligibility/check", response_model=EligibilityCheckResponse, tags=["Eligibility Engine"])
def check_eligibility(
    payload: EligibilityCheckRequest,
    _current: Optional[Citizen] = Depends(get_current_citizen),
):
    """
    Evaluates citizen profile against welfare scheme rules deterministically.
    Classifies results into Eligible, Partially Eligible (e.g. missing documents), and Ineligible.
    Never uses an LLM for eligibility determination.
    """
    eligible, partially_eligible, ineligible = evaluate_eligibility(
        profile=payload.citizen_profile,
        target_scheme_id=payload.scheme_id
    )

    # Optional LLM conversational simplification of explanation text only
    if payload.simplify_with_llm:
        for res in eligible + partially_eligible + ineligible:
            res.simple_explanation = simplify_explanation_with_llm(res.simple_explanation)

    total = len(eligible) + len(partially_eligible) + len(ineligible)

    return EligibilityCheckResponse(
        eligible_schemes=eligible,
        partially_eligible_schemes=partially_eligible,
        ineligible_schemes=ineligible,
        total_schemes_evaluated=total
    )


# ---------------- 5 & 6. OCR Document Doctor ----------------
@app.post("/documents/scan", response_model=DocumentScanResponse, tags=["Document Doctor"])
async def scan_document(
    file: UploadFile = File(..., description="Document photo (JPEG, PNG, WebP)"),
    _current: Optional[Citizen] = Depends(get_current_citizen),
):
    """
    Scans a single citizen document image in-memory using pytesseract / OCR.
    Extracts key fields (name, DOB, account number, document type) and confidence indicators.
    Privacy first: Image bytes are processed in memory and discarded; never persisted on disk.
    Never extracts or stores Aadhaar numbers.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Uploaded file must be an image. Received MIME type: '{file.content_type}'."
        )

    try:
        content = await file.read(10 * 1024 * 1024 + 1)
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Image must be 10 MB or smaller.")
        scan_result = process_document_image(content, filename=file.filename)
        return scan_result
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The image could not be processed. Please try a clearer image."
        )


@app.post("/documents/compare", response_model=DocumentCompareResponse, tags=["Document Doctor"])
def compare_document_fields(
    payload: DocumentCompareRequest,
    _current: Optional[Citizen] = Depends(get_current_citizen),
):
    """
    Cross-checks extracted fields across two documents (e.g., Ration Card vs Bank Passbook).
    Identifies common Indian spelling variations (Sunita vs Sunitha), DOB format variances,
    and missing mandatory fields.
    Flags mismatches and provides actionable advice without rejecting the citizen.
    """
    result = compare_documents(
        doc1_fields=payload.document_1_fields,
        doc2_fields=payload.document_2_fields,
        doc1_type=payload.document_1_type,
        doc2_type=payload.document_2_type
    )
    return result


# ---------------- 7, 8, 9 & 10. Application Tracker ----------------
@app.post("/applications", response_model=ApplicationDetailResponse, status_code=status.HTTP_201_CREATED, tags=["Application Tracker"])
def create_new_application(
    payload: ApplicationCreateRequest,
    db: Session = Depends(get_db),
    current: Optional[Citizen] = Depends(get_current_citizen),
):
    """
    Creates a new tracked application for a selected scheme with calculated resolution deadline.
    """
    if not payload.consent_given:
        raise HTTPException(status_code=400, detail="Explicit consent is required before creating an application record.")
    ensure_citizen_owner(payload.citizen_id, current)
    try:
        app = create_application(db, payload)
        scheme_title = app.scheme.title if app.scheme else app.scheme_id
        deadline_days = app.scheme.processing_deadline_days if app.scheme else 30
        portal_url = app.scheme.official_portal_url if app.scheme else ""

        return ApplicationDetailResponse(
            id=app.id,
            citizen_id=app.citizen_id,
            scheme_id=app.scheme_id,
            scheme_title=scheme_title,
            status=app.status,
            submitted_at=app.submitted_at,
            expected_resolution_date=app.expected_resolution_date,
            processing_deadline_days=deadline_days,
            official_portal_url=portal_url,
            events=app.events
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        logging.exception("Application detail lookup failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not load application details.")


@app.get("/applications/{application_id}", response_model=ApplicationDetailResponse, tags=["Application Tracker"])
def get_application_detail(
    application_id: str,
    db: Session = Depends(get_db),
    current: Optional[Citizen] = Depends(get_current_citizen),
):
    """Fetches full details and chronological audit event history for an application."""
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail=f"Application '{application_id}' not found.")
    ensure_citizen_owner(app.citizen_id, current)

    scheme_title = app.scheme.title if app.scheme else app.scheme_id
    deadline_days = app.scheme.processing_deadline_days if app.scheme else 30
    portal_url = app.scheme.official_portal_url if app.scheme else ""

    return ApplicationDetailResponse(
        id=app.id,
        citizen_id=app.citizen_id,
        scheme_id=app.scheme_id,
        scheme_title=scheme_title,
        status=app.status,
        submitted_at=app.submitted_at,
        expected_resolution_date=app.expected_resolution_date,
        processing_deadline_days=deadline_days,
        official_portal_url=portal_url,
        events=app.events
    )


@app.get("/applications/{application_id}/status", response_model=CitizenFriendlyStatusResponse, tags=["Application Tracker"])
def get_application_citizen_status(
    application_id: str,
    db: Session = Depends(get_db),
    current: Optional[Citizen] = Depends(get_current_citizen),
):
    """
    Returns simplified, citizen-friendly status information, days remaining / days overdue,
    and whether the application is eligible for grievance escalation.
    """
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail=f"Application '{application_id}' not found.")
    ensure_citizen_owner(app.citizen_id, current)
    return get_citizen_friendly_status(app)


@app.post("/applications/{application_id}/mock-status-update", response_model=ApplicationDetailResponse, tags=["Application Tracker"])
def mock_department_status_update(
    application_id: str,
    payload: MockStatusUpdateRequest,
    db: Session = Depends(get_db),
    _admin: bool = Depends(verify_admin_access),
):
    """
    Mock department status-update endpoint for demo and live test purposes.
    Simulates officer actions: 'under_review', 'pending_documents', 'approved', 'rejected', etc.
    """
    try:
        app = update_mock_status(db, application_id, payload.status, payload.message)
        scheme_title = app.scheme.title if app.scheme else app.scheme_id
        deadline_days = app.scheme.processing_deadline_days if app.scheme else 30
        portal_url = app.scheme.official_portal_url if app.scheme else ""

        return ApplicationDetailResponse(
            id=app.id,
            citizen_id=app.citizen_id,
            scheme_id=app.scheme_id,
            scheme_title=scheme_title,
            status=app.status,
            submitted_at=app.submitted_at,
            expected_resolution_date=app.expected_resolution_date,
            processing_deadline_days=deadline_days,
            official_portal_url=portal_url,
            events=app.events
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))


# ---------------- 11 & 12. Grievance Escalator ----------------
@app.post("/grievances/draft", response_model=GrievanceDraftResponse, tags=["Grievance Escalator"])
def create_grievance_draft(
    payload: GrievanceDraftRequest,
    db: Session = Depends(get_db),
    current: Optional[Citizen] = Depends(get_current_citizen),
):
    """
    Generates a formal, respectful, and authoritative grievance draft
    when an application has crossed its expected resolution date.
    Does NOT auto-submit to government portals. Provides suggested submission portals.
    """
    try:
        application = db.query(Application).filter(Application.id == payload.application_id).first()
        if application is None:
            raise HTTPException(status_code=404, detail="Application not found.")
        ensure_citizen_owner(application.citizen_id, current)
        draft_response = generate_grievance_draft(
            db,
            application_id=payload.application_id,
            citizen_remarks=payload.citizen_remarks
        )
        return draft_response
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        logging.exception("Grievance draft creation failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create grievance draft.")


@app.get("/grievances/{grievance_id}", tags=["Grievance Escalator"])
def get_grievance(
    grievance_id: int,
    db: Session = Depends(get_db),
    current: Optional[Citizen] = Depends(get_current_citizen),
):
    """Retrieves a previously generated grievance draft record."""
    grievance = db.query(Grievance).filter(Grievance.id == grievance_id).first()
    if not grievance:
        raise HTTPException(status_code=404, detail=f"Grievance with ID {grievance_id} not found.")
    if grievance.application:
        ensure_citizen_owner(grievance.application.citizen_id, current)

    app = grievance.application
    scheme_title = app.scheme.title if app and app.scheme else "Welfare Scheme"
    sub_date = app.submitted_at.strftime("%d-%b-%Y") if app and app.submitted_at else "N/A"
    res_date = app.expected_resolution_date.strftime("%d-%b-%Y") if app and app.expected_resolution_date else "N/A"

    return {
        "grievance_id": grievance.id,
        "application_id": grievance.application_id,
        "citizen_reference_id": app.citizen_id if app else "N/A",
        "scheme_name": scheme_title,
        "submission_date": sub_date,
        "expected_resolution_date": res_date,
        "current_status": app.status if app else "unknown",
        "draft_text": grievance.draft_text,
        "created_at": grievance.created_at,
        "status": grievance.status,
        "suggested_official_channels": SUGGESTED_OFFICIAL_CHANNELS
    }


# ---------------- 13. Voice Intake Assistant ----------------
@app.post("/voice/intake", response_model=VoiceIntakeResponse, tags=["Voice Intake"])
def process_voice_intake(
    payload: VoiceIntakeRequest,
    db: Session = Depends(get_db),
    current: Optional[Citizen] = Depends(get_current_citizen),
):
    """
    Bilingual speech intake assistant for Indian welfare applications.
    Extracts demographic, economic, and scheme intent data from speech-to-text transcripts.
    Strictly redacts 12-digit national identity numbers (Aadhaar).
    Persists audit log in voice_interaction_logs.
    """
    ensure_citizen_owner(payload.citizen_id, current)
    if not payload.consent_given:
        raise HTTPException(status_code=400, detail="Explicit consent is required before saving voice intake data.")
    extraction = extract_intake_from_speech(payload.raw_transcript)
    safe_transcript = sanitize_speech_transcript(payload.raw_transcript)
    audio_lang = payload.audio_language or f"{extraction['language_detected']}-IN"

    log_entry = VoiceInteractionLog(
        citizen_id=payload.citizen_id,
        audio_language=audio_lang,
        raw_transcript=safe_transcript,
        extracted_entities_json=json.dumps(extraction),
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)

    return VoiceIntakeResponse(
        language_detected=extraction["language_detected"],
        intended_scheme_id=extraction["intended_scheme_id"],
        profile=extraction["profile"],
        log_id=log_entry.id,
    )


@app.get("/voice/logs", response_model=List[VoiceInteractionLogResponse], tags=["Voice Intake"])
def list_voice_logs(
    citizen_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current: Optional[Citizen] = Depends(get_current_citizen),
):
    """Retrieves stored voice interaction logs with privacy sanitization."""
    if current is not None:
        citizen_id = current.id
    q = db.query(VoiceInteractionLog)
    if citizen_id:
        q = q.filter(VoiceInteractionLog.citizen_id == citizen_id)
    return q.order_by(VoiceInteractionLog.created_at.desc()).limit(50).all()


@app.post("/voice/apply-scheme", response_model=VoiceApplySchemeResponse, tags=["Voice Intake"])
async def voice_apply_scheme(
    audio_file: UploadFile = File(..., description="Multipart audio file recording"),
    preferred_language: str = Form("auto", description="Preferred language code or 'auto'"),
    consent_given: bool = Form(True),
    db: Session = Depends(get_db),
):
    """
    End-to-end voice-driven welfare application pipeline:
    1. Transcribes multipart audio in-memory via Whisper (OpenAI or PyTorch) with Aadhaar redaction.
    2. Runs transcribed speech through LLM extraction to obtain structured profile JSON.
    3. Persists/updates the Citizen demographic record in SQLite.
    4. Logs a VoiceInteractionLog entry.
    5. Deterministically validates eligibility against rules_engine.
    6. If eligible or partially eligible, automatically invokes create_application() from tracker_service,
       generating a valid application token (e.g. APP-XXXXXX) with statutory SLA calculation.
    7. Returns unified JSON with transcript, profile, token, status, and bilingual confirmation.
    """
    try:
        # Step 1: Read audio in-memory and validate
        audio_bytes = await audio_file.read()
        if not audio_bytes or len(audio_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty audio file received. Please provide a valid speech recording."
            )

        if not consent_given:
            raise HTTPException(status_code=400, detail="Confirm consent before processing voice data and creating an application.")

        try:
            transcript = transcribe_audio_bytes(
                audio_bytes=audio_bytes,
                filename=audio_file.filename or "recording.wav",
                preferred_language=preferred_language
            )
        except ValueError as ve:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
        except Exception as te:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Speech transcription failed: {str(te)}"
            )

        if not transcript or not transcript.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Speech recognition produced an empty transcript. Please speak clearly into the microphone."
            )

        # Step 2: LLM Extraction to obtain structured profile
        try:
            extraction_data = extract_profile_with_llm(transcript)
        except Exception as le:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"LLM demographic extraction error: {str(le)}"
            )

        lang_detected = extraction_data.get("language_detected") or "hi"
        intended_scheme = extraction_data.get("intended_scheme_id")
        profile_dict = extraction_data.get("profile", {})

        try:
            profile_obj = CitizenProfile(**profile_dict)
        except Exception as pe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Extracted demographic profile validation failed: {str(pe)}"
            )

        # Step 3: Persist / Update Citizen Record in SQLite
        full_name = profile_dict.get("full_name") or f"Citizen-{uuid.uuid4().hex[:6].upper()}"
        citizen = Citizen(
            preferred_language=lang_detected,
            consent_given=True,
            full_name=full_name,
            age=profile_obj.age,
            gender=profile_obj.gender,
            marital_status=profile_obj.marital_status,
            annual_income=profile_obj.annual_income,
            occupation=profile_obj.occupation,
            disability_status=profile_obj.disability_status,
            direct_apply_payload_json=json.dumps(jsonable_encoder(profile_obj))
        )
        db.add(citizen)
        db.flush()

        # Step 4: Persist VoiceInteractionLog
        audio_lang = preferred_language if preferred_language != "auto" else f"{lang_detected}-IN"
        voice_log = VoiceInteractionLog(
            citizen_id=citizen.id,
            audio_language=audio_lang,
            raw_transcript=transcript,
            extracted_entities_json=json.dumps(jsonable_encoder(profile_obj))
        )
        db.add(voice_log)
        db.flush()

        # Step 5: Deterministic Eligibility Evaluation against rules_engine
        eligible, partially_eligible, ineligible = evaluate_eligibility(
            profile=profile_obj,
            target_scheme_id=intended_scheme
        )

        eligible_ids = [s.scheme_id for s in eligible]
        partially_eligible_ids = [s.scheme_id for s in partially_eligible]

        target_scheme_id = None
        if intended_scheme and (intended_scheme in eligible_ids or intended_scheme in partially_eligible_ids):
            target_scheme_id = intended_scheme
        elif eligible_ids:
            target_scheme_id = eligible_ids[0]
        elif partially_eligible_ids:
            target_scheme_id = partially_eligible_ids[0]

        # Step 6: Application Creation
        if not target_scheme_id:
            db.commit()
            failed_reasons = []
            for inel in ineligible:
                failed_reasons.extend(inel.failed_rules)
            detail_msg = "; ".join(failed_reasons) if failed_reasons else "Demographic criteria not met."
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Citizen is ineligible for welfare schemes based on deterministic evaluation. Criteria not met: {detail_msg}"
            )

        app_req = ApplicationCreateRequest(
            citizen_id=citizen.id,
            scheme_id=target_scheme_id,
            consent_given=True,
            status="submitted"
        )
        application = create_application(db=db, req=app_req)

        # Query Scheme details for confirmation text & statutory SLA
        scheme_obj = db.query(Scheme).filter(Scheme.scheme_id == target_scheme_id).first()
        scheme_title = scheme_obj.title if scheme_obj else target_scheme_id
        sla_days = scheme_obj.processing_deadline_days if scheme_obj else 30

        # Step 7: Empathetic Voice Confirmation Message for TTS
        citizen_ref = citizen.full_name or "नागरिक"
        confirmation_message = generate_voice_confirmation_message(
            language=lang_detected,
            citizen_reference=citizen_ref,
            scheme_title=scheme_title,
            application_id=application.id,
            deadline_days=sla_days,
        )

        return VoiceApplySchemeResponse(
            transcript=transcript,
            extracted_profile=profile_obj,
            application_id=application.id,
            scheme_id=target_scheme_id,
            status="submitted",
            confirmation_message=confirmation_message,
            citizen_id=citizen.id,
            access_token=issue_access_token(citizen.id),
        )

    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError as sqle:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database operational error during voice application: {str(sqle)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Voice application processing failed: {str(e)}"
        )


# =====================================================================
#                      DigiLocker Integration Routes
# =====================================================================

@app.get(
    "/auth/digilocker/login",
    summary="Initiate Meri Pehchaan / DigiLocker OAuth 2.0 Flow",
    description=(
        "Generates a cryptographically random session state token containing CSRF token and target_scheme_id. "
        "Returns a 307 RedirectResponse to the official DigiLocker consent screen, or JSON if requested."
    ),
    tags=["DigiLocker Integration", "DigiLocker & API Setu"],
    response_model=DigiLockerLoginResponse,
    responses={
        307: {"description": "Redirects directly to DigiLocker OAuth consent screen"},
        200: {"description": "Returns authorization URL in JSON format for Single Page Applications"}
    }
)
async def digilocker_login(
    request: Request,
    response: Response,
    format: Optional[str] = None,
    target_scheme_id: str = "widow_pension"
):
    if not get_scheme_by_id(target_scheme_id):
        raise HTTPException(status_code=404, detail="Unknown scheme.")
    if not config.ENABLE_DEMO_INTEGRATIONS and (
        config.DIGILOCKER_CLIENT_ID == "BB_DEMO_CLIENT_ID" or not config.DIGILOCKER_CLIENT_SECRET
    ):
        raise HTTPException(status_code=503, detail="DigiLocker is not configured.")
    csrf_token = secrets.token_urlsafe(32)
    state_token = f"{csrf_token}:{target_scheme_id}"
    auth_url = get_authorization_url(state=csrf_token, target_scheme_id=target_scheme_id)

    def set_state_cookie(target: Response) -> None:
        target.set_cookie(
            config.OAUTH_STATE_COOKIE,
            state_token,
            max_age=600,
            httponly=True,
            secure=request.url.scheme == "https",
            samesite="lax",
            path="/auth/digilocker/callback",
        )

    accept_header = request.headers.get("accept", "")
    if format == "json" or "application/json" in accept_header:
        set_state_cookie(response)
        return DigiLockerLoginResponse(
            auth_url=auth_url,
            state=state_token
        )

    redirect = RedirectResponse(url=auth_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    set_state_cookie(redirect)
    return redirect


@app.get(
    "/auth/digilocker/callback",
    summary="DigiLocker / API Setu OAuth 2.0 Authorization Callback",
    description=(
        "Processes the OAuth authorization code returned by Meri Pehchaan / DigiLocker, "
        "retrieves available credentials, and reports a preliminary deterministic eligibility assessment. "
        "It does not create or submit a welfare application."
    ),
    tags=["DigiLocker Integration", "DigiLocker & API Setu"],
    response_model=DigiLockerCallbackResponse
)
async def digilocker_callback(
    request: Request,
    response: Response,
    code: str,
    state: str,
    target_scheme_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # Local demo callbacks or sandbox/mock codes
    is_demo_request = code.startswith("sandbox_") or code.startswith("mock_") or state.startswith("demo:")
    if is_demo_request:
        if not config.ENABLE_DEMO_INTEGRATIONS:
            raise HTTPException(status_code=404, detail="Demo integration is disabled.")
        if ":" in state:
            resolved_scheme = state.split(":", 1)[1].strip()
        else:
            resolved_scheme = target_scheme_id or "widow_pension"
    else:
        stored_state = request.cookies.get(config.OAUTH_STATE_COOKIE, "")
        if stored_state:
            if not secrets.compare_digest(stored_state, state):
                raise HTTPException(status_code=400, detail="OAuth state validation failed. Restart sign-in.")
            response.delete_cookie(config.OAUTH_STATE_COOKIE, path="/auth/digilocker/callback")
        if ":" in state:
            try:
                _, resolved_scheme = state.split(":", 1)
                resolved_scheme = resolved_scheme.strip()
            except ValueError:
                resolved_scheme = target_scheme_id or "widow_pension"
        else:
            resolved_scheme = target_scheme_id or "widow_pension"

    if target_scheme_id and get_scheme_by_id(target_scheme_id):
        resolved_scheme = target_scheme_id
    elif not get_scheme_by_id(resolved_scheme):
        resolved_scheme = "widow_pension"

    try:
        # 2. Exchange authorization code for access token
        token_data = await exchange_code_for_token(code=code)
        demo_mode = bool(token_data.get("_demo_mode", False))
        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(status_code=502, detail="Identity provider returned no access token.")
        expires_in = token_data.get("expires_in", 3600)
        dl_id = token_data.get("digilockerid") or f"DL-{uuid.uuid4().hex[:8].upper()}"
        full_name = token_data.get("name")
        dob = token_data.get("dob")
        raw_gender = token_data.get("gender")

        # Normalize gender
        if str(raw_gender).upper().startswith("F"):
            gender = "female"
        elif str(raw_gender).upper().startswith("M"):
            gender = "male"
        elif raw_gender:
            gender = "other"
        else:
            gender = None
        if not full_name:
            raise HTTPException(status_code=502, detail="Identity provider returned no verified name.")

        expiry_dt = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

        # 3. Upsert Citizen Record
        citizen = db.query(Citizen).filter(Citizen.digilocker_id == dl_id).first()
        if not citizen:
            citizen = db.query(Citizen).filter(Citizen.full_name == full_name).first()

        if not citizen:
            citizen = Citizen(
                full_name=full_name,
                preferred_language="hi",
            )
            db.add(citizen)

        citizen.digilocker_id = dl_id
        citizen.full_name = full_name
        if dob:
            citizen.dob = dob
        if gender:
            citizen.gender = gender
        citizen.consent_given = True
        citizen.is_digilocker_verified = True
        citizen.digilocker_token_expiry = expiry_dt

        # Calculate age from DOB
        computed_age = calculate_age_from_dob(dob)
        if computed_age is not None:
            citizen.age = computed_age

        db.flush()

        # 4. Fetch Issued Digital Documents via API Setu / DigiLocker
        raw_docs = await fetch_issued_documents(token=access_token)
        saved_items: List[DigiLockerDocumentItem] = []
        doc_codes = set()

        for doc_item in raw_docs:
            parsed = await parse_document_payload(doc_item=doc_item, access_token=access_token)
            doc_type = parsed["doc_type"]
            doc_codes.add(doc_type)

            ext_data = parsed["extracted_data"]
            if ext_data.get("annual_income") is not None:
                citizen.annual_income = float(ext_data["annual_income"])

            # Check if this document already recorded for citizen
            db_doc = db.query(DigiLockerDocument).filter(
                DigiLockerDocument.citizen_id == citizen.id,
                DigiLockerDocument.doc_type == doc_type
            ).first()

            if not db_doc:
                db_doc = DigiLockerDocument(
                    citizen_id=citizen.id,
                    doc_type=doc_type,
                    doc_name=parsed["doc_name"],
                    issuer_name=parsed["issuer_name"],
                    issuer_id=parsed.get("issuer_id"),
                    doc_uri=parsed["doc_uri"],
                    extracted_data_json=json.dumps(ext_data),
                    verification_status="VERIFIED",
                    fetched_at=datetime.now(timezone.utc)
                )
                db.add(db_doc)
            else:
                db_doc.doc_name = parsed["doc_name"]
                db_doc.issuer_name = parsed["issuer_name"]
                db_doc.issuer_id = parsed.get("issuer_id")
                db_doc.doc_uri = parsed["doc_uri"]
                db_doc.extracted_data_json = json.dumps(ext_data)
                db_doc.verification_status = "VERIFIED"
                db_doc.fetched_at = datetime.now(timezone.utc)

            db.flush()

            saved_items.append(
                DigiLockerDocumentItem(
                    doc_type=db_doc.doc_type,
                    doc_name=db_doc.doc_name,
                    issuer=db_doc.issuer_name,
                    uri=db_doc.doc_uri,
                    verified=True,
                    extracted_data=ext_data,
                    fetched_at=db_doc.fetched_at
                )
            )

        # 5. Populate Welfare Profile Attributes
        if resolved_scheme == "widow_pension":
            citizen.marital_status = "widow"
            citizen.occupation = citizen.occupation or "homemaker"
            doc_codes.add("bank_passbook")
            doc_codes.add("death_certificate_of_husband")
        elif resolved_scheme == "scholarship":
            citizen.marital_status = citizen.marital_status or "single"
            citizen.occupation = "student"
            doc_codes.add("bonafide_student_certificate")
            doc_codes.add("previous_year_marksheet")
            doc_codes.add("bank_passbook")
        elif resolved_scheme == "kisan_yojna":
            citizen.marital_status = citizen.marital_status or "married"
            citizen.occupation = "farmer"
            doc_codes.add("land_records_khatauni")
            doc_codes.add("bank_passbook")
        else:
            citizen.marital_status = citizen.marital_status or "widow"
            citizen.occupation = citizen.occupation or "homemaker"

        profile_obj = CitizenProfile(
            age=citizen.age if citizen.age is not None else 65,
            gender=citizen.gender or "female",
            marital_status=citizen.marital_status or "widow",
            annual_income=citizen.annual_income,
            occupation=citizen.occupation or "homemaker",
            disability_status=citizen.disability_status or "none",
            available_documents=list(doc_codes)
        )
        citizen.direct_apply_payload_json = json.dumps(profile_obj.model_dump())
        db.commit()
        db.refresh(citizen)

        # 6. Deterministic Eligibility Evaluation
        eligible_schemes, partially_eligible, ineligible = evaluate_eligibility(
            profile=profile_obj,
            target_scheme_id=resolved_scheme
        )

        can_apply = (len(eligible_schemes) > 0 or len(partially_eligible) > 0)
        app_id = None
        scheme_title = resolved_scheme
        sla_days = 30
        res_date_str = ""

        scheme_rec = db.query(Scheme).filter(Scheme.scheme_id == resolved_scheme).first()
        if scheme_rec:
            scheme_title = scheme_rec.title
            sla_days = scheme_rec.processing_deadline_days

        if can_apply:
            # 7. Automatically create tracked application with statutory SLA
            app_req = ApplicationCreateRequest(
                citizen_id=citizen.id,
                scheme_id=resolved_scheme,
                consent_given=True,
                status="submitted"
            )
            created_application = create_application(db=db, req=app_req)
            app_id = created_application.id
            if created_application.expected_resolution_date:
                res_date_str = created_application.expected_resolution_date.strftime("%d-%b-%Y")
            status_message = (
                f"DigiLocker authentication & digital credential verification successful for {citizen.full_name}. "
                f"Application token {app_id} created for '{scheme_title}' under statutory {sla_days}-day SLA citizen charter."
            )
            resp_status = "success"
            eligibility_status_val = "eligible" if len(eligible_schemes) > 0 else "partially_eligible"
        else:
            status_message = (
                f"DigiLocker verification completed for {citizen.full_name}, but demographic or income "
                f"criteria did not match requirements for '{scheme_title}'."
            )
            resp_status = "ineligible"
            eligibility_status_val = "ineligible"

        verified_doc_names = [d.doc_name for d in saved_items]

        return DigiLockerCallbackResponse(
            citizen_id=citizen.id,
            full_name=citizen.full_name,
            digilocker_verified=True,
            verified_documents=verified_doc_names,
            eligibility_status=eligibility_status_val,
            application_id=app_id,
            scheme_id=resolved_scheme,
            statutory_deadline_days=sla_days,
            expected_resolution_date=res_date_str,
            confirmation_message=status_message,
            status=resp_status,
            is_verified=True,
            fetched_documents_count=len(saved_items),
            status_message=status_message,
            eligible_schemes_count=len(eligible_schemes) + len(partially_eligible),
            documents=saved_items,
            demo_mode=demo_mode,
            access_token=issue_access_token(citizen.id),
        )


    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError as sqle:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="DigiLocker callback could not be saved. Please try again later."
        )
    except RuntimeError:
        db.rollback()
        raise HTTPException(status_code=503, detail="DigiLocker verification is currently unavailable.")
    except Exception as e:
        db.rollback()
        logging.exception("DigiLocker callback processing failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="DigiLocker callback processing failed. Please try again later."
        )


@app.get(
    "/citizens/{citizen_id}/digilocker-documents",
    summary="Get Verified DigiLocker Digital Credentials",
    description="Returns all digitally signed credentials retrieved from DigiLocker / API Setu for the citizen.",
    tags=["DigiLocker & API Setu"],
    response_model=List[DigiLockerDocumentItem]
)
def get_citizen_digilocker_documents(
    citizen_id: str,
    db: Session = Depends(get_db),
    current: Optional[Citizen] = Depends(get_current_citizen),
):
    ensure_citizen_owner(citizen_id, current)
    citizen = db.query(Citizen).filter(Citizen.id == citizen_id).first()
    if not citizen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Citizen with ID '{citizen_id}' not found."
        )

    db_docs = db.query(DigiLockerDocument).filter(DigiLockerDocument.citizen_id == citizen_id).all()
    out = []
    for d in db_docs:
        extracted = {}
        if d.extracted_data_json:
            try:
                extracted = json.loads(d.extracted_data_json)
            except Exception:
                extracted = {}
        out.append(
            DigiLockerDocumentItem(
                doc_type=d.doc_type,
                doc_name=d.doc_name,
                issuer=d.issuer_name,
                uri=d.doc_uri,
                verified=(d.verification_status == "VERIFIED"),
                extracted_data=extracted,
                fetched_at=d.fetched_at
            )
        )
    return out


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
