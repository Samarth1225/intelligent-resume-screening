# Intelligent Resume Screening & Candidate Ranking System

An AI-assisted recruitment MVP that lets a recruiter create a job, upload a
batch of resumes (PDF/DOCX), and get back a ranked, **explainable** shortlist
— every candidate's score is broken into five visible components with a
plain-language reason for each point gained or lost.

> **Disclaimer:** This system provides an automated job-description matching
> analysis and is intended to assist, not replace, human recruitment decisions.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Technology Stack](#technology-stack)
4. [System Architecture](#system-architecture)
5. [Installation](#installation)
6. [Backend Setup](#backend-setup)
7. [Frontend Setup](#frontend-setup)
8. [Database Setup](#database-setup)
9. [How to Run](#how-to-run)
10. [API Documentation](#api-documentation)
11. [Matching Algorithm](#matching-algorithm)
12. [Scoring Methodology](#scoring-methodology)
13. [Sample Credentials](#sample-credentials)
14. [Future Enhancements](#future-enhancements)
15. [Limitations](#limitations)

---

## Project Overview

A recruiter creates a job (title, description, required/preferred skills,
minimum experience, education requirement), uploads multiple resumes, and the
system:

1. Extracts raw text from each PDF/DOCX resume.
2. Runs NLP extraction to pull out name, email, phone, education, experience,
   skills, projects, and certifications.
3. Compares the resume against the job on five weighted dimensions.
4. Produces a 0–100 **job-description match score**, with matched/missing
   skills and a bullet-point explanation of why the score landed where it did.
5. Ranks all candidates for the job, highest score first, on a searchable,
   filterable recruiter dashboard.

## Features

- Create jobs with structured requirements (skills, experience, education)
- Bulk resume upload (PDF + DOCX), with live per-file status feedback
- Rule-based + spaCy-assisted resume parsing, with graceful "Not detected"
  fallbacks — a bad file never crashes the batch
- Transparent, configurable weighted scoring (skills / experience / education
  / project relevance / semantic similarity)
- Explainability panel: a plain-language `+`/`−` list behind every score
- Ranked, searchable, sortable, filterable candidate table
- Candidate detail page with full breakdown, matched vs. missing skills, and
  a score-component chart
- Re-analyze a candidate on demand (e.g. after editing job requirements)
- 5 demo candidates + 2 demo jobs pre-loadable via a seed script
- Responsive UI with loading, empty, and error states throughout
- No use of gender, religion, caste, race, age, disability, marital status, or
  photographs in ranking — see [Limitations](#limitations) for the fairness
  approach in more detail

## Technology Stack

**Frontend:** React (Vite), Tailwind CSS v4, React Router, Axios, Recharts, lucide-react
**Backend:** Python 3.12, FastAPI, Uvicorn
**AI/NLP:** spaCy (`en_core_web_sm`), scikit-learn (TF-IDF + cosine similarity)
**Resume Processing:** pdfplumber (PDF), python-docx (DOCX)
**Database:** SQLite + SQLAlchemy ORM
**Charts:** Recharts

> **A note on "Sentence Transformers"** — the original spec suggested
> `sentence-transformers` for semantic similarity. That library downloads
> pretrained weights from the Hugging Face Hub at first use, which requires
> outbound internet access to `huggingface.co`. Many local/offline dev and
> classroom environments block this. To keep the app **fully functional out
> of the box with no external downloads**, the semantic-similarity component
> ships with a TF-IDF + cosine-similarity implementation (scikit-learn) behind
> a small `SimilarityEngine` interface (`backend/app/nlp/similarity.py`).
> If you have Hugging Face Hub access, swapping in real sentence-transformer
> embeddings (or an LLM embeddings API) is a ~20-line change isolated to that
> one file — nothing else in the codebase needs to know.

## System Architecture

```
intelligent-resume-screening/
│
├── frontend/                 React + Vite + Tailwind SPA
│   └── src/
│       ├── pages/            Login, Dashboard, Jobs, JobDetail, CandidateDetail
│       ├── components/       Layout, tables, cards, upload dropzone, modals
│       ├── api/client.js     Axios instance + typed API helpers
│       └── context/          Demo auth context
│
├── backend/                  FastAPI application
│   └── app/
│       ├── main.py           App entrypoint, CORS, router registration
│       ├── config.py         Scoring weights, education levels, demo auth
│       ├── database.py       SQLAlchemy engine/session
│       ├── models/           Job, Candidate, Resume, CandidateScore, Skill
│       ├── schemas/          Pydantic request/response models
│       ├── routes/           auth.py, jobs.py, candidates.py
│       ├── services/         job/candidate/resume orchestration logic
│       ├── nlp/              parser, extractor, skills_db, similarity, scoring
│       └── utils/            file upload validation & storage
│   ├── seed_data.py          Loads sample_data/ into the DB via the real pipeline
│   └── generate_sample_files.py   (Re)generates the sample PDF/DOCX resumes
│
├── sample_data/
│   ├── resumes/               5 real, readable sample PDF/DOCX resumes
│   └── job_descriptions/      2 sample job description text files
│
└── README.md
```

**Request flow for a resume upload:**

`POST /api/jobs/{id}/resumes` → save file → `nlp/parser.py` extracts raw text
→ `nlp/extractor.py` pulls structured fields → `nlp/scoring.py` computes the
weighted match against the job → results persisted to `candidates`,
`candidate_scores`, and `skills` tables → returned to the frontend, which
polls nothing (it's synchronous) but shows a staged progress UI while it
waits.

---

## Installation

### Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- ~500MB free disk space (spaCy model + Python/Node dependencies)

### Clone / unzip the project, then set up each half:

## Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

# spaCy's small English model isn't on PyPI — install it from its GitHub
# release (see requirements.txt for the same command):
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl

cp .env.example .env            # optional — defaults work out of the box
```

## Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env            # optional — defaults to http://localhost:8000
```

## Database Setup

No manual step needed — tables are created automatically on backend startup
(`Base.metadata.create_all` in `app/main.py`). SQLite stores everything in a
single file: `backend/resume_screening.db`.

To load the **5 sample candidates across 2 sample jobs** (recommended for a
first run / demo):

```bash
cd backend
python3 generate_sample_files.py   # (re)creates the sample PDF/DOCX resumes
python3 seed_data.py               # loads them into the DB through the real pipeline
```

Run `python3 seed_data.py --reset` at any time to wipe the DB and reseed from
scratch.

## How to Run

**Terminal 1 — backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```
API is now live at `http://localhost:8000` (interactive docs at `/docs`).

**Terminal 2 — frontend:**
```bash
cd frontend
npm run dev
```
App is now live at `http://localhost:5173`. Log in with the
[demo credentials](#sample-credentials) and you'll land on the dashboard.

---

## API Documentation

Interactive Swagger UI is auto-generated at `GET /docs` once the backend is
running. Summary of the main endpoints (all except `/api/auth/login` require
`Authorization: Bearer <token>`, obtained from login):

| Method | Path                              | Description                                   |
|--------|-----------------------------------|------------------------------------------------|
| POST   | `/api/auth/login`                 | Demo login, returns a bearer token             |
| POST   | `/api/jobs`                       | Create a job                                   |
| GET    | `/api/jobs`                       | List all jobs with aggregate stats             |
| GET    | `/api/jobs/{id}`                  | Get one job's details + stats                  |
| POST   | `/api/jobs/{id}/resumes`          | Upload one or more resumes (multipart, `files`)|
| GET    | `/api/jobs/{id}/candidates`       | Ranked candidates; supports `search`, `min_score`, `skills`, `sort_by` |
| GET    | `/api/jobs/{id}/rankings`         | Full ranked list (no filters)                  |
| GET    | `/api/candidates/{id}`            | Full candidate detail + score breakdown        |
| POST   | `/api/candidates/{id}/analyze`    | Re-run scoring against current job requirements|
| GET    | `/api/meta`                       | Education options + score weights (for forms)  |
| GET    | `/api/health`                     | Health check                                   |

## Matching Algorithm

Each candidate is scored on five components, combined with configurable
weights (`backend/app/config.py: SCORE_WEIGHTS`):

| Component            | Weight | What it measures                                              |
|-----------------------|--------|----------------------------------------------------------------|
| Skill Match           | 50%    | Required + preferred skills found on the resume                |
| Experience Match      | 20%    | Detected years of experience vs. the job's minimum              |
| Education Match       | 10%    | Candidate's highest qualification vs. the job's requirement      |
| Project Relevance     | 10%    | TF-IDF/cosine similarity between the job and the projects section|
| Semantic Similarity   | 10%    | TF-IDF/cosine similarity between the job description and the full resume |

```
Overall Score = 0.50 × Skill + 0.20 × Experience + 0.10 × Education
              + 0.10 × Project + 0.10 × Semantic
```

Skill matching is normalized through an alias table (e.g. `"ReactJS"` and
`"react.js"` both resolve to `react`), so recruiters and candidates don't need
to use identical spelling for a skill to count as a match.

## Scoring Methodology

- **Skill Match**: required skills are worth more than preferred skills
  (80/20 split when both are present); 100% if a job lists no skills at all.
- **Experience Match**: 100% if the candidate meets or exceeds the minimum;
  scaled linearly below that (e.g. 1 year against a 2-year minimum → 50%).
- **Education Match**: 100% if the candidate's level meets or exceeds the
  requirement, 50% if exactly one level below, 0% otherwise (levels: High
  School < Diploma < Bachelor's < Master's < PhD).
- **Project Relevance / Semantic Similarity**: cosine similarity over TF-IDF
  vectors, scaled to 0–100.
- **Explainability**: `nlp/scoring.py` also emits a list of `+`/`−` bullet
  points (matched/missing skills, experience gap, education gap, project
  relevance) shown on the candidate detail page — the score is never a bare,
  unexplained number.

All of this is a **job-description match score**, not a hiring
recommendation or a judgment of the candidate's overall quality — this is
stated in the API root response and on the candidate detail page.

## Sample Credentials

```
Email:    demo@resumescreen.ai
Password: demo1234
```

(Configurable via `DEMO_USER_EMAIL` / `DEMO_USER_PASSWORD` in `backend/.env`.)

## Future Enhancements

- Swap the local TF-IDF similarity engine for real sentence-transformer
  embeddings or an LLM embeddings API (see the note in
  [Technology Stack](#technology-stack) — the interface is already there)
- Real multi-user authentication and role-based access (recruiter vs. hiring
  manager) instead of the single demo account
- Async/background resume processing with progress polling for very large
  batches, instead of synchronous per-request processing
- Interview scheduling integration once a shortlist is finalized
- Per-recruiter configurable scoring weights (currently global)
- Analytics on hiring-funnel outcomes vs. match score over time

## Limitations

- **Demo authentication only** — one hardcoded account, a static bearer
  token, no password hashing or session expiry. Do not deploy this
  authentication approach beyond a local demo.
- **Local NLP, not an LLM** — extraction is regex + spaCy NER + a rule-based
  skill dictionary. It works well on clearly-structured resumes and may
  under-extract on very unconventional layouts (this is why every field
  degrades to "Not detected" instead of erroring).
- **Text-based files only** — a scanned/image-only PDF with no embedded text
  layer will yield "Not detected" for all fields (no OCR is included).
  Native PDF/DOCX exports work well.
- **TF-IDF, not deep semantic embeddings** — see the Technology Stack note;
  this still rewards shared vocabulary but doesn't capture meaning the way a
  transformer embedding would.
- **Global scoring weights** — one weight configuration applies to every job;
  per-job or per-recruiter weight tuning isn't implemented yet.
- **Synchronous processing** — a very large batch of resumes uploaded at once
  will block the request until all are processed; there's no background job
  queue in this MVP.
