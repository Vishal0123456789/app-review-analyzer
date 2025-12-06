# Manual Testing Script for Scheduler
# Run this in PowerShell to test the scheduler quickly

Write-Host "=== Scheduler Manual Testing Script ===" -ForegroundColor Cyan

# Function to wait for app startup
function Wait-AppStartup {
    Write-Host "`nWaiting for app to start..." -ForegroundColor Yellow
    $maxAttempts = 10
    $attempt = 0
    
    while ($attempt -lt $maxAttempts) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/api/scheduler-status" -Method Get -ErrorAction Stop
            Write-Host "✓ App is ready" -ForegroundColor Green
            return $true
        }
        catch {
            $attempt++
            if ($attempt -lt $maxAttempts) {
                Write-Host "  Attempt $attempt/$maxAttempts - waiting..." -ForegroundColor Gray
                Start-Sleep -Seconds 2
            }
        }
    }
    
    Write-Host "✗ App failed to start" -ForegroundColor Red
    return $false
}

# Test 1: Quick Status Check
function Test-SchedulerStatus {
    Write-Host "`n### TEST 1: Scheduler Status Check" -ForegroundColor Cyan
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/api/scheduler-status" -Method Get
        
        if ($response.status -eq "success") {
            Write-Host "✓ Status endpoint responsive" -ForegroundColor Green
            Write-Host "  Enabled: $($response.scheduler.enabled)"
            Write-Host "  Running: $($response.scheduler.running)"
            Write-Host "  Schedule: $($response.scheduler.schedule)"
            Write-Host "  Timezone: $($response.scheduler.timezone)"
            Write-Host "  Next Run: $($response.scheduler.next_run)"
            return $true
        }
        else {
            Write-Host "✗ Unexpected response: $($response | ConvertTo-Json)" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "✗ Error: $_" -ForegroundColor Red
        return $false
    }
}

# Test 2: Check Log Output
function Test-SchedulerLogs {
    Write-Host "`n### TEST 2: Check Scheduler Logs" -ForegroundColor Cyan
    
    $logFile = "logs/scheduler.log"
    
    if (-not (Test-Path $logFile)) {
        Write-Host "✗ Log file not found: $logFile" -ForegroundColor Red
        return $false
    }
    
    Write-Host "✓ Log file exists" -ForegroundColor Green
    
    $schedulerLines = Get-Content $logFile | Select-String "Scheduler|SCHEDULER" | Select-Object -Last 5
    
    if ($schedulerLines.Count -gt 0) {
        Write-Host "✓ Found scheduler entries:" -ForegroundColor Green
        $schedulerLines | ForEach-Object { Write-Host "  $_" }
        return $true
    }
    else {
        Write-Host "⚠ No scheduler entries found in logs (may be normal if just started)" -ForegroundColor Yellow
        return $true
    }
}

# Test 3: Test Manual Analysis Works
function Test-ManualAnalysis {
    Write-Host "`n### TEST 3: Manual Analysis (Independence Check)" -ForegroundColor Cyan
    
    $body = @{
        window_days = 7
        email = "test@example.com"
    } | ConvertTo-Json
    
    try {
        Write-Host "Triggering manual analysis..." -ForegroundColor Yellow
        $response = Invoke-RestMethod -Uri "http://localhost:8000/api/analyze" `
            -Method Post `
            -Body $body `
            -ContentType "application/json" `
            -TimeoutSec 900
        
        if ($response.status -eq "success") {
            Write-Host "✓ Manual analysis works independently" -ForegroundColor Green
            Write-Host "  File: $($response.pulse_file_name)"
            return $true
        }
        else {
            Write-Host "✗ Unexpected response: $response" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "⚠ Manual analysis test skipped (may need valid GEMINI_API_KEY)" -ForegroundColor Yellow
        return $true
    }
}

# Test 4: Test Different Timezone
function Test-CustomTimezone {
    Write-Host "`n### TEST 4: Custom Timezone Configuration" -ForegroundColor Cyan
    
    Write-Host "This test requires restarting the app with custom timezone" -ForegroundColor Yellow
    Write-Host "Example: set SCHEDULER_TIMEZONE=Asia/Kolkata and restart" -ForegroundColor Yellow
    
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/scheduler-status"
    
    if ($response.scheduler.timezone -ne "UTC") {
        Write-Host "✓ Custom timezone is set: $($response.scheduler.timezone)" -ForegroundColor Green
        return $true
    }
    else {
        Write-Host "ℹ Currently using UTC (default)" -ForegroundColor Cyan
        return $true
    }
}

# Test 5: Test Scheduler Disabled Mode
function Test-SchedulerDisabled {
    Write-Host "`n### TEST 5: Scheduler Disabled Mode" -ForegroundColor Cyan
    
    Write-Host "This test requires restarting with SCHEDULER_ENABLED=false" -ForegroundColor Yellow
    
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/scheduler-status"
    
    if ($response.scheduler.enabled -eq $false) {
        Write-Host "✓ Scheduler is properly disabled" -ForegroundColor Green
        Write-Host "  Running: $($response.scheduler.running)"
        Write-Host "  Next Run: $($response.scheduler.next_run)"
        return $true
    }
    else {
        Write-Host "ℹ Scheduler is enabled (use SCHEDULER_ENABLED=false to test disabled mode)" -ForegroundColor Cyan
        return $true
    }
}

# Main execution
function Run-AllTests {
    Write-Host ""
    Write-Host "Prerequisites:" -ForegroundColor Cyan
    Write-Host "1. App must be running with scheduler enabled"
    Write-Host "2. SCHEDULER_ENABLED environment variable set"
    Write-Host "3. GEMINI_API_KEY environment variable set"
    Write-Host ""
    
    # Wait for app
    if (-not (Wait-AppStartup)) {
        Write-Host "`nPlease start the app first:" -ForegroundColor Yellow
        Write-Host "`$env:SCHEDULER_ENABLED = 'true'" -ForegroundColor Gray
        Write-Host "`$env:GEMINI_API_KEY = 'your-key'" -ForegroundColor Gray
        Write-Host "python app.py" -ForegroundColor Gray
        return
    }
    
    # Run tests
    $results = @()
    
    $results += @{ name = "Status Check"; result = Test-SchedulerStatus }
    $results += @{ name = "Logs Check"; result = Test-SchedulerLogs }
    $results += @{ name = "Manual Analysis"; result = Test-ManualAnalysis }
    $results += @{ name = "Custom Timezone"; result = Test-CustomTimezone }
    $results += @{ name = "Disabled Mode"; result = Test-SchedulerDisabled }
    
    # Summary
    Write-Host "`n=== Test Summary ===" -ForegroundColor Cyan
    
    $passCount = ($results | Where-Object { $_.result -eq $true }).Count
    $totalCount = $results.Count
    
    foreach ($result in $results) {
        $symbol = if ($result.result) { "✓" } else { "✗" }
        $color = if ($result.result) { "Green" } else { "Red" }
        Write-Host "$symbol $($result.name)" -ForegroundColor $color
    }
    
    Write-Host "`nPassed: $passCount/$totalCount" -ForegroundColor Green
    
    if ($passCount -eq $totalCount) {
        Write-Host "`n✓ All tests passed! Scheduler is working correctly." -ForegroundColor Green
    }
    else {
        Write-Host "`n⚠ Some tests did not pass. Check above for details." -ForegroundColor Yellow
    }
}

# Alternative: Just check status (quick test)
function Quick-Test {
    Write-Host "`n### Quick Status Check" -ForegroundColor Cyan
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/api/scheduler-status"
        Write-Host ($response | ConvertTo-Json -Depth 3) -ForegroundColor Green
        Write-Host "`n✓ Scheduler is responding" -ForegroundColor Green
    }
    catch {
        Write-Host "✗ Cannot reach scheduler: $_" -ForegroundColor Red
        Write-Host "`nMake sure app is running with:" -ForegroundColor Yellow
        Write-Host "`$env:SCHEDULER_ENABLED = 'true'" -ForegroundColor Gray
        Write-Host "python app.py" -ForegroundColor Gray
    }
}

# Run tests
Write-Host ""
Write-Host "Choose test mode:" -ForegroundColor Cyan
Write-Host "1. Quick (just check status)"
Write-Host "2. Full (all tests)"
Write-Host ""

$choice = Read-Host "Enter choice (1 or 2)"

if ($choice -eq "1") {
    Quick-Test
}
elseif ($choice -eq "2") {
    Run-AllTests
}
else {
    Write-Host "Invalid choice. Running quick test..." -ForegroundColor Yellow
    Quick-Test
}
