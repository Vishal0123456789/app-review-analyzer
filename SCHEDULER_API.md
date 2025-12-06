# Scheduler API Reference

## Endpoints

### 1. Get Scheduler Status

**Endpoint**: `GET /api/scheduler-status`

**Description**: Returns current scheduler configuration and next scheduled run time.

**Authentication**: None required

**Request**:
```bash
curl http://localhost:8000/api/scheduler-status
```

**Response (Scheduler Enabled)**:
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

**Response (Scheduler Disabled)**:
```json
{
  "status": "success",
  "scheduler": {
    "enabled": false,
    "running": false,
    "schedule": "mon 08:00",
    "timezone": "UTC",
    "next_run": "Not scheduled"
  }
}
```

**Response (Error - Scheduler Not Initialized)**:
```json
{
  "status": "error",
  "message": "Scheduler not initialized"
}
```

**Status Codes**:
- `200 OK` - Status retrieved successfully
- `500 Internal Server Error` - Scheduler initialization failed

---

### 2. Manual Analysis (Existing Endpoint)

**Endpoint**: `POST /api/analyze`

**Description**: Manually trigger analysis pipeline. Works independently of scheduler.

**Request Body**:
```json
{
  "window_days": 7,
  "email": "user@example.com"
}
```

**Parameters**:
- `window_days` (integer, required): Analysis window in days (7-35)
- `email` (string, optional): Additional recipient email

**Response (Success)**:
```json
{
  "status": "success",
  "message": "Weekly pulse generated and emails sent.",
  "window_days": 7,
  "pulse_file_name": "review_pulse_20251123_20251205.json",
  "pulse_data": {
    "start_date": "2025-11-23",
    "end_date": "2025-12-05",
    "top_themes": [...],
    "quotes": [...],
    "action_ideas": [...],
    "note_markdown": "..."
  }
}
```

**Response (Error - Invalid Window Days)**:
```json
{
  "status": 400,
  "detail": {
    "status": "error",
    "message": "window_days must be between 7 and 35 (1-5 weeks)."
  }
}
```

**Response (Error - Missing API Key)**:
```json
{
  "status": 500,
  "detail": {
    "status": "error",
    "message": "GEMINI_API_KEY environment variable is not set. Please set it before running."
  }
}
```

**Status Codes**:
- `200 OK` - Analysis completed successfully
- `400 Bad Request` - Invalid request parameters
- `500 Internal Server Error` - Analysis failed or timeout

**Timeout**: 15 minutes (900 seconds)

---

### 3. Download Pulse File (Existing Endpoint)

**Endpoint**: `GET /api/download-pulse`

**Description**: Download a previously generated pulse file in JSON format.

**Query Parameters**:
- `file` (string, required): Filename to download (must start with "review_pulse_")

**Example**:
```bash
curl http://localhost:8000/api/download-pulse?file=review_pulse_20251123_20251205.json
```

**Response**: File download (application/json)

**Status Codes**:
- `200 OK` - File downloaded successfully
- `400 Bad Request` - Invalid filename
- `404 Not Found` - File does not exist

---

## Usage Examples

### Example 1: Check If Scheduler Is Running

```bash
# PowerShell
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/scheduler-status" -Method Get
$response | ConvertTo-Json

# Output:
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

### Example 2: Trigger Manual Analysis with Custom Email

```bash
# PowerShell
$body = @{
    window_days = 14
    email = "analyst@company.com"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/analyze" `
  -Method Post `
  -Body $body `
  -ContentType "application/json"

# Output:
# {
#   "status": "success",
#   "message": "Weekly pulse generated and emails sent.",
#   "window_days": 14,
#   "pulse_file_name": "review_pulse_...",
#   ...
# }
```

### Example 3: Download Latest Pulse File

```bash
# PowerShell
$pulsePath = "review_pulse_20251123_20251205.json"
Invoke-RestMethod -Uri "http://localhost:8000/api/download-pulse?file=$pulsePath" `
  -Method Get `
  -OutFile "pulse_$((Get-Date).ToString('yyyyMMdd')).json"
```

### Example 4: Monitor Scheduler Status in Script

```powershell
# Check scheduler status every minute
while ($true) {
    $status = Invoke-RestMethod -Uri "http://localhost:8000/api/scheduler-status"
    
    if ($status.scheduler.enabled) {
        Write-Host "Scheduler enabled, next run: $($status.scheduler.next_run)"
    } else {
        Write-Host "Scheduler is disabled"
    }
    
    Start-Sleep -Seconds 60
}
```

---

## Scheduler Behavior Details

### When Scheduler Triggers

The scheduler executes at the configured time:

1. **Request**: APScheduler triggers `_run_analysis()` at scheduled time
2. **Validation**: Checks GEMINI_API_KEY is set
3. **Execution**: Runs `python orchestrator.py --window-days {WINDOW_DAYS}`
4. **Emails**: Sends results to DEFAULT_EMAIL
5. **Logging**: Logs all steps with `[SCHEDULER]` prefix

### Email Recipients

- **Manual Analysis** (`/api/analyze`): User's email + DEFAULT_EMAIL
- **Scheduled Analysis**: DEFAULT_EMAIL only

### Analysis Windows

- **Manual**: User specifies (7-35 days)
- **Scheduled**: Uses SCHEDULER_WINDOW_DAYS (default: 7)

### Timeouts

- **Manual**: 15 minutes (900 seconds)
- **Scheduled**: 30 minutes (1800 seconds)

---

## Monitoring

### Real-Time Status Check

```bash
# Check scheduler status
curl http://localhost:8000/api/scheduler-status | jq '.scheduler.next_run'

# Output:
# "2025-12-08 08:00:00 UTC"
```

### Log Monitoring

```bash
# Watch for scheduler execution
Get-Content -Path "logs/scheduler.log" -Wait | Select-String "SCHEDULER"

# Or check recent scheduler entries
Get-Content "logs/scheduler.log" -Tail 20 | Select-String "SCHEDULER"
```

### Expected Log Entries

```
AnalysisScheduler initialized - Enabled: true, Schedule: mon 08:00 UTC
Scheduler started successfully - Next run: 2025-12-08 08:00:00 UTC
[SCHEDULER] Starting automatic analysis execution at 2025-12-08 08:00:00
[SCHEDULER] Executing: python orchestrator.py --window-days 7
[SCHEDULER] Analysis completed successfully
```

---

## Error Responses

### Missing GEMINI_API_KEY

**Scheduler**: Logs error, skips execution
```
[SCHEDULER] GEMINI_API_KEY not set - analysis skipped
```

**Manual API**: Returns 500 error
```json
{
  "status": 500,
  "detail": {
    "status": "error",
    "message": "GEMINI_API_KEY environment variable is not set..."
  }
}
```

### Analysis Timeout

**Scheduler**: Logs timeout, moves to next scheduled time
```
[SCHEDULER] Analysis execution timeout (30 minutes)
```

**Manual API**: Returns 500 error with timeout message
```json
{
  "status": 500,
  "detail": {
    "status": "error",
    "message": "Analysis timeout (15 minutes)..."
  }
}
```

### Invalid Request Parameters

**Manual API**: Returns 400 error
```json
{
  "status": 400,
  "detail": {
    "status": "error",
    "message": "window_days must be between 7 and 35 (1-5 weeks)."
  }
}
```

---

## Integration Examples

### Frontend Integration (React)

```typescript
// Check scheduler status on app load
const checkSchedulerStatus = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/scheduler-status');
    const data = await response.json();
    
    if (data.scheduler.enabled) {
      console.log(`Scheduler next run: ${data.scheduler.next_run}`);
    } else {
      console.log('Scheduler is disabled');
    }
  } catch (error) {
    console.error('Failed to fetch scheduler status:', error);
  }
};

// Call on component mount
useEffect(() => {
  checkSchedulerStatus();
}, []);
```

### Scheduled Task Automation (Node.js)

```javascript
// Schedule status check every 5 minutes
setInterval(async () => {
  const response = await fetch('http://localhost:8000/api/scheduler-status');
  const data = await response.json();
  
  if (data.scheduler.enabled && data.scheduler.next_run !== 'Not scheduled') {
    console.log(`Next automated run: ${data.scheduler.next_run}`);
  }
}, 5 * 60 * 1000);
```

---

## Limitations & Notes

1. **Schedule Changes Require Restart**: To change schedule, update env vars and restart app
2. **Timezone Matters**: Use standard timezone strings (e.g., `Asia/Kolkata`, not `IST`)
3. **Concurrent Executions**: Scheduler and manual analysis can run simultaneously without conflict
4. **Email Configuration**: Scheduler always sends to DEFAULT_EMAIL; manual API respects user-provided email
5. **No Manual Trigger Endpoint**: Current implementation doesn't support manual scheduler trigger via API (can be added if needed)

---

## FAQ

**Q: Can I manually trigger the scheduler outside of schedule?**
A: Not via the current API. You can call `/api/analyze` for manual analysis instead.

**Q: What if manual analysis and scheduler run at the same time?**
A: They're independent processes. Both will complete successfully without conflicts.

**Q: How do I change the schedule without restarting?**
A: Currently not supported. Update env vars and restart the application.

**Q: Can scheduler send to multiple emails?**
A: Modify `scheduler.py` `_run_analysis()` method to customize recipient list.

**Q: What happens if an analysis takes longer than the timeout?**
A: Process terminates and error is logged. Next scheduled run proceeds normally.
