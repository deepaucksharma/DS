# Common Pitfalls

Learn from the mistakes others have made in distributed systems.

## Design Anti-Patterns

### 1. Distributed Monolith

**Anti-Pattern**: Creating microservices that are tightly coupled and must be deployed together.

```python
# Bad: Tight coupling between services
class OrderService:
    def create_order(self, order_data):
        # Direct synchronous calls to many services
        customer = customer_service.get_customer(order_data.customer_id)  # Sync call
        inventory = inventory_service.reserve_items(order_data.items)     # Sync call  
        pricing = pricing_service.calculate_total(order_data.items)       # Sync call
        payment = payment_service.charge(customer.payment_method, pricing.total)  # Sync call
        
        if not all([customer, inventory, pricing, payment]):
            # Compensate for failures - complex cleanup logic
            self.rollback_everything(customer, inventory, pricing, payment)
            raise OrderCreationFailed()
        
        return self.save_order(order_data)
```

**Problems**:
- All services must be available for any order to succeed
- Changes in one service break others
- Can't deploy services independently
- Single point of failure

**Better Approach**:
```python
# Good: Loose coupling with eventual consistency
class OrderService:
    def create_order(self, order_data):
        # Create order in pending state
        order = Order(order_data, status='pending')
        self.save_order(order)
        
        # Publish event for async processing
        self.event_bus.publish(OrderCreated(order.id, order_data))
        
        return order.id

# Separate handlers process asynchronously
class OrderEventHandler:
    def handle_order_created(self, event):
        # Each step can fail independently and retry
        try:
            inventory_service.reserve_items_async(event.order_id, event.items)
        except Exception:
            self.schedule_retry(event, delay=30)
```

### 2. Chatty APIs

**Anti-Pattern**: Making multiple API calls to render a single page.

```python
# Bad: N+1 query problem in microservices
class UserProfileController:
    def get_user_profile(self, user_id):
        user = user_service.get_user(user_id)           # 1 call
        
        posts = []
        for post_id in user.recent_post_ids:           # N calls
            post = post_service.get_post(post_id)
            posts.append(post)
        
        friends = []
        for friend_id in user.friend_ids:              # M calls  
            friend = user_service.get_user(friend_id)
            friends.append(friend)
        
        return UserProfile(user, posts, friends)
```

**Problems**:
- High latency due to multiple network calls
- Increased failure probability (more calls = more chances to fail)
- Resource waste

**Better Approaches**:
```python
# Option 1: Batch APIs
class UserProfileController:
    def get_user_profile(self, user_id):
        user = user_service.get_user(user_id)
        
        # Batch calls reduce round trips
        posts = post_service.get_posts_batch(user.recent_post_ids)
        friends = user_service.get_users_batch(user.friend_ids)
        
        return UserProfile(user, posts, friends)

# Option 2: Composite API / Backend for Frontend (BFF)
class UserProfileBFF:
    def get_user_profile(self, user_id):
        # Single call returns all needed data
        return profile_composite_service.get_complete_profile(user_id)
```

### 3. Shared Database Anti-Pattern

**Anti-Pattern**: Multiple services sharing the same database.

```python
# Bad: Services coupled through shared database
class OrderService:
    def create_order(self, order_data):
        # Direct database access
        with shared_db.transaction():
            order_id = shared_db.insert('orders', order_data)
            shared_db.update('inventory', {'quantity': 'quantity - %s'}, [order_data.quantity])
            shared_db.insert('notifications', {'user_id': order_data.customer_id, 'type': 'order_created'})

class InventoryService:
    def update_inventory(self, product_id, quantity):
        # Both services touching same table
        shared_db.update('inventory', {'quantity': quantity}, {'product_id': product_id})
```

**Problems**:
- Database becomes coupling point
- Schema changes affect multiple services
- Hard to scale services independently
- Shared database becomes bottleneck

**Better Approach**:
```python
# Good: Database per service + events
class OrderService:
    def __init__(self):
        self.order_db = OrderDatabase()  # Own database
    
    def create_order(self, order_data):
        order = self.order_db.save_order(order_data)
        
        # Communicate via events, not shared data
        self.event_bus.publish(OrderCreated(order.id, order_data))
        
        return order

class InventoryService:
    def __init__(self):
        self.inventory_db = InventoryDatabase()  # Own database
    
    def handle_order_created(self, event):
        # Update own database based on events
        self.inventory_db.reserve_items(event.items)
```

## Implementation Anti-Patterns

### 4. Synchronous Communication Everywhere

**Anti-Pattern**: Using synchronous calls for everything.

```python
# Bad: Synchronous chain of calls
class CheckoutService:
    def checkout(self, cart_id):
        cart = cart_service.get_cart(cart_id)                    # Sync - 50ms
        customer = customer_service.get_customer(cart.user_id)   # Sync - 30ms
        payment = payment_service.charge(customer, cart.total)   # Sync - 200ms
        inventory = inventory_service.reserve(cart.items)        # Sync - 100ms
        shipping = shipping_service.create_label(customer.address) # Sync - 150ms
        
        # Total latency: 530ms, failure probability multiplied
        return Order(cart, customer, payment, inventory, shipping)
```

**Problems**:
- High latency (sum of all calls)
- High failure probability (chain fails if any link fails)
- Resource waste (threads blocked waiting)
- Poor user experience

**Better Approach**:
```python
# Good: Async processing with immediate response
class CheckoutService:
    def checkout(self, cart_id):
        # Immediate response to user
        order = Order(cart_id, status='processing')
        self.order_db.save(order)
        
        # Async processing
        self.queue.enqueue(ProcessCheckout(order.id))
        
        return order.id  # Fast response ~10ms

class CheckoutProcessor:
    def process_checkout(self, order_id):
        # Process steps asynchronously
        # Can retry individual steps on failure
        # Can parallelize independent operations
        pass
```

### 5. No Timeout Configuration

**Anti-Pattern**: Not setting timeouts on network calls.

```python
# Bad: No timeouts
def call_external_service(data):
    response = requests.post('http://external-api/endpoint', json=data)
    return response.json()
```

**Problems**:
- Calls can hang forever
- Resources exhausted by hanging connections
- Cascading failures when service becomes slow

**Better Approach**:
```python
# Good: Proper timeout configuration
class ExternalServiceClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = (5, 30)  # 5s connect, 30s read
        
    def call_service(self, data):
        try:
            response = self.session.post(
                'http://external-api/endpoint',
                json=data,
                timeout=10  # Overall timeout
            )
            return response.json()
        except requests.Timeout:
            raise ServiceUnavailableError("External service timeout")
```

### 6. Retry Storms

**Anti-Pattern**: Immediate retries without backoff.

```python
# Bad: Aggressive retries causing storms
def unreliable_operation():
    max_retries = 10
    for attempt in range(max_retries):
        try:
            return external_api.call()
        except Exception:
            if attempt == max_retries - 1:
                raise
            # No delay - retry immediately
            continue
```

**Problems**:
- Creates retry storms that overwhelm failing service
- Prevents service recovery
- Wastes resources

**Better Approach**:
```python
# Good: Exponential backoff with jitter
import random
import time

def reliable_operation():
    max_retries = 5
    base_delay = 1
    
    for attempt in range(max_retries):
        try:
            return external_api.call()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            # Exponential backoff with jitter
            delay = (base_delay * (2 ** attempt)) + random.uniform(0, 1)
            time.sleep(min(delay, 60))  # Cap at 60 seconds
```

## Operational Anti-Patterns

### 7. Logging Sensitive Data

**Anti-Pattern**: Logging passwords, tokens, or personal data.

```python
# Bad: Logging sensitive information
def authenticate_user(username, password):
    logger.info(f"Login attempt for user {username} with password {password}")
    
    token = auth_service.authenticate(username, password)
    logger.info(f"Generated token: {token}")
    
    return token
```

**Problems**:
- Security violation
- Compliance issues (GDPR, PCI-DSS)
- Data leakage risk

**Better Approach**:
```python
# Good: Sanitized logging
def authenticate_user(username, password):
    logger.info(f"Login attempt for user {username}")
    
    try:
        token = auth_service.authenticate(username, password)
        logger.info(f"Authentication successful for user {username}")
        return token
    except AuthenticationError:
        logger.warning(f"Authentication failed for user {username}")
        raise
```

### 8. No Circuit Breakers

**Anti-Pattern**: No protection against cascading failures.

```python
# Bad: No failure protection
class OrderService:
    def create_order(self, order_data):
        # If payment service is down, this will keep trying
        payment_result = payment_service.charge(order_data.payment_info)
        
        if not payment_result.success:
            raise PaymentFailedError()
        
        return self.save_order(order_data)
```

**Problems**:
- Cascading failures when dependencies go down
- Resource exhaustion
- Poor user experience (long timeouts)

**Better Approach**:
```python
# Good: Circuit breaker protection
class OrderService:
    def __init__(self):
        self.payment_circuit = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60
        )
    
    def create_order(self, order_data):
        try:
            payment_result = self.payment_circuit.call(
                payment_service.charge, 
                order_data.payment_info
            )
        except CircuitBreakerOpenError:
            # Fail fast instead of waiting
            raise PaymentServiceUnavailableError()
        
        return self.save_order(order_data)
```

### 9. Inadequate Monitoring

**Anti-Pattern**: Only monitoring basic metrics like CPU and memory.

```python
# Bad: Basic monitoring only
def monitor_service():
    return {
        'cpu_usage': get_cpu_usage(),
        'memory_usage': get_memory_usage(),
        'disk_usage': get_disk_usage()
    }
```

**Problems**:
- Can't detect business logic failures
- No insight into user experience
- Hard to troubleshoot issues

**Better Approach**:
```python
# Good: Business metrics + technical metrics
class ServiceMonitoring:
    def get_health_metrics(self):
        return {
            # Technical metrics
            'cpu_usage': get_cpu_usage(),
            'memory_usage': get_memory_usage(),
            
            # Business metrics
            'orders_per_minute': self.get_orders_rate(),
            'order_success_rate': self.get_success_rate(),
            'average_order_value': self.get_avg_order_value(),
            
            # Performance metrics
            'response_time_p95': self.get_latency_p95(),
            'error_rate': self.get_error_rate(),
            
            # Dependencies
            'database_connection_pool_usage': self.get_db_pool_usage(),
            'external_api_success_rate': self.get_external_api_rate()
        }
```

## Data Anti-Patterns

### 10. Event Ordering Assumptions

**Anti-Pattern**: Assuming events arrive in order.

```python
# Bad: Assuming event order
class AccountEventHandler:
    def handle_event(self, event):
        if event.type == 'AccountCreated':
            self.create_account(event.account_id)
        elif event.type == 'AccountUpdated':
            # This might arrive before AccountCreated!
            self.update_account(event.account_id, event.data)
```

**Problems**:
- Events can arrive out of order
- Network partitions can cause reordering
- Data corruption

**Better Approach**:
```python
# Good: Handle out-of-order events
class AccountEventHandler:
    def handle_event(self, event):
        account = self.get_or_create_account(event.account_id)
        
        # Use event timestamps and version numbers
        if event.timestamp <= account.last_updated:
            logger.info(f"Ignoring out-of-order event {event.id}")
            return
        
        if event.type == 'AccountCreated':
            self.create_account(event.account_id)
        elif event.type == 'AccountUpdated':
            self.update_account(event.account_id, event.data)
        
        account.last_updated = event.timestamp
        self.save_account(account)
```

### 11. Large Event Payloads

**Anti-Pattern**: Putting entire objects in events.

```python
# Bad: Large event payloads
def publish_user_updated_event(user):
    event = UserUpdatedEvent(
        user_id=user.id,
        user_data=user.to_dict(),  # Entire user object
        profile_picture=user.profile_picture_data,  # Binary data!
        friend_list=user.friends,  # Potentially huge list
        order_history=user.order_history  # Another huge list
    )
    event_bus.publish(event)
```

**Problems**:
- Large message size affects performance
- Network bandwidth waste
- Storage costs
- Serialization overhead

**Better Approach**:
```python
# Good: Minimal event payloads
def publish_user_updated_event(user, changed_fields):
    event = UserUpdatedEvent(
        user_id=user.id,
        changed_fields=changed_fields,  # Only what changed
        timestamp=datetime.utcnow()
    )
    event_bus.publish(event)

# Consumers fetch additional data if needed
class UserEventHandler:
    def handle_user_updated(self, event):
        if 'email' in event.changed_fields:
            # Fetch full user data only when needed
            user = user_service.get_user(event.user_id)
            self.update_email_index(user)
```

## Testing Anti-Patterns

### 12. Testing Only Happy Paths

**Anti-Pattern**: Only testing when everything works perfectly.

```python
# Bad: Only happy path tests
def test_create_order():
    order_data = {'customer_id': 123, 'items': [{'id': 1, 'qty': 2}]}
    order = order_service.create_order(order_data)
    assert order.id is not None
```

**Problems**:
- Production failures not caught
- Edge cases not handled
- False confidence in system reliability

**Better Approach**:
```python
# Good: Test failure scenarios
def test_create_order_payment_fails():
    with mock.patch('payment_service.charge') as mock_payment:
        mock_payment.side_effect = PaymentError("Card declined")
        
        with pytest.raises(PaymentError):
            order_service.create_order(order_data)
        
        # Verify no partial state left behind
        assert not order_repository.exists(order_data['customer_id'])

def test_create_order_timeout():
    with mock.patch('payment_service.charge') as mock_payment:
        mock_payment.side_effect = Timeout()
        
        with pytest.raises(ServiceUnavailableError):
            order_service.create_order(order_data)

def test_create_order_inventory_unavailable():
    with mock.patch('inventory_service.reserve') as mock_inventory:
        mock_inventory.side_effect = ServiceUnavailableError()
        
        # Should gracefully degrade
        order = order_service.create_order(order_data)
        assert order.status == 'pending_inventory'
```

## Key Takeaways

1. **Design for Failure**: Assume everything will fail
2. **Loose Coupling**: Services should be independent
3. **Async When Possible**: Don't block on non-critical operations
4. **Timeouts Everywhere**: Every network call needs a timeout
5. **Proper Retry Logic**: Use exponential backoff with jitter
6. **Circuit Breakers**: Protect against cascading failures
7. **Monitor Business Metrics**: Not just technical metrics
8. **Test Failure Scenarios**: Happy path testing isn't enough
9. **Handle Out-of-Order Events**: Don't assume ordering
10. **Keep Events Small**: Large payloads hurt performance

Learning from these anti-patterns will help you avoid common mistakes and build more robust distributed systems.