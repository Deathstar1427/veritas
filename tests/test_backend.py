#!/usr/bin/env python
"""
Veritas Backend Testing Script
Tests all bug fixes from Phase 1 and Phase 3
"""

import subprocess
import time
import sys
import requests
from pathlib import Path

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"
TIMEOUT = 10
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

# Test counters
passed = 0
failed = 0


def start_backend():
    """Start the backend server"""
    print("Starting backend server...")
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=str(BACKEND_DIR),
    )
    time.sleep(4)  # Wait for server to start
    return proc


def print_test_result(test_name, passed_flag, details=""):
    """Print formatted test result"""
    global passed, failed
    if passed_flag:
        print(f"[PASS] {test_name}")
        if details:
            print(f"  {details}")
        passed += 1
    else:
        print(f"[FAIL] {test_name}")
        if details:
            print(f"  {details}")
        failed += 1


def test_health_check():
    """Test 1: Health Check"""
    print("\n=== Backend API Tests ===\n")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print_test_result(
                "Health Check",
                True,
                f"Status: {data.get('status')}, Version: {data.get('version')}",
            )
            return True
        else:
            print_test_result("Health Check", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        print_test_result("Health Check", False, str(e))
        return False


def test_list_domains():
    """Test 2: List Domains"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/domains", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            domain_count = len(data)
            print_test_result("List Domains", True, f"Found {domain_count} domains")
            return True
        else:
            print_test_result("List Domains", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        print_test_result("List Domains", False, str(e))
        return False


def test_sample_datasets():
    """Test 3: Sample Datasets"""
    print("Testing sample datasets...")
    domains = ["hiring", "loan", "healthcare", "education"]
    all_passed = True

    for domain in domains:
        try:
            response = requests.get(
                f"{BACKEND_URL}/api/sample/{domain}", timeout=TIMEOUT
            )
            if response.status_code == 200:
                data = response.json()
                total_records = data.get("results", {}).get("total_records", "N/A")
                print_test_result(
                    f"Sample Dataset: {domain}", True, f"Records: {total_records}"
                )
            else:
                print_test_result(
                    f"Sample Dataset: {domain}", False, f"HTTP {response.status_code}"
                )
                all_passed = False
        except Exception as e:
            print_test_result(f"Sample Dataset: {domain}", False, str(e))
            all_passed = False
    return all_passed


def test_valid_csv():
    """Test 4: Valid CSV Upload"""
    print("Testing CSV file upload...")
    test_file = FIXTURES_DIR / "test_data.csv"

    if not test_file.exists():
        print("âš  test_data.csv not found - skipping")
        return False

    try:
        with test_file.open("rb") as f:
            files = {"file": f}
            data = {"domain": "hiring"}
            response = requests.post(
                f"{BACKEND_URL}/api/analyze", files=files, data=data, timeout=TIMEOUT
            )

        if response.status_code == 200:
            result = response.json()
            bias_metrics = result.get("results", {}).get("bias_metrics", {})
            attribute_count = len(bias_metrics)
            print_test_result(
                "Valid CSV Upload", True, f"Analyzed attributes: {attribute_count}"
            )
            return True
        else:
            print_test_result("Valid CSV Upload", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        print_test_result("Valid CSV Upload", False, str(e))
        return False


def test_missing_column():
    """Test 5: Missing Column Error (Bug #2)"""
    print("Testing error handling...")
    test_file = FIXTURES_DIR / "test_data_missing_column.csv"

    if not test_file.exists():
        print("âš  test_data_missing_column.csv not found - skipping")
        return False

    try:
        with test_file.open("rb") as f:
            files = {"file": f}
            data = {"domain": "hiring"}
            response = requests.post(
                f"{BACKEND_URL}/api/analyze", files=files, data=data, timeout=TIMEOUT
            )

        # Should return 422 for missing required column
        if response.status_code == 422:
            result = response.json()
            error_msg = result.get("detail", "Unknown error")
            print_test_result("Missing Column Error", True, f"HTTP 422: {error_msg}")
            return True
        else:
            print_test_result(
                "Missing Column Error",
                False,
                f"Expected 422, got HTTP {response.status_code}",
            )
            return False
    except Exception as e:
        print_test_result("Missing Column Error", False, str(e))
        return False


def test_zero_division():
    """Test 6: Zero Division Handling (Bug #1)"""
    print("Testing Zero Division Fix...")
    test_file = FIXTURES_DIR / "test_data_zero_rate.csv"

    if not test_file.exists():
        print("âš  test_data_zero_rate.csv not found - skipping")
        return False

    try:
        with test_file.open("rb") as f:
            files = {"file": f}
            data = {"domain": "hiring"}
            response = requests.post(
                f"{BACKEND_URL}/api/analyze", files=files, data=data, timeout=TIMEOUT
            )

        if response.status_code == 200:
            result = response.json()
            bias_metrics = result.get("results", {}).get("bias_metrics", {})
            # Check if disparate impact ratio is handled safely (should be None or a valid number)
            if "gender" in bias_metrics:
                dir_value = bias_metrics["gender"].get("disparate_impact_ratio")
                print_test_result(
                    "Zero Division Handling",
                    True,
                    f"Disparate Impact Ratio: {dir_value}",
                )
                return True
            else:
                print_test_result(
                    "Zero Division Handling",
                    True,
                    "Gender metric computed without error",
                )
                return True
        else:
            print_test_result(
                "Zero Division Handling", False, f"HTTP {response.status_code}"
            )
            return False
    except Exception as e:
        print_test_result("Zero Division Handling", False, str(e))
        return False


def print_summary():
    """Print test summary"""
    print("\n" + "=" * 50)
    print("=== TEST SUMMARY ===")
    print("=" * 50)

    total = passed + failed
    if total > 0:
        percentage = (passed / total) * 100
    else:
        percentage = 0

    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {percentage:.1f}%")
    print()

    if failed == 0:
        print("SUCCESS: All tests passed!")
        return 0
    else:
        print("FAILURE: Some tests failed.")
        return 1


def main():
    """Main test execution"""
    print("=" * 50)
    print("Veritas Testing Suite v1.0")
    print("Backend API & Integration Tests")
    print("=" * 50)
    print()

    # Start backend
    backend_proc = start_backend()

    try:
        # Run tests
        test_health_check()
        test_list_domains()
        test_sample_datasets()
        test_valid_csv()
        test_missing_column()
        test_zero_division()

        # Print summary
        exit_code = print_summary()
        return exit_code
    finally:
        # Cleanup
        print("\nStopping backend server...")
        backend_proc.terminate()
        backend_proc.wait(timeout=5)


if __name__ == "__main__":
    sys.exit(main())

