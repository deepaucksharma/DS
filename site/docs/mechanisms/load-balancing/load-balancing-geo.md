# Geographic Load Balancing and Global Traffic Management

## Overview

Geographic load balancing distributes traffic across multiple data centers and regions based on user location, providing optimal performance and disaster recovery capabilities for global applications.

## Global Load Balancing Architecture

```mermaid
graph TB
    subgraph DNS[DNS Layer - Global Traffic Management]
        GDNS[Global DNS<br/>Route 53 / CloudFlare<br/>GeoDNS Resolution]
        GTM[Global Traffic Manager<br/>• Health monitoring<br/>• Latency-based routing<br/>• Failover policies]
    end

    subgraph Users[Global Users]
        US_USER[US East User<br/>New York<br/>40.7128°N, 74.0060°W]
        EU_USER[European User<br/>London<br/>51.5074°N, 0.1278°W]
        ASIA_USER[Asia User<br/>Tokyo<br/>35.6762°N, 139.6503°E]
        AU_USER[Australia User<br/>Sydney<br/>33.8688°S, 151.2093°E]
    end

    subgraph Regions[Global Data Centers]
        US_EAST[US East (Virginia)<br/>Load Balancer: ALB<br/>Instances: 4x m5.large<br/>Latency to NYC: 10ms]
        EU_WEST[EU West (Ireland)<br/>Load Balancer: ALB<br/>Instances: 3x m5.large<br/>Latency to London: 15ms]
        ASIA_SE[Asia SE (Singapore)<br/>Load Balancer: ALB<br/>Instances: 3x m5.large<br/>Latency to Tokyo: 25ms]
        AU_SE[Australia SE (Sydney)<br/>Load Balancer: ALB<br/>Instances: 2x m5.large<br/>Latency to Sydney: 5ms]
    end

    subgraph Monitoring[Global Monitoring]
        HEALTH[Health Monitors<br/>• Synthetic tests<br/>• Real user monitoring<br/>• SLA tracking]
        METRICS[Metrics Collection<br/>• Response times<br/>• Error rates<br/>• Traffic patterns]
    end

    US_USER --> GDNS
    EU_USER --> GDNS
    ASIA_USER --> GDNS
    AU_USER --> GDNS

    GDNS --> GTM

    GTM -.->|Closest/Fastest| US_EAST
    GTM -.->|Closest/Fastest| EU_WEST
    GTM -.->|Closest/Fastest| ASIA_SE
    GTM -.->|Closest/Fastest| AU_SE

    US_EAST --> HEALTH
    EU_WEST --> HEALTH
    ASIA_SE --> HEALTH
    AU_SE --> HEALTH

    HEALTH --> METRICS

    %% Styling
    classDef dns fill:#87CEEB,stroke:#4682B4,color:#000
    classDef user fill:#98FB98,stroke:#32CD32,color:#000
    classDef region fill:#FFB6C1,stroke:#FF69B4,color:#000
    classDef monitor fill:#DDA0DD,stroke:#9370DB,color:#000

    class GDNS,GTM dns
    class US_USER,EU_USER,ASIA_USER,AU_USER user
    class US_EAST,EU_WEST,ASIA_SE,AU_SE region
    class HEALTH,METRICS monitor
```

## Geolocation-Based Routing Implementation

### DNS-Based Geographic Routing

```python
import geoip2.database
import socket
import asyncio
import aiohttp
import time
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from geopy.distance import geodesic

@dataclass
class DataCenter:
    name: str
    region: str
    endpoint: str
    latitude: float
    longitude: float
    health_status: str = "healthy"
    capacity: int = 100
    current_load: int = 0

@dataclass
class RoutingResult:
    datacenter: DataCenter
    distance_km: float
    latency_ms: float
    routing_reason: str

class GeographicLoadBalancer:
    """Geographic load balancer with intelligent routing"""

    def __init__(self, geoip_db_path: str):
        self.geoip_reader = geoip2.database.Reader(geoip_db_path)
        self.datacenters: List[DataCenter] = []
        self.routing_policies = {
            'closest': self._route_by_closest,
            'lowest_latency': self._route_by_latency,
            'least_loaded': self._route_by_load,
            'hybrid': self._route_hybrid
        }
        self.latency_cache = {}  # Cache measured latencies
        self.routing_stats = {
            'total_requests': 0,
            'routing_decisions': {},
            'failovers': 0
        }

    def add_datacenter(self, datacenter: DataCenter):
        """Add datacenter to the routing pool"""
        self.datacenters.append(datacenter)
        print(f"Added datacenter: {datacenter.name} in {datacenter.region}")

    def get_client_location(self, ip_address: str) -> Tuple[float, float]:
        """Get client location from IP address"""
        try:
            response = self.geoip_reader.city(ip_address)
            return float(response.location.latitude), float(response.location.longitude)
        except Exception as e:
            print(f"GeoIP lookup failed for {ip_address}: {e}")
            # Default to US East coast if lookup fails
            return 40.7128, -74.0060

    def _route_by_closest(self, client_lat: float, client_lon: float) -> DataCenter:
        """Route to geographically closest datacenter"""
        client_location = (client_lat, client_lon)
        closest_dc = None
        min_distance = float('inf')

        for dc in self.datacenters:
            if dc.health_status != 'healthy':
                continue

            dc_location = (dc.latitude, dc.longitude)
            distance = geodesic(client_location, dc_location).kilometers

            if distance < min_distance:
                min_distance = distance
                closest_dc = dc

        return closest_dc

    async def _route_by_latency(self, client_lat: float, client_lon: float) -> DataCenter:
        """Route to datacenter with lowest network latency"""
        # In production, this would measure actual network latency
        # For demo, we'll use geographic distance as proxy
        latency_tasks = []

        for dc in self.datacenters:
            if dc.health_status == 'healthy':
                task = asyncio.create_task(self._measure_latency(dc))
                latency_tasks.append((dc, task))

        lowest_latency_dc = None
        min_latency = float('inf')

        for dc, task in latency_tasks:
            try:
                latency = await task
                if latency < min_latency:
                    min_latency = latency
                    lowest_latency_dc = dc
            except Exception:
                continue  # Skip failed latency measurements

        return lowest_latency_dc

    def _route_by_load(self, client_lat: float, client_lon: float) -> DataCenter:
        """Route to datacenter with lowest current load"""
        least_loaded_dc = None
        min_load_percentage = float('inf')

        for dc in self.datacenters:
            if dc.health_status != 'healthy':
                continue

            load_percentage = (dc.current_load / dc.capacity) * 100
            if load_percentage < min_load_percentage:
                min_load_percentage = load_percentage
                least_loaded_dc = dc

        return least_loaded_dc

    def _route_hybrid(self, client_lat: float, client_lon: float) -> DataCenter:
        """Hybrid routing considering distance, latency, and load"""
        client_location = (client_lat, client_lon)
        best_dc = None
        best_score = float('inf')

        for dc in self.datacenters:
            if dc.health_status != 'healthy':
                continue

            # Calculate distance score (normalized to 0-100)
            dc_location = (dc.latitude, dc.longitude)
            distance = geodesic(client_location, dc_location).kilometers
            distance_score = min(distance / 100, 100)  # Cap at 100

            # Calculate load score (0-100)
            load_score = (dc.current_load / dc.capacity) * 100

            # Get cached latency or use distance as proxy
            latency_key = f"{client_lat},{client_lon}->{dc.name}"
            latency_score = self.latency_cache.get(latency_key, distance / 10)

            # Weighted combination (distance: 40%, load: 30%, latency: 30%)
            composite_score = (
                distance_score * 0.4 +
                load_score * 0.3 +
                latency_score * 0.3
            )

            if composite_score < best_score:
                best_score = composite_score
                best_dc = dc

        return best_dc

    async def _measure_latency(self, datacenter: DataCenter) -> float:
        """Measure network latency to datacenter"""
        start_time = time.time()

        try:
            # Use health check endpoint for latency measurement
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f"{datacenter.endpoint}/ping") as response:
                    await response.text()

            latency_ms = (time.time() - start_time) * 1000
            return latency_ms

        except Exception:
            # Return high latency for failed connections
            return 5000

    async def route_request(self, client_ip: str, policy: str = 'hybrid') -> RoutingResult:
        """Route request to optimal datacenter"""
        self.routing_stats['total_requests'] += 1

        # Get client location
        client_lat, client_lon = self.get_client_location(client_ip)

        # Apply routing policy
        routing_func = self.routing_policies.get(policy, self._route_hybrid)
        if asyncio.iscoroutinefunction(routing_func):
            selected_dc = await routing_func(client_lat, client_lon)
        else:
            selected_dc = routing_func(client_lat, client_lon)

        if not selected_dc:
            # Failover to any healthy datacenter
            healthy_dcs = [dc for dc in self.datacenters if dc.health_status == 'healthy']
            if healthy_dcs:
                selected_dc = healthy_dcs[0]
                self.routing_stats['failovers'] += 1
                routing_reason = "failover_to_any_healthy"
            else:
                raise Exception("No healthy datacenters available")
        else:
            routing_reason = policy

        # Calculate distance and estimated latency
        client_location = (client_lat, client_lon)
        dc_location = (selected_dc.latitude, selected_dc.longitude)
        distance = geodesic(client_location, dc_location).kilometers

        # Estimate latency based on distance (rough approximation)
        estimated_latency = distance / 10  # ~10km per ms is rough estimate

        # Update routing statistics
        if routing_reason not in self.routing_stats['routing_decisions']:
            self.routing_stats['routing_decisions'][routing_reason] = 0
        self.routing_stats['routing_decisions'][routing_reason] += 1

        # Update datacenter load
        selected_dc.current_load += 1

        return RoutingResult(
            datacenter=selected_dc,
            distance_km=distance,
            latency_ms=estimated_latency,
            routing_reason=routing_reason
        )

    def update_datacenter_health(self, datacenter_name: str, health_status: str):
        """Update datacenter health status"""
        for dc in self.datacenters:
            if dc.name == datacenter_name:
                old_status = dc.health_status
                dc.health_status = health_status
                print(f"Datacenter {datacenter_name}: {old_status} -> {health_status}")
                break

    def get_routing_stats(self) -> Dict:
        """Get routing statistics"""
        return {
            'total_requests': self.routing_stats['total_requests'],
            'routing_decisions': self.routing_stats['routing_decisions'],
            'failovers': self.routing_stats['failovers'],
            'datacenter_status': [
                {
                    'name': dc.name,
                    'region': dc.region,
                    'health': dc.health_status,
                    'load': f"{dc.current_load}/{dc.capacity} ({(dc.current_load/dc.capacity)*100:.1f}%)"
                }
                for dc in self.datacenters
            ]
        }

# Production-grade DNS server integration
class GeoDNSServer:
    """DNS server with geographic routing"""

    def __init__(self, geo_balancer: GeographicLoadBalancer):
        self.geo_balancer = geo_balancer
        self.dns_cache = {}
        self.ttl = 60  # DNS TTL in seconds

    async def resolve_dns_query(self, domain: str, client_ip: str) -> str:
        """Resolve DNS query with geographic routing"""
        cache_key = f"{domain}:{client_ip}"

        # Check cache first
        if cache_key in self.dns_cache:
            cached_result, timestamp = self.dns_cache[cache_key]
            if time.time() - timestamp < self.ttl:
                return cached_result

        # Route request to optimal datacenter
        routing_result = await self.geo_balancer.route_request(client_ip)

        # Extract IP from endpoint (in production, this would be more sophisticated)
        import re
        ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', routing_result.datacenter.endpoint)
        if ip_match:
            resolved_ip = ip_match.group(1)
        else:
            # Fallback to a default IP
            resolved_ip = "203.0.113.1"

        # Cache the result
        self.dns_cache[cache_key] = (resolved_ip, time.time())

        print(f"DNS resolution: {domain} for {client_ip} -> {resolved_ip} "
              f"(datacenter: {routing_result.datacenter.name}, "
              f"distance: {routing_result.distance_km:.1f}km)")

        return resolved_ip

# Example implementation with multiple datacenters
async def main():
    # Initialize geographic load balancer
    # Note: In production, download GeoLite2 database from MaxMind
    geo_balancer = GeographicLoadBalancer('/path/to/GeoLite2-City.mmdb')

    # Add global datacenters
    datacenters = [
        DataCenter("us-east-1", "North America", "https://10.0.1.10", 38.9072, -77.0369, capacity=200),
        DataCenter("us-west-1", "North America", "https://10.0.2.10", 37.7749, -122.4194, capacity=150),
        DataCenter("eu-west-1", "Europe", "https://10.0.3.10", 53.3498, -6.2603, capacity=100),
        DataCenter("ap-southeast-1", "Asia", "https://10.0.4.10", 1.3521, 103.8198, capacity=120),
        DataCenter("ap-northeast-1", "Asia", "https://10.0.5.10", 35.6762, 139.6503, capacity=180),
        DataCenter("ap-southeast-2", "Australia", "https://10.0.6.10", -33.8688, 151.2093, capacity=80)
    ]

    for dc in datacenters:
        geo_balancer.add_datacenter(dc)

    # Initialize DNS server
    dns_server = GeoDNSServer(geo_balancer)

    # Simulate requests from different global locations
    test_requests = [
        ("203.0.113.100", "New York, US"),      # US East Coast
        ("198.51.100.50", "Los Angeles, US"),   # US West Coast
        ("192.0.2.25", "London, UK"),          # Europe
        ("172.16.0.10", "Singapore"),          # Southeast Asia
        ("10.0.0.5", "Tokyo, Japan"),          # Northeast Asia
        ("192.168.1.100", "Sydney, Australia") # Australia
    ]

    print("Geographic Load Balancing Simulation")
    print("=" * 50)

    for client_ip, location in test_requests:
        print(f"\nRequest from {location} ({client_ip}):")

        # Test different routing policies
        for policy in ['closest', 'hybrid']:
            routing_result = await geo_balancer.route_request(client_ip, policy)
            print(f"  {policy.capitalize()} routing -> {routing_result.datacenter.name} "
                  f"({routing_result.distance_km:.1f}km, estimated latency: {routing_result.latency_ms:.1f}ms)")

        # DNS resolution
        resolved_ip = await dns_server.resolve_dns_query("api.company.com", client_ip)
        print(f"  DNS resolution: api.company.com -> {resolved_ip}")

    # Simulate datacenter failure
    print(f"\n{'='*50}")
    print("Simulating EU West datacenter failure...")
    geo_balancer.update_datacenter_health("eu-west-1", "unhealthy")

    # Test failover
    eu_client_ip = "192.0.2.25"  # London IP
    failover_result = await geo_balancer.route_request(eu_client_ip, 'closest')
    print(f"Failover routing for London client -> {failover_result.datacenter.name} "
          f"(reason: {failover_result.routing_reason})")

    # Print final statistics
    print(f"\n{'='*50}")
    print("Routing Statistics:")
    stats = geo_balancer.get_routing_stats()
    print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
```

## AWS Route 53 Configuration

### Terraform Configuration for Global Load Balancing

```hcl
# terraform/route53-geo-routing.tf

# Health checks for each region
resource "aws_route53_health_check" "us_east" {
  fqdn                            = "us-east.api.company.com"
  port                            = 443
  type                            = "HTTPS"
  resource_path                   = "/health"
  failure_threshold               = "3"
  request_interval                = "30"
  insufficient_data_health_status = "Failure"

  tags = {
    Name = "US East Health Check"
    Environment = "production"
  }
}

resource "aws_route53_health_check" "eu_west" {
  fqdn                            = "eu-west.api.company.com"
  port                            = 443
  type                            = "HTTPS"
  resource_path                   = "/health"
  failure_threshold               = "3"
  request_interval                = "30"

  tags = {
    Name = "EU West Health Check"
    Environment = "production"
  }
}

resource "aws_route53_health_check" "ap_southeast" {
  fqdn                            = "ap-southeast.api.company.com"
  port                            = 443
  type                            = "HTTPS"
  resource_path                   = "/health"
  failure_threshold               = "3"
  request_interval                = "30"

  tags = {
    Name = "AP Southeast Health Check"
    Environment = "production"
  }
}

# Primary DNS zone
resource "aws_route53_zone" "main" {
  name = "company.com"

  tags = {
    Environment = "production"
  }
}

# Geolocation-based routing records
resource "aws_route53_record" "api_us" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.company.com"
  type    = "A"
  ttl     = 60

  set_identifier = "US"
  geolocation_routing_policy {
    continent = "NA"  # North America
  }

  health_check_id = aws_route53_health_check.us_east.id

  records = [aws_eip.us_east_lb.public_ip]
}

resource "aws_route53_record" "api_eu" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.company.com"
  type    = "A"
  ttl     = 60

  set_identifier = "EU"
  geolocation_routing_policy {
    continent = "EU"  # Europe
  }

  health_check_id = aws_route53_health_check.eu_west.id

  records = [aws_eip.eu_west_lb.public_ip]
}

resource "aws_route53_record" "api_asia" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.company.com"
  type    = "A"
  ttl     = 60

  set_identifier = "ASIA"
  geolocation_routing_policy {
    continent = "AS"  # Asia
  }

  health_check_id = aws_route53_health_check.ap_southeast.id

  records = [aws_eip.ap_southeast_lb.public_ip]
}

# Default fallback for unmatched locations
resource "aws_route53_record" "api_default" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.company.com"
  type    = "A"
  ttl     = 60

  set_identifier = "DEFAULT"
  geolocation_routing_policy {
    country = "*"  # Default for all other countries
  }

  health_check_id = aws_route53_health_check.us_east.id

  records = [aws_eip.us_east_lb.public_ip]
}

# Latency-based routing (alternative approach)
resource "aws_route53_record" "api_latency_us" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "latency.api.company.com"
  type    = "A"
  ttl     = 60

  set_identifier = "US-EAST-LATENCY"
  latency_routing_policy {
    region = "us-east-1"
  }

  health_check_id = aws_route53_health_check.us_east.id

  records = [aws_eip.us_east_lb.public_ip]
}

resource "aws_route53_record" "api_latency_eu" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "latency.api.company.com"
  type    = "A"
  ttl     = 60

  set_identifier = "EU-WEST-LATENCY"
  latency_routing_policy {
    region = "eu-west-1"
  }

  health_check_id = aws_route53_health_check.eu_west.id

  records = [aws_eip.eu_west_lb.public_ip]
}

# Weighted routing for gradual traffic shifting
resource "aws_route53_record" "api_weighted_current" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "beta.api.company.com"
  type    = "A"
  ttl     = 60

  set_identifier = "CURRENT-90"
  weighted_routing_policy {
    weight = 90
  }

  health_check_id = aws_route53_health_check.us_east.id

  records = [aws_eip.us_east_lb.public_ip]
}

resource "aws_route53_record" "api_weighted_canary" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "beta.api.company.com"
  type    = "A"
  ttl     = 60

  set_identifier = "CANARY-10"
  weighted_routing_policy {
    weight = 10
  }

  health_check_id = aws_route53_health_check.eu_west.id

  records = [aws_eip.eu_west_lb.public_ip]
}

# CloudWatch alarms for health check failures
resource "aws_cloudwatch_metric_alarm" "health_check_us_east" {
  alarm_name          = "route53-health-check-us-east-failure"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "HealthCheckStatus"
  namespace           = "AWS/Route53"
  period              = "60"
  statistic           = "Minimum"
  threshold           = "1"
  alarm_description   = "This metric monitors US East health check"

  dimensions = {
    HealthCheckId = aws_route53_health_check.us_east.id
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
}

# SNS topic for alerts
resource "aws_sns_topic" "alerts" {
  name = "route53-health-alerts"
}

# Output important values
output "name_servers" {
  value = aws_route53_zone.main.name_servers
}

output "health_check_ids" {
  value = {
    us_east      = aws_route53_health_check.us_east.id
    eu_west      = aws_route53_health_check.eu_west.id
    ap_southeast = aws_route53_health_check.ap_southeast.id
  }
}
```

## Cloudflare Global Load Balancing

### Cloudflare Load Balancer Configuration

```javascript
// cloudflare-geo-lb.js - Cloudflare Worker for intelligent routing

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
});

class CloudflareGeoLoadBalancer {
  constructor() {
    this.pools = {
      'us-east': {
        name: 'US East',
        origins: [
          { address: '10.0.1.10', weight: 1, enabled: true },
          { address: '10.0.1.11', weight: 1, enabled: true }
        ],
        monitor: 'health-check-us-east',
        latitude: 38.9072,
        longitude: -77.0369
      },
      'eu-west': {
        name: 'EU West',
        origins: [
          { address: '10.0.3.10', weight: 1, enabled: true },
          { address: '10.0.3.11', weight: 1, enabled: true }
        ],
        monitor: 'health-check-eu-west',
        latitude: 53.3498,
        longitude: -6.2603
      },
      'ap-southeast': {
        name: 'AP Southeast',
        origins: [
          { address: '10.0.4.10', weight: 1, enabled: true },
          { address: '10.0.4.11', weight: 1, enabled: true }
        ],
        monitor: 'health-check-ap-southeast',
        latitude: 1.3521,
        longitude: 103.8198
      }
    };

    this.healthChecks = {};
    this.routingPolicy = 'proximity'; // proximity, latency, performance
  }

  calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Earth's radius in kilometers
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
  }

  getClientLocation(request) {
    // Cloudflare provides geolocation data
    const country = request.cf.country;
    const latitude = request.cf.latitude;
    const longitude = request.cf.longitude;
    const city = request.cf.city;
    const timezone = request.cf.timezone;

    return {
      country,
      latitude: parseFloat(latitude) || 0,
      longitude: parseFloat(longitude) || 0,
      city,
      timezone
    };
  }

  async getPoolHealth(poolId) {
    // In production, this would check actual health monitoring
    // For demo, simulate some pools being down
    const healthStatus = {
      'us-east': { healthy: true, latency: 45 },
      'eu-west': { healthy: true, latency: 32 },
      'ap-southeast': { healthy: true, latency: 67 }
    };

    return healthStatus[poolId] || { healthy: false, latency: 9999 };
  }

  async selectPool(clientLocation) {
    const candidatePools = [];

    // Evaluate each pool
    for (const [poolId, pool] of Object.entries(this.pools)) {
      const health = await this.getPoolHealth(poolId);

      if (!health.healthy) continue;

      const distance = this.calculateDistance(
        clientLocation.latitude,
        clientLocation.longitude,
        pool.latitude,
        pool.longitude
      );

      candidatePools.push({
        poolId,
        pool,
        distance,
        latency: health.latency,
        score: this.calculatePoolScore(distance, health.latency)
      });
    }

    if (candidatePools.length === 0) {
      throw new Error('No healthy pools available');
    }

    // Sort by score (lower is better)
    candidatePools.sort((a, b) => a.score - b.score);

    return candidatePools[0];
  }

  calculatePoolScore(distance, latency) {
    // Weighted scoring: 60% distance, 40% latency
    const distanceScore = distance / 100; // Normalize distance
    const latencyScore = latency / 10;    // Normalize latency
    return (distanceScore * 0.6) + (latencyScore * 0.4);
  }

  selectOrigin(pool) {
    // Select healthy origin from pool using weighted round robin
    const healthyOrigins = pool.origins.filter(origin => origin.enabled);

    if (healthyOrigins.length === 0) {
      throw new Error('No healthy origins in pool');
    }

    // Simple round robin for demo (in production, use proper load balancing)
    const timestamp = Date.now();
    const index = Math.floor(timestamp / 1000) % healthyOrigins.length;
    return healthyOrigins[index];
  }

  async routeRequest(request) {
    const clientLocation = this.getClientLocation(request);

    try {
      const selectedPool = await this.selectPool(clientLocation);
      const selectedOrigin = this.selectOrigin(selectedPool.pool);

      // Log routing decision
      console.log(`Routing client from ${clientLocation.city}, ${clientLocation.country} ` +
                 `to pool ${selectedPool.poolId} (${selectedPool.distance.toFixed(1)}km away), ` +
                 `origin ${selectedOrigin.address}`);

      // Construct target URL
      const url = new URL(request.url);
      url.hostname = selectedOrigin.address;

      // Add routing headers
      const modifiedRequest = new Request(url.toString(), {
        method: request.method,
        headers: request.headers,
        body: request.body
      });

      modifiedRequest.headers.set('X-CF-Pool', selectedPool.poolId);
      modifiedRequest.headers.set('X-CF-Origin', selectedOrigin.address);
      modifiedRequest.headers.set('X-CF-Distance-KM', selectedPool.distance.toFixed(1));
      modifiedRequest.headers.set('X-CF-Client-City', clientLocation.city);
      modifiedRequest.headers.set('X-CF-Client-Country', clientLocation.country);

      return fetch(modifiedRequest);

    } catch (error) {
      // Fallback to default pool
      console.error('Routing error:', error);
      return new Response('Service temporarily unavailable', {
        status: 503,
        headers: {
          'Content-Type': 'text/plain',
          'X-CF-Error': error.message
        }
      });
    }
  }
}

async function handleRequest(request) {
  const loadBalancer = new CloudflareGeoLoadBalancer();

  // Handle health check requests locally
  if (request.url.includes('/cf-health')) {
    return new Response(JSON.stringify({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      pools: Object.keys(loadBalancer.pools)
    }), {
      headers: { 'Content-Type': 'application/json' }
    });
  }

  // Route all other requests
  return loadBalancer.routeRequest(request);
}
```

## Performance Monitoring for Geographic Load Balancing

### Real User Monitoring (RUM)

```javascript
// client-side RUM collection
class GeographicPerformanceMonitor {
  constructor() {
    this.metrics = {
      dns_time: 0,
      connect_time: 0,
      ssl_time: 0,
      response_time: 0,
      total_time: 0
    };
    this.server_info = {};
  }

  collectPerformanceMetrics() {
    if (!window.performance || !window.performance.timing) {
      return null;
    }

    const timing = window.performance.timing;
    const navigation = window.performance.navigation;

    this.metrics = {
      dns_time: timing.domainLookupEnd - timing.domainLookupStart,
      connect_time: timing.connectEnd - timing.connectStart,
      ssl_time: timing.connectEnd - timing.secureConnectionStart,
      response_time: timing.responseEnd - timing.responseStart,
      total_time: timing.loadEventEnd - timing.navigationStart,
      redirect_time: timing.redirectEnd - timing.redirectStart,
      cache_hit: navigation.type === navigation.TYPE_BACK_FORWARD
    };

    // Collect server routing information from headers
    this.collectServerInfo();

    return this.metrics;
  }

  async collectServerInfo() {
    try {
      const response = await fetch('/api/server-info');
      const data = await response.json();

      this.server_info = {
        datacenter: response.headers.get('X-Datacenter') || 'unknown',
        region: response.headers.get('X-Region') || 'unknown',
        server_id: response.headers.get('X-Server-ID') || 'unknown',
        routing_policy: response.headers.get('X-Routing-Policy') || 'unknown',
        client_distance_km: parseFloat(response.headers.get('X-Distance-KM')) || 0
      };
    } catch (error) {
      console.warn('Failed to collect server info:', error);
    }
  }

  async sendMetrics() {
    const payload = {
      timestamp: new Date().toISOString(),
      user_agent: navigator.userAgent,
      url: window.location.href,
      client_info: {
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        language: navigator.language,
        connection: navigator.connection ? {
          effective_type: navigator.connection.effectiveType,
          downlink: navigator.connection.downlink,
          rtt: navigator.connection.rtt
        } : null
      },
      performance: this.metrics,
      server: this.server_info
    };

    try {
      await fetch('/api/metrics/rum', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });
    } catch (error) {
      console.warn('Failed to send RUM metrics:', error);
    }
  }

  init() {
    // Collect metrics after page load
    window.addEventListener('load', () => {
      setTimeout(() => {
        this.collectPerformanceMetrics();
        this.sendMetrics();
      }, 1000);
    });
  }
}

// Initialize monitoring
const rumMonitor = new GeographicPerformanceMonitor();
rumMonitor.init();
```

This comprehensive geographic load balancing implementation provides production-ready global traffic distribution with intelligent routing, health monitoring, and performance optimization across multiple data centers and cloud providers.