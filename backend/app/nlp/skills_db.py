"""
Canonical skill list + alias map used for rule-based skill extraction.

This is intentionally simple (keyword/phrase matching) rather than a trained
classifier, in line with the MVP's "working local NLP approach" requirement.
It's easy to extend: add the canonical name to CANONICAL_SKILLS and any
alternate spellings to ALIASES.
"""

CANONICAL_SKILLS = [
    # Languages
    "java", "python", "javascript", "typescript", "c++", "c", "c#", "go", "rust",
    "php", "ruby", "kotlin", "swift", "r", "scala",
    # Web / frontend
    "html", "css", "react", "redux", "angular", "vue", "next.js", "tailwind css",
    "bootstrap", "jquery",
    # Backend / frameworks
    "node.js", "express.js", "django", "flask", "fastapi", "spring boot", "spring",
    ".net", "asp.net", "laravel", "ruby on rails",
    # APIs & architecture
    "rest api", "graphql", "microservices", "grpc", "soap",
    # Databases
    "sql", "mysql", "postgresql", "mongodb", "sqlite", "oracle", "redis",
    "cassandra", "dynamodb", "elasticsearch",
    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "ci/cd",
    "terraform", "ansible", "linux", "git", "github", "gitlab", "nginx",
    # Data / AI / ML
    "machine learning", "deep learning", "nlp", "computer vision",
    "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "keras",
    "data analysis", "data visualization", "power bi", "tableau", "spark",
    "hadoop", "etl",
    # Testing & tools
    "junit", "selenium", "postman", "jira", "agile", "scrum", "kanban",
    # Mobile
    "android", "ios", "flutter", "react native",
    # Messaging / streaming
    "kafka", "rabbitmq",
]

# Map common alternate spellings / abbreviations -> canonical skill name
ALIASES = {
    "js": "javascript",
    "ts": "typescript",
    "reactjs": "react",
    "react.js": "react",
    "vuejs": "vue",
    "vue.js": "vue",
    "nodejs": "node.js",
    "node": "node.js",
    "expressjs": "express.js",
    "spring-boot": "spring boot",
    "springboot": "spring boot",
    "postgres": "postgresql",
    "mongo": "mongodb",
    "k8s": "kubernetes",
    "ml": "machine learning",
    "dl": "deep learning",
    "tf": "tensorflow",
    "sklearn": "scikit-learn",
    "restful api": "rest api",
    "rest apis": "rest api",
    "restful apis": "rest api",
    "ci cd": "ci/cd",
    "cicd": "ci/cd",
    "html5": "html",
    "css3": "css",
    "golang": "go",
    "c plus plus": "c++",
    "dotnet": ".net",
    "power-bi": "power bi",
    "powerbi": "power bi",
}


def canonical_skill_set():
    return set(CANONICAL_SKILLS)


def normalize_skill(raw: str) -> str:
    """Normalize a recruiter-entered or extracted skill string to its
    canonical form when known; otherwise just lower/trim it so it can still
    be compared consistently even if it's outside our canonical list."""
    cleaned = raw.strip().lower()
    return ALIASES.get(cleaned, cleaned)


def normalize_skill_list(raw_list: list[str]) -> list[str]:
    seen = []
    for item in raw_list:
        if not item or not item.strip():
            continue
        norm = normalize_skill(item)
        if norm not in seen:
            seen.append(norm)
    return seen
