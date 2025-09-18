# PostgreSQL Streaming Replication

## Architecture Overview

PostgreSQL streaming replication uses Write-Ahead Logging (WAL) to provide real-time data replication from a primary server to one or more standby servers.

### Streaming Replication Components

```mermaid
graph TB
    subgraph PostgreSQL Streaming Replication Architecture
        subgraph Primary Server
            WAL_WRITER[WAL Writer Process]
            WAL_SENDER[WAL Sender Process]
            WAL_FILES[WAL Files<br/>- 16MB segments<br/>- Sequential writing<br/>- Archived after use]
            POSTGRES_PRIMARY[PostgreSQL Primary<br/>- Accepts writes<br/>- Generates WAL<br/>- Manages replication]
        end

        subgraph Standby Server
            WAL_RECEIVER[WAL Receiver Process]
            WAL_REPLAY[Startup Process<br/>(WAL Replay)]
            POSTGRES_STANDBY[PostgreSQL Standby<br/>- Read-only<br/>- Applies WAL changes<br/>- Can serve reads]
            STANDBY_WAL[Standby WAL Files]
        end

        subgraph Network Connection
            STREAM[Replication Stream<br/>- TCP connection<br/>- Continuous streaming<br/>- Async/Sync modes]
        end

        subgraph Clients
            WRITE_CLIENT[Write Clients]
            READ_CLIENT[Read Clients]
        end
    end

    WRITE_CLIENT --> POSTGRES_PRIMARY
    READ_CLIENT --> POSTGRES_STANDBY

    POSTGRES_PRIMARY --> WAL_WRITER
    WAL_WRITER --> WAL_FILES
    WAL_FILES --> WAL_SENDER
    WAL_SENDER --> STREAM
    STREAM --> WAL_RECEIVER
    WAL_RECEIVER --> STANDBY_WAL
    STANDBY_WAL --> WAL_REPLAY
    WAL_REPLAY --> POSTGRES_STANDBY

    %% Apply 4-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class WRITE_CLIENT,READ_CLIENT edgeStyle
    class POSTGRES_PRIMARY,POSTGRES_STANDBY,WAL_WRITER,WAL_RECEIVER,WAL_REPLAY serviceStyle
    class WAL_FILES,STANDBY_WAL,STREAM stateStyle
    class WAL_SENDER controlStyle
```

### WAL Record Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant P as Primary
    participant W as WAL Writer
    participant S as WAL Sender
    participant R as WAL Receiver
    participant T as Standby

    Note over C,T: PostgreSQL Streaming Replication Flow

    C->>P: BEGIN; INSERT INTO users...; COMMIT;
    P->>P: Generate WAL records
    P->>W: Write WAL to buffer

    alt Synchronous Commit
        W->>W: fsync() WAL to disk
        W-->>P: WAL safely written
        P->>S: Notify new WAL available
        S->>R: Stream WAL records
        R->>R: Write WAL to standby
        R-->>S: ACK WAL received
        S-->>P: Standby confirmed
        P->>C: COMMIT successful
    else Asynchronous Commit
        P->>C: COMMIT successful (immediate)
        W->>W: fsync() WAL to disk (async)
        W->>S: Notify new WAL available
        S->>R: Stream WAL records (async)
        R->>R: Write WAL to standby
        R->>T: Apply WAL changes
    end

    Note over T: Standby applies changes and serves reads
```

## Configuration and Setup

### Primary Server Configuration

```sql
-- postgresql.conf on primary server
-- WAL Configuration
wal_level = replica                    -- Enable WAL for replication
max_wal_senders = 10                   -- Max concurrent WAL sender processes
wal_keep_segments = 64                 -- Keep WAL segments for standbys
max_replication_slots = 10             -- Replication slots for reliability

-- Archiving (optional but recommended)
archive_mode = on
archive_command = 'test ! -f /var/lib/postgresql/archive/%f && cp %p /var/lib/postgresql/archive/%f'

-- Synchronous replication (optional)
synchronous_standby_names = 'standby1,standby2'
synchronous_commit = on                -- Wait for standby confirmation

-- Connection settings
listen_addresses = '*'
port = 5432
max_connections = 200

-- Performance tuning
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
```

```sql
-- pg_hba.conf on primary server
# Allow replication connections
host    replication     replicator      10.0.1.0/24            md5
host    replication     replicator      standby1.internal       md5
host    replication     replicator      standby2.internal       md5

# Allow application connections
host    all             all             10.0.1.0/24            md5
```

### Standby Server Configuration

```sql
-- postgresql.conf on standby server
-- Basic standby configuration
primary_conninfo = 'host=primary.internal port=5432 user=replicator password=secret application_name=standby1'
primary_slot_name = 'standby1_slot'   -- Use replication slot

-- Hot standby (allow read queries)
hot_standby = on
hot_standby_feedback = on              -- Send feedback to primary
max_standby_streaming_delay = 30s      -- Max delay for queries
max_standby_archive_delay = 300s       -- Max delay for archived WAL

-- Connection settings (same as primary for consistency)
port = 5432
max_connections = 200

-- Recovery settings (PostgreSQL 12+)
restore_command = 'cp /var/lib/postgresql/archive/%f %p'
recovery_target_timeline = 'latest'
```

```bash
# Create standby.signal file to indicate standby mode
touch /var/lib/postgresql/data/standby.signal
```

### Replication Slot Setup

```sql
-- On primary server: Create replication slots
SELECT pg_create_physical_replication_slot('standby1_slot');
SELECT pg_create_physical_replication_slot('standby2_slot');

-- Monitor replication slots
SELECT
    slot_name,
    slot_type,
    database,
    active,
    restart_lsn,
    confirmed_flush_lsn,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS lag_size
FROM pg_replication_slots;

-- Drop unused replication slots
SELECT pg_drop_replication_slot('unused_slot');
```

## Monitoring and Maintenance

### Replication Status Monitoring

```sql
-- Monitor replication status (run on primary)
SELECT
    pid,
    usename,
    application_name,
    client_addr,
    client_hostname,
    client_port,
    backend_start,
    backend_xmin,
    state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    write_lag,
    flush_lag,
    replay_lag,
    sync_priority,
    sync_state,
    reply_time
FROM pg_stat_replication;

-- Calculate replication lag in bytes
SELECT
    application_name,
    client_addr,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), sent_lsn)) AS send_lag,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), flush_lsn)) AS flush_lag,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn)) AS replay_lag
FROM pg_stat_replication;
```

```sql
-- Monitor replication on standby server
SELECT
    pg_is_in_recovery() AS is_standby,
    pg_last_wal_receive_lsn() AS last_received,
    pg_last_wal_replay_lsn() AS last_replayed,
    CASE
        WHEN pg_last_wal_receive_lsn() = pg_last_wal_replay_lsn() THEN 'Up to date'
        ELSE pg_size_pretty(pg_wal_lsn_diff(pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn()))
    END AS replay_lag,
    pg_last_xact_replay_timestamp() AS last_replay_time,
    EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp())) AS lag_seconds;
```

### Comprehensive Monitoring Script

```python
#!/usr/bin/env python3
# postgresql_replication_monitor.py

import psycopg2
import time
import json
from datetime import datetime
from typing import Dict, List, Optional

class PostgreSQLReplicationMonitor:
    def __init__(self, primary_config: Dict, standby_configs: List[Dict]):
        self.primary_config = primary_config
        self.standby_configs = standby_configs

    def get_primary_stats(self) -> Dict:
        """Get replication statistics from primary server"""
        try:
            conn = psycopg2.connect(**self.primary_config)
            cur = conn.cursor()

            # Get replication status
            cur.execute("""
                SELECT
                    application_name,
                    client_addr::text,
                    state,
                    pg_wal_lsn_diff(pg_current_wal_lsn(), sent_lsn) AS send_lag_bytes,
                    pg_wal_lsn_diff(pg_current_wal_lsn(), flush_lsn) AS flush_lag_bytes,
                    pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS replay_lag_bytes,
                    EXTRACT(EPOCH FROM write_lag) AS write_lag_seconds,
                    EXTRACT(EPOCH FROM flush_lag) AS flush_lag_seconds,
                    EXTRACT(EPOCH FROM replay_lag) AS replay_lag_seconds,
                    sync_state
                FROM pg_stat_replication;
            """)

            replicas = []
            for row in cur.fetchall():
                replicas.append({
                    'application_name': row[0],
                    'client_addr': row[1],
                    'state': row[2],
                    'send_lag_bytes': row[3] or 0,
                    'flush_lag_bytes': row[4] or 0,
                    'replay_lag_bytes': row[5] or 0,
                    'write_lag_seconds': row[6] or 0,
                    'flush_lag_seconds': row[7] or 0,
                    'replay_lag_seconds': row[8] or 0,
                    'sync_state': row[9]
                })

            # Get WAL generation rate
            cur.execute("SELECT pg_current_wal_lsn()")
            current_wal_lsn = cur.fetchone()[0]

            # Get replication slot information
            cur.execute("""
                SELECT
                    slot_name,
                    active,
                    pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) AS slot_lag_bytes
                FROM pg_replication_slots
                WHERE slot_type = 'physical';
            """)

            slots = []
            for row in cur.fetchall():
                slots.append({
                    'slot_name': row[0],
                    'active': row[1],
                    'lag_bytes': row[2] or 0
                })

            conn.close()

            return {
                'timestamp': datetime.now().isoformat(),
                'role': 'primary',
                'current_wal_lsn': current_wal_lsn,
                'replicas': replicas,
                'replication_slots': slots,
                'total_replicas': len(replicas),
                'active_replicas': len([r for r in replicas if r['state'] == 'streaming'])
            }

        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'role': 'primary',
                'error': str(e)
            }

    def get_standby_stats(self, standby_config: Dict) -> Dict:
        """Get replication statistics from standby server"""
        try:
            conn = psycopg2.connect(**standby_config)
            cur = conn.cursor()

            # Check if this is actually a standby
            cur.execute("SELECT pg_is_in_recovery()")
            is_standby = cur.fetchone()[0]

            if not is_standby:
                conn.close()
                return {
                    'timestamp': datetime.now().isoformat(),
                    'host': standby_config['host'],
                    'role': 'primary',  # This server is not in recovery
                    'error': 'Server is not in standby mode'
                }

            # Get standby-specific statistics
            cur.execute("""
                SELECT
                    pg_last_wal_receive_lsn(),
                    pg_last_wal_replay_lsn(),
                    pg_wal_lsn_diff(pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn()) AS receive_replay_lag,
                    pg_last_xact_replay_timestamp(),
                    EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp())) AS time_lag_seconds
            """)

            row = cur.fetchone()
            last_received = row[0]
            last_replayed = row[1]
            receive_replay_lag = row[2] or 0
            last_replay_time = row[3]
            time_lag_seconds = row[4] or 0

            # Get conflict statistics
            cur.execute("""
                SELECT
                    confl_tablespace,
                    confl_lock,
                    confl_snapshot,
                    confl_bufferpin,
                    confl_deadlock
                FROM pg_stat_database_conflicts
                WHERE datname = current_database();
            """)

            conflicts = cur.fetchone()
            total_conflicts = sum(conflicts) if conflicts else 0

            conn.close()

            return {
                'timestamp': datetime.now().isoformat(),
                'host': standby_config['host'],
                'role': 'standby',
                'last_received_lsn': last_received,
                'last_replayed_lsn': last_replayed,
                'receive_replay_lag_bytes': receive_replay_lag,
                'last_replay_time': last_replay_time.isoformat() if last_replay_time else None,
                'time_lag_seconds': time_lag_seconds,
                'conflicts': {
                    'tablespace': conflicts[0] if conflicts else 0,
                    'lock': conflicts[1] if conflicts else 0,
                    'snapshot': conflicts[2] if conflicts else 0,
                    'bufferpin': conflicts[3] if conflicts else 0,
                    'deadlock': conflicts[4] if conflicts else 0,
                    'total': total_conflicts
                },
                'status': self._get_standby_status(time_lag_seconds, total_conflicts)
            }

        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'host': standby_config['host'],
                'role': 'standby',
                'error': str(e)
            }

    def _get_standby_status(self, lag_seconds: float, conflicts: int) -> str:
        """Determine standby health status"""
        if lag_seconds > 300:  # 5 minutes
            return 'critical'
        elif lag_seconds > 60:  # 1 minute
            return 'warning'
        elif conflicts > 100:
            return 'warning'
        else:
            return 'healthy'

    def generate_health_report(self) -> Dict:
        """Generate comprehensive replication health report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'primary': self.get_primary_stats(),
            'standbys': [],
            'summary': {
                'total_standbys': len(self.standby_configs),
                'healthy_standbys': 0,
                'warning_standbys': 0,
                'critical_standbys': 0,
                'max_lag_seconds': 0,
                'avg_lag_seconds': 0
            }
        }

        # Collect standby statistics
        total_lag = 0
        valid_standbys = 0

        for standby_config in self.standby_configs:
            standby_stats = self.get_standby_stats(standby_config)
            report['standbys'].append(standby_stats)

            if 'error' not in standby_stats:
                status = standby_stats.get('status', 'unknown')
                report['summary'][f'{status}_standbys'] += 1

                lag_seconds = standby_stats.get('time_lag_seconds', 0)
                report['summary']['max_lag_seconds'] = max(
                    report['summary']['max_lag_seconds'],
                    lag_seconds
                )
                total_lag += lag_seconds
                valid_standbys += 1

        if valid_standbys > 0:
            report['summary']['avg_lag_seconds'] = total_lag / valid_standbys

        return report

    def monitor_continuously(self, interval_seconds: int = 30):
        """Run continuous monitoring"""
        print("Starting PostgreSQL replication monitoring...")
        print(f"Monitoring interval: {interval_seconds} seconds")

        while True:
            try:
                report = self.generate_health_report()

                # Print summary
                summary = report['summary']
                print(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Replication Status:")
                print(f"  Standbys: {summary['healthy_standbys']} healthy, "
                      f"{summary['warning_standbys']} warning, "
                      f"{summary['critical_standbys']} critical")
                print(f"  Max lag: {summary['max_lag_seconds']:.2f}s, "
                      f"Avg lag: {summary['avg_lag_seconds']:.2f}s")

                # Print detailed standby info
                for standby in report['standbys']:
                    if 'error' in standby:
                        print(f"  {standby['host']}: ERROR - {standby['error']}")
                    else:
                        print(f"  {standby['host']}: {standby['status']} - "
                              f"lag: {standby['time_lag_seconds']:.2f}s")

                time.sleep(interval_seconds)

            except KeyboardInterrupt:
                print("\nMonitoring stopped.")
                break
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(interval_seconds)

if __name__ == "__main__":
    # Configuration
    primary_config = {
        'host': 'pg-primary.internal',
        'port': 5432,
        'database': 'postgres',
        'user': 'monitor',
        'password': 'secret'
    }

    standby_configs = [
        {
            'host': 'pg-standby-1.internal',
            'port': 5432,
            'database': 'postgres',
            'user': 'monitor',
            'password': 'secret'
        },
        {
            'host': 'pg-standby-2.internal',
            'port': 5432,
            'database': 'postgres',
            'user': 'monitor',
            'password': 'secret'
        }
    ]

    monitor = PostgreSQLReplicationMonitor(primary_config, standby_configs)

    # Generate single report
    report = monitor.generate_health_report()
    print(json.dumps(report, indent=2, default=str))

    # Or run continuous monitoring
    # monitor.monitor_continuously(30)
```

## Failover and Recovery

### Automatic Failover with Patroni

```yaml
# patroni.yml configuration for automatic failover
scope: postgresql-cluster
name: postgresql-primary

restapi:
  listen: 0.0.0.0:8008
  connect_address: postgresql-primary.internal:8008

etcd3:
  hosts: etcd1.internal:2379,etcd2.internal:2379,etcd3.internal:2379

bootstrap:
  dcs:
    ttl: 30
    loop_wait: 10
    retry_timeout: 30
    maximum_lag_on_failover: 1048576  # 1MB
    master_start_timeout: 300
    synchronous_mode: true
    synchronous_mode_strict: false
    postgresql:
      use_pg_rewind: true
      use_slots: true
      parameters:
        wal_level: replica
        hot_standby: "on"
        max_connections: 200
        max_worker_processes: 8
        wal_keep_segments: 32
        max_wal_senders: 10
        max_replication_slots: 10
        hot_standby_feedback: "on"

  initdb:
    - encoding: UTF8
    - data-checksums

postgresql:
  listen: 0.0.0.0:5432
  connect_address: postgresql-primary.internal:5432
  data_dir: /var/lib/postgresql/data
  bin_dir: /usr/lib/postgresql/13/bin
  pgpass: /var/lib/postgresql/.pgpass
  authentication:
    replication:
      username: replicator
      password: replication_password
    superuser:
      username: postgres
      password: postgres_password

tags:
  nofailover: false
  noloadbalance: false
  clonefrom: false
  nosync: false
```

### Manual Failover Process

```bash
#!/bin/bash
# manual_failover.sh

set -e

PRIMARY_HOST="pg-primary.internal"
STANDBY_HOST="pg-standby-1.internal"
POSTGRES_USER="postgres"

echo "=== PostgreSQL Manual Failover Process ==="

echo "Step 1: Stop writes to primary"
echo "- Update application configuration to stop writes"
echo "- Wait for current transactions to complete"
read -p "Press Enter when writes are stopped..."

echo "Step 2: Check replication lag"
psql -h $STANDBY_HOST -U $POSTGRES_USER -c "
    SELECT
        CASE
            WHEN pg_last_wal_receive_lsn() = pg_last_wal_replay_lsn() THEN 'Up to date'
            ELSE 'Lag: ' || pg_size_pretty(pg_wal_lsn_diff(pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn()))
        END AS replication_status;
"

echo "Step 3: Shutdown primary server"
echo "Shutting down primary PostgreSQL..."
ssh $PRIMARY_HOST "sudo systemctl stop postgresql"

echo "Step 4: Promote standby to primary"
echo "Promoting standby..."
ssh $STANDBY_HOST "sudo -u postgres pg_ctl promote -D /var/lib/postgresql/data"

echo "Step 5: Update DNS/Load balancer"
echo "- Update DNS to point to new primary: $STANDBY_HOST"
echo "- Update application configuration"
echo "- Update connection pools"

echo "Step 6: Verify new primary"
psql -h $STANDBY_HOST -U $POSTGRES_USER -c "
    SELECT
        pg_is_in_recovery() AS is_standby,
        CASE
            WHEN pg_is_in_recovery() THEN 'Still in recovery mode'
            ELSE 'Successfully promoted to primary'
        END AS status;
"

echo "Step 7: Configure old primary as new standby (optional)"
echo "Would you like to configure the old primary as a standby? (y/n)"
read -r configure_standby

if [ "$configure_standby" = "y" ]; then
    echo "Setting up old primary as standby..."

    # Create recovery configuration
    ssh $PRIMARY_HOST "sudo -u postgres cat > /var/lib/postgresql/data/postgresql.conf << EOF
primary_conninfo = 'host=$STANDBY_HOST port=5432 user=replicator'
restore_command = 'cp /var/lib/postgresql/archive/%f %p'
recovery_target_timeline = 'latest'
EOF"

    # Create standby.signal
    ssh $PRIMARY_HOST "sudo -u postgres touch /var/lib/postgresql/data/standby.signal"

    # Start PostgreSQL
    ssh $PRIMARY_HOST "sudo systemctl start postgresql"

    echo "Old primary configured as standby"
fi

echo "=== Failover Complete ==="
echo "New primary: $STANDBY_HOST"
echo "Remember to:"
echo "- Update monitoring configurations"
echo "- Update backup scripts"
echo "- Verify application connectivity"
echo "- Monitor replication if standby was configured"
```

## Performance Tuning

### WAL Optimization

```sql
-- WAL performance tuning parameters
-- postgresql.conf

-- WAL writing
wal_buffers = 16MB                     -- WAL buffer size
wal_writer_delay = 200ms               -- WAL writer sleep time
wal_writer_flush_after = 1MB           -- Force flush after this amount

-- Checkpointing
checkpoint_timeout = 5min              -- Maximum time between checkpoints
max_wal_size = 1GB                     -- Checkpoint when WAL grows beyond this
min_wal_size = 80MB                    -- Keep at least this much WAL
checkpoint_completion_target = 0.9     -- Spread checkpoint I/O
checkpoint_warning = 30s               -- Warn if checkpoints too frequent

-- Background writer
bgwriter_delay = 200ms                 -- Background writer sleep time
bgwriter_lru_maxpages = 100            -- Max pages written per round
bgwriter_lru_multiplier = 2.0          -- Multiple of recent usage
bgwriter_flush_after = 512kB           -- Force OS flush after this amount

-- Asynchronous I/O
effective_io_concurrency = 200         -- Number of concurrent I/O operations
maintenance_io_concurrency = 10       -- Concurrent I/O for maintenance

-- Memory settings for replication
shared_buffers = 256MB                 -- Buffer cache size
work_mem = 4MB                         -- Memory per sort/hash operation
maintenance_work_mem = 64MB            -- Memory for maintenance operations
```

This comprehensive guide covers PostgreSQL streaming replication from basic setup through advanced monitoring, failover procedures, and performance optimization for production environments.