# FairScan Quick Start Testing Guide

Get up and running with FairScan testing in 5 minutes.

---

## 🚀 Quick Start (3 Steps)

### Step 1: Start Backend
```bash
cd D:\fairscan\backend
python main.py
```

**Expected**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 2: Start Frontend (New Terminal)
```bash
cd D:\fairscan\frontend
npm run dev
```

**Expected**:
```
➜  Local:   http://localhost:5173/
```

### Step 3: Open in Browser
Visit **http://localhost:5173**

---

## ✅ Manual Testing (2 minutes)

### Backend Quick Tests
```powershell
# Test 1: Health Check
curl http://localhost:8000/health

# Test 2: List all domains
curl http://localhost:8000/api/domains

# Test 3: Load sample data
curl http://localhost:8000/api/sample/hiring

# Test 4: Upload test file
curl -X POST http://localhost:8000/api/analyze `
  -F "file=@test_data.csv" `
  -F "domain=hiring"
```

### Frontend Quick Tests
1. **Page loads** → See "FairScan" header
2. **Select domain** → Click "Hiring"
3. **Load sample** → Click "Use Sample Data"
4. **View results** → See bias metrics
5. **Export PDF** → Click "Export Report as PDF"

---

## 🤖 Automated Testing

### Run All Tests (PowerShell)
```powershell
cd D:\fairscan

# Make sure test files are present
ls test_data*.csv

# Run automated tests
.\run_tests.ps1
```

**Expected Output**:
```
✓ PASS - Health Check (HTTP 200)
✓ PASS - List Domains (HTTP 200)
✓ PASS - Sample Dataset: hiring (HTTP 200)
✓ PASS - Sample Dataset: loan (HTTP 200)
✓ PASS - Sample Dataset: healthcare (HTTP 200)
✓ PASS - Sample Dataset: education (HTTP 200)
✓ PASS - Valid CSV Upload (HTTP 200)
✓ PASS - Missing Column Error (HTTP 422)
✓ PASS - Invalid Domain Error (HTTP 400)
✓ PASS - Zero Division Handling (HTTP 200)

=== TEST SUMMARY ===
Total Tests: 10
Passed: 10
Failed: 0
Success Rate: 100%
```

---

## 📋 Test Cases by Priority

### Critical (Must Pass)
- [ ] Backend health check: `GET /health` → 200
- [ ] Frontend loads: http://localhost:5173 → No errors
- [ ] Sample data loads: `GET /api/sample/hiring` → 200
- [ ] File upload works: `POST /api/analyze` → 200
- [ ] PDF export works: File downloads

### Important (Should Pass)
- [ ] Invalid file rejected: `.txt` → 400
- [ ] Missing column error: CSV without `hired` → 422
- [ ] File size limit: 11MB file → 413
- [ ] All 4 domains load samples
- [ ] Error messages are clear

### Nice to Have
- [ ] Gemini explanations generate
- [ ] Responsive design (mobile)
- [ ] Keyboard navigation works
- [ ] Dark theme renders correctly

---

## 🐛 Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Port 8000 in use | Kill process: `netstat -ano \| findstr :8000` |
| Backend won't start | Check Python 3.11+: `python --version` |
| Frontend won't build | Install deps: `npm install --legacy-peer-deps` |
| API calls fail | Ensure backend running on localhost:8000 |
| PDF export fails | Check explanation not null in response |
| Dark theme missing | Check browser console for Tailwind errors |

---

## 📊 Test Results Template

Print this out and fill in as you test:

```
Date: _______________
Tester: _______________
Environment: Windows / macOS / Linux

BACKEND TESTS (✓/✗)
  [ ] Health Check
  [ ] List Domains
  [ ] Sample Hiring
  [ ] Sample Loan
  [ ] Sample Healthcare
  [ ] Sample Education
  [ ] Upload Valid CSV
  [ ] Reject Missing Column
  [ ] Reject Invalid Domain
  [ ] Zero Division Fix

FRONTEND TESTS (✓/✗)
  [ ] Page Loads
  [ ] Domain Selection
  [ ] Sample Data Load
  [ ] Results Display
  [ ] Metrics Visible
  [ ] Charts Render
  [ ] Error Handling
  [ ] Error Recovery
  [ ] PDF Export
  [ ] Dark Theme

INTEGRATION (✓/✗)
  [ ] End-to-End Flow
  [ ] Sample Data Flow
  [ ] Error Recovery

Issues Found:
_________________________________
_________________________________

Notes:
_________________________________
_________________________________
```

---

## 🔍 Detailed Testing

For comprehensive testing, see **TESTING_GUIDE.md**:
- 30+ manual test cases
- 10+ integration flows
- Performance benchmarks
- Troubleshooting guide
- Full API documentation

---

## 📈 Success Criteria

You're done when:
- ✓ All 10 automated tests pass
- ✓ Page loads without console errors
- ✓ Sample data loads for all domains
- ✓ File upload works
- ✓ Results display correctly
- ✓ PDF exports successfully
- ✓ Error messages make sense
- ✓ No crashes or hangs

---

## 🎯 Next Steps

After testing passes:

1. **Deploy Backend** → GCP Cloud Run
   ```bash
   cd backend
   gcloud run deploy fairscan --source .
   ```

2. **Deploy Frontend** → Firebase Hosting
   ```bash
   cd frontend
   npm run build
   firebase deploy
   ```

3. **Monitor** → Check logs and alerts

---

## ❓ Need Help?

See **TESTING_GUIDE.md** for:
- Extended test cases
- Network troubleshooting
- Browser dev tools tips
- Postman collection
- Test data formats

---

Generated: 2026-04-12
Version: 1.0
