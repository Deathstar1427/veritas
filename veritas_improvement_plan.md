# Veritas — Full Improvement Plan

> Hackathon: Solution Challenge 2026 · Unbiased AI Decision theme  
> Current estimated score: **72.5 / 100**  
> Target after improvements: **90+ / 100**

---

## Summary

| Phase | Items | Effort | Est. Points Gained |
|---|---|---|---|
| Phase 1 — Tonight (before Apr 28 deadline) | 5 | 4–6 hrs | +20 |
| Phase 2 — High impact (next few days) | 7 | 2–3 days | +29 |
| Phase 3 — Future roadmap (for pitch/post-hackathon) | 6 | — | mention in deck |

---

## Phase 1 — Do Tonight (Critical, before Apr 28 11:59 PM IST)

### 1. Add remediation suggestions to the Gemini prompt
**Score impact:** +8 pts on Alignment With Cause (25%)

The hackathon objective literally says "flag **and fix**." Right now Veritas only flags. Update your Gemini prompt to also return 3 concrete fix recommendations per attribute.

**What to do:**

In `backend/app/services/gemini_service.py`, append to your existing prompt:

```
Also suggest 3 concrete remediation steps to reduce the detected bias.
Format as:
REMEDIATION:
1. [step one]
2. [step two]  
3. [step three]
```

Then parse the `REMEDIATION:` block in your response handler and pass it to the frontend alongside the explanation. Display it as a separate "How to fix this" section in the AI sidebar (`GeminiExplanation.jsx`).

No new API endpoints needed — this is a pure prompt + display change.

---

### 2. Add a one-click sample dataset demo on the workspace page
**Score impact:** +4 pts on User Experience (10%)

Judges who can't figure out the app in 60 seconds move on. You already have `/api/sample/{domain}` and an `onSampleAnalyze` handler in `App.jsx`. Just wire it to a visible button on the landing state.

**What to do:**

In `frontend/src/components/dashboard/WorkspaceView.jsx`, add a prominent button:

```jsx
<button onClick={() => onSampleAnalyze('hiring')}>
  Try a sample — Hiring dataset
</button>
```

Add three buttons for hiring, loan, and healthcare. Label them clearly: "No CSV? Try a sample dataset." Place them below the upload zone so the primary action is still upload, but the fallback is obvious.

---

### 3. Add ARIA labels to chart canvases and navigation elements
**Score impact:** +2 pts on UX Accessibility sub-criterion

Accessibility is explicitly listed under the UX scoring criteria. This is a 20-minute change.

**What to do:**

In `frontend/src/components/MetricsChart.jsx`:

```jsx
<canvas
  role="img"
  aria-label={`Bar chart showing ${attribute} group outcome rates. ${Object.entries(groupRates).map(([g, r]) => `${g}: ${r}%`).join(', ')}`}
/>
```

In `frontend/src/components/dashboard/TopNav.jsx`:

```jsx
<a aria-current={activeView === 'workspace' ? 'page' : undefined}>
  Workspace
</a>
```

Also add `alt=""` to any decorative images and ensure all interactive buttons have descriptive text (not just icons).

---

### 4. Clean up git history with meaningful commits
**Score impact:** +3 pts on Technical Merit (impression on judges)

3 commits total is a red flag. It signals the project was assembled quickly. Break your history into at least 8–10 meaningful commits with descriptive messages using interactive rebase.

**What to do:**

```bash
git rebase -i --root
# Mark each commit as 'reword' or 'edit' to split/rename
```

Suggested commit message structure:

```
feat: initialize FastAPI backend with health and domain endpoints
feat: add Fairlearn bias metrics (DPD, EOD, DIR) via bias_service
feat: integrate Google Gemini for plain-language explanations
feat: add Firebase Auth with token verification middleware
feat: add PDF export endpoint using ReportLab and Matplotlib
feat: add sample dataset endpoints with module-level cache
feat: build React + Vite frontend with workspace and results views
feat: add collapsible AI explanation sidebar with markdown support
fix: graceful Gemini fallback on API quota or key failures
docs: add ARCHITECTURE.md technical reference and README setup guide
```

---

### 5. Add a "Roadmap" section to the README
**Score impact:** +3 pts on Innovation / Future Potential sub-criterion

Future Potential is an explicit sub-criterion under Innovation (25%). Judges read your README. Add a roadmap section — it takes 15 minutes and directly maps to points.

**What to add in `README.md`:**

```markdown
## Roadmap

The following features are planned for future iterations:

- [ ] **What-If threshold simulator** — adjust decision thresholds live and see how DPD/EOD/DIR change in real time
- [ ] **Proxy column detector** — automatically identify non-protected columns that correlate strongly with protected attributes
- [ ] **Custom column mapping** — support any CSV schema, not just the 4 pre-defined domains
- [ ] **Auto-generated model cards** — produce Hugging Face-format model cards directly from audit results
- [ ] **Real-time model monitoring** — REST endpoint for CI/CD pipelines to audit models on every training run
- [ ] **Regulatory compliance mapping** — map results to EU AI Act, EEOC, and ECOA standards
- [ ] **Audit history persistence** — store and compare audits over time via Firestore
- [ ] **NLP and image bias detection** — extend beyond tabular data to text classifiers and vision models
- [ ] **Team collaboration** — share audits, add comments, assign remediation owners
- [ ] **Public audit API** — expose fairness checks as a developer API with key-based auth
```

---

## Phase 2 — High Impact (Next Few Days)

### 6. Build the What-If threshold simulator
**Score impact:** +6 pts on Innovation (25%)

This is the single feature that most differentiates Veritas from existing tools like IBM AI Fairness 360. All computation can happen client-side — no API changes needed.

**What to do:**

In `ResultsView.jsx`, add a slider per attribute. The `group_selection_rates` are already returned in the API response. Use them to recompute DIR live as the threshold changes:

```jsx
// For each attribute card, add:
const [threshold, setThreshold] = useState(0.5);

// Recompute adjusted rates at threshold
const adjustedRates = Object.fromEntries(
  Object.entries(groupRates).map(([group, rate]) => [
    group,
    Math.min(100, rate * (threshold / 0.5)) // simplified adjustment
  ])
);

const adjustedDIR = Math.min(...Object.values(adjustedRates)) /
                    Math.max(...Object.values(adjustedRates));

// Render slider and live DisparateImpactStatus chip
<input type="range" min={0.1} max={0.9} step={0.01}
  value={threshold} onChange={e => setThreshold(+e.target.value)} />
<DisparateImpactStatus dir={adjustedDIR} />
```

---

### 7. Add a proxy column detector
**Score impact:** +6 pts on Innovation + Technical Merit

A genuine technical contribution. After bias is detected, compute the correlation of each non-protected column with the protected attribute and surface the top 3 likely proxies. This is insight that auditors miss in practice and something no drag-and-drop fairness tool does automatically.

**What to do:**

In `backend/app/services/bias_service.py`, add after bias computation:

```python
def detect_proxy_columns(df, protected_attr, outcome_col, protected_attrs):
    proxies = {}
    for col in df.columns:
        if col in protected_attrs or col == outcome_col:
            continue
        try:
            # Encode if categorical
            a = pd.Categorical(df[col]).codes if df[col].dtype == object else df[col]
            b = pd.Categorical(df[protected_attr]).codes if df[protected_attr].dtype == object else df[protected_attr]
            corr = abs(a.corr(b))
            if not pd.isna(corr):
                proxies[col] = round(float(corr), 3)
        except Exception:
            continue
    top = sorted(proxies.items(), key=lambda x: x[1], reverse=True)[:3]
    return [{"column": col, "correlation": corr} for col, corr in top]
```

Add the result to the `/api/analyze` response under `proxy_columns`. Display in the results dashboard as a "Likely proxy columns" warning card.

---

### 8. Add custom column mapping for arbitrary CSVs
**Score impact:** +5 pts on Technical Merit + Alignment

Currently only CSVs with exact column names matching the 4 domain configs work. This limits real-world usefulness significantly.

**What to do:**

1. Parse the CSV header row client-side after file selection:

```jsx
const headers = csvText.split('\n')[0].split(',').map(h => h.trim());
setAvailableColumns(headers);
setShowMapping(true);
```

2. Add a mapping step in `WorkspaceView.jsx` with two dropdowns:
   - "Which column is the outcome?" (select one)
   - "Which columns are protected attributes?" (select multiple)

3. Send these as additional fields to `/api/analyze`:

```python
# In analyze.py route — accept optional overrides:
outcome_col: Optional[str] = Form(None)
protected_attrs: Optional[str] = Form(None)  # comma-separated
```

4. In `bias_service.py`, prefer the user-supplied columns over the domain config defaults.

---

### 9. Persist audit history to Firestore
**Score impact:** +3 pts on UX + Technical Merit

The `HistoryView` loses everything on reload. Since Firebase is already set up, Firestore is one import away.

**What to do:**

In `frontend/src/firebase.js`, add:

```js
import { getFirestore } from 'firebase/firestore';
export const db = getFirestore(app);
```

On analysis success in `App.jsx`:

```js
import { collection, addDoc, serverTimestamp } from 'firebase/firestore';

await addDoc(collection(db, 'audits'), {
  uid: user.uid,
  timestamp: serverTimestamp(),
  domain: selectedDomain,
  filename: uploadedFile.name,
  totalRecords: results.total_records,
  severityCounts: {
    high: Object.values(results.bias_metrics).filter(m => m.bias_severity === 'High').length,
    medium: Object.values(results.bias_metrics).filter(m => m.bias_severity === 'Medium').length,
    low: Object.values(results.bias_metrics).filter(m => m.bias_severity === 'Low').length,
  }
});
```

In `HistoryView.jsx`, query the user's last 10 audits on mount and render them as cards.

---

### 10. Add API rate limiting and input sanitization
**Score impact:** +3 pts on Security & Privacy sub-criterion

Security & Privacy is an explicit sub-criterion of Technical Merit (40%).

**What to do:**

```bash
pip install slowapi
```

In `backend/main.py`:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

In `backend/app/routes/analyze.py`:

```python
@router.post("/analyze")
@limiter.limit("20/minute")
async def analyze(request: Request, file: UploadFile = File(...), ...):
    # Validate file extension
    if not file.filename.endswith('.csv'):
        raise HTTPException(400, "Only CSV files are accepted")
    
    # Validate file size (already done, keep it)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(413, "File exceeds 10MB limit")
    
    # Validate parseable as CSV
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception:
        raise HTTPException(400, "File could not be parsed as CSV")
```

---

### 11. Add a GitHub Actions CI pipeline
**Score impact:** +2 pts on Technical Complexity sub-criterion

You have a `tests/` folder but no automated runner. Even a minimal pipeline signals engineering discipline.

**What to do:**

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ -v
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}

  frontend-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      - name: Install and build
        run: |
          cd frontend
          npm install --legacy-peer-deps
          npm run build
```

---

### 12. Auto-generate a model card from audit results
**Score impact:** +4 pts on Innovation / Creative Use of Technologies

This is the "Creative Use of Technologies" angle. Offer a "Generate Model Card" button after analysis. Use Gemini to produce a Hugging Face-format model card as a downloadable `.md` file.

**What to do:**

Add a new Gemini prompt in `gemini_service.py`:

```python
async def generate_model_card(bias_results: dict, domain: str) -> str:
    prompt = f"""
Generate a Hugging Face model card in markdown format based on these fairness audit results
for a {domain} prediction model.

Audit results: {json.dumps(bias_results, indent=2)}

Include these sections:
- Model description
- Intended use and out-of-scope uses  
- Bias and fairness evaluation (with a markdown table of metrics)
- Recommendations
- Ethical considerations

Use proper markdown headings. Be specific and cite the actual metric values.
"""
    # Call Gemini and return the markdown string
```

Add a `POST /api/model-card` endpoint that returns the markdown as a downloadable file. In the frontend, add a "Download model card" button in `HistoryView.jsx`.

---

## Phase 3 — Future Roadmap (Mention in Your Pitch Deck)

These are not expected for the prototype submission but should be described in your project deck and README to score on the Future Potential sub-criterion.

| Feature | Why it matters | Tech path |
|---|---|---|
| Real-time model monitoring | CI/CD pipelines call `/api/audit` after each training run | Webhook endpoint + Cloud Run |
| NLP & image bias detection | Extends beyond tabular data | Gemini Vision + text embeddings |
| Regulatory compliance mapping | Maps results to EU AI Act, EEOC, ECOA | Rules engine + compliance DB |
| Team collaboration workspace | Shared audits, comments, remediation owners | Firestore + shared collections |
| Public audit API with keys | Developer-facing product, monetization path | API key management + quotas |
| Configurable severity thresholds | EU cutoffs differ from US 0.80 standard | Per-org config in Firestore |

---

## Priority Order (If Time Is Short)

If you only have 2 hours left before the deadline, do these in order:

1. **Gemini remediation suggestions** — 30 min, backend only, highest points per minute
2. **Sample dataset button** — 15 min, already wired, just add the UI
3. **README roadmap section** — 15 min, pure writing, direct points
4. **Git commit cleanup** — 15 min, big impression impact
5. **ARIA labels** — 20 min, accessibility signals professionalism

The proxy column detector is the best single code contribution if you have an extra hour.

---

*Good luck — the foundation is solid. These additions push Veritas from "good prototype" to "top 30 submission."*
