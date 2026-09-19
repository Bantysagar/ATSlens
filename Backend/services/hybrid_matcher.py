"""Combine deterministic, semantic, and skill-relation signals for ATSLens V3.1."""

from __future__ import annotations


PRIORITY_WEIGHT = {"must": 3.0, "preferred": 2.0, "bonus": 1.0}


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def combine_matches(
    requirements: list,
    exact_result: dict,
    semantic_result: dict,
    graph_result: dict,
) -> dict:
    exact_by_skill = {item["skill"]: item for item in exact_result.get("matches", [])}
    semantic_by_skill = {item["skill"]: item for item in semantic_result.get("matches", [])}
    graph_by_skill = {item["requirement"]: item for item in graph_result.get("matches", [])}

    combined = []
    for requirement in requirements:
        skill = requirement["skill"]
        exact = exact_by_skill.get(skill, {})
        semantic = semantic_by_skill.get(skill, {})
        graph = graph_by_skill.get(skill, {})

        match_type = "missing"
        match_score = 0.0
        evidence = None
        evidence_section = None
        evidence_strength = "none"
        graph_score = float(graph.get("graph_signal") or 0.0)

        if exact.get("exact_match"):
            match_type = exact.get("match_type", "exact")
            match_score = 1.0 if match_type == "exact" else 0.96
            evidence_section = (exact.get("evidence_sections") or [None])[0]
            evidence_strength = exact.get("evidence_strength", "medium")
        else:
            semantic_score = float(semantic.get("similarity") or 0.0)

            if semantic.get("semantic_match"):
                # A semantic match is partial evidence, never equivalent to an
                # explicit mention. V3.1 reduces the previous inflation where a
                # threshold-level semantic match could receive >80% credit.
                match_type = "semantic"
                match_score = min(0.84, 0.38 + 0.50 * semantic_score)
                evidence = semantic.get("evidence")
                evidence_section = semantic.get("section")
                evidence_strength = "strong" if semantic.get("strength") == "strong" else "medium"

                if graph_score >= 0.70:
                    match_score = min(0.87, match_score + 0.04 * graph_score)
                    match_type = "semantic+related"
            elif graph_score >= 0.70:
                # Related skills are informative but do not prove possession of
                # the missing requirement. Keep a small partial score while the
                # requirement remains unmatched.
                match_type = "related"
                match_score = min(0.40, 0.20 + 0.18 * graph_score)
                evidence_strength = "low"

        match_score = _bounded(match_score)
        matched = match_score >= 0.60 and match_type not in {"missing", "related"}

        if matched:
            status = match_type
            exposed_match_type = match_type
        elif match_type == "related":
            status = "related-only"
            exposed_match_type = "related"
        else:
            status = "missing"
            exposed_match_type = "none"

        combined.append({
            "skill": skill,
            "priority": requirement.get("priority", "preferred"),
            "status": status,
            "matched": matched,
            "match_type": exposed_match_type,
            "match_score": round(match_score, 4),
            "match_score_percent": round(match_score * 100, 1),
            "evidence_section": evidence_section,
            "evidence": evidence,
            "evidence_strength": evidence_strength,
            "deterministic": exact,
            "semantic": semantic,
            "skill_graph": graph,
        })

    matched_items = [item for item in combined if item["matched"]]
    missing_items = [item for item in combined if not item["matched"]]
    denominator = sum(PRIORITY_WEIGHT.get(item["priority"], 1.0) for item in combined) or 1.0
    weighted = sum(
        PRIORITY_WEIGHT.get(item["priority"], 1.0) * item["match_score"]
        for item in combined
    ) / denominator

    return {
        "matches": combined,
        "matched_count": len(matched_items),
        "missing_count": len(missing_items),
        "matched_skills": [item["skill"] for item in matched_items],
        "missing_skills": [item["skill"] for item in missing_items],
        "exact_count": sum(1 for item in matched_items if item["match_type"] == "exact"),
        "alias_count": sum(1 for item in matched_items if item["match_type"] == "alias"),
        "semantic_count": sum(1 for item in matched_items if item["match_type"].startswith("semantic")),
        "related_count": sum(1 for item in combined if item["match_type"] == "related"),
        "weighted_requirement_coverage": round(weighted * 100, 1),
        "method": "exact-alias-conservative-semantic-related-hybrid-v2",
    }
