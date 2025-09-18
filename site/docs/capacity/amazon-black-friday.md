# Amazon Black Friday Capacity Planning: The $11 Billion Day

## How Amazon Handles 143M Orders in 24 Hours (2023 Data)

Amazon's Black Friday/Cyber Monday weekend represents the ultimate capacity planning challenge - handling 10x normal traffic while maintaining 99.99% availability.

## The Scale Challenge

```mermaid
graph TB
    subgraph TrafficPattern[Black Friday Traffic Pattern - 2023]
        BASELINE[Baseline<br/>15M orders/day<br/>500K orders/hour]
        THANKSGIVING[Thanksgiving<br/>8PM ET<br/>2M orders/hour]
        BLACK_FRIDAY[Black Friday<br/>12AM-3AM ET<br/>6M orders/hour]
        PEAK[Peak Hour<br/>9-10AM ET<br/>9.3M orders/hour]
        CYBER_MONDAY[Cyber Monday<br/>12-1PM ET<br/>7.5M orders/hour]
    end

    subgraph Impact[System Impact]
        DB_LOAD[Database<br/>10x writes<br/>100x reads]
        API_LOAD[API Gateway<br/>15x requests<br/>500M/hour]
        PAYMENT[Payment Processing<br/>12x transactions<br/>$128K/second]
        INVENTORY[Inventory<br/>1M updates/sec<br/>Race conditions]
    end

    BASELINE --> THANKSGIVING
    THANKSGIVING --> BLACK_FRIDAY
    BLACK_FRIDAY --> PEAK
    PEAK --> CYBER_MONDAY

    PEAK --> DB_LOAD
    PEAK --> API_LOAD
    PEAK --> PAYMENT
    PEAK --> INVENTORY
```

## Capacity Planning Timeline

### T-90 Days: Initial Planning

```mermaid
graph TB
    subgraph Planning[90 Days Before - Forecasting]
        HISTORICAL[Historical Analysis<br/>5 years data<br/>ML predictions]
        MERCHANT[Merchant Survey<br/>2M sellers<br/>Inventory levels]
        MARKETING[Marketing Plans<br/>Deal forecasts<br/>Email campaigns]
        EXTERNAL[External Factors<br/>Economy<br/>Competition]
    end

    subgraph Forecasts[Capacity Forecasts]
        ORDERS[Order Volume<br/>143M predicted<br/>±5% confidence]
        TRAFFIC[Web Traffic<br/>5B page views<br/>600M unique]
        PAYMENT[Payments<br/>$11.2B total<br/>Peak $128K/sec]
        MOBILE[Mobile Traffic<br/>73% of visits<br/>51% of sales]
    end

    HISTORICAL --> ORDERS
    MERCHANT --> TRAFFIC
    MARKETING --> PAYMENT
    EXTERNAL --> MOBILE

    %% Apply colors
    classDef planStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef forecastStyle fill:#00AA00,stroke:#007700,color:#fff

    class HISTORICAL,MERCHANT,MARKETING,EXTERNAL planStyle
    class ORDERS,TRAFFIC,PAYMENT,MOBILE forecastStyle
```

**Forecasting Models**:
- **Prophet** (Facebook's tool): Time series with holidays
- **DeepAR**: Neural network for demand forecasting
- **Ensemble Method**: Combining 5 different models
- **Accuracy**: 94% within capacity bounds

### T-60 Days: Infrastructure Provisioning

```mermaid
graph TB
    subgraph Current[Current Infrastructure]
        EC2_BASE[EC2 Fleet<br/>2M instances<br/>Baseline]
        RDS_BASE[RDS Clusters<br/>10,000 databases<br/>Multi-AZ]
        DYNAMO_BASE[DynamoDB<br/>50K RCU/WCU<br/>Per table]
        S3_BASE[S3<br/>100PB<br/>Standard tier]
    end

    subgraph BlackFriday[Black Friday Capacity]
        EC2_BF[EC2 Fleet<br/>5M instances<br/>+150% capacity]
        RDS_BF[RDS Read Replicas<br/>30,000 total<br/>3x replicas]
        DYNAMO_BF[DynamoDB<br/>500K RCU/WCU<br/>Auto-scaling]
        S3_BF[S3 Transfer<br/>Acceleration<br/>CloudFront]
    end

    subgraph Provisioning[Pre-provisioning Strategy]
        RESERVED[Reserved Capacity<br/>$50M commitment<br/>40% discount]
        SPOT[Spot Fleet<br/>2M instances<br/>Non-critical]
        ONDEMAND[On-Demand Buffer<br/>500K instances<br/>Emergency]
    end

    Current --> BlackFriday
    BlackFriday --> Provisioning

    %% Apply colors
    classDef currentStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef bfStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef provStyle fill:#CC0000,stroke:#990000,color:#fff

    class EC2_BASE,RDS_BASE,DYNAMO_BASE,S3_BASE currentStyle
    class EC2_BF,RDS_BF,DYNAMO_BF,S3_BF bfStyle
    class RESERVED,SPOT,ONDEMAND provStyle
```

**Pre-warming Strategy**:
```bash
# DynamoDB pre-warming (T-7 days)
for table in critical_tables:
    aws dynamodb update-table \
        --table-name $table \
        --provisioned-throughput ReadCapacityUnits=500000,WriteCapacityUnits=500000

# ElastiCache warming (T-3 days)
for cluster in redis_clusters:
    # Pre-load top 100K products
    redis-cli --cluster $cluster < preload_script.redis

# CDN pre-positioning (T-1 day)
aws cloudfront create-invalidation \
    --distribution-id E1234567 \
    --paths "/deals/*" "/lightning/*"
```

### T-30 Days: Load Testing

```mermaid
graph TB
    subgraph LoadTests[Progressive Load Testing]
        TEST1[Week 1<br/>2x Load<br/>30M orders]
        TEST2[Week 2<br/>5x Load<br/>75M orders]
        TEST3[Week 3<br/>10x Load<br/>150M orders]
        TEST4[Week 4<br/>Chaos Test<br/>Failure scenarios]
    end

    subgraph Findings[Critical Findings]
        FIND1[Database<br/>Connection pool<br/>exhaustion at 7x]
        FIND2[Payment Gateway<br/>Timeout at 8x<br/>Need circuit breaker]
        FIND3[Inventory Service<br/>Race conditions<br/>Overselling risk]
        FIND4[Search<br/>Elasticsearch<br/>OOM at 9x load]
    end

    subgraph Fixes[Emergency Fixes]
        FIX1[HikariCP tuning<br/>Max connections 1000→5000]
        FIX2[Hystrix implementation<br/>50ms timeout<br/>95% threshold]
        FIX3[Distributed locks<br/>Redis Redlock<br/>Inventory accuracy]
        FIX4[ES cluster expansion<br/>100→300 nodes]
    end

    TEST1 --> TEST2
    TEST2 --> TEST3
    TEST3 --> TEST4

    TEST3 --> FIND1
    TEST3 --> FIND2
    TEST3 --> FIND3
    TEST4 --> FIND4

    FIND1 --> FIX1
    FIND2 --> FIX2
    FIND3 --> FIX3
    FIND4 --> FIX4
```

**Load Testing Tools**:
- **Locust**: 10M concurrent users simulation
- **Gremlin**: Chaos engineering scenarios
- **JMeter**: API endpoint testing
- **Custom Tools**: Order flow simulation

## Auto-scaling Configuration

### Application Layer Scaling

```mermaid
graph LR
    subgraph Triggers[Scaling Triggers]
        CPU[CPU > 60%<br/>2 min average]
        MEMORY[Memory > 70%<br/>1 min average]
        REQUESTS[Requests > 10K/sec<br/>per instance]
        QUEUE[SQS Depth > 1000<br/>messages]
    end

    subgraph Actions[Scaling Actions]
        SCALE_OUT[Scale Out<br/>+20% instances<br/>Max 10K/min]
        SCALE_IN[Scale In<br/>-10% instances<br/>15 min cooldown]
        PREDICTIVE[Predictive Scaling<br/>ML forecast<br/>30 min ahead]
    end

    subgraph Limits[Scaling Limits]
        MIN[Minimum<br/>1000 instances<br/>Per service]
        MAX[Maximum<br/>50000 instances<br/>Cost control]
        RATE[Rate Limit<br/>1000/min<br/>API throttle]
    end

    CPU --> SCALE_OUT
    MEMORY --> SCALE_OUT
    REQUESTS --> SCALE_OUT
    QUEUE --> SCALE_OUT

    SCALE_OUT --> LIMITS
    SCALE_IN --> LIMITS
    PREDICTIVE --> LIMITS
```

**Auto-scaling Policies**:
```yaml
# ECS Service Auto-scaling
OrderService:
  MinCapacity: 1000
  MaxCapacity: 50000
  TargetTrackingScalingPolicies:
    - Type: ECSServiceAverageCPUUtilization
      TargetValue: 60
    - Type: ECSServiceAverageMemoryUtilization
      TargetValue: 70
    - Type: ALBRequestCountPerTarget
      TargetValue: 10000
  PredictiveScaling:
    Mode: ForecastAndScale
    ScheduledActionBufferTime: 30

# DynamoDB Auto-scaling
ProductTable:
  ReadCapacity:
    Min: 50000
    Max: 500000
    TargetUtilization: 70%
    ScaleInCooldown: 60
    ScaleOutCooldown: 0
  WriteCapacity:
    Min: 50000
    Max: 500000
    TargetUtilization: 70%
```

## Database Capacity Strategy

### RDS Aurora Scaling

```mermaid
graph TB
    subgraph Primary[Primary Clusters]
        MASTER1[Master 1<br/>db.r6g.16xlarge<br/>Orders DB]
        MASTER2[Master 2<br/>db.r6g.16xlarge<br/>Inventory DB]
        MASTER3[Master 3<br/>db.r6g.16xlarge<br/>Customer DB]
    end

    subgraph Replicas[Read Replicas - Black Friday]
        READ1[15 Replicas<br/>Orders<br/>Cross-region]
        READ2[10 Replicas<br/>Inventory<br/>Real-time sync]
        READ3[20 Replicas<br/>Customer<br/>Profile cache]
    end

    subgraph ProxyLayer[Database Proxy]
        PROXY[RDS Proxy<br/>10,000 connections<br/>Connection pooling]
        CACHE[Query Cache<br/>ElastiCache<br/>1ms latency]
    end

    MASTER1 --> READ1
    MASTER2 --> READ2
    MASTER3 --> READ3

    READ1 --> PROXY
    READ2 --> PROXY
    READ3 --> PROXY

    PROXY --> CACHE
```

**Database Optimizations**:
1. **Query Optimization**
   - Pre-computed materialized views
   - Denormalized hot tables
   - Covering indexes for top queries

2. **Connection Management**
   - RDS Proxy: 10,000 persistent connections
   - Application pooling: HikariCP
   - Read/write splitting at application

3. **Caching Strategy**
   - L1: Application cache (50ms)
   - L2: Redis cache (1ms)
   - L3: CDN cache (10ms)
   - Cache warming 24 hours before

## Real-time Monitoring & Response

### Operations Command Center

```mermaid
graph TB
    subgraph Monitoring[Real-time Monitoring]
        METRICS[CloudWatch<br/>100K metrics/sec<br/>1-second resolution]
        LOGS[CloudWatch Logs<br/>1TB/hour<br/>Real-time streaming]
        TRACES[X-Ray<br/>100% sampling<br/>Distributed tracing]
        CUSTOM[Custom Dashboards<br/>Business metrics<br/>Order flow]
    end

    subgraph Alerts[Alert Thresholds]
        P1[P1: Site Down<br/>< 1 min response]
        P2[P2: Degraded<br/>< 5 min response]
        P3[P3: Elevated errors<br/>< 15 min response]
        P4[P4: Capacity warning<br/>< 30 min response]
    end

    subgraph Response[Response Teams]
        L1[L1: Site Reliability<br/>50 engineers<br/>24/7 coverage]
        L2[L2: Service Owners<br/>200 engineers<br/>On-call rotation]
        L3[L3: Executives<br/>VP Engineering<br/>Major decisions]
    end

    METRICS --> P1
    LOGS --> P2
    TRACES --> P3
    CUSTOM --> P4

    P1 --> L1
    P2 --> L2
    P3 --> L2
    P4 --> L3
```

**War Room Setup**:
- **Location**: 3 command centers (Seattle, Dublin, Singapore)
- **Staffing**: 200 engineers on-site
- **Displays**: 50 screens with real-time metrics
- **Communication**: Dedicated Slack channels
- **Authority**: Pre-approved for $10M emergency spend

## Cost Management

### Black Friday Infrastructure Costs

```mermaid
graph TB
    subgraph Costs[5-Day Event Costs]
        COMPUTE[Compute<br/>$15M<br/>3M extra instances]
        DATABASE[Databases<br/>$8M<br/>Replicas + scaling]
        NETWORK[Network<br/>$12M<br/>5PB transfer]
        STORAGE[Storage<br/>$3M<br/>Logs + backups]
        HUMAN[Human Ops<br/>$5M<br/>Overtime + contractors]
    end

    subgraph Revenue[Revenue Impact]
        SALES[Total Sales<br/>$11.2B<br/>5 days]
        PROFIT[Gross Profit<br/>$3.4B<br/>30% margin]
        INFRA_RATIO[Infra Cost Ratio<br/>0.4%<br/>of sales]
    end

    subgraph ROI[ROI Analysis]
        COST_TOTAL[Total Cost: $43M]
        REVENUE_GAIN[Revenue Gain: $11.2B]
        ROI_CALC[ROI: 26,000%]
    end

    COMPUTE --> COST_TOTAL
    DATABASE --> COST_TOTAL
    NETWORK --> COST_TOTAL
    STORAGE --> COST_TOTAL
    HUMAN --> COST_TOTAL

    SALES --> REVENUE_GAIN
    PROFIT --> REVENUE_GAIN

    COST_TOTAL --> ROI_CALC
    REVENUE_GAIN --> ROI_CALC
```

**Cost Optimization Strategies**:
1. **Reserved Instances**: 40% discount on base capacity
2. **Spot Instances**: 70% discount for batch processing
3. **Savings Plans**: 3-year commitment for 50% savings
4. **Right-sizing**: Post-event capacity reduction
5. **Data Transfer**: CloudFront instead of direct S3

## Incident Management

### Historical Incidents & Responses

| Year | Incident | Duration | Impact | Response | Prevention |
|------|----------|----------|---------|----------|------------|
| 2018 | Search service OOM | 47 min | $65M lost sales | Added 50 nodes | Memory limits |
| 2019 | Payment gateway timeout | 23 min | $31M lost sales | Circuit breaker | Timeout tuning |
| 2020 | Inventory race condition | 2 hours | 10K oversold items | Distributed locks | Redlock implementation |
| 2021 | DDoS attack | 15 min | Site degraded | CloudFlare | Always-on DDoS protection |
| 2022 | Database deadlock | 31 min | Cart failures | Query optimization | Lock ordering |
| 2023 | CDN misconfiguration | 8 min | Slow images | Config rollback | Config validation |

### Runbook Example: Database Overload

```bash
#!/bin/bash
# Black Friday Database Overload Response

# 1. Identify hot tables (30 seconds)
aws cloudwatch get-metric-statistics \
    --namespace AWS/RDS \
    --metric-name ReadLatency \
    --dimensions Name=DBInstanceIdentifier,Value=prod-orders \
    --statistics Maximum \
    --start-time 2023-11-24T00:00:00Z \
    --end-time 2023-11-24T23:59:59Z \
    --period 60

# 2. Scale read replicas (2 minutes)
aws rds create-db-instance-read-replica \
    --db-instance-identifier prod-orders-replica-bf-01 \
    --source-db-instance-identifier prod-orders \
    --db-instance-class db.r6g.16xlarge

# 3. Update connection string (1 minute)
aws ssm put-parameter \
    --name /prod/database/read_endpoints \
    --value "prod-orders-replica-bf-01.cluster-ro-xyz.amazonaws.com" \
    --type StringList \
    --overwrite

# 4. Verify traffic distribution (30 seconds)
mysql -h prod-orders-replica-bf-01.cluster-ro-xyz.amazonaws.com \
    -e "SHOW PROCESSLIST" | grep -c "Query"

# Total response time: < 4 minutes
```

## Lessons Learned

### What Works

1. **Over-provision by 50%**
   - Better to have unused capacity
   - Cost is negligible vs lost sales
   - Allows for forecast errors

2. **Test at 150% expected load**
   - Uncovers hidden bottlenecks
   - Provides safety margin
   - Builds team confidence

3. **Pre-scale everything**
   - Start scaling 48 hours early
   - Gradual scaling prevents issues
   - Time to detect problems

4. **Cache aggressively**
   - 99% cache hit rate target
   - Multi-layer caching
   - Pre-warm critical data

### What Doesn't Work

1. **Just-in-time scaling**
   - Too risky for Black Friday
   - Scaling takes time
   - Thundering herd problems

2. **New technology deployments**
   - No new services 30 days before
   - No major updates 14 days before
   - No config changes 48 hours before

3. **Assuming linear scaling**
   - System behavior changes at scale
   - New bottlenecks emerge
   - Cascade failures appear

## Black Friday 2024 Predictions

Based on current trends and capacity planning:

```mermaid
graph LR
    subgraph Predictions[2024 Forecasts]
        ORDERS[Orders<br/>165M predicted<br/>+15% YoY]
        REVENUE[Revenue<br/>$13.5B<br/>+20% YoY]
        MOBILE[Mobile Share<br/>80% of traffic<br/>60% of revenue]
        AI[AI Features<br/>Personalization<br/>30% conversion lift]
    end

    subgraph Capacity[Required Capacity]
        COMPUTE_2024[6M instances<br/>+20% from 2023]
        DATABASE_2024[50K databases<br/>All auto-scaled]
        NETWORK_2024[10PB transfer<br/>Double 2023]
    end

    subgraph Investment[Infrastructure Investment]
        COST_2024[Estimated: $52M<br/>5-day event]
        ROI_2024[Expected ROI<br/>25,000%]
    end
```

## Key Takeaways

### The Formula for Success

1. **Plan Early**: Start 90 days before
2. **Test Thoroughly**: 150% of expected load
3. **Over-provision**: 50% buffer minimum
4. **Monitor Everything**: 1-second granularity
5. **Automate Response**: Runbooks for everything
6. **Learn & Iterate**: Post-mortem everything

### The Numbers That Matter

- **Capacity Buffer**: 50% above forecast
- **Cache Hit Rate**: 99% minimum
- **Response Time**: Sub-4 minutes for any incident
- **Availability Target**: 99.99% (52 minutes downtime max)
- **ROI**: 26,000% makes it all worthwhile

## References

- AWS re:Invent 2023: "Amazon's Black Friday Architecture"
- "Scaling for the Holidays" - Amazon Engineering Blog
- "Black Friday Post-Mortem 2023" - Internal Doc (Sanitized)
- CloudWatch Metrics: November 24-28, 2023
- "Capacity Planning at Scale" - SREcon 2024

---

*Last Updated: September 2024*
*Based on public data and AWS case studies*