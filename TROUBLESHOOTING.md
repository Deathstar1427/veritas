# Troubleshooting Guide for Veritas

> **Solutions to common issues when running or deploying Veritas.**

## Backend Issues

### "ModuleNotFoundError: No module named 'fastapi'"

**Problem:** FastAPI not installed in Python environment

**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

**Check:** Verify installation
```bash
python -c "import fastapi; print(fastapi.__version__)"
```

---

### "GEMINI_API_KEY not set"

**Problem:** Gemini explanations missing from results

**Symptom:**
```
API response: { "status": "success", "results": {...}, "explanation": "Explanation unavailable — check your GEMINI_API_KEY." }
```

**Solution:**

1. **Get API key** from https://ai.google.dev/
2. **Create `.env` file** in `backend/`:
   ```bash
   cp .env.example .env
   ```
3. **Add your key:**
   ```
   GEMINI_API_KEY=sk_YOUR_KEY_HERE
   ```
4. **Restart backend:**
   ```bash
   uvicorn main:app --reload
   ```

**Verify:**
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('GEMINI_API_KEY')[:10])"
```

**Note:** Bias analysis still works without GEMINI_API_KEY. Only AI explanation fails gracefully.

---

### "Port 8000 already in use"

**Problem:** Another service already using port 8000

**Solution (Option 1): Kill existing process**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :8000
kill -9 <PID>
```

**Solution (Option 2): Use different port**
```bash
uvicorn main:app --reload --port 8001
# Then update frontend VITE_API_URL=http://localhost:8001
```

---

### "Uvicorn: Starlette requires Python 3.8+"

**Problem:** Python version too old

**Solution:**
```bash
python --version  # Check version

# If < 3.8, install Python 3.11+:
# Windows: python-3.11.0-amd64.exe from python.org
# macOS: brew install python@3.11
# Linux: apt-get install python3.11
```

---

### "CORS error: Access to XMLHttpRequest blocked"

**Problem:** Frontend can't connect to backend (CORS policy)

**Browser Error:**
```
Access to XMLHttpRequest at 'http://localhost:8000/api/domains' from origin 'http://localhost:5173' has been blocked by CORS policy
```

**Causes:**
1. Backend running on different port than expected
2. CORS not configured for frontend URL
3. Frontend using wrong API URL

**Solution:**

**Step 1:** Verify backend is running
```bash
curl http://localhost:8000/health
# Should return: {"status":"ok","version":"1.0.0"}
```

**Step 2:** Verify frontend API URL
- Check `frontend/.env.local`:
  ```
  VITE_API_URL=http://localhost:8000
  ```
- Or check hardcoded in `frontend/src/App.jsx` (should use env var)

**Step 3:** Verify CORS in backend
- Open `backend/main.py`
- Check `allow_origins` list includes frontend URL:
  ```python
  allow_origins=[
      "http://localhost:5173",  # Local dev
      "http://127.0.0.1:5173",
      # Production:
      # "https://your-domain.com",
  ]
  ```

**Step 4:** Restart both backend and frontend
```bash
# Terminal 1: Backend
cd backend && uvicorn main:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev
```

**Production Fix:**
In `backend/main.py`, update CORS for your domain:
```python
allow_origins=[
    "https://your-domain.com",
    "https://www.your-domain.com",
]
```

---

### "Fairlearn not found" or "fairlearn dependency error"

**Problem:** Fairlearn installation failed or version conflict

**Solution:**
```bash
cd backend
pip install --upgrade fairlearn scikit-learn numpy

# Or reinstall from scratch
pip uninstall fairlearn
pip install fairlearn>=0.9.0
```

**Verify:**
```bash
python -c "from fairlearn.metrics import demographic_parity_difference; print('OK')"
```

---

## Frontend Issues

### "npm ERR! code ERESOLVE"

**Problem:** npm peer dependency conflict

**Solution:**
```bash
cd frontend
npm install --legacy-peer-deps
```

**Explanation:** React 19 has peer dependency mismatches with some packages. `--legacy-peer-deps` uses old resolution algorithm.

---

### "Cannot find module 'react' or other packages"

**Problem:** npm packages not installed

**Solution:**
```bash
cd frontend
npm install --legacy-peer-deps

# Or clean reinstall
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

---

### "Port 5173 already in use"

**Problem:** Vite dev server port occupied

**Solution:**
```bash
# Kill existing process
# Windows
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Or use different port
npm run dev -- --port 5174
```

---

### "VITE_API_URL is undefined"

**Problem:** Frontend can't reach backend API

**Symptom:** 
```
"API request failed: GET http://undefined/api/domains"
```

**Causes:**
1. `.env.local` not set
2. Env variable not loaded by Vite
3. Typo in env var name

**Solution:**

**Step 1:** Create `frontend/.env.local`:
```
VITE_API_URL=http://localhost:8000
```

**Step 2:** Verify Vite sees it:
```bash
cd frontend
npm run dev
# Look for: VITE_API_URL loaded
```

**Step 3:** Check code uses it correctly:
In components, should use:
```javascript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
```

**Production:**
Create `frontend/.env.production`:
```
VITE_API_URL=https://api.your-domain.com
```

Then rebuild:
```bash
npm run build
```

---

### "Blank screen or components not rendering"

**Problem:** React not rendering components

**Causes:**
1. JavaScript error in console
2. Missing CSS/styling
3. React root not mounted

**Solution:**

**Step 1:** Check browser console for errors
- Open DevTools (F12 or right-click → Inspect)
- Check Console tab for errors
- Fix error and retry

**Step 2:** Verify React root exists
- In `frontend/index.html`, check:
  ```html
  <div id="root"></div>
  <script type="module" src="/src/main.jsx"></script>
  ```

**Step 3:** Verify CSS loads
- Check if styling is broken (all elements unstyled)
- Check `App.css` and `index.css` in Sources tab
- If missing, rebuild: `npm run build`

**Step 4:** Check for API errors
- Open DevTools Network tab
- Try uploading a file
- Check if `/api/analyze` returns 200 or error
- If error, see Backend Issues above

---

### "Charts not displaying (blank area where chart should be)"

**Problem:** Tremor charts failing to render

**Causes:**
1. Data format wrong
2. Tremor component misconfigured
3. Browser doesn't support chart library

**Solution:**

**Step 1:** Check data format in Network tab
- POST to `/api/analyze`
- Check response JSON for `results.attributes` structure
- Should be array of objects with `groups`, `severity`, etc.

**Step 2:** Verify Tremor is installed
```bash
cd frontend
npm list @tremor/react
# Should show @tremor/react@3.18.7
```

**Step 3:** Check for errors in console
- DevTools Console tab
- Look for Tremor-related errors
- Fix and retry

---

### "Export PDF button not working"

**Problem:** PDF download fails or doesn't trigger

**Symptom:**
- Button clicked but nothing happens
- Or error message appears

**Causes:**
1. Backend `/api/export` endpoint failing
2. File too large (Blob handling)
3. Browser security (cross-origin, downloads blocked)

**Solution:**

**Step 1:** Check backend is working
```bash
curl -X POST http://localhost:8000/api/export \
  -H "Content-Type: application/json" \
  -d '{"bias_results": {...}, "gemini_explanation": "..."}'
```

If fails, check backend logs for errors.

**Step 2:** Check browser allows downloads
- Settings → Privacy & Security → Files → Allow downloads from [site]
- Some corporate networks block downloads

**Step 3:** Check browser console for errors
- DevTools Console
- Look for CORS errors, network errors, etc.

**Step 4:** Verify response headers
- Network tab → POST to `/api/export`
- Response headers should include:
  ```
  Content-Type: application/pdf
  Content-Disposition: attachment; filename=fairscan_report.pdf
  ```

---

## Data & Analysis Issues

### "CSV upload returns error: 'Missing required columns'"

**Problem:** Uploaded CSV doesn't have required columns

**Cause:** Wrong domain selected or CSV headers misnamed

**Solution:**

**Step 1:** Verify domain matches data
- HIRING: needs `hired` column
- LOAN: needs `approved` column
- HEALTHCARE: needs `diagnosis_positive` column
- EDUCATION: needs `admitted` column

**Step 2:** Verify column names match exactly
- Check spelling (case-sensitive)
- No extra spaces
- Rename in CSV if needed

**Step 3:** Check column exists in CSV
- Open CSV in text editor or Excel
- Verify first row has column headers
- Verify outcome column name is correct

**Example fix:**

❌ **Before:** CSV has `hire` instead of `hired`
```csv
hire,gender,age_group
1,Female,30-40
```

✅ **After:** Renamed to correct column
```csv
hired,gender,age_group
1,Female,30-40
```

---

### "Analysis results show very low/high bias for all attributes"

**Problem:** All attributes get HIGH or LOW severity (suspicious uniformity)

**Causes:**
1. CSV doesn't have prediction/outcome properly encoded
2. All groups have identical outcomes (no variation)
3. Data quality issue (all 1s or all 0s)

**Solution:**

**Step 1:** Check outcome column distribution
- Count rows where outcome = 0 and outcome = 1
- Should be both present (not all 1s or all 0s)
- If all same: data quality issue

**Example:**
```python
import pandas as pd
df = pd.read_csv('data.csv')
print(df['hired'].value_counts())
# Output should be: 0: 250, 1: 250 (or similar split, not 0: 0, 1: 500)
```

**Step 2:** Check protected attributes have variation
- Verify multiple groups in each protected attribute column
- If only one group present: won't show bias (nothing to compare)

```python
print(df['gender'].value_counts())
# Output should be: Female: 250, Male: 250 (or similar split)
```

**Step 3:** Verify data makes sense
- Sample a few rows
- Confirm outcomes and attributes are reasonable
- If suspicious, investigate source data

---

### "Gemini explanation is vague or unhelpful"

**Problem:** AI explanation doesn't clearly identify bias root causes

**Causes:**
1. Prompt too generic (backend sends raw metrics)
2. Bias complexity (multiple factors)
3. Gemini misunderstands metrics

**Solution:**

**Step 1:** Check metrics are clear first
- Look at raw bias results before explanation
- If metrics are confusing, explanation will be too
- Try CSV_FORMAT_GUIDE.md for better data quality

**Step 2:** Provide better context in your data
- Add columns that might explain bias (experience, education, qualifications)
- This gives Gemini more context for explanation

**Step 3:** Report issue
- If Gemini is consistently unhelpful, file issue
- Include sample data (anonymized) and explanation
- Backend maintainers can improve prompt

---

### "Sample data analysis returns error"

**Problem:** `/api/sample/{domain}` endpoint fails

**Cause:** Sample CSV files missing or corrupted

**Solution:**

**Step 1:** Verify sample CSV exists
```bash
ls backend/sample_data/
# Should show: hiring.csv, loan.csv, healthcare.csv, education.csv
```

**Step 2:** Check CSV is readable
```bash
# Verify first few lines
head -5 backend/sample_data/hiring.csv
```

**Step 3:** If missing, regenerate
```bash
cd backend
python generate_samples.py
# Should create sample_data/*.csv files
```

**Step 4:** Restart backend
```bash
uvicorn main:app --reload
```

---

## Deployment Issues

### "Docker build fails: 'No module named fastapi'"

**Problem:** Docker build can't install Python dependencies

**Cause:** requirements.txt not included or corrupt

**Solution:**

**Step 1:** Verify requirements.txt exists
```bash
ls backend/requirements.txt
```

**Step 2:** Check for issues
```bash
cat backend/requirements.txt | grep fastapi
# Should show: fastapi==0.111.0
```

**Step 3:** Rebuild Docker
```bash
cd backend
docker build -t veritas-backend .
```

---

### "Firebase deploy fails: Build or function error"

**Problem:** `firebase deploy` returns error

**Causes:**
1. Not logged in to Firebase
2. Wrong project selected
3. Build failed

**Solution:**

**Step 1:** Login to Firebase
```bash
firebase login
```

**Step 2:** Check project
```bash
firebase projects:list
firebase use <project-id>
```

**Step 3:** Rebuild frontend first
```bash
cd frontend
npm run build
# Should create ./dist/ folder
```

**Step 4:** Try deploy
```bash
firebase deploy
```

---

### "GCP Cloud Run: Health check failing"

**Problem:** Backend container exits after deploy

**Symptom:** Cloud Run shows "Service unavailable"

**Causes:**
1. Port not correct (Cloud Run expects 8080)
2. GEMINI_API_KEY not set in environment
3. Code error on startup

**Solution:**

**Step 1:** Check Dockerfile EXPOSE and CMD
```dockerfile
EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**Step 2:** Set GEMINI_API_KEY in Cloud Run
- Go to Cloud Run Console
- Select service
- Edit → Add environment variable
- `GEMINI_API_KEY=sk_YOUR_KEY`
- Deploy

**Step 3:** Check logs
```bash
gcloud run logs read veritas-backend
```

---

### "Production frontend stuck on loading"

**Problem:** Frontend infinite loading spinner after deployment

**Causes:**
1. API_URL points to wrong backend
2. CORS not configured for production domain
3. Backend API failing

**Solution:**

**Step 1:** Check browser Network tab
- Should see requests to your API domain
- If requests fail: 404 or CORS error

**Step 2:** Check frontend env vars
```bash
cd frontend && npm run build
# Verify VITE_API_URL set correctly in .env.production
```

**Step 3:** Check backend CORS
In `backend/main.py`:
```python
allow_origins=[
    "https://your-frontend-domain.com",
]
```

**Step 4:** Verify backend API endpoint
```bash
curl https://api.your-domain.com/api/domains
# Should return domain list, not 404
```

---

## Performance Issues

### "Upload takes >30 seconds"

**Problem:** CSV analysis is slow

**Causes:**
1. Large CSV (>1000 rows)
2. Gemini API slow to respond
3. Network latency

**Solution:**

**Step 1:** Check file size
- If >5 MB: consider splitting into smaller datasets
- Smaller files process faster

**Step 2:** Check Gemini latency
- Gemini API can be slow (5-10 seconds)
- If 20+ seconds: likely Gemini bottleneck
- Consider disabling Gemini for dev (`comment out explain_bias()` call)

**Step 3:** Monitor network
- Network tab → POST to `/api/analyze`
- Check how long each phase takes:
  - CSV upload: <1 second
  - Bias detection: <2 seconds
  - Gemini call: 5-10 seconds
  - Total: should be <20 seconds

---

### "Frontend is slow / charts take forever to render"

**Problem:** UI freezes or lags

**Causes:**
1. Large result set (100+ attributes)
2. Chart library (Tremor) rendering slowly
3. Browser memory issue

**Solution:**

**Step 1:** Check device performance
- Open DevTools → Performance tab
- Record while uploading/rendering
- Look for long-running tasks

**Step 2:** Reduce data complexity
- If analyzing 100 protected attributes: will be slow
- Focus on key attributes (2-3)

**Step 3:** Clear browser cache
```bash
# Chrome: Ctrl+Shift+Delete → Clear all
# Firefox: Ctrl+Shift+Delete → Clear all
```

---

## Still Having Issues?

### Enable Debug Mode

**Backend:**
```python
# In backend/main.py, add:
import logging
logging.basicConfig(level=logging.DEBUG)
```

Then restart and check logs.

**Frontend:**
```javascript
// In frontend/.env.local, add:
VITE_DEBUG=true
```

Then check browser console.

### Collect Debug Info

Before reporting issue, gather:
1. Full error message (screenshot or copy)
2. Browser: Chrome vs Firefox vs Safari
3. OS: Windows vs macOS vs Linux
4. Steps to reproduce
5. Backend logs (if applicable)
6. Frontend console errors (DevTools)

### Report Issue

Submit to: https://github.com/anomalyco/opencode/issues

Include:
- Title: "Veritas: [Brief description]"
- Description: Error message + steps to reproduce
- Environment: OS, Python version, npm version
- Attached: Log files, sanitized screenshots

---

## Common Questions

### Q: Why does my CSV with 50 rows say "not enough data"?

**A:** Veritas technically works with 50 rows, but results are unreliable. Recommend ≥500 rows for meaningful bias analysis.

### Q: Can I run frontend and backend on same port?

**A:** Not easily. Separate ports (8000 backend, 5173 frontend) is standard. If you must use one port, use a reverse proxy (Nginx).

### Q: How do I run Veritas without internet (offline)?

**A:** Backend works fine offline (local analysis only). Frontend needs internet only for UI libraries (loaded on first build). Gemini requires internet (API call).

To run offline: Disable Gemini, all local APIs work.

### Q: Is my data safe with Veritas?

**A:** Veritas is stateless (no database). Data uploaded is analyzed in memory then discarded. Enable HTTPS in production. Don't upload unencrypted PII.

---

## Getting Help

- **Documentation:** Start with README.md, AGENTS.md, ARCHITECTURE.md
- **CSV Issues:** Check CSV_FORMAT_GUIDE.md
- **Bias Metrics:** Check METRICS_EXPLAINED.md
- **Code Issues:** Check error message in this guide
- **Community:** GitHub Issues (include reproducible example)
