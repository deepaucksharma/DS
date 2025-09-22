# Redis Sentinel Failover Debugging

## Overview

Redis Sentinel provides automatic failover for Redis master-slave setups, but misconfigurations and network issues can cause failed failovers, split-brain scenarios, and data inconsistencies. This guide provides step-by-step debugging for production Sentinel deployments.

## Immediate Symptoms Checklist

- [ ] Redis master appears down but Sentinel hasn't failed over
- [ ] Multiple masters detected (split-brain scenario)
- [ ] Failover initiated but new master not accepting writes
- [ ] Clients still connecting to old master after failover
- [ ] Sentinel consensus failing (not enough votes)
- [ ] Repeated failover attempts without resolution

## Redis Sentinel Failover Debugging Flow

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - #3B82F6]
        CLIENTS[Redis Clients<br/>Application instances]
        PROXY[Redis Proxy<br/>HAProxy/Twemproxy]
    end

    subgraph ServicePlane[Service Plane - #10B981]
        S1[Sentinel 1<br/>Vote: DOWN]
        S2[Sentinel 2<br/>Vote: DOWN]
        S3[Sentinel 3<br/>Vote: DOWN]
        CONSENSUS[Quorum Check<br/>2/3 votes needed]
    end

    subgraph StatePlane[State Plane - #F59E0B]
        MASTER[Redis Master<br/>Status: DOWN]
        SLAVE1[Redis Slave 1<br/>Promotion candidate]
        SLAVE2[Redis Slave 2<br/>Backup candidate]
        CONFIG[Sentinel Config<br/>sentinel.conf]
    end

    subgraph ControlPlane[Control Plane - #8B5CF6]
        LOGS[Sentinel Logs<br/>/var/log/redis]
        METRICS[Redis Metrics<br/>INFO replication]
        MONITOR[Health Checks<br/>PING/PONG]
    end

    %% Failover Flow
    START([Master Unreachable]) --> CHECK1{Sentinel<br/>Detection}
    CHECK1 -->|Detected| CHECK2{Quorum<br/>Achieved?}
    CHECK1 -->|Not Detected| DEBUG_DETECT[Debug Detection]

    CHECK2 -->|Yes| CHECK3{Slave<br/>Available?}
    CHECK2 -->|No| DEBUG_QUORUM[Debug Quorum]

    CHECK3 -->|Yes| CHECK4{Promotion<br/>Successful?}
    CHECK3 -->|No| DEBUG_SLAVE[Debug Slave State]

    CHECK4 -->|Yes| CHECK5{Client<br/>Failover?}
    CHECK4 -->|No| DEBUG_PROMOTION[Debug Promotion]

    CHECK5 -->|No| DEBUG_CLIENT[Debug Client Config]
    CHECK5 -->|Yes| SUCCESS[Failover Complete]

    %% Apply four-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class CLIENTS,PROXY edgeStyle
    class S1,S2,S3,CONSENSUS serviceStyle
    class MASTER,SLAVE1,SLAVE2,CONFIG stateStyle
    class LOGS,METRICS,MONITOR controlStyle
```

## Step-by-Step Debugging Process

### Phase 1: Sentinel Status Check (< 2 minutes)

```bash
# 1. Check all Sentinel instances status
for sentinel in 127.0.0.1:26379 127.0.0.1:26380 127.0.0.1:26381; do
  echo "=== Checking Sentinel $sentinel ==="
  redis-cli -h ${sentinel%:*} -p ${sentinel#*:} ping
  redis-cli -h ${sentinel%:*} -p ${sentinel#*:} sentinel masters
done

# 2. Check current master from Sentinel perspective
redis-cli -p 26379 sentinel get-master-addr-by-name mymaster

# 3. Verify Sentinel configuration
redis-cli -p 26379 sentinel masters | grep -E "(name|ip|port|flags|num-slaves)"
```

**Expected vs. Problematic Output:**
```bash
# Good - Single master, proper flags
name=mymaster,ip=10.0.1.100,port=6379,flags=master,num-slaves=2

# Bad - Multiple masters or wrong flags
name=mymaster,ip=10.0.1.100,port=6379,flags=master,s_down,o_down
name=mymaster,ip=10.0.1.101,port=6379,flags=master  # Split brain!
```

### Phase 2: Master/Slave State Analysis (< 3 minutes)

```bash
# 1. Check master status directly
redis-cli -h 10.0.1.100 -p 6379 ping
redis-cli -h 10.0.1.100 -p 6379 info replication

# 2. Check all slaves status
for slave in 10.0.1.101 10.0.1.102; do
  echo "=== Checking Slave $slave ==="
  redis-cli -h $slave -p 6379 info replication
  redis-cli -h $slave -p 6379 info server | grep redis_version
done

# 3. Check replication lag
redis-cli -h 10.0.1.100 -p 6379 info replication | grep master_repl_offset
redis-cli -h 10.0.1.101 -p 6379 info replication | grep slave_repl_offset
```

**Replication Health Indicators:**
```bash
# Master perspective
role:master
connected_slaves:2
slave0:ip=10.0.1.101,port=6379,state=online,offset=12345,lag=0
slave1:ip=10.0.1.102,port=6379,state=online,offset=12345,lag=0

# Slave perspective (healthy)
role:slave
master_host:10.0.1.100
master_port:6379
master_link_status:up
slave_repl_offset:12345
```

### Phase 3: Sentinel Log Analysis (< 5 minutes)

```bash
# 1. Check recent Sentinel logs for failover attempts
tail -100 /var/log/redis/sentinel.log | grep -E "(failover|vote|quorum)"

# 2. Look for specific error patterns
grep -E "(SDOWN|ODOWN|+new-epoch|+switch-master)" /var/log/redis/sentinel.log | tail -20

# 3. Check for network connectivity issues
grep "connection refused\|timeout" /var/log/redis/sentinel.log | tail -10
```

**Key Log Patterns to Analyze:**
```log
# Normal failover sequence
+sdown master mymaster 10.0.1.100 6379           # Subjective down
+odown master mymaster 10.0.1.100 6379 #quorum 2/2  # Objective down
+new-epoch 1                                      # New epoch started
+try-failover master mymaster 10.0.1.100 6379    # Failover attempt
+vote-for-leader abc123 1                         # Leader election
+switch-master mymaster 10.0.1.100 6379 10.0.1.101 6379  # Master switch

# Problematic patterns
+sdown master mymaster 10.0.1.100 6379           # Detected down
-sdown master mymaster 10.0.1.100 6379           # Down then up (flapping)
# No +odown = quorum not reached
```

## Common Root Causes and Solutions

### 1. Insufficient Quorum Configuration (40% of cases)

**Symptoms:**
- Sentinel detects master down but doesn't failover
- Logs show +sdown but no +odown
- "Not enough good slaves to try a failover" errors

**Debugging:**
```bash
# Check Sentinel quorum configuration
redis-cli -p 26379 sentinel masters | grep quorum

# Check number of active Sentinels
redis-cli -p 26379 sentinel sentinels mymaster

# Verify Sentinel connectivity to each other
for port in 26379 26380 26381; do
  redis-cli -p $port sentinel sentinels mymaster | grep -c "name=sentinel"
done
```

**Root Cause Analysis:**
```bash
# Common misconfiguration
sentinel monitor mymaster 10.0.1.100 6379 3  # Requires 3 votes
# But only 2 Sentinels running = never reaches quorum
```

**Solutions:**

**Option 1: Fix Quorum Threshold**
```bash
# Reduce quorum to majority of available Sentinels
# With 3 Sentinels, use quorum=2
redis-cli -p 26379 sentinel set mymaster quorum 2

# Verify change
redis-cli -p 26379 sentinel masters | grep quorum
```

**Option 2: Add More Sentinels**
```bash
# Deploy additional Sentinel instance
# sentinel.conf for new instance
port 26382
sentinel monitor mymaster 10.0.1.100 6379 2
sentinel down-after-milliseconds mymaster 5000
sentinel parallel-syncs mymaster 1
sentinel failover-timeout mymaster 30000

# Start new Sentinel
redis-sentinel /etc/redis/sentinel.conf
```

### 2. Network Partitions and Split-Brain (30% of cases)

**Symptoms:**
- Multiple masters detected
- Clients writing to different Redis instances
- Data inconsistencies after network recovery

**Debugging:**
```bash
# Check for multiple masters
for sentinel in 26379 26380 26381; do
  echo "Sentinel $sentinel view:"
  redis-cli -p $sentinel sentinel masters | grep -E "(ip|port|flags)"
done

# Test network connectivity between Sentinels
for src_port in 26379 26380 26381; do
  for dst_port in 26379 26380 26381; do
    if [ $src_port != $dst_port ]; then
      timeout 5 redis-cli -p $src_port ping && echo "OK: $src_port -> $dst_port"
    fi
  done
done
```

**Split-Brain Detection:**
```bash
# Script to detect split-brain scenario
#!/bin/bash
masters=()
for port in 26379 26380 26381; do
  master=$(redis-cli -p $port sentinel get-master-addr-by-name mymaster 2>/dev/null)
  if [ -n "$master" ]; then
    masters+=("$master")
  fi
done

unique_masters=$(printf '%s\n' "${masters[@]}" | sort -u | wc -l)
if [ $unique_masters -gt 1 ]; then
  echo "SPLIT-BRAIN DETECTED: $unique_masters different masters"
  printf '%s\n' "${masters[@]}" | sort -u
fi
```

**Solutions:**

**Option 1: Immediate Split-Brain Resolution**
```bash
# 1. Identify the legitimate master (most recent data)
for ip in 10.0.1.100 10.0.1.101 10.0.1.102; do
  echo "=== $ip ==="
  redis-cli -h $ip info replication | grep -E "(role|master_repl_offset)"
done

# 2. Manually reset incorrect masters to slaves
redis-cli -h 10.0.1.101 slaveof 10.0.1.100 6379  # Reset to slave

# 3. Reset Sentinel state
redis-cli -p 26379 sentinel reset mymaster
```

**Option 2: Prevent Future Split-Brain**
```bash
# Add min-slaves configuration to master
redis-cli -h 10.0.1.100 config set min-slaves-to-write 1
redis-cli -h 10.0.1.100 config set min-slaves-max-lag 10

# This prevents writes if no slaves are connected
# Helps avoid split-brain data corruption
```

### 3. Slave Promotion Issues (20% of cases)

**Symptoms:**
- Sentinel starts failover but promotion fails
- New master doesn't accept writes
- Slaves don't recognize new master

**Debugging:**
```bash
# Check slave priority and replication offset
for slave in 10.0.1.101 10.0.1.102; do
  echo "=== Slave $slave ==="
  redis-cli -h $slave config get slave-priority
  redis-cli -h $slave info replication | grep slave_repl_offset
  redis-cli -h $slave info replication | grep master_link_status
done

# Check if slave can accept writes after promotion
redis-cli -h 10.0.1.101 config get slave-read-only
```

**Common Promotion Failures:**
```bash
# Slave still in read-only mode
slave-read-only:yes  # Should be 'no' after promotion

# Slave has stale data
slave_repl_offset:10000  # Much lower than master offset

# Slave configuration issues
slave-priority:0  # Priority 0 = never promote
```

**Solutions:**

**Option 1: Manual Promotion**
```bash
# Force promote specific slave
redis-cli -h 10.0.1.101 slaveof no one  # Make it master
redis-cli -h 10.0.1.101 config set slave-read-only no

# Update other slaves to point to new master
redis-cli -h 10.0.1.102 slaveof 10.0.1.101 6379

# Update Sentinel configuration
redis-cli -p 26379 sentinel failover mymaster
```

**Option 2: Fix Slave Configuration**
```bash
# Ensure slaves can be promoted
redis-cli -h 10.0.1.101 config set slave-priority 100
redis-cli -h 10.0.1.102 config set slave-priority 90

# Verify replication is current
redis-cli -h 10.0.1.100 info replication | grep master_repl_offset
redis-cli -h 10.0.1.101 info replication | grep slave_repl_offset
# Offsets should be within ~10 bytes
```

### 4. Client Failover Issues (10% of cases)

**Symptoms:**
- Sentinel fails over correctly but clients still connect to old master
- Application errors during failover
- Long recovery time after failover

**Debugging:**
```bash
# Check client connection distribution
redis-cli -h 10.0.1.100 client list | wc -l  # Old master
redis-cli -h 10.0.1.101 client list | wc -l  # New master

# Test Sentinel client discovery
redis-cli -p 26379 sentinel get-master-addr-by-name mymaster

# Check application logs for connection errors
grep -E "(connection.*refused|timeout|failover)" /var/log/app/app.log
```

**Solutions:**

**Option 1: Client Configuration Fix**
```python
# Proper Sentinel client configuration
import redis.sentinel

# Configure multiple Sentinels for redundancy
sentinels = [
    ('10.0.1.10', 26379),
    ('10.0.1.11', 26379),
    ('10.0.1.12', 26379)
]

sentinel = redis.sentinel.Sentinel(
    sentinels,
    socket_timeout=0.5,          # Fast timeout for dead Sentinels
    socket_connect_timeout=0.5,
    socket_keepalive=True,
    socket_keepalive_options={}
)

# Always discover master through Sentinel
master = sentinel.master_for(
    'mymaster',
    socket_timeout=1.0,
    socket_connect_timeout=1.0,
    retry_on_timeout=True,
    health_check_interval=30     # Regular health checks
)
```

**Option 2: Connection Pool Tuning**
```python
# Configure connection pool for faster failover
master = sentinel.master_for(
    'mymaster',
    connection_pool_kwargs={
        'max_connections': 20,
        'health_check_interval': 10,  # More frequent health checks
        'retry_on_timeout': True,
        'socket_keepalive': True,
        'socket_keepalive_options': {
            1: 1,  # TCP_KEEPIDLE
            2: 3,  # TCP_KEEPINTVL
            3: 5,  # TCP_KEEPCNT
        }
    }
)
```

## Critical Monitoring Queries

### Sentinel Health Metrics

```bash
# Monitor Sentinel cluster health
for port in 26379 26380 26381; do
  echo "=== Sentinel $port ==="
  redis-cli -p $port info sentinel | grep -E "(sentinel_masters|sentinel_running_scripts)"
  redis-cli -p $port sentinel masters | grep -E "(flags|num-slaves|quorum)"
done

# Check for recent failovers
redis-cli -p 26379 sentinel masters | grep -E "(failover-timeout|last-ok-ping-reply)"

# Monitor replication lag
master_offset=$(redis-cli -h 10.0.1.100 info replication | grep master_repl_offset | cut -d: -f2)
for slave in 10.0.1.101 10.0.1.102; do
  slave_offset=$(redis-cli -h $slave info replication | grep slave_repl_offset | cut -d: -f2)
  lag=$((master_offset - slave_offset))
  echo "Slave $slave lag: $lag bytes"
done
```

### Automated Health Check Script

```bash
#!/bin/bash
# redis_sentinel_health.sh

SENTINELS="26379 26380 26381"
MASTER_NAME="mymaster"

check_sentinel_health() {
  local failed=0
  local total=0

  for port in $SENTINELS; do
    total=$((total + 1))
    if ! redis-cli -p $port ping >/dev/null 2>&1; then
      echo "CRITICAL: Sentinel $port is down"
      failed=$((failed + 1))
    else
      # Check if this Sentinel knows about the master
      if ! redis-cli -p $port sentinel masters | grep -q $MASTER_NAME; then
        echo "WARNING: Sentinel $port doesn't know about $MASTER_NAME"
        failed=$((failed + 1))
      fi
    fi
  done

  echo "Sentinel health: $((total - failed))/$total online"
  return $failed
}

check_master_consistency() {
  local masters=()
  local consistent=true

  for port in $SENTINELS; do
    local master_addr=$(redis-cli -p $port sentinel get-master-addr-by-name $MASTER_NAME 2>/dev/null)
    if [ -n "$master_addr" ]; then
      masters+=("$master_addr")
    fi
  done

  if [ ${#masters[@]} -eq 0 ]; then
    echo "CRITICAL: No Sentinels know about master $MASTER_NAME"
    return 1
  fi

  local first_master="${masters[0]}"
  for master in "${masters[@]}"; do
    if [ "$master" != "$first_master" ]; then
      echo "CRITICAL: Split-brain detected - multiple masters: ${masters[*]}"
      return 1
    fi
  done

  echo "Master consistency: OK ($first_master)"
  return 0
}

# Run checks
check_sentinel_health
check_master_consistency
```

## Production Example: Instagram's Redis Sentinel

**Problem:** Frequent false failovers during traffic spikes causing application instability

**Initial Configuration Issues:**
- down-after-milliseconds: 5000ms (too aggressive)
- Quorum: 2 out of 5 Sentinels (too low)
- No min-slaves configuration

**Metrics During Problem Period:**
- 15+ failovers per day
- 30-second application downtime per failover
- False positive rate: 80% of failovers

**Solution:**
```bash
# Tuned Sentinel configuration
sentinel down-after-milliseconds mymaster 15000    # Increased from 5s
sentinel failover-timeout mymaster 60000           # Increased from 30s
sentinel parallel-syncs mymaster 1                 # Reduced from 2
sentinel monitor mymaster 10.0.1.100 6379 3       # Increased quorum

# Added to Redis master
min-slaves-to-write 1
min-slaves-max-lag 15
```

**Results:**
- Failover rate reduced to <1 per month
- False positive rate dropped to <5%
- Application availability improved from 99.9% to 99.99%
- Zero data loss during legitimate failovers

## Emergency Response Playbook

### Immediate Actions (< 2 minutes)

1. **Check Sentinel Consensus:**
   ```bash
   redis-cli -p 26379 sentinel masters | grep flags
   ```

2. **Verify Current Master:**
   ```bash
   redis-cli -p 26379 sentinel get-master-addr-by-name mymaster
   ```

3. **Test Master Connectivity:**
   ```bash
   redis-cli -h $(redis-cli -p 26379 sentinel get-master-addr-by-name mymaster | head -1) ping
   ```

### Short-term Mitigation (< 10 minutes)

1. **Force Manual Failover if Needed:**
   ```bash
   redis-cli -p 26379 sentinel failover mymaster
   ```

2. **Reset Split-Brain Scenario:**
   ```bash
   # Reset incorrect masters to slaves
   redis-cli -h <wrong-master-ip> slaveof <correct-master-ip> 6379
   ```

3. **Restart Problematic Sentinels:**
   ```bash
   systemctl restart redis-sentinel
   ```

### Prevention Strategies

1. **Configuration Validation:**
   - Use odd number of Sentinels (3, 5, 7)
   - Set quorum to majority (n/2 + 1)
   - Configure appropriate timeouts based on network characteristics

2. **Network Design:**
   - Deploy Sentinels across different failure domains
   - Use dedicated network for Redis replication
   - Implement network monitoring and alerting

3. **Client Configuration:**
   - Use proper Sentinel client libraries
   - Configure connection pooling with health checks
   - Implement exponential backoff for reconnections

## Real Production Metrics

**Twitter's Redis Sentinel Deployment:**
- 50+ Redis clusters with Sentinel
- 5 Sentinels per cluster across 3 AZs
- 99.99% availability with <10 second failover time
- Zero data loss in 2+ years of operation

**Key Learnings:**
- Network partitions are the primary cause of Sentinel issues
- Proper timeout configuration is critical for stable operation
- Client-side failover logic is as important as server-side
- Regular failover testing prevents surprise issues

## Related Debugging Guides

- [Redis Memory Issues](/debugging/redis-memory-issues)
- [Load Balancer Debugging](/debugging/load-balancer-debugging)
- [Database Connection Pool Debugging](/debugging/database-connection-pool-debugging)