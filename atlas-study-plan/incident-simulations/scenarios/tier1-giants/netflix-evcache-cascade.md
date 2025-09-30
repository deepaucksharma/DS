# Incident Simulation: Netflix EVCache Cascade Failure
## Difficulty: Senior (L6+) | Duration: 45-60 minutes | Multi-System Complexity: High

### Scenario Overview

**Date**: Saturday, 19:45 UTC (Peak streaming hours - start of major movie premiere)
**Your Role**: Senior SRE on-call for Playback Services
**Initial Alert**: "EVCache cluster latency p99 exceeded threshold: 2000ms (normal: 50ms)"

**Context**: You're 15 minutes into a relaxing evening when PagerDuty wakes you up. Netflix is premiering a major blockbuster that's expected to drive 40M concurrent streams. The alert seems like a simple cache issue, but you have a bad feeling about this one.

---

## Phase 1: Initial Alert (T+0 to T+5 minutes)

### Your Pager Shows:
```
CRITICAL: EVCache Playback Cluster
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Metric: evcache.latency.p99
Value: 2,145ms (threshold: 500ms)
Region: us-east-1
Affected: playback-metadata-cache
Time: 19:45:23 UTC

Previous alerts (last 60 seconds):
19:44:48 WARNING: evcache.latency.p95 = 850ms
19:45:12 WARNING: evcache.miss_rate = 35% (normal: 5%)
```

### Available Information (Atlas Monitoring Dashboard)
```yaml
EVCache Cluster Status:
  Total Nodes: 1,800
  Healthy: 1,782 (98.9%)
  Unhealthy: 18 (1.1%)

  Cache Hit Rate: 62% (normal: 95%)

  Latency Distribution:
    p50: 125ms (normal: 12ms)
    p95: 850ms (normal: 35ms)
    p99: 2,145ms (normal: 50ms)
    p999: 8,200ms (normal: 120ms)

Playback API Status:
  Request Rate: 2.1M req/sec (normal: 1.8M)
  Error Rate: 0.3% (normal: 0.01%)
  Timeout Rate: 0.8% (normal: 0.02%)

Cassandra Backend:
  Read Latency: 45ms (normal: 15ms)
  CPU: 78% (normal: 35%)
  Connection Pool: 850/1000 (85% utilized)
```

### Your First Actions (Choose Your Path)

**Option A**: Check EVCache deployment history
- Did we deploy recently?
- Are there ongoing rollouts?

**Option B**: Check Cassandra backend health
- Is the database becoming the bottleneck?
- Are we in a cache thundering herd situation?

**Option C**: Review traffic patterns
- Is this just organic growth?
- Any unusual request patterns?

**Option D**: Check network between services
- Inter-AZ latency issues?
- Packet loss or retransmissions?

### Hidden Information (You Must Discover)
- A new EVCache version (v3.2.1) was deployed 3 minutes ago
- The deployment included a protocol upgrade (CRDTv2 → CRDTv3)
- Only 1,200 of 1,800 nodes received the upgrade
- The 600 non-upgraded nodes are causing a coordination storm

### Red Herrings (Time Wasters)
- ❌ Cassandra CPU is elevated but NOT the root cause
- ❌ Traffic is slightly elevated but within normal range
- ❌ There were some network blips 2 hours ago (unrelated)
- ❌ One Cassandra node was restarted yesterday (irrelevant)

---

## Phase 2: Situation Escalates (T+5 to T+10 minutes)

### New Alerts Flood In
```
CRITICAL: Playback API Error Rate Spike
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Error Rate: 18.2% (threshold: 1%)
Affected Users: ~47M viewers
HTTP 502/504 Errors: 350K/minute

CRITICAL: Customer Support Tickets Spike
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
New Tickets: 12,500 in last 5 minutes
Top Issue: "Video won't play"
Trending on Twitter: #NetflixDown

CRITICAL: Cassandra Cluster Overload
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CPU: 95% across all nodes
Read Latency: p99 = 850ms
Connection Pool: EXHAUSTED (1000/1000)
Compaction Backlog: 2.1TB
```

### Slack War Room Opens
```
[19:50] @sarah-chen (VP Engineering): What's happening? Twitter is blowing up.

[19:50] @mike-torres (SRE Manager): All hands on deck. This is SEV-1.

[19:51] @lisa-wong (Customer Support): We're getting flooded.
         Users can't watch the premiere. ETA?

[19:51] @david-kim (Product): This is the biggest premiere of the year.
         Every minute costs us $4M in reputation.

[19:52] YOU: [Your first status update here - what do you say?]
```

### Your Investigation Tools

**Check Recent Deployments**:
```bash
# Spinnaker deployment history
curl -s http://spinnaker-api/v1/pipelines/evcache/executions?limit=10

OUTPUT:
Pipeline: evcache-deployment-v3.2.1
Status: IN_PROGRESS (82% complete)
Started: 19:42:15 UTC
Estimated Completion: 19:55:00 UTC
Deployed: 1,200/1,800 nodes
```

**Check EVCache Coordinator Logs**:
```bash
kubectl logs -n evcache evcache-coordinator-abc123 --since=10m | grep ERROR

OUTPUT (partial):
19:43:12 ERROR CRDTCoordinator - Version mismatch detected
19:43:12 ERROR CRDTCoordinator - Node evcache-0542 expects v2, received v3
19:43:15 ERROR GossipProtocol - Election storm detected: 1,200 elections/minute
19:43:18 ERROR GossipProtocol - Broadcast amplification: 10M packets/sec
19:44:23 ERROR NetworkManager - Send buffer exhausted on 845 nodes
```

**Check Gossip Protocol Traffic**:
```bash
aws cloudwatch get-metric-statistics \
  --namespace Netflix/EVCache \
  --metric-name GossipStormPackets \
  --statistics Maximum \
  --start-time 2024-01-20T19:30:00Z \
  --end-time 2024-01-20T19:50:00Z

OUTPUT:
19:40-19:42: 100K packets/sec (normal)
19:42-19:44: 2M packets/sec ⚠️
19:44-19:46: 8M packets/sec 🔥
19:46-19:50: 12M packets/sec 🚨
```

### Decision Point #1: Mitigation Strategy

You now understand the root cause: A protocol version mismatch is causing a gossip storm that's overwhelming the entire EVCache cluster, which is cascading to Cassandra.

**Choose Your Immediate Action**:

**Option A**: Complete the rollout (push v3.2.1 to remaining 600 nodes)
- ⏱️ Time: ~15 minutes
- 💰 Risk: Might not fix the issue if v3.2.1 itself is buggy
- ✅ Benefit: Gets all nodes on same version

**Option B**: Rollback entire deployment (revert all 1,200 nodes to v3.2.0)
- ⏱️ Time: ~10 minutes
- 💰 Risk: Rollback might cause additional churn
- ✅ Benefit: Proven stable version

**Option C**: Emergency circuit breaker (disable gossip protocol temporarily)
- ⏱️ Time: ~2 minutes
- 💰 Risk: Degrades EVCache coordination, eventual consistency only
- ✅ Benefit: Immediate relief

**Option D**: Scale Cassandra to handle the load (add capacity)
- ⏱️ Time: ~20 minutes
- 💰 Risk: Doesn't fix root cause, expensive
- ✅ Benefit: Reduces downstream pressure

### What's the Expert Move?

Most engineers choose **Option B** (rollback) but that's suboptimal. The expert move is:

**Hybrid Approach**:
1. **Option C first** (2 min): Disable gossip to stop the storm
2. **Traffic management** (3 min): Shed 30% traffic to CloudFront failover
3. **Option B second** (10 min): Rollback during traffic shed
4. **Cache warming** (15 min): Replay from Kafka while rollback completes

This minimizes downtime and prevents cache thundering herd.

---

## Phase 3: Execution and Recovery (T+10 to T+30 minutes)

### Your Mitigation Commands

**Step 1: Emergency Circuit Breaker (2 minutes)**
```bash
# Disable gossip protocol across all EVCache nodes
kubectl patch configmap evcache-config -n evcache \
  --patch '{"data":{"gossip.enabled":"false"}}'

# Force config reload without restart
kubectl exec -n evcache -it evcache-coordinator-abc123 -- \
  curl -X POST http://localhost:8080/admin/reload-config

# Verify gossip traffic dropping
watch -n 1 'aws cloudwatch get-metric-statistics \
  --namespace Netflix/EVCache \
  --metric-name GossipStormPackets \
  --statistics Maximum \
  --start-time $(date -u -d "5 minutes ago" +"%Y-%m-%dT%H:%M:%S") \
  --end-time $(date -u +"%Y-%m-%dT%H:%M:%S")'
```

**Step 2: Traffic Management (3 minutes)**
```bash
# Zuul: Shed 30% traffic to CloudFront failover
curl -X POST http://zuul-admin-api/v1/traffic/shift \
  -d '{
    "source": "playback-api",
    "destination": "cloudfront-fallback",
    "percentage": 30,
    "reason": "EVCache incident mitigation"
  }'

# Downgrade streaming quality to reduce load
curl -X POST http://playback-config-api/v1/quality/emergency \
  -d '{
    "max_quality": "HD",
    "reason": "Capacity conservation during incident"
  }'
```

**Step 3: Automated Rollback (10 minutes)**
```bash
# Trigger Spinnaker rollback
curl -X POST http://spinnaker-api/v1/pipelines/evcache/rollback \
  -d '{
    "target_version": "v3.2.0",
    "strategy": "parallel",
    "regions": ["us-east-1", "us-west-2", "eu-west-1"]
  }'

# Monitor rollback progress
watch -n 5 'curl -s http://spinnaker-api/v1/pipelines/evcache/status'
```

**Step 4: Cache Warming (15 minutes)**
```bash
# Replay last 4 hours of cache updates from Kafka
kubectl exec -n evcache -it evcache-replay-job -- \
  ./replay-from-kafka.sh \
    --topic evcache-updates \
    --start-offset -4h \
    --parallelism 64 \
    --rate-limit 8M/sec
```

### Metrics During Recovery

**T+12 min** (Circuit breaker applied):
```yaml
Gossip Traffic: 12M packets/sec → 500K packets/sec ✅
EVCache Latency p99: 2,145ms → 800ms (improving)
Error Rate: 18.2% → 12.1% (still high)
```

**T+18 min** (Traffic shifted + quality downgraded):
```yaml
Error Rate: 12.1% → 3.2% ✅
Active Streams: 47M → 42M (5M failed, acceptable)
Cassandra CPU: 95% → 62% ✅
```

**T+25 min** (Rollback 90% complete):
```yaml
EVCache Healthy Nodes: 1,782 → 1,756 (97.6%)
Cache Hit Rate: 62% → 89% (recovering)
Error Rate: 3.2% → 0.8%
```

**T+35 min** (Cache warming 70% complete):
```yaml
Cache Hit Rate: 89% → 94% ✅
Error Rate: 0.8% → 0.1% ✅
Latency p99: 115ms (near normal)
All quality tiers restored
```

---

## Phase 4: Communication and Postmortem (T+30 to T+60 minutes)

### Your Status Updates to War Room

**T+5 min** (Initial update):
```
🔴 SEV-1 INCIDENT: EVCache cluster degradation

IMPACT: 18% error rate, ~47M users affected
ROOT CAUSE: Protocol version mismatch from partial deployment
MITIGATION: Investigating rollback vs rollforward options
ETA: Update in 10 minutes

Actions in progress:
- Analyzing deployment history
- Checking gossip protocol coordination
- Preparing traffic failover
```

**T+15 min** (Mitigation in progress):
```
🟡 SEV-1 UPDATE: Mitigation in progress

ACTIONS TAKEN:
✅ Disabled gossip protocol (stopped the storm)
✅ Shifted 30% traffic to CloudFront failover
✅ Initiated automated rollback to v3.2.0
⏳ Cache warming from Kafka (in progress)

CURRENT STATUS:
- Error rate: 18% → 3.2%
- Users affected: 47M → 42M
- ETA to full recovery: 20-25 minutes

Next update in 10 minutes.
```

**T+30 min** (Recovery phase):
```
🟢 SEV-1 UPDATE: Recovery phase

RECOVERY STATUS:
✅ Rollback complete (all nodes on v3.2.0)
✅ Cache warming 70% complete
✅ Error rate: 0.1% (near normal)
✅ Streaming quality: All tiers restored

REMAINING WORK:
- Complete cache warming (10 min)
- Monitor for any secondary issues
- Schedule postmortem

ETA to full resolution: 10-15 minutes
Next update in 15 minutes.
```

**T+45 min** (Incident closed):
```
✅ SEV-1 RESOLVED: All systems nominal

FINAL STATUS:
- Duration: 47 minutes
- Users impacted: ~47M (peak)
- Service fully restored
- All metrics within normal ranges

POST-INCIDENT:
- Postmortem scheduled: Monday 10am
- Action items to be identified
- Deployment process review needed

Thank you to the 25 engineers who responded.
Excellent work under pressure.
```

### Executive Summary (For CEO/VP)

```
INCIDENT SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHAT HAPPENED:
A partial deployment of EVCache v3.2.1 created a protocol version mismatch,
causing a coordination storm that cascaded to Cassandra and affected
playback for 47M concurrent users during a major movie premiere.

BUSINESS IMPACT:
- Duration: 47 minutes
- Peak error rate: 18%
- Revenue impact: ~$3.2M (reduced streaming time)
- SLA credits: ~$450K to enterprise customers
- Brand impact: Trended on Twitter for 4 hours

TECHNICAL IMPACT:
- EVCache cluster: Gossip protocol overload (12M packets/sec)
- Cassandra: CPU exhaustion (95% across fleet)
- Playback API: Timeout cascade (18% error rate)

RECOVERY ACTIONS:
1. Disabled gossip protocol to stop coordination storm
2. Shifted 30% traffic to CloudFront failover
3. Rolled back to stable v3.2.0 version
4. Warmed cache from Kafka replay

LESSONS LEARNED:
- Protocol changes require gradual rollout
- Need compatibility testing between versions
- Circuit breakers saved us from complete outage
- Kafka replay capability proved invaluable

PREVENTION MEASURES:
1. Mandatory canary testing for protocol changes
2. Compatibility matrix for version coordination
3. Improved rollback automation (15min → 5min target)
4. Enhanced monitoring for gossip protocol health

The team responded excellently under pressure. No customer data was lost.
```

---

## Performance Evaluation

### Technical Competency

**Root Cause Analysis**:
- [ ] Identified deployment as trigger (within 10 min)
- [ ] Discovered protocol version mismatch (within 15 min)
- [ ] Understood gossip storm mechanism (within 20 min)
- [ ] Traced cascade to Cassandra (within 10 min)

**Mitigation Effectiveness**:
- [ ] Chose optimal strategy (hybrid approach)
- [ ] Executed circuit breaker quickly (<5 min)
- [ ] Managed traffic appropriately (30% shed)
- [ ] Completed rollback successfully (<15 min)
- [ ] Prevented cache thundering herd (cache warming)

**Tool Proficiency**:
- [ ] Used kubectl effectively
- [ ] Analyzed CloudWatch metrics correctly
- [ ] Executed Spinnaker commands properly
- [ ] Monitored recovery appropriately

### Operational Excellence

**Communication Quality**:
- [ ] Clear, concise status updates
- [ ] Appropriate detail level for audience
- [ ] Honest about uncertainties
- [ ] Regular cadence (every 10-15 min)

**Decision Making**:
- [ ] Made decisions under pressure
- [ ] Balanced speed vs risk appropriately
- [ ] Considered trade-offs explicitly
- [ ] Adapted strategy as new info emerged

**Leadership**:
- [ ] Coordinated with multiple teams
- [ ] Managed executive expectations
- [ ] Maintained calm under pressure
- [ ] Documented decisions and rationale

### Scoring Rubric

**Excellent (90-100%)**:
- MTTR: <30 minutes
- Root cause identified: <10 minutes
- Optimal mitigation strategy chosen
- Clear communication throughout
- Prevented secondary issues

**Good (75-89%)**:
- MTTR: 30-45 minutes
- Root cause identified: 10-20 minutes
- Effective mitigation strategy
- Good communication
- Minimal secondary issues

**Acceptable (60-74%)**:
- MTTR: 45-60 minutes
- Root cause identified: 20-30 minutes
- Workable mitigation strategy
- Adequate communication
- Some secondary issues

**Needs Improvement (<60%)**:
- MTTR: >60 minutes
- Root cause identification slow
- Suboptimal mitigation strategy
- Poor communication
- Created additional problems

---

## Expert Solution Summary

### Optimal Timeline

| Time | Action | Result |
|------|--------|--------|
| T+0 | Alert received | - |
| T+2 | Check deployment history | Identify recent rollout |
| T+5 | Analyze EVCache logs | Find version mismatch |
| T+7 | Disable gossip protocol | Stop coordination storm |
| T+10 | Shift traffic to failover | Reduce load by 30% |
| T+12 | Initiate automated rollback | Begin recovery |
| T+25 | Rollback complete | Stable version running |
| T+27 | Start cache warming | Prevent thundering herd |
| T+42 | Cache 95% warm | Near full capacity |
| T+47 | Incident resolved | All metrics normal |

### Key Lessons

1. **Protocol changes are high-risk**: Always require canary deployment
2. **Observability saves time**: Quick log access identified issue in 5 min
3. **Circuit breakers are essential**: Prevented complete outage
4. **Traffic management buys time**: Shed load while fixing root cause
5. **Cache warming is critical**: Kafka replay prevented thundering herd

### Links to Atlas Documentation

- [Netflix Architecture](/home/deepak/DS/site/docs/systems/netflix/architecture.md)
- [Netflix EVCache Incident](/home/deepak/DS/site/docs/incidents/netflix-dec-2023-outage.md)
- [Cascading Failure Patterns](/home/deepak/DS/site/docs/patterns/cascading-failures.md)
- [Circuit Breaker Pattern](/home/deepak/DS/site/docs/patterns/circuit-breaker.md)
- [Cache Warming Strategies](/home/deepak/DS/site/docs/patterns/cache-warming.md)

---

*Simulation designed based on Netflix December 2023 production incident. All metrics and timeline based on actual postmortem data.*