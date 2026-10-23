import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from schemas import (
    CitizenProfile,
    SchemeEvaluationResult,
    EligibilityCheckResponse,
    SchemeDetail,
    EligibilityRules,
    DocumentRequirementItem
)

RULES_DIR = Path(__file__).resolve().parent / "rules"


def load_all_scheme_rules() -> Dict[str, dict]:
    """
    Loads all scheme rule JSON files from the rules directory.
    Returns a dictionary mapping scheme_id -> rule dictionary.
    """
    schemes: Dict[str, dict] = {}
    if not RULES_DIR.exists():
        return schemes

    for json_file in sorted(RULES_DIR.glob("*.json")):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                scheme_id = data.get("scheme_id")
                if scheme_id:
                    schemes[scheme_id] = data
        except Exception as e:
            print(f"[RulesEngine] Warning: Failed to parse rule file {json_file}: {e}")
    return schemes


def get_scheme_by_id(scheme_id: str) -> Optional[dict]:
    """Retrieve raw scheme rule dict by scheme_id."""
    schemes = load_all_scheme_rules()
    return schemes.get(scheme_id)


def evaluate_single_scheme(profile: CitizenProfile, rule_data: dict) -> SchemeEvaluationResult:
    """
    Deterministically evaluates a citizen profile against a single scheme rule definition.
    Never uses an LLM for decision making.
    """
    scheme_id = rule_data.get("scheme_id", "unknown")
    scheme_title = rule_data.get("title", "Unknown Scheme")
    rule_version = rule_data.get("rule_version", "v1.0.0")
    portal_url = str(rule_data.get("official_portal_url", "")).replace("https://nsap.nic.in", "https://nsap.dord.gov.in")
    official_source_name = rule_data.get("official_source_name", "Official Government Authority")
    citizen_charter_clause = rule_data.get("citizen_charter_clause", "Statutory Citizens Charter Guarantee")
    rules = rule_data.get("eligibility_rules", {})

    matched_rules: List[str] = []
    failed_rules: List[str] = []
    missing_information: List[str] = []

    # 1. Age Evaluation
    min_age = rules.get("min_age")
    max_age = rules.get("max_age")
    if profile.age is None:
        if min_age is not None or max_age is not None:
            missing_information.append("Age")
    elif min_age is not None and profile.age < min_age:
        failed_rules.append(f"Age requirement not met: age {profile.age} is below minimum required age of {min_age} years.")
    elif max_age is not None and profile.age > max_age:
        failed_rules.append(f"Age requirement not met: age {profile.age} exceeds maximum allowable age of {max_age} years.")
    elif profile.age is not None:
        age_str = f"Age {profile.age} meets criteria"
        if min_age is not None and max_age is not None:
            age_str += f" ({min_age}-{max_age} years)"
        elif min_age is not None:
            age_str += f" (min {min_age} years)"
        matched_rules.append(age_str)

    # 2. Gender Evaluation
    allowed_genders = [g.lower() for g in rules.get("gender", ["all"])]
    if "all" in allowed_genders or "any" in allowed_genders:
        matched_rules.append("Gender: open to all genders")
    elif not profile.gender or profile.gender.lower() == "unknown":
        missing_information.append("Gender")
    elif profile.gender.lower() in allowed_genders:
        matched_rules.append(f"Gender: {profile.gender.capitalize()} matches scheme requirement ({', '.join(allowed_genders)})")
    else:
        failed_rules.append(f"Gender requirement not met: citizen is {profile.gender.capitalize()}, scheme is restricted to {', '.join(allowed_genders)}.")

    # 3. Marital Status Evaluation
    allowed_marital = [m.lower() for m in rules.get("marital_status", ["all"])]
    if "all" in allowed_marital or "any" in allowed_marital:
        matched_rules.append("Marital status: open to all marital statuses")
    elif not profile.marital_status or profile.marital_status.lower() == "unknown":
        missing_information.append("Marital status")
    elif profile.marital_status.lower() in allowed_marital:
        matched_rules.append(f"Marital status: '{profile.marital_status}' matches scheme target group")
    else:
        failed_rules.append(f"Marital status not met: citizen is '{profile.marital_status}', scheme requires {', '.join(allowed_marital)}.")

    # 4. Income Limit Evaluation
    income_limit = rules.get("income_limit")
    if income_limit is None:
        matched_rules.append("Income: no strict income ceiling specified")
    elif profile.annual_income is None:
        missing_information.append("Annual household income")
    elif profile.annual_income <= income_limit:
        matched_rules.append(f"Income: annual income ₹{profile.annual_income:,.0f} is within limit of ₹{income_limit:,.0f}")
    else:
        excess = profile.annual_income - income_limit
        failed_rules.append(f"Income limit exceeded: annual income ₹{profile.annual_income:,.0f} exceeds ₹{income_limit:,.0f} limit (by ₹{excess:,.0f}).")

    # 5. Occupation Evaluation
    allowed_occupations = [o.lower() for o in rules.get("occupation", ["any"])]
    if "any" in allowed_occupations or "all" in allowed_occupations:
        matched_rules.append("Occupation: open to all occupations")
    elif not profile.occupation or profile.occupation.lower() == "unknown":
        missing_information.append("Occupation")
    elif profile.occupation.lower() in allowed_occupations:
        matched_rules.append(f"Occupation: '{profile.occupation}' qualifies under scheme criteria")
    else:
        failed_rules.append(f"Occupation requirement not met: citizen is '{profile.occupation}', scheme specifies {', '.join(allowed_occupations)}.")

    # 6. Disability Status Evaluation
    req_disability = str(rules.get("disability_status", "any")).lower()
    if req_disability in ["any", "all", "none"]:
        matched_rules.append("Disability criteria: non-restrictive")
    else:
        if not profile.disability_status or profile.disability_status.lower() == "unknown":
            missing_information.append("Disability status")
        elif profile.disability_status.lower() in ["none", "no", ""]:
            failed_rules.append("Disability criterion not met: scheme is designated for citizens with documented disability.")
        else:
            matched_rules.append(f"Disability criteria met: {profile.disability_status}")

    # 7. Document Readiness Evaluation
    required_docs = rules.get("required_documents", [])
    available_normalized = {d.lower().strip() for d in profile.available_documents}

    missing_docs: List[str] = []
    doc_info_list = rule_data.get("documents_required", [])
    doc_code_to_name = {d.get("code", ""): d.get("name", d.get("code", "")) for d in doc_info_list}

    for doc_code in required_docs:
        if doc_code.lower() not in available_normalized:
            display_name = doc_code_to_name.get(doc_code, doc_code.replace("_", " ").title())
            missing_docs.append(display_name)

    # Classification Logic
    if len(failed_rules) > 0:
        status = "ineligible"
        reasons = "; ".join(failed_rules)
        explanation = (
            f"You are currently ineligible for {scheme_title} because: {reasons}."
        )
    elif len(missing_docs) > 0 or len(missing_information) > 0:
        pending = []
        if missing_information:
            pending.append("confirm " + ", ".join(missing_information))
        if missing_docs:
            pending.append("arrange " + ", ".join(missing_docs))
        status = "partially_eligible"
        explanation = (
            f"We can’t confirm eligibility for {scheme_title} yet. Please {' and '.join(pending)}."
        )
    else:
        status = "eligible"
        explanation = (
            f"You are fully eligible for {scheme_title}! You meet all criteria "
            f"and have all {len(required_docs)} required documents ready to apply."
        )

    return SchemeEvaluationResult(
        scheme_id=scheme_id,
        scheme_title=scheme_title,
        status=status,
        matched_rules=matched_rules,
        failed_rules=failed_rules,
        missing_documents=missing_docs,
        missing_information=missing_information,
        simple_explanation=explanation,
        rule_version=rule_version,
        official_portal_url=portal_url,
        official_source_name=official_source_name,
        citizen_charter_clause=citizen_charter_clause
    )


def evaluate_eligibility(
    profile: CitizenProfile,
    target_scheme_id: Optional[str] = None
) -> Tuple[List[SchemeEvaluationResult], List[SchemeEvaluationResult], List[SchemeEvaluationResult]]:
    """
    Evaluates profile across schemes.
    Returns: (eligible_schemes, partially_eligible_schemes, ineligible_schemes)
    """
    all_schemes = load_all_scheme_rules()

    if target_scheme_id:
        if target_scheme_id in all_schemes:
            schemes_to_eval = [all_schemes[target_scheme_id]]
        else:
            return ([], [], [])
    else:
        schemes_to_eval = list(all_schemes.values())

    eligible: List[SchemeEvaluationResult] = []
    partially_eligible: List[SchemeEvaluationResult] = []
    ineligible: List[SchemeEvaluationResult] = []

    for rule_data in schemes_to_eval:
        result = evaluate_single_scheme(profile, rule_data)
        if result.status == "eligible":
            eligible.append(result)
        elif result.status == "partially_eligible":
            partially_eligible.append(result)
        else:
            ineligible.append(result)

    return (eligible, partially_eligible, ineligible)


def simplify_explanation_with_llm(text: str) -> str:
    """
    Optional LLM helper strictly used to translate or simplify explanations
    into conversational language. It NEVER alters eligibility decisions or outcomes.
    If no LLM API key or network fails, gracefully returns the original deterministic text.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return text

    try:
        import httpx
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an assistant for Indian welfare applicants. "
                        "Rewrite the given scheme eligibility explanation into friendly, "
                        "clear 5th-grade language. Do not change whether the applicant is eligible or not. "
                        "Keep it concise (1-2 sentences)."
                    )
                },
                {"role": "user", "content": text}
            ],
            "temperature": 0.2,
            "max_tokens": 120
        }
        with httpx.Client(timeout=4.0) as client:
            resp = client.post(f"{base_url}/chat/completions", headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                simplified = data["choices"][0]["message"]["content"].strip()
                if simplified:
                    return simplified
    except Exception as e:
        print(f"[RulesEngine] LLM explanation simplification skipped: {e}")

    return text
