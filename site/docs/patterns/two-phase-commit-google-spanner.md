# Two-Phase Commit: Google Spanner Implementation

## Pattern Overview

Two-Phase Commit (2PC) ensures atomicity across distributed transactions by coordinating commit/abort decisions across multiple participants. Google Spanner implements a sophisticated 2PC protocol with TrueTime for globally consistent transactions across multiple datacenters, enabling ACID guarantees at global scale.

## Google Spanner 2PC Architecture

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane]
        ClientApp[Client Applications<br/>gRPC/HTTP APIs<br/>Global distribution<br/>p99: 10ms latency]
        Proxy[Spanner Proxy<br/>Regional endpoints<br/>Connection pooling<br/>Load balancing]
    end

    subgraph ServicePlane[Service Plane]
        SpannerFE[Spanner Frontend<br/>Request routing<br/>Transaction coordination<br/>SQL processing]

        TxnCoordinator[Transaction Coordinator<br/>2PC orchestration<br/>TrueTime integration<br/>Global consistency]

        ParticipantManager[Participant Manager<br/>Shard coordination<br/>Lock management<br/>Prepare/Commit handling]

        TrueTime[TrueTime Service<br/>GPS + Atomic clocks<br/>Global time ordering<br/>Uncertainty bounds]
    end

    subgraph StatePlane[State Plane - Multiple Regions]
        subgraph Region1[US-Central (Primary)]
            LeaderShard1[Leader Shard 1<br/>Paxos group<br/>SSD storage]
            FollowerShard1A[Follower 1A<br/>Replica]
            FollowerShard1B[Follower 1B<br/>Replica]
        end

        subgraph Region2[US-East (Secondary)]
            LeaderShard2[Leader Shard 2<br/>Paxos group<br/>SSD storage]
            FollowerShard2A[Follower 2A<br/>Replica]
            FollowerShard2B[Follower 2B<br/>Replica]
        end

        subgraph Region3[Europe-West (Tertiary)]
            LeaderShard3[Leader Shard 3<br/>Paxos group<br/>SSD storage]
            FollowerShard3A[Follower 3A<br/>Replica]
            FollowerShard3B[Follower 3B<br/>Replica]
        end

        LockTable[(Distributed Lock Table<br/>Two-phase locking<br/>Deadlock detection)]

        TransactionLog[(Global Transaction Log<br/>Paxos-replicated<br/>Commit timestamps)]
    end

    subgraph ControlPlane[Control Plane]
        TxnMonitor[Transaction Monitor<br/>2PC progress tracking<br/>Timeout management<br/>Recovery coordination]

        DeadlockDetector[Deadlock Detector<br/>Global cycle detection<br/>Transaction abortion<br/>Victim selection]

        TrueTimeOracle[TrueTime Oracle<br/>Time synchronization<br/>Uncertainty calculation<br/>Clock drift monitoring]

        Metrics[Spanner Metrics<br/>Transaction latency<br/>Abort rates<br/>2PC success rates]
    end

    %% Request Flow
    ClientApp --> Proxy
    Proxy --> SpannerFE
    SpannerFE --> TxnCoordinator

    %% 2PC Coordination
    TxnCoordinator --> ParticipantManager
    ParticipantManager --> LeaderShard1
    ParticipantManager --> LeaderShard2
    ParticipantManager --> LeaderShard3

    %% Paxos Replication within Shards
    LeaderShard1 --> FollowerShard1A
    LeaderShard1 --> FollowerShard1B
    LeaderShard2 --> FollowerShard2A
    LeaderShard2 --> FollowerShard2B
    LeaderShard3 --> FollowerShard3A
    LeaderShard3 --> FollowerShard3B

    %% Lock Management
    ParticipantManager --> LockTable
    TxnCoordinator --> TransactionLog

    %% TrueTime Integration
    TxnCoordinator --> TrueTime
    TrueTime --> TrueTimeOracle

    %% Monitoring
    TxnCoordinator --> TxnMonitor
    ParticipantManager --> DeadlockDetector
    TxnMonitor --> Metrics

    %% Styling
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class ClientApp,Proxy edgeStyle
    class SpannerFE,TxnCoordinator,ParticipantManager,TrueTime serviceStyle
    class LeaderShard1,FollowerShard1A,FollowerShard1B,LeaderShard2,FollowerShard2A,FollowerShard2B,LeaderShard3,FollowerShard3A,FollowerShard3B,LockTable,TransactionLog stateStyle
    class TxnMonitor,DeadlockDetector,TrueTimeOracle,Metrics controlStyle
```

## Spanner 2PC Transaction Flow

```mermaid
sequenceDiagram
    participant Client
    participant TxnCoordinator
    participant Shard1Leader
    participant Shard2Leader
    participant Shard3Leader
    participant TrueTime
    participant TransactionLog

    Note over Client,TransactionLog: Global Multi-Shard Transaction<br/>txn_id: txn_abc123<br/>Spans 3 regions

    Client->>TxnCoordinator: BEGIN TRANSACTION<br/>isolation: SERIALIZABLE
    TxnCoordinator->>TrueTime: Get current timestamp
    TrueTime-->>TxnCoordinator: timestamp: 1699123456789<br/>uncertainty: ±7ms

    %% Phase 1: Acquire Locks and Prepare
    Note over TxnCoordinator: Phase 1 - PREPARE

    TxnCoordinator->>Shard1Leader: UPDATE users SET balance = balance - 100<br/>WHERE user_id = 'user123'
    Shard1Leader->>Shard1Leader: Acquire write lock<br/>Validate constraints
    Shard1Leader-->>TxnCoordinator: LOCK_ACQUIRED<br/>prepare_timestamp: 1699123456795

    TxnCoordinator->>Shard2Leader: INSERT INTO transactions<br/>VALUES (txn_abc123, 'transfer', 100)
    Shard2Leader->>Shard2Leader: Acquire write lock<br/>Validate constraints
    Shard2Leader-->>TxnCoordinator: LOCK_ACQUIRED<br/>prepare_timestamp: 1699123456797

    TxnCoordinator->>Shard3Leader: UPDATE users SET balance = balance + 100<br/>WHERE user_id = 'user456'
    Shard3Leader->>Shard3Leader: Acquire write lock<br/>Validate constraints
    Shard3Leader-->>TxnCoordinator: LOCK_ACQUIRED<br/>prepare_timestamp: 1699123456799

    %% All participants prepared - choose commit timestamp
    TxnCoordinator->>TrueTime: Calculate commit timestamp
    Note over TrueTime: commit_ts = max(prepare_timestamps) + uncertainty<br/>commit_ts = 1699123456799 + 7 = 1699123456806

    TrueTime-->>TxnCoordinator: commit_timestamp: 1699123456806

    %% Phase 2: Commit Decision
    Note over TxnCoordinator: Phase 2 - COMMIT

    TxnCoordinator->>TransactionLog: Log COMMIT decision<br/>txn_id: txn_abc123<br/>commit_ts: 1699123456806
    TransactionLog-->>TxnCoordinator: Logged via Paxos consensus

    par Parallel Commit
        TxnCoordinator->>Shard1Leader: COMMIT<br/>commit_ts: 1699123456806
        Shard1Leader->>Shard1Leader: Apply changes<br/>Release locks
        Shard1Leader-->>TxnCoordinator: COMMITTED
    and
        TxnCoordinator->>Shard2Leader: COMMIT<br/>commit_ts: 1699123456806
        Shard2Leader->>Shard2Leader: Apply changes<br/>Release locks
        Shard2Leader-->>TxnCoordinator: COMMITTED
    and
        TxnCoordinator->>Shard3Leader: COMMIT<br/>commit_ts: 1699123456806
        Shard3Leader->>Shard3Leader: Apply changes<br/>Release locks
        Shard3Leader-->>TxnCoordinator: COMMITTED
    end

    TxnCoordinator-->>Client: TRANSACTION COMMITTED<br/>commit_timestamp: 1699123456806<br/>duration: 17ms
```

## TrueTime Integration for Global Consistency

### TrueTime Architecture

```mermaid
graph TB
    subgraph TrueTimeInfra[TrueTime Infrastructure]
        GPS[GPS Receivers<br/>Satellite time sync<br/>±100µs accuracy]
        AtomicClocks[Atomic Clocks<br/>Cesium/Rubidium<br/>±50µs accuracy]
        TimeServer[Time Servers<br/>Reference sources<br/>Multiple per datacenter]
    end

    subgraph SpannerNodes[Spanner Nodes]
        TrueTimeAPI[TrueTime API<br/>tt.now()<br/>Uncertainty bounds]
        LocalClock[Local Machine Clock<br/>NTP synchronized<br/>Uncertainty tracking]
        UncertaintyCalc[Uncertainty Calculator<br/>Clock drift estimation<br/>Network delay compensation]
    end

    subgraph TransactionLogic[Transaction Logic]
        CommitTSSelect[Commit Timestamp Selection<br/>External consistency<br/>Causality preservation]
        WaitForSafety[Commit Wait<br/>uncertainty.after(commit_ts)<br/>Before acknowledging]
    end

    GPS --> TimeServer
    AtomicClocks --> TimeServer
    TimeServer --> TrueTimeAPI
    TrueTimeAPI --> LocalClock
    LocalClock --> UncertaintyCalc
    UncertaintyCalc --> CommitTSSelect
    CommitTSSelect --> WaitForSafety

    classDef trueTimeStyle fill:#E11D48,stroke:#BE185D,color:#fff
    classDef spannerStyle fill:#10B981,stroke:#059669,color:#fff
    classDef txnStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class GPS,AtomicClocks,TimeServer trueTimeStyle
    class TrueTimeAPI,LocalClock,UncertaintyCalc spannerStyle
    class CommitTSSelect,WaitForSafety txnStyle
```

## 2PC Implementation Details

### Transaction Coordinator

```java
@Component
public class SpannerTransactionCoordinator {

    @Autowired
    private TrueTimeService trueTimeService;

    @Autowired
    private ParticipantManager participantManager;

    @Autowired
    private TransactionLogService transactionLog;

    @Autowired
    private LockManager lockManager;

    public TransactionResult executeTransaction(TransactionRequest request) {
        String transactionId = generateTransactionId();
        TrueTimeTimestamp startTime = trueTimeService.now();

        try {
            // Phase 1: Prepare all participants
            PrepareResult prepareResult = executePhaseOne(transactionId, request);

            if (!prepareResult.isAllPrepared()) {
                // Abort transaction if any participant failed to prepare
                abortTransaction(transactionId, prepareResult.getPreparedParticipants());
                return TransactionResult.aborted(transactionId, prepareResult.getFailureReason());
            }

            // Calculate commit timestamp using TrueTime
            TrueTimeTimestamp commitTimestamp = calculateCommitTimestamp(
                prepareResult.getMaxPrepareTimestamp(),
                trueTimeService.now()
            );

            // Phase 2: Commit all participants
            CommitResult commitResult = executePhaseTwo(
                transactionId,
                commitTimestamp,
                prepareResult.getParticipants()
            );

            if (commitResult.isSuccessful()) {
                return TransactionResult.committed(transactionId, commitTimestamp);
            } else {
                // This should be extremely rare in Spanner due to Paxos guarantees
                throw new TransactionCommitException(
                    "Phase 2 commit failed after successful prepare: " + transactionId);
            }

        } catch (Exception e) {
            // Clean up any resources and abort
            abortTransaction(transactionId, Collections.emptyList());
            throw new TransactionExecutionException("Transaction failed: " + transactionId, e);
        }
    }

    private PrepareResult executePhaseOne(String transactionId, TransactionRequest request) {
        List<TransactionParticipant> participants = identifyParticipants(request);
        List<PrepareResponse> prepareResponses = new ArrayList<>();
        TrueTimeTimestamp maxPrepareTimestamp = TrueTimeTimestamp.earliest();

        for (TransactionParticipant participant : participants) {
            try {
                PrepareResponse response = participantManager.prepare(
                    participant,
                    transactionId,
                    request.getOperationsForParticipant(participant)
                );

                if (response.isPrepared()) {
                    prepareResponses.add(response);
                    maxPrepareTimestamp = TrueTimeTimestamp.max(
                        maxPrepareTimestamp,
                        response.getPrepareTimestamp()
                    );
                } else {
                    // Abort if any participant cannot prepare
                    return PrepareResult.failed(
                        transactionId,
                        participant,
                        response.getFailureReason(),
                        prepareResponses
                    );
                }

            } catch (Exception e) {
                return PrepareResult.failed(
                    transactionId,
                    participant,
                    "Prepare communication failed: " + e.getMessage(),
                    prepareResponses
                );
            }
        }

        return PrepareResult.successful(transactionId, participants, maxPrepareTimestamp);
    }

    private CommitResult executePhaseTwo(String transactionId,
                                        TrueTimeTimestamp commitTimestamp,
                                        List<TransactionParticipant> participants) {
        // First, log the commit decision in the transaction log
        transactionLog.logCommitDecision(transactionId, commitTimestamp);

        // Wait for TrueTime uncertainty to pass
        trueTimeService.waitUntilAfter(commitTimestamp);

        // Commit all participants in parallel
        List<CompletableFuture<Boolean>> commitFutures = participants.stream()
            .map(participant -> CompletableFuture.supplyAsync(() ->
                participantManager.commit(participant, transactionId, commitTimestamp)))
            .collect(Collectors.toList());

        // Wait for all commits to complete
        try {
            List<Boolean> commitResults = commitFutures.stream()
                .map(CompletableFuture::join)
                .collect(Collectors.toList());

            boolean allCommitted = commitResults.stream().allMatch(Boolean::booleanValue);

            return CommitResult.builder()
                .transactionId(transactionId)
                .commitTimestamp(commitTimestamp)
                .successful(allCommitted)
                .build();

        } catch (Exception e) {
            log.error("Phase 2 commit failed for transaction: {}", transactionId, e);
            return CommitResult.failed(transactionId, e.getMessage());
        }
    }

    private TrueTimeTimestamp calculateCommitTimestamp(TrueTimeTimestamp maxPrepareTimestamp,
                                                      TrueTimeTimestamp currentTime) {
        // Commit timestamp must be:
        // 1. After all prepare timestamps (causality)
        // 2. After TrueTime uncertainty bound (external consistency)
        TrueTimeTimestamp minCommitTime = TrueTimeTimestamp.max(
            maxPrepareTimestamp,
            currentTime.latest() // current time + uncertainty
        );

        return minCommitTime;
    }
}
```

### Participant Shard Implementation

```java
@Component
public class SpannerShardParticipant {

    @Autowired
    private PaxosConsensus paxosConsensus;

    @Autowired
    private LockManager lockManager;

    @Autowired
    private StorageEngine storageEngine;

    @Autowired
    private TrueTimeService trueTimeService;

    public PrepareResponse prepare(String transactionId,
                                  List<TransactionOperation> operations) {
        try {
            // Acquire all necessary locks
            List<Lock> acquiredLocks = new ArrayList<>();

            for (TransactionOperation operation : operations) {
                Lock lock = lockManager.acquireLock(
                    operation.getKey(),
                    operation.getLockType(),
                    transactionId
                );

                if (lock == null) {
                    // Lock acquisition failed - release any acquired locks
                    releaseLocks(acquiredLocks);
                    return PrepareResponse.failed(
                        transactionId,
                        "Failed to acquire lock for key: " + operation.getKey()
                    );
                }

                acquiredLocks.add(lock);
            }

            // Validate all operations can be performed
            for (TransactionOperation operation : operations) {
                ValidationResult validation = validateOperation(operation);
                if (!validation.isValid()) {
                    releaseLocks(acquiredLocks);
                    return PrepareResponse.failed(
                        transactionId,
                        "Operation validation failed: " + validation.getErrorMessage()
                    );
                }
            }

            // Prepare the changes but don't commit yet
            PreparedTransaction preparedTxn = PreparedTransaction.builder()
                .transactionId(transactionId)
                .operations(operations)
                .acquiredLocks(acquiredLocks)
                .prepareTimestamp(trueTimeService.now())
                .build();

            // Store prepared state in Paxos-replicated log
            paxosConsensus.propose(PrepareLogEntry.builder()
                .transactionId(transactionId)
                .preparedTransaction(preparedTxn)
                .build());

            return PrepareResponse.successful(
                transactionId,
                preparedTxn.getPrepareTimestamp()
            );

        } catch (Exception e) {
            log.error("Prepare failed for transaction: {}", transactionId, e);
            return PrepareResponse.failed(transactionId, "Prepare error: " + e.getMessage());
        }
    }

    public boolean commit(String transactionId, TrueTimeTimestamp commitTimestamp) {
        try {
            // Retrieve prepared transaction state
            PreparedTransaction preparedTxn = getPreparedTransaction(transactionId);

            if (preparedTxn == null) {
                log.error("No prepared transaction found for commit: {}", transactionId);
                return false;
            }

            // Apply all operations atomically
            List<StorageOperation> storageOps = preparedTxn.getOperations().stream()
                .map(this::convertToStorageOperation)
                .collect(Collectors.toList());

            // Apply changes with commit timestamp
            storageEngine.applyOperations(storageOps, commitTimestamp);

            // Release all locks
            releaseLocks(preparedTxn.getAcquiredLocks());

            // Log commit completion via Paxos
            paxosConsensus.propose(CommitLogEntry.builder()
                .transactionId(transactionId)
                .commitTimestamp(commitTimestamp)
                .build());

            return true;

        } catch (Exception e) {
            log.error("Commit failed for transaction: {}", transactionId, e);
            return false;
        }
    }

    public void abort(String transactionId) {
        try {
            PreparedTransaction preparedTxn = getPreparedTransaction(transactionId);

            if (preparedTxn != null) {
                // Release all acquired locks
                releaseLocks(preparedTxn.getAcquiredLocks());

                // Log abort via Paxos
                paxosConsensus.propose(AbortLogEntry.builder()
                    .transactionId(transactionId)
                    .abortTimestamp(trueTimeService.now())
                    .build());
            }

        } catch (Exception e) {
            log.error("Abort failed for transaction: {}", transactionId, e);
        }
    }
}
```

## Real Production Metrics

### Google Spanner 2PC Scale (2023)

- **Global Deployment**: 100+ datacenters across 6 continents
- **Daily Transactions**: 10+ billion 2PC transactions
- **Cross-Shard Transactions**: 40% of all transactions
- **Global Commit Latency**: p99 < 100ms for cross-region
- **Availability**: 99.999% (5 nines) SLA

### Performance Characteristics

```mermaid
xychart-beta
    title "Spanner 2PC Performance by Region Span"
    x-axis ["Single Region", "Cross Region (Same Continent)", "Cross Continent", "Global (3+ Continents)"]
    y-axis "Latency (ms)" 0 --> 200
    bar "p50 Latency" [8, 25, 65, 120]
    bar "p99 Latency" [15, 45, 95, 180]
```

### Transaction Success Rates

```mermaid
pie title "Transaction Outcomes (Daily)"
    "Committed Successfully" : 95.2
    "Aborted (Conflicts)" : 3.8
    "Aborted (Timeouts)" : 0.8
    "Failed (System Error)" : 0.2
```

## Advanced 2PC Optimizations

### Parallel Prepare Optimization

```java
@Component
public class OptimizedTransactionCoordinator {

    @Autowired
    private ParticipantManager participantManager;

    private static final Duration PREPARE_TIMEOUT = Duration.ofSeconds(10);

    public PrepareResult executePhaseOneOptimized(String transactionId,
                                                 TransactionRequest request) {
        List<TransactionParticipant> participants = identifyParticipants(request);

        // Execute prepare operations in parallel
        Map<TransactionParticipant, CompletableFuture<PrepareResponse>> prepareFutures =
            participants.stream().collect(Collectors.toMap(
                participant -> participant,
                participant -> CompletableFuture.supplyAsync(() ->
                    participantManager.prepare(
                        participant,
                        transactionId,
                        request.getOperationsForParticipant(participant)
                    ))
            ));

        // Wait for all prepares with timeout
        Map<TransactionParticipant, PrepareResponse> prepareResults = new HashMap<>();
        TrueTimeTimestamp maxPrepareTimestamp = TrueTimeTimestamp.earliest();
        boolean allPrepared = true;
        String failureReason = null;

        for (Map.Entry<TransactionParticipant, CompletableFuture<PrepareResponse>> entry :
             prepareFutures.entrySet()) {

            try {
                PrepareResponse response = entry.getValue().get(
                    PREPARE_TIMEOUT.toMillis(),
                    TimeUnit.MILLISECONDS
                );

                prepareResults.put(entry.getKey(), response);

                if (response.isPrepared()) {
                    maxPrepareTimestamp = TrueTimeTimestamp.max(
                        maxPrepareTimestamp,
                        response.getPrepareTimestamp()
                    );
                } else {
                    allPrepared = false;
                    failureReason = response.getFailureReason();
                    break; // Early exit on first failure
                }

            } catch (TimeoutException e) {
                allPrepared = false;
                failureReason = "Prepare timeout for participant: " + entry.getKey().getId();
                break;
            } catch (Exception e) {
                allPrepared = false;
                failureReason = "Prepare error for participant: " + entry.getKey().getId();
                break;
            }
        }

        if (allPrepared) {
            return PrepareResult.successful(transactionId, participants, maxPrepareTimestamp);
        } else {
            // Abort all successfully prepared participants
            abortPreparedParticipants(transactionId, prepareResults);
            return PrepareResult.failed(transactionId, null, failureReason, prepareResults.values());
        }
    }
}
```

### Deadlock Detection and Resolution

```java
@Component
public class GlobalDeadlockDetector {

    @Autowired
    private LockManager lockManager;

    @Autowired
    private TransactionManager transactionManager;

    private final Map<String, TransactionWaitGraph> waitGraphs = new ConcurrentHashMap<>();

    @Scheduled(fixedDelay = 1000) // Check every second
    public void detectDeadlocks() {
        // Build global wait-for graph
        TransactionWaitGraph globalWaitGraph = buildGlobalWaitGraph();

        // Detect cycles in the wait graph
        List<DeadlockCycle> cycles = detectCycles(globalWaitGraph);

        if (!cycles.isEmpty()) {
            log.warn("Detected {} deadlock cycles", cycles.size());

            // Resolve deadlocks by aborting victim transactions
            for (DeadlockCycle cycle : cycles) {
                resolveDeadlock(cycle);
            }
        }
    }

    private TransactionWaitGraph buildGlobalWaitGraph() {
        TransactionWaitGraph graph = new TransactionWaitGraph();

        // Collect wait information from all participants
        List<LockWaitInfo> allWaits = lockManager.getAllLockWaits();

        for (LockWaitInfo waitInfo : allWaits) {
            graph.addEdge(
                waitInfo.getWaitingTransaction(),
                waitInfo.getHoldingTransaction(),
                waitInfo.getResource()
            );
        }

        return graph;
    }

    private void resolveDeadlock(DeadlockCycle cycle) {
        // Select victim transaction (e.g., youngest transaction)
        String victimTransaction = selectVictim(cycle.getTransactions());

        log.info("Aborting transaction {} to resolve deadlock involving transactions: {}",
            victimTransaction, cycle.getTransactions());

        // Abort the victim transaction
        transactionManager.abortTransaction(
            victimTransaction,
            "Aborted to resolve deadlock"
        );

        // Update metrics
        metricsCollector.incrementCounter("deadlock_resolutions");
        metricsCollector.recordGauge("deadlock_cycle_size", cycle.getTransactions().size());
    }

    private String selectVictim(List<String> transactions) {
        // Choose victim based on cost heuristics:
        // 1. Prefer younger transactions (less work done)
        // 2. Prefer transactions with fewer locks
        // 3. Prefer transactions that haven't been restarted recently

        return transactions.stream()
            .min(Comparator
                .comparing(this::getTransactionAge)
                .thenComparing(this::getTransactionLockCount)
                .thenComparing(this::getTransactionRestartCount))
            .orElse(transactions.get(0));
    }
}
```

## Monitoring and Observability

### 2PC Performance Metrics

```yaml
# Spanner 2PC monitoring configuration
spanner_2pc_metrics:
  transaction_latency:
    target_p99: 100ms
    alert_threshold: 150ms
    critical_threshold: 300ms

  prepare_success_rate:
    target: 98.5%
    alert_threshold: 97.0%
    critical_threshold: 95.0%

  commit_success_rate:
    target: 99.8%
    alert_threshold: 99.5%
    critical_threshold: 99.0%

  deadlock_rate:
    target: <0.5%
    alert_threshold: 1.0%
    critical_threshold: 2.0%

  truetime_uncertainty:
    target: <10ms
    alert_threshold: 15ms
    critical_threshold: 25ms
```

### Transaction Tracing

```java
@Component
public class SpannerTransactionTracer {

    @Autowired
    private DistributedTracing distributedTracing;

    public void traceTransaction(String transactionId, TransactionRequest request) {
        Span transactionSpan = distributedTracing.startSpan("spanner.transaction")
            .setTag("transaction.id", transactionId)
            .setTag("transaction.participants", request.getParticipants().size())
            .setTag("transaction.operations", request.getOperations().size());

        try {
            // Phase 1 tracing
            Span prepareSpan = distributedTracing.startSpan("spanner.prepare", transactionSpan)
                .setTag("phase", "prepare");

            for (TransactionParticipant participant : request.getParticipants()) {
                Span participantSpan = distributedTracing.startSpan(
                    "spanner.prepare.participant", prepareSpan)
                    .setTag("participant.id", participant.getId())
                    .setTag("participant.region", participant.getRegion());

                // ... prepare operations ...

                participantSpan.finish();
            }

            prepareSpan.finish();

            // Phase 2 tracing
            Span commitSpan = distributedTracing.startSpan("spanner.commit", transactionSpan)
                .setTag("phase", "commit");

            // ... commit operations ...

            commitSpan.finish();

        } finally {
            transactionSpan.finish();
        }
    }
}
```

## Cost and Performance Analysis

### Spanner 2PC Costs

| Component | Monthly Cost | Purpose |
|-----------|--------------|---------|
| Compute (Global) | $2.5M | Transaction coordinators and participants |
| Storage (Global) | $800K | Multi-region data replication |
| Network (Cross-region) | $1.2M | Inter-datacenter communication |
| TrueTime Infrastructure | $500K | GPS/atomic clock infrastructure |
| **Total** | **$5M** | **For 10B+ daily transactions** |

### Performance Trade-offs

| Consistency Level | Latency | Throughput | Use Case |
|------------------|---------|------------|----------|
| Single Region | 5-15ms | Very High | Local applications |
| Cross Region | 20-50ms | High | Regional applications |
| Cross Continent | 50-100ms | Medium | Global applications |
| Global Strong | 100-200ms | Lower | Critical consistency |

## Best Practices & Lessons Learned

### 2PC Design Principles

1. **Minimize Participants**: Fewer participants = lower latency and failure probability
2. **Optimize Prepare Phase**: Parallel execution reduces overall latency
3. **Handle Failures Gracefully**: Robust timeout and retry mechanisms
4. **Monitor Carefully**: Track success rates, latency, and deadlock rates
5. **Design for Recovery**: Handle coordinator failures and participant recovery

### Common Anti-Patterns

❌ **Long-Running Transactions**
```java
// Wrong: Holding locks for extended periods
@Transactional
public void longRunningTransaction() {
    // Complex business logic taking 30+ seconds
    // High deadlock probability, poor performance
}
```

✅ **Short, Focused Transactions**
```java
// Correct: Minimize transaction scope
@Transactional
public void atomicUpdate() {
    // Quick, focused operations
    // Release locks quickly
}
```

### Transaction Optimization Guidelines

| Transaction Type | Max Duration | Max Participants | Optimization Strategy |
|-----------------|--------------|------------------|----------------------|
| OLTP Transactions | 100ms | 3-5 | Minimize cross-region |
| Batch Updates | 1s | 10+ | Use bulk operations |
| Read-Only | No limit | Any | Use snapshot reads |
| Administrative | 10s | Few | Use separate coordinator |

## Conclusion

Google Spanner's 2PC implementation provides:

- **Global ACID transactions** across multiple continents
- **10+ billion daily transactions** with strong consistency
- **99.999% availability** despite complex coordination
- **100ms p99 latency** for cross-continent transactions
- **Revolutionary TrueTime integration** for external consistency

The implementation demonstrates how sophisticated distributed systems can achieve both strong consistency and high performance at global scale through careful engineering of consensus protocols, time synchronization, and failure recovery mechanisms.