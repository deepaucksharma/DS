# Service Discovery: Consul at HashiCorp

## Overview

HashiCorp Consul provides service discovery and configuration management for 10,000+ services across multi-cloud environments. Used internally by HashiCorp and thousands of enterprises, Consul handles service registration, health checking, and dynamic configuration with strong consistency guarantees.

## Production Architecture

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - #3B82F6]
        LB[Load Balancer<br/>F5/NGINX<br/>Service routing]
        PROXY[Consul Connect<br/>Service Mesh<br/>mTLS encryption]
    end

    subgraph ServicePlane[Service Plane - #10B981]
        subgraph ConsulCluster[Consul Server Cluster]
            CONSUL1[Consul Server 1<br/>Leader<br/>m5.xlarge]
            CONSUL2[Consul Server 2<br/>Follower<br/>m5.xlarge]
            CONSUL3[Consul Server 3<br/>Follower<br/>m5.xlarge]
            CONSUL4[Consul Server 4<br/>Follower<br/>m5.xlarge]
            CONSUL5[Consul Server 5<br/>Follower<br/>m5.xlarge]
        end

        subgraph ConsulAgents[Consul Agent Network]
            AGENT1[Consul Agent<br/>Web Services<br/>Health checks]
            AGENT2[Consul Agent<br/>API Services<br/>Service registration]
            AGENT3[Consul Agent<br/>Database Services<br/>Monitoring]
        end

        subgraph Applications[Application Services]
            WEB[Web Service<br/>Frontend<br/>Load balanced]
            API[API Service<br/>Business logic<br/>Auto-scaling]
            DB[Database Service<br/>PostgreSQL<br/>Primary/replica]
        end
    end

    subgraph StatePlane[State Plane - #F59E0B]
        subgraph ConsulStorage[Consul Storage]
            RAFT[(Raft Consensus<br/>Distributed log<br/>Strong consistency)]
            KV_STORE[(Key-Value Store<br/>Configuration<br/>Feature flags)]
            SERVICE_CATALOG[(Service Catalog<br/>Service registry<br/>Health status)]
        end

        subgraph ExternalSystems[External Systems]
            VAULT[(HashiCorp Vault<br/>Secrets management<br/>Dynamic credentials)]
            NOMAD[(HashiCorp Nomad<br/>Job scheduler<br/>Container orchestration)]
        end
    end

    subgraph ControlPlane[Control Plane - #8B5CF6]
        CONSUL_UI[Consul Web UI<br/>Service visualization<br/>Configuration management]
        PROMETHEUS[Prometheus<br/>Metrics collection<br/>Consul telemetry]
        GRAFANA[Grafana<br/>Service dashboards<br/>Health monitoring]
        ALERTS[AlertManager<br/>Service alerts<br/>Failure notifications]
    end

    %% Client connections
    LB --> PROXY
    PROXY --> CONSUL1

    %% Consul cluster
    CONSUL1 --> CONSUL2
    CONSUL1 --> CONSUL3
    CONSUL1 --> CONSUL4
    CONSUL1 --> CONSUL5

    %% Agent connections
    CONSUL1 --> AGENT1
    CONSUL2 --> AGENT2
    CONSUL3 --> AGENT3

    %% Service registration
    AGENT1 --> WEB
    AGENT2 --> API
    AGENT3 --> DB

    %% Storage
    CONSUL1 --> RAFT
    CONSUL1 --> KV_STORE
    CONSUL1 --> SERVICE_CATALOG

    %% External integrations
    CONSUL1 --> VAULT
    CONSUL1 --> NOMAD

    %% Monitoring
    CONSUL_UI --> CONSUL1
    PROMETHEUS --> CONSUL1
    PROMETHEUS --> AGENT1
    GRAFANA --> PROMETHEUS
    ALERTS --> PROMETHEUS

    %% Apply four-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#1E40AF,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#047857,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#6D28D9,color:#fff

    class LB,PROXY edgeStyle
    class CONSUL1,CONSUL2,CONSUL3,CONSUL4,CONSUL5,AGENT1,AGENT2,AGENT3,WEB,API,DB serviceStyle
    class RAFT,KV_STORE,SERVICE_CATALOG,VAULT,NOMAD stateStyle
    class CONSUL_UI,PROMETHEUS,GRAFANA,ALERTS controlStyle
```

## Service Registration and Discovery Flow

```mermaid
sequenceDiagram
    participant Service as New Service Instance
    participant Agent as Consul Agent
    participant Server as Consul Server
    participant Client as Client Application

    Note over Service: Service starts up
    Service->>Agent: Register service
    Note over Agent: Service: api-service<br/>Address: 10.0.1.100<br/>Port: 8080<br/>Tags: [v1.2, production]

    Agent->>Agent: Start health checks
    Note over Agent: HTTP: /health every 10s<br/>TCP: port 8080 every 30s<br/>TTL: 60s heartbeat

    Agent->>Server: Register service with health
    Server->>Server: Update service catalog
    Note over Server: Raft consensus<br/>Replicate to followers

    Note over Client: Client needs API service
    Client->>Agent: DNS query: api-service.service.consul
    Agent->>Server: Query service catalog
    Server-->>Agent: Healthy instances
    Agent-->>Client: DNS response: 10.0.1.100

    Note over Client: Alternative: HTTP API
    Client->>Agent: GET /v1/health/service/api-service
    Agent->>Server: Query with health filter
    Server-->>Agent: JSON response with metadata
    Agent-->>Client: Service instances + health status

    Note over Service: Health check fails
    Agent->>Agent: Mark service unhealthy
    Agent->>Server: Update health status
    Server->>Server: Remove from healthy pool

    Note over Client: Subsequent queries
    Client->>Agent: Query api-service
    Agent-->>Client: Only healthy instances returned
```

## Multi-Datacenter Federation

```mermaid
graph TB
    subgraph MultiDC[Multi-Datacenter Consul Federation]
        subgraph DC1[Datacenter: us-east-1]
            CONSUL_DC1_1[Consul Server 1<br/>Primary DC<br/>Leader election]
            CONSUL_DC1_2[Consul Server 2<br/>Follower<br/>Local consensus]
            CONSUL_DC1_3[Consul Server 3<br/>Follower<br/>Backup leader]

            SERVICES_DC1[Services DC1<br/>Web tier<br/>API tier<br/>Database]
        end

        subgraph DC2[Datacenter: us-west-2]
            CONSUL_DC2_1[Consul Server 1<br/>Secondary DC<br/>Cross-DC replication]
            CONSUL_DC2_2[Consul Server 2<br/>Follower<br/>Local services]
            CONSUL_DC2_3[Consul Server 3<br/>Follower<br/>DR capability]

            SERVICES_DC2[Services DC2<br/>Regional services<br/>Cache layer<br/>CDN nodes]
        end

        subgraph DC3[Datacenter: eu-west-1]
            CONSUL_DC3_1[Consul Server 1<br/>EU Region<br/>Data sovereignty]
            CONSUL_DC3_2[Consul Server 2<br/>Follower<br/>GDPR compliance]
            CONSUL_DC3_3[Consul Server 3<br/>Follower<br/>Local regulations]

            SERVICES_DC3[Services DC3<br/>European users<br/>Localized content<br/>Regional APIs]
        end

        subgraph Federation[Federation Layer]
            WAN_GOSSIP[WAN Gossip Pool<br/>Cross-DC communication<br/>Failure detection<br/>Metadata sync]
            PREPARED_QUERIES[Prepared Queries<br/>Cross-DC failover<br/>Intelligent routing<br/>Latency optimization]
            MESH_GATEWAYS[Mesh Gateways<br/>Secure connectivity<br/>Traffic routing<br/>Network isolation]
        end
    end

    %% Intra-DC connections
    CONSUL_DC1_1 --> CONSUL_DC1_2
    CONSUL_DC1_1 --> CONSUL_DC1_3
    CONSUL_DC1_1 --> SERVICES_DC1

    CONSUL_DC2_1 --> CONSUL_DC2_2
    CONSUL_DC2_1 --> CONSUL_DC2_3
    CONSUL_DC2_1 --> SERVICES_DC2

    CONSUL_DC3_1 --> CONSUL_DC3_2
    CONSUL_DC3_1 --> CONSUL_DC3_3
    CONSUL_DC3_1 --> SERVICES_DC3

    %% Cross-DC federation
    CONSUL_DC1_1 --> WAN_GOSSIP
    CONSUL_DC2_1 --> WAN_GOSSIP
    CONSUL_DC3_1 --> WAN_GOSSIP

    WAN_GOSSIP --> PREPARED_QUERIES
    WAN_GOSSIP --> MESH_GATEWAYS

    classDef dc1Style fill:#10B981,stroke:#047857,color:#fff
    classDef dc2Style fill:#F59E0B,stroke:#D97706,color:#fff
    classDef dc3Style fill:#8B5CF6,stroke:#6D28D9,color:#fff
    classDef federationStyle fill:#DC2626,stroke:#B91C1C,color:#fff

    class CONSUL_DC1_1,CONSUL_DC1_2,CONSUL_DC1_3,SERVICES_DC1 dc1Style
    class CONSUL_DC2_1,CONSUL_DC2_2,CONSUL_DC2_3,SERVICES_DC2 dc2Style
    class CONSUL_DC3_1,CONSUL_DC3_2,CONSUL_DC3_3,SERVICES_DC3 dc3Style
    class WAN_GOSSIP,PREPARED_QUERIES,MESH_GATEWAYS federationStyle
```

## Health Checking and Failure Detection

```mermaid
graph TB
    subgraph HealthChecking[Comprehensive Health Checking]
        subgraph CheckTypes[Health Check Types]
            HTTP_CHECK[HTTP Health Check<br/>GET /health<br/>200-299 status<br/>5-second timeout]
            TCP_CHECK[TCP Health Check<br/>Port connectivity<br/>Socket connection<br/>Low overhead]
            SCRIPT_CHECK[Script Health Check<br/>Custom validation<br/>Exit code 0<br/>Application-specific]
            TTL_CHECK[TTL Health Check<br/>Application heartbeat<br/>Self-reporting<br/>60-second TTL]
        end

        subgraph CheckScheduling[Check Scheduling]
            INTERVALS[Check Intervals<br/>Normal: 10s<br/>Fast: 1s<br/>Slow: 60s]
            JITTER[Jitter and Spreading<br/>Random delays<br/>Load distribution<br/>Thundering herd prevention]
            RETRY_LOGIC[Retry Logic<br/>3 consecutive failures<br/>Exponential backoff<br/>Circuit breaker]
        end

        subgraph FailureDetection[Failure Detection]
            THRESHOLD[Failure Threshold<br/>3 consecutive failures<br/>Mark as critical<br/>Remove from LB]
            RECOVERY[Recovery Detection<br/>1 successful check<br/>Mark as passing<br/>Add to LB pool]
            MAINTENANCE[Maintenance Mode<br/>Planned downtime<br/>Manual override<br/>Graceful drain]
        end

        subgraph AlertingIntegration[Alerting Integration]
            PROMETHEUS_METRICS[Prometheus Metrics<br/>Check success rate<br/>Response time<br/>Failure counts]
            WEBHOOK_ALERTS[Webhook Alerts<br/>Service state changes<br/>Critical failures<br/>Custom actions]
            LOG_EVENTS[Log Events<br/>Structured logging<br/>Audit trail<br/>Debug information]
        end
    end

    HTTP_CHECK --> INTERVALS
    TCP_CHECK --> INTERVALS
    SCRIPT_CHECK --> JITTER
    TTL_CHECK --> JITTER

    INTERVALS --> THRESHOLD
    JITTER --> THRESHOLD
    RETRY_LOGIC --> RECOVERY

    THRESHOLD --> MAINTENANCE
    RECOVERY --> MAINTENANCE

    MAINTENANCE --> PROMETHEUS_METRICS
    MAINTENANCE --> WEBHOOK_ALERTS
    MAINTENANCE --> LOG_EVENTS

    classDef checkStyle fill:#10B981,stroke:#047857,color:#fff
    classDef scheduleStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef failureStyle fill:#DC2626,stroke:#B91C1C,color:#fff
    classDef alertStyle fill:#8B5CF6,stroke:#6D28D9,color:#fff

    class HTTP_CHECK,TCP_CHECK,SCRIPT_CHECK,TTL_CHECK checkStyle
    class INTERVALS,JITTER,RETRY_LOGIC scheduleStyle
    class THRESHOLD,RECOVERY,MAINTENANCE failureStyle
    class PROMETHEUS_METRICS,WEBHOOK_ALERTS,LOG_EVENTS alertStyle
```

## Production Metrics

### Service Discovery Performance
- **Services Registered**: 10,000+ active services
- **DNS Queries**: 1M queries/second peak
- **Service Lookup Latency**: P99 < 5ms
- **Catalog Update Propagation**: <500ms globally

### Cluster Health
- **Cluster Availability**: 99.99% uptime
- **Leader Election Time**: <3 seconds
- **Raft Log Entries**: 10M+ entries/day
- **Cross-DC Latency**: <200ms WAN gossip

### Health Check Performance
- **Health Checks**: 100K+ checks/minute
- **Check Success Rate**: 99.95%
- **False Positive Rate**: <0.1%
- **Recovery Detection Time**: <30 seconds

## Implementation Details

### Service Registration
```json
{
  "ID": "api-service-001",
  "Name": "api-service",
  "Tags": ["v1.2", "production", "us-east-1"],
  "Address": "10.0.1.100",
  "Port": 8080,
  "Meta": {
    "version": "1.2.3",
    "environment": "production",
    "team": "platform"
  },
  "Check": {
    "HTTP": "http://10.0.1.100:8080/health",
    "Interval": "10s",
    "Timeout": "5s",
    "DeregisterCriticalServiceAfter": "1m"
  },
  "Weights": {
    "Passing": 10,
    "Warning": 1
  }
}
```

### Configuration Management
```hcl
# Consul server configuration
datacenter = "us-east-1"
data_dir = "/opt/consul/data"
log_level = "INFO"
server = true
bootstrap_expect = 5

bind_addr = "{{ GetInterfaceIP \"eth0\" }}"
client_addr = "0.0.0.0"

retry_join = [
  "consul-1.internal",
  "consul-2.internal",
  "consul-3.internal"
]

encrypt = "cg8StVXbQJ0gPvMd9o7yrg=="

acl = {
  enabled = true
  default_policy = "deny"
  enable_token_persistence = true
}

connect = {
  enabled = true
}

ui_config = {
  enabled = true
}

telemetry = {
  prometheus_retention_time = "30s"
  disable_hostname = true
}
```

### Prepared Queries for Failover
```json
{
  "Name": "api-service-failover",
  "Service": {
    "Service": "api-service",
    "Failover": {
      "NearestN": 3,
      "Datacenters": ["us-west-2", "eu-west-1"]
    },
    "OnlyPassing": true,
    "Tags": ["production"]
  },
  "DNS": {
    "TTL": "10s"
  }
}
```

### Health Check Script
```bash
#!/bin/bash
# Custom health check script

# Check database connectivity
if ! pg_isready -h db.internal -p 5432 -U app; then
    echo "Database connection failed"
    exit 1
fi

# Check Redis connectivity
if ! redis-cli -h cache.internal ping > /dev/null; then
    echo "Redis connection failed"
    exit 1
fi

# Check API endpoint
if ! curl -sf http://localhost:8080/health > /dev/null; then
    echo "HTTP health check failed"
    exit 1
fi

# Check disk space
DISK_USAGE=$(df /var/log | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    echo "Disk usage too high: ${DISK_USAGE}%"
    exit 1
fi

echo "All health checks passed"
exit 0
```

## Cost Analysis

### Infrastructure Costs
- **Consul Servers**: $3K/month (15 m5.xlarge across 3 DCs)
- **Consul Agents**: $2K/month (included in application nodes)
- **Network Transfer**: $500/month (cross-DC gossip)
- **Monitoring**: $300/month
- **Total Monthly**: $5.8K

### Operational Benefits
- **Service Discovery Automation**: $50K/year saved in manual configuration
- **Health Check Automation**: $30K/year operational efficiency
- **Incident Response**: 60% faster MTTR
- **Configuration Management**: $40K/year reduced complexity

## Battle-tested Lessons

### What Works at 3 AM
1. **Automatic Deregistration**: Failed services auto-remove from load balancers
2. **Cross-DC Failover**: Prepared queries route to healthy datacenters
3. **Rich Metadata**: Service tags enable intelligent routing decisions
4. **Health Check Diversity**: Multiple check types catch different failure modes

### Common Service Discovery Issues
1. **Split-brain Scenarios**: Network partitions causing multiple leaders
2. **Agent Connectivity**: Agents losing connection to servers
3. **Health Check Flapping**: Intermittent failures causing instability
4. **DNS Caching**: Stale DNS responses causing traffic to failed services

### Operational Best Practices
1. **Gradual Rollouts**: Use health checks to control traffic flow
2. **Maintenance Windows**: Proper service deregistration during deploys
3. **Monitor Everything**: Track service registration/deregistration patterns
4. **ACL Policies**: Secure service registration with proper permissions

## Related Patterns
- [Load Balancing](./load-balancing.md)
- [Health Check](./health-check.md)
- [Circuit Breaker](./circuit-breaker.md)

*Source: HashiCorp Documentation, Consul at Scale, Personal Production Experience*