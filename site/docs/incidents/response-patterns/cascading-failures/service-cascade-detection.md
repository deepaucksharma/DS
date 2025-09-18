# Service Cascading Failure Detection and Response

> **3 AM Emergency Protocol**: Service cascade failures can take down entire platforms within minutes. This diagram shows exactly what to look for and how to stop the cascade.

## Quick Detection Checklist
- [ ] Check service mesh error rates: `kubectl get vs -o wide | grep -E "5[0-9][0-9]"`
- [ ] Monitor connection pool exhaustion: `netstat -an | grep TIME_WAIT | wc -l`
- [ ] Watch circuit breaker status: `curl http://service-health/hystrix.stream`
- [ ] Alert on cascade patterns: Error rate > 10% AND latency > 2x baseline

## Cascade Detection Flow

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - Detection]
        LB[Load Balancer<br/>nginx/HAProxy<br/>Check: upstream_response_time]
        WAF[WAF/CDN<br/>CloudFlare/AWS<br/>Monitor: origin_errors]
    end

    subgraph ServicePlane[Service Plane - Propagation]
        API[API Gateway<br/>Kong/Ambassador<br/>Watch: circuit_breaker_state]
        AUTH[Auth Service<br/>p99: 50ms → 2000ms<br/>ERROR: jwt_validation_timeout]
        ORDER[Order Service<br/>p99: 100ms → 5000ms<br/>ERROR: downstream_dependency_failure]
        PAY[Payment Service<br/>p99: 200ms → TIMEOUT<br/>ERROR: connection_pool_exhausted]
        INV[Inventory Service<br/>Status: Circuit OPEN<br/>ERROR: max_connections_reached]
    end

    subgraph StatePlane[State Plane - Bottlenecks]
        REDIS[(Redis Cluster<br/>Connections: 1000/1000<br/>ERROR: MAXCLIENTS reached)]
        DB[(PostgreSQL<br/>Active: 95/100 connections<br/>ERROR: too many connections)]
        QUEUE[(Message Queue<br/>RabbitMQ depth: 10M<br/>ERROR: queue_overflow)]
    end

    subgraph ControlPlane[Control Plane - Response]
        MONITOR[Monitoring<br/>Prometheus/DataDog<br/>ALERT: cascade_detected]
        ALERT[Alert Manager<br/>PagerDuty escalation<br/>ACTION: emergency_response]
        AUTO[Auto-Remediation<br/>Circuit breakers<br/>ACTION: graceful_degradation]
    end

    %% Cascade Flow
    LB -.->|"503 errors > 5%"| API
    API -->|"Auth timeout 2s"| AUTH
    AUTH -.->|"JWT validation fails"| ORDER
    ORDER -.->|"Payment timeout"| PAY
    PAY -.->|"Pool exhausted"| INV

    %% State Dependencies
    AUTH -.->|"Cache miss cascade"| REDIS
    ORDER -->|"DB connection starvation"| DB
    PAY -.->|"Queue backup"| QUEUE

    %% Detection Signals
    AUTH -.->|"latency_spike_alert"| MONITOR
    DB -.->|"connection_pool_alert"| MONITOR
    QUEUE -.->|"depth_alert"| MONITOR
    MONITOR -->|"cascade_pattern"| ALERT
    ALERT -->|"trigger_circuit_breakers"| AUTO

    %% 4-plane styling
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class LB,WAF edgeStyle
    class API,AUTH,ORDER,PAY,INV serviceStyle
    class REDIS,DB,QUEUE stateStyle
    class MONITOR,ALERT,AUTO controlStyle
```

## 3 AM Response Commands

### 1. Immediate Detection (30 seconds)
```bash
# Check overall health
curl -s http://health-endpoint/status | jq '.services[] | select(.status != "healthy")'

# Monitor error rates
kubectl top pods --selector=tier=service | grep -E "CPU|Memory"

# Check circuit breaker status
curl -s http://hystrix-dashboard/api/circuit-breakers | jq '.[] | select(.state != "CLOSED")'
```

### 2. Stop the Cascade (60 seconds)
```bash
# Enable circuit breakers manually
kubectl patch deployment auth-service -p '{"spec":{"template":{"metadata":{"annotations":{"circuit-breaker":"OPEN"}}}}}'

# Scale up critical services
kubectl scale deployment auth-service --replicas=20
kubectl scale deployment order-service --replicas=15

# Drain problematic nodes
kubectl drain node-xyz --ignore-daemonsets --delete-emptydir-data
```

### 3. Database Protection (90 seconds)
```bash
# Check DB connections
psql -h db-host -c "SELECT state, count(*) FROM pg_stat_activity GROUP BY state;"

# Enable read-only mode if needed
psql -h db-host -c "ALTER SYSTEM SET default_transaction_read_only = on; SELECT pg_reload_conf();"

# Clear connection pools
pgbouncer -R /etc/pgbouncer/pgbouncer.ini
```

## Error Message Patterns

### Redis Connection Exhaustion
```
ERROR: MAXCLIENTS Redis connection limit reached
LOCATION: /var/log/redis/redis-server.log
ACTION: Increase maxclients or kill idle connections
COMMAND: redis-cli CONFIG SET maxclients 20000
```

### Database Connection Pool
```
ERROR: FATAL: too many connections for role "app_user"
LOCATION: PostgreSQL logs, application logs
ACTION: Scale connection pools or enable read replicas
COMMAND: kubectl scale deployment pgbouncer --replicas=5
```

### Circuit Breaker Activation
```
ERROR: CircuitBreakerOpenException: auth-service
LOCATION: Application logs, service mesh logs
ACTION: Check downstream health, consider manual bypass
COMMAND: curl -X POST http://circuit-breaker/force-close/auth-service
```

## Recovery Checklist

### Phase 1: Immediate (0-5 minutes)
- [ ] Activate all circuit breakers
- [ ] Scale up healthy services 2x
- [ ] Enable graceful degradation modes
- [ ] Notify all stakeholders

### Phase 2: Stabilize (5-15 minutes)
- [ ] Clear Redis connection pools
- [ ] Restart unhealthy service instances
- [ ] Enable read-only database mode
- [ ] Implement request throttling

### Phase 3: Recovery (15-60 minutes)
- [ ] Gradually increase traffic limits
- [ ] Monitor cascade indicators
- [ ] Test critical user journeys
- [ ] Document incident timeline

## Real-World Examples

### Slack February 2022 Cascade
- **Trigger**: Authentication service latency spike
- **Cascade**: WebSocket connections → Message delivery → File uploads
- **Detection**: p99 latency 50ms → 3000ms in 2 minutes
- **Resolution**: Circuit breakers + service restarts

### GitHub October 2021 Database Cascade
- **Trigger**: MySQL connection pool exhaustion
- **Cascade**: API responses → Git operations → CI/CD pipelines
- **Detection**: Connection count 95/100 → timeouts
- **Resolution**: Read replica promotion + connection scaling

---
*Last Updated: Based on incidents from Slack, GitHub, Stripe production outages*
*Next Review: Monitor for new cascade patterns in incident reports*