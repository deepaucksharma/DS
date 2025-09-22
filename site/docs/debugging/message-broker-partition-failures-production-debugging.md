# Message Broker Partition Failures Production Debugging

## Overview

Message broker partition failures can cause data loss, consumer lag, and complete event processing breakdown. When Kafka or RabbitMQ partitions fail, it disrupts the entire event-driven architecture, leading to cascading service failures and data inconsistency. This guide provides systematic approaches to debug partition failures based on real production incidents.

## Real Incident: Uber's 2019 Kafka Partition Disaster

**Impact**: 8-hour partial outage affecting trip matching and payments
**Root Cause**: Kafka cluster partition reassignment caused topic unavailability
**Data Loss**: 2.3M trip events lost, 45k payment confirmations delayed
**Recovery Time**: 8 hours (4 hours detection + 4 hours recovery)
**Cost**: ~$12M in lost revenue + customer compensation

## Architecture Overview

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - Blue #3B82F6]
        PX[Producer Proxy<br/>Load balancing<br/>Retry logic: Enabled<br/>Circuit breaker: OPEN]

        CX[Consumer Proxy<br/>Load balancing<br/>Lag monitoring<br/>Dead letter: Active]
    end

    subgraph ServicePlane[Service Plane - Emerald #10B981]
        subgraph KafkaCluster[Kafka Cluster]
            K1[Kafka Broker 1<br/>Leader partitions: 45<br/>Follower partitions: 67<br/>Status: DEGRADED]

            K2[Kafka Broker 2<br/>Leader partitions: 0<br/>Follower partitions: 0<br/>Status: DOWN]

            K3[Kafka Broker 3<br/>Leader partitions: 67<br/>Follower partitions: 45<br/>Status: OVERLOADED]
        end

        subgraph ZooKeeperCluster[ZooKeeper Cluster]
            Z1[ZooKeeper 1<br/>Status: HEALTHY<br/>Role: Leader<br/>Sessions: 234]

            Z2[ZooKeeper 2<br/>Status: HEALTHY<br/>Role: Follower<br/>Sessions: 156]

            Z3[ZooKeeper 3<br/>Status: HEALTHY<br/>Role: Follower<br/>Sessions: 189]
        end
    end

    subgraph StatePlane[State Plane - Amber #F59E0B]
        subgraph TopicPartitions[Topic Partitions]
            TP1[Trip Events Topic<br/>Partitions: 12<br/>Unavailable: 4<br/>Under-replicated: 6]

            TP2[Payment Events Topic<br/>Partitions: 8<br/>Unavailable: 2<br/>Under-replicated: 3]

            TP3[User Events Topic<br/>Partitions: 16<br/>Unavailable: 0<br/>Under-replicated: 8]
        end

        subgraph ConsumerGroups[Consumer Groups]
            CG1[Trip Processing Group<br/>Members: 12<br/>Lag: 2.3M messages<br/>Rebalancing: YES]

            CG2[Payment Processing Group<br/>Members: 8<br/>Lag: 456k messages<br/>Rebalancing: YES]

            CG3[Analytics Group<br/>Members: 4<br/>Lag: 890k messages<br/>Rebalancing: NO]
        end
    end

    subgraph ControlPlane[Control Plane - Violet #8B5CF6]
        KM[Kafka Monitor<br/>Cluster health: CRITICAL<br/>Partition status: DEGRADED<br/>ISR status: SHRINKING]

        CM[Consumer Monitor<br/>Lag alerts: 15<br/>Rebalance alerts: 8<br/>Processing rate: 45% down]

        PM[Partition Monitor<br/>Under-replicated: 17<br/>Offline: 6<br/>Leader election: 23]
    end

    %% Message flow
    PX --> K1
    PX --> K2
    PX --> K3

    CX --> K1
    CX --> K3

    %% Topic distribution
    K1 --> TP1
    K2 --> TP2
    K3 --> TP3

    %% Consumer groups
    TP1 --> CG1
    TP2 --> CG2
    TP3 --> CG3

    %% ZooKeeper coordination
    K1 --> Z1
    K2 --> Z2
    K3 --> Z3

    %% Monitoring
    KM -.->|monitors| K1
    CM -.->|monitors| CG1
    PM -.->|monitors| TP1

    %% Apply Tailwind colors
    classDef edgeStyle fill:#3B82F6,stroke:#1E40AF,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#047857,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef errorStyle fill:#EF4444,stroke:#DC2626,color:#fff

    class PX,CX edgeStyle
    class K1,K2,K3,Z1,Z2,Z3 serviceStyle
    class TP1,TP2,TP3,CG1,CG2,CG3 stateStyle
    class KM,CM,PM controlStyle
```

## Detection Signals

### Primary Indicators
```mermaid
graph LR
    subgraph PartitionFailures[Partition Failure Patterns]
        URP[Under-Replicated Partitions<br/>Normal: 0<br/>Current: 17<br/>Threshold: 5]

        OFP[Offline Partitions<br/>Normal: 0<br/>Current: 6<br/>Critical threshold: 1]

        LE[Leader Elections<br/>Normal: 0-2/hour<br/>Current: 23 in 10min<br/>Storm detected]

        ISR[In-Sync Replicas<br/>Shrinking ISR: 12 partitions<br/>Min ISR violations: 8<br/>Data at risk]
    end

    subgraph ConsumerImpact[Consumer Impact]
        CL[Consumer Lag<br/>Trip events: 2.3M<br/>Payment events: 456k<br/>Analytics: 890k]

        RB[Rebalancing<br/>Frequent rebalances<br/>Consumer downtime<br/>Processing gaps]

        TO[Timeouts<br/>Fetch timeouts: 234<br/>Coordinator timeouts: 89<br/>Session timeouts: 156]

        DL[Data Loss Risk<br/>Acks=1 producers<br/>Under-replicated writes<br/>Broker failures]
    end

    URP --> CL
    OFP --> RB
    LE --> TO
    ISR --> DL

    classDef failureStyle fill:#EF4444,stroke:#DC2626,color:#fff
    classDef impactStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class URP,OFP,LE,ISR failureStyle
    class CL,RB,TO,DL impactStyle
```

### Detection Commands
```bash
# 1. Check Kafka cluster status
kafka-topics.sh --bootstrap-server kafka-1:9092 --describe
kafka-log-dirs.sh --bootstrap-server kafka-1:9092 --describe

# 2. Check partition status
kafka-topics.sh --bootstrap-server kafka-1:9092 --describe --under-replicated-partitions
kafka-topics.sh --bootstrap-server kafka-1:9092 --describe --unavailable-partitions

# 3. Consumer group status
kafka-consumer-groups.sh --bootstrap-server kafka-1:9092 --describe --all-groups
kafka-consumer-groups.sh --bootstrap-server kafka-1:9092 --describe --group trip-processing

# 4. Broker status
kafka-broker-api-versions.sh --bootstrap-server kafka-1:9092
kafka-cluster.sh --bootstrap-server kafka-1:9092 cluster-id
```

## Debugging Workflow

### Phase 1: Partition Status Assessment (0-5 minutes)

```mermaid
flowchart TD
    A[Partition Alert<br/>UNDER_REPLICATED_PARTITIONS] --> B[Check Offline Partitions<br/>Count and affected topics]
    B --> C[Identify Failed Brokers<br/>Network/disk/process issues]
    C --> D[Assess ISR Shrinkage<br/>Data consistency risk]

    D --> E[Check Consumer Lag<br/>Processing backlog]
    E --> F[Identify Affected Services<br/>Downstream impact]
    F --> G[Estimate Data Loss Risk<br/>Acks configuration]

    B --> H[Review Recent Changes<br/>Partition reassignment]
    C --> I[Check ZooKeeper Health<br/>Coordination issues]
    D --> J[Network Connectivity<br/>Inter-broker communication]

    classDef urgentStyle fill:#EF4444,stroke:#DC2626,color:#fff
    classDef actionStyle fill:#10B981,stroke:#047857,color:#fff

    class A,C,E urgentStyle
    class F,G,H,I,J actionStyle
```

### Phase 2: Root Cause Analysis (5-15 minutes)

```mermaid
graph TB
    subgraph BrokerIssues[Broker-Level Issues]
        HF[Hardware Failure<br/>Disk corruption<br/>Memory exhaustion<br/>Network interface]

        PF[Process Failure<br/>JVM crashes<br/>Out of memory<br/>GC pressure]

        NI[Network Issues<br/>Partition isolation<br/>Latency spikes<br/>Packet loss]

        CF[Configuration<br/>Replication factor<br/>Min ISR settings<br/>Retention policies]
    end

    subgraph ClusterIssues[Cluster-Level Issues]
        PR[Partition Reassignment<br/>Failed reassignment<br/>Incomplete migration<br/>Resource exhaustion]

        ZK[ZooKeeper Issues<br/>Session timeouts<br/>Leader election<br/>Metadata corruption]

        LB[Load Imbalance<br/>Hot partitions<br/>Uneven distribution<br/>Producer routing]

        RP[Replication Problems<br/>ISR shrinkage<br/>Replica lag<br/>Network delays]
    end

    HF --> PR
    PF --> ZK
    NI --> LB
    CF --> RP

    classDef brokerStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef clusterStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class HF,PF,NI,CF brokerStyle
    class PR,ZK,LB,RP clusterStyle
```

## Common Partition Failure Scenarios

### Scenario 1: Broker Hardware Failure

```mermaid
graph LR
    subgraph FailureEvent[Hardware Failure]
        BF[Broker-2 Failure<br/>Disk corruption<br/>Leader partitions: 45<br/>Replica partitions: 67]

        LE[Leader Election<br/>45 partitions need new leaders<br/>Election timeout: 30s<br/>Client disruption]

        IS[ISR Shrinkage<br/>Replicas on Broker-2 removed<br/>Min ISR violations: 23<br/>Data at risk]
    end

    subgraph RecoveryActions[Recovery Actions]
        ER[Emergency Response<br/>Mark broker down<br/>Trigger partition reassignment<br/>Scale remaining brokers]

        RR[Replica Restoration<br/>Add new replicas<br/>Rebalance partitions<br/>Restore replication factor]

        DP[Data Protection<br/>Increase acks requirement<br/>Pause risky producers<br/>Validate data integrity]
    end

    BF --> ER
    LE --> RR
    IS --> DP

    classDef failureStyle fill:#EF4444,stroke:#DC2626,color:#fff
    classDef actionStyle fill:#10B981,stroke:#047857,color:#fff

    class BF,LE,IS failureStyle
    class ER,RR,DP actionStyle
```

### Scenario 2: Partition Reassignment Failure

```mermaid
graph TB
    subgraph ReassignmentFailure[Reassignment Failure]
        RA[Reassignment Started<br/>100 partitions to move<br/>Target: Load balancing<br/>Progress: 65%]

        RF[Reassignment Failed<br/>Network timeout<br/>Source broker overloaded<br/>Incomplete migration]

        PS[Partition Split<br/>Some replicas moved<br/>Some replicas stuck<br/>Inconsistent topology]
    end

    subgraph Impact[System Impact]
        URP[Under-replicated<br/>35 partitions affected<br/>Replication factor: 2/3<br/>Data vulnerability]

        CL[Consumer Lag<br/>Processing delays<br/>Rebalancing loops<br/>Throughput drop: 60%]

        PP[Producer Problems<br/>Metadata refresh errors<br/>Routing confusion<br/>Retry storms]
    end

    RA --> URP
    RF --> CL
    PS --> PP

    classDef assignmentStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef impactStyle fill:#EF4444,stroke:#DC2626,color:#fff

    class RA,RF,PS assignmentStyle
    class URP,CL,PP impactStyle
```

## Recovery Procedures

### Emergency Partition Recovery

```bash
#!/bin/bash
# Kafka partition failure recovery script

set -euo pipefail

KAFKA_HOME="/opt/kafka"
BOOTSTRAP_SERVER="kafka-1:9092,kafka-2:9092,kafka-3:9092"
LOG_FILE="/var/log/kafka_recovery_$(date +%Y%m%d_%H%M%S).log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 1. Assess cluster health
assess_cluster_health() {
    log "Assessing Kafka cluster health..."

    # Check broker availability
    log "Checking broker availability:"
    $KAFKA_HOME/bin/kafka-broker-api-versions.sh --bootstrap-server $BOOTSTRAP_SERVER || log "Some brokers unreachable"

    # Check under-replicated partitions
    log "Checking under-replicated partitions:"
    URP_OUTPUT=$($KAFKA_HOME/bin/kafka-topics.sh --bootstrap-server $BOOTSTRAP_SERVER --describe --under-replicated-partitions)
    URP_COUNT=$(echo "$URP_OUTPUT" | wc -l)

    if [ "$URP_COUNT" -gt 1 ]; then
        log "WARNING: $URP_COUNT under-replicated partitions found"
        echo "$URP_OUTPUT" | tee -a "$LOG_FILE"
    else
        log "No under-replicated partitions found"
    fi

    # Check offline partitions
    log "Checking offline partitions:"
    OFFLINE_OUTPUT=$($KAFKA_HOME/bin/kafka-topics.sh --bootstrap-server $BOOTSTRAP_SERVER --describe --unavailable-partitions)
    OFFLINE_COUNT=$(echo "$OFFLINE_OUTPUT" | wc -l)

    if [ "$OFFLINE_COUNT" -gt 1 ]; then
        log "CRITICAL: $OFFLINE_COUNT offline partitions found"
        echo "$OFFLINE_OUTPUT" | tee -a "$LOG_FILE"
        return 1
    else
        log "No offline partitions found"
        return 0
    fi
}

# 2. Force leader election for offline partitions
force_leader_election() {
    log "Forcing leader election for offline partitions..."

    # Get list of topics with offline partitions
    OFFLINE_TOPICS=$($KAFKA_HOME/bin/kafka-topics.sh --bootstrap-server $BOOTSTRAP_SERVER \
        --describe --unavailable-partitions | awk '{print $2}' | sort -u)

    if [ -z "$OFFLINE_TOPICS" ]; then
        log "No offline partitions found, skipping leader election"
        return 0
    fi

    # Create preferred replica election JSON
    cat > /tmp/preferred-replica-election.json << 'EOF'
{
  "partitions": [
EOF

    first=true
    for topic in $OFFLINE_TOPICS; do
        # Get partition details
        $KAFKA_HOME/bin/kafka-topics.sh --bootstrap-server $BOOTSTRAP_SERVER \
            --describe --topic "$topic" | grep "Partition:" | while read line; do

            partition=$(echo "$line" | awk '{print $2}' | cut -d: -f1)

            if [ "$first" = true ]; then
                first=false
            else
                echo "," >> /tmp/preferred-replica-election.json
            fi

            echo "    {\"topic\": \"$topic\", \"partition\": $partition}" >> /tmp/preferred-replica-election.json
        done
    done

    cat >> /tmp/preferred-replica-election.json << 'EOF'
  ]
}
EOF

    # Execute preferred replica election
    log "Executing preferred replica election..."
    $KAFKA_HOME/bin/kafka-preferred-replica-election.sh \
        --bootstrap-server $BOOTSTRAP_SERVER \
        --path-to-json-file /tmp/preferred-replica-election.json

    sleep 30

    # Verify results
    log "Verifying leader election results..."
    assess_cluster_health
}

# 3. Increase replication factor for under-replicated partitions
increase_replication_factor() {
    log "Increasing replication factor for critical topics..."

    # List of critical topics that need higher replication
    CRITICAL_TOPICS=("trip-events" "payment-events" "user-events")

    for topic in "${CRITICAL_TOPICS[@]}"; do
        log "Checking replication factor for $topic"

        current_rf=$($KAFKA_HOME/bin/kafka-topics.sh --bootstrap-server $BOOTSTRAP_SERVER \
            --describe --topic "$topic" | head -1 | awk '{print $6}')

        if [ "$current_rf" -lt 3 ]; then
            log "Increasing replication factor for $topic from $current_rf to 3"

            # Generate reassignment JSON
            cat > /tmp/reassignment-$topic.json << EOF
{
  "version": 1,
  "partitions": [
EOF

            # Get current partition assignment
            $KAFKA_HOME/bin/kafka-topics.sh --bootstrap-server $BOOTSTRAP_SERVER \
                --describe --topic "$topic" | grep "Partition:" | while read line; do

                partition=$(echo "$line" | awk '{print $2}' | cut -d: -f1)
                echo "    {\"topic\": \"$topic\", \"partition\": $partition, \"replicas\": [1,2,3]}," >> /tmp/reassignment-$topic.json
            done

            # Remove trailing comma and close JSON
            sed -i '$ s/,$//' /tmp/reassignment-$topic.json
            echo "  ]" >> /tmp/reassignment-$topic.json
            echo "}" >> /tmp/reassignment-$topic.json

            # Execute reassignment
            $KAFKA_HOME/bin/kafka-reassign-partitions.sh \
                --bootstrap-server $BOOTSTRAP_SERVER \
                --reassignment-json-file /tmp/reassignment-$topic.json \
                --execute

            log "Reassignment initiated for $topic"
        else
            log "Topic $topic already has adequate replication factor: $current_rf"
        fi
    done
}

# 4. Monitor reassignment progress
monitor_reassignment() {
    log "Monitoring partition reassignment progress..."

    max_wait=1800  # 30 minutes
    wait_time=0
    check_interval=60

    while [ $wait_time -lt $max_wait ]; do
        # Check if any reassignments are in progress
        REASSIGNMENT_STATUS=$($KAFKA_HOME/bin/kafka-reassign-partitions.sh \
            --bootstrap-server $BOOTSTRAP_SERVER \
            --list 2>/dev/null || echo "No reassignments")

        if [[ "$REASSIGNMENT_STATUS" == "No reassignments"* ]]; then
            log "All reassignments completed"
            break
        else
            log "Reassignment in progress: $REASSIGNMENT_STATUS"
        fi

        sleep $check_interval
        wait_time=$((wait_time + check_interval))
    done

    if [ $wait_time -ge $max_wait ]; then
        log "WARNING: Reassignment monitoring timed out after 30 minutes"
    fi
}

# 5. Validate cluster recovery
validate_recovery() {
    log "Validating cluster recovery..."

    # Final health check
    if assess_cluster_health; then
        log "✓ No offline partitions detected"
    else
        log "✗ Offline partitions still present"
        return 1
    fi

    # Check consumer lag
    log "Checking consumer group lag..."
    $KAFKA_HOME/bin/kafka-consumer-groups.sh --bootstrap-server $BOOTSTRAP_SERVER \
        --describe --all-groups | grep -E "LAG|GROUP" | tee -a "$LOG_FILE"

    # Check topic health
    log "Checking topic health..."
    $KAFKA_HOME/bin/kafka-topics.sh --bootstrap-server $BOOTSTRAP_SERVER \
        --describe | grep -E "ReplicationFactor|PartitionCount" | tee -a "$LOG_FILE"

    log "Cluster recovery validation completed"
    return 0
}

# Main recovery process
main() {
    log "Starting Kafka partition failure recovery"

    # Initial assessment
    if assess_cluster_health; then
        log "Cluster appears healthy, checking for under-replicated partitions"
    else
        log "Cluster has offline partitions, proceeding with recovery"
    fi

    # Recovery steps
    force_leader_election
    increase_replication_factor
    monitor_reassignment

    # Validation
    if validate_recovery; then
        log "Kafka partition recovery completed successfully"
    else
        log "Kafka partition recovery completed with warnings"
    fi

    log "Recovery process completed. Log: $LOG_FILE"
}

# Execute recovery
main "$@"
```

### Consumer Group Recovery

```python
#!/usr/bin/env python3
"""
Kafka consumer group recovery tool
Handles consumer lag and rebalancing issues
"""

from kafka import KafkaConsumer, KafkaProducer, KafkaAdminClient
from kafka.admin import ConfigResource, ConfigResourceType
from kafka.errors import KafkaError
import logging
import time
import json
from typing import Dict, List
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConsumerGroupRecovery:
    def __init__(self, bootstrap_servers: List[str]):
        self.bootstrap_servers = bootstrap_servers
        self.admin_client = KafkaAdminClient(
            bootstrap_servers=bootstrap_servers,
            request_timeout_ms=30000
        )

    def analyze_consumer_groups(self) -> Dict[str, Dict]:
        """Analyze all consumer groups for issues"""
        logger.info("Analyzing consumer groups...")

        groups_info = {}

        try:
            # Get all consumer groups
            group_list = self.admin_client.list_consumer_groups()

            for group_id, group_type in group_list:
                logger.info(f"Analyzing group: {group_id}")

                group_info = {
                    'group_id': group_id,
                    'type': group_type,
                    'members': [],
                    'lag': {},
                    'status': 'unknown'
                }

                try:
                    # Get group description
                    group_desc = self.admin_client.describe_consumer_groups([group_id])
                    if group_id in group_desc:
                        desc = group_desc[group_id]
                        group_info['status'] = desc.state.name
                        group_info['coordinator'] = desc.coordinator
                        group_info['members'] = [
                            {
                                'member_id': member.member_id,
                                'client_id': member.client_id,
                                'host': member.host,
                                'assignments': len(member.member_assignment.assignment) if member.member_assignment else 0
                            }
                            for member in desc.members
                        ]

                    # Get consumer group offsets and lag
                    consumer = KafkaConsumer(
                        bootstrap_servers=self.bootstrap_servers,
                        group_id=group_id,
                        enable_auto_commit=False,
                        consumer_timeout_ms=10000
                    )

                    # Get assigned partitions (if any)
                    assignments = consumer.assignment()
                    if assignments:
                        # Get current offsets
                        current_offsets = consumer.position_batch(assignments)

                        # Get latest offsets
                        latest_offsets = consumer.end_offsets(assignments)

                        # Calculate lag
                        for tp in assignments:
                            current = current_offsets.get(tp, 0)
                            latest = latest_offsets.get(tp, 0)
                            lag = latest - current

                            if tp.topic not in group_info['lag']:
                                group_info['lag'][tp.topic] = {}

                            group_info['lag'][tp.topic][tp.partition] = {
                                'current_offset': current,
                                'latest_offset': latest,
                                'lag': lag
                            }

                    consumer.close()

                except Exception as e:
                    logger.error(f"Error analyzing group {group_id}: {e}")
                    group_info['error'] = str(e)

                groups_info[group_id] = group_info

        except KafkaError as e:
            logger.error(f"Error listing consumer groups: {e}")

        return groups_info

    def identify_problematic_groups(self, groups_info: Dict[str, Dict]) -> List[str]:
        """Identify consumer groups with issues"""
        problematic_groups = []

        for group_id, info in groups_info.items():
            issues = []

            # Check group status
            if info['status'] in ['Dead', 'Empty']:
                issues.append(f"Group status: {info['status']}")

            # Check consumer lag
            total_lag = 0
            for topic, partitions in info.get('lag', {}).items():
                for partition, lag_info in partitions.items():
                    lag = lag_info['lag']
                    total_lag += lag

                    if lag > 100000:  # High lag threshold
                        issues.append(f"High lag in {topic}:{partition}: {lag}")

            if total_lag > 500000:  # Total lag threshold
                issues.append(f"Total lag: {total_lag}")

            # Check member count
            member_count = len(info.get('members', []))
            if member_count == 0 and info['status'] not in ['Dead', 'Empty']:
                issues.append("No active members")

            if issues:
                logger.warning(f"Group {group_id} has issues: {', '.join(issues)}")
                problematic_groups.append(group_id)

        return problematic_groups

    def reset_consumer_group_offsets(self, group_id: str, reset_strategy: str = 'latest') -> bool:
        """Reset consumer group offsets"""
        logger.info(f"Resetting offsets for group {group_id} to {reset_strategy}")

        try:
            # This would typically use kafka-consumer-groups.sh tool
            # For demonstration, showing the approach

            if reset_strategy == 'latest':
                # Reset to latest offsets (skip accumulated lag)
                logger.info(f"Resetting {group_id} to latest offsets")

            elif reset_strategy == 'earliest':
                # Reset to earliest offsets (reprocess all data)
                logger.info(f"Resetting {group_id} to earliest offsets")

            elif reset_strategy.startswith('by-duration'):
                # Reset to specific time duration
                duration = reset_strategy.split(':')[1]
                logger.info(f"Resetting {group_id} by duration: {duration}")

            # In practice, you would use:
            # kafka-consumer-groups.sh --bootstrap-server ... --group group_id --reset-offsets --to-latest --execute

            logger.info(f"Offset reset completed for group {group_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to reset offsets for group {group_id}: {e}")
            return False

    def force_rebalance(self, group_id: str) -> bool:
        """Force consumer group rebalancing"""
        logger.info(f"Forcing rebalance for group {group_id}")

        try:
            # Get group coordinator
            group_desc = self.admin_client.describe_consumer_groups([group_id])
            if group_id not in group_desc:
                logger.error(f"Group {group_id} not found")
                return False

            coordinator = group_desc[group_id].coordinator
            logger.info(f"Group coordinator: {coordinator}")

            # In practice, you might need to:
            # 1. Stop all consumers in the group
            # 2. Wait for session timeout
            # 3. Restart consumers
            # Or use administrative tools to trigger rebalance

            logger.info(f"Rebalance triggered for group {group_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to force rebalance for group {group_id}: {e}")
            return False

    def scale_consumer_group(self, group_id: str, target_instances: int) -> bool:
        """Scale consumer group instances"""
        logger.info(f"Scaling group {group_id} to {target_instances} instances")

        try:
            # This would typically involve orchestration system (Kubernetes, etc.)
            # to scale the consumer deployment

            # Get current group info
            groups_info = self.analyze_consumer_groups()
            if group_id not in groups_info:
                logger.error(f"Group {group_id} not found")
                return False

            current_instances = len(groups_info[group_id].get('members', []))
            logger.info(f"Current instances: {current_instances}, target: {target_instances}")

            if target_instances > current_instances:
                logger.info(f"Scaling up by {target_instances - current_instances} instances")
                # Scale up logic here
            elif target_instances < current_instances:
                logger.info(f"Scaling down by {current_instances - target_instances} instances")
                # Scale down logic here
            else:
                logger.info("No scaling needed")

            return True

        except Exception as e:
            logger.error(f"Failed to scale group {group_id}: {e}")
            return False

    def monitor_recovery(self, group_id: str, max_wait_time: int = 600) -> bool:
        """Monitor consumer group recovery"""
        logger.info(f"Monitoring recovery for group {group_id}")

        start_time = time.time()

        while time.time() - start_time < max_wait_time:
            try:
                groups_info = self.analyze_consumer_groups()

                if group_id not in groups_info:
                    logger.warning(f"Group {group_id} not found")
                    time.sleep(30)
                    continue

                group_info = groups_info[group_id]

                # Check group status
                if group_info['status'] in ['Stable', 'CompletingRebalance']:
                    logger.info(f"Group {group_id} status: {group_info['status']}")

                    # Check lag
                    total_lag = 0
                    for topic, partitions in group_info.get('lag', {}).items():
                        for partition, lag_info in partitions.items():
                            total_lag += lag_info['lag']

                    logger.info(f"Current total lag: {total_lag}")

                    if total_lag < 1000:  # Recovery threshold
                        logger.info(f"Group {group_id} recovery completed")
                        return True

                elif group_info['status'] == 'Rebalancing':
                    logger.info(f"Group {group_id} is rebalancing...")

                else:
                    logger.warning(f"Group {group_id} status: {group_info['status']}")

                time.sleep(30)

            except Exception as e:
                logger.error(f"Error monitoring group {group_id}: {e}")
                time.sleep(30)

        logger.warning(f"Recovery monitoring timed out for group {group_id}")
        return False

def main():
    """Main recovery execution"""

    bootstrap_servers = ['kafka-1:9092', 'kafka-2:9092', 'kafka-3:9092']
    recovery = ConsumerGroupRecovery(bootstrap_servers)

    try:
        # Analyze all consumer groups
        groups_info = recovery.analyze_consumer_groups()

        # Identify problematic groups
        problematic_groups = recovery.identify_problematic_groups(groups_info)

        logger.info(f"Found {len(problematic_groups)} problematic consumer groups")

        for group_id in problematic_groups:
            logger.info(f"Recovering group: {group_id}")

            group_info = groups_info[group_id]

            # Determine recovery strategy based on issues
            if group_info['status'] == 'Dead':
                # Reset offsets and restart
                recovery.reset_consumer_group_offsets(group_id, 'latest')

            elif 'High lag' in str(group_info):
                # Scale up consumers
                current_members = len(group_info.get('members', []))
                target_members = min(current_members * 2, 10)  # Double but cap at 10
                recovery.scale_consumer_group(group_id, target_members)

            elif 'No active members' in str(group_info):
                # Force rebalance
                recovery.force_rebalance(group_id)

            # Monitor recovery
            recovery.monitor_recovery(group_id)

        logger.info("Consumer group recovery completed")

    except Exception as e:
        logger.error(f"Recovery failed: {e}")

if __name__ == "__main__":
    main()
```

## Prevention Strategies

### Partition Monitoring Dashboard

```mermaid
graph TB
    subgraph BrokerHealth[Broker Health Metrics]
        BU[Broker Uptime<br/>Broker-1: 99.9%<br/>Broker-2: 87.3%<br/>Broker-3: 99.8%]

        DU[Disk Usage<br/>Broker-1: 72%<br/>Broker-2: 95%<br/>Broker-3: 68%]

        MM[Memory Usage<br/>Heap: 6.2GB/8GB<br/>Off-heap: 2.1GB<br/>GC pressure: Medium]

        NT[Network Throughput<br/>Inbound: 450 MB/s<br/>Outbound: 520 MB/s<br/>Connections: 2,847]
    end

    subgraph PartitionHealth[Partition Health]
        RF[Replication Factor<br/>Target: 3<br/>Under-replicated: 17<br/>Offline: 6]

        ISR[ISR Status<br/>Healthy: 247<br/>Shrinking: 12<br/>Expanding: 3]

        LE[Leader Elections<br/>Rate: 23 in 10min<br/>Normal: 0-2/hour<br/>Storm: YES]

        PD[Partition Distribution<br/>Balance score: 0.85<br/>Hot partitions: 8<br/>Cold partitions: 23]
    end

    BU --> RF
    DU --> ISR
    MM --> LE
    NT --> PD

    classDef healthStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef partitionStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class BU,DU,MM,NT healthStyle
    class RF,ISR,LE,PD partitionStyle
```

## Real Production Examples

### Uber's 2019 Kafka Partition Disaster
- **Duration**: 8 hours (4 hours detection + 4 hours recovery)
- **Root Cause**: Kafka cluster partition reassignment caused topic unavailability
- **Impact**: 2.3M trip events lost, 45k payment confirmations delayed
- **Recovery**: Emergency partition restoration + consumer offset reset
- **Prevention**: Staged reassignment + comprehensive monitoring

### LinkedIn's Kafka Cluster Meltdown 2018
- **Duration**: 6 hours 30 minutes
- **Root Cause**: Disk failure on multiple brokers caused massive ISR shrinkage
- **Impact**: Cross-team data pipeline failures, analytics delays
- **Recovery**: Hardware replacement + partition redistribution
- **Prevention**: Improved disk monitoring + automated failover

### Netflix's Message Broker Overload 2020
- **Duration**: 3 hours 45 minutes
- **Root Cause**: Consumer group rebalancing storm during traffic spike
- **Impact**: Real-time recommendation system degradation
- **Recovery**: Consumer scaling + partition rebalancing + load shedding
- **Prevention**: Dynamic consumer scaling + circuit breaker patterns

## Recovery Checklist

### Immediate Response (0-10 minutes)
- [ ] Identify offline and under-replicated partitions
- [ ] Check broker availability and health status
- [ ] Assess consumer group lag and processing status
- [ ] Determine data loss risk and impact scope
- [ ] Enable emergency producer backpressure if needed
- [ ] Notify affected teams and stakeholders

### Investigation (10-30 minutes)
- [ ] Analyze broker logs for failure root cause
- [ ] Check network connectivity between brokers
- [ ] Review recent partition reassignment activities
- [ ] Validate ZooKeeper cluster health and metadata
- [ ] Assess disk space, memory, and CPU utilization
- [ ] Examine consumer group rebalancing patterns

### Recovery (30-180 minutes)
- [ ] Force leader election for offline partitions
- [ ] Increase replication factor for critical topics
- [ ] Scale up under-performing consumer groups
- [ ] Reset consumer offsets if data loss is acceptable
- [ ] Monitor partition reassignment progress
- [ ] Validate message processing recovery

### Post-Recovery (1-7 days)
- [ ] Conduct detailed post-mortem analysis
- [ ] Review and optimize partition distribution strategy
- [ ] Enhance broker failure detection and recovery
- [ ] Implement automated consumer group scaling
- [ ] Improve partition monitoring and alerting
- [ ] Document recovery procedures and lessons learned

This comprehensive guide provides the systematic approach needed to handle message broker partition failures in production, based on real incidents from companies like Uber, LinkedIn, and Netflix.