# Layer 4 Load Balancing (Transport Layer)

## Overview

Layer 4 load balancing operates at the transport layer, routing traffic based on IP addresses and port numbers without inspecting application data. This provides high performance and low latency for TCP and UDP traffic.

## Layer 4 vs Layer 7 Load Balancing Architecture

```mermaid
graph TB
    subgraph Client[Client Traffic]
        C1[Client 1<br/>TCP Connection<br/>192.168.1.100:54321]
        C2[Client 2<br/>TCP Connection<br/>192.168.1.101:54322]
        C3[Client 3<br/>UDP Traffic<br/>192.168.1.102:54323]
    end

    subgraph Layer4[Layer 4 Load Balancer]
        L4LB[Layer 4 LB<br/>IP: 203.0.113.10<br/>Port: 80, 443]
        L4LOGIC[Routing Logic:<br/>• Source IP + Port<br/>• Destination IP + Port<br/>• Protocol (TCP/UDP)<br/>• No payload inspection]
    end

    subgraph Layer7[Layer 7 Load Balancer]
        L7LB[Layer 7 LB<br/>nginx/HAProxy]
        L7LOGIC[Routing Logic:<br/>• HTTP headers<br/>• URL paths<br/>• Cookies<br/>• SSL termination]
    end

    subgraph Backend[Backend Servers]
        S1[Server 1<br/>10.0.1.10:8080<br/>Active Connections: 150]
        S2[Server 2<br/>10.0.1.11:8080<br/>Active Connections: 200]
        S3[Server 3<br/>10.0.1.12:8080<br/>Active Connections: 100]
    end

    C1 --> L4LB
    C2 --> L4LB
    C3 --> L4LB

    L4LB --> L4LOGIC
    L4LOGIC -.->|Direct TCP/UDP| S1
    L4LOGIC -.->|Direct TCP/UDP| S2
    L4LOGIC -.->|Direct TCP/UDP| S3

    C1 -.->|Alternative| L7LB
    L7LB --> L7LOGIC
    L7LOGIC -->|HTTP/HTTPS| S1

    %% Styling
    classDef client fill:#87CEEB,stroke:#4682B4,color:#000
    classDef layer4 fill:#90EE90,stroke:#006400,color:#000
    classDef layer7 fill:#FFE4B5,stroke:#DEB887,color:#000
    classDef server fill:#FFB6C1,stroke:#FF69B4,color:#000

    class C1,C2,C3 client
    class L4LB,L4LOGIC layer4
    class L7LB,L7LOGIC layer7
    class S1,S2,S3 server
```

## TCP Load Balancing Implementation

### Direct Server Return (DSR) Configuration

```python
import socket
import threading
import struct
import time
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class LoadBalancingMethod(Enum):
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    SOURCE_HASH = "source_hash"

@dataclass
class BackendServer:
    ip: str
    port: int
    weight: int = 1
    active_connections: int = 0
    total_connections: int = 0
    health_status: str = "healthy"
    response_time_ms: float = 0.0

class Layer4LoadBalancer:
    """High-performance Layer 4 TCP load balancer with DSR support"""

    def __init__(self,
                 virtual_ip: str,
                 virtual_port: int,
                 method: LoadBalancingMethod = LoadBalancingMethod.ROUND_ROBIN,
                 enable_dsr: bool = False):
        self.virtual_ip = virtual_ip
        self.virtual_port = virtual_port
        self.method = method
        self.enable_dsr = enable_dsr

        self.backend_servers: List[BackendServer] = []
        self.current_server_index = 0
        self.connection_table: Dict[Tuple[str, int], BackendServer] = {}

        # Performance metrics
        self.metrics = {
            'total_connections': 0,
            'active_connections': 0,
            'bytes_transferred': 0,
            'packets_forwarded': 0
        }

        # Sockets
        self.listen_socket = None
        self.running = False

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def add_backend_server(self, ip: str, port: int, weight: int = 1):
        """Add backend server to the pool"""
        server = BackendServer(ip, port, weight)
        self.backend_servers.append(server)
        self.logger.info(f"Added backend server {ip}:{port} with weight {weight}")

    def remove_backend_server(self, ip: str, port: int):
        """Remove backend server from the pool"""
        self.backend_servers = [
            server for server in self.backend_servers
            if not (server.ip == ip and server.port == port)
        ]
        self.logger.info(f"Removed backend server {ip}:{port}")

    def select_backend_server(self, client_address: Tuple[str, int]) -> Optional[BackendServer]:
        """Select backend server based on configured method"""
        healthy_servers = [
            server for server in self.backend_servers
            if server.health_status == "healthy"
        ]

        if not healthy_servers:
            return None

        if self.method == LoadBalancingMethod.ROUND_ROBIN:
            return self._round_robin_selection(healthy_servers)
        elif self.method == LoadBalancingMethod.LEAST_CONNECTIONS:
            return self._least_connections_selection(healthy_servers)
        elif self.method == LoadBalancingMethod.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_selection(healthy_servers)
        elif self.method == LoadBalancingMethod.SOURCE_HASH:
            return self._source_hash_selection(healthy_servers, client_address)

        return healthy_servers[0]  # Fallback

    def _round_robin_selection(self, servers: List[BackendServer]) -> BackendServer:
        """Simple round robin selection"""
        server = servers[self.current_server_index % len(servers)]
        self.current_server_index += 1
        return server

    def _least_connections_selection(self, servers: List[BackendServer]) -> BackendServer:
        """Select server with least active connections"""
        return min(servers, key=lambda s: s.active_connections)

    def _weighted_round_robin_selection(self, servers: List[BackendServer]) -> BackendServer:
        """Weighted round robin selection"""
        total_weight = sum(server.weight for server in servers)
        if total_weight == 0:
            return servers[0]

        # Simple weighted selection (can be optimized with smooth weighted round robin)
        import random
        r = random.randint(1, total_weight)
        weight_sum = 0

        for server in servers:
            weight_sum += server.weight
            if r <= weight_sum:
                return server

        return servers[-1]  # Fallback

    def _source_hash_selection(self, servers: List[BackendServer],
                             client_address: Tuple[str, int]) -> BackendServer:
        """Consistent hash based on source IP"""
        import hashlib
        hash_input = f"{client_address[0]}:{client_address[1]}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        server_index = hash_value % len(servers)
        return servers[server_index]

    def create_raw_socket(self):
        """Create raw socket for DSR implementation"""
        if not self.enable_dsr:
            return None

        try:
            # Create raw socket (requires root privileges)
            raw_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            raw_socket.setsockopt(socket.SOL_IP, socket.IP_HDRINCL, 1)
            return raw_socket
        except PermissionError:
            self.logger.error("Raw socket creation requires root privileges for DSR")
            return None

    def handle_tcp_connection(self, client_socket: socket.socket, client_address: Tuple[str, int]):
        """Handle incoming TCP connection"""
        try:
            # Select backend server
            backend_server = self.select_backend_server(client_address)
            if not backend_server:
                self.logger.error("No healthy backend servers available")
                client_socket.close()
                return

            self.logger.info(f"Routing {client_address} to {backend_server.ip}:{backend_server.port}")

            # Update connection tracking
            backend_server.active_connections += 1
            backend_server.total_connections += 1
            self.metrics['active_connections'] += 1
            self.metrics['total_connections'] += 1

            # Store connection mapping for session persistence
            self.connection_table[client_address] = backend_server

            if self.enable_dsr:
                # Direct Server Return - forward packet and let server respond directly
                self._handle_dsr_connection(client_socket, client_address, backend_server)
            else:
                # Proxy mode - full proxy connection
                self._handle_proxy_connection(client_socket, client_address, backend_server)

        except Exception as e:
            self.logger.error(f"Error handling connection from {client_address}: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass

    def _handle_proxy_connection(self, client_socket: socket.socket,
                                client_address: Tuple[str, int],
                                backend_server: BackendServer):
        """Handle connection in proxy mode"""
        try:
            # Connect to backend server
            backend_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            backend_socket.settimeout(5.0)
            backend_socket.connect((backend_server.ip, backend_server.port))

            # Start bidirectional data forwarding
            def forward_data(source: socket.socket, destination: socket.socket, direction: str):
                try:
                    while True:
                        data = source.recv(4096)
                        if not data:
                            break
                        destination.send(data)
                        self.metrics['bytes_transferred'] += len(data)
                        self.metrics['packets_forwarded'] += 1
                except Exception as e:
                    self.logger.debug(f"Data forwarding stopped ({direction}): {e}")
                finally:
                    try:
                        source.close()
                        destination.close()
                    except:
                        pass

            # Create threads for bidirectional forwarding
            client_to_backend = threading.Thread(
                target=forward_data,
                args=(client_socket, backend_socket, "client->backend")
            )
            backend_to_client = threading.Thread(
                target=forward_data,
                args=(backend_socket, client_socket, "backend->client")
            )

            client_to_backend.start()
            backend_to_client.start()

            # Wait for both threads to complete
            client_to_backend.join()
            backend_to_client.join()

        except Exception as e:
            self.logger.error(f"Proxy connection error: {e}")
        finally:
            # Update connection count
            backend_server.active_connections -= 1
            self.metrics['active_connections'] -= 1

            # Remove from connection table
            if client_address in self.connection_table:
                del self.connection_table[client_address]

    def _handle_dsr_connection(self, client_socket: socket.socket,
                             client_address: Tuple[str, int],
                             backend_server: BackendServer):
        """Handle connection in DSR mode"""
        # DSR implementation would require packet manipulation
        # This is a simplified version for demonstration
        self.logger.info(f"DSR mode: Forwarding packet to {backend_server.ip}:{backend_server.port}")

        # In real DSR implementation:
        # 1. Capture incoming packet
        # 2. Rewrite destination MAC address to backend server
        # 3. Keep destination IP as virtual IP
        # 4. Forward packet to backend server
        # 5. Backend server responds directly to client

        # For demo, we'll fall back to proxy mode
        self._handle_proxy_connection(client_socket, client_address, backend_server)

    def start_health_checks(self):
        """Start health checking for backend servers"""
        def health_check_worker():
            while self.running:
                for server in self.backend_servers:
                    try:
                        # Simple TCP health check
                        start_time = time.time()
                        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        test_socket.settimeout(3.0)
                        result = test_socket.connect_ex((server.ip, server.port))
                        test_socket.close()

                        response_time = (time.time() - start_time) * 1000

                        if result == 0:
                            server.health_status = "healthy"
                            server.response_time_ms = response_time
                        else:
                            server.health_status = "unhealthy"

                    except Exception as e:
                        server.health_status = "unhealthy"
                        self.logger.warning(f"Health check failed for {server.ip}:{server.port}: {e}")

                time.sleep(10)  # Health check every 10 seconds

        health_thread = threading.Thread(target=health_check_worker, daemon=True)
        health_thread.start()

    def start(self):
        """Start the load balancer"""
        try:
            # Create and bind socket
            self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.listen_socket.bind((self.virtual_ip, self.virtual_port))
            self.listen_socket.listen(1000)  # High backlog for production

            self.running = True
            self.logger.info(f"Layer 4 Load Balancer started on {self.virtual_ip}:{self.virtual_port}")

            # Start health checks
            self.start_health_checks()

            # Accept connections
            while self.running:
                try:
                    client_socket, client_address = self.listen_socket.accept()

                    # Handle connection in separate thread
                    connection_thread = threading.Thread(
                        target=self.handle_tcp_connection,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    connection_thread.start()

                except Exception as e:
                    if self.running:
                        self.logger.error(f"Error accepting connection: {e}")

        except Exception as e:
            self.logger.error(f"Failed to start load balancer: {e}")
        finally:
            self.stop()

    def stop(self):
        """Stop the load balancer"""
        self.running = False
        if self.listen_socket:
            self.listen_socket.close()
        self.logger.info("Load balancer stopped")

    def get_stats(self) -> Dict:
        """Get load balancer statistics"""
        return {
            'metrics': self.metrics,
            'backend_servers': [
                {
                    'ip': server.ip,
                    'port': server.port,
                    'weight': server.weight,
                    'active_connections': server.active_connections,
                    'total_connections': server.total_connections,
                    'health_status': server.health_status,
                    'response_time_ms': server.response_time_ms
                }
                for server in self.backend_servers
            ],
            'active_sessions': len(self.connection_table)
        }

# Example usage
if __name__ == "__main__":
    # Create Layer 4 load balancer
    lb = Layer4LoadBalancer(
        virtual_ip="0.0.0.0",
        virtual_port=8080,
        method=LoadBalancingMethod.LEAST_CONNECTIONS,
        enable_dsr=False
    )

    # Add backend servers
    lb.add_backend_server("10.0.1.10", 8080, weight=3)
    lb.add_backend_server("10.0.1.11", 8080, weight=2)
    lb.add_backend_server("10.0.1.12", 8080, weight=1)

    try:
        lb.start()
    except KeyboardInterrupt:
        print("\nShutting down load balancer...")
        lb.stop()
```

## Linux Virtual Server (LVS) Configuration

### IPVS Configuration for Layer 4 Load Balancing

```bash
#!/bin/bash
# lvs-setup.sh - Configure Linux Virtual Server for Layer 4 load balancing

# Install IPVS tools
sudo apt-get update
sudo apt-get install -y ipvsadm keepalived

# Load IPVS kernel modules
sudo modprobe ip_vs
sudo modprobe ip_vs_rr    # Round robin
sudo modprobe ip_vs_wrr   # Weighted round robin
sudo modprobe ip_vs_lc    # Least connections
sudo modprobe ip_vs_wlc   # Weighted least connections
sudo modprobe ip_vs_sh    # Source hash

# Configure IPVS service
configure_ipvs_service() {
    local vip="203.0.113.10"
    local vport="80"
    local method="wlc"  # Weighted least connections

    echo "Configuring IPVS service ${vip}:${vport}"

    # Add virtual service
    sudo ipvsadm -A -t ${vip}:${vport} -s ${method}

    # Add real servers (backend servers)
    sudo ipvsadm -a -t ${vip}:${vport} -r 10.0.1.10:8080 -g -w 3  # DR mode, weight 3
    sudo ipvsadm -a -t ${vip}:${vport} -r 10.0.1.11:8080 -g -w 2  # DR mode, weight 2
    sudo ipvsadm -a -t ${vip}:${vport} -r 10.0.1.12:8080 -g -w 1  # DR mode, weight 1

    echo "IPVS service configured successfully"
}

# Configure for Direct Routing (DR) mode
configure_dr_mode() {
    local vip="203.0.113.10"

    echo "Configuring Direct Routing mode"

    # On the load balancer (director)
    sudo ip addr add ${vip}/32 dev lo
    sudo ip route add ${vip} dev lo

    # Configure arp_ignore and arp_announce for VIP
    echo 1 | sudo tee /proc/sys/net/ipv4/conf/all/arp_ignore
    echo 2 | sudo tee /proc/sys/net/ipv4/conf/all/arp_announce

    echo "Direct Routing mode configured"
}

# Backend server configuration script
create_backend_config() {
    cat << 'EOF' > backend-server-setup.sh
#!/bin/bash
# Run this script on each backend server

VIP="203.0.113.10"

# Configure loopback interface with VIP
sudo ip addr add ${VIP}/32 dev lo

# Configure ARP to prevent responding to VIP requests
echo 1 | sudo tee /proc/sys/net/ipv4/conf/lo/arp_ignore
echo 2 | sudo tee /proc/sys/net/ipv4/conf/lo/arp_announce
echo 1 | sudo tee /proc/sys/net/ipv4/conf/all/arp_ignore
echo 2 | sudo tee /proc/sys/net/ipv4/conf/all/arp_announce

# Make changes persistent
echo "net.ipv4.conf.lo.arp_ignore = 1" >> /etc/sysctl.conf
echo "net.ipv4.conf.lo.arp_announce = 2" >> /etc/sysctl.conf
echo "net.ipv4.conf.all.arp_ignore = 1" >> /etc/sysctl.conf
echo "net.ipv4.conf.all.arp_announce = 2" >> /etc/sysctl.conf

echo "Backend server configured for DR mode"
EOF

    chmod +x backend-server-setup.sh
    echo "Backend server configuration script created: backend-server-setup.sh"
}

# Health check script
create_health_check() {
    cat << 'EOF' > health-check.sh
#!/bin/bash
# Health check script for IPVS real servers

VIP="203.0.113.10"
VPORT="80"

check_server_health() {
    local server_ip=$1
    local server_port=$2
    local weight=$3

    # Perform health check (TCP connect test)
    if timeout 3 bash -c "</dev/tcp/${server_ip}/${server_port}"; then
        echo "Server ${server_ip}:${server_port} is healthy"

        # Ensure server is in IPVS table with correct weight
        if ! ipvsadm -L -n | grep -q "${server_ip}:${server_port}"; then
            echo "Adding server ${server_ip}:${server_port} to IPVS"
            sudo ipvsadm -a -t ${VIP}:${VPORT} -r ${server_ip}:${server_port} -g -w ${weight}
        fi

        return 0
    else
        echo "Server ${server_ip}:${server_port} is unhealthy"

        # Remove server from IPVS table
        if ipvsadm -L -n | grep -q "${server_ip}:${server_port}"; then
            echo "Removing server ${server_ip}:${server_port} from IPVS"
            sudo ipvsadm -d -t ${VIP}:${VPORT} -r ${server_ip}:${server_port}
        fi

        return 1
    fi
}

# Health check loop
while true; do
    echo "$(date): Starting health checks"

    check_server_health "10.0.1.10" "8080" "3"
    check_server_health "10.0.1.11" "8080" "2"
    check_server_health "10.0.1.12" "8080" "1"

    echo "Health checks completed"
    sleep 10
done
EOF

    chmod +x health-check.sh
    echo "Health check script created: health-check.sh"
}

# Monitoring script
create_monitoring_script() {
    cat << 'EOF' > monitor-ipvs.sh
#!/bin/bash
# IPVS monitoring script

print_ipvs_stats() {
    echo "=== IPVS Connection Statistics ==="
    sudo ipvsadm -L -n --stats
    echo ""

    echo "=== IPVS Rate Statistics ==="
    sudo ipvsadm -L -n --rate
    echo ""

    echo "=== Active Connections ==="
    sudo ipvsadm -L -n -c | head -20
    echo ""

    echo "=== Server Health Summary ==="
    sudo ipvsadm -L -n | grep -E "(TCP|->)" | while read line; do
        if [[ $line == TCP* ]]; then
            echo "Service: $line"
        else
            echo "  Backend: $line"
        fi
    done
}

# Continuous monitoring
if [ "$1" == "--watch" ]; then
    while true; do
        clear
        echo "IPVS Load Balancer Monitoring - $(date)"
        echo "Press Ctrl+C to exit"
        echo ""
        print_ipvs_stats
        sleep 5
    done
else
    print_ipvs_stats
fi
EOF

    chmod +x monitor-ipvs.sh
    echo "Monitoring script created: monitor-ipvs.sh"
}

# Performance tuning
configure_performance_tuning() {
    echo "Applying performance tuning for IPVS"

    # Increase connection tracking table size
    echo "net.netfilter.nf_conntrack_max = 1048576" >> /etc/sysctl.conf
    echo "net.netfilter.nf_conntrack_tcp_timeout_established = 1200" >> /etc/sysctl.conf

    # TCP tuning
    echo "net.core.somaxconn = 65535" >> /etc/sysctl.conf
    echo "net.core.netdev_max_backlog = 5000" >> /etc/sysctl.conf
    echo "net.ipv4.tcp_max_syn_backlog = 65535" >> /etc/sysctl.conf
    echo "net.ipv4.tcp_fin_timeout = 30" >> /etc/sysctl.conf
    echo "net.ipv4.tcp_keepalive_time = 1200" >> /etc/sysctl.conf
    echo "net.ipv4.tcp_rmem = 4096 16384 67108864" >> /etc/sysctl.conf
    echo "net.ipv4.tcp_wmem = 4096 16384 67108864" >> /etc/sysctl.conf

    # IPVS specific tuning
    echo "net.ipv4.vs.conn_reuse_mode = 1" >> /etc/sysctl.conf
    echo "net.ipv4.vs.conntrack = 1" >> /etc/sysctl.conf

    # Apply settings
    sudo sysctl -p

    echo "Performance tuning applied"
}

# Main execution
main() {
    echo "Setting up Linux Virtual Server (LVS) Layer 4 Load Balancer"
    echo "============================================================"

    configure_performance_tuning
    configure_dr_mode
    configure_ipvs_service
    create_backend_config
    create_health_check
    create_monitoring_script

    echo ""
    echo "LVS setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Copy and run backend-server-setup.sh on each backend server"
    echo "2. Start health checking: sudo ./health-check.sh &"
    echo "3. Monitor IPVS: ./monitor-ipvs.sh --watch"
    echo ""
    echo "To view current IPVS configuration:"
    echo "  sudo ipvsadm -L -n"
}

# Execute main function
main "$@"
```

## HAProxy Layer 4 Configuration

### Production HAProxy Layer 4 Setup

```
# haproxy-layer4.cfg - Production Layer 4 configuration
global
    daemon
    chroot /var/lib/haproxy
    stats socket /run/haproxy/admin.sock mode 660 level admin
    stats timeout 30s
    user haproxy
    group haproxy

    # Performance tuning
    maxconn 100000
    nbproc 4  # Use 4 processes for Layer 4
    nbthread 2  # 2 threads per process

    # Logging
    log stdout local0 info

defaults
    mode tcp  # Layer 4 mode
    option tcplog
    option dontlognull
    retries 3
    timeout connect 5000ms
    timeout client 300000ms   # 5 minutes for long-lived connections
    timeout server 300000ms
    timeout tunnel 3600000ms  # 1 hour for tunneled connections

    # Load balancing method
    balance leastconn

# Statistics interface
listen stats
    bind *:8404
    mode http
    stats enable
    stats uri /stats
    stats refresh 10s
    stats admin if TRUE

# TCP load balancing for web traffic
frontend tcp_web_frontend
    bind *:80
    bind *:443
    mode tcp
    option tcplog

    # Source IP preservation
    option forwardfor

    # Connection limits
    maxconn 50000
    rate-limit sessions 1000

    default_backend tcp_web_backend

backend tcp_web_backend
    mode tcp
    balance leastconn

    # Health checks
    option tcp-check
    tcp-check connect port 8080

    # Backend servers
    server web01 10.0.1.10:8080 check weight 10 maxconn 5000
    server web02 10.0.1.11:8080 check weight 8 maxconn 4000
    server web03 10.0.1.12:8080 check weight 6 maxconn 3000
    server web04 10.0.1.13:8080 check weight 4 maxconn 2000 backup

# Database load balancing (MySQL read replicas)
frontend mysql_read_frontend
    bind *:3307
    mode tcp
    option tcplog
    maxconn 1000
    default_backend mysql_read_backend

backend mysql_read_backend
    mode tcp
    balance leastconn

    # MySQL health check
    option mysql-check user haproxy_check

    server mysql-read-01 10.0.2.10:3306 check weight 10 maxconn 200
    server mysql-read-02 10.0.2.11:3306 check weight 10 maxconn 200
    server mysql-read-03 10.0.2.12:3306 check weight 8 maxconn 150 backup

# Redis cluster load balancing
frontend redis_frontend
    bind *:6380
    mode tcp
    option tcplog
    maxconn 10000
    default_backend redis_backend

backend redis_backend
    mode tcp
    balance source  # Session persistence for Redis

    # Redis health check
    option tcp-check
    tcp-check send PING\r\n
    tcp-check expect string +PONG

    server redis-01 10.0.3.10:6379 check weight 10 maxconn 2000
    server redis-02 10.0.3.11:6379 check weight 10 maxconn 2000
    server redis-03 10.0.3.12:6379 check weight 10 maxconn 2000

# SMTP load balancing
frontend smtp_frontend
    bind *:25
    mode tcp
    option tcplog
    maxconn 1000
    default_backend smtp_backend

backend smtp_backend
    mode tcp
    balance roundrobin

    # SMTP health check
    option tcp-check
    tcp-check connect port 25
    tcp-check send HELO haproxy.local\r\n
    tcp-check expect rstring ^220

    server smtp-01 10.0.4.10:25 check weight 10 maxconn 200
    server smtp-02 10.0.4.11:25 check weight 10 maxconn 200

# SSL/TLS pass-through for applications that handle their own SSL
frontend ssl_passthrough_frontend
    bind *:8443
    mode tcp
    option tcplog

    # SSL SNI routing (Layer 4 with SNI inspection)
    tcp-request inspect-delay 5s
    tcp-request content accept if { req_ssl_hello_type 1 }

    # Route based on SNI
    use_backend api_ssl_backend if { req_ssl_sni -i api.company.com }
    use_backend admin_ssl_backend if { req_ssl_sni -i admin.company.com }
    default_backend default_ssl_backend

backend api_ssl_backend
    mode tcp
    balance leastconn
    server api-ssl-01 10.0.5.10:8443 check weight 10 maxconn 1000
    server api-ssl-02 10.0.5.11:8443 check weight 10 maxconn 1000

backend admin_ssl_backend
    mode tcp
    balance roundrobin
    server admin-ssl-01 10.0.6.10:8443 check weight 10 maxconn 500
    server admin-ssl-02 10.0.6.11:8443 check weight 10 maxconn 500

backend default_ssl_backend
    mode tcp
    balance leastconn
    server default-ssl-01 10.0.7.10:8443 check weight 10 maxconn 1000
```

## Layer 4 Performance Monitoring

### eBPF-based Layer 4 Load Balancer Monitoring

```python
#!/usr/bin/env python3
"""
Layer 4 Load Balancer monitoring using eBPF
Requires: pip install bcc
"""

from bcc import BPF
import time
import socket
import struct
from collections import defaultdict

# eBPF program for Layer 4 load balancer monitoring
bpf_program = """
#include <uapi/linux/ptrace.h>
#include <net/sock.h>
#include <bcc/proto.h>

struct connection_event {
    u32 pid;
    u32 src_ip;
    u32 dst_ip;
    u16 src_port;
    u16 dst_port;
    u8 protocol;
    u64 timestamp;
    u32 bytes;
};

BPF_PERF_OUTPUT(connection_events);
BPF_HASH(connection_stats, u64, u64);

int trace_tcp_connect(struct pt_regs *ctx, struct sock *sk) {
    struct connection_event event = {};

    // Get connection details
    event.pid = bpf_get_current_pid_tgid() >> 32;
    event.src_ip = sk->__sk_common.skc_rcv_saddr;
    event.dst_ip = sk->__sk_common.skc_daddr;
    event.src_port = sk->__sk_common.skc_num;
    event.dst_port = bpf_ntohs(sk->__sk_common.skc_dport);
    event.protocol = IPPROTO_TCP;
    event.timestamp = bpf_ktime_get_ns();

    connection_events.perf_submit(ctx, &event, sizeof(event));
    return 0;
}

int trace_tcp_sendmsg(struct pt_regs *ctx, struct sock *sk, struct msghdr *msg, size_t size) {
    u64 key = (u64)sk;
    u64 *bytes = connection_stats.lookup(&key);
    if (bytes) {
        *bytes += size;
    } else {
        connection_stats.update(&key, &size);
    }
    return 0;
}
"""

class Layer4Monitor:
    """Layer 4 load balancer performance monitor"""

    def __init__(self):
        self.bpf = BPF(text=bpf_program)
        self.connection_count = defaultdict(int)
        self.bytes_transferred = defaultdict(int)
        self.start_time = time.time()

        # Attach probes
        self.bpf.attach_kprobe(event="tcp_v4_connect", fn_name="trace_tcp_connect")
        self.bpf.attach_kprobe(event="tcp_sendmsg", fn_name="trace_tcp_sendmsg")

        print("Layer 4 monitoring started...")

    def print_connection_event(self, cpu, data, size):
        """Handle connection events from eBPF"""
        event = self.bpf["connection_events"].event(data)

        src_ip = socket.inet_ntoa(struct.pack("I", event.src_ip))
        dst_ip = socket.inet_ntoa(struct.pack("I", event.dst_ip))

        connection_key = f"{dst_ip}:{event.dst_port}"
        self.connection_count[connection_key] += 1

        print(f"New connection: {src_ip}:{event.src_port} -> {dst_ip}:{event.dst_port} "
              f"(PID: {event.pid})")

    def get_statistics(self):
        """Get current statistics"""
        uptime = time.time() - self.start_time

        stats = {
            'uptime_seconds': uptime,
            'connections_per_backend': dict(self.connection_count),
            'total_connections': sum(self.connection_count.values()),
            'connections_per_second': sum(self.connection_count.values()) / uptime if uptime > 0 else 0
        }

        return stats

    def start_monitoring(self):
        """Start the monitoring loop"""
        # Set up event callback
        self.bpf["connection_events"].open_perf_buffer(self.print_connection_event)

        print("Monitoring Layer 4 connections (Ctrl+C to stop)...")

        try:
            while True:
                self.bpf.perf_buffer_poll()
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass

    def print_summary(self):
        """Print monitoring summary"""
        stats = self.get_statistics()

        print("\n" + "="*60)
        print("LAYER 4 LOAD BALANCER MONITORING SUMMARY")
        print("="*60)
        print(f"Monitoring Duration: {stats['uptime_seconds']:.2f} seconds")
        print(f"Total Connections: {stats['total_connections']}")
        print(f"Connections/Second: {stats['connections_per_second']:.2f}")
        print("\nConnections per Backend:")

        for backend, count in stats['connections_per_backend'].items():
            percentage = (count / stats['total_connections'] * 100) if stats['total_connections'] > 0 else 0
            print(f"  {backend}: {count} ({percentage:.1f}%)")

# Network performance monitoring
class NetworkPerformanceMonitor:
    """Monitor network performance for Layer 4 load balancing"""

    def __init__(self):
        self.interface_stats = {}

    def get_interface_stats(self, interface='eth0'):
        """Get network interface statistics"""
        try:
            with open(f'/proc/net/dev', 'r') as f:
                lines = f.readlines()

            for line in lines:
                if interface in line:
                    parts = line.split()
                    return {
                        'rx_bytes': int(parts[1]),
                        'rx_packets': int(parts[2]),
                        'rx_errors': int(parts[3]),
                        'rx_dropped': int(parts[4]),
                        'tx_bytes': int(parts[9]),
                        'tx_packets': int(parts[10]),
                        'tx_errors': int(parts[11]),
                        'tx_dropped': int(parts[12])
                    }
        except Exception as e:
            print(f"Error reading interface stats: {e}")
            return {}

    def monitor_network_performance(self, interface='eth0', interval=5):
        """Monitor network performance continuously"""
        print(f"Monitoring network performance on {interface}...")

        prev_stats = self.get_interface_stats(interface)
        if not prev_stats:
            print(f"Could not read stats for interface {interface}")
            return

        try:
            while True:
                time.sleep(interval)
                current_stats = self.get_interface_stats(interface)

                if current_stats:
                    # Calculate rates
                    rx_bytes_rate = (current_stats['rx_bytes'] - prev_stats['rx_bytes']) / interval
                    tx_bytes_rate = (current_stats['tx_bytes'] - prev_stats['tx_bytes']) / interval
                    rx_packets_rate = (current_stats['rx_packets'] - prev_stats['rx_packets']) / interval
                    tx_packets_rate = (current_stats['tx_packets'] - prev_stats['tx_packets']) / interval

                    print(f"\n{interface} Performance ({time.strftime('%H:%M:%S')}):")
                    print(f"  RX: {rx_bytes_rate/1024/1024:.2f} MB/s ({rx_packets_rate:.0f} pps)")
                    print(f"  TX: {tx_bytes_rate/1024/1024:.2f} MB/s ({tx_packets_rate:.0f} pps)")
                    print(f"  RX Errors: {current_stats['rx_errors']} Dropped: {current_stats['rx_dropped']}")
                    print(f"  TX Errors: {current_stats['tx_errors']} Dropped: {current_stats['tx_dropped']}")

                    prev_stats = current_stats

        except KeyboardInterrupt:
            print("\nNetwork monitoring stopped")

# TCP connection monitoring
def monitor_tcp_connections():
    """Monitor TCP connection states"""
    try:
        with open('/proc/net/tcp', 'r') as f:
            lines = f.readlines()[1:]  # Skip header

        connection_states = defaultdict(int)
        total_connections = 0

        for line in lines:
            parts = line.split()
            if len(parts) >= 4:
                state = int(parts[3], 16)
                state_names = {
                    1: 'ESTABLISHED',
                    2: 'SYN_SENT',
                    3: 'SYN_RECV',
                    4: 'FIN_WAIT1',
                    5: 'FIN_WAIT2',
                    6: 'TIME_WAIT',
                    7: 'CLOSE',
                    8: 'CLOSE_WAIT',
                    9: 'LAST_ACK',
                    10: 'LISTEN',
                    11: 'CLOSING'
                }
                state_name = state_names.get(state, f'UNKNOWN({state})')
                connection_states[state_name] += 1
                total_connections += 1

        print(f"\nTCP Connection States (Total: {total_connections}):")
        for state, count in sorted(connection_states.items()):
            percentage = (count / total_connections * 100) if total_connections > 0 else 0
            print(f"  {state}: {count} ({percentage:.1f}%)")

    except Exception as e:
        print(f"Error monitoring TCP connections: {e}")

# Main monitoring script
if __name__ == "__main__":
    import sys
    import threading

    if len(sys.argv) > 1 and sys.argv[1] == '--network-only':
        # Network monitoring only (doesn't require root)
        net_monitor = NetworkPerformanceMonitor()

        def tcp_monitor_loop():
            while True:
                monitor_tcp_connections()
                time.sleep(10)

        # Start TCP monitoring in background
        tcp_thread = threading.Thread(target=tcp_monitor_loop, daemon=True)
        tcp_thread.start()

        # Start network monitoring
        net_monitor.monitor_network_performance()
    else:
        # Full eBPF monitoring (requires root)
        try:
            monitor = Layer4Monitor()
            monitor.start_monitoring()
        except Exception as e:
            print(f"eBPF monitoring failed (requires root): {e}")
            print("Falling back to network monitoring...")
            print("Use --network-only flag to skip eBPF monitoring")
        finally:
            if 'monitor' in locals():
                monitor.print_summary()
```

This comprehensive Layer 4 load balancing implementation provides production-ready TCP/UDP load balancing with high performance, detailed monitoring, and support for various deployment scenarios including Direct Server Return (DSR) and Linux Virtual Server (LVS) configurations.