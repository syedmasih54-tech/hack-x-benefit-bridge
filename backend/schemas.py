import re
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator


def parse_annual_income(v: Any) -> float:
    """
    Robust Pydantic v2 pre-validator parser for annual_income:
    - Numerical values (int, float) -> cast to float.
    - Text nil values ('nil', 'none', 'zero', 'shunya', 'shunya rupaye', '') -> return 0.0.
    - Text with 'lakh', 'lac' -> multiply by 100,000.0 (e.g., '1.2 Lakh' -> 120000.0).
    - Text with 'k' -> multiply by 1,000.0 (e.g., '75k' -> 75000.0).
    - Text with currency symbols (₹, Rs, INR) and commas -> strip symbols and parse cleanly.
    - Fallback: Any unparseable string defaults gracefully to 0.0 without throwing exceptions.
    """
    if v is None or isinstance(v, bool):
        return 0.0

    if isinstance(v, (int, float)):
        try:
            return max(0.0, float(v))
        except (ValueError, TypeError):
            return 0.0

    if not isinstance(v, str):
        return 0.0

    raw = v.strip().lower()
    if not raw:
        return 0.0

    nil_tokens = {
        "nil", "none", "zero", "shunya", "shunya rupaye", "shunya rupeye",
        "shunya rupee", "shunya rupees", "shoonya", "shoonya rupaye",
        "kuch nahi", "nothing", "null", "n/a", "na", "-", "0"
    }
    if raw in nil_tokens:
        return 0.0

    # Match transliterated phrases like 'shunya rupaye'
    if re.match(r"^(?:shunya|shoonya|zero|nil)\s*(?:rupaye|rupeye|rupees?|rs\.?)?$", raw):
        return 0.0

    # Strip currency symbols, suffixes, and Indian notations
    cleaned = raw.replace("₹", " ").replace("/-", " ")
    cleaned = re.sub(r"\b(inr|rupees?|rupaye|rupeye)\b", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"(?:^|\b|\s)rs\.?\s*", " ", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.replace(",", "").strip()

    if not cleaned or cleaned in nil_tokens or cleaned == "0":
        return 0.0

    # Match Indian notations: Lakh / Lac (100,000)
    lakh_match = re.search(r"^([0-9]+(?:\.[0-9]+)?)\s*(?:lakhs?|lac|lacs|l)\b", cleaned)
    if lakh_match:
        try:
            return float(lakh_match.group(1)) * 100_000.0
        except ValueError:
            return 0.0

    # Match Indian notations: Crore / Cr (10,000,000)
    crore_match = re.search(r"^([0-9]+(?:\.[0-9]+)?)\s*(?:crores?|cr)\b", cleaned)
    if crore_match:
        try:
            return float(crore_match.group(1)) * 10_000_000.0
        except ValueError:
            return 0.0

    # Match thousands: K / thousand (1,000)
    k_match = re.search(r"^([0-9]+(?:\.[0-9]+)?)\s*(?:k|thousand)\b", cleaned)
    if k_match:
        try:
            return float(k_match.group(1)) * 1_000.0
        except ValueError:
            return 0.0

    # Direct float conversion
    try:
        val = float(cleaned)
        return max(0.0, val)
    except ValueError:
        pass

    # Extract any embedded numeric sequence
    num_match = re.search(r"([0-9]+(?:\.[0-9]+)?)", cleaned)
    if num_match:
        try:
            return max(0.0, float(num_match.group(1)))
        except ValueError:
            pass

    return 0.0


# ---------------- Citizen Schemas ----------------
class CitizenBase(BaseModel):
    preferred_language: str = Field(default="en", description="Preferred language code: en, hi, etc.")
    consent_given: bool = Field(..., description="Explicit consent from citizen to process non-Aadhaar verification details.")
    full_name: Optional[str] = Field(default=None, max_length=128, description="Citizen full name")
    digilocker_id: Optional[str] = Field(default=None, max_length=64, description="DigiLocker unique account ID")
    dob: Optional[str] = Field(default=None, max_length=16, description="Date of birth (DD/MM/YYYY)")
    age: Optional[int] = Field(default=None, ge=0, le=130, description="Age in completed years")
    gender: Optional[str] = Field(default=None, description="'female', 'male', or 'other'")
    marital_status: Optional[str] = Field(default=None, description="'widow', 'married', 'unmarried', 'divorced', etc.")
    annual_income: float = Field(default=0.0, ge=0.0, description="Total annual household income in INR")
    occupation: Optional[str] = Field(default=None, description="Occupation: 'homemaker', 'student', 'farmer', 'daily_wage', 'unemployed', etc.")
    disability_status: Optional[str] = Field(default="none", description="Disability status: 'none', 'yes', or percentage/type")
    is_digilocker_verified: bool = Field(default=False, description="True if verified via DigiLocker / API Setu")
    direct_apply_payload_json: Optional[str] = Field(default=None, description="Serialized JSON payload for prefilled application data")

    @field_validator("annual_income", mode="before")
    @classmethod
    def clean_annual_income(cls, v: Any) -> float:
        return parse_annual_income(v)


class CitizenCreate(CitizenBase):
    pass


class CitizenResponse(CitizenBase):
    id: str
    created_at: datetime
    access_token: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ---------------- Voice Interaction Schemas ----------------
class VoiceInteractionLogCreate(BaseModel):
    citizen_id: Optional[str] = Field(default=None, description="Associated citizen ID")
    audio_language: str = Field(default="hi-IN", description="Language code: 'hi-IN', 'en-IN', etc.")
    raw_transcript: str = Field(..., description="Recognized voice transcript")
    extracted_entities_json: Optional[str] = Field(default=None, description="JSON serialized extracted entities")


class VoiceInteractionLogResponse(VoiceInteractionLogCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------- Scheme Schemas ----------------
class DocumentRequirementItem(BaseModel):
    code: str
    name: str
    mandatory: bool = True


class EligibilityRules(BaseModel):
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    gender: List[str] = Field(default_factory=lambda: ["all"])
    marital_status: List[str] = Field(default_factory=lambda: ["all"])
    income_limit: Optional[float] = None
    occupation: List[str] = Field(default_factory=lambda: ["any"])
    disability_status: str = "any"
    required_documents: List[str] = Field(default_factory=list)


class SchemeDetail(BaseModel):
    scheme_id: str
    title: str
    description: str
    state_or_level: str
    eligibility_rules: EligibilityRules
    documents_required: List[DocumentRequirementItem]
    processing_deadline_days: int
    official_portal_url: str
    rule_version: str
    source_reference: str
    ministry_or_department: str = Field(..., description="Ministry or Department overseeing scheme")
    official_guidelines_url: Optional[str] = Field(default=None, description="Official operational guideline or gazette URL")
    citizen_charter_clause: Optional[str] = Field(default=None, description="Statutory citizen charter / public services guarantee clause")
    last_synced_at: Optional[datetime] = Field(default=None, description="UTC timestamp of last live sync")
    is_live_source: bool = Field(default=False, description="True only when scheme rules were fetched and verified from a live source")

    # Backward compatibility attributes
    official_source_name: str = Field(default="", description="Official government source authority")
    source_gazette_or_guideline_url: str = Field(default="", description="Authentic operational guideline or gazette URL")
    last_verified_date: Optional[str] = Field(default=None, description="Date the scheme rules were last verified against an official source")
    is_live_data_source: bool = Field(default=False, description="True only when scheme rules were fetched and verified from a live source")

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def sync_detail_provenance(cls, data: Any) -> Any:
        if hasattr(data, "__dict__"):
            ministry = getattr(data, "ministry_or_department", None) or getattr(data, "official_source_name", None) or "Official Government Authority"
            guideline = getattr(data, "official_guidelines_url", None) or getattr(data, "source_gazette_or_guideline_url", None) or getattr(data, "official_portal_url", "")
            is_live = getattr(data, "is_live_source", None)
            if is_live is None:
                is_live = getattr(data, "is_live_data_source", False)
            last_synced = getattr(data, "last_synced_at", None) or datetime.now()
            last_verified = getattr(data, "last_verified_date", None)
            if not last_verified and bool(is_live) and isinstance(last_synced, datetime):
                last_verified = last_synced.strftime("%d-%b-%Y")
            d = {k: v for k, v in data.__dict__.items() if not k.startswith("_")}
            d["ministry_or_department"] = ministry
            d["official_source_name"] = ministry
            d["official_guidelines_url"] = guideline
            d["source_gazette_or_guideline_url"] = guideline
            d["is_live_source"] = bool(is_live)
            d["is_live_data_source"] = bool(is_live)
            d["last_synced_at"] = last_synced
            d["last_verified_date"] = last_verified
            return d
        elif isinstance(data, dict):
            ministry = data.get("ministry_or_department") or data.get("official_source_name") or "Official Government Authority"
            guideline = data.get("official_guidelines_url") or data.get("source_gazette_or_guideline_url") or data.get("official_portal_url", "")
            is_live = data.get("is_live_source")
            if is_live is None:
                is_live = data.get("is_live_data_source", False)
            data["ministry_or_department"] = ministry
            data["official_source_name"] = ministry
            data["official_guidelines_url"] = guideline
            data["source_gazette_or_guideline_url"] = guideline
            data["is_live_source"] = bool(is_live)
            data["is_live_data_source"] = bool(is_live)
            if "last_synced_at" not in data or data["last_synced_at"] is None:
                data["last_synced_at"] = datetime.now()
            if "last_verified_date" not in data or not data["last_verified_date"]:
                if bool(is_live) and isinstance(data.get("last_synced_at"), datetime):
                    data["last_verified_date"] = data["last_synced_at"].strftime("%d-%b-%Y")
                else:
                    data["last_verified_date"] = None
        return data


class SchemeSummary(BaseModel):
    scheme_id: str
    title: str
    description: str
    state_or_level: str
    processing_deadline_days: int
    official_portal_url: str
    rule_version: str
    ministry_or_department: str = Field(..., description="Ministry or Department overseeing scheme")
    official_guidelines_url: Optional[str] = Field(default=None, description="Official operational guideline or gazette URL")
    citizen_charter_clause: Optional[str] = Field(default=None, description="Statutory citizen charter / public services guarantee clause")
    last_synced_at: Optional[datetime] = Field(default=None, description="UTC timestamp of last live sync")
    is_live_source: bool = Field(default=False, description="True only if verified against a live external source")

    # Backward compatibility attributes
    official_source_name: str = Field(default="", description="Official government source authority")
    source_gazette_or_guideline_url: str = Field(default="", description="Authentic operational guideline or gazette URL")
    last_verified_date: Optional[str] = Field(default=None, description="Date verified against official portal (DD-Mon-YYYY)")
    is_live_data_source: bool = Field(default=False, description="True only if verified against a live external source")

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def sync_summary_provenance(cls, data: Any) -> Any:
        if hasattr(data, "__dict__"):
            ministry = getattr(data, "ministry_or_department", None) or getattr(data, "official_source_name", None) or "Official Government Authority"
            guideline = getattr(data, "official_guidelines_url", None) or getattr(data, "source_gazette_or_guideline_url", None) or getattr(data, "official_portal_url", "")
            is_live = getattr(data, "is_live_source", None)
            if is_live is None:
                is_live = getattr(data, "is_live_data_source", False)
            last_synced = getattr(data, "last_synced_at", None)
            last_verified = getattr(data, "last_verified_date", None)
            if not last_verified and isinstance(last_synced, datetime):
                last_verified = last_synced.strftime("%d-%b-%Y")
            d = {k: v for k, v in data.__dict__.items() if not k.startswith("_")}
            d["ministry_or_department"] = ministry
            d["official_source_name"] = ministry
            d["official_guidelines_url"] = guideline
            d["source_gazette_or_guideline_url"] = guideline
            d["is_live_source"] = bool(is_live)
            d["is_live_data_source"] = bool(is_live)
            d["last_synced_at"] = last_synced
            d["last_verified_date"] = last_verified
            return d
        elif isinstance(data, dict):
            ministry = data.get("ministry_or_department") or data.get("official_source_name") or "Official Government Authority"
            guideline = data.get("official_guidelines_url") or data.get("source_gazette_or_guideline_url") or data.get("official_portal_url", "")
            is_live = data.get("is_live_source")
            if is_live is None:
                is_live = data.get("is_live_data_source", False)
            data["ministry_or_department"] = ministry
            data["official_source_name"] = ministry
            data["official_guidelines_url"] = guideline
            data["source_gazette_or_guideline_url"] = guideline
            data["is_live_source"] = bool(is_live)
            data["is_live_data_source"] = bool(is_live)
            if "last_verified_date" not in data or not data["last_verified_date"]:
                if isinstance(data["last_synced_at"], datetime):
                    data["last_verified_date"] = data["last_synced_at"].strftime("%d-%b-%Y")
                else:
                    data["last_verified_date"] = None
        return data


class SyncSourceStatus(BaseModel):
    name: str = Field(..., description="Official government repository name")
    url: str = Field(..., description="Official portal or dataset URL")
    status: str = Field(..., description="'synced', 'live_verified', 'mirror_fallback', or 'offline'")
    details: Optional[str] = Field(default=None, description="Detailed ingestion note or statutory clause reference")


class LiveSyncResponse(BaseModel):
    status: str = Field(default="success", description="Overall sync status")
    synced_schemes_count: int = Field(..., description="Total schemes updated in SQLite & rules engine")
    schemes_synced: List[str] = Field(..., description="List of scheme IDs synced")
    sources_contacted: List[SyncSourceStatus] = Field(..., description="Audit list of external portals queried")
    timestamp: datetime = Field(..., description="UTC completion timestamp")
    errors: List[str] = Field(default_factory=list, description="Any transient warnings or network errors handled gracefully")



# ---------------- Eligibility Check Schemas ----------------
class CitizenProfile(BaseModel):
    age: Optional[int] = Field(default=None, ge=0, le=130, description="Age in completed years, if known")
    gender: Optional[str] = Field(default=None, description="'female', 'male', or 'other', if known")
    marital_status: Optional[str] = Field(default=None, description="Marital status, if known")
    annual_income: float = Field(default=0.0, ge=0.0, description="Total annual household income in INR")
    occupation: Optional[str] = Field(default=None, description="Occupation, if known")
    disability_status: Optional[str] = Field(default=None, description="'none', 'yes', or percentage/type, if known")
    available_documents: List[str] = Field(
        default_factory=list,
        description="List of document codes held by citizen, e.g. ['ration_card', 'bank_passbook']"
    )

    @field_validator("annual_income", mode="before")
    @classmethod
    def clean_annual_income(cls, v: Any) -> float:
        return parse_annual_income(v)


class VoiceIntakeRequest(BaseModel):
    raw_transcript: str = Field(..., description="Speech-to-text input transcript from citizen")
    audio_language: Optional[str] = Field(default=None, description="Optional audio language: 'hi-IN', 'en-IN'")
    citizen_id: str = Field(..., description="Authenticated citizen record receiving this intake")
    consent_given: bool = Field(default=False, description="Explicit consent to process and retain this voice intake")


class VoiceIntakeResponse(BaseModel):
    language_detected: str = Field(..., description="'hi' or 'en'")
    intended_scheme_id: Optional[str] = Field(default=None, description="'widow_pension', 'kisan_yojna', 'scholarship', or null")
    profile: CitizenProfile
    log_id: Optional[int] = Field(default=None, description="Database VoiceInteractionLog ID")


class VoiceApplySchemeResponse(BaseModel):
    transcript: str = Field(..., description="Processed speech-to-text transcript (Aadhaar redacted)")
    extracted_profile: CitizenProfile = Field(..., description="Structured demographic & financial profile")
    application_id: Optional[str] = Field(default=None, description="Generated application tracking token (e.g., APP-XXXXXX)")
    scheme_id: Optional[str] = Field(default=None, description="Target welfare scheme ID applied for")
    status: str = Field(default="submitted", description="Application status: 'submitted' or 'ineligible'")
    confirmation_message: str = Field(..., description="Bilingual audio/text feedback string")
    citizen_id: Optional[str] = None
    access_token: Optional[str] = None


class EligibilityCheckRequest(BaseModel):
    citizen_profile: CitizenProfile
    scheme_id: Optional[str] = Field(
        default=None,
        description="Optional scheme_id to check against a single scheme, or leave empty for all schemes"
    )
    simplify_with_llm: bool = Field(
        default=False,
        description="Optional LLM simplification of explanation text only (never decides eligibility)"
    )


class SchemeEvaluationResult(BaseModel):
    scheme_id: str
    scheme_title: str
    status: str = Field(..., description="'eligible', 'partially_eligible', or 'ineligible'")
    matched_rules: List[str]
    failed_rules: List[str]
    missing_documents: List[str]
    missing_information: List[str] = Field(default_factory=list)
    simple_explanation: str
    rule_version: str
    official_portal_url: str
    official_source_name: str = Field(default="Official Government Authority", description="Official government authority name")
    citizen_charter_clause: str = Field(default="Statutory Citizens Charter Guarantee", description="Statutory citizen charter clause")


class EligibilityCheckResponse(BaseModel):
    eligible_schemes: List[SchemeEvaluationResult]
    partially_eligible_schemes: List[SchemeEvaluationResult]
    ineligible_schemes: List[SchemeEvaluationResult]
    total_schemes_evaluated: int
    citizen_disclaimer: str = (
        "BenefitBridge provides preparatory assistance only. "
        "Final eligibility and benefit disbursal are solely determined by official government portals and designated field officers."
    )


# ---------------- OCR & Document Doctor Schemas ----------------
class ExtractedFields(BaseModel):
    full_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    account_number: Optional[str] = None
    document_type: Optional[str] = None
    ifsc_code: Optional[str] = None


class DocumentScanResponse(BaseModel):
    document_type: str
    extracted_fields: ExtractedFields
    raw_ocr_text: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    confidence_indicator: str = Field(..., description="'HIGH', 'MEDIUM', 'LOW'")
    warnings: List[str]
    manual_verification_required: bool
    privacy_notice: str = "Uploaded image processed in-memory and discarded. BenefitBridge does NOT store identity images or Aadhaar numbers."


class DocumentCompareRequest(BaseModel):
    document_1_fields: Dict[str, Any]
    document_2_fields: Dict[str, Any]
    document_1_type: str = "ration_card"
    document_2_type: str = "bank_passbook"


class DocumentCompareResponse(BaseModel):
    name_match_status: str = Field(
        ...,
        description="'exact_match', 'likely_match_with_spelling_variation', 'mismatch', 'missing_field'"
    )
    name_document_1: Optional[str] = None
    name_document_2: Optional[str] = None
    similarity_score: float = Field(..., ge=0.0, le=1.0)
    mismatches_detected: List[str]
    recommendations: List[str]
    citizen_warning: str
    requires_affidavit_or_update: bool


# ---------------- Application Tracker Schemas ----------------
class ApplicationCreateRequest(BaseModel):
    citizen_id: str
    scheme_id: str
    consent_given: bool = False
    status: str = "submitted"
    custom_submitted_at: Optional[datetime] = Field(
        default=None,
        description="Optional backdated submission timestamp for testing/demoing overdue status"
    )


class ApplicationEventResponse(BaseModel):
    id: int
    event_type: str
    message: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplicationDetailResponse(BaseModel):
    id: str
    citizen_id: str
    scheme_id: str
    scheme_title: str
    status: str
    submitted_at: Optional[datetime]
    expected_resolution_date: Optional[datetime]
    processing_deadline_days: int
    official_portal_url: str
    events: List[ApplicationEventResponse]

    model_config = ConfigDict(from_attributes=True)


class CitizenFriendlyStatusResponse(BaseModel):
    application_id: str
    scheme_title: str
    current_stage: str
    status: str
    next_action: str
    is_overdue: bool
    days_remaining: Optional[int] = None
    days_overdue: Optional[int] = None
    expected_resolution_date: Optional[str] = None
    simple_explanation: str
    can_file_grievance: bool


class MockStatusUpdateRequest(BaseModel):
    status: str = Field(
        ...,
        description="'draft', 'submitted', 'under_review', 'pending_documents', 'approved', 'rejected', 'grievance_filed'"
    )
    message: Optional[str] = None


# ---------------- Grievance Escalator Schemas ----------------
class GrievanceDraftRequest(BaseModel):
    application_id: str
    citizen_remarks: Optional[str] = None


class GrievanceDraftResponse(BaseModel):
    grievance_id: int
    application_id: str
    citizen_reference_id: str
    scheme_name: str
    submission_date: str
    expected_resolution_date: str
    current_status: str
    days_overdue: int
    draft_text: str
    suggested_official_channels: List[Dict[str, str]]
    disclaimer: str = (
        "This is an automated grievance draft prepared for the citizen. "
        "BenefitBridge does NOT automatically file or dispatch this to government portals. "
        "Please copy this draft and submit it directly through the official CPGRAMS or State CM Helpline portal."
    )


# ---------------- DigiLocker & API Setu Schemas ----------------
class DigiLockerLoginResponse(BaseModel):
    auth_url: str = Field(..., description="Official DigiLocker / Meri Pehchaan OAuth 2.0 authorization URL")
    state: str = Field(..., description="Cryptographically secure CSRF state token")
    status: str = Field(default="success", description="Status string")
    authorization_url: Optional[str] = Field(default="", description="Alias for auth_url")

    def model_post_init(self, __context: Any) -> None:
        if self.auth_url and not self.authorization_url:
            self.authorization_url = self.auth_url
        elif self.authorization_url and not self.auth_url:
            self.auth_url = self.authorization_url


class DigiLockerAuthResponse(DigiLockerLoginResponse):
    pass


class DigiLockerDocumentItem(BaseModel):
    doc_type: str = Field(..., description="Normalized document type code, e.g. 'ration_card', 'income_certificate'")
    doc_name: str = Field(..., description="Display title of the issued certificate")
    issuer: str = Field(..., description="Authentic government issuing authority name")
    uri: str = Field(..., description="Official DigiLocker URI schema string")
    verified: bool = Field(default=False, description="True only when the credential signature has been verified")
    extracted_data: Optional[Dict[str, Any]] = Field(default=None, description="Extracted XML/JSON metadata attributes")
    fetched_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DigiLockerCallbackResponse(BaseModel):
    citizen_id: str = Field(..., description="BenefitBridge Citizen unique identifier")
    full_name: str = Field(..., description="Citizen verified name from DigiLocker")
    digilocker_verified: bool = Field(default=False, description="True only when identity was verified by National SSO")
    verified_documents: List[str] = Field(default_factory=list, description="List of verified document names pulled from DigiLocker")
    eligibility_status: str = Field(default="eligible", description="'eligible', 'partially_eligible', or 'ineligible'")
    application_id: Optional[str] = Field(default=None, description="Generated tracked application token (e.g., APP-XXXXXX)")
    scheme_id: str = Field(..., description="Welfare scheme ID applied for")
    statutory_deadline_days: int = Field(default=30, description="Guaranteed statutory SLA processing days")
    expected_resolution_date: str = Field(default="", description="Target resolution date under citizen charter")
    confirmation_message: str = Field(default="", description="Citizen-friendly feedback explaining the result and SLA guarantee")
    demo_mode: bool = Field(default=False, description="True when this response uses synthetic demonstration data")
    access_token: Optional[str] = Field(default=None, description="Short lived citizen session token")

    # Compatibility fields for legacy and extended API consumers
    status: Optional[str] = Field(default="success", description="'success' or 'ineligible'")
    is_verified: Optional[bool] = Field(default=False, description="True only when DigiLocker verification completed")
    fetched_documents_count: Optional[int] = Field(default=0, description="Number of issued credentials pulled and verified")
    status_message: Optional[str] = Field(default="", description="Detailed status message")
    eligible_schemes_count: Optional[int] = Field(default=0, description="Total matching schemes count")
    documents: Optional[List[DigiLockerDocumentItem]] = Field(default_factory=list, description="List of fetched DigiLocker credentials")

    model_config = ConfigDict(from_attributes=True)


