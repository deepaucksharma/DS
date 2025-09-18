# Data Inconsistency Resolution Guide

## Overview

Data inconsistencies in distributed systems can manifest as stale reads, lost updates, phantom data, and conflicting transactions. This guide provides systematic approaches used by engineering teams at Stripe, Airbnb, and Shopify to detect, diagnose, and resolve data consistency issues in production environments.

**Time to Resolution**: 20-60 minutes for cache inconsistencies, 2-8 hours for distributed transaction conflicts

## Decision Tree

```mermaid
graph TD
    A[Data Inconsistency Detected] --> B{Consistency Model?}
    B -->|Strong| C[Strong Consistency Analysis]
    B -->|Eventual| D[Eventual Consistency Analysis]
    B -->|Weak| E[Weak Consistency Analysis]

    C --> F[ACID Transaction Check]
    F --> G{Transaction Isolation Issue?}

    G -->|Yes| H[Isolation Level Analysis]
    G -->|No| I[Distributed Transaction Check]

    D --> J[Convergence Time Analysis]
    J --> K[Replication Lag Check]

    E --> L[Read-Your-Writes Verification]

    H --> M[Lock Contention Analysis]
    I --> N[Two-Phase Commit Status]

    K --> O[Anti-entropy Process]
    L --> P[Session Affinity Check]

    N --> Q{2PC Phase?}
    Q -->|Prepare| R[Resource Manager Status]
    Q -->|Commit| S[Coordinator Recovery]

    style A fill:#8B5CF6,stroke:#7C3AED,color:#fff
    style I fill:#F59E0B,stroke:#D97706,color:#fff
    style O fill:#10B981,stroke:#059669,color:#fff
```

## Immediate Triage Commands (First 5 Minutes)

### 1. Consistency State Overview
```bash
# Database transaction isolation levels
# PostgreSQL
psql -c "SHOW default_transaction_isolation;"
psql -c "SELECT pid, state, query, xact_start FROM pg_stat_activity WHERE state = 'active';"

# MySQL
mysql -e "SELECT @@transaction_isolation;"
mysql -e "SELECT * FROM INFORMATION_SCHEMA.INNODB_TRX;"

# Check for long-running transactions
psql -c "SELECT now() - xact_start as duration, pid, state, query FROM pg_stat_activity WHERE xact_start IS NOT NULL ORDER BY duration DESC LIMIT 10;"
```

### 2. Replication Lag Detection
```bash
# PostgreSQL replication lag
psql -c "SELECT client_addr, state, sent_lsn, write_lsn, flush_lsn, replay_lsn,
         (EXTRACT(EPOCH FROM write_lag)||'s')::INTERVAL AS write_lag,
         (EXTRACT(EPOCH FROM flush_lag)||'s')::INTERVAL AS flush_lag,
         (EXTRACT(EPOCH FROM replay_lag)||'s')::INTERVAL AS replay_lag
         FROM pg_stat_replication;"

# MySQL replica status
mysql -e "SHOW SLAVE STATUS\G" | grep -E "(Seconds_Behind_Master|Last_SQL_Error|Last_IO_Error)"

# MongoDB replica set lag
mongosh --eval "rs.printSlaveReplicationInfo()"

# Redis replication info
redis-cli info replication | grep -E "(master_repl_offset|slave_repl_offset|lag)"
```

### 3. Cache Coherence Check
```bash
# Compare cache vs database values for key entities
key="user:12345"

# Redis cache value
redis_value=$(redis-cli get "$key")
echo "Redis: $redis_value"

# Database value (example query)
db_value=$(psql -t -c "SELECT data FROM users WHERE id = 12345;")
echo "Database: $db_value"

# Compare checksums
redis_hash=$(echo "$redis_value" | md5sum)
db_hash=$(echo "$db_value" | md5sum)
if [ "$redis_hash" = "$db_hash" ]; then
    echo "Cache consistent"
else
    echo "CACHE INCONSISTENCY DETECTED"
fi
```

## Strong Consistency Debugging

### 1. ACID Transaction Analysis
```sql
-- PostgreSQL transaction analysis
-- Check current transaction isolation levels and locks
SELECT
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS current_statement_in_blocking_process
FROM pg_catalog.pg_locks blocked_locks
    JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
    JOIN pg_catalog.pg_locks blocking_locks
        ON blocking_locks.locktype = blocked_locks.locktype
        AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
        AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
        AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
        AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
        AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
        AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
        AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
        AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
        AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
        AND blocking_locks.pid != blocked_locks.pid
    JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;

-- Deadlock detection
SELECT * FROM pg_stat_database WHERE datname = current_database() AND deadlocks > 0;

-- Long-running transactions that might cause inconsistency
SELECT
    pid,
    now() - pg_stat_activity.query_start AS duration,
    query,
    state,
    backend_xid,
    backend_xmin
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes'
  AND state IN ('active', 'idle in transaction');
```

### 2. Distributed Transaction Monitoring
```python
# Python implementation for monitoring distributed transactions
import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

class TransactionPhase(Enum):
    PREPARE = "prepare"
    COMMIT = "commit"
    ABORT = "abort"
    UNKNOWN = "unknown"

class TransactionState(Enum):
    ACTIVE = "active"
    PREPARED = "prepared"
    COMMITTED = "committed"
    ABORTED = "aborted"
    UNCERTAIN = "uncertain"

@dataclass
class TransactionParticipant:
    participant_id: str
    endpoint: str
    state: TransactionState
    phase: TransactionPhase
    last_updated: datetime
    error_message: Optional[str] = None

@dataclass
class DistributedTransaction:
    transaction_id: str
    coordinator_id: str
    participants: List[TransactionParticipant]
    global_state: TransactionState
    started_at: datetime
    timeout_at: datetime
    current_phase: TransactionPhase

class DistributedTransactionMonitor:
    def __init__(self, coordinator_endpoints: List[str]):
        self.coordinator_endpoints = coordinator_endpoints
        self.active_transactions: Dict[str, DistributedTransaction] = {}
        self.logger = logging.getLogger(__name__)

    async def check_transaction_consistency(self) -> Dict[str, List[str]]:
        """Check for inconsistencies across distributed transactions"""
        inconsistencies = {
            'hanging_transactions': [],
            'participant_mismatches': [],
            'timeout_violations': [],
            'orphaned_participants': []
        }

        # Collect transaction states from all coordinators
        all_transactions = await self.collect_transaction_states()

        for tx_id, transaction in all_transactions.items():
            # Check for hanging transactions
            if self._is_transaction_hanging(transaction):
                inconsistencies['hanging_transactions'].append(tx_id)

            # Check for participant state mismatches
            if self._has_participant_mismatch(transaction):
                inconsistencies['participant_mismatches'].append(tx_id)

            # Check for timeout violations
            if datetime.now() > transaction.timeout_at and transaction.global_state == TransactionState.ACTIVE:
                inconsistencies['timeout_violations'].append(tx_id)

        return inconsistencies

    async def collect_transaction_states(self) -> Dict[str, DistributedTransaction]:
        """Collect transaction states from all coordinators"""
        all_transactions = {}

        for coordinator_endpoint in self.coordinator_endpoints:
            try:
                transactions = await self.get_coordinator_transactions(coordinator_endpoint)
                all_transactions.update(transactions)
            except Exception as e:
                self.logger.error(f"Failed to get transactions from {coordinator_endpoint}: {e}")

        return all_transactions

    async def get_coordinator_transactions(self, coordinator_endpoint: str) -> Dict[str, DistributedTransaction]:
        """Get transaction state from a specific coordinator"""
        transactions = {}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"http://{coordinator_endpoint}/transactions/active") as response:
                    if response.status == 200:
                        data = await response.json()

                        for tx_data in data.get('transactions', []):
                            participants = []
                            for p_data in tx_data.get('participants', []):
                                participant = TransactionParticipant(
                                    participant_id=p_data['id'],
                                    endpoint=p_data['endpoint'],
                                    state=TransactionState(p_data['state']),
                                    phase=TransactionPhase(p_data['phase']),
                                    last_updated=datetime.fromisoformat(p_data['last_updated']),
                                    error_message=p_data.get('error')
                                )
                                participants.append(participant)

                            transaction = DistributedTransaction(
                                transaction_id=tx_data['id'],
                                coordinator_id=tx_data['coordinator_id'],
                                participants=participants,
                                global_state=TransactionState(tx_data['global_state']),
                                started_at=datetime.fromisoformat(tx_data['started_at']),
                                timeout_at=datetime.fromisoformat(tx_data['timeout_at']),
                                current_phase=TransactionPhase(tx_data['current_phase'])
                            )
                            transactions[transaction.transaction_id] = transaction

            except Exception as e:
                self.logger.error(f"Error collecting transactions from {coordinator_endpoint}: {e}")

        return transactions

    def _is_transaction_hanging(self, transaction: DistributedTransaction) -> bool:
        """Check if transaction is hanging in an intermediate state"""
        hanging_duration = timedelta(minutes=5)  # Consider hanging after 5 minutes

        if transaction.current_phase == TransactionPhase.PREPARE:
            # Transaction has been in prepare phase too long
            if datetime.now() - transaction.started_at > hanging_duration:
                return True

        if transaction.global_state == TransactionState.UNCERTAIN:
            # Transaction is in uncertain state
            return True

        return False

    def _has_participant_mismatch(self, transaction: DistributedTransaction) -> bool:
        """Check if participants have inconsistent states"""
        if not transaction.participants:
            return False

        # All participants should be in compatible states for the current phase
        if transaction.current_phase == TransactionPhase.PREPARE:
            # During prepare phase, participants should be ACTIVE or PREPARED
            valid_states = {TransactionState.ACTIVE, TransactionState.PREPARED}
            return not all(p.state in valid_states for p in transaction.participants)

        elif transaction.current_phase == TransactionPhase.COMMIT:
            # During commit phase, participants should be PREPARED or COMMITTED
            valid_states = {TransactionState.PREPARED, TransactionState.COMMITTED}
            return not all(p.state in valid_states for p in transaction.participants)

        elif transaction.current_phase == TransactionPhase.ABORT:
            # During abort phase, participants should be ABORTED
            return not all(p.state == TransactionState.ABORTED for p in transaction.participants)

        return False

    async def resolve_hanging_transaction(self, transaction_id: str) -> Dict[str, str]:
        """Attempt to resolve a hanging distributed transaction"""
        transaction = self.active_transactions.get(transaction_id)
        if not transaction:
            return {'status': 'error', 'message': 'Transaction not found'}

        self.logger.info(f"Attempting to resolve hanging transaction {transaction_id}")

        # Check if we can determine the outcome
        if transaction.current_phase == TransactionPhase.PREPARE:
            # Check if all participants are prepared
            all_prepared = all(p.state == TransactionState.PREPARED for p in transaction.participants)

            if all_prepared:
                # All participants prepared, attempt commit
                result = await self.force_commit_transaction(transaction)
            else:
                # Some participants not prepared, abort
                result = await self.force_abort_transaction(transaction)
        else:
            # Transaction in commit or abort phase, need coordinator recovery
            result = await self.recover_coordinator_state(transaction)

        return result

    async def force_commit_transaction(self, transaction: DistributedTransaction) -> Dict[str, str]:
        """Force commit a prepared transaction"""
        self.logger.info(f"Force committing transaction {transaction.transaction_id}")

        commit_results = []
        for participant in transaction.participants:
            try:
                async with aiohttp.ClientSession() as session:
                    commit_data = {
                        'transaction_id': transaction.transaction_id,
                        'action': 'commit'
                    }
                    async with session.post(f"http://{participant.endpoint}/transaction/commit",
                                          json=commit_data) as response:
                        if response.status == 200:
                            commit_results.append(f"{participant.participant_id}: committed")
                        else:
                            commit_results.append(f"{participant.participant_id}: commit failed ({response.status})")
            except Exception as e:
                commit_results.append(f"{participant.participant_id}: error - {e}")

        return {
            'status': 'completed',
            'action': 'force_commit',
            'results': commit_results
        }

    async def force_abort_transaction(self, transaction: DistributedTransaction) -> Dict[str, str]:
        """Force abort a transaction"""
        self.logger.info(f"Force aborting transaction {transaction.transaction_id}")

        abort_results = []
        for participant in transaction.participants:
            try:
                async with aiohttp.ClientSession() as session:
                    abort_data = {
                        'transaction_id': transaction.transaction_id,
                        'action': 'abort'
                    }
                    async with session.post(f"http://{participant.endpoint}/transaction/abort",
                                          json=abort_data) as response:
                        if response.status == 200:
                            abort_results.append(f"{participant.participant_id}: aborted")
                        else:
                            abort_results.append(f"{participant.participant_id}: abort failed ({response.status})")
            except Exception as e:
                abort_results.append(f"{participant.participant_id}: error - {e}")

        return {
            'status': 'completed',
            'action': 'force_abort',
            'results': abort_results
        }

    async def recover_coordinator_state(self, transaction: DistributedTransaction) -> Dict[str, str]:
        """Recover coordinator state by querying participants"""
        self.logger.info(f"Recovering coordinator state for transaction {transaction.transaction_id}")

        participant_states = []
        for participant in transaction.participants:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"http://{participant.endpoint}/transaction/{transaction.transaction_id}/state") as response:
                        if response.status == 200:
                            data = await response.json()
                            participant_states.append({
                                'participant': participant.participant_id,
                                'state': data.get('state'),
                                'committed': data.get('committed', False)
                            })
            except Exception as e:
                self.logger.error(f"Failed to get state from {participant.participant_id}: {e}")

        # Determine global state from participant states
        if all(p.get('committed', False) for p in participant_states):
            global_decision = 'committed'
        elif any(p.get('state') == 'aborted' for p in participant_states):
            global_decision = 'aborted'
        else:
            global_decision = 'uncertain'

        return {
            'status': 'recovered',
            'global_decision': global_decision,
            'participant_states': participant_states
        }

# Usage example
async def main():
    monitor = DistributedTransactionMonitor([
        'coordinator1:8080',
        'coordinator2:8080',
        'coordinator3:8080'
    ])

    # Check for inconsistencies
    inconsistencies = await monitor.check_transaction_consistency()

    if any(inconsistencies.values()):
        print("Data consistency issues detected:")
        for issue_type, transactions in inconsistencies.items():
            if transactions:
                print(f"  {issue_type}: {transactions}")

        # Attempt to resolve hanging transactions
        for tx_id in inconsistencies['hanging_transactions']:
            result = await monitor.resolve_hanging_transaction(tx_id)
            print(f"Resolution attempt for {tx_id}: {result}")

# Run the monitor
if __name__ == '__main__':
    asyncio.run(main())
```

## Event Sourcing Consistency Issues

### 1. Event Store Consistency Check
```python
# Event sourcing consistency validation
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json

@dataclass
class Event:
    event_id: str
    aggregate_id: str
    event_type: str
    event_data: Dict[str, Any]
    version: int
    timestamp: datetime
    correlation_id: Optional[str] = None

@dataclass
class AggregateSnapshot:
    aggregate_id: str
    version: int
    state: Dict[str, Any]
    timestamp: datetime

class EventStoreConsistencyChecker:
    def __init__(self, event_store_connection):
        self.event_store = event_store_connection

    async def check_event_stream_consistency(self, aggregate_id: str) -> Dict[str, Any]:
        """Check consistency of event stream for an aggregate"""
        events = await self.get_events_for_aggregate(aggregate_id)

        consistency_report = {
            'aggregate_id': aggregate_id,
            'total_events': len(events),
            'issues': [],
            'sequence_gaps': [],
            'duplicate_versions': [],
            'timestamp_anomalies': [],
            'data_integrity_errors': []
        }

        # Check version sequence
        expected_version = 1
        seen_versions = set()

        for event in events:
            # Check for sequence gaps
            if event.version != expected_version:
                consistency_report['sequence_gaps'].append({
                    'expected': expected_version,
                    'actual': event.version,
                    'event_id': event.event_id
                })

            # Check for duplicate versions
            if event.version in seen_versions:
                consistency_report['duplicate_versions'].append({
                    'version': event.version,
                    'event_id': event.event_id
                })
            else:
                seen_versions.add(event.version)

            expected_version = event.version + 1

        # Check timestamp ordering
        for i in range(1, len(events)):
            if events[i].timestamp < events[i-1].timestamp:
                consistency_report['timestamp_anomalies'].append({
                    'previous_event': events[i-1].event_id,
                    'current_event': events[i].event_id,
                    'timestamp_regression': (events[i-1].timestamp - events[i].timestamp).total_seconds()
                })

        # Check data integrity with checksums
        for event in events:
            expected_checksum = self.calculate_event_checksum(event)
            stored_checksum = await self.get_stored_event_checksum(event.event_id)

            if expected_checksum != stored_checksum:
                consistency_report['data_integrity_errors'].append({
                    'event_id': event.event_id,
                    'expected_checksum': expected_checksum,
                    'stored_checksum': stored_checksum
                })

        return consistency_report

    def calculate_event_checksum(self, event: Event) -> str:
        """Calculate checksum for event data integrity"""
        event_content = {
            'event_id': event.event_id,
            'aggregate_id': event.aggregate_id,
            'event_type': event.event_type,
            'event_data': event.event_data,
            'version': event.version
        }

        content_json = json.dumps(event_content, sort_keys=True)
        return hashlib.sha256(content_json.encode()).hexdigest()

    async def repair_event_sequence_gaps(self, aggregate_id: str, gaps: List[Dict]) -> Dict[str, Any]:
        """Attempt to repair sequence gaps in event stream"""
        repair_report = {
            'aggregate_id': aggregate_id,
            'gaps_processed': 0,
            'successful_repairs': 0,
            'failed_repairs': []
        }

        for gap in gaps:
            repair_report['gaps_processed'] += 1

            try:
                # Look for missing events in backup or other replicas
                missing_event = await self.find_missing_event(aggregate_id, gap['expected'])

                if missing_event:
                    # Insert missing event
                    await self.insert_missing_event(missing_event)
                    repair_report['successful_repairs'] += 1
                else:
                    # Create compensating event or mark as unrecoverable
                    compensating_event = await self.create_compensating_event(aggregate_id, gap)
                    if compensating_event:
                        await self.insert_missing_event(compensating_event)
                        repair_report['successful_repairs'] += 1
                    else:
                        repair_report['failed_repairs'].append(gap)

            except Exception as e:
                repair_report['failed_repairs'].append({**gap, 'error': str(e)})

        return repair_report

    async def validate_aggregate_consistency(self, aggregate_id: str) -> Dict[str, Any]:
        """Validate that aggregate state is consistent with event stream"""
        events = await self.get_events_for_aggregate(aggregate_id)
        current_snapshot = await self.get_aggregate_snapshot(aggregate_id)

        # Rebuild state from events
        rebuilt_state = await self.rebuild_aggregate_from_events(events)

        consistency_check = {
            'aggregate_id': aggregate_id,
            'snapshot_version': current_snapshot.version if current_snapshot else 0,
            'rebuilt_version': len(events),
            'state_matches': False,
            'discrepancies': []
        }

        if current_snapshot:
            # Compare rebuilt state with snapshot
            state_diff = self.compare_aggregate_states(current_snapshot.state, rebuilt_state)
            consistency_check['state_matches'] = len(state_diff) == 0
            consistency_check['discrepancies'] = state_diff

        return consistency_check

    def compare_aggregate_states(self, snapshot_state: Dict, rebuilt_state: Dict) -> List[Dict]:
        """Compare two aggregate states and return differences"""
        differences = []

        all_keys = set(snapshot_state.keys()) | set(rebuilt_state.keys())

        for key in all_keys:
            snapshot_value = snapshot_state.get(key)
            rebuilt_value = rebuilt_state.get(key)

            if snapshot_value != rebuilt_value:
                differences.append({
                    'field': key,
                    'snapshot_value': snapshot_value,
                    'rebuilt_value': rebuilt_value
                })

        return differences

    async def get_events_for_aggregate(self, aggregate_id: str) -> List[Event]:
        """Get all events for an aggregate (mock implementation)"""
        # This would query your actual event store
        pass

    async def get_aggregate_snapshot(self, aggregate_id: str) -> Optional[AggregateSnapshot]:
        """Get current snapshot for an aggregate (mock implementation)"""
        # This would query your snapshot store
        pass

    async def rebuild_aggregate_from_events(self, events: List[Event]) -> Dict[str, Any]:
        """Rebuild aggregate state from event stream (mock implementation)"""
        # This would apply all events to build current state
        pass
```

### 2. CQRS Synchronization Monitoring
```python
# CQRS read model synchronization monitoring
import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class ProjectionHealth:
    projection_name: str
    last_processed_event: str
    last_processed_timestamp: datetime
    lag_seconds: float
    error_count: int
    is_healthy: bool

class CQRSConsistencyMonitor:
    def __init__(self, event_store_endpoint: str, projection_endpoints: Dict[str, str]):
        self.event_store_endpoint = event_store_endpoint
        self.projection_endpoints = projection_endpoints

    async def check_projection_consistency(self) -> Dict[str, ProjectionHealth]:
        """Check consistency of all CQRS projections"""
        latest_event = await self.get_latest_event_from_store()
        projection_health = {}

        for projection_name, endpoint in self.projection_endpoints.items():
            health = await self.check_single_projection_health(
                projection_name, endpoint, latest_event
            )
            projection_health[projection_name] = health

        return projection_health

    async def get_latest_event_from_store(self) -> Dict:
        """Get the latest event from the event store"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.event_store_endpoint}/events/latest") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Failed to get latest event: {response.status}")

    async def check_single_projection_health(self, projection_name: str, endpoint: str, latest_event: Dict) -> ProjectionHealth:
        """Check health of a single projection"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{endpoint}/health") as response:
                    if response.status == 200:
                        health_data = await response.json()

                        last_processed = datetime.fromisoformat(health_data['last_processed_timestamp'])
                        latest_event_time = datetime.fromisoformat(latest_event['timestamp'])
                        lag_seconds = (latest_event_time - last_processed).total_seconds()

                        return ProjectionHealth(
                            projection_name=projection_name,
                            last_processed_event=health_data['last_processed_event'],
                            last_processed_timestamp=last_processed,
                            lag_seconds=lag_seconds,
                            error_count=health_data.get('error_count', 0),
                            is_healthy=lag_seconds < 300 and health_data.get('error_count', 0) == 0  # 5 min threshold
                        )
                    else:
                        return ProjectionHealth(
                            projection_name=projection_name,
                            last_processed_event="",
                            last_processed_timestamp=datetime.min,
                            lag_seconds=float('inf'),
                            error_count=1,
                            is_healthy=False
                        )
        except Exception as e:
            return ProjectionHealth(
                projection_name=projection_name,
                last_processed_event="",
                last_processed_timestamp=datetime.min,
                lag_seconds=float('inf'),
                error_count=1,
                is_healthy=False
            )

    async def rebuild_stale_projection(self, projection_name: str) -> Dict[str, str]:
        """Rebuild a stale projection from event store"""
        endpoint = self.projection_endpoints[projection_name]

        try:
            async with aiohttp.ClientSession() as session:
                rebuild_request = {
                    'action': 'rebuild',
                    'from_beginning': True,
                    'timestamp': datetime.now().isoformat()
                }

                async with session.post(f"{endpoint}/rebuild", json=rebuild_request) as response:
                    if response.status == 202:
                        return {'status': 'accepted', 'message': f'Rebuild initiated for {projection_name}'}
                    else:
                        return {'status': 'error', 'message': f'Rebuild failed with status {response.status}'}
        except Exception as e:
            return {'status': 'error', 'message': f'Rebuild request failed: {e}'}
```

## Cache Coherence Resolution

### 1. Multi-Level Cache Consistency
```python
# Multi-level cache consistency checker and resolver
import asyncio
import aioredis
import asyncpg
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json
import hashlib

@dataclass
class CacheEntry:
    key: str
    value: Any
    ttl: Optional[int]
    timestamp: datetime
    source: str  # 'redis', 'memcached', 'application', 'database'

class CacheCoherenceManager:
    def __init__(self, redis_url: str, db_url: str):
        self.redis_url = redis_url
        self.db_url = db_url
        self.redis_client = None
        self.db_pool = None

    async def initialize(self):
        """Initialize cache and database connections"""
        self.redis_client = await aioredis.from_url(self.redis_url)
        self.db_pool = await asyncpg.create_pool(self.db_url)

    async def check_cache_consistency(self, keys: List[str]) -> Dict[str, Dict[str, Any]]:
        """Check consistency across cache layers and database"""
        consistency_report = {}

        for key in keys:
            entries = await self.get_all_cache_entries(key)
            database_value = await self.get_database_value(key)

            # Add database value to comparison
            if database_value is not None:
                entries['database'] = CacheEntry(
                    key=key,
                    value=database_value,
                    ttl=None,
                    timestamp=datetime.now(),
                    source='database'
                )

            consistency_analysis = self.analyze_cache_consistency(entries)
            consistency_report[key] = {
                'entries': {source: entry.value for source, entry in entries.items()},
                'consistent': consistency_analysis['consistent'],
                'conflicts': consistency_analysis['conflicts'],
                'recommended_action': consistency_analysis['recommended_action']
            }

        return consistency_report

    async def get_all_cache_entries(self, key: str) -> Dict[str, CacheEntry]:
        """Get cache entry from all cache layers"""
        entries = {}

        # Redis cache
        try:
            redis_value = await self.redis_client.get(key)
            if redis_value:
                ttl = await self.redis_client.ttl(key)
                entries['redis'] = CacheEntry(
                    key=key,
                    value=json.loads(redis_value) if redis_value else None,
                    ttl=ttl if ttl > 0 else None,
                    timestamp=datetime.now(),  # Redis doesn't store creation time
                    source='redis'
                )
        except Exception as e:
            print(f"Error getting Redis value for {key}: {e}")

        # Application-level cache (example)
        app_cache_value = await self.get_application_cache_value(key)
        if app_cache_value:
            entries['application'] = CacheEntry(
                key=key,
                value=app_cache_value['value'],
                ttl=app_cache_value.get('ttl'),
                timestamp=datetime.fromisoformat(app_cache_value['timestamp']),
                source='application'
            )

        return entries

    async def get_database_value(self, key: str) -> Optional[Any]:
        """Get authoritative value from database"""
        try:
            # This is a simplified example - adjust based on your schema
            async with self.db_pool.acquire() as connection:
                # Assuming key format like "user:123" maps to users table
                if key.startswith('user:'):
                    user_id = key.split(':')[1]
                    result = await connection.fetchrow(
                        "SELECT * FROM users WHERE id = $1", int(user_id)
                    )
                    return dict(result) if result else None
                elif key.startswith('product:'):
                    product_id = key.split(':')[1]
                    result = await connection.fetchrow(
                        "SELECT * FROM products WHERE id = $1", int(product_id)
                    )
                    return dict(result) if result else None
                # Add more key patterns as needed
        except Exception as e:
            print(f"Error getting database value for {key}: {e}")
            return None

    async def get_application_cache_value(self, key: str) -> Optional[Dict]:
        """Get value from application-level cache (mock implementation)"""
        # This would integrate with your application cache
        # For demo purposes, return None
        return None

    def analyze_cache_consistency(self, entries: Dict[str, CacheEntry]) -> Dict[str, Any]:
        """Analyze consistency between cache entries"""
        if len(entries) <= 1:
            return {'consistent': True, 'conflicts': [], 'recommended_action': 'none'}

        # Create value signatures for comparison
        signatures = {}
        for source, entry in entries.items():
            # Use hash of JSON representation for comparison
            value_json = json.dumps(entry.value, sort_keys=True) if entry.value else "null"
            signatures[source] = hashlib.md5(value_json.encode()).hexdigest()

        unique_signatures = set(signatures.values())
        consistent = len(unique_signatures) <= 1

        conflicts = []
        if not consistent:
            # Identify conflicts
            signature_groups = {}
            for source, signature in signatures.items():
                if signature not in signature_groups:
                    signature_groups[signature] = []
                signature_groups[signature].append(source)

            for signature, sources in signature_groups.items():
                if len(sources) > 1:
                    conflicts.append({
                        'signature': signature,
                        'sources': sources,
                        'value': entries[sources[0]].value
                    })

        # Recommend action based on analysis
        recommended_action = 'none'
        if not consistent:
            if 'database' in entries:
                recommended_action = 'invalidate_caches'  # Database is source of truth
            else:
                recommended_action = 'manual_resolution'

        return {
            'consistent': consistent,
            'conflicts': conflicts,
            'recommended_action': recommended_action
        }

    async def resolve_cache_inconsistency(self, key: str, strategy: str = 'database_wins') -> Dict[str, str]:
        """Resolve cache inconsistency using specified strategy"""
        if strategy == 'database_wins':
            return await self.resolve_with_database_authority(key)
        elif strategy == 'latest_timestamp_wins':
            return await self.resolve_with_latest_timestamp(key)
        elif strategy == 'invalidate_all':
            return await self.invalidate_all_cache_entries(key)
        else:
            return {'status': 'error', 'message': f'Unknown resolution strategy: {strategy}'}

    async def resolve_with_database_authority(self, key: str) -> Dict[str, str]:
        """Resolve inconsistency by using database as source of truth"""
        database_value = await self.get_database_value(key)

        if database_value is None:
            # Database has no value, invalidate all caches
            return await self.invalidate_all_cache_entries(key)

        # Update all cache layers with database value
        try:
            # Update Redis
            await self.redis_client.set(
                key,
                json.dumps(database_value),
                ex=3600  # 1 hour TTL
            )

            # Update application cache (if applicable)
            await self.update_application_cache(key, database_value)

            return {
                'status': 'resolved',
                'strategy': 'database_authority',
                'message': f'Updated all caches with database value for {key}'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to update caches: {e}'
            }

    async def resolve_with_latest_timestamp(self, key: str) -> Dict[str, str]:
        """Resolve inconsistency by using entry with latest timestamp"""
        entries = await self.get_all_cache_entries(key)

        if not entries:
            return {'status': 'error', 'message': 'No cache entries found'}

        # Find entry with latest timestamp
        latest_entry = max(entries.values(), key=lambda e: e.timestamp)

        # Update all other caches with latest value
        try:
            for source, entry in entries.items():
                if entry.timestamp < latest_entry.timestamp:
                    if source == 'redis':
                        await self.redis_client.set(
                            key,
                            json.dumps(latest_entry.value),
                            ex=3600
                        )
                    elif source == 'application':
                        await self.update_application_cache(key, latest_entry.value)

            return {
                'status': 'resolved',
                'strategy': 'latest_timestamp',
                'message': f'Updated caches with latest value from {latest_entry.source}'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to resolve with latest timestamp: {e}'
            }

    async def invalidate_all_cache_entries(self, key: str) -> Dict[str, str]:
        """Invalidate all cache entries for a key"""
        try:
            # Invalidate Redis
            await self.redis_client.delete(key)

            # Invalidate application cache
            await self.invalidate_application_cache(key)

            return {
                'status': 'resolved',
                'strategy': 'invalidate_all',
                'message': f'Invalidated all cache entries for {key}'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to invalidate caches: {e}'
            }

    async def update_application_cache(self, key: str, value: Any):
        """Update application-level cache (mock implementation)"""
        # This would integrate with your application cache
        pass

    async def invalidate_application_cache(self, key: str):
        """Invalidate application-level cache (mock implementation)"""
        # This would integrate with your application cache
        pass

# Usage example
async def main():
    cache_manager = CacheCoherenceManager('redis://localhost', 'postgresql://user:pass@localhost/db')
    await cache_manager.initialize()

    # Check consistency for critical keys
    critical_keys = ['user:12345', 'product:67890', 'config:system']
    consistency_report = await cache_manager.check_cache_consistency(critical_keys)

    for key, report in consistency_report.items():
        if not report['consistent']:
            print(f"Inconsistency detected for {key}")
            print(f"Conflicts: {report['conflicts']}")

            # Resolve inconsistency
            resolution = await cache_manager.resolve_cache_inconsistency(key, 'database_wins')
            print(f"Resolution: {resolution}")

if __name__ == '__main__':
    asyncio.run(main())
```

## Production Case Studies

### Case Study 1: Stripe - Payment Processing Inconsistency

**Problem**: Payment transactions showing as "pending" in one service but "completed" in another, causing double charges

**Investigation Process**:
1. **Transaction log analysis** revealed distributed transaction coordinator failures
2. **Database isolation level** check showed insufficient isolation
3. **Event sourcing** analysis found missing compensation events

**Commands Used**:
```sql
-- Check for transaction inconsistencies
SELECT
    payment_id,
    status,
    created_at,
    updated_at
FROM payments
WHERE payment_id IN (
    SELECT payment_id
    FROM payment_events
    GROUP BY payment_id
    HAVING COUNT(DISTINCT status) > 1
);

-- Analyze event store consistency
SELECT
    aggregate_id,
    version,
    event_type,
    created_at,
    LAG(version) OVER (PARTITION BY aggregate_id ORDER BY version) as prev_version
FROM payment_events
WHERE aggregate_id = 'payment_12345'
AND version != (LAG(version) OVER (PARTITION BY aggregate_id ORDER BY version) + 1);
```

**Resolution**: Implemented saga pattern with compensation, added proper distributed transaction monitoring
**Time to Resolution**: 6 hours

### Case Study 2: Airbnb - Booking Double-Allocation

**Problem**: Same property booked by multiple guests for overlapping dates due to race conditions

**Root Cause**: Insufficient read-after-write consistency in reservation system

**Investigation Commands**:
```sql
-- Find conflicting bookings
SELECT
    property_id,
    guest_id,
    check_in,
    check_out,
    created_at
FROM bookings b1
WHERE EXISTS (
    SELECT 1 FROM bookings b2
    WHERE b2.property_id = b1.property_id
    AND b2.id != b1.id
    AND (
        (b2.check_in <= b1.check_in AND b2.check_out > b1.check_in) OR
        (b2.check_in < b1.check_out AND b2.check_out >= b1.check_out) OR
        (b2.check_in >= b1.check_in AND b2.check_out <= b1.check_out)
    )
)
ORDER BY property_id, check_in;

-- Check for read replica lag
SELECT
    client_addr,
    state,
    replay_lag
FROM pg_stat_replication
WHERE replay_lag > interval '5 seconds';
```

**Resolution**: Implemented optimistic locking with version fields, added read-from-master for critical booking operations
**Time to Resolution**: 4 hours

### Case Study 3: Shopify - Order Inventory Mismatch

**Problem**: Orders processing successfully despite insufficient inventory, causing overselling

**Root Cause**: Cache coherence issues between inventory cache and database

**Investigation Process**:
```python
# Python script to check inventory consistency
import redis
import psycopg2

def check_inventory_consistency():
    redis_client = redis.Redis()
    db_conn = psycopg2.connect("postgresql://...")

    inconsistencies = []

    # Get all cached inventory
    cached_keys = redis_client.keys('inventory:*')

    for key in cached_keys:
        product_id = key.decode().split(':')[1]
        cached_quantity = int(redis_client.get(key) or 0)

        # Get database quantity
        cursor = db_conn.cursor()
        cursor.execute("SELECT quantity FROM inventory WHERE product_id = %s", (product_id,))
        result = cursor.fetchone()
        db_quantity = result[0] if result else 0

        if cached_quantity != db_quantity:
            inconsistencies.append({
                'product_id': product_id,
                'cached_quantity': cached_quantity,
                'db_quantity': db_quantity,
                'difference': cached_quantity - db_quantity
            })

    return inconsistencies

inconsistencies = check_inventory_consistency()
for item in inconsistencies:
    print(f"Product {item['product_id']}: Cache={item['cached_quantity']}, DB={item['db_quantity']}")
```

**Resolution**: Implemented cache-aside pattern with write-through updates, added inventory reconciliation job
**Time to Resolution**: 3 hours

## 3 AM Debugging Checklist

When you're called at 3 AM for data inconsistency issues:

### First 2 Minutes
- [ ] Identify which systems are showing inconsistent data
- [ ] Check if issue is affecting active transactions
- [ ] Verify database replication status and lag
- [ ] Look for recent deployments or configuration changes

### Minutes 2-5
- [ ] Check cache hit/miss ratios and invalidation patterns
- [ ] Verify distributed transaction coordinator health
- [ ] Look for isolation level or locking issues
- [ ] Check event sourcing projection lag

### Minutes 5-15
- [ ] Compare data checksums between systems
- [ ] Analyze recent transaction logs for anomalies
- [ ] Check for network partitions or service failures
- [ ] Validate that compensating actions completed

### If Still Debugging After 15 Minutes
- [ ] Escalate to senior engineer or data team lead
- [ ] Consider forcing cache invalidation for affected keys
- [ ] Implement temporary read-from-source-of-truth
- [ ] Document inconsistent state for detailed analysis

## Data Consistency Metrics and SLOs

### Key Metrics to Track
- **Replication lag** across all read replicas
- **Cache hit ratio** and invalidation frequency
- **Transaction rollback rate** for distributed transactions
- **Event sourcing projection lag**
- **Data integrity check failures**

### Example SLO Configuration
```yaml
data_consistency_slos:
  - name: "Replication Lag"
    description: "Database replica lag stays below 5 seconds"
    metric: "pg_stat_replication_replay_lag_seconds"
    target: 5
    window: "5m"

  - name: "Cache Coherence"
    description: "Cache inconsistency rate stays below 0.1%"
    metric: "cache_inconsistencies / cache_validations"
    target: 0.001
    window: "1h"
```

**Remember**: Data consistency issues can have financial and legal implications. When in doubt, prioritize data integrity over performance. Always have compensating mechanisms ready for when consistency guarantees are violated.

This guide represents proven strategies from teams managing consistent data across globally distributed systems processing millions of transactions daily.