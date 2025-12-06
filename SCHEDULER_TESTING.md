# Scheduler Testing Guide

## Overview

This guide covers all testing methods for the auto-scheduler implementation.

---

## Quick Test (5 minutes)

### Test 1: Verify Scheduler Status Endpoint

**Start the app:**
```powershell
$env:SCHEDULER_ENABLED = "true"
$env:GEMINI_API_KEY = "your-key"
python app.py
```

**In another terminal, check status:**
```powershell
curl http://localhost:8000/api/scheduler-status
```

**Expected Response:**
```json
{
  "status": "success",
  "scheduler": {
    "enabled": true,
    "running": true,
    "schedule": "mon 08:00",
    "timezone": "UTC",
    "next_run": "2025-12-08 08:00:00 UTC"
  }
}
```

---

## Unit Tests

### Create Test File

```powershell
# Create test file
New-Item -ItemType File -Path "test_scheduler.py"
```

### Test 1: Scheduler Initialization

```python
import pytest
from layer4_email.scheduler import AnalysisScheduler, create_scheduler
import os

def test_scheduler_initialization():
    """Test scheduler initializes with correct parameters"""
    scheduler = AnalysisScheduler(
        enabled=True,
        schedule_day="mon",
        schedule_hour=8,
        schedule_minute=0,
        timezone="UTC"
    )
    
    assert scheduler.enabled == True
    assert scheduler.schedule_day == "mon"
    assert scheduler.schedule_hour == 8
    assert scheduler.schedule_minute == 0
    assert scheduler.timezone == "UTC"
    assert scheduler.is_running == False

def test_scheduler_disabled():
    """Test scheduler respects enabled flag"""
    scheduler = AnalysisScheduler(enabled=False)
    scheduler.start()
    
    assert scheduler.is_running == False

def test_create_scheduler_from_env():
    """Test factory function reads environment"""
    os.environ['SCHEDULER_ENABLED'] = 'true'
    os.environ['SCHEDULER_DAY'] = 'fri'
    os.environ['SCHEDULER_HOUR'] = '18'
    os.environ['SCHEDULER_TIMEZONE'] = 'Asia/Kolkata'
    
    scheduler = create_scheduler()
    
    assert scheduler.enabled == True
    assert scheduler.schedule_day == 'fri'
    assert scheduler.schedule_hour == 18
    assert scheduler.timezone == 'Asia/Kolkata'
```

### Test 2: Status Method

```python
def test_get_status():
    """Test get_status returns correct format"""
    scheduler = AnalysisScheduler(enabled=True)
    status = scheduler.get_status()
    
    assert 'enabled' in status
    assert 'running' in status
    assert 'schedule' in status
    assert 'timezone' in status
    assert 'next_run' in status
```

### Test 3: Scheduler Lifecycle

```python
def test_scheduler_start_stop():
    """Test scheduler start and stop"""
    scheduler = AnalysisScheduler(enabled=True)
    
    # Start scheduler
    scheduler.start()
    assert scheduler.is_running == True
    assert scheduler.scheduler is not None
    
    # Stop scheduler
    scheduler.stop()
    assert scheduler.is_running == False
```

### Run Unit Tests

```powershell
# Install pytest
pip install pytest pytest-asyncio

# Run tests
pytest test_scheduler.py -v
```

**Expected Output:**
```
test_scheduler.py::test_scheduler_initialization PASSED
test_scheduler.py::test_scheduler_disabled PASSED
test_scheduler.py::test_create_scheduler_from_env PASSED
test_scheduler.py::test_get_status PASSED
test_scheduler.py::test_scheduler_start_stop PASSED

====== 5 passed in 0.45s ======
```

---

## Integration Tests

### Test 1: App Startup with Scheduler

```powershell
# Terminal 1: Start app with scheduler enabled
$env:SCHEDULER_ENABLED = "true"
$env:GEMINI_API_KEY = "test-key"
python app.py

# Look for these log messages:
# AnalysisScheduler initialized - Enabled: true, Schedule: mon 08:00 UTC
# Scheduler started successfully - Next run: 2025-12-08 08:00:00 UTC
```

### Test 2: Scheduler Status Endpoint

```powershell
# Terminal 2: Call status endpoint
Invoke-RestMethod -Uri "http://localhost:8000/api/scheduler-status" | ConvertTo-Json

# Should return:
# {
#   "status": "success",
#   "scheduler": {
#     "enabled": true,
#     "running": true,
#     "schedule": "mon 08:00",
#     "timezone": "UTC",
#     "next_run": "2025-12-08 08:00:00 UTC"
#   }
# }
```

### Test 3: Manual Analysis Still Works

```powershell
# While scheduler is running, trigger manual analysis
$body = @{
    window_days = 7
    email = "test@example.com"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/analyze" `
  -Method Post `
  -Body $body `
  -ContentType "application/json"

# Should complete without scheduler interference
```

### Test 4: Scheduler Disabled

```powershell
# Restart app with scheduler disabled
$env:SCHEDULER_ENABLED = "false"
python app.py

# Check status endpoint
Invoke-RestMethod -Uri "http://localhost:8000/api/scheduler-status" | ConvertTo-Json

# Should show:
# "running": false
# "next_run": "Not scheduled"
```

---

## Manual Testing (Simulate Schedule Trigger)

### Test 1: Modify Schedule to Run Soon

```powershell
# Set scheduler to run in 2 minutes from now
$now = Get-Date
$targetTime = $now.AddMinutes(2)

$env:SCHEDULER_ENABLED = "true"
$env:SCHEDULER_HOUR = $targetTime.Hour
$env:SCHEDULER_MINUTE = $targetTime.Minute
$env:SCHEDULER_DAY = $targetTime.DayOfWeek.ToString().ToLower().Substring(0,3)
$env:GEMINI_API_KEY = "your-key"

python app.py
```

**Monitor logs:**
```powershell
Get-Content logs/scheduler.log -Wait | Select-String "SCHEDULER"
```

**Expected logs (in 2 minutes):**
```
[SCHEDULER] Starting automatic analysis execution at 2025-12-07 00:25:00
[SCHEDULER] Executing: python orchestrator.py --window-days 7
[SCHEDULER] Analysis completed successfully
```

### Test 2: Test Different Timezones

```powershell
# Test UTC
$env:SCHEDULER_TIMEZONE = "UTC"
$env:SCHEDULER_HOUR = "8"

# Then check status endpoint - should show 08:00 UTC

# Test Asia/Kolkata
$env:SCHEDULER_TIMEZONE = "Asia/Kolkata"
$env:SCHEDULER_HOUR = "13"  # 13:30 IST = 08:00 UTC

# Check status - should show correct IST time
```

### Test 3: Test All Days of Week

```powershell
@("mon", "tue", "wed", "thu", "fri", "sat", "sun") | ForEach-Object {
    $env:SCHEDULER_DAY = $_
    $status = Invoke-RestMethod -Uri "http://localhost:8000/api/scheduler-status"
    Write-Host "Day: $_ - Schedule: $($status.scheduler.schedule)"
}
```

---

## Log Monitoring

### View Scheduler Logs

```powershell
# Real-time monitoring
Get-Content logs/scheduler.log -Wait

# Last 20 lines
Get-Content logs/scheduler.log -Tail 20

# Filter for scheduler entries
Get-Content logs/scheduler.log | Select-String "SCHEDULER"

# Filter for errors
Get-Content logs/scheduler.log | Select-String "ERROR|Error"
```

### Expected Log Entries

**On Startup:**
```
AnalysisScheduler initialized - Enabled: true, Schedule: mon 08:00 UTC
Scheduler started successfully - Next run: 2025-12-08 08:00:00 UTC
```

**On Execution:**
```
[SCHEDULER] Starting automatic analysis execution at 2025-12-08 08:00:00
[SCHEDULER] Executing: python orchestrator.py --window-days 7
[SCHEDULER] Analysis completed successfully
```

**On Error:**
```
[SCHEDULER] GEMINI_API_KEY not set - analysis skipped
[SCHEDULER] Error during analysis execution: [error details]
```

**On Shutdown:**
```
Scheduler stopped successfully
```

---

## Load Testing

### Test Multiple Endpoints

```powershell
# Run 5 concurrent status requests
1..5 | ForEach-Object {
    Start-Job -ScriptBlock {
        Invoke-RestMethod -Uri "http://localhost:8000/api/scheduler-status"
    }
} | Wait-Job | Receive-Job

# All should return successfully
```

### Test Concurrent Execution

```powershell
# Trigger manual analysis
$body = @{ window_days = 7; email = "test@example.com" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/analyze" `
  -Method Post `
  -Body $body `
  -ContentType "application/json" `
  -TimeoutSec 900

# While that's running, check scheduler status
Invoke-RestMethod -Uri "http://localhost:8000/api/scheduler-status"

# Both should complete without interference
```

---

## Error Scenario Testing

### Test 1: Missing GEMINI_API_KEY

```powershell
$env:SCHEDULER_ENABLED = "true"
$env:GEMINI_API_KEY = ""  # Remove key

python app.py

# Expected log:
# [SCHEDULER] GEMINI_API_KEY not set - analysis skipped
```

### Test 2: Invalid Timezone

```powershell
$env:SCHEDULER_ENABLED = "true"
$env:SCHEDULER_TIMEZONE = "Invalid/Timezone"

python app.py

# Should handle gracefully or log error
```

### Test 3: Orchestrator Timeout

The scheduler has a 30-minute timeout. To test:

```powershell
# Modify scheduler.py timeout temporarily to 5 seconds
# Run scheduler
# Observe timeout logging:
# [SCHEDULER] Analysis execution timeout (30 minutes)
```

---

## Checklist-Based Testing

### Pre-Deployment Testing

- [ ] Scheduler initializes on app startup
- [ ] Scheduler respects SCHEDULER_ENABLED flag
- [ ] `/api/scheduler-status` endpoint returns correct format
- [ ] Manual analysis works independently of scheduler
- [ ] Scheduler logs include `[SCHEDULER]` prefix
- [ ] App shuts down gracefully
- [ ] Scheduler disabled mode works
- [ ] Custom timezones work correctly
- [ ] Different days of week work
- [ ] Manual and automatic flows don't interfere

### Production Testing

- [ ] Set correct timezone for deployment region
- [ ] Verify GEMINI_API_KEY is set in production
- [ ] Verify DEFAULT_EMAIL is correct
- [ ] Monitor logs for first scheduled execution
- [ ] Verify email was sent to DEFAULT_EMAIL
- [ ] Check scheduler status via `/api/scheduler-status`
- [ ] Verify next run time is correct
- [ ] Ensure logs are properly written to logs/ directory

---

## Quick Test Commands

### One-Command Setup and Test

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment
$env:SCHEDULER_ENABLED = "true"
$env:GEMINI_API_KEY = "test-key"

# 3. Start app (in background or separate terminal)
python app.py

# 4. Wait 2 seconds for startup
Start-Sleep -Seconds 2

# 5. Check scheduler status
curl http://localhost:8000/api/scheduler-status | jq '.scheduler.next_run'

# 6. View logs
Get-Content logs/scheduler.log | Select-String "Scheduler"
```

### Docker Testing (If Deployed)

```bash
# View logs
docker logs <container-id> | grep SCHEDULER

# Check status from host
curl http://localhost:8000/api/scheduler-status

# Exec into container
docker exec -it <container-id> bash
tail -f logs/scheduler.log
```

---

## Expected Test Results

### Success Indicators

- ✅ Scheduler initializes with `enabled: true`
- ✅ Next run time is future date/time
- ✅ Manual analysis completes independently
- ✅ Logs contain `[SCHEDULER]` prefix messages
- ✅ Status endpoint is responsive
- ✅ Timezone is correctly applied to next_run
- ✅ All 7 days of week work as schedule_day
- ✅ Hours 0-23 work correctly
- ✅ Minutes 0-59 work correctly

### Failure Indicators

- ❌ Scheduler shows `running: false` when enabled
- ❌ No log entries with `[SCHEDULER]` prefix
- ❌ Status endpoint returns 500 error
- ❌ Manual analysis fails when scheduler is enabled
- ❌ Next run time is in the past
- ❌ Invalid timezone silently fails
- ❌ App crashes on startup

---

## Troubleshooting Tests

### If Scheduler Shows "Not scheduled"

1. Check logs: `Get-Content logs/scheduler.log | Select-String "Scheduler"`
2. Verify SCHEDULER_ENABLED: `$env:SCHEDULER_ENABLED`
3. Verify timezone: `[System.TimeZoneInfo]::GetSystemTimeZones() | Select-String "Asia/Kolkata"`
4. Restart app with debug logging

### If Status Endpoint Returns 500

1. Check app console for errors
2. Verify scheduler is initialized: look for "AnalysisScheduler initialized"
3. Check if APScheduler is installed: `pip show apscheduler`
4. Restart app

### If Logs Show Wrong Time

1. Verify `SCHEDULER_TIMEZONE` is set correctly
2. Check system timezone: `Get-TimeZone`
3. Use UTC timezone for testing: `$env:SCHEDULER_TIMEZONE = "UTC"`

---

## Summary

**Basic Test** (2 minutes):
1. Start app with `SCHEDULER_ENABLED=true`
2. Call `/api/scheduler-status`
3. Verify response format

**Comprehensive Test** (15 minutes):
1. Run unit tests with pytest
2. Test status endpoint
3. Test manual analysis
4. Test scheduler disabled
5. Monitor logs
6. Test different configurations

**Production Test** (30 minutes):
1. Deploy with correct timezone
2. Verify first scheduled execution
3. Check email delivery
4. Monitor logs for 24 hours
5. Verify next run time calculation
