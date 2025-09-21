# Message Queue Comprehensive Sizing - Production Capacity Planning

## Executive Summary

Message queue capacity planning involves optimizing throughput, latency, and durability across distributed systems while ensuring fault tolerance and cost efficiency. This model provides mathematical frameworks for sizing Kafka, RabbitMQ, Amazon SQS, and other queue systems under production loads.

**Uber Message Queue Metrics (2023)**:
- Peak throughput: 4.2M messages/second
- Queue infrastructure: 15,000+ Kafka brokers
- Message durability: 99.999% (5-nines)
- Average latency: 2.1ms publish, 4.7ms consume
- Daily message volume: 1.2 trillion messages
- Storage requirements: 2.8 PB active, 45 PB archived
- Cost efficiency: 67% reduction vs managed services

## Mathematical Queue Sizing Models

### 1. Kafka Cluster Capacity Model

```python
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import math

class KafkaCapacityModel:
    def __init__(self):
        self.broker_specs = {
            'cpu_cores': 32,
            'memory_gb': 128,
            'disk_capacity_gb': 4000,
            'network_bandwidth_gbps': 10,
            'disk_iops': 7500,
            'replication_factor': 3
        }

        self.performance_targets = {
            'max_publish_latency_ms': 10,
            'max_consume_latency_ms': 5,
            'target_throughput_msg_per_sec': 50000,  # Per broker
            'retention_days': 7,
            'availability_percentage': 99.95
        }

    def calculate_broker_capacity(self, message_profile):
        """Calculate capacity for a single Kafka broker"""
        avg_message_size_kb = message_profile['avg_message_size_kb']
        peak_messages_per_sec = message_profile['peak_messages_per_sec']

        # Network bandwidth constraint
        network_throughput_mbps = (peak_messages_per_sec * avg_message_size_kb) / 1024
        network_limit_msg_per_sec = (
            self.broker_specs['network_bandwidth_gbps'] * 1024 * 1024
        ) / avg_message_size_kb

        # Disk I/O constraint
        # Each message write requires log append + index update
        writes_per_message = 1.2  # Including index updates
        disk_iops_required = peak_messages_per_sec * writes_per_message
        disk_limit_msg_per_sec = self.broker_specs['disk_iops'] / writes_per_message

        # CPU constraint (simplified model)
        cpu_per_message_us = 50  # 50 microseconds per message
        cpu_limit_msg_per_sec = (
            self.broker_specs['cpu_cores'] * 1_000_000
        ) / cpu_per_message_us

        # Memory constraint (buffer management)
        memory_per_partition_mb = 1  # 1MB per partition buffer
        max_partitions = self.broker_specs['memory_gb'] * 1024 * 0.7 / memory_per_partition_mb
        memory_limit_msg_per_sec = max_partitions * 1000  # 1000 msg/sec per partition

        # Storage constraint
        daily_data_gb = (peak_messages_per_sec * avg_message_size_kb * 86400) / (1024 * 1024)
        retention_data_gb = daily_data_gb * self.performance_targets['retention_days']
        storage_utilization = retention_data_gb / self.broker_specs['disk_capacity_gb']

        return {
            'network_limit_msg_per_sec': network_limit_msg_per_sec,
            'disk_limit_msg_per_sec': disk_limit_msg_per_sec,
            'cpu_limit_msg_per_sec': cpu_limit_msg_per_sec,
            'memory_limit_msg_per_sec': memory_limit_msg_per_sec,
            'bottleneck': self.identify_bottleneck([
                ('network', network_limit_msg_per_sec),
                ('disk', disk_limit_msg_per_sec),
                ('cpu', cpu_limit_msg_per_sec),
                ('memory', memory_limit_msg_per_sec)
            ]),
            'effective_capacity_msg_per_sec': min(
                network_limit_msg_per_sec,
                disk_limit_msg_per_sec,
                cpu_limit_msg_per_sec,
                memory_limit_msg_per_sec
            ),
            'storage_utilization': storage_utilization,
            'daily_data_gb': daily_data_gb
        }

    def identify_bottleneck(self, limits):
        """Identify the primary bottleneck"""
        return min(limits, key=lambda x: x[1])

    def calculate_cluster_size(self, workload_requirements):
        """Calculate required Kafka cluster size"""
        total_peak_msgs_per_sec = workload_requirements['total_peak_msgs_per_sec']
        message_profile = workload_requirements['message_profile']

        # Calculate single broker capacity
        broker_capacity = self.calculate_broker_capacity(message_profile)
        effective_capacity = broker_capacity['effective_capacity_msg_per_sec']

        # Apply replication factor overhead
        replication_overhead = self.broker_specs['replication_factor']
        effective_capacity_with_replication = effective_capacity / replication_overhead

        # Calculate required brokers with buffer
        safety_buffer = 1.3  # 30% safety buffer
        required_brokers = math.ceil(
            (total_peak_msgs_per_sec * safety_buffer) / effective_capacity_with_replication
        )

        # Ensure minimum cluster size for fault tolerance
        min_brokers = max(3, self.broker_specs['replication_factor'])
        final_broker_count = max(required_brokers, min_brokers)

        # Calculate partition strategy
        partitions_per_topic = self.calculate_optimal_partitions(
            total_peak_msgs_per_sec, final_broker_count
        )

        return {
            'required_brokers': final_broker_count,
            'broker_capacity_analysis': broker_capacity,
            'cluster_total_capacity_msg_per_sec': final_broker_count * effective_capacity_with_replication,
            'utilization_percentage': (total_peak_msgs_per_sec / (final_broker_count * effective_capacity_with_replication)) * 100,
            'partitions_per_topic': partitions_per_topic,
            'total_storage_required_gb': broker_capacity['daily_data_gb'] * self.performance_targets['retention_days'] * final_broker_count,
            'cost_analysis': self.calculate_cluster_costs(final_broker_count)
        }

    def calculate_optimal_partitions(self, peak_msgs_per_sec, broker_count):
        """Calculate optimal number of partitions per topic"""
        # Rule of thumb: 1 partition per 1000 msg/sec for optimal parallelism
        base_partitions = max(1, peak_msgs_per_sec // 1000)

        # Ensure partitions are well distributed across brokers
        partitions_per_broker = math.ceil(base_partitions / broker_count)
        optimal_partitions = partitions_per_broker * broker_count

        # Cap at reasonable maximum (100 partitions per topic)
        return min(optimal_partitions, 100)

    def calculate_cluster_costs(self, broker_count):
        """Calculate monthly cluster costs"""
        # AWS MSK pricing (approximate)
        broker_cost_per_hour = 1.68  # kafka.m5.2xlarge
        storage_cost_per_gb_month = 0.10

        monthly_hours = 24 * 30
        broker_costs = broker_count * broker_cost_per_hour * monthly_hours

        total_storage_gb = broker_count * self.broker_specs['disk_capacity_gb']
        storage_costs = total_storage_gb * storage_cost_per_gb_month

        return {
            'monthly_broker_costs': broker_costs,
            'monthly_storage_costs': storage_costs,
            'total_monthly_cost': broker_costs + storage_costs,
            'cost_per_broker': broker_costs / broker_count
        }

    def simulate_throughput_patterns(self, daily_patterns, duration_hours=24):
        """Simulate cluster behavior under varying load patterns"""
        timeline = []
        current_cluster_size = 10  # Start with baseline

        for hour in range(duration_hours):
            current_load = daily_patterns[hour % len(daily_patterns)]

            # Determine if scaling is needed
            workload = {
                'total_peak_msgs_per_sec': current_load,
                'message_profile': {'avg_message_size_kb': 2}
            }

            required_cluster = self.calculate_cluster_size(workload)
            required_brokers = required_cluster['required_brokers']

            # Simulate scaling decisions (conservative approach)
            if required_brokers > current_cluster_size:
                current_cluster_size = required_brokers
            elif required_brokers < current_cluster_size * 0.7:  # Scale down if <70% utilization
                current_cluster_size = max(required_brokers, 3)

            timeline.append({
                'hour': hour,
                'load_msg_per_sec': current_load,
                'cluster_size': current_cluster_size,
                'utilization': (current_load / (current_cluster_size * 15000)) * 100,  # 15k msgs/sec per broker
                'hourly_cost': (current_cluster_size * 1.68)
            })

        return timeline

# Example usage
kafka_model = KafkaCapacityModel()

# Define workload requirements
workload = {
    'total_peak_msgs_per_sec': 500000,  # 500K messages per second at peak
    'message_profile': {
        'avg_message_size_kb': 2,        # 2KB average message size
        'peak_multiplier': 3.0           # Peak is 3x average
    }
}

# Calculate cluster requirements
cluster_requirements = kafka_model.calculate_cluster_size(workload)

print("Kafka Cluster Sizing Results:")
print("=" * 40)
print(f"Required Brokers: {cluster_requirements['required_brokers']}")
print(f"Cluster Capacity: {cluster_requirements['cluster_total_capacity_msg_per_sec']:,.0f} msg/sec")
print(f"Utilization: {cluster_requirements['utilization_percentage']:.1f}%")
print(f"Monthly Cost: ${cluster_requirements['cost_analysis']['total_monthly_cost']:,.2f}")
print(f"Bottleneck: {cluster_requirements['broker_capacity_analysis']['bottleneck'][0]}")

# Simulate daily load pattern
daily_load_pattern = [
    50000, 45000, 40000, 35000, 40000, 50000,     # 00-06: Low traffic
    80000, 120000, 180000, 250000, 300000, 350000, # 06-12: Morning ramp
    400000, 450000, 500000, 480000, 420000, 380000, # 12-18: Peak hours
    320000, 280000, 220000, 180000, 120000, 80000   # 18-24: Evening decline
]

simulation = kafka_model.simulate_throughput_patterns(daily_load_pattern)
avg_cost = np.mean([s['hourly_cost'] for s in simulation])
print(f"\nDaily Average Cost: ${avg_cost * 24:.2f}")
```

### 2. RabbitMQ Capacity Planning Model

```python
class RabbitMQCapacityModel:
    def __init__(self):
        self.node_specs = {
            'cpu_cores': 16,
            'memory_gb': 64,
            'disk_capacity_gb': 1000,
            'network_bandwidth_mbps': 1000,
            'max_connections': 65536
        }

        self.rabbitmq_limits = {
            'messages_per_sec_per_core': 2500,
            'memory_per_message_bytes': 1024,  # Memory overhead per queued message
            'disk_write_overhead': 1.5,        # Write amplification factor
            'connection_overhead_mb': 2        # Memory per connection
        }

    def calculate_node_capacity(self, queue_profile):
        """Calculate capacity for a single RabbitMQ node"""
        avg_message_size_kb = queue_profile['avg_message_size_kb']
        target_msg_per_sec = queue_profile['target_msg_per_sec']
        avg_queue_depth = queue_profile.get('avg_queue_depth', 1000)

        # CPU-based capacity
        cpu_capacity = (
            self.node_specs['cpu_cores'] *
            self.rabbitmq_limits['messages_per_sec_per_core']
        )

        # Memory-based capacity
        # Account for message storage + connection overhead + OS/RabbitMQ overhead
        message_memory_mb = (
            avg_queue_depth * avg_message_size_kb *
            self.rabbitmq_limits['memory_per_message_bytes'] / 1024 / 1024
        )

        connection_memory_mb = (
            queue_profile.get('concurrent_connections', 1000) *
            self.rabbitmq_limits['connection_overhead_mb']
        )

        system_overhead_mb = self.node_specs['memory_gb'] * 1024 * 0.3  # 30% system overhead
        available_memory_mb = (
            self.node_specs['memory_gb'] * 1024 -
            system_overhead_mb - connection_memory_mb
        )

        memory_capacity_messages = available_memory_mb / (avg_message_size_kb / 1024)

        # Network bandwidth capacity
        network_capacity_msg_per_sec = (
            self.node_specs['network_bandwidth_mbps'] * 1024
        ) / avg_message_size_kb

        # Disk I/O capacity
        estimated_iops = 3000  # Conservative estimate for standard SSD
        disk_capacity_msg_per_sec = estimated_iops / self.rabbitmq_limits['disk_write_overhead']

        return {
            'cpu_capacity_msg_per_sec': cpu_capacity,
            'memory_capacity_messages': memory_capacity_messages,
            'network_capacity_msg_per_sec': network_capacity_msg_per_sec,
            'disk_capacity_msg_per_sec': disk_capacity_msg_per_sec,
            'effective_capacity': min(cpu_capacity, network_capacity_msg_per_sec, disk_capacity_msg_per_sec),
            'memory_utilization': (message_memory_mb / available_memory_mb) * 100,
            'bottleneck': self.identify_rabbitmq_bottleneck([
                ('cpu', cpu_capacity),
                ('network', network_capacity_msg_per_sec),
                ('disk', disk_capacity_msg_per_sec)
            ])
        }

    def identify_rabbitmq_bottleneck(self, capacities):
        """Identify the limiting factor"""
        return min(capacities, key=lambda x: x[1])

    def calculate_cluster_size(self, workload_requirements):
        """Calculate RabbitMQ cluster size requirements"""
        total_msg_per_sec = workload_requirements['total_msg_per_sec']
        queue_profile = workload_requirements['queue_profile']

        # Calculate single node capacity
        node_capacity = self.calculate_node_capacity(queue_profile)
        effective_capacity = node_capacity['effective_capacity']

        # Apply high availability factor (active-passive or clustering overhead)
        ha_overhead = 1.4  # 40% overhead for clustering and HA
        effective_capacity_with_ha = effective_capacity / ha_overhead

        # Calculate required nodes
        safety_buffer = 1.2  # 20% safety buffer
        required_nodes = math.ceil(
            (total_msg_per_sec * safety_buffer) / effective_capacity_with_ha
        )

        # Minimum cluster size for HA
        min_nodes = 3
        final_node_count = max(required_nodes, min_nodes)

        return {
            'required_nodes': final_node_count,
            'node_capacity_analysis': node_capacity,
            'cluster_total_capacity': final_node_count * effective_capacity_with_ha,
            'utilization_percentage': (total_msg_per_sec / (final_node_count * effective_capacity_with_ha)) * 100,
            'cost_analysis': self.calculate_rabbitmq_costs(final_node_count),
            'memory_requirements': self.calculate_memory_requirements(queue_profile, final_node_count)
        }

    def calculate_rabbitmq_costs(self, node_count):
        """Calculate RabbitMQ cluster costs"""
        # EC2 instance costs (c5.4xlarge approximate)
        instance_cost_per_hour = 0.68
        monthly_hours = 24 * 30

        instance_costs = node_count * instance_cost_per_hour * monthly_hours
        storage_costs = node_count * self.node_specs['disk_capacity_gb'] * 0.10

        return {
            'monthly_instance_costs': instance_costs,
            'monthly_storage_costs': storage_costs,
            'total_monthly_cost': instance_costs + storage_costs
        }

    def calculate_memory_requirements(self, queue_profile, node_count):
        """Calculate memory requirements for the cluster"""
        messages_per_node = queue_profile.get('avg_queue_depth', 1000) / node_count
        memory_per_node_gb = (
            messages_per_node * queue_profile['avg_message_size_kb'] / 1024 / 1024
        )

        return {
            'memory_per_node_gb': memory_per_node_gb,
            'total_cluster_memory_gb': memory_per_node_gb * node_count,
            'memory_utilization_percentage': (memory_per_node_gb / self.node_specs['memory_gb']) * 100
        }

# Example RabbitMQ sizing
rabbitmq_model = RabbitMQCapacityModel()

rabbitmq_workload = {
    'total_msg_per_sec': 50000,
    'queue_profile': {
        'avg_message_size_kb': 4,
        'target_msg_per_sec': 50000,
        'avg_queue_depth': 10000,
        'concurrent_connections': 2000
    }
}

rabbitmq_cluster = rabbitmq_model.calculate_cluster_size(rabbitmq_workload)

print("\nRabbitMQ Cluster Sizing Results:")
print("=" * 40)
print(f"Required Nodes: {rabbitmq_cluster['required_nodes']}")
print(f"Cluster Capacity: {rabbitmq_cluster['cluster_total_capacity']:,.0f} msg/sec")
print(f"Utilization: {rabbitmq_cluster['utilization_percentage']:.1f}%")
print(f"Monthly Cost: ${rabbitmq_cluster['cost_analysis']['total_monthly_cost']:,.2f}")
```

### 3. Amazon SQS Cost and Performance Model

```python
class SQSCapacityModel:
    def __init__(self):
        self.sqs_pricing = {
            'standard_queue_requests_per_million': 0.40,
            'fifo_queue_requests_per_million': 0.50,
            'extended_client_storage_per_gb': 0.023,  # S3 storage for large messages
            'data_transfer_per_gb': 0.09
        }

        self.sqs_limits = {
            'standard_queue_throughput': float('inf'),  # Virtually unlimited
            'fifo_queue_throughput': 3000,              # 3000 TPS per FIFO queue
            'max_message_size_kb': 256,                 # 256 KB max
            'max_visibility_timeout_seconds': 43200,    # 12 hours
            'max_retention_days': 14
        }

    def calculate_sqs_costs(self, workload_profile):
        """Calculate SQS costs for given workload"""
        monthly_requests = workload_profile['monthly_requests']
        queue_type = workload_profile['queue_type']  # 'standard' or 'fifo'
        avg_message_size_kb = workload_profile['avg_message_size_kb']

        # Base request costs
        if queue_type == 'standard':
            request_cost = (monthly_requests / 1_000_000) * self.sqs_pricing['standard_queue_requests_per_million']
        else:
            request_cost = (monthly_requests / 1_000_000) * self.sqs_pricing['fifo_queue_requests_per_million']

        # Extended client storage costs (for messages > 256 KB)
        extended_storage_cost = 0
        if avg_message_size_kb > 256:
            # Messages larger than 256KB are stored in S3
            excess_size_kb = avg_message_size_kb - 256
            monthly_storage_gb = (monthly_requests * excess_size_kb) / (1024 * 1024)
            extended_storage_cost = monthly_storage_gb * self.sqs_pricing['extended_client_storage_per_gb']

        # Data transfer costs (simplified)
        monthly_data_transfer_gb = (monthly_requests * avg_message_size_kb) / (1024 * 1024)
        data_transfer_cost = monthly_data_transfer_gb * self.sqs_pricing['data_transfer_per_gb']

        total_cost = request_cost + extended_storage_cost + data_transfer_cost

        return {
            'request_cost': request_cost,
            'extended_storage_cost': extended_storage_cost,
            'data_transfer_cost': data_transfer_cost,
            'total_monthly_cost': total_cost,
            'cost_per_million_messages': (total_cost / monthly_requests) * 1_000_000,
            'throughput_analysis': self.analyze_throughput_requirements(workload_profile)
        }

    def analyze_throughput_requirements(self, workload_profile):
        """Analyze if SQS can meet throughput requirements"""
        peak_msg_per_sec = workload_profile.get('peak_msg_per_sec', 1000)
        queue_type = workload_profile['queue_type']

        if queue_type == 'standard':
            throughput_sufficient = True
            queues_needed = 1
            notes = "Standard queues have virtually unlimited throughput"
        else:
            # FIFO queues limited to 3000 TPS
            queues_needed = math.ceil(peak_msg_per_sec / self.sqs_limits['fifo_queue_throughput'])
            throughput_sufficient = queues_needed <= 10  # Practical limit for management

            if queues_needed > 1:
                notes = f"Need {queues_needed} FIFO queues for required throughput"
            else:
                notes = "Single FIFO queue sufficient"

        return {
            'throughput_sufficient': throughput_sufficient,
            'queues_needed': queues_needed,
            'notes': notes,
            'max_single_queue_throughput': self.sqs_limits['fifo_queue_throughput'] if queue_type == 'fifo' else float('inf')
        }

    def compare_queue_solutions(self, workload_scenarios):
        """Compare different queue solutions for various workloads"""
        comparison = {}

        for scenario_name, workload in workload_scenarios.items():
            # SQS Analysis
            sqs_standard = self.calculate_sqs_costs({**workload, 'queue_type': 'standard'})
            sqs_fifo = self.calculate_sqs_costs({**workload, 'queue_type': 'fifo'})

            # Kafka Analysis (simplified)
            kafka_brokers_needed = max(3, math.ceil(workload.get('peak_msg_per_sec', 1000) / 50000))
            kafka_monthly_cost = kafka_brokers_needed * 1.68 * 24 * 30

            # RabbitMQ Analysis (simplified)
            rabbitmq_nodes_needed = max(3, math.ceil(workload.get('peak_msg_per_sec', 1000) / 10000))
            rabbitmq_monthly_cost = rabbitmq_nodes_needed * 0.68 * 24 * 30

            comparison[scenario_name] = {
                'workload': workload,
                'sqs_standard': {**sqs_standard, 'solution': 'SQS Standard'},
                'sqs_fifo': {**sqs_fifo, 'solution': 'SQS FIFO'},
                'kafka_estimate': {
                    'total_monthly_cost': kafka_monthly_cost,
                    'brokers_needed': kafka_brokers_needed,
                    'solution': 'Kafka'
                },
                'rabbitmq_estimate': {
                    'total_monthly_cost': rabbitmq_monthly_cost,
                    'nodes_needed': rabbitmq_nodes_needed,
                    'solution': 'RabbitMQ'
                }
            }

        return comparison

# Example comparison
sqs_model = SQSCapacityModel()

workload_scenarios = {
    'low_volume': {
        'monthly_requests': 10_000_000,      # 10M requests/month
        'avg_message_size_kb': 2,
        'peak_msg_per_sec': 100
    },
    'medium_volume': {
        'monthly_requests': 500_000_000,     # 500M requests/month
        'avg_message_size_kb': 4,
        'peak_msg_per_sec': 5000
    },
    'high_volume': {
        'monthly_requests': 10_000_000_000,  # 10B requests/month
        'avg_message_size_kb': 8,
        'peak_msg_per_sec': 100000
    }
}

comparison = sqs_model.compare_queue_solutions(workload_scenarios)

print("\nMessage Queue Solution Comparison:")
print("=" * 50)
for scenario, analysis in comparison.items():
    print(f"\n{scenario.title()} Scenario:")
    print(f"  Peak throughput: {analysis['workload']['peak_msg_per_sec']:,} msg/sec")
    print(f"  Monthly requests: {analysis['workload']['monthly_requests']:,}")

    solutions = [
        ('SQS Standard', analysis['sqs_standard']['total_monthly_cost']),
        ('SQS FIFO', analysis['sqs_fifo']['total_monthly_cost']),
        ('Kafka', analysis['kafka_estimate']['total_monthly_cost']),
        ('RabbitMQ', analysis['rabbitmq_estimate']['total_monthly_cost'])
    ]

    # Sort by cost
    solutions.sort(key=lambda x: x[1])

    print("  Cost ranking (lowest to highest):")
    for i, (solution, cost) in enumerate(solutions):
        print(f"    {i+1}. {solution}: ${cost:,.2f}/month")
```

## Production Configuration Examples

### Kafka Production Configuration

```yaml
# Kafka Broker Configuration (server.properties)
############################# Server Basics #############################
broker.id=1
listeners=PLAINTEXT://kafka-broker-1:9092,SSL://kafka-broker-1:9093
advertised.listeners=PLAINTEXT://kafka-broker-1:9092,SSL://kafka-broker-1:9093
num.network.threads=8
num.io.threads=16
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600

############################# Log Basics #############################
log.dirs=/var/kafka-logs-1,/var/kafka-logs-2,/var/kafka-logs-3
num.partitions=12
num.recovery.threads.per.data.dir=4
offsets.topic.replication.factor=3
transaction.state.log.replication.factor=3
transaction.state.log.min.isr=2

############################# Performance Tuning #############################
# Replication settings
default.replication.factor=3
min.insync.replicas=2
replica.lag.time.max.ms=30000

# Log settings for high throughput
log.segment.bytes=536870912          # 512MB segments
log.retention.hours=168              # 7 days retention
log.retention.check.interval.ms=300000
log.cleanup.policy=delete

# Compression for efficiency
compression.type=lz4

# Producer settings
batch.size=65536                     # 64KB batch size
linger.ms=5                         # 5ms linger time
buffer.memory=134217728             # 128MB buffer

# Consumer settings
fetch.min.bytes=50000               # 50KB minimum fetch
fetch.max.wait.ms=500              # 500ms max wait

############################# High Availability #############################
unclean.leader.election.enable=false
auto.leader.rebalance.enable=true
leader.imbalance.per.broker.percentage=10
leader.imbalance.check.interval.seconds=300

# JVM Settings (kafka-server-start.sh)
export KAFKA_HEAP_OPTS="-Xmx8G -Xms8G"
export KAFKA_JVM_PERFORMANCE_OPTS="-server -XX:+UseG1GC -XX:MaxGCPauseMillis=20 -XX:InitiatingHeapOccupancyPercent=35 -XX:+ExplicitGCInvokesConcurrent -Djava.awt.headless=true"

---
# Kafka Connect Configuration for scaling
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaConnect
metadata:
  name: kafka-connect-cluster
spec:
  replicas: 6
  bootstrapServers: kafka-cluster-kafka-bootstrap:9093
  tls:
    trustedCertificates:
      - secretName: kafka-cluster-cluster-ca-cert
        certificate: ca.crt
  config:
    group.id: connect-cluster
    offset.storage.topic: connect-cluster-offsets
    offset.storage.replication.factor: 3
    config.storage.topic: connect-cluster-configs
    config.storage.replication.factor: 3
    status.storage.topic: connect-cluster-status
    status.storage.replication.factor: 3
    key.converter: org.apache.kafka.connect.json.JsonConverter
    value.converter: org.apache.kafka.connect.json.JsonConverter
    key.converter.schemas.enable: false
    value.converter.schemas.enable: false
    internal.key.converter: org.apache.kafka.connect.json.JsonConverter
    internal.value.converter: org.apache.kafka.connect.json.JsonConverter
    internal.key.converter.schemas.enable: false
    internal.value.converter.schemas.enable: false
  resources:
    requests:
      memory: 2Gi
      cpu: 1000m
    limits:
      memory: 4Gi
      cpu: 2000m
```

This comprehensive message queue sizing model provides mathematical frameworks, production configurations, and cost optimization strategies for designing efficient message queue systems at scale.