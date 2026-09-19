"""Offline evaluation harness for ATSLens V3.

Input CSV columns are described in dataset_template.csv. Human labels/scores must
come from an independent annotation protocol; this script does not create them.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "Backend"
sys.path.insert(0, str(BACKEND))

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import f1_score, precision_score, recall_score, mean_absolute_error
from sklearn.metrics.pairwise import cosine_similarity

from services.v3_engine import analyze_resume_v3


def tfidf_baseline(resume: str, jd: str) -> float:
    matrix = TfidfVectorizer(ngram_range=(1, 2), stop_words="english").fit_transform([resume, jd])
    return float(cosine_similarity(matrix[0:1], matrix[1:2])[0, 0]) * 100


def load_rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    parser.add_argument("--threshold", type=float, default=60.0)
    args = parser.parse_args()

    rows = load_rows(Path(args.csv_path))
    predictions, baselines, labels, human_scores = [], [], [], []
    details = []

    for row in rows:
        resume = row["resume_text"]
        jd = row["job_description"]
        result = analyze_resume_v3(
            resume_text=resume,
            job_description=jd,
            candidate_type=row.get("candidate_type") or "Fresher",
            target_field=row.get("target_field") or "AI/ML",
            experience_years=int(row.get("experience_years") or 0),
            preferred_role=row.get("preferred_role") or "",
            target_company=row.get("target_company") or "MNC",
        )
        score = float(result["scores"]["job_match_score"])
        baseline = tfidf_baseline(resume, jd)
        predictions.append(score)
        baselines.append(baseline)

        if row.get("human_match_label", "") != "":
            labels.append(int(row["human_match_label"]))
        if row.get("human_match_score", "") != "":
            human_scores.append(float(row["human_match_score"]))

        details.append({
            "id": row.get("id"),
            "atslens_job_match": score,
            "tfidf_baseline": round(baseline, 2),
            "human_match_label": row.get("human_match_label"),
            "human_match_score": row.get("human_match_score"),
        })

    output = {"n": len(rows), "threshold": args.threshold, "details": details}

    if len(labels) == len(rows) and rows:
        y_pred = [1 if score >= args.threshold else 0 for score in predictions]
        base_pred = [1 if score >= args.threshold else 0 for score in baselines]
        output["atslens_classification"] = {
            "precision": precision_score(labels, y_pred, zero_division=0),
            "recall": recall_score(labels, y_pred, zero_division=0),
            "f1": f1_score(labels, y_pred, zero_division=0),
        }
        output["tfidf_classification"] = {
            "precision": precision_score(labels, base_pred, zero_division=0),
            "recall": recall_score(labels, base_pred, zero_division=0),
            "f1": f1_score(labels, base_pred, zero_division=0),
        }

    if len(human_scores) == len(rows) and rows:
        output["atslens_mae"] = mean_absolute_error(human_scores, predictions)
        output["tfidf_mae"] = mean_absolute_error(human_scores, baselines)

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
