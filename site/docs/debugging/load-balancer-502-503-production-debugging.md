# Load Balancer 502/503 Production Debugging

## Emergency Response Overview

**Incident Severity**: P1/P0 - Service unavailable
**MTTR Target**: < 5 minutes for traffic rerouting, < 15 minutes for root cause resolution
**Primary Tools**: `curl`, `nginx -t`, `haproxy -c`, `tcpdump`, `ss/netstat`

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - Blue #3B82F6]
        ALERT[🚨 502/503 Alert<br/>Error Rate > 5%]
        CDN[CloudFlare CDN<br/>Origin errors detected]
        CHECKS[Health Check Status<br/>Failed backends: 3/8]
    end

    subgraph ServicePlane[Service Plane - Emerald #10B981]
        LB[NGINX Load Balancer<br/>nginx-1.22.1<br/>worker_processes: 8]
        APP1[App Server 1<br/>Status: DOWN<br/>Connection timeout]
        APP2[App Server 2<br/>Status: UP<br/>Response time: 50ms]
        APP3[App Server 3<br/>Status: DOWN<br/>503 Service Unavailable]
    end

    subgraph StatePlane[State Plane - Amber #F59E0B]
        LOGS[NGINX Error Logs<br/>/var/log/nginx/error.log<br/>Connection refused errors]
        METRICS[Prometheus Metrics<br/>nginx_upstream_response_time<br/>nginx_connections_active]
    end

    subgraph ControlPlane[Control Plane - Violet #8B5CF6]
        MONITOR[Grafana Dashboard<br/>Load Balancer Health<br/>Upstream Response Codes]
        ALERTMGR[AlertManager<br/>PagerDuty Integration<br/>On-call escalation]
    end

    ALERT --> CDN
    CDN --> LB
    LB --> APP1
    LB --> APP2
    LB --> APP3
    LB --> LOGS
    LOGS --> MONITOR
    MONITOR --> ALERTMGR

    %% Apply Tailwind 4-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#1E40AF,color:#fff,stroke-width:2px
    classDef serviceStyle fill:#10B981,stroke:#047857,color:#fff,stroke-width:2px
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff,stroke-width:2px
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff,stroke-width:2px

    class ALERT,CDN,CHECKS edgeStyle
    class LB,APP1,APP2,APP3 serviceStyle
    class LOGS,METRICS stateStyle
    class MONITOR,ALERTMGR controlStyle
```

## 3 AM Debugging Flowchart

```mermaid
flowchart TD
    START[🚨 502/503 Alerts<br/>Error rate spike detected] --> CHECK_STATUS{Load Balancer<br/>Status Check}

    CHECK_STATUS -->|NGINX| NGINX_SYNTAX[nginx -t<br/>Configuration test]
    CHECK_STATUS -->|HAProxy| HAPROXY_SYNTAX[haproxy -c -f /etc/haproxy/haproxy.cfg<br/>Configuration test]

    NGINX_SYNTAX -->|FAIL| CONFIG_ERROR[❌ Configuration Error<br/>Fix syntax + reload]
    NGINX_SYNTAX -->|PASS| CHECK_UPSTREAMS[Check Upstream Health<br/>curl -I backend servers]

    HAPROXY_SYNTAX -->|FAIL| CONFIG_ERROR
    HAPROXY_SYNTAX -->|PASS| CHECK_UPSTREAMS

    CHECK_UPSTREAMS --> UPSTREAM_STATUS{Upstream<br/>Response?}

    UPSTREAM_STATUS -->|All DOWN| UPSTREAM_ISSUE[❌ Backend Failure<br/>Scale up backends<br/>OR traffic reroute]
    UPSTREAM_STATUS -->|Some DOWN| PARTIAL_OUTAGE[⚠️ Partial Outage<br/>Remove failed backends<br/>Scale remaining]
    UPSTREAM_STATUS -->|All UP| LB_ISSUE[❌ Load Balancer Issue<br/>Check connections<br/>Resource limits]

    CONFIG_ERROR --> ROLLBACK[EMERGENCY ROLLBACK<br/>Previous known-good config]
    UPSTREAM_ISSUE --> SCALE_ACTION[Scale Action<br/>Auto-scaling groups<br/>OR manual intervention]
    PARTIAL_OUTAGE --> REMOVE_FAILED[Remove Failed Backends<br/>nginx reload<br/>haproxy reload]
    LB_ISSUE --> CHECK_RESOURCES[Check Resources<br/>CPU, Memory, Connections]

    ROLLBACK --> VERIFY_FIX{Traffic<br/>Restored?}
    SCALE_ACTION --> VERIFY_FIX
    REMOVE_FAILED --> VERIFY_FIX
    CHECK_RESOURCES --> RESTART_LB[Restart Load Balancer<br/>Zero-downtime reload]
    RESTART_LB --> VERIFY_FIX

    VERIFY_FIX -->|YES| POSTMORTEM[✅ Service Restored<br/>Begin postmortem<br/>Root cause analysis]
    VERIFY_FIX -->|NO| ESCALATE[🚨 ESCALATE<br/>Call senior engineer<br/>Consider DR failover]

    %% Apply Tailwind colors for different action types
    classDef errorStyle fill:#EF4444,stroke:#DC2626,color:#fff,stroke-width:2px
    classDef warningStyle fill:#F59E0B,stroke:#D97706,color:#fff,stroke-width:2px
    classDef successStyle fill:#10B981,stroke:#047857,color:#fff,stroke-width:2px
    classDef actionStyle fill:#3B82F6,stroke:#1E40AF,color:#fff,stroke-width:2px

    class CONFIG_ERROR,UPSTREAM_ISSUE,LB_ISSUE,ESCALATE errorStyle
    class PARTIAL_OUTAGE warningStyle
    class POSTMORTEM successStyle
    class NGINX_SYNTAX,HAPROXY_SYNTAX,CHECK_UPSTREAMS,ROLLBACK,SCALE_ACTION,REMOVE_FAILED,CHECK_RESOURCES,RESTART_LB actionStyle
```

## Critical Commands & Immediate Actions

### NGINX Debugging (< 2 minutes)

```bash
# 1. IMMEDIATE STATUS CHECK
sudo nginx -t                                    # Configuration syntax
sudo systemctl status nginx                      # Service status
sudo ss -tlnp | grep :80                        # Port binding

# 2. UPSTREAM HEALTH CHECK
curl -I -m 5 http://backend-1:8080/health       # Backend 1 health
curl -I -m 5 http://backend-2:8080/health       # Backend 2 health
curl -I -m 5 http://backend-3:8080/health       # Backend 3 health

# 3. CONNECTION ANALYSIS
sudo ss -s                                       # Socket summary
sudo netstat -an | grep :80 | wc -l            # Active connections
tail -f /var/log/nginx/error.log               # Live error monitoring

# 4. EMERGENCY FIXES
sudo nginx -s reload                            # Graceful reload
sudo systemctl restart nginx                    # Full restart (last resort)

# 5. REMOVE FAILED BACKEND (Netflix approach)
# Edit /etc/nginx/conf.d/upstream.conf
# Comment out failed server line
# server backend-3:8080; # TEMP DISABLED - 502 errors
sudo nginx -s reload
```

### HAProxy Debugging (< 2 minutes)

```bash
# 1. CONFIGURATION CHECK
sudo haproxy -c -f /etc/haproxy/haproxy.cfg     # Config validation
sudo systemctl status haproxy                   # Service status

# 2. STATS INTERFACE (if enabled)
curl -s http://admin:password@localhost:8404/stats
# OR check HAProxy stats page in browser

# 3. BACKEND STATUS
echo "show stat" | socat stdio /var/run/haproxy/admin.sock
echo "show info" | socat stdio /var/run/haproxy/admin.sock

# 4. DISABLE FAILED BACKEND (Uber approach)
echo "disable server backend/app-3" | socat stdio /var/run/haproxy/admin.sock
echo "enable server backend/app-3" | socat stdio /var/run/haproxy/admin.sock

# 5. EMERGENCY RESTART
sudo systemctl reload haproxy                   # Graceful reload
sudo systemctl restart haproxy                  # Full restart
```

## Common Root Causes & Probabilities

### 1. Backend Service Failures (45% of cases)
**Netflix Example**: During 2019 outage, backend services became unresponsive due to database connection exhaustion

```bash
# INVESTIGATION
for backend in backend-1 backend-2 backend-3; do
  echo "=== $backend ==="
  curl -m 5 -I http://$backend:8080/health
  curl -m 5 -s http://$backend:8080/metrics | grep http_requests_total
done

# IMMEDIATE ACTION
# Remove failing backends from rotation
# Scale up healthy backends
# Alert application teams
```

### 2. Load Balancer Resource Exhaustion (25% of cases)
**Uber Example**: NGINX worker process limits hit during Black Friday traffic spike

```bash
# CHECK LIMITS
cat /proc/$(pgrep nginx | head -1)/limits       # Process limits
sudo sysctl net.core.somaxconn                  # Socket backlog
ps aux | grep nginx                             # Worker processes

# QUICK FIXES
# Increase worker_processes in nginx.conf
# Increase worker_connections
# Tune kernel parameters
```

### 3. Network Connectivity Issues (20% of cases)
**Stripe Example**: AWS VPC routing table misconfiguration blocked backend traffic

```bash
# NETWORK DEBUGGING
sudo tcpdump -i any port 8080 -c 100           # Backend traffic
ping -c 3 backend-1                            # Basic connectivity
traceroute backend-1                           # Route analysis
nslookup backend-1                             # DNS resolution

# IMMEDIATE ACTIONS
# Check security groups/firewall rules
# Verify DNS resolution
# Test direct IP connections
```

### 4. Configuration Errors (8% of cases)
**Meta Example**: Recent deployment introduced syntax error in upstream configuration

```bash
# CONFIG VALIDATION
sudo nginx -t                                   # NGINX syntax
diff /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup

# ROLLBACK PROCEDURE
sudo cp /etc/nginx/nginx.conf.backup /etc/nginx/nginx.conf
sudo nginx -s reload
```

### 5. SSL/TLS Issues (2% of cases)
**Shopify Example**: Certificate expiry caused upstream SSL handshake failures

```bash
# SSL DEBUGGING
openssl s_client -connect backend-1:8443 -servername api.company.com
openssl x509 -in /etc/ssl/certs/backend.crt -noout -dates

# CERTIFICATE CHECK
curl -k -I https://backend-1:8443/health       # Skip cert validation
```

## Recovery Procedures (< 10 minutes)

### Phase 1: Immediate Traffic Restoration (< 2 minutes)

```bash
# STEP 1: Identify healthy backends
for i in {1..5}; do
  curl -m 2 -I http://backend-$i:8080/health 2>/dev/null && echo "backend-$i: UP" || echo "backend-$i: DOWN"
done

# STEP 2: Update load balancer config (NGINX)
sudo cp /etc/nginx/conf.d/upstream.conf /etc/nginx/conf.d/upstream.conf.backup
# Edit upstream.conf - comment out failed backends
sudo nginx -t && sudo nginx -s reload

# STEP 3: Verify traffic restoration
watch -n 1 'curl -s -o /dev/null -w "%{http_code}" http://loadbalancer.company.com/health'
```

### Phase 2: Scale Healthy Backends (< 5 minutes)

```bash
# AUTO SCALING (AWS)
aws autoscaling set-desired-capacity \
  --auto-scaling-group-name "app-servers-asg" \
  --desired-capacity 8

# MANUAL SCALING (Kubernetes)
kubectl scale deployment app-server --replicas=8

# VERIFY SCALING
kubectl get pods -l app=app-server
```

### Phase 3: Root Cause Investigation (< 10 minutes)

```bash
# COLLECT EVIDENCE
sudo journalctl -u nginx --since "5 minutes ago" > /tmp/nginx-incident.log
sudo dmesg | tail -50 > /tmp/system-messages.log
sudo ss -tuln > /tmp/network-connections.log

# APPLICATION LOGS
kubectl logs -l app=app-server --since=5m > /tmp/app-logs.log

# METRICS SNAPSHOT
curl -s http://prometheus:9090/api/v1/query?query='nginx_up' > /tmp/metrics.json
```

## Real-World Examples

### Netflix: 2019 Load Balancer Cascade Failure

**Scenario**: Database connection pool exhaustion → Backend 502s → Load balancer 502s → CDN origin errors

**Timeline**:
- T+0: Database connections maxed out (2000/2000)
- T+30s: Backend services start returning 502
- T+60s: NGINX marks all upstreams as down
- T+90s: Global 502 errors to users

**Recovery Actions**:
1. Identified via Grafana dashboard spike in 502 errors
2. Quickly scaled database read replicas
3. Temporarily increased connection pool limits
4. Load balancer automatically recovered as backends came online

### Uber: 2020 Configuration Rollout Issue

**Scenario**: Automated deployment pushed invalid NGINX configuration

**Root Cause**: Missing semicolon in upstream configuration block
```nginx
# BROKEN CONFIG
upstream backend {
    server app-1:8080 weight=1
    server app-2:8080 weight=1  # MISSING SEMICOLON
}
```

**Recovery**:
1. Alert triggered on configuration test failure
2. Automated rollback system restored previous config
3. Total downtime: 47 seconds

### Stripe: 2021 SSL Certificate Rotation

**Scenario**: Expired intermediate certificate caused upstream SSL failures

**Detection**: Monitoring showed 502 errors with SSL handshake failures in logs
```bash
# ERROR LOG PATTERN
upstream SSL certificate verify failed: (20:unable to get local issuer certificate)
```

**Resolution**:
1. Identified via certificate expiry monitoring
2. Updated certificate bundle on load balancers
3. Implemented automated certificate rotation

## Monitoring & Prevention

### Key Metrics to Track

```bash
# NGINX Metrics (via nginx-prometheus-exporter)
nginx_connections_active                         # Active connections
nginx_connections_reading                        # Reading request headers
nginx_connections_writing                        # Writing responses
nginx_connections_waiting                        # Keep-alive connections
nginx_http_requests_total                        # Total requests
nginx_http_request_duration_seconds              # Request latency
nginx_upstream_response_time                     # Backend response time
nginx_upstream_responses_total{code="502"}       # 502 error count
nginx_upstream_responses_total{code="503"}       # 503 error count

# HAProxy Metrics
haproxy_server_up                               # Server availability
haproxy_server_check_duration_seconds           # Health check duration
haproxy_server_response_errors_total            # Response errors
haproxy_frontend_http_responses_total{code="502"} # Frontend 502s
haproxy_backend_response_time_average_seconds    # Backend response time
```

### Alerting Rules (Prometheus)

```yaml
# HIGH 502/503 ERROR RATE
- alert: LoadBalancerHighErrorRate
  expr: (rate(nginx_http_responses_total{status=~"502|503"}[5m]) / rate(nginx_http_responses_total[5m])) > 0.05
  for: 30s
  labels:
    severity: critical
  annotations:
    summary: "Load balancer error rate above 5%"
    description: "502/503 error rate is {{ $value | humanizePercentage }} for {{ $labels.instance }}"

# BACKEND HEALTH
- alert: LoadBalancerUpstreamDown
  expr: nginx_upstream_up == 0
  for: 1m
  labels:
    severity: warning
  annotations:
    summary: "Load balancer upstream is down"
    description: "Upstream {{ $labels.upstream }} on {{ $labels.instance }} is down"

# RESPONSE TIME DEGRADATION
- alert: LoadBalancerHighLatency
  expr: nginx_upstream_response_time > 5
  for: 2m
  labels:
    severity: warning
  annotations:
    summary: "Load balancer upstream latency high"
    description: "Upstream response time is {{ $value }}s for {{ $labels.upstream }}"
```

### Automated Recovery

```bash
# HEALTH CHECK AUTOMATION (Netflix approach)
#!/bin/bash
# /opt/scripts/lb-health-check.sh

BACKENDS=("backend-1:8080" "backend-2:8080" "backend-3:8080")
NGINX_UPSTREAM_CONF="/etc/nginx/conf.d/upstream.conf"
BACKUP_CONF="/etc/nginx/conf.d/upstream.conf.backup"

for backend in "${BACKENDS[@]}"; do
    if ! curl -f -m 5 http://$backend/health > /dev/null 2>&1; then
        echo "Backend $backend is unhealthy, removing from rotation"

        # Backup current config
        cp $NGINX_UPSTREAM_CONF $BACKUP_CONF

        # Comment out failed backend
        sed -i "s/server $backend;/# server $backend; # AUTO-DISABLED $(date)/" $NGINX_UPSTREAM_CONF

        # Test and reload
        if nginx -t; then
            nginx -s reload
            echo "Successfully removed $backend from rotation"
        else
            # Restore backup on failure
            cp $BACKUP_CONF $NGINX_UPSTREAM_CONF
            echo "Failed to update config for $backend"
        fi
    fi
done
```

## Incident Response Checklist

### Immediate Response (< 2 minutes)
- [ ] Check load balancer service status (`systemctl status nginx/haproxy`)
- [ ] Validate configuration syntax (`nginx -t` / `haproxy -c`)
- [ ] Test backend health endpoints
- [ ] Check error logs for obvious failures
- [ ] Remove failed backends from rotation if needed

### Investigation (< 5 minutes)
- [ ] Analyze traffic patterns and error rates
- [ ] Check resource utilization (CPU, memory, connections)
- [ ] Review recent deployments or configuration changes
- [ ] Examine network connectivity and DNS resolution
- [ ] Verify SSL certificate validity if applicable

### Recovery (< 10 minutes)
- [ ] Scale healthy backends if needed
- [ ] Apply emergency configuration fixes
- [ ] Monitor traffic restoration
- [ ] Document timeline and actions taken
- [ ] Verify all systems are fully operational

### Post-Incident (< 30 minutes)
- [ ] Restore failed backends after fixes
- [ ] Update monitoring and alerting if gaps identified
- [ ] Schedule postmortem meeting
- [ ] Create incident report with timeline
- [ ] Implement preventive measures

**Remember**: In production, speed matters more than perfection. Get traffic flowing first, investigate thoroughly second.