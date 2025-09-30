# Incident Simulation: Uber Surge Pricing Calculation Failure
## Difficulty: Senior (L6+) | Duration: 40-55 minutes | Real-Time Systems Crisis

### Scenario Overview

**Date**: Friday, 21:30 local time (New Year's Eve - highest demand of the year)
**Your Role**: On-call SRE for Marketplace Systems
**Initial Alert**: "Surge pricing calculator service experiencing high error rate"

**Context**: It's New Year's Eve in major cities worldwide. Demand is 30x normal. You're enjoying dinner when your phone erupts with alerts. This is the night that makes or breaks Uber's quarterly revenue.

---

## Phase 1: The Alert Storm (T+0 to T+3 minutes)

### Your Pager Explodes:
```
CRITICAL: Surge Pricing Service Error Rate
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Service: surge-calculation-service
Error Rate: 42% (threshold: 1%)
Region: Global (all regions affected)
Impact: REVENUE CRITICAL

CRITICAL: Kafka Consumer Lag Spike
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Topic: ride-requests
Consumer: surge-calculator
Lag: 2.4M messages (normal: <1000)
Growing: +50K/second

CRITICAL: Redis Cluster Memory Alert
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Cluster: surge-pricing-cache
Memory Usage: 98% (threshold: 85%)
Evictions: 125K/second
Keys Lost: 4.2M in last 2 minutes
```

### War Room Immediately Forms
```
[21:30] @jane-kim (VP Marketplace): This is New Year's Eve.
        We cannot have surge pricing down. This is a P0.

[21:30] @marcus-chen (Pricing Team Lead): We're losing millions per minute.
        Drivers see no surge, riders see infinite wait times.

[21:31] @sarah-lopez (Operations): 157 cities affected.
        Support tickets: 45K and climbing.

[21:31] @david-patel (CTO): All hands. I want updates every 5 minutes.
        What's the ETA?

[21:31] YOU: [Initial response - you have 60 seconds]
```

### Available Monitoring Data
```yaml
Surge Calculation Service:
  Instances: 64 (Java 11, 16 cores each)
  Request Rate: 850K req/sec (normal: 120K)
  Error Rate: 42%
  Response Time:
    p50: 2,400ms (normal: 35ms)
    p99: 45,000ms (normal: 150ms)
  Timeouts: 315K/minute

Kafka Consumer:
  Consumer Group: surge-calculator-group
  Partitions: 100
  Lag: 2.4M messages and growing
  Throughput: 12K msg/sec (normal: 95K msg/sec)
  Processing Time: 8.2 seconds per message (normal: 0.1s)

Redis Cluster:
  Nodes: 48 (r6g.2xlarge)
  Memory: 98% across all nodes
  Evictions: 125K/second
  Connection Pool: 15K/20K (75% utilized)
  Latency p99: 850ms (normal: 2ms)

Cassandra (Historical Data):
  Read Latency: 4,500ms (normal: 25ms)
  CPU: 96% across fleet
  Compaction: STALLED
  Query Queue: 8.4M queries backed up
```

### Initial Investigation Commands

**Check Service Health**:
```bash
# Service status
kubectl get pods -n marketplace | grep surge-calculation

OUTPUT:
surge-calculation-7f8b4c-2xq9p    1/1     Running   5 restarts   8h
surge-calculation-7f8b4c-5mk2w    0/1     CrashLoopBackOff        8h
surge-calculation-7f8b4c-8nwp3    1/1     Running   12 restarts  8h
... (64 pods total, 18 in CrashLoopBackOff)
```

**Check JVM Memory**:
```bash
# JVM heap usage
kubectl exec -n marketplace surge-calculation-7f8b4c-2xq9p -- \
  jstat -gc 1

OUTPUT:
S0C    S1C    S0U    S1U      EC       EU        OC         OU       MC     MU
0.0   0.0    0.0    0.0   524288.0 524288.0  4718592.0  4718589.0  125952.0 119485.5

Old Generation: 99.99% FULL
Major GC count: 1,847 (in last 10 minutes!)
GC Time: 8.2 seconds average per GC
```

**Check Redis Memory Usage**:
```bash
# Redis memory breakdown
redis-cli -h surge-cache-1.prod INFO memory

OUTPUT:
used_memory:62537318400  # 58.2GB of 60GB
used_memory_peak:62914560000
mem_fragmentation_ratio:0.98
evicted_keys:4251837  # Last 2 minutes!

# Key patterns being evicted
redis-cli -h surge-cache-1.prod --bigkeys

OUTPUT (top keys by size):
[00.00%] Biggest hash   "surge:demand:newyork:manhattan"        2,847,392 fields
[00.00%] Biggest hash   "surge:demand:london:westend"           2,156,841 fields
[00.00%] Biggest hash   "surge:demand:tokyo:shibuya"            1,983,275 fields
```

### Hidden Problem (You Must Discover)

The surge calculation service is performing a **massive join query** for each calculation:
1. Read historical demand from Cassandra (last 90 days)
2. Load geospatial data from Redis (all active drivers in area)
3. Calculate surge multiplier with ML model (CPU-intensive)
4. Store result back to Redis

During normal load, this works fine. But at 30x load with New Year's Eve:
- Cassandra queries take 4+ seconds (normally 25ms)
- Redis cache misses force more Cassandra queries
- ML model calculations exhaust JVM heap
- Garbage collection pauses block all requests
- Kafka consumer can't keep up, lag grows

**The Death Spiral**:
```
More demand → More calculations needed → More Cassandra queries
→ Slower responses → Kafka lag grows → Surge values stale
→ Redis keys expire → Cache misses → Even more Cassandra queries
→ System grinds to halt
```

---

## Phase 2: The Crisis Deepens (T+3 to T+8 minutes)

### Business Impact Becomes Clear

```
[21:33] @jane-kim: I'm looking at the dashboard. We're losing $2.8M per minute.
        Drivers are going offline because they see no surge pricing.

[21:34] @marcus-chen: Data Science reports surge multipliers are frozen at
        1.0x across all cities. No driver incentive to come online.

[21:35] @sarah-lopez: 178 cities now. Wait times: 45+ minutes average.
        Cancellation rate: 67%. This is a disaster.

[21:35] @david-patel: I need a plan in 2 minutes. What are we doing?
```

### New Alerts - The Cascade
```
CRITICAL: Driver App - No Surge Displayed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Impact: Drivers not incentivized to go online
Cities: 178/180 affected
Active Drivers: 125K online (normal for NYE: 450K)
Driver churn: 12K/minute going offline

CRITICAL: Rider App - Infinite Wait Times
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Average Wait: 47 minutes (normal: 4 min)
Match Rate: 18% (normal: 94%)
Cancellation Rate: 67%
App Store Reviews: Dropping rapidly

WARNING: Database Connection Pool Exhausted
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Service: surge-calculation
Cassandra Pool: 1000/1000 (EXHAUSTED)
Redis Pool: 18,500/20,000 (93%)
Connection Wait Time: 25+ seconds
```

### Investigation Reveals Root Cause

**Check Database Query Performance**:
```sql
-- Query being run 850K times per second!
SELECT
    demand_level,
    driver_count,
    avg_wait_time,
    historical_surge
FROM marketplace.historical_demand
WHERE
    city = 'new_york'
    AND zone = 'manhattan'
    AND hour_of_day = 21
    AND day_of_week = 5
    AND date >= NOW() - INTERVAL 90 DAYS
ORDER BY date DESC
LIMIT 1000;

-- This query takes 4.5 seconds during high load!
-- Normally: 25ms
```

**Check ML Model Performance**:
```bash
# CPU profiling
kubectl exec -n marketplace surge-calculation-7f8b4c-2xq9p -- \
  jcmd 1 VM.native_memory summary

OUTPUT:
Total reserved: 8.2GB
Total committed: 7.8GB

ML Model Memory:
- Feature vectors: 3.2GB
- Model weights: 1.8GB
- Intermediate calculations: 2.1GB

GC Impact:
- Full GC every 3-4 seconds
- GC pauses: 8-12 seconds each
- Application threads blocked during GC
```

---

## Phase 3: Decision Time (T+8 to T+12 minutes)

### You've Identified Three Problems:

1. **Cassandra Query Storm**: Expensive queries hitting database
2. **Redis Memory Exhaustion**: Cache evictions forcing more queries
3. **JVM Heap Pressure**: ML model calculations causing GC death spiral

### Mitigation Options

**Option A**: Emergency Scale (Add Capacity)
```yaml
Actions:
  - Scale surge-calculation from 64 → 256 instances
  - Add Redis cache nodes: 48 → 96 nodes
  - Scale Cassandra read replicas

Time: 8-12 minutes
Cost: $45K/hour additional
Risk: Won't fix root cause, might make worse
Success Probability: 30%
```

**Option B**: Fallback to Static Surge (Simplified Logic)
```yaml
Actions:
  - Deploy emergency surge-simple-service
  - Use rule-based surge (no ML, no historical data)
  - Basic formula: (demand / supply) * time_multiplier

Time: 3-5 minutes (pre-built fallback exists)
Cost: $0 additional
Risk: Less accurate pricing, but works
Success Probability: 95%
```

**Option C**: Query Optimization (Fix Root Cause)
```yaml
Actions:
  - Add query result caching layer
  - Reduce historical lookback from 90 days → 7 days
  - Implement request batching
  - Disable ML model temporarily

Time: 15-20 minutes
Cost: $0 additional
Risk: Requires code changes under pressure
Success Probability: 70%
```

**Option D**: Hybrid Approach
```yaml
Actions:
  1. Immediately deploy static surge (Option B) - 3 min
  2. Scale Redis cache (partial Option A) - 5 min
  3. Optimize queries in parallel (Option C) - 15 min
  4. Gradual rollback to ML-based surge - 10 min

Total Time: 25-30 minutes
Cost: $8K/hour additional
Success Probability: 98%
```

### The Expert Move: Option D (Hybrid)

**Execution Plan**:
```bash
# Step 1: Deploy static surge calculator (3 minutes)
kubectl apply -f k8s/surge-simple-fallback.yaml

kubectl patch service surge-calculation-service \
  --patch '{"spec":{"selector":{"app":"surge-simple"}}}'

# Verify traffic switching
curl http://surge-api.internal/health
# Expected: {"version":"simple-fallback","status":"healthy"}

# Step 2: Scale Redis (5 minutes)
aws elasticache modify-replication-group \
  --replication-group-id surge-pricing-cache \
  --node-group-count 72 \
  --apply-immediately

# Step 3: Optimize ML service queries (parallel work)
# Deploy config change to reduce historical lookback
kubectl set env deployment/surge-calculation \
  HISTORICAL_DAYS=7 \
  ENABLE_QUERY_CACHE=true \
  BATCH_SIZE=100

# Step 4: Increase JVM heap and tune GC
kubectl set resources deployment/surge-calculation \
  --limits=memory=24Gi \
  --requests=memory=24Gi

kubectl set env deployment/surge-calculation \
  JAVA_OPTS="-Xmx20g -Xms20g -XX:+UseG1GC -XX:MaxGCPauseMillis=200"
```

---

## Phase 4: Recovery and Monitoring (T+12 to T+40 minutes)

### Timeline of Recovery

**T+15 min** (Static surge deployed):
```yaml
Status Update:
  Service: surge-simple-fallback
  Error Rate: 42% → 0.2% ✅
  Response Time p99: 45s → 85ms ✅
  Kafka Lag: 2.4M → Draining at 85K/sec

Business Impact:
  Surge Pricing: Active (rule-based)
  Driver Availability: Recovering
  Match Rate: 18% → 35% (improving)

Known Limitations:
  - Surge less accurate than ML-based
  - Simpler logic may over/under price some areas
  - Acceptable for emergency restoration
```

**T+22 min** (Redis scaled, ML service optimized):
```yaml
Status Update:
  Redis Nodes: 48 → 72 ✅
  Memory Usage: 98% → 64% ✅
  Cache Hit Rate: 12% → 78% (recovering)

  ML Service:
    Historical Lookback: 90 days → 7 days
    Query Time: 4.5s → 180ms ✅
    JVM Heap: 8GB → 20GB
    GC Pauses: 8-12s → 0.5-1.2s ✅

Kafka Consumer:
  Lag: 2.4M → 450K (draining)
  Throughput: 12K/sec → 72K/sec ✅
```

**T+35 min** (Gradual rollback to ML-based surge):
```yaml
Traffic Split:
  surge-simple: 70%
  surge-ml-optimized: 30% (canary)

ML Service Performance:
  Error Rate: 0.1%
  Response Time p99: 125ms
  Kafka Lag: 450K → 15K

Business Metrics:
  Active Drivers: 125K → 398K ✅
  Match Rate: 35% → 82% ✅
  Wait Time: 47min → 6min ✅
  Revenue Rate: Recovered to 92% of target
```

**T+48 min** (Full ML-based surge restored):
```yaml
INCIDENT RESOLVED:
  Service: 100% traffic on surge-ml-optimized
  All Metrics: Within normal ranges
  Kafka Lag: <500 messages
  Revenue: Fully recovered

System State:
  ✅ Surge pricing accurate and fast
  ✅ Driver availability normal for NYE
  ✅ Rider experience restored
  ✅ No data loss or corruption
```

### Status Updates to War Room

**T+3 min** (Initial assessment):
```
🔴 P0 INCIDENT: Surge pricing system failure

ROOT CAUSE (preliminary):
- Cassandra query storm under 30x NYE load
- Redis cache exhaustion causing cascading failures
- JVM heap pressure from ML calculations

IMMEDIATE ACTIONS:
1. Deploying static surge fallback (ETA: 3 min)
2. Scaling Redis cache capacity
3. Optimizing ML service queries

ESTIMATED RECOVERY: 15-20 minutes to basic service,
40 minutes to full ML-based surge restoration.

Business impact: $2.8M/min loss. Mitigating now.
```

**T+15 min** (Partial recovery):
```
🟡 P0 UPDATE: Basic surge pricing restored

RECOVERY STATUS:
✅ Static surge deployed and serving 100% traffic
✅ Error rate: 42% → 0.2%
✅ Drivers seeing surge incentives (simplified)
⏳ Redis scaling in progress
⏳ ML service optimization in progress

CURRENT STATE:
- Match rate: 18% → 35% (improving)
- Active drivers: Growing (125K → 245K)
- Wait times: Decreasing (47min → 18min)

NEXT STEPS:
- Complete Redis scaling (7 min)
- Deploy optimized ML service (10 min)
- Gradual rollback to ML-based surge

ETA to full restoration: 25-30 minutes
```

**T+35 min** (Near full recovery):
```
🟢 P0 UPDATE: ML-based surge 30% deployed

RECOVERY STATUS:
✅ Redis scaled to 72 nodes (memory: 98% → 64%)
✅ ML service optimized (query time: 4.5s → 180ms)
✅ Kafka lag draining (2.4M → 15K)
✅ Business metrics recovering strongly

CANARY DEPLOYMENT:
- 30% traffic on ML-based surge (optimized)
- 70% traffic on static surge (stable)
- All metrics healthy, preparing 100% rollback

Match rate: 82% | Active drivers: 398K | Wait: 6min

ETA to full ML restoration: 10-15 minutes
```

**T+48 min** (Incident resolved):
```
✅ P0 RESOLVED: All systems optimal

FINAL STATUS:
- 100% traffic on optimized ML-based surge
- All KPIs within normal ranges for NYE
- Revenue fully recovered
- Zero data loss

INCIDENT DURATION: 48 minutes
ESTIMATED REVENUE IMPACT: $134M loss
(48 min × $2.8M/min)

PREVENTION MEASURES NEEDED:
1. Query optimization for high-load scenarios
2. Improved cache warming strategy
3. Better JVM tuning for ML workloads
4. Enhanced monitoring and alerting

POST-MORTEM: Scheduled for Jan 2nd
THANK YOU to 42 engineers who responded.
```

### Executive Summary for Leadership

```markdown
NEW YEAR'S EVE SURGE PRICING INCIDENT

WHAT HAPPENED:
At peak New Year's Eve demand (30x normal load), our ML-based surge
pricing calculator overwhelmed Cassandra with expensive historical queries,
exhausted Redis cache memory, and experienced JVM GC death spirals.

This caused complete surge pricing failure across 178 cities globally,
resulting in no driver incentives and 67% ride cancellations.

BUSINESS IMPACT:
- Duration: 48 minutes (21:30-22:18 local time)
- Revenue loss: ~$134M (direct impact)
- Driver churn: 12K drivers went offline
- Customer satisfaction: 45K support tickets, App Store review drop
- Market perception: Trending negatively on social media

TECHNICAL ROOT CAUSE:
1. Cassandra queries not optimized for extreme load (4.5s vs 25ms)
2. Redis memory exhaustion causing cache eviction storm
3. ML model heap pressure causing 8-12 second GC pauses

RECOVERY STRATEGY:
Phase 1 (3 min): Deploy static surge fallback - immediate stabilization
Phase 2 (20 min): Scale Redis + optimize queries - prepare for ML
Phase 3 (25 min): Gradual rollback to optimized ML surge
Total: 48 minutes to full recovery

WHAT WENT WELL:
- Pre-built fallback system activated in 3 minutes
- War room assembled and coordinated effectively
- No data loss or corruption occurred
- Recovery plan executed flawlessly

WHAT NEEDS IMPROVEMENT:
- Load testing didn't catch this failure mode
- Monitoring didn't alert before cascade
- No automatic failover to static surge
- Query optimization should have been proactive

IMMEDIATE ACTIONS TAKEN:
✅ Reduced historical query lookback (90 days → 7 days)
✅ Implemented query result caching
✅ Scaled Redis capacity by 50%
✅ Improved JVM tuning for ML workloads

LONG-TERM PREVENTION:
1. Automatic failover to static surge at high error rates
2. Database query circuit breakers
3. Progressive degradation framework
4. Better load testing for peak scenarios
5. Query optimization as part of quarterly reviews

COST OF INCIDENT: $134M revenue loss + $450K infra scaling
COST OF PREVENTION: ~$2M/year in optimization and testing

ROI: Prevention costs 1.5% of potential incident cost.
```

---

## Performance Evaluation Scorecard

### Technical Competency (40 points)

**Root Cause Analysis** (15 points):
- [ ] Identified Cassandra query storm (5 pts)
- [ ] Discovered Redis memory exhaustion (5 pts)
- [ ] Understood JVM GC pressure (5 pts)

**Mitigation Strategy** (15 points):
- [ ] Chose hybrid approach (10 pts) / Other approach (0-8 pts)
- [ ] Executed fallback deployment quickly (3 pts)
- [ ] Managed gradual recovery appropriately (2 pts)

**Technical Execution** (10 points):
- [ ] Correctly deployed static surge (3 pts)
- [ ] Properly scaled Redis (2 pts)
- [ ] Applied query optimizations (3 pts)
- [ ] Monitored recovery effectively (2 pts)

### Operational Excellence (30 points)

**Communication** (15 points):
- [ ] Initial status update clear and timely (4 pts)
- [ ] Regular updates every 10-15 min (4 pts)
- [ ] Appropriate detail for different audiences (4 pts)
- [ ] Honest about uncertainties and risks (3 pts)

**Decision Making** (15 points):
- [ ] Made critical decisions quickly (5 pts)
- [ ] Balanced immediate vs long-term fixes (5 pts)
- [ ] Considered business impact appropriately (5 pts)

### Business Acumen (20 points)

**Impact Assessment** (10 points):
- [ ] Calculated revenue impact accurately (3 pts)
- [ ] Understood customer experience effects (3 pts)
- [ ] Considered market perception (2 pts)
- [ ] Identified reputational risks (2 pts)

**Trade-off Analysis** (10 points):
- [ ] Weighed accuracy vs availability (5 pts)
- [ ] Balanced cost vs recovery speed (3 pts)
- [ ] Prioritized correctly (2 pts)

### Leadership & Collaboration (10 points)

- [ ] Coordinated effectively with multiple teams (3 pts)
- [ ] Managed executive expectations (3 pts)
- [ ] Maintained composure under pressure (2 pts)
- [ ] Documented decisions and rationale (2 pts)

### Scoring

- **90-100 points**: Exceptional - Incident Commander level
- **75-89 points**: Excellent - Senior SRE level
- **60-74 points**: Good - Mid-level SRE proficiency
- **<60 points**: Needs improvement - Additional training recommended

---

## Key Lessons from This Simulation

### 1. Fallback Systems Are Essential
Pre-built fallback (static surge) allowed 3-minute recovery. Without it, recovery would have taken 30+ minutes and caused $200M+ loss.

### 2. Database Queries Under Load
Queries that work fine at normal load can become disasters at 30x load. Always optimize for worst-case, not average-case.

### 3. Cache Sizing Matters
Redis memory exhaustion caused cascading cache misses that amplified the database problem. Always over-provision cache capacity.

### 4. JVM GC Tuning Is Critical
8-12 second GC pauses made a bad situation catastrophic. Proper heap sizing and G1GC tuning prevented complete collapse.

### 5. Hybrid Approach Usually Wins
Pure scaling (Option A) wouldn't have worked. Pure optimization (Option C) too slow. Hybrid approach (Option D) provided both immediate relief and long-term fix.

---

## Links to Atlas Documentation

- [Uber Architecture](/home/deepak/DS/site/docs/systems/uber/architecture.md)
- [Uber Marketplace Systems](/home/deepak/DS/site/docs/systems/uber/request-flow.md)
- [Kafka Consumer Lag Debugging](/home/deepak/DS/site/docs/debugging/kafka-consumer-lag-debugging-production.md)
- [Redis Memory Management](/home/deepak/DS/site/docs/patterns/cache-management.md)
- [Circuit Breaker Pattern](/home/deepak/DS/site/docs/patterns/circuit-breaker.md)
- [Progressive Degradation](/home/deepak/DS/site/docs/patterns/progressive-degradation.md)

---

*Simulation based on Uber's 2020 marketplace outage and surge pricing challenges during peak demand periods. Metrics and recovery strategies informed by actual incident reports.*