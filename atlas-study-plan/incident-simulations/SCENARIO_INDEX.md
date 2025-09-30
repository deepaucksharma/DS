# Complete Incident Scenario Index
## 50 Production-Ready Incident Simulations

### Overview

This index catalogs all 50 incident simulations organized by company tier, difficulty level, and failure pattern. Each scenario is designed to teach specific lessons from real production incidents.

---

## Scenario Organization

### By Company Tier

**Tier 1: The Giants** (16 scenarios)
- Netflix (3 scenarios)
- Uber (3 scenarios)
- Amazon (2 scenarios)
- Google (2 scenarios)
- Meta/Facebook (2 scenarios)
- Microsoft (2 scenarios)
- LinkedIn (1 scenario)
- Twitter/X (1 scenario)

**Tier 2: The Innovators** (17 scenarios)
- Stripe (2 scenarios)
- Spotify (2 scenarios)
- Airbnb (2 scenarios)
- Discord (2 scenarios)
- Cloudflare (2 scenarios)
- GitHub (2 scenarios)
- Shopify (1 scenario)
- DoorDash (1 scenario)
- Slack (1 scenario)
- Pinterest (1 scenario)
- Twitch (1 scenario)

**Tier 3: The Specialists** (17 scenarios)
- Coinbase (2 scenarios)
- Reddit (2 scenarios)
- Datadog (2 scenarios)
- Robinhood (2 scenarios)
- Zoom (2 scenarios)
- TikTok (2 scenarios)
- Square (1 scenario)
- Snap (1 scenario)
- Dropbox (1 scenario)
- Instacart (1 scenario)
- OpenAI (1 scenario)

### By Difficulty Level

```yaml
Junior (L3-L4): 15 scenarios
  Focus: Single-service failures
  Complexity: Low
  Time: 30-45 minutes
  Concepts: Basic debugging, rollback, scaling

Mid-Level (L5): 15 scenarios
  Focus: Multi-service cascades
  Complexity: Medium
  Time: 45-60 minutes
  Concepts: Root cause analysis, mitigation strategies

Senior (L6+): 15 scenarios
  Focus: Complex system failures
  Complexity: High
  Time: 60-90 minutes
  Concepts: Trade-off decisions, prevention design

Incident Commander: 5 scenarios
  Focus: Leadership and coordination
  Complexity: Extreme
  Time: 90-120 minutes
  Concepts: Multi-team management, executive communication
```

### By Failure Pattern

```yaml
Cascading Failures (15 scenarios):
  - Retry storms
  - Circuit breaker failures
  - Dependency cascades
  - Connection pool exhaustion

Data Integrity (10 scenarios):
  - Corruption
  - Loss
  - Consistency violations
  - Replication lag

Performance Degradation (10 scenarios):
  - Memory leaks
  - GC pauses
  - Slow queries
  - Lock contention

Capacity Exhaustion (8 scenarios):
  - Resource limits
  - Queue backups
  - Rate limiting
  - Disk space

Network Failures (4 scenarios):
  - Partitions
  - Latency spikes
  - DNS issues

Security Incidents (3 scenarios):
  - DDoS attacks
  - Authentication failures
  - Data breaches
```

---

## Complete Scenario Catalog

### Tier 1: The Giants (16 scenarios)

#### Netflix (3 scenarios)

**NF-001: EVCache Cascade Failure** ⭐ [CREATED]
- **File**: `scenarios/tier1-giants/netflix-evcache-cascade.md`
- **Difficulty**: Senior (L6+)
- **Duration**: 45-60 minutes
- **Patterns**: C-001 (Retry Storm), C-015 (Thundering Herd), P-007 (GC Pauses)
- **Skills**: Protocol debugging, cache warming, circuit breakers
- **Real Incident**: Netflix December 2023 outage
- **Key Lesson**: Protocol version incompatibility can cause cluster-wide coordination storms

**NF-002: Regional Failover During Peak Traffic**
- **Difficulty**: Senior (L6+)
- **Patterns**: N-001 (Network Partition), C-003 (Failover Cascade)
- **Scenario**: AWS us-east-1 region degradation during Saturday night peak
- **Challenge**: Fail over 40M active streams without disruption
- **Key Decision**: Gradual vs immediate failover

**NF-003: Content Delivery CDN Overload**
- **Difficulty**: Mid-Level (L5)
- **Patterns**: Cap-005 (Bandwidth Exhaustion), C-015 (Cache Miss Storm)
- **Scenario**: New popular series launch overwhelms CDN
- **Challenge**: Balance cost vs user experience

#### Uber (3 scenarios)

**UB-001: Surge Pricing Calculation Failure** ⭐ [CREATED]
- **File**: `scenarios/tier1-giants/uber-surge-pricing-failure.md`
- **Difficulty**: Senior (L6+)
- **Duration**: 40-55 minutes
- **Patterns**: C-008 (Connection Pool), P-002 (Memory Leak), Cap-003 (Kafka Lag)
- **Skills**: Database optimization, fallback strategies, business impact assessment
- **Real Incident**: Uber 2020 marketplace outage
- **Key Lesson**: Need fallback systems for revenue-critical services

**UB-002: Real-Time Location Processing Lag**
- **Difficulty**: Senior (L6+)
- **Patterns**: Cap-003 (Kafka Consumer Lag), P-018 (Lock Contention)
- **Scenario**: Driver location updates lag 30+ seconds during rush hour
- **Challenge**: Incorrect ETAs causing failed matches

**UB-003: Payment Processing Timeout Cascade**
- **Difficulty**: Mid-Level (L5)
- **Patterns**: C-002 (Circuit Breaker), P-012 (Slow Query)
- **Scenario**: Payment gateway slowdown cascades to ride completion
- **Challenge**: Users can't complete rides, drivers not getting paid

#### Amazon (2 scenarios)

**AZ-001: S3 Eventual Consistency Race Condition**
- **Difficulty**: Senior (L6+)
- **Patterns**: D-005 (Eventual Consistency), D-008 (Race Condition)
- **Scenario**: Deployment system fails due to S3 list-after-write inconsistency
- **Challenge**: Diagnose subtle consistency timing issues

**AZ-002: DynamoDB Throttling Cascade**
- **Difficulty**: Mid-Level (L5)
- **Patterns**: Cap-012 (Rate Limiting), C-001 (Retry Storm)
- **Scenario**: Black Friday traffic exceeds provisioned capacity
- **Challenge**: Balance costs vs capacity during peak events

#### Google (2 scenarios)

**GO-001: Spanner Global Replication Lag**
- **Difficulty**: Senior (L6+)
- **Patterns**: D-005 (Consistency), N-006 (Cross-Region Latency)
- **Scenario**: Multi-region transaction latency spikes during fiber cut
- **Challenge**: Maintain consistency guarantees during network degradation

**GO-002: GKE Control Plane Overload**
- **Difficulty**: Mid-Level (L5)
- **Patterns**: Cap-008 (API Rate Limit), C-022 (Deployment Storm)
- **Scenario**: Simultaneous deployments overwhelm Kubernetes API
- **Challenge**: Coordinate deployment strategies across teams

#### Meta/Facebook (2 scenarios)

**FB-001: TAO Cache Invalidation Storm**
- **Difficulty**: Senior (L6+)
- **Patterns**: C-015 (Cache Invalidation), D-006 (Stale Reads)
- **Scenario**: News feed cache invalidation causes database overload
- **Challenge**: Social graph query cascade

**FB-002: BGP Route Withdrawal** ⚠️
- **Difficulty**: Incident Commander
- **Patterns**: N-001 (Network Partition), C-030 (Complete Outage)
- **Scenario**: BGP misconfiguration makes entire platform unreachable
- **Challenge**: Physical datacenter access required for recovery
- **Real Incident**: October 2021 global outage

#### Microsoft (2 scenarios)

**MS-001: Azure SQL DTU Exhaustion**
- **Difficulty**: Mid-Level (L5)
- **Patterns**: Cap-001 (Resource Exhaustion), P-012 (Query Storm)
- **Scenario**: Inefficient query depletes database DTUs
- **Challenge**: Identify and kill runaway queries

**MS-002: Teams Call Quality Degradation**
- **Difficulty**: Senior (L6+)
- **Patterns**: N-002 (Packet Loss), P-015 (Media Processing)
- **Scenario**: WebRTC call quality degrades during work-from-home surge
- **Challenge**: Distributed debugging across CDN and media servers

#### LinkedIn (1 scenario)

**LI-001: Kafka Consumer Rebalance Storm**
- **Difficulty**: Mid-Level (L5)
- **Patterns**: Cap-003 (Kafka Lag), C-005 (Rebalance Storm)
- **Scenario**: Consumer group rebalancing causes notification delays
- **Real Incident**: Black Friday 2019
- **Links**: [Kafka Consumer Lag Debugging](/home/deepak/DS/site/docs/debugging/kafka-consumer-lag-debugging-production.md)

#### Twitter/X (1 scenario)

**TW-001: Timeline Generation Overload**
- **Difficulty**: Senior (L6+)
- **Patterns**: P-020 (Fanout Explosion), Cap-005 (CPU Exhaustion)
- **Scenario**: Viral tweet causes timeline fanout storm
- **Challenge**: Rate limit fanout vs user experience

---

### Tier 2: The Innovators (17 scenarios)

#### Stripe (2 scenarios)

**ST-001: Payment Idempotency Key Collision**
- **Difficulty**: Senior (L6+)
- **Patterns**: D-008 (Race Condition), D-012 (Duplicate Processing)
- **Scenario**: High-frequency duplicate payments during flash sale
- **Challenge**: Financial accuracy vs availability

**ST-002: Webhook Delivery Failure Cascade**
- **Difficulty**: Mid-Level (L5)
- **Patterns**: C-001 (Retry Storm), Cap-009 (Queue Backup)
- **Scenario**: Slow webhook endpoints cause delivery queue backup
- **Challenge**: Balance delivery guarantees vs system health

#### Spotify (2 scenarios)

**SP-001: Music Recommendation Service Timeout**
- **Difficulty**: Mid-Level (L5)
- **Patterns**: P-025 (ML Model Latency), C-002 (Circuit Breaker)
- **Scenario**: ML model inference timeout cascades to user experience
- **Challenge**: Graceful degradation strategies

**SP-002: Kafka Topic Replication Lag**
- **Difficulty**: Mid-Level (L5)
- **Patterns**: Cap-003 (Kafka Lag), D-005 (Eventual Consistency)
- **Scenario**: Play count updates lag during viral song release
- **Challenge**: Consistency vs real-time requirements

#### Airbnb (2 scenarios)

**AB-001: Search Service Elasticsearch Overload**
- **Difficulty**: Senior (L6+)
- **Patterns**: P-012 (Slow Query), Cap-014 (Search Saturation)
- **Scenario**: Complex search queries exhaust Elasticsearch cluster
- **Challenge**: Query optimization under load

**AB-002: Booking Concurrency Race Condition**
- **Difficulty**: Senior (L6+)
- **Patterns**: D-008 (Race Condition), D-013 (Double Booking)
- **Scenario**: Two guests book same property simultaneously
- **Challenge**: Transactional consistency vs performance

#### Discord (2 scenarios)

**DC-001: Voice Server Media Pipeline Failure**
- **Difficulty**: Senior (L6+)
- **Patterns**: N-002 (Packet Loss), P-015 (Media Processing)
- **Scenario**: Voice quality degradation in large servers
- **Real Incident**: March 2024 voice outage
- **Links**: [Discord March 2024 Incident](/home/deepak/DS/site/docs/incidents/discord-march-2024.md)

**DC-002: Message Delivery Delay Cascade**
- **Difficulty**: Mid-Level (L5)
- **Patterns**: Cap-003 (Queue Backup), C-003 (Cascade)
- **Scenario**: Large guild message storm delays delivery
- **Real Incident**: 2022 API degradation
- **Links**: [Discord 2022 Incident](/home/deepak/DS/site/docs/incidents/discord-2022-api.md)

#### Cloudflare (2 scenarios)

**CF-001: WAF Regex Catastrophic Backtracking** ⭐
- **Difficulty**: Senior (L6+)
- **Patterns**: P-023 (Regex Backtracking), Cap-001 (CPU Exhaustion)
- **Scenario**: Regex pattern causes CPU exhaustion across global PoPs
- **Real Incident**: July 2019 global outage
- **Duration**: 30 minutes
- **Links**: [Cloudflare 2019 Incident](/home/deepak/DS/site/docs/incidents/cloudflare-2019.md)
- **Key Lesson**: Input validation critical for regex patterns

**CF-002: Cache Purge API Rate Limit Storm**
- **Difficulty**: Mid-Level (L5)
- **Patterns**: Cap-012 (Rate Limiting), C-001 (API Storm)
- **Scenario**: Automated cache purges overwhelm API
- **Challenge**: Coordinate customer communications

#### GitHub (2 scenarios)

**GH-001: Git LFS Storage Backend Failure**
- **Difficulty**: Senior (L6+)
- **Patterns**: D-002 (Data Corruption), Cap-007 (Storage Exhaustion)
- **Scenario**: Large binary files corrupt during storage migration
- **Challenge**: Data integrity validation

**GH-002: GitHub Actions Queue Backup**
- **Difficulty**: Mid-Level (L5)
- **Patterns**: Cap-009 (Queue Backup), Cap-010 (Worker Exhaustion)
- **Scenario**: CI/CD runners saturated during OSS release day
- **Challenge**: Fair queuing vs priority handling

#### Shopify (1 scenario)

**SH-001: Flash Sale Database Write Amplification**
- **Difficulty**: Senior (L6+)
- **Patterns**: P-012 (Write Storm), Cap-002 (Database Saturation)
- **Scenario**: Black Friday flash sale overwhelms database writes
- **Challenge**: Inventory consistency during high concurrency

#### DoorDash (1 scenario)

**DD-001: Real-Time Order Routing Failure**
- **Difficulty**: Mid-Level (L5)
- **Patterns**: P-018 (Lock Contention), Cap-003 (Queue Backup)
- **Scenario**: Dasher assignment algorithm locks cause delays
- **Challenge**: Food quality degradation during delays

#### Slack (1 scenario)

**SL-001: Workspace Message Search Timeout**
- **Difficulty**: Mid-Level (L5)
- **Patterns**: P-012 (Slow Query), Cap-014 (Search Overload)
- **Scenario**: Large workspace search queries timeout
- **Real Incident**: 2022 search degradation
- **Links**: [Slack 2022 Incident](/home/deepak/DS/site/docs/incidents/slack-2022.md)

#### Pinterest (1 scenario)

**PI-001: Image CDN Cache Miss Storm**
- **Difficulty**: Mid-Level (L5)
- **Patterns**: C-015 (Cache Miss), Cap-005 (Bandwidth)
- **Scenario**: Viral pin causes CDN cache eviction cascade
- **Challenge**: Origin server protection

#### Twitch (1 scenario)

**TW-001: Live Stream Transcoding Backlog**
- **Difficulty**: Senior (L6+)
- **Patterns**: Cap-010 (Worker Saturation), P-015 (Media Processing)
- **Scenario**: Transcoding capacity exhausted during major event
- **Challenge**: Stream quality vs capacity constraints

---

### Tier 3: The Specialists (17 scenarios)

#### Coinbase (2 scenarios)

**CB-001: Trading Engine Order Matching Timeout**
- **Difficulty**: Senior (L6+)
- **Patterns**: P-018 (Lock Contention), D-010 (Financial Accuracy)
- **Scenario**: High volatility causes order matching delays
- **Challenge**: Financial integrity vs low latency

**CB-002: Crypto Price Feed Lag**
- **Difficulty**: Mid-Level (L5)
- **Patterns**: Cap-003 (Stream Lag), D-005 (Stale Data)
- **Scenario**: Price feed delay during rapid market movement
- **Challenge**: Stale prices cause arbitrage opportunities

#### Reddit (2 scenarios)

**RD-001: Comment Tree Recursive Query Explosion**
- **Difficulty**: Senior (L6+)
- **Patterns**: P-012 (Recursive Query), Cap-002 (Database CPU)
- **Scenario**: Deep comment thread causes query timeout
- **Challenge**: Display strategy vs database load

**RD-002: Voting System Write Amplification**
- **Difficulty**: Mid-Level (L5)
- **Patterns**: P-020 (Write Storm), Cap-002 (Hot Partition)
- **Scenario**: Frontpage post vote storm overwhelms database
- **Challenge**: Vote accuracy vs scalability

#### Datadog (2 scenarios)

**DD-001: Metrics Ingestion Pipeline Backup**
- **Difficulty**: Senior (L6+)
- **Patterns**: Cap-009 (Queue Backup), Cap-003 (Kafka Lag)
- **Scenario**: Metrics ingestion falls behind during incident spike
- **Challenge**: The monitoring system is down during outages

**DD-002: Time Series Query Timeout**
- **Difficulty**: Mid-Level (L5)
- **Patterns**: P-012 (Slow Query), Cap-014 (Query Complexity)
- **Scenario**: Complex dashboard queries timeout
- **Challenge**: Query optimization vs flexibility

#### Robinhood (2 scenarios)

**RH-001: Market Data Feed Processing Lag**
- **Difficulty**: Senior (L6+)
- **Patterns**: Cap-003 (Stream Processing), D-010 (Financial Data)
- **Scenario**: Trading halts cause quote backlog
- **Challenge**: Regulatory requirements vs system capacity

**RH-002: Order Execution Database Deadlock**
- **Difficulty**: Senior (L6+)
- **Patterns**: P-018 (Deadlock), D-010 (Financial Integrity)
- **Scenario**: Concurrent order processing causes deadlocks
- **Challenge**: Transaction isolation vs throughput

#### Zoom (2 scenarios)

**ZM-001: WebRTC Connection Establishment Failure**
- **Difficulty**: Senior (L6+)
- **Patterns**: N-002 (Network), P-015 (Media Processing)
- **Scenario**: Call quality degradation during peak hours
- **Challenge**: Multi-region media routing

**ZM-002: Meeting Participant Limit Exceeded**
- **Difficulty**: Mid-Level (L5)
- **Patterns**: Cap-010 (Capacity Limit), P-025 (Resource Allocation)
- **Scenario**: Large webinar exceeds connection limits
- **Challenge**: Hard limits vs customer expectations

#### TikTok (2 scenarios)

**TK-001: Video Recommendation Algorithm Timeout**
- **Difficulty**: Senior (L6+)
- **Patterns**: P-025 (ML Inference), C-002 (Timeout Cascade)
- **Scenario**: Recommendation model latency spike
- **Challenge**: Personalization vs fallback strategy

**TK-002: Video Upload Processing Backlog**
- **Difficulty**: Mid-Level (L5)
- **Patterns**: Cap-009 (Queue Backup), P-015 (Encoding)
- **Scenario**: Viral challenge causes upload spike
- **Challenge**: Processing SLA vs capacity

#### Square (1 scenario)

**SQ-001: Point of Sale Transaction Timeout**
- **Difficulty**: Mid-Level (L5)
- **Patterns**: N-002 (Network Latency), C-002 (Timeout)
- **Scenario**: Network degradation affects in-person payments
- **Challenge**: Offline mode vs authorization requirements

#### Snap (1 scenario)

**SN-001: Ephemeral Content Deletion Failure**
- **Difficulty**: Mid-Level (L5)
- **Patterns**: D-011 (Deletion Failure), Cap-009 (Queue Backup)
- **Scenario**: Snaps not deleting after expiration
- **Challenge**: Privacy guarantees vs system reliability

#### Dropbox (1 scenario)

**DB-001: File Sync Conflict Resolution Storm**
- **Difficulty**: Senior (L6+)
- **Patterns**: D-007 (Conflict Resolution), P-020 (Sync Storm)
- **Scenario**: Concurrent edits cause conflict cascade
- **Challenge**: Last-write-wins vs user intent preservation

#### Instacart (1 scenario)

**IC-001: Real-Time Inventory Sync Lag**
- **Difficulty**: Mid-Level (L5)
- **Patterns**: D-005 (Eventual Consistency), Cap-003 (Sync Lag)
- **Scenario**: Out-of-stock items showing as available
- **Challenge**: Shopper efficiency vs inventory accuracy

#### OpenAI (1 scenario)

**OA-001: ChatGPT Token Generation Timeout**
- **Difficulty**: Senior (L6+)
- **Patterns**: P-025 (ML Inference), Cap-010 (GPU Saturation)
- **Scenario**: Response generation timeout during high demand
- **Challenge**: Quality vs latency tradeoffs

---

## Training Progressions

### Beginner Path (Weeks 1-4)

```yaml
Week 1: Single-Service Failures
  - MS-001: Azure SQL DTU Exhaustion
  - SP-002: Kafka Replication Lag
  - PI-001: CDN Cache Miss

Week 2: Basic Cascades
  - SQ-001: POS Transaction Timeout
  - IC-001: Inventory Sync Lag
  - SN-001: Content Deletion Failure

Week 3: Performance Issues
  - SL-001: Search Timeout
  - DD-002: Time Series Query
  - ZM-002: Meeting Capacity

Week 4: Assessment
  - Random selection from Week 1-3
  - Timed evaluation
  - Peer review
```

### Intermediate Path (Weeks 5-8)

```yaml
Week 5: Multi-Service Cascades
  - UB-003: Payment Timeout Cascade
  - ST-002: Webhook Delivery Failure
  - DD-001: Order Routing Failure

Week 6: Data Consistency
  - AZ-001: S3 Eventual Consistency
  - SP-001: ML Service Timeout
  - CB-002: Price Feed Lag

Week 7: Complex Performance
  - AB-001: Elasticsearch Overload
  - RD-001: Comment Tree Explosion
  - TW-001: Timeline Fanout

Week 8: Assessment + Project
  - Design prevention for common patterns
  - Create runbooks for team
```

### Advanced Path (Weeks 9-12)

```yaml
Week 9: Critical Systems
  - NF-001: EVCache Cascade
  - UB-001: Surge Pricing Failure
  - ST-001: Idempotency Collision

Week 10: Novel Failure Modes
  - CF-001: Regex Backtracking
  - FB-001: TAO Cache Storm
  - GO-001: Spanner Replication

Week 11: Business-Critical
  - AB-002: Booking Race Condition
  - RH-001: Market Data Lag
  - CB-001: Trading Engine Timeout

Week 12: Incident Commander Training
  - FB-002: BGP Route Withdrawal
  - Multi-incident coordination
  - Executive stakeholder management
```

---

## Scenario Selection Guide

### By Your Current Level

```yaml
If you're L3-L4 (Junior):
  Start with: MS-001, SP-002, PI-001
  Focus on: Basic debugging, monitoring, rollback
  Success: 60%+ score, <60min MTTR

If you're L5 (Mid-Level):
  Start with: UB-003, ST-002, AB-001
  Focus on: Root cause analysis, mitigation strategy
  Success: 75%+ score, <45min MTTR

If you're L6+ (Senior):
  Start with: NF-001, UB-001, CF-001
  Focus on: Complex systems, prevention design
  Success: 85%+ score, <30min MTTR

If you're IC Track:
  Start with: FB-002, Multi-incident exercises
  Focus on: Leadership, coordination, communication
  Success: Team effectiveness, stakeholder management
```

### By Failure Pattern Interest

```yaml
If you want to learn about Cascading Failures:
  - NF-001: Protocol cascade
  - UB-003: Payment cascade
  - ST-002: Webhook cascade
  - CF-002: API rate limit storm

If you want to learn about Data Issues:
  - AZ-001: Eventual consistency
  - AB-002: Race conditions
  - ST-001: Idempotency
  - DB-001: Sync conflicts

If you want to learn about Performance:
  - CF-001: Regex backtracking
  - AB-001: Query optimization
  - RD-001: Recursive queries
  - TK-001: ML inference

If you want to learn about Capacity:
  - SH-001: Write amplification
  - DD-001: Metrics ingestion
  - TW-001: Transcoding backlog
  - GH-002: CI/CD queue
```

### By Company You're Interviewing

```yaml
Interviewing at Netflix?
  Study: NF-001, NF-002, NF-003
  Focus: Microservices, caching, chaos engineering

Interviewing at Uber?
  Study: UB-001, UB-002, UB-003
  Focus: Real-time systems, geo-distributed, high availability

Interviewing at Stripe?
  Study: ST-001, ST-002
  Focus: Financial accuracy, idempotency, webhooks

Interviewing at Cloudflare?
  Study: CF-001, CF-002
  Focus: Global PoP networks, edge computing, security
```

---

## Next Steps

1. **Assess Your Level**: Take self-assessment quiz
2. **Choose Your Path**: Beginner, Intermediate, or Advanced
3. **Start First Scenario**: Pick appropriate difficulty
4. **Track Progress**: Use evaluation scorecards
5. **Review Patterns**: Reference failure pattern library
6. **Join Community**: Share experiences, get feedback

---

*"50 scenarios × Deliberate practice = Production incident mastery"*

**Start with scenarios that challenge you, but don't overwhelm. Progress systematically through the levels.**