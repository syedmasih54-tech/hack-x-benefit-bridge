from datetime import datetime, timezone
import uuid
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship
from database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Citizen(Base):
    __tablename__ = "citizens"

    id = Column(String(64), primary_key=True, default=lambda: f"CIT-{uuid.uuid4().hex[:8].upper()}")
    created_at = Column(DateTime, default=utc_now, nullable=False)
    preferred_language = Column(String(16), default="en", nullable=False)
    consent_given = Column(Boolean, default=False, nullable=False)

    # Demographic, economic, and application profile attributes
    # PRIVACY CONSTRAINT: Strictly NO national identity numbers (Aadhaar) are stored.
    digilocker_id = Column(String(64), unique=True, index=True, nullable=True)
    full_name = Column(String(128), nullable=True)
    dob = Column(String(16), nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(32), nullable=True)
    marital_status = Column(String(32), nullable=True)
    annual_income = Column(Float, default=0.0, nullable=False)
    occupation = Column(String(64), nullable=True)
    disability_status = Column(String(64), default="none", nullable=True)
    is_digilocker_verified = Column(Boolean, default=False, nullable=False)
    digilocker_token_expiry = Column(DateTime, nullable=True)
    direct_apply_payload_json = Column(Text, nullable=True)

    applications = relationship("Application", back_populates="citizen", cascade="all, delete-orphan")
    voice_logs = relationship("VoiceInteractionLog", back_populates="citizen", cascade="all, delete-orphan")
    verified_documents = relationship("DigiLockerDocument", back_populates="citizen", cascade="all, delete-orphan")


class DigiLockerDocument(Base):
    __tablename__ = "digilocker_documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    citizen_id = Column(String(64), ForeignKey("citizens.id", ondelete="CASCADE"), nullable=False)
    doc_type = Column(String(64), nullable=False)  # e.g., 'ration_card', 'income_certificate', 'caste_certificate'
    doc_name = Column(String(255), nullable=False)
    issuer_name = Column(String(255), nullable=False)
    issuer_id = Column(String(128), nullable=True)
    doc_uri = Column(String(512), nullable=False)  # Authentic DigiLocker URI schema
    extracted_data_json = Column(Text, nullable=False)  # Parsed XML/JSON metadata with zero Aadhaar numbers
    verification_status = Column(String(32), default="VERIFIED", nullable=False)
    fetched_at = Column(DateTime, default=utc_now, nullable=False)

    citizen = relationship("Citizen", back_populates="verified_documents")


class VoiceInteractionLog(Base):
    __tablename__ = "voice_interaction_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    citizen_id = Column(String(64), ForeignKey("citizens.id", ondelete="CASCADE"), nullable=True)
    audio_language = Column(String(16), default="hi-IN", nullable=False)
    raw_transcript = Column(Text, nullable=False)
    extracted_entities_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    citizen = relationship("Citizen", back_populates="voice_logs")


class Scheme(Base):
    __tablename__ = "schemes"

    scheme_id = Column(String(64), primary_key=True)
    title = Column(String(255), nullable=False)
    ministry_or_department = Column(String(255), nullable=False)
    state_or_level = Column(String(64), default="Central", nullable=False)  # "Central", "Delhi", "Telangana", etc.
    rule_version = Column(String(32), nullable=False)
    processing_deadline_days = Column(Integer, nullable=False)
    official_portal_url = Column(String(512), nullable=False)
    citizen_charter_clause = Column(String(255), nullable=True)  # e.g., "Right to Public Services Act, Sec 4"
    official_guidelines_url = Column(String(512), nullable=True)  # Official Gazette or Operational Guidelines PDF/URL
    last_synced_at = Column(DateTime, default=utc_now, nullable=False)
    is_live_source = Column(Boolean, default=False, nullable=False)

    # Backward compatibility columns / aliases for existing codebase & database
    official_source_name = Column(String(255), nullable=True)
    source_gazette_or_guideline_url = Column(String(512), nullable=True)
    last_verified_date = Column(String(32), nullable=True)
    is_live_data_source = Column(Boolean, default=False, nullable=True)

    applications = relationship("Application", back_populates="scheme")


class Application(Base):
    __tablename__ = "applications"

    id = Column(String(64), primary_key=True, default=lambda: f"APP-{uuid.uuid4().hex[:8].upper()}")
    citizen_id = Column(String(64), ForeignKey("citizens.id"), nullable=False)
    scheme_id = Column(String(64), ForeignKey("schemes.scheme_id"), nullable=False)
    status = Column(String(32), default="draft", nullable=False)
    submitted_at = Column(DateTime, nullable=True)
    expected_resolution_date = Column(DateTime, nullable=True)

    citizen = relationship("Citizen", back_populates="applications")
    scheme = relationship("Scheme", back_populates="applications")
    events = relationship("ApplicationEvent", back_populates="application", cascade="all, delete-orphan", order_by="ApplicationEvent.created_at")
    document_checks = relationship("DocumentCheck", back_populates="application")
    grievances = relationship("Grievance", back_populates="application", cascade="all, delete-orphan")


class ApplicationEvent(Base):
    __tablename__ = "application_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(String(64), ForeignKey("applications.id"), nullable=False)
    event_type = Column(String(64), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    application = relationship("Application", back_populates="events")


class DocumentCheck(Base):
    __tablename__ = "document_checks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(String(64), ForeignKey("applications.id"), nullable=True)
    document_type = Column(String(64), nullable=False)
    extracted_fields_json = Column(Text, nullable=False)  # JSON serialized dict
    mismatch_warnings_json = Column(Text, nullable=False)  # JSON serialized list
    created_at = Column(DateTime, default=utc_now, nullable=False)

    application = relationship("Application", back_populates="document_checks")


class Grievance(Base):
    __tablename__ = "grievances"

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(String(64), ForeignKey("applications.id"), nullable=False)
    draft_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    status = Column(String(32), default="drafted", nullable=False)

    application = relationship("Application", back_populates="grievances")
