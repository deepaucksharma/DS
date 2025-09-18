# SQS/SNS Performance Profile

## Overview

Amazon SQS and SNS performance characteristics in production environments, covering FIFO vs Standard queue performance, long polling optimization, fan-out patterns with SNS, and dead letter queue overhead. Based on Netflix's event-driven architecture and other high-scale AWS deployments.

## FIFO vs Standard Queue Performance

### Standard SQS Queue Characteristics

```mermaid
graph TB
    subgraph "Standard Queue Architecture"
        STD1[Distributed queue system<br/>Multiple servers<br/>At-least-once delivery<br/>Best-effort ordering<br/>Nearly unlimited throughput]

        STD2[Performance metrics<br/>Throughput: 3000 TPS per action<br/>Batch send: 10 messages<br/>Effective rate: 30K msg/sec<br/>Latency: 10-50ms]

        STD3[Scaling characteristics<br/>Auto-scaling: Automatic<br/>No provisioning required<br/>Regional availability<br/>Cross-AZ replication]

        STD1 --> STD2 --> STD3
    end

    subgraph "Standard Queue Message Flow"
        PROD[Producer Application<br/>Send rate: 10K msg/sec<br/>Batch size: 10 messages<br/>API calls: 1K TPS]

        SQS_STD[Standard SQS Queue<br/>Distributed storage<br/>Multiple servers<br/>Message duplication possible]

        CONS1[Consumer 1<br/>Receive rate: 5K msg/sec<br/>Long polling: 20s<br/>Batch size: 10]

        CONS2[Consumer 2<br/>Receive rate: 5K msg/sec<br/>Long polling: 20s<br/>Batch size: 10]

        PROD --> SQS_STD
        SQS_STD --> CONS1
        SQS_STD --> CONS2
    end

    classDef standardStyle fill:#10B981,stroke:#059669,color:#fff
    classDef flowStyle fill:#3B82F6,stroke:#2563EB,color:#fff

    class STD1,STD2,STD3 standardStyle
    class PROD,SQS_STD,CONS1,CONS2 flowStyle
```

### FIFO SQS Queue Characteristics

```mermaid
graph TB
    subgraph "FIFO Queue Architecture"
        FIFO1[Single logical queue<br/>Message groups<br/>Exactly-once processing<br/>Strict ordering<br/>Limited throughput]

        FIFO2[Performance metrics<br/>Throughput: 300 TPS per group<br/>Max groups: 20K<br/>Theoretical max: 6M msg/sec<br/>Practical max: 100K msg/sec]

        FIFO3[Ordering guarantees<br/>Group ordering: Strict<br/>Cross-group ordering: None<br/>Deduplication: 5-minute window<br/>Content-based dedup: Supported]

        FIFO1 --> FIFO2 --> FIFO3
    end

    subgraph "FIFO Queue Message Flow"
        PROD_FIFO[Producer Application<br/>Send rate: 1K msg/sec<br/>Group ID: user_123<br/>Dedup ID: Required]

        SQS_FIFO[FIFO SQS Queue<br/>Message groups<br/>Strict ordering per group<br/>Deduplication enabled]

        CONS_FIFO[Consumer Application<br/>Sequential processing<br/>Per-group ordering<br/>Rate: 300 msg/sec per group]

        PROD_FIFO --> SQS_FIFO --> CONS_FIFO
    end

    classDef fifoStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef fifoFlowStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class FIFO1,FIFO2,FIFO3 fifoStyle
    class PROD_FIFO,SQS_FIFO,CONS_FIFO fifoFlowStyle
```

### Performance Comparison Matrix

```mermaid
graph LR
    subgraph "Throughput Comparison"
        THR1[Standard Queue<br/>Single queue: 30K msg/sec<br/>Multiple queues: Unlimited<br/>Batching: 10x improvement<br/>Regional limits: None]

        THR2[FIFO Queue<br/>Single group: 300 msg/sec<br/>Multiple groups: 100K msg/sec<br/>Batching: 10x improvement<br/>Regional limits: Apply]
    end

    subgraph "Latency Comparison"
        LAT1[Standard Queue<br/>Receive: 10-50ms<br/>Visibility timeout: Configurable<br/>Polling: Long/Short available<br/>Jitter: Moderate]

        LAT2[FIFO Queue<br/>Receive: 50-200ms<br/>Group processing: Sequential<br/>Dedup overhead: +20ms<br/>Jitter: Higher]
    end

    subgraph "Cost Comparison"
        COST1[Standard Queue<br/>Base cost: $0.40/million requests<br/>Data transfer: Standard rates<br/>No ordering premium<br/>High volume discounts]

        COST2[FIFO Queue<br/>Base cost: $0.50/million requests<br/>Data transfer: Standard rates<br/>Ordering premium: 25%<br/>Limited volume discounts]
    end

    classDef standardStyle fill:#10B981,stroke:#059669,color:#fff
    classDef fifoStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class THR1,LAT1,COST1 standardStyle
    class THR2,LAT2,COST2 fifoStyle
```

## Long Polling Optimization

### Polling Strategy Performance Impact

```mermaid
graph TB
    subgraph "Short Polling (0 seconds)"
        SHORT1[Polling configuration<br/>WaitTimeSeconds: 0<br/>Immediate return<br/>Empty response possible<br/>High API call frequency]

        SHORT2[Performance characteristics<br/>Latency: 10-20ms<br/>API calls: 1 per second minimum<br/>Cost: High (empty receives)<br/>CPU usage: High]

        SHORT3[Use cases<br/>Real-time processing<br/>Low-latency requirements<br/>Simple implementation<br/>High cost tolerance]

        SHORT1 --> SHORT2 --> SHORT3
    end

    subgraph "Long Polling (20 seconds)"
        LONG1[Polling configuration<br/>WaitTimeSeconds: 20<br/>Wait for messages<br/>Connection held open<br/>Reduced API calls]

        LONG2[Performance characteristics<br/>Latency: 0-20000ms<br/>API calls: Reduced by 10x<br/>Cost: Low (fewer empty receives)<br/>CPU usage: Low]

        LONG3[Use cases<br/>Batch processing<br/>Cost optimization<br/>Standard workloads<br/>Reduced complexity]

        LONG1 --> LONG2 --> LONG3
    end

    subgraph "Hybrid Polling Strategy"
        HYBRID1[Adaptive polling<br/>Short poll during high load<br/>Long poll during low load<br/>Dynamic adjustment<br/>Load-based switching]

        HYBRID2[Implementation<br/>CloudWatch metrics<br/>Queue depth monitoring<br/>Automatic switching<br/>Cost optimization]

        HYBRID1 --> HYBRID2
    end

    classDef shortStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef longStyle fill:#10B981,stroke:#059669,color:#fff
    classDef hybridStyle fill:#3B82F6,stroke:#2563EB,color:#fff

    class SHORT1,SHORT2,SHORT3 shortStyle
    class LONG1,LONG2,LONG3 longStyle
    class HYBRID1,HYBRID2 hybridStyle
```

### Batching Impact on Performance

```mermaid
graph LR
    subgraph "Single Message Processing"
        SINGLE1[Batch size: 1<br/>API calls: High<br/>Network overhead: High<br/>Processing efficiency: Low]

        SINGLE2[Performance metrics<br/>Throughput: 1K msg/sec<br/>API cost: $40/million messages<br/>Latency: 20ms per message<br/>Network utilization: 30%]

        SINGLE1 --> SINGLE2
    end

    subgraph "Optimal Batch Processing"
        BATCH1[Batch size: 10<br/>API calls: Reduced 10x<br/>Network overhead: Low<br/>Processing efficiency: High]

        BATCH2[Performance metrics<br/>Throughput: 10K msg/sec<br/>API cost: $4/million messages<br/>Latency: 20ms per batch<br/>Network utilization: 90%]

        BATCH1 --> BATCH2
    end

    subgraph "Batch Size Optimization"
        OPT1[Factors affecting batch size<br/>• Message size<br/>• Processing latency<br/>• Memory constraints<br/>• Error handling complexity]

        OPT2[Optimal configurations<br/>Small messages: Batch 10<br/>Large messages: Batch 2-5<br/>Fast processing: Batch 10<br/>Slow processing: Batch 3-5]

        OPT1 --> OPT2
    end

    classDef singleStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef batchStyle fill:#10B981,stroke:#059669,color:#fff
    classDef optStyle fill:#3B82F6,stroke:#2563EB,color:#fff

    class SINGLE1,SINGLE2 singleStyle
    class BATCH1,BATCH2 batchStyle
    class OPT1,OPT2 optStyle
```

## Fan-out Patterns with SNS

### SNS Topic Fan-out Architecture

```mermaid
graph TB
    subgraph "Publisher to SNS Topic"
        PUB[Event Publisher<br/>Application: Order service<br/>Event: Order placed<br/>Rate: 10K events/sec]

        TOPIC[SNS Topic: OrderEvents<br/>Message filtering<br/>Fan-out delivery<br/>Regional replication]

        PUB --> TOPIC
    end

    subgraph "SNS Subscription Types"
        SQS_SUB[SQS Subscription<br/>Queue: inventory-updates<br/>Filter: product_category<br/>Delivery: Reliable]

        LAMBDA_SUB[Lambda Subscription<br/>Function: send-notification<br/>Filter: customer_type = premium<br/>Delivery: Asynchronous]

        HTTP_SUB[HTTP Subscription<br/>Endpoint: analytics-webhook<br/>Filter: order_value > 100<br/>Delivery: Retry with backoff]

        EMAIL_SUB[Email Subscription<br/>Address: alerts@company.com<br/>Filter: order_value > 10000<br/>Delivery: Best effort]

        TOPIC --> SQS_SUB
        TOPIC --> LAMBDA_SUB
        TOPIC --> HTTP_SUB
        TOPIC --> EMAIL_SUB
    end

    subgraph "Performance Characteristics"
        PERF1[Fan-out performance<br/>Parallel delivery<br/>Per-subscription filtering<br/>Independent scaling<br/>Failure isolation]

        PERF2[Delivery metrics<br/>SQS: 99.9% success rate<br/>Lambda: 99.5% success rate<br/>HTTP: 95% success rate<br/>Email: 90% success rate]

        SQS_SUB --> PERF1
        LAMBDA_SUB --> PERF1
        HTTP_SUB --> PERF2
        EMAIL_SUB --> PERF2
    end

    classDef pubStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef topicStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef subStyle fill:#10B981,stroke:#059669,color:#fff
    classDef perfStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class PUB,TOPIC pubStyle
    class TOPIC topicStyle
    class SQS_SUB,LAMBDA_SUB,HTTP_SUB,EMAIL_SUB subStyle
    class PERF1,PERF2 perfStyle
```

### Message Filtering Performance

```mermaid
graph TB
    subgraph "No Filtering (Broadcast)"
        NO_FILTER1[All messages delivered<br/>to all subscriptions<br/>Processing overhead: High<br/>Network utilization: High]

        NO_FILTER2[Performance impact<br/>Delivery rate: 100K msg/sec<br/>Network bandwidth: 500 Mbps<br/>Processing cost: $100/day<br/>Unwanted messages: 80%]

        NO_FILTER1 --> NO_FILTER2
    end

    subgraph "Attribute-based Filtering"
        ATTR_FILTER1[Server-side filtering<br/>Message attributes<br/>Filter policies<br/>Selective delivery]

        ATTR_FILTER2[Performance impact<br/>Delivery rate: 20K msg/sec<br/>Network bandwidth: 100 Mbps<br/>Processing cost: $20/day<br/>Unwanted messages: 5%]

        ATTR_FILTER1 --> ATTR_FILTER2
    end

    subgraph "Content-based Filtering"
        CONTENT_FILTER1[Message body filtering<br/>JSON path expressions<br/>Complex conditions<br/>Advanced matching]

        CONTENT_FILTER2[Performance impact<br/>Filter overhead: +5ms<br/>CPU usage: +30%<br/>Precision: 99%<br/>Complexity: High]

        CONTENT_FILTER1 --> CONTENT_FILTER2
    end

    subgraph "Filter Policy Examples"
        EXAMPLES[Attribute filtering<br/>{"order_value": [{"numeric": [">=", 100]}]}<br/>{"region": ["us-east-1", "us-west-2"]}<br/>{"event_type": ["order", "payment"]}]
    end

    classDef noFilterStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef attrFilterStyle fill:#10B981,stroke:#059669,color:#fff
    classDef contentFilterStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef exampleStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class NO_FILTER1,NO_FILTER2 noFilterStyle
    class ATTR_FILTER1,ATTR_FILTER2 attrFilterStyle
    class CONTENT_FILTER1,CONTENT_FILTER2 contentFilterStyle
    class EXAMPLES exampleStyle
```

## Dead Letter Queue Overhead

### DLQ Configuration and Performance

```mermaid
graph TB
    subgraph "Standard Queue with DLQ"
        MAIN_Q[Main Queue<br/>Message processing<br/>Visibility timeout: 30s<br/>Max receive count: 3]

        DLQ[Dead Letter Queue<br/>Failed messages<br/>Manual inspection<br/>Reprocessing capability]

        PROC[Message Processor<br/>Success rate: 95%<br/>Retry attempts: 3<br/>Processing time: 5s avg]

        MAIN_Q --> PROC
        PROC -->|Success 95%| MAIN_Q
        PROC -->|Failure 5%| DLQ
    end

    subgraph "DLQ Performance Impact"
        IMPACT1[Processing overhead<br/>Receive count tracking<br/>Message redirection<br/>Additional API calls]

        IMPACT2[Performance metrics<br/>Success path: 50ms latency<br/>Failure path: 200ms latency<br/>DLQ overhead: 20ms<br/>Storage cost: +10%]

        IMPACT1 --> IMPACT2
    end

    subgraph "DLQ Analysis and Recovery"
        ANALYSIS[Message analysis<br/>Failure pattern detection<br/>Error categorization<br/>Root cause identification]

        RECOVERY[Recovery strategies<br/>Message replay<br/>Format correction<br/>Manual processing<br/>Discard decision]

        DLQ --> ANALYSIS --> RECOVERY
    end

    classDef queueStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef processStyle fill:#10B981,stroke:#059669,color:#fff
    classDef impactStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef analysisStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class MAIN_Q,DLQ queueStyle
    class PROC processStyle
    class IMPACT1,IMPACT2 impactStyle
    class ANALYSIS,RECOVERY analysisStyle
```

### DLQ Strategy Comparison

```mermaid
graph LR
    subgraph "Immediate DLQ Transfer"
        IMMEDIATE1[Configuration<br/>Max receive count: 1<br/>No retry attempts<br/>Fast failure detection<br/>Low processing cost]

        IMMEDIATE2[Use cases<br/>Format validation<br/>Schema violations<br/>Poison messages<br/>Fast debugging]

        IMMEDIATE1 --> IMMEDIATE2
    end

    subgraph "Retry with Exponential Backoff"
        RETRY1[Configuration<br/>Max receive count: 5<br/>Visibility timeout: Progressive<br/>30s, 60s, 120s, 300s<br/>Higher processing cost]

        RETRY2[Use cases<br/>Transient failures<br/>External service timeouts<br/>Network issues<br/>Resource contention]

        RETRY1 --> RETRY2
    end

    subgraph "Hybrid Strategy"
        HYBRID1[Error type classification<br/>Permanent errors: Immediate DLQ<br/>Transient errors: Retry<br/>Classification logic required<br/>Complex but efficient]

        HYBRID2[Implementation<br/>Message attribute analysis<br/>Error code mapping<br/>Dynamic routing<br/>Optimal resource usage]

        HYBRID1 --> HYBRID2
    end

    classDef immediateStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef retryStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef hybridStyle fill:#10B981,stroke:#059669,color:#fff

    class IMMEDIATE1,IMMEDIATE2 immediateStyle
    class RETRY1,RETRY2 retryStyle
    class HYBRID1,HYBRID2 hybridStyle
```

## Netflix's Event-Driven Architecture

### Netflix's SQS/SNS Usage Scale

```mermaid
graph TB
    subgraph "Netflix Event Architecture"
        EVENTS[Event Sources<br/>User interactions: 1B/day<br/>System events: 10B/day<br/>Service communications: 100B/day<br/>Total volume: 111B events/day]

        SNS_TOPICS[SNS Topics<br/>User events: 100 topics<br/>System events: 500 topics<br/>Service events: 1000 topics<br/>Regional replication: 3 regions]

        SQS_QUEUES[SQS Queues<br/>Processing queues: 5000<br/>Dead letter queues: 500<br/>Batch processing: 1000<br/>Real-time: 4000]

        EVENTS --> SNS_TOPICS
        SNS_TOPICS --> SQS_QUEUES
    end

    subgraph "Performance Characteristics"
        PERF1[Throughput metrics<br/>Peak events: 2M/sec<br/>Average events: 1.3M/sec<br/>Processing latency: p95 < 100ms<br/>End-to-end: p95 < 5 seconds]

        PERF2[Reliability metrics<br/>Event delivery: 99.99%<br/>Processing success: 99.5%<br/>DLQ rate: 0.1%<br/>Replay capability: 24 hours]
    end

    subgraph "Cost Optimization"
        COST1[Batching strategies<br/>SQS batch sends: 10 messages<br/>SNS fan-out: Optimized<br/>Long polling: 20 seconds<br/>Reserved capacity: Critical paths]

        COST2[Cost metrics<br/>SQS costs: $50K/month<br/>SNS costs: $30K/month<br/>Lambda triggers: $20K/month<br/>Total messaging: $100K/month]
    end

    classDef eventStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef perfStyle fill:#10B981,stroke:#059669,color:#fff
    classDef costStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class EVENTS,SNS_TOPICS,SQS_QUEUES eventStyle
    class PERF1,PERF2 perfStyle
    class COST1,COST2 costStyle
```

### Critical Architecture Patterns

```mermaid
graph TB
    subgraph "Event Sourcing Pattern"
        ES1[Event store<br/>SNS topic per aggregate<br/>All state changes captured<br/>Immutable event log]

        ES2[Event replay<br/>SQS queues for consumers<br/>Checkpointing supported<br/>Temporal decoupling]

        ES3[Projection building<br/>Multiple materialized views<br/>Eventually consistent<br/>Independent scaling]

        ES1 --> ES2 --> ES3
    end

    subgraph "CQRS Implementation"
        CQRS1[Command handling<br/>Write-side processing<br/>Business logic validation<br/>Event publication]

        CQRS2[Read model updates<br/>Event subscribers<br/>Denormalized views<br/>Query optimization]

        CQRS3[Read/write separation<br/>Independent scaling<br/>Technology diversity<br/>Performance optimization]

        CQRS1 --> CQRS2 --> CQRS3
    end

    subgraph "Saga Orchestration"
        SAGA1[Saga coordinator<br/>Long-running transactions<br/>Compensation actions<br/>State management]

        SAGA2[Step execution<br/>SQS for step commands<br/>SNS for step completion<br/>Error handling]

        SAGA3[Saga recovery<br/>DLQ for failed steps<br/>Manual intervention<br/>Compensation execution]

        SAGA1 --> SAGA2 --> SAGA3
    end

    classDef esStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef cqrsStyle fill:#10B981,stroke:#059669,color:#fff
    classDef sagaStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class ES1,ES2,ES3 esStyle
    class CQRS1,CQRS2,CQRS3 cqrsStyle
    class SAGA1,SAGA2,SAGA3 sagaStyle
```

### Monitoring and Observability

```mermaid
graph LR
    subgraph "SQS Metrics"
        SQS_METRICS[Key metrics<br/>• ApproximateNumberOfMessages<br/>• ApproximateAgeOfOldestMessage<br/>• NumberOfMessagesSent<br/>• NumberOfMessagesReceived<br/>• NumberOfMessagesDeleted]
    end

    subgraph "SNS Metrics"
        SNS_METRICS[Key metrics<br/>• NumberOfMessagesPublished<br/>• NumberOfNotificationsFailed<br/>• NumberOfNotificationsDelivered<br/>• PublishSize<br/>• SMSMonthToDateSpentUSD]
    end

    subgraph "Alerting Strategy"
        ALERTS1[Critical alerts<br/>Queue depth > 10K messages<br/>Message age > 15 minutes<br/>DLQ message count > 0<br/>SNS delivery failure rate > 1%]

        ALERTS2[Capacity alerts<br/>Message rate > 80% of limit<br/>Queue depth growth rate<br/>Processing lag increasing<br/>Cost thresholds exceeded]
    end

    subgraph "Dashboards"
        DASH1[Real-time monitoring<br/>Message flow visualization<br/>Queue depth trends<br/>Error rate tracking<br/>Cost analysis]
    end

    SQS_METRICS --> ALERTS1
    SNS_METRICS --> ALERTS1
    ALERTS1 --> ALERTS2
    ALERTS2 --> DASH1

    classDef metricsStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef alertStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef dashStyle fill:#10B981,stroke:#059669,color:#fff

    class SQS_METRICS,SNS_METRICS metricsStyle
    class ALERTS1,ALERTS2 alertStyle
    class DASH1 dashStyle
```

## Production Lessons Learned

### Performance Optimization Best Practices

1. **Queue Type Selection**: Standard for throughput, FIFO for ordering requirements
2. **Polling Strategy**: Long polling reduces costs by 90% with minimal latency impact
3. **Batching**: Always use maximum batch size (10) for optimal performance/cost
4. **Message Filtering**: Server-side SNS filtering reduces unnecessary processing by 80%
5. **DLQ Strategy**: Configure based on failure types - immediate for permanent errors

### Critical Performance Factors

```mermaid
graph TB
    subgraph "Throughput Optimization"
        THR_OPT1[Batching strategies<br/>• Send/receive in batches of 10<br/>• Use SendMessageBatch API<br/>• Implement client-side batching<br/>• Monitor batch efficiency]
    end

    subgraph "Latency Optimization"
        LAT_OPT1[Polling optimization<br/>• Use long polling (20s)<br/>• Minimize empty receives<br/>• Implement adaptive polling<br/>• Monitor receive latency]
    end

    subgraph "Cost Optimization"
        COST_OPT1[Cost reduction strategies<br/>• Message filtering at SNS<br/>• Optimal visibility timeouts<br/>• Reserved capacity for predictable loads<br/>• DLQ threshold tuning]
    end

    subgraph "Reliability Optimization"
        REL_OPT1[Error handling<br/>• Appropriate DLQ configuration<br/>• Exponential backoff<br/>• Circuit breaker patterns<br/>• Monitoring and alerting]
    end

    classDef optStyle fill:#3B82F6,stroke:#2563EB,color:#fff

    class THR_OPT1,LAT_OPT1,COST_OPT1,REL_OPT1 optStyle
```

### Performance Benchmarks by Configuration

| Configuration | Throughput | Latency p95 | Cost/Million Msgs | Use Case |
|---------------|------------|-------------|-------------------|----------|
| **Standard + Batching** | 30K msg/sec | 50ms | $4 | High throughput |
| **FIFO + Batching** | 3K msg/sec | 100ms | $5 | Ordered processing |
| **SNS Fan-out** | 100K msg/sec | 200ms | $0.5 + delivery | Event distribution |
| **DLQ Enabled** | -10% throughput | +20ms | +10% cost | Reliability |

### Common Pitfalls

1. **Short polling overuse**: Increases costs by 10x without latency benefits
2. **Single message processing**: Reduces throughput by 90% and increases costs
3. **No message filtering**: Wastes processing resources and increases costs
4. **Inappropriate queue types**: Using FIFO when ordering not required
5. **Poor DLQ configuration**: Either too aggressive or too permissive retry policies

**Source**: Based on Netflix, Airbnb, and AWS Well-Architected messaging patterns