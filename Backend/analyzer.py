import re
from difflib import SequenceMatcher

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


FIELD_SKILLS = {
    "Software Engineer": [
        "python", "java", "c++", "data structures", "algorithms", "oop",
        "dbms", "sql", "git", "problem solving", "system design", "rest api"
    ],

    "AI/ML Engineer": [
        "python", "machine learning", "deep learning", "nlp",
        "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
        "model deployment", "data preprocessing", "generative ai",
        "llm", "rag", "mlops"
    ],

    "Data Analyst": [
        "sql", "excel", "power bi", "tableau", "python", "pandas",
        "statistics", "data visualization", "data analysis", "dashboard"
    ],

    "Web Developer": [
        "html", "css", "javascript", "react", "node.js", "api",
        "git", "responsive design", "database", "frontend"
    ],

    "Backend Developer": [
        "python", "java", "fastapi", "django", "flask", "node.js",
        "sql", "mongodb", "api", "rest api", "docker"
    ],

    "Full Stack Developer": [
        "html", "css", "javascript", "react", "node.js", "python",
        "sql", "mongodb", "api", "git", "deployment"
    ],

    "Data Engineer": [
        "python", "sql", "etl", "spark", "airflow", "aws",
        "data pipeline", "big data", "database", "linux"
    ],

    "Cloud Engineer": [
        "aws", "azure", "gcp", "linux", "docker", "kubernetes",
        "ci/cd", "networking", "cloud", "devops"
    ],

    "Cybersecurity Analyst": [
        "network security", "linux", "python", "security", "firewall",
        "vulnerability", "siem", "ethical hacking", "cybersecurity"
    ],

    "Human Resource Generalist": [
        "recruitment", "onboarding", "employee relations",
        "payroll", "performance management", "hr policies",
        "compliance", "hr analytics"
    ],

    "Human Resource Assciate": [
        "recruitment", "onboarding", "hr operations",
        "employee records", "payroll", "communication",
        "compliance", "human resources"
    ],

    "Human Resource Manager": [
        "talent acquisition", "performance management",
        "employee relations", "hr strategy", "leadership",
        "compliance", "workforce planning", "hr analytics"
    ],

    "Human Resource Busniness Partner": [
        "hr strategy", "business partnering", "employee relations",
        "talent management", "performance management",
        "workforce planning", "change management", "hr analytics"
    ],

    "Human Resource Assistant Manager": [
        "recruitment", "team management", "employee relations",
        "performance management", "hr operations", "compliance",
        "payroll", "hr analytics"
    ]
}


EXTRA_SKILLS = {
    "mysql",
    "postgresql",
    "mongodb",
    "github",
    "typescript",
    "bootstrap",
    "tailwind",
    "keras",
    "opencv",
    "matplotlib",
    "seaborn",
    "classification",
    "regression",
    "clustering",
    "feature engineering",
    "communication",
    "leadership",
    "teamwork",
    "redis",
    "graphql",
    "jenkins",

    "html",
    "css",
    "javascript",
    "python",
    "java",
    "c",
    "c++",

    "api",
    "rest api",
    "fastapi",
    "flask",
    "django",

    "docker",
    "kubernetes",
    "linux",

    "aws",
    "azure",
    "gcp",

    "git",
    "github",

    "machine learning",
    "deep learning",
    "nlp",
    "natural language processing",

    "generative ai",
    "genai",

    "llm",
    "large language model",
    "large language models",

    "rag",
    "retrieval augmented generation",

    "langchain",
    "hugging face",
    "transformers",

    "chromadb",
    "faiss",
    "vector database",
    "embeddings",

    "prompt engineering",
    "mlops",
    "model deployment",
    "model monitoring",

    "data preprocessing",
    "data science",
    "statistics",

    "excel",
    "power bi",
    "tableau",

    "spark",
    "airflow",
    "etl",

    "ci/cd",
    "devops",
    "networking",
    "cybersecurity",

    "recruitment",
    "onboarding",
    "employee relations",
    "payroll",
    "hr operations",
    "performance management",
    "talent acquisition",
    "talent management",
    "hr strategy",
    "workforce planning",
    "business partnering",
    "change management",
    "human resources"
}


ALL_SKILLS = sorted(
    set(
        skill
        for skills in FIELD_SKILLS.values()
        for skill in skills
    ) | EXTRA_SKILLS
)


TECHNOLOGIES = {
    "python",
    "java",
    "c++",
    "javascript",
    "typescript",

    "react",
    "node.js",

    "fastapi",
    "django",
    "flask",

    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "redis",

    "docker",
    "kubernetes",

    "aws",
    "azure",
    "gcp",

    "tensorflow",
    "pytorch",
    "scikit-learn",

    "git",
    "github",

    "power bi",
    "tableau",

    "html",
    "css",

    "spark",
    "airflow",

    "langchain",
    "hugging face",
    "chromadb",
    "faiss"
}


ACTION_VERBS = {
    "built",
    "developed",
    "designed",
    "implemented",
    "deployed",
    "created",
    "optimized",
    "automated",
    "engineered",
    "integrated",
    "trained",
    "evaluated",
    "improved",
    "managed",
    "led",
    "analyzed",
    "delivered"
}


PROJECT_EVIDENCE_WORDS = {
    "github",
    "deployed",
    "deployment",
    "api",
    "database",
    "model",
    "dashboard",
    "web app",
    "application",
    "pipeline",
    "frontend",
    "backend",
    "accuracy",
    "precision",
    "recall",
    "f1",
    "auc",
    "users",
    "performance"
}


DEGREE_TERMS = {
    "b tech",
    "btech",
    "bca",
    "mca",
    "b sc",
    "bsc",
    "m sc",
    "msc",
    "bachelor",
    "master",
    "degree",
    "computer science",
    "information technology",
    "artificial intelligence",
    "data science"
}


INSTITUTION_TERMS = {
    "university",
    "college",
    "institute",
    "school"
}


def analyze_resume(
    resume_text: str,
    job_description: str,
    candidate_type: str,
    target_field: str,
    experience_years: int,
    preferred_role: str,
    target_company: str
) -> dict:

    resume = clean_text(resume_text)
    jd = clean_text(job_description)

    if len(resume.split()) < 40:
        raise ValueError(
            "Resume text is too short or unreadable."
        )

    if len(jd.split()) < 5:
        raise ValueError(
            "Job description is too short."
        )

    resume_skills = extract_skills(resume)

    jd_skills = extract_skills(jd)

    target_skills = FIELD_SKILLS.get(
        target_field,
        []
    )


    required_skills = sorted(
        set(jd_skills) |
        set(target_skills)
    )


    matched_skills = sorted(
        set(resume_skills)
        .intersection(required_skills)
    )


    missing_skills = sorted(
        set(required_skills)
        .difference(resume_skills)
    )


    breakdown = {

        "structure":
            score_structure(resume),

        "skills":
            score_skills(
                resume_skills,
                jd_skills,
                target_skills
            ),

        "technologies":
            score_technologies(
                resume_skills,
                jd_skills,
                target_skills
            ),

        "projects":
            score_projects(
                resume,
                resume_skills,
                jd_skills,
                target_skills
            ),

        "experience":
            score_experience(
                resume,
                candidate_type,
                experience_years,
                resume_skills,
                jd_skills,
                target_skills
            ),

        "education":
            score_education(resume),

        "keywords":
            score_keywords(
                resume,
                jd,
                resume_skills,
                jd_skills
            ),

        "formatting":
            score_formatting(
                resume_text
            )
    }


    total_obtained = sum(
        breakdown.values()
    )


    total_marks = 130


    score = round(
        (
            total_obtained /
            total_marks
        ) * 100
    )


    grade = get_grade(score)

    verdict = get_verdict(score)


    mnc_chance = calculate_mnc_chance(
        score,
        breakdown,
        target_company
    )


    mnc_label, mnc_message = \
        get_mnc_message(
            mnc_chance
        )


    field_matches = calculate_field_matches(
        resume_skills,
        resume
    )


    key_strengths = get_key_strengths(
        breakdown,
        matched_skills
    )


    roadmap = build_roadmap(
        target_field,
        missing_skills,
        candidate_type
    )


    summary = build_summary(
        score,
        matched_skills,
        missing_skills,
        target_field
    )


    final_advice = build_final_advice(
        score,
        target_field,
        missing_skills
    )


    return {

        "filename": "",

        "candidate_type":
            candidate_type,

        "target_field":
            target_field,

        "preferred_role":
            preferred_role,

        "target_company":
            target_company,

        "experience_years":
            experience_years,

        "score":
            score,

        "grade":
            grade,

        "verdict":
            verdict,

        "summary":
            summary,

        "breakdown":
            breakdown,

        "total_obtained":
            total_obtained,

        "total_marks":
            total_marks,

        "matched_skills":
            matched_skills,

        "missing_skills":
            missing_skills,

        "resume_skills":
            resume_skills,

        "jd_skills":
            jd_skills,

        "key_strengths":
            key_strengths,

        "roadmap":
            roadmap,

        "field_matches":
            field_matches,

        "mnc_chance":
            mnc_chance,

        "mnc_label":
            mnc_label,

        "mnc_message":
            mnc_message,

        "final_advice":
            final_advice
    }


# ======================================================
# TEXT CLEANING
# ======================================================

def clean_text(text: str) -> str:

    text = (text or "").lower()

    text = text.replace(
        "c++",
        "cplusplus"
    )

    text = text.replace(
        "c#",
        "csharp"
    )

    text = text.replace(
        "node.js",
        "nodejs"
    )

    text = text.replace(
        "ci/cd",
        "cicd"
    )


    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )


    text = text.replace(
        "cplusplus",
        "c++"
    )

    text = text.replace(
        "csharp",
        "c#"
    )

    text = text.replace(
        "nodejs",
        "node.js"
    )

    text = text.replace(
        "cicd",
        "ci/cd"
    )


    text = re.sub(
        r"\s+",
        " ",
        text
    )


    return text.strip()


def contains_phrase(
    text: str,
    phrase: str
) -> bool:

    normalized_phrase = clean_text(
        phrase
    )

    if not normalized_phrase:
        return False


    pattern = (
        r"(?<![a-z0-9])"
        + re.escape(
            normalized_phrase
        )
        + r"(?![a-z0-9])"
    )


    return bool(
        re.search(
            pattern,
            text
        )
    )


# ======================================================
# SKILL EXTRACTION
# ======================================================

def extract_skills(
    text: str
) -> list:

    found = []


    for skill in ALL_SKILLS:

        if contains_phrase(
            text,
            skill
        ):

            found.append(
                skill
            )


    return sorted(
        set(found)
    )


def coverage_score(
    found: set,
    required: set,
    max_score: int
) -> int:

    if not required:
        return 0


    ratio = (
        len(
            found.intersection(
                required
            )
        )
        /
        len(required)
    )


    return round(
        ratio *
        max_score
    )


# ======================================================
# STRUCTURE
# ======================================================

def score_structure(
    resume: str
) -> int:

    score = 0


    if (
        "summary" in resume
        or
        "objective" in resume
        or
        "profile" in resume
    ):
        score += 3


    if (
        "education" in resume
        or
        any(
            contains_phrase(
                resume,
                term
            )
            for term in DEGREE_TERMS
        )
    ):
        score += 4


    if (
        "skills" in resume
        or
        "technical skills" in resume
    ):
        score += 4


    if (
        "project" in resume
        or
        "projects" in resume
    ):
        score += 4


    if (
        "experience" in resume
        or
        "internship" in resume
        or
        "intern" in resume
    ):
        score += 3


    if (
        "certification" in resume
        or
        "certifications" in resume
        or
        "achievement" in resume
    ):
        score += 2


    return min(
        score,
        20
    )


# ======================================================
# SKILLS SCORE
# ======================================================

def score_skills(
    resume_skills: list,
    jd_skills: list,
    target_skills: list
) -> int:

    resume_set = set(
        resume_skills
    )

    jd_set = set(
        jd_skills
    )

    target_set = set(
        target_skills
    )


    if jd_set:

        jd_component = coverage_score(
            resume_set,
            jd_set,
            14
        )


        baseline_component = (
            coverage_score(
                resume_set,
                target_set,
                6
            )
            if target_set
            else 0
        )


        return min(
            jd_component +
            baseline_component,
            20
        )


    if target_set:

        return coverage_score(
            resume_set,
            target_set,
            20
        )


    return 0


# ======================================================
# TECHNOLOGIES
# ======================================================

def score_technologies(
    resume_skills: list,
    jd_skills: list,
    target_skills: list
) -> int:

    resume_tech = (
        set(resume_skills)
        .intersection(
            TECHNOLOGIES
        )
    )


    jd_tech = (
        set(jd_skills)
        .intersection(
            TECHNOLOGIES
        )
    )


    target_tech = (
        set(target_skills)
        .intersection(
            TECHNOLOGIES
        )
    )


    if jd_tech:

        jd_component = coverage_score(
            resume_tech,
            jd_tech,
            15
        )


        target_component = (
            coverage_score(
                resume_tech,
                target_tech,
                5
            )
            if target_tech
            else 0
        )


        return min(
            jd_component +
            target_component,
            20
        )


    if target_tech:

        return coverage_score(
            resume_tech,
            target_tech,
            20
        )


    return min(
        len(resume_tech),
        5
    )


# ======================================================
# PROJECT SCORE
# ======================================================

def score_projects(
    resume: str,
    resume_skills: list,
    jd_skills: list,
    target_skills: list
) -> int:

    if (
        "project" not in resume
        and
        "projects" not in resume
    ):
        return 0


    score = 4


    action_count = sum(
        1
        for word in ACTION_VERBS
        if contains_phrase(
            resume,
            word
        )
    )


    score += min(
        action_count,
        4
    )


    evidence_count = sum(
        1
        for word
        in PROJECT_EVIDENCE_WORDS
        if contains_phrase(
            resume,
            word
        )
    )


    score += min(
        evidence_count,
        4
    )


    required = (
        set(jd_skills)
        if jd_skills
        else set(target_skills)
    )


    if required:

        relevant_count = len(
            set(resume_skills)
            .intersection(
                required
            )
        )


        score += min(
            relevant_count,
            5
        )


    if re.search(
        r"\b\d+(?:\.\d+)?\s*%\b",
        resume
    ):
        score += 2

    elif re.search(
        r"\b\d{2,}\b",
        resume
    ):
        score += 1


    if (
        "github" in resume
        or
        "deployed" in resume
        or
        "deployment" in resume
    ):
        score += 1


    return min(
        score,
        20
    )


# ======================================================
# EXPERIENCE
# ======================================================

def score_experience(
    resume: str,
    candidate_type: str,
    experience_years: int,
    resume_skills: list,
    jd_skills: list,
    target_skills: list
) -> int:

    score = 0


    candidate_is_experienced = (
        candidate_type.lower()
        ==
        "experienced"
    )


    has_experience = (
        "experience" in resume
        or
        "employment" in resume
        or
        "work history" in resume
    )


    has_internship = (
        "internship" in resume
        or
        contains_phrase(
            resume,
            "intern"
        )
    )


    if has_experience:
        score += 5


    if has_internship:

        if candidate_is_experienced:
            score += 3
        else:
            score += 5


    action_count = sum(
        1
        for word in ACTION_VERBS
        if contains_phrase(
            resume,
            word
        )
    )


    score += min(
        action_count,
        3
    )


    required = (
        set(jd_skills)
        if jd_skills
        else set(target_skills)
    )


    relevant_count = (
        len(
            set(resume_skills)
            .intersection(
                required
            )
        )
        if required
        else 0
    )


    score += min(
        relevant_count,
        4
    )


    if (
        re.search(
            r"\b\d+(?:\.\d+)?\s*%\b",
            resume
        )
        or
        re.search(
            r"\b\d{2,}\b",
            resume
        )
    ):
        score += 2


    if candidate_is_experienced:

        score += min(
            max(
                int(experience_years),
                0
            ),
            4
        )

    else:

        # Fresher project work should not
        # automatically become job experience.
        if (
            not has_experience
            and
            not has_internship
        ):
            score = min(
                score,
                7
            )


    return min(
        score,
        20
    )


# ======================================================
# EDUCATION
# ======================================================

def score_education(
    resume: str
) -> int:

    score = 0


    if "education" in resume:
        score += 3


    if any(
        contains_phrase(
            resume,
            term
        )
        for term in DEGREE_TERMS
    ):
        score += 4


    if any(
        contains_phrase(
            resume,
            term
        )
        for term in INSTITUTION_TERMS
    ):
        score += 2


    if (
        "cgpa" in resume
        or
        "gpa" in resume
        or
        "percentage" in resume
        or
        re.search(
            r"\b\d+(?:\.\d+)?\s*%\b",
            resume
        )
    ):
        score += 1


    return min(
        score,
        10
    )


# ======================================================
# JD KEYWORD / SEMANTIC MATCH
# ======================================================

def score_keywords(
    resume: str,
    jd: str,
    resume_skills: list,
    jd_skills: list
) -> int:

    similarity_score = 0


    try:

        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2)
        )


        vectors = (
            vectorizer
            .fit_transform(
                [resume, jd]
            )
        )


        similarity = (
            cosine_similarity(
                vectors[0:1],
                vectors[1:2]
            )[0][0]
        )


        similarity_score = round(
            similarity * 6
        )


    except Exception:

        ratio = SequenceMatcher(
            None,
            resume,
            jd
        ).ratio()


        similarity_score = round(
            ratio * 6
        )


    skill_score = 0


    if jd_skills:

        skill_coverage = (
            len(
                set(resume_skills)
                .intersection(
                    set(jd_skills)
                )
            )
            /
            len(
                set(jd_skills)
            )
        )


        skill_score = round(
            skill_coverage * 4
        )


    return min(
        similarity_score +
        skill_score,
        10
    )


# ======================================================
# FORMATTING / READABILITY
# ======================================================

def score_formatting(
    original_text: str
) -> int:

    words = original_text.split()

    word_count = len(words)

    score = 0


    if (
        300 <=
        word_count <=
        850
    ):
        score += 3

    elif (
        180 <=
        word_count <=
        1100
    ):
        score += 2

    elif word_count >= 100:
        score += 1


    lines = [
        line.strip()
        for line
        in original_text.splitlines()
        if line.strip()
    ]


    if len(lines) >= 12:
        score += 2

    elif len(lines) >= 6:
        score += 1


    if re.search(
        r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",
        original_text
    ):
        score += 1


    if re.search(
        r"(?:\+?\d[\d\s()-]{7,}\d)",
        original_text
    ):
        score += 1


    if not has_too_many_symbols(
        original_text
    ):
        score += 2


    if lines:

        avg_line_length = (
            sum(
                len(line)
                for line in lines
            )
            /
            len(lines)
        )


        if avg_line_length <= 140:
            score += 1


    return min(
        score,
        10
    )


def has_too_many_symbols(
    text: str
) -> bool:

    symbols = re.findall(
        r"[^a-zA-Z0-9\s.,:@/+%#&()_-]",
        text
    )


    limit = max(
        80,
        int(
            len(text) *
            0.03
        )
    )


    return (
        len(symbols) >
        limit
    )


# ======================================================
# FIELD MATCH
# ======================================================

def calculate_field_matches(
    resume_skills: list,
    resume: str
) -> list:

    results = []

    resume_set = set(
        resume_skills
    )


    for field, skills in \
            FIELD_SKILLS.items():

        field_set = set(
            skills
        )


        matched = (
            resume_set
            .intersection(
                field_set
            )
        )


        match = (
            round(
                (
                    len(matched)
                    /
                    len(field_set)
                ) * 100
            )
            if field_set
            else 0
        )


        if contains_phrase(
            resume,
            field
        ):
            match = min(
                match + 5,
                100
            )


        results.append({
            "field": field,
            "match": match
        })


    return sorted(
        results,
        key=lambda item:
            item["match"],
        reverse=True
    )


# ======================================================
# MNC READINESS
# ======================================================

def calculate_mnc_chance(
    score: int,
    breakdown: dict,
    company_type: str
) -> int:

    chance = score


    if breakdown["skills"] >= 16:
        chance += 3


    if breakdown["projects"] >= 16:
        chance += 3


    if breakdown["keywords"] >= 8:
        chance += 2


    if breakdown["formatting"] <= 4:
        chance -= 5


    if (
        company_type.lower()
        ==
        "mnc"
    ):
        chance -= 2


    return max(
        0,
        min(
            chance,
            95
        )
    )


# ======================================================
# GRADE / VERDICT
# ======================================================

def get_grade(
    score: int
) -> str:

    if score >= 90:
        return "A+"

    if score >= 80:
        return "A"

    if score >= 70:
        return "B+"

    if score >= 60:
        return "B"

    if score >= 50:
        return "C"

    return "D"


def get_verdict(
    score: int
) -> str:

    if score >= 90:
        return "Outstanding Match"

    if score >= 80:
        return "Excellent Match"

    if score >= 70:
        return "Strong Match"

    if score >= 60:
        return "Good Match"

    if score >= 50:
        return "Average Match"

    return "Needs Improvement"


# ======================================================
# MNC MESSAGE
# ======================================================

def get_mnc_message(
    chance: int
):

    if chance >= 80:

        return (
            "High Chance",
            "Your resume shows strong readiness for this type of MNC role. "
            "Final shortlisting still depends on the employer's actual screening process."
        )


    if chance >= 65:

        return (
            "Good Chance",
            "Your resume is reasonably aligned. Improve the missing JD skills "
            "and measurable project impact."
        )


    if chance >= 50:

        return (
            "Moderate Chance",
            "Your resume has relevant foundations, but important job-specific gaps remain."
        )


    return (
        "Low Chance",
        "Your resume currently has significant gaps for this target role. "
        "Improve JD alignment, evidence, and resume quality before applying."
    )


# ======================================================
# KEY STRENGTHS
# ======================================================

def get_key_strengths(
    breakdown: dict,
    matched_skills: list
) -> list:

    strengths = []


    if breakdown["skills"] >= 15:

        strengths.append(
            "Strong job-specific skill alignment"
        )


    if breakdown["projects"] >= 15:

        strengths.append(
            "Projects contain relevant technical evidence"
        )


    if breakdown["structure"] >= 15:

        strengths.append(
            "Well-structured resume"
        )


    if breakdown["keywords"] >= 7:

        strengths.append(
            "Good resume-to-JD keyword alignment"
        )


    if len(matched_skills) >= 5:

        strengths.append(
            "Multiple relevant skills matched"
        )


    if not strengths:

        strengths.append(
            "Basic resume foundation available"
        )


    return strengths


# ======================================================
# ROADMAP
# ======================================================

def build_roadmap(
    target_field: str,
    missing_skills: list,
    candidate_type: str
) -> list:

    roadmap = []


    if missing_skills:

        for skill in \
                missing_skills[:5]:

            roadmap.append(
                f"Learn and demonstrate {skill} with practical evidence"
            )


    if target_field == "AI/ML Engineer":

        roadmap.extend([
            "Build 2 job-relevant machine learning or GenAI projects",
            "Deploy at least one AI model or API using FastAPI",
            "Add measurable model results such as accuracy, F1, latency, or business impact"
        ])


    elif target_field == "Software Engineer":

        roadmap.extend([
            "Practice DSA regularly",
            "Strengthen DBMS, OS, and OOP fundamentals",
            "Build and document production-style GitHub projects"
        ])


    elif target_field == "Data Analyst":

        roadmap.extend([
            "Create dashboards using Power BI or Tableau",
            "Practice intermediate and advanced SQL",
            "Build data analysis case studies with measurable insights"
        ])


    elif target_field == "Web Developer":

        roadmap.extend([
            "Build responsive production-style frontend projects",
            "Strengthen JavaScript fundamentals",
            "Practice API integration and deployment"
        ])


    elif target_field == "Backend Developer":

        roadmap.extend([
            "Build REST APIs with authentication",
            "Practice database schema design",
            "Deploy a backend project using Docker or cloud hosting"
        ])


    else:

        roadmap.extend([
            "Improve project or work descriptions with evidence",
            "Add measurable achievements",
            "Customize the resume for each job description"
        ])


    if (
        candidate_type.lower()
        ==
        "fresher"
    ):

        roadmap.append(
            "Add internships, certifications, open-source work, or strong academic projects"
        )


    return roadmap[:8]


# ======================================================
# SUMMARY
# ======================================================

def build_summary(
    score: int,
    matched: list,
    missing: list,
    target_field: str
) -> str:

    return (
        f"Your evidence-based ATSLens score is {score}% for {target_field}. "
        f"The resume matched {len(matched)} relevant skills and missed "
        f"{len(missing)} identified skills. "
        "This is an internal resume-to-JD readiness estimate, "
        "not an employer's official ATS score."
    )


# ======================================================
# FINAL ADVICE
# ======================================================

def build_final_advice(
    score: int,
    target_field: str,
    missing: list
) -> str:

    if score >= 80:

        return (
            f"Your resume is strongly aligned with this {target_field} target. "
            "Keep tailoring it to each JD and preserve measurable evidence."
        )


    if score >= 65:

        top_missing = (
            ", ".join(
                missing[:3]
            )
            if missing
            else
            "advanced job-specific skills"
        )


        return (
            f"Your resume has a good foundation. Prioritize {top_missing} "
            "and add stronger evidence before applying to highly competitive roles."
        )


    top_missing = (
        ", ".join(
            missing[:3]
        )
        if missing
        else
        "job-specific skills and evidence"
    )


    return (
        f"Your resume needs stronger alignment for {target_field}. "
        f"Start with {top_missing}, then improve project/work evidence "
        "and re-run the analysis."
    )