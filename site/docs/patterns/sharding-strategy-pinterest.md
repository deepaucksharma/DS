# Sharding Strategy: Pinterest's Approach

## Overview

Pinterest's sharding strategy handles 250 billion pins across MySQL clusters, using a custom Python-based sharding framework that routes requests based on object IDs. Their approach eliminates single points of failure while maintaining data locality for user feeds and board operations.

## Production Architecture

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - #3B82F6]
        LB[Load Balancer<br/>NGINX Plus<br/>p99: 2ms]
        CDN[CloudFlare CDN<br/>Cache Hit: 94%<br/>Edge Locations: 270]
    end

    subgraph ServicePlane[Service Plane - #10B981]
        API[API Gateway<br/>Kong<br/>Rate: 100K RPS]
        SHARD[Shard Router<br/>Python Service<br/>Lookup: <1ms]
        APP[Application Layer<br/>Django<br/>200 instances]
    end

    subgraph StatePlane[State Plane - #F59E0B]
        subgraph Shard1[Shard 1 - Users 0-99M]
            DB1[(MySQL 8.0<br/>db.r5.12xlarge<br/>16TB storage)]
            SLAVE1[(Read Replica<br/>3x slaves<br/>Lag: <100ms)]
        end

        subgraph Shard2[Shard 2 - Users 100M-199M]
            DB2[(MySQL 8.0<br/>db.r5.12xlarge<br/>16TB storage)]
            SLAVE2[(Read Replica<br/>3x slaves<br/>Lag: <100ms)]
        end

        subgraph Shard3[Shard 3 - Users 200M+]
            DB3[(MySQL 8.0<br/>db.r5.12xlarge<br/>16TB storage)]
            SLAVE3[(Read Replica<br/>3x slaves<br/>Lag: <100ms)]
        end

        REDIS[(Redis Cluster<br/>Shard Mapping<br/>r5.2xlarge x12)]
    end

    subgraph ControlPlane[Control Plane - #8B5CF6]
        CONSUL[Consul<br/>Service Discovery<br/>Health Checks]
        PROM[Prometheus<br/>Metrics Collection<br/>1M samples/sec]
        ALERT[AlertManager<br/>PagerDuty Integration<br/>SLA: 99.9%]
    end

    %% Request Flow
    CDN --> LB
    LB --> API
    API --> SHARD
    SHARD --> REDIS
    REDIS --> SHARD
    SHARD --> DB1
    SHARD --> DB2
    SHARD --> DB3
    SHARD --> APP
    APP --> SLAVE1
    APP --> SLAVE2
    APP --> SLAVE3

    %% Control connections
    CONSUL --> SHARD
    CONSUL --> APP
    PROM --> DB1
    PROM --> DB2
    PROM --> DB3
    ALERT --> PROM

    %% Apply four-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#1E40AF,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#047857,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#6D28D9,color:#fff

    class LB,CDN edgeStyle
    class API,SHARD,APP serviceStyle
    class DB1,DB2,DB3,SLAVE1,SLAVE2,SLAVE3,REDIS stateStyle
    class CONSUL,PROM,ALERT controlStyle
```

## Shard Key Strategy

```mermaid
graph LR
    subgraph ShardLogic[Shard Determination Logic]
        INPUT[User ID: 245891032]
        HASH[MD5 Hash<br/>a4b7c9d2...]
        MOD[Modulo Operation<br/>hash % 4096]
        BUCKET[Bucket: 2847]
        LOOKUP[Shard Lookup<br/>Redis Cache]
        SHARD[Target: Shard 3<br/>mysql-shard-03]
    end

    INPUT --> HASH
    HASH --> MOD
    MOD --> BUCKET
    BUCKET --> LOOKUP
    LOOKUP --> SHARD

    classDef processStyle fill:#10B981,stroke:#047857,color:#fff
    class INPUT,HASH,MOD,BUCKET,LOOKUP,SHARD processStyle
```

## Data Distribution Pattern

```mermaid
graph TB
    subgraph DataFlow[Pinterest Data Flow]
        USER[User: 245891032<br/>Creates Pin]
        ROUTE[Shard Router<br/>Determines Shard 3]

        subgraph Shard3Data[Shard 3 - Data Layout]
            USERS[(users table<br/>245M-365M IDs)]
            PINS[(pins table<br/>Partition by user_id)]
            BOARDS[(boards table<br/>Partition by user_id)]
            FOLLOWS[(follows table<br/>Cross-shard refs)]
        end

        subgraph CrossShard[Cross-Shard Operations]
            FEED[Home Feed<br/>Aggregates from<br/>multiple shards]
            SEARCH[Search Service<br/>Elasticsearch<br/>Indexes all shards]
        end
    end

    USER --> ROUTE
    ROUTE --> USERS
    ROUTE --> PINS
    ROUTE --> BOARDS
    ROUTE --> FOLLOWS

    USERS --> FEED
    PINS --> FEED
    BOARDS --> FEED
    FOLLOWS --> SEARCH

    classDef userStyle fill:#3B82F6,stroke:#1E40AF,color:#fff
    classDef routeStyle fill:#10B981,stroke:#047857,color:#fff
    classDef dataStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef crossStyle fill:#8B5CF6,stroke:#6D28D9,color:#fff

    class USER userStyle
    class ROUTE routeStyle
    class USERS,PINS,BOARDS,FOLLOWS dataStyle
    class FEED,SEARCH crossStyle
```

## Failure Recovery and Resharding

```mermaid
graph TB
    subgraph FailureScenario[Shard 2 Failure Recovery]
        DETECT[Failure Detection<br/>Health Check Fail<br/>Response: 30s timeout]

        subgraph Emergency[Emergency Response]
            PROMOTE[Promote Read Replica<br/>mysql-shard-02-slave-01<br/>Time: 60 seconds]
            REDIRECT[Update Shard Mapping<br/>Redis Cluster Update<br/>Propagation: 5s]
            VERIFY[Verify Write Operations<br/>Test Suite: 200 queries<br/>Success Rate: 100%]
        end

        subgraph LongTerm[Long-term Recovery]
            REBUILD[Rebuild Failed Primary<br/>From Binary Logs<br/>Time: 4-6 hours]
            RESYNC[Resync Replication<br/>Catch-up: 2-3 hours<br/>Lag Target: <100ms]
            FAILBACK[Failback to Primary<br/>During Low Traffic<br/>Window: 2-4 AM PST]
        end
    end

    DETECT --> PROMOTE
    PROMOTE --> REDIRECT
    REDIRECT --> VERIFY
    VERIFY --> REBUILD
    REBUILD --> RESYNC
    RESYNC --> FAILBACK

    classDef detectStyle fill:#DC2626,stroke:#B91C1C,color:#fff
    classDef emergencyStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef recoveryStyle fill:#10B981,stroke:#047857,color:#fff

    class DETECT detectStyle
    class PROMOTE,REDIRECT,VERIFY emergencyStyle
    class REBUILD,RESYNC,FAILBACK recoveryStyle
```

## Production Metrics

### Shard Performance
- **Query Distribution**: 70% reads, 30% writes
- **Shard Utilization**: 60-80% capacity per shard
- **Cross-shard Queries**: <5% of total traffic
- **Hotspot Detection**: Automated monitoring for 2x average load

### Operational Metrics
- **Failover Time**: 60-90 seconds (RTO)
- **Data Loss**: <1 second of writes (RPO)
- **Rebalancing**: 6-month cycle, 2TB/hour migration rate
- **Schema Changes**: Zero-downtime via read replicas

## Implementation Details

### Shard Router Configuration
```python
# Pinterest's shard router logic (simplified)
SHARD_CONFIG = {
    'shard_01': {'range': (0, 99999999), 'primary': 'mysql-01'},
    'shard_02': {'range': (100000000, 199999999), 'primary': 'mysql-02'},
    'shard_03': {'range': (200000000, 299999999), 'primary': 'mysql-03'},
    'shard_04': {'range': (300000000, 399999999), 'primary': 'mysql-04'}
}

def get_shard(user_id):
    shard_key = hash(user_id) % NUM_SHARDS
    return SHARD_CONFIG[f'shard_{shard_key:02d}']
```

### Cost Breakdown
- **Database Infrastructure**: $180K/month (60% of data tier)
- **Cross-shard Query Overhead**: 15% performance penalty
- **Operational Complexity**: 2x DBA team size requirement
- **Migration Costs**: $2M for major resharding project

## Battle-tested Lessons

### What Works at 3 AM
1. **Automated Failover**: Sub-60 second promotion of read replicas
2. **Shard Health Monitoring**: Real-time capacity and performance alerts
3. **Cross-shard Query Limiting**: Circuit breakers prevent cascade failures
4. **Read Replica Load Distribution**: 80% of reads served from replicas

### Common Failure Patterns
1. **Hot Shard Syndrome**: Celebrity users causing uneven load
2. **Cross-shard Join Explosion**: Naive queries spanning all shards
3. **Replication Lag Cascade**: Slow replica affecting read performance
4. **Shard Map Inconsistency**: Stale routing causing data corruption

## Related Patterns
- [Database Partitioning](./database-partitioning.md)
- [Consistent Hashing](./consistent-hashing.md)
- [Read Replica Scaling](./read-replica-scaling.md)

*Source: Pinterest Engineering Blog, MySQL Performance Blog, Personal interviews with Pinterest DBAs*