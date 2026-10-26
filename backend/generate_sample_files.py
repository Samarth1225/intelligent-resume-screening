"""
Creates real, readable PDF and DOCX sample resumes (+ job description text
files) under sample_data/, so the app has demonstrable content immediately
after installation (spec section 18). Run once:

    python generate_sample_files.py
"""
from pathlib import Path

from fpdf import FPDF
import docx

ROOT = Path(__file__).resolve().parent.parent
RESUME_DIR = ROOT / "sample_data" / "resumes"
JD_DIR = ROOT / "sample_data" / "job_descriptions"
RESUME_DIR.mkdir(parents=True, exist_ok=True)
JD_DIR.mkdir(parents=True, exist_ok=True)


def write_pdf(filename: str, lines: list[str]) -> None:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    for line in lines:
        pdf.set_x(pdf.l_margin)
        if line.startswith("## "):
            pdf.set_font("Helvetica", "B", 13)
            pdf.ln(3)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(0, 7, line[3:])
            pdf.set_font("Helvetica", size=11)
        elif line.startswith("# "):
            pdf.set_font("Helvetica", "B", 16)
            pdf.multi_cell(0, 8, line[2:])
            pdf.set_font("Helvetica", size=11)
        else:
            pdf.multi_cell(0, 6, line)
        pdf.ln(0.5)
    pdf.output(str(RESUME_DIR / filename))


def write_docx(filename: str, lines: list[str]) -> None:
    document = docx.Document()
    for line in lines:
        if line.startswith("## "):
            document.add_heading(line[3:], level=2)
        elif line.startswith("# "):
            document.add_heading(line[2:], level=1)
        elif line.strip() == "":
            document.add_paragraph("")
        else:
            document.add_paragraph(line)
    document.save(str(RESUME_DIR / filename))


# ---------------------------------------------------------------------------
# Candidate 1 — strong match for the Java Backend Developer role (PDF)
# ---------------------------------------------------------------------------
write_pdf("ananya_rao_resume.pdf", [
    "# Ananya Rao",
    "Email: ananya.rao@example.com | Phone: +91 98765 43210",
    "",
    "## Education",
    "B.Tech in Computer Science, National Institute of Technology, 2019",
    "",
    "## Experience",
    "Backend Developer, FinEdge Technologies, 2021 - Present",
    "Backend Developer, CodeWorks Pvt Ltd, 2019 - 2021",
    "3 years of experience building backend services for fintech products.",
    "",
    "## Projects",
    "Built a Java Spring Boot microservices platform for payment processing, exposing REST APIs "
    "consumed by mobile and web clients, backed by PostgreSQL and deployed with Docker on AWS.",
    "Designed a SQL-based reconciliation engine that reduced nightly batch runtime by 40%.",
    "",
    "## Skills",
    "Java, Spring Boot, REST API, SQL, PostgreSQL, Git, Docker, AWS, Microservices, Jenkins",
    "",
    "## Certifications",
    "AWS Certified Developer - Associate",
    "Oracle Certified Professional, Java SE",
])

# ---------------------------------------------------------------------------
# Candidate 2 — good match, slightly less experience (DOCX)
# ---------------------------------------------------------------------------
write_docx("karan_mehta_resume.docx", [
    "# Karan Mehta",
    "Email: karan.mehta@example.com | Phone: 9812345670",
    "",
    "## Education",
    "B.E. in Information Technology, Pune University, 2021",
    "",
    "## Experience",
    "Software Engineer, Bright Solutions, 2021 - Present",
    "2 years of experience in Java backend development.",
    "",
    "## Projects",
    "Developed REST APIs using Spring Boot for an inventory management system, integrated with "
    "a MySQL database and used Git for version control.",
    "Contributed to CI/CD pipeline setup with Jenkins.",
    "",
    "## Skills",
    "Java, Spring Boot, SQL, MySQL, REST API, Git, Jenkins, Agile",
    "",
    "## Certifications",
    "Not detected",
])

# ---------------------------------------------------------------------------
# Candidate 3 — full-stack, decent but partial match (PDF)
# ---------------------------------------------------------------------------
write_pdf("priya_nair_resume.pdf", [
    "# Priya Nair",
    "Email: priya.nair@example.com | Phone: +91 90000 11223",
    "",
    "## Education",
    "B.Tech in Computer Science, VIT University, 2020",
    "",
    "## Experience",
    "Full Stack Developer, WebNova Systems, 2020 - Present",
    "2 years of experience across frontend and backend development.",
    "",
    "## Projects",
    "Built a React.js dashboard consuming REST APIs written in Java and Spring Boot, "
    "with a SQL database for storing analytics events.",
    "Created reusable UI components with Tailwind CSS and Redux.",
    "",
    "## Skills",
    "Java, Spring, React, JavaScript, REST API, SQL, HTML, CSS, Git",
    "",
    "## Certifications",
    "Not detected",
])

# ---------------------------------------------------------------------------
# Candidate 4 — junior, weaker match (DOCX)
# ---------------------------------------------------------------------------
write_docx("suresh_iyer_resume.docx", [
    "# Suresh Iyer",
    "Email: suresh.iyer@example.com | Phone: 9898989898",
    "",
    "## Education",
    "Diploma in Computer Engineering, Mumbai Polytechnic, 2023",
    "",
    "## Experience",
    "Junior Developer, StartHub Labs, 2023 - Present",
    "1 year of experience with Java applications.",
    "",
    "## Projects",
    "Assisted in building a small Java console application for inventory tracking using basic SQL "
    "queries.",
    "",
    "## Skills",
    "Java, SQL, Git, HTML, CSS",
    "",
    "## Certifications",
    "Not detected",
])

# ---------------------------------------------------------------------------
# Candidate 5 — Data/ML profile (strong match for the Data Analyst JD, weak
# match for the Java Backend JD — demonstrates the ranking changes per job)
# ---------------------------------------------------------------------------
write_pdf("neha_kulkarni_resume.pdf", [
    "# Neha Kulkarni",
    "Email: neha.kulkarni@example.com | Phone: +91 91234 56789",
    "",
    "## Education",
    "M.Tech in Data Science, IIT Bombay, 2022",
    "",
    "## Experience",
    "Data Analyst, InsightWorks Analytics, 2022 - Present",
    "2 years of experience in data analysis and machine learning.",
    "",
    "## Projects",
    "Built a machine learning pipeline in Python using scikit-learn and pandas to predict customer "
    "churn, visualized results with Power BI, and queried source data with SQL.",
    "Explored deep learning models with TensorFlow for a demand forecasting proof of concept.",
    "",
    "## Skills",
    "Python, Machine Learning, Pandas, NumPy, Scikit-learn, SQL, Power BI, TensorFlow, Data Analysis",
    "",
    "## Certifications",
    "Google Data Analytics Professional Certificate",
])

# ---------------------------------------------------------------------------
# Sample job descriptions (reference text — also used by seed_data.py)
# ---------------------------------------------------------------------------
(JD_DIR / "java_backend_developer.txt").write_text(
    "Job Title: Java Backend Developer\n\n"
    "We are looking for a Java Backend Developer to design and build scalable REST APIs for our "
    "fintech platform. You will work with Spring Boot, SQL databases, and modern DevOps tooling "
    "in an agile team.\n\n"
    "Required Skills: Java, Spring Boot, SQL, REST API, Git\n"
    "Preferred Skills: Docker, AWS\n"
    "Minimum Experience: 2 years\n"
    "Education: Bachelor's degree in Computer Science or related field\n"
)

(JD_DIR / "data_analyst.txt").write_text(
    "Job Title: Data Analyst / ML Engineer\n\n"
    "We are hiring a Data Analyst to build machine learning models and dashboards that drive "
    "product decisions. You will work with Python, pandas, SQL, and visualization tools to turn "
    "data into insight.\n\n"
    "Required Skills: Python, Machine Learning, Pandas, SQL, Data Analysis\n"
    "Preferred Skills: TensorFlow, Power BI\n"
    "Minimum Experience: 1 year\n"
    "Education: Bachelor's degree in Computer Science, Statistics, or related field\n"
)

print("Sample resumes and job descriptions generated.")
