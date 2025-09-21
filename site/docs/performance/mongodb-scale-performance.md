# MongoDB at Scale: Uber's High-Performance Optimization Profile

## Overview

Uber operates one of the world's largest MongoDB deployments, managing petabytes of real-time location data, trip information, and user analytics. Their MongoDB infrastructure handles millions of writes per second with strict consistency requirements while serving global ride-sharing operations across 70+ countries.

## Architecture for Performance

```mermaid
graph TB
    subgraph EdgePlane["Edge Plane"]
        LB[Uber Load Balancer<br/>Envoy Proxy<br/>99.99% availability]
        CDN[Uber CDN<br/>Edge caching<br/>Location-aware routing]
    end

    subgraph ServicePlane["Service Plane"]
        API[Uber APIs<br/>Go microservices<br/>5000+ instances]
        ROUTER[MongoDB Router<br/>mongos processes<br/>Query routing layer]
    end

    subgraph StatePlane["State Plane"]
        CONFIG[Config Servers<br/>3x r6g.xlarge<br/>Metadata storage]
        SHARD1[Shard 1<br/>3x r6g.16xlarge<br/>Primary + 2 secondaries]
        SHARD2[Shard 2<br/>3x r6g.16xlarge<br/>Primary + 2 secondaries]
        SHARDN[Shard N<br/>500 total shards<br/>1500 replica set members]
    end

    subgraph ControlPlane["Control Plane"]
        MON[Monitoring<br/>MongoDB Ops Manager<br/>Real-time metrics]
        BACKUP[Backup System<br/>Continuous backup<br/>Point-in-time recovery]
    end

    LB --> API
    CDN --> LB
    API --> ROUTER
    ROUTER --> CONFIG
    ROUTER --> SHARD1
    ROUTER --> SHARD2
    ROUTER --> SHARDN

    MON --> CONFIG
    MON --> SHARD1
    BACKUP --> SHARD1

    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class LB,CDN edgeStyle
    class API,ROUTER serviceStyle
    class CONFIG,SHARD1,SHARD2,SHARDN stateStyle
    class MON,BACKUP controlStyle
```

## Performance Metrics and Benchmarks

### Cluster Overview
- **Total Data Size**: 2.5 petabytes across all shards
- **Write Operations**: 3.5M writes per second peak
- **Read Operations**: 8M reads per second peak
- **Shard Count**: 500 shards (1,500 replica set members)
- **Instance Type**: r6g.16xlarge (64 vCPUs, 512GB RAM)
- **Storage per Shard**: 5TB NVMe SSD
- **Replication Factor**: 3 (Primary + 2 Secondaries)

### Operation Performance Profile
```mermaid
graph LR
    subgraph OperationLatency[MongoDB Operation Latency - p95]
        INSERT[Insert: 2.5ms<br/>Single document<br/>Write concern majority]
        UPDATE[Update: 3.2ms<br/>Indexed field update<br/>Find and modify]
        FIND[Find: 1.8ms<br/>Indexed query<br/>Single document]
        AGG[Aggregation: 45ms<br/>Complex pipeline<br/>Multi-stage processing]
        INDEX[Index Scan: 12ms<br/>Range query<br/>Compound index]
    end

    subgraph Percentiles[Response Time Distribution]
        P50[p50: 1.2ms]
        P95[p95: 4.8ms]
        P99[p99: 12.5ms]
        P999[p999: 45ms]
        P9999[p9999: 180ms]
    end

    subgraph Throughput[Operations per Second]
        WRITES[Writes: 3.5M/sec<br/>Peak traffic<br/>Global operations]
        READS[Reads: 8M/sec<br/>Read preference secondary<br/>High concurrency]
        BULK[Bulk Ops: 250K/sec<br/>Batch inserts<br/>Optimized batching]
    end

    classDef metricStyle fill:#F59E0B,stroke:#D97706,color:#fff
    class INSERT,UPDATE,FIND,AGG,INDEX,P50,P95,P99,P999,P9999,WRITES,READS,BULK metricStyle
```

### Shard-Level Performance
- **Documents per Shard**: 50M-100M documents average
- **Storage per Shard**: 5TB (3.5TB data + 1.5TB indexes)
- **Connections per Shard**: 2,000 active connections
- **CPU Utilization**: 65% average, 85% peak
- **Memory Utilization**: 450GB working set per shard
- **Network Throughput**: 20 Gbps per shard cluster

## Optimization Techniques Used

### 1. Sharding Strategy
```mermaid
graph TB
    subgraph ShardingStrategy[Uber's MongoDB Sharding Strategy]
        GEO[Geographic Sharding<br/>Location-based routing<br/>Regional data isolation]
        TIME[Time-based Sharding<br/>Trip data by date<br/>Automatic archival]
        HASH[Hash-based Sharding<br/>User data distribution<br/>Even load balancing]
        COMPOUND[Compound Shard Keys<br/>Multi-field routing<br/>Query optimization]
    end

    subgraph ShardKeyDesign[Shard Key Examples]
        TRIP[Trip Data<br/>{'city_id': 1, 'created_at': 1}<br/>Geographic + temporal]
        USER[User Data<br/>{'user_id': 'hashed'}<br/>Even distribution]
        DRIVER[Driver Data<br/>{'region': 1, 'driver_id': 1}<br/>Regional optimization]
        PAYMENT[Payment Data<br/>{'payment_method': 1, 'timestamp': 1}<br/>Type + time based]
    end

    subgraph Benefits[Sharding Benefits]
        LOCALITY[Data Locality<br/>Reduced cross-shard queries<br/>90% single-shard operations]
        SCALE[Linear Scaling<br/>Add shards for capacity<br/>No single points of failure]
        ISOLATION[Fault Isolation<br/>Shard failures contained<br/>Regional disaster recovery]
    end

    GEO --> TRIP
    TIME --> PAYMENT
    HASH --> USER
    COMPOUND --> DRIVER

    classDef strategyStyle fill:#10B981,stroke:#059669,color:#fff
    classDef keyStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef benefitStyle fill:#3B82F6,stroke:#2563EB,color:#fff

    class GEO,TIME,HASH,COMPOUND strategyStyle
    class TRIP,USER,DRIVER,PAYMENT keyStyle
    class LOCALITY,SCALE,ISOLATION benefitStyle
```

### 2. Index Strategy
- **Compound Indexes**: Optimized for query patterns (location + time)
- **Partial Indexes**: Filter on active trips only (60% storage savings)
- **Text Indexes**: Sparse indexes for search functionality
- **Geospatial Indexes**: 2dsphere indexes for location queries
- **TTL Indexes**: Automatic cleanup of temporary data

### 3. Write Optimization
```yaml
# MongoDB Write Configuration
writeConcern:
  w: "majority"           # Ensure data durability
  j: true                 # Journal sync for consistency
  wtimeout: 1000         # 1 second write timeout

readConcern:
  level: "majority"       # Read majority committed data

readPreference:
  mode: "secondaryPreferred"  # Distribute read load
  maxStalenessSeconds: 90     # Allow 90s replication lag
```

### 4. Memory and Storage Optimization
- **WiredTiger Cache**: 256GB cache per node (50% of total RAM)
- **Compression**: zstd compression (40% storage reduction)
- **Journal Configuration**: 128MB journal files with group commits
- **Connection Pooling**: 2,000 connections per mongos router

## Bottleneck Analysis

### 1. Write Performance Bottlenecks
```mermaid
graph TB
    subgraph WriteBottlenecks[Write Performance Analysis]
        JOURNAL[Journal Sync<br/>25% write latency<br/>Disk I/O dependency]
        REPLICATION[Replication Lag<br/>15% write latency<br/>Network + disk I/O]
        LOCKING[Document Locking<br/>10% write latency<br/>Concurrent updates]
        INDEX[Index Updates<br/>35% write latency<br/>Multiple index maintenance]
        VALIDATION[Schema Validation<br/>15% write latency<br/>Document validation rules]
    end

    subgraph Solutions[Write Optimization Solutions]
        NVME[NVMe Storage<br/>Ultra-low latency journal<br/>80% latency reduction]
        BATCH[Bulk Operations<br/>Batch inserts/updates<br/>10x throughput gain]
        PARTIAL[Partial Indexes<br/>Reduced index overhead<br/>40% faster writes]
        ASYNC[Async Replication<br/>Pipeline replication<br/>50% lag reduction]
    end

    JOURNAL --> NVME
    INDEX --> PARTIAL
    INDEX --> BATCH
    REPLICATION --> ASYNC

    classDef bottleneckStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef solutionStyle fill:#10B981,stroke:#059669,color:#fff

    class JOURNAL,REPLICATION,LOCKING,INDEX,VALIDATION bottleneckStyle
    class NVME,BATCH,PARTIAL,ASYNC solutionStyle
```

### 2. Read Performance Bottlenecks
- **Index Scans**: 60% of queries require index optimization
- **Cross-Shard Queries**: 10% of queries span multiple shards
- **Aggregation Pipelines**: Complex aggregations consume 40% CPU
- **Memory Pressure**: Working set exceeds cache during peak traffic
- **Network Latency**: Cross-region reads add 50ms latency

### 3. Query Pattern Analysis
- **Point Queries**: 70% (single document lookups)
- **Range Queries**: 20% (time-based or location-based ranges)
- **Aggregation Queries**: 8% (analytics and reporting)
- **Text Search**: 2% (driver/rider name searches)

## Scaling Limits Discovered

### 1. Single Shard Limits
```mermaid
graph LR
    subgraph ShardScaling[Single Shard Scaling Analysis]
        S1[10M Docs<br/>Latency: 1.5ms<br/>Storage: 500GB<br/>Optimal Performance]
        S2[50M Docs<br/>Latency: 2.8ms<br/>Storage: 2.5TB<br/>Good Performance]
        S3[100M Docs<br/>Latency: 5.2ms<br/>Storage: 5TB<br/>Acceptable]
        S4[200M Docs<br/>Latency: 12ms<br/>Storage: 10TB<br/>Performance Degrades]
        S5[300M+ Docs<br/>Index Size > RAM<br/>Disk I/O bottleneck<br/>Needs resharding]
    end

    S1 --> S2 --> S3 --> S4 --> S5

    subgraph Solution[Scaling Solution]
        RESHARD[Automatic Resharding<br/>Split at 100M docs<br/>Maintained performance<br/>Zero downtime]
    end

    S5 --> RESHARD

    classDef scaleStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef solutionStyle fill:#10B981,stroke:#059669,color:#fff

    class S1,S2,S3,S4,S5 scaleStyle
    class RESHARD solutionStyle
```

### 2. Cluster Scaling Challenges
- **Balancer Overhead**: Chunk migration impacts performance during scaling
- **Config Server Limits**: Metadata queries become bottleneck beyond 1000 shards
- **mongos Router Limits**: Single router handles max 10K connections
- **Network Coordination**: Gossip protocol overhead increases with cluster size

### 3. Hardware Limits Reached
- **Memory Scaling**: 512GB per node optimal for MongoDB overhead
- **CPU Saturation**: 64 vCPU optimal for concurrent operations
- **Storage I/O**: NVMe required for journal and index performance
- **Network Bandwidth**: 25 Gbps per node during peak replication

## Cost vs Performance Trade-offs

### 1. Infrastructure Costs (Monthly)
```mermaid
graph TB
    subgraph CostBreakdown[Monthly Infrastructure Cost: $4,800,000]
        COMPUTE[Compute Instances<br/>1500 × r6g.16xlarge<br/>$2,800/month each<br/>$4,200,000 total]

        STORAGE[NVMe Storage<br/>7.5PB total @ $0.10/GB<br/>$750,000/month]

        NETWORK[Data Transfer<br/>10PB/month @ $0.09/GB<br/>$900,000/month]

        BACKUP[Backup Storage<br/>2.5PB @ $0.023/GB<br/>$57,500/month]

        MONITORING[MongoDB Ops Manager<br/>Enterprise licensing<br/>$125,000/month]

        SUPPORT[Enterprise Support<br/>24/7 MongoDB support<br/>$250,000/month]

        TEAM[Engineering Team<br/>25 database engineers<br/>$2,916,500/month]
    end

    COMPUTE --> TOTAL[Total Monthly Cost<br/>$4,800,000]
    STORAGE --> TOTAL
    NETWORK --> TOTAL
    BACKUP --> TOTAL
    MONITORING --> TOTAL
    SUPPORT --> TOTAL
    TEAM --> TOTAL

    classDef costStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef totalStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class COMPUTE,STORAGE,NETWORK,BACKUP,MONITORING,SUPPORT,TEAM costStyle
    class TOTAL totalStyle
```

### 2. Performance ROI Analysis
- **Cost per Operation**: $0.0000014 per read/write operation
- **Cost per Trip**: $0.025 per completed trip
- **Infrastructure vs Revenue**: 8% of total Uber revenue
- **Performance Investment**: 25% cost increase for 3x throughput improvement

### 3. Alternative Database Considerations
- **PostgreSQL**: 40% lower cost, limited horizontal scaling
- **Cassandra**: 20% lower cost, eventual consistency trade-offs
- **DynamoDB**: 35% higher cost, vendor lock-in concerns
- **CockroachDB**: 45% higher cost, stronger consistency guarantees

## Real Production Configurations

### MongoDB Configuration (mongod.conf)
```yaml
# Storage Configuration
storage:
  dbPath: /data/mongodb
  journal:
    enabled: true
    commitIntervalMs: 100
  wiredTiger:
    engineConfig:
      cacheSizeGB: 256
      journalCompressor: zstd
      directoryForIndexes: true
    collectionConfig:
      blockCompressor: zstd
    indexConfig:
      prefixCompression: true

# Replication Configuration
replication:
  replSetName: "uber-shard-01"
  enableMajorityReadConcern: true

# Sharding Configuration
sharding:
  clusterRole: shardsvr

# Network Configuration
net:
  port: 27017
  bindIp: 0.0.0.0
  maxIncomingConnections: 2000

# Operation Profiling
operationProfiling:
  mode: slowOp
  slowOpThresholdMs: 100
  slowOpSampleRate: 0.1

# Security Configuration
security:
  authorization: enabled
  keyFile: /etc/mongodb/keyfile

# Process Management
processManagement:
  fork: true
  pidFilePath: /var/run/mongodb/mongod.pid

# System Log
systemLog:
  destination: file
  path: /var/log/mongodb/mongod.log
  logAppend: true
  logRotate: reopen
```

### Shard Key Design Examples
```javascript
// Trip data shard key - Geographic + Temporal
db.trips.createIndex({"city_id": 1, "created_at": 1})
sh.shardCollection("uber.trips", {"city_id": 1, "created_at": 1})

// User data shard key - Hashed for even distribution
db.users.createIndex({"user_id": "hashed"})
sh.shardCollection("uber.users", {"user_id": "hashed"})

// Driver location shard key - Geographic clustering
db.driver_locations.createIndex({"region": 1, "driver_id": 1})
sh.shardCollection("uber.driver_locations", {"region": 1, "driver_id": 1})

// Payment data shard key - Method + Time
db.payments.createIndex({"payment_method": 1, "timestamp": 1})
sh.shardCollection("uber.payments", {"payment_method": 1, "timestamp": 1})
```

## Monitoring and Profiling Setup

### 1. Key Performance Indicators
```mermaid
graph TB
    subgraph Metrics[MongoDB Performance Dashboard]
        OPS[Operations/sec<br/>Current: 11.5M<br/>Target: <15M<br/>Alert: >13M]

        LATENCY[Operation Latency<br/>p95: 4.8ms<br/>Target: <10ms<br/>Alert: >15ms]

        MEMORY[WiredTiger Cache<br/>Current: 85%<br/>Target: <90%<br/>Alert: >95%]

        CONNECTIONS[Active Connections<br/>Current: 1.2M<br/>Target: <1.5M<br/>Alert: >1.8M]

        REPLICATION[Replication Lag<br/>Current: 45ms<br/>Target: <100ms<br/>Alert: >500ms]

        DISK[Disk Utilization<br/>Current: 70%<br/>Target: <80%<br/>Alert: >85%]

        QUEUE[Global Lock Queue<br/>Current: 5<br/>Target: <20<br/>Alert: >50]

        CURSORS[Open Cursors<br/>Current: 25K<br/>Target: <50K<br/>Alert: >75K]
    end

    subgraph Health[Cluster Health Monitoring]
        SHARDS[Shard Status<br/>Active shards<br/>Balancer state]

        CHUNKS[Chunk Distribution<br/>Balanced chunks<br/>Migration status]

        CONFIG[Config Servers<br/>Metadata consistency<br/>Election status]
    end

    classDef metricStyle fill:#10B981,stroke:#059669,color:#fff
    classDef healthStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class OPS,LATENCY,MEMORY,CONNECTIONS,REPLICATION,DISK,QUEUE,CURSORS metricStyle
    class SHARDS,CHUNKS,CONFIG healthStyle
```

### 2. Performance Testing Framework
```python
# Uber MongoDB Performance Testing
import pymongo
import threading
import time
import random
from datetime import datetime

class UberMongoLoadTest:
    def __init__(self):
        self.client = pymongo.MongoClient('mongodb://mongos.uber.internal:27017/')
        self.db = self.client.uber

    def simulate_trip_creation(self):
        """Simulate trip creation workload"""
        cities = ['san_francisco', 'new_york', 'london', 'mumbai']

        for _ in range(10000):
            trip_doc = {
                'trip_id': f"trip_{random.randint(1, 10000000)}",
                'city_id': random.choice(cities),
                'user_id': f"user_{random.randint(1, 1000000)}",
                'driver_id': f"driver_{random.randint(1, 100000)}",
                'created_at': datetime.utcnow(),
                'status': 'requested',
                'pickup_location': {
                    'type': 'Point',
                    'coordinates': [
                        random.uniform(-122.5, -122.3),  # SF longitude
                        random.uniform(37.7, 37.8)       # SF latitude
                    ]
                }
            }

            start_time = time.time()
            self.db.trips.insert_one(trip_doc)
            latency = time.time() - start_time
            print(f"Insert latency: {latency:.3f}s")

    def simulate_location_updates(self):
        """Simulate driver location updates"""
        for _ in range(50000):
            driver_id = f"driver_{random.randint(1, 100000)}"

            start_time = time.time()
            self.db.driver_locations.update_one(
                {'driver_id': driver_id},
                {
                    '$set': {
                        'location': {
                            'type': 'Point',
                            'coordinates': [
                                random.uniform(-122.5, -122.3),
                                random.uniform(37.7, 37.8)
                            ]
                        },
                        'updated_at': datetime.utcnow()
                    }
                },
                upsert=True
            )
            latency = time.time() - start_time
            print(f"Update latency: {latency:.3f}s")

# Run load test with multiple threads
def run_load_test():
    test = UberMongoLoadTest()

    # Create multiple threads for concurrent testing
    threads = []
    for i in range(100):
        if i % 2 == 0:
            thread = threading.Thread(target=test.simulate_trip_creation)
        else:
            thread = threading.Thread(target=test.simulate_location_updates)
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()
```

### 3. Profiling and Monitoring Tools
- **MongoDB Profiler**: Captures slow operations >100ms
- **Ops Manager**: Real-time cluster monitoring and alerting
- **Custom Metrics**: Application-level performance tracking
- **Network Monitoring**: Cross-shard query analysis
- **Resource Monitoring**: CPU, memory, and disk utilization

## Key Performance Insights

### 1. Critical Success Factors
- **Shard Key Design**: Geographic + temporal sharding eliminates hotspots
- **Index Strategy**: Compound indexes reduce query execution time by 80%
- **Hardware Selection**: NVMe storage essential for write performance
- **Connection Pooling**: Proper pooling reduces connection overhead by 90%
- **Read Preference**: Secondary reads distribute load effectively

### 2. Lessons Learned
- **100M Document Limit**: Shards perform optimally under 100M documents
- **Memory Requirements**: Working set must fit in WiredTiger cache
- **Write Concern**: Majority write concern essential for consistency
- **Balancer Timing**: Schedule chunk migrations during low traffic
- **Query Patterns**: 90% single-shard queries optimal for performance

### 3. Anti-patterns Avoided
- **Poor Shard Keys**: Avoid monotonically increasing keys
- **Large Documents**: Keep documents under 16MB limit
- **Unbounded Arrays**: Limit array growth to prevent bloat
- **Cross-Shard Joins**: Minimize $lookup operations across shards
- **Unindexed Queries**: Ensure all queries use proper indexes

### 4. Future Optimization Strategies
- **MongoDB 6.0 Features**: Time-series collections for location data
- **Queryable Encryption**: Enhanced security for sensitive data
- **Auto-scaling**: Dynamic shard addition based on load
- **Global Clusters**: Multi-region deployment for disaster recovery
- **Change Streams**: Real-time data synchronization and analytics

This performance profile demonstrates how Uber achieves exceptional MongoDB performance at massive scale through careful shard key design, hardware optimization, and operational excellence. Their implementation serves as a blueprint for building globally distributed, high-performance MongoDB systems that can handle millions of operations per second with strict consistency requirements.