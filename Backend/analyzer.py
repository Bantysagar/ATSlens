import re
from difflib import SequenceMatcher

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


FIELD_SKILLS = {
    "Software Engineer": [
        "python", "java", "c++", "data structures", "algorithms", "oop",
        "dbms", "sql", "git", "problem solving", "system design"
    ],
    "AI/ML Engineer": [
        "python", "machine learning", "deep learning", "nlp", "tensorflow",
        "pytorch", "scikit-learn", "pandas", "numpy", "model deployment",
        "data preprocessing"
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
        "python", "sql", "etl", "spark", "airflow", "aws", "data pipeline",
        "big data", "database", "linux"
    ],
    "Cloud Engineer": [
        "aws", "azure", "gcp", "linux", "docker", "kubernetes",
        "ci/cd", "networking", "cloud", "devops"
    ],
    "Cybersecurity Analyst": [
        "network security", "linux", "python", "security", "firewall",
        "vulnerability", "siem", "ethical hacking", "cybersecurity"
    ]
}


ALL_SKILLS = sorted(set(skill for skills in FIELD_SKILLS.values() for skill in skills) | {
    "mysql", "postgresql", "mongodb", "github", "typescript", "bootstrap",
    "tailwind", "keras", "opencv", "matplotlib", "seaborn", "classification",
    "regression", "clustering", "feature engineering", "powerpoint",
    "communication", "leadership", "teamwork", "redis", "graphql", "jenkins",
    "html", "css", "javascript", "python", "java", "c", "c++"
})


TECHNOLOGIES = [
    "python", "java", "c++", "javascript", "react", "node.js", "fastapi",
    "django", "flask", "sql", "mysql", "postgresql", "mongodb", "docker",
    "kubernetes", "aws", "azure", "gcp", "tensorflow", "pytorch", "git",
    "github", "power bi", "tableau", "html", "css"
]


SECTIONS = [
    "education", "skills", "projects", "experience", "certifications",
    "summary", "objective", "internship"
]


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
        raise ValueError("Resume text is too short or unreadable.")

    if len(jd.split()) < 5:
        raise ValueError("Job description is too short.")

    resume_skills = extract_skills(resume)
    jd_skills = extract_skills(jd)
    target_skills = FIELD_SKILLS.get(target_field, [])

    required_skills = sorted(set(jd_skills + target_skills))
    matched_skills = sorted(set(resume_skills).intersection(required_skills))
    missing_skills = sorted(set(required_skills).difference(resume_skills))

    breakdown = {
        "structure": score_structure(resume),
        "skills": score_skills(matched_skills, required_skills),
        "technologies": score_technologies(resume_skills, target_skills),
        "projects": score_projects(resume),
        "experience": score_experience(resume, candidate_type, experience_years),
        "education": score_education(resume),
        "keywords": score_keywords(resume, jd),
        "formatting": score_formatting(resume_text)
    }

    total_obtained = sum(breakdown.values())
    total_marks = 130
    score = round((total_obtained / total_marks) * 100)

    grade = get_grade(score)
    verdict = get_verdict(score)

    mnc_chance = calculate_mnc_chance(score, breakdown, target_company)
    mnc_label, mnc_message = get_mnc_message(mnc_chance)

    field_matches = calculate_field_matches(resume_skills, resume)
    key_strengths = get_key_strengths(breakdown, matched_skills)
    roadmap = build_roadmap(target_field, missing_skills, candidate_type)
    summary = build_summary(score, matched_skills, missing_skills, target_field)
    final_advice = build_final_advice(score, target_field, missing_skills)

    return {
        "filename": "",
        "candidate_type": candidate_type,
        "target_field": target_field,
        "preferred_role": preferred_role,
        "target_company": target_company,
        "experience_years": experience_years,
        "score": score,
        "grade": grade,
        "verdict": verdict,
        "summary": summary,
        "breakdown": breakdown,
        "total_obtained": total_obtained,
        "total_marks": total_marks,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "resume_skills": resume_skills,
        "jd_skills": jd_skills,
        "key_strengths": key_strengths,
        "roadmap": roadmap,
        "field_matches": field_matches,
        "mnc_chance": mnc_chance,
        "mnc_label": mnc_label,
        "mnc_message": mnc_message,
        "final_advice": final_advice
    }


def clean_text(text: str) -> str:
    text = text.lower()
    text = text.replace("c++", "cplusplus")
    text = text.replace("node.js", "nodejs")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = text.replace("cplusplus", "c++")
    text = text.replace("nodejs", "node.js")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def contains_phrase(text: str, phrase: str) -> bool:
    pattern = r"(^|\s)" + re.escape(phrase.lower()) + r"($|\s)"
    return bool(re.search(pattern, text))


def extract_skills(text: str) -> list:
    found = []

    for skill in ALL_SKILLS:
        if contains_phrase(text, skill):
            found.append(skill)

    return sorted(set(found))


def score_structure(resume: str) -> int:
    found = sum(1 for section in SECTIONS if section in resume)
    return min(round((found / 6) * 20), 20)


def score_skills(matched: list, required: list) -> int:
    if not required:
        return 10

    return min(round((len(matched) / len(required)) * 20), 20)


def score_technologies(resume_skills: list, target_skills: list) -> int:
    tech_found = set(resume_skills).intersection(set(TECHNOLOGIES))
    target_tech = set(target_skills).intersection(set(TECHNOLOGIES))

    if not target_tech:
        return min(len(tech_found) * 2, 20)

    return min(round((len(tech_found.intersection(target_tech)) / len(target_tech)) * 20), 20)


def score_projects(resume: str) -> int:
    score = 0

    if "project" in resume or "projects" in resume:
        score += 8

    project_keywords = [
        "github", "deployed", "api", "database", "model", "dashboard",
        "web app", "machine learning", "frontend", "backend"
    ]

    for word in project_keywords:
        if word in resume:
            score += 2

    return min(score, 20)


def score_experience(resume: str, candidate_type: str, experience_years: int) -> int:
    score = 0

    if "experience" in resume:
        score += 7

    if "internship" in resume or "intern" in resume:
        score += 5

    if "worked" in resume or "developed" in resume or "built" in resume:
        score += 4

    if candidate_type.lower() == "experienced":
        score += min(experience_years * 2, 4)
    else:
        if "project" in resume:
            score += 4

    return min(score, 20)


def score_education(resume: str) -> int:
    score = 0

    if "education" in resume:
        score += 4

    degree_words = [
        "b.tech", "bca", "mca", "b.sc", "m.sc", "degree",
        "university", "college", "bachelor", "master"
    ]

    for word in degree_words:
        if word in resume:
            score += 2
            break

    if "cgpa" in resume or "percentage" in resume or "%" in resume:
        score += 2

    return min(score, 10)


def score_keywords(resume: str, jd: str) -> int:
    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        vectors = vectorizer.fit_transform([resume, jd])
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        return min(round(similarity * 10), 10)
    except Exception:
        ratio = SequenceMatcher(None, resume, jd).ratio()
        return min(round(ratio * 10), 10)


def score_formatting(original_text: str) -> int:
    words = original_text.split()
    word_count = len(words)

    score = 0

    if 250 <= word_count <= 900:
        score += 4
    elif word_count > 120:
        score += 2

    if "\n" in original_text:
        score += 2

    if len(original_text) > 1000:
        score += 2

    if not has_too_many_symbols(original_text):
        score += 2

    return min(score, 10)


def has_too_many_symbols(text: str) -> bool:
    symbols = re.findall(r"[^a-zA-Z0-9\s.,:@/+%-]", text)
    return len(symbols) > 80


def calculate_field_matches(resume_skills: list, resume: str) -> list:
    results = []

    for field, skills in FIELD_SKILLS.items():
        matched = set(resume_skills).intersection(set(skills))
        match = round((len(matched) / len(skills)) * 100)

        if field.lower() in resume:
            match = min(match + 8, 100)

        results.append({
            "field": field,
            "match": match
        })

    return sorted(results, key=lambda item: item["match"], reverse=True)


def calculate_mnc_chance(score: int, breakdown: dict, company_type: str) -> int:
    chance = score

    if breakdown["projects"] >= 15:
        chance += 4

    if breakdown["skills"] >= 15:
        chance += 4

    if breakdown["formatting"] < 5:
        chance -= 5

    if company_type.lower() == "mnc":
        chance -= 3

    return max(0, min(chance, 95))


def get_grade(score: int) -> str:
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


def get_verdict(score: int) -> str:
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


def get_mnc_message(chance: int):
    if chance >= 80:
        return (
            "High Chance",
            "Your resume is strong for MNC shortlisting. Keep applying with targeted job descriptions."
        )

    if chance >= 65:
        return (
            "Good Chance",
            "You are on the right track. Improve missing skills to increase your chances."
        )

    if chance >= 50:
        return (
            "Moderate Chance",
            "Your resume has potential, but you should improve projects, skills, and keywords."
        )

    return (
        "Low Chance",
        "You need to improve skills, projects, formatting, and job-specific keywords before applying."
    )


def get_key_strengths(breakdown: dict, matched_skills: list) -> list:
    strengths = []

    if breakdown["skills"] >= 15:
        strengths.append("Strong technical skills")

    if breakdown["projects"] >= 15:
        strengths.append("Good project experience")

    if breakdown["structure"] >= 15:
        strengths.append("Well-structured resume")

    if breakdown["keywords"] >= 7:
        strengths.append("Good keyword match")

    if len(matched_skills) >= 5:
        strengths.append("Relevant skill alignment")

    if not strengths:
        strengths.append("Basic resume foundation available")

    return strengths


def build_roadmap(target_field: str, missing_skills: list, candidate_type: str) -> list:
    roadmap = []

    if missing_skills:
        for skill in missing_skills[:5]:
            roadmap.append(f"Learn and practice {skill}")

    if target_field == "AI/ML Engineer":
        roadmap.extend([
            "Build 2 machine learning projects",
            "Learn model deployment using FastAPI",
            "Practice data preprocessing and feature engineering"
        ])

    elif target_field == "Software Engineer":
        roadmap.extend([
            "Practice DSA regularly",
            "Learn DBMS, OS, and OOP concepts",
            "Build strong GitHub projects"
        ])

    elif target_field == "Data Analyst":
        roadmap.extend([
            "Create dashboards using Power BI or Tableau",
            "Practice SQL queries",
            "Build data analysis case studies"
        ])

    elif target_field == "Web Developer":
        roadmap.extend([
            "Build responsive frontend projects",
            "Learn JavaScript deeply",
            "Practice API integration and deployment"
        ])

    elif target_field == "Backend Developer":
        roadmap.extend([
            "Learn REST API development",
            "Practice database design",
            "Build backend projects with authentication"
        ])

    else:
        roadmap.extend([
            "Improve project descriptions",
            "Add measurable achievements",
            "Customize resume for each job description"
        ])

    if candidate_type.lower() == "fresher":
        roadmap.append("Add internships, certifications, or academic projects")

    return roadmap[:8]


def build_summary(score: int, matched: list, missing: list, target_field: str) -> str:
    return (
        f"Your resume scored {score}% for the target field {target_field}. "
        f"It matched {len(matched)} important skills and missed {len(missing)} skills. "
        f"Improve missing skills and project details to increase shortlisting chances."
    )


def build_final_advice(score: int, target_field: str, missing: list) -> str:
    if score >= 80:
        return (
            f"Excellent performance. You can apply for {target_field} roles, "
            f"but keep improving missing skills."
        )

    if score >= 65:
        top_missing = ", ".join(missing[:3]) if missing else "advanced job-specific skills"
        return (
            f"Good resume. Improve skills like {top_missing} to become stronger."
        )

    return (
        f"Your resume needs improvement before applying for top {target_field} roles. "
        f"Focus on skills, projects, and ATS keywords."
    )