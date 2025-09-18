# Memory Leak Detection and Emergency Response

> **3 AM Emergency Protocol**: Memory leaks can cause OOMKills and cascade to entire node failures. This diagram shows how to quickly identify, contain, and resolve memory exhaustion before it spreads.

## Quick Detection Checklist
- [ ] Monitor memory growth: `free -h` and `ps aux --sort=-%mem | head -10`
- [ ] Check OOMKills: `dmesg | grep -i "killed process"` and `journalctl -u kubelet | grep OOMKilled`
- [ ] Watch heap dumps: `jmap -histo [pid]` for Java, `pmap -x [pid]` for native
- [ ] Alert on memory trends: `rate(container_memory_usage_bytes[5m]) > 0` over 30 minutes

## Memory Leak Detection and Mitigation

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - Load Sources]
        USERS[Active Users<br/>Current: 50,000<br/>Memory per session: 2MB]
        BOTS[Bot Traffic<br/>Detected: 5,000 req/min<br/>Memory pattern: Abnormal]
        BATCH[Batch Jobs<br/>Running: 10 concurrent<br/>Memory: Growing unbounded]
    end

    subgraph ServicePlane[Service Plane - Memory Consumers]
        subgraph API_PODS[API Service Pods]
            API_1[API Pod 1<br/>Memory: 6GB/8GB (75%)<br/>Trend: +50MB/hour<br/>Status: WARNING]
            API_2[API Pod 2<br/>Memory: 7.5GB/8GB (94%)<br/>Trend: +100MB/hour<br/>Status: CRITICAL]
            API_3[API Pod 3<br/>Memory: 7.8GB/8GB (98%)<br/>Trend: +200MB/hour<br/>Status: OOM IMMINENT]
        end

        subgraph WORKER_PODS[Worker Service Pods]
            WORKER_1[Worker Pod 1<br/>Memory: 3GB/4GB (75%)<br/>Processing: Image uploads<br/>Heap growth: Linear]
            WORKER_2[Worker Pod 2<br/>Memory: 3.9GB/4GB (97%)<br/>Processing: Video encoding<br/>LEAK DETECTED]
        end

        LB[Load Balancer<br/>Health check: /health<br/>Memory threshold: 90%<br/>Auto-restart: Enabled]
    end

    subgraph StatePlane[State Plane - Memory Pressure]
        NODE_1[Node 1<br/>Memory: 28GB/32GB (87%)<br/>Available: 4GB<br/>Swap: 2GB used]
        NODE_2[Node 2<br/>Memory: 30GB/32GB (94%)<br/>Available: 2GB<br/>Swap: 4GB used]
        NODE_3[Node 3<br/>Memory: 31.5GB/32GB (98%)<br/>Available: 512MB<br/>Status: CRITICAL]

        CACHE[(Redis Cache<br/>Memory: 10GB/12GB<br/>Eviction policy: allkeys-lru<br/>Hit ratio: Degrading)]
        DB[(Database<br/>Buffer pool: 8GB/10GB<br/>Query cache: Full<br/>Temp tables: Growing)]
    end

    subgraph ControlPlane[Control Plane - Memory Management]
        MONITOR[Memory Monitoring<br/>Prometheus + Grafana<br/>Alert threshold: 85%<br/>Trend analysis: Enabled]

        subgraph RESPONSE[Emergency Response]
            OOM_KILLER[OOM Killer<br/>Kernel mechanism<br/>Last killed: worker-2<br/>Score adjustment: -999]
            AUTO_RESTART[Auto Restart<br/>Kubernetes policy<br/>Restart count: 5<br/>Backoff: Exponential]
            SCALE_OUT[Horizontal Scaling<br/>HPA triggered<br/>Target CPU: 70%<br/>Target Memory: 80%]
        end

        HEAP_ANALYSIS[Heap Analysis<br/>Memory profiling<br/>Leak detection tools<br/>Root cause identification]
    end

    %% Memory consumption flow
    USERS -->|"Session data"| API_1
    USERS -->|"Session data"| API_2
    BOTS -.->|"Abnormal patterns"| API_3
    BATCH -->|"Large payloads"| WORKER_1
    BATCH -.->|"Memory leak"| WORKER_2

    %% Load balancing with health checks
    LB --> API_1
    LB --> API_2
    LB -.->|"Health check failing"| API_3

    %% Node pressure
    API_1 --> NODE_1
    API_2 --> NODE_2
    API_3 --> NODE_3
    WORKER_1 --> NODE_1
    WORKER_2 --> NODE_2

    %% Cache and database pressure
    API_1 --> CACHE
    API_2 --> CACHE
    API_3 --> DB
    WORKER_1 --> DB

    %% Monitoring and alerts
    NODE_1 --> MONITOR
    NODE_2 --> MONITOR
    NODE_3 --> MONITOR
    CACHE --> MONITOR
    DB --> MONITOR

    %% Emergency responses
    MONITOR -->|"OOM threshold"| OOM_KILLER
    MONITOR -->|"Pod restart"| AUTO_RESTART
    MONITOR -->|"Scale trigger"| SCALE_OUT
    OOM_KILLER -.->|"Kill process"| API_3
    AUTO_RESTART -.->|"Restart pod"| WORKER_2
    SCALE_OUT -->|"Add replicas"| API_PODS

    %% Analysis and debugging
    MONITOR --> HEAP_ANALYSIS
    HEAP_ANALYSIS -.->|"Profile memory"| API_PODS
    HEAP_ANALYSIS -.->|"Identify leaks"| WORKER_PODS

    %% 4-plane styling
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff
    classDef criticalStyle fill:#FF0000,stroke:#CC0000,color:#fff
    classDef warningStyle fill:#FFA500,stroke:#CC8800,color:#fff

    class USERS,BOTS,BATCH edgeStyle
    class API_1,API_2,API_3,WORKER_1,WORKER_2,LB serviceStyle
    class NODE_1,NODE_2,NODE_3,CACHE,DB stateStyle
    class MONITOR,OOM_KILLER,AUTO_RESTART,SCALE_OUT,HEAP_ANALYSIS controlStyle
    class API_3,WORKER_2,NODE_3 criticalStyle
    class API_1,WORKER_1,NODE_1 warningStyle
```

## 3 AM Emergency Response Commands

### 1. Immediate Memory Assessment (30 seconds)
```bash
# Check system memory status
free -h
cat /proc/meminfo | grep -E "(MemTotal|MemAvailable|MemFree)"

# Identify memory hogs
ps aux --sort=-%mem | head -10
pmap -x $(pgrep -f "java|node|python") | tail -1

# Check for OOM kills
dmesg | grep -i "killed process" | tail -5
journalctl -u kubelet --since="10 minutes ago" | grep OOMKilled
```

### 2. Emergency Memory Recovery (60 seconds)
```bash
# Restart highest memory consuming pods
kubectl get pods --sort-by='.status.containerStatuses[0].restartCount' -o wide
kubectl delete pod $(kubectl get pods --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}')

# Force garbage collection (Java applications)
jcmd $(pgrep java) GC.run_finalization
jcmd $(pgrep java) GC.run

# Clear system caches if safe
echo 3 > /proc/sys/vm/drop_caches  # Only if system is stable
```

### 3. Scale and Mitigate (90 seconds)
```bash
# Horizontal pod autoscaling
kubectl scale deployment api-service --replicas=6
kubectl scale deployment worker-service --replicas=4

# Adjust memory limits temporarily
kubectl patch deployment api-service -p '{"spec":{"template":{"spec":{"containers":[{"name":"api","resources":{"limits":{"memory":"12Gi"}}}]}}}}'

# Route traffic away from problematic nodes
kubectl cordon node-with-memory-pressure
kubectl drain node-with-memory-pressure --ignore-daemonsets --delete-emptydir-data
```

## Memory Leak Pattern Recognition

### Linear Memory Growth (Classic Leak)
```
Time    Process_Memory    Available_Memory    Trend
10:00   2.1GB            29.9GB              Baseline
10:15   2.5GB            29.5GB              +26MB/min
10:30   2.9GB            29.1GB              +26MB/min
10:45   3.3GB            28.7GB              +26MB/min
11:00   3.7GB            28.3GB              LEAK CONFIRMED
```

### Exponential Memory Growth (Recursive Leak)
```
Time    Heap_Size    Objects_Count    Growth_Rate
10:00   512MB        1M objects       Baseline
10:05   1GB          2M objects       2x in 5min
10:10   2GB          4M objects       2x in 5min
10:15   4GB          8M objects       2x in 5min
10:20   8GB          16M objects      EXPONENTIAL LEAK
```

### Sawtooth Pattern (GC Pressure)
```
Time    Memory_Usage    GC_Frequency    Pattern
10:00   2GB → 4GB       Every 30s       Sawtooth
10:30   3GB → 6GB       Every 20s       Growing base
11:00   4GB → 8GB       Every 10s       GC thrashing
11:30   OOM             Continuous      FAILURE
```

## Error Message Patterns

### Kubernetes OOMKilled
```
ERROR: Pod was OOMKilled
PATTERN: "Last State: Terminated (Reason: OOMKilled)"
LOCATION: kubectl describe pod, kubelet logs
ACTION: Increase memory limits, investigate memory usage
COMMAND: kubectl describe pod [pod-name] | grep -A5 "Last State"
```

### Java OutOfMemoryError
```
ERROR: java.lang.OutOfMemoryError: Java heap space
PATTERN: Heap dump files (.hprof) generated
LOCATION: Application logs, heap dump directory
ACTION: Analyze heap dump, increase heap size
COMMAND: jmap -dump:live,format=b,file=heap.hprof [pid]
```

### Linux OOM Killer
```
ERROR: Out of memory: Kill process [pid]
PATTERN: "Killed process [pid] (java) total-vm:[size]"
LOCATION: /var/log/messages, dmesg output
ACTION: Increase system memory, tune OOM scores
COMMAND: echo -1000 > /proc/[pid]/oom_score_adj
```

## Memory Profiling and Analysis

### Java Heap Analysis
```bash
# Generate heap dump
jmap -dump:live,format=b,file=heap-$(date +%Y%m%d-%H%M%S).hprof $(pgrep java)

# Analyze heap usage
jmap -histo $(pgrep java) | head -20

# Monitor GC activity
jstat -gc $(pgrep java) 5s

# Use Eclipse MAT for deep analysis
# java -Xmx4g -jar org.eclipse.mat.api-1.12.0.jar heap.hprof
```

### Node.js Memory Analysis
```bash
# Generate heap snapshot
kill -USR2 $(pgrep node)  # If configured for heapdump

# Monitor V8 heap
node --inspect=0.0.0.0:9229 app.js
# Connect Chrome DevTools to ws://localhost:9229

# Use clinic.js for analysis
npm install -g clinic
clinic doctor -- node app.js
```

### Python Memory Profiling
```bash
# Install memory profiler
pip install memory-profiler psutil

# Profile memory usage
python -m memory_profiler app.py

# Generate memory timeline
mprof run python app.py
mprof plot

# Use py-spy for live profiling
py-spy record -o profile.svg --pid [pid] --duration 60
```

## Memory Leak Prevention Strategies

### Resource Limits and Monitoring
```yaml
# Kubernetes resource configuration
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-service
spec:
  template:
    spec:
      containers:
      - name: api
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"    # 2x request for headroom
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
```

### JVM Tuning for Memory Management
```bash
# JVM memory configuration
JAVA_OPTS="-Xms2g -Xmx4g \
  -XX:+UseG1GC \
  -XX:MaxGCPauseMillis=200 \
  -XX:+PrintGC \
  -XX:+PrintGCDetails \
  -XX:+PrintGCTimeStamps \
  -XX:+HeapDumpOnOutOfMemoryError \
  -XX:HeapDumpPath=/tmp/heapdumps/ \
  -XX:OnOutOfMemoryError='kubectl delete pod $HOSTNAME'"
```

### Memory Circuit Breakers
```python
# Python memory circuit breaker
import psutil
import gc

class MemoryCircuitBreaker:
    def __init__(self, threshold_percent=85):
        self.threshold = threshold_percent
        self.is_open = False

    def check_memory(self):
        memory_percent = psutil.virtual_memory().percent
        if memory_percent > self.threshold:
            if not self.is_open:
                self.is_open = True
                gc.collect()  # Force garbage collection
                print(f"Memory circuit breaker OPEN: {memory_percent}%")
                # Implement fallback behavior
                return False
        else:
            self.is_open = False
        return True

# Usage in request handler
breaker = MemoryCircuitBreaker(threshold_percent=85)

def handle_request(request):
    if not breaker.check_memory():
        return "Service temporarily unavailable - memory pressure"
    # Process request normally
```

## Recovery Procedures

### Phase 1: Immediate Stabilization (0-5 minutes)
- [ ] Identify and restart highest memory consuming pods
- [ ] Scale out healthy replicas to handle load
- [ ] Clear non-essential caches and buffers
- [ ] Route traffic away from affected nodes

### Phase 2: Root Cause Analysis (5-30 minutes)
- [ ] Generate heap dumps from affected services
- [ ] Analyze memory growth patterns and trends
- [ ] Identify specific memory leak sources
- [ ] Check for unusual traffic patterns or data

### Phase 3: Long-term Fix (30+ minutes)
- [ ] Deploy memory leak fixes
- [ ] Adjust resource limits based on analysis
- [ ] Implement additional monitoring and alerting
- [ ] Update auto-scaling policies and thresholds

## Memory Optimization Strategies

### Garbage Collection Tuning
```bash
# G1GC tuning for large heaps
-XX:+UseG1GC
-XX:MaxGCPauseMillis=100
-XX:G1HeapRegionSize=32m
-XX:G1NewSizePercent=20
-XX:G1MaxNewSizePercent=30
-XX:InitiatingHeapOccupancyPercent=45
```

### Memory-Efficient Data Structures
```java
// Use primitive collections instead of boxed types
import gnu.trove.map.TIntObjectMap;
import gnu.trove.map.hash.TIntObjectHashMap;

// Efficient memory usage
TIntObjectMap<String> efficientMap = new TIntObjectHashMap<>();
// Instead of Map<Integer, String> which boxes integers
```

### Connection Pool Optimization
```yaml
# Database connection pool tuning
spring:
  datasource:
    hikari:
      maximum-pool-size: 20      # Limit connections
      minimum-idle: 5            # Reduce idle connections
      idle-timeout: 300000       # 5 minutes
      max-lifetime: 1200000      # 20 minutes
      leak-detection-threshold: 60000  # 1 minute
```

## Real-World Memory Leak Incidents

### Uber Memory Leak (2020)
- **Cause**: Goroutine leak in Go service handling WebSocket connections
- **Impact**: 20GB memory growth over 6 hours, OOM kills every 30 minutes
- **Detection**: Prometheus memory metrics + pprof analysis
- **Fix**: Proper goroutine cleanup in connection handlers

### Shopify Rails Memory Bloat (2019)
- **Cause**: ActiveRecord objects not being garbage collected
- **Impact**: Ruby processes growing from 200MB to 2GB over 24 hours
- **Detection**: NewRelic memory tracking + Ruby heap dumps
- **Fix**: Explicit object disposal + memory profiling in CI

### Discord Memory Leak (2021)
- **Cause**: JavaScript event listeners not being removed
- **Impact**: Browser memory usage growing indefinitely
- **Detection**: Chrome DevTools memory snapshots
- **Fix**: Proper event listener cleanup + WeakMap usage

---
*Last Updated: Based on Uber, Shopify, Discord memory leak incidents*
*Next Review: Monitor for new memory leak patterns in containerized environments*