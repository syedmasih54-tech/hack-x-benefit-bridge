import io
import os
import re
import shutil
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image
import pytesseract

from schemas import ExtractedFields, DocumentScanResponse

# Locate Tesseract OCR binary across common environments
POSSIBLE_TESSERACT_PATHS = [
    os.getenv("TESSERACT_CMD"),
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
    "/usr/bin/tesseract",
    "/usr/local/bin/tesseract",
    "/opt/homebrew/bin/tesseract",
]

TESSERACT_AVAILABLE = False
for path in POSSIBLE_TESSERACT_PATHS:
    if path and (shutil.which(path) or os.path.isfile(path)):
        pytesseract.pytesseract.tesseract_cmd = path
        TESSERACT_AVAILABLE = True
        break

if not TESSERACT_AVAILABLE and shutil.which("tesseract"):
    TESSERACT_AVAILABLE = True


# RegEx patterns for Indian public welfare documents
NAME_PATTERNS = [
    re.compile(r"(?:Name|Beneficiary Name|Card Holder|Card Holder Name|Account Holder|Account Holder Name|नाम)\s*[:\-]\s*([A-Za-z\t \.\'\-]+)", re.IGNORECASE),
    re.compile(r"(?:Name of Beneficiary|Member Name|Head of Family|Head of Household)\s*[:\-]\s*([A-Za-z\t \.\'\-]+)", re.IGNORECASE),
    re.compile(r"\b(?:Smt\.|Shri|Kumari|Dr\.)\s+([A-Za-z\t \.\'\-]+)", re.IGNORECASE),
    re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b"),  # General capitalized multi-word name
]

DOB_PATTERNS = [
    re.compile(r"(?:DOB|Date of Birth|D\.O\.B|जन्म तिथि)\s*[:\-]\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})", re.IGNORECASE),
    re.compile(r"(?:DOB|Date of Birth)\s*[:\-]\s*(\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2})", re.IGNORECASE),
    re.compile(r"\b(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.](?:19|20)\d{2})\b"),
]

ACCOUNT_PATTERNS = [
    re.compile(r"(?:A\/C No|Account No|Account Number|खाता संख्या)\s*[:\-]\s*(\d{9,18})", re.IGNORECASE),
    re.compile(r"(?:SB A\/C|Account)\s*[:\-]\s*(\d{9,18})", re.IGNORECASE),
    re.compile(r"\b(\d{11,16})\b"),
]

IFSC_PATTERN = re.compile(r"\b([A-Z]{4}0[A-Z0-9]{6})\b")
RATION_CARD_NUM_PATTERN = re.compile(r"(?:Ration Card No|RC No|NFSA ID)\s*[:\-]\s*([A-Z0-9\-]+)", re.IGNORECASE)

# Privacy protection: Aadhaar regex (3 blocks of 4 digits) - Must never be logged or retained
AADHAAR_PATTERN = re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b")


def sanitize_text_for_privacy(text: str) -> str:
    """Masks any potential 12-digit Aadhaar patterns to strictly comply with Indian privacy laws."""
    return AADHAAR_PATTERN.sub("[REDACTED-AADHAAR-PROTECTED]", text)


def detect_document_type(text: str) -> str:
    """Classifies document type based on key Indian governance keywords."""
    lower_text = text.lower()
    if any(k in lower_text for k in ["ration card", "food security", "nfsa", "antyodaya", "bpl card", "rashan"]):
        return "ration_card"
    if any(k in lower_text for k in ["passbook", "bank of", "state bank", "ifsc", "savings account", "account number", "cif"]):
        return "bank_passbook"
    if any(k in lower_text for k in ["income certificate", "annual income", "tehsildar", "revenue department", "tahsildar"]):
        return "income_certificate"
    if any(k in lower_text for k in ["death certificate", "deceased", "cremation", "date of death"]):
        return "death_certificate"
    if any(k in lower_text for k in ["caste certificate", "scheduled caste", "scheduled tribe", "obc certificate"]):
        return "caste_certificate"
    if any(k in lower_text for k in ["scholarship", "bonafide", "student", "roll number", "institution"]):
        return "bonafide_certificate"
    return "general_welfare_document"


def extract_fields_from_text(text: str, doc_type: str) -> Tuple[ExtractedFields, List[str]]:
    """Extracts structured key-value fields from raw OCR text with fallback patterns and warnings."""
    warnings: List[str] = []
    sanitized = sanitize_text_for_privacy(text)

    # 1. Full Name Extraction
    full_name = None
    for pattern in NAME_PATTERNS:
        match = pattern.search(sanitized)
        if match:
            candidate = match.group(1).strip()
            # Basic sanity check: filter out common document headers falsely matching names
            if len(candidate) > 2 and not any(h in candidate.lower() for h in ["government", "department", "india", "ration", "bank", "state"]):
                full_name = candidate
                break

    if not full_name:
        warnings.append("Could not automatically locate beneficiary full name; manual verification recommended.")

    # 2. Date of Birth Extraction
    dob = None
    for pattern in DOB_PATTERNS:
        match = pattern.search(sanitized)
        if match:
            dob = match.group(1).strip()
            break

    # 3. Account Number Extraction
    account_num = None
    for pattern in ACCOUNT_PATTERNS:
        match = pattern.search(sanitized)
        if match:
            account_num = match.group(1).strip()
            break

    # 4. IFSC Code Extraction
    ifsc_match = IFSC_PATTERN.search(sanitized)
    ifsc_code = ifsc_match.group(1) if ifsc_match else None

    # Contextual warnings
    if doc_type == "bank_passbook" and not account_num:
        warnings.append("Bank passbook detected but account number was unclear or unreadable.")
    if doc_type == "bank_passbook" and not ifsc_code:
        warnings.append("IFSC code not found; ensure top section of passbook is clearly visible.")

    extracted = ExtractedFields(
        full_name=full_name,
        date_of_birth=dob,
        account_number=account_num,
        document_type=doc_type,
        ifsc_code=ifsc_code,
    )
    return extracted, warnings


def calculate_ocr_confidence(ocr_data: Optional[dict], raw_text: str) -> Tuple[float, str, bool]:
    """
    Computes an average confidence score (0.0 to 1.0) and flag if manual verification is required.
    """
    if ocr_data and "conf" in ocr_data:
        confs = [c for c in ocr_data["conf"] if isinstance(c, (int, float)) and c >= 0]
        if confs:
            avg_conf = sum(confs) / (len(confs) * 100.0)
            avg_conf = max(0.0, min(1.0, avg_conf))
        else:
            avg_conf = 0.5
    else:
        # Fallback heuristic based on text length and structured token presence
        if len(raw_text.strip()) > 80:
            avg_conf = 0.85
        elif len(raw_text.strip()) > 30:
            avg_conf = 0.70
        else:
            avg_conf = 0.35

    if avg_conf >= 0.80:
        indicator = "HIGH"
        manual_verification = False
    elif avg_conf >= 0.60:
        indicator = "MEDIUM"
        manual_verification = False
    else:
        indicator = "LOW"
        manual_verification = True

    return avg_conf, indicator, manual_verification


def process_document_image(image_bytes: bytes, filename: Optional[str] = None) -> DocumentScanResponse:
    """
    In-memory image processing using PIL and pytesseract.
    Never stores uploaded image on disk (preserves citizen data privacy).
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        if image.width * image.height > 30_000_000:
            raise ValueError("Image dimensions are too large. Please use an image below 30 megapixels.")
        # Convert image to RGB if needed
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")
    except Exception as e:
        raise ValueError(f"Invalid image format or corrupted image file: {str(e)}")

    raw_text = ""
    ocr_data = None

    if TESSERACT_AVAILABLE:
        try:
            raw_text = pytesseract.image_to_string(image)
            ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        except Exception as e:
            print(f"[OCRService] Pytesseract execution warning: {e}. Falling back to image text recovery.")

    sanitized_text = sanitize_text_for_privacy(raw_text)
    doc_type = detect_document_type(sanitized_text)
    extracted, warnings = extract_fields_from_text(sanitized_text, doc_type)
    confidence, indicator, manual_req = calculate_ocr_confidence(ocr_data, sanitized_text)

    if not sanitized_text.strip():
        warnings.append("No text could be read. Confirm that OCR is installed or upload a clearer image.")
        manual_req = True

    if manual_req and "Low OCR confidence: manual verification required" not in warnings:
        warnings.append("Low OCR confidence: image quality or lighting may be low. Manual verification required.")

    return DocumentScanResponse(
        document_type=doc_type,
        extracted_fields=extracted,
        raw_ocr_text=sanitized_text.strip(),
        confidence_score=round(confidence, 2),
        confidence_indicator=indicator,
        warnings=warnings,
        manual_verification_required=manual_req
    )
