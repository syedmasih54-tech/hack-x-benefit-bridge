import os
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

# Support Supabase / Postgres or local/serverless SQLite
raw_db_url = os.getenv("DATABASE_URL", "").strip()

if raw_db_url:
    # Ensure standard SQLAlchemy psycopg2 driver prefix for Supabase / PostgreSQL
    if raw_db_url.startswith("postgres://"):
        DATABASE_URL = raw_db_url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif raw_db_url.startswith("postgresql://") and not raw_db_url.startswith("postgresql+"):
        DATABASE_URL = raw_db_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    else:
        DATABASE_URL = raw_db_url

    # Check for serverless runtime (Vercel / AWS Lambda)
    is_serverless = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))

    engine_kwargs = {
        "pool_pre_ping": True,
    }

    # In serverless environments, avoid persistent connection holding to preserve Supabase connection pool
    if is_serverless:
        engine_kwargs["poolclass"] = NullPool
    else:
        engine_kwargs["pool_size"] = 5
        engine_kwargs["max_overflow"] = 10
        engine_kwargs["pool_timeout"] = 30.0
        engine_kwargs["pool_recycle"] = 1800

    # Supabase requires SSL encryption
    if "sslmode=" not in DATABASE_URL:
        engine_kwargs["connect_args"] = {"sslmode": "require"}

    engine = create_engine(DATABASE_URL, **engine_kwargs)

else:
    # Fallback to local / serverless SQLite
    DEFAULT_DB_PATH = "/tmp/benefitbridge.db" if os.getenv("VERCEL") else str(Path(__file__).resolve().parent / "benefitbridge.db")
    DATABASE_FILE = os.getenv("BENEFITBRIDGE_DB_PATH", DEFAULT_DB_PATH)
    try:
        Path(DATABASE_FILE).parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

    engine = create_engine(
        DATABASE_URL,
        connect_args={
            "check_same_thread": False,
            "timeout": 30.0,
        },
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30.0,
        pool_pre_ping=True,
    )


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable Write-Ahead Logging (WAL) and busy handling for multi-threaded SQLite."""
    if DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency generator that provides a SQLAlchemy session per request."""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
