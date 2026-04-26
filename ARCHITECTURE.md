# FairScan Architecture

Technical reference for the current FairScan codebase.

---

## 1) System Overview

FairScan is a desktop-first bias auditing SaaS with two independently deployable tiers:

- **Frontend**: React 18 + Vite SPA with Firebase Auth (Google sign-in), hosted on Firebase Hosting
- **Backend**: FastAPI service with Firebase Admin SDK token verification, deployed to Cloud Run

Core flow:

1. User signs in via Google (Firebase Auth)
2. Selects an audit domain and uploads a CSV
3. Backend validates input, computes Fairlearn-based fairness metrics
4. Backend requests Gemini explanation text (with graceful fallback)
5. Frontend renders metrics, charts, and AI explanation
6. User can export a styled PDF report

---

## 2) Runtime Architecture

```text
Browser (React SPA)
  |
  | HTTP + Bearer token (authenticatedFetch)
  v
FastAPI backend (/api/*)
  |- auth_middleware.py         (Firebase token verification)
  |- firebase_admin_init.py     (Firebase Admin SDK bootstrap)
  |- app/routes/analyze.py      (endpoints)
  |- app/services/bias_service.py
  |- app/services/gemini_service.py
  |- app/services/pdf_generator.py
  `- app/domain_config.py
```

---

## 3) Authentication

### 3.1 Frontend Auth

- `frontend/src/firebase.js`
  - Initializes Firebase app from `VITE_FIREBASE_*` env vars
  - Exports `auth` instance and `GoogleAuthProvider`

- `frontend/src/AuthContext.jsx`
  - React Context providing `{ user, login, logout, loading }`
  - `login()` → `signInWithPopup` (Google)
  - `logout()` → `signOut`
  - Listens to `onAuthStateChanged` for session persistence

- `frontend/src/ProtectedRoute.jsx`
  - Wraps dashboard; redirects to `/login` when unauthenticated

- `frontend/src/api.js`
  - `authenticatedFetch(url, options)` wrapper
  - Attaches `Authorization: Bearer <idToken>` to every request
  - Auto-sets `Content-Type: application/json` for non-FormData bodies

- `frontend/src/pages/Login.jsx`
  - Full-page Google sign-in UI with branded design
  - Redirects to original path after successful login

### 3.2 Backend Auth

- `backend/auth_middleware.py`
  - FastAPI dependency `verify_token()`
  - Extracts Bearer token from `Authorization` header
  - Verifies via `firebase_admin.auth.verify_id_token()`
  - Returns `uid` on success; raises 401 on failure

- `backend/firebase_admin_init.py`
  - `init_firebase()` — idempotent Firebase Admin init
  - Credential resolution order:
    1. `FIREBASE_SERVICE_ACCOUNT_JSON` env var (base64 or raw JSON)
    2. Local `serviceAccountKey.json` file
    3. Application Default Credentials (Cloud Run)

---

## 4) Backend Architecture

### 4.1 Entry Point

- `backend/main.py`
  - Initializes FastAPI app (title: "Veritas API", v1.0.0)
  - CORS middleware for local dev + production origins
  - Registers router under `/api`
  - Exposes `GET /` and `GET /health`

### 4.2 Router

- `backend/app/routes/analyze.py`

Endpoints:

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/api/domains` | No | Returns available domains and config |
| `POST` | `/api/analyze` | Yes (Bearer) | Accepts CSV + domain, returns bias metrics + explanation |
| `POST` | `/api/export` | No | Accepts bias results JSON, returns PDF stream |

### 4.3 Services

- `backend/app/services/bias_service.py`
  - `detect_bias(df, domain)` — main analysis function
  - Validates outcome column and protected attributes exist in CSV
  - For each protected attribute computes:
    - **Demographic Parity Difference** (via Fairlearn)
    - **Equalized Odds Difference** (custom TPR-based: `max(TPR) - min(TPR)`)
    - **Group selection rates** (percent of positive outcomes per group)
    - **Disparate Impact Ratio** (`min_rate / max_rate`)
  - Determines bias severity per attribute (`High`, `Medium`, `Low`)
  - Returns `equalized_odds_tpr_by_group` per attribute for debugging

- `backend/app/services/gemini_service.py`
  - Initializes Gemini client from `GEMINI_API_KEY`
  - Dynamically selects preferred available model
  - Produces concise natural-language explanation
  - Handles API/model/quota failures with fallback messages

- `backend/app/services/pdf_generator.py`
  - Builds PDF via ReportLab with dark-themed styling
  - Generates bar charts and donut charts via Matplotlib (`Agg` backend)
  - All temporary chart images written to a `tempfile.mkdtemp()` dir
  - Cleanup via `shutil.rmtree()` in `finally` block
  - Registers DejaVuSans font for Unicode support when available

### 4.4 Domain Configuration

- `backend/app/domain_config.py`
  - Single source of truth for supported domains
  - Current domains: `hiring`, `loan`, `healthcare`, `education`
  - Each domain defines:
    - `description`
    - `protected_attributes` (list)
    - `outcome_column`
    - `positive_outcome`

---

## 5) Frontend Architecture

### 5.1 Routing

- `frontend/src/App.jsx` — top-level component

```text
BrowserRouter
  ├── /login     → Login page (public)
  └── /          → ProtectedRoute → DashboardPage
```

### 5.2 DashboardPage (Screen Orchestration)

Lives inside `App.jsx`. Manages top-level state:

- Selected domain, uploaded file, CSV preview rows
- Analysis response, screen mode, errors, busy flag
- Results transition animation timer

Screen modes: `workspace` | `loading` | `results`

Key actions:
- `refreshDomains()` — fetches domain list from backend
- `runAnalysis()` — sends CSV + domain to `/api/analyze`
- `exportReport()` — sends results to `/api/export`, triggers PDF download
- `resetAudit()` — returns to workspace, clears analysis state

### 5.3 Dashboard Views

- `WorkspaceView.jsx`
  - Domain selection cards with icons (Briefcase, DollarSign, Heart, BookOpen)
  - CSV upload zone with drag/drop hint and file preview table
  - Run analysis button panel with validation hints
  - Domain card skeletons during loading

- `LoadingView.jsx` + `LoadingStep.jsx`
  - Staged analysis progress UI with animated step indicators

- `ResultsView.jsx`
  - Per-attribute metric cards with severity badges
  - Group-rate bar charts via `MetricsChart`
  - DIR status chips via `DisparateImpactStatus`
  - Collapsible AI explanation sidebar (`aiSidebarOpen` toggle)
  - PDF export and "New Audit" actions

- `TopNav.jsx`
  - Sticky header with brand logo, nav tabs (Workspace / Results)
  - Results tab disabled until analysis exists
  - User avatar + name display, sign-out button
  - Uses `useAuth()` for user info and logout

### 5.4 Shared UI Components

- `MetricsChart.jsx` — group outcome rate comparison bar chart (Recharts)
- `GeminiExplanation.jsx` — parses and renders AI explanation with section splitting and `react-markdown`
- `DisparateImpactStatus.jsx` — standardized status chip (`Biased`/`Fair`/`Perfect`/`N/A`)
- `disparateImpact.js` — shared DIR thresholds and helpers
- `MetricCard.jsx` — reusable label + large-value display card
- `SkeletonBlock.jsx` — animated pulse placeholder for loading states
- `config.js` — severity style map (`High`/`Medium`/`Low` → colors, glows)

---

## 6) Data Contracts

### 6.1 `/api/analyze` response shape

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
        "equalized_odds_tpr_by_group": {
          "Male": 0.7654,
          "Female": 0.6632
        },
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

### 6.2 `/api/export` request shape

```json
{
  "bias_results": { "...": "..." },
  "gemini_explanation": "..."
}
```

Response: `application/pdf` stream.

---

## 7) Bias Logic

### 7.1 Metric Computation (backend)

Within each protected attribute:

- `dpd = demographic_parity_difference(y_true, y_pred, sensitive_features)`
  - Uses Fairlearn library
  - `y_pred` falls back to `y_true` when no `prediction` column exists
- `eod = max(TPR per group) - min(TPR per group)`
  - Custom implementation in `_compute_equalized_odds_difference()`
  - "Qualified" mask determined by `_select_qualified_mask()`:
    1. `credit_score >= 650` when that column exists
    2. Otherwise top 40% by first available numeric feature
    3. Fallback: all rows treated as qualified
- `group_selection_rates` computed as percent values
- `dir_value = min_rate / max_rate` when valid

DIR is set to `null` when rates do not allow safe ratio computation.

### 7.2 Severity Classification (backend)

- `High` if `dir_value < 0.8`
- else `Medium` if `abs(dpd) > 0.1`
- else `Low`

### 7.3 DIR Status Classification (frontend)

Shared in `frontend/src/components/disparateImpact.js`:

- `< 0.80` => `Biased`
- `0.80-0.99` => `Fair`
- `>= 1.00` => `Perfect`
- invalid/missing => `N/A`

Target label displayed in UI: `Target: at least 0.80`

---

## 8) Validation and Error Handling

### Backend validations

- Reject non-CSV uploads (`.csv` extension required)
- Enforce max upload size (10MB, double-checked after read)
- Validate domain key exists in `DOMAIN_CONFIG`
- Validate outcome column exists in CSV
- Validate at least one configured protected attribute exists

### Fallback behavior

- Gemini explanation failures do not fail analysis response
- PDF generation errors return HTTP 500 with error detail

### Frontend behavior

- Protected routes require user login (redirect to `/login`)
- Guards against analyze without domain/file selected
- Displays backend `detail` when available
- Resets busy/error state per action cycle

---

## 9) Deployment Topology

- **Frontend**: Firebase Hosting
  - Config in `firebase.json`
  - Public dir: `frontend/dist`
  - SPA rewrite: `** → /index.html`
  - Cache headers: `no-cache` for `index.html`, immutable for `/assets/**`
- **Backend**: Cloud Run (Dockerfile: `python:3.11-slim` + Uvicorn on port 8080)
- **Production CORS origins**:
  - `https://veritas-ai-01.web.app`
  - `https://veritas-ai-01.firebaseapp.com`

---

## 10) Key Files

### Backend

- `backend/main.py` — FastAPI app init + CORS + router
- `backend/auth_middleware.py` — Bearer token verification
- `backend/firebase_admin_init.py` — Firebase Admin SDK bootstrap
- `backend/app/routes/analyze.py` — API endpoints
- `backend/app/domain_config.py` — domain definitions
- `backend/app/services/bias_service.py` — Fairlearn metric computation
- `backend/app/services/gemini_service.py` — AI explanation generation
- `backend/app/services/pdf_generator.py` — PDF report builder

### Frontend

- `frontend/src/main.jsx` — React entry point
- `frontend/src/App.jsx` — routing + dashboard orchestration
- `frontend/src/firebase.js` — Firebase client init
- `frontend/src/AuthContext.jsx` — auth context provider
- `frontend/src/ProtectedRoute.jsx` — auth route guard
- `frontend/src/api.js` — authenticated HTTP wrapper
- `frontend/src/pages/Login.jsx` — Google sign-in page
- `frontend/src/components/dashboard/WorkspaceView.jsx`
- `frontend/src/components/dashboard/LoadingView.jsx`
- `frontend/src/components/dashboard/LoadingStep.jsx`
- `frontend/src/components/dashboard/ResultsView.jsx`
- `frontend/src/components/dashboard/TopNav.jsx`
- `frontend/src/components/dashboard/MetricCard.jsx`
- `frontend/src/components/dashboard/SkeletonBlock.jsx`
- `frontend/src/components/dashboard/config.js`
- `frontend/src/components/GeminiExplanation.jsx`
- `frontend/src/components/MetricsChart.jsx`
- `frontend/src/components/DisparateImpactStatus.jsx`
- `frontend/src/components/disparateImpact.js`

---

## 11) Known Constraints

- Backend bias analysis is stateless; uploaded CSVs are not persisted
- Domain config is static and defined in code
- `equalized_odds_difference` uses a custom TPR-based implementation, not Fairlearn's built-in
- Qualified mask heuristic may not suit all domains (relies on `credit_score` or first numeric column)
- Frontend still displays "Veritas" branding in Login and TopNav
