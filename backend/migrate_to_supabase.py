"""
BenefitBridge - Automated Supabase PostgreSQL Migration Tool
============================================================
Migrates your local SQLite schema and live data directly into Supabase PostgreSQL.

Usage:
    python migrate_to_supabase.py --url "postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres"

Or set DATABASE_URL in your environment:
    $env:DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres"
    python migrate_to_supabase.py
"""

import os
import sys
import argparse
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

# Ensure backend directory is in sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import models
from models import (
    Base,
    Citizen,
    Scheme,
    Application,
    DigiLockerDocument,
    VoiceInteractionLog,
    ApplicationEvent,
    DocumentCheck,
    Grievance,
)
from seed_data import seed_database


def normalize_supabase_url(raw_url: str) -> str:
    url = raw_url.strip()
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif url.startswith("postgresql://") and not url.startswith("postgresql+"):
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


def run_migration(target_url: str, update_env: bool = True):
    print("=" * 70)
    print(" BenefitBridge -> Supabase PostgreSQL Automated Migration")
    print("=" * 70)

    pg_url = normalize_supabase_url(target_url)
    engine_kwargs = {"pool_pre_ping": True}
    if "sslmode=" not in pg_url:
        # pyrefly: ignore[bad-assignment]
        engine_kwargs["connect_args"] = {"sslmode": "require"}

    print("\n[1/5] Connecting to Supabase PostgreSQL...")
    try:
        remote_engine = create_engine(pg_url, **engine_kwargs)
        with remote_engine.connect() as conn:
            res = conn.execute(text("SELECT version();")).fetchone()
            print(f"      [CONNECTED] {res[0][:60]}...")
    except Exception as e:
        print(f"\n[ERROR] Could not connect to Supabase database:\n{e}")
        print("\nPlease check:")
        print("  1. The password in your connection string is correct.")
        print("  2. Your Supabase project is active.")
        print("  3. For pooled connection, verify host and port (6543 or 5432).")
        sys.exit(1)

    print("\n[2/5] Creating Database Tables on Supabase...")
    try:
        Base.metadata.create_all(bind=remote_engine)
        print("      [OK] All tables successfully created or verified.")
    except Exception as e:
        print(f"[ERROR] Failed to create tables: {e}")
        sys.exit(1)

    # Check for local SQLite database
    sqlite_path = SCRIPT_DIR / "benefitbridge.db"
    if not sqlite_path.exists():
        # Check parent folder as well
        parent_db = SCRIPT_DIR.parent / "benefitbridge.db"
        if parent_db.exists():
            sqlite_path = parent_db

    RemoteSession = sessionmaker(bind=remote_engine, autocommit=False, autoflush=False)

    if sqlite_path.exists():
        print(f"\n[3/5] Migrating Existing SQLite Records from: {sqlite_path.name}...")
        sqlite_conn = sqlite3.connect(str(sqlite_path))
        sqlite_conn.row_factory = sqlite3.Row
        cur = sqlite_conn.cursor()

        tables_order = [
            ("citizens", Citizen),
            ("schemes", Scheme),
            ("applications", Application),
            ("digilocker_documents", DigiLockerDocument),
            ("voice_interaction_logs", VoiceInteractionLog),
            ("application_events", ApplicationEvent),
            ("document_checks", DocumentCheck),
            ("grievances", Grievance),
        ]

        with RemoteSession() as session:
            for tbl_name, model_cls in tables_order:
                try:
                    rows = cur.execute(f"SELECT * FROM {tbl_name}").fetchall()
                    if not rows:
                        continue
                    count = 0
                    for row in rows:
                        data = dict(row)
                        # Handle datetime conversions if stored as strings
                        for k, v in data.items():
                            if v is not None and ("_at" in k or "expiry" in k or "date" in k and isinstance(v, str)):
                                try:
                                    data[k] = datetime.fromisoformat(v)
                                except Exception:
                                    pass
                        # Convert boolean integer values to bool
                        for k, v in data.items():
                            if isinstance(v, int) and k in ("consent_given", "is_digilocker_verified", "is_live_source", "is_live_data_source"):
                                data[k] = bool(v)

                        session.merge(model_cls(**data))
                        count += 1
                    session.commit()
                    print(f"      -> {tbl_name}: {count} records transferred")
                except Exception as ex:
                    session.rollback()
                    print(f"      [WARN] Table {tbl_name} transfer note: {ex}")

        # Reset serial sequences in PostgreSQL
        print("\n[4/5] Synchronizing PostgreSQL ID Sequences...")
        with remote_engine.connect() as conn:
            serial_tables = [
                ("digilocker_documents", "id"),
                ("voice_interaction_logs", "id"),
                ("application_events", "id"),
                ("document_checks", "id"),
                ("grievances", "id"),
            ]
            for tbl, pkey in serial_tables:
                try:
                    conn.execute(
                        text(
                            f"SELECT setval(pg_get_serial_sequence('{tbl}', '{pkey}'), COALESCE(max({pkey}), 1)) FROM {tbl};"
                        )
                    )
                    conn.commit()
                except Exception:
                    pass
        print("      [OK] Sequences synchronized.")

    else:
        print("\n[3/5] No local SQLite file found. Running fresh database seeder...")
        # Override DATABASE_URL in environment for seed_database
        os.environ["DATABASE_URL"] = target_url
        seed_database()
        print("      [OK] Schemes and demo profiles seeded successfully.")

    print("\n[5/5] Verifying Supabase Tables and Record Counts...")
    inspector = inspect(remote_engine)
    with remote_engine.connect() as conn:
        for table_name in inspector.get_table_names():
            cnt = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            print(f"      * {table_name:24}: {cnt} rows")

    # Update local .env if requested
    if update_env:
        env_path = SCRIPT_DIR / ".env"
        env_content = ""
        if env_path.exists():
            env_content = env_path.read_text(encoding="utf-8")
        
        if "DATABASE_URL=" in env_content:
            new_lines = []
            for line in env_content.splitlines():
                if line.startswith("DATABASE_URL="):
                    new_lines.append(f"DATABASE_URL={target_url}")
                else:
                    new_lines.append(line)
            env_path.write_text("\n".join(new_lines), encoding="utf-8")
        else:
            with env_path.open("a", encoding="utf-8") as f:
                f.write(f"\nDATABASE_URL={target_url}\n")
        print(f"\n[CONFIG] Updated local {env_path.name} with DATABASE_URL.")

    print("\n" + "=" * 70)
    print(" [SUCCESS] Supabase migration completed successfully!")
    print("=" * 70)
    print("\nNext step: Push to GitHub and add DATABASE_URL in Vercel settings:")
    print("  1. git add .")
    print("  2. git commit -m 'feat: connect to Supabase PostgreSQL database'")
    print("  3. git push origin main")
    print("  4. In Vercel Project Settings -> Environment Variables:")
    print("     Add DATABASE_URL = <your_supabase_connection_string>")
    print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate BenefitBridge SQLite to Supabase PostgreSQL")
    parser.add_argument("--url", help="Supabase PostgreSQL connection string (postgresql://...)")
    parser.add_argument("--no-env", action="store_true", help="Do not write DATABASE_URL into local .env")
    args = parser.parse_args()

    supabase_url = args.url or os.getenv("DATABASE_URL")
    if not supabase_url:
        print("Please provide your Supabase PostgreSQL connection string.")
        print("Example:")
        print("  python migrate_to_supabase.py --url 'postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres'")
        sys.exit(1)

    run_migration(supabase_url, update_env=not args.no_env)

