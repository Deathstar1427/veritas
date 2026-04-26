import unittest
import requests
import subprocess
import time
import sys
from pathlib import Path

BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_PORT = 5173
FRONTEND_URL = f"http://127.0.0.1:{FRONTEND_PORT}"
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


class TestVeritas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start backend
        print("Starting backend...")
        cls.backend_proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=str(BACKEND_DIR)
        )
        # Wait for backend
        for _ in range(30):
            try:
                if requests.get(f"{BACKEND_URL}/health").status_code == 200:
                    break
            except requests.exceptions.ConnectionError:
                time.sleep(1)
        else:
            raise RuntimeError("Backend failed to start")

        # Start frontend
        print("Starting frontend (dist)...")
        cls.frontend_proc = subprocess.Popen(
            [sys.executable, "-m", "http.server", str(FRONTEND_PORT), "--directory", "dist"],
            cwd=str(FRONTEND_DIR),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        # Wait for frontend
        for _ in range(10):
            try:
                if requests.get(FRONTEND_URL).status_code == 200:
                    break
            except requests.exceptions.ConnectionError:
                time.sleep(1)
        else:
            raise RuntimeError("Frontend failed to start")

    @classmethod
    def tearDownClass(cls):
        print("Stopping servers...")
        cls.backend_proc.terminate()
        cls.frontend_proc.terminate()

    # --- Backend Tests ---
    def test_backend_health(self):
        resp = requests.get(f"{BACKEND_URL}/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get("status"), "ok")

    def test_backend_list_domains(self):
        resp = requests.get(f"{BACKEND_URL}/api/domains")
        self.assertEqual(resp.status_code, 200)
        domains = resp.json()
        self.assertIn("hiring", domains)

    def test_backend_sample_data(self):
        resp = requests.get(f"{BACKEND_URL}/api/sample/hiring")
        self.assertEqual(resp.status_code, 200)

    # --- Frontend Tests ---
    def test_frontend_loads(self):
        resp = requests.get(FRONTEND_URL)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("<!doctype html>", resp.text.lower())

    def test_frontend_assets(self):
        resp = requests.get(FRONTEND_URL)
        # In Vite build (dist), index HTML references assets via index-<hash>.css or similarly.
        self.assertTrue(".css" in resp.text or ".js" in resp.text, "Missing assets link in HTML.")

    # --- Integration Tests ---
    def test_integration_upload_flow(self):
        test_file = FIXTURES_DIR / "test_data.csv"
        self.assertTrue(test_file.exists(), "Test CSV not found.")
        
        # Simulate frontend making a multipart/form request to backend API
        with test_file.open("rb") as f:
            resp = requests.post(
                f"{BACKEND_URL}/api/analyze",
                files={"file": f},
                data={"domain": "hiring"},
                headers={"Origin": FRONTEND_URL}
            )
        self.assertEqual(resp.status_code, 200)
        
        # Ensure CORS is configured properly
        self.assertIn("access-control-allow-origin", resp.headers)
        
        result_content = resp.json()
        results = result_content.get("results", {})
        self.assertIn("bias_metrics", results)
        
        # Explanation field should exist (from Gemini or mock)
        self.assertIn("explanation", result_content)


if __name__ == "__main__":
    unittest.main()

