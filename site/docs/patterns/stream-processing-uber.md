# Stream Processing: Uber's Apache Flink

## Overview

Uber processes 100 billion events daily through Apache Flink, powering real-time features like surge pricing, driver matching, and fraud detection. Their streaming platform handles 20 million rides per day with sub-second latency requirements for critical business operations.

## Production Architecture

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - #3B82F6]
        MOBILE[Mobile Apps<br/>Driver/Rider<br/>Location events]
        API[Uber API Gateway<br/>Kong<br/>Rate limiting]
        LB[Load Balancer<br/>F5/NGINX<br/>Geographic routing]
    end

    subgraph ServicePlane[Service Plane - #10B981]
        subgraph FlinkCluster[Flink Streaming Cluster]
            JM[JobManager<br/>HA with Zookeeper<br/>Job coordination]
            TM1[TaskManager 1<br/>r5.4xlarge<br/>16 cores, 64GB]
            TM2[TaskManager 2<br/>r5.4xlarge<br/>16 cores, 64GB]
            TMN[TaskManager N<br/>Auto-scaling<br/>200+ nodes peak]
        end

        subgraph StreamingJobs[Real-time Streaming Jobs]
            LOCATION[Location Tracking<br/>GPS coordinates<br/>Map matching]
            PRICING[Dynamic Pricing<br/>Surge calculation<br/>Supply/demand]
            MATCHING[Driver Matching<br/>ETA optimization<br/>Route planning]
            FRAUD[Fraud Detection<br/>ML models<br/>Risk scoring]
        end
    end

    subgraph StatePlane[State Plane - #F59E0B]
        subgraph MessageBrokers[Message Brokers]
            KAFKA[Kafka Cluster<br/>50+ brokers<br/>10K partitions<br/>Retention: 7 days]
            PULSAR[Apache Pulsar<br/>Geo-replication<br/>Multi-tenancy]
        end

        subgraph StateStores[State Management]
            ROCKSDB[RocksDB<br/>Local state<br/>Checkpointing]
            HDFS[HDFS<br/>Checkpoint storage<br/>State recovery]
        end

        subgraph DataStores[Data Storage]
            CASSANDRA[(Cassandra<br/>Driver states<br/>Multi-region)]
            REDIS[(Redis Cluster<br/>Real-time cache<br/>Sub-ms latency)]
            MYSQL[(MySQL<br/>Trip metadata<br/>ACID compliance)]
        end
    end

    subgraph ControlPlane[Control Plane - #8B5CF6]
        PROMETHEUS[Prometheus<br/>Metrics collection<br/>Stream monitoring]
        GRAFANA[Grafana<br/>Real-time dashboards<br/>SLA tracking]
        FLINK_UI[Flink WebUI<br/>Job monitoring<br/>Backpressure analysis]
        ALERTS[AlertManager<br/>PagerDuty<br/>Escalation policies]
    end

    %% Data flow
    MOBILE --> API
    API --> LB
    LB --> KAFKA
    KAFKA --> JM
    JM --> TM1
    JM --> TM2
    JM --> TMN

    %% Stream processing
    TM1 --> LOCATION
    TM1 --> PRICING
    TM2 --> MATCHING
    TM2 --> FRAUD

    %% State management
    LOCATION --> ROCKSDB
    PRICING --> ROCKSDB
    MATCHING --> ROCKSDB
    FRAUD --> ROCKSDB
    ROCKSDB --> HDFS

    %% Output sinks
    LOCATION --> CASSANDRA
    PRICING --> REDIS
    MATCHING --> MYSQL
    FRAUD --> KAFKA

    %% Control connections
    JM --> PROMETHEUS
    TM1 --> PROMETHEUS
    TM2 --> PROMETHEUS
    PROMETHEUS --> GRAFANA
    PROMETHEUS --> ALERTS
    JM --> FLINK_UI

    %% Apply four-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#1E40AF,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#047857,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#6D28D9,color:#fff

    class MOBILE,API,LB edgeStyle
    class JM,TM1,TM2,TMN,LOCATION,PRICING,MATCHING,FRAUD serviceStyle
    class KAFKA,PULSAR,ROCKSDB,HDFS,CASSANDRA,REDIS,MYSQL stateStyle
    class PROMETHEUS,GRAFANA,FLINK_UI,ALERTS controlStyle
```

## Real-time Driver Matching Pipeline

```mermaid
graph TB
    subgraph DriverMatching[Real-time Driver Matching Stream]
        subgraph InputStreams[Input Event Streams]
            RIDE_REQUEST[Ride Request Stream<br/>Passenger location<br/>Destination<br/>Ride type]
            DRIVER_LOCATION[Driver Location Stream<br/>GPS coordinates<br/>5-second intervals<br/>Driver status]
            TRAFFIC_DATA[Traffic Data Stream<br/>Real-time conditions<br/>Route optimization<br/>ETA calculation]
        end

        subgraph StreamProcessing[Stream Processing Logic]
            GEOHASH[Geo-hashing<br/>Spatial indexing<br/>Nearby drivers<br/>500m radius]
            ETA_CALC[ETA Calculation<br/>Machine learning<br/>Historical patterns<br/>Real-time traffic]
            SUPPLY_DEMAND[Supply/Demand<br/>Dynamic pricing<br/>Surge multiplier<br/>Region-based]
            MATCHING_ALGO[Matching Algorithm<br/>Bipartite matching<br/>Cost optimization<br/>Fairness constraints]
        end

        subgraph StateManagement[Stateful Operations]
            DRIVER_STATE[Driver State<br/>Available/Busy<br/>Session tracking<br/>Performance metrics]
            REQUEST_STATE[Request State<br/>Pending matches<br/>Timeout handling<br/>Retry logic]
            REGION_STATE[Region State<br/>Supply metrics<br/>Demand patterns<br/>Surge levels]
        end

        subgraph OutputSinks[Output Streams]
            MATCH_RESULT[Match Results<br/>Driver-rider pairs<br/>ETA predictions<br/>Pricing info]
            PRICING_UPDATE[Pricing Updates<br/>Surge notifications<br/>Driver incentives<br/>Regional adjustments]
            ANALYTICS[Analytics Events<br/>Performance metrics<br/>Conversion rates<br/>Wait times]
        end
    end

    RIDE_REQUEST --> GEOHASH
    DRIVER_LOCATION --> GEOHASH
    TRAFFIC_DATA --> ETA_CALC

    GEOHASH --> MATCHING_ALGO
    ETA_CALC --> MATCHING_ALGO
    SUPPLY_DEMAND --> MATCHING_ALGO

    MATCHING_ALGO --> DRIVER_STATE
    MATCHING_ALGO --> REQUEST_STATE
    MATCHING_ALGO --> REGION_STATE

    DRIVER_STATE --> MATCH_RESULT
    REQUEST_STATE --> PRICING_UPDATE
    REGION_STATE --> ANALYTICS

    classDef inputStyle fill:#3B82F6,stroke:#1E40AF,color:#fff
    classDef processStyle fill:#10B981,stroke:#047857,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef outputStyle fill:#8B5CF6,stroke:#6D28D9,color:#fff

    class RIDE_REQUEST,DRIVER_LOCATION,TRAFFIC_DATA inputStyle
    class GEOHASH,ETA_CALC,SUPPLY_DEMAND,MATCHING_ALGO processStyle
    class DRIVER_STATE,REQUEST_STATE,REGION_STATE stateStyle
    class MATCH_RESULT,PRICING_UPDATE,ANALYTICS outputStyle
```

## Windowing and Aggregation Patterns

```mermaid
graph TB
    subgraph WindowingPatterns[Flink Windowing Patterns]
        subgraph TumblingWindows[Tumbling Windows]
            TUMBLE_1MIN[1-minute Windows<br/>Driver availability<br/>Real-time metrics<br/>No overlap]
            TUMBLE_5MIN[5-minute Windows<br/>Regional demand<br/>Surge calculation<br/>Business metrics]
            TUMBLE_1HOUR[1-hour Windows<br/>Performance reports<br/>Driver incentives<br/>Analytics]
        end

        subgraph SlidingWindows[Sliding Windows]
            SLIDE_30SEC[30-second Slide<br/>ETA predictions<br/>Traffic monitoring<br/>Real-time updates]
            SLIDE_2MIN[2-minute Slide<br/>Fraud detection<br/>Pattern analysis<br/>Anomaly detection]
            SLIDE_15MIN[15-minute Slide<br/>Price optimization<br/>Market analysis<br/>Demand forecasting]
        end

        subgraph SessionWindows[Session Windows]
            DRIVER_SESSION[Driver Sessions<br/>Login to logout<br/>Performance tracking<br/>Earnings calculation]
            RIDER_SESSION[Rider Sessions<br/>App interactions<br/>Conversion funnel<br/>User experience]
            TRIP_SESSION[Trip Sessions<br/>Request to completion<br/>End-to-end metrics<br/>Service quality]
        end

        subgraph ProcessingTime[Processing Time Windows]
            REAL_TIME[Real-time Processing<br/>Low latency<br/>Approximate results<br/>System clock based]
            EVENT_TIME[Event Time Processing<br/>Accurate results<br/>Handle late events<br/>Watermarks]
            INGESTION_TIME[Ingestion Time<br/>Balanced approach<br/>Kafka timestamp<br/>Reasonable latency]
        end
    end

    TUMBLE_1MIN --> SLIDE_30SEC
    TUMBLE_5MIN --> SLIDE_2MIN
    TUMBLE_1HOUR --> SLIDE_15MIN

    SLIDE_30SEC --> DRIVER_SESSION
    SLIDE_2MIN --> RIDER_SESSION
    SLIDE_15MIN --> TRIP_SESSION

    DRIVER_SESSION --> REAL_TIME
    RIDER_SESSION --> EVENT_TIME
    TRIP_SESSION --> INGESTION_TIME

    classDef tumblingStyle fill:#10B981,stroke:#047857,color:#fff
    classDef slidingStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef sessionStyle fill:#8B5CF6,stroke:#6D28D9,color:#fff
    classDef timeStyle fill:#DC2626,stroke:#B91C1C,color:#fff

    class TUMBLE_1MIN,TUMBLE_5MIN,TUMBLE_1HOUR tumblingStyle
    class SLIDE_30SEC,SLIDE_2MIN,SLIDE_15MIN slidingStyle
    class DRIVER_SESSION,RIDER_SESSION,TRIP_SESSION sessionStyle
    class REAL_TIME,EVENT_TIME,INGESTION_TIME timeStyle
```

## Fault Tolerance and Recovery

```mermaid
graph TB
    subgraph FaultTolerance[Flink Fault Tolerance]
        subgraph Checkpointing[Checkpointing Strategy]
            CHECKPOINT_TRIGGER[Checkpoint Trigger<br/>Every 30 seconds<br/>Barrier alignment<br/>Distributed snapshots]
            STATE_SNAPSHOT[State Snapshot<br/>RocksDB backup<br/>Incremental saves<br/>Compressed storage]
            METADATA_STORAGE[Metadata Storage<br/>HDFS/S3 storage<br/>Checkpoint coordination<br/>Recovery metadata]
        end

        subgraph FailureRecovery[Failure Recovery]
            FAILURE_DETECTION[Failure Detection<br/>Heartbeat timeout<br/>Task failure<br/>JVM crashes]
            JOB_RESTART[Job Restart<br/>From last checkpoint<br/>State restoration<br/>Operator recovery]
            REPROCESSING[Event Reprocessing<br/>Kafka offset reset<br/>Duplicate handling<br/>Idempotent operations]
        end

        subgraph BackpressureHandling[Backpressure Management]
            BUFFER_MONITORING[Buffer Monitoring<br/>Network buffers<br/>Queue lengths<br/>Processing rates]
            RATE_LIMITING[Rate Limiting<br/>Input throttling<br/>Congestion control<br/>Load shedding]
            SCALING[Auto-scaling<br/>Task parallelism<br/>Resource allocation<br/>Elastic scaling]
        end

        subgraph MonitoringAlerts[Monitoring & Alerts]
            LAG_MONITORING[Lag Monitoring<br/>Processing delay<br/>Kafka lag<br/>SLA violations]
            ERROR_TRACKING[Error Tracking<br/>Exception rates<br/>Dead letter queues<br/>Circuit breakers]
            PERFORMANCE_METRICS[Performance Metrics<br/>Throughput<br/>Latency percentiles<br/>Resource utilization]
        end
    end

    CHECKPOINT_TRIGGER --> STATE_SNAPSHOT
    STATE_SNAPSHOT --> METADATA_STORAGE

    FAILURE_DETECTION --> JOB_RESTART
    JOB_RESTART --> REPROCESSING
    METADATA_STORAGE --> JOB_RESTART

    BUFFER_MONITORING --> RATE_LIMITING
    RATE_LIMITING --> SCALING

    LAG_MONITORING --> ERROR_TRACKING
    ERROR_TRACKING --> PERFORMANCE_METRICS
    PERFORMANCE_METRICS --> CHECKPOINT_TRIGGER

    classDef checkpointStyle fill:#10B981,stroke:#047857,color:#fff
    classDef recoveryStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef backpressureStyle fill:#8B5CF6,stroke:#6D28D9,color:#fff
    classDef monitorStyle fill:#DC2626,stroke:#B91C1C,color:#fff

    class CHECKPOINT_TRIGGER,STATE_SNAPSHOT,METADATA_STORAGE checkpointStyle
    class FAILURE_DETECTION,JOB_RESTART,REPROCESSING recoveryStyle
    class BUFFER_MONITORING,RATE_LIMITING,SCALING backpressureStyle
    class LAG_MONITORING,ERROR_TRACKING,PERFORMANCE_METRICS monitorStyle
```

## Production Metrics

### Streaming Performance
- **Events Processed**: 100 billion events/day
- **Peak Throughput**: 10 million events/second
- **End-to-end Latency**: p99 < 500ms, p50 < 100ms
- **Checkpoint Duration**: p99 < 10 seconds

### System Reliability
- **Job Uptime**: 99.95% availability
- **Recovery Time**: < 30 seconds from last checkpoint
- **Data Loss**: Zero tolerance (exactly-once processing)
- **Backpressure Events**: < 0.1% of processing time

### Resource Utilization
- **TaskManager Nodes**: 200+ nodes (auto-scaling)
- **CPU Utilization**: 70-85% average
- **Memory Usage**: 80% heap, 20% off-heap
- **Network I/O**: 40 Gbps peak throughput

## Implementation Details

### Flink Job Configuration
```java
public class UberDriverMatchingJob {

    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment
            .getExecutionEnvironment();

        // Configure checkpointing
        env.enableCheckpointing(30000); // 30 seconds
        env.getCheckpointConfig().setCheckpointingMode(
            CheckpointingMode.EXACTLY_ONCE);
        env.getCheckpointConfig().setMinPauseBetweenCheckpoints(5000);
        env.getCheckpointConfig().setCheckpointTimeout(60000);

        // Configure Kafka source
        Properties kafkaProps = new Properties();
        kafkaProps.setProperty("bootstrap.servers", "kafka-cluster:9092");
        kafkaProps.setProperty("group.id", "driver-matching");

        DataStream<RideRequest> rideRequests = env
            .addSource(new FlinkKafkaConsumer<>(
                "ride-requests",
                new RideRequestSchema(),
                kafkaProps))
            .assignTimestampsAndWatermarks(
                WatermarkStrategy.<RideRequest>forBoundedOutOfOrderness(
                    Duration.ofSeconds(5))
                .withTimestampAssigner((event, timestamp) ->
                    event.getTimestamp()));

        DataStream<DriverLocation> driverLocations = env
            .addSource(new FlinkKafkaConsumer<>(
                "driver-locations",
                new DriverLocationSchema(),
                kafkaProps))
            .assignTimestampsAndWatermarks(
                WatermarkStrategy.<DriverLocation>forBoundedOutOfOrderness(
                    Duration.ofSeconds(2))
                .withTimestampAssigner((event, timestamp) ->
                    event.getTimestamp()));

        // Spatial join for driver matching
        DataStream<MatchResult> matches = rideRequests
            .keyBy(RideRequest::getGeoHash)
            .connect(driverLocations.keyBy(DriverLocation::getGeoHash))
            .process(new DriverMatchingFunction())
            .name("driver-matching");

        // Sink to Kafka
        matches.addSink(new FlinkKafkaProducer<>(
            "match-results",
            new MatchResultSchema(),
            kafkaProps));

        env.execute("Uber Driver Matching");
    }
}

public class DriverMatchingFunction
    extends CoProcessFunction<RideRequest, DriverLocation, MatchResult> {

    private ValueState<List<DriverLocation>> availableDrivers;
    private ValueState<List<RideRequest>> pendingRequests;

    @Override
    public void open(Configuration parameters) {
        ValueStateDescriptor<List<DriverLocation>> driverDescriptor =
            new ValueStateDescriptor<>("available-drivers",
                Types.LIST(Types.POJO(DriverLocation.class)));
        availableDrivers = getRuntimeContext().getState(driverDescriptor);

        ValueStateDescriptor<List<RideRequest>> requestDescriptor =
            new ValueStateDescriptor<>("pending-requests",
                Types.LIST(Types.POJO(RideRequest.class)));
        pendingRequests = getRuntimeContext().getState(requestDescriptor);
    }

    @Override
    public void processElement1(RideRequest request, Context ctx,
                               Collector<MatchResult> out) throws Exception {
        List<DriverLocation> drivers = availableDrivers.value();
        if (drivers != null && !drivers.isEmpty()) {
            DriverLocation bestDriver = findBestMatch(request, drivers);
            if (bestDriver != null) {
                out.collect(new MatchResult(request, bestDriver));
                drivers.remove(bestDriver);
                availableDrivers.update(drivers);
                return;
            }
        }

        // No driver available, add to pending
        List<RideRequest> pending = pendingRequests.value();
        if (pending == null) pending = new ArrayList<>();
        pending.add(request);
        pendingRequests.update(pending);

        // Set timer for request timeout
        ctx.timerService().registerEventTimeTimer(
            request.getTimestamp() + 300000); // 5 minutes
    }

    @Override
    public void processElement2(DriverLocation driver, Context ctx,
                               Collector<MatchResult> out) throws Exception {
        if (!driver.isAvailable()) return;

        List<RideRequest> pending = pendingRequests.value();
        if (pending != null && !pending.isEmpty()) {
            RideRequest bestRequest = findBestRequest(driver, pending);
            if (bestRequest != null) {
                out.collect(new MatchResult(bestRequest, driver));
                pending.remove(bestRequest);
                pendingRequests.update(pending);
                return;
            }
        }

        // No pending request, add driver to available pool
        List<DriverLocation> drivers = availableDrivers.value();
        if (drivers == null) drivers = new ArrayList<>();
        drivers.add(driver);
        availableDrivers.update(drivers);
    }
}
```

### Monitoring Configuration
```yaml
# Prometheus metrics for Flink
flink_metrics:
  - name: flink_job_uptime
    query: flink_jobmanager_job_uptime
    alert_threshold: 0.999

  - name: flink_checkpoint_duration
    query: flink_jobmanager_job_lastCheckpointDuration
    alert_threshold: 60000  # 60 seconds

  - name: flink_records_lag
    query: flink_taskmanager_job_task_operator_recordsLagMax
    alert_threshold: 10000

  - name: flink_backpressure
    query: flink_taskmanager_job_task_backPressuredTimeMsPerSecond
    alert_threshold: 500
```

## Cost Analysis

### Infrastructure Costs
- **Flink Cluster**: $80K/month (200 r5.4xlarge nodes)
- **Kafka Infrastructure**: $40K/month (50 brokers)
- **Storage (HDFS/S3)**: $15K/month (checkpoint storage)
- **Monitoring Stack**: $8K/month
- **Total Monthly**: $143K

### Operational Costs
- **Stream Processing Team**: $150K/month (6 engineers)
- **On-call Support**: $25K/month
- **Training and Tooling**: $10K/month
- **Total Operational**: $185K/month

### Business Value
- **Real-time Matching**: $100M/year revenue from optimized matching
- **Dynamic Pricing**: $50M/year from surge optimization
- **Fraud Prevention**: $20M/year losses prevented
- **Operational Efficiency**: $30M/year cost savings

## Battle-tested Lessons

### What Works at 3 AM
1. **Exactly-once Processing**: Zero data loss during failures
2. **Fast Recovery**: 30-second recovery from checkpoints
3. **Backpressure Management**: System stays stable under load
4. **Rich Monitoring**: Detailed visibility into stream health

### Common Stream Processing Failures
1. **State Size Explosion**: Large state causes OOM failures
2. **Late Event Handling**: Watermark configuration issues
3. **Serialization Problems**: Schema evolution breaks jobs
4. **Resource Starvation**: CPU/memory exhaustion under load

### Operational Best Practices
1. **Gradual Deployment**: Blue-green deployments for stream jobs
2. **State Migration**: Backward-compatible state schema changes
3. **Resource Planning**: Monitor resource usage patterns
4. **Circuit Breakers**: Protect downstream systems from overload

## Advanced Patterns

### Complex Event Processing
```java
// Pattern detection for fraud
Pattern<Transaction, ?> fraudPattern = Pattern
    .<Transaction>begin("first")
    .where(new SimpleCondition<Transaction>() {
        @Override
        public boolean filter(Transaction transaction) {
            return transaction.getAmount() > 1000;
        }
    })
    .next("second")
    .where(new SimpleCondition<Transaction>() {
        @Override
        public boolean filter(Transaction transaction) {
            return transaction.getAmount() > 1000;
        }
    })
    .within(Time.minutes(10));
```

### Machine Learning Integration
```java
// Real-time ML model serving
DataStream<ScoredEvent> scoredEvents = events
    .map(new RichMapFunction<Event, ScoredEvent>() {
        private MLModel model;

        @Override
        public void open(Configuration parameters) {
            model = MLModelLoader.load("fraud-detection-v1.2");
        }

        @Override
        public ScoredEvent map(Event event) {
            double score = model.predict(event.getFeatures());
            return new ScoredEvent(event, score);
        }
    });
```

## Related Patterns
- [Event Sourcing](./event-sourcing.md)
- [CQRS](./cqrs.md)
- [Microservices](./microservices.md)

*Source: Uber Engineering Blog, Apache Flink Documentation, Personal Production Experience, Flink Forward Conferences*