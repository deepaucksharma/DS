# MySQL Performance Profile

## Overview

MySQL performance characteristics in production environments, covering InnoDB optimization, replication, partitioning, and threading models. Based on Uber's Schemaless implementation and other high-scale deployments.

## 4-Plane MySQL Architecture Performance Profile

### Complete MySQL Performance Stack

```mermaid
graph TB
    subgraph EdgePlane[🔵 Edge Plane - Connection Management]
        ProxySQL[ProxySQL<br/>Connection Pooling<br/>Read/Write Split<br/>Query Routing<br/>💰 $500/month]

        HAProxy[HAProxy<br/>Load Balancing<br/>Health Checks<br/>Circuit Breaking<br/>💰 $200/month]

        MaxScale[MariaDB MaxScale<br/>Connection Multiplexing<br/>Query Load Balancing<br/>Firewall Rules<br/>💰 $800/month]
    end

    subgraph ServicePlane[🟢 Service Plane - Query Processing]
        QueryCache[Query Cache<br/>❌ DISABLED<br/>Reason: High Contention<br/>Replaced with Application Cache]

        QueryParser[SQL Parser & Optimizer<br/>Cost-Based Optimization<br/>Index Selection<br/>Join Algorithms]

        QueryExec[Query Execution Engine<br/>Thread Pool: 64 threads<br/>Memory: 256MB per thread<br/>Timeout: 30s]
    end

    subgraph StatePlane[🟠 State Plane - Storage & Buffer Management]
        BufferPool[InnoDB Buffer Pool<br/>Size: 48GB (75% of RAM)<br/>Instances: 16<br/>Hit Ratio: 99.8%<br/>💰 $2,000/month]

        Storage[Storage Engine<br/>InnoDB: 95% of tables<br/>MyISAM: 5% (read-only)<br/>NVMe SSD: 20,000 IOPS<br/>💰 $3,500/month]

        Replication[Group Replication<br/>3-node cluster<br/>Strong consistency<br/>Auto-failover: 30s<br/>💰 $6,000/month]
    end

    subgraph ControlPlane[🔴 Control Plane - Monitoring & Operations]
        PerfSchema[Performance Schema<br/>Query Analysis<br/>Lock Monitoring<br/>Resource Usage<br/>Storage: 1GB]

        Monitoring[Prometheus + Grafana<br/>MySQL Exporter<br/>Real-time Metrics<br/>Alerting Rules<br/>💰 $300/month]

        Backup[Backup & Recovery<br/>XtraBackup: Daily<br/>Binlog: Real-time<br/>RTO: 15 minutes<br/>💰 $800/month]
    end

    %% Connections
    ProxySQL --> QueryParser
    HAProxy --> QueryExec
    QueryExec --> BufferPool
    BufferPool --> Storage
    Storage --> Replication
    PerfSchema --> Monitoring
    Monitoring --> Backup

    %% Apply 4-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class ProxySQL,HAProxy,MaxScale edgeStyle
    class QueryCache,QueryParser,QueryExec serviceStyle
    class BufferPool,Storage,Replication stateStyle
    class PerfSchema,Monitoring,Backup controlStyle
```

### InnoDB Buffer Pool Optimization - Production Commands

```bash
# 🟠 State Plane Buffer Pool Analysis Commands
# Check current buffer pool status
mysql -e "SHOW ENGINE INNODB STATUS\G" | grep -A 20 "BUFFER POOL AND MEMORY"

# Buffer pool hit ratio (target: >99%)
mysql -e "SELECT
  ROUND(100 - ((Innodb_buffer_pool_reads / Innodb_buffer_pool_read_requests) * 100), 2) AS hit_ratio
  FROM (SELECT VARIABLE_VALUE AS Innodb_buffer_pool_reads FROM performance_schema.global_status WHERE VARIABLE_NAME = 'Innodb_buffer_pool_reads') r,
       (SELECT VARIABLE_VALUE AS Innodb_buffer_pool_read_requests FROM performance_schema.global_status WHERE VARIABLE_NAME = 'Innodb_buffer_pool_read_requests') rr;"

# Buffer pool utilization by instance
mysql -e "SELECT pool_id, pool_size, free_buffers, database_pages, old_database_pages
          FROM information_schema.INNODB_BUFFER_POOL_STATS
          ORDER BY pool_id;"

# Page flush rate monitoring (every 5 seconds)
mysql -e "SELECT pages_made_dirty, pages_flushed,
          (pages_made_dirty - pages_flushed) AS dirty_pages_backlog
          FROM information_schema.INNODB_BUFFER_POOL_STATS;"

# Buffer pool optimization recommendations
mysql -e "SELECT
  'innodb_buffer_pool_size' as parameter,
  @@innodb_buffer_pool_size / 1024 / 1024 / 1024 as current_gb,
  'Recommended: 75% of total RAM' as recommendation
  UNION ALL
  SELECT
  'innodb_buffer_pool_instances' as parameter,
  @@innodb_buffer_pool_instances as current_value,
  'Recommended: 16 for 48GB+ buffer pool' as recommendation;"
```

### Buffer Pool Tuning Results - Uber Schemaless

```mermaid
graph LR
    subgraph Before Optimization
        B1[innodb_buffer_pool_size = 4GB<br/>innodb_buffer_pool_instances = 1<br/>Hit ratio: 95%<br/>Query latency p95: 15ms]
    end

    subgraph After Optimization
        A1[innodb_buffer_pool_size = 48GB<br/>innodb_buffer_pool_instances = 16<br/>Hit ratio: 99.8%<br/>Query latency p95: 2ms]
    end

    subgraph Configuration Changes
        C1[Buffer pool sizing<br/>75% of available RAM<br/>64GB server → 48GB pool]

        C2[Instance count<br/>16 instances for better concurrency<br/>Reduces mutex contention]

        C3[Page flushing<br/>innodb_io_capacity = 20000<br/>innodb_io_capacity_max = 40000]
    end

    B1 --> A1
    A1 --> C1
    C1 --> C2
    C2 --> C3

    classDef beforeStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef afterStyle fill:#10B981,stroke:#059669,color:#fff
    classDef configStyle fill:#3B82F6,stroke:#2563EB,color:#fff

    class B1 beforeStyle
    class A1 afterStyle
    class C1,C2,C3 configStyle
```

## Group Replication Performance

### Group Replication Architecture

```mermaid
graph TB
    subgraph MySQL Group Replication Cluster
        M1[(Master 1<br/>Primary mode<br/>Write load: 30K TPS<br/>Group communication: 50ms)]

        M2[(Master 2<br/>Secondary<br/>Read load: 100K QPS<br/>Apply lag: 20ms)]

        M3[(Master 3<br/>Secondary<br/>Read load: 80K QPS<br/>Apply lag: 25ms)]

        subgraph Group Communication
            GC[XCom Consensus<br/>Paxos protocol<br/>Majority voting<br/>Network partition tolerance]

            GL[Group Logging<br/>Binary log events<br/>GTIDs coordination<br/>Conflict detection]
        end

        M1 <--> GC
        M2 <--> GC
        M3 <--> GC
        GC --> GL
    end

    subgraph Performance Metrics
        P1[Transaction certification<br/>Success rate: 99.5%<br/>Conflict rate: 0.5%<br/>Latency overhead: 5ms]

        P2[Network overhead<br/>Bandwidth: 50 Mbps<br/>Message size: 1-2KB avg<br/>Round-trip time: 2ms]
    end

    classDef masterStyle fill:#10B981,stroke:#059669,color:#fff
    classDef commStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef perfStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class M1,M2,M3 masterStyle
    class GC,GL commStyle
    class P1,P2 perfStyle
```

### Group Replication vs Traditional Replication

```mermaid
graph LR
    subgraph Traditional Master-Slave
        T1[Master<br/>Writes: All<br/>Reads: Optional]
        T2[Slave 1<br/>Lag: 100ms<br/>Consistent: Eventually]
        T3[Slave 2<br/>Lag: 200ms<br/>Consistent: Eventually]

        T1 --> T2
        T1 --> T3

        T4[Failover: Manual<br/>RTO: 5-10 minutes<br/>Data loss: Possible]
    end

    subgraph Group Replication
        G1[Primary<br/>Writes: All<br/>Synchronous commit]
        G2[Secondary 1<br/>Lag: 20ms<br/>Consistent: Strong]
        G3[Secondary 2<br/>Lag: 25ms<br/>Consistent: Strong]

        G1 <--> G2
        G2 <--> G3
        G3 <--> G1

        G4[Failover: Automatic<br/>RTO: 30 seconds<br/>Data loss: None]
    end

    classDef traditionalStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef groupStyle fill:#10B981,stroke:#059669,color:#fff
    classDef metricStyle fill:#3B82F6,stroke:#2563EB,color:#fff

    class T1,T2,T3 traditionalStyle
    class G1,G2,G3 groupStyle
    class T4,G4 metricStyle
```

## Partition Pruning Benefits

### Range Partitioning Performance

```mermaid
graph TB
    subgraph Partitioned Table - Order History
        P1[Partition 2024_Q1<br/>Rows: 10M<br/>Size: 2GB<br/>Index size: 200MB]

        P2[Partition 2024_Q2<br/>Rows: 12M<br/>Size: 2.4GB<br/>Index size: 240MB]

        P3[Partition 2024_Q3<br/>Rows: 15M<br/>Size: 3GB<br/>Index size: 300MB]

        P4[Partition 2024_Q4<br/>Rows: 18M<br/>Size: 3.6GB<br/>Index size: 360MB]
    end

    subgraph Query Performance
        Q1[SELECT * FROM orders<br/>WHERE order_date >= '2024-10-01'<br/>AND order_date < '2024-11-01']

        Q2[Partition pruning<br/>Examines: P4 only<br/>Rows scanned: 3M instead of 55M<br/>Query time: 0.5s vs 8s]

        Q1 --> Q2
    end

    subgraph Maintenance Benefits
        M1[Partition dropping<br/>DELETE old data: 0.1s<br/>vs DELETE command: 2 hours]

        M2[Index maintenance<br/>Per-partition indexes<br/>Rebuild time: 10min vs 4 hours]

        M3[Backup strategy<br/>Incremental per partition<br/>Recovery granularity improved]
    end

    classDef partitionStyle fill:#10B981,stroke:#059669,color:#fff
    classDef queryStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef maintStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class P1,P2,P3,P4 partitionStyle
    class Q1,Q2 queryStyle
    class M1,M2,M3 maintStyle
```

### Hash Partitioning for Load Distribution

```mermaid
graph TB
    subgraph Hash Partitioned User Table
        H1[Partition 0<br/>hash user_id % 8 = 0<br/>Rows: 12.5M<br/>Hotness: Even]

        H2[Partition 1<br/>hash user_id % 8 = 1<br/>Rows: 12.5M<br/>Hotness: Even]

        H3[Partition 7<br/>hash user_id % 8 = 7<br/>Rows: 12.5M<br/>Hotness: Even]

        H4[Total: 100M users<br/>Even distribution<br/>No hot partitions]
    end

    subgraph Load Balancing Results
        L1[Write distribution<br/>Each partition: 12.5K TPS<br/>No bottlenecks<br/>Linear scaling]

        L2[Read distribution<br/>Cache hit ratio: 95%<br/>Buffer pool efficiency<br/>Parallel query execution]
    end

    subgraph vs Single Table
        S1[Single table issues<br/>Lock contention<br/>Buffer pool thrashing<br/>Index hotspots]

        S2[Partition benefits<br/>Parallel processing<br/>Reduced lock scope<br/>Better cache locality]
    end

    classDef hashStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef loadStyle fill:#10B981,stroke:#059669,color:#fff
    classDef compStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class H1,H2,H3,H4 hashStyle
    class L1,L2 loadStyle
    class S1,S2 compStyle
```

## Thread Pool vs Connection-per-Thread

### Threading Model Comparison

```mermaid
graph LR
    subgraph Connection-per-Thread (Default)
        CT1[Client 1] --> T1[Thread 1<br/>Memory: 2MB<br/>Context switches: High]
        CT2[Client 2] --> T2[Thread 2<br/>Memory: 2MB<br/>Dedicated connection]
        CT3[Client 1000] --> T1000[Thread 1000<br/>Memory: 2GB total<br/>Scheduler overhead: High]
    end

    subgraph Thread Pool
        TP1[Client 1] --> P1[Thread Pool<br/>Size: 64 threads<br/>Memory: 128MB]
        TP2[Client 2] --> P1
        TP3[Client 1000] --> P1

        P1 --> W1[Worker 1<br/>Multiple clients<br/>Efficient scheduling]
        P1 --> W2[Worker 64<br/>Better CPU utilization<br/>Reduced context switching]
    end

    subgraph Performance Impact
        PI1[Connection-per-thread<br/>Max connections: 1000<br/>Memory: 2GB threads<br/>Context switches: 50K/sec]

        PI2[Thread pool<br/>Max connections: 10000<br/>Memory: 128MB threads<br/>Context switches: 5K/sec]
    end

    classDef traditionalStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef poolStyle fill:#10B981,stroke:#059669,color:#fff
    classDef metricStyle fill:#3B82F6,stroke:#2563EB,color:#fff

    class CT1,CT2,CT3,T1,T2,T1000 traditionalStyle
    class TP1,TP2,TP3,P1,W1,W2 poolStyle
    class PI1,PI2 metricStyle
```

### Thread Pool Configuration Impact

```mermaid
graph TB
    subgraph Thread Pool Sizing Strategy
        S1[thread_pool_size = CPU cores<br/>For CPU-bound workloads<br/>64 cores = 64 threads]

        S2[thread_pool_size = 2 × CPU cores<br/>For mixed workloads<br/>64 cores = 128 threads]

        S3[thread_pool_size = 4 × CPU cores<br/>For I/O-bound workloads<br/>64 cores = 256 threads]
    end

    subgraph Real Performance Results
        R1[CPU-bound sizing<br/>Latency p95: 5ms<br/>Throughput: 80K QPS<br/>CPU utilization: 95%]

        R2[Mixed workload sizing<br/>Latency p95: 8ms<br/>Throughput: 120K QPS<br/>CPU utilization: 85%]

        R3[I/O-bound sizing<br/>Latency p95: 15ms<br/>Throughput: 150K QPS<br/>CPU utilization: 70%]
    end

    S1 --> R1
    S2 --> R2
    S3 --> R3

    classDef strategyStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef resultStyle fill:#10B981,stroke:#059669,color:#fff

    class S1,S2,S3 strategyStyle
    class R1,R2,R3 resultStyle
```

## Uber's Schemaless Implementation Metrics

### Schemaless Architecture Performance

```mermaid
graph TB
    subgraph Uber Schemaless Layer
        APP[Uber Application<br/>Requests: 1M QPS<br/>Latency target: < 5ms p99]

        SCHEMA[Schemaless Layer<br/>Connection pooling<br/>Intelligent routing<br/>Consistent hashing]

        subgraph MySQL Shards
            S1[(Shard 1<br/>Users: 10M<br/>TPS: 50K<br/>Storage: 2TB)]

            S2[(Shard 2<br/>Users: 10M<br/>TPS: 50K<br/>Storage: 2TB)]

            S16[(Shard 16<br/>Users: 10M<br/>TPS: 50K<br/>Storage: 2TB)]
        end

        APP --> SCHEMA
        SCHEMA --> S1
        SCHEMA --> S2
        SCHEMA --> S16
    end

    subgraph Performance Achievements
        P1[Total throughput: 800K TPS<br/>Read latency p99: 2ms<br/>Write latency p99: 5ms<br/>Availability: 99.99%]

        P2[Scaling characteristics<br/>Linear scaling to 200+ shards<br/>No cross-shard transactions<br/>Automatic failover: 30s]
    end

    classDef appStyle fill:#10B981,stroke:#059669,color:#fff
    classDef schemaStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef shardStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef perfStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class APP appStyle
    class SCHEMA schemaStyle
    class S1,S2,S16 shardStyle
    class P1,P2 perfStyle
```

### Key Configuration Parameters

```mermaid
graph LR
    subgraph InnoDB Configuration
        I1[innodb_buffer_pool_size = 48GB<br/>innodb_buffer_pool_instances = 16<br/>innodb_log_file_size = 2GB<br/>innodb_flush_log_at_trx_commit = 1]
    end

    subgraph Performance Configuration
        P1[max_connections = 2000<br/>thread_pool_size = 128<br/>query_cache_type = OFF<br/>innodb_io_capacity = 20000]
    end

    subgraph Replication Configuration
        R1[log_bin = ON<br/>binlog_format = ROW<br/>sync_binlog = 1<br/>gtid_mode = ON]
    end

    subgraph Results
        RES1[Peak QPS: 50K per shard<br/>Buffer pool hit rate: 99.8%<br/>Replication lag: < 1s p99<br/>Crash recovery: < 30s]
    end

    I1 --> RES1
    P1 --> RES1
    R1 --> RES1

    classDef configStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef resultStyle fill:#10B981,stroke:#059669,color:#fff

    class I1,P1,R1 configStyle
    class RES1 resultStyle
```

## Production Optimization Strategies

### Query Optimization Pipeline

```mermaid
graph TB
    subgraph Slow Query Analysis
        SQ1[Enable slow_query_log<br/>long_query_time = 0.1<br/>log_queries_not_using_indexes = ON]

        SQ2[Query analysis tools<br/>pt-query-digest<br/>Performance Schema<br/>sys schema views]

        SQ1 --> SQ2
    end

    subgraph Index Optimization
        IO1[Missing index detection<br/>EXPLAIN analysis<br/>Index usage statistics<br/>Duplicate index removal]

        IO2[Composite index strategy<br/>Left-most prefix rule<br/>Covering indexes<br/>Index merge optimization]

        IO1 --> IO2
    end

    subgraph Results Achieved
        R1[Query performance<br/>p95 latency: 15ms → 2ms<br/>Index efficiency: 85% → 99%<br/>Full table scans: 5% → 0.1%]
    end

    SQ2 --> IO1
    IO2 --> R1

    classDef analysisStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef optimStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef resultStyle fill:#10B981,stroke:#059669,color:#fff

    class SQ1,SQ2 analysisStyle
    class IO1,IO2 optimStyle
    class R1 resultStyle
```

### 🚨 Production MySQL Performance Troubleshooting

### 4-Plane Performance Bottleneck Commands

#### 🔵 Edge Plane Performance Issues
```bash
# Connection pool analysis (ProxySQL/HAProxy)
# ProxySQL connection stats
mysql -h proxysql-admin -P6032 -uadmin -padmin -e "SELECT * FROM stats_mysql_connection_pool ORDER BY ConnUsed DESC;"

# HAProxy connection metrics
echo "show stat" | socat stdio /var/lib/haproxy/stats | grep mysql | awk -F, '{print $1,$5,$17,$18}'

# Connection refused errors
ss -tuln | grep :3306
netstat -an | grep :3306 | grep -c ESTABLISHED
```

#### 🟢 Service Plane Performance Issues
```bash
# Thread pool saturation detection
mysql -e "SELECT COUNT(*) as active_threads FROM performance_schema.threads WHERE PROCESSLIST_STATE IS NOT NULL;"

# Query execution bottlenecks
mysql -e "SELECT digest_text, count_star, avg_timer_wait/1000000000 as avg_seconds
          FROM performance_schema.events_statements_summary_by_digest
          WHERE avg_timer_wait > 1000000000 ORDER BY avg_timer_wait DESC LIMIT 10;"

# Lock contention analysis
mysql -e "SELECT object_schema, object_name, lock_type, lock_duration, lock_status
          FROM performance_schema.metadata_locks WHERE lock_status = 'PENDING';"
```

#### 🟠 State Plane Performance Issues
```bash
# Buffer pool pressure indicators
mysql -e "SELECT
  pool_id,
  (database_pages / pool_size) * 100 as utilization_pct,
  free_buffers,
  pages_made_dirty - pages_flushed as dirty_backlog
  FROM information_schema.INNODB_BUFFER_POOL_STATS;"

# I/O bottlenecks
mysql -e "SELECT file_name, SUM(count_read) as reads, SUM(count_write) as writes,
          SUM(sum_timer_wait)/1000000000 as total_seconds
          FROM performance_schema.file_summary_by_instance
          GROUP BY file_name ORDER BY total_seconds DESC LIMIT 10;"

# Replication lag measurement
mysql -e "SELECT
  CHANNEL_NAME,
  SERVICE_STATE,
  LAST_ERROR_MESSAGE,
  LAST_ERROR_TIMESTAMP
  FROM performance_schema.replication_connection_status;"
```

#### 🔴 Control Plane Performance Issues
```bash
# Performance Schema overhead
mysql -e "SELECT COUNT(*) as enabled_instruments FROM performance_schema.setup_instruments WHERE ENABLED='YES';"

# Resource exhaustion alerts
mysql -e "SELECT
  'max_connections' as setting,
  @@max_connections as max_value,
  (SELECT COUNT(*) FROM performance_schema.threads WHERE PROCESSLIST_USER IS NOT NULL) as current_connections,
  ROUND(((SELECT COUNT(*) FROM performance_schema.threads WHERE PROCESSLIST_USER IS NOT NULL) / @@max_connections) * 100, 2) as utilization_pct;"

# Backup impact on performance
mysqladmin processlist | grep -i backup
mysql -e "SELECT EVENT_NAME, COUNT_STAR, SUM_TIMER_WAIT/1000000000 as seconds
          FROM performance_schema.events_waits_summary_global_by_event_name
          WHERE EVENT_NAME LIKE '%file%' ORDER BY seconds DESC LIMIT 5;"
```

### Performance Optimization Quick Wins

#### Immediate Actions (< 5 minutes)
1. **Kill Long-Running Queries**:
   ```bash
   mysql -e "SELECT concat('KILL ',id,';') FROM information_schema.processlist
             WHERE command != 'Sleep' AND time > 300;"
   ```

2. **Flush Query Cache** (if enabled):
   ```bash
   mysql -e "FLUSH QUERY CACHE; RESET QUERY CACHE;"
   ```

3. **Check for Lock Waits**:
   ```bash
   mysql -e "SELECT r.trx_id waiting_trx_id, r.trx_mysql_thread_id waiting_thread,
             r.trx_query waiting_query, b.trx_id blocking_trx_id,
             b.trx_mysql_thread_id blocking_thread, b.trx_query blocking_query
             FROM information_schema.innodb_lock_waits w
             INNER JOIN information_schema.innodb_trx b ON b.trx_id = w.blocking_trx_id
             INNER JOIN information_schema.innodb_trx r ON r.trx_id = w.requesting_trx_id;"
   ```

#### Medium-term Optimizations (< 30 minutes)
1. **Enable Thread Pool** (MySQL 8.0+):
   ```sql
   INSTALL PLUGIN thread_pool SONAME 'thread_pool.so';
   SET GLOBAL thread_pool_size = 16;
   SET GLOBAL thread_pool_max_threads = 1000;
   ```

2. **Optimize Buffer Pool**:
   ```sql
   SET GLOBAL innodb_buffer_pool_dump_at_shutdown = ON;
   SET GLOBAL innodb_buffer_pool_load_at_startup = ON;
   ```

3. **Adjust I/O Capacity**:
   ```sql
   SET GLOBAL innodb_io_capacity = 2000;
   SET GLOBAL innodb_io_capacity_max = 4000;
   ```

### Critical Performance Thresholds

| Metric | Healthy | Warning | Critical | Action |
|--------|---------|---------|----------|---------|
| Buffer Pool Hit Rate | >99% | 95-99% | <95% | Increase buffer pool size |
| Active Connections | <70% max | 70-85% | >85% | Scale connection pool |
| Query Response Time | <100ms | 100ms-1s | >1s | Optimize slow queries |
| Replication Lag | <1s | 1-10s | >10s | Check master load |
| Lock Wait Time | <100ms | 100ms-1s | >1s | Identify blocking queries |
| I/O Utilization | <70% | 70-85% | >85% | Upgrade storage |

### Cost-Performance Optimization Matrix

#### Scale Point 1: < 10K QPS
- **Instance**: db.t3.large ($150/month)
- **Storage**: 100GB GP2 SSD ($10/month)
- **Configuration**: Basic InnoDB settings
- **Total Cost**: $160/month

#### Scale Point 2: 10K-50K QPS
- **Instance**: db.r5.xlarge ($450/month)
- **Storage**: 500GB GP3 SSD ($60/month)
- **Read Replicas**: 2x db.r5.large ($600/month)
- **Configuration**: Optimized buffer pool, thread pool
- **Total Cost**: $1,110/month

#### Scale Point 3: > 50K QPS
- **Instance**: db.r5.4xlarge ($1,800/month)
- **Storage**: 2TB GP3 SSD ($240/month)
- **Read Replicas**: 4x db.r5.2xlarge ($2,400/month)
- **Sharding**: Multiple clusters
- **Total Cost**: $4,440/month

### Critical Lessons Learned

1. **Buffer Pool Sizing**: 75% of RAM is optimal for most workloads
   - **Command**: `SELECT @@innodb_buffer_pool_size / (1024*1024*1024) as buffer_pool_gb;`
   - **Monitor**: Buffer pool hit ratio >99%

2. **Thread Pool**: Essential for high-concurrency applications (> 1000 connections)
   - **Command**: `SHOW VARIABLES LIKE 'thread_pool%';`
   - **Monitor**: Thread pool utilization <80%

3. **Partitioning**: Mandatory for tables > 100GB or high-velocity time-series data
   - **Command**: `SELECT table_name, partition_name, table_rows FROM information_schema.partitions WHERE table_schema='mydb';`
   - **Monitor**: Query pruning effectiveness

4. **Group Replication**: Adds 5-10ms latency but provides strong consistency
   - **Command**: `SELECT * FROM performance_schema.replication_group_members;`
   - **Monitor**: Group replication lag <1s

5. **Connection Pooling**: Application-level pooling more effective than MySQL thread pool alone
   - **Monitor**: Connection pool utilization <70%
   - **Alert**: Connection refused errors

**Performance Benchmarks**:
- **Small Scale** (< 10K QPS): Single server, basic configuration
- **Medium Scale** (10K-100K QPS): Read replicas, partitioning, optimized configuration
- **Large Scale** (> 100K QPS): Sharding, advanced replication, specialized hardware

**Source**: Based on Uber Schemaless, Shopify, and GitHub MySQL implementations