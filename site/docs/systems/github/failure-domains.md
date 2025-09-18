# GitHub Failure Domains: Blast Radius and Circuit Breaker Architecture

## Executive Summary
GitHub's failure domain architecture is designed to limit blast radius during incidents. With 99.95% availability serving 100M users, the system employs sophisticated circuit breakers, bulkheads, and isolation boundaries to prevent cascading failures.

## Complete Failure Domain Map

```mermaid
graph TB
    subgraph GitHub_Failure_Domains___Production[""GitHub Failure Domains - Production Architecture""]
        subgraph Level1[Level 1 - Edge Isolation]
            subgraph CDN_DOMAIN[CDN Failure Domain - 200 PoPs]
                FASTLY1[Fastly PoP 1<br/>Americas<br/>Isolated failure]
                FASTLY2[Fastly PoP 2<br/>EMEA<br/>Isolated failure]
                FASTLY3[Fastly PoP 3<br/>APAC<br/>Isolated failure]
            end

            subgraph LB_DOMAIN[Load Balancer Domain]
                LB_CLUSTER1[LB Cluster 1<br/>AZ-1a<br/>10 instances]
                LB_CLUSTER2[LB Cluster 2<br/>AZ-1b<br/>10 instances]
                LB_CLUSTER3[LB Cluster 3<br/>AZ-1c<br/>10 instances]
            end
        end

        subgraph Level2[Level 2 - Service Isolation]
            subgraph WEB_DOMAIN[Web Tier Domain]
                WEB_SHARD1[Rails Shard 1<br/>500 servers<br/>25% capacity]
                WEB_SHARD2[Rails Shard 2<br/>500 servers<br/>25% capacity]
                WEB_SHARD3[Rails Shard 3<br/>500 servers<br/>25% capacity]
                WEB_SHARD4[Rails Shard 4<br/>500 servers<br/>25% capacity]

                API_CIRCUIT[API Circuit Breaker<br/>500ms timeout<br/>5% error threshold]
            end

            subgraph GIT_DOMAIN[Git Service Domain]
                GIT_REGION1[Git Cluster 1<br/>Primary East<br/>Full replication]
                GIT_REGION2[Git Cluster 2<br/>Secondary West<br/>Read replica]
                GIT_REGION3[Git Cluster 3<br/>EU Cache<br/>Cache only]

                GIT_CIRCUIT[Git Circuit Breaker<br/>1s timeout<br/>10% error threshold]
            end

            subgraph ACTIONS_DOMAIN[Actions Platform Domain]
                ACTIONS_CTRL1[Actions Controller 1<br/>100 servers<br/>Linux runners]
                ACTIONS_CTRL2[Actions Controller 2<br/>100 servers<br/>Windows runners]
                ACTIONS_CTRL3[Actions Controller 3<br/>100 servers<br/>macOS runners]

                RUNNER_POOLS[Runner Pool Isolation<br/>100K VMs<br/>Firecracker isolation]
            end
        end

        subgraph Level3[Level 3 - Data Isolation]
            subgraph MYSQL_DOMAIN[MySQL Failure Domain]
                MYSQL_SHARD1[MySQL Shard 1-25<br/>User data<br/>25% of users]
                MYSQL_SHARD2[MySQL Shard 26-50<br/>Repo metadata<br/>25% of repos]
                MYSQL_SHARD3[MySQL Shard 51-75<br/>Issue data<br/>25% of issues]
                MYSQL_SHARD4[MySQL Shard 76-100<br/>Actions data<br/>25% of workflows]

                MYSQL_CIRCUIT[MySQL Circuit Breaker<br/>100ms timeout<br/>3% error threshold]
            end

            subgraph SPOKES_DOMAIN[Git Storage Domain]
                SPOKES_CLUSTER1[Spokes Cluster 1<br/>Replica A<br/>33% of repos]
                SPOKES_CLUSTER2[Spokes Cluster 2<br/>Replica B<br/>33% of repos]
                SPOKES_CLUSTER3[Spokes Cluster 3<br/>Replica C<br/>33% of repos]

                STORAGE_CIRCUIT[Storage Circuit Breaker<br/>2s timeout<br/>15% error threshold]
            end

            subgraph CACHE_DOMAIN[Cache Failure Domain]
                REDIS_CLUSTER1[Redis Cluster 1<br/>200 nodes<br/>Hot data]
                REDIS_CLUSTER2[Redis Cluster 2<br/>200 nodes<br/>Session data]
                MEMCACHED_CLUSTER[Memcached Cluster<br/>500 nodes<br/>Page cache]
            end
        end

        subgraph Level4[Level 4 - Infrastructure Isolation]
            subgraph AZ_ISOLATION[Availability Zone Isolation]
                AZ_1A[AZ us-east-1a<br/>40% capacity<br/>Independent power/network]
                AZ_1B[AZ us-east-1b<br/>40% capacity<br/>Independent power/network]
                AZ_1C[AZ us-east-1c<br/>20% capacity<br/>Independent power/network]
            end

            subgraph REGION_ISOLATION[Regional Isolation]
                PRIMARY_REGION[US East Primary<br/>Full stack<br/>Active]
                SECONDARY_REGION[US West Secondary<br/>Read replicas<br/>Standby]
                CACHE_REGIONS[EU/APAC Regions<br/>Cache tier only<br/>Passive]
            end
        end

        %% Failure propagation paths
        FASTLY1 -.->|CDN Fail| LB_CLUSTER1
        LB_CLUSTER1 -.->|LB Fail| WEB_SHARD1
        WEB_SHARD1 -.->|Web Fail| MYSQL_SHARD1

        API_CIRCUIT -.->|Circuit Open| DEGRADED_MODE[Degraded Mode<br/>Read-only operations<br/>Cached responses]
        GIT_CIRCUIT -.->|Circuit Open| GIT_READONLY[Git Read-Only<br/>Clone/fetch only<br/>No push operations]
        MYSQL_CIRCUIT -.->|Circuit Open| REPLICA_FALLBACK[Replica Fallback<br/>Read from replicas<br/>Eventual consistency]

        %% Cross-domain isolation
        WEB_DOMAIN -.->|Isolated from| GIT_DOMAIN
        GIT_DOMAIN -.->|Isolated from| ACTIONS_DOMAIN
        ACTIONS_DOMAIN -.->|Isolated from| WEB_DOMAIN

        %% Recovery flows
        PRIMARY_REGION -.->|Failover| SECONDARY_REGION
        SPOKES_CLUSTER1 -.->|Replica Sync| SPOKES_CLUSTER2
        MYSQL_SHARD1 -.->|Binlog Replication| MYSQL_REPLICA[MySQL Replica<br/>Read-only fallback]
    end

    %% Apply four-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef failureStyle fill:#EF4444,stroke:#DC2626,color:#fff

    class FASTLY1,FASTLY2,FASTLY3,LB_CLUSTER1,LB_CLUSTER2,LB_CLUSTER3 edgeStyle
    class WEB_SHARD1,WEB_SHARD2,WEB_SHARD3,WEB_SHARD4,GIT_REGION1,GIT_REGION2,GIT_REGION3,ACTIONS_CTRL1,ACTIONS_CTRL2,ACTIONS_CTRL3 serviceStyle
    class MYSQL_SHARD1,MYSQL_SHARD2,MYSQL_SHARD3,MYSQL_SHARD4,SPOKES_CLUSTER1,SPOKES_CLUSTER2,SPOKES_CLUSTER3,REDIS_CLUSTER1,REDIS_CLUSTER2,MEMCACHED_CLUSTER stateStyle
    class API_CIRCUIT,GIT_CIRCUIT,MYSQL_CIRCUIT,STORAGE_CIRCUIT,AZ_1A,AZ_1B,AZ_1C controlStyle
    class DEGRADED_MODE,GIT_READONLY,REPLICA_FALLBACK failureStyle
```

## Blast Radius Analysis

### Critical Failure Scenarios

#### 1. MySQL Primary Shard Failure
```python
blast_radius = {
    "affected_users": "25% of total users (25M)",
    "affected_operations": [
        "Web authentication",
        "Repository metadata access",
        "Issue/PR operations",
        "Actions workflow history"
    ],
    "detection_time": "< 5 seconds",
    "failover_time": "< 30 seconds",
    "recovery_strategy": {
        "immediate": "Promote read replica to primary",
        "data_consistency": "0 data loss (sync replication)",
        "fallback": "Read-only mode if promotion fails"
    },
    "mitigation": {
        "circuit_breaker": "100ms timeout, 3% error threshold",
        "retry_policy": "Exponential backoff, max 3 attempts",
        "graceful_degradation": "Show cached data, disable writes"
    }
}
```

#### 2. Git Storage Cluster Failure
```python
git_failure_impact = {
    "blast_radius": "33% of repositories (110M repos)",
    "operations_affected": [
        "Git clone/fetch/push",
        "Repository browsing",
        "Code search",
        "Actions checkout"
    ],
    "detection": {
        "method": "Health checks every 5 seconds",
        "alerts": "PagerDuty to git-systems on-call",
        "escalation": "VP Engineering after 15 minutes"
    },
    "automatic_recovery": {
        "reroute_to_replicas": "< 10 seconds",
        "background_resync": "Starts immediately",
        "replica_promotion": "Manual approval required"
    },
    "user_impact": {
        "git_operations": "Slower (replica lag 1-5 seconds)",
        "web_browsing": "Cached version shown",
        "actions": "Workflows queued until recovery"
    }
}
```

#### 3. Entire Availability Zone Loss
```python
az_failure_impact = {
    "capacity_loss": "40% of total capacity",
    "affected_components": [
        "40% of web servers",
        "40% of database shards",
        "40% of git storage nodes",
        "40% of actions runners"
    ],
    "automatic_response": {
        "load_balancer": "Removes AZ from rotation < 30s",
        "autoscaling": "Spins up instances in healthy AZs",
        "dns_failover": "Routes traffic to remaining AZs"
    },
    "performance_impact": {
        "latency_increase": "50-100ms (cross-AZ traffic)",
        "throughput_reduction": "40% until scaling complete",
        "error_rate": "< 0.1% (well within SLO)"
    },
    "recovery_time": {
        "traffic_reroute": "< 5 minutes",
        "capacity_restoration": "15-30 minutes",
        "full_redundancy": "2-4 hours"
    }
}
```

## Circuit Breaker Configuration

### Production Circuit Breakers

```python
class GitHubCircuitBreakers:
    """Production circuit breaker configurations"""

    def __init__(self):
        self.configurations = {
            "mysql_primary": {
                "timeout": "100ms",
                "error_threshold": "3%",
                "volume_threshold": "100 requests/10s",
                "sleep_window": "30s",
                "half_open_max_calls": "10"
            },

            "git_storage": {
                "timeout": "2s",  # Git operations take longer
                "error_threshold": "15%",
                "volume_threshold": "50 requests/10s",
                "sleep_window": "60s",
                "half_open_max_calls": "5"
            },

            "actions_runners": {
                "timeout": "30s",  # Job startup time
                "error_threshold": "20%",
                "volume_threshold": "1000 jobs/minute",
                "sleep_window": "120s",
                "half_open_max_calls": "100"
            },

            "external_apis": {
                "timeout": "5s",
                "error_threshold": "10%",
                "volume_threshold": "10 requests/10s",
                "sleep_window": "300s",  # Longer for external deps
                "half_open_max_calls": "3"
            }
        }

    def handle_mysql_failure(self):
        """MySQL circuit breaker logic"""
        return {
            "fallback_strategy": "Route to read replicas",
            "degraded_operations": [
                "Authentication becomes read-only",
                "Repository metadata from cache",
                "Issue/PR updates queued"
            ],
            "user_experience": {
                "read_operations": "Normal (from cache/replicas)",
                "write_operations": "Error message with retry guidance",
                "api_responses": "503 with Retry-After header"
            }
        }

    def handle_git_storage_failure(self):
        """Git storage circuit breaker logic"""
        return {
            "fallback_strategy": "Route to healthy replicas",
            "degraded_operations": [
                "Push operations to failed cluster disabled",
                "Clone/fetch from replica (may be stale)",
                "Repository browsing from cache"
            ],
            "automatic_recovery": {
                "health_check_interval": "10s",
                "replica_sync_priority": "High",
                "traffic_gradual_restore": "10% every 5 minutes"
            }
        }
```

## Cascading Failure Prevention

### Bulkhead Patterns

```yaml
bulkhead_isolation:
  thread_pool_isolation:
    web_requests:
      pool_size: 200
      queue_size: 1000
      timeout: "30s"

    git_operations:
      pool_size: 500
      queue_size: 5000
      timeout: "60s"

    background_jobs:
      pool_size: 100
      queue_size: 10000
      timeout: "300s"

  connection_pool_isolation:
    mysql_read:
      max_connections: 500
      idle_timeout: "10m"
      max_lifetime: "1h"

    mysql_write:
      max_connections: 100
      idle_timeout: "5m"
      max_lifetime: "30m"

    redis_cache:
      max_connections: 1000
      idle_timeout: "5m"
      max_lifetime: "15m"

  resource_quotas:
    cpu_limits:
      web_tier: "80% of node capacity"
      git_tier: "90% of node capacity"
      background: "20% of node capacity"

    memory_limits:
      web_processes: "8GB per process"
      git_processes: "16GB per process"
      cache_processes: "32GB per process"
```

## Real Incident Examples

### Incident: MySQL Replication Lag Spike
```yaml
incident_2024_03_15:
  trigger: "Large repository import caused 10-minute replication lag"

  blast_radius:
    affected_users: "15M users"
    affected_operations: ["Repository browsing", "Issue updates", "PR merges"]
    duration: "25 minutes"

  failure_progression:
    1: "00:05 - Single large repo import starts (10GB repository)"
    2: "00:10 - MySQL primary CPU spikes to 95%"
    3: "00:12 - Replication lag increases to 30 seconds"
    4: "00:15 - Circuit breaker trips on read replicas"
    5: "00:17 - Web tier falls back to cached data"
    6: "00:25 - Import rate limited, replication catches up"
    7: "00:30 - Circuit breakers reset, full service restored"

  prevented_cascading_failure:
    - "Circuit breakers prevented read replica overload"
    - "Bulkhead isolation kept git operations running"
    - "Rate limiting prevented additional large imports"

  lessons_learned:
    - "Implement import size limits (1GB per request)"
    - "Add dedicated import worker pool"
    - "Improve replication lag monitoring"
```

### Incident: Actions Runner Capacity Exhaustion
```yaml
incident_2024_07_22:
  trigger: "Major open source project released, 50K concurrent workflows"

  blast_radius:
    affected_service: "GitHub Actions only"
    queue_depth: "100K jobs waiting"
    wait_times: "Up to 45 minutes"

  isolation_success:
    - "Web interface remained responsive"
    - "Git operations unaffected"
    - "API continued normal operation"
    - "Only Actions workflows queued"

  recovery_actions:
    1: "Auto-scaling triggered additional 20K runners"
    2: "Workflow throttling applied to heavy users"
    3: "Cache hit rate optimized to reduce job duration"
    4: "Queue prioritization for paying customers"

  prevention_measures:
    - "Predictive scaling based on calendar events"
    - "Burst capacity pool (10K warm instances)"
    - "Better communication about major releases"
```

## Circuit Breaker Monitoring

### Key Metrics Dashboard

```python
circuit_breaker_metrics = {
    "mysql_circuit": {
        "current_state": "CLOSED",
        "error_rate": "0.8%",
        "avg_response_time": "45ms",
        "requests_last_minute": 125000,
        "trips_last_24h": 0
    },

    "git_circuit": {
        "current_state": "HALF_OPEN",
        "error_rate": "12%",
        "avg_response_time": "850ms",
        "requests_last_minute": 8500,
        "trips_last_24h": 2
    },

    "actions_circuit": {
        "current_state": "CLOSED",
        "error_rate": "5%",
        "avg_response_time": "15s",
        "requests_last_minute": 2000,
        "trips_last_24h": 1
    }
}

# Alerting thresholds
alert_thresholds = {
    "circuit_open": "Immediate PagerDuty",
    "error_rate_high": "> 10% for 5 minutes",
    "response_time_high": "> 2x baseline for 10 minutes",
    "multiple_circuits_degraded": "Escalate to VP Engineering"
}
```

## The 3 AM Playbook

### Circuit Breaker Incident Response

```python
def circuit_breaker_runbook(circuit_name, state):
    """3 AM incident response for circuit breaker failures"""

    if circuit_name == "mysql" and state == "OPEN":
        return {
            "immediate_check": [
                "Check MySQL primary CPU/memory",
                "Verify replication lag on all replicas",
                "Look for long-running queries",
                "Check connection pool exhaustion"
            ],
            "common_causes": [
                "Large query without proper indexing",
                "Connection pool leak",
                "Disk I/O saturation",
                "Lock contention"
            ],
            "quick_fixes": [
                "Kill problematic queries",
                "Restart connection pools",
                "Promote replica if primary unhealthy",
                "Enable read-only mode if needed"
            ],
            "escalation": "Page database team if not resolved in 10 minutes"
        }

    elif circuit_name == "git_storage" and state == "OPEN":
        return {
            "immediate_check": [
                "Spokes cluster health dashboard",
                "Check storage node disk usage",
                "Verify network connectivity between replicas",
                "Look for large repository operations"
            ],
            "common_causes": [
                "Storage node disk full",
                "Large push overwhelming single node",
                "Network partition between replicas",
                "Filesystem corruption"
            ],
            "quick_fixes": [
                "Remove failed node from cluster",
                "Rate limit large repository operations",
                "Force traffic to healthy replicas",
                "Trigger background cleanup jobs"
            ],
            "escalation": "Page git-systems team immediately"
        }
```

## Key Innovations in Failure Isolation

1. **Hierarchical Circuit Breakers**: Multiple layers from network to application
2. **Blast Radius Calculation**: Real-time impact assessment for failures
3. **Gradual Traffic Restoration**: Automatic recovery with safety checks
4. **Cross-Service Isolation**: Git failures don't affect web, Actions isolated
5. **Predictive Failure Detection**: ML-based anomaly detection before failures
6. **Chaos Engineering**: Regular failure injection to test isolation boundaries

*"Our failure isolation architecture is designed on the principle that everything will fail eventually. The question is not if, but when - and how well we contain the blast radius."* - GitHub Site Reliability Engineering Team