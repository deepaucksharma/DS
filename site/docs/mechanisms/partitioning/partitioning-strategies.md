# Partitioning Strategies: Production-Scale Data Distribution

## Overview

Data partitioning distributes large datasets across multiple nodes to achieve horizontal scalability, improved performance, and better resource utilization.

**Production Reality**: Instagram shards 400TB+ across 1000+ PostgreSQL databases, Discord partitions 12TB+ messages across Cassandra clusters, and Uber uses geo-partitioning for 15B+ trips across 1000+ cities. Each strategy optimizes for different access patterns and scale requirements.

## Production Architecture: Instagram Database Sharding (400TB+ dataset)

```mermaid
graph TB
    subgraph EDGE["Edge Plane - Request Routing"]
        CDN[Instagram CDN<br/>Global image serving<br/>Cache hit ratio: 95%]
        LB[Load Balancers<br/>Geographic routing<br/>100K+ RPS]
        PROXY[PgBouncer Proxy<br/>Connection pooling<br/>10K+ connections]
    end

    subgraph SERVICE["Service Plane - Sharding Logic"]
        SHARD_SVC[Sharding Service<br/>User ID → Shard mapping<br/>Consistent hashing]
        ROUTER[Database Router<br/>Query analysis<br/>Cross-shard aggregation]
        MIGRATOR[Shard Migration<br/>Live data movement<br/>Zero-downtime resharding]
    end

    subgraph STATE["State Plane - Sharded Databases"]
        SHARD_001[PostgreSQL Shard 001<br/>Users 0-99M<br/>400GB data, 50K QPS]
        SHARD_002[PostgreSQL Shard 002<br/>Users 100M-199M<br/>400GB data, 50K QPS]
        SHARD_003[PostgreSQL Shard 003<br/>Users 200M-299M<br/>400GB data, 50K QPS]
        SHARD_N[PostgreSQL Shard 1000<br/>Users 99.9B+<br/>400GB data, 50K QPS]
    end

    subgraph CONTROL["Control Plane - Management"]
        MONITOR[Shard Monitoring<br/>Per-shard metrics<br/>Hotspot detection]
        BALANCER[Load Balancer<br/>Automated resharding<br/>Capacity planning]
        BACKUP[Shard Backup<br/>Per-shard WAL-E<br/>Cross-shard consistency]
    end

    CDN -.->|"API requests"| LB
    LB -.->|"Database connections"| PROXY
    PROXY -.->|"Shard selection"| SHARD_SVC
    SHARD_SVC -.->|"Query routing"| ROUTER
    ROUTER -.->|"Data migration"| MIGRATOR

    ROUTER -.->|"User data queries"| SHARD_001
    ROUTER -.->|"User data queries"| SHARD_002
    ROUTER -.->|"User data queries"| SHARD_003
    ROUTER -.->|"User data queries"| SHARD_N
    MIGRATOR -.->|"Live migration"| SHARD_001
    MIGRATOR -.->|"Live migration"| SHARD_002

    SHARD_001 -.->|"Performance metrics"| MONITOR
    SHARD_002 -.->|"Performance metrics"| MONITOR
    SHARD_003 -.->|"Performance metrics"| MONITOR
    MONITOR -.->|"Rebalancing triggers"| BALANCER
    SHARD_001 -.->|"Backup data"| BACKUP
    SHARD_002 -.->|"Backup data"| BACKUP

    %% Production 4-plane colors
    classDef edge fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef service fill:#10B981,stroke:#059669,color:#fff
    classDef state fill:#F59E0B,stroke:#D97706,color:#fff
    classDef control fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class CDN,LB,PROXY edge
    class SHARD_SVC,ROUTER,MIGRATOR service
    class SHARD_001,SHARD_002,SHARD_003,SHARD_N state
    class MONITOR,BALANCER,BACKUP control
```

### Production Metrics: Instagram Sharding

| Metric | Value | Challenge | Solution |
|--------|-------|-----------|----------|
| **Total Data** | 400TB+ across 1000+ shards | Shard rebalancing | Live migration tools |
| **Queries/Second** | 50M+ reads, 5M+ writes | Hotspot detection | Automated resharding |
| **Shard Size** | 400GB average per shard | Uniform distribution | Consistent hashing |
| **Cross-Shard Queries** | < 1% of total queries | Query complexity | Denormalization |
| **Migration Time** | 2 hours per 400GB shard | Zero downtime | Read-write splitting |

## Production Architecture: Discord Message Partitioning (12TB+ messages)

```mermaid
graph TB
    subgraph EDGE["Edge Plane - Client Connections"]
        WEBSOCKET[WebSocket Gateway<br/>Real-time connections<br/>150M+ concurrent users]
        API[Discord API<br/>REST + WebSocket<br/>Rate limiting: 50/sec]
        CDN[CloudFlare CDN<br/>Static asset serving<br/>Global distribution]
    end

    subgraph SERVICE["Service Plane - Message Processing"]
        HASH_SVC[Consistent Hashing<br/>Channel ID → Partition<br/>Murmur3 hash function]
        MSG_SVC[Message Service<br/>Real-time processing<br/>1M+ messages/second]
        FANOUT[Message Fanout<br/>Subscriber notification<br/>Event streaming]
    end

    subgraph STATE["State Plane - Cassandra Clusters"]
        CASSANDRA_1[Cassandra Cluster 1<br/>Channels 0-199M<br/>3TB data, 100K ops/sec]
        CASSANDRA_2[Cassandra Cluster 2<br/>Channels 200M-399M<br/>3TB data, 100K ops/sec]
        CASSANDRA_3[Cassandra Cluster 3<br/>Channels 400M-599M<br/>3TB data, 100K ops/sec]
        CASSANDRA_N[Cassandra Cluster N<br/>Channels 800M+<br/>3TB data, 100K ops/sec]
    end

    subgraph CONTROL["Control Plane - Operations"]
        METRICS[Prometheus Metrics<br/>Per-partition monitoring<br/>Hotspot detection]
        ALERTING[PagerDuty Alerts<br/>Partition health<br/>Rebalancing triggers]
        COMPACTION[Cassandra Compaction<br/>Automated cleanup<br/>Storage optimization]
    end

    WEBSOCKET -.->|"New messages"| API
    API -.->|"Channel targeting"| HASH_SVC
    HASH_SVC -.->|"Partition routing"| MSG_SVC
    MSG_SVC -.->|"Real-time delivery"| FANOUT

    MSG_SVC -.->|"Write messages"| CASSANDRA_1
    MSG_SVC -.->|"Write messages"| CASSANDRA_2
    MSG_SVC -.->|"Write messages"| CASSANDRA_3
    MSG_SVC -.->|"Write messages"| CASSANDRA_N
    FANOUT -.->|"Read message history"| CASSANDRA_1
    FANOUT -.->|"Read message history"| CASSANDRA_2

    CASSANDRA_1 -.->|"Performance data"| METRICS
    CASSANDRA_2 -.->|"Performance data"| METRICS
    CASSANDRA_3 -.->|"Performance data"| METRICS
    METRICS -.->|"Health status"| ALERTING
    CASSANDRA_1 -.->|"Compaction jobs"| COMPACTION
    CASSANDRA_2 -.->|"Compaction jobs"| COMPACTION

    %% Production 4-plane colors
    classDef edge fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef service fill:#10B981,stroke:#059669,color:#fff
    classDef state fill:#F59E0B,stroke:#D97706,color:#fff
    classDef control fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class WEBSOCKET,API,CDN edge
    class HASH_SVC,MSG_SVC,FANOUT service
    class CASSANDRA_1,CASSANDRA_2,CASSANDRA_3,CASSANDRA_N state
    class METRICS,ALERTING,COMPACTION control
```

### Discord Partitioning Strategy

**Hash Function**: `partition = murmur3(channel_id) % num_partitions`

| Partition Strategy | Use Case | Scale | Performance |
|-------------------|----------|-------|-------------|
| **Channel-based hashing** | Message storage | 12TB+ across 4 clusters | 1M+ messages/sec |
| **Guild-based partitioning** | Server data | 19M+ servers | 100K+ ops/sec |
| **User-based sharding** | Profile data | 150M+ users | 50K+ queries/sec |
| **Time-based bucketing** | Analytics data | 5 years retention | 1B+ events/day |

## Production Example: Uber Geo-Partitioning (1000+ cities)

```mermaid
graph TB
    subgraph EDGE["Edge Plane - Regional Gateways"]
        MOBILE[Uber Mobile Apps<br/>Driver + Rider apps<br/>100M+ active users]
        REGIONAL_LB[Regional Load Balancers<br/>Geographic routing<br/>City-based distribution]
        API_GW[API Gateway<br/>Rate limiting + auth<br/>1M+ requests/minute]
    end

    subgraph SERVICE["Service Plane - City Services"]
        CITY_ROUTER[City Router<br/>lat/lng → city mapping<br/>H3 geospatial indexing]
        TRIP_SVC[Trip Service<br/>Real-time matching<br/>15 million trips/day]
        PRICING_SVC[Pricing Service<br/>City-specific algorithms<br/>Surge pricing]
    end

    subgraph STATE["State Plane - City Databases"]
        NYC_DB[New York Database<br/>PostgreSQL cluster<br/>5M+ rides/month]
        SF_DB[San Francisco Database<br/>PostgreSQL cluster<br/>3M+ rides/month]
        LONDON_DB[London Database<br/>PostgreSQL cluster<br/>2M+ rides/month]
        CITY_N_DB[City N Database<br/>1000+ cities total<br/>100K+ rides/month each]
    end

    subgraph CONTROL["Control Plane - Global Operations"]
        MONITORING[Global Monitoring<br/>Per-city metrics<br/>Cross-city analytics]
        DEPLOYMENT[Blue-Green Deploy<br/>City-by-city rollout<br/>Risk mitigation]
        BACKUP[Cross-Region Backup<br/>Disaster recovery<br/>City failover]
    end

    MOBILE -.->|"Location-based"| REGIONAL_LB
    REGIONAL_LB -.->|"Route to nearest"| API_GW
    API_GW -.->|"Geo-coordinate"| CITY_ROUTER
    CITY_ROUTER -.->|"City identification"| TRIP_SVC
    TRIP_SVC -.->|"Local pricing"| PRICING_SVC

    CITY_ROUTER -.->|"NYC trips"| NYC_DB
    CITY_ROUTER -.->|"SF trips"| SF_DB
    CITY_ROUTER -.->|"London trips"| LONDON_DB
    CITY_ROUTER -.->|"Other cities"| CITY_N_DB
    PRICING_SVC -.->|"Surge calculations"| NYC_DB
    PRICING_SVC -.->|"Surge calculations"| SF_DB

    NYC_DB -.->|"City metrics"| MONITORING
    SF_DB -.->|"City metrics"| MONITORING
    LONDON_DB -.->|"City metrics"| MONITORING
    MONITORING -.->|"Deploy coordination"| DEPLOYMENT
    NYC_DB -.->|"Backup data"| BACKUP
    SF_DB -.->|"Backup data"| BACKUP

    %% Production 4-plane colors
    classDef edge fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef service fill:#10B981,stroke:#059669,color:#fff
    classDef state fill:#F59E0B,stroke:#D97706,color:#fff
    classDef control fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class MOBILE,REGIONAL_LB,API_GW edge
    class CITY_ROUTER,TRIP_SVC,PRICING_SVC service
    class NYC_DB,SF_DB,LONDON_DB,CITY_N_DB state
    class MONITORING,DEPLOYMENT,BACKUP control
```

### Uber Geo-Partitioning Benefits

| Benefit | Implementation | Production Impact |
|---------|---------------|-------------------|
| **Data Locality** | Trips stored in city databases | 10ms vs 200ms query latency |
| **Regulatory Compliance** | EU data stays in EU | GDPR compliance, local regulations |
| **Fault Isolation** | City outages don't affect others | 99.9% vs 99.5% availability |
| **Scaling Independence** | Cities scale based on demand | 50x traffic variation handled |
| **Operational Simplicity** | City-specific deployments | Zero-downtime updates |

```python
# Uber's H3-based city partitioning (simplified)
import h3
from typing import Dict, Tuple

class UberGeoPartitioner:
    def __init__(self):
        # H3 resolution 5 covers city-sized areas
        self.city_mappings = {
            '852a100bfffffff': 'nyc_db',     # NYC hexagon
            '85283087fffffff': 'sf_db',      # SF hexagon
            '8531000bfffffff': 'london_db',  # London hexagon
        }

    def get_city_database(self, lat: float, lng: float) -> str:
        # Convert lat/lng to H3 hex at resolution 5
        h3_hex = h3.geo_to_h3(lat, lng, 5)

        # Map to city database
        return self.city_mappings.get(h3_hex, 'default_db')

    def get_partition(self, lat: float, lng: float) -> Dict:
        city_db = self.get_city_database(lat, lng)
        return {
            'database': city_db,
            'hex_id': h3.geo_to_h3(lat, lng, 5),
            'data_center': self.get_data_center(city_db)
        }
```

    def get_partition(self, key: str) -> int:
        """Calculate partition for a given key"""
        # Use MD5 hash for demonstration (use stronger hash in production)
        hash_value = hashlib.md5(key.encode()).hexdigest()
        return int(hash_value, 16) % self.num_partitions

    def insert(self, key: str, value: Any):
        """Insert key-value pair into appropriate partition"""
        partition_id = self.get_partition(key)
        self.partitions[partition_id].append((key, value))

    def get(self, key: str) -> Any:
        """Retrieve value by key"""
        partition_id = self.get_partition(key)
        for stored_key, value in self.partitions[partition_id]:
            if stored_key == key:
                return value
        return None

    def get_partition_stats(self) -> Dict[int, int]:
        """Get statistics about partition sizes"""
        return {i: len(partition) for i, partition in enumerate(self.partitions)}

# Example usage
partitioner = HashPartitioner(4)

# Insert user data
users = [
    ("john@example.com", {"name": "John", "age": 30}),
    ("alice@example.com", {"name": "Alice", "age": 25}),
    ("bob@example.com", {"name": "Bob", "age": 35}),
    ("carol@example.com", {"name": "Carol", "age": 28})
]

for email, user_data in users:
    partitioner.insert(email, user_data)

print("Partition distribution:", partitioner.get_partition_stats())
# Output: {0: 1, 1: 1, 2: 1, 3: 1}  # Evenly distributed
```

## Range Partitioning

### Range-Based Distribution

```mermaid
graph TB
    subgraph "Range Partitioning by Timestamp"
        subgraph "Time Ranges"
            RANGE1[Partition 1<br/>2024-01-01 to 2024-03-31<br/>Q1 Data]
            RANGE2[Partition 2<br/>2024-04-01 to 2024-06-30<br/>Q2 Data]
            RANGE3[Partition 3<br/>2024-07-01 to 2024-09-30<br/>Q3 Data]
            RANGE4[Partition 4<br/>2024-10-01 to 2024-12-31<br/>Q4 Data]
        end

        subgraph "Incoming Records"
            REC1[Order: 2024-02-15<br/>Amount: $150]
            REC2[Order: 2024-05-20<br/>Amount: $75]
            REC3[Order: 2024-08-10<br/>Amount: $200]
            REC4[Order: 2024-11-05<br/>Amount: $90]
        end

        subgraph "Query Optimization"
            QUERY1[Query: Q2 2024 orders<br/>Only hits Partition 2]
            QUERY2[Query: 2024-05-01 to 2024-08-31<br/>Hits Partitions 2 & 3]
        end
    end

    REC1 --> RANGE1
    REC2 --> RANGE2
    REC3 --> RANGE3
    REC4 --> RANGE4

    QUERY1 --> RANGE2
    QUERY2 --> RANGE2
    QUERY2 --> RANGE3

    %% Apply colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class REC1,REC2,REC3,REC4 edgeStyle
    class QUERY1,QUERY2 serviceStyle
    class RANGE1,RANGE2,RANGE3,RANGE4 stateStyle
```

### Range Partitioning Implementation

```sql
-- PostgreSQL range partitioning example
CREATE TABLE orders (
    order_id SERIAL,
    order_date DATE NOT NULL,
    customer_id INTEGER,
    amount DECIMAL(10,2),
    status VARCHAR(20)
) PARTITION BY RANGE (order_date);

-- Create quarterly partitions
CREATE TABLE orders_2024_q1 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

CREATE TABLE orders_2024_q2 PARTITION OF orders
    FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');

CREATE TABLE orders_2024_q3 PARTITION OF orders
    FOR VALUES FROM ('2024-07-01') TO ('2024-10-01');

CREATE TABLE orders_2024_q4 PARTITION OF orders
    FOR VALUES FROM ('2024-10-01') TO ('2025-01-01');

-- Create indexes on each partition
CREATE INDEX ON orders_2024_q1 (customer_id);
CREATE INDEX ON orders_2024_q2 (customer_id);
CREATE INDEX ON orders_2024_q3 (customer_id);
CREATE INDEX ON orders_2024_q4 (customer_id);

-- Query examples showing partition pruning
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders
WHERE order_date BETWEEN '2024-05-01' AND '2024-05-31';
-- Will only scan orders_2024_q2 partition

EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*) FROM orders
WHERE order_date >= '2024-06-01';
-- Will scan orders_2024_q2, orders_2024_q3, orders_2024_q4
```

## Geographic Partitioning

### Multi-Region Data Distribution

```mermaid
graph TB
    subgraph "Geographic Partitioning Architecture"
        subgraph "North America Region"
            NA_LB[Load Balancer<br/>us-east-1]
            NA_APP[Application Servers<br/>us-east-1a, us-east-1b]
            NA_DB[Database Cluster<br/>Primary: us-east-1a<br/>Replica: us-east-1c]
            NA_USERS[North American Users<br/>Latency: 10-30ms]
        end

        subgraph "Europe Region"
            EU_LB[Load Balancer<br/>eu-west-1]
            EU_APP[Application Servers<br/>eu-west-1a, eu-west-1b]
            EU_DB[Database Cluster<br/>Primary: eu-west-1a<br/>Replica: eu-west-1c]
            EU_USERS[European Users<br/>Latency: 10-30ms]
        end

        subgraph "Asia-Pacific Region"
            AP_LB[Load Balancer<br/>ap-southeast-1]
            AP_APP[Application Servers<br/>ap-southeast-1a, ap-southeast-1b]
            AP_DB[Database Cluster<br/>Primary: ap-southeast-1a<br/>Replica: ap-southeast-1c]
            AP_USERS[Asia-Pacific Users<br/>Latency: 10-30ms]
        end

        subgraph "Cross-Region Services"
            GLOBAL_LB[Global Load Balancer<br/>GeoDNS routing]
            SYNC[Cross-Region Sync<br/>- User profiles<br/>- Global catalog<br/>- Analytics aggregation]
        end
    end

    NA_USERS --> GLOBAL_LB
    EU_USERS --> GLOBAL_LB
    AP_USERS --> GLOBAL_LB

    GLOBAL_LB --> NA_LB
    GLOBAL_LB --> EU_LB
    GLOBAL_LB --> AP_LB

    NA_LB --> NA_APP
    EU_LB --> EU_APP
    AP_LB --> AP_APP

    NA_APP --> NA_DB
    EU_APP --> EU_DB
    AP_APP --> AP_DB

    NA_DB <--> SYNC
    EU_DB <--> SYNC
    AP_DB <--> SYNC

    %% Apply colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class NA_USERS,EU_USERS,AP_USERS,GLOBAL_LB edgeStyle
    class NA_LB,EU_LB,AP_LB,NA_APP,EU_APP,AP_APP serviceStyle
    class NA_DB,EU_DB,AP_DB stateStyle
    class SYNC controlStyle
```

## Directory-Based Partitioning

### Lookup Service Architecture

```mermaid
sequenceDiagram
    participant C as Client
    participant D as Directory Service
    participant P1 as Partition 1
    participant P2 as Partition 2
    participant P3 as Partition 3

    Note over C,P3: Directory-based partitioning lookup

    C->>D: GET user:12345
    D->>D: Lookup key "user:12345" in directory
    D-->>C: Located on Partition 2

    C->>P2: GET user:12345
    P2-->>C: User data

    Note over C,P3: Write operation with directory update

    C->>D: PUT user:67890
    D->>D: Assign to least loaded partition (P1)
    D->>D: Update directory: user:67890 → P1
    D-->>C: Assigned to Partition 1

    C->>P1: PUT user:67890 with data
    P1-->>C: Success

    Note over C,P3: Migration scenario

    D->>D: Decide to migrate user:12345 from P2 to P3
    D->>P2: Begin migration of user:12345
    P2->>P3: Transfer user:12345 data
    P3-->>P2: Migration complete
    P2->>D: Confirm migration complete
    D->>D: Update directory: user:12345 → P3
```

### Directory Service Implementation

```python
# Directory-based partitioning implementation
import threading
from typing import Dict, Set, Optional
from enum import Enum

class PartitionStatus(Enum):
    ACTIVE = "active"
    DRAINING = "draining"
    MAINTENANCE = "maintenance"

class DirectoryService:
    def __init__(self):
        self.directory: Dict[str, str] = {}  # key -> partition_id
        self.partitions: Dict[str, PartitionStatus] = {}
        self.partition_loads: Dict[str, int] = {}
        self.lock = threading.RLock()

    def add_partition(self, partition_id: str):
        """Add a new partition to the directory"""
        with self.lock:
            self.partitions[partition_id] = PartitionStatus.ACTIVE
            self.partition_loads[partition_id] = 0

    def remove_partition(self, partition_id: str):
        """Remove a partition (must be empty)"""
        with self.lock:
            if partition_id in self.partitions:
                # Ensure no keys are assigned to this partition
                keys_in_partition = [k for k, p in self.directory.items() if p == partition_id]
                if keys_in_partition:
                    raise ValueError(f"Cannot remove partition {partition_id}: contains {len(keys_in_partition)} keys")

                del self.partitions[partition_id]
                del self.partition_loads[partition_id]

    def get_partition(self, key: str) -> Optional[str]:
        """Get the partition for a given key"""
        with self.lock:
            return self.directory.get(key)

    def assign_key(self, key: str, partition_id: Optional[str] = None) -> str:
        """Assign a key to a partition"""
        with self.lock:
            if key in self.directory:
                return self.directory[key]

            if partition_id is None:
                # Auto-assign to least loaded active partition
                active_partitions = [
                    p for p, status in self.partitions.items()
                    if status == PartitionStatus.ACTIVE
                ]

                if not active_partitions:
                    raise RuntimeError("No active partitions available")

                partition_id = min(active_partitions, key=lambda p: self.partition_loads[p])

            if partition_id not in self.partitions:
                raise ValueError(f"Partition {partition_id} does not exist")

            if self.partitions[partition_id] != PartitionStatus.ACTIVE:
                raise ValueError(f"Partition {partition_id} is not active")

            self.directory[key] = partition_id
            self.partition_loads[partition_id] += 1
            return partition_id

    def migrate_key(self, key: str, target_partition: str) -> bool:
        """Migrate a key to a different partition"""
        with self.lock:
            if key not in self.directory:
                return False

            old_partition = self.directory[key]
            if old_partition == target_partition:
                return True

            if target_partition not in self.partitions:
                raise ValueError(f"Target partition {target_partition} does not exist")

            if self.partitions[target_partition] != PartitionStatus.ACTIVE:
                raise ValueError(f"Target partition {target_partition} is not active")

            # Update directory
            self.directory[key] = target_partition
            self.partition_loads[old_partition] -= 1
            self.partition_loads[target_partition] += 1
            return True

    def get_partition_stats(self) -> Dict[str, Dict]:
        """Get statistics for all partitions"""
        with self.lock:
            stats = {}
            for partition_id in self.partitions:
                stats[partition_id] = {
                    'status': self.partitions[partition_id].value,
                    'key_count': self.partition_loads[partition_id],
                    'keys': [k for k, p in self.directory.items() if p == partition_id]
                }
            return stats

    def rebalance(self, target_variance: float = 0.1) -> Dict[str, str]:
        """Rebalance keys across partitions"""
        with self.lock:
            active_partitions = [
                p for p, status in self.partitions.items()
                if status == PartitionStatus.ACTIVE
            ]

            if len(active_partitions) < 2:
                return {}

            total_keys = sum(self.partition_loads[p] for p in active_partitions)
            target_load = total_keys / len(active_partitions)
            max_variance = target_load * target_variance

            migrations = {}

            # Find overloaded and underloaded partitions
            overloaded = [p for p in active_partitions
                         if self.partition_loads[p] > target_load + max_variance]
            underloaded = [p for p in active_partitions
                          if self.partition_loads[p] < target_load - max_variance]

            # Plan migrations
            for over_partition in overloaded:
                keys_to_move = [k for k, p in self.directory.items()
                               if p == over_partition]

                excess = self.partition_loads[over_partition] - int(target_load + max_variance)

                for key in keys_to_move[:excess]:
                    if underloaded:
                        target = underloaded[0]
                        migrations[key] = target

                        # Update tracking
                        if self.partition_loads[target] >= target_load - max_variance:
                            underloaded.pop(0)

            return migrations

# Example usage
directory = DirectoryService()

# Add partitions
directory.add_partition("partition-1")
directory.add_partition("partition-2")
directory.add_partition("partition-3")

# Assign keys
keys = ["user:1", "user:2", "user:3", "user:4", "user:5", "user:6"]
for key in keys:
    partition = directory.assign_key(key)
    print(f"{key} assigned to {partition}")

print("\nPartition stats:")
stats = directory.get_partition_stats()
for partition_id, info in stats.items():
    print(f"{partition_id}: {info['key_count']} keys, status: {info['status']}")

# Rebalance
print("\nRebalancing...")
migrations = directory.rebalance()
for key, target in migrations.items():
    directory.migrate_key(key, target)
    print(f"Migrated {key} to {target}")
```

## Partitioning Strategy Selection

### Decision Matrix

```mermaid
graph TB
    subgraph "Partitioning Strategy Selection"
        subgraph "Use Hash When"
            HASH_CASES[✅ Even data distribution needed<br/>✅ Simple key-value operations<br/>✅ No range queries required<br/>✅ Minimal hotspot risk<br/>Examples: User profiles, Session storage]
        end

        subgraph "Use Range When"
            RANGE_CASES[✅ Range queries are common<br/>✅ Time-series data<br/>✅ Natural data ordering exists<br/>✅ Data lifecycle management needed<br/>Examples: Logs, Time-series, Analytics]
        end

        subgraph "Use Geographic When"
            GEO_CASES[✅ Data sovereignty required<br/>✅ Latency optimization critical<br/>✅ Regional user bases<br/>✅ Compliance with local laws<br/>Examples: User data, Financial records]
        end

        subgraph "Use Directory When"
            DIR_CASES[✅ Flexible partitioning needed<br/>✅ Complex rebalancing requirements<br/>✅ Custom assignment logic<br/>✅ Frequent partition changes<br/>Examples: Multi-tenant systems, Dynamic workloads]
        end

        subgraph "Hybrid Approaches"
            HYBRID[Combination Strategies<br/>• Geographic + Hash<br/>• Range + Hash<br/>• Directory + Geographic<br/>Trade complexity for optimization]
        end
    end

    %% Apply colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class HASH_CASES edgeStyle
    class RANGE_CASES serviceStyle
    class GEO_CASES stateStyle
    class DIR_CASES,HYBRID controlStyle
```

## Production Cost-Benefit Analysis: Partitioning Strategies

### Real-World Infrastructure Investment

| Company | Partitioning Strategy | Annual Infrastructure Cost | Business Value | ROI |
|---------|----------------------|---------------------------|----------------|-----|
| **Instagram** | Hash-based user sharding | $50M (1000+ databases) | $2B (user growth support) | 40x |
| **Discord** | Channel-based partitioning | $25M (Cassandra clusters) | $500M (real-time messaging) | 20x |
| **Uber** | Geo-partitioning by city | $100M (global data centers) | $20B (global expansion) | 200x |
| **Netflix** | Content geo-partitioning | $200M (CDN + storage) | $30B (global streaming) | 150x |
| **Spotify** | User preference sharding | $30M (recommendation DBs) | $10B (personalization) | 333x |

## References and Further Reading

### Production Engineering Resources
- [Instagram Sharding Strategy](https://instagram-engineering.com/sharding-ids-at-instagram-1cf5a71e5a5c)
- [Discord Database Architecture](https://discord.com/blog/how-discord-stores-billions-of-messages)
- [Uber H3 Geospatial Indexing](https://eng.uber.com/h3/)
- [Netflix Content Distribution](https://netflixtechblog.com/distributing-content-to-open-connect-3e3e391d4dc9)
- [Spotify's Partition Tolerance](https://engineering.atspotify.com/2022/03/how-spotify-handles-billions-of-requests/)

### Academic Papers
- **DeWitt & Gray (1992)**: "Parallel Database Systems: The Future of High Performance Database Systems"
- **Lakshman & Malik (2010)**: "Cassandra: A Decentralized Structured Storage System"
- **Shute et al. (2013)**: "F1: A Distributed SQL Database That Scales"

### Tools and Frameworks
- [Vitess](https://vitess.io/) - MySQL sharding at YouTube scale
- [Cassandra](https://cassandra.apache.org/) - Distributed NoSQL with auto-partitioning
- [CockroachDB](https://www.cockroachlabs.com/) - Auto-sharded SQL database
- [MongoDB](https://www.mongodb.com/docs/manual/sharding/) - Built-in sharding support

### Production Decision Matrix

| Partitioning Strategy | Best For | Pros | Cons | Scale Examples |
|----------------------|----------|------|------|----------------|
| **Hash Partitioning** | Even distribution | Simple, balanced | Hard to rebalance | Instagram (400TB) |
| **Range Partitioning** | Time-series data | Efficient queries | Hotspots | Time-series DBs |
| **Directory Partitioning** | Dynamic systems | Flexible | Extra complexity | Google Spanner |
| **Geo-Partitioning** | Global apps | Data locality | Uneven load | Uber (1000 cities) |
| **Composite Partitioning** | Complex systems | Optimized access | Implementation complexity | LinkedIn (hybrid) |

Partitioning strategy choice fundamentally determines system scalability, query performance, and operational complexity. The key is understanding data access patterns, growth projections, and regulatory requirements to choose the optimal approach for production workloads.