# ATSLens Advanced V3 Integrated Prototype

This package preserves the legacy `/analyze` API and Phase-1 `/analyze-v2`, then adds a parallel `/analyze-v3` research/development path.

## Integrated layers
- Deterministic requirement classification and exact/alias matching
- Optional Sentence-Transformer semantic matching with TF-IDF fallback
- Transparent related-skill graph
- Hybrid requirement scoring
- Evidence localization, recency signal, and documented-evidence strength
- Keyword-stuffing, explicit contradiction, and timeline checks
- Structured confidence signal (not statistically calibrated)
- Grounded deterministic explanation layer with an LLM-ready evidence payload
- Advanced PDF report
- Separate `Frontend/advanced.html` dashboard
- Offline research evaluation harness

## Local run
```powershell
cd Backend
python -m pip install -r requirements.txt
# Optional, for transformer semantic matching:
python -m pip install -r requirements-advanced.txt
uvicorn main:app --reload
```

Open `http://127.0.0.1:8000/docs` and test `/v3/health`, then `/analyze-v3`.

For the visual dashboard, use VS Code Live Server on `Frontend/advanced.html` while the backend is running locally.

## Important research limitations
Semantic thresholds and confidence are engineering defaults until evaluated/calibrated on labeled data. Skill-graph relations provide partial context, not proof. ATSLens scores are decision-support metrics and must not be presented as a proprietary employer ATS acceptance probability.
