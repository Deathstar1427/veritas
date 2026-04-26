# Veritas Architecture

Technical reference for the current production-oriented Veritas implementation.

---

## 1) System Overview

Veritas is a two-tier web application:

- Frontend: React + Vite SPA (hosted on Firebase Hosting)
- Backend: FastAPI API service (Cloud Run/local Uvicorn)

Core flow:

1. User selects domain and uploads CSV (or chooses sample dataset)
2. Backend validates input and computes fairness metrics
3. Backend requests Gemini explanation text (with fallback behavior)
4. Frontend renders metrics + explanation + recommendations
5. User can export a PDF report

---

## 2) Runtime Architecture

```text
Browser (React SPA)
  |
  | HTTP (Axios)
  v
FastAPI backend (/api/*)
  |- routes/analyze.py
  |- services/bias_service.py
  |- services/bias_engine.py
  |- services/gemini_service.py
  |- services/pdf_generator.py
  `- domain_config.py
```

Frontend and backend are independently deployable.

---

## 3) Backend Architecture

### 3.1 Entry Point

- `backend/main.py`
  - Initializes FastAPI app
  - Configures CORS for local + deployed frontend origins
  - Registers router under `/api`
  - Exposes `/` and `/health`

### 3.2 Router

- `backend/app/routes/analyze.py`

Endpoints:

- `GET /api/domains`
- `POST /api/analyze`
- `GET /api/sample-datasets`
- `GET /api/sample/{domain}`
- `POST /api/export`

### 3.3 Services

- `backend/app/services/bias_service.py`
  - Validates required outcome/protected columns
  - Computes:
    - Demographic Parity Difference
    - Equalized Odds Difference
    - Group selection rates
    - Disparate Impact Ratio
  - Computes bias severity (`High`, `Medium`, `Low`)

- `backend/app/services/bias_engine.py`
  - Loads domain sample CSV from `backend/sample_data`
  - Caches analyzed sample results in module-level `_sample_cache`

- `backend/app/services/gemini_service.py`
  - Initializes Gemini client from `GEMINI_API_KEY`
  - Chooses preferred available model dynamically when possible
  - Produces concise natural-language explanation
  - Handles API/model/quota failures with fallback messages

- `backend/app/services/pdf_generator.py`
  - Builds PDF via ReportLab
  - Generates charts via Matplotlib (non-interactive backend)
  - Embeds metrics and explanation in report

### 3.4 Domain Configuration

- `backend/app/domain_config.py`
  - Single source of truth for domains
  - Defines for each domain:
    - `description`
    - `protected_attributes`
    - `outcome_column`
    - `positive_outcome`

---

## 4) Frontend Architecture

### 4.1 Root and Screen Orchestration

- `frontend/src/App.jsx`

Main responsibilities:

- Fetches domains from backend
- Manages top-level state:
  - selected domain, uploaded file, preview rows
  - analysis response, screen mode, errors, busy flag
- Routes between screen views:
  - `workspace`
  - `loading`
  - `results`
  - `history`
- Handles CSV analyze and sample analyze actions
- Handles PDF export request

### 4.2 Dashboard Views

- `frontend/src/components/dashboard/WorkspaceView.jsx`
  - Domain selection cards
  - CSV upload and preview
  - Run analysis actions

- `frontend/src/components/dashboard/LoadingView.jsx`
  - Analysis progress UI and staged loading indicators

- `frontend/src/components/dashboard/ResultsView.jsx`
  - Per-attribute metric cards
  - Group-rate chart blocks via `MetricsChart`
  - Shared DIR label/status rendering
  - Collapsible AI sidebar (`aiSidebarOpen`)
  - Responsive grid (`md:grid-cols-12`), stacked on small screens

- `frontend/src/components/dashboard/HistoryView.jsx`
  - Report-style printable view
  - PDF download trigger
  - Recent audit cards

- `frontend/src/components/dashboard/TopNav.jsx`
  - Workspace/results/history navigation
  - Results/history disabled until analysis exists

### 4.3 Shared Frontend Components

- `frontend/src/components/MetricsChart.jsx`
  - Renders group outcome rate comparison bars
  - Shows DIR value + shared status chip

- `frontend/src/components/GeminiExplanation.jsx`
  - Splits explanation into sections when headings are present
  - Renders markdown content via `react-markdown`

- `frontend/src/components/DisparateImpactStatus.jsx`
  - Displays standardized status chip (`Biased`/`Fair`/`Perfect`/`N/A`)

- `frontend/src/components/disparateImpact.js`
  - Shared DIR thresholds and helpers:
    - `disparateImpactTargetLabel`
    - `getDisparateImpactLabel`
    - `isDisparateImpactPassing`

---

## 5) Data Contracts

### 5.1 `/api/analyze` and `/api/sample/{domain}` response shape

```json
{
  "status": "success",
  "results": {
    "domain": "hiring",
    "total_records": 500,
    "outcome_column": "hired",
    "attributes_analyzed": ["gender", "age_group"],
    "bias_metrics": {
      "gender": {
        "groups": ["Male", "Female"],
        "demographic_parity_difference": 0.1234,
        "equalized_odds_difference": 0.1022,
        "disparate_impact_ratio": 0.78,
        "group_selection_rates": {
          "Male": 63.5,
          "Female": 47.5
        },
        "bias_severity": "High"
      }
    }
  },
  "explanation": "..."
}
```

### 5.2 `/api/export` request shape

```json
{
  "bias_results": { "...": "..." },
  "gemini_explanation": "..."
}
```

Response: `application/pdf` stream.

---

## 6) Bias Logic

### 6.1 Metric Computation (backend)

Within each protected attribute:

- `dpd = demographic_parity_difference(...)`
- `eod = equalized_odds_difference(...)`
- `group_selection_rates` computed as percent values
- `dir_value = min_rate / max_rate` when valid

DIR is set to `null` when rates do not allow safe ratio computation.

### 6.2 Severity Classification (backend)

- `High` if `dir_value < 0.8`
- else `Medium` if `abs(dpd) > 0.1`
- else `Low`

### 6.3 DIR Status Classification (frontend)

Shared in `frontend/src/components/disparateImpact.js`:

- `< 0.80` => `Biased`
- `0.80-0.99` => `Fair`
- `>= 1.00` => `Perfect`
- invalid/missing => `N/A`

Target label displayed in UI:

- `Target: at least 0.80`

---

## 7) Validation and Error Handling

### Backend validations

- Reject non-CSV uploads (`.csv` extension required)
- Enforce max upload size (10MB)
- Validate domain key exists in `DOMAIN_CONFIG`
- Validate outcome column exists in CSV
- Validate at least one configured protected attribute exists

### Fallback behavior

- Gemini explanation failures do not fail analysis response
- PDF generation errors return HTTP 500 with error detail

### Frontend behavior

- Guards against analyze without domain/file
- Displays backend `detail` when available
- Resets busy/error state per action cycle

---

## 8) Deployment Topology

- Frontend static assets: Firebase Hosting
  - Config in `firebase.json`
  - Public dir: `frontend/dist`
- Backend API: Cloud Run (or local Uvicorn)
- Production frontend URL currently allowed in backend CORS:
  - `https://veritas-ai-01.web.app`
  - `https://veritas-ai-01.firebaseapp.com`

---

## 9) Key Files

### Backend

- `backend/main.py`
- `backend/app/routes/analyze.py`
- `backend/app/domain_config.py`
- `backend/app/services/bias_service.py`
- `backend/app/services/bias_engine.py`
- `backend/app/services/gemini_service.py`
- `backend/app/services/pdf_generator.py`

### Frontend

- `frontend/src/App.jsx`
- `frontend/src/components/dashboard/WorkspaceView.jsx`
- `frontend/src/components/dashboard/LoadingView.jsx`
- `frontend/src/components/dashboard/ResultsView.jsx`
- `frontend/src/components/dashboard/HistoryView.jsx`
- `frontend/src/components/GeminiExplanation.jsx`
- `frontend/src/components/MetricsChart.jsx`
- `frontend/src/components/DisparateImpactStatus.jsx`
- `frontend/src/components/disparateImpact.js`

---

## 10) Known Constraints

- Backend is stateless and in-memory; no persistent audit history
- Sample result cache is process-local (not shared across instances)
- Frontend report history is session-derived from current analysis
- PDF chart generation writes temporary image files by name during build
