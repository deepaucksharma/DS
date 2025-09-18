# Conflict Resolution Emergency Patterns

> **3 AM Emergency Protocol**: Data conflicts in distributed systems can cause lost updates, inconsistent state, and business logic failures. This diagram shows how to detect, resolve, and prevent conflicts across distributed data stores.

## Quick Detection Checklist
- [ ] Monitor merge conflicts: Check for concurrent update patterns in logs
- [ ] Watch for lost updates: Compare expected vs actual state changes
- [ ] Check vector clocks: Look for causality violations in distributed timestamps
- [ ] Alert on conflict rates: `merge_conflicts_per_minute > baseline * 5`

## Conflict Resolution Pattern Detection and Resolution

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - Concurrent Operations]
        USER_A[User A: Mobile App<br/>Action: Update profile<br/>Timestamp: 10:03:45.123<br/>Field: phone_number = "+1-555-0001"]
        USER_B[User B: Web App<br/>Action: Update profile<br/>Timestamp: 10:03:45.156<br/>Field: phone_number = "+1-555-0002"]
        ADMIN[Admin: Dashboard<br/>Action: Bulk update users<br/>Timestamp: 10:03:45.089<br/>Field: status = "verified"]
        API_CLIENT[API Client: CRM<br/>Action: Sync customer data<br/>Timestamp: 10:03:45.234<br/>Field: email = "new@email.com"]
    end

    subgraph ServicePlane[Service Plane - Conflict Detection]
        subgraph CONFLICT_DETECTION[Conflict Detection Layer]
            VERSION_TRACKER[Version Tracker<br/>Algorithm: Vector clocks<br/>Node count: 5<br/>Current conflicts: 12 active]
            TIMESTAMP_MONITOR[Timestamp Monitor<br/>Clock synchronization: NTP<br/>Drift tolerance: 100ms<br/>Status: 2 nodes out of sync]
            OPTIMISTIC_LOCK[Optimistic Locking<br/>Version field: updated_at<br/>Check strategy: Compare-and-swap<br/>Conflict rate: 5.2%]
        end

        subgraph RESOLUTION_ENGINE[Conflict Resolution Engine]
            LAST_WRITER_WINS[Last Writer Wins<br/>Strategy: Timestamp-based<br/>Precision: Millisecond<br/>Success rate: 85%]
            FIELD_MERGE[Field-Level Merge<br/>Strategy: Non-conflicting fields<br/>Merge logic: Custom rules<br/>Success rate: 92%]
            MANUAL_RESOLUTION[Manual Resolution<br/>Queue: 45 conflicts pending<br/>SLA: 2 hours response<br/>Escalation: Auto after 4 hours]
        end
    end

    subgraph StatePlane[State Plane - Data Storage Systems]
        subgraph DISTRIBUTED_STORAGE[Distributed Storage]
            DB_NODE_1[(Database Node 1<br/>Region: US-East<br/>Vector clock: [1:15, 2:8, 3:12]<br/>Pending writes: 3)]
            DB_NODE_2[(Database Node 2<br/>Region: US-West<br/>Vector clock: [1:14, 2:9, 3:12]<br/>Pending writes: 7)]
            DB_NODE_3[(Database Node 3<br/>Region: EU<br/>Vector clock: [1:13, 2:8, 3:13]<br/>Pending writes: 2)]
        end

        subgraph CONFLICT_STORAGE[Conflict Storage]
            CONFLICT_LOG[Conflict Log<br/>Storage: Event store<br/>Retention: 30 days<br/>Current entries: 1,247]
            RESOLUTION_HISTORY[Resolution History<br/>Successful resolutions: 98.5%<br/>Manual interventions: 1.2%<br/>Data loss events: 0.3%]
            VECTOR_CLOCK_STORE[Vector Clock Store<br/>Per-record timestamps<br/>Causality tracking<br/>Conflict detection: Real-time]
        end

        subgraph BACKUP_SYSTEMS[Backup and Recovery]
            SNAPSHOT_STORE[Snapshot Store<br/>Point-in-time recovery<br/>Frequency: Every 15 minutes<br/>Retention: 7 days]
            CONSENSUS_LOG[Consensus Log<br/>Raft/Paxos decisions<br/>Conflict resolutions<br/>Audit trail: Complete]
        end
    end

    subgraph ControlPlane[Control Plane - Conflict Management]
        MONITORING[Conflict Monitoring<br/>Detection rate: Real-time<br/>Alert threshold: 10 conflicts/min<br/>Dashboard: Live updates]

        subgraph RESOLUTION_STRATEGIES[Resolution Strategies]
            AUTOMATIC[Automatic Resolution<br/>Rules engine: 47 rules<br/>Success rate: 94%<br/>Processing time: <100ms]
            HUMAN_REVIEW[Human Review Queue<br/>Pending: 8 conflicts<br/>Average resolution: 45 minutes<br/>SLA compliance: 96%]
            ROLLBACK[Rollback Mechanism<br/>Transaction log: Complete<br/>Recovery point: Any timestamp<br/>Data loss: Zero tolerance]
        end

        subgraph PREVENTION[Conflict Prevention]
            ORDERING[Operation Ordering<br/>Logical timestamps<br/>Causal consistency<br/>Conflict reduction: 40%]
            PESSIMISTIC[Pessimistic Locking<br/>Critical operations only<br/>Lock timeout: 30 seconds<br/>Deadlock detection: Active]
            CRDT[CRDT Implementation<br/>Conflict-free data types<br/>Coverage: 60% of operations<br/>Zero conflicts by design]
        end
    end

    %% Concurrent operations causing conflicts
    USER_A --> VERSION_TRACKER
    USER_B --> VERSION_TRACKER
    ADMIN --> TIMESTAMP_MONITOR
    API_CLIENT --> OPTIMISTIC_LOCK

    %% Conflict detection flow
    VERSION_TRACKER --> FIELD_MERGE
    TIMESTAMP_MONITOR --> LAST_WRITER_WINS
    OPTIMISTIC_LOCK -.->|"Version mismatch"| MANUAL_RESOLUTION

    %% Data storage with vector clocks
    USER_A --> DB_NODE_1
    USER_B --> DB_NODE_2
    ADMIN --> DB_NODE_3
    API_CLIENT --> DB_NODE_1

    %% Conflict propagation between nodes
    DB_NODE_1 -.->|"Sync conflict"| DB_NODE_2
    DB_NODE_2 -.->|"Vector clock compare"| DB_NODE_3
    DB_NODE_3 -.->|"Causality violation"| DB_NODE_1

    %% Conflict logging and tracking
    FIELD_MERGE --> CONFLICT_LOG
    LAST_WRITER_WINS --> RESOLUTION_HISTORY
    MANUAL_RESOLUTION --> VECTOR_CLOCK_STORE

    %% Backup for recovery
    DB_NODE_1 --> SNAPSHOT_STORE
    RESOLUTION_HISTORY --> CONSENSUS_LOG

    %% Monitoring and resolution
    CONFLICT_LOG --> MONITORING
    RESOLUTION_HISTORY --> MONITORING
    VECTOR_CLOCK_STORE --> MONITORING

    MONITORING --> AUTOMATIC
    MONITORING --> HUMAN_REVIEW
    MONITORING --> ROLLBACK

    %% Prevention mechanisms
    AUTOMATIC --> ORDERING
    HUMAN_REVIEW --> PESSIMISTIC
    ROLLBACK --> CRDT

    %% Resolution application
    ORDERING -.->|"Prevent conflicts"| VERSION_TRACKER
    PESSIMISTIC -.->|"Lock coordination"| OPTIMISTIC_LOCK
    CRDT -.->|"Conflict-free merge"| FIELD_MERGE

    %% 4-plane styling
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff
    classDef conflictStyle fill:#FF0000,stroke:#CC0000,color:#fff
    classDef resolutionStyle fill:#FFA500,stroke:#CC8800,color:#fff
    classDef preventionStyle fill:#00FF00,stroke:#00CC00,color:#fff

    class USER_A,USER_B,ADMIN,API_CLIENT edgeStyle
    class VERSION_TRACKER,TIMESTAMP_MONITOR,OPTIMISTIC_LOCK,LAST_WRITER_WINS,FIELD_MERGE,MANUAL_RESOLUTION serviceStyle
    class DB_NODE_1,DB_NODE_2,DB_NODE_3,CONFLICT_LOG,RESOLUTION_HISTORY,VECTOR_CLOCK_STORE,SNAPSHOT_STORE,CONSENSUS_LOG stateStyle
    class MONITORING,AUTOMATIC,HUMAN_REVIEW,ROLLBACK,ORDERING,PESSIMISTIC,CRDT controlStyle
    class VERSION_TRACKER,OPTIMISTIC_LOCK,CONFLICT_LOG conflictStyle
    class FIELD_MERGE,LAST_WRITER_WINS,MANUAL_RESOLUTION resolutionStyle
    class ORDERING,CRDT preventionStyle
```

## 3 AM Emergency Response Commands

### 1. Conflict Detection Assessment (30 seconds)
```sql
-- Check for concurrent updates in last 5 minutes
SELECT
    table_name,
    record_id,
    COUNT(*) as concurrent_updates,
    MIN(updated_at) as first_update,
    MAX(updated_at) as last_update,
    MAX(updated_at) - MIN(updated_at) as time_window
FROM audit_log
WHERE updated_at > NOW() - INTERVAL '5 minutes'
GROUP BY table_name, record_id
HAVING COUNT(*) > 1
ORDER BY concurrent_updates DESC;

-- PostgreSQL: Check for version conflicts
SELECT
    id,
    version,
    updated_at,
    updated_by
FROM users
WHERE id IN (
    SELECT id FROM users
    GROUP BY id
    HAVING COUNT(DISTINCT version) > 1
);

-- MongoDB: Check for write conflicts
db.users.find({
    "conflicts": { "$exists": true, "$ne": [] }
}).limit(10);
```

### 2. Emergency Conflict Resolution (60 seconds)
```python
# Python script for immediate conflict resolution
import json
import time
from datetime import datetime, timedelta

def resolve_user_profile_conflicts():
    """Emergency resolution for user profile conflicts"""

    # Get all pending conflicts
    conflicts = get_pending_conflicts('user_profiles')

    for conflict in conflicts:
        try:
            # Last Writer Wins for non-critical fields
            if conflict['field'] in ['phone', 'address', 'preferences']:
                resolve_last_writer_wins(conflict)

            # Field-level merge for compatible changes
            elif conflict['field'] in ['tags', 'permissions']:
                resolve_field_merge(conflict)

            # Manual review for critical fields
            elif conflict['field'] in ['email', 'payment_method']:
                queue_for_manual_review(conflict)

            # CRDT resolution for counters
            elif conflict['field'] in ['login_count', 'points']:
                resolve_crdt_merge(conflict)

        except Exception as e:
            log_resolution_failure(conflict, e)

def resolve_last_writer_wins(conflict):
    """Resolve using timestamp comparison"""
    latest_version = max(conflict['versions'], key=lambda v: v['timestamp'])

    update_query = f"""
        UPDATE {conflict['table']}
        SET {conflict['field']} = %s,
            version = version + 1,
            updated_at = NOW(),
            conflict_resolved = TRUE
        WHERE id = %s
    """

    execute_query(update_query, [latest_version['value'], conflict['record_id']])
    log_resolution(conflict, 'last_writer_wins', latest_version)

def resolve_field_merge(conflict):
    """Merge non-conflicting field changes"""
    base_version = conflict['base_version']
    versions = conflict['versions']

    merged_data = base_version.copy()

    for version in versions:
        for field, value in version['changes'].items():
            # Only merge if field wasn't changed in base
            if field not in base_version['changes']:
                merged_data[field] = value

    update_merged_record(conflict['record_id'], merged_data)
    log_resolution(conflict, 'field_merge', merged_data)
```

### 3. System-Wide Conflict Prevention (90 seconds)
```bash
# Enable optimistic locking across all critical tables
psql production -c "
ALTER TABLE users ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1;
ALTER TABLE payments ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1;

-- Create conflict detection trigger
CREATE OR REPLACE FUNCTION detect_update_conflicts()
RETURNS TRIGGER AS \$\$
BEGIN
    IF OLD.version != NEW.version THEN
        INSERT INTO conflict_log (table_name, record_id, old_version, new_version, detected_at)
        VALUES (TG_TABLE_NAME, NEW.id, OLD.version, NEW.version, NOW());
    END IF;

    NEW.version = NEW.version + 1;
    NEW.updated_at = NOW();
    RETURN NEW;
END;
\$\$ LANGUAGE plpgsql;

-- Apply trigger to critical tables
CREATE TRIGGER users_conflict_trigger
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION detect_update_conflicts();
"

# Restart application with conflict resolution enabled
kubectl patch deployment user-service -p '{"spec":{"template":{"metadata":{"annotations":{"conflict-resolution":"enabled"}}}}}'
kubectl rollout restart deployment user-service

# Monitor conflict resolution performance
kubectl logs -f deployment/user-service | grep "CONFLICT"
```

## Conflict Pattern Recognition

### Concurrent Update Pattern
```
Time         User_A_Action              User_B_Action              Result
10:03:45.100 Read profile (v1)         -                          No conflict
10:03:45.150 -                         Read profile (v1)          No conflict
10:03:45.200 Update phone (v1→v2)      -                          Success
10:03:45.250 -                         Update email (v1→v2)       CONFLICT!
10:03:45.300 Conflict detected         Conflict detected          Resolution needed
```

### Lost Update Scenario
```
Operation_Sequence    Database_State        Expected_Result    Actual_Result    Issue
1. Read balance: $100 balance = $100        N/A               N/A              -
2. User A: -$30       balance = $100        $70 pending       $100             Read
3. User B: -$50       balance = $100        $50 pending       $100             Read
4. A commits: $70     balance = $70         $70               $70              OK
5. B commits: $50     balance = $50         $20               $50              LOST UPDATE!
```

### Vector Clock Conflicts
```
Node     Event                Vector_Clock        Causality_Relation
Node1    User update phone    [1:15, 2:8, 3:12]  -
Node2    Admin update status  [1:14, 2:9, 3:12]  Concurrent with Node1
Node3    Sync from Node1      [1:15, 2:8, 3:13]  After Node1
Node2    Receive Node3 sync   [1:15, 2:9, 3:13]  CONFLICT: 2:9 vs 2:8
```

## Error Message Patterns

### Optimistic Lock Failures
```
ERROR: Optimistic lock exception - record modified by another user
PATTERN: "Version mismatch" or "Record version conflict"
LOCATION: Application logs, ORM error messages
ACTION: Refresh record, merge changes, retry operation
RESOLUTION: Implement automatic retry with exponential backoff
```

### Vector Clock Causality Violations
```
ERROR: Causality violation detected in vector clock
PATTERN: "Clock drift" or "Causal ordering violation"
LOCATION: Distributed system logs, conflict resolution logs
ACTION: Synchronize clocks, resolve based on business rules
PREVENTION: Implement logical timestamps, clock skew detection
```

### CRDT Merge Conflicts
```
ERROR: CRDT merge conflict - incompatible operations
PATTERN: Conflicting operations on same CRDT element
LOCATION: CRDT library logs, merge operation logs
ACTION: Apply CRDT-specific resolution rules
INVESTIGATION: Check if operations are truly commutative
```

## Conflict Resolution Strategies Implementation

### Vector Clock Implementation
```python
# Vector clock for causality tracking
from typing import Dict, List, Optional
import json

class VectorClock:
    def __init__(self, node_id: str, nodes: List[str]):
        self.node_id = node_id
        self.clock = {node: 0 for node in nodes}

    def tick(self):
        """Increment local clock"""
        self.clock[self.node_id] += 1

    def update(self, other_clock: Dict[str, int]):
        """Update clock with received timestamp"""
        for node in self.clock:
            if node in other_clock:
                self.clock[node] = max(self.clock[node], other_clock[node])
        self.tick()

    def compare(self, other_clock: Dict[str, int]) -> str:
        """Compare vector clocks for causality"""
        self_before_other = all(
            self.clock[node] <= other_clock.get(node, 0)
            for node in self.clock
        )
        other_before_self = all(
            other_clock.get(node, 0) <= self.clock[node]
            for node in self.clock
        )

        if self_before_other and not other_before_self:
            return "before"
        elif other_before_self and not self_before_other:
            return "after"
        else:
            return "concurrent"

    def to_dict(self) -> Dict[str, int]:
        return self.clock.copy()

class ConflictResolutionEngine:
    def __init__(self, node_id: str, nodes: List[str]):
        self.node_id = node_id
        self.vector_clock = VectorClock(node_id, nodes)
        self.conflict_handlers = {}

    def register_handler(self, data_type: str, handler_func):
        """Register conflict resolution handler for data type"""
        self.conflict_handlers[data_type] = handler_func

    def update_record(self, record_id: str, data: Dict, data_type: str):
        """Update record with conflict detection"""
        self.vector_clock.tick()

        update_event = {
            'record_id': record_id,
            'data': data,
            'data_type': data_type,
            'node_id': self.node_id,
            'vector_clock': self.vector_clock.to_dict(),
            'timestamp': time.time()
        }

        # Check for conflicts with existing versions
        conflicts = self.detect_conflicts(record_id, update_event)

        if conflicts:
            resolved_data = self.resolve_conflicts(conflicts, update_event)
            return self.apply_update(record_id, resolved_data, update_event)
        else:
            return self.apply_update(record_id, data, update_event)

    def detect_conflicts(self, record_id: str, new_event: Dict) -> List[Dict]:
        """Detect conflicts with concurrent updates"""
        # Get all pending updates for this record
        pending_updates = self.get_pending_updates(record_id)
        conflicts = []

        for pending in pending_updates:
            relation = self.vector_clock.compare(pending['vector_clock'])

            if relation == "concurrent":
                # Check if updates conflict at field level
                if self.have_field_conflicts(new_event['data'], pending['data']):
                    conflicts.append(pending)

        return conflicts

    def have_field_conflicts(self, data1: Dict, data2: Dict) -> bool:
        """Check if two updates have conflicting field changes"""
        common_fields = set(data1.keys()) & set(data2.keys())

        for field in common_fields:
            if data1[field] != data2[field]:
                return True

        return False

    def resolve_conflicts(self, conflicts: List[Dict], new_event: Dict) -> Dict:
        """Resolve conflicts using registered handlers"""
        data_type = new_event['data_type']

        if data_type in self.conflict_handlers:
            return self.conflict_handlers[data_type](conflicts, new_event)
        else:
            # Default: Last Writer Wins
            return self.last_writer_wins_resolution(conflicts, new_event)

    def last_writer_wins_resolution(self, conflicts: List[Dict], new_event: Dict) -> Dict:
        """Resolve conflicts using timestamp comparison"""
        all_events = conflicts + [new_event]
        latest_event = max(all_events, key=lambda e: e['timestamp'])
        return latest_event['data']

    def field_level_merge_resolution(self, conflicts: List[Dict], new_event: Dict) -> Dict:
        """Merge non-conflicting field changes"""
        all_events = conflicts + [new_event]
        merged_data = {}

        # Collect all field updates
        field_updates = {}
        for event in all_events:
            for field, value in event['data'].items():
                if field not in field_updates:
                    field_updates[field] = []
                field_updates[field].append({
                    'value': value,
                    'timestamp': event['timestamp'],
                    'node_id': event['node_id']
                })

        # For each field, use the latest update
        for field, updates in field_updates.items():
            latest_update = max(updates, key=lambda u: u['timestamp'])
            merged_data[field] = latest_update['value']

        return merged_data

# Register handlers for different data types
engine = ConflictResolutionEngine("node1", ["node1", "node2", "node3"])

# User profile: Field-level merge for non-conflicting changes
engine.register_handler("user_profile", engine.field_level_merge_resolution)

# Financial data: Manual review required
def financial_conflict_handler(conflicts, new_event):
    # Queue for manual resolution
    queue_for_manual_review({
        'conflicts': conflicts,
        'new_event': new_event,
        'priority': 'high',
        'type': 'financial_data'
    })
    # Return original data until resolved
    return new_event['data']

engine.register_handler("financial_data", financial_conflict_handler)
```

### CRDT Implementation for Conflict-Free Updates
```python
# CRDT (Conflict-free Replicated Data Types) implementation
from typing import Set, Dict, Any
import time

class GCounterCRDT:
    """Grow-only counter CRDT"""
    def __init__(self, node_id: str, nodes: Set[str]):
        self.node_id = node_id
        self.state = {node: 0 for node in nodes}

    def increment(self, amount: int = 1):
        """Increment counter (only local node can increment its counter)"""
        self.state[self.node_id] += amount

    def merge(self, other_state: Dict[str, int]):
        """Merge with another counter state"""
        for node, count in other_state.items():
            if node in self.state:
                self.state[node] = max(self.state[node], count)

    def value(self) -> int:
        """Get current counter value"""
        return sum(self.state.values())

class PNCounterCRDT:
    """Increment/Decrement counter CRDT"""
    def __init__(self, node_id: str, nodes: Set[str]):
        self.positive = GCounterCRDT(node_id, nodes)
        self.negative = GCounterCRDT(node_id, nodes)

    def increment(self, amount: int = 1):
        self.positive.increment(amount)

    def decrement(self, amount: int = 1):
        self.negative.increment(amount)

    def merge(self, other_positive: Dict[str, int], other_negative: Dict[str, int]):
        self.positive.merge(other_positive)
        self.negative.merge(other_negative)

    def value(self) -> int:
        return self.positive.value() - self.negative.value()

class LWWRegisterCRDT:
    """Last-Writer-Wins Register CRDT"""
    def __init__(self, node_id: str, initial_value: Any = None):
        self.node_id = node_id
        self.value = initial_value
        self.timestamp = time.time()
        self.node = node_id

    def set(self, value: Any):
        """Set new value with current timestamp"""
        self.value = value
        self.timestamp = time.time()
        self.node = self.node_id

    def merge(self, other_value: Any, other_timestamp: float, other_node: str):
        """Merge with another register"""
        if (other_timestamp > self.timestamp or
            (other_timestamp == self.timestamp and other_node > self.node)):
            self.value = other_value
            self.timestamp = other_timestamp
            self.node = other_node

class AWSetCRDT:
    """Add-Wins Set CRDT"""
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.added = {}  # element -> set of unique tags
        self.removed = {}  # element -> set of unique tags

    def add(self, element: Any):
        """Add element to set"""
        tag = f"{self.node_id}:{time.time()}:{hash(element)}"

        if element not in self.added:
            self.added[element] = set()
        self.added[element].add(tag)

    def remove(self, element: Any):
        """Remove element from set"""
        if element in self.added:
            if element not in self.removed:
                self.removed[element] = set()
            # Move all add tags to removed
            self.removed[element].update(self.added[element])

    def merge(self, other_added: Dict, other_removed: Dict):
        """Merge with another set"""
        # Merge added elements
        for element, tags in other_added.items():
            if element not in self.added:
                self.added[element] = set()
            self.added[element].update(tags)

        # Merge removed elements
        for element, tags in other_removed.items():
            if element not in self.removed:
                self.removed[element] = set()
            self.removed[element].update(tags)

    def contains(self, element: Any) -> bool:
        """Check if element is in set"""
        if element not in self.added:
            return False

        added_tags = self.added[element]
        removed_tags = self.removed.get(element, set())

        # Element is present if it has add tags not in removed tags
        return len(added_tags - removed_tags) > 0

    def elements(self) -> Set[Any]:
        """Get all elements in set"""
        result = set()
        for element in self.added:
            if self.contains(element):
                result.add(element)
        return result

# Usage example for user preferences (conflict-free)
class UserPreferencesCRDT:
    def __init__(self, user_id: str, node_id: str):
        self.user_id = user_id
        self.node_id = node_id

        # Use different CRDTs for different preference types
        self.notification_count = PNCounterCRDT(node_id, {"node1", "node2", "node3"})
        self.theme = LWWRegisterCRDT(node_id, "light")
        self.enabled_features = AWSetCRDT(node_id)
        self.privacy_settings = {}  # field -> LWWRegisterCRDT

    def increment_notifications(self, count: int = 1):
        self.notification_count.increment(count)

    def set_theme(self, theme: str):
        self.theme.set(theme)

    def enable_feature(self, feature: str):
        self.enabled_features.add(feature)

    def disable_feature(self, feature: str):
        self.enabled_features.remove(feature)

    def set_privacy_setting(self, setting: str, value: Any):
        if setting not in self.privacy_settings:
            self.privacy_settings[setting] = LWWRegisterCRDT(self.node_id, value)
        else:
            self.privacy_settings[setting].set(value)

    def merge_with_replica(self, replica_state: Dict):
        """Merge with state from another replica"""
        # Merge notification counter
        self.notification_count.merge(
            replica_state['notification_count']['positive'],
            replica_state['notification_count']['negative']
        )

        # Merge theme setting
        self.theme.merge(
            replica_state['theme']['value'],
            replica_state['theme']['timestamp'],
            replica_state['theme']['node']
        )

        # Merge enabled features
        self.enabled_features.merge(
            replica_state['enabled_features']['added'],
            replica_state['enabled_features']['removed']
        )

        # Merge privacy settings
        for setting, state in replica_state['privacy_settings'].items():
            if setting not in self.privacy_settings:
                self.privacy_settings[setting] = LWWRegisterCRDT(self.node_id)

            self.privacy_settings[setting].merge(
                state['value'],
                state['timestamp'],
                state['node']
            )

    def to_dict(self) -> Dict:
        """Serialize state for replication"""
        return {
            'user_id': self.user_id,
            'notification_count': {
                'positive': self.notification_count.positive.state,
                'negative': self.notification_count.negative.state
            },
            'theme': {
                'value': self.theme.value,
                'timestamp': self.theme.timestamp,
                'node': self.theme.node
            },
            'enabled_features': {
                'added': {k: list(v) for k, v in self.enabled_features.added.items()},
                'removed': {k: list(v) for k, v in self.enabled_features.removed.items()}
            },
            'privacy_settings': {
                setting: {
                    'value': crdt.value,
                    'timestamp': crdt.timestamp,
                    'node': crdt.node
                }
                for setting, crdt in self.privacy_settings.items()
            }
        }

# Example usage
prefs = UserPreferencesCRDT("user123", "node1")
prefs.set_theme("dark")
prefs.enable_feature("beta_features")
prefs.increment_notifications(5)

# Replicate to other nodes - no conflicts possible!
replica_state = prefs.to_dict()
# ... send to other nodes ...

# Merge updates from other nodes
other_node_state = get_updates_from_other_nodes()
prefs.merge_with_replica(other_node_state)
```

## Recovery Procedures

### Phase 1: Immediate Conflict Containment (0-5 minutes)
- [ ] Stop conflicting write operations to affected records
- [ ] Enable optimistic locking for critical tables
- [ ] Route reads to consistent replicas only
- [ ] Queue conflicting updates for manual resolution

### Phase 2: Automated Resolution (5-15 minutes)
- [ ] Apply automatic resolution rules based on conflict type
- [ ] Merge non-conflicting field changes where possible
- [ ] Use last-writer-wins for low-impact fields
- [ ] Escalate critical conflicts to manual review queue

### Phase 3: Consistency Restoration (15+ minutes)
- [ ] Validate resolved data meets business constraints
- [ ] Update vector clocks and causality information
- [ ] Resume normal operations with enhanced conflict detection
- [ ] Review and improve conflict prevention strategies

## Real-World Conflict Resolution Incidents

### Dynamo Write Conflicts at Amazon (2007)
- **Trigger**: Shopping cart updates from multiple devices simultaneously
- **Impact**: Lost shopping cart items, inconsistent cart state
- **Detection**: Customer complaints about disappearing items
- **Resolution**: Vector clock implementation + last-writer-wins for cart merging

### CouchDB Replication Conflicts (2010)
- **Trigger**: Document updates during network partition healing
- **Impact**: Conflicting document versions across replicas
- **Detection**: Automatic conflict detection in _conflicts field
- **Resolution**: Application-level merge logic + manual conflict resolution

### Riak Multi-Datacenter Conflicts (2013)
- **Trigger**: Cross-datacenter replication with network delays
- **Impact**: Inconsistent user profile data across regions
- **Detection**: Vector clock causality violations
- **Resolution**: CRDT adoption for user preferences + conflict-free counters

---
*Last Updated: Based on Amazon Dynamo, CouchDB, Riak conflict resolution incidents*
*Next Review: Monitor for new conflict resolution patterns and CRDT implementations*