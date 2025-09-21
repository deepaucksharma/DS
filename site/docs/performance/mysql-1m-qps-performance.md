# MySQL at 1M QPS: Facebook's High-Performance Optimization Profile

## Overview

Facebook operates one of the world's largest MySQL deployments, handling over 1 million queries per second across thousands of instances. Their infrastructure supports 3 billion users with complex social graph queries, timeline generation, and real-time messaging, requiring sub-millisecond response times with strict consistency guarantees.

## Architecture for Performance

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - #0066CC]
        LB[Facebook Load Balancer<br/>Katran + BGP<br/>99.99% availability]
        CDN[Facebook CDN<br/>Global edge network<br/>87% cache hit ratio]
    end

    subgraph ServicePlane[Service Plane - #00AA00]
        API[Social Graph API<br/>Hack/PHP + C++<br/>50,000+ instances]
        PROXY[MySQL Proxy<br/>Custom proxy layer<br/>Connection multiplexing]
    end

    subgraph StatePlane[State Plane - #FF8800]
        PRIMARY[Primary MySQL<br/>500x r6i.32xlarge<br/>Write operations]
        REPLICA[Read Replicas<br/>5000x r6i.16xlarge<br/>Read scaling]
        CACHE[TAO Cache Layer<br/>Memcached clusters<br/>99.8% hit ratio]
    end

    subgraph ControlPlane[Control Plane - #CC0000]
        MON[Monitoring<br/>Facebook ODS<br/>Real-time metrics]
        FAILOVER[Automated Failover<br/>MHA + Custom tools<br/><30s recovery]
    end

    CDN --> LB
    LB --> API
    API --> PROXY
    API --> CACHE
    PROXY --> PRIMARY
    PROXY --> REPLICA
    CACHE --> REPLICA

    MON --> PRIMARY
    MON --> REPLICA
    FAILOVER --> PRIMARY

    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class LB,CDN edgeStyle
    class API,PROXY serviceStyle
    class PRIMARY,REPLICA,CACHE stateStyle
    class MON,FAILOVER controlStyle
```

## Performance Metrics and Benchmarks

### Global Cluster Overview
- **Total QPS**: 1.2M queries per second peak
- **Write QPS**: 250K writes per second
- **Read QPS**: 950K reads per second
- **Instance Count**: 5,500 MySQL instances total
- **Primary Instances**: 500 write masters
- **Read Replicas**: 5,000 read slaves (10:1 ratio)
- **Instance Types**: r6i.32xlarge (primary), r6i.16xlarge (replicas)

### Query Performance Profile
```mermaid
graph LR
    subgraph QueryLatency[MySQL Query Latency - p99]
        POINT[Point Query: 0.3ms<br/>Primary key lookup<br/>InnoDB buffer hit]
        RANGE[Range Query: 2.1ms<br/>Index range scan<br/>Social graph traversal]
        JOIN[Complex Join: 8.5ms<br/>Multi-table join<br/>Timeline generation]
        AGG[Aggregation: 15ms<br/>GROUP BY query<br/>Analytics processing]
        UPDATE[Update: 1.2ms<br/>Single row update<br/>Index maintenance]
    end

    subgraph Percentiles[Response Time Distribution]
        P50[p50: 0.2ms]
        P95[p95: 1.4ms]
        P99[p99: 4.8ms]
        P999[p999: 18ms]
        P9999[p9999: 85ms]
    end

    subgraph Workload[Query Distribution]
        READS[Read Queries: 80%<br/>Profile lookups<br/>Timeline queries]
        WRITES[Write Queries: 15%<br/>Posts, comments<br/>Status updates]
        ANALYTICS[Analytics: 5%<br/>Reporting queries<br/>Background processing]
    end

    classDef metricStyle fill:#FF8800,stroke:#CC6600,color:#fff
    class POINT,RANGE,JOIN,AGG,UPDATE,P50,P95,P99,P999,P9999,READS,WRITES,ANALYTICS metricStyle
```

### Primary Instance Performance
- **Instance Type**: r6i.32xlarge (128 vCPUs, 1TB RAM)
- **QPS per Primary**: 2,500 queries per second
- **Storage**: 20TB NVMe SSD per instance
- **Buffer Pool**: 768GB (75% of total RAM)
- **Connections**: 8,000 active connections per instance
- **Replication Lag**: 50ms average to read replicas

## Optimization Techniques Used

### 1. InnoDB Configuration Optimization
```yaml
# Facebook MySQL Configuration
innodb_buffer_pool_size: 768G              # 75% of total RAM
innodb_buffer_pool_instances: 64            # Reduce contention
innodb_log_file_size: 128G                  # Large redo logs
innodb_log_buffer_size: 256M                # Write buffering
innodb_flush_log_at_trx_commit: 2          # Performance over durability
innodb_flush_method: O_DIRECT              # Bypass OS cache
innodb_io_capacity: 20000                   # NVMe optimization
innodb_io_capacity_max: 40000               # Burst capacity
innodb_read_io_threads: 32                  # Parallel reads
innodb_write_io_threads: 32                 # Parallel writes
innodb_thread_concurrency: 0               # Unlimited concurrency
innodb_adaptive_hash_index: ON             # Query optimization
```

### 2. Query Optimization Strategy
```mermaid
graph TB
    subgraph QueryOpt[Facebook's MySQL Query Optimization]
        SCHEMA[Schema Design<br/>Denormalized tables<br/>Query-specific optimization]
        INDEXES[Index Strategy<br/>Composite indexes<br/>Covering indexes]
        PARTITION[Partitioning<br/>Time-based partitioning<br/>User-based sharding]
        CACHE[Query Caching<br/>Application-level caching<br/>Prepared statements]
    end

    subgraph Techniques[Optimization Techniques]
        DENORM[Denormalization<br/>Trade storage for performance<br/>Eliminate joins]
        COVERING[Covering Indexes<br/>Index-only queries<br/>Avoid table lookups]
        SHARD[Horizontal Sharding<br/>User-based partitioning<br/>Linear scaling]
        PREPARE[Prepared Statements<br/>Query plan caching<br/>Reduced parsing overhead]
    end

    SCHEMA --> DENORM
    INDEXES --> COVERING
    PARTITION --> SHARD
    CACHE --> PREPARE

    classDef optStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef techniqueStyle fill:#FF8800,stroke:#CC6600,color:#fff

    class SCHEMA,INDEXES,PARTITION,CACHE optStyle
    class DENORM,COVERING,SHARD,PREPARE techniqueStyle
```

### 3. Replication Optimization
- **Semi-synchronous Replication**: For critical writes
- **Parallel Replication**: Multi-threaded slave processing
- **GTID Replication**: Global transaction identifiers
- **Read-Only Routing**: Automatic read traffic distribution
- **Lag Monitoring**: Real-time replication lag tracking

### 4. Connection Management
- **Connection Pooling**: Custom proxy layer handles 50K+ connections
- **Persistent Connections**: Long-lived connections reduce overhead
- **Load Balancing**: Intelligent routing based on query type
- **Circuit Breakers**: Automatic failover on instance failure

## Bottleneck Analysis

### 1. I/O Performance Bottlenecks
```mermaid
graph TB
    subgraph IOBottlenecks[I/O Performance Analysis]
        RANDOM[Random I/O<br/>Point queries<br/>Buffer pool misses]
        SEQUENTIAL[Sequential I/O<br/>Range scans<br/>Large result sets]
        LOG[Redo Log I/O<br/>Transaction commits<br/>Write amplification]
        TEMP[Temporary I/O<br/>Sort operations<br/>JOIN processing]
    end

    subgraph Solutions[I/O Optimization Solutions]
        NVME[NVMe Storage<br/>Ultra-low latency<br/>High IOPS capacity]
        BUFFER[Large Buffer Pool<br/>768GB per instance<br/>99.8% hit ratio]
        ASYNC[Async I/O<br/>Native AIO<br/>Better concurrency]
        COMPRESS[Compression<br/>InnoDB page compression<br/>Reduced I/O volume]
    end

    RANDOM --> BUFFER
    SEQUENTIAL --> NVME
    LOG --> ASYNC
    TEMP --> COMPRESS

    classDef bottleneckStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef solutionStyle fill:#00AA00,stroke:#007700,color:#fff

    class RANDOM,SEQUENTIAL,LOG,TEMP bottleneckStyle
    class NVME,BUFFER,ASYNC,COMPRESS solutionStyle
```

### 2. CPU Bottlenecks
- **Query Processing**: 45% CPU for complex social graph queries
- **Index Maintenance**: 25% CPU for write-heavy workloads
- **Replication**: 15% CPU for slave processing
- **Connection Handling**: 10% CPU for connection management
- **Background Tasks**: 5% CPU for maintenance operations

### 3. Memory Bottlenecks
- **Buffer Pool Pressure**: Working set must fit in 768GB buffer
- **Sort Buffer**: Large GROUP BY operations require memory
- **Connection Memory**: 8K connections × 1MB = 8GB overhead
- **Temporary Tables**: Memory tables for intermediate results

## Scaling Limits Discovered

### 1. Single Instance Limits
```mermaid
graph LR
    subgraph InstanceScaling[Single Instance Scaling Analysis]
        I1[1K QPS<br/>Latency: 0.2ms<br/>CPU: 20%<br/>Memory: 200GB]
        I2[2K QPS<br/>Latency: 0.4ms<br/>CPU: 40%<br/>Memory: 400GB]
        I3[3K QPS<br/>Latency: 1.2ms<br/>CPU: 70%<br/>Memory: 650GB]
        I4[4K QPS<br/>Latency: 3.5ms<br/>CPU: 90%<br/>Memory: 900GB]
        I5[5K+ QPS<br/>CPU saturation<br/>Buffer pool thrashing<br/>Performance cliff]
    end

    I1 --> I2 --> I3 --> I4 --> I5

    subgraph Solution[Horizontal Scaling Solution]
        REPLICAS[Read Replicas<br/>10:1 read/write ratio<br/>Linear read scaling]
        SHARDING[Database Sharding<br/>User-based partitioning<br/>Write scaling]
    end

    I5 --> REPLICAS
    I5 --> SHARDING

    classDef scaleStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef solutionStyle fill:#00AA00,stroke:#007700,color:#fff

    class I1,I2,I3,I4,I5 scaleStyle
    class REPLICAS,SHARDING solutionStyle
```

### 2. Replication Scaling Limits
- **Read Replica Count**: 10 replicas optimal per primary
- **Replication Lag**: Increases with replica count
- **Network Bandwidth**: 25 Gbps limit per primary instance
- **Binary Log Size**: Large transactions cause lag spikes

### 3. Connection Scaling Limits
- **Connection Limit**: 8,000 connections per instance maximum
- **Memory Overhead**: Each connection consumes ~1MB RAM
- **CPU Context Switching**: High connection count degrades performance
- **Proxy Scaling**: Custom proxy layer handles connection multiplexing

## Cost vs Performance Trade-offs

### 1. Infrastructure Costs (Monthly)
```mermaid
graph TB
    subgraph CostBreakdown[Monthly Infrastructure Cost: $18,500,000]
        PRIMARY_COMPUTE[Primary Instances<br/>500 × r6i.32xlarge<br/>$7,200/month each<br/>$3,600,000 total]

        REPLICA_COMPUTE[Read Replicas<br/>5000 × r6i.16xlarge<br/>$3,600/month each<br/>$18,000,000 total]

        STORAGE[NVMe Storage<br/>110PB total @ $0.10/GB<br/>$11,000,000/month]

        NETWORK[Data Transfer<br/>50PB/month @ $0.09/GB<br/>$4,500,000/month]

        CACHE[TAO Cache Layer<br/>Memcached clusters<br/>$800,000/month]

        MONITORING[Monitoring Tools<br/>ODS + Custom tools<br/>$150,000/month]

        SUPPORT[Database Team<br/>200 MySQL experts<br/>$24,000,000/month]
    end

    PRIMARY_COMPUTE --> TOTAL[Total Monthly Cost<br/>$58,050,000]
    REPLICA_COMPUTE --> TOTAL
    STORAGE --> TOTAL
    NETWORK --> TOTAL
    CACHE --> TOTAL
    MONITORING --> TOTAL
    SUPPORT --> TOTAL

    classDef costStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef totalStyle fill:#CC0000,stroke:#990000,color:#fff

    class PRIMARY_COMPUTE,REPLICA_COMPUTE,STORAGE,NETWORK,CACHE,MONITORING,SUPPORT costStyle
    class TOTAL totalStyle
```

### 2. Performance ROI Analysis
- **Cost per Query**: $0.0000019 per query
- **Cost per User**: $1.85 per monthly active user
- **Infrastructure vs Revenue**: 12% of Facebook's total revenue
- **Cache ROI**: TAO cache saves $15M monthly in database costs

### 3. Alternative Database Considerations
- **PostgreSQL**: 30% lower cost, limited horizontal scaling
- **NoSQL Solutions**: 40% lower cost, consistency trade-offs
- **Cloud MySQL**: 200% higher cost, reduced operational overhead
- **NewSQL**: 60% higher cost, better consistency guarantees

## Real Production Configurations

### MySQL Configuration (my.cnf)
```ini
[mysqld]
# Basic Configuration
port = 3306
socket = /var/lib/mysql/mysql.sock
user = mysql
basedir = /usr
datadir = /data/mysql
tmpdir = /tmp

# InnoDB Configuration
default-storage-engine = InnoDB
innodb_buffer_pool_size = 768G
innodb_buffer_pool_instances = 64
innodb_log_file_size = 128G
innodb_log_files_in_group = 2
innodb_log_buffer_size = 256M
innodb_flush_log_at_trx_commit = 2
innodb_flush_method = O_DIRECT
innodb_file_per_table = 1
innodb_io_capacity = 20000
innodb_io_capacity_max = 40000
innodb_read_io_threads = 32
innodb_write_io_threads = 32
innodb_thread_concurrency = 0
innodb_adaptive_hash_index = ON
innodb_change_buffering = all
innodb_old_blocks_time = 1000

# Query Cache
query_cache_type = 0  # Disabled for high concurrency
query_cache_size = 0

# Connection Configuration
max_connections = 8000
max_connect_errors = 100000
connect_timeout = 10
wait_timeout = 600
interactive_timeout = 600

# Buffer Configuration
sort_buffer_size = 32M
join_buffer_size = 32M
read_buffer_size = 8M
read_rnd_buffer_size = 16M
key_buffer_size = 512M
table_open_cache = 65536
table_definition_cache = 65536

# Binary Logging
log-bin = /data/mysql/binlog/mysql-bin
binlog_format = ROW
expire_logs_days = 7
max_binlog_size = 1G
sync_binlog = 0  # Performance optimization

# Replication
server-id = 1
gtid_mode = ON
enforce_gtid_consistency = ON
log_slave_updates = ON
slave_parallel_workers = 32
slave_parallel_type = LOGICAL_CLOCK

# Performance Schema
performance_schema = ON
performance_schema_max_table_instances = 40000
performance_schema_max_sql_text_length = 4096
```

### Schema Design Example
```sql
-- Facebook User Profile Table (Optimized)
CREATE TABLE user_profiles (
    user_id BIGINT UNSIGNED NOT NULL,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    birth_date DATE,
    gender ENUM('M', 'F', 'O'),
    location_id INT UNSIGNED,
    profile_picture_url VARCHAR(500),
    bio TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    
    PRIMARY KEY (user_id),
    UNIQUE KEY idx_username (username),
    UNIQUE KEY idx_email (email),
    KEY idx_location_active (location_id, is_active),
    KEY idx_created_at (created_at)
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci
  ROW_FORMAT=COMPRESSED
  KEY_BLOCK_SIZE=8;

-- Facebook Social Graph (Friendship) Table
CREATE TABLE friendships (
    user_id BIGINT UNSIGNED NOT NULL,
    friend_id BIGINT UNSIGNED NOT NULL,
    status ENUM('pending', 'accepted', 'blocked') NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    PRIMARY KEY (user_id, friend_id),
    KEY idx_friend_user (friend_id, user_id),
    KEY idx_user_status (user_id, status),
    KEY idx_friend_status (friend_id, status)
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci
  PARTITION BY HASH(user_id)
  PARTITIONS 1024;
```

## Monitoring and Profiling Setup

### 1. Key Performance Indicators
```mermaid
graph TB
    subgraph Metrics[MySQL Performance Dashboard]
        QPS[Queries Per Second<br/>Current: 1.1M<br/>Target: <1.5M<br/>Alert: >1.3M]

        LATENCY[Query Latency<br/>p99: 4.8ms<br/>Target: <10ms<br/>Alert: >15ms]

        CPU[CPU Utilization<br/>Current: 65%<br/>Target: <80%<br/>Alert: >85%]

        BUFFER[Buffer Pool Hit<br/>Current: 99.8%<br/>Target: >99%<br/>Alert: <98%]

        REPL_LAG[Replication Lag<br/>Current: 50ms<br/>Target: <100ms<br/>Alert: >500ms]

        CONNECTIONS[Active Connections<br/>Current: 6.5K<br/>Target: <7.5K<br/>Alert: >7.8K]

        DISK[Disk Utilization<br/>Current: 70%<br/>Target: <80%<br/>Alert: >85%]

        SLOW_QUERIES[Slow Queries<br/>Current: 0.1%<br/>Target: <0.5%<br/>Alert: >1%]
    end

    subgraph Health[Database Health Monitoring]
        MASTER[Master Status<br/>Read/write status<br/>Failover readiness]

        SLAVES[Slave Status<br/>Replication health<br/>Lag monitoring]

        DEADLOCKS[Deadlock Rate<br/>Lock contention<br/>Transaction conflicts]
    end

    classDef metricStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef healthStyle fill:#FF8800,stroke:#CC6600,color:#fff

    class QPS,LATENCY,CPU,BUFFER,REPL_LAG,CONNECTIONS,DISK,SLOW_QUERIES metricStyle
    class MASTER,SLAVES,DEADLOCKS healthStyle
```

### 2. Performance Testing Framework
```python
# Facebook MySQL Performance Testing
import mysql.connector
import threading
import time
import random
from datetime import datetime

class FacebookMySQLLoadTest:
    def __init__(self):
        self.config = {
            'host': 'mysql-master.facebook.internal',
            'port': 3306,
            'user': 'test_user',
            'password': 'test_pass',
            'database': 'facebook',
            'charset': 'utf8mb4',
            'use_unicode': True,
            'autocommit': True
        }

    def simulate_user_queries(self):
        """Simulate typical Facebook user query workload"""
        conn = mysql.connector.connect(**self.config)
        cursor = conn.cursor(prepared=True)

        # Prepared statements for common queries
        profile_query = "SELECT * FROM user_profiles WHERE user_id = ?"
        friends_query = "SELECT friend_id FROM friendships WHERE user_id = ? AND status = 'accepted'"
        timeline_query = "SELECT * FROM posts WHERE user_id IN (SELECT friend_id FROM friendships WHERE user_id = ? AND status = 'accepted') ORDER BY created_at DESC LIMIT 50"

        for _ in range(10000):
            user_id = random.randint(1, 3000000000)  # 3B users
            query_type = random.choice(['profile', 'friends', 'timeline'])
            
            start_time = time.time()
            
            if query_type == 'profile':
                cursor.execute(profile_query, (user_id,))
                results = cursor.fetchall()
            elif query_type == 'friends':
                cursor.execute(friends_query, (user_id,))
                results = cursor.fetchall()
            else:  # timeline
                cursor.execute(timeline_query, (user_id,))
                results = cursor.fetchall()
            
            latency = time.time() - start_time
            print(f"{query_type} query latency: {latency:.3f}s")

        cursor.close()
        conn.close()

    def simulate_write_operations(self):
        """Simulate write-heavy operations"""
        conn = mysql.connector.connect(**self.config)
        cursor = conn.cursor(prepared=True)

        insert_post = "INSERT INTO posts (user_id, content, created_at) VALUES (?, ?, ?)"
        update_profile = "UPDATE user_profiles SET updated_at = ? WHERE user_id = ?"
        insert_friendship = "INSERT IGNORE INTO friendships (user_id, friend_id, status) VALUES (?, ?, 'pending')"

        for _ in range(5000):
            user_id = random.randint(1, 3000000000)
            operation = random.choice(['post', 'update', 'friend_request'])
            
            start_time = time.time()
            
            if operation == 'post':
                cursor.execute(insert_post, (user_id, f"Test post {random.randint(1, 1000000)}", datetime.now()))
            elif operation == 'update':
                cursor.execute(update_profile, (datetime.now(), user_id))
            else:  # friend_request
                friend_id = random.randint(1, 3000000000)
                cursor.execute(insert_friendship, (user_id, friend_id))
            
            latency = time.time() - start_time
            print(f"{operation} latency: {latency:.3f}s")

        cursor.close()
        conn.close()

# Run comprehensive load test
def run_facebook_load_test():
    test = FacebookMySQLLoadTest()
    
    # Create multiple threads simulating concurrent users
    threads = []
    for i in range(1000):  # 1000 concurrent connections
        if i % 5 == 0:  # 20% writes, 80% reads
            thread = threading.Thread(target=test.simulate_write_operations)
        else:
            thread = threading.Thread(target=test.simulate_user_queries)
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()
```

## Key Performance Insights

### 1. Critical Success Factors
- **Read Replica Scaling**: 10:1 read/write ratio enables massive read scaling
- **TAO Cache Layer**: 99.8% cache hit ratio reduces database load by 95%
- **Schema Optimization**: Denormalized, query-specific tables eliminate joins
- **Hardware Selection**: NVMe storage and large memory essential for performance
- **Connection Pooling**: Custom proxy layer enables 50K+ concurrent connections

### 2. Lessons Learned
- **3K QPS Limit**: Single MySQL instance peaks at ~3,000 QPS
- **Buffer Pool Critical**: 99%+ buffer pool hit ratio essential for performance
- **Replication Scaling**: 10 read replicas optimal per primary
- **Schema Design**: Query-optimized schemas more important than normalization
- **Monitoring Essential**: Real-time performance monitoring prevents cascading failures

### 3. Anti-patterns Avoided
- **Complex Joins**: Denormalized schemas eliminate expensive join operations
- **Query Cache**: Disabled query cache for high-concurrency workloads
- **Small Buffer Pool**: Large buffer pool (768GB) prevents I/O bottlenecks
- **Synchronous Replication**: Semi-sync only for critical writes
- **Default Configuration**: Heavy tuning required for 1M QPS performance

### 4. Future Optimization Strategies
- **MySQL 8.0 Features**: Hash joins and improved optimizer
- **Storage Engines**: Evaluation of RocksDB for write-heavy workloads
- **Sharding Automation**: Automated shard management and rebalancing
- **Machine Learning**: Query performance prediction and optimization
- **Hardware Evolution**: Persistent memory and ARM processor adoption

This performance profile demonstrates how Facebook achieves exceptional MySQL performance at unprecedented scale through careful architecture design, aggressive caching, and operational excellence. Their 1M QPS deployment serves as the definitive blueprint for building high-performance relational database systems that can support billions of users with complex social graph operations.