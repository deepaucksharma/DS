# Load Balancer Health Checks and Monitoring

## Overview

Health checks are critical for maintaining service availability in load-balanced environments. They determine which backend servers should receive traffic and trigger automatic failover when issues are detected.

## Health Check Architecture

```mermaid
graph TB
    subgraph LoadBalancer[Load Balancer Layer]
        LB[Load Balancer<br/>nginx/HAProxy/AWS ALB]
        HC[Health Check Engine<br/>• HTTP checks<br/>• TCP checks<br/>• Custom scripts<br/>• Circuit breaker]
    end

    subgraph HealthChecks[Health Check Types]
        HTTP[HTTP Health Check<br/>GET /health<br/>Response: 200 OK<br/>Body: {"status": "healthy"}]
        TCP[TCP Health Check<br/>Socket connect<br/>Port 8080<br/>Timeout: 3s]
        SCRIPT[Custom Script<br/>./check_app.sh<br/>Exit code: 0 = healthy]
        DEEP[Deep Health Check<br/>Database connectivity<br/>External API status<br/>Memory/CPU usage]
    end

    subgraph Backend[Backend Server Pool]
        S1[Server 1<br/>Status: ✅ Healthy<br/>Last Check: 5s ago<br/>Consecutive Failures: 0]
        S2[Server 2<br/>Status: ❌ Unhealthy<br/>Last Check: 2s ago<br/>Consecutive Failures: 3]
        S3[Server 3<br/>Status: ✅ Healthy<br/>Last Check: 3s ago<br/>Consecutive Failures: 0]
        S4[Server 4<br/>Status: ⚠️ Degraded<br/>Last Check: 1s ago<br/>Response Time: 5000ms]
    end

    subgraph Monitoring[Monitoring & Alerting]
        METRICS[Metrics Collection<br/>• Success rate<br/>• Response times<br/>• Failure patterns]
        ALERT[Alerting System<br/>• PagerDuty<br/>• Slack notifications<br/>• Email alerts]
        DASH[Dashboard<br/>• Real-time status<br/>• Historical trends<br/>• SLA tracking]
    end

    LB --> HC
    HC --> HTTP
    HC --> TCP
    HC --> SCRIPT
    HC --> DEEP

    HC -.-> S1
    HC -.-> S2
    HC -.-> S3
    HC -.-> S4

    S1 --> METRICS
    S2 --> METRICS
    S3 --> METRICS
    S4 --> METRICS

    METRICS --> ALERT
    METRICS --> DASH

    %% Styling
    classDef balancer fill:#90EE90,stroke:#006400,color:#000
    classDef check fill:#87CEEB,stroke:#4682B4,color:#000
    classDef healthy fill:#98FB98,stroke:#32CD32,color:#000
    classDef unhealthy fill:#FFB6C1,stroke:#FF69B4,color:#000
    classDef degraded fill:#FFE4B5,stroke:#DEB887,color:#000
    classDef monitor fill:#DDA0DD,stroke:#9370DB,color:#000

    class LB,HC balancer
    class HTTP,TCP,SCRIPT,DEEP check
    class S1,S3 healthy
    class S2 unhealthy
    class S4 degraded
    class METRICS,ALERT,DASH monitor
```

## Health Check Implementation

### HTTP Health Check System

```python
import asyncio
import aiohttp
import time
import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class HealthStatus(Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"

@dataclass
class HealthCheckResult:
    server: str
    status: HealthStatus
    response_time_ms: float
    timestamp: float
    status_code: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None

class HTTPHealthChecker:
    """Advanced HTTP health checker with circuit breaker pattern"""

    def __init__(self,
                 check_interval: int = 10,
                 timeout: int = 5,
                 healthy_threshold: int = 2,
                 unhealthy_threshold: int = 3,
                 degraded_threshold_ms: int = 5000):
        self.check_interval = check_interval
        self.timeout = timeout
        self.healthy_threshold = healthy_threshold
        self.unhealthy_threshold = unhealthy_threshold
        self.degraded_threshold_ms = degraded_threshold_ms

        # Server state tracking
        self.server_states: Dict[str, Dict] = {}
        self.health_history: Dict[str, List[HealthCheckResult]] = {}
        self.running = False

        # Metrics
        self.metrics = {
            'total_checks': 0,
            'successful_checks': 0,
            'failed_checks': 0,
            'avg_response_time': 0.0
        }

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def add_server(self, server: str, health_endpoint: str = "/health"):
        """Add server to health check monitoring"""
        self.server_states[server] = {
            'url': f"http://{server}{health_endpoint}",
            'status': HealthStatus.UNKNOWN,
            'consecutive_failures': 0,
            'consecutive_successes': 0,
            'last_check': 0,
            'in_rotation': False,
            'response_times': []  # Rolling window of response times
        }
        self.health_history[server] = []
        self.logger.info(f"Added server {server} to health monitoring")

    async def check_server_health(self, server: str) -> HealthCheckResult:
        """Perform health check on a single server"""
        state = self.server_states[server]
        start_time = time.time()

        try:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(state['url']) as response:
                    response_time_ms = (time.time() - start_time) * 1000
                    response_body = await response.text()

                    # Determine health status
                    if response.status == 200:
                        # Parse response for additional health indicators
                        try:
                            health_data = json.loads(response_body)
                            if self._evaluate_health_response(health_data, response_time_ms):
                                status = HealthStatus.HEALTHY
                            else:
                                status = HealthStatus.DEGRADED
                        except json.JSONDecodeError:
                            # Simple 200 OK is considered healthy
                            status = HealthStatus.HEALTHY
                            if response_time_ms > self.degraded_threshold_ms:
                                status = HealthStatus.DEGRADED
                    else:
                        status = HealthStatus.UNHEALTHY

                    return HealthCheckResult(
                        server=server,
                        status=status,
                        response_time_ms=response_time_ms,
                        timestamp=time.time(),
                        status_code=response.status,
                        response_body=response_body[:500]  # Truncate long responses
                    )

        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                server=server,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=response_time_ms,
                timestamp=time.time(),
                error_message=str(e)
            )

    def _evaluate_health_response(self, health_data: Dict, response_time_ms: float) -> bool:
        """Evaluate detailed health response"""
        # Check for degraded performance indicators
        if response_time_ms > self.degraded_threshold_ms:
            return False

        # Check for application-level health indicators
        if 'database' in health_data and health_data['database'] != 'connected':
            return False

        if 'memory_usage' in health_data:
            memory_usage = float(health_data['memory_usage'].rstrip('%'))
            if memory_usage > 90:  # >90% memory usage is degraded
                return False

        if 'cpu_usage' in health_data:
            cpu_usage = float(health_data['cpu_usage'].rstrip('%'))
            if cpu_usage > 85:  # >85% CPU usage is degraded
                return False

        return True

    def update_server_state(self, result: HealthCheckResult):
        """Update server state based on health check result"""
        server = result.server
        state = self.server_states[server]

        # Update response time rolling average
        state['response_times'].append(result.response_time_ms)
        if len(state['response_times']) > 10:  # Keep only last 10 measurements
            state['response_times'].pop(0)

        # Update consecutive counters
        if result.status == HealthStatus.HEALTHY:
            state['consecutive_successes'] += 1
            state['consecutive_failures'] = 0
        else:
            state['consecutive_failures'] += 1
            state['consecutive_successes'] = 0

        # Determine if server should be in rotation
        old_status = state['status']
        old_in_rotation = state['in_rotation']

        if state['consecutive_successes'] >= self.healthy_threshold:
            state['status'] = HealthStatus.HEALTHY
            state['in_rotation'] = True
        elif state['consecutive_failures'] >= self.unhealthy_threshold:
            state['status'] = HealthStatus.UNHEALTHY
            state['in_rotation'] = False
        elif result.status == HealthStatus.DEGRADED:
            state['status'] = HealthStatus.DEGRADED
            state['in_rotation'] = True  # Keep degraded servers in rotation with warnings

        state['last_check'] = result.timestamp

        # Log status changes
        if old_status != state['status'] or old_in_rotation != state['in_rotation']:
            self.logger.warning(
                f"Server {server} status changed: {old_status.value} -> {state['status'].value}, "
                f"in_rotation: {old_in_rotation} -> {state['in_rotation']}"
            )

        # Store health history
        self.health_history[server].append(result)
        if len(self.health_history[server]) > 100:  # Keep last 100 checks
            self.health_history[server].pop(0)

    async def run_health_checks(self):
        """Main health check loop"""
        self.running = True
        self.logger.info("Starting health check monitoring")

        while self.running:
            check_tasks = []
            for server in self.server_states.keys():
                task = asyncio.create_task(self.check_server_health(server))
                check_tasks.append(task)

            # Execute all health checks concurrently
            results = await asyncio.gather(*check_tasks, return_exceptions=True)

            # Process results
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    server = list(self.server_states.keys())[i]
                    self.logger.error(f"Health check error for {server}: {result}")
                    # Create failed result
                    result = HealthCheckResult(
                        server=server,
                        status=HealthStatus.UNHEALTHY,
                        response_time_ms=self.timeout * 1000,
                        timestamp=time.time(),
                        error_message=str(result)
                    )

                self.update_server_state(result)
                self.update_metrics(result)

            await asyncio.sleep(self.check_interval)

    def update_metrics(self, result: HealthCheckResult):
        """Update health check metrics"""
        self.metrics['total_checks'] += 1

        if result.status == HealthStatus.HEALTHY:
            self.metrics['successful_checks'] += 1
        else:
            self.metrics['failed_checks'] += 1

        # Update rolling average response time
        current_avg = self.metrics['avg_response_time']
        total_checks = self.metrics['total_checks']
        self.metrics['avg_response_time'] = (
            (current_avg * (total_checks - 1) + result.response_time_ms) / total_checks
        )

    def get_healthy_servers(self) -> List[str]:
        """Get list of healthy servers eligible for load balancing"""
        return [
            server for server, state in self.server_states.items()
            if state['in_rotation'] and state['status'] != HealthStatus.UNHEALTHY
        ]

    def get_server_status(self) -> Dict[str, Dict]:
        """Get detailed status of all servers"""
        status = {}
        for server, state in self.server_states.items():
            avg_response_time = (
                sum(state['response_times']) / len(state['response_times'])
                if state['response_times'] else 0
            )

            status[server] = {
                'status': state['status'].value,
                'in_rotation': state['in_rotation'],
                'consecutive_failures': state['consecutive_failures'],
                'consecutive_successes': state['consecutive_successes'],
                'last_check_ago_seconds': time.time() - state['last_check'],
                'avg_response_time_ms': round(avg_response_time, 2),
                'url': state['url']
            }

        return status

    def stop(self):
        """Stop health check monitoring"""
        self.running = False
        self.logger.info("Stopping health check monitoring")

# Example usage with integration to load balancer
class HealthAwareLoadBalancer:
    """Load balancer that integrates with health checker"""

    def __init__(self, servers: List[str]):
        self.health_checker = HTTPHealthChecker(
            check_interval=5,  # Check every 5 seconds
            healthy_threshold=2,
            unhealthy_threshold=3
        )

        # Add servers to health monitoring
        for server in servers:
            self.health_checker.add_server(server)

        self.request_count = 0

    async def start(self):
        """Start the health-aware load balancer"""
        # Start health checking in background
        asyncio.create_task(self.health_checker.run_health_checks())

    def get_server(self) -> Optional[str]:
        """Get next healthy server using round robin"""
        healthy_servers = self.health_checker.get_healthy_servers()

        if not healthy_servers:
            # No healthy servers available
            return None

        # Simple round robin among healthy servers
        server = healthy_servers[self.request_count % len(healthy_servers)]
        self.request_count += 1
        return server

    def get_dashboard_data(self) -> Dict:
        """Get data for monitoring dashboard"""
        return {
            'servers': self.health_checker.get_server_status(),
            'metrics': self.health_checker.metrics,
            'healthy_server_count': len(self.health_checker.get_healthy_servers()),
            'total_server_count': len(self.health_checker.server_states)
        }

# Production deployment example
async def main():
    servers = [
        '10.0.1.10:8080',
        '10.0.1.11:8080',
        '10.0.1.12:8080',
        '10.0.1.13:8080'
    ]

    balancer = HealthAwareLoadBalancer(servers)
    await balancer.start()

    # Simulate request routing
    for i in range(20):
        server = balancer.get_server()
        if server:
            print(f"Request {i+1} -> {server}")
        else:
            print(f"Request {i+1} -> No healthy servers available!")

        await asyncio.sleep(1)

    # Print dashboard data
    dashboard = balancer.get_dashboard_data()
    print("\nHealth Status Dashboard:")
    for server, status in dashboard['servers'].items():
        print(f"{server}: {status['status']} (in_rotation: {status['in_rotation']})")

if __name__ == "__main__":
    asyncio.run(main())
```

## Application Health Endpoint Implementation

### Node.js Express Health Endpoint

```javascript
const express = require('express');
const os = require('os');
const { Pool } = require('pg');

class HealthChecker {
    constructor() {
        this.app = express();
        this.dbPool = new Pool({
            connectionString: process.env.DATABASE_URL,
            max: 5,
            idleTimeoutMillis: 30000,
            connectionTimeoutMillis: 2000,
        });

        this.setupHealthEndpoints();
        this.startTime = Date.now();
    }

    setupHealthEndpoints() {
        // Basic health check
        this.app.get('/health', async (req, res) => {
            try {
                const healthStatus = await this.performHealthCheck();

                if (healthStatus.overall === 'healthy') {
                    res.status(200).json(healthStatus);
                } else if (healthStatus.overall === 'degraded') {
                    res.status(200).json(healthStatus); // Still accepting traffic
                } else {
                    res.status(503).json(healthStatus); // Service unavailable
                }
            } catch (error) {
                res.status(503).json({
                    overall: 'unhealthy',
                    error: error.message,
                    timestamp: new Date().toISOString()
                });
            }
        });

        // Detailed health check for monitoring
        this.app.get('/health/detailed', async (req, res) => {
            const detailedHealth = await this.performDetailedHealthCheck();
            res.status(200).json(detailedHealth);
        });

        // Readiness probe (Kubernetes-style)
        this.app.get('/ready', async (req, res) => {
            const isReady = await this.checkReadiness();
            res.status(isReady ? 200 : 503).json({ ready: isReady });
        });

        // Liveness probe (Kubernetes-style)
        this.app.get('/live', (req, res) => {
            res.status(200).json({ alive: true, uptime: Date.now() - this.startTime });
        });
    }

    async performHealthCheck() {
        const checks = await Promise.allSettled([
            this.checkDatabase(),
            this.checkMemory(),
            this.checkCPU(),
            this.checkDiskSpace()
        ]);

        const results = {
            database: checks[0].status === 'fulfilled' ? checks[0].value : 'unhealthy',
            memory: checks[1].status === 'fulfilled' ? checks[1].value : 'unhealthy',
            cpu: checks[2].status === 'fulfilled' ? checks[2].value : 'unhealthy',
            disk: checks[3].status === 'fulfilled' ? checks[3].value : 'unhealthy'
        };

        // Determine overall health
        const unhealthyChecks = Object.values(results).filter(status => status === 'unhealthy');
        const degradedChecks = Object.values(results).filter(status => status === 'degraded');

        let overall;
        if (unhealthyChecks.length > 0) {
            overall = 'unhealthy';
        } else if (degradedChecks.length > 0) {
            overall = 'degraded';
        } else {
            overall = 'healthy';
        }

        return {
            overall,
            checks: results,
            timestamp: new Date().toISOString(),
            uptime: Date.now() - this.startTime,
            version: process.env.APP_VERSION || 'unknown'
        };
    }

    async checkDatabase() {
        try {
            const start = Date.now();
            const client = await this.dbPool.connect();

            await client.query('SELECT 1');
            client.release();

            const responseTime = Date.now() - start;

            if (responseTime > 5000) return 'degraded';  // >5s is degraded
            if (responseTime > 10000) return 'unhealthy'; // >10s is unhealthy

            return 'healthy';
        } catch (error) {
            console.error('Database health check failed:', error);
            return 'unhealthy';
        }
    }

    async checkMemory() {
        const used = process.memoryUsage();
        const total = os.totalmem();
        const free = os.freemem();

        const usagePercentage = ((total - free) / total) * 100;

        if (usagePercentage > 95) return 'unhealthy';
        if (usagePercentage > 85) return 'degraded';

        return 'healthy';
    }

    async checkCPU() {
        return new Promise((resolve) => {
            const start = process.cpuUsage();

            setTimeout(() => {
                const usage = process.cpuUsage(start);
                const totalUsage = (usage.user + usage.system) / 1000000; // Convert to seconds
                const cpuPercentage = (totalUsage / 1) * 100; // 1 second interval

                if (cpuPercentage > 90) resolve('unhealthy');
                else if (cpuPercentage > 75) resolve('degraded');
                else resolve('healthy');
            }, 1000);
        });
    }

    async checkDiskSpace() {
        // Simplified disk space check (in production, use proper disk monitoring)
        return 'healthy'; // Placeholder - implement actual disk space checking
    }

    async checkReadiness() {
        // Application is ready when database is accessible
        try {
            await this.checkDatabase();
            return true;
        } catch {
            return false;
        }
    }

    async performDetailedHealthCheck() {
        const basic = await this.performHealthCheck();

        return {
            ...basic,
            system: {
                nodejs_version: process.version,
                platform: os.platform(),
                architecture: os.arch(),
                load_average: os.loadavg(),
                free_memory: os.freemem(),
                total_memory: os.totalmem(),
                cpu_count: os.cpus().length
            },
            process: {
                pid: process.pid,
                memory_usage: process.memoryUsage(),
                cpu_usage: process.cpuUsage(),
                uptime: process.uptime()
            },
            environment: {
                node_env: process.env.NODE_ENV,
                port: process.env.PORT,
                timezone: process.env.TZ || 'UTC'
            }
        };
    }

    listen(port = 3000) {
        this.app.listen(port, () => {
            console.log(`Health check server running on port ${port}`);
        });
    }
}

// Usage
const healthChecker = new HealthChecker();
healthChecker.listen(3000);

module.exports = HealthChecker;
```

## Circuit Breaker Pattern for Health Checks

```python
import asyncio
import time
from enum import Enum
from typing import Callable, Any

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, failing fast
    HALF_OPEN = "half_open" # Testing if service recovered

class CircuitBreaker:
    """Circuit breaker for health check integration"""

    def __init__(self,
                 failure_threshold: int = 5,
                 recovery_timeout: int = 60,
                 expected_exception: Exception = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function through circuit breaker"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result

        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        return (time.time() - self.last_failure_time) >= self.recovery_timeout

    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

class CircuitBreakerHealthChecker(HTTPHealthChecker):
    """Health checker with circuit breaker protection"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.circuit_breakers = {}

    def add_server(self, server: str, health_endpoint: str = "/health"):
        """Add server with circuit breaker protection"""
        super().add_server(server, health_endpoint)
        self.circuit_breakers[server] = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=30
        )

    async def check_server_health(self, server: str) -> HealthCheckResult:
        """Health check with circuit breaker protection"""
        circuit_breaker = self.circuit_breakers[server]

        try:
            return await circuit_breaker.call(
                super().check_server_health,
                server
            )
        except Exception as e:
            # Circuit breaker is open, mark as unhealthy
            return HealthCheckResult(
                server=server,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=0,
                timestamp=time.time(),
                error_message=f"Circuit breaker: {str(e)}"
            )
```

## Production Monitoring and Alerting

### Prometheus Metrics for Health Checks

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server

class HealthCheckMetrics:
    """Prometheus metrics for health check monitoring"""

    def __init__(self):
        # Counters
        self.health_checks_total = Counter(
            'health_checks_total',
            'Total number of health checks performed',
            ['server', 'status']
        )

        self.health_check_failures_total = Counter(
            'health_check_failures_total',
            'Total number of failed health checks',
            ['server', 'reason']
        )

        # Histograms
        self.health_check_duration = Histogram(
            'health_check_duration_seconds',
            'Duration of health checks',
            ['server'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
        )

        # Gauges
        self.healthy_servers = Gauge(
            'healthy_servers',
            'Number of healthy servers'
        )

        self.unhealthy_servers = Gauge(
            'unhealthy_servers',
            'Number of unhealthy servers'
        )

        self.server_health_status = Gauge(
            'server_health_status',
            'Server health status (1=healthy, 0=unhealthy)',
            ['server']
        )

    def record_health_check(self, result: HealthCheckResult):
        """Record health check metrics"""
        # Update counters
        self.health_checks_total.labels(
            server=result.server,
            status=result.status.value
        ).inc()

        if result.status != HealthStatus.HEALTHY:
            reason = result.error_message or 'unknown'
            self.health_check_failures_total.labels(
                server=result.server,
                reason=reason
            ).inc()

        # Update histogram
        self.health_check_duration.labels(
            server=result.server
        ).observe(result.response_time_ms / 1000)

        # Update server status gauge
        status_value = 1 if result.status == HealthStatus.HEALTHY else 0
        self.server_health_status.labels(server=result.server).set(status_value)

    def update_server_counts(self, healthy_count: int, unhealthy_count: int):
        """Update server count gauges"""
        self.healthy_servers.set(healthy_count)
        self.unhealthy_servers.set(unhealthy_count)

# Integration with health checker
class MonitoredHealthChecker(HTTPHealthChecker):
    """Health checker with Prometheus monitoring"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metrics = HealthCheckMetrics()

        # Start Prometheus metrics server
        start_http_server(8000)

    def update_server_state(self, result: HealthCheckResult):
        """Update server state and record metrics"""
        super().update_server_state(result)

        # Record metrics
        self.metrics.record_health_check(result)

        # Update server counts
        healthy_count = len([
            s for s in self.server_states.values()
            if s['status'] == HealthStatus.HEALTHY
        ])
        unhealthy_count = len([
            s for s in self.server_states.values()
            if s['status'] == HealthStatus.UNHEALTHY
        ])

        self.metrics.update_server_counts(healthy_count, unhealthy_count)
```

### Grafana Dashboard Configuration

```json
{
  "dashboard": {
    "title": "Load Balancer Health Monitoring",
    "panels": [
      {
        "title": "Server Health Status",
        "type": "stat",
        "targets": [
          {
            "expr": "server_health_status",
            "legendFormat": "{{server}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "mappings": [
              {"options": {"0": {"text": "Unhealthy", "color": "red"}}},
              {"options": {"1": {"text": "Healthy", "color": "green"}}}
            ]
          }
        }
      },
      {
        "title": "Health Check Response Times",
        "type": "timeseries",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, health_check_duration_seconds_bucket)",
            "legendFormat": "95th percentile"
          },
          {
            "expr": "histogram_quantile(0.50, health_check_duration_seconds_bucket)",
            "legendFormat": "50th percentile"
          }
        ]
      },
      {
        "title": "Health Check Success Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "rate(health_checks_total{status=\"healthy\"}[5m]) / rate(health_checks_total[5m]) * 100",
            "legendFormat": "Success Rate %"
          }
        ]
      },
      {
        "title": "Server Count by Status",
        "type": "timeseries",
        "targets": [
          {
            "expr": "healthy_servers",
            "legendFormat": "Healthy Servers"
          },
          {
            "expr": "unhealthy_servers",
            "legendFormat": "Unhealthy Servers"
          }
        ]
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "10s"
  }
}
```

This comprehensive health check system provides production-ready monitoring, circuit breaker protection, and detailed metrics collection for maintaining high availability in load-balanced environments.