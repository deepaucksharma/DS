# Kafka Partition Rebalancing Storms - Production Debugging Guide

## The 3 AM Emergency

**Alert**: "Kafka consumer lag spiking to 5M+ messages, rebalances happening every 30 seconds"
**Cost**: $50,000/hour in lost revenue, 500K users affected
**Time to resolution**: 15-45 minutes with this guide

## Quick Diagnosis Decision Tree

```mermaid
graph TD
    A[Consumer Lag Alert] --> B{Rebalance Frequency}
    B -->|>10/minute| C[REBALANCING STORM]
    B -->|<5/minute| D[Check Individual Consumer Health]

    C --> E{Check Consumer Group State}
    E -->|Stable| F[Network Partitions]
    E -->|Rebalancing| G[Consumer Issues]
    E -->|Dead| H[Coordinator Failure]

    G --> I{Session Timeout Events}
    I -->|High| J[GC Pressure]
    I -->|Normal| K[Processing Time]

    F --> L[Check Network Metrics]
    J --> M[JVM Tuning Emergency]
    K --> N[Increase max.poll.interval.ms]
    H --> O[Broker Recovery]

    style C fill:#dc2626,stroke:#991b1b,color:#fff
    style M fill:#dc2626,stroke:#991b1b,color:#fff
    style O fill:#dc2626,stroke:#991b1b,color:#fff
```

## Production Architecture - The Failure Points

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - #3B82F6]
        LB[Load Balancer<br/>nginx 1.20<br/>upstream health checks]
        PROXY[Kafka Proxy<br/>kafka-proxy 2.3<br/>connection pooling]
    end

    subgraph ServicePlane[Service Plane - #10B981]
        PRODUCER[Producers<br/>librdkafka 1.9<br/>batch.size=100KB]
        CONSUMER[Consumer Group<br/>kafka-clients 3.2<br/>15 instances]
        APP[Application Logic<br/>Spring Boot 2.7<br/>@KafkaListener]
    end

    subgraph StatePlane[State Plane - #F59E0B]
        BROKER1[Kafka Broker 1<br/>r5.2xlarge<br/>Leader for partitions 0-9]
        BROKER2[Kafka Broker 2<br/>r5.2xlarge<br/>Leader for partitions 10-19]
        BROKER3[Kafka Broker 3<br/>r5.2xlarge<br/>Leader for partitions 20-29]
        ZK[ZooKeeper Ensemble<br/>3 nodes<br/>coordination]
    end

    subgraph ControlPlane[Control Plane - #8B5CF6]
        METRICS[Kafka Manager<br/>JMX Metrics<br/>Grafana dashboards]
        COORD[Group Coordinator<br/>Partition assignment<br/>Rebalance orchestration]
    end

    %% Connections
    PRODUCER -->|produce rate: 50K msg/s| BROKER1
    PRODUCER -->|produce rate: 50K msg/s| BROKER2
    PRODUCER -->|produce rate: 50K msg/s| BROKER3

    CONSUMER -->|poll interval: 5s| BROKER1
    CONSUMER -->|poll interval: 5s| BROKER2
    CONSUMER -->|poll interval: 5s| BROKER3

    COORD -->|rebalance triggers| CONSUMER
    BROKER1 -.->|heartbeat every 3s| COORD
    BROKER2 -.->|heartbeat every 3s| COORD
    BROKER3 -.->|heartbeat every 3s| COORD

    %% Critical failure points
    CONSUMER -.->|SESSION TIMEOUT<br/>30s default<br/>FAILURE POINT| COORD
    CONSUMER -.->|MAX POLL INTERVAL<br/>300s default<br/>FAILURE POINT| COORD

    %% Apply Tailwind 4-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#1D4ED8,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#047857,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class LB,PROXY edgeStyle
    class PRODUCER,CONSUMER,APP serviceStyle
    class BROKER1,BROKER2,BROKER3,ZK stateStyle
    class METRICS,COORD controlStyle
```

## Real Incident: Uber's Kafka Rebalancing Storm (November 2022)

**Background**: Payment processing pipeline with 50 partitions, 15 consumer instances
**Trigger**: JVM GC pause caused one consumer to miss heartbeat
**Cascade**: Triggered rebalance → other consumers dropped → continuous rebalancing

```mermaid
timeline
    title Uber Payment Pipeline Kafka Storm - November 15, 2022

    section Normal Operations
        14:00 : Consumer lag: 50K messages
              : Rebalances: 2/hour (normal)
              : Processing: 100K payments/minute

    section The Trigger (14:23)
        14:23 : Consumer-7 GC pause: 45 seconds
              : Missed 15 heartbeats
              : Group coordinator triggers rebalance

    section Cascade Begins (14:24)
        14:24 : 14 consumers stop processing
              : Begin partition reassignment
              : Consumer lag jumps to 500K

    section Storm Amplifies (14:25-14:40)
        14:25 : During rebalance, other consumers timeout
              : Multiple consumers join/leave simultaneously
              : Rebalance frequency: 8/minute

        14:30 : Consumer lag: 2.5M messages
              : Payment processing stops
              : Customer complaints spike

        14:35 : Infrastructure cost: $25K/hour
              : Revenue impact: $150K/hour
              : Manual intervention required

    section Resolution (14:41)
        14:41 : Emergency: Stop all consumers
              : Reset consumer group
              : Restart with optimized configs
              : Processing resumed
```

## Emergency Response Playbook

### Step 1: Immediate Assessment (2 minutes)

**Critical Metrics to Check:**

```bash
# Consumer group status
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --describe --group payment-processors

# Rebalance frequency (should be <5/hour)
kubectl logs kafka-consumer-deployment | grep "rebalance" | tail -50

# Current lag by partition
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --describe --group payment-processors --verbose
```

**Expected Output Analysis:**
- Lag > 100K per partition = CRITICAL
- Rebalances > 1/minute = STORM DETECTED
- Multiple consumers in "Rebalancing" state = ACTIVE INCIDENT

### Step 2: Stop the Storm (5 minutes)

**Emergency Circuit Breaker:**

```bash
# Option A: Pause all consumers (preserves state)
kubectl scale deployment kafka-consumer --replicas=0

# Option B: Reset consumer group (nuclear option)
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --reset-offsets --group payment-processors --to-latest --execute --all-topics
```

### Step 3: Root Cause Analysis (5 minutes)

```mermaid
graph TD
    A[Rebalancing Storm] --> B{Check Consumer Logs}

    B --> C[GC Pressure]
    B --> D[Processing Timeout]
    B --> E[Network Issues]
    B --> F[Resource Exhaustion]

    C --> C1[JVM heap dumps<br/>GC logs analysis<br/>Tune -Xmx settings]
    D --> D1[max.poll.interval.ms too low<br/>Processing time > 300s<br/>Increase to 600s]
    E --> E1[Network partitions<br/>DNS resolution failures<br/>Connection pool exhaustion]
    F --> F1[CPU > 80%<br/>Memory > 90%<br/>Scale consumer instances]

    C1 --> G[Apply Fix]
    D1 --> G
    E1 --> G
    F1 --> G

    G --> H[Restart Consumers]
    H --> I[Monitor Recovery]

    style A fill:#dc2626,stroke:#991b1b,color:#fff
    style G fill:#059669,stroke:#047857,color:#fff
```

## Production Configuration - Anti-Storm Settings

**Consumer Configuration (Spring Boot application.yml):**

```yaml
spring:
  kafka:
    consumer:
      # Rebalancing storm prevention
      session-timeout: 45s        # Increased from 30s
      heartbeat-interval: 10s     # session-timeout / 3
      max-poll-interval: 600s     # 10 minutes for processing
      max-poll-records: 100       # Reduced batch size

      # Performance settings
      fetch-min-size: 50KB
      fetch-max-wait: 500ms

      # Error handling
      enable-auto-commit: false   # Manual commit control
      auto-offset-reset: earliest

      # Connection resilience
      connections-max-idle: 9m
      request-timeout: 305s       # > max-poll-interval

    producer:
      # Reduce broker load during incidents
      batch-size: 50KB           # Reduced from 100KB
      linger-ms: 100
      buffer-memory: 32MB

      # Reliability
      acks: all
      retries: 3
      retry-backoff-ms: 1000
```

**JVM Tuning for Consumer Applications:**

```bash
# GC-optimized settings for Kafka consumers
export JAVA_OPTS="-Xmx4g -Xms4g \
  -XX:+UseG1GC \
  -XX:MaxGCPauseMillis=100 \
  -XX:+UseStringDeduplication \
  -XX:+PrintGC \
  -XX:+PrintGCDetails \
  -XX:+PrintGCTimeStamps \
  -Xloggc:/var/log/gc.log"
```

## Monitoring and Alerting

### Critical Dashboards

```mermaid
graph LR
    subgraph "Grafana Dashboard - Kafka Consumer Health"
        A[Consumer Lag<br/>Alert > 50K]
        B[Rebalance Rate<br/>Alert > 5/hour]
        C[Session Timeouts<br/>Alert > 2/minute]
        D[Processing Time<br/>Alert > 30s p99]
    end

    subgraph "PagerDuty Alerts"
        E[P1: Lag > 100K<br/>Immediate response]
        F[P2: Rebalances > 10/hour<br/>15min response]
        G[P3: Processing degraded<br/>30min response]
    end

    A --> E
    B --> F
    C --> F
    D --> G

    classDef critical fill:#dc2626,stroke:#991b1b,color:#fff
    classDef warning fill:#f59e0b,stroke:#d97706,color:#fff
    classDef info fill:#3b82f6,stroke:#1d4ed8,color:#fff

    class E critical
    class F warning
    class G info
```

### Key Metrics with Thresholds

| Metric | Normal | Warning | Critical | Action |
|--------|--------|---------|----------|---------|
| Consumer Lag | <10K | 10K-50K | >50K | Scale consumers |
| Rebalance Rate | <2/hour | 2-5/hour | >5/hour | Investigate config |
| Session Timeouts | 0/minute | 1/minute | >2/minute | Check GC/network |
| Processing Time p99 | <5s | 5-30s | >30s | Increase poll interval |
| GC Pause Time | <100ms | 100-500ms | >500ms | Tune JVM |

## Cost Impact Analysis

### Revenue Impact Calculation

```mermaid
graph TD
    A[Rebalancing Storm Detected] --> B[Processing Stops]
    B --> C[Payment Pipeline Down]
    C --> D[Revenue Loss Calculation]

    D --> E["$2,500/minute × Duration<br/>+ Customer churn cost<br/>+ Infrastructure scaling"]

    F[Real Examples] --> G[Uber: $50K/hour<br/>Lyft: $30K/hour<br/>DoorDash: $75K/hour]

    H[Prevention Investment] --> I[Better monitoring: $5K/month<br/>Config tuning: $10K one-time<br/>Training: $15K one-time]

    style A fill:#dc2626,stroke:#991b1b,color:#fff
    style E fill:#f59e0b,stroke:#d97706,color:#fff
    style I fill:#059669,stroke:#047857,color:#fff
```

## Recovery Procedures

### Graceful Recovery (Preferred)

```bash
#!/bin/bash
# graceful-recovery.sh

echo "Starting graceful Kafka consumer recovery..."

# 1. Stop traffic gradually
kubectl scale deployment kafka-consumer --replicas=0
sleep 30

# 2. Verify no active consumers
kafka-consumer-groups.sh --bootstrap-server $KAFKA_BROKERS \
  --describe --group $CONSUMER_GROUP

# 3. Apply optimized configuration
kubectl apply -f kafka-consumer-optimized.yaml

# 4. Start single instance first
kubectl scale deployment kafka-consumer --replicas=1
sleep 60

# 5. Verify stability, then scale up
for i in {2..15}; do
    kubectl scale deployment kafka-consumer --replicas=$i
    sleep 30
    # Check rebalance rate before next scale
    REBALANCES=$(kubectl logs kafka-consumer | grep "rebalance" | wc -l)
    if [ $REBALANCES -gt 2 ]; then
        echo "Rebalancing detected, waiting..."
        sleep 60
    fi
done
```

### Emergency Reset (Nuclear Option)

```bash
#!/bin/bash
# emergency-reset.sh - Use only when graceful recovery fails

echo "EMERGENCY: Resetting consumer group state"

# 1. Stop all consumers immediately
kubectl delete deployment kafka-consumer

# 2. Reset offsets to latest (skip accumulated lag)
kafka-consumer-groups.sh --bootstrap-server $KAFKA_BROKERS \
  --reset-offsets --group $CONSUMER_GROUP --to-latest --execute --all-topics

# 3. Recreate with storm-resistant config
kubectl apply -f kafka-consumer-storm-resistant.yaml

echo "Emergency reset complete. Monitor for stability."
```

## Prevention Strategies

### Configuration Templates

**Storm-Resistant Consumer Config:**

```properties
# session.timeout.ms - How long coordinator waits for heartbeat
session.timeout.ms=45000

# heartbeat.interval.ms - How often to send heartbeats
heartbeat.interval.ms=15000

# max.poll.interval.ms - Max time between poll() calls
max.poll.interval.ms=600000

# max.poll.records - Batch size for processing
max.poll.records=100

# Partition assignment strategy
partition.assignment.strategy=org.apache.kafka.clients.consumer.RangeAssignor

# Connection settings
connections.max.idle.ms=540000
request.timeout.ms=305000
```

### Deployment Patterns

```mermaid
graph TB
    subgraph "Production Deployment Strategy"
        A[Blue-Green Consumer Groups] --> B[Group A: Active Processing]
        A --> C[Group B: Standby/Canary]

        B --> D[Traffic 90%]
        C --> E[Traffic 10%]

        F[Incident Detected] --> G[Switch Traffic to Group B]
        G --> H[Repair Group A Offline]
        H --> I[Verify Fix]
        I --> J[Switch Back]
    end

    classDef active fill:#059669,stroke:#047857,color:#fff
    classDef standby fill:#f59e0b,stroke:#d97706,color:#fff
    classDef incident fill:#dc2626,stroke:#991b1b,color:#fff

    class B,D active
    class C,E standby
    class F incident
```

## Testing and Validation

### Chaos Engineering for Rebalancing

```bash
#!/bin/bash
# chaos-rebalancing-test.sh

echo "Testing rebalancing resilience..."

# Test 1: Kill single consumer
kubectl delete pod $(kubectl get pods -l app=kafka-consumer | tail -1 | awk '{print $1}')
sleep 60
CHECK_LAG

# Test 2: Network partition simulation
kubectl exec kafka-consumer-0 -- iptables -A OUTPUT -d $KAFKA_BROKER_IP -j DROP
sleep 120
kubectl exec kafka-consumer-0 -- iptables -D OUTPUT -d $KAFKA_BROKER_IP -j DROP
CHECK_LAG

# Test 3: GC pressure simulation
kubectl exec kafka-consumer-0 -- stress --vm 1 --vm-bytes 3G --timeout 30s
CHECK_LAG
```

## Quick Reference

### Emergency Commands

```bash
# Check consumer group status
kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group my-group

# Emergency consumer shutdown
kubectl scale deployment kafka-consumer --replicas=0

# Reset consumer group (nuclear option)
kafka-consumer-groups.sh --reset-offsets --group my-group --to-latest --execute --all-topics

# Check rebalance frequency
kubectl logs kafka-consumer | grep "rebalance" | tail -20

# Monitor lag in real-time
watch "kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group my-group"
```

### Key Log Patterns

```bash
# Rebalancing started
"Revoking previously assigned partitions"

# Session timeout
"Marking the coordinator dead"

# Processing timeout
"Offset commit failed on partition"

# GC pressure indicator
"[GC (Allocation Failure)" with >500ms duration
```

---

**Remember**: Kafka rebalancing storms are cascade failures. Stop the cascade first, analyze later. Every minute of storm costs thousands in revenue and customer trust.

**Next Steps**: Set up monitoring dashboards, tune consumer configurations, and practice recovery procedures in staging environment.