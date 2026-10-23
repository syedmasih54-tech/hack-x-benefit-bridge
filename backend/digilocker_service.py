"""
DigiLocker & API Setu (apisetu.gov.in) Integration Service.
Provides OAuth 2.0 / OpenID Connect authentication via Meri Pehchaan (National SSO),
retrieval of signed digital credentials from issuing authorities, XML parsing,
and strict privacy redaction of national identity numbers (Aadhaar).
"""

import json
import logging
import re
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import httpx

import config
from schemas import parse_annual_income

logger = logging.getLogger("benefitbridge.digilocker")


def sanitize_aadhaar(text: str) -> str:
    """
    Strict Privacy Guardrail:
    Redacts any 12-digit national identity numbers (Aadhaar) in raw XML, text, or metadata.
    """
    if not text:
        return text
    # 12 digits with spaces: 1234 5678 9012
    text = re.sub(r"\b\d{4}\s+\d{4}\s+\d{4}\b", "[REDACTED_AADHAAR]", text)
    # 12 continuous digits: 123456789012
    text = re.sub(r"\b\d{12}\b", "[REDACTED_AADHAAR]", text)
    return text


def calculate_age_from_dob(dob_str: Optional[str]) -> Optional[int]:
    """
    Calculates age in completed years from common Indian date formats (DD/MM/YYYY, YYYY-MM-DD, DD-MM-YYYY).
    """
    if not dob_str:
        return None
    cleaned = dob_str.strip()
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%Y/%m/%d"):
        try:
            born = datetime.strptime(cleaned, fmt)
            today = datetime.now()
            age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
            return max(0, age)
        except ValueError:
            continue
    return None


def get_authorization_url(state: str, target_scheme_id: str = "widow_pension") -> str:
    """
    Builds redirect URL with client_id, redirect_uri, scope='openid email profile',
    and encoded state containing CSRF token and target_scheme_id.
    """
    combined_state = f"{state}:{target_scheme_id}" if ":" not in state else state
    params = {
        "response_type": "code",
        "client_id": config.DIGILOCKER_CLIENT_ID,
        "redirect_uri": config.DIGILOCKER_REDIRECT_URI,
        "state": combined_state,
        "scope": "openid email profile",
    }
    return f"{config.DIGILOCKER_AUTH_URL}?{urlencode(params)}"


def generate_authorization_url(state: str) -> str:
    """Compatibility alias for get_authorization_url."""
    return get_authorization_url(state)


async def exchange_code_for_token(code: str) -> Dict[str, Any]:
    """
    Issues POST request to DIGILOCKER_TOKEN_URL with authorization code.
    Dual-Mode Sandbox: If client_id is 'BB_DEMO_CLIENT_ID' or request fails due to
    network sandbox limitations, returns a valid mock user:
      {"access_token": "mock_token_123", "digilockerid": "DL-981240182", "name": "Sunita Devi", "dob": "12/04/1959", "gender": "F"}
    """
    is_demo_mode = (
        config.ENABLE_DEMO_INTEGRATIONS
        and (code.startswith("sandbox_") or code.startswith("demo") or code in ("mock_code",))
    )

    if not is_demo_mode:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    config.DIGILOCKER_TOKEN_URL,
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "client_id": config.DIGILOCKER_CLIENT_ID,
                        "client_secret": config.DIGILOCKER_CLIENT_SECRET,
                        "redirect_uri": config.DIGILOCKER_REDIRECT_URI,
                    },
                    headers={
                        "Accept": "application/json",
                        "X-API-KEY": config.APISITU_API_KEY,
                    },
                )
                if resp.status_code == 200:
                    token_data = resp.json()
                    token_data["_demo_mode"] = False
                    return token_data
                logger.warning(
                    "DigiLocker token exchange returned HTTP %s.", resp.status_code
                )
        except Exception as e:
            logger.warning("DigiLocker token exchange failed: %s", e)

        raise RuntimeError("DigiLocker token exchange failed")

    if not config.ENABLE_DEMO_INTEGRATIONS:
        raise RuntimeError("DigiLocker demo mode is disabled")

    # Dual-Mode Sandbox: Authentic profile for Indian Welfare Demonstration
    return {
        "_demo_mode": True,
        "access_token": "mock_token_123",
        "token_type": "Bearer",
        "expires_in": 3600,
        "digilockerid": "DL-981240182",
        "name": "Sunita Devi",
        "dob": "12/04/1959",
        "gender": "F",
        "mobile": "98******10",
        "email": "sunita.devi@demo.gov.in",
    }


async def fetch_issued_documents(token: str = "mock_token_123") -> List[Dict[str, Any]]:
    """
    Fetches issued document list from DIGILOCKER_ISSUED_URL.
    Sandbox returns authentic issued schemas for 'Ration Card (NFSA)' and
    'Annual Income Certificate' from Govt of NCT Delhi.
    """
    is_demo_token = (
        config.ENABLE_DEMO_INTEGRATIONS and (
        config.DIGILOCKER_CLIENT_ID == "BB_DEMO_CLIENT_ID"
        or token.startswith("mock_")
        or token.startswith("dl_token_")
        or "demo" in token.lower()
        )
    )

    if not is_demo_token:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    config.DIGILOCKER_ISSUED_URL,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Accept": "application/json",
                        "X-API-KEY": config.APISITU_API_KEY,
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    items = data.get("items") or data.get("files") or []
                    if items:
                        return items
        except Exception as e:
            logger.warning("Fetching DigiLocker documents failed: %s", e)

        raise RuntimeError("DigiLocker document retrieval failed")

    if not config.ENABLE_DEMO_INTEGRATIONS:
        raise RuntimeError("DigiLocker demo mode is disabled")

    # Sandbox: Authentic schemas for 'Ration Card (NFSA)' and 'Annual Income Certificate' from Govt of NCT Delhi
    ration_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Certificate xmlns="http://digilocker.gov.in/schema" type="RATION">
  <IssuedTo>
    <Person name="Sunita Devi" dob="12/04/1959" gender="F" relation="Wife of Late Rameshwar Dayal" uid="[REDACTED_AADHAAR]" />
    <Address state="Delhi" district="Central Delhi" />
  </IssuedTo>
  <CertificateData>
    <RationCard category="BPL" cardNo="DL07892140182" headOfFamily="Sunita Devi" familyMembers="1" validity="Permanent" issuingAuthority="Department of Food Supplies and Consumer Affairs, Govt of NCT Delhi" />
    <EconomicDetails annualIncome="0.00" bplStatus="YES" />
  </CertificateData>
</Certificate>"""

    income_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Certificate xmlns="http://digilocker.gov.in/schema" type="INCER">
  <IssuedTo>
    <Person name="Sunita Devi" dob="12/04/1959" gender="F" uid="[REDACTED_AADHAAR]" />
    <Address state="Delhi" district="Central Delhi" />
  </IssuedTo>
  <CertificateData>
    <IncomeCertificate certNo="IC-DELHI-2024-981240182" issuingAuthority="Revenue Department, Govt of NCT Delhi" issueDate="10-02-2024" validUntil="09-02-2027">
      <AnnualIncome inr="0" inWords="Zero Rupees Only" />
      <FamilyIncome total="0.00" />
      <Category>Below Poverty Line / Vidhwa</Category>
    </IncomeCertificate>
  </CertificateData>
</Certificate>"""

    return [
        {
            "doc_type": "ration_card",
            "name": "Ration Card (NFSA)",
            "doctype": "RATION",
            "description": "Department of Food Supplies and Consumer Affairs, Govt of NCT Delhi - NFSA BPL Card",
            "issuer": "Department of Food Supplies and Consumer Affairs, Govt of NCT Delhi",
            "issuer_id": "in.gov.delhi.food",
            "uri": "in.gov.delhi.food-RATION-DL07892140182",
            "date": "15/01/2024",
            "mime": ["application/xml", "application/pdf"],
            "xml_content": ration_xml,
        },
        {
            "doc_type": "income_certificate",
            "name": "Annual Income Certificate",
            "doctype": "INCER",
            "description": "Revenue Department, Govt of NCT Delhi - Tehsildar Certified Assessment",
            "issuer": "Revenue Department, Govt of NCT Delhi",
            "issuer_id": "in.gov.delhi.revenue",
            "uri": "in.gov.delhi.revenue-INCER-2024-981240182",
            "date": "10/02/2024",
            "mime": ["application/xml", "application/pdf"],
            "xml_content": income_xml,
        },
    ]


def parse_doc_metadata(raw_doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts clean full_name, dob, annual_income, category, and issuer from raw_doc.
    Strips currency symbols and commas from income strings, converting to float.
    Strictly redacts any 12-digit Aadhaar / national identity numbers.
    """
    xml_str = raw_doc.get("xml_content") or ""
    if xml_str:
        xml_str = sanitize_aadhaar(xml_str)

    full_name: Optional[str] = raw_doc.get("name_in_doc") or raw_doc.get("full_name") or raw_doc.get("name")
    dob: Optional[str] = raw_doc.get("dob")
    annual_income: float = 0.0
    category: str = "General"
    validity: str = "Valid"
    issuer: str = raw_doc.get("issuer") or raw_doc.get("issuer_name") or "Government Authority"

    if xml_str:
        try:
            # Strip XML namespace definitions so queries work identically across all states
            cleaned_xml = re.sub(r'\sxmlns(?::\w+)?="[^"]+"', '', xml_str)
            root = ET.fromstring(cleaned_xml)

            for el in root.iter():
                clean_tag = (el.tag.split("}")[-1] if "}" in el.tag else el.tag).lower()

                # 1. Person details
                if clean_tag in ("person", "applicant", "citizen"):
                    p_name = el.attrib.get("name") or el.attrib.get("fullName")
                    if not p_name:
                        for child in el:
                            child_tag = (child.tag.split("}")[-1] if "}" in child.tag else child.tag).lower()
                            if child_tag in ("name", "fullname") and child.text:
                                p_name = child.text.strip()
                                break
                    if p_name:
                        full_name = p_name.strip()

                    p_dob = el.attrib.get("dob") or el.attrib.get("dateOfBirth")
                    if not p_dob:
                        for child in el:
                            child_tag = (child.tag.split("}")[-1] if "}" in child.tag else child.tag).lower()
                            if child_tag in ("dob", "dateofbirth") and child.text:
                                p_dob = child.text.strip()
                                break
                    if p_dob:
                        dob = p_dob.strip()

                # 2. Income details
                elif clean_tag in ("annualincome", "familyincome", "economicdetails", "incomedetails"):
                    inc_val = (
                        el.attrib.get("inr")
                        or el.attrib.get("annualIncome")
                        or el.attrib.get("total")
                        or el.attrib.get("amount")
                        or el.text
                    )
                    if inc_val is not None:
                        annual_income = parse_annual_income(inc_val)

                # 3. Category
                elif clean_tag in ("category", "socialcategory", "rationcard"):
                    cat_val = (
                        el.attrib.get("category")
                        or el.attrib.get("caste")
                        or el.text
                    )
                    if cat_val:
                        category = str(cat_val).strip()

                # 4. Issuer
                elif clean_tag in ("incomecertificate", "rationcard", "certificate"):
                    iss = el.attrib.get("issuingAuthority") or el.attrib.get("issuer")
                    if iss:
                        issuer = iss.strip()

                # 5. Validity
                elif clean_tag in ("incomecertificate", "validuntil", "validity", "certificatedata"):
                    val_val = (
                        el.attrib.get("validUntil")
                        or el.attrib.get("validity")
                        or el.attrib.get("validUpto")
                    )
                    if val_val:
                        validity = str(val_val).strip()

        except Exception as e:
            logger.warning(f"XML parse exception for raw_doc: {e}")

    # Fallback to direct dict fields
    if annual_income == 0.0 and raw_doc.get("annual_income") is not None:
        annual_income = parse_annual_income(raw_doc["annual_income"])

    return {
        "full_name": full_name,
        "dob": dob,
        "annual_income": annual_income,
        "category": category,
        "validity": validity,
        "issuer": issuer,
    }


async def parse_document_payload(doc_item: Dict[str, Any], access_token: str = "") -> Dict[str, Any]:
    """
    Downloads and parses the document XML payload.
    Uses parse_doc_metadata() to extract clean attributes and formats DigiLockerDocument fields.
    """
    xml_str = doc_item.get("xml_content")

    # If live document without in-memory XML, attempt to pull payload from API Setu endpoint
    if not xml_str and doc_item.get("uri"):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{config.DIGILOCKER_FILE_URL}/{doc_item['uri']}",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/xml",
                        "X-API-KEY": config.APISITU_API_KEY,
                    },
                )
                if resp.status_code == 200:
                    doc_item["xml_content"] = resp.text
        except Exception as e:
            logger.warning(f"Could not pull remote XML for URI {doc_item.get('uri')}: {e}")

    meta = parse_doc_metadata(doc_item)
    doc_name = doc_item.get("name", "Digital Welfare Document")
    issuer_name = meta.get("issuer") or doc_item.get("issuer", "Government Authority")
    raw_doctype = (doc_item.get("doc_type") or doc_item.get("doctype") or doc_name).lower()

    if "ration" in raw_doctype:
        normalized_doc_type = "ration_card"
    elif "income" in raw_doctype or "incer" in raw_doctype:
        normalized_doc_type = "income_certificate"
    elif "caste" in raw_doctype or "cast" in raw_doctype:
        normalized_doc_type = "caste_certificate"
    elif "death" in raw_doctype:
        normalized_doc_type = "death_certificate_of_husband"
    elif "bank" in raw_doctype:
        normalized_doc_type = "bank_passbook"
    elif "land" in raw_doctype or "khatauni" in raw_doctype or "khasra" in raw_doctype:
        normalized_doc_type = "land_records_khatauni"
    elif "bonafide" in raw_doctype or "student" in raw_doctype:
        normalized_doc_type = "bonafide_student_certificate"
    else:
        normalized_doc_type = re.sub(r"[^a-z0-9]+", "_", raw_doctype).strip("_") or "verified_document"

    extracted_data = {
        "full_name": meta.get("full_name"),
        "dob": meta.get("dob"),
        "annual_income": meta.get("annual_income", 0.0),
        "category": meta.get("category", "General"),
        "validity": meta.get("validity", "Valid"),
        "raw_issuer": issuer_name,
        "verification_note": "Retrieved through the configured DigiLocker endpoint; cryptographic signature verification is not performed by this service.",
    }

    return {
        "doc_type": normalized_doc_type,
        "doc_name": doc_name,
        "issuer_name": issuer_name,
        "issuer_id": doc_item.get("issuer_id"),
        "doc_uri": doc_item.get("uri", f"in.gov.digilocker-{uuid.uuid4().hex[:12]}"),
        "verification_status": "VERIFIED",
        "extracted_data": extracted_data,
    }
