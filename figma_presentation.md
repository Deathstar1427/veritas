# Team Details

**Team name:** Death Dev
**Team leader name:** Anant Kumar

**Problem Statement:** 
AI models in critical domains (hiring, loan, healthcare, education) are prone to bias. Detecting this requires deep technical expertise, making it a barrier for non-technical stakeholders to audit systems effectively.

---

# Brief about your solution

FairScan (Veritas) is a full-stack, cloud-native fairness auditing web app. Users upload a dataset, and the system computes industry-standard bias metrics (DPD, EOD, DIR). It uses Google Gemini to generate plain-language explanations and mitigation guidance, and exports everything as a PDF audit report.

---

# Opportunities

**How different is it from any of the other existing ideas?**
Existing bias detection tools (like Fairlearn) are code-only libraries aimed at data scientists. FairScan provides a no-code visual interface for non-technical stakeholders.

**How will it be able to solve the problem?**
By automating complex statistical calculations and translating results into human-readable insights using Gemini.

**USP of the proposed solution**
Seamless integration of rigorous statistical metrics with Google Gemini's generative AI to translate complex data into actionable, plain-English audit guidance.

---

# List of features offered by the solution

* Domain-Specific Analysis (Hiring, Lending, Healthcare, Education)
* Automated Bias Metrics (DPD, EOD, DIR)
* Algorithmic Severity Classification
* Generative AI Explanations via Google Gemini
* Interactive Dashboard with Responsive Charts
* Secure Access via Firebase Auth
* Automated PDF Reporting

---

# Process flow diagram

*(Insert your Process Flow diagram here)*
User Login -> Upload CSV -> FastAPI processes Fairlearn metrics -> Backend calls Gemini API -> React Dashboard Renders -> PDF Export

---

# Wireframes/Mock diagrams

*(Insert Screenshots of FairScan Dashboard)*

---

# Architecture diagram

*(Insert your Architecture Diagram here)*
React SPA on Firebase Hosting -> FastAPI on Google Cloud Run. Backend connects to Firebase Auth, Gemini API, and ReportLab.

---

# Technologies to be used in the solution

* **Frontend:** React 19, Vite, Tailwind CSS, Tremor
* **Backend:** Python 3.11+, FastAPI, Uvicorn
* **Data/ML:** Fairlearn, Pandas, Scikit-learn
* **Cloud:** Firebase Hosting, Firebase Auth, Google Cloud Run
* **AI:** Google Gemini API (google-generativeai)

---

# Estimated implementation cost

* **Development & Testing:** $0 (Free Tiers)
* **Hosting & Auth (Firebase):** $0 (Spark Plan)
* **Backend (Cloud Run):** Pay-per-use (Generous Free Tier)
* **AI (Gemini API):** Free tier access
* **Total MVP Cost:** $0 to launch initially due to serverless architecture.

---

# Snapshots of the MVP

*(Insert actual screenshots of FairScan: Login, Upload workspace, Results dashboard, PDF report)*

---

# Additional Details / Future Development

* **Database Integration:** Google Cloud Firestore for persisting audit histories.
* **Advanced Mitigation:** Using Gemini to suggest data reweighing techniques.
* **Enterprise Features:** Team workspaces and role-based access control (RBAC).

---

# Links

* **GitHub Public Repository:** [Insert Link]
* **Demo Video Link (3 Minutes):** [Insert Link]
* **MVP Link:** https://veritas-ai-01.web.app
* **Working Prototype Link:** https://veritas-ai-01.web.app
