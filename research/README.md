# ATSLens V3 Research Evaluation

This folder is an **evaluation framework**, not a claim that the model is already validated.

1. Create an anonymized resume–JD dataset using `dataset_template.csv`.
2. Obtain independent human labels. Define the annotation rubric before labeling.
3. Run: `python research/evaluate_v3.py research/your_dataset.csv`.
4. Report ATSLens and TF-IDF results on the same split.
5. Add ablations by disabling semantic, graph, evidence, or reliability components and re-running the same dataset.

Recommended paper metrics depend on the task definition: Precision/Recall/F1 for binary fit classification; MAE/correlation for scored agreement; MRR/nDCG for ranked-candidate experiments. Statistical calibration requires a held-out labeled set and should not be claimed from the current heuristic confidence value.
