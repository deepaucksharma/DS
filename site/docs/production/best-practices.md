# Best Practices

Production-tested guidelines for building and operating distributed systems.

## Design Principles

### 1. Design for Failure

**Principle**: Assume every component will fail and design accordingly.

```python
# Good: Graceful degradation
def get_user_recommendations(user_id):
    try:
        recommendations = ml_service.get_recommendations(user_id)
        return recommendations
    except MLServiceUnavailable:
        # Fallback to popular items
        return catalog_service.get_popular_items()
    except Exception:
        # Ultimate fallback
        return []

# Bad: No error handling
def get_user_recommendations(user_id):
    return ml_service.get_recommendations(user_id)  # Will crash if service is down
```

**Implementation Checklist**:
- [ ] Circuit breakers on all external dependencies
- [ ] Timeouts on all network calls
- [ ] Retry logic with exponential backoff
- [ ] Fallback strategies for critical paths
- [ ] Bulkheads to isolate failures

### 2. Embrace Eventual Consistency

**Principle**: Strong consistency is expensive; use the weakest consistency model that meets your requirements.

```python
# Social media example - eventual consistency is fine
class SocialMediaFeed:
    def post_update(self, user_id, content):
        # Write to user's timeline immediately
        user_timeline.add_post(user_id, content)
        
        # Async propagate to followers (eventual)
        async_queue.enqueue(PropagateToFollowers(user_id, content))
        
        return PostCreated(post_id)

# Financial example - strong consistency required
class BankAccount:
    def transfer(self, from_account, to_account, amount):
        # Must be atomic - both succeed or both fail
        with database.transaction():
            from_balance = accounts.get_balance(from_account)
            if from_balance < amount:
                raise InsufficientFunds()
            
            accounts.debit(from_account, amount)
            accounts.credit(to_account, amount)
```

### 3. Make Services Stateless When Possible

**Principle**: Stateless services are easier to scale, deploy, and reason about.

```python
# Good: Stateless service
class OrderService:
    def __init__(self, database):
        self.db = database  # External state
    
    def process_order(self, order_request):
        # No local state - can run anywhere
        order = Order.from_request(order_request)
        order_id = self.db.save_order(order)
        return order_id

# Avoid: Stateful service  
class StatefulOrderService:
    def __init__(self):
        self.pending_orders = {}  # Local state
    
    def add_order(self, order):
        self.pending_orders[order.id] = order  # Tied to this instance
```

## Operational Excellence

### 1. Monitoring and Alerting

**The Golden Signals**: Monitor these four metrics for every service.

```python
class ServiceMetrics:
    def collect_golden_signals(self):
        return {
            # Latency: How long requests take
            'latency_p50': self.histogram.percentile(50),
            'latency_p95': self.histogram.percentile(95),
            'latency_p99': self.histogram.percentile(99),
            
            # Traffic: How many requests 
            'requests_per_second': self.counter.rate(),
            
            # Errors: Rate of failed requests
            'error_rate': self.errors.rate() / self.requests.rate(),
            
            # Saturation: How "full" the service is
            'cpu_utilization': system.cpu_percent(),
            'memory_utilization': system.memory_percent(),
            'queue_depth': self.queue.size()
        }
```

**Alert Design Principles**:

```yaml
alert_guidelines:
  actionable: "Every alert must have a clear action"
  avoid_alert_fatigue: "Tune thresholds to reduce false positives"
  escalation: "Escalate based on duration, not just threshold"
  
good_alert:
  name: "High Error Rate"
  condition: "error_rate > 5% for 5 minutes"
  action: "Check logs, recent deployments, dependency health"
  
bad_alert:
  name: "CPU High"  
  condition: "cpu > 80%"
  problem: "80% might be normal, no clear action"
```

### 2. Deployment Best Practices

**Blue-Green Deployment**:
```python
class BlueGreenDeployment:
    def deploy_new_version(self, new_version):
        # Deploy to green environment
        green_env.deploy(new_version)
        
        # Run health checks
        if not self.health_check(green_env):
            raise DeploymentFailed("Health checks failed")
        
        # Run smoke tests
        if not self.smoke_tests(green_env):
            raise DeploymentFailed("Smoke tests failed")
        
        # Switch traffic gradually
        self.gradually_shift_traffic(blue_env, green_env)
        
        # Monitor for regressions
        if self.detect_regression():
            self.rollback_traffic(green_env, blue_env)
            raise DeploymentFailed("Regression detected")
```

**Feature Flags for Safe Rollouts**:
```python
class FeatureFlag:
    def __init__(self, flag_name, rollout_percentage=0):
        self.flag_name = flag_name
        self.rollout_percentage = rollout_percentage
    
    def is_enabled(self, user_id):
        # Consistent hashing for stable rollout
        user_hash = hash(f"{self.flag_name}:{user_id}") % 100
        return user_hash < self.rollout_percentage
    
    def enable_for_percentage(self, percentage):
        # Gradual rollout: 1% → 5% → 25% → 50% → 100%
        self.rollout_percentage = percentage

# Usage
new_algorithm_flag = FeatureFlag("new_recommendation_algorithm")

def get_recommendations(user_id):
    if new_algorithm_flag.is_enabled(user_id):
        return new_recommendation_service.get(user_id)
    else:
        return legacy_recommendation_service.get(user_id)
```

### 3. Incident Response

**Runbook Template**:
```markdown
# Service X Incident Response

## Immediate Actions (First 5 minutes)
1. Acknowledge alert to stop noise
2. Check service dashboard for obvious issues
3. Verify recent deployments
4. Page on-call engineer if not already involved

## Investigation Steps
1. Check error logs for patterns
2. Verify dependency health
3. Check resource utilization (CPU, memory, disk)
4. Review recent configuration changes

## Common Issues and Solutions
- **High latency**: Check database connection pool, cache hit rates
- **Error spike**: Check recent deployments, dependency failures  
- **Memory issues**: Look for memory leaks, GC pressure
- **Disk full**: Clean up logs, expand storage

## Escalation
- Page senior engineer after 15 minutes
- Page team lead after 30 minutes
- Declare major incident after 1 hour
```

## Performance Best Practices

### 1. Caching Strategy

**Cache Patterns**:
```python
# Cache-aside pattern
class CacheAside:
    def get(self, key):
        # Try cache first
        value = cache.get(key)
        if value is not None:
            return value
        
        # Cache miss - get from database
        value = database.get(key)
        if value is not None:
            cache.set(key, value, ttl=300)  # 5 minute TTL
        
        return value
    
    def update(self, key, value):
        # Update database first
        database.update(key, value)
        
        # Invalidate cache
        cache.delete(key)

# Write-through pattern (for critical data)
class WriteThrough:
    def update(self, key, value):
        # Write to database and cache atomically
        with transaction():
            database.update(key, value)
            cache.set(key, value)
```

**Cache Invalidation Strategies**:
```python
# TTL-based (simple but can serve stale data)
cache.set(key, value, ttl=300)

# Event-based invalidation (more complex but accurate)
def on_user_updated(user_id):
    cache.delete(f"user:{user_id}")
    cache.delete(f"user_profile:{user_id}")

# Version-based invalidation (for distributed caches)
def cache_with_version(key, value):
    version = database.get_version(key)
    cache.set(f"{key}:v{version}", value)
```

### 2. Database Optimization

**Connection Pooling**:
```python
class DatabasePool:
    def __init__(self, max_connections=20):
        self.pool = ConnectionPool(
            max_connections=max_connections,
            # Don't hold connections too long
            max_idle_time=300,  
            # Validate connections before use
            test_on_borrow=True
        )
    
    def execute_query(self, query):
        with self.pool.get_connection() as conn:
            return conn.execute(query)
```

**Query Optimization**:
```python
# Good: Use indexes, limit results
def get_recent_orders(user_id, limit=10):
    return db.query("""
        SELECT * FROM orders 
        WHERE user_id = %s 
        ORDER BY created_at DESC 
        LIMIT %s
    """, [user_id, limit])

# Bad: Full table scan, no limits
def get_recent_orders(user_id):
    orders = db.query("SELECT * FROM orders")
    user_orders = [o for o in orders if o.user_id == user_id]
    return sorted(user_orders, key=lambda x: x.created_at, reverse=True)
```

### 3. Load Balancing

**Health Check Design**:
```python
class HealthCheck:
    def check_health(self):
        checks = {
            'database': self.check_database(),
            'cache': self.check_cache(),
            'disk_space': self.check_disk_space(),
            'memory': self.check_memory()
        }
        
        # Fail if any critical dependency is down
        if not checks['database']:
            return {'status': 'unhealthy', 'reason': 'database_down'}
        
        # Warn if non-critical issues
        warnings = []
        if not checks['cache']:
            warnings.append('cache_unavailable')
        
        return {'status': 'healthy', 'warnings': warnings}
    
    def check_database(self):
        try:
            # Simple query that touches the database
            db.execute("SELECT 1")
            return True
        except Exception:
            return False
```

## Security Best Practices

### 1. Authentication and Authorization

**JWT Token Validation**:
```python
import jwt
from datetime import datetime, timedelta

class JWTAuth:
    def __init__(self, secret_key):
        self.secret_key = secret_key
    
    def create_token(self, user_id, expiry_hours=24):
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=expiry_hours),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def validate_token(self, token):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload['user_id']
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")
```

### 2. Data Protection

**Encryption at Rest and in Transit**:
```python
# Database encryption
class EncryptedDatabase:
    def __init__(self, encryption_key):
        self.cipher = AES.new(encryption_key, AES.MODE_GCM)
    
    def store_sensitive_data(self, data):
        # Encrypt before storing
        encrypted_data, tag = self.cipher.encrypt_and_digest(data.encode())
        return database.store(encrypted_data + tag)
    
    def retrieve_sensitive_data(self, record_id):
        encrypted_data = database.get(record_id)
        tag = encrypted_data[-16:]  # Last 16 bytes
        ciphertext = encrypted_data[:-16]
        
        return self.cipher.decrypt_and_verify(ciphertext, tag).decode()

# HTTPS enforcement
def require_https(func):
    def wrapper(request, *args, **kwargs):
        if not request.is_secure():
            return redirect(f"https://{request.get_host()}{request.get_full_path()}")
        return func(request, *args, **kwargs)
    return wrapper
```

## Testing Best Practices

### 1. Test Pyramid

```python
# Unit tests (fast, isolated)
def test_calculate_tax():
    calculator = TaxCalculator()
    tax = calculator.calculate(amount=100, rate=0.08)
    assert tax == 8.0

# Integration tests (test component interactions)
def test_order_processing_flow():
    order_service = OrderService(database=test_db)
    payment_service = PaymentService(payment_gateway=mock_gateway)
    
    order = order_service.create_order(customer_id=123, items=[item1, item2])
    payment_result = payment_service.process_payment(order.total_amount)
    
    assert payment_result.success
    assert order.status == "paid"

# End-to-end tests (test full user flows)
def test_complete_checkout_flow():
    # Test with real browser automation
    browser.visit("/products/123")
    browser.click("Add to Cart")
    browser.visit("/checkout")
    browser.fill("credit_card", "4111111111111111")
    browser.click("Place Order")
    
    assert browser.text_contains("Order confirmed")
```

### 2. Chaos Engineering

```python
class ChaosExperiments:
    def kill_random_instance(self, service_name):
        """Test service resilience by killing random instances"""
        instances = self.get_service_instances(service_name)
        victim = random.choice(instances)
        
        self.monitor.start_experiment("kill_instance")
        self.kill_instance(victim)
        
        # Verify service remains available
        assert self.health_check(service_name).status == "healthy"
    
    def inject_network_latency(self, service_name, latency_ms=1000):
        """Test timeout handling by injecting latency"""
        self.network.add_latency(service_name, latency_ms)
        
        # Verify graceful degradation
        response_time = self.measure_response_time(service_name)
        assert response_time < 5000  # Should timeout and fallback quickly
```

## Key Takeaways

1. **Design for Failure**: Every component will fail; plan accordingly
2. **Monitor Everything**: You can't fix what you can't see
3. **Start Simple**: Avoid premature optimization and over-engineering
4. **Automate Relentlessly**: Reduce human error with automation
5. **Learn from Failures**: Blameless postmortems and continuous improvement
6. **Security by Design**: Build security in from the start, not as an afterthought
7. **Test at All Levels**: Unit, integration, end-to-end, and chaos testing
8. **Performance Matters**: Cache effectively, optimize databases, design for scale

Remember: these are guidelines, not rigid rules. Adapt them to your specific context, requirements, and constraints.