# CDN Cache Misses - Investigation and Optimization Guide

## Overview

Systematic approaches to investigating poor CDN cache hit rates and optimizing content delivery. Based on production experiences from Cloudflare's edge optimization, Fastly's cache strategies, and AWS CloudFront performance tuning.

## CDN Cache Analysis Commands

### Basic Cache Performance Investigation
```bash
# Check cache hit ratios via CDN logs
grep "cache-status" /var/log/nginx/access.log | awk '{print $NF}' | sort | uniq -c

# Analyze CloudFront cache behavior
aws logs filter-log-events --log-group-name /aws/cloudfront/distribution/EXAMPLE123 \
  --filter-pattern="[timestamp, request_id, client_ip, method, uri, status, cache_status]"

# Check Cloudflare cache analytics
curl -X GET "https://api.cloudflare.com/client/v4/zones/ZONE_ID/analytics/dashboard" \
  -H "Authorization: Bearer YOUR_API_TOKEN"

# Monitor cache misses in real-time
tail -f /var/log/nginx/access.log | grep "MISS"
```

## Production Examples

### Cloudflare Edge: Cache Optimization Strategy
```javascript
// Cloudflare Workers script for intelligent cache optimization
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

class CloudflareCacheOptimizer {
  constructor() {
    this.cacheRules = {
      static: {
        extensions: ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2'],
        ttl: 86400 * 30, // 30 days
        browser_ttl: 86400 * 7 // 7 days
      },
      api: {
        paths: ['/api/users/', '/api/products/'],
        ttl: 300, // 5 minutes
        browser_ttl: 60 // 1 minute
      },
      dynamic: {
        paths: ['/search', '/recommendations'],
        ttl: 60, // 1 minute
        browser_ttl: 0, // No browser cache
        vary_headers: ['Authorization', 'Accept-Language', 'User-Agent']
      }
    }
  }

  async handleRequest(request) {
    const url = new URL(request.url)
    const cacheKey = this.generateCacheKey(request, url)

    try {
      // Try cache first
      const cachedResponse = await this.getFromCache(cacheKey, request)
      if (cachedResponse) {
        return this.addCacheHeaders(cachedResponse, 'HIT')
      }

      // Cache miss - fetch from origin
      const originResponse = await this.fetchFromOrigin(request)

      // Determine if response should be cached
      const cacheConfig = this.determineCacheConfig(url, originResponse)

      if (cacheConfig && this.shouldCache(originResponse)) {
        await this.storeInCache(cacheKey, originResponse, cacheConfig)
      }

      return this.addCacheHeaders(originResponse, 'MISS')

    } catch (error) {
      console.error('Cache handling error:', error)
      // Fallback to origin
      return await this.fetchFromOrigin(request)
    }
  }

  generateCacheKey(request, url) {
    const baseKey = `${request.method}:${url.pathname}${url.search}`

    // Add vary factors for dynamic content
    const varyFactors = []

    // Geographic variation
    const country = request.cf?.country || 'unknown'
    varyFactors.push(`country:${country}`)

    // Device type variation
    const userAgent = request.headers.get('User-Agent') || ''
    const deviceType = this.detectDeviceType(userAgent)
    varyFactors.push(`device:${deviceType}`)

    // Authentication variation for personalized content
    if (this.isPersonalizedPath(url.pathname)) {
      const authHash = this.hashAuthToken(request.headers.get('Authorization'))
      if (authHash) {
        varyFactors.push(`auth:${authHash}`)
      }
    }

    // Language variation
    const acceptLanguage = request.headers.get('Accept-Language')
    if (acceptLanguage) {
      const primaryLang = acceptLanguage.split(',')[0].split('-')[0]
      varyFactors.push(`lang:${primaryLang}`)
    }

    return varyFactors.length > 0 ? `${baseKey}|${varyFactors.join('|')}` : baseKey
  }

  async getFromCache(cacheKey, request) {
    // Try Cloudflare edge cache first
    const cache = caches.default
    const cacheRequest = new Request(`https://cache.example.com/${encodeURIComponent(cacheKey)}`, {
      method: 'GET',
      headers: {
        'Cache-Key': cacheKey
      }
    })

    return await cache.match(cacheRequest)
  }

  async storeInCache(cacheKey, response, config) {
    const cache = caches.default

    // Clone response for caching
    const responseToCache = response.clone()

    // Add cache control headers
    const headers = new Headers(responseToCache.headers)
    headers.set('Cache-Control', `public, max-age=${config.ttl}`)
    headers.set('X-Cache-Config', JSON.stringify(config))
    headers.set('X-Cache-Key', cacheKey)
    headers.set('X-Cached-At', new Date().toISOString())

    const cachedResponse = new Response(responseToCache.body, {
      status: responseToCache.status,
      statusText: responseToCache.statusText,
      headers: headers
    })

    const cacheRequest = new Request(`https://cache.example.com/${encodeURIComponent(cacheKey)}`, {
      method: 'GET',
      headers: {
        'Cache-Key': cacheKey
      }
    })

    await cache.put(cacheRequest, cachedResponse)
  }

  determineCacheConfig(url, response) {
    const pathname = url.pathname
    const extension = this.getFileExtension(pathname)

    // Static assets
    if (this.cacheRules.static.extensions.includes(extension)) {
      return {
        type: 'static',
        ttl: this.cacheRules.static.ttl,
        browser_ttl: this.cacheRules.static.browser_ttl,
        vary: []
      }
    }

    // API endpoints
    for (const apiPath of this.cacheRules.api.paths) {
      if (pathname.startsWith(apiPath)) {
        return {
          type: 'api',
          ttl: this.cacheRules.api.ttl,
          browser_ttl: this.cacheRules.api.browser_ttl,
          vary: ['Authorization']
        }
      }
    }

    // Dynamic content
    for (const dynamicPath of this.cacheRules.dynamic.paths) {
      if (pathname.startsWith(dynamicPath)) {
        return {
          type: 'dynamic',
          ttl: this.cacheRules.dynamic.ttl,
          browser_ttl: this.cacheRules.dynamic.browser_ttl,
          vary: this.cacheRules.dynamic.vary_headers
        }
      }
    }

    // Default: no cache
    return null
  }

  shouldCache(response) {
    // Don't cache error responses
    if (response.status >= 400) {
      return false
    }

    // Don't cache responses with certain headers
    const cacheControl = response.headers.get('Cache-Control')
    if (cacheControl && (cacheControl.includes('no-cache') || cacheControl.includes('no-store'))) {
      return false
    }

    // Don't cache responses with Set-Cookie headers (unless explicitly allowed)
    if (response.headers.get('Set-Cookie')) {
      return false
    }

    return true
  }

  addCacheHeaders(response, cacheStatus) {
    const headers = new Headers(response.headers)
    headers.set('X-Cache', cacheStatus)
    headers.set('X-Cache-Date', new Date().toISOString())

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: headers
    })
  }

  async fetchFromOrigin(request) {
    // Add origin request headers
    const originHeaders = new Headers(request.headers)
    originHeaders.set('X-Forwarded-For', request.headers.get('CF-Connecting-IP') || '')
    originHeaders.set('X-Real-IP', request.headers.get('CF-Connecting-IP') || '')

    const originRequest = new Request(request.url, {
      method: request.method,
      headers: originHeaders,
      body: request.body
    })

    return await fetch(originRequest)
  }

  detectDeviceType(userAgent) {
    if (/Mobile|Android|iPhone|iPad/.test(userAgent)) {
      return 'mobile'
    }
    if (/Tablet/.test(userAgent)) {
      return 'tablet'
    }
    return 'desktop'
  }

  isPersonalizedPath(pathname) {
    const personalizedPaths = ['/dashboard', '/profile', '/recommendations', '/feed']
    return personalizedPaths.some(path => pathname.startsWith(path))
  }

  hashAuthToken(authHeader) {
    if (!authHeader) return null

    // Extract token and create hash (simplified)
    const token = authHeader.replace('Bearer ', '')
    return token ? btoa(token.substring(0, 10)) : null
  }

  getFileExtension(pathname) {
    const lastDot = pathname.lastIndexOf('.')
    return lastDot > 0 ? pathname.substring(lastDot) : ''
  }
}

async function handleRequest(request) {
  const optimizer = new CloudflareCacheOptimizer()
  return await optimizer.handleRequest(request)
}
```

### AWS CloudFront: Cache Behavior Analysis
```python
#!/usr/bin/env python3
"""
AWS CloudFront cache miss analysis and optimization
"""
import boto3
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any
import gzip
import re

class CloudFrontCacheAnalyzer:
    def __init__(self, distribution_id: str):
        self.distribution_id = distribution_id
        self.cloudfront = boto3.client('cloudfront')
        self.s3 = boto3.client('s3')
        self.logs_client = boto3.client('logs')

    def analyze_cache_performance(self, hours_back: int = 24) -> Dict[str, Any]:
        """Analyze CloudFront cache performance over specified time period"""

        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours_back)

        # Get distribution config
        dist_config = self.get_distribution_config()

        # Analyze access logs
        log_analysis = self.analyze_access_logs(start_time, end_time)

        # Get CloudWatch metrics
        cloudwatch_metrics = self.get_cloudwatch_metrics(start_time, end_time)

        # Generate cache miss analysis
        cache_analysis = self.analyze_cache_misses(log_analysis)

        # Generate recommendations
        recommendations = self.generate_optimization_recommendations(
            dist_config, log_analysis, cache_analysis
        )

        return {
            'distribution_id': self.distribution_id,
            'analysis_period': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat(),
                'hours': hours_back
            },
            'cache_performance': log_analysis,
            'cloudwatch_metrics': cloudwatch_metrics,
            'cache_miss_analysis': cache_analysis,
            'optimization_recommendations': recommendations
        }

    def analyze_access_logs(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Analyze CloudFront access logs for cache performance"""

        # Get log files from S3 (assuming logs are stored in S3)
        log_bucket = f"cloudfront-logs-{self.distribution_id}"
        log_files = self.get_log_files_in_range(log_bucket, start_time, end_time)

        cache_stats = {
            'total_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'hit_ratio': 0.0,
            'status_codes': {},
            'cache_status_breakdown': {},
            'top_missed_paths': {},
            'edge_locations': {},
            'user_agents': {},
            'request_methods': {}
        }

        # Process log files
        for log_file in log_files:
            try:
                log_data = self.download_and_parse_log_file(log_bucket, log_file)
                self.process_log_entries(log_data, cache_stats)
            except Exception as e:
                print(f"Error processing log file {log_file}: {e}")
                continue

        # Calculate derived metrics
        if cache_stats['total_requests'] > 0:
            cache_stats['hit_ratio'] = (cache_stats['cache_hits'] / cache_stats['total_requests']) * 100

        # Sort top missed paths
        cache_stats['top_missed_paths'] = dict(
            sorted(cache_stats['top_missed_paths'].items(),
                  key=lambda x: x[1], reverse=True)[:20]
        )

        return cache_stats

    def process_log_entries(self, log_entries: List[Dict], cache_stats: Dict):
        """Process individual log entries for cache analysis"""

        for entry in log_entries:
            cache_stats['total_requests'] += 1

            # Extract cache status
            cache_status = entry.get('x-edge-result-type', 'Unknown')
            cache_stats['cache_status_breakdown'][cache_status] = \
                cache_stats['cache_status_breakdown'].get(cache_status, 0) + 1

            # Count hits vs misses
            if cache_status in ['Hit', 'RefreshHit']:
                cache_stats['cache_hits'] += 1
            elif cache_status in ['Miss', 'Error', 'CapacityExceeded']:
                cache_stats['cache_misses'] += 1

                # Track missed paths
                path = entry.get('cs-uri-stem', '')
                cache_stats['top_missed_paths'][path] = \
                    cache_stats['top_missed_paths'].get(path, 0) + 1

            # Track status codes
            status_code = entry.get('sc-status', '000')
            cache_stats['status_codes'][status_code] = \
                cache_stats['status_codes'].get(status_code, 0) + 1

            # Track edge locations
            edge_location = entry.get('x-edge-location', 'Unknown')
            cache_stats['edge_locations'][edge_location] = \
                cache_stats['edge_locations'].get(edge_location, 0) + 1

            # Track user agents (simplified)
            user_agent = entry.get('cs(User-Agent)', '')
            ua_category = self.categorize_user_agent(user_agent)
            cache_stats['user_agents'][ua_category] = \
                cache_stats['user_agents'].get(ua_category, 0) + 1

            # Track request methods
            method = entry.get('cs-method', 'GET')
            cache_stats['request_methods'][method] = \
                cache_stats['request_methods'].get(method, 0) + 1

    def analyze_cache_misses(self, log_analysis: Dict) -> Dict[str, Any]:
        """Detailed analysis of cache misses"""

        miss_analysis = {
            'miss_patterns': {},
            'miss_by_file_type': {},
            'miss_by_path_pattern': {},
            'cacheable_misses': 0,
            'non_cacheable_misses': 0,
            'potential_savings': {}
        }

        # Analyze top missed paths
        for path, miss_count in log_analysis['top_missed_paths'].items():
            # Categorize by file type
            file_extension = self.get_file_extension(path)
            miss_analysis['miss_by_file_type'][file_extension] = \
                miss_analysis['miss_by_file_type'].get(file_extension, 0) + miss_count

            # Categorize by path pattern
            path_pattern = self.categorize_path(path)
            miss_analysis['miss_by_path_pattern'][path_pattern] = \
                miss_analysis['miss_by_path_pattern'].get(path_pattern, 0) + miss_count

            # Determine if potentially cacheable
            if self.is_potentially_cacheable(path):
                miss_analysis['cacheable_misses'] += miss_count
            else:
                miss_analysis['non_cacheable_misses'] += miss_count

        # Calculate potential cache savings
        total_misses = sum(log_analysis['top_missed_paths'].values())
        if total_misses > 0:
            miss_analysis['potential_savings'] = {
                'cacheable_miss_ratio': (miss_analysis['cacheable_misses'] / total_misses) * 100,
                'estimated_hit_ratio_improvement': self.estimate_hit_ratio_improvement(miss_analysis),
                'bandwidth_savings_potential': self.estimate_bandwidth_savings(miss_analysis, log_analysis)
            }

        return miss_analysis

    def generate_optimization_recommendations(self, dist_config: Dict,
                                            log_analysis: Dict,
                                            cache_analysis: Dict) -> List[Dict[str, str]]:
        """Generate specific optimization recommendations"""

        recommendations = []

        # Check cache hit ratio
        hit_ratio = log_analysis.get('hit_ratio', 0)
        if hit_ratio < 80:
            recommendations.append({
                'type': 'hit_ratio',
                'priority': 'high',
                'title': 'Low Cache Hit Ratio',
                'description': f'Current hit ratio is {hit_ratio:.1f}%. Target should be >80%.',
                'action': 'Review cache behaviors and TTL settings'
            })

        # Check for cacheable misses
        cacheable_misses = cache_analysis.get('cacheable_misses', 0)
        total_misses = sum(log_analysis['top_missed_paths'].values())

        if cacheable_misses > total_misses * 0.3:
            recommendations.append({
                'type': 'cache_behavior',
                'priority': 'high',
                'title': 'High Cacheable Miss Rate',
                'description': f'{cacheable_misses} cacheable requests are missing cache',
                'action': 'Add cache behaviors for static assets and API responses'
            })

        # Check for static asset misses
        static_misses = cache_analysis['miss_by_file_type']
        for ext, count in static_misses.items():
            if ext in ['.css', '.js', '.png', '.jpg', '.gif', '.svg'] and count > 100:
                recommendations.append({
                    'type': 'static_assets',
                    'priority': 'medium',
                    'title': f'Static Asset Misses ({ext})',
                    'description': f'{count} cache misses for {ext} files',
                    'action': f'Increase TTL for {ext} files or fix cache invalidation'
                })

        # Check query string handling
        query_string_paths = [path for path in log_analysis['top_missed_paths'].keys()
                             if '?' in path]
        if len(query_string_paths) > 10:
            recommendations.append({
                'type': 'query_strings',
                'priority': 'medium',
                'title': 'Query String Cache Misses',
                'description': f'{len(query_string_paths)} paths with query strings missing cache',
                'action': 'Configure query string forwarding or whitelist specific parameters'
            })

        # Check for geographic distribution issues
        edge_locations = log_analysis.get('edge_locations', {})
        if len(edge_locations) < 5:
            recommendations.append({
                'type': 'geographic',
                'priority': 'medium',
                'title': 'Limited Edge Location Usage',
                'description': f'Only {len(edge_locations)} edge locations serving traffic',
                'action': 'Review price class and geographic restrictions'
            })

        return recommendations

    def get_file_extension(self, path: str) -> str:
        """Extract file extension from path"""
        if '.' in path:
            return '.' + path.split('.')[-1].split('?')[0]
        return 'no_extension'

    def categorize_path(self, path: str) -> str:
        """Categorize path for pattern analysis"""
        if path.startswith('/api/'):
            return 'api'
        elif path.startswith('/static/') or path.startswith('/assets/'):
            return 'static_assets'
        elif path.startswith('/images/') or path.startswith('/img/'):
            return 'images'
        elif any(path.endswith(ext) for ext in ['.css', '.js', '.png', '.jpg', '.gif']):
            return 'static_files'
        else:
            return 'dynamic_content'

    def is_potentially_cacheable(self, path: str) -> bool:
        """Determine if a path is potentially cacheable"""
        # Static file extensions
        static_extensions = ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg',
                           '.ico', '.woff', '.woff2', '.ttf', '.pdf']

        if any(path.endswith(ext) for ext in static_extensions):
            return True

        # API endpoints that could be cached
        if path.startswith('/api/') and any(keyword in path for keyword in
                                          ['public', 'products', 'categories', 'config']):
            return True

        # Static paths
        if path.startswith(('/static/', '/assets/', '/public/')):
            return True

        return False

    def estimate_hit_ratio_improvement(self, cache_analysis: Dict) -> float:
        """Estimate potential hit ratio improvement"""
        cacheable_misses = cache_analysis.get('cacheable_misses', 0)
        total_misses = cacheable_misses + cache_analysis.get('non_cacheable_misses', 0)

        if total_misses == 0:
            return 0

        # Assume 70% of cacheable misses could become hits with optimization
        potential_new_hits = cacheable_misses * 0.7
        return (potential_new_hits / total_misses) * 100

    def get_distribution_config(self) -> Dict:
        """Get CloudFront distribution configuration"""
        try:
            response = self.cloudfront.get_distribution_config(Id=self.distribution_id)
            return response['DistributionConfig']
        except Exception as e:
            print(f"Error getting distribution config: {e}")
            return {}

    def categorize_user_agent(self, user_agent: str) -> str:
        """Categorize user agent for analysis"""
        if 'bot' in user_agent.lower() or 'crawler' in user_agent.lower():
            return 'bot'
        elif 'Mobile' in user_agent or 'Android' in user_agent:
            return 'mobile'
        elif 'curl' in user_agent.lower() or 'wget' in user_agent.lower():
            return 'script'
        else:
            return 'browser'

# Usage example
if __name__ == '__main__':
    analyzer = CloudFrontCacheAnalyzer('E1234567890123')
    analysis = analyzer.analyze_cache_performance(hours_back=24)

    print("CloudFront Cache Analysis Results:")
    print(f"Hit Ratio: {analysis['cache_performance']['hit_ratio']:.1f}%")
    print(f"Total Requests: {analysis['cache_performance']['total_requests']:,}")

    print("\nTop Recommendations:")
    for rec in analysis['optimization_recommendations'][:3]:
        print(f"- {rec['title']}: {rec['description']}")
```

### Fastly VCL: Advanced Cache Optimization
```vcl
# Fastly VCL configuration for optimized caching
vcl 4.0;

import std;
import header_manipulation;

# Backend configuration
backend origin {
    .host = "origin.example.com";
    .port = "80";
    .connect_timeout = 5s;
    .first_byte_timeout = 30s;
    .between_bytes_timeout = 10s;
}

# Cache configuration for different content types
table cache_configs {
    "static": "31536000", # 1 year for static assets
    "api": "300",         # 5 minutes for API responses
    "html": "3600",       # 1 hour for HTML pages
    "images": "2592000",  # 30 days for images
    "dynamic": "60"       # 1 minute for dynamic content
}

sub vcl_recv {
    # Normalize URL for better cache hit rates
    call normalize_url;

    # Handle cache-busting parameters
    call handle_cache_busting;

    # Set cache category based on request
    call categorize_request;

    # Custom cache key generation
    call generate_cache_key;

    return(lookup);
}

sub normalize_url {
    # Remove common tracking parameters
    set req.url = regsuball(req.url, "[?&](utm_[^&]*|fbclid|gclid|ref|source)=[^&]*", "");

    # Remove trailing slashes for consistency
    set req.url = regsub(req.url, "/$", "");

    # Sort query parameters for consistent cache keys
    if (req.url ~ "\?") {
        set req.http.X-Sorted-Query = std.querysort(req.url);
        set req.url = regsub(req.http.X-Sorted-Query, "^[^?]*", req.url.path);
    }
}

sub handle_cache_busting {
    # Handle version-based cache busting
    if (req.url ~ "\?v=\d+$") {
        set req.http.X-Cache-Bust-Version = regsub(req.url, ".*\?v=(\d+)$", "\1");
        set req.url = regsub(req.url, "\?v=\d+$", "");
    }

    # Handle hash-based cache busting
    if (req.url ~ "\?h=[a-f0-9]+$") {
        set req.http.X-Cache-Bust-Hash = regsub(req.url, ".*\?h=([a-f0-9]+)$", "\1");
        set req.url = regsub(req.url, "\?h=[a-f0-9]+$", "");
    }
}

sub categorize_request {
    # Categorize request for cache behavior
    if (req.url ~ "^/api/") {
        set req.http.X-Cache-Category = "api";
    } else if (req.url ~ "\.(css|js|png|jpg|jpeg|gif|svg|ico|woff|woff2)$") {
        set req.http.X-Cache-Category = "static";
    } else if (req.url ~ "\.(html|htm)$" || req.url ~ "^/$") {
        set req.http.X-Cache-Category = "html";
    } else if (req.url ~ "\.(png|jpg|jpeg|gif|svg|webp)") {
        set req.http.X-Cache-Category = "images";
    } else {
        set req.http.X-Cache-Category = "dynamic";
    }
}

sub generate_cache_key {
    # Base cache key
    set req.hash_always_miss = false;

    # Add device type to cache key for responsive content
    if (req.http.User-Agent ~ "(?i)(mobile|android|iphone|ipad)") {
        set req.http.X-Device-Type = "mobile";
    } else {
        set req.http.X-Device-Type = "desktop";
    }

    # Add geography for geo-targeted content
    if (req.url ~ "^/(api/|)location") {
        set req.http.X-Geo-Key = geoip.country_code;
    }

    # Add authentication state for personalized content
    if (req.http.Authorization || req.http.Cookie ~ "session=") {
        set req.http.X-Auth-State = "authenticated";
    } else {
        set req.http.X-Auth-State = "anonymous";
    }
}

sub vcl_hash {
    hash_data(req.url);
    hash_data(req.http.host);

    # Include device type in hash for responsive content
    if (req.http.X-Device-Type) {
        hash_data(req.http.X-Device-Type);
    }

    # Include geography for location-based content
    if (req.http.X-Geo-Key) {
        hash_data(req.http.X-Geo-Key);
    }

    # Include auth state for personalized content
    if (req.http.X-Auth-State) {
        hash_data(req.http.X-Auth-State);
    }

    return (lookup);
}

sub vcl_backend_response {
    # Set cache TTL based on content category
    if (beresp.status == 200) {
        set beresp.http.X-Cache-Category = bereq.http.X-Cache-Category;

        if (table.lookup(cache_configs, bereq.http.X-Cache-Category, "60")) {
            set beresp.ttl = std.duration(
                table.lookup(cache_configs, bereq.http.X-Cache-Category, "60") + "s",
                60s
            );
        }

        # Set appropriate cache control headers
        call set_cache_control_headers;
    }

    # Handle cache-busting headers
    if (bereq.http.X-Cache-Bust-Version) {
        set beresp.http.X-Cache-Version = bereq.http.X-Cache-Bust-Version;
    }

    # Enable streaming for large responses
    if (beresp.http.Content-Length ~ "^\d+$" &&
        std.integer(beresp.http.Content-Length, 0) > 1048576) { # 1MB
        set beresp.do_stream = true;
    }

    return(deliver);
}

sub set_cache_control_headers {
    if (bereq.http.X-Cache-Category == "static") {
        set beresp.http.Cache-Control = "public, max-age=31536000, immutable";
    } else if (bereq.http.X-Cache-Category == "images") {
        set beresp.http.Cache-Control = "public, max-age=2592000";
    } else if (bereq.http.X-Cache-Category == "api") {
        set beresp.http.Cache-Control = "public, max-age=300, s-maxage=300";
    } else if (bereq.http.X-Cache-Category == "html") {
        set beresp.http.Cache-Control = "public, max-age=3600, s-maxage=3600";
    } else {
        set beresp.http.Cache-Control = "public, max-age=60, s-maxage=60";
    }

    # Add Vary headers for content that varies by device/geo
    if (bereq.http.X-Device-Type || bereq.http.X-Geo-Key) {
        set beresp.http.Vary = "User-Agent";
        if (bereq.http.X-Geo-Key) {
            set beresp.http.Vary = beresp.http.Vary + ", CloudFront-Viewer-Country";
        }
    }
}

sub vcl_deliver {
    # Add cache debugging headers
    set resp.http.X-Cache-Status = obj.hits > 0 ? "HIT" : "MISS";
    set resp.http.X-Cache-Hits = obj.hits;
    set resp.http.X-Cache-Category = resp.http.X-Cache-Category;

    # Remove internal headers
    unset resp.http.X-Cache-Category;

    return(deliver);
}

sub vcl_miss {
    # Track cache misses for analysis
    std.log("cache_miss:url:" + req.url + ":category:" + req.http.X-Cache-Category);
    return(fetch);
}

sub vcl_hit {
    # Track cache hits for analysis
    std.log("cache_hit:url:" + req.url + ":age:" + obj.age);
    return(deliver);
}
```

## Monitoring and Alerting

### CDN Performance Metrics
```yaml
groups:
- name: cdn_cache_alerts
  rules:
  - alert: LowCDNCacheHitRatio
    expr: cdn_cache_hit_ratio < 80
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "CDN cache hit ratio is low"
      description: "Cache hit ratio is {{ $value }}%"

  - alert: HighCDNCacheMissRate
    expr: rate(cdn_cache_misses_total[5m]) > 100
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High CDN cache miss rate"
      description: "{{ $value }} cache misses per second"

  - alert: CDNOriginErrors
    expr: rate(cdn_origin_errors_total[5m]) > 10
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "CDN origin errors detected"
      description: "{{ $value }} origin errors per second"
```

## Success Metrics

- **Cache Hit Ratio**: > 85% for static content, > 70% overall
- **Origin Offload**: > 80% of requests served from cache
- **Cache Miss Latency**: < 200ms additional latency for misses
- **Geographic Coverage**: Content served from < 100ms RTT locations
- **Bandwidth Savings**: > 60% bandwidth reduction vs no CDN

## The 3 AM Test

**Scenario**: Your CDN cache hit ratio has dropped from 85% to 45% overnight, causing origin servers to be overwhelmed with traffic and users experiencing slow page loads worldwide.

**This guide provides**:
1. **Cache hit analysis**: Tools to identify why cache misses are occurring
2. **Configuration optimization**: Strategies to improve cache behaviors and TTL settings
3. **Cache key optimization**: Techniques to normalize URLs and improve cache efficiency
4. **Geographic analysis**: Investigation of edge location performance and coverage
5. **Real-time monitoring**: Setup for automated cache performance tracking and alerting

**Expected outcome**: Cache miss patterns identified within 15 minutes, immediate cache configuration fixes applied within 1 hour, hit ratio restored to 80%+ within 2 hours.