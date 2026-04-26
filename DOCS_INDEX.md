# Veritas Documentation Index

> **Complete guide to Veritas documentation and where to find information.**

---

## Quick Navigation

### For First-Time Users
1. **START HERE:** [START_HERE.md](START_HERE.md) - 5-minute overview
2. **Deploy:** [QUICKSTART_DEPLOY.md](QUICKSTART_DEPLOY.md) - 15 minutes to running
3. **Prepare Data:** [CSV_FORMAT_GUIDE.md](CSV_FORMAT_GUIDE.md) - Uploading datasets

### For Developers
1. **Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md) - Complete system design
2. **Development:** [AGENTS.md](AGENTS.md) - Technical deep dive
3. **Metrics:** [METRICS_EXPLAINED.md](METRICS_EXPLAINED.md) - Understanding bias metrics

### For Operations / Production
1. **Production Deployment:** [DEPLOYMENT_FREE_TIER.md](DEPLOYMENT_FREE_TIER.md) - Step-by-step setup
2. **Troubleshooting:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues & fixes
3. **Production Ready:** [PRODUCTION_READY.md](PRODUCTION_READY.md) - Security checklist

### For Business / Non-Technical
1. **What is Veritas?** [README.md](README.md) - Overview & features
2. **Understanding Bias:** [METRICS_EXPLAINED.md](METRICS_EXPLAINED.md) - Plain-language explanations
3. **CSV Format:** [CSV_FORMAT_GUIDE.md](CSV_FORMAT_GUIDE.md) - How to prepare data

---

## All Documentation Files

### Core Documentation

| File | Purpose | Audience | Read Time |
|------|---------|----------|-----------|
| **README.md** | Project overview, features, quick links | Everyone | 10 min |
| **START_HERE.md** | Quick start guide, installation basics | New users | 5 min |
| **QUICKSTART_DEPLOY.md** | Manual 15-minute deployment guide | Developers | 15 min |
| **ARCHITECTURE.md** | Complete system architecture, data flow, components | Developers | 20 min |
| **AGENTS.md** | Deep technical guide, quirks, critical files | Developers | 30 min |
| **METRICS_EXPLAINED.md** | Bias metrics explained plain-language | Everyone | 20 min |
| **CSV_FORMAT_GUIDE.md** | CSV specifications, examples, errors | Data analysts | 15 min |
| **TROUBLESHOOTING.md** | Problems & solutions, debugging guide | Everyone | 30 min |

### Deployment & Production

| File | Purpose | Audience | Read Time |
|------|---------|----------|-----------|
| **DEPLOYMENT_FREE_TIER.md** | Free tier deployment (GCP, Firebase) | DevOps | 30 min |
| **PRODUCTION_READY.md** | Security audit, CORS fixes, checklist | DevOps | 10 min |
| **DEPLOYMENT_STATUS.md** | Current deployment readiness | DevOps | 5 min |
| **PRODUCTION_READINESS_REPORT.md** | Full production audit results | DevOps | 15 min |

### Reference

| File | Purpose | Audience | Read Time |
|------|---------|----------|-----------|
| **API_TESTING_REFERENCE.md** | API endpoint examples & curl commands | Developers | 10 min |
| **QUICK_START_TESTING.md** | Testing manual verification steps | QA | 10 min |

### Historical / Archive

| File | Purpose | Status |
|------|---------|--------|
| fairscan_master_prompt.md | Original planning document | Archived |
| implementation_plan.md | Initial implementation plan | Archived |
| IMPLEMENTATION_COMPLETED.md | Old completion checklist | Archived |
| TEST_RESULTS.md | Old test run results | Archived |
| test_results.txt | Old test output | Archived |

---

## Reading Paths by Use Case

### Use Case 1: "I want to deploy Veritas in 30 minutes"

1. Read: [START_HERE.md](START_HERE.md) - (5 min)
2. Read: [QUICKSTART_DEPLOY.md](QUICKSTART_DEPLOY.md) - (15 min)
3. Follow: deployment script `deploy.ps1` or `deploy.sh`
4. Test: "Use Sample Data" button to verify
5. Done! 🎉

**Total Time:** ~30 minutes

---

### Use Case 2: "I'm a developer who wants to understand the code"

1. Read: [README.md](README.md) - (10 min) - Overview
2. Read: [ARCHITECTURE.md](ARCHITECTURE.md) - (20 min) - System design
3. Read: [AGENTS.md](AGENTS.md) - (30 min) - Technical details & quirks
4. Explore: `backend/app/` and `frontend/src/` directories
5. Understand: [METRICS_EXPLAINED.md](METRICS_EXPLAINED.md) - (20 min) - What metrics mean

**Total Time:** ~90 minutes

---

### Use Case 3: "I need to prepare data for analysis"

1. Read: [CSV_FORMAT_GUIDE.md](CSV_FORMAT_GUIDE.md) - Format specs & examples
2. Use: Examples section to create your CSV
3. Verify: Checklist at end of guide
4. Upload: Via Veritas UI

**Total Time:** ~20 minutes

---

### Use Case 4: "I want to deploy to production with security"

1. Read: [DEPLOYMENT_FREE_TIER.md](DEPLOYMENT_FREE_TIER.md) - (30 min)
2. Read: [PRODUCTION_READY.md](PRODUCTION_READY.md) - (10 min) - Security checklist
3. Follow: Deployment steps with production hardening
4. Verify: Security fixes applied (CORS, env vars, HTTPS)
5. Test: Full e2e deployment

**Total Time:** ~60 minutes

---

### Use Case 5: "Something broke! I need help now"

1. Check: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Find: Your error message or symptom
3. Follow: Solution steps
4. Test: Does it work?
5. If not: Collect debug info and report issue

**Total Time:** ~10-30 minutes depending on issue

---

### Use Case 6: "I'm non-technical but need to understand bias"

1. Read: [METRICS_EXPLAINED.md](METRICS_EXPLAINED.md) - Bias concepts in plain English
2. Read: [README.md](README.md) - Project overview
3. Read: [CSV_FORMAT_GUIDE.md](CSV_FORMAT_GUIDE.md) - How to prepare data
4. Use: Veritas with sample data to see it in action
5. Read: Results and AI explanation

**Total Time:** ~40 minutes

---

## Key Concepts Quick Reference

### Bias Metrics

- **Disparate Impact Ratio (DIR)**: Compares outcome rates between groups. <0.80 = high bias
- **Demographic Parity Difference (DPD)**: Percentage-point difference in outcomes. >0.10 = bias
- **Equalized Odds Difference (EOD)**: Compares error rates across groups. >0.10 = bias

📖 **Learn More:** [METRICS_EXPLAINED.md](METRICS_EXPLAINED.md)

### System Architecture

```
Frontend (React 19 + Vite)
    ↓
Backend (FastAPI + Uvicorn)
    ├─ Routes (HTTP endpoints)
    ├─ Services (business logic)
    │  ├─ Bias detection (Fairlearn)
    │  ├─ AI explanation (Gemini)
    │  ├─ PDF generation (ReportLab)
    │  └─ Sample caching
    └─ Config (domain definitions)
```

📖 **Learn More:** [ARCHITECTURE.md](ARCHITECTURE.md)

### File Structure

```
veritas/
├── backend/          # FastAPI application
│  ├── main.py       # Entry point
│  ├── app/
│  │  ├── routes/    # HTTP endpoints
│  │  ├── services/  # Business logic
│  │  └── domain_config.py  # Schema
│  └── sample_data/  # Pre-generated CSVs
├── frontend/         # React application
│  └── src/
│     ├── App.jsx    # Root component
│     ├── components/ # UI components
│     └── index.css  # Styling
└── docs/            # Documentation
```

📖 **Learn More:** [ARCHITECTURE.md](ARCHITECTURE.md)

### Data Flow

1. User selects domain (Hiring, Loan, Healthcare, Education)
2. User uploads CSV file
3. Backend validates → detects bias → generates explanation
4. Frontend displays results with charts
5. User exports to PDF

📖 **Learn More:** [ARCHITECTURE.md](ARCHITECTURE.md)

---

## Critical Files for Each Role

### Backend Developer
- `backend/main.py` - Entry point
- `backend/app/routes/analyze.py` - API endpoints
- `backend/app/services/bias_service.py` - Core algorithm
- `backend/app/domain_config.py` - Configuration

### Frontend Developer
- `frontend/src/App.jsx` - Root component
- `frontend/src/components/*.jsx` - UI components
- `frontend/vite.config.js` - Build config
- `frontend/.env.local` - Environment

### DevOps / Operations
- `deploy.ps1` / `deploy.sh` - Deployment scripts
- `.env.example` - Environment template
- `backend/Dockerfile` - Container config
- `firebase.json` - Firebase config

### Data Analyst
- [CSV_FORMAT_GUIDE.md](CSV_FORMAT_GUIDE.md) - Data requirements
- [METRICS_EXPLAINED.md](METRICS_EXPLAINED.md) - Understanding metrics
- `backend/sample_data/` - Example datasets

---

## Troubleshooting by Symptom

### "Something doesn't work"
→ Start here: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### "Frontend blank / not rendering"
→ [TROUBLESHOOTING.md](TROUBLESHOOTING.md) → "Frontend Issues" section

### "API errors / Backend down"
→ [TROUBLESHOOTING.md](TROUBLESHOOTING.md) → "Backend Issues" section

### "CSV upload fails"
→ [CSV_FORMAT_GUIDE.md](CSV_FORMAT_GUIDE.md) → "Error Messages & Fixes" section

### "Bias metrics look wrong"
→ [METRICS_EXPLAINED.md](METRICS_EXPLAINED.md) → "FAQ" section

### "Deployment failed"
→ [DEPLOYMENT_FREE_TIER.md](DEPLOYMENT_FREE_TIER.md) → Troubleshooting section

### "Can't connect frontend to backend"
→ [TROUBLESHOOTING.md](TROUBLESHOOTING.md) → "CORS error" section

---

## Documentation Quality Standards

All documentation in Veritas follows:

✅ **Clear & Concise**
- Sections shorter than 2000 words
- Examples included for complex topics
- Table of contents with quick navigation

✅ **Audience-Appropriate**
- Technical docs for developers
- Plain-language for non-technical users
- Multiple learning paths for different roles

✅ **Actionable**
- Step-by-step instructions where applicable
- Code examples that can be copy-pasted
- Links to related docs

✅ **Up-to-Date**
- Reflects current code (v1.0.0)
- All API endpoints documented
- Deployment steps verified

---

## Contributing to Documentation

Found an issue or want to improve docs?

1. **Report Issue:**
   - GitHub: https://github.com/anomalyco/opencode/issues
   - Title: "Veritas Docs: [Issue]"
   - Include: What's wrong, what should be

2. **Suggest Improvement:**
   - What doc is unclear?
   - What's missing?
   - What would help you?

3. **Pull Request:**
   - Fork repo
   - Edit `.md` files
   - Submit PR with description

---

## Version Information

- **Veritas Version:** 1.0.0
- **Documentation Updated:** 2026-04-18
- **Tested With:**
  - Python 3.11+
  - Node 18+
  - React 19+
  - FastAPI 0.111.0+

---

## Quick Links

- **GitHub:** https://github.com/anomalyco/opencode
- **Report Issues:** https://github.com/anomalyco/opencode/issues
- **Fairlearn Docs:** https://fairlearn.org/
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **React Docs:** https://react.dev/

---

## Document List for Reference

```
├── README.md
├── START_HERE.md
├── QUICKSTART_DEPLOY.md
├── DEPLOYMENT_FREE_TIER.md
├── PRODUCTION_READY.md
├── PRODUCTION_READINESS_REPORT.md
├── DEPLOYMENT_STATUS.md
├── AGENTS.md
├── ARCHITECTURE.md
├── METRICS_EXPLAINED.md
├── CSV_FORMAT_GUIDE.md
├── TROUBLESHOOTING.md
├── API_TESTING_REFERENCE.md
├── QUICK_START_TESTING.md
├── TESTING_GUIDE.md
└── DOCS_INDEX.md (← You are here)
```

---

## Feedback

**Is this documentation helpful?**

- ✅ Yes → Great! Let us know what else would help
- ❌ No → Tell us what's unclear: https://github.com/anomalyco/opencode/issues
- 🤔 Partially → What's missing? What needs clarification?

Your feedback makes documentation better for everyone. 🙏
