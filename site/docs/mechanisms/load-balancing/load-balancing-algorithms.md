# Load Balancing Algorithms and Implementation

## Overview

Load balancing algorithms determine how incoming requests are distributed across backend servers. The choice of algorithm significantly impacts performance, reliability, and user experience in production systems.

## Core Load Balancing Algorithms

```mermaid
graph TB
    subgraph Client[Client Requests]
        C1[Client 1]
        C2[Client 2]
        C3[Client 3]
        C4[Client 4]
        C5[Client 5]
    end

    subgraph LoadBalancer[Load Balancer - Algorithm Engine]
        LB[Load Balancer<br/>nginx/HAProxy/AWS ALB]
        ALG[Algorithm Selection:<br/>• Round Robin<br/>• Weighted Round Robin<br/>• Least Connections<br/>• IP Hash<br/>• Random<br/>• Health-based]
    end

    subgraph Backend[Backend Server Pool]
        S1[Server 1<br/>CPU: 40%<br/>Connections: 150<br/>Weight: 3]
        S2[Server 2<br/>CPU: 60%<br/>Connections: 200<br/>Weight: 2]
        S3[Server 3<br/>CPU: 20%<br/>Connections: 100<br/>Weight: 5]
        S4[Server 4<br/>CPU: 80%<br/>Connections: 250<br/>Weight: 1]
    end

    C1 --> LB
    C2 --> LB
    C3 --> LB
    C4 --> LB
    C5 --> LB

    LB --> ALG
    ALG --> S1
    ALG --> S2
    ALG --> S3
    ALG --> S4

    %% Styling
    classDef client fill:#87CEEB,stroke:#4682B4,color:#000
    classDef balancer fill:#90EE90,stroke:#006400,color:#000
    classDef server fill:#FFB6C1,stroke:#FF69B4,color:#000

    class C1,C2,C3,C4,C5 client
    class LB,ALG balancer
    class S1,S2,S3,S4 server
```

## Algorithm Implementation Comparison

### Round Robin Algorithm

```python
class RoundRobinBalancer:
    """Simple round robin load balancer implementation"""

    def __init__(self, servers):
        self.servers = servers
        self.current = 0
        self.total_requests = 0

    def get_server(self):
        """Get next server in round robin fashion"""
        server = self.servers[self.current]
        self.current = (self.current + 1) % len(self.servers)
        self.total_requests += 1
        return server

    def add_server(self, server):
        """Add new server to the pool"""
        self.servers.append(server)

    def remove_server(self, server):
        """Remove server from the pool"""
        if server in self.servers:
            index = self.servers.index(server)
            self.servers.remove(server)

            # Adjust current pointer if needed
            if index < self.current:
                self.current -= 1
            elif index == self.current and self.current >= len(self.servers):
                self.current = 0

# Example usage
servers = ['10.0.1.10', '10.0.1.11', '10.0.1.12', '10.0.1.13']
balancer = RoundRobinBalancer(servers)

# Distribute requests
for i in range(8):
    server = balancer.get_server()
    print(f"Request {i+1} -> {server}")

# Output:
# Request 1 -> 10.0.1.10
# Request 2 -> 10.0.1.11
# Request 3 -> 10.0.1.12
# Request 4 -> 10.0.1.13
# Request 5 -> 10.0.1.10
# Request 6 -> 10.0.1.11
# Request 7 -> 10.0.1.12
# Request 8 -> 10.0.1.13
```

### Weighted Round Robin Algorithm

```python
import threading
from typing import List, Dict, Tuple

class WeightedRoundRobinBalancer:
    """Weighted round robin with smooth distribution"""

    def __init__(self, servers: List[Tuple[str, int]]):
        """
        Initialize with servers and their weights
        servers: List of (server_address, weight) tuples
        """
        self.servers = {}
        self.lock = threading.Lock()

        for server, weight in servers:
            self.servers[server] = {
                'weight': weight,
                'current_weight': 0,
                'effective_weight': weight,
                'total_requests': 0,
                'failed_requests': 0
            }

        self.total_weight = sum(s['weight'] for s in self.servers.values())
        self.total_requests = 0

    def get_server(self) -> str:
        """Get server using smooth weighted round robin algorithm"""
        with self.lock:
            if not self.servers:
                return None

            # Find server with highest current_weight
            best_server = None
            max_weight = -1

            for server, data in self.servers.items():
                # Add effective weight to current weight
                data['current_weight'] += data['effective_weight']

                if data['current_weight'] > max_weight:
                    max_weight = data['current_weight']
                    best_server = server

            if best_server:
                # Subtract total weight from selected server
                self.servers[best_server]['current_weight'] -= self.total_weight
                self.servers[best_server]['total_requests'] += 1
                self.total_requests += 1

            return best_server

    def update_server_weight(self, server: str, new_weight: int):
        """Update server weight dynamically"""
        with self.lock:
            if server in self.servers:
                old_weight = self.servers[server]['weight']
                self.servers[server]['weight'] = new_weight
                self.servers[server]['effective_weight'] = new_weight
                self.total_weight = self.total_weight - old_weight + new_weight

    def mark_server_down(self, server: str):
        """Mark server as down (weight = 0)"""
        with self.lock:
            if server in self.servers:
                self.servers[server]['effective_weight'] = 0

    def mark_server_up(self, server: str):
        """Mark server as up (restore original weight)"""
        with self.lock:
            if server in self.servers:
                self.servers[server]['effective_weight'] = self.servers[server]['weight']

    def get_stats(self) -> Dict:
        """Get load balancer statistics"""
        with self.lock:
            stats = {
                'total_requests': self.total_requests,
                'servers': {}
            }

            for server, data in self.servers.items():
                stats['servers'][server] = {
                    'requests': data['total_requests'],
                    'weight': data['weight'],
                    'current_weight': data['current_weight'],
                    'effective_weight': data['effective_weight'],
                    'percentage': (data['total_requests'] / self.total_requests * 100)
                              if self.total_requests > 0 else 0
                }

            return stats

# Production example with different server capacities
servers = [
    ('app-01.prod.com', 5),  # High-capacity server
    ('app-02.prod.com', 3),  # Medium-capacity server
    ('app-03.prod.com', 2),  # Low-capacity server
    ('app-04.prod.com', 1)   # Backup server
]

balancer = WeightedRoundRobinBalancer(servers)

# Simulate request distribution
print("Request distribution with weighted round robin:")
for i in range(20):
    server = balancer.get_server()
    print(f"Request {i+1:2d} -> {server}")

# Print statistics
stats = balancer.get_stats()
print("\nDistribution Statistics:")
for server, data in stats['servers'].items():
    print(f"{server}: {data['requests']} requests ({data['percentage']:.1f}%)")
```

### Least Connections Algorithm

```python
import threading
import time
from typing import Dict, Optional

class LeastConnectionsBalancer:
    """Least connections load balancer with connection tracking"""

    def __init__(self, servers: List[str]):
        self.servers = {}
        self.lock = threading.Lock()

        for server in servers:
            self.servers[server] = {
                'active_connections': 0,
                'total_connections': 0,
                'last_assigned': 0,
                'response_time_ms': 0,  # Average response time
                'health_status': 'healthy'
            }

    def get_server(self) -> Optional[str]:
        """Get server with least active connections"""
        with self.lock:
            healthy_servers = {
                server: data for server, data in self.servers.items()
                if data['health_status'] == 'healthy'
            }

            if not healthy_servers:
                return None

            # Find server with minimum connections
            # Break ties by choosing server with earliest last assignment
            min_connections = min(s['active_connections'] for s in healthy_servers.values())
            candidates = [
                server for server, data in healthy_servers.items()
                if data['active_connections'] == min_connections
            ]

            # If multiple servers have same connection count, use round-robin
            best_server = min(candidates,
                            key=lambda s: healthy_servers[s]['last_assigned'])

            # Update connection count and assignment time
            self.servers[best_server]['active_connections'] += 1
            self.servers[best_server]['total_connections'] += 1
            self.servers[best_server]['last_assigned'] = time.time()

            return best_server

    def release_connection(self, server: str, response_time_ms: float = 0):
        """Release connection and update response time"""
        with self.lock:
            if server in self.servers:
                self.servers[server]['active_connections'] = max(0,
                    self.servers[server]['active_connections'] - 1)

                # Update rolling average response time
                if response_time_ms > 0:
                    current_avg = self.servers[server]['response_time_ms']
                    self.servers[server]['response_time_ms'] = (
                        current_avg * 0.9 + response_time_ms * 0.1
                    )

    def mark_server_unhealthy(self, server: str):
        """Mark server as unhealthy"""
        with self.lock:
            if server in self.servers:
                self.servers[server]['health_status'] = 'unhealthy'

    def mark_server_healthy(self, server: str):
        """Mark server as healthy"""
        with self.lock:
            if server in self.servers:
                self.servers[server]['health_status'] = 'healthy'

    def get_server_stats(self) -> Dict:
        """Get detailed server statistics"""
        with self.lock:
            return {
                server: {
                    'active_connections': data['active_connections'],
                    'total_connections': data['total_connections'],
                    'avg_response_time_ms': round(data['response_time_ms'], 2),
                    'health_status': data['health_status'],
                    'utilization': data['active_connections']  # Can be enhanced with capacity
                }
                for server, data in self.servers.items()
            }

# Example usage with connection simulation
import asyncio
import aiohttp
import random

class ConnectionSimulator:
    """Simulate realistic connection patterns"""

    def __init__(self, balancer: LeastConnectionsBalancer):
        self.balancer = balancer

    async def simulate_request(self, request_id: int):
        """Simulate a request with realistic timing"""
        server = self.balancer.get_server()
        if not server:
            print(f"Request {request_id}: No healthy servers available")
            return

        start_time = time.time()
        print(f"Request {request_id} -> {server} (connections: {self.balancer.servers[server]['active_connections']})")

        # Simulate request processing time (50ms to 500ms)
        processing_time = random.uniform(0.05, 0.5)
        await asyncio.sleep(processing_time)

        # Calculate response time
        response_time_ms = (time.time() - start_time) * 1000

        # Release connection
        self.balancer.release_connection(server, response_time_ms)
        print(f"Request {request_id} completed in {response_time_ms:.1f}ms")

    async def run_simulation(self, num_requests: int, concurrency: int):
        """Run concurrent request simulation"""
        semaphore = asyncio.Semaphore(concurrency)

        async def bounded_request(request_id):
            async with semaphore:
                await self.simulate_request(request_id)

        # Create and run concurrent tasks
        tasks = [bounded_request(i) for i in range(num_requests)]
        await asyncio.gather(*tasks)

        # Print final statistics
        print("\nFinal Server Statistics:")
        stats = self.balancer.get_server_stats()
        for server, data in stats.items():
            print(f"{server}: {data['active_connections']} active, "
                  f"{data['total_connections']} total, "
                  f"{data['avg_response_time_ms']}ms avg")

# Run simulation
if __name__ == "__main__":
    servers = ['app-01.prod.com', 'app-02.prod.com', 'app-03.prod.com']
    balancer = LeastConnectionsBalancer(servers)
    simulator = ConnectionSimulator(balancer)

    # Run 50 requests with max 10 concurrent
    asyncio.run(simulator.run_simulation(50, 10))
```

## Advanced Algorithm: Consistent Hashing

```python
import hashlib
import bisect
from typing import List, Dict, Optional

class ConsistentHashBalancer:
    """Consistent hashing load balancer for session affinity"""

    def __init__(self, servers: List[str], virtual_nodes: int = 150):
        self.servers = set(servers)
        self.virtual_nodes = virtual_nodes
        self.ring: Dict[int, str] = {}
        self.sorted_keys: List[int] = []
        self._build_ring()

    def _hash(self, key: str) -> int:
        """Hash function for consistent hashing"""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def _build_ring(self):
        """Build the consistent hash ring"""
        self.ring.clear()

        for server in self.servers:
            for i in range(self.virtual_nodes):
                virtual_key = f"{server}:{i}"
                hash_value = self._hash(virtual_key)
                self.ring[hash_value] = server

        self.sorted_keys = sorted(self.ring.keys())

    def get_server(self, key: str) -> Optional[str]:
        """Get server for a given key using consistent hashing"""
        if not self.ring:
            return None

        hash_value = self._hash(key)

        # Find the first server clockwise on the ring
        idx = bisect.bisect_right(self.sorted_keys, hash_value)
        if idx == len(self.sorted_keys):
            idx = 0  # Wrap around

        return self.ring[self.sorted_keys[idx]]

    def add_server(self, server: str):
        """Add server to the ring"""
        if server not in self.servers:
            self.servers.add(server)
            self._build_ring()

    def remove_server(self, server: str):
        """Remove server from the ring"""
        if server in self.servers:
            self.servers.remove(server)
            self._build_ring()

    def get_key_distribution(self, keys: List[str]) -> Dict[str, int]:
        """Analyze key distribution across servers"""
        distribution = {server: 0 for server in self.servers}

        for key in keys:
            server = self.get_server(key)
            if server:
                distribution[server] += 1

        return distribution

# Example: Session affinity for user sessions
user_sessions = [f"user:{i}" for i in range(1000)]
balancer = ConsistentHashBalancer(['web-01', 'web-02', 'web-03', 'web-04'])

# Test key distribution
distribution = balancer.get_key_distribution(user_sessions)
total_keys = sum(distribution.values())

print("Session Distribution:")
for server, count in distribution.items():
    percentage = (count / total_keys) * 100
    print(f"{server}: {count} sessions ({percentage:.1f}%)")

# Test adding a new server
print("\nAdding new server 'web-05'...")
balancer.add_server('web-05')
new_distribution = balancer.get_key_distribution(user_sessions)

print("New Session Distribution:")
for server, count in new_distribution.items():
    percentage = (count / total_keys) * 100
    print(f"{server}: {count} sessions ({percentage:.1f}%)")

# Calculate session migration
migrations = 0
for session in user_sessions:
    old_server = ConsistentHashBalancer(['web-01', 'web-02', 'web-03', 'web-04']).get_server(session)
    new_server = balancer.get_server(session)
    if old_server != new_server:
        migrations += 1

print(f"\nSessions migrated: {migrations} ({migrations/total_keys*100:.1f}%)")
```

## Algorithm Decision Matrix

```mermaid
graph TB
    subgraph Decision[Algorithm Selection Decision Tree]
        START[Incoming Request] --> SESSION{Session Affinity Required?}

        SESSION -->|Yes| HASH[IP Hash / Consistent Hash]
        SESSION -->|No| CAPACITY{Servers Different Capacity?}

        CAPACITY -->|Yes| WEIGHTED[Weighted Round Robin]
        CAPACITY -->|No| CONNECTIONS{Connection-based?}

        CONNECTIONS -->|Yes| LEAST[Least Connections]
        CONNECTIONS -->|No| SIMPLE{Simple Distribution?}

        SIMPLE -->|Yes| ROBIN[Round Robin]
        SIMPLE -->|No| RANDOM[Random]

        HASH --> RESULT1[User always goes to same server]
        WEIGHTED --> RESULT2[Higher capacity servers get more traffic]
        LEAST --> RESULT3[Distribute based on current load]
        ROBIN --> RESULT4[Equal distribution across servers]
        RANDOM --> RESULT5[Random distribution]
    end

    %% Styling
    classDef decision fill:#FFE4B5,stroke:#DEB887,color:#000
    classDef algorithm fill:#90EE90,stroke:#006400,color:#000
    classDef result fill:#E6E6FA,stroke:#9370DB,color:#000

    class SESSION,CAPACITY,CONNECTIONS,SIMPLE decision
    class HASH,WEIGHTED,LEAST,ROBIN,RANDOM algorithm
    class RESULT1,RESULT2,RESULT3,RESULT4,RESULT5 result
```

## Production Configuration Examples

### nginx Load Balancer Configuration

```nginx
# nginx.conf - Production load balancer configuration
upstream backend_pool {
    # Least connections algorithm
    least_conn;

    # Server definitions with weights and health checks
    server 10.0.1.10:8080 weight=5 max_fails=3 fail_timeout=30s;
    server 10.0.1.11:8080 weight=3 max_fails=3 fail_timeout=30s;
    server 10.0.1.12:8080 weight=2 max_fails=3 fail_timeout=30s;
    server 10.0.1.13:8080 weight=1 max_fails=3 fail_timeout=30s backup;

    # Connection pooling
    keepalive 32;
    keepalive_requests 1000;
    keepalive_timeout 60s;
}

# Session affinity upstream (IP hash)
upstream session_backend {
    ip_hash;

    server 10.0.1.20:8080 max_fails=2 fail_timeout=10s;
    server 10.0.1.21:8080 max_fails=2 fail_timeout=10s;
    server 10.0.1.22:8080 max_fails=2 fail_timeout=10s;
}

server {
    listen 80;
    server_name api.company.com;

    # API endpoints (stateless - least connections)
    location /api/ {
        proxy_pass http://backend_pool;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Connection and timeout settings
        proxy_connect_timeout 5s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504;
        proxy_next_upstream_tries 3;
        proxy_next_upstream_timeout 10s;

        # Health check headers
        add_header X-Upstream-Server $upstream_addr always;
        add_header X-Response-Time $upstream_response_time always;
    }

    # Session endpoints (stateful - IP hash)
    location /auth/ {
        proxy_pass http://session_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Health check endpoint
    location /nginx-health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}

# Status page for monitoring
server {
    listen 8080;
    server_name localhost;

    location /nginx_status {
        stub_status on;
        access_log off;
        allow 127.0.0.1;
        allow 10.0.0.0/8;
        deny all;
    }

    location /upstream_status {
        upstream_status;
        access_log off;
        allow 127.0.0.1;
        allow 10.0.0.0/8;
        deny all;
    }
}
```

### HAProxy Configuration

```
# haproxy.cfg - Production configuration with multiple algorithms
global
    daemon
    chroot /var/lib/haproxy
    stats socket /run/haproxy/admin.sock mode 660 level admin
    stats timeout 30s
    user haproxy
    group haproxy

    # SSL configuration
    ssl-default-bind-ciphers ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!SHA1:!AESCCM
    ssl-default-bind-options ssl-min-ver TLSv1.2 no-tls-tickets

defaults
    mode http
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms
    option httplog
    option dontlognull
    option redispatch
    retries 3

    # Health checks
    option httpchk GET /health
    http-check expect status 200

# Frontend for web traffic
frontend web_frontend
    bind *:80
    bind *:443 ssl crt /etc/ssl/certs/company.pem

    # Redirect HTTP to HTTPS
    redirect scheme https if !{ ssl_fc }

    # Route based on path
    acl is_api path_beg /api/
    acl is_auth path_beg /auth/
    acl is_static path_beg /static/

    use_backend api_backend if is_api
    use_backend auth_backend if is_auth
    use_backend static_backend if is_static
    default_backend web_backend

# API backend - round robin with health checks
backend api_backend
    balance roundrobin
    option httpchk GET /api/health

    server api-01 10.0.1.10:8080 check weight 10 maxconn 1000
    server api-02 10.0.1.11:8080 check weight 8 maxconn 800
    server api-03 10.0.1.12:8080 check weight 6 maxconn 600
    server api-04 10.0.1.13:8080 check weight 4 maxconn 400 backup

# Authentication backend - source IP hash for session affinity
backend auth_backend
    balance source
    hash-type consistent
    option httpchk GET /auth/health

    server auth-01 10.0.1.20:8080 check maxconn 500
    server auth-02 10.0.1.21:8080 check maxconn 500
    server auth-03 10.0.1.22:8080 check maxconn 500

# Static content backend - least connections
backend static_backend
    balance leastconn
    option httpchk GET /static/health.txt

    server static-01 10.0.1.30:8080 check weight 10
    server static-02 10.0.1.31:8080 check weight 10
    server static-03 10.0.1.32:8080 check weight 10

# Main web backend - weighted round robin
backend web_backend
    balance roundrobin
    option httpchk GET /health

    # High-performance servers
    server web-01 10.0.1.40:8080 check weight 15 maxconn 2000
    server web-02 10.0.1.41:8080 check weight 15 maxconn 2000

    # Medium-performance servers
    server web-03 10.0.1.42:8080 check weight 10 maxconn 1500
    server web-04 10.0.1.43:8080 check weight 10 maxconn 1500

    # Backup server
    server web-05 10.0.1.44:8080 check weight 5 maxconn 1000 backup

# Statistics page
listen stats
    bind *:8404
    stats enable
    stats uri /stats
    stats refresh 30s
    stats admin if TRUE
    stats auth admin:secure_password_here
```

## Performance Benchmarking

### Algorithm Performance Comparison

```python
import time
import threading
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

class LoadBalancerBenchmark:
    """Benchmark different load balancing algorithms"""

    def __init__(self):
        self.servers = ['server-01', 'server-02', 'server-03', 'server-04']
        self.results = {}

    def benchmark_algorithm(self, algorithm_class, algorithm_name: str,
                          num_requests: int, num_threads: int):
        """Benchmark a specific algorithm"""
        print(f"Benchmarking {algorithm_name}...")

        # Initialize algorithm
        if algorithm_name == "WeightedRoundRobin":
            balancer = algorithm_class([
                (server, random.randint(1, 5)) for server in self.servers
            ])
        else:
            balancer = algorithm_class(self.servers)

        # Benchmark metrics
        start_time = time.time()
        request_times = []
        server_counts = {server: 0 for server in self.servers}

        def make_request(request_id):
            """Simulate a single request"""
            req_start = time.time()

            if algorithm_name == "ConsistentHash":
                server = balancer.get_server(f"user:{request_id}")
            else:
                server = balancer.get_server()

            # Simulate processing time
            time.sleep(random.uniform(0.001, 0.005))

            req_end = time.time()
            return server, req_end - req_start

        # Execute requests concurrently
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(make_request, i) for i in range(num_requests)]

            for future in as_completed(futures):
                server, req_time = future.result()
                request_times.append(req_time)
                server_counts[server] += 1

        total_time = time.time() - start_time

        # Calculate metrics
        avg_request_time = sum(request_times) / len(request_times)
        requests_per_second = num_requests / total_time

        # Calculate distribution fairness (coefficient of variation)
        counts = list(server_counts.values())
        mean_count = sum(counts) / len(counts)
        variance = sum((x - mean_count) ** 2 for x in counts) / len(counts)
        std_dev = variance ** 0.5
        cv = (std_dev / mean_count) * 100 if mean_count > 0 else 0

        self.results[algorithm_name] = {
            'total_time': total_time,
            'avg_request_time_ms': avg_request_time * 1000,
            'requests_per_second': requests_per_second,
            'distribution': server_counts,
            'fairness_cv': cv  # Lower is more fair
        }

    def run_benchmarks(self, num_requests: int = 10000, num_threads: int = 50):
        """Run benchmarks for all algorithms"""
        algorithms = [
            (RoundRobinBalancer, "RoundRobin"),
            (WeightedRoundRobinBalancer, "WeightedRoundRobin"),
            (LeastConnectionsBalancer, "LeastConnections"),
            (ConsistentHashBalancer, "ConsistentHash")
        ]

        for algorithm_class, algorithm_name in algorithms:
            try:
                self.benchmark_algorithm(algorithm_class, algorithm_name,
                                       num_requests, num_threads)
            except Exception as e:
                print(f"Error benchmarking {algorithm_name}: {e}")

        self.print_results()

    def print_results(self):
        """Print benchmark results"""
        print("\n" + "="*80)
        print("LOAD BALANCING ALGORITHM BENCHMARK RESULTS")
        print("="*80)

        for algorithm, results in self.results.items():
            print(f"\n{algorithm}:")
            print(f"  Total Time: {results['total_time']:.2f}s")
            print(f"  Avg Request Time: {results['avg_request_time_ms']:.2f}ms")
            print(f"  Requests/Second: {results['requests_per_second']:.1f}")
            print(f"  Distribution Fairness CV: {results['fairness_cv']:.1f}%")
            print(f"  Server Distribution:")
            for server, count in results['distribution'].items():
                percentage = (count / sum(results['distribution'].values())) * 100
                print(f"    {server}: {count} ({percentage:.1f}%)")

if __name__ == "__main__":
    benchmark = LoadBalancerBenchmark()
    benchmark.run_benchmarks(num_requests=5000, num_threads=25)
```

## Real-World Algorithm Selection

### Netflix: Weighted Round Robin
- **Challenge**: Different EC2 instance types with varying capacity
- **Solution**: Dynamic weights based on instance CPU/memory capacity
- **Result**: 30% better resource utilization

### Google: Consistent Hashing
- **Challenge**: Minimize request migration during server changes
- **Solution**: Consistent hashing with virtual nodes
- **Result**: <5% of requests need migration when adding/removing servers

### Facebook: Least Connections + Geography
- **Challenge**: Global user base with varying connection patterns
- **Solution**: Least connections within geographic regions
- **Result**: 40% reduction in average response times

This comprehensive guide provides production-ready implementations of load balancing algorithms with real performance characteristics and configuration examples used in high-scale deployments.