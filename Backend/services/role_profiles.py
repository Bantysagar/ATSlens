"""Curated role profiles for ATSLens Career Intelligence V4.

These profiles are transparent engineering defaults for role-fit analysis. They
are not labor-market forecasts and do not represent hiring probabilities.
"""

from __future__ import annotations

from services.skill_taxonomy import canonicalize_skills


RAW_ROLE_PROFILES = {
    "AI Engineer": {
        "family": "Artificial Intelligence",
        "core": [
            "python", "machine learning", "natural language processing",
            "data preprocessing", "scikit-learn", "api", "sql",
        ],
        "preferred": [
            "deep learning", "generative ai", "large language models",
            "retrieval augmented generation", "fastapi", "embeddings",
            "model deployment", "docker",
        ],
        "optional": ["pytorch", "tensorflow", "mlops", "cloud", "github"],
        "path": ["AI Engineer", "Applied AI Engineer", "Senior AI Engineer"],
    },
    "Machine Learning Engineer": {
        "family": "Machine Learning",
        "core": [
            "python", "machine learning", "scikit-learn", "data preprocessing",
            "feature engineering", "classification", "regression", "sql",
        ],
        "preferred": [
            "deep learning", "pytorch", "tensorflow", "model deployment",
            "docker", "mlops", "git",
        ],
        "optional": ["cloud", "aws", "azure", "statistics", "github"],
        "path": ["Machine Learning Engineer", "ML Platform Engineer", "Senior ML Engineer"],
    },
    "Generative AI Engineer": {
        "family": "Generative AI",
        "core": [
            "python", "generative ai", "large language models", "embeddings",
            "retrieval augmented generation", "natural language processing",
        ],
        "preferred": [
            "prompt engineering", "langchain", "hugging face", "transformers",
            "chromadb", "faiss", "fastapi", "api",
        ],
        "optional": ["pytorch", "docker", "cloud", "model deployment"],
        "path": ["Generative AI Engineer", "LLM Engineer", "Applied AI Engineer"],
    },
    "LLM / RAG Engineer": {
        "family": "Generative AI",
        "core": [
            "python", "large language models", "retrieval augmented generation",
            "embeddings", "natural language processing",
        ],
        "preferred": [
            "prompt engineering", "langchain", "hugging face", "transformers",
            "chromadb", "faiss", "vector database", "fastapi",
        ],
        "optional": ["generative ai", "docker", "cloud", "api"],
        "path": ["LLM / RAG Engineer", "LLM Engineer", "Applied AI Engineer"],
    },
    "NLP Engineer": {
        "family": "Natural Language Processing",
        "core": [
            "python", "natural language processing", "machine learning",
            "scikit-learn", "classification", "data preprocessing",
        ],
        "preferred": [
            "transformers", "hugging face", "deep learning", "pytorch",
            "tensorflow", "embeddings", "large language models",
        ],
        "optional": ["generative ai", "retrieval augmented generation", "fastapi"],
        "path": ["NLP Engineer", "NLP / LLM Engineer", "Applied AI Engineer"],
    },
    "Applied AI Engineer": {
        "family": "Artificial Intelligence",
        "core": [
            "python", "machine learning", "api", "fastapi", "sql",
            "model deployment", "problem solving",
        ],
        "preferred": [
            "natural language processing", "generative ai", "deep learning",
            "docker", "cloud", "github",
        ],
        "optional": ["mlops", "pytorch", "tensorflow", "retrieval augmented generation"],
        "path": ["Applied AI Engineer", "Senior Applied AI Engineer", "AI Solutions Engineer"],
    },
    "AI Backend Engineer": {
        "family": "AI Engineering",
        "core": [
            "python", "fastapi", "api", "rest api", "sql", "database", "git",
        ],
        "preferred": [
            "machine learning", "model deployment", "docker", "postgresql",
            "mysql", "cloud", "github",
        ],
        "optional": ["generative ai", "retrieval augmented generation", "mlops"],
        "path": ["AI Backend Engineer", "AI Platform Engineer", "Senior AI Backend Engineer"],
    },
    "Data Scientist": {
        "family": "Data Science",
        "core": [
            "python", "data science", "machine learning", "pandas", "numpy",
            "statistics", "sql", "data preprocessing",
        ],
        "preferred": [
            "feature engineering", "classification", "regression", "clustering",
            "matplotlib", "scikit-learn",
        ],
        "optional": ["deep learning", "power bi", "tableau", "model deployment"],
        "path": ["Data Scientist", "Senior Data Scientist", "Applied Scientist"],
    },
    "Computer Vision Engineer": {
        "family": "Computer Vision",
        "core": ["python", "opencv", "deep learning", "pytorch", "tensorflow"],
        "preferred": [
            "machine learning", "numpy", "data preprocessing", "model deployment",
            "docker",
        ],
        "optional": ["cloud", "mlops", "classification"],
        "path": ["Computer Vision Engineer", "Applied Vision Engineer", "Senior CV Engineer"],
    },
    "MLOps Engineer": {
        "family": "MLOps",
        "core": ["python", "mlops", "model deployment", "docker", "git", "cloud"],
        "preferred": [
            "machine learning", "aws", "azure", "ci/cd", "linux", "kubernetes",
        ],
        "optional": ["github", "sql", "api", "model monitoring"],
        "path": ["MLOps Engineer", "ML Platform Engineer", "Senior MLOps Engineer"],
    },
    "Data Analyst": {
        "family": "Data Analytics",
        "core": ["sql", "excel", "python", "pandas", "data analysis", "statistics"],
        "preferred": ["power bi", "tableau", "data visualization", "dashboard", "numpy"],
        "optional": ["machine learning", "matplotlib"],
        "path": ["Data Analyst", "Senior Data Analyst", "Analytics Engineer"],
    },
}


def _normalize_profile(profile: dict) -> dict:
    return {
        **profile,
        "core": canonicalize_skills(profile.get("core", [])),
        "preferred": canonicalize_skills(profile.get("preferred", [])),
        "optional": canonicalize_skills(profile.get("optional", [])),
    }


ROLE_PROFILES = {name: _normalize_profile(profile) for name, profile in RAW_ROLE_PROFILES.items()}


def get_role_profiles() -> dict:
    return ROLE_PROFILES


def role_names() -> list[str]:
    return list(ROLE_PROFILES.keys())
