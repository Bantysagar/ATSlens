from services.section_mapper import map_sections
from services.requirement_classifier import classify_requirements
from services.exact_matcher import match_requirements
from services.scoring_v2 import score_v2


def analyze_resume_v2(
    resume_text: str,
    job_description: str,
    candidate_type: str,
    target_field: str,
    experience_years: int = 0,
    preferred_role: str = "",
    target_company: str = "MNC",
) -> dict:
    if len((resume_text or "").split()) < 40:
        raise ValueError("Resume text is too short or unreadable.")
    if len((job_description or "").split()) < 5:
        raise ValueError("Job description is too short.")

    section_map = map_sections(resume_text)
    requirement_map = classify_requirements(job_description)
    exact_match_result = match_requirements(
        resume_text,
        section_map,
        requirement_map["requirements"],
    )

    scores = score_v2(
        resume_text=resume_text,
        target_field=target_field,
        section_map=section_map,
        exact_match_result=exact_match_result,
        requirements=requirement_map["requirements"],
    )

    return {
        "engine_version": "ATSLens-Advanced-V2-Phase1",
        "research_status": "phase-1-deterministic-baseline",
        "candidate_type": candidate_type,
        "target_field": target_field,
        "preferred_role": preferred_role,
        "target_company": target_company,
        "experience_years": experience_years,
        "scores": scores,
        "sections": {
            "detected": section_map["detected_sections"],
            "count": section_map["section_count"],
        },
        "requirements": requirement_map,
        "exact_matching": exact_match_result,
        "limitations": [
            "Phase 1 uses exact skill matching only; semantic matching is added in Phase 2.",
            "Analysis confidence is heuristic and not statistically calibrated yet.",
            "Requirement priority is inferred from JD wording and should be user-reviewable in the final system.",
        ],
    }
