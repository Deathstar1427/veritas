# Veritas Agent Guide

Veritas is a bias auditing tool: FastAPI backend + React frontend. Users upload CSV datasets, the system detects unfair ML outcomes using Fairlearn metrics, and Gemini provides plain-language explanations.

## Quick Start

### Backend (Python 3.11+, FastAPI)
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env                    # Add GEMINI_API_KEY
uvicorn main:app --reload               # Runs at http://localhost:8000
```

### Frontend (React 18, Vite, Node 18+)
```bash
cd frontend
npm install --legacy-peer-deps
npm run dev                              # Runs at http://localhost:5173
```

**Critical:** Frontend hardcodes API to `http://localhost:8000`. Update `.env.local` if backend is elsewhere.

## Key Directories & Entrypoints

| Path | Purpose |
|------|---------|
| `backend/main.py` | FastAPI app + CORS middleware. **All routes imported from `app.routes.analyze`** |
| `backend/app/routes/analyze.py` | 5 endpoints: `/domains`, `/analyze` (CSV upload), `/sample/{domain}`, `/export` (PDF) |
| `backend/app/services/bias_service.py` | Fairlearn metrics: Demographic Parity, Equalized Odds, Disparate Impact Ratio |
| `backend/app/domain_config.py` | Protected attributes, outcome columns per domain (hiring, loan, healthcare, education) |
| `frontend/src/App.jsx` | 3-panel layout: DomainSelector â†’ FileUpload â†’ BiasReport |

## Critical Quirks & Gotchas

### Bias Calculation
- **Disparate Impact Ratio** = (group outcome rate) / (reference group rate). If < 0.80 â†’ HIGH bias.
- **Zero-division protection**: If reference group has 0 positive outcomes, ratio is `null` (not a number).
- Only attributes that **exist in the CSV** are analyzed. Missing protected attributes are silently skipped (line 34 in `bias_service.py`).

### CSV Upload Flow
1. Frontend validates file type (must end `.csv`)
2. Backend validates domain + required outcome column
3. Fairlearn computes metrics **for each protected attribute** separately
4. **Gemini API call** happens after bias metrics (can fail gracefully; fallback message used)
5. PDF export requires `bias_results` + `gemini_explanation` JSON in POST body

### Domain Configuration (`domain_config.py`)
Each domain defines:
- `outcome_column`: what gets analyzed (e.g., `hired`, `approved`, `diagnosis_positive`)
- `protected_attributes`: what to check for bias (e.g., `gender`, `age_group`, `ethnicity`)
- `positive_outcome`: what counts as favorable (always `1` in current config)

**If adding a domain:** add entry to `DOMAIN_CONFIG` dict, create sample CSV in `backend/sample_data/`, and update `bias_engine.py` cache.

### Sample Datasets
- Pre-generated with seeded bias. Located in `backend/sample_data/`
- Loaded on-demand via `/api/sample/{domain}`. Cached in memory in `bias_engine.py`.
- Always return HIGH severity to demonstrate the tool works.

### File Size & Format
- Max CSV upload: **10MB** (enforced in `analyze.py` line 40)
- Only `.csv` files accepted (line 47)
- Must be valid UTF-8 decodable

### Environment
- Backend requires `.env` with `GEMINI_API_KEY`
- Frontend uses `.env.local` (already configured for localhost)
- CORS is wide-open (`allow_origins=["*"]`) â€” **lock down in production** (line 13 in `main.py`)

## Testing

### Manual Quick Test
```bash
cd backend
python -m pytest test_backend.py -v                   # If pytest installed
# OR use provided test script:
cd D:\Veritas
.\run_tests.ps1                                      # PowerShell
bash run_tests.sh                                    # Bash (if available)
```

### Test Data Files
- `test_data.csv`: Valid hiring dataset (should pass)
- `test_data_missing_column.csv`: Missing required column (should error 422)
- `test_data_zero_rate.csv`: Zero outcomes in one group (tests division-by-zero fix)

### API Health Check
```bash
curl http://localhost:8000/health                   # Returns {"status":"ok","version":"1.0.0"}
curl http://localhost:8000/api/domains              # Lists all domains
curl http://localhost:8000/api/sample/hiring        # Analyze sample hiring dataset
```

## Deployment

### Docker Build
```bash
cd backend
docker build -t Veritas-backend .
docker run -p 8000:8000 -e GEMINI_API_KEY=<key> Veritas-backend
```

**Note:** Dockerfile exposes port `8080`, but `main:app` doesn't specify a port. Add `--port 8000` or use env var.

### Frontend Build
```bash
cd frontend
npm run build                                        # Outputs to ./dist/
npm run preview                                      # Test build locally
firebase deploy                                      # Deploy to Firebase Hosting (requires auth)
```

## Common Agent Mistakes to Avoid

1. **Forgetting GEMINI_API_KEY** â†’ Gemini calls fail silently, but return fallback message. Always check `.env` exists.
2. **CSV column mismatch** â†’ Bias detection fails if outcome_column missing. Error message includes available columns.
3. **Frontend API URL** â†’ Hardcoded to `http://localhost:8000`. If backend runs elsewhere, update `frontend/.env.local` `VITE_API_URL`.
4. **Protected attributes** â†’ Only attributes in both the CSV AND `domain_config.py` are analyzed. Typos in domain CSV are silently ignored.
5. **Disparate Impact Ratio edge case** â†’ If one group has 0% positive outcomes, ratio = `null`. Don't assume it's always a number.
6. **npm legacy-peer-deps** â†’ Frontend package.json has peer dependency conflicts. Always use `npm install --legacy-peer-deps`.
7. **CORS in production** â†’ Current setup allows any origin. Restrict to frontend URL before shipping.

## Key Files to Read When Debugging

1. **"API returns wrong structure"** â†’ Check `backend/app/routes/analyze.py` lines 14â€“82 (endpoint responses)
2. **"Bias metrics are wrong"** â†’ Check `backend/app/services/bias_service.py` (Fairlearn integration)
3. **"Gemini explanation missing"** â†’ Check `backend/app/services/gemini_service.py` (API call logic)
4. **"PDF export fails"** â†’ Check `backend/app/services/pdf_generator.py` (ReportLab chart generation)
5. **"Frontend doesn't load"** â†’ Check `frontend/vite.config.js` build config and `frontend/src/App.jsx` layout

## Architecture Notes

- **Stateless backend**: No database. All data processed in-memory, requests are independent.
- **Frontend-driven flow**: Frontend drives the entire interaction (select domain â†’ upload file â†’ show results â†’ export PDF).
- **Lazy bias engine**: Sample datasets loaded on first request to `/api/sample/{domain}`, cached after.
- **Graceful Gemini failures**: If Gemini API unreachable, returns fallback message. Analysis still completes.

## Build & Lint

No formal CI/CD setup. Manual checks:
- Backend: `pip install -r requirements.txt` validates dependencies
- Frontend: `npm run lint` uses ESLint; `npm run build` uses Vite (outputs to `dist/`)
- Tests: `run_tests.ps1` or `run_tests.sh` manually test API endpoints

## References

- **Fairlearn metrics**: https://fairlearn.org/ (Demographic Parity, Equalized Odds, Disparate Impact)
- **FastAPI docs**: Auto-generated at `http://localhost:8000/docs` (Swagger UI)
- **Gemini API**: https://ai.google.dev/

