# Incident Log Template

Use this template to document incidents for post-mortem analysis and continuous improvement.

## Incident Metadata

**Incident ID:** INC-YYYY-MM-DD-###  
**Date/Time:** YYYY-MM-DD HH:MM UTC  
**Severity:** P0 / P1 / P2 / P3  
**Status:** Investigating / Mitigating / Resolved / Closed  
**Incident Commander:** [Name]  
**Scribe:** [Name]

## Impact Assessment

**Services Affected:**
- [ ] Dokploy UI
- [ ] Application: [name]
- [ ] Database
- [ ] Monitoring
- [ ] Other: ___________

**User Impact:**
- Affected users: [number or percentage]
- Duration: [start] to [end] = [total minutes]
- Symptoms: [what users experienced]

**Business Impact:**
- Revenue loss: [if applicable]
- SLA breach: Yes / No
- Customer complaints: [number]

## Timeline (All times in UTC)

| Time | Event | Action Taken | Person |
|------|-------|--------------|--------|
| HH:MM | First alert triggered | Uptime Kuma sent notification | Automated |
| HH:MM | Engineer joined | Began investigation | [Name] |
| HH:MM | Root cause identified | [description] | [Name] |
| HH:MM | Mitigation started | [action] | [Name] |
| HH:MM | Service restored | [verification] | [Name] |
| HH:MM | Incident closed | Post-mortem scheduled | [Name] |

## Root Cause Analysis

### Symptoms Observed
[What did monitoring/logs show?]

### Investigation Steps
1. [First thing checked]
2. [Second thing checked]
3. [etc.]

### Root Cause
[The underlying technical reason for the failure]

**Why it happened:**
- Immediate cause: [trigger event]
- Contributing factors: [what allowed it to escalate]
- Root cause: [systemic issue]

## Resolution

### Mitigation Steps
1. [What was done to restore service]
2. [Emergency fixes applied]
3. [Rollback or workaround used]

### Permanent Fix
[What will prevent recurrence]

### Verification
- [ ] Service health checks passing
- [ ] Application accessible
- [ ] Monitoring restored
- [ ] No errors in logs
- [ ] Performance metrics normal

## Prevention

### Immediate Actions (This Week)
- [ ] [Action item 1] - Owner: [Name] - Due: [Date]
- [ ] [Action item 2] - Owner: [Name] - Due: [Date]

### Short-term Actions (This Month)
- [ ] [Improvement 1] - Owner: [Name] - Due: [Date]
- [ ] [Improvement 2] - Owner: [Name] - Due: [Date]

### Long-term Actions (This Quarter)
- [ ] [System improvement] - Owner: [Name] - Due: [Date]

## Lessons Learned

### What Went Well
- [Positive aspects of the response]
- [Effective monitoring/alerting]
- [Good communication]

### What Went Wrong
- [Delayed response]
- [Ineffective troubleshooting]
- [Poor communication]

### What We'll Do Differently
- [Process improvements]
- [Tool enhancements]
- [Training needs]

## Supporting Information

### Logs
```
[Relevant log excerpts with timestamps]
```

### Commands Executed
```bash
# [Commands run during investigation/mitigation]
docker logs container-name
docker restart container-name
# etc.
```

### Metrics/Graphs
[Screenshots or links to monitoring dashboards showing the incident]

### Communication
- Internal notification: [method] at [time]
- Customer notification: [method] at [time]
- Status page updated: Yes / No

## Attachments
- Log files: [links or filenames]
- Screenshots: [links or filenames]
- Related incidents: [INC-XXX, INC-YYY]

---

## Example Filled Template

**Incident ID:** INC-2024-01-15-001  
**Date/Time:** 2024-01-15 14:32 UTC  
**Severity:** P1  
**Status:** Closed  
**Incident Commander:** Alice  
**Scribe:** Bob

### Impact Assessment
**Services Affected:**
- [x] Application: api.example.com
- [ ] Dokploy UI

**User Impact:**
- Affected users: 100% (all users)
- Duration: 14:32 to 14:47 UTC = 15 minutes
- Symptoms: 502 Bad Gateway errors

**Business Impact:**
- Revenue loss: ~$500 (15 min downtime)
- SLA breach: No (within 99.9% monthly target)
- Customer complaints: 3

### Timeline
| Time | Event | Action | Person |
|------|-------|--------|--------|
| 14:32 | Uptime Kuma alert | "api.example.com is DOWN" | Automated |
| 14:34 | Alice joined | Checked Dokploy dashboard | Alice |
| 14:36 | Root cause found | App container OOM killed (Exited 137) | Alice |
| 14:38 | Mitigation | Increased memory limit to 1GB | Alice |
| 14:40 | Container restarted | docker restart api-app | Alice |
| 14:42 | Service verified | curl api.example.com/health = 200 | Alice |
| 14:47 | Monitoring cleared | Uptime Kuma showing "Up" | Automated |

### Root Cause
Node.js memory leak in background job processor caused gradual memory growth until OOM killer terminated the container.

**Why it happened:**
- Immediate: Memory limit (512MB) too low for current load
- Contributing: No memory monitoring alerts configured
- Root cause: Code doesn't properly release processed job data

### Resolution
**Mitigation:** Increased memory limit from 512MB to 1GB (2x headroom)

**Permanent Fix:**
1. Code fix deployed to v1.2.1 (released 2024-01-16)
2. Added memory usage alerts at 80% and 90%
3. Enabled automatic container restart on OOM

### Prevention
**Immediate (This Week):**
- [x] Add memory alerts to Uptime Kuma - Alice - 2024-01-16
- [x] Review all container memory limits - Bob - 2024-01-17

**Short-term (This Month):**
- [ ] Implement memory profiling in staging - Dev team - 2024-01-30
- [ ] Add load testing to CI/CD - DevOps - 2024-02-01

### Lessons Learned
**What Went Well:**
- Fast detection (Uptime Kuma alerted immediately)
- Clear logs showing OOM (docker logs + dmesg)
- Quick mitigation (15 min total)

**What Went Wrong:**
- No proactive memory alerts (reactive, not proactive)
- Insufficient testing under load

**What We'll Do Differently:**
- Add memory monitoring to all containers
- Run weekly load tests in staging
- Review resource limits quarterly
