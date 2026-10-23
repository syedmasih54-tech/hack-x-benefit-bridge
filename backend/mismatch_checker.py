import re
from difflib import SequenceMatcher
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
# pyrefly: ignore[missing-source-for-stubs]
from dateutil import parser as date_parser

from schemas import DocumentCompareResponse

HONORIFICS = ["smt", "smt.", "shri", "shri.", "km.", "mrs", "mr", "dr", "dr."]


def clean_name(name: Optional[str]) -> str:
    """Normalizes Indian names by removing common honorifics, punctuation, and extra whitespace."""
    if not name:
        return ""
    cleaned = name.lower()
    for h in HONORIFICS:
        cleaned = re.sub(rf"\b{re.escape(h)}\b", "", cleaned)
    cleaned = re.sub(r"[^\w\s]|[\d_]", " ", cleaned, flags=re.UNICODE)
    tokens = [t.strip() for t in cleaned.split() if t.strip()]
    return " ".join(tokens)


def phonetic_phoneme_normalize(text: str) -> str:
    """
    Normalizes common Indian English transliteration variations:
    - 'th' -> 't' (e.g., Sunitha -> Sunita)
    - 'ee' -> 'i' (e.g., Preeti -> Priti)
    - 'oo' -> 'u' (e.g., Pooja -> Puja)
    - 'w' -> 'v' (e.g., Shweta -> Shveta)
    - double consonants -> single consonant
    """
    s = text.lower()
    s = s.replace("th", "t")
    s = s.replace("ee", "i")
    s = s.replace("oo", "u")
    s = s.replace("w", "v")
    # Collapse double characters (e.g., mittal -> mital)
    s = re.sub(r"(.)\1+", r"\1", s)
    return s


def compute_name_similarity(name1: str, name2: str) -> Tuple[float, str]:
    """
    Computes similarity ratio and classified status between two Indian names.
    Returns: (similarity_score, match_status)
    """
    c1 = clean_name(name1)
    c2 = clean_name(name2)

    if not c1 or not c2:
        return 0.0, "missing_field"

    if c1 == c2:
        return 1.0, "exact_match"

    # Phonetic transliteration check (very common in Indian certificates)
    p1 = phonetic_phoneme_normalize(c1)
    p2 = phonetic_phoneme_normalize(c2)
    if p1 == p2:
        return 0.95, "likely_match_with_spelling_variation"

    # Sequence matcher on cleaned strings
    ratio = SequenceMatcher(None, c1, c2).ratio()

    # Also check token-sorted match (e.g. "Devi Sunita" vs "Sunita Devi")
    tokens1 = sorted(c1.split())
    tokens2 = sorted(c2.split())
    if tokens1 == tokens2:
        return 0.92, "likely_match_with_spelling_variation"

    sorted_ratio = SequenceMatcher(None, " ".join(tokens1), " ".join(tokens2)).ratio()
    best_score = max(ratio, sorted_ratio)

    if best_score >= 0.78:
        return round(best_score, 2), "likely_match_with_spelling_variation"
    else:
        return round(best_score, 2), "mismatch"


def compare_date_strings(dob1: Optional[str], dob2: Optional[str]) -> Tuple[List[str], List[str]]:
    """
    Compares two date strings across different formats (DD/MM/YYYY, YYYY-MM-DD, etc.).
    Returns (mismatches, notes).
    """
    mismatches: List[str] = []
    notes: List[str] = []

    if not dob1 or not dob2:
        return mismatches, notes

    try:
        # fuzzy parse with day-first preference typical in India
        d1 = date_parser.parse(dob1, dayfirst=True)
        d2 = date_parser.parse(dob2, dayfirst=True)

        if d1.date() == d2.date():
            if dob1.strip() != dob2.strip():
                notes.append(
                    f"Date of birth represents the same calendar date ({d1.strftime('%d-%b-%Y')}) "
                    f"presented in different formats: '{dob1}' vs '{dob2}'."
                )
        else:
            mismatches.append(
                f"Date of birth mismatch: Document 1 indicates '{dob1}' ({d1.strftime('%d-%b-%Y')}) "
                f"while Document 2 indicates '{dob2}' ({d2.strftime('%d-%b-%Y')})."
            )
    except Exception:
        # Fallback raw string comparison if unparseable
        if dob1.strip().lower() != dob2.strip().lower():
            mismatches.append(f"Date fields differ textually: '{dob1}' vs '{dob2}'.")

    return mismatches, notes


def compare_documents(
    doc1_fields: Dict[str, Any],
    doc2_fields: Dict[str, Any],
    doc1_type: str = "ration_card",
    doc2_type: str = "bank_passbook"
) -> DocumentCompareResponse:
    """
    Deeply compares extracted fields between two citizen welfare documents.
    Generates non-intimidating warnings and actionable citizen recommendations.
    Never approves or rejects the citizen.
    """
    name1 = doc1_fields.get("full_name")
    name2 = doc2_fields.get("full_name")
    dob1 = doc1_fields.get("date_of_birth")
    dob2 = doc2_fields.get("date_of_birth")

    score, status = compute_name_similarity(name1 or "", name2 or "")

    mismatches: List[str] = []
    recommendations: List[str] = []
    requires_affidavit_or_update = False

    # Name evaluation
    if status == "exact_match":
        # No warning needed for exact match
        pass
    elif status == "likely_match_with_spelling_variation":
        requires_affidavit_or_update = True
        mismatches.append(
            f"Spelling variation detected: {doc1_type.replace('_', ' ').title()} displays '{name1}', "
            f"whereas {doc2_type.replace('_', ' ').title()} displays '{name2}'."
        )
        recommendations.append(
            "Direct Benefit Transfer (DBT) bank accounts require names to closely match. "
            "Please ask your bank branch to update your passbook to match your primary ID, "
            "or carry a standard 1-page name discrepancy affidavit from a local notary."
        )
    elif status == "mismatch":
        requires_affidavit_or_update = True
        mismatches.append(
            f"Significant name discrepancy: '{name1}' vs '{name2}'. "
            f"These appear to be distinct names across {doc1_type} and {doc2_type}."
        )
        recommendations.append(
            "Verify that both documents belong to the same citizen before submitting your welfare application. "
            "An application submitted with conflicting names may be put on hold by verification officers."
        )
    elif status == "missing_field":
        missing_doc = doc1_type if not name1 else doc2_type
        mismatches.append(f"Beneficiary name could not be extracted from {missing_doc.replace('_', ' ')}.")
        recommendations.append("Ensure clear photo scans where all printed letters are legible.")

    # DOB evaluation
    date_mismatches, date_notes = compare_date_strings(dob1, dob2)
    mismatches.extend(date_mismatches)
    if date_mismatches:
        requires_affidavit_or_update = True
        recommendations.append(
            "Ensure supporting age proof (e.g., Voter ID or School Certificate) resolves the date of birth variance."
        )

    # Missing mandatory bank fields
    if doc2_type == "bank_passbook":
        acc = doc2_fields.get("account_number")
        if not acc:
            mismatches.append("Bank passbook is missing an extracted account number.")
            recommendations.append("Re-upload a clearer picture showing the printed Account Number.")

    # Citizen guidance warning
    if status == "exact_match" and not mismatches:
        citizen_warning = "All key identity fields match cleanly across both documents! You are ready to proceed."
    elif status == "likely_match_with_spelling_variation":
        citizen_warning = (
            "Minor spelling variation noted. BenefitBridge does NOT reject your application, "
            "but resolving this spelling difference now will prevent DBT bank transfer delays later."
        )
    else:
        citizen_warning = (
            "Document fields show noticeable differences. Please review the recommendations below "
            "to ensure smooth processing by government verification teams."
        )

    return DocumentCompareResponse(
        name_match_status=status,
        name_document_1=name1,
        name_document_2=name2,
        similarity_score=score,
        mismatches_detected=mismatches,
        recommendations=recommendations,
        citizen_warning=citizen_warning,
        requires_affidavit_or_update=requires_affidavit_or_update
    )
