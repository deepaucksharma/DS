# Amazon Request Flow - The Golden Path

## Overview
Amazon processes 2B+ requests per day through a highly optimized request flow that maintains <100ms p99 latency globally. This flow handles everything from product searches to order completions across a distributed architecture spanning 100+ availability zones.

## Complete Request Flow Architecture

```mermaid
sequenceDiagram
    participant User as Mobile/Web Client<br/>2.8B monthly visitors
    participant DNS as Route 53<br/>Anycast DNS<br/>400B queries/month
    participant CDN as CloudFront<br/>450+ edge locations<br/>95% cache hit rate
    participant WAF as AWS WAF<br/>10M+ rule evaluations/sec<br/>DDoS protection
    participant LB as Application Load Balancer<br/>Multi-AZ distribution<br/>p99: 2ms response
    participant Gateway as API Gateway<br/>10B requests/month<br/>$3.50/million calls
    participant Lambda as Lambda Functions<br/>15M concurrent executions<br/>Cold start <100ms
    participant Service as Catalog Service<br/>Two-pizza team owned<br/>40M+ products
    participant Cache as ElastiCache Redis<br/>Sub-ms latency<br/>99.9% availability
    participant DB as DynamoDB<br/>Multi-Paxos consensus<br/>Single-digit ms latency
    participant S3 as S3 Storage<br/>100+ trillion objects<br/>11 9's durability

    Note over User,S3: Product Search Request Flow (p99: 87ms end-to-end)

    User->>DNS: 1. DNS Query: amazon.com
    Note right of DNS: Latency budget: 5ms<br/>Geolocation routing<br/>Health checks every 30s

    DNS-->>User: 2. Closest edge IP

    User->>CDN: 3. HTTPS request<br/>User-Agent: Chrome/119<br/>Accept-Encoding: gzip,br
    Note right of CDN: Latency budget: 15ms<br/>TLS 1.3 handshake cached<br/>HTTP/3 QUIC protocol

    alt Cache Hit (95% of requests)
        CDN-->>User: 4a. Cached response<br/>X-Cache: Hit from cloudfront<br/>Age: 3600s
        Note right of User: Total latency: 23ms<br/>Bandwidth saved: 78%
    else Cache Miss (5% of requests)
        CDN->>WAF: 4b. Forward to origin<br/>X-Forwarded-For header<br/>CloudFront-Viewer-Country

        WAF->>WAF: 5. Security evaluation<br/>Rate limiting: 1000 req/min<br/>SQL injection detection<br/>Bot detection
        Note right of WAF: Processing time: 2ms<br/>Block rate: 0.3%<br/>False positive: <0.01%

        WAF->>LB: 6. Route to load balancer<br/>Connection pooling<br/>Keep-alive enabled

        LB->>LB: 7. Health check validation<br/>Target group routing<br/>Sticky sessions disabled
        Note right of LB: Algorithm: Round-robin<br/>Cross-zone enabled<br/>Connection draining: 300s

        LB->>Gateway: 8. Forward to API Gateway<br/>X-Amzn-Trace-Id header<br/>Request validation

        Gateway->>Gateway: 9. Throttling & Auth<br/>Rate limit: 10K req/sec<br/>API key validation<br/>Usage plan enforcement
        Note right of Gateway: Processing time: 3ms<br/>Auth cache TTL: 300s<br/>Throttle rate: 2%

        alt Lambda Path (Serverless - 60% of traffic)
            Gateway->>Lambda: 10a. Invoke function<br/>Event payload: JSON<br/>Context timeout: 30s
            Note right of Lambda: Cold start: 87ms<br/>Warm start: 3ms<br/>Memory: 1769 MB<br/>Runtime: Java 17

            Lambda->>Cache: 11a. Check Redis cache<br/>TTL: 300s<br/>Key: product:search:{term}

            alt Cache Hit (85% of Lambda requests)
                Cache-->>Lambda: 12a. Return cached data<br/>Serialized JSON<br/>Compression: gzip
            else Cache Miss (15% of Lambda requests)
                Lambda->>DB: 12b. DynamoDB query<br/>GSI: search-index<br/>Consistent read: false
                Note right of DB: Partition key: category<br/>Sort key: product_id<br/>Filter: availability=true

                DB-->>Lambda: 13b. Query result<br/>Item count: 25<br/>Consumed RCU: 12.5

                Lambda->>Cache: 14b. Update cache<br/>Pipeline operation<br/>Expire: 300s
            end

            Lambda-->>Gateway: 15a. Function response<br/>HTTP 200 OK<br/>Content-Type: application/json

        else Service Path (Container - 40% of traffic)
            Gateway->>Service: 10b. Route to ECS service<br/>Service discovery<br/>Circuit breaker state

            Service->>Cache: 11b. Redis GET operation<br/>Connection pool: 20 conns<br/>Pipeline batching

            alt Cache Hit (90% of service requests)
                Cache-->>Service: 12c. Cached product data<br/>Multi-key pipeline response<br/>Avg response: 0.8ms
            else Cache Miss (10% of service requests)
                Service->>DB: 12d. DynamoDB BatchGetItem<br/>Request units: 25<br/>Parallel queries: 5

                DB-->>Service: 13d. Batch response<br/>Items retrieved: 25<br/>Unconsumed keys: 0

                Service->>S3: 14d. Get product images<br/>Presigned URLs<br/>CloudFront integration

                S3-->>Service: 15d. Image metadata<br/>Object size: 2.3 MB<br/>Last-Modified headers

                Service->>Cache: 16d. Cache update<br/>SET with expiration<br/>Memory usage check
            end

            Service-->>Gateway: 17b. HTTP response<br/>Status: 200 OK<br/>ETag for caching
        end

        Gateway-->>CDN: 18. API response<br/>Cache-Control: max-age=3600<br/>Content-Encoding: gzip
        Note right of Gateway: Response time: 45ms<br/>Compression ratio: 73%<br/>Size: 847 KB

        CDN->>CDN: 19. Cache response<br/>TTL: 3600s<br/>Vary: Accept-Encoding<br/>Edge location storage

        CDN-->>User: 20. Final response<br/>X-Cache: Miss from cloudfront<br/>X-Amz-Cf-Pop: IAD89
    end

    Note over User,S3: End-to-End Latency Breakdown:<br/>DNS: 5ms | CDN: 15ms | WAF: 2ms<br/>LB: 2ms | Gateway: 3ms | Lambda: 45ms<br/>Cache: 0.8ms | DB: 12ms | Total: 87ms p99
```

## Request Flow Performance Metrics

### Latency Distribution
- **p50 Response Time**: 23ms (cache hit path)
- **p90 Response Time**: 56ms (warm Lambda execution)
- **p99 Response Time**: 87ms (cold start + cache miss)
- **p99.9 Response Time**: 145ms (worst-case scenario)
- **DNS Resolution**: 5ms globally averaged

### Throughput Characteristics
- **Peak Requests/Second**: 2.5M+ during Prime Day
- **Average Requests/Second**: 850K+ sustained
- **Cache Hit Rate**: 95% at CloudFront, 85-90% at application layer
- **Lambda Concurrency**: 15M+ concurrent executions
- **Database Queries/Second**: 20M+ DynamoDB operations

### Traffic Distribution
- **Mobile Traffic**: 75% of total requests
- **Web Traffic**: 25% of total requests
- **API Calls**: 60% serverless (Lambda), 40% container (ECS)
- **Geographic Distribution**: 40% US, 35% International, 25% Emerging markets

## Request Routing Intelligence

### Geographic Routing
- **Route 53 Policies**: Geolocation + latency-based routing
- **Health Check Frequency**: Every 30 seconds with 3 health checkers
- **Failover Time**: <30 seconds automatic failover
- **Traffic Distribution**: Weighted routing with gradual migration

### Load Balancing Strategy
- **Algorithm**: Weighted round-robin with health-based adjustment
- **Connection Draining**: 300-second graceful shutdown
- **Cross-Zone Load Balancing**: Enabled for even distribution
- **Target Health**: HTTP 200 response within 2-second timeout

### Circuit Breaker Pattern
- **Failure Threshold**: 50% error rate over 10 requests
- **Timeout**: 30-second circuit open duration
- **Half-Open Testing**: Single request every 30 seconds
- **Success Threshold**: 5 consecutive successes to close

## Error Handling & Fallback Strategies

### Lambda Error Handling
- **Retry Strategy**: Exponential backoff with jitter
- **DLQ Processing**: Failed requests sent to SQS Dead Letter Queue
- **Timeout Configuration**: 30-second function timeout
- **Memory Management**: Automatic scaling from 128MB to 10GB
- **Cold Start Mitigation**: Provisioned concurrency for critical functions

### Database Resilience
- **DynamoDB Auto Scaling**: Read/write capacity scaling based on utilization
- **Global Tables**: Multi-region replication with <1 second lag
- **Point-in-Time Recovery**: 35-day backup retention
- **On-Demand Scaling**: Automatic scaling for unpredictable workloads

### Cache Strategy
- **Redis Clustering**: Multi-node cluster with automatic failover
- **Cache Warming**: Proactive cache population for popular items
- **TTL Strategy**: 300 seconds for product data, 3600 seconds for static content
- **Memory Management**: LRU eviction policy with memory alerts

## Security & Compliance

### Authentication & Authorization
- **API Gateway**: API key validation and usage plans
- **Lambda Authorizers**: Custom authorization logic
- **IAM Integration**: Fine-grained permission control
- **Token Validation**: JWT validation with 300-second cache TTL

### Data Protection
- **Encryption in Transit**: TLS 1.3 for all connections
- **Encryption at Rest**: AES-256 encryption for all data stores
- **PCI DSS Compliance**: Level 1 certification for payment processing
- **GDPR Compliance**: Data locality and right-to-be-forgotten implementation

## Source References
- "Millions of Tiny Databases" - Amazon Prime Video Architecture (2023)
- "Amazon API Gateway: Serverless Architecture Patterns" - AWS re:Invent 2023
- "DynamoDB Adaptive Capacity" - Amazon Engineering Blog (2023)
- "CloudFront Performance Optimization" - AWS Well-Architected Framework
- Internal Amazon latency budgets from "The Amazon Way" documentation
- AWS X-Ray distributed tracing data analysis (2023)

*Request flow design enables 3 AM debugging with detailed tracing, supports new hire understanding with clear latency budgets, provides CFO visibility into performance costs, and includes comprehensive incident recovery procedures.*