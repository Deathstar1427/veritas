# Veritas

Upload a dataset, detect fairness risks, and generate plain-language audit guidance.

Veritas is a full-stack fairness auditing web app with a FastAPI backend and a React + Vite frontend. It computes Fairlearn metrics (Demographic Parity Difference, Equalized Odds Difference, Disparate Impact Ratio), classifies severity, generates Gemini-based explanations, and exports PDF reports. The app features Firebase Authentication to secure access to the dashboard.

Live app: `https://veritas-ai-01.web.app`

---

## What It Does

- **Secure Access**: Protected routes and authentication via Firebase Auth (Google Provider).
- **Domains**: Supports four audit domains: hiring, loan, healthcare, education.
- **Analysis**: Accepts uploaded CSV files.
- **Fairness Metrics**: Computes per-attribute fairness metrics using Fairlearn.
- **Severity Classification**: Classifies bias severity (`High` / `Medium` / `Low`).
- **AI Explanations**: Generates explanation text via Google Gemini to summarize bias.
- **Dashboard**:
  - Responsive design with glowing severity chips and cards.
  - Metrics cards and interactive group-rate bar charts.
  - Shared Disparate Impact status labels (`Biased`, `Fair`, `Perfect`).
  - Collapsible AI explanation sidebar with markdown support.
- **Export**: Exports a printable/downloadable PDF report containing the charts, metrics, and AI explanation.

---

## Tech Stack

### Backend
- Python 3.11+
- FastAPI + Uvicorn
- Fairlearn + pandas + scikit-learn
- Google Generative AI SDK (`google-generativeai`)
- ReportLab + Matplotlib (PDF generation, using `tempfile` for safe resource cleanup)
- Firebase Admin SDK (token verification)

### Frontend
- React 19 + Vite 8
- Tailwind CSS 3
- Tremor (visual components)
- Radix Accordion
- Lucide React icons
- react-markdown
- Firebase SDK (Client Auth)

---

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- Gemini API key
- Firebase Project with Authentication (Google) enabled

### 1) Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Set GEMINI_API_KEY in .env
uvicorn main:app --reload
```

Backend URLs:
- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

**Note:** For authentication to work locally, the backend needs access to your Firebase service account (via `FIREBASE_SERVICE_ACCOUNT_JSON` env var or `serviceAccountKey.json` at the project root).

### 2) Frontend

Create a `.env.local` file in `frontend/` containing your Firebase credentials:
```env
VITE_FIREBASE_API_KEY=your_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_auth_domain
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_API_URL=http://localhost:8000
```

```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```

Frontend URL:
- App: `http://localhost:5173`

---

## API Endpoints

### `GET /health`
Returns basic health information.

### `GET /api/domains`
Returns available domains, protected attributes, and outcome columns.

### `POST /api/analyze`
Analyzes uploaded CSV (`multipart/form-data`) with fields:
- `file`: CSV
- `domain`: `hiring | loan | healthcare | education`
- Headers: `Authorization: Bearer <firebase_token>`

Returns:
- `status`
- `results` (bias metrics keyed by attribute)
- `explanation` (Gemini-generated text)

### `POST /api/export`
Generates a PDF report from a JSON payload containing the bias results and Gemini explanation.
Returns a PDF stream as a downloadable file.

### `GET /api/sample/{domain}`
Returns a pre-built sample CSV for the given domain (`hiring`, `loan`, `healthcare`).
Useful for one-click demo functionality. Rate limited to 30 requests per minute.

### `POST /api/model-card`
Generates a Hugging Face-format model card in markdown from the bias audit results.
Requires authentication. Expects:
- `bias_results`: the full results object from `/api/analyze`
- `domain`: the domain name

Returns a downloadable markdown file.

---

## Bias Metrics and Severity

### Metrics
- **Demographic Parity Difference (DPD)**
- **Equalized Odds Difference (EOD)**
- **Disparate Impact Ratio (DIR)**

### Backend severity logic
- `High`: `DIR < 0.80`
- `Medium`: `abs(DPD) > 0.10` (when DIR is not high)
- `Low`: otherwise

### Frontend DIR status labels
- `Biased`: `< 0.80`
- `Fair`: `0.80-0.99`
- `Perfect`: `>= 1.00`

---

## Project Structure

```text
veritas/
├─ backend/
│  ├─ main.py
│  ├─ requirements.txt
│  ├─ auth_middleware.py
│  ├─ firebase_admin_init.py
│  ├─ app/
│  │  ├─ domain_config.py
│  │  ├─ routes/analyze.py
│  │  └─ services/
│  │     ├─ bias_service.py
│  │     ├─ gemini_service.py
│  │     └─ pdf_generator.py
│  └─ sample_datasets/
├─ frontend/
│  ├─ src/
│  │  ├─ App.jsx
│  │  ├─ AuthContext.jsx
│  │  ├─ ProtectedRoute.jsx
│  │  ├─ api.js
│  │  ├─ firebase.js
│  │  ├─ components/
│  │  ├─ pages/Login.jsx
│  │  └─ index.css
│  └─ package.json
├─ tests/
├─ firebase.json
├─ README.md
└─ ARCHITECTURE.md
```

---

## Deploy

Frontend hosting is configured in `firebase.json` with `frontend/dist` as public output.

Typical deploy flow:

```bash
cd frontend
npm run build
cd ..
firebase deploy --only hosting --project veritas-ai-01
```

---

## Notes and Limitations

- **Stateless Backend:** The backend is completely stateless and processes data in-memory. Uploaded CSVs are not persisted to any database.
- **No Database Needed:** While Firebase Auth is used for user authentication, there is no database (like Firestore or PostgreSQL) needed or used to store past audit results.
- **Graceful Degradation:** Gemini failures (e.g., rate limits or invalid keys) are handled gracefully with a fallback explanation text. Bias metrics will still be computed and displayed.

---

## Roadmap

The following features are planned for future iterations:

- [ ] **What-If threshold simulator** — adjust decision thresholds live and see how DPD/EOD/DIR change in real time *(implemented in v1.1)*
- [ ] **Proxy column detector** — automatically identify non-protected columns that correlate strongly with protected attributes *(implemented in v1.1)*
- [ ] **AI remediation suggestions** — Gemini-generated concrete steps to reduce detected bias *(implemented in v1.1)*
- [ ] **Auto-generated model cards** — produce Hugging Face-format model cards directly from audit results *(implemented in v1.1)*
- [ ] **Custom column mapping** — support any CSV schema, not just the 4 pre-defined domains
- [ ] **Real-time model monitoring** — REST endpoint for CI/CD pipelines to audit models on every training run
- [ ] **Regulatory compliance mapping** — map results to EU AI Act, EEOC, and ECOA standards
- [ ] **Audit history persistence** — store and compare audits over time via Firestore
- [ ] **NLP and image bias detection** — extend beyond tabular data to text classifiers and vision models
- [ ] **Team collaboration** — share audits, add comments, assign remediation owners
- [ ] **Public audit API** — expose fairness checks as a developer API with key-based auth
- [ ] **Configurable severity thresholds** — EU cutoffs differ from US 0.80 standard

