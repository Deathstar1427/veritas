# Veritas Testing Script (PowerShell)
# Run automated tests against backend

param(
    [string]$BackendUrl = "http://localhost:8000",
    [int]$Timeout = 10
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
$FixtureDir = Join-Path $ScriptDir "fixtures"

# Test counters
$passed = 0
$failed = 0

# Function to print colored output
function Write-TestResult {
    param(
        [string]$TestName,
        [int]$ResponseCode,
        [int]$ExpectedCode,
        [string]$Details = ""
    )
    
    if ($ResponseCode -eq $ExpectedCode) {
        Write-Host "âœ“ PASS" -ForegroundColor Green -NoNewline
        Write-Host " - $TestName (HTTP $ResponseCode)"
        if ($Details) { Write-Host "  $Details" -ForegroundColor Gray }
        return $true
    } else {
        Write-Host "âœ— FAIL" -ForegroundColor Red -NoNewline
        Write-Host " - $TestName (Expected $ExpectedCode, got $ResponseCode)"
        if ($Details) { Write-Host "  $Details" -ForegroundColor Gray }
        return $false
    }
}

# Check backend connectivity
function Check-Backend {
    Write-Host "Checking backend connectivity..." -ForegroundColor Yellow
    
    try {
        $response = Invoke-WebRequest -Uri "$BackendUrl/health" `
            -Method GET `
            -TimeoutSec 2 `
            -ErrorAction Stop
        Write-Host "âœ“ Backend is running" -ForegroundColor Green
        Write-Host ""
        return $true
    } catch {
        Write-Host "âœ— Backend not running!" -ForegroundColor Red
        Write-Host "Start backend with: cd $RootDir\backend && uvicorn main:app --reload" -ForegroundColor Yellow
        return $false
    }
}

# Test 1: Health Check
function Test-HealthCheck {
    Write-Host "=== Backend API Tests ===" -ForegroundColor Cyan
    Write-Host ""
    
    try {
        $response = Invoke-WebRequest -Uri "$BackendUrl/health" -Method GET -TimeoutSec $Timeout -ErrorAction Stop
        $body = $response.Content | ConvertFrom-Json
        
        if (Write-TestResult "Health Check" $response.StatusCode 200) {
            $global:passed++
            Write-Host "  Response: $(ConvertTo-Json $body -Compress)" -ForegroundColor Gray
        } else {
            $global:failed++
        }
    } catch {
        Write-Host "âœ— FAIL - Health Check: $($_.Exception.Message)" -ForegroundColor Red
        $global:failed++
    }
    Write-Host ""
}

# Test 2: List Domains
function Test-ListDomains {
    try {
        $response = Invoke-WebRequest -Uri "$BackendUrl/api/domains" -Method GET -TimeoutSec $Timeout -ErrorAction Stop
        $body = $response.Content | ConvertFrom-Json
        
        if (Write-TestResult "List Domains" $response.StatusCode 200) {
            $global:passed++
            $domainCount = $body | Get-Member -MemberType NoteProperty | Measure-Object | Select-Object -ExpandProperty Count
            Write-Host "  Found domains: $domainCount" -ForegroundColor Gray
        } else {
            $global:failed++
        }
    } catch {
        Write-Host "âœ— FAIL - List Domains: $($_.Exception.Message)" -ForegroundColor Red
        $global:failed++
    }
    Write-Host ""
}

# Test 3: Sample Datasets
function Test-SampleDatasets {
    Write-Host "Testing sample datasets..." -ForegroundColor Yellow
    
    $domains = @("hiring", "loan", "healthcare", "education")
    
    foreach ($domain in $domains) {
        try {
            $response = Invoke-WebRequest -Uri "$BackendUrl/api/sample/$domain" -Method GET -TimeoutSec $Timeout -ErrorAction Stop
            $body = $response.Content | ConvertFrom-Json
            
            if (Write-TestResult "Sample Dataset: $domain" $response.StatusCode 200) {
                $global:passed++
                $records = $body.results.total_records
                Write-Host "  Records: $records" -ForegroundColor Gray
            } else {
                $global:failed++
            }
        } catch {
            Write-Host "âœ— FAIL - Sample $domain : $($_.Exception.Message)" -ForegroundColor Red
            $global:failed++
        }
    }
    Write-Host ""
}

# Test 4: Valid CSV Upload
function Test-ValidCSV {
    Write-Host "Testing CSV file upload..." -ForegroundColor Yellow
    
    $testDataPath = Join-Path $FixtureDir "test_data.csv"

    if (-not (Test-Path $testDataPath)) {
        Write-Host "âš  test_data.csv not found - skipping" -ForegroundColor Yellow
        return
    }

    try {
        $form = @{
            file   = Get-Item $testDataPath
            domain = "hiring"
        }
        
        $response = Invoke-WebRequest -Uri "$BackendUrl/api/analyze" `
            -Method POST `
            -Form $form `
            -TimeoutSec $Timeout `
            -ErrorAction Stop
        
        $body = $response.Content | ConvertFrom-Json
        
        if (Write-TestResult "Valid CSV Upload" $response.StatusCode 200) {
            $global:passed++
            $attributes = $body.results.bias_metrics | Get-Member -MemberType NoteProperty | Measure-Object | Select-Object -ExpandProperty Count
            Write-Host "  Analyzed attributes: $attributes" -ForegroundColor Gray
        } else {
            $global:failed++
        }
    } catch {
        Write-Host "âœ— FAIL - Valid CSV: $($_.Exception.Message)" -ForegroundColor Red
        $global:failed++
    }
    Write-Host ""
}

# Test 5: Missing Column Error
function Test-MissingColumn {
    Write-Host "Testing error handling..." -ForegroundColor Yellow
    
    $missingColPath = Join-Path $FixtureDir "test_data_missing_column.csv"

    if (-not (Test-Path $missingColPath)) {
        Write-Host "âš  test_data_missing_column.csv not found - skipping" -ForegroundColor Yellow
        return
    }
    
    try {
        $form = @{
            file   = Get-Item $missingColPath
            domain = "hiring"
        }
        
        $response = Invoke-WebRequest -Uri "$BackendUrl/api/analyze" `
            -Method POST `
            -Form $form `
            -TimeoutSec $Timeout `
            -ErrorAction Stop -SkipHttpErrorCheck
        
        $body = $response.Content | ConvertFrom-Json
        
        if ($response.StatusCode -eq 422) {
            Write-Host "âœ“ PASS - Missing Column Error (HTTP 422)" -ForegroundColor Green
            $global:passed++
            Write-Host "  Error: $($body.detail)" -ForegroundColor Gray
        } else {
            Write-Host "âœ— FAIL - Missing Column (Expected 422, got $($response.StatusCode))" -ForegroundColor Red
            $global:failed++
        }
    } catch {
        Write-Host "âœ— FAIL - Missing Column: $($_.Exception.Message)" -ForegroundColor Red
        $global:failed++
    }
    Write-Host ""
}

# Test 6: Invalid Domain
function Test-InvalidDomain {
    try {
        $testDataPath = Join-Path $FixtureDir "test_data.csv"
        $form = @{
            file   = Get-Item $testDataPath
            domain = "invalid_domain"
        }
        
        $response = Invoke-WebRequest -Uri "$BackendUrl/api/analyze" `
            -Method POST `
            -Form $form `
            -TimeoutSec $Timeout `
            -ErrorAction Stop -SkipHttpErrorCheck
        
        if ($response.StatusCode -eq 400) {
            Write-Host "âœ“ PASS - Invalid Domain Error (HTTP 400)" -ForegroundColor Green
            $global:passed++
        } else {
            Write-Host "âœ— FAIL - Invalid Domain (Expected 400, got $($response.StatusCode))" -ForegroundColor Red
            $global:failed++
        }
    } catch {
        Write-Host "âœ— FAIL - Invalid Domain: $($_.Exception.Message)" -ForegroundColor Red
        $global:failed++
    }
    Write-Host ""
}

# Test 7: Zero Division Handling
function Test-ZeroDivision {
    Write-Host "Testing Zero Division Fix (Bug #1)..." -ForegroundColor Yellow
    
    $zeroRatePath = Join-Path $FixtureDir "test_data_zero_rate.csv"

    if (-not (Test-Path $zeroRatePath)) {
        Write-Host "âš  test_data_zero_rate.csv not found - skipping" -ForegroundColor Yellow
        return
    }
    
    try {
        $form = @{
            file   = Get-Item $zeroRatePath
            domain = "hiring"
        }
        
        $response = Invoke-WebRequest -Uri "$BackendUrl/api/analyze" `
            -Method POST `
            -Form $form `
            -TimeoutSec $Timeout `
            -ErrorAction Stop
        
        $body = $response.Content | ConvertFrom-Json
        
        if (Write-TestResult "Zero Division Handling" $response.StatusCode 200) {
            $global:passed++
            $dir = $body.results.bias_metrics.gender.disparate_impact_ratio
            Write-Host "  Disparate Impact Ratio: $dir (should be null or valid)" -ForegroundColor Gray
        } else {
            $global:failed++
        }
    } catch {
        Write-Host "âœ— FAIL - Zero Division: $($_.Exception.Message)" -ForegroundColor Red
        $global:failed++
    }
    Write-Host ""
}

# Print Summary
function Print-Summary {
    Write-Host ""
    Write-Host "=== TEST SUMMARY ===" -ForegroundColor Cyan
    
    $total = $passed + $failed
    if ($total -gt 0) {
        $percentage = [math]::Round(($passed / $total) * 100, 1)
    } else {
        $percentage = 0
    }
    
    Write-Host "Total Tests: $total"
    Write-Host "Passed: $passed" -ForegroundColor Green
    Write-Host "Failed: $failed" -ForegroundColor Red
    Write-Host "Success Rate: $percentage%"
    Write-Host ""
    
    if ($failed -eq 0) {
        Write-Host "âœ“ All tests passed!" -ForegroundColor Green
        return 0
    } else {
        Write-Host "âœ— Some tests failed." -ForegroundColor Red
        return 1
    }
}

# Main execution
Write-Host "â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—" -ForegroundColor Cyan
Write-Host "â•‘   Veritas Testing Suite v1.0          â•‘" -ForegroundColor Cyan
Write-Host "â•‘   Backend API & Integration Tests      â•‘" -ForegroundColor Cyan
Write-Host "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Cyan
Write-Host ""

if (-not (Check-Backend)) {
    exit 1
}

Test-HealthCheck
Test-ListDomains
Test-SampleDatasets
Test-ValidCSV
Test-MissingColumn
Test-InvalidDomain
Test-ZeroDivision

Print-Summary

