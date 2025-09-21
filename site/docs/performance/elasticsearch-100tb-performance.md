# Elasticsearch at 100TB: GitHub's Code Search Performance Profile

## Overview

GitHub operates one of the world's largest code search systems, indexing over 100TB of source code across millions of repositories. Their Elasticsearch deployment handles complex search queries with sub-second response times while maintaining 99.9% availability. This profile examines their indexing strategies, query optimization, and infrastructure architecture.

## Architecture for Performance

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - #3B82F6]
        LB[GitHub Load Balancer<br/>NGINX + HAProxy<br/>99.99% availability]
        CDN[Search Result Cache<br/>Redis + Varnish<br/>65% cache hit ratio]
    end

    subgraph ServicePlane[Service Plane - #10B981]
        API[Search API<br/>Ruby on Rails<br/>500 instances]
        QUEUE[Index Queue<br/>Redis + Sidekiq<br/>100K jobs/hour]
    end

    subgraph StatePlane[State Plane - #F59E0B]
        ES_MASTER[ES Master Nodes<br/>3x r6g.2xlarge<br/>Cluster coordination]
        ES_DATA[ES Data Nodes<br/>200x r6g.8xlarge<br/>32GB RAM, 4TB NVMe]
        ES_INGEST[ES Ingest Nodes<br/>20x c6g.4xlarge<br/>Preprocessing pipeline]
    end

    subgraph ControlPlane[Control Plane - #8B5CF6]
        MON[Monitoring<br/>Elasticsearch + Kibana<br/>Custom dashboards]
        BACKUP[Backup System<br/>S3 snapshots<br/>Daily incremental]
    end

    LB --> API
    CDN --> LB
    API --> QUEUE
    API --> ES_MASTER
    QUEUE --> ES_INGEST
    ES_MASTER --> ES_DATA
    ES_INGEST --> ES_DATA

    MON --> ES_MASTER
    MON --> ES_DATA
    BACKUP --> ES_DATA

    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class LB,CDN edgeStyle
    class API,QUEUE serviceStyle
    class ES_MASTER,ES_DATA,ES_INGEST stateStyle
    class MON,BACKUP controlStyle
```

## Performance Metrics and Benchmarks

### Cluster Overview
- **Total Data Size**: 100TB indexed content
- **Daily Indexing**: 15TB new/updated code
- **Search QPS**: 25,000 queries per second peak
- **Index Rate**: 50,000 documents per second
- **Node Count**: 223 total (3 master, 200 data, 20 ingest)
- **Shard Count**: 12,000 shards across all indices
- **Replica Count**: 1 replica per shard (2x data storage)

### Query Performance Profile
```mermaid
graph LR
    subgraph QueryLatency[Search Query Latency Breakdown - p95]
        PARSE[Query Parse: 2ms<br/>Lucene query building<br/>Complex regex handling]
        ROUTE[Routing: 1ms<br/>Shard selection<br/>Node coordination]
        EXEC[Execution: 125ms<br/>Parallel shard search<br/>Score calculation]
        MERGE[Result Merge: 8ms<br/>Cross-shard sorting<br/>Relevance ranking]
        RETURN[Response: 1ms<br/>JSON serialization<br/>Network transfer]
    end

    subgraph Percentiles[Response Time Distribution]
        P50[p50: 89ms]
        P95[p95: 137ms]
        P99[p99: 245ms]
        P999[p999: 890ms]
    end

    subgraph QueryTypes[Query Performance by Type]
        SIMPLE[Simple Term: 45ms<br/>Single field match<br/>High cache hit]
        REGEX[Regex Search: 180ms<br/>Complex patterns<br/>CPU intensive]
        FUZZY[Fuzzy Match: 220ms<br/>Edit distance<br/>Multiple variations]
        PHRASE[Phrase Query: 95ms<br/>Position-aware<br/>Proximity scoring]
    end

    classDef metricStyle fill:#F59E0B,stroke:#D97706,color:#fff
    class PARSE,ROUTE,EXEC,MERGE,RETURN,P50,P95,P99,P999,SIMPLE,REGEX,FUZZY,PHRASE metricStyle
```

### Indexing Performance
- **Indexing Rate**: 50,000 documents per second sustained
- **Peak Indexing**: 85,000 documents per second
- **Bulk Request Size**: 10MB batches (optimal throughput)
- **Refresh Interval**: 30 seconds (balances search vs indexing)
- **Merge Policy**: 50% deleted docs trigger segment merge
- **Index Size**: 500GB average per index

## Optimization Techniques Used

### 1. Index Design Strategy
```mermaid
graph TB
    subgraph IndexArchitecture[GitHub Code Index Architecture]
        REPO[Repository Index<br/>Daily rotation<br/>repo-YYYY-MM-DD]
        CODE[Code Content Index<br/>Language-specific<br/>code-lang-YYYY-MM]
        COMMIT[Commit Index<br/>Git metadata<br/>commit-YYYY-MM]
        ISSUE[Issues Index<br/>User content<br/>issue-YYYY-MM]
    end

    subgraph ShardStrategy[Sharding Strategy]
        REPO_SHARD[Repository Shards<br/>60 shards per index<br/>Size-based routing]
        CODE_SHARD[Code Shards<br/>120 shards per index<br/>Language-based routing]
        TIME_SHARD[Time-based Shards<br/>Monthly rotation<br/>Automatic deletion]
    end

    subgraph MappingOptimization[Field Mapping Optimization]
        CONTENT[Content Field<br/>analyzed text<br/>Standard analyzer]
        PATH[Path Field<br/>keyword type<br/>Exact match only]
        LANG[Language Field<br/>keyword type<br/>Faceted search]
        SIZE[Size Field<br/>integer type<br/>Range queries]
    end

    REPO --> REPO_SHARD
    CODE --> CODE_SHARD
    COMMIT --> TIME_SHARD

    classDef indexStyle fill:#10B981,stroke:#059669,color:#fff
    classDef shardStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef mappingStyle fill:#3B82F6,stroke:#2563EB,color:#fff

    class REPO,CODE,COMMIT,ISSUE indexStyle
    class REPO_SHARD,CODE_SHARD,TIME_SHARD shardStyle
    class CONTENT,PATH,LANG,SIZE mappingStyle
```

### 2. Query Optimization
- **Query Caching**: Filter cache 85% hit ratio
- **Request Cache**: Query result cache 40% hit ratio
- **Field Data Cache**: 8GB per node for sorting/aggregations
- **Bool Query Optimization**: Complex queries use should/must clauses
- **Highlight Optimization**: Fast vector highlighter for code snippets

### 3. Hardware Configuration Per Data Node
```yaml
# Elasticsearch Node Configuration - r6g.8xlarge
Instance Type: r6g.8xlarge
CPU: 32 vCPUs (ARM Graviton2)
Memory: 256GB total
  - JVM Heap: 31GB (Xmx31g)
  - OS Cache: 225GB
Storage: 4TB NVMe SSD
  - Data: 3.5TB usable
  - OS: 500GB
Network: 25 Gbps
```

### 4. JVM Tuning
```bash
# Elasticsearch JVM Settings
-Xms31g
-Xmx31g
-XX:+UseG1GC
-XX:G1HeapRegionSize=32m
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200
-XX:G1NewSizePercent=30
-XX:G1MaxNewSizePercent=40
-XX:+UseStringDeduplication
-XX:+UnlockExperimentalVMOptions
-XX:+UseTransparentHugePages
```

## Bottleneck Analysis

### 1. I/O Performance Analysis
```mermaid
graph TB
    subgraph IOBottlenecks[I/O Performance Bottlenecks]
        READ[Read I/O: 2.5GB/s<br/>Query execution<br/>Segment reading]
        WRITE[Write I/O: 800MB/s<br/>Index updates<br/>Segment merging]
        MERGE[Merge I/O: 1.2GB/s<br/>Background merging<br/>Segment optimization]
        SNAP[Snapshot I/O: 500MB/s<br/>Backup operations<br/>S3 transfers]
    end

    subgraph Solutions[I/O Optimization Solutions]
        NVME[NVMe Storage<br/>4TB per node<br/>Ultra-low latency]
        CACHE[OS Page Cache<br/>225GB per node<br/>Hot data caching]
        ASYNC[Async I/O<br/>Non-blocking operations<br/>Better throughput]
        COMPRESS[Index Compression<br/>LZ4 algorithm<br/>30% space savings]
    end

    READ --> NVME
    READ --> CACHE
    WRITE --> ASYNC
    MERGE --> COMPRESS

    classDef bottleneckStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef solutionStyle fill:#10B981,stroke:#059669,color:#fff

    class READ,WRITE,MERGE,SNAP bottleneckStyle
    class NVME,CACHE,ASYNC,COMPRESS solutionStyle
```

### 2. Memory Bottlenecks
- **Heap Pressure**: 31GB heap limit to avoid GC pauses
- **Field Data**: Limited to 40% of heap for aggregations
- **Filter Cache**: 10% of heap for frequently used filters
- **Request Cache**: 1% of heap for query result caching
- **OS Cache Pressure**: 225GB OS cache critical for performance

### 3. CPU Bottlenecks
- **Query Processing**: 60% CPU during peak search traffic
- **Indexing Load**: 40% CPU during heavy indexing periods
- **Regex Queries**: Can consume 80% CPU for complex patterns
- **JSON Parsing**: 15% CPU for large document processing
- **Compression**: 10% CPU for index compression

## Scaling Limits Discovered

### 1. Shard Count Limits
```mermaid
graph LR
    subgraph ShardScaling[Shard Scaling Analysis]
        S1000[1K Shards<br/>Query Time: 45ms<br/>Memory: 2GB<br/>Optimal Performance]
        S5000[5K Shards<br/>Query Time: 85ms<br/>Memory: 8GB<br/>Good Performance]
        S10000[10K Shards<br/>Query Time: 140ms<br/>Memory: 18GB<br/>Acceptable]
        S15000[15K Shards<br/>Query Time: 280ms<br/>Memory: 35GB<br/>Performance Degrades]
        S20000[20K+ Shards<br/>Query Time: >500ms<br/>Memory: >50GB<br/>Cluster Instability]
    end

    S1000 --> S5000 --> S10000 --> S15000 --> S20000

    subgraph Solution[Scaling Solution]
        REINDEX[Index Optimization<br/>12K shards total<br/>60 shards per index<br/>Maintained performance]
    end

    S20000 --> REINDEX

    classDef scaleStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef solutionStyle fill:#10B981,stroke:#059669,color:#fff

    class S1000,S5000,S10000,S15000,S20000 scaleStyle
    class REINDEX solutionStyle
```

### 2. Node Count Scaling
- **Master Node Limit**: 3 masters optimal for split-brain prevention
- **Data Node Scaling**: Linear scaling up to 200 nodes
- **Network Overhead**: Cluster coordination increases with node count
- **Shard Allocation**: More nodes = better distribution but more overhead

### 3. Query Complexity Limits
- **Regex Timeout**: 30 second timeout for complex regex patterns
- **Wildcard Limits**: Leading wildcards disabled for performance
- **Aggregation Memory**: Limited by available heap and field data cache
- **Result Size**: 10,000 results maximum per query

## Cost vs Performance Trade-offs

### 1. Infrastructure Costs (Monthly)
```mermaid
graph TB
    subgraph CostBreakdown[Monthly Infrastructure Cost: $2,850,000]
        DATA_NODES[Data Nodes<br/>200 × r6g.8xlarge<br/>$2,400/month each<br/>$480,000 total]

        MASTER_NODES[Master Nodes<br/>3 × r6g.2xlarge<br/>$600/month each<br/>$1,800 total]

        INGEST_NODES[Ingest Nodes<br/>20 × c6g.4xlarge<br/>$800/month each<br/>$16,000 total]

        STORAGE[NVMe Storage<br/>800TB total @ $0.10/GB<br/>$80,000/month]

        NETWORK[Data Transfer<br/>5PB/month @ $0.09/GB<br/>$450,000/month]

        BACKUP[S3 Backup Storage<br/>200TB @ $0.023/GB<br/>$4,600/month]

        MONITORING[Monitoring Stack<br/>Kibana + Grafana<br/>$25,000/month]

        SUPPORT[Enterprise Support<br/>24/7 Elasticsearch support<br/>$150,000/month]

        TEAM[Engineering Team<br/>15 search engineers<br/>$1,642,600/month]
    end

    DATA_NODES --> TOTAL[Total Monthly Cost<br/>$2,850,000]
    MASTER_NODES --> TOTAL
    INGEST_NODES --> TOTAL
    STORAGE --> TOTAL
    NETWORK --> TOTAL
    BACKUP --> TOTAL
    MONITORING --> TOTAL
    SUPPORT --> TOTAL
    TEAM --> TOTAL

    classDef costStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef totalStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class DATA_NODES,MASTER_NODES,INGEST_NODES,STORAGE,NETWORK,BACKUP,MONITORING,SUPPORT,TEAM costStyle
    class TOTAL totalStyle
```

### 2. Performance ROI Analysis
- **Cost per Search**: $0.0033 per search query
- **Cost per Indexed Document**: $0.0000017 per document
- **Storage Efficiency**: 50% compression saves $200K monthly
- **Query Optimization**: 40% latency improvement from caching

### 3. Alternative Architectures
- **Solr**: 30% lower cost, 25% slower query performance
- **Amazon OpenSearch**: 20% higher cost, managed service benefits
- **Self-managed**: Current setup optimal for GitHub's requirements
- **Hybrid Cloud**: 15% cost savings, increased complexity

## Real Production Configurations

### Elasticsearch Configuration (elasticsearch.yml)
```yaml
# Cluster Configuration
cluster.name: github-code-search
node.name: ${HOSTNAME}
node.roles: [ data, ingest ]

# Network Configuration
network.host: 0.0.0.0
http.port: 9200
transport.port: 9300

# Discovery Configuration
discovery.seed_hosts: ["master-1", "master-2", "master-3"]
cluster.initial_master_nodes: ["master-1", "master-2", "master-3"]

# Memory Configuration
indices.memory.index_buffer_size: 20%
indices.memory.min_index_buffer_size: 96mb

# Query Cache Configuration
indices.queries.cache.size: 40%
indices.request.cache.size: 1%

# Indexing Configuration
index.refresh_interval: 30s
index.number_of_shards: 60
index.number_of_replicas: 1

# Search Configuration
search.max_buckets: 65536
indices.fielddata.cache.size: 40%

# Thread Pool Configuration
thread_pool.search.size: 32
thread_pool.search.queue_size: 1000
thread_pool.index.size: 8
thread_pool.index.queue_size: 200

# Circuit Breaker Configuration
indices.breaker.total.limit: 85%
indices.breaker.fielddata.limit: 40%
indices.breaker.request.limit: 30%
```

### Index Template for Code Search
```json
{
  "index_patterns": ["code-*"],
  "template": {
    "settings": {
      "number_of_shards": 60,
      "number_of_replicas": 1,
      "refresh_interval": "30s",
      "index.codec": "best_compression",
      "index.merge.policy.max_merged_segment": "2gb",
      "index.merge.policy.segments_per_tier": 24,
      "analysis": {
        "analyzer": {
          "code_analyzer": {
            "type": "custom",
            "tokenizer": "keyword",
            "filter": ["lowercase", "github_ngram"]
          }
        },
        "filter": {
          "github_ngram": {
            "type": "ngram",
            "min_gram": 2,
            "max_gram": 20
          }
        }
      }
    },
    "mappings": {
      "properties": {
        "content": {
          "type": "text",
          "analyzer": "code_analyzer",
          "search_analyzer": "standard",
          "term_vector": "with_positions_offsets"
        },
        "path": {
          "type": "keyword",
          "fields": {
            "analyzed": {
              "type": "text",
              "analyzer": "path_hierarchy"
            }
          }
        },
        "language": {
          "type": "keyword"
        },
        "repository": {
          "type": "keyword"
        },
        "size": {
          "type": "integer"
        },
        "last_modified": {
          "type": "date"
        }
      }
    }
  }
}
```

## Monitoring and Profiling Setup

### 1. Key Performance Indicators
```mermaid
graph TB
    subgraph Metrics[Elasticsearch Performance Dashboard]
        QPS[Search QPS<br/>Current: 18.5K<br/>Target: <25K<br/>Alert: >23K]

        LATENCY[Query Latency<br/>p95: 137ms<br/>Target: <200ms<br/>Alert: >300ms]

        INDEX_RATE[Index Rate<br/>Current: 42K docs/sec<br/>Target: >30K/sec<br/>Alert: <25K/sec]

        HEAP[JVM Heap Usage<br/>Current: 75%<br/>Target: <80%<br/>Alert: >85%]

        CACHE[Cache Hit Ratio<br/>Filter: 85%<br/>Request: 40%<br/>Alert: <70%]

        DISK[Disk Utilization<br/>Current: 70%<br/>Target: <80%<br/>Alert: >85%]

        CPU[CPU Utilization<br/>Current: 55%<br/>Target: <70%<br/>Alert: >80%]

        NETWORK[Network I/O<br/>Current: 15 Gbps<br/>Target: <20 Gbps<br/>Alert: >22 Gbps]
    end

    subgraph ClusterHealth[Cluster Health Monitoring]
        STATUS[Cluster Status<br/>Green/Yellow/Red<br/>Real-time monitoring]

        SHARDS[Shard Health<br/>Unassigned shards<br/>Relocating shards]

        NODES[Node Health<br/>Active nodes<br/>Memory pressure]
    end

    classDef metricStyle fill:#10B981,stroke:#059669,color:#fff
    classDef healthStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class QPS,LATENCY,INDEX_RATE,HEAP,CACHE,DISK,CPU,NETWORK metricStyle
    class STATUS,SHARDS,NODES healthStyle
```

### 2. Performance Testing Framework
```bash
# GitHub Elasticsearch Load Testing
#!/bin/bash

# Rally benchmarking tool
esrally race \
  --track-path=/home/github/rally-tracks/github-code-search \
  --target-hosts=elasticsearch-cluster.github.internal:9200 \
  --pipeline=benchmark-only \
  --challenge=github-workload \
  --user-tag="github-production-test" \
  --report-format=csv \
  --report-file=results.csv

# Custom search load test
cat github-search-test.py:
import elasticsearch
import concurrent.futures
import time
import random

def search_test():
    es = elasticsearch.Elasticsearch(['elasticsearch-cluster.github.internal:9200'])

    queries = [
        "function main",
        "class.*Component",
        "import.*react",
        "def.*test",
        "async.*await"
    ]

    for _ in range(1000):
        query = random.choice(queries)
        start = time.time()
        es.search(index="code-*", q=query, size=50)
        latency = time.time() - start
        print(f"Query: {query}, Latency: {latency:.3f}s")
```

### 3. Profiling and Debugging Tools
- **Hot Threads API**: Identify CPU-intensive operations
- **Query Profiler**: Analyze query execution breakdown
- **Index Stats**: Monitor index performance metrics
- **Node Stats**: Track node-level resource usage
- **Slow Log**: Capture queries exceeding latency thresholds

## Key Performance Insights

### 1. Critical Success Factors
- **Index Design**: Proper sharding strategy eliminates hotspots
- **Hardware Selection**: NVMe storage critical for query performance
- **Memory Management**: 225GB OS cache provides 85% query acceleration
- **Query Optimization**: Proper caching reduces latency by 60%
- **Cluster Sizing**: 200 data nodes provide optimal price/performance

### 2. Lessons Learned
- **Shard Count**: 12K shards optimal, beyond 15K degrades performance
- **JVM Heap**: 31GB heap size prevents garbage collection pauses
- **Regex Performance**: Complex patterns require careful timeout handling
- **Index Rotation**: Daily rotation prevents indices from becoming too large
- **Compression**: 30% storage savings with minimal CPU overhead

### 3. Anti-patterns Avoided
- **Too Many Shards**: Avoid >100 shards per GB heap memory
- **Large Shards**: Keep shards under 50GB for optimal performance
- **Deep Pagination**: Limit result sets to avoid memory exhaustion
- **Wildcard Abuse**: Leading wildcards cause performance degradation
- **Sync Refresh**: Avoid refresh_interval=1s in high-throughput scenarios

### 4. Future Optimization Strategies
- **Machine Learning**: Query performance prediction and optimization
- **Hybrid Storage**: Hot/warm/cold data tiering for cost optimization
- **Vector Search**: Semantic code search using embeddings
- **Auto-scaling**: Dynamic cluster sizing based on load patterns
- **Edge Caching**: Geographic distribution for global performance

This performance profile demonstrates how GitHub achieves exceptional search performance across 100TB of source code through careful architecture design, hardware optimization, and operational excellence. Their implementation serves as a blueprint for building large-scale search systems that can handle complex queries with sub-second response times.