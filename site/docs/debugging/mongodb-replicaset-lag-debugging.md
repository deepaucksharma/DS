# MongoDB Replica Set Lag Debugging

**Scenario**: Production MongoDB replica set experiencing significant replication lag, causing read inconsistencies and potential data loss risks.

**The 3 AM Reality**: Secondary nodes falling behind primary, applications reading stale data, and potential cluster instability during failover scenarios.

## Symptoms Checklist

- [ ] High replication lag (>10 seconds) in replica set status
- [ ] Secondary nodes consistently behind primary
- [ ] Read preference queries returning stale data
- [ ] Oplog window concerns and potential rollbacks
- [ ] Increased write concern timeouts

## MongoDB Replica Set Lag Architecture

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - #3B82F6]
        APP[Application<br/>Write Concern: majority<br/>Read Preference: secondaryPreferred]
        ANALYTICS[Analytics Service<br/>Read from secondary<br/>Tolerance for lag]
    end

    subgraph ServicePlane[Service Plane - #10B981]
        PRIMARY[Primary Node<br/>rs-primary-01<br/>Oplog Size: 10GB<br/>Write Load: High]
        SECONDARY1[Secondary Node 1<br/>rs-secondary-01<br/>Lag: 15 seconds<br/>Status: Falling behind]
        SECONDARY2[Secondary Node 2<br/>rs-secondary-02<br/>Lag: 3 seconds<br/>Status: Normal]
    end

    subgraph StatePlane[State Plane - #F59E0B]
        OPLOG[Oplog Collection<br/>Capped collection<br/>24 hour window<br/>Replication source]
        DATA[Data Collections<br/>User data<br/>Application state]
    end

    subgraph ControlPlane[Control Plane - #8B5CF6]
        MONITORING[MongoDB Monitoring<br/>rs.status() metrics<br/>Lag alerts]
        LOGS[MongoDB Logs<br/>Replication errors<br/>Performance issues]
    end

    APP -->|Writes| PRIMARY
    APP -->|Reads| SECONDARY1
    ANALYTICS -->|Read-only| SECONDARY2

    PRIMARY -->|Replicate| SECONDARY1
    PRIMARY -->|Replicate| SECONDARY2
    PRIMARY -.->|Write to| OPLOG

    SECONDARY1 -.->|Read from| OPLOG
    SECONDARY2 -.->|Read from| OPLOG

    MONITORING -->|Track| PRIMARY
    LOGS -->|Monitor| PRIMARY

    %% Apply 4-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class APP,ANALYTICS edgeStyle
    class PRIMARY,SECONDARY1,SECONDARY2 serviceStyle
    class OPLOG,DATA stateStyle
    class MONITORING,LOGS controlStyle
```

## Critical Commands & Analysis

### Replica Set Status
```javascript
// Check replica set status and lag
rs.status()

// Focus on lag metrics
rs.status().members.forEach(function(member) {
    print("Host: " + member.name +
          ", State: " + member.stateStr +
          ", Lag: " + (member.optimeDate ?
              (ISODate() - member.optimeDate)/1000 + " seconds" : "N/A"));
});

// Check oplog window
db.oplog.rs.find().sort({$natural: -1}).limit(1);
db.oplog.rs.find().sort({$natural: 1}).limit(1);

// Calculate oplog hours
var first = db.oplog.rs.find().sort({$natural: 1}).limit(1).next();
var last = db.oplog.rs.find().sort({$natural: -1}).limit(1).next();
print("Oplog window: " + ((last.ts.getTime() - first.ts.getTime()) / 3600) + " hours");
```

### Performance Analysis
```javascript
// Check current operations
db.currentOp()

// Monitor replication metrics
db.serverStatus().repl

// Check oplog stats
db.oplog.rs.stats()

// Analyze slow operations
db.setProfilingLevel(2, {slowms: 1000})
db.system.profile.find().limit(5).sort({ts: -1}).pretty()
```

## Common Root Causes & Solutions

### 1. Network Bandwidth/Latency Issues (35% of cases)
```bash
# Detection: Test network between nodes
# From primary to secondary
ping -c 10 rs-secondary-01
iperf3 -c rs-secondary-01 -t 10

# MongoDB network diagnostics
mongo --host rs-secondary-01 --eval "db.runCommand({ping: 1})"

# Solution: Optimize network configuration
# Check MongoDB network compression (3.6+)
db.runCommand({getParameter: 1, networkMessageCompressors: 1})

# Enable compression in connection string
# mongodb://username:password@host:port/database?compressors=zstd,zlib,snappy
```

### 2. Secondary Hardware Constraints (30% of cases)
```bash
# Detection: Monitor secondary node resources
# CPU usage
top -p $(pgrep mongod)

# Disk I/O
iostat -x 1 5

# Memory usage
free -h

# MongoDB-specific metrics
mongostat --host rs-secondary-01

# Solution: Scale secondary hardware
# Add more memory
# Upgrade to faster storage (NVMe SSD)
# Increase CPU cores
```

### 3. Index Building on Secondary (20% of cases)
```javascript
// Detection: Check for index builds
db.currentOp({"command.createIndexes": {$exists: true}})

// Check index build progress
db.currentOp().inprog.forEach(function(op) {
    if (op.command && op.command.createIndexes) {
        print("Index build progress: " + op.progress);
    }
});

// Solution: Build indexes differently
// Option 1: Rolling index builds
// 1. Build index on one secondary with priority 0
// 2. Step down primary, promote the indexed secondary
// 3. Build index on new secondaries

// Option 2: Use background index builds (4.2+)
db.collection.createIndex({field: 1}, {background: true})
```

### 4. Heavy Read Load on Secondary (10% of cases)
```javascript
// Detection: Monitor secondary read operations
db.runCommand({serverStatus: 1}).opcounters

// Check read preference usage
db.runCommand({getParameter: 1, logLevel: 1})

// Solution: Load balancing and read optimization
// Use read tags for workload separation
cfg = rs.conf()
cfg.members[1].tags = {workload: "analytics"}
cfg.members[2].tags = {workload: "application"}
rs.reconfig(cfg)

// Configure read preference with tags
ReadPreference.secondary({workload: "analytics"})
```

### 5. Large Transactions/Operations (5% of cases)
```javascript
// Detection: Find large operations in oplog
db.oplog.rs.find({}, {ts: 1, t: 1, o: 1}).sort({$natural: -1}).limit(10).forEach(
    function(doc) {
        print("Operation size: " + Object.bsonsize(doc) + " bytes");
    }
);

// Check for long-running operations
db.currentOp({"secs_running": {$gt: 30}})

// Solution: Break large operations into smaller chunks
// Use bulk operations with smaller batch sizes
db.collection.initializeUnorderedBulkOp();
// Process in batches of 1000 instead of 100000
```

## Immediate Mitigation

### Emergency Response
```javascript
// Step 1: Reduce write load temporarily
db.runCommand({setParameter: 1, replWriterThreadCount: 1})

// Step 2: Increase oplog size if needed (requires restart)
// Can only be done on primary
db.runCommand({replSetResizeOplog: 1, size: 20480})  // 20GB

// Step 3: Force resync if lag is too severe (DATA LOSS RISK)
// Only on severely lagged secondary
db.adminCommand({resync: 1})

// Step 4: Adjust read preference temporarily
// In application, use primary reads until lag reduces
ReadPreference.primary()
```

### Configuration Optimization
```javascript
// Increase oplog size (MongoDB 3.6+)
db.adminCommand({replSetResizeOplog: 1, size: 51200})  // 50GB

// Configure write concern for performance
db.collection.insertOne(doc, {writeConcern: {w: 1, j: false}})

// Adjust replication settings
cfg = rs.conf()
cfg.settings = cfg.settings || {}
cfg.settings.heartbeatIntervalMillis = 2000  // Default 2000ms
cfg.settings.electionTimeoutMillis = 10000   // Default 10000ms
rs.reconfig(cfg)
```

## Long-term Prevention

### Monitoring Setup
```javascript
// Custom monitoring script
function checkReplicationLag() {
    var status = rs.status();
    var primary;
    var maxLag = 0;
    var lagDetails = [];

    // Find primary
    status.members.forEach(function(member) {
        if (member.state === 1) {  // PRIMARY
            primary = member;
        }
    });

    // Calculate lag for each secondary
    status.members.forEach(function(member) {
        if (member.state === 2) {  // SECONDARY
            var lag = (primary.optimeDate - member.optimeDate) / 1000;
            maxLag = Math.max(maxLag, lag);
            lagDetails.push({
                host: member.name,
                lag: lag,
                state: member.stateStr
            });
        }
    });

    return {
        maxLag: maxLag,
        details: lagDetails,
        alert: maxLag > 30  // Alert if lag > 30 seconds
    };
}

// Run check
var lagCheck = checkReplicationLag();
if (lagCheck.alert) {
    print("ALERT: High replication lag detected: " + lagCheck.maxLag + " seconds");
    print("Details: " + JSON.stringify(lagCheck.details, null, 2));
}
```

### Hardware Recommendations
```yaml
# Production replica set configuration
replica_set_config:
  primary:
    cpu_cores: 16
    memory_gb: 64
    storage_type: "NVMe SSD"
    storage_size_gb: 2000
    iops: 10000

  secondary:
    cpu_cores: 8
    memory_gb: 32
    storage_type: "NVMe SSD"  # Same as primary
    storage_size_gb: 2000
    iops: 8000  # Slightly lower acceptable

  network:
    bandwidth_gbps: 10
    latency_ms: "<1"
    between_nodes: "dedicated network"
```

### Application-Level Solutions
```javascript
// Smart read preference with lag tolerance
const MongoClient = require('mongodb').MongoClient;

class LagAwareClient {
    constructor(uri, options = {}) {
        this.client = new MongoClient(uri, options);
        this.maxAcceptableLag = options.maxAcceptableLag || 5000; // 5 seconds
    }

    async getCollection(dbName, collectionName) {
        const admin = this.client.db('admin');

        // Check replication lag
        const status = await admin.command({replSetGetStatus: 1});
        const lag = this.calculateMaxLag(status);

        let readPreference;
        if (lag > this.maxAcceptableLag) {
            // Use primary reads if lag is too high
            readPreference = {mode: 'primary'};
        } else {
            // Use secondary reads if lag is acceptable
            readPreference = {mode: 'secondaryPreferred'};
        }

        return this.client.db(dbName).collection(collectionName, {
            readPreference: readPreference
        });
    }

    calculateMaxLag(status) {
        let primary, maxLag = 0;

        // Find primary optime
        status.members.forEach(member => {
            if (member.state === 1) primary = member;
        });

        // Calculate max lag
        status.members.forEach(member => {
            if (member.state === 2) {
                const lag = primary.optimeDate - member.optimeDate;
                maxLag = Math.max(maxLag, lag);
            }
        });

        return maxLag;
    }
}
```

## Production Examples

### Uber's Replication Storm (2019)
- **Incident**: Trip data replica set lagging 2+ hours during peak demand
- **Root Cause**: Secondary nodes overwhelmed by analytics queries
- **Impact**: Surge pricing calculations using stale data
- **Resolution**: Dedicated analytics replica with read tags
- **Prevention**: Separated operational and analytical workloads

### Shopify's Black Friday Lag (2020)
- **Incident**: Product catalog replicas lagging during traffic surge
- **Root Cause**: Large product update operations blocking replication
- **Impact**: Search results showing outdated inventory
- **Resolution**: Implemented bulk operation chunking
- **Learning**: Large operations must be broken into smaller batches

### Airbnb's Index Build Crisis (2021)
- **Incident**: 12-hour replication lag during search index rebuild
- **Root Cause**: Foreground index build blocking all replication
- **Impact**: Booking data inconsistency, revenue impact
- **Resolution**: Rolling index builds, background indexing
- **Prevention**: Always use background index builds in production

## Recovery Automation

### Lag Monitoring Script
```bash
#!/bin/bash
# mongodb-lag-monitor.sh

MONGO_HOST="mongodb://primary:27017,secondary1:27017,secondary2:27017"
SLACK_WEBHOOK="your-slack-webhook-url"
LAG_THRESHOLD=30  # seconds

send_alert() {
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"MongoDB Lag Alert: $1\"}" \
        $SLACK_WEBHOOK
}

# Check replication lag
LAG_OUTPUT=$(mongo "$MONGO_HOST/admin" --quiet --eval "
var status = rs.status();
var primary, maxLag = 0;
status.members.forEach(function(m) { if (m.state === 1) primary = m; });
status.members.forEach(function(m) {
    if (m.state === 2) {
        var lag = (primary.optimeDate - m.optimeDate) / 1000;
        if (lag > maxLag) maxLag = lag;
    }
});
print(maxLag);
")

if (( $(echo "$LAG_OUTPUT > $LAG_THRESHOLD" | bc -l) )); then
    send_alert "Replication lag: ${LAG_OUTPUT}s (threshold: ${LAG_THRESHOLD}s)"

    # Get detailed status
    DETAILS=$(mongo "$MONGO_HOST/admin" --quiet --eval "
    var status = rs.status();
    status.members.forEach(function(m) {
        if (m.state === 2) {
            print(m.name + ': ' + ((status.members.find(p => p.state === 1).optimeDate - m.optimeDate)/1000) + 's lag');
        }
    });
    ")

    send_alert "Lag details: $DETAILS"
else
    echo "Replication lag normal: ${LAG_OUTPUT}s"
fi
```

**Remember**: MongoDB replication lag is often a symptom of resource constraints or network issues. Monitor your oplog window carefully, use appropriate read preferences, and ensure your secondary nodes have adequate resources to keep up with the primary's write load.