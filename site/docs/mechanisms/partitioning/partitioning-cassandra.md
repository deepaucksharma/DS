# Cassandra Partitioning Architecture

## Overview of Cassandra's Approach

Apache Cassandra uses a sophisticated partitioning scheme based on consistent hashing with virtual nodes (vnodes) to achieve excellent horizontal scalability and fault tolerance.

### Cassandra Ring Architecture

```mermaid
graph TB
    subgraph Cassandra Ring Architecture
        subgraph Hash Ring (0 to 2^127-1)
            RING[Token Ring<br/>128-bit MD5 hash space<br/>Tokens distributed across nodes]
        end

        subgraph Physical Nodes
            NODE1[Node 1 (10.0.1.10)<br/>256 virtual nodes<br/>Tokens: 123...456, 789...012, ...]
            NODE2[Node 2 (10.0.1.11)<br/>256 virtual nodes<br/>Tokens: 234...567, 890...123, ...]
            NODE3[Node 3 (10.0.1.12)<br/>256 virtual nodes<br/>Tokens: 345...678, 901...234, ...]
            NODE4[Node 4 (10.0.1.13)<br/>256 virtual nodes<br/>Tokens: 456...789, 012...345, ...]
        end

        subgraph Data Distribution
            PARTITION[Partition Key Hashing<br/>hash(partition_key) → token<br/>Data placed on ring position]
            REPLICATION[Replication Strategy<br/>RF=3: Next N nodes clockwise<br/>NetworkTopologyStrategy]
        end

        subgraph Client Operations
            CLIENT[Client Queries<br/>Coordinator node selection<br/>Token-aware routing]
            COORDINATOR[Coordinator Node<br/>Query coordination<br/>Response aggregation]
        end
    end

    CLIENT --> COORDINATOR
    COORDINATOR --> PARTITION
    PARTITION --> RING
    RING --> NODE1
    RING --> NODE2
    RING --> NODE3
    RING --> NODE4
    NODE1 --> REPLICATION
    NODE2 --> REPLICATION
    NODE3 --> REPLICATION
    NODE4 --> REPLICATION

    %% Apply 4-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDev stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class CLIENT edgeStyle
    class COORDINATOR,NODE1,NODE2,NODE3,NODE4 serviceStyle
    class RING,PARTITION stateStyle
    class REPLICATION controlStyle
```

## Token Assignment and Virtual Nodes

### Virtual Node Distribution

```mermaid
graph LR
    subgraph Cassandra Virtual Nodes (VNodes)
        subgraph Traditional Single Token per Node
            SINGLE[Single Token Assignment<br/>Node A: token 25%<br/>Node B: token 50%<br/>Node C: token 75%<br/>Node D: token 100%<br/><br/>Problems:<br/>• Hotspots possible<br/>• Slow rebalancing<br/>• Manual token management]
        end

        subgraph Virtual Nodes (Default: 256 per node)
            VIRTUAL[Virtual Node Assignment<br/>Node A: 256 random tokens<br/>Node B: 256 random tokens<br/>Node C: 256 random tokens<br/>Node D: 256 random tokens<br/><br/>Benefits:<br/>• Even load distribution<br/>• Fast rebalancing<br/>• Automatic token assignment]
        end

        subgraph Token Ownership
            OWNERSHIP[Token Ownership Examples<br/>Node A owns tokens:<br/>• 12,345,678...90,123,456<br/>• 23,456,789...01,234,567<br/>• 34,567,890...12,345,678<br/>• ... (253 more)<br/><br/>Data Range: Each token owns<br/>range from previous token<br/>to current token (clockwise)]
        end
    end

    SINGLE --> VIRTUAL
    VIRTUAL --> OWNERSHIP

    %% Apply state plane color for data structures
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    class SINGLE,VIRTUAL,OWNERSHIP stateStyle
```

### Token Calculation and Assignment

```python
# Cassandra-style token calculation
import hashlib
import random
from typing import List, Dict, Set

class CassandraTokenRing:
    def __init__(self, num_vnodes_per_node: int = 256):
        self.num_vnodes_per_node = num_vnodes_per_node
        self.ring: Dict[int, str] = {}  # token -> node_id
        self.node_tokens: Dict[str, List[int]] = {}  # node_id -> [tokens]
        self.max_token = 2 ** 127 - 1

    def add_node(self, node_id: str) -> List[int]:
        """Add a node with randomly assigned virtual nodes"""
        if node_id in self.node_tokens:
            return self.node_tokens[node_id]

        # Generate random tokens for this node
        tokens = []
        existing_tokens = set(self.ring.keys())

        while len(tokens) < self.num_vnodes_per_node:
            # Generate random token in the hash space
            token = random.randint(0, self.max_token)

            # Ensure token doesn't already exist
            if token not in existing_tokens:
                tokens.append(token)
                existing_tokens.add(token)
                self.ring[token] = node_id

        tokens.sort()
        self.node_tokens[node_id] = tokens

        return tokens

    def remove_node(self, node_id: str) -> List[int]:
        """Remove a node and return its tokens"""
        if node_id not in self.node_tokens:
            return []

        tokens = self.node_tokens[node_id]

        # Remove tokens from ring
        for token in tokens:
            del self.ring[token]

        del self.node_tokens[node_id]
        return tokens

    def get_partition_key_token(self, partition_key: str) -> int:
        """Calculate token for a partition key using MD5"""
        # Cassandra uses MD5 hash of partition key
        hash_bytes = hashlib.md5(partition_key.encode()).digest()

        # Convert first 16 bytes to 128-bit integer
        token = int.from_bytes(hash_bytes, byteorder='big')

        # Cassandra uses signed 64-bit tokens in practice, but conceptually 128-bit
        return token % (self.max_token + 1)

    def get_responsible_nodes(self, partition_key: str, replication_factor: int = 3) -> List[str]:
        """Get nodes responsible for a partition key"""
        token = self.get_partition_key_token(partition_key)
        return self.get_nodes_for_token(token, replication_factor)

    def get_nodes_for_token(self, token: int, replication_factor: int = 3) -> List[str]:
        """Get nodes responsible for a token"""
        if not self.ring:
            return []

        sorted_tokens = sorted(self.ring.keys())

        # Find the first token >= given token (clockwise)
        start_idx = 0
        for i, ring_token in enumerate(sorted_tokens):
            if ring_token >= token:
                start_idx = i
                break

        # Collect unique nodes starting from start_idx
        responsible_nodes = []
        seen_nodes = set()
        idx = start_idx

        while len(responsible_nodes) < replication_factor and len(seen_nodes) < len(self.node_tokens):
            ring_token = sorted_tokens[idx % len(sorted_tokens)]
            node = self.ring[ring_token]

            if node not in seen_nodes:
                responsible_nodes.append(node)
                seen_nodes.add(node)

            idx += 1

        return responsible_nodes

    def get_load_distribution(self) -> Dict[str, Dict]:
        """Analyze load distribution across nodes"""
        if not self.ring:
            return {}

        sorted_tokens = sorted(self.ring.keys())
        node_ranges = {}

        for i, token in enumerate(sorted_tokens):
            node = self.ring[token]

            # Calculate range size (from previous token to current token)
            if i == 0:
                # First token: range from last token to this token (wrap around)
                range_size = token + (self.max_token + 1 - sorted_tokens[-1])
            else:
                range_size = token - sorted_tokens[i - 1]

            if node not in node_ranges:
                node_ranges[node] = {'total_range': 0, 'token_count': 0, 'ranges': []}

            node_ranges[node]['total_range'] += range_size
            node_ranges[node]['token_count'] += 1
            node_ranges[node]['ranges'].append(range_size)

        # Calculate percentages
        total_range = self.max_token + 1
        for node_data in node_ranges.values():
            node_data['percentage'] = (node_data['total_range'] / total_range) * 100
            node_data['avg_range_size'] = node_data['total_range'] / node_data['token_count']

        return node_ranges

    def simulate_node_failure(self, failed_node: str) -> Dict[str, List[str]]:
        """Simulate node failure and show data movement"""
        if failed_node not in self.node_tokens:
            return {}

        failed_tokens = self.node_tokens[failed_node]
        data_movement = {}

        for token in failed_tokens:
            # Find the next available nodes for each token
            remaining_nodes = [node for node in self.node_tokens.keys() if node != failed_node]
            if not remaining_nodes:
                continue

            # Get next nodes clockwise from this token
            next_nodes = []
            sorted_tokens = sorted([t for t, n in self.ring.items() if n != failed_node])

            # Find position and get next nodes
            for ring_token in sorted_tokens:
                if ring_token > token:
                    next_nodes.append(self.ring[ring_token])
                    break

            if not next_nodes and sorted_tokens:
                # Wrap around to first token
                next_nodes.append(self.ring[sorted_tokens[0]])

            if next_nodes:
                takeover_node = next_nodes[0]
                if takeover_node not in data_movement:
                    data_movement[takeover_node] = []
                data_movement[takeover_node].append(f"token_{token}")

        return data_movement

# Example usage and demonstration
def demonstrate_cassandra_partitioning():
    # Create a 4-node cluster
    ring = CassandraTokenRing(num_vnodes_per_node=64)  # Reduced for demo

    nodes = ['cassandra-1', 'cassandra-2', 'cassandra-3', 'cassandra-4']
    for node in nodes:
        tokens = ring.add_node(node)
        print(f"Added {node} with {len(tokens)} virtual nodes")

    # Analyze load distribution
    print("\nLoad distribution:")
    distribution = ring.get_load_distribution()
    for node, data in distribution.items():
        print(f"  {node}: {data['percentage']:.2f}% of keyspace, {data['token_count']} tokens")

    # Test partition key placement
    test_keys = ['user:12345', 'order:67890', 'product:abcde', 'session:xyz123']
    print(f"\nPartition key placement (RF=3):")
    for key in test_keys:
        responsible_nodes = ring.get_responsible_nodes(key, 3)
        token = ring.get_partition_key_token(key)
        print(f"  {key} (token: {token}) -> {responsible_nodes}")

    # Simulate node failure
    print(f"\nSimulating failure of cassandra-2:")
    data_movement = ring.simulate_node_failure('cassandra-2')
    for node, tokens in data_movement.items():
        print(f"  {node} takes over {len(tokens)} token ranges")

    # Add new node
    print(f"\nAdding new node cassandra-5:")
    new_tokens = ring.add_node('cassandra-5')
    print(f"  Added with {len(new_tokens)} virtual nodes")

    # New distribution
    print("\nNew load distribution:")
    distribution = ring.get_load_distribution()
    for node, data in distribution.items():
        print(f"  {node}: {data['percentage']:.2f}% of keyspace")

if __name__ == "__main__":
    demonstrate_cassandra_partitioning()
```

## Replication Strategies

### NetworkTopologyStrategy

```mermaid
graph TB
    subgraph Cassandra NetworkTopologyStrategy
        subgraph Multi-Datacenter Setup
            subgraph DC1 (Primary)
                DC1_RACK1[Rack 1<br/>cassandra-1<br/>cassandra-2]
                DC1_RACK2[Rack 2<br/>cassandra-3<br/>cassandra-4]
                DC1_RACK3[Rack 3<br/>cassandra-5<br/>cassandra-6]
            end

            subgraph DC2 (Secondary)
                DC2_RACK1[Rack 1<br/>cassandra-7<br/>cassandra-8]
                DC2_RACK2[Rack 2<br/>cassandra-9<br/>cassandra-10]
            end
        end

        subgraph Replication Configuration
            RF_CONFIG[Replication Factor<br/>DC1: RF=3<br/>DC2: RF=2<br/><br/>Total replicas: 5<br/>Rack-aware placement]
        end

        subgraph Data Placement Rules
            PLACEMENT[Placement Rules<br/>1. First replica: calculated node<br/>2. Subsequent replicas: next nodes<br/>3. Rack diversity within DC<br/>4. DC placement per RF config]
        end
    end

    DC1_RACK1 <--> DC1_RACK2
    DC1_RACK2 <--> DC1_RACK3
    DC1_RACK1 <--> DC1_RACK3

    DC2_RACK1 <--> DC2_RACK2

    DC1_RACK2 -.-> DC2_RACK1
    DC1_RACK3 -.-> DC2_RACK2

    RF_CONFIG --> PLACEMENT

    %% Apply colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class DC1_RACK1,DC1_RACK2,DC1_RACK3,DC2_RACK1,DC2_RACK2 serviceStyle
    class RF_CONFIG stateStyle
    class PLACEMENT controlStyle
```

### Replica Placement Algorithm

```python
# Cassandra replica placement simulation
from typing import Dict, List, Set
from dataclasses import dataclass

@dataclass
class CassandraNode:
    node_id: str
    datacenter: str
    rack: str
    tokens: List[int]

class NetworkTopologyStrategy:
    def __init__(self):
        self.nodes: Dict[str, CassandraNode] = {}
        self.dc_nodes: Dict[str, List[str]] = {}
        self.rack_nodes: Dict[str, Dict[str, List[str]]] = {}

    def add_node(self, node: CassandraNode):
        """Add a node to the cluster topology"""
        self.nodes[node.node_id] = node

        # Update datacenter mapping
        if node.datacenter not in self.dc_nodes:
            self.dc_nodes[node.datacenter] = []
        self.dc_nodes[node.datacenter].append(node.node_id)

        # Update rack mapping
        if node.datacenter not in self.rack_nodes:
            self.rack_nodes[node.datacenter] = {}
        if node.rack not in self.rack_nodes[node.datacenter]:
            self.rack_nodes[node.datacenter][node.rack] = []
        self.rack_nodes[node.datacenter][node.rack].append(node.node_id)

    def get_replicas(self, primary_node: str, replication_factors: Dict[str, int]) -> List[str]:
        """Get replica nodes using NetworkTopologyStrategy"""
        replicas = []
        primary_dc = self.nodes[primary_node].datacenter

        # Start with primary node
        current_node = primary_node
        visited_nodes = set([primary_node])

        # For each datacenter in replication factor config
        for dc, rf in replication_factors.items():
            dc_replicas = []

            if dc == primary_dc:
                # Include primary node for its datacenter
                dc_replicas.append(primary_node)
                rf -= 1  # Already have one replica

            # Get additional replicas for this datacenter
            dc_candidates = [n for n in self.dc_nodes.get(dc, []) if n not in visited_nodes]

            # Sort candidates by ring position relative to primary
            dc_candidates = self._sort_by_ring_position(dc_candidates, primary_node)

            # Apply rack diversity
            selected_replicas = self._select_with_rack_diversity(dc_candidates, rf, dc)

            dc_replicas.extend(selected_replicas)
            visited_nodes.update(selected_replicas)
            replicas.extend(dc_replicas)

        return replicas

    def _sort_by_ring_position(self, candidates: List[str], primary_node: str) -> List[str]:
        """Sort candidate nodes by their position on the ring"""
        # In practice, this would use actual token positions
        # For demo, we'll use a simplified approach
        primary_tokens = self.nodes[primary_node].tokens

        if not primary_tokens:
            return candidates

        primary_token = min(primary_tokens)  # Use smallest token as reference

        def token_distance(node_id: str):
            node_tokens = self.nodes[node_id].tokens
            if not node_tokens:
                return float('inf')

            min_distance = float('inf')
            for token in node_tokens:
                # Calculate clockwise distance
                if token >= primary_token:
                    distance = token - primary_token
                else:
                    # Wrap around
                    distance = (2**127 - primary_token) + token

                min_distance = min(min_distance, distance)

            return min_distance

        return sorted(candidates, key=token_distance)

    def _select_with_rack_diversity(self, candidates: List[str], rf: int, dc: str) -> List[str]:
        """Select replicas with rack diversity"""
        if rf <= 0:
            return []

        selected = []
        used_racks = set()

        # First pass: one replica per rack
        for node_id in candidates:
            if len(selected) >= rf:
                break

            node_rack = self.nodes[node_id].rack
            if node_rack not in used_racks:
                selected.append(node_id)
                used_racks.add(node_rack)

        # Second pass: fill remaining slots if needed
        if len(selected) < rf:
            remaining_candidates = [n for n in candidates if n not in selected]
            needed = rf - len(selected)
            selected.extend(remaining_candidates[:needed])

        return selected

    def analyze_replica_distribution(self, replication_factors: Dict[str, int]) -> Dict:
        """Analyze how replicas would be distributed"""
        analysis = {
            'total_replicas_per_dc': {},
            'rack_distribution': {},
            'load_balance': {}
        }

        # Sample some tokens to analyze distribution
        sample_tokens = [i * (2**127 // 1000) for i in range(1000)]  # 1000 sample points

        for token in sample_tokens:
            # Find primary node for this token (simplified)
            primary_node = self._find_primary_node_for_token(token)
            if not primary_node:
                continue

            replicas = self.get_replicas(primary_node, replication_factors)

            # Count by datacenter
            for replica in replicas:
                dc = self.nodes[replica].datacenter
                if dc not in analysis['total_replicas_per_dc']:
                    analysis['total_replicas_per_dc'][dc] = 0
                analysis['total_replicas_per_dc'][dc] += 1

                # Count by rack
                rack = f"{dc}:{self.nodes[replica].rack}"
                if rack not in analysis['rack_distribution']:
                    analysis['rack_distribution'][rack] = 0
                analysis['rack_distribution'][rack] += 1

        return analysis

    def _find_primary_node_for_token(self, token: int) -> str:
        """Find the primary node responsible for a token"""
        # Simplified: return first node with a token >= given token
        best_node = None
        min_distance = float('inf')

        for node_id, node in self.nodes.items():
            for node_token in node.tokens:
                if node_token >= token:
                    distance = node_token - token
                    if distance < min_distance:
                        min_distance = distance
                        best_node = node_id

        return best_node or list(self.nodes.keys())[0]

# Example usage
def demonstrate_network_topology_strategy():
    strategy = NetworkTopologyStrategy()

    # Create a multi-DC, multi-rack cluster
    nodes = [
        # DC1 nodes
        CassandraNode('node1', 'dc1', 'rack1', [100, 500, 900]),
        CassandraNode('node2', 'dc1', 'rack1', [200, 600, 1000]),
        CassandraNode('node3', 'dc1', 'rack2', [300, 700, 1100]),
        CassandraNode('node4', 'dc1', 'rack2', [400, 800, 1200]),

        # DC2 nodes
        CassandraNode('node5', 'dc2', 'rack1', [150, 550, 950]),
        CassandraNode('node6', 'dc2', 'rack2', [250, 650, 1050]),
    ]

    for node in nodes:
        strategy.add_node(node)

    # Test replication with RF=3 in DC1, RF=2 in DC2
    replication_config = {'dc1': 3, 'dc2': 2}

    print("Cluster topology:")
    for dc, nodes_in_dc in strategy.dc_nodes.items():
        print(f"  {dc}: {len(nodes_in_dc)} nodes")
        for rack, rack_nodes in strategy.rack_nodes[dc].items():
            print(f"    {rack}: {rack_nodes}")

    print(f"\nReplication configuration: {replication_config}")

    # Test replica placement for different primary nodes
    test_primaries = ['node1', 'node3', 'node5']
    for primary in test_primaries:
        replicas = strategy.get_replicas(primary, replication_config)
        print(f"\nPrimary: {primary} ({strategy.nodes[primary].datacenter}:{strategy.nodes[primary].rack})")
        print(f"Replicas: {replicas}")

        # Show datacenter distribution
        dc_count = {}
        for replica in replicas:
            dc = strategy.nodes[replica].datacenter
            dc_count[dc] = dc_count.get(dc, 0) + 1
        print(f"DC distribution: {dc_count}")

if __name__ == "__main__":
    demonstrate_network_topology_strategy()
```

## Data Distribution and Hotspots

### Handling Hotspots in Cassandra

```mermaid
graph TB
    subgraph Cassandra Hotspot Mitigation
        subgraph Partition Key Design
            GOOD_KEYS[Good Partition Keys<br/>• High cardinality<br/>• Even distribution<br/>• Include tenant/shard ID<br/>Example: tenant_id + user_id]
            BAD_KEYS[Bad Partition Keys<br/>• Low cardinality<br/>• Skewed distribution<br/>• Sequential values<br/>Example: timestamp only]
        end

        subgraph Virtual Node Benefits
            VNODE_BENEFITS[Virtual Node Mitigation<br/>• Distribute hotspots<br/>• Multiple small ranges per node<br/>• Faster rebalancing<br/>• Better failure recovery]
        end

        subgraph Schema Design Patterns
            BUCKETING[Time Bucketing<br/>partition_key = date_bucket + id<br/>WHERE date_bucket = '2024-01'<br/>AND id = 'user123']

            SHARDING[Manual Sharding<br/>partition_key = shard_id + business_key<br/>shard_id = hash(user_id) % 100<br/>Distribute across 100 shards]
        end

        subgraph Monitoring and Detection
            MONITORING[Hotspot Detection<br/>• Per-node request rates<br/>• CPU/memory utilization<br/>• Token range statistics<br/>• Compaction patterns]
        end
    end

    BAD_KEYS --> GOOD_KEYS
    GOOD_KEYS --> VNODE_BENEFITS
    VNODE_BENEFITS --> BUCKETING
    VNODE_BENEFITS --> SHARDING
    BUCKETING --> MONITORING
    SHARDING --> MONITORING

    %% Apply colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class BAD_KEYS edgeStyle
    class GOOD_KEYS,VNODE_BENEFITS serviceStyle
    class BUCKETING,SHARDING stateStyle
    class MONITORING controlStyle
```

## Cassandra Configuration Examples

### Production Cluster Configuration

```yaml
# cassandra.yaml - Production configuration
cluster_name: 'Production Cluster'

# Storage settings
data_file_directories:
  - /var/lib/cassandra/data
commitlog_directory: /var/lib/cassandra/commitlog
saved_caches_directory: /var/lib/cassandra/saved_caches

# Network settings
listen_address: 10.0.1.10
broadcast_address: 10.0.1.10
rpc_address: 0.0.0.0
broadcast_rpc_address: 10.0.1.10

# Seed configuration
seed_provider:
  - class_name: org.apache.cassandra.locator.SimpleSeedProvider
    parameters:
      - seeds: "10.0.1.10,10.0.1.11,10.0.1.12"

# Virtual nodes
num_tokens: 256
initial_token:  # Leave empty for automatic token assignment

# Snitch configuration (topology awareness)
endpoint_snitch: GossipingPropertyFileSnitch

# Performance tuning
concurrent_reads: 32
concurrent_writes: 32
concurrent_counter_writes: 32

# Memory settings
memtable_heap_space_in_mb: 2048
memtable_offheap_space_in_mb: 2048

# Compaction
compaction_throughput_mb_per_sec: 64
concurrent_compactors: 4

# Commit log
commitlog_sync: periodic
commitlog_sync_period_in_ms: 10000
commitlog_segment_size_in_mb: 32

# Timeouts
read_request_timeout_in_ms: 5000
range_request_timeout_in_ms: 10000
write_request_timeout_in_ms: 2000
counter_write_request_timeout_in_ms: 5000
cas_contention_timeout_in_ms: 1000
truncate_request_timeout_in_ms: 60000
request_timeout_in_ms: 10000
```

```properties
# cassandra-rackdc.properties
dc=dc1
rack=rack1
# prefer_local=true
```

### CQL Schema Design Examples

```sql
-- Good partition key design examples

-- 1. User data with tenant sharding
CREATE TABLE user_profiles (
    tenant_id text,
    user_id uuid,
    created_date date,
    email text,
    profile_data map<text, text>,
    PRIMARY KEY ((tenant_id, user_id))
);

-- 2. Time-series data with bucketing
CREATE TABLE sensor_readings (
    sensor_id text,
    bucket_date date,
    reading_time timestamp,
    temperature double,
    humidity double,
    PRIMARY KEY ((sensor_id, bucket_date), reading_time)
) WITH CLUSTERING ORDER BY (reading_time DESC);

-- 3. Event logging with sharding
CREATE TABLE application_logs (
    shard_id int,
    log_level text,
    timestamp timestamp,
    application text,
    message text,
    PRIMARY KEY ((shard_id, log_level), timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);

-- 4. Social media posts with user bucketing
CREATE TABLE user_posts (
    user_bucket int,  -- hash(user_id) % 100
    user_id uuid,
    post_id timeuuid,
    content text,
    created_at timestamp,
    PRIMARY KEY ((user_bucket, user_id), post_id)
) WITH CLUSTERING ORDER BY (post_id DESC);

-- Keyspace with NetworkTopologyStrategy
CREATE KEYSPACE production
WITH REPLICATION = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3,
    'dc2': 2
} AND DURABLE_WRITES = true;
```

### Monitoring and Metrics

```yaml
# Cassandra monitoring with Prometheus
cassandra_metrics:
  node_metrics:
    - name: cassandra_storage_load_bytes
      description: "Storage load per node"
      query: "cassandra_storage_load_bytes"

    - name: cassandra_compaction_pending_tasks
      description: "Pending compaction tasks"
      query: "cassandra_compaction_pending_tasks"

    - name: cassandra_read_latency_99p
      description: "Read latency 99th percentile"
      query: "histogram_quantile(0.99, cassandra_read_latency_seconds_bucket)"

  token_range_metrics:
    - name: cassandra_token_ownership
      description: "Token ownership percentage per node"
      calculation: "Based on virtual node distribution"

    - name: cassandra_hotspot_detection
      description: "Request rate variance across nodes"
      threshold: "3x standard deviation from mean"

  alerts:
    - name: CassandraNodeDown
      condition: "up{job='cassandra'} == 0"
      severity: critical

    - name: CassandraHighReadLatency
      condition: "cassandra_read_latency_99p > 0.1"  # 100ms
      severity: warning

    - name: CassandraTokenImbalance
      condition: "max(cassandra_token_ownership) - min(cassandra_token_ownership) > 20"
      severity: warning

    - name: CassandraCompactionBacklog
      condition: "cassandra_compaction_pending_tasks > 20"
      severity: warning
```

This comprehensive overview of Cassandra's partitioning architecture demonstrates how it achieves excellent horizontal scalability through consistent hashing, virtual nodes, and topology-aware replication strategies.