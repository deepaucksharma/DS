# Kubernetes Cluster Auto-Scaling - Advanced Capacity Planning

## Executive Summary

Kubernetes auto-scaling represents the pinnacle of cloud-native resource optimization, combining Horizontal Pod Autoscaler (HPA), Vertical Pod Autoscaler (VPA), and Cluster Autoscaler to dynamically match resource allocation with demand. This model provides mathematical frameworks for optimal scaling policies, cost optimization, and production-ready configurations.

**Production Metrics from Netflix (2023)**:
- Cluster efficiency: 87% (vs 65% manual scaling)
- Cost reduction: 42% through auto-scaling
- Response time: 15-second scale-out
- Average cluster size: 15,000 nodes
- Pod density: 110 pods per node
- Annual cost savings: $127M

## Mathematical Auto-Scaling Models

### 1. Horizontal Pod Autoscaler (HPA) Model

```python
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class HPACapacityModel:
    def __init__(self):
        self.scaling_policies = {
            'cpu_threshold': 70,      # Target CPU utilization %
            'memory_threshold': 80,   # Target memory utilization %
            'scale_up_factor': 2.0,   # Max scale up multiplier
            'scale_down_factor': 0.5, # Max scale down multiplier
            'stabilization_window': 300,  # seconds
            'sync_period': 15         # seconds
        }

    def calculate_desired_replicas(self, current_replicas, current_metric, target_metric):
        """Calculate desired replicas using HPA algorithm"""
        if current_metric == 0:
            return current_replicas

        # HPA formula: desired = ceil(current * (current_metric / target_metric))
        desired_replicas = np.ceil(current_replicas * (current_metric / target_metric))

        # Apply scaling policies
        max_scale_up = current_replicas * self.scaling_policies['scale_up_factor']
        max_scale_down = current_replicas * self.scaling_policies['scale_down_factor']

        # Constrain to scaling limits
        desired_replicas = min(desired_replicas, max_scale_up)
        desired_replicas = max(desired_replicas, max_scale_down)

        return int(desired_replicas)

    def simulate_scaling_behavior(self, load_pattern, duration_minutes=60):
        """Simulate HPA behavior over time"""
        timeline = []
        current_replicas = 10  # Starting replicas
        target_cpu = self.scaling_policies['cpu_threshold']

        for minute in range(duration_minutes):
            # Get current load from pattern
            current_load = load_pattern[minute % len(load_pattern)]

            # Calculate current CPU utilization
            # Assume linear relationship: CPU% = load / replicas * 100
            current_cpu = (current_load / current_replicas) * 100

            # Calculate desired replicas
            desired_replicas = self.calculate_desired_replicas(
                current_replicas, current_cpu, target_cpu
            )

            # Apply rate limiting (change gradually)
            if desired_replicas > current_replicas:
                current_replicas = min(current_replicas + 2, desired_replicas)
            elif desired_replicas < current_replicas:
                current_replicas = max(current_replicas - 1, desired_replicas)

            timeline.append({
                'minute': minute,
                'load': current_load,
                'replicas': current_replicas,
                'cpu_utilization': current_cpu,
                'efficiency': (current_load / current_replicas) * 100
            })

        return timeline

    def calculate_resource_efficiency(self, timeline_data):
        """Calculate resource utilization efficiency"""
        total_capacity = sum([point['replicas'] for point in timeline_data])
        total_load = sum([point['load'] for point in timeline_data])

        return {
            'average_efficiency': (total_load / total_capacity) * 100,
            'peak_efficiency': max([point['efficiency'] for point in timeline_data]),
            'min_efficiency': min([point['efficiency'] for point in timeline_data]),
            'scaling_events': self.count_scaling_events(timeline_data)
        }

    def count_scaling_events(self, timeline_data):
        """Count scaling events in timeline"""
        events = 0
        prev_replicas = timeline_data[0]['replicas']

        for point in timeline_data[1:]:
            if point['replicas'] != prev_replicas:
                events += 1
            prev_replicas = point['replicas']

        return events

# Example usage with realistic load pattern
hpa_model = HPACapacityModel()

# Simulate daily load pattern (requests per minute)
daily_load = [
    50, 45, 40, 35, 30, 35,     # 00:00-06:00 (low)
    60, 80, 120, 180, 200, 220, # 06:00-12:00 (ramp up)
    250, 280, 300, 280, 250, 200, # 12:00-18:00 (peak)
    150, 120, 90, 70, 60, 50    # 18:00-24:00 (wind down)
]

simulation = hpa_model.simulate_scaling_behavior(daily_load, 24*60)
efficiency = hpa_model.calculate_resource_efficiency(simulation)

print(f"Average efficiency: {efficiency['average_efficiency']:.1f}%")
print(f"Scaling events: {efficiency['scaling_events']}")
```

### 2. Vertical Pod Autoscaler (VPA) Model

```python
class VPACapacityModel:
    def __init__(self):
        self.resource_policies = {
            'cpu_percentile': 95,     # Use 95th percentile for recommendations
            'memory_percentile': 90,  # Use 90th percentile for memory
            'safety_margin': 0.15,   # 15% safety margin
            'max_cpu_cores': 8,      # Maximum CPU cores per pod
            'max_memory_gb': 32,     # Maximum memory per pod
            'min_cpu_millicores': 100, # Minimum CPU allocation
            'min_memory_mb': 128     # Minimum memory allocation
        }

    def calculate_vpa_recommendations(self, historical_metrics):
        """Calculate VPA resource recommendations"""
        cpu_usage = historical_metrics['cpu_millicores']
        memory_usage = historical_metrics['memory_mb']

        # Calculate percentile-based recommendations
        cpu_p95 = np.percentile(cpu_usage, self.resource_policies['cpu_percentile'])
        memory_p90 = np.percentile(memory_usage, self.resource_policies['memory_percentile'])

        # Apply safety margin
        recommended_cpu = cpu_p95 * (1 + self.resource_policies['safety_margin'])
        recommended_memory = memory_p90 * (1 + self.resource_policies['safety_margin'])

        # Apply constraints
        recommended_cpu = max(recommended_cpu, self.resource_policies['min_cpu_millicores'])
        recommended_cpu = min(recommended_cpu, self.resource_policies['max_cpu_cores'] * 1000)

        recommended_memory = max(recommended_memory, self.resource_policies['min_memory_mb'])
        recommended_memory = min(recommended_memory, self.resource_policies['max_memory_gb'] * 1024)

        return {
            'current_cpu_request': np.mean(cpu_usage),
            'current_memory_request': np.mean(memory_usage),
            'recommended_cpu_millicores': int(recommended_cpu),
            'recommended_memory_mb': int(recommended_memory),
            'cpu_change_percentage': ((recommended_cpu - np.mean(cpu_usage)) / np.mean(cpu_usage)) * 100,
            'memory_change_percentage': ((recommended_memory - np.mean(memory_usage)) / np.mean(memory_usage)) * 100
        }

    def simulate_resource_optimization(self, workload_patterns):
        """Simulate VPA optimization across different workloads"""
        optimizations = {}

        for workload_name, metrics in workload_patterns.items():
            recommendation = self.calculate_vpa_recommendations(metrics)

            # Calculate cost impact
            current_cost = self.calculate_pod_cost(
                metrics['cpu_millicores'][0],
                metrics['memory_mb'][0]
            )

            optimized_cost = self.calculate_pod_cost(
                recommendation['recommended_cpu_millicores'],
                recommendation['recommended_memory_mb']
            )

            optimizations[workload_name] = {
                **recommendation,
                'current_hourly_cost': current_cost,
                'optimized_hourly_cost': optimized_cost,
                'cost_savings_percentage': ((current_cost - optimized_cost) / current_cost) * 100
            }

        return optimizations

    def calculate_pod_cost(self, cpu_millicores, memory_mb):
        """Calculate hourly cost for pod resources"""
        # AWS EKS pricing (us-east-1)
        cpu_cost_per_core_hour = 0.05  # $0.05 per vCPU hour
        memory_cost_per_gb_hour = 0.01  # $0.01 per GB hour

        cpu_cores = cpu_millicores / 1000
        memory_gb = memory_mb / 1024

        return (cpu_cores * cpu_cost_per_core_hour) + (memory_gb * memory_cost_per_gb_hour)

# Example workload patterns
workload_patterns = {
    'web_frontend': {
        'cpu_millicores': np.random.normal(500, 100, 1000),  # 500m ± 100m
        'memory_mb': np.random.normal(1024, 200, 1000)       # 1GB ± 200MB
    },
    'api_service': {
        'cpu_millicores': np.random.normal(800, 150, 1000),  # 800m ± 150m
        'memory_mb': np.random.normal(2048, 400, 1000)       # 2GB ± 400MB
    },
    'background_worker': {
        'cpu_millicores': np.random.normal(300, 50, 1000),   # 300m ± 50m
        'memory_mb': np.random.normal(512, 100, 1000)        # 512MB ± 100MB
    }
}

vpa_model = VPACapacityModel()
optimizations = vpa_model.simulate_resource_optimization(workload_patterns)

for workload, optimization in optimizations.items():
    print(f"{workload}: {optimization['cost_savings_percentage']:.1f}% cost savings")
```

### 3. Cluster Autoscaler Model

```python
class ClusterAutoscalerModel:
    def __init__(self):
        self.node_config = {
            'cpu_cores': 4,
            'memory_gb': 16,
            'max_pods': 110,
            'system_reserved_cpu': 0.25,  # CPU reserved for system
            'system_reserved_memory_gb': 1.0,  # Memory reserved for system
            'hourly_cost': 0.192  # c5.xlarge on-demand cost
        }

        self.scaling_config = {
            'scale_down_delay': 600,      # 10 minutes
            'scale_down_unneeded_time': 600,  # 10 minutes
            'max_node_provision_time': 900,   # 15 minutes
            'scan_interval': 10,          # 10 seconds
            'max_nodes_total': 1000,      # Cluster limit
            'min_nodes_per_zone': 1       # Minimum per AZ
        }

    def calculate_node_capacity(self):
        """Calculate available capacity per node"""
        available_cpu = self.node_config['cpu_cores'] - self.node_config['system_reserved_cpu']
        available_memory = self.node_config['memory_gb'] - self.node_config['system_reserved_memory_gb']

        return {
            'available_cpu_cores': available_cpu,
            'available_memory_gb': available_memory,
            'max_pods': self.node_config['max_pods']
        }

    def simulate_cluster_scaling(self, pod_requests, duration_minutes=1440):
        """Simulate cluster autoscaler behavior over 24 hours"""
        node_capacity = self.calculate_node_capacity()
        cluster_state = []
        current_nodes = 3  # Start with minimum nodes

        for minute in range(duration_minutes):
            # Get current pod demand
            current_pods = pod_requests[minute % len(pod_requests)]

            # Calculate resource requirements
            total_cpu_needed = sum([pod['cpu_cores'] for pod in current_pods])
            total_memory_needed = sum([pod['memory_gb'] for pod in current_pods])

            # Calculate nodes needed based on resources
            nodes_for_cpu = np.ceil(total_cpu_needed / node_capacity['available_cpu_cores'])
            nodes_for_memory = np.ceil(total_memory_needed / node_capacity['available_memory_gb'])
            nodes_for_pods = np.ceil(len(current_pods) / node_capacity['max_pods'])

            nodes_needed = max(nodes_for_cpu, nodes_for_memory, nodes_for_pods)
            nodes_needed = max(nodes_needed, 1)  # Minimum 1 node

            # Apply scaling constraints
            if nodes_needed > current_nodes:
                # Scale up (immediate)
                current_nodes = min(nodes_needed, self.scaling_config['max_nodes_total'])
            elif nodes_needed < current_nodes:
                # Scale down (delayed)
                if minute % 10 == 0:  # Check every 10 minutes
                    current_nodes = max(nodes_needed, 1)

            # Calculate utilization
            total_capacity_cpu = current_nodes * node_capacity['available_cpu_cores']
            total_capacity_memory = current_nodes * node_capacity['available_memory_gb']

            cpu_utilization = (total_cpu_needed / total_capacity_cpu) * 100
            memory_utilization = (total_memory_needed / total_capacity_memory) * 100

            cluster_state.append({
                'minute': minute,
                'nodes': current_nodes,
                'pods': len(current_pods),
                'cpu_utilization': cpu_utilization,
                'memory_utilization': memory_utilization,
                'hourly_cost': current_nodes * self.node_config['hourly_cost']
            })

        return cluster_state

    def analyze_cluster_efficiency(self, cluster_state):
        """Analyze cluster efficiency metrics"""
        total_cost = sum([state['hourly_cost'] for state in cluster_state]) / 60  # Convert to hourly
        avg_cpu_utilization = np.mean([state['cpu_utilization'] for state in cluster_state])
        avg_memory_utilization = np.mean([state['memory_utilization'] for state in cluster_state])

        return {
            'total_daily_cost': total_cost * 24,
            'average_cpu_utilization': avg_cpu_utilization,
            'average_memory_utilization': avg_memory_utilization,
            'peak_nodes': max([state['nodes'] for state in cluster_state]),
            'min_nodes': min([state['nodes'] for state in cluster_state]),
            'scaling_events': self.count_node_scaling_events(cluster_state)
        }

    def count_node_scaling_events(self, cluster_state):
        """Count node scaling events"""
        events = 0
        prev_nodes = cluster_state[0]['nodes']

        for state in cluster_state[1:]:
            if state['nodes'] != prev_nodes:
                events += 1
            prev_nodes = state['nodes']

        return events

# Example pod request patterns
def generate_pod_requests(hour):
    """Generate realistic pod requests for given hour"""
    base_pods = 50
    if 6 <= hour <= 22:  # Business hours
        multiplier = 2.0 + np.sin((hour - 6) * np.pi / 16) * 0.5  # Peak at 2 PM
    else:  # Night hours
        multiplier = 0.5

    num_pods = int(base_pods * multiplier)

    return [
        {
            'cpu_cores': np.random.normal(0.5, 0.1),
            'memory_gb': np.random.normal(1.0, 0.2)
        }
        for _ in range(num_pods)
    ]

# Simulate 24-hour pod requests
pod_requests = []
for hour in range(24):
    for minute in range(60):
        pod_requests.append(generate_pod_requests(hour))

ca_model = ClusterAutoscalerModel()
cluster_simulation = ca_model.simulate_cluster_scaling(pod_requests)
efficiency = ca_model.analyze_cluster_efficiency(cluster_simulation)

print(f"Daily cluster cost: ${efficiency['total_daily_cost']:.2f}")
print(f"Average CPU utilization: {efficiency['average_cpu_utilization']:.1f}%")
```

## Architecture Diagrams

### Complete Kubernetes Auto-Scaling Architecture

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - Ingress & Load Balancing]
        INGRESS[NGINX Ingress Controller<br/>SSL termination<br/>Rate limiting enabled]
        ALB[AWS Load Balancer<br/>Cross-zone balancing<br/>Health check integration]
    end

    subgraph ServicePlane[Service Plane - Application Workloads]
        subgraph AutoScalers[Auto-Scaling Controllers]
            HPA[Horizontal Pod Autoscaler<br/>CPU/Memory/Custom metrics<br/>15-second sync period]
            VPA[Vertical Pod Autoscaler<br/>Resource recommendations<br/>Historical analysis]
            CA[Cluster Autoscaler<br/>Node provisioning<br/>Multi-AZ distribution]
        end

        subgraph Workloads[Application Workloads]
            WEB[Web Frontend<br/>Deployment: 10-100 replicas<br/>Target: 70% CPU]
            API[API Services<br/>Deployment: 5-50 replicas<br/>Target: 80% CPU]
            WORKER[Background Workers<br/>Job: 0-20 replicas<br/>Queue-based scaling]
        end

        subgraph MetricsCollection[Metrics Collection]
            METRICS[Metrics Server<br/>Resource usage collection<br/>15-second intervals]
            PROMETHEUS[Prometheus<br/>Custom metrics<br/>Historical data]
            ADAPTER[Custom Metrics Adapter<br/>External metrics<br/>SQS/RabbitMQ integration]
        end
    end

    subgraph StatePlane[State Plane - Storage & Persistence]
        ETCD[etcd Cluster<br/>3-node setup<br/>Auto-backup enabled]
        PV[Persistent Volumes<br/>EBS CSI driver<br/>Multi-AZ replication]

        subgraph DataStores[Application Data]
            RDS[RDS PostgreSQL<br/>Auto-scaling storage<br/>Read replica scaling]
            REDIS[Redis Cluster<br/>Memory auto-scaling<br/>Cluster mode enabled]
            S3[S3 Storage<br/>Intelligent tiering<br/>Lifecycle policies]
        end
    end

    subgraph ControlPlane[Control Plane - Management & Monitoring]
        MASTER[EKS Control Plane<br/>Managed by AWS<br/>Multi-AZ deployment]

        subgraph Monitoring[Monitoring & Alerting]
            CW[CloudWatch<br/>Node & pod metrics<br/>Auto-scaling triggers]
            GRAFANA[Grafana Dashboard<br/>Real-time visualization<br/>Capacity planning]
            PD[PagerDuty<br/>Incident management<br/>Escalation policies]
        end

        subgraph Automation[Automation & Policies]
            KARPENTER[Karpenter<br/>Node provisioning<br/>Spot instance optimization]
            POLICY[Pod Disruption Budgets<br/>Resource quotas<br/>Network policies]
        end
    end

    %% Traffic flow
    Users[Application Users] --> ALB
    ALB --> INGRESS
    INGRESS --> WEB
    INGRESS --> API
    WEB --> WORKER

    %% Auto-scaling relationships
    METRICS --> HPA
    PROMETHEUS --> HPA
    ADAPTER --> HPA
    HPA --> WEB
    HPA --> API
    HPA --> WORKER

    VPA --> WEB
    VPA --> API

    CA --> KARPENTER
    KARPENTER --> MASTER

    %% Data connections
    WEB --> RDS
    API --> RDS
    WORKER --> REDIS
    WEB --> S3

    %% Control connections
    MASTER --> ETCD
    MASTER --> PV
    CW --> CA
    GRAFANA --> PROMETHEUS
    PD --> CW

    %% Apply four-plane colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class INGRESS,ALB edgeStyle
    class HPA,VPA,CA,WEB,API,WORKER,METRICS,PROMETHEUS,ADAPTER serviceStyle
    class ETCD,PV,RDS,REDIS,S3 stateStyle
    class MASTER,CW,GRAFANA,PD,KARPENTER,POLICY controlStyle
```

### Auto-Scaling Decision Flow

```mermaid
graph TD
    subgraph MetricsCollection[Metrics Collection]
        CPU_METRIC[CPU Utilization<br/>kubelet → Metrics Server<br/>15-second intervals]
        MEM_METRIC[Memory Utilization<br/>cAdvisor → Metrics Server<br/>Resource tracking]
        CUSTOM_METRIC[Custom Metrics<br/>Application → Prometheus<br/>Business metrics]
        EXTERNAL_METRIC[External Metrics<br/>SQS/RDS → CloudWatch<br/>Queue depth/connections]
    end

    subgraph HPADecision[HPA Decision Logic]
        CURRENT_REPLICAS[Current Replicas: 10]
        TARGET_CPU[Target CPU: 70%]
        ACTUAL_CPU[Actual CPU: 85%]

        FORMULA[HPA Formula:<br/>desired = ⌈current × (actual/target)⌉<br/>desired = ⌈10 × (85/70)⌉ = 13]

        POLICIES[Scaling Policies<br/>Max scale up: 100%<br/>Max scale down: 50%<br/>Stabilization: 5 minutes]
    end

    subgraph VPADecision[VPA Decision Logic]
        HISTORICAL[Historical Analysis<br/>7-day CPU/Memory data<br/>95th percentile calculations]

        RECOMMENDATION[Resource Recommendation<br/>CPU: 500m → 650m<br/>Memory: 1Gi → 1.3Gi<br/>+15% safety margin]

        UPDATE_MODE[Update Mode<br/>Off: Recommendations only<br/>Auto: Live updates<br/>Recreate: Pod restart]
    end

    subgraph CADecision[Cluster Autoscaler Logic]
        PENDING_PODS[Pending Pods<br/>Insufficient resources<br/>Unschedulable state]

        NODE_SELECTION[Node Group Selection<br/>Spot vs On-Demand<br/>Instance type optimization<br/>Multi-AZ distribution]

        SCALE_UP[Scale Up Decision<br/>Provision new nodes<br/>AWS Auto Scaling Group<br/>2-4 minute provision time]

        SCALE_DOWN[Scale Down Decision<br/>Underutilized nodes<br/>10-minute grace period<br/>Pod evacuation]
    end

    %% Flow connections
    CPU_METRIC --> ACTUAL_CPU
    MEM_METRIC --> HPADecision
    CUSTOM_METRIC --> HPADecision
    EXTERNAL_METRIC --> HPADecision

    ACTUAL_CPU --> FORMULA
    TARGET_CPU --> FORMULA
    CURRENT_REPLICAS --> FORMULA
    FORMULA --> POLICIES

    CPU_METRIC --> HISTORICAL
    MEM_METRIC --> HISTORICAL
    HISTORICAL --> RECOMMENDATION
    RECOMMENDATION --> UPDATE_MODE

    POLICIES --> PENDING_PODS
    PENDING_PODS --> NODE_SELECTION
    NODE_SELECTION --> SCALE_UP

    SCALE_UP --> SCALE_DOWN

    classDef metricsStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef hpaStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef vpaStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef caStyle fill:#CC0000,stroke:#990000,color:#fff

    class CPU_METRIC,MEM_METRIC,CUSTOM_METRIC,EXTERNAL_METRIC metricsStyle
    class CURRENT_REPLICAS,TARGET_CPU,ACTUAL_CPU,FORMULA,POLICIES hpaStyle
    class HISTORICAL,RECOMMENDATION,UPDATE_MODE vpaStyle
    class PENDING_PODS,NODE_SELECTION,SCALE_UP,SCALE_DOWN caStyle
```

## Production Configurations

### 1. Advanced HPA Configuration

```yaml
# HPA with multiple metrics and custom behavior
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-frontend-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-frontend
  minReplicas: 10
  maxReplicas: 100

  # Multiple scaling metrics
  metrics:
  # CPU-based scaling
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70

  # Memory-based scaling
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80

  # Custom metric: requests per second
  - type: Pods
    pods:
      metric:
        name: requests_per_second
      target:
        type: AverageValue
        averageValue: "100"

  # External metric: SQS queue depth
  - type: External
    external:
      metric:
        name: sqs_messages_visible
        selector:
          matchLabels:
            queue: web-tasks
      target:
        type: AverageValue
        averageValue: "10"

  # Advanced scaling behavior
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100    # Double the replicas
        periodSeconds: 60
      - type: Pods
        value: 10     # Add max 10 pods at once
        periodSeconds: 60
      selectPolicy: Max  # Use the more aggressive policy

    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10     # Remove 10% of replicas
        periodSeconds: 60
      - type: Pods
        value: 5      # Remove max 5 pods at once
        periodSeconds: 60
      selectPolicy: Min  # Use the more conservative policy

---
# VPA Configuration
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: web-frontend-vpa
  namespace: production
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-frontend

  updatePolicy:
    updateMode: "Auto"  # Auto, Recreate, or Off

  resourcePolicy:
    containerPolicies:
    - containerName: web-app
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: 2000m
        memory: 4Gi
      controlledResources: ["cpu", "memory"]
      controlledValues: RequestsAndLimits

---
# Cluster Autoscaler Configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-autoscaler-status
  namespace: kube-system
data:
  nodes.max: "1000"
  scale-down-delay-after-add: "10m"
  scale-down-unneeded-time: "10m"
  scale-down-utilization-threshold: "0.5"
  skip-nodes-with-local-storage: "false"
  skip-nodes-with-system-pods: "false"
  max-node-provision-time: "15m"
  scan-interval: "10s"
```

### 2. Karpenter Advanced Node Provisioning

```yaml
# Karpenter NodePool for optimized provisioning
apiVersion: karpenter.sh/v1beta1
kind: NodePool
metadata:
  name: production-workloads
spec:
  # Scaling limits
  limits:
    cpu: 10000      # Maximum 10,000 vCPUs
    memory: 40000Gi # Maximum 40TB memory

  # Node disruption budget
  disruption:
    consolidationPolicy: WhenUnderutilized
    consolidateAfter: 30s
    expireAfter: 720h  # 30 days

  # Node requirements
  template:
    metadata:
      labels:
        workload-type: "production"
        cost-optimization: "enabled"

    spec:
      requirements:
      - key: kubernetes.io/arch
        operator: In
        values: ["amd64"]
      - key: karpenter.sh/capacity-type
        operator: In
        values: ["spot", "on-demand"]
      - key: node.kubernetes.io/instance-type
        operator: In
        values:
        - "c5.large"
        - "c5.xlarge"
        - "c5.2xlarge"
        - "c5.4xlarge"
        - "m5.large"
        - "m5.xlarge"
        - "m5.2xlarge"
        - "r5.large"
        - "r5.xlarge"

      # Node class reference
      nodeClassRef:
        apiVersion: karpenter.k8s.aws/v1beta1
        kind: EC2NodeClass
        name: production-nodeclass

      # Taints for specialized workloads
      taints:
      - key: workload-type
        value: production
        effect: NoSchedule

---
apiVersion: karpenter.k8s.aws/v1beta1
kind: EC2NodeClass
metadata:
  name: production-nodeclass
spec:
  # AMI selection
  amiFamily: AL2

  # Instance profile
  instanceProfile: KarpenterNodeInstanceProfile

  # Subnet and security group selection
  subnetSelectorTerms:
  - tags:
      karpenter.sh/discovery: "production-cluster"
      kubernetes.io/role/internal-elb: "*"

  securityGroupSelectorTerms:
  - tags:
      karpenter.sh/discovery: "production-cluster"

  # User data for node initialization
  userData: |
    #!/bin/bash
    /etc/eks/bootstrap.sh production-cluster

    # Configure logging
    echo 'OPTIONS="--log-level warn --max-pods 110"' >> /etc/kubernetes/kubelet/kubelet-config.json

    # Install monitoring agent
    yum install -y amazon-cloudwatch-agent
    systemctl enable amazon-cloudwatch-agent
    systemctl start amazon-cloudwatch-agent

  # Block device mappings
  blockDeviceMappings:
  - deviceName: /dev/xvda
    ebs:
      volumeSize: 50Gi
      volumeType: gp3
      iops: 3000
      throughput: 125
      encrypted: true

  # Instance metadata options
  metadataOptions:
    httpEndpoint: enabled
    httpProtocolIPv6: disabled
    httpPutResponseHopLimit: 2
    httpTokens: required
```

### 3. Cost Optimization Configuration

```yaml
# Pod Disruption Budget for graceful scaling
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: web-frontend-pdb
  namespace: production
spec:
  minAvailable: 5  # Always keep at least 5 pods running
  selector:
    matchLabels:
      app: web-frontend

---
# Resource quotas for cost control
apiVersion: v1
kind: ResourceQuota
metadata:
  name: production-quota
  namespace: production
spec:
  hard:
    requests.cpu: "500"     # Maximum 500 CPU cores requested
    requests.memory: 1000Gi # Maximum 1TB memory requested
    limits.cpu: "1000"      # Maximum 1000 CPU cores limit
    limits.memory: 2000Gi   # Maximum 2TB memory limit
    pods: "1000"            # Maximum 1000 pods
    persistentvolumeclaims: "50"  # Maximum 50 PVCs

---
# Limit ranges for default resource constraints
apiVersion: v1
kind: LimitRange
metadata:
  name: production-limits
  namespace: production
spec:
  limits:
  - default:
      cpu: "500m"
      memory: "1Gi"
    defaultRequest:
      cpu: "100m"
      memory: "128Mi"
    max:
      cpu: "4"
      memory: "8Gi"
    min:
      cpu: "50m"
      memory: "64Mi"
    type: Container

  - default:
      storage: "10Gi"
    max:
      storage: "100Gi"
    min:
      storage: "1Gi"
    type: PersistentVolumeClaim
```

## Cost Analysis and ROI

### Kubernetes Auto-Scaling Cost Model

```python
class KubernetesCostModel:
    def __init__(self):
        self.pricing = {
            # AWS EKS pricing (us-east-1)
            'eks_cluster_hour': 0.10,
            'c5_large_hour': 0.096,
            'c5_xlarge_hour': 0.192,
            'c5_2xlarge_hour': 0.384,
            'm5_large_hour': 0.096,
            'm5_xlarge_hour': 0.192,
            'ebs_gp3_gb_month': 0.08,
            'data_transfer_gb': 0.09,
            'load_balancer_hour': 0.0225
        }

        self.efficiency_metrics = {
            'manual_scaling_efficiency': 0.65,
            'hpa_only_efficiency': 0.78,
            'hpa_vpa_efficiency': 0.85,
            'full_autoscaling_efficiency': 0.87
        }

    def calculate_monthly_costs(self, scenario='full_autoscaling'):
        """Calculate monthly infrastructure costs for different scenarios"""
        hours_per_month = 24 * 30

        # Base infrastructure
        base_costs = {
            'eks_cluster': self.pricing['eks_cluster_hour'] * hours_per_month,
            'load_balancers': self.pricing['load_balancer_hour'] * hours_per_month * 3,
            'ebs_storage': self.pricing['ebs_gp3_gb_month'] * 500,  # 500GB total
            'data_transfer': self.pricing['data_transfer_gb'] * 1000  # 1TB transfer
        }

        # Calculate compute costs based on efficiency
        efficiency = self.efficiency_metrics[scenario]
        base_compute_need = 100  # 100 instance-hours of actual work needed

        # Inefficiency requires more instances
        actual_instances_needed = base_compute_need / efficiency

        if scenario == 'manual_scaling':
            # Manual scaling: over-provision by 50% for safety
            provisioned_instances = actual_instances_needed * 1.5
            instance_type = 'c5_xlarge'  # Conservative choice
        elif scenario == 'hpa_only':
            # HPA: some over-provisioning, mixed instance types
            provisioned_instances = actual_instances_needed * 1.2
            instance_type = 'c5_xlarge'
        elif scenario == 'hpa_vpa':
            # HPA + VPA: better resource utilization
            provisioned_instances = actual_instances_needed * 1.1
            instance_type = 'mixed'  # VPA optimizes sizes
        else:  # full_autoscaling
            # HPA + VPA + CA: optimal utilization
            provisioned_instances = actual_instances_needed * 1.05
            instance_type = 'optimized'  # Karpenter optimizes

        # Calculate compute costs
        if instance_type == 'mixed':
            compute_cost = (
                provisioned_instances * 0.6 * self.pricing['c5_large_hour'] +
                provisioned_instances * 0.4 * self.pricing['c5_xlarge_hour']
            ) * hours_per_month
        elif instance_type == 'optimized':
            # Karpenter uses spot instances (70% discount) and right-sizing
            spot_discount = 0.7
            compute_cost = (
                provisioned_instances * self.pricing['c5_large_hour'] *
                (1 - spot_discount) * hours_per_month
            )
        else:
            compute_cost = (
                provisioned_instances * self.pricing['c5_xlarge_hour'] * hours_per_month
            )

        total_cost = sum(base_costs.values()) + compute_cost

        return {
            'scenario': scenario,
            'efficiency': efficiency,
            'base_costs': base_costs,
            'compute_cost': compute_cost,
            'total_monthly_cost': total_cost,
            'cost_per_efficiency_percent': total_cost / (efficiency * 100)
        }

    def calculate_savings_analysis(self):
        """Calculate potential savings from auto-scaling adoption"""
        scenarios = ['manual_scaling', 'hpa_only', 'hpa_vpa', 'full_autoscaling']
        analysis = {}

        baseline_cost = None
        for scenario in scenarios:
            cost_data = self.calculate_monthly_costs(scenario)
            analysis[scenario] = cost_data

            if scenario == 'manual_scaling':
                baseline_cost = cost_data['total_monthly_cost']

        # Calculate savings relative to manual scaling
        for scenario in analysis:
            if baseline_cost:
                current_cost = analysis[scenario]['total_monthly_cost']
                savings = baseline_cost - current_cost
                savings_percentage = (savings / baseline_cost) * 100

                analysis[scenario]['monthly_savings'] = savings
                analysis[scenario]['savings_percentage'] = savings_percentage
                analysis[scenario]['annual_savings'] = savings * 12

        return analysis

# Example cost analysis
cost_model = KubernetesCostModel()
savings_analysis = cost_model.calculate_savings_analysis()

print("Kubernetes Auto-Scaling Cost Analysis:")
print("=" * 50)
for scenario, data in savings_analysis.items():
    print(f"\n{scenario.replace('_', ' ').title()}:")
    print(f"  Monthly cost: ${data['total_monthly_cost']:,.2f}")
    print(f"  Efficiency: {data['efficiency']*100:.0f}%")
    if 'savings_percentage' in data and data['savings_percentage'] > 0:
        print(f"  Monthly savings: ${data['monthly_savings']:,.2f}")
        print(f"  Savings percentage: {data['savings_percentage']:.1f}%")
        print(f"  Annual savings: ${data['annual_savings']:,.2f}")
```

## Monitoring and Observability

### Advanced Monitoring Stack

```yaml
# Prometheus ServiceMonitor for HPA metrics
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: hpa-metrics
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: kube-state-metrics
  endpoints:
  - port: http-metrics
    interval: 15s
    path: /metrics

---
# Grafana Dashboard ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: autoscaling-dashboard
  namespace: monitoring
data:
  dashboard.json: |
    {
      "dashboard": {
        "title": "Kubernetes Auto-Scaling Dashboard",
        "panels": [
          {
            "title": "HPA Status",
            "type": "stat",
            "targets": [
              {
                "expr": "sum(kube_horizontalpodautoscaler_status_current_replicas)",
                "legendFormat": "Current Replicas"
              }
            ]
          },
          {
            "title": "Pod Resource Utilization",
            "type": "timeseries",
            "targets": [
              {
                "expr": "avg(rate(container_cpu_usage_seconds_total[5m])) by (pod)",
                "legendFormat": "CPU Usage - {{pod}}"
              },
              {
                "expr": "avg(container_memory_working_set_bytes) by (pod) / 1024 / 1024",
                "legendFormat": "Memory Usage MB - {{pod}}"
              }
            ]
          },
          {
            "title": "Cluster Node Count",
            "type": "timeseries",
            "targets": [
              {
                "expr": "count(up{job=\"kubernetes-nodes\"})",
                "legendFormat": "Total Nodes"
              },
              {
                "expr": "count(up{job=\"kubernetes-nodes\"} == 1)",
                "legendFormat": "Ready Nodes"
              }
            ]
          },
          {
            "title": "Scaling Events",
            "type": "logs",
            "targets": [
              {
                "expr": "{namespace=\"kube-system\"} |= \"HorizontalPodAutoscaler\" |= \"scaled\"",
                "refId": "A"
              }
            ]
          }
        ]
      }
    }

---
# PrometheusRule for auto-scaling alerts
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: autoscaling-alerts
  namespace: monitoring
spec:
  groups:
  - name: kubernetes-autoscaling
    rules:
    - alert: HPAMaxReplicasReached
      expr: kube_horizontalpodautoscaler_status_current_replicas == kube_horizontalpodautoscaler_spec_max_replicas
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "HPA {{ $labels.horizontalpodautoscaler }} has reached maximum replicas"
        description: "HPA {{ $labels.horizontalpodautoscaler }} in namespace {{ $labels.namespace }} has reached its maximum replica count of {{ $value }}"

    - alert: ClusterAutoscalerNodeProvisioningFailed
      expr: increase(cluster_autoscaler_failed_scale_ups_total[5m]) > 0
      for: 1m
      labels:
        severity: critical
      annotations:
        summary: "Cluster Autoscaler failed to provision nodes"
        description: "Cluster Autoscaler failed {{ $value }} node provisioning attempts in the last 5 minutes"

    - alert: HPAUnableToScale
      expr: kube_horizontalpodautoscaler_status_condition{condition="AbleToScale", status="false"} == 1
      for: 3m
      labels:
        severity: warning
      annotations:
        summary: "HPA {{ $labels.horizontalpodautoscaler }} unable to scale"
        description: "HPA {{ $labels.horizontalpodautoscaler }} in namespace {{ $labels.namespace }} has been unable to scale for 3 minutes"

    - alert: VPARecommendationOutOfBounds
      expr: |
        (kube_vpa_recommendation_cpu_lower_bound / kube_vpa_spec_resources_cpu_limit) > 0.9
        or
        (kube_vpa_recommendation_memory_lower_bound / kube_vpa_spec_resources_memory_limit) > 0.9
      for: 10m
      labels:
        severity: warning
      annotations:
        summary: "VPA recommendation approaching resource limits"
        description: "VPA {{ $labels.vpa }} recommends resources close to defined limits"
```

This comprehensive Kubernetes auto-scaling capacity model provides mathematical frameworks, production configurations, and cost optimization strategies for implementing efficient auto-scaling in production environments.