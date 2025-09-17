# API Reference

## Framework API

The Distributed Systems Framework provides programmatic APIs for system design and validation.

## Design Engine API

### System Design

```python
from ds_framework import DesignEngine, Requirements

# Create design engine
engine = DesignEngine()

# Define requirements
requirements = Requirements(
    domain='e-commerce',
    throughput_rps=10000,
    latency_p99_ms=100,
    availability_target=0.999,
    consistency_model='eventual',
    cost_budget_monthly=50000
)

# Generate system design
design = engine.design_system(requirements)

print(f"Recommended pattern: {design.pattern}")
print(f"Required primitives: {design.primitives}")
print(f"Estimated cost: ${design.monthly_cost}")
```

#### Requirements Class

```python
class Requirements:
    def __init__(
        self,
        domain: str,
        throughput_rps: int,
        latency_p99_ms: int,
        availability_target: float,
        consistency_model: str,
        cost_budget_monthly: int,
        geographic_distribution: List[str] = None,
        compliance_requirements: List[str] = None
    ):
        """
        Define system requirements for design generation.
        
        Args:
            domain: Application domain (e-commerce, social, financial, etc.)
            throughput_rps: Required requests per second
            latency_p99_ms: 99th percentile latency budget in milliseconds
            availability_target: Target availability (0.99, 0.999, 0.9999)
            consistency_model: Required consistency (strong, eventual, causal)
            cost_budget_monthly: Monthly budget in USD
            geographic_distribution: List of regions for deployment
            compliance_requirements: List of compliance needs (GDPR, PCI, SOX)
        """
```

#### SystemDesign Class

```python
class SystemDesign:
    def __init__(self):
        self.pattern: str = None
        self.primitives: List[str] = []
        self.capabilities: List[str] = []
        self.technologies: Dict[str, str] = {}
        self.monthly_cost: int = 0
        self.throughput_capacity: int = 0
        self.latency_p99: int = 0
        self.availability: float = 0.0
        self.proof_obligations: List[str] = []
    
    def validate_requirements(self, requirements: Requirements) -> List[str]:
        """Validate that design meets requirements."""
        
    def generate_deployment_yaml(self) -> str:
        """Generate Kubernetes deployment configuration."""
        
    def generate_terraform(self) -> str:
        """Generate Terraform infrastructure code."""
        
    def generate_monitoring_config(self) -> Dict:
        """Generate monitoring and alerting configuration."""
```

### Primitive Validation

```python
from ds_framework import PrimitiveValidator

validator = PrimitiveValidator()

# Validate primitive combination
primitives = ['P1_Partitioning', 'P2_Replication', 'P5_Consensus']
conflicts = validator.check_conflicts(primitives)

if conflicts:
    print(f"Conflicting primitives: {conflicts}")

# Get capability mapping
capabilities = validator.get_capabilities(primitives)
print(f"Provided capabilities: {capabilities}")
```

### Pattern Detection

```python
from ds_framework import PatternDetector

detector = PatternDetector()

# Detect patterns from primitives
primitives = ['P3_DurableLog', 'P7_Idempotency', 'P19_CDC']
patterns = detector.detect_patterns(primitives)

print(f"Detected patterns: {patterns}")
# Output: ['Outbox']

# Get pattern implementation guide
guide = detector.get_implementation_guide('Outbox')
print(guide.checklist)
print(guide.code_example)
```

## Monitoring API

### Metrics Collection

```python
from ds_framework.monitoring import MetricsCollector, GoldenSignals

collector = MetricsCollector()

# Collect golden signals
signals = collector.collect_golden_signals('order-service')

print(f"Latency P99: {signals.latency_p99}ms")
print(f"Error rate: {signals.error_rate}%")
print(f"Throughput: {signals.requests_per_second} RPS")
print(f"Saturation: {signals.cpu_utilization}%")
```

### Invariant Checking

```python
from ds_framework.monitoring import InvariantChecker

checker = InvariantChecker()

# Define business invariant
@checker.invariant("account_balance_non_negative")
def check_account_balances():
    """All account balances must be non-negative"""
    negative_accounts = db.query("""
        SELECT account_id FROM accounts WHERE balance < 0
    """)
    return len(negative_accounts) == 0

# Run checks
violations = checker.check_all_invariants()
if violations:
    print(f"Invariant violations: {violations}")
```

### Chaos Engineering

```python
from ds_framework.chaos import ChaosExperiment

experiment = ChaosExperiment()

# Kill random instances
experiment.kill_random_instances(
    service_name='user-service',
    percentage=0.1,  # Kill 10% of instances
    duration_minutes=5
)

# Inject network latency
experiment.inject_network_latency(
    target_service='payment-service',
    latency_ms=1000,
    duration_minutes=10
)

# Monitor impact
results = experiment.get_results()
print(f"Service availability during experiment: {results.availability}")
```

## Testing API

### Property-Based Testing

```python
from ds_framework.testing import DistributedProperty
from hypothesis import given, strategies as st

class EventualConsistencyProperty(DistributedProperty):
    @given(operations=st.lists(st.text(), min_size=1, max_size=100))
    def test_eventual_consistency(self, operations):
        """Test that replicas eventually converge"""
        replicas = self.create_replicas(3)
        
        # Apply operations to random replicas
        for op in operations:
            replica = random.choice(replicas)
            replica.apply_operation(op)
        
        # Wait for convergence
        self.wait_for_convergence(replicas, timeout=30)
        
        # Verify all replicas have same state
        states = [replica.get_state() for replica in replicas]
        assert all(state == states[0] for state in states)
```

### Integration Testing

```python
from ds_framework.testing import IntegrationTest

class OrderServiceIntegrationTest(IntegrationTest):
    def setup_services(self):
        """Setup test environment with real services"""
        self.services = {
            'order-service': self.start_service('order-service'),
            'payment-service': self.start_service('payment-service'),
            'inventory-service': self.start_service('inventory-service')
        }
    
    def test_order_creation_flow(self):
        """Test complete order creation flow"""
        # Create order
        order_response = self.services['order-service'].post('/orders', {
            'customer_id': 123,
            'items': [{'product_id': 456, 'quantity': 2}]
        })
        
        order_id = order_response.json()['order_id']
        
        # Verify payment was processed
        self.wait_for_event('PaymentProcessed', order_id)
        
        # Verify inventory was reserved
        self.wait_for_event('InventoryReserved', order_id)
        
        # Verify final order state
        order = self.services['order-service'].get(f'/orders/{order_id}')
        assert order.json()['status'] == 'confirmed'
```

## Verification API

### Formal Verification

```python
from ds_framework.verification import TLAGenerator, ModelChecker

# Generate TLA+ specification
generator = TLAGenerator()
spec = generator.generate_consensus_spec(
    nodes=5,
    algorithm='raft'
)

print(spec)

# Model check the specification
checker = ModelChecker()
result = checker.check_safety_properties(spec)

if result.violations:
    print(f"Safety violations found: {result.violations}")
else:
    print("All safety properties verified")
```

### Linearizability Checking

```python
from ds_framework.verification import LinearizabilityChecker

checker = LinearizabilityChecker()

# Record operations
checker.start_recording()

# Perform concurrent operations
operations = [
    {'type': 'write', 'key': 'x', 'value': 1, 'start_time': 100, 'end_time': 150},
    {'type': 'read', 'key': 'x', 'value': 1, 'start_time': 120, 'end_time': 140},
    {'type': 'write', 'key': 'x', 'value': 2, 'start_time': 160, 'end_time': 200}
]

# Check linearizability
result = checker.check_linearizability(operations)

if result.is_linearizable:
    print("Operations are linearizable")
else:
    print(f"Linearizability violation: {result.violation}")
```

## Capacity Planning API

### Load Modeling

```python
from ds_framework.capacity import LoadModel, CapacityPlanner

# Model expected load
load_model = LoadModel()
load_model.add_daily_pattern(
    peak_hour=14,  # 2 PM peak
    peak_multiplier=3.0,
    base_rps=1000
)
load_model.add_seasonal_pattern(
    peak_month=12,  # December peak
    peak_multiplier=5.0
)

# Plan capacity
planner = CapacityPlanner()
capacity_plan = planner.plan_capacity(
    load_model=load_model,
    target_utilization=0.7,
    availability_target=0.999
)

print(f"Required instances: {capacity_plan.instances}")
print(f"Estimated cost: ${capacity_plan.monthly_cost}")
```

### Performance Modeling

```python
from ds_framework.capacity import PerformanceModel

model = PerformanceModel()

# Model system performance
model.add_component('load_balancer', latency_ms=2, throughput_rps=50000)
model.add_component('api_server', latency_ms=20, throughput_rps=1000)
model.add_component('database', latency_ms=5, throughput_rps=5000)

# Calculate end-to-end performance
performance = model.calculate_performance()

print(f"End-to-end latency P50: {performance.latency_p50}ms")
print(f"System throughput: {performance.throughput_rps} RPS")
```

## Error Handling

All APIs use consistent error handling:

```python
from ds_framework.exceptions import (
    DesignValidationError,
    IncompatiblePrimitivesError,
    CapacityExceededError,
    VerificationFailedError
)

try:
    design = engine.design_system(requirements)
except DesignValidationError as e:
    print(f"Design validation failed: {e.violations}")
except IncompatiblePrimitivesError as e:
    print(f"Incompatible primitives: {e.conflicts}")
```

## Configuration

```python
from ds_framework import configure

# Configure framework
configure(
    log_level='INFO',
    monitoring_endpoint='http://prometheus:9090',
    chaos_enabled=True,
    verification_level='strict'
)
```

This API reference provides the programmatic interface to the Distributed Systems Framework, enabling automated system design, validation, and testing.