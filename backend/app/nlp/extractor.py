"""
Rule-based + spaCy-assisted structured field extraction from raw resume text.

Every function here is defensive: resumes come in wildly different layouts,
so extraction is heuristic by nature. When a field can't be confidently
detected, functions return None / "" and the caller substitutes the
"Not detected" placeholder rather than raising — per spec section 4 & 20.
"""
import re
import logging
from datetime import datetime

import spacy

from app.config import EDUCATION_LEVELS
from app.nlp.skills_db import CANONICAL_SKILLS, ALIASES

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# spaCy model — loaded once. Falls back to a blank English pipeline (tokenizer
# only, no NER) if the trained model isn't installed, so the app still boots.
# ---------------------------------------------------------------------------
try:
    _NLP = spacy.load("en_core_web_sm")
except OSError:
    logger.warning(
        "en_core_web_sm not found — falling back to blank pipeline. "
        "Run: pip install https://github.com/explosion/spacy-models/releases/"
        "download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl"
    )
    _NLP = spacy.blank("en")

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"\+?\d[\d\-\s]{7,14}\d")
YEARS_EXP_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years|yrs|year)\s*(?:of)?\s*(?:experience|exp)?",
    re.IGNORECASE,
)
DATE_RANGE_RE = re.compile(
    r"(20\d{2}|19\d{2})\s*(?:-|–|to)\s*(20\d{2}|19\d{2}|present|current)",
    re.IGNORECASE,
)

SECTION_HEADERS = {
    "education": ["education", "academic background", "qualifications"],
    "experience": ["experience", "work experience", "employment history", "professional experience"],
    "projects": ["projects", "project experience", "academic projects"],
    "certifications": ["certifications", "certificates", "licenses"],
    "skills": ["skills", "technical skills", "core competencies", "key skills"],
}

DEGREE_PATTERNS = [
    (r"\bph\.?d\.?\b|\bdoctorate\b", "phd"),
    (r"\bm\.?tech\.?\b|\bm\.?e\.?\b|\bm\.?sc\.?\b|\bmca\b|\bmba\b|\bm\.?a\.?\b|\bmaster'?s?\b", "master"),
    (r"\bb\.?tech\.?\b|\bb\.?e\.?\b|\bb\.?sc\.?\b|\bbca\b|\bb\.?com\.?\b|\bb\.?a\.?\b|\bbachelor'?s?\b", "bachelor"),
    (r"\bdiploma\b|\bassociate\b", "diploma"),
    (r"\bhigh school\b|\b12th\b|\bhsc\b", "high school"),
]


def extract_email(text: str) -> str | None:
    match = EMAIL_RE.search(text)
    return match.group(0) if match else None


def extract_phone(text: str) -> str | None:
    for line in text.splitlines():
        if re.search(r"phone|mobile|contact|tel", line, re.IGNORECASE) or re.search(r"\+?\d[\d\s-]{8,}\d", line):
            match = PHONE_RE.search(line)
            if match and len(re.sub(r"\D", "", match.group(0))) >= 7:
                return match.group(0).strip()
    match = PHONE_RE.search(text)
    if match and len(re.sub(r"\D", "", match.group(0))) >= 7:
        return match.group(0).strip()
    return None


def extract_name(text: str) -> str | None:
    """Heuristic: try spaCy PERSON entity in the first few non-empty lines
    (resumes almost always open with the candidate's name); fall back to the
    first plausible line (short, no email/digits, title-case-ish).
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()][:8]
    head_text = "\n".join(lines)
    NON_NAME_WORDS = {"email", "phone", "mobile", "contact", "address", "tel"}

    try:
        doc = _NLP(head_text)
        for ent in getattr(doc, "ents", []):
            if ent.label_ != "PERSON":
                continue
            # spaCy's small model occasionally merges an entity across a
            # newline into the next header word (e.g. "Priya Nair\nEmail") —
            # keep only the first line and drop trailing non-name tokens.
            candidate = ent.text.split("\n")[0].strip()
            words = [w for w in candidate.split() if w.lower() not in NON_NAME_WORDS]
            candidate = " ".join(words)
            if candidate and 1 <= len(words) <= 4 and not any(ch.isdigit() for ch in candidate):
                return candidate
    except Exception:
        pass

    for line in lines:
        if EMAIL_RE.search(line) or PHONE_RE.search(line):
            continue
        if any(ch.isdigit() for ch in line):
            continue
        words = line.split()
        if 1 <= len(words) <= 4 and all(w[0].isupper() for w in words if w[0].isalpha()):
            return line
    return None


def split_sections(text: str) -> dict:
    """Split resume text into named sections based on common header lines.
    Returns a dict of section_name -> text block (may be empty strings)."""
    lines = text.splitlines()
    header_at = {}  # line_index -> section_name
    for idx, line in enumerate(lines):
        clean = line.strip().lower().rstrip(":")
        if not clean or len(clean.split()) > 5:
            continue
        for section, headers in SECTION_HEADERS.items():
            if clean in headers:
                header_at[idx] = section
                break

    sections = {name: "" for name in SECTION_HEADERS}
    sorted_idx = sorted(header_at.keys())
    for pos, idx in enumerate(sorted_idx):
        section = header_at[idx]
        end = sorted_idx[pos + 1] if pos + 1 < len(sorted_idx) else len(lines)
        sections[section] += "\n".join(lines[idx + 1:end]).strip() + "\n"
    return sections


def extract_education(text: str) -> tuple[str | None, int]:
    """Returns (raw_snippet_or_None, ordinal_level)."""
    best_level = 0
    best_snippet = None
    for line in text.splitlines():
        for pattern, level_name in DEGREE_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                level = EDUCATION_LEVELS[level_name]
                if level > best_level:
                    best_level = level
                    best_snippet = line.strip()
    return best_snippet, best_level


def _years_between(start: int, end_str: str) -> float:
    end = datetime.now().year if end_str.lower() in ("present", "current") else int(end_str)
    return max(0.0, float(end - start))


def extract_experience_years(text: str, experience_section: str = "") -> float | None:
    """Try explicit 'X years of experience' phrasing first (most reliable),
    then fall back to summing date ranges found in the experience section."""
    match = YEARS_EXP_RE.search(text)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            pass

    search_space = experience_section or text
    ranges = DATE_RANGE_RE.findall(search_space)
    if ranges:
        total = 0.0
        for start, end in ranges:
            try:
                total += _years_between(int(start), end)
            except ValueError:
                continue
        if total > 0:
            return round(total, 1)
    return None


def extract_skills(text: str) -> list[str]:
    """Rule-based canonical-skill detection using word-boundary matching,
    with alias normalization (e.g. 'ReactJS' -> 'react')."""
    lowered = text.lower()
    found = set()

    for alias, canonical in ALIASES.items():
        pattern = r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])"
        if re.search(pattern, lowered):
            found.add(canonical)

    for skill in CANONICAL_SKILLS:
        pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
        if re.search(pattern, lowered):
            found.add(skill)

    return sorted(found)


def extract_certifications(cert_section: str) -> list[str]:
    if not cert_section.strip():
        return []
    lines = [re.sub(r"^[\u2022\-\*\s]+", "", l).strip() for l in cert_section.splitlines()]
    return [l for l in lines if l and len(l) > 3][:10]


def parse_resume(text: str) -> dict:
    """Run the full extraction pipeline on raw resume text and return a
    plain dict ready to populate a Candidate row. Never raises."""
    text = text or ""
    sections = split_sections(text)

    education_snippet, education_level = extract_education(text)
    experience_years = extract_experience_years(text, sections.get("experience", ""))
    skills = extract_skills(text)
    certifications = extract_certifications(sections.get("certifications", ""))
    projects_text = sections.get("projects", "").strip()
    experience_text = sections.get("experience", "").strip()

    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "education": education_snippet,
        "education_level": education_level,
        "experience_years": experience_years,
        "experience_text": experience_text or None,
        "skills": skills,
        "projects_text": projects_text or None,
        "certifications": certifications,
    }
# ---------------------------------------------------------------------------
# Experience extraction fix (overrides the earlier definitions above)
# ---------------------------------------------------------------------------
YEARS_EXP_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:[A-Za-z/.+#-]+\s+){0,3}?(?:experience|exp)\b",
    re.IGNORECASE,
)
DATE_RANGE_RE = re.compile(
    r"\b(19\d{2}|20\d{2})\s*(?:-|\u2013|\u2014|to)\s*(19\d{2}|20\d{2}|present|current)\b",
    re.IGNORECASE,
)
EDU_WORDS = ("b.tech", "btech", "b.e.", "bachelor", "master", "m.tech", "mca", "bca", "diploma",
             "ph.d", "phd", "university", "college", "school", "institute", "cgpa", "gpa",
             "degree", "hsc", "ssc", "12th", "10th")


def _merge_and_sum(intervals):
    if not intervals:
        return 0.0
    intervals.sort()
    total, (cs, ce) = 0.0, intervals[0]
    for s, e in intervals[1:]:
        if s <= ce:
            ce = max(ce, e)
        else:
            total += ce - cs
            cs, ce = s, e
    return total + (ce - cs)


def extract_experience_years(text: str, experience_section: str = "") -> float | None:
    m = YEARS_EXP_RE.search(text)
    if m:
        value = float(m.group(1))
        if 0 < value <= 45:
            return value

    if not experience_section.strip():
        return None

    now = datetime.now().year
    intervals = []
    for line in experience_section.splitlines():
        if any(w in line.lower() for w in EDU_WORDS):
            continue
        for start, end in DATE_RANGE_RE.findall(line):
            end_year = now if end.lower() in ("present", "current") else int(end)
            if end_year >= int(start):
                intervals.append((int(start), end_year))

    total = _merge_and_sum(intervals)
    return round(total, 1) if total > 0 else None