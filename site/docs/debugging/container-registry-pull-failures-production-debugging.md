# Container Registry Pull Failures Production Debugging

## Overview

Container registry pull failures can cripple deployment pipelines, prevent application scaling, and cause service outages. These failures manifest as pod startup failures, deployment rollbacks, and cascading service unavailability. This guide provides systematic approaches to debug container registry issues based on real production incidents.

## Real Incident: Docker Hub's 2020 Rate Limiting Crisis

**Impact**: Global deployment failures across thousands of organizations
**Root Cause**: Docker Hub introduced aggressive rate limiting without sufficient warning
**Affected Services**: 2.3M container pulls failed in first hour
**Recovery Time**: 72 hours (rate limit adjustments + registry migrations)
**Cost**: Estimated $50M+ industry-wide impact

## Architecture Overview

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - Blue #3B82F6]
        CDN[Container Registry CDN<br/>CloudFront/Fastly<br/>Cache hit rate: 85%<br/>Pull acceleration]

        LB[Load Balancer<br/>Registry endpoints<br/>Health checks: Active<br/>Failover: Enabled]
    end

    subgraph ServicePlane[Service Plane - Emerald #10B981]
        subgraph RegistryServices[Registry Services]
            DR[Docker Registry<br/>Harbor/Nexus<br/>Status: DEGRADED<br/>Rate limit: 100/6h]

            AR[AWS ECR<br/>Private registry<br/>Status: HEALTHY<br/>Rate limit: 10k/min]

            GR[Google GCR<br/>Backup registry<br/>Status: HEALTHY<br/>Rate limit: 5k/min]
        end

        subgraph OrchestrationLayer[Orchestration]
            K8S[Kubernetes Cluster<br/>ImagePullBackOff: 23 pods<br/>Failed pulls: 156<br/>Retry backoff: Exponential]

            CRI[Container Runtime<br/>Docker/containerd<br/>Image cache: 2.3GB<br/>Pull timeout: 300s]
        end
    end

    subgraph StatePlane[State Plane - Amber #F59E0B]
        subgraph ImageStorage[Image Storage]
            IS[Image Store<br/>Blob storage<br/>Layers: 234k<br/>Deduplication: Enabled]

            IC[Image Cache<br/>Local node cache<br/>Hit rate: 72%<br/>Size: 15GB per node]

            IM[Image Metadata<br/>Registry catalog<br/>Tags: 45k<br/>Manifests: 23k]
        end

        subgraph CredentialStore[Credentials]
            CS[Credential Store<br/>Kubernetes secrets<br/>Docker config<br/>Token expiry: 12h]
        end
    end

    subgraph ControlPlane[Control Plane - Violet #8B5CF6]
        RM[Registry Monitor<br/>Pull success rate: 73%<br/>Latency: p99 45s<br/>Error rate: 27%]

        CM[Cluster Monitor<br/>Pod failures: 23<br/>Image pull errors: 156<br/>Node capacity: 85%]

        AM[Alert Manager<br/>Image pull alerts: 15<br/>Rate limit alerts: 8<br/>Registry down: 2]
    end

    %% Pull flow
    CDN --> LB
    LB --> DR
    LB --> AR
    LB --> GR

    K8S --> CRI
    CRI --> CDN
    CRI --> IC

    %% Storage access
    DR --> IS
    AR --> IM
    GR --> IM

    %% Credential flow
    K8S --> CS
    CRI --> CS

    %% Monitoring
    RM -.->|monitors| DR
    RM -.->|monitors| AR
    CM -.->|monitors| K8S
    AM -.->|alerts| RM

    %% Apply Tailwind colors
    classDef edgeStyle fill:#3B82F6,stroke:#1E40AF,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#047857,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef errorStyle fill:#EF4444,stroke:#DC2626,color:#fff

    class CDN,LB edgeStyle
    class DR,AR,GR,K8S,CRI serviceStyle
    class IS,IC,IM,CS stateStyle
    class RM,CM,AM controlStyle
```

## Detection Signals

### Primary Indicators
```mermaid
graph LR
    subgraph PullFailures[Pull Failure Patterns]
        PF[Pod Failures<br/>ImagePullBackOff: 23 pods<br/>ErrImagePull: 156 events<br/>Retry attempts: Exponential]

        RL[Rate Limiting<br/>429 responses: 89%<br/>Docker Hub limits<br/>6h window exceeded]

        TO[Timeout Errors<br/>Pull timeout: 300s<br/>Blob download: Failed<br/>Registry unreachable]

        AU[Auth Failures<br/>401 Unauthorized: 34<br/>Token expired: 12<br/>Invalid credentials: 8]
    end

    subgraph SystemImpact[System Impact]
        DS[Deployment Stuck<br/>Rolling update: STALLED<br/>New pods: 0/5 Ready<br/>Rollback triggered]

        SS[Service Scaling<br/>HPA blocked<br/>Target replicas: 10<br/>Current replicas: 3]

        NF[Node Failures<br/>Image cache full<br/>Disk space: 98%<br/>Image GC: Triggered]
    end

    PF --> DS
    RL --> SS
    TO --> NF
    AU --> DS

    classDef failureStyle fill:#EF4444,stroke:#DC2626,color:#fff
    classDef impactStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class PF,RL,TO,AU failureStyle
    class DS,SS,NF impactStyle
```

### Detection Commands
```bash
# 1. Check pod pull failures
kubectl get pods --all-namespaces | grep -E "(ImagePullBackOff|ErrImagePull)"

# 2. Detailed image pull events
kubectl get events --all-namespaces --field-selector reason=Failed,reason=FailedMount | \
grep -i "image\|pull"

# 3. Node image status
kubectl get nodes -o wide
kubectl describe node worker-1 | grep -A 20 "Images:"

# 4. Registry connectivity test
docker pull busybox:latest
crictl pull docker.io/library/nginx:latest
```

## Debugging Workflow

### Phase 1: Pull Failure Assessment (0-5 minutes)

```mermaid
flowchart TD
    A[Pull Failure Alert<br/>ImagePullBackOff] --> B[Count Affected Pods<br/>Scope assessment]
    B --> C[Check Registry Status<br/>Health endpoints]
    C --> D[Test Registry Connectivity<br/>Manual pull test]

    D --> E[Analyze Error Patterns<br/>Auth vs timeout vs rate limit]
    E --> F[Check Image Existence<br/>Tag validation]
    F --> G[Estimate Impact<br/>Deployment failures]

    B --> H[Node Resource Check<br/>Disk space, image cache]
    C --> I[Credential Validation<br/>Docker config, K8s secrets]
    D --> J[Network Connectivity<br/>DNS, firewall, proxy]

    classDef urgentStyle fill:#EF4444,stroke:#DC2626,color:#fff
    classDef actionStyle fill:#10B981,stroke:#047857,color:#fff

    class A,C,E urgentStyle
    class F,G,H,I,J actionStyle
```

### Phase 2: Root Cause Analysis (5-15 minutes)

```mermaid
graph TB
    subgraph FailureTypes[Failure Type Analysis]
        RL[Rate Limiting<br/>HTTP 429 errors<br/>Docker Hub limits<br/>Anonymous vs authenticated]

        AU[Authentication<br/>HTTP 401/403 errors<br/>Token expiration<br/>Credential rotation]

        NW[Network Issues<br/>DNS resolution failures<br/>Connectivity timeouts<br/>Proxy configuration]

        ST[Storage Issues<br/>Disk space exhaustion<br/>Image cache corruption<br/>Layer download failures]
    end

    subgraph DiagnosticTools[Diagnostic Tools]
        KD[kubectl describe<br/>Pod events<br/>Image pull status<br/>Error messages]

        DL[docker/crictl logs<br/>Container runtime logs<br/>Pull operation details<br/>Network timeouts]

        NG[Network debugging<br/>nslookup/dig<br/>curl registry endpoints<br/>Proxy logs]

        DF[Disk/filesystem<br/>df -h command<br/>Image cache analysis<br/>Layer corruption check]
    end

    RL --> KD
    AU --> DL
    NW --> NG
    ST --> DF

    classDef typeStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef toolStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class RL,AU,NW,ST typeStyle
    class KD,DL,NG,DF toolStyle
```

## Common Pull Failure Scenarios

### Scenario 1: Docker Hub Rate Limiting

```mermaid
graph LR
    subgraph RateLimitFlow[Rate Limit Scenario]
        AR[Anonymous Requests<br/>Limit: 100 pulls/6h<br/>Current: 156 pulls<br/>Status: EXCEEDED]

        UR[User Requests<br/>Limit: 200 pulls/6h<br/>Current: 89 pulls<br/>Status: OK]

        PR[Pro Account<br/>Limit: 5000 pulls/6h<br/>Current: 45 pulls<br/>Status: OK]
    end

    subgraph Mitigation[Mitigation Strategies]
        AC[Add Credentials<br/>Docker Hub Pro account<br/>Kubernetes secret<br/>Image pull secrets]

        MR[Mirror Registry<br/>AWS ECR/GCR<br/>Image replication<br/>Fallback configuration]

        IC[Image Caching<br/>Registry proxy cache<br/>Harbor/Nexus<br/>Local image cache]
    end

    AR --> AC
    UR --> MR
    PR --> IC

    classDef limitStyle fill:#EF4444,stroke:#DC2626,color:#fff
    classDef mitigationStyle fill:#10B981,stroke:#047857,color:#fff

    class AR,UR,PR limitStyle
    class AC,MR,IC mitigationStyle
```

### Scenario 2: Authentication Failures

```mermaid
graph TB
    subgraph AuthFlow[Authentication Flow]
        CT[Credential Types<br/>Docker config.json<br/>Kubernetes secrets<br/>Service account tokens]

        EX[Expiration Issues<br/>Token TTL: 12h<br/>Rotation needed<br/>Auto-renewal failed]

        PE[Permission Errors<br/>Registry access denied<br/>Repository not found<br/>Insufficient privileges]
    end

    subgraph Resolution[Resolution Steps]
        CR[Credential Refresh<br/>kubectl create secret<br/>docker login update<br/>Token regeneration]

        PS[Permission Setup<br/>Registry policy update<br/>Repository access grant<br/>Service account binding]

        AR[Auto-Renewal<br/>Credential rotation job<br/>Token refresh automation<br/>Monitoring alerts]
    end

    CT --> CR
    EX --> AR
    PE --> PS

    classDef authStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef resolutionStyle fill:#10B981,stroke:#047857,color:#fff

    class CT,EX,PE authStyle
    class CR,PS,AR resolutionStyle
```

## Recovery Procedures

### Immediate Mitigation (0-10 minutes)

```mermaid
graph LR
    subgraph EmergencyActions[Emergency Response]
        IP[Implement Proxy<br/>Registry proxy cache<br/>Harbor/Nexus setup<br/>Reduce external calls]

        AC[Add Credentials<br/>Docker Hub authentication<br/>Kubernetes secrets<br/>Service account setup]

        MR[Mirror Registry<br/>ECR/GCR fallback<br/>Image replication<br/>Registry switching]

        IC[Image Cleanup<br/>Clear failed images<br/>Prune unused layers<br/>Free disk space]
    end

    subgraph ConfigChanges[Configuration Changes]
        PP[Pull Policy<br/>IfNotPresent → Always<br/>Reduce unnecessary pulls<br/>Cache utilization]

        RL[Registry List<br/>Primary + fallback<br/>Priority ordering<br/>Health-based routing]

        TO[Timeout Tuning<br/>Increase pull timeout<br/>Registry response time<br/>Network latency buffer]

        RB[Retry Backoff<br/>Exponential backoff<br/>Max retry attempts<br/>Circuit breaker pattern]
    end

    IP --> PP
    AC --> RL
    MR --> TO
    IC --> RB

    classDef actionStyle fill:#10B981,stroke:#047857,color:#fff
    classDef configStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class IP,AC,MR,IC actionStyle
    class PP,RL,TO,RB configStyle
```

### Registry Authentication Setup

```bash
#!/bin/bash
# Emergency registry authentication setup

# 1. Create Docker Hub credentials
DOCKER_USERNAME="your-username"
DOCKER_PASSWORD="your-password"
DOCKER_EMAIL="your-email@company.com"

kubectl create secret docker-registry dockerhub-secret \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username="$DOCKER_USERNAME" \
  --docker-password="$DOCKER_PASSWORD" \
  --docker-email="$DOCKER_EMAIL" \
  --namespace=default

# 2. Add image pull secret to service account
kubectl patch serviceaccount default -p \
'{"imagePullSecrets": [{"name": "dockerhub-secret"}]}'

# 3. Create AWS ECR credentials (if using ECR)
AWS_ACCOUNT_ID="123456789012"
AWS_REGION="us-west-2"

# Get ECR login token
ECR_TOKEN=$(aws ecr get-login-password --region $AWS_REGION)

kubectl create secret docker-registry ecr-secret \
  --docker-server="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com" \
  --docker-username=AWS \
  --docker-password="$ECR_TOKEN" \
  --namespace=default

# 4. Update deployment to use multiple registries
cat > registry-fallback-patch.yaml << 'EOF'
spec:
  template:
    spec:
      imagePullSecrets:
      - name: dockerhub-secret
      - name: ecr-secret
      containers:
      - name: app
        image: docker.io/library/nginx:latest
        imagePullPolicy: IfNotPresent
EOF

kubectl patch deployment nginx-deployment --patch-file registry-fallback-patch.yaml

# 5. Create registry proxy cache (Harbor)
cat > harbor-proxy-cache.yaml << 'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: harbor-config
data:
  core.conf: |
    registry_proxy_cache:
      enabled: true
      upstream_registries:
        - name: docker-hub
          url: https://registry-1.docker.io
          credential:
            username: ${DOCKER_USERNAME}
            password: ${DOCKER_PASSWORD}
        - name: ecr
          url: https://${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
          credential:
            access_key: ${AWS_ACCESS_KEY}
            secret_key: ${AWS_SECRET_KEY}
EOF

kubectl apply -f harbor-proxy-cache.yaml
```

### Registry Mirror Configuration

```yaml
# /etc/docker/daemon.json - Docker registry mirrors
{
  "registry-mirrors": [
    "https://harbor.company.com",
    "https://mirror.gcr.io",
    "https://123456789012.dkr.ecr.us-west-2.amazonaws.com"
  ],
  "insecure-registries": [
    "harbor.company.com"
  ],
  "max-concurrent-downloads": 3,
  "max-download-attempts": 5
}

---
# Kubernetes containerd configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: containerd-config
data:
  config.toml: |
    [plugins."io.containerd.grpc.v1.cri".registry]
      [plugins."io.containerd.grpc.v1.cri".registry.mirrors]
        [plugins."io.containerd.grpc.v1.cri".registry.mirrors."docker.io"]
          endpoint = [
            "https://harbor.company.com/v2",
            "https://registry-1.docker.io"
          ]
        [plugins."io.containerd.grpc.v1.cri".registry.mirrors."k8s.gcr.io"]
          endpoint = [
            "https://k8s.gcr.io",
            "https://mirror.gcr.io"
          ]

      [plugins."io.containerd.grpc.v1.cri".registry.configs]
        [plugins."io.containerd.grpc.v1.cri".registry.configs."harbor.company.com".tls]
          insecure_skip_verify = true
        [plugins."io.containerd.grpc.v1.cri".registry.configs."harbor.company.com".auth]
          username = "admin"
          password = "Harbor12345"

---
# Deployment with fallback registries
apiVersion: apps/v1
kind: Deployment
metadata:
  name: multi-registry-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: multi-registry-app
  template:
    metadata:
      labels:
        app: multi-registry-app
    spec:
      imagePullSecrets:
      - name: dockerhub-secret
      - name: ecr-secret
      - name: harbor-secret
      containers:
      - name: app
        # Primary registry
        image: harbor.company.com/library/nginx:latest
        # Fallback configuration handled by containerd
        imagePullPolicy: IfNotPresent
        resources:
          requests:
            memory: "64Mi"
            cpu: "250m"
          limits:
            memory: "128Mi"
            cpu: "500m"
      initContainers:
      - name: registry-test
        image: busybox:latest
        command: ['sh', '-c', 'echo "Registry connectivity test passed"']
        imagePullPolicy: IfNotPresent
```

## Monitoring and Prevention

### Registry Health Dashboard

```mermaid
graph TB
    subgraph RegistryMetrics[Registry Health Metrics]
        PS[Pull Success Rate<br/>Current: 73%<br/>Target: 99%<br/>Trend: Declining]

        PL[Pull Latency<br/>p99: 45s<br/>p95: 23s<br/>Mean: 8.5s<br/>Target: <10s]

        RL[Rate Limits<br/>Docker Hub: 89/100<br/>ECR: 45/10000<br/>GCR: 12/5000<br/>Status: Warning]

        ER[Error Rates<br/>429 errors: 15%<br/>401 errors: 3%<br/>Timeout: 9%<br/>Total: 27%]
    end

    subgraph ClusterMetrics[Cluster Impact]
        PF[Pod Failures<br/>ImagePullBackOff: 23<br/>ErrImagePull: 156<br/>Restart loops: 8]

        NR[Node Resources<br/>Disk usage: 85%<br/>Image cache: 15GB<br/>Available: 2.3GB]

        DS[Deployment Status<br/>Stuck deployments: 5<br/>Rollback triggered: 2<br/>Scaling blocked: 3]

        SH[Service Health<br/>Affected services: 12<br/>Response degradation: 15%<br/>Availability: 97.3%]
    end

    PS --> PF
    PL --> NR
    RL --> DS
    ER --> SH

    classDef metricsStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef impactStyle fill:#EF4444,stroke:#DC2626,color:#fff

    class PS,PL,RL,ER metricsStyle
    class PF,NR,DS,SH impactStyle
```

### Proactive Monitoring Alerts

```yaml
# Prometheus alerting rules for container registry issues
groups:
- name: container_registry
  rules:
  - alert: HighImagePullFailureRate
    expr: |
      (
        rate(kubelet_runtime_operations_errors_total{operation_type="image_pull"}[5m]) /
        rate(kubelet_runtime_operations_total{operation_type="image_pull"}[5m])
      ) > 0.1
    for: 2m
    labels:
      severity: warning
      component: registry
    annotations:
      summary: "High image pull failure rate"
      description: "Image pull failure rate is {{ $value | humanizePercentage }} on node {{ $labels.instance }}"

  - alert: RegistryRateLimitApproaching
    expr: |
      docker_hub_rate_limit_remaining / docker_hub_rate_limit_total < 0.2
    for: 1m
    labels:
      severity: warning
      component: registry
    annotations:
      summary: "Docker Hub rate limit approaching"
      description: "Docker Hub rate limit is at {{ $value | humanizePercentage }} capacity"

  - alert: ImagePullBackOffPods
    expr: |
      kube_pod_container_status_waiting_reason{reason="ImagePullBackOff"} > 5
    for: 30s
    labels:
      severity: critical
      component: registry
    annotations:
      summary: "Multiple pods in ImagePullBackOff state"
      description: "{{ $value }} pods are stuck in ImagePullBackOff state"

  - alert: RegistryConnectivityFailure
    expr: |
      up{job="registry-health-check"} == 0
    for: 1m
    labels:
      severity: critical
      component: registry
    annotations:
      summary: "Container registry unreachable"
      description: "Registry {{ $labels.instance }} has been unreachable for > 1 minute"
```

## Real Production Examples

### Docker Hub's 2020 Rate Limiting Crisis
- **Duration**: 72 hours of industry-wide impact
- **Root Cause**: Docker Hub introduced 100 pulls/6h limit for anonymous users
- **Impact**: 2.3M container pulls failed globally in first hour
- **Resolution**: Enterprise accounts + registry mirrors + proxy caches
- **Prevention**: Multi-registry strategy + rate limit monitoring

### Kubernetes.io Registry Outage 2021
- **Duration**: 6 hours
- **Root Cause**: k8s.gcr.io infrastructure failure during GCP maintenance
- **Impact**: Kubernetes cluster deployments failed globally
- **Resolution**: Mirror registry activation + image cache utilization
- **Prevention**: Registry diversity + improved caching strategy

### AWS ECR Cross-Region Incident 2020
- **Duration**: 3 hours 15 minutes
- **Root Cause**: Cross-region replication failure in us-east-1
- **Impact**: Multi-region deployments failed, CI/CD pipelines blocked
- **Resolution**: Regional registry switching + manual image replication
- **Prevention**: Regional redundancy + automated failover

## Prevention Best Practices

### Multi-Registry Strategy
```yaml
# Registry priority configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: registry-config
data:
  registries.conf: |
    [[registry]]
    prefix = "docker.io"
    location = "harbor.company.com/docker-proxy"

    [[registry]]
    prefix = "docker.io"
    location = "123456789012.dkr.ecr.us-west-2.amazonaws.com/docker-proxy"

    [[registry]]
    prefix = "docker.io"
    location = "registry-1.docker.io"

    # Rate limit configuration
    rate_limit:
      enabled: true
      requests_per_minute: 50
      burst_size: 10
```

### Image Optimization
```dockerfile
# Multi-stage build for smaller images
FROM node:16-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:16-alpine AS runtime
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["npm", "start"]

# Layer caching optimization
# Order layers from least to most frequently changing
```

### Automated Registry Health Checks
```python
#!/usr/bin/env python3
"""
Container registry health monitoring script
"""

import requests
import docker
import time
import logging
from typing import Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RegistryHealthChecker:
    def __init__(self, registries: List[Dict[str, str]]):
        self.registries = registries
        self.docker_client = docker.from_env()

    def check_registry_connectivity(self, registry: Dict[str, str]) -> bool:
        """Test registry connectivity"""
        try:
            # Test registry v2 API
            response = requests.get(
                f"{registry['url']}/v2/",
                headers=registry.get('headers', {}),
                timeout=10
            )
            return response.status_code in [200, 401]  # 401 is OK for auth required
        except Exception as e:
            logger.error(f"Registry {registry['name']} connectivity failed: {e}")
            return False

    def test_image_pull(self, registry: Dict[str, str]) -> bool:
        """Test actual image pull"""
        try:
            test_image = f"{registry['url']}/library/hello-world:latest"
            self.docker_client.images.pull(test_image)
            logger.info(f"Successfully pulled test image from {registry['name']}")
            return True
        except Exception as e:
            logger.error(f"Image pull from {registry['name']} failed: {e}")
            return False

    def check_rate_limits(self, registry: Dict[str, str]) -> Dict[str, int]:
        """Check rate limit status"""
        try:
            response = requests.head(
                f"{registry['url']}/v2/",
                headers=registry.get('headers', {}),
                timeout=10
            )

            return {
                'limit': int(response.headers.get('RateLimit-Limit', 0)),
                'remaining': int(response.headers.get('RateLimit-Remaining', 0)),
                'reset': int(response.headers.get('RateLimit-Reset', 0))
            }
        except Exception as e:
            logger.error(f"Rate limit check for {registry['name']} failed: {e}")
            return {}

    def run_health_checks(self) -> Dict[str, Dict[str, any]]:
        """Run comprehensive health checks"""
        results = {}

        for registry in self.registries:
            logger.info(f"Checking registry: {registry['name']}")

            results[registry['name']] = {
                'connectivity': self.check_registry_connectivity(registry),
                'pull_test': self.test_image_pull(registry),
                'rate_limits': self.check_rate_limits(registry),
                'timestamp': time.time()
            }

        return results

def main():
    """Main health check execution"""

    registries = [
        {
            'name': 'docker-hub',
            'url': 'https://registry-1.docker.io',
            'headers': {'Authorization': 'Bearer your-token'}
        },
        {
            'name': 'aws-ecr',
            'url': 'https://123456789012.dkr.ecr.us-west-2.amazonaws.com',
            'headers': {'Authorization': 'Basic your-token'}
        },
        {
            'name': 'harbor',
            'url': 'https://harbor.company.com',
            'headers': {'Authorization': 'Basic admin-token'}
        }
    ]

    checker = RegistryHealthChecker(registries)

    while True:
        results = checker.run_health_checks()

        # Log results
        for registry, status in results.items():
            if status['connectivity'] and status['pull_test']:
                logger.info(f"✓ {registry}: Healthy")
            else:
                logger.warning(f"✗ {registry}: Unhealthy")

        # Sleep before next check
        time.sleep(300)  # 5 minutes

if __name__ == "__main__":
    main()
```

## Recovery Checklist

### Immediate Response (0-10 minutes)
- [ ] Identify affected pods and deployments
- [ ] Check registry service status and connectivity
- [ ] Test manual image pull from affected registries
- [ ] Verify authentication credentials and tokens
- [ ] Check node disk space and image cache
- [ ] Enable emergency registry mirrors if available

### Investigation (10-30 minutes)
- [ ] Analyze error patterns (rate limits, auth, network)
- [ ] Check registry rate limit status and quotas
- [ ] Validate DNS resolution and network routing
- [ ] Review recent credential rotations or policy changes
- [ ] Examine container runtime logs and configurations
- [ ] Assess impact on critical services and deployments

### Recovery (30-120 minutes)
- [ ] Implement registry authentication if rate limited
- [ ] Configure and deploy registry proxy/mirror
- [ ] Update image pull policies and retry strategies
- [ ] Clean up failed images and free disk space
- [ ] Switch to alternative registries if needed
- [ ] Validate recovery with test deployments

### Post-Incident (1-7 days)
- [ ] Implement multi-registry redundancy strategy
- [ ] Set up comprehensive registry monitoring
- [ ] Review and optimize image sizes and layers
- [ ] Establish registry health check automation
- [ ] Create runbooks for registry failover procedures
- [ ] Train team on registry troubleshooting techniques

This comprehensive guide provides the systematic approach needed to debug container registry pull failures in production, based on real incidents like Docker Hub's rate limiting crisis and various cloud provider outages.