"""
Configuration and Environment Settings for BenefitBridge.
Loads official API Setu / Meri Pehchaan / DigiLocker OAuth 2.0 parameters.
"""

import os
from pathlib import Path

# Load optional .env file if present
_env_path = Path(__file__).resolve().parent / ".env"
if _env_path.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_path)
    except ImportError:
        pass

IS_SERVERLESS: bool = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))
ENABLE_DEMO_INTEGRATIONS: bool = os.getenv(
    "ENABLE_DEMO_INTEGRATIONS", "false" if IS_SERVERLESS else "true"
).strip().lower() in {"1", "true", "yes", "on"}

# ---------------- DigiLocker & Meri Pehchaan (National SSO) OAuth 2.0 ----------------
DIGILOCKER_CLIENT_ID: str = os.getenv("DIGILOCKER_CLIENT_ID", os.getenv("APISITU_CLIENT_ID", "BB_DEMO_CLIENT_ID"))
DIGILOCKER_CLIENT_SECRET: str = os.getenv("DIGILOCKER_CLIENT_SECRET", os.getenv("APISITU_CLIENT_SECRET", ""))
DIGILOCKER_REDIRECT_URI: str = os.getenv(
    "DIGILOCKER_REDIRECT_URI",
    os.getenv("APISITU_REDIRECT_URI", "http://localhost:8000/auth/digilocker/callback")
)

DIGILOCKER_AUTH_URL: str = os.getenv(
    "DIGILOCKER_AUTH_URL",
    os.getenv("DIGILOCKER_AUTH_ENDPOINT", "https://digilocker.meripehchaan.gov.in/public/oauth2/1/authorize")
)
DIGILOCKER_TOKEN_URL: str = os.getenv(
    "DIGILOCKER_TOKEN_URL",
    os.getenv("DIGILOCKER_TOKEN_ENDPOINT", "https://digilocker.meripehchaan.gov.in/public/oauth2/1/token")
)
DIGILOCKER_ISSUED_URL: str = os.getenv(
    "DIGILOCKER_ISSUED_URL",
    os.getenv("DIGILOCKER_ISSUED_DOCS_ENDPOINT", "https://digilocker.meripehchaan.gov.in/public/oauth2/1/files/issued")
)
DIGILOCKER_FILE_URL: str = os.getenv(
    "DIGILOCKER_FILE_URL",
    os.getenv("DIGILOCKER_PULL_DOC_ENDPOINT", "https://digilocker.meripehchaan.gov.in/public/oauth2/1/file")
)

# Compatibility Aliases
APISITU_CLIENT_ID: str = DIGILOCKER_CLIENT_ID
APISITU_CLIENT_SECRET: str = DIGILOCKER_CLIENT_SECRET
APISITU_REDIRECT_URI: str = DIGILOCKER_REDIRECT_URI
DIGILOCKER_AUTH_ENDPOINT: str = DIGILOCKER_AUTH_URL
DIGILOCKER_TOKEN_ENDPOINT: str = DIGILOCKER_TOKEN_URL
DIGILOCKER_ISSUED_DOCS_ENDPOINT: str = DIGILOCKER_ISSUED_URL
DIGILOCKER_PULL_DOC_ENDPOINT: str = DIGILOCKER_FILE_URL
APISITU_API_KEY: str = os.getenv("APISITU_API_KEY", "")
OAUTH_STATE_COOKIE: str = "benefitbridge_oauth_state"
