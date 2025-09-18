# CPU Spike Emergency Response

> **3 AM Emergency Protocol**: CPU spikes can cause cascading latency and service degradation. This diagram shows how to quickly identify CPU bottlenecks, mitigate immediate impact, and restore performance.

## Quick Detection Checklist
- [ ] Monitor CPU usage: `top -c` and `htop` for process-level analysis
- [ ] Check system load: `uptime` and `cat /proc/loadavg` for load averages
- [ ] Identify CPU hogs: `ps aux --sort=-%cpu | head -10`
- [ ] Alert on CPU trends: `rate(cpu_usage_percent[5m]) > 80%` sustained

## CPU Spike Detection and Emergency Response

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - Load Sources]
        TRAFFIC[Traffic Spike<br/>Current: 10,000 req/sec<br/>Normal: 2,000 req/sec<br/>Increase: 5x baseline]
        BOTS[Bot Activity<br/>Scraping attempts: 500/sec<br/>CPU-intensive parsing<br/>Pattern: Distributed]
        BATCH[Batch Processing<br/>Jobs queued: 50<br/>CPU per job: 2 cores<br/>Total demand: 100 cores]
    end

    subgraph ServicePlane[Service Plane - CPU Consumers]
        subgraph API_PODS[API Service Cluster]
            API_1[API Pod 1<br/>CPU: 95% (1.9/2.0 cores)<br/>Response time: 2000ms<br/>Status: THROTTLED]
            API_2[API Pod 2<br/>CPU: 98% (3.9/4.0 cores)<br/>Response time: 5000ms<br/>Status: OVERLOADED]
            API_3[API Pod 3<br/>CPU: 85% (1.7/2.0 cores)<br/>Response time: 500ms<br/>Status: HEALTHY]
        end

        subgraph WORKER_PODS[Background Workers]
            WORKER_1[Worker Pod 1<br/>CPU: 100% (4.0/4.0 cores)<br/>Task: Image processing<br/>Queue: Backing up]
            WORKER_2[Worker Pod 2<br/>CPU: 100% (4.0/4.0 cores)<br/>Task: Data analytics<br/>Memory: Growing]
        end

        LB[Load Balancer<br/>Health check: CPU < 90%<br/>Current routing: Failing<br/>Backup servers: Activating]
    end

    subgraph StatePlane[State Plane - System Resources]
        subgraph NODE_RESOURCES[Node Resources]
            NODE_1[Node 1<br/>CPU: 24/32 cores (75%)<br/>Load average: 28.5<br/>Status: HIGH LOAD]
            NODE_2[Node 2<br/>CPU: 31/32 cores (97%)<br/>Load average: 45.2<br/>Status: CRITICAL]
            NODE_3[Node 3<br/>CPU: 18/32 cores (56%)<br/>Load average: 12.1<br/>Status: HEALTHY]
        end

        subgraph SYSTEM_LIMITS[System Constraints]
            CPU_QUOTA[CPU Quotas<br/>Enforced by cgroups<br/>Throttling events: 1,500<br/>Impact: Response delay]
            THERMAL[Thermal Management<br/>CPU temperature: 85°C<br/>Throttling: Active<br/>Performance: Reduced]
        end

        CACHE[(Redis Cache<br/>CPU: 15% (0.6/4 cores)<br/>Memory pressure: Low<br/>Hit ratio: Stable)]
    end

    subgraph ControlPlane[Control Plane - CPU Management]
        MONITOR[CPU Monitoring<br/>Prometheus + Node Exporter<br/>Sample rate: 15s<br/>Alert threshold: 85%]

        subgraph SCALING[Auto Scaling Response]
            HPA[Horizontal Pod Autoscaler<br/>Target CPU: 70%<br/>Current utilization: 95%<br/>Scaling: +5 replicas]
            VPA[Vertical Pod Autoscaler<br/>Recommending: +2 cores<br/>Action: Restart required<br/>Priority: High]
            CA[Cluster Autoscaler<br/>Node shortage detected<br/>Adding: 2 new nodes<br/>ETA: 3 minutes]
        end

        subgraph MITIGATION[Emergency Mitigation]
            THROTTLE[Request Throttling<br/>Rate limit: 50% reduction<br/>Priority queues: Active<br/>Shedding: Non-critical]
            CIRCUIT[Circuit Breakers<br/>CPU threshold: 90%<br/>Fallback mode: Enabled<br/>Recovery: Automatic]
            KILL[Process Management<br/>Kill low-priority tasks<br/>Nice values: Adjusted<br/>CPU shares: Redistributed]
        end
    end

    %% Load sources causing CPU pressure
    TRAFFIC --> LB
    BOTS --> LB
    BATCH --> WORKER_1

    %% Load balancer routing
    LB --> API_1
    LB --> API_2
    LB -.->|"Health check failed"| API_3

    %% Pod placement on nodes
    API_1 --> NODE_1
    API_2 --> NODE_2
    API_3 --> NODE_3
    WORKER_1 --> NODE_2
    WORKER_2 --> NODE_1

    %% Resource constraints
    NODE_2 --> CPU_QUOTA
    NODE_2 --> THERMAL
    API_1 --> CACHE

    %% Monitoring and alerting
    NODE_1 --> MONITOR
    NODE_2 --> MONITOR
    NODE_3 --> MONITOR
    API_1 --> MONITOR
    API_2 --> MONITOR

    %% Auto-scaling responses
    MONITOR --> HPA
    MONITOR --> VPA
    MONITOR --> CA
    HPA -.->|"Scale out"| API_PODS
    VPA -.->|"Increase CPU"| API_PODS
    CA -.->|"Add nodes"| NODE_RESOURCES

    %% Emergency mitigation
    MONITOR --> THROTTLE
    MONITOR --> CIRCUIT
    MONITOR --> KILL
    THROTTLE -.->|"Reduce load"| LB
    CIRCUIT -.->|"Block requests"| API_2
    KILL -.->|"Free CPU"| WORKER_2

    %% 4-plane styling
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef criticalStyle fill:#FF0000,stroke:#8B5CF6,color:#fff
    classDef warningStyle fill:#FFA500,stroke:#CC8800,color:#fff

    class TRAFFIC,BOTS,BATCH edgeStyle
    class LB,API_1,API_2,API_3,WORKER_1,WORKER_2 serviceStyle
    class NODE_1,NODE_2,NODE_3,CPU_QUOTA,THERMAL,CACHE stateStyle
    class MONITOR,HPA,VPA,CA,THROTTLE,CIRCUIT,KILL controlStyle
    class API_2,WORKER_1,NODE_2 criticalStyle
    class API_1,NODE_1 warningStyle
```

## 3 AM Emergency Response Commands

### 1. CPU Spike Assessment (30 seconds)
```bash
# Check current CPU usage and load
uptime
top -b -n1 | head -20
cat /proc/loadavg

# Identify CPU-intensive processes
ps aux --sort=-%cpu | head -15
pidstat -u 1 5  # Monitor for 5 seconds

# Check container CPU usage
kubectl top pods --sort-by=cpu --all-namespaces | head -20
kubectl top nodes
```

### 2. Emergency CPU Relief (60 seconds)
```bash
# Kill highest CPU consuming processes (if safe)
# First identify the processes:
ps aux --sort=-%cpu | head -5

# For batch jobs or non-critical processes:
kill -TERM $(pgrep -f "batch-processor")
kill -TERM $(pgrep -f "analytics-job")

# Reduce process priorities
renice +10 $(pgrep -f "background-worker")
renice +5 $(pgrep -f "data-processor")

# Scale down CPU-intensive deployments temporarily
kubectl scale deployment batch-processor --replicas=1
kubectl scale deployment analytics-service --replicas=0
```

### 3. Auto-Scaling Activation (90 seconds)
```bash
# Force horizontal pod autoscaler
kubectl patch hpa api-service -p '{"spec":{"targetCPUUtilizationPercentage":50}}'

# Add cluster nodes manually if autoscaler is slow
kubectl apply -f - <<EOF
apiVersion: v1
kind: Node
metadata:
  name: emergency-node-$(date +%s)
spec:
  capacity:
    cpu: "8"
    memory: "32Gi"
EOF

# Update resource limits for critical services
kubectl patch deployment api-service -p '{"spec":{"template":{"spec":{"containers":[{"name":"api","resources":{"limits":{"cpu":"4","memory":"8Gi"}}}]}}}}'
```

## CPU Spike Pattern Recognition

### Gradual CPU Degradation
```
Time    CPU_Usage    Load_Avg    Response_Time    Pattern
10:00   45%          2.1         150ms            Baseline
10:15   60%          4.5         200ms            Growing load
10:30   75%          8.2         500ms            Approaching limit
10:45   85%          12.8        1000ms           Degrading performance
11:00   95%          18.5        3000ms           CRITICAL
```

### Sudden CPU Spike
```
Time    CPU_Usage    Trigger_Event           Impact
10:00   40%          Normal operations       Healthy
10:01   95%          Batch job started       Immediate spike
10:02   98%          Queue backup           Processing slows
10:03   100%         Thermal throttling     Performance drops
10:04   100%         System unresponsive    Service failure
```

### CPU Thrashing Pattern
```
Process    CPU_Usage    Memory_Usage    Pattern
worker-1   25%          8GB            Context switching
worker-2   25%          8GB            Context switching
worker-3   25%          8GB            Context switching
worker-4   25%          8GB            Context switching
Total:     100%         32GB           Thrashing detected
```

## Error Message Patterns

### CPU Throttling Events
```
ERROR: CPU throttling detected
PATTERN: "Task in /kubepods throttled for Xms"
LOCATION: /var/log/messages, dmesg, kernel logs
ACTION: Increase CPU limits or reduce load
COMMAND: grep "throttled" /sys/fs/cgroup/cpu/kubepods/*/cpu.stat
```

### Load Average Warnings
```
WARNING: Load average exceeds CPU core count
PATTERN: Load average > number of CPU cores for >5 minutes
LOCATION: System monitoring, uptime command
ACTION: Identify runaway processes, reduce concurrency
MONITORING: cat /proc/loadavg | awk '{if($1 > 8) print "HIGH LOAD: " $1}'
```

### Process CPU Saturation
```
ERROR: Process consuming 100% CPU for extended period
PATTERN: Single process with sustained high CPU usage
LOCATION: top, htop, process monitoring
ACTION: Profile process, check for infinite loops
COMMAND: strace -c -p [pid] ; perf top -p [pid]
```

## CPU Optimization Strategies

### Process Priority Management
```bash
# Adjust process nice values
nice -n 10 python batch_processor.py  # Lower priority
nice -n -5 ./critical_service         # Higher priority

# Set CPU affinity for critical processes
taskset -c 0,1 ./critical_service     # Pin to cores 0-1
taskset -c 2-7 ./background_job       # Use cores 2-7

# Monitor CPU affinity
ps -eo pid,psr,comm | grep critical_service
```

### Container CPU Management
```yaml
# Kubernetes CPU resource management
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
            cpu: "1"        # Guaranteed CPU
            memory: "2Gi"
          limits:
            cpu: "2"        # Maximum CPU burst
            memory: "4Gi"
        env:
        - name: GOMAXPROCS   # Limit Go runtime
          value: "2"
        - name: UV_THREADPOOL_SIZE  # Limit Node.js threads
          value: "4"
```

### JVM CPU Optimization
```bash
# JVM flags for CPU optimization
JAVA_OPTS="-server \
  -XX:+UseG1GC \
  -XX:+UnlockExperimentalVMOptions \
  -XX:+UseCompressedOops \
  -XX:+UseCompressedClassPointers \
  -XX:+TieredCompilation \
  -XX:TieredStopAtLevel=1 \
  -Xms2g -Xmx4g"

# Monitor JIT compilation
-XX:+PrintCompilation \
-XX:+TraceClassLoading \
-XX:+LogVMOutput
```

## CPU Profiling and Analysis

### System-Level CPU Analysis
```bash
# Use perf for detailed CPU analysis
perf top -p $(pgrep java)              # Live process profiling
perf record -g -p $(pgrep java) sleep 10  # Record for 10 seconds
perf report --stdio                    # View report

# Use sar for historical CPU data
sar -u 1 10                           # CPU usage every second for 10 samples
sar -q 1 10                           # Load average and queue length

# Monitor CPU with iostat
iostat -c 1                           # CPU statistics every second
```

### Application-Level Profiling
```bash
# Java profiling with async-profiler
java -jar async-profiler.jar -e cpu -d 30 -f profile.html $(pgrep java)

# Python profiling with py-spy
py-spy record -o profile.svg --pid $(pgrep python) --duration 60

# Node.js profiling
node --prof app.js                    # Enable V8 profiler
node --prof-process isolate-*.log > processed.txt  # Process profile
```

### Container CPU Monitoring
```bash
# Monitor container CPU usage
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Check CPU throttling in Kubernetes
kubectl describe pod [pod-name] | grep -A5 -B5 "cpu"
kubectl top pod [pod-name] --containers

# Monitor CPU quotas and limits
cat /sys/fs/cgroup/cpu/cpu.cfs_quota_us
cat /sys/fs/cgroup/cpu/cpu.cfs_period_us
cat /sys/fs/cgroup/cpu/cpu.stat | grep throttled
```

## Emergency CPU Scaling Procedures

### Phase 1: Immediate Relief (0-2 minutes)
- [ ] Kill non-critical high-CPU processes
- [ ] Reduce priority of background tasks
- [ ] Enable circuit breakers for CPU-intensive endpoints
- [ ] Scale down batch processing workloads

### Phase 2: Capacity Scaling (2-10 minutes)
- [ ] Trigger horizontal pod autoscaling
- [ ] Add new cluster nodes if available
- [ ] Increase CPU limits for critical services
- [ ] Route traffic to less loaded instances

### Phase 3: Performance Optimization (10+ minutes)
- [ ] Profile CPU-intensive code paths
- [ ] Optimize algorithms and data structures
- [ ] Implement CPU-aware load balancing
- [ ] Review and tune garbage collection settings

## CPU Load Balancing Strategies

### CPU-Aware Load Balancing
```nginx
# Nginx upstream configuration with CPU awareness
upstream backend {
    least_conn;                    # Route to least connections
    server 10.0.1.1:8080 weight=3; # Higher CPU capacity
    server 10.0.1.2:8080 weight=2; # Medium CPU capacity
    server 10.0.1.3:8080 weight=1; # Lower CPU capacity

    # Health checks with CPU consideration
    health_check interval=5s fails=2 passes=2;
}
```

### Kubernetes CPU-Based Scheduling
```yaml
# Pod with CPU-based node affinity
apiVersion: v1
kind: Pod
metadata:
  name: cpu-intensive-task
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: node.kubernetes.io/instance-type
            operator: In
            values: ["c5.4xlarge", "c5.9xlarge"]  # CPU-optimized instances
  containers:
  - name: worker
    image: cpu-intensive-app:latest
    resources:
      requests:
        cpu: "4"
      limits:
        cpu: "8"
```

## Real-World CPU Spike Incidents

### Reddit Comment Processing Spike (2020)
- **Trigger**: Viral post generated millions of comments rapidly
- **Impact**: Comment processing service CPU hit 100%, response times >10s
- **Detection**: CPU monitoring alerts + user reports of slow loading
- **Resolution**: Emergency scaling + comment processing optimization

### Zoom Video Processing Overload (2020)
- **Trigger**: COVID-19 usage spike overwhelmed video encoding services
- **Impact**: CPU across encoding fleet hit 100%, video quality degraded
- **Detection**: CPU metrics + video quality monitoring
- **Resolution**: Emergency capacity addition + encoding efficiency improvements

### Netflix Encoding Farm CPU Storm (2019)
- **Trigger**: New encoding algorithm caused CPU usage spike
- **Impact**: Video encoding throughput dropped 70%, queue backup
- **Detection**: Encoding job completion rate monitoring
- **Resolution**: Algorithm rollback + gradual optimization deployment

---
*Last Updated: Based on Reddit, Zoom, Netflix CPU spike incidents*
*Next Review: Monitor for new CPU optimization patterns and scaling strategies*