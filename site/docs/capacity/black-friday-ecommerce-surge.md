# Black Friday E-commerce Surge - Capacity Planning Model

## Executive Summary

Black Friday represents the ultimate stress test for e-commerce platforms, with traffic surges of 10-50x normal levels concentrated in a 4-hour window. This model provides mathematical frameworks, auto-scaling strategies, and cost optimization techniques for surviving peak shopping events.

**Key Metrics (2023 Data)**:
- Average traffic surge: 15x normal levels
- Peak duration: 4-6 hours (midnight to 6 AM)
- Conversion rate under load: 2.1% (vs 3.8% normal)
- Cart abandonment spike: 68% (vs 23% normal)
- Infrastructure cost spike: $2.3M for 24 hours

## Mathematical Capacity Models

### 1. Traffic Surge Prediction Model

```python
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class BlackFridayCapacityModel:
    def __init__(self, baseline_rps=1000):
        self.baseline_rps = baseline_rps
        self.surge_multipliers = {
            'pre_week': 1.2,      # Week before
            'thursday': 2.5,       # Thanksgiving
            'midnight_peak': 15.0, # 12-2 AM
            'morning_peak': 12.0,  # 6-10 AM
            'afternoon': 8.0,      # 12-4 PM
            'evening': 6.0,        # 6-10 PM
            'recovery': 2.0        # Weekend after
        }

    def calculate_required_capacity(self, time_window='midnight_peak'):
        """Calculate required capacity for specific time window"""
        multiplier = self.surge_multipliers[time_window]
        required_rps = self.baseline_rps * multiplier

        # Add 30% buffer for unexpected spikes
        buffered_capacity = required_rps * 1.3

        return {
            'baseline_rps': self.baseline_rps,
            'surge_multiplier': multiplier,
            'required_rps': required_rps,
            'buffered_capacity': buffered_capacity,
            'additional_instances_needed': self.calculate_instances(buffered_capacity)
        }

    def calculate_instances(self, target_rps):
        """Calculate required instances based on per-instance capacity"""
        instance_capacity = 100  # RPS per instance
        return int(np.ceil(target_rps / instance_capacity))

    def hourly_traffic_pattern(self):
        """Generate 24-hour traffic pattern for Black Friday"""
        hours = range(24)
        multipliers = [
            15.0, 14.0, 10.0, 8.0, 6.0, 5.0,    # 12-6 AM
            8.0, 10.0, 12.0, 11.0, 9.0, 8.0,    # 6 AM-12 PM
            8.0, 9.0, 10.0, 8.0, 6.0, 7.0,      # 12-6 PM
            8.0, 9.0, 7.0, 5.0, 3.0, 2.0        # 6 PM-12 AM
        ]
        return [(h, self.baseline_rps * m) for h, m in zip(hours, multipliers)]

# Example usage
model = BlackFridayCapacityModel(baseline_rps=5000)
peak_capacity = model.calculate_required_capacity('midnight_peak')
print(f"Peak capacity needed: {peak_capacity['buffered_capacity']:,.0f} RPS")
print(f"Additional instances: {peak_capacity['additional_instances_needed']}")
```

### 2. Database Connection Pool Sizing

```python
class DatabaseCapacityModel:
    def __init__(self, normal_connections=200):
        self.normal_connections = normal_connections

    def calculate_pool_size(self, expected_rps, avg_query_time_ms=50):
        """Calculate optimal connection pool size"""
        # Little's Law: L = λ × W
        # L = connections needed
        # λ = requests per second
        # W = average service time in seconds

        service_time_sec = avg_query_time_ms / 1000
        required_connections = expected_rps * service_time_sec

        # Add buffer for connection overhead and spikes
        buffered_connections = required_connections * 1.4

        return {
            'calculated_connections': required_connections,
            'recommended_pool_size': int(buffered_connections),
            'overhead_factor': 1.4
        }

# Example for Black Friday peak
db_model = DatabaseCapacityModel()
pool_sizing = db_model.calculate_pool_size(expected_rps=75000, avg_query_time_ms=75)
print(f"Recommended pool size: {pool_sizing['recommended_pool_size']}")
```

## Architecture Diagrams

### Complete Black Friday Architecture

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - CDN & Load Balancing]
        CF[Cloudflare CDN<br/>500+ PoPs<br/>95% cache hit]
        ALB[AWS ALB<br/>Auto-scaling enabled<br/>Cross-AZ distribution]
        WAF[AWS WAF<br/>DDoS protection<br/>Rate limiting: 1000 req/min]
    end

    subgraph ServicePlane[Service Plane - Application Layer]
        ASG[Auto Scaling Group<br/>Min: 50, Max: 500<br/>Target: 70% CPU]
        API[API Gateway<br/>10,000 RPS limit<br/>Throttling enabled]

        subgraph Microservices[Microservices Cluster]
            CART[Cart Service<br/>100 instances<br/>Redis sessions]
            ORDER[Order Service<br/>150 instances<br/>PostgreSQL]
            PAY[Payment Service<br/>80 instances<br/>Stripe integration]
            INV[Inventory Service<br/>120 instances<br/>Real-time updates]
            SEARCH[Search Service<br/>60 instances<br/>Elasticsearch]
        end
    end

    subgraph StatePlane[State Plane - Data Layer]
        RDS[RDS PostgreSQL<br/>db.r6g.16xlarge<br/>Multi-AZ, Read replicas]
        REDIS[Redis Cluster<br/>cache.r6g.8xlarge<br/>Sharded across 6 nodes]
        ES[Elasticsearch<br/>r6g.2xlarge × 12<br/>Product catalog index]
        S3[S3 Static Assets<br/>CloudFront integration<br/>Multi-region replication]
    end

    subgraph ControlPlane[Control Plane - Operations]
        CW[CloudWatch<br/>Custom metrics<br/>Auto-scaling triggers]
        PD[PagerDuty<br/>Incident response<br/>On-call rotation]
        DD[DataDog<br/>APM monitoring<br/>Real-time dashboards]
    end

    %% Traffic flow
    Users[10M+ Concurrent Users] --> CF
    CF --> ALB
    ALB --> API
    API --> ASG
    ASG --> CART
    ASG --> ORDER
    ASG --> PAY
    ASG --> INV
    ASG --> SEARCH

    %% Data connections
    CART --> REDIS
    ORDER --> RDS
    PAY --> RDS
    INV --> RDS
    SEARCH --> ES

    %% Static content
    CF --> S3

    %% Monitoring
    CW --> ASG
    DD --> API
    PD --> CW

    %% Apply four-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class CF,ALB,WAF edgeStyle
    class ASG,API,CART,ORDER,PAY,INV,SEARCH serviceStyle
    class RDS,REDIS,ES,S3 stateStyle
    class CW,PD,DD controlStyle
```

### Auto-Scaling Triggers and Thresholds

```mermaid
graph LR
    subgraph Metrics[Monitoring Metrics]
        CPU[CPU Utilization<br/>Target: 70%<br/>Scale-out: 80%<br/>Scale-in: 50%]
        RPS[Requests/Second<br/>Baseline: 5,000<br/>Alert: 50,000<br/>Emergency: 75,000]
        LAT[Response Latency<br/>p95 target: 200ms<br/>Alert: 500ms<br/>Critical: 1000ms]
        ERR[Error Rate<br/>Target: <0.1%<br/>Alert: >1%<br/>Critical: >5%]
    end

    subgraph Actions[Scaling Actions]
        SCALE_OUT[Scale Out<br/>+20% capacity<br/>2-minute cooldown]
        SCALE_IN[Scale In<br/>-10% capacity<br/>15-minute cooldown]
        EMERGENCY[Emergency Scale<br/>+50% capacity<br/>Override limits]
    end

    subgraph Resources[Resource Targets]
        WEB[Web Servers<br/>Min: 50<br/>Max: 500<br/>Current: 150]
        DB[Database<br/>Read replicas<br/>Connection pools<br/>Query optimization]
        CACHE[Cache Layer<br/>Memory scaling<br/>Eviction policies<br/>Warming strategies]
    end

    CPU --> SCALE_OUT
    RPS --> SCALE_OUT
    LAT --> EMERGENCY
    ERR --> EMERGENCY

    SCALE_OUT --> WEB
    SCALE_OUT --> DB
    SCALE_OUT --> CACHE

    SCALE_IN --> WEB

    classDef metricStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef actionStyle fill:#10B981,stroke:#059669,color:#fff
    classDef resourceStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class CPU,RPS,LAT,ERR metricStyle
    class SCALE_OUT,SCALE_IN,EMERGENCY actionStyle
    class WEB,DB,CACHE resourceStyle
```

## Real-World Implementation Examples

### 1. Shopify Black Friday 2023 Configuration

```yaml
# Kubernetes HPA Configuration
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: black-friday-web-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-servers
  minReplicas: 50
  maxReplicas: 500
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: Pods
    pods:
      metric:
        name: requests_per_second
      target:
        type: AverageValue
        averageValue: "100"
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
```

### 2. Database Scaling Configuration

```yaml
# RDS Aurora Auto Scaling
AuroraCluster:
  Type: AWS::RDS::DBCluster
  Properties:
    Engine: aurora-postgresql
    EngineVersion: '14.9'
    DatabaseName: ecommerce
    MasterUsername: admin
    DBClusterParameterGroupName: !Ref AuroraParameterGroup
    VpcSecurityGroupIds:
      - !Ref DatabaseSecurityGroup
    DBSubnetGroupName: !Ref DatabaseSubnetGroup
    BackupRetentionPeriod: 7
    PreferredBackupWindow: "03:00-04:00"
    PreferredMaintenanceWindow: "sun:04:00-sun:05:00"
    DeletionProtection: true
    StorageEncrypted: true

# Auto Scaling for Read Replicas
ReadReplicaAutoScaling:
  Type: AWS::ApplicationAutoScaling::ScalableTarget
  Properties:
    ServiceNamespace: rds
    ResourceId: cluster:aurora-cluster-id
    ScalableDimension: rds:cluster:ReadReplicaCount
    MinCapacity: 2
    MaxCapacity: 15
    RoleArn: !GetAtt AutoScalingRole.Arn

ReadReplicaScalingPolicy:
  Type: AWS::ApplicationAutoScaling::ScalingPolicy
  Properties:
    PolicyName: ReadReplicaCPUScaling
    PolicyType: TargetTrackingScaling
    ScalingTargetId: !Ref ReadReplicaAutoScaling
    TargetTrackingScalingPolicyConfiguration:
      TargetValue: 70.0
      PredefinedMetricSpecification:
        PredefinedMetricType: RDSReaderAverageCPUUtilization
      ScaleOutCooldown: 300
      ScaleInCooldown: 600
```

## Cost Optimization Strategies

### Infrastructure Cost Breakdown

```mermaid
pie title Black Friday Infrastructure Costs (24 hours)
    "Compute (EC2)" : 45
    "Database (RDS)" : 25
    "CDN (CloudFront)" : 15
    "Load Balancers" : 8
    "Monitoring & Logs" : 4
    "Data Transfer" : 3
```

### Cost Calculation Model

```python
class BlackFridayCostModel:
    def __init__(self):
        # AWS pricing (us-east-1, on-demand)
        self.pricing = {
            'ec2_c5_2xlarge': 0.34,      # per hour
            'rds_r6g_16xlarge': 7.68,    # per hour
            'redis_r6g_8xlarge': 5.33,   # per hour
            'alb': 0.0225,               # per hour
            'cloudfront': 0.085,         # per GB
            'data_transfer': 0.09,       # per GB
        }

    def calculate_surge_costs(self, duration_hours=24):
        """Calculate additional costs for Black Friday surge"""
        normal_costs = {
            'compute': 50 * self.pricing['ec2_c5_2xlarge'] * duration_hours,
            'database': 3 * self.pricing['rds_r6g_16xlarge'] * duration_hours,
            'cache': 6 * self.pricing['redis_r6g_8xlarge'] * duration_hours,
            'load_balancer': 4 * self.pricing['alb'] * duration_hours,
        }

        surge_costs = {
            'compute': 400 * self.pricing['ec2_c5_2xlarge'] * duration_hours,
            'database': 8 * self.pricing['rds_r6g_16xlarge'] * duration_hours,
            'cache': 12 * self.pricing['redis_r6g_8xlarge'] * duration_hours,
            'load_balancer': 8 * self.pricing['alb'] * duration_hours,
            'cdn': 50000 * self.pricing['cloudfront'],  # 50TB data transfer
            'bandwidth': 25000 * self.pricing['data_transfer'],  # 25TB
        }

        additional_costs = {}
        for service in normal_costs:
            additional_costs[service] = surge_costs[service] - normal_costs[service]

        additional_costs['cdn'] = surge_costs['cdn']
        additional_costs['bandwidth'] = surge_costs['bandwidth']

        return {
            'normal_24h_cost': sum(normal_costs.values()),
            'surge_24h_cost': sum(surge_costs.values()),
            'additional_cost': sum(additional_costs.values()),
            'breakdown': additional_costs
        }

# Calculate Black Friday costs
cost_model = BlackFridayCostModel()
costs = cost_model.calculate_surge_costs()
print(f"Additional Black Friday costs: ${costs['additional_cost']:,.2f}")
```

## Monitoring and Alerting Setup

### Critical Metrics Dashboard

```yaml
# CloudWatch Custom Metrics
custom_metrics:
  business_metrics:
    - orders_per_minute
    - revenue_per_minute
    - cart_abandonment_rate
    - checkout_completion_rate
    - payment_success_rate

  technical_metrics:
    - response_time_p95
    - error_rate_percentage
    - database_connections_active
    - cache_hit_ratio
    - cpu_utilization_average

  capacity_metrics:
    - requests_per_second
    - concurrent_users
    - queue_depth
    - auto_scaling_events
    - instance_count_current

# PagerDuty Escalation Policy
escalation_policy:
  level_1:
    - on_call_engineer
    - timeout: 5_minutes
  level_2:
    - team_lead
    - senior_engineer
    - timeout: 10_minutes
  level_3:
    - engineering_manager
    - cto
    - timeout: 15_minutes

# Alert Thresholds
alerts:
  critical:
    error_rate: ">5%"
    response_time_p95: ">2000ms"
    orders_per_minute: "<100"  # Should be >1000 during peak

  warning:
    error_rate: ">1%"
    response_time_p95: ">1000ms"
    cpu_utilization: ">80%"
    database_connections: ">80%"
```

## Failure Scenarios and Recovery

### Cascade Failure Prevention

```mermaid
graph TB
    subgraph FailureScenarios[Potential Failure Points]
        DB_FAIL[Database Overload<br/>Connection pool exhaustion<br/>Recovery: 2-5 minutes]
        CACHE_FAIL[Cache Cluster Failure<br/>Redis memory overflow<br/>Recovery: 30 seconds]
        PAY_FAIL[Payment Gateway Timeout<br/>Stripe API limits<br/>Recovery: 1-2 minutes]
        CDN_FAIL[CDN Cache Miss Storm<br/>Origin server overload<br/>Recovery: 5-10 minutes]
    end

    subgraph CircuitBreakers[Circuit Breaker Pattern]
        CB_DB[Database Circuit Breaker<br/>Threshold: 50% errors<br/>Timeout: 30 seconds]
        CB_PAY[Payment Circuit Breaker<br/>Threshold: 20% errors<br/>Timeout: 60 seconds]
        CB_SEARCH[Search Circuit Breaker<br/>Threshold: 30% errors<br/>Timeout: 10 seconds]
    end

    subgraph Fallbacks[Fallback Strategies]
        DB_FALLBACK[Read from Cache<br/>Eventual consistency<br/>Degraded experience]
        PAY_FALLBACK[Queue payments<br/>Process later<br/>Email confirmation]
        SEARCH_FALLBACK[Static results<br/>Popular products<br/>Cached recommendations]
    end

    DB_FAIL --> CB_DB --> DB_FALLBACK
    PAY_FAIL --> CB_PAY --> PAY_FALLBACK
    CACHE_FAIL --> CB_SEARCH --> SEARCH_FALLBACK

    classDef failureStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef breakerStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef fallbackStyle fill:#10B981,stroke:#059669,color:#fff

    class DB_FAIL,CACHE_FAIL,PAY_FAIL,CDN_FAIL failureStyle
    class CB_DB,CB_PAY,CB_SEARCH breakerStyle
    class DB_FALLBACK,PAY_FALLBACK,SEARCH_FALLBACK fallbackStyle
```

## Production Runbook

### Pre-Event Checklist (48 hours before)

1. **Infrastructure Scaling**
   ```bash
   # Scale up databases
   aws rds modify-db-cluster --db-cluster-identifier prod-cluster \
     --apply-immediately --scaling-configuration MinCapacity=8,MaxCapacity=16

   # Pre-warm cache
   redis-cli -h cache-cluster.abc123.cache.amazonaws.com \
     eval "$(cat scripts/cache-warmup.lua)" 0

   # Scale ECS services
   aws ecs update-service --cluster prod --service web-service \
     --desired-count 150
   ```

2. **Circuit Breaker Configuration**
   ```bash
   # Update circuit breaker thresholds
   kubectl apply -f configs/black-friday-circuit-breakers.yaml

   # Verify health checks
   kubectl get pods -l app=web-service | grep Running
   ```

3. **Monitoring Setup**
   ```bash
   # Deploy additional monitoring
   helm upgrade datadog datadog/datadog \
     --set resources.requests.memory=2Gi \
     --set resources.limits.memory=4Gi
   ```

### During Event Response Procedures

#### High Error Rate (>5%)
```bash
# Immediate actions
1. Check application logs
   kubectl logs -l app=web-service --tail=100 | grep ERROR

2. Scale up immediately
   kubectl scale deployment web-service --replicas=300

3. Check database connections
   psql -h prod-db.cluster-xyz.rds.amazonaws.com \
     -c "SELECT count(*) FROM pg_stat_activity;"

4. Activate circuit breakers if needed
   curl -X POST http://admin.internal/circuit-breaker/payment/open
```

#### Database Overload
```bash
# Emergency procedures
1. Scale read replicas
   aws rds create-db-instance --db-instance-identifier read-replica-emergency

2. Enable read-only mode for non-critical features
   redis-cli SET feature:search:enabled false
   redis-cli SET feature:recommendations:enabled false

3. Increase connection pool size
   kubectl patch configmap db-config --patch '{"data":{"max_connections":"800"}}'
```

## Success Metrics and SLAs

### Business Metrics
- **Order completion rate**: >95% (vs 97% normal)
- **Revenue per minute**: >$50,000 during peak hours
- **Cart abandonment**: <70% (vs 23% normal)
- **Payment success rate**: >98%
- **Customer satisfaction**: >4.0/5.0

### Technical SLAs
- **Response time p95**: <500ms for product pages
- **Response time p99**: <1000ms for checkout
- **Uptime**: 99.9% during Black Friday event
- **Error rate**: <1% overall, <0.1% for payments
- **Database query time**: <100ms p95

### Cost Efficiency
- **Cost per order**: <$2.50 (including surge costs)
- **Infrastructure ROI**: >300% (revenue vs. infrastructure costs)
- **Reserved instance utilization**: >85%

## Post-Event Analysis

### Performance Review Template

```python
class BlackFridayAnalysis:
    def __init__(self, metrics_data):
        self.metrics = metrics_data

    def analyze_performance(self):
        """Analyze Black Friday performance metrics"""
        analysis = {
            'peak_traffic': max(self.metrics['rps_timeline']),
            'avg_response_time': np.mean(self.metrics['response_times']),
            'error_rate_peak': max(self.metrics['error_rates']),
            'cost_efficiency': self.calculate_cost_per_order(),
            'scaling_efficiency': self.analyze_scaling_events(),
            'bottlenecks_identified': self.identify_bottlenecks()
        }
        return analysis

    def generate_recommendations(self):
        """Generate recommendations for next year"""
        return {
            'capacity_planning': [
                'Increase database connection pools by 20%',
                'Pre-provision 25% more cache capacity',
                'Implement predictive scaling 2 hours before peak'
            ],
            'cost_optimization': [
                'Use more reserved instances for predictable load',
                'Implement intelligent CDN caching',
                'Optimize database queries identified as slow'
            ],
            'reliability_improvements': [
                'Add chaos engineering tests',
                'Implement progressive traffic shifting',
                'Enhance circuit breaker logic'
            ]
        }
```

This Black Friday capacity planning model provides a comprehensive framework for handling extreme traffic surges with mathematical models, real-world configurations, and battle-tested procedures. The model emphasizes proactive scaling, cost optimization, and failure recovery to ensure business continuity during critical sales events.