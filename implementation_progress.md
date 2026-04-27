# Veritas Improvement Plan — Implementation Progress

## ✅ Completed Items

### Backend (Phase 1 – Critical)

| # | Feature | File(s) Modified | Status |
|---|---------|-------------------|--------|
| 1 | **Gemini prompt remediation** — AI returns 3 concrete remediation steps | `gemini_service.py` | ✅ Done |
| 2 | **Proxy column detection** — detects top-3 correlated non-protected columns | `bias_service.py` | ✅ Done |
| 3 | **API rate limiting** — 10/min on `/analyze`, 20/min on `/model-card`, 30/min on `/sample` | `main.py`, `analyze.py`, `requirements.txt` | ✅ Done |
| 4 | **Model card generator** — HuggingFace-format markdown export | `gemini_service.py`, `analyze.py` | ✅ Done |
| 5 | **Sample dataset endpoint** — `/api/sample/{domain}` for one-click demo | `main.py` + 3 CSVs in `sample_datasets/` | ✅ Done |

### Frontend (Phase 1 – UX)

| # | Feature | File(s) Modified | Status |
|---|---------|-------------------|--------|
| 6 | **Sample dataset demo buttons** — "No CSV? Try a sample" section | `WorkspaceView.jsx`, `App.jsx` | ✅ Done |
| 7 | **ARIA labels** — charts, nav, buttons, form controls | `MetricsChart.jsx`, `TopNav.jsx`, `WorkspaceView.jsx`, `ResultsView.jsx` | ✅ Done |
| 8 | **What-If threshold simulator** — interactive slider per attribute | `ResultsView.jsx` | ✅ Done |
| 9 | **Remediation steps display** — numbered AI-generated steps in sidebar | `ResultsView.jsx` | ✅ Done |
| 10 | **Proxy columns warning card** — amber card with correlation values | `ResultsView.jsx` | ✅ Done |
| 11 | **Model Card download button** — in results action bar | `ResultsView.jsx`, `App.jsx` | ✅ Done |

### Documentation & DevOps

| # | Feature | File(s) Modified | Status |
|---|---------|-------------------|--------|
| 12 | **README roadmap** — 12-item roadmap with v1.1 annotations | `README.md` | ✅ Done |
| 13 | **README new API endpoints** — sample + model-card docs | `README.md` | ✅ Done |
| 14 | **ARCHITECTURE.md update** — reflects all new services/endpoints | `ARCHITECTURE.md` | ✅ Done |
| 15 | **GitHub Actions CI** — backend tests + frontend build | `.github/workflows/ci.yml` | ✅ Done |

---

## 🔲 Remaining Items

| # | Feature | Priority | Notes |
|---|---------|----------|-------|
| R1 | Git rebase / squash cleanup | Medium | Manual step — recommend before final submission |
| R2 | Firestore audit history persistence | Low | Deferred — current stateless design is fine for MVP |
| R3 | Custom column mapping wizard | Low | Roadmap item |

---

## Files Changed Summary

```
Backend:
  backend/app/services/gemini_service.py   — explain_bias returns dict, added generate_model_card
  backend/app/services/bias_service.py     — added detect_proxy_columns
  backend/app/routes/analyze.py            — proxy_columns, remediation, model-card endpoint, rate limits
  backend/main.py                          — rate limiting, sample dataset endpoint
  backend/requirements.txt                 — added slowapi
  backend/sample_datasets/hiring_sample.csv    — regenerated with correct columns
  backend/sample_datasets/loan_sample.csv      — new
  backend/sample_datasets/healthcare_sample.csv — new

Frontend:
  frontend/src/App.jsx                     — onSampleAnalyze, exportModelCard, new props
  frontend/src/components/dashboard/WorkspaceView.jsx  — sample dataset buttons
  frontend/src/components/dashboard/ResultsView.jsx    — What-If simulator, proxy card, remediation, model card btn
  frontend/src/components/dashboard/TopNav.jsx         — ARIA labels
  frontend/src/components/MetricsChart.jsx             — ARIA chart description

DevOps & Docs:
  .github/workflows/ci.yml   — new CI pipeline
  README.md                  — roadmap, new endpoints
  ARCHITECTURE.md            — updated services and endpoints
```
