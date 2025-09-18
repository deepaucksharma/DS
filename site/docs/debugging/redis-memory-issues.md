# Redis Memory Issues - Analysis and Optimization Guide

## Overview

Systematic approaches to debugging Redis memory issues and optimizing memory usage. Based on production experiences from Twitter's Redis infrastructure, Instagram's caching layer, and Airbnb's session storage optimization.

## Memory Analysis Commands

### Basic Memory Investigation
```bash
# Check Redis memory usage
redis-cli INFO memory

# Get memory usage by database
redis-cli INFO keyspace

# Check specific key memory usage
redis-cli MEMORY USAGE key_name

# Get largest keys
redis-cli --bigkeys

# Sample keys for memory analysis
redis-cli --memkeys

# Check memory fragmentation
redis-cli INFO memory | grep fragmentation

# Get detailed memory breakdown
redis-cli MEMORY STATS
```

## Production Examples

### Twitter Redis: Timeline Cache Optimization
```python
#!/usr/bin/env python3
"""
Twitter-style Redis memory optimization for timeline caching
"""
import redis
import json
import zlib
import pickle
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class MemoryOptimizationResult:
    original_size: int
    optimized_size: int
    compression_ratio: float
    time_taken: float

class TwitterRedisMemoryOptimizer:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.compression_threshold = 1024  # 1KB
        self.max_timeline_age = timedelta(days=7)

    def analyze_memory_usage(self) -> Dict[str, Any]:
        """Comprehensive memory analysis"""
        info = self.redis.info('memory')
        keyspace = self.redis.info('keyspace')

        analysis = {
            'total_memory': info['used_memory'],
            'total_memory_human': info['used_memory_human'],
            'memory_fragmentation_ratio': info['mem_fragmentation_ratio'],
            'memory_efficiency': info.get('mem_efficiency', 'N/A'),
            'key_analysis': {},
            'recommendations': []
        }

        # Analyze key patterns
        key_patterns = self.analyze_key_patterns()
        analysis['key_analysis'] = key_patterns

        # Generate recommendations
        analysis['recommendations'] = self.generate_memory_recommendations(info, key_patterns)

        return analysis

    def analyze_key_patterns(self) -> Dict[str, Any]:
        """Analyze Redis key patterns for memory optimization"""
        patterns = {
            'timeline:': {'count': 0, 'total_memory': 0, 'avg_size': 0},
            'user:': {'count': 0, 'total_memory': 0, 'avg_size': 0},
            'tweet:': {'count': 0, 'total_memory': 0, 'avg_size': 0},
            'session:': {'count': 0, 'total_memory': 0, 'avg_size': 0},
            'cache:': {'count': 0, 'total_memory': 0, 'avg_size': 0}
        }

        # Sample keys for analysis (Redis SCAN is more memory-efficient than KEYS *)
        cursor = 0
        sample_size = 0
        max_samples = 10000

        while cursor != 0 or sample_size == 0:
            cursor, keys = self.redis.scan(cursor=cursor, count=100)

            for key in keys:
                if sample_size >= max_samples:
                    break

                key_str = key.decode('utf-8') if isinstance(key, bytes) else key
                memory_usage = self.redis.memory_usage(key)

                # Categorize by pattern
                for pattern in patterns:
                    if key_str.startswith(pattern):
                        patterns[pattern]['count'] += 1
                        patterns[pattern]['total_memory'] += memory_usage
                        break

                sample_size += 1

            if sample_size >= max_samples:
                break

        # Calculate averages
        for pattern, stats in patterns.items():
            if stats['count'] > 0:
                stats['avg_size'] = stats['total_memory'] / stats['count']

        return patterns

    def optimize_timeline_storage(self, user_id: str, timeline_data: List[Dict]) -> MemoryOptimizationResult:
        """Optimize timeline storage with compression and efficient data structures"""
        start_time = time.time()

        # Original storage method
        original_key = f"timeline:{user_id}"
        original_data = json.dumps(timeline_data)
        original_size = len(original_data.encode('utf-8'))

        # Optimization 1: Remove old tweets
        current_time = datetime.utcnow()
        filtered_timeline = []

        for tweet in timeline_data:
            tweet_time = datetime.fromisoformat(tweet.get('created_at', '1970-01-01'))
            if current_time - tweet_time <= self.max_timeline_age:
                # Optimization 2: Remove unnecessary fields
                optimized_tweet = {
                    'id': tweet['id'],
                    'text': tweet.get('text', '')[:280],  # Truncate to Twitter limit
                    'user_id': tweet['user_id'],
                    'created_at': tweet['created_at'],
                    'metrics': {
                        'likes': tweet.get('likes', 0),
                        'retweets': tweet.get('retweets', 0)
                    }
                }
                filtered_timeline.append(optimized_tweet)

        # Optimization 3: Use more efficient serialization
        optimized_data = pickle.dumps(filtered_timeline, protocol=pickle.HIGHEST_PROTOCOL)

        # Optimization 4: Compress if beneficial
        if len(optimized_data) > self.compression_threshold:
            compressed_data = zlib.compress(optimized_data, level=6)
            if len(compressed_data) < len(optimized_data) * 0.9:  # Only if >10% savings
                final_data = b'COMPRESSED:' + compressed_data
                optimized_key = f"timeline:c:{user_id}"
            else:
                final_data = optimized_data
                optimized_key = f"timeline:o:{user_id}"
        else:
            final_data = optimized_data
            optimized_key = f"timeline:o:{user_id}"

        # Store optimized data
        self.redis.set(optimized_key, final_data, ex=int(self.max_timeline_age.total_seconds()))

        # Clean up old key if different
        if optimized_key != original_key and self.redis.exists(original_key):
            self.redis.delete(original_key)

        optimized_size = len(final_data)
        time_taken = time.time() - start_time

        return MemoryOptimizationResult(
            original_size=original_size,
            optimized_size=optimized_size,
            compression_ratio=original_size / optimized_size if optimized_size > 0 else 1,
            time_taken=time_taken
        )

    def retrieve_optimized_timeline(self, user_id: str) -> Optional[List[Dict]]:
        """Retrieve and decompress timeline data"""
        # Try different key formats
        for key_prefix in [f"timeline:c:{user_id}", f"timeline:o:{user_id}", f"timeline:{user_id}"]:
            data = self.redis.get(key_prefix)
            if data:
                try:
                    if data.startswith(b'COMPRESSED:'):
                        # Decompress
                        compressed_data = data[11:]  # Remove 'COMPRESSED:' prefix
                        decompressed_data = zlib.decompress(compressed_data)
                        return pickle.loads(decompressed_data)
                    elif key_prefix.startswith("timeline:o:"):
                        # Pickled but not compressed
                        return pickle.loads(data)
                    else:
                        # JSON format (legacy)
                        return json.loads(data.decode('utf-8'))
                except Exception as e:
                    print(f"Error retrieving timeline for {user_id}: {e}")
                    continue

        return None

    def cleanup_expired_keys(self) -> Dict[str, int]:
        """Clean up expired and unnecessary keys"""
        cleanup_stats = {
            'deleted_keys': 0,
            'freed_memory': 0,
            'processed_keys': 0
        }

        cursor = 0
        batch_size = 1000

        while True:
            cursor, keys = self.redis.scan(cursor=cursor, count=batch_size)

            for key in keys:
                cleanup_stats['processed_keys'] += 1
                key_str = key.decode('utf-8') if isinstance(key, bytes) else key

                # Check if key should be cleaned up
                should_delete = False
                memory_before = 0

                # Get memory usage before deletion
                try:
                    memory_before = self.redis.memory_usage(key)
                except:
                    memory_before = 0

                # Clean up based on patterns
                if key_str.startswith('session:'):
                    # Check if session is expired
                    ttl = self.redis.ttl(key)
                    if ttl == -1:  # No TTL set
                        self.redis.expire(key, 3600)  # Set 1 hour TTL
                    elif ttl == -2:  # Key doesn't exist
                        should_delete = True

                elif key_str.startswith('cache:temp:'):
                    # Temporary cache keys older than 1 hour
                    ttl = self.redis.ttl(key)
                    if ttl == -1 or ttl > 3600:
                        self.redis.expire(key, 3600)

                elif key_str.startswith('timeline:') and not key_str.startswith(('timeline:c:', 'timeline:o:')):
                    # Old format timeline keys
                    should_delete = True

                if should_delete:
                    self.redis.delete(key)
                    cleanup_stats['deleted_keys'] += 1
                    cleanup_stats['freed_memory'] += memory_before

            if cursor == 0:
                break

        return cleanup_stats

    def optimize_data_structures(self) -> Dict[str, Any]:
        """Optimize Redis data structures for memory efficiency"""
        optimizations = {
            'hash_optimizations': 0,
            'list_optimizations': 0,
            'set_optimizations': 0,
            'memory_saved': 0
        }

        cursor = 0
        while True:
            cursor, keys = self.redis.scan(cursor=cursor, count=100)

            for key in keys:
                key_str = key.decode('utf-8') if isinstance(key, bytes) else key
                key_type = self.redis.type(key).decode('utf-8')

                memory_before = self.redis.memory_usage(key)

                if key_type == 'hash' and key_str.startswith('user:'):
                    # Optimize user data storage
                    self.optimize_user_hash(key_str)
                    optimizations['hash_optimizations'] += 1

                elif key_type == 'list' and key_str.startswith('notifications:'):
                    # Optimize notification lists
                    self.optimize_notification_list(key_str)
                    optimizations['list_optimizations'] += 1

                elif key_type == 'set' and key_str.startswith('followers:'):
                    # Optimize follower sets
                    self.optimize_follower_set(key_str)
                    optimizations['set_optimizations'] += 1

                memory_after = self.redis.memory_usage(key)
                optimizations['memory_saved'] += max(0, memory_before - memory_after)

            if cursor == 0:
                break

        return optimizations

    def optimize_user_hash(self, key: str):
        """Optimize user hash storage"""
        user_data = self.redis.hgetall(key)

        # Convert to more memory-efficient format
        optimized_data = {}

        for field, value in user_data.items():
            field_str = field.decode('utf-8') if isinstance(field, bytes) else field
            value_str = value.decode('utf-8') if isinstance(value, bytes) else value

            # Store only essential fields
            if field_str in ['id', 'username', 'display_name', 'avatar_url', 'verified', 'followers_count']:
                optimized_data[field_str] = value_str

        # Replace with optimized data
        pipe = self.redis.pipeline()
        pipe.delete(key)
        for field, value in optimized_data.items():
            pipe.hset(key, field, value)
        pipe.expire(key, 86400)  # 24 hour TTL
        pipe.execute()

    def generate_memory_recommendations(self, memory_info: Dict, key_patterns: Dict) -> List[str]:
        """Generate memory optimization recommendations"""
        recommendations = []

        # Check fragmentation
        if memory_info['mem_fragmentation_ratio'] > 1.5:
            recommendations.append(
                f"High memory fragmentation ({memory_info['mem_fragmentation_ratio']:.2f}). "
                "Consider running MEMORY PURGE or restarting Redis during maintenance window."
            )

        # Check for large key patterns
        for pattern, stats in key_patterns.items():
            if stats['avg_size'] > 10000:  # 10KB average
                recommendations.append(
                    f"Pattern '{pattern}' has large average key size ({stats['avg_size']:,.0f} bytes). "
                    "Consider compression or data structure optimization."
                )

        # Check total memory usage
        total_memory_mb = memory_info['used_memory'] / (1024 * 1024)
        if total_memory_mb > 1000:  # 1GB
            recommendations.append(
                f"High memory usage ({total_memory_mb:.0f} MB). "
                "Consider implementing TTLs, data compression, or scaling to multiple instances."
            )

        return recommendations

    def generate_memory_report(self) -> Dict[str, Any]:
        """Generate comprehensive memory report"""
        analysis = self.analyze_memory_usage()

        # Run optimizations
        cleanup_stats = self.cleanup_expired_keys()
        optimization_stats = self.optimize_data_structures()

        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'memory_analysis': analysis,
            'cleanup_performed': cleanup_stats,
            'optimizations_performed': optimization_stats,
            'summary': {
                'total_memory_freed': cleanup_stats['freed_memory'] + optimization_stats['memory_saved'],
                'keys_optimized': (
                    cleanup_stats['deleted_keys'] +
                    optimization_stats['hash_optimizations'] +
                    optimization_stats['list_optimizations'] +
                    optimization_stats['set_optimizations']
                ),
                'fragmentation_ratio': analysis['memory_fragmentation_ratio']
            }
        }

        return report

# Usage example
if __name__ == '__main__':
    # Connect to Redis
    redis_client = redis.Redis(host='localhost', port=6379, db=0)

    # Initialize optimizer
    optimizer = TwitterRedisMemoryOptimizer(redis_client)

    # Generate memory report
    report = optimizer.generate_memory_report()

    print("Redis Memory Optimization Report:")
    print(f"Total Memory Freed: {report['summary']['total_memory_freed']:,} bytes")
    print(f"Keys Optimized: {report['summary']['keys_optimized']}")
    print(f"Memory Fragmentation: {report['summary']['fragmentation_ratio']:.2f}")

    # Print recommendations
    print("\nRecommendations:")
    for rec in report['memory_analysis']['recommendations']:
        print(f"- {rec}")
```

### Instagram Redis: Session Storage Optimization
```ruby
# Instagram-style Redis session optimization
class InstagramRedisSessionOptimizer
  def initialize(redis_client)
    @redis = redis_client
    @session_ttl = 30.days
    @compression_threshold = 512
  end

  def analyze_session_memory_usage
    analysis = {
      total_sessions: 0,
      total_memory: 0,
      compressed_sessions: 0,
      uncompressed_sessions: 0,
      average_session_size: 0,
      size_distribution: Hash.new(0)
    }

    # Scan session keys
    @redis.scan_each(match: "session:*", count: 1000) do |key|
      memory_usage = @redis.memory_usage(key)

      analysis[:total_sessions] += 1
      analysis[:total_memory] += memory_usage

      # Check if compressed
      if key.start_with?("session:c:")
        analysis[:compressed_sessions] += 1
      else
        analysis[:uncompressed_sessions] += 1
      end

      # Size distribution
      size_bucket = case memory_usage
                   when 0..512 then "0-512B"
                   when 513..1024 then "512B-1KB"
                   when 1025..5120 then "1-5KB"
                   when 5121..10240 then "5-10KB"
                   else "10KB+"
                   end

      analysis[:size_distribution][size_bucket] += 1
    end

    if analysis[:total_sessions] > 0
      analysis[:average_session_size] = analysis[:total_memory] / analysis[:total_sessions]
    end

    analysis
  end

  def optimize_session_storage(session_id, session_data)
    original_size = session_data.to_json.bytesize

    # Step 1: Remove unnecessary data
    optimized_data = optimize_session_data(session_data)

    # Step 2: Use efficient serialization
    serialized_data = MessagePack.pack(optimized_data)

    # Step 3: Compress if beneficial
    if serialized_data.bytesize > @compression_threshold
      compressed_data = Zlib::Deflate.deflate(serialized_data, Zlib::BEST_COMPRESSION)

      if compressed_data.bytesize < serialized_data.bytesize * 0.8
        # Compression worth it
        key = "session:c:#{session_id}"
        final_data = compressed_data
      else
        key = "session:o:#{session_id}"
        final_data = serialized_data
      end
    else
      key = "session:o:#{session_id}"
      final_data = serialized_data
    end

    # Store with TTL
    @redis.setex(key, @session_ttl, final_data)

    # Clean up old session if exists
    cleanup_old_session_keys(session_id)

    {
      original_size: original_size,
      optimized_size: final_data.bytesize,
      compression_ratio: original_size.to_f / final_data.bytesize,
      key_format: key.split(':')[1] # 'c' for compressed, 'o' for optimized
    }
  end

  def retrieve_session(session_id)
    # Try different key formats
    %W[session:c:#{session_id} session:o:#{session_id} session:#{session_id}].each do |key|
      data = @redis.get(key)
      next unless data

      begin
        case key.split(':')[1]
        when 'c'
          # Compressed
          decompressed = Zlib::Inflate.inflate(data)
          return MessagePack.unpack(decompressed)
        when 'o'
          # Optimized but not compressed
          return MessagePack.unpack(data)
        else
          # Legacy JSON format
          return JSON.parse(data)
        end
      rescue => e
        Rails.logger.warn "Failed to parse session #{session_id} from #{key}: #{e}"
        next
      end
    end

    nil
  end

  private

  def optimize_session_data(session_data)
    optimized = {}

    # Keep only essential session data
    essential_keys = %w[
      user_id username csrf_token last_activity
      preferences theme language timezone
    ]

    essential_keys.each do |key|
      optimized[key] = session_data[key] if session_data.key?(key)
    end

    # Compress user preferences if present
    if session_data['preferences'].is_a?(Hash)
      optimized['preferences'] = compress_preferences(session_data['preferences'])
    end

    # Store only recent activity (last 10 items)
    if session_data['recent_activity'].is_a?(Array)
      optimized['recent_activity'] = session_data['recent_activity'].last(10)
    end

    optimized
  end

  def compress_preferences(preferences)
    # Convert boolean preferences to bit flags
    compressed = {}

    boolean_prefs = %w[
      dark_mode email_notifications push_notifications
      show_activity_status auto_play_videos
    ]

    bit_flags = 0
    boolean_prefs.each_with_index do |pref, index|
      bit_flags |= (1 << index) if preferences[pref]
    end

    compressed['flags'] = bit_flags

    # Keep non-boolean preferences as-is
    preferences.each do |key, value|
      unless boolean_prefs.include?(key)
        compressed[key] = value
      end
    end

    compressed
  end

  def cleanup_old_session_keys(session_id)
    # Remove old format keys
    old_keys = [
      "session:#{session_id}",
      "user_session:#{session_id}",
      "sess:#{session_id}"
    ]

    old_keys.each do |key|
      @redis.del(key) if @redis.exists(key)
    end
  end

  def cleanup_expired_sessions
    deleted_count = 0
    freed_memory = 0

    @redis.scan_each(match: "session:*", count: 1000) do |key|
      ttl = @redis.ttl(key)

      case ttl
      when -2
        # Key doesn't exist (race condition)
        next
      when -1
        # No TTL set - add one
        @redis.expire(key, @session_ttl)
      when 0..3600
        # Expiring soon - check if active
        unless session_recently_active?(key)
          memory_before = @redis.memory_usage(key)
          @redis.del(key)
          deleted_count += 1
          freed_memory += memory_before
        end
      end
    end

    {
      deleted_sessions: deleted_count,
      freed_memory: freed_memory
    }
  end

  def session_recently_active?(session_key)
    session_data = @redis.get(session_key)
    return false unless session_data

    begin
      # Parse session to check last activity
      parsed_data = case session_key.split(':')[1]
                   when 'c'
                     MessagePack.unpack(Zlib::Inflate.inflate(session_data))
                   when 'o'
                     MessagePack.unpack(session_data)
                   else
                     JSON.parse(session_data)
                   end

      last_activity = Time.parse(parsed_data['last_activity'])
      last_activity > 1.hour.ago
    rescue
      false
    end
  end

  def generate_optimization_report
    analysis = analyze_session_memory_usage
    cleanup_stats = cleanup_expired_sessions

    report = {
      timestamp: Time.current,
      session_analysis: analysis,
      cleanup_performed: cleanup_stats,
      recommendations: generate_recommendations(analysis)
    }

    # Log report
    Rails.logger.info "Redis Session Optimization Report: #{report.to_json}"

    report
  end

  def generate_recommendations(analysis)
    recommendations = []

    if analysis[:uncompressed_sessions] > analysis[:compressed_sessions]
      recommendations << "Consider migrating more sessions to compressed format"
    end

    if analysis[:average_session_size] > 2048
      recommendations << "Average session size is large (#{analysis[:average_session_size]} bytes). Review session data structure."
    end

    if analysis[:size_distribution]["10KB+"] > analysis[:total_sessions] * 0.1
      recommendations << "More than 10% of sessions are larger than 10KB. Investigate large session data."
    end

    recommendations
  end
end

# Usage
redis = Redis.new(url: ENV['REDIS_URL'])
optimizer = InstagramRedisSessionOptimizer.new(redis)

# Generate optimization report
report = optimizer.generate_optimization_report
puts "Session optimization completed:"
puts "- Total sessions: #{report[:session_analysis][:total_sessions]}"
puts "- Average size: #{report[:session_analysis][:average_session_size]} bytes"
puts "- Deleted expired: #{report[:cleanup_performed][:deleted_sessions]}"
puts "- Memory freed: #{report[:cleanup_performed][:freed_memory]} bytes"
```

## Monitoring and Alerting

### Redis Memory Alerts
```yaml
groups:
- name: redis_memory_alerts
  rules:
  - alert: RedisHighMemoryUsage
    expr: redis_memory_used_bytes / redis_memory_max_bytes > 0.8
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Redis memory usage is high"
      description: "Memory usage is {{ $value | humanizePercentage }}"

  - alert: RedisMemoryFragmentation
    expr: redis_memory_fragmentation_ratio > 2.0
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "High Redis memory fragmentation"
      description: "Fragmentation ratio is {{ $value }}"

  - alert: RedisSlowQueries
    expr: increase(redis_slowlog_length[5m]) > 10
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "Redis slow queries detected"
      description: "{{ $value }} slow queries in last 5 minutes"
```

## Success Metrics

- **Memory Efficiency**: > 80% useful data vs total memory
- **Fragmentation Ratio**: < 1.5 under normal load
- **Compression Ratio**: > 2:1 for large objects
- **Key Expiration**: > 95% of keys have appropriate TTLs
- **Memory Growth Rate**: < 10% per month under normal growth

## The 3 AM Test

**Scenario**: Your Redis cluster is consuming 95% of available memory, experiencing high fragmentation, and some instances are hitting OOM conditions causing cache misses and degraded application performance.

**This guide provides**:
1. **Memory analysis**: Tools to identify memory usage patterns and largest consumers
2. **Data optimization**: Compression and efficient serialization strategies
3. **Key lifecycle management**: TTL optimization and cleanup procedures
4. **Fragmentation resolution**: Techniques to reduce memory fragmentation
5. **Monitoring setup**: Automated tracking of memory usage patterns and alerting

**Expected outcome**: Memory usage patterns identified within 10 minutes, immediate cleanup reducing usage by 20-30%, comprehensive optimization deployed within 2 hours reducing memory footprint by 50%+.