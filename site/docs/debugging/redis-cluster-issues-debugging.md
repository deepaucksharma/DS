# Redis Cluster Issues Debugging: Split-Brain and Failover Troubleshooting Guide

## Executive Summary

Redis cluster issues affect 20% of distributed cache deployments and can cause data inconsistency and application failures. This guide provides systematic debugging approaches for cluster split-brain scenarios, node failures, and slot migration issues.

## Common Redis Cluster Error Patterns

### Split-Brain Detection
```bash
# Check cluster status
redis-cli cluster nodes

# Look for multiple masters for same slots
redis-cli cluster info | grep cluster_slots_fail

# Check node connectivity
redis-cli cluster nodes | grep fail

# Validate slot assignment
redis-cli cluster slots
```

### Investigation Commands
```bash
# Monitor cluster state changes
redis-cli --cluster check 127.0.0.1:7000

# Check specific node status
redis-cli -p 7001 cluster nodes | grep myself

# Monitor key distribution
redis-cli --cluster info 127.0.0.1:7000

# Check replication lag
redis-cli -p 7001 info replication
```

## Split-Brain Scenarios

### Detection and Resolution
```bash
# Scenario: Network partition causes split-brain
# Symptoms: Multiple masters claiming same hash slots

# 1. Identify conflicting masters
redis-cli cluster nodes | grep master | awk '{print $1, $2, $8}'

# 2. Check which nodes have quorum
redis-cli cluster nodes | grep master | while read line; do
  node_id=$(echo $line | awk '{print $1}')
  echo "Node $node_id has quorum: $(redis-cli cluster count-failure-reports $node_id)"
done

# 3. Manual failover to resolve split-brain
redis-cli -p 7002 cluster failover takeover  # Force takeover on slave

# 4. Reset problematic nodes
redis-cli -p 7003 cluster reset hard
redis-cli -p 7003 cluster meet 127.0.0.1 7000
```

### Cluster Recovery Process
```bash
#!/bin/bash
# redis-cluster-recovery.sh

echo "🔍 Redis Cluster Recovery Process"

# Check overall cluster health
CLUSTER_STATE=$(redis-cli cluster info | grep cluster_state | cut -d: -f2)
echo "Cluster state: $CLUSTER_STATE"

if [ "$CLUSTER_STATE" != "ok" ]; then
    echo "❌ Cluster in failed state, investigating..."

    # Get failing nodes
    redis-cli cluster nodes | grep fail > failing_nodes.txt

    while read node; do
        NODE_ID=$(echo $node | awk '{print $1}')
        NODE_ADDR=$(echo $node | awk '{print $2}')
        echo "Attempting to recover node: $NODE_ADDR"

        # Try to reset and rejoin
        redis-cli -h ${NODE_ADDR%:*} -p ${NODE_ADDR#*:} cluster reset soft
        redis-cli -h ${NODE_ADDR%:*} -p ${NODE_ADDR#*:} cluster meet 127.0.0.1 7000
    done < failing_nodes.txt

    rm failing_nodes.txt
fi

echo "✅ Recovery process completed"
```

## Monitoring and Prevention

### Cluster Health Monitoring
```python
import redis
import time

def monitor_cluster_health():
    try:
        rc = redis.RedisCluster(host='localhost', port=7000, decode_responses=True)

        # Check cluster info
        cluster_info = rc.cluster_info()
        print(f"Cluster state: {cluster_info['cluster_state']}")
        print(f"Cluster slots assigned: {cluster_info['cluster_slots_assigned']}")

        # Check node health
        nodes = rc.cluster_nodes()
        healthy_masters = 0
        total_masters = 0

        for node_id, node_info in nodes.items():
            if 'master' in node_info['flags']:
                total_masters += 1
                if 'fail' not in node_info['flags']:
                    healthy_masters += 1

        print(f"Healthy masters: {healthy_masters}/{total_masters}")

        if healthy_masters < total_masters:
            print("⚠️  Some master nodes are failing!")

    except Exception as e:
        print(f"❌ Cluster monitoring failed: {e}")

# Run monitoring every 30 seconds
while True:
    monitor_cluster_health()
    time.sleep(30)
```

### Automatic Failover Configuration
```bash
# redis.conf optimizations for cluster stability
cluster-enabled yes
cluster-config-file nodes.conf
cluster-node-timeout 5000
cluster-announce-ip 192.168.1.10
cluster-announce-port 7000
cluster-announce-bus-port 17000

# Prevent split-brain with minimum masters
cluster-require-full-coverage no
cluster-migration-barrier 1
```

This debugging guide covers the most critical Redis cluster issues and their resolution strategies based on production experience.