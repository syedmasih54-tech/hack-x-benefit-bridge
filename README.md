
# BenefitBridge 🇮🇳 (Hack X)
### *Citizen-Side Welfare Navigator & Verification Intelligence Layer for India*

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.0+-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-8.0+-646CFF.svg?logo=vite&logoColor=white)](https://vitejs.dev)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-4.0+-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00.svg)](https://www.sqlalchemy.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 📖 Overview

Welfare delivery in India faces a critical **last-mile navigation challenge**:
- **Opaque scheme rules**: Millions of eligible citizens struggle to decipher complex eligibility criteria across central and state welfare departments.
- **Pre-submission spelling discrepancies**: Subtle variations (e.g. *Sunita* vs *Sunitha*, *Choudhary* vs *Chaudhary*) across Aadhaar, Ration Cards, and Bank Passbooks trigger Direct Benefit Transfer (DBT) rejection months down the line.
- **Lack of tracking visibility**: Citizens receive cryptic bureaucratic status codes without insight into statutory Service Level Agreements (SLAs).
- **Enforcement hurdles**: When statutory deadlines elapse, citizens lack structured tools to draft legal grievances for CPGRAMS and State CM Helplines.

**BenefitBridge** serves as an intelligent assistance, preparation, and transparency layer for citizens — bridging the gap before final submission to official government portals.

> [!IMPORTANT]
> **What BenefitBridge Does NOT Do:**  
> BenefitBridge does **NOT** replace official government portals, does **NOT** automatically submit applications without citizen consent, and does **NOT** make final statutory benefit sanction determinations. It is an empathetic preparatory, verification, and transparency layer.

---

## 🏛️ System Architecture

```
                                  +------------------------------------+
                                  |   Frontend (React 19 / Vite / GSAP)|
                                  |         http://127.0.0.1:5173      |
                                  +------------------+-----------------+
                                                     | REST API / JSON
                                                     v
+---------------------------------------------------------------------------------------------------+
|                                  FastAPI Backend (Port 8000)                                       |
|                                                                                                   |
|   GET  /schemes                  POST /eligibility/check          POST /documents/scan            |
|   GET  /schemes/{id}             (Deterministic Rules Engine)     POST /documents/compare         |
|   POST /schemes/sync-live-data                                    (Phonetic Indian OCR Doctor)    |
|                                                                                                   |
|   POST /applications             GET  /applications/{id}/status   POST /grievances/draft          |
|   (Tracker Service)              (SLA Citizen Tracker)            (CPGRAMS Legal Escalator)       |
|                                                                                                   |
|   POST /voice/intake             POST /voice/apply-scheme         GET  /auth/digilocker/*         |
|   (Bilingual Voice Intake)       (Audio Speech Normalizer)        (Meri Pehchaan SSO / API Setu)  |
+---------------------------------------------------------------------------------------------------+
       |                                |                                   |
       v                                v                                   v
+------------------+         +---------------------+              +--------------------+
|  Rules Engine    |         |  OCR & Match Doctor |              | SQLite Database    |
|  rules/*.json    |         |  - In-memory buffer |              | SQLAlchemy 2.0     |
|  - widow_pension |         |  - Redaction filter |              | - citizens         |
|  - old_age       |         |  - Levenshtein /    |              | - schemes          |
|  - scholarship   |         |    Phonetic matcher |              | - applications     |
|  - kisan_yojna   |         +---------------------+              | - app_events       |
|  - family_benefit|                                              | - document_checks  |
+------------------+                                              | - grievances       |
                                                                  | - digilocker_docs  |
                                                                  +--------------------+
```

---

## ✨ Key Features

1. **Deterministic Scheme Discovery**:
   - Zero hallucination: Evaluates applicant age, income, caste, landholding, and disability status against versioned scheme rules.
   - Highlights matching conditions, missing requirements, and specific clauses under Citizen Charters.

2. **Pre-Application Document Doctor**:
   - In-memory OCR scanning of Ration Cards, Passbooks, and Certificates.
   - Indian phonetic and transliteration discrepancy analyzer (e.g., *Devi* vs *D/O*, *Smt* prefix stripping, *th* $\leftrightarrow$ *t*).
   - Generates empathetic advice preventing DBT failure rather than harsh rejections.

3. **Privacy & DPDPA Compliance**:
   - Document images are processed strictly in-memory and discarded immediately upon response delivery.
   - Automatic 12-digit Aadhaar regex scrubber replaces sequences with `[REDACTED-AADHAAR-PROTECTED]`.
   - Never stores sensitive PII without explicit consent gates.

4. **SLA Tracker & CPGRAMS Grievance Escalator**:
   - Translates opaque status codes into plain-language citizen milestones.
   - Calculates statutory deadlines under the Right to Public Services Act.
   - Automatically drafts formal, legally structured CPGRAMS/CM Helpline petitions when applications become overdue.

5. **DigiLocker & Meri Pehchaan Integration**:
   - Seamless OAuth flow fetching verified government credentials (Ration Card, Income Certificate).

6. **Bilingual Voice Intake**:
   - Voice-guided workflow in Hindi and English with intelligent entity extraction.

---

## ☁️ 1-Click Deployment to Vercel

BenefitBridge is fully pre-configured for seamless serverless full-stack deployment on **Vercel** with zero manual server configuration.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fsyedmasih54-tech%2Fhack-x)

### How It Works on Vercel + Supabase:
1. **Frontend**: The React 19 / Vite / Tailwind UI automatically compiles and deploys to Vercel's global Edge CDN (`/`).
2. **Backend**: The FastAPI app runs as a high-performance Python Serverless Function (`api/index.py`), handling all `/schemes`, `/eligibility/*`, `/documents/*`, `/applications/*`, `/grievances/*`, `/auth/*`, `/docs`, and `/health` routes.
3. **Database (Supabase PostgreSQL)**: When `DATABASE_URL` is set in Vercel environment variables, BenefitBridge connects to your managed Supabase PostgreSQL instance with connection pooling and SSL encryption. (If unset, it seamlessly falls back to ephemeral `/tmp/benefitbridge.db`).
4. **Single-Domain Synergy**: Both frontend and backend share the identical origin (`*.vercel.app`), eliminating CORS configuration headaches.

### Deploy in 4 Steps (GitHub + Supabase + Vercel):

#### 1. Create your Supabase Database
1. Go to **[supabase.com](https://supabase.com)** and create a new project.
2. In your Supabase Project Settings -> **Database**, copy your **Connection String** (URI).
   - *Direct Connection*: `postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres`
   - *Supavisor Pooler (Transaction Mode, port 6543)*: `postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres`

#### 2. Run Database Schema & Seed on Supabase
You can choose either option:
- **Option A (Automated CLI Script)**:
  ```bash
  python backend/migrate_to_supabase.py --url "YOUR_SUPABASE_POSTGRES_URL"
  ```
  *This automatically creates all 8 tables and migrates all 104 demo citizens, schemes, applications, and SLA events.*
- **Option B (Supabase Dashboard Web SQL Editor)**:
  1. Open your Supabase Dashboard -> **SQL Editor**.
  2. Paste and run [`supabase/schema.sql`](supabase/schema.sql).
  3. Paste and run [`supabase/seed.sql`](supabase/seed.sql).

#### 3. Push your repository to GitHub
```bash
git add .
git commit -m "feat: configure Supabase PostgreSQL database integration"
git push origin main
```

#### 4. Deploy via Vercel Dashboard
1. Open **[vercel.com/new](https://vercel.com/new)** and import `syedmasih54-tech/hack-x`.
2. Under **Environment Variables**, add:
   - `DATABASE_URL`: `your_supabase_postgres_url`
3. Click **Deploy**! Every future `git push` to GitHub will automatically deploy updates.

---

## 📁 Repository Structure

```
hack-x/
├── api/                              # Vercel Serverless Function Layer
│   ├── index.py                      # Serverless ASGI entrypoint for FastAPI
│   └── requirements.txt              # Serverless Python dependencies (with psycopg2-binary)
├── backend/                          # FastAPI Application Modules & Data
│   ├── rules/                        # Versioned scheme rules (JSON)
│   ├── sample_documents/             # Synthetic test documents for OCR verification
│   ├── static/                       # Bundled static web assets
│   ├── config.py                     # Configuration & environment loader
│   ├── database.py                   # SQLAlchemy engine (Supabase Postgres & SQLite fallback)
│   ├── digilocker_service.py         # DigiLocker & Meri Pehchaan OAuth service
│   ├── grievance_service.py          # CPGRAMS & CM Helpline draft generator
│   ├── main.py                       # FastAPI application & 19 REST endpoints
│   ├── migrate_to_supabase.py        # Automated CLI migration to Supabase PostgreSQL
│   ├── mismatch_checker.py           # Indian phonetic name & document comparator
│   ├── models.py                     # Database models (Citizens, Schemes, Applications, etc.)
│   ├── ocr_service.py                # Image OCR & Aadhaar regex scrubber
│   ├── requirements.txt              # Python dependencies (with psycopg2-binary)
│   ├── rules_engine.py               # Deterministic eligibility evaluator
│   ├── schemas.py                    # Pydantic v2 validation schemas
│   ├── seed_data.py                  # Database seeder & synthetic test data
│   ├── sync_gov_data.py              # Live government portal synchronizer
│   ├── test_backend.py               # Complete 19-endpoint automated test suite
│   ├── tracker_service.py            # SLA tracking & citizen milestone translator
│   └── voice_service.py              # Bilingual speech intake & entity extractor
├── supabase/                         # Supabase PostgreSQL DDL & Seed Scripts
│   ├── schema.sql                    # Full PostgreSQL table DDL & index definitions
│   └── seed.sql                      # Seed export with all 104 demo citizens, schemes & events
│
├── src/                              # React 19 Frontend Source
│   ├── components/                   # UI sections, preloader, tickets, closing
│   ├── lib/                          # Helper utilities & dynamic URL resolver
│   ├── App.tsx                       # Main React interactive application
│   ├── index.css                     # Tailwind CSS styles & typography
│   └── main.tsx                      # React entry point
│
├── public/                           # Public assets, logos, and favicons
├── package.json                      # NPM scripts & Vite dependencies
├── vite.config.ts                    # Vite dev server & production builder
├── tsconfig.json                     # TypeScript compiler configuration
├── vercel.json                       # Vercel serverless rewrite & routing rules
├── .gitignore                        # Global ignore for venv, node_modules, sqlite DBs
└── README.md                         # Complete project documentation
```

---

## 🚀 Quickstart & Setup

### 1. Prerequisites
- **Python**: 3.11 or newer
- **Node.js**: 20.18+ / 22+
- **Git**

---

### 2. Backend Setup (FastAPI)

```bash
# Navigate to the backend directory
cd backend

# Create and activate a virtual environment
# Windows:
python -m venv .venv
.\.venv\Scripts\activate
# Linux / macOS:
# python -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database seeding & test generation
python seed_data.py

# Launch the FastAPI backend server
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

* **Interactive Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
* **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

### 3. Frontend Setup (React / Vite)

```bash
# From the project root (the frontend is in this directory)

# Install dependencies
npm install

# Start the Vite development server on port 5173
npm run dev -- --host 127.0.0.1
```

* **Citizen Portal Frontend**: [http://127.0.0.1:5173/](http://127.0.0.1:5173/)

---

## 🧪 Verification & Automated Testing

Run the included end-to-end verification suite validating all 19 system endpoints:

```bash
cd backend
python test_backend.py
```

### Verified Test Results:
```text
==================================================
      BenefitBridge Backend Test Suite            
==================================================
[PASS] 0. GET / -> Served BenefitBridge Web UI successfully
[PASS] 1. GET /health -> healthy
[PASS] 2. GET /schemes -> Found 5 schemes with authentic provenance
[PASS] 3a. GET /schemes/widow_pension -> Title: Indira Gandhi National Widow Pension Scheme
[PASS] 3b. GET /schemes/kisan_yojna -> Title: PM-KISAN Yojna
[PASS] 4a. POST /eligibility/check (65yo widow) -> Eligible schemes: ['old_age_pension', 'widow_pension']
[PASS] 4b. POST /eligibility/check (Student missing docs) -> Partial match identified
[PASS] 4c. POST /eligibility/check (45yo Farmer) -> Eligible schemes: ['kisan_yojna']
[PASS] 5a. POST /documents/scan (Ration Card) -> Extracted: 'Sunita Devi'
[PASS] 5b. POST /documents/scan (Bank Passbook) -> Extracted: 'Sunitha Devi'
[PASS] 6. POST /documents/compare -> Status: likely_match_with_spelling_variation (Score: 0.95)
[PASS] 7. POST /applications -> Created ID: APP-85B71275 | Status: submitted
[PASS] 8. GET /applications/{id} -> Events logged successfully
[PASS] 9. GET /applications/{id}/status -> Stage: 'Application Received'
[PASS] 10. POST /applications/{id}/mock-status-update -> New Status: under_review
[PASS] 11. POST /grievances/draft -> Grievance generated (21 days overdue)
[PASS] 12. GET /grievances/{id} -> Successfully retrieved draft text
[PASS] 13. POST /voice/intake -> Scheme: 'widow_pension' | Aadhaar Redacted
[PASS] 14. POST /voice/apply-scheme -> App ID generated & Scheme submitted
[PASS] 15. GET /auth/digilocker/login -> OAuth URL generated
[PASS] 16. GET /auth/digilocker/callback -> Verified Citizen credentials
[PASS] 17. GET /citizens/{id}/digilocker-documents -> Verified credentials retrieved
[PASS] 18. POST /schemes/sync-live-data -> Ingested 5 schemes from live repositories
[PASS] 19. GET /schemes/old_age_pension -> Verified Provenance & SLA
==================================================
     ALL 19 ENDPOINTS PASSED WITH FLYING COLORS!   
==================================================
```

---

## 📜 License

This project is licensed under the MIT License.

