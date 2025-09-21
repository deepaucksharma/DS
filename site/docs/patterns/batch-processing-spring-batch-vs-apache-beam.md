# Batch Processing Pattern: Spring Batch vs Apache Beam in Production

## Overview

Comprehensive analysis of batch processing frameworks: Spring Batch (used by banks, financial institutions) vs Apache Beam (Google, Netflix, Spotify). Both handle large-scale data processing, but Spring Batch focuses on traditional ETL workflows while Apache Beam provides unified stream/batch processing. Real production data shows critical differences in scalability, development complexity, and operational characteristics.

## Production Architecture Comparison

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - #3B82F6]
        SCHEDULER[Job Scheduler<br/>Cron/Airflow<br/>Trigger management<br/>SLA monitoring]
        DATA_INGRESS[Data Ingress<br/>File uploads<br/>API endpoints<br/>Streaming sources]
    end

    subgraph ServicePlane[Service Plane - #10B981]
        subgraph SpringBatchImplementation[Spring Batch - Banking/Financial]
            BATCH_APP[Spring Boot Application<br/>Job launcher<br/>Step executor<br/>Chunk processing]

            subgraph BatchJobs[Batch Job Structure]
                JOB_LAUNCHER[Job Launcher<br/>Parameter validation<br/>Job execution<br/>Status tracking]
                STEP_EXECUTOR[Step Executor<br/>Reader-Processor-Writer<br/>Chunk-based processing<br/>Transaction management]
                CHUNK_PROCESSOR[Chunk Processor<br/>Configurable chunk size<br/>Parallel processing<br/>Error handling]
            end

            SPRING_SCHEDULER[Spring Task Scheduler<br/>@Scheduled jobs<br/>Async execution<br/>Thread pool management]
        end

        subgraph ApacheBeamImplementation[Apache Beam - Google/Netflix/Spotify]
            BEAM_PIPELINE[Beam Pipeline<br/>Dataflow runner<br/>Unified batch/stream<br/>Auto-scaling]

            subgraph BeamComponents[Beam Pipeline Components]
                PCOLLECTION[PCollection<br/>Immutable data sets<br/>Parallel processing<br/>Windowing support]
                PTRANSFORM[PTransform<br/>Data transformations<br/>User-defined functions<br/>Built-in transforms]
                PIPELINE_RUNNER[Pipeline Runner<br/>Dataflow/Flink/Spark<br/>Resource management<br/>Fault tolerance]
            end

            BEAM_SCHEDULER[Workflow Orchestration<br/>Dataflow templates<br/>Cloud Composer<br/>Kubernetes jobs]
        end

        subgraph ProcessingWorkers[Processing Workers]
            WORKER_NODES[Worker Nodes<br/>Parallel execution<br/>Resource allocation<br/>Load balancing]
            EXECUTOR_POOLS[Executor Thread Pools<br/>Configurable sizing<br/>CPU optimization<br/>Memory management]
        end
    end

    subgraph StatePlane[State Plane - #F59E0B]
        subgraph SpringBatchState[Spring Batch State Management]
            BATCH_METADATA[Batch Metadata DB<br/>Job repository<br/>Execution context<br/>Step status tracking]
            CHECKPOINT_STORE[Checkpoint Store<br/>Restart capability<br/>Step completion<br/>Skip records]
            ITEM_STORE[Item Store<br/>Reader state<br/>Skip lists<br/>Retry counts]
        end

        subgraph BeamState[Apache Beam State Management]
            BEAM_STATE[Beam State Store<br/>Stateful processing<br/>Windowing state<br/>Timers and triggers]
            SIDE_INPUTS[Side Inputs<br/>Reference data<br/>Broadcast variables<br/>Lookup tables]
            METRICS_STORE[Metrics Store<br/>Pipeline metrics<br/>Transform statistics<br/>Element counts]
        end

        subgraph DataSources[Data Sources & Sinks]
            INPUT_DATA[(Input Data Sources<br/>Databases<br/>File systems<br/>Message queues<br/>APIs)]
            OUTPUT_DATA[(Output Data Sinks<br/>Data warehouses<br/>Analytics systems<br/>Reporting databases<br/>File exports)]
            TEMP_STORAGE[Temporary Storage<br/>Processing buffers<br/>Shuffle data<br/>Intermediate results]
        end
    end

    subgraph ControlPlane[Control Plane - #8B5CF6]
        JOB_MONITOR[Job Monitoring<br/>Execution tracking<br/>Performance metrics<br/>Failure detection]
        RESOURCE_MANAGER[Resource Management<br/>Auto-scaling<br/>Memory allocation<br/>CPU optimization]
        ALERTING[Batch Job Alerting<br/>Failure notifications<br/>SLA violations<br/>Resource exhaustion]
        SCHEDULER_MGMT[Scheduler Management<br/>Job dependencies<br/>Priority queues<br/>Resource contention]
    end

    SCHEDULER --> DATA_INGRESS
    DATA_INGRESS --> BATCH_APP
    DATA_INGRESS --> BEAM_PIPELINE

    BATCH_APP --> JOB_LAUNCHER
    JOB_LAUNCHER --> STEP_EXECUTOR
    STEP_EXECUTOR --> CHUNK_PROCESSOR
    CHUNK_PROCESSOR --> SPRING_SCHEDULER

    BEAM_PIPELINE --> PCOLLECTION
    PCOLLECTION --> PTRANSFORM
    PTRANSFORM --> PIPELINE_RUNNER
    PIPELINE_RUNNER --> BEAM_SCHEDULER

    JOB_LAUNCHER --> WORKER_NODES
    PIPELINE_RUNNER --> EXECUTOR_POOLS

    STEP_EXECUTOR --> BATCH_METADATA
    CHUNK_PROCESSOR --> CHECKPOINT_STORE
    SPRING_SCHEDULER --> ITEM_STORE

    PCOLLECTION --> BEAM_STATE
    PTRANSFORM --> SIDE_INPUTS
    PIPELINE_RUNNER --> METRICS_STORE

    WORKER_NODES --> INPUT_DATA
    EXECUTOR_POOLS --> OUTPUT_DATA
    BATCH_METADATA --> TEMP_STORAGE

    JOB_LAUNCHER --> JOB_MONITOR
    PIPELINE_RUNNER --> JOB_MONITOR
    JOB_MONITOR --> RESOURCE_MANAGER
    RESOURCE_MANAGER --> ALERTING
    ALERTING --> SCHEDULER_MGMT

    classDef edgeStyle fill:#3B82F6,stroke:#1E40AF,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#047857,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#6D28D9,color:#fff

    class SCHEDULER,DATA_INGRESS edgeStyle
    class BATCH_APP,JOB_LAUNCHER,STEP_EXECUTOR,CHUNK_PROCESSOR,SPRING_SCHEDULER,BEAM_PIPELINE,PCOLLECTION,PTRANSFORM,PIPELINE_RUNNER,BEAM_SCHEDULER,WORKER_NODES,EXECUTOR_POOLS serviceStyle
    class BATCH_METADATA,CHECKPOINT_STORE,ITEM_STORE,BEAM_STATE,SIDE_INPUTS,METRICS_STORE,INPUT_DATA,OUTPUT_DATA,TEMP_STORAGE stateStyle
    class JOB_MONITOR,RESOURCE_MANAGER,ALERTING,SCHEDULER_MGMT controlStyle
```

## Batch Processing Execution Flow

```mermaid
sequenceDiagram
    participant Scheduler
    participant SpringBatch as Spring Batch Job
    participant BeamPipeline as Beam Pipeline
    participant DataSource as Data Source
    participant DataSink as Data Sink
    participant Monitor as Job Monitor

    Note over Scheduler,Monitor: Job Initialization

    %% Spring Batch Flow
    Scheduler->>SpringBatch: Launch daily ETL job
    SpringBatch->>SpringBatch: Validate job parameters
    SpringBatch->>Monitor: Job started event

    SpringBatch->>DataSource: Initialize ItemReader
    DataSource-->>SpringBatch: Reader configured (chunk size: 1000)

    loop Chunk Processing
        SpringBatch->>DataSource: Read chunk (1000 items)
        DataSource-->>SpringBatch: Data chunk
        SpringBatch->>SpringBatch: Process chunk (transform)
        SpringBatch->>DataSink: Write processed chunk
        DataSink-->>SpringBatch: Write successful
        SpringBatch->>Monitor: Progress update (10000 items processed)
    end

    SpringBatch->>Monitor: Job completed successfully

    Note over Scheduler,Monitor: Apache Beam Flow

    %% Apache Beam Flow
    Scheduler->>BeamPipeline: Submit pipeline job
    BeamPipeline->>BeamPipeline: Parse pipeline definition
    BeamPipeline->>Monitor: Pipeline started

    BeamPipeline->>DataSource: Create PCollection
    DataSource-->>BeamPipeline: Bounded/Unbounded source

    BeamPipeline->>BeamPipeline: Apply PTransforms
    Note over BeamPipeline: Parallel execution across workers

    BeamPipeline->>BeamPipeline: Execute pipeline DAG
    Note over BeamPipeline: Auto-scaling based on data volume

    BeamPipeline->>DataSink: Write results
    DataSink-->>BeamPipeline: Output written

    BeamPipeline->>Monitor: Pipeline completed

    Note over Scheduler,Monitor: Error Handling

    %% Error Scenarios
    SpringBatch->>DataSource: Read chunk
    DataSource-->>SpringBatch: IOException
    SpringBatch->>SpringBatch: Skip item and continue
    SpringBatch->>Monitor: Error logged, job continues

    BeamPipeline->>BeamPipeline: Transform failure
    BeamPipeline->>BeamPipeline: Retry with exponential backoff
    BeamPipeline->>Monitor: Transform retried successfully
```

## Batch Processing Patterns Deep Dive

```mermaid
graph TB
    subgraph ProcessingPatterns[Batch Processing Pattern Analysis]
        subgraph SpringBatchPatterns[Spring Batch Patterns - Banking/Financial]
            CHUNK_PROCESSING[Chunk-based Processing<br/>Read-Process-Write<br/>Configurable chunk size<br/>Transaction boundaries]

            TASKLET_PATTERN[Tasklet Pattern<br/>Single operation tasks<br/>Custom logic execution<br/>Simple transformations]

            PARTITION_PATTERN[Partitioning Pattern<br/>Parallel step execution<br/>Data partitioning<br/>Worker thread pools]

            CONDITIONAL_FLOW[Conditional Flow<br/>Decision-based routing<br/>Conditional step execution<br/>Flow control logic]

            RESTART_PATTERN[Restart Pattern<br/>Job restart capability<br/>Skip processed items<br/>Failure recovery]
        end

        subgraph BeamPatterns[Apache Beam Patterns - Google/Netflix]
            PIPELINE_PATTERN[Pipeline Pattern<br/>DAG execution<br/>Transform composition<br/>Immutable PCollections]

            WINDOWING_PATTERN[Windowing Pattern<br/>Time-based windows<br/>Session windows<br/>Sliding windows]

            SIDE_INPUT_PATTERN[Side Input Pattern<br/>Reference data joins<br/>Broadcast variables<br/>Lookup enrichment]

            STATEFUL_PROCESSING[Stateful Processing<br/>State and timers<br/>Key-based state<br/>Custom state stores]

            STREAMING_BATCH[Unified Stream/Batch<br/>Same code for both<br/>Watermarks<br/>Late data handling]
        end

        subgraph PerformancePatterns[Performance Optimization Patterns]
            PARALLEL_EXECUTION[Parallel Execution<br/>Multi-threading<br/>Worker distribution<br/>Resource utilization]

            MEMORY_OPTIMIZATION[Memory Optimization<br/>Streaming reads<br/>Garbage collection<br/>Buffer management]

            IO_OPTIMIZATION[I/O Optimization<br/>Batch reads/writes<br/>Connection pooling<br/>Asynchronous I/O]

            RESOURCE_SCALING[Resource Scaling<br/>Auto-scaling workers<br/>Dynamic allocation<br/>Cost optimization]
        end
    end

    subgraph DataPatterns[Data Processing Patterns]
        subgraph ETLPatterns[ETL Pattern Implementation]
            EXTRACT_PATTERNS[Extract Patterns<br/>Database readers<br/>File readers<br/>API extractors<br/>Incremental extraction]

            TRANSFORM_PATTERNS[Transform Patterns<br/>Data validation<br/>Type conversion<br/>Business logic<br/>Aggregation]

            LOAD_PATTERNS[Load Patterns<br/>Batch inserts<br/>Upsert operations<br/>Data partitioning<br/>Index management]

            ERROR_HANDLING[Error Handling<br/>Skip records<br/>Dead letter queues<br/>Error reporting<br/>Data quality]
        end

        subgraph ScalabilityPatterns[Scalability Patterns]
            HORIZONTAL_SCALING[Horizontal Scaling<br/>Worker node scaling<br/>Data partitioning<br/>Load distribution]

            VERTICAL_SCALING[Vertical Scaling<br/>Memory allocation<br/>CPU optimization<br/>Thread tuning]

            ELASTIC_SCALING[Elastic Scaling<br/>Cloud auto-scaling<br/>Cost-aware scaling<br/>Spot instance usage]

            BACKPRESSURE[Backpressure Handling<br/>Rate limiting<br/>Flow control<br/>Queue management]
        end
    end

    CHUNK_PROCESSING --> EXTRACT_PATTERNS
    TASKLET_PATTERN --> TRANSFORM_PATTERNS
    PIPELINE_PATTERN --> LOAD_PATTERNS
    WINDOWING_PATTERN --> ERROR_HANDLING

    PARTITION_PATTERN --> HORIZONTAL_SCALING
    STATEFUL_PROCESSING --> VERTICAL_SCALING
    STREAMING_BATCH --> ELASTIC_SCALING
    RESTART_PATTERN --> BACKPRESSURE

    PARALLEL_EXECUTION --> HORIZONTAL_SCALING
    MEMORY_OPTIMIZATION --> VERTICAL_SCALING
    IO_OPTIMIZATION --> ELASTIC_SCALING
    RESOURCE_SCALING --> BACKPRESSURE

    classDef springStyle fill:#6DB33F,stroke:#5A9E36,color:#fff
    classDef beamStyle fill:#FF6600,stroke:#E55A00,color:#fff
    classDef performanceStyle fill:#3B82F6,stroke:#1E40AF,color:#fff
    classDef etlStyle fill:#8B5CF6,stroke:#6D28D9,color:#fff
    classDef scalabilityStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class CHUNK_PROCESSING,TASKLET_PATTERN,PARTITION_PATTERN,CONDITIONAL_FLOW,RESTART_PATTERN springStyle
    class PIPELINE_PATTERN,WINDOWING_PATTERN,SIDE_INPUT_PATTERN,STATEFUL_PROCESSING,STREAMING_BATCH beamStyle
    class PARALLEL_EXECUTION,MEMORY_OPTIMIZATION,IO_OPTIMIZATION,RESOURCE_SCALING performanceStyle
    class EXTRACT_PATTERNS,TRANSFORM_PATTERNS,LOAD_PATTERNS,ERROR_HANDLING etlStyle
    class HORIZONTAL_SCALING,VERTICAL_SCALING,ELASTIC_SCALING,BACKPRESSURE scalabilityStyle
```

## Production Use Cases and Performance

```mermaid
graph TB
    subgraph UseCaseAnalysis[Production Use Case Analysis]
        subgraph BankingUseCases[Banking Use Cases - Spring Batch]
            DAILY_RECONCILIATION[Daily Reconciliation<br/>Transaction matching<br/>Account balancing<br/>Regulatory reporting]

            INTEREST_CALCULATION[Interest Calculation<br/>Compound interest<br/>Account processing<br/>Rate application]

            RISK_REPORTING[Risk Reporting<br/>Credit risk analysis<br/>Market risk calculation<br/>Regulatory compliance]

            CUSTOMER_STATEMENTS[Customer Statements<br/>Monthly statements<br/>PDF generation<br/>Multi-channel delivery]
        end

        subgraph TechCompanyUseCases[Tech Company Use Cases - Apache Beam]
            LOG_ANALYTICS[Log Analytics<br/>Real-time processing<br/>Anomaly detection<br/>Metrics aggregation]

            RECOMMENDATION_ENGINE[Recommendation Engine<br/>User behavior analysis<br/>ML feature generation<br/>Real-time serving]

            DATA_LAKE_ETL[Data Lake ETL<br/>Multi-source ingestion<br/>Schema evolution<br/>Format conversion]

            STREAMING_ANALYTICS[Streaming Analytics<br/>Event processing<br/>Window aggregations<br/>Late data handling]
        end

        subgraph PerformanceCharacteristics[Performance Characteristics]
            THROUGHPUT_COMPARISON[Throughput Comparison<br/>Spring Batch: 100K-1M records/min<br/>Apache Beam: 1M-10M+ records/min<br/>Depends on complexity]

            LATENCY_COMPARISON[Latency Comparison<br/>Spring Batch: Minutes to hours<br/>Apache Beam: Seconds to minutes<br/>Real-time vs batch]

            RESOURCE_USAGE[Resource Usage<br/>Spring Batch: Fixed resources<br/>Apache Beam: Elastic scaling<br/>Cost implications]

            COMPLEXITY_ANALYSIS[Development Complexity<br/>Spring Batch: Simple ETL<br/>Apache Beam: Complex patterns<br/>Learning curve]
        end
    end

    subgraph ScalabilityAnalysis[Scalability Analysis]
        subgraph SpringBatchScaling[Spring Batch Scaling Limits]
            SINGLE_JVM[Single JVM Limitation<br/>Memory constraints<br/>CPU bottlenecks<br/>Threading limits]

            PARTITIONING_LIMITS[Partitioning Limits<br/>Fixed worker pools<br/>Manual scaling<br/>Resource planning]

            DATABASE_BOTTLENECKS[Database Bottlenecks<br/>Connection pool limits<br/>Lock contention<br/>Transaction overhead]

            DEPLOYMENT_COMPLEXITY[Deployment Complexity<br/>Application servers<br/>Configuration management<br/>Version coordination]
        end

        subgraph BeamScaling[Apache Beam Scaling Capabilities]
            AUTO_SCALING[Auto-scaling<br/>Dynamic worker allocation<br/>Spot instance usage<br/>Cost optimization]

            DISTRIBUTED_PROCESSING[Distributed Processing<br/>Multi-node execution<br/>Fault tolerance<br/>Load balancing]

            RUNNER_FLEXIBILITY[Runner Flexibility<br/>Dataflow/Flink/Spark<br/>Cloud/on-premise<br/>Resource optimization]

            UNIFIED_MODEL[Unified Batch/Stream<br/>Same codebase<br/>Consistent semantics<br/>Operational simplicity]
        end
    end

    DAILY_RECONCILIATION --> THROUGHPUT_COMPARISON
    LOG_ANALYTICS --> LATENCY_COMPARISON
    INTEREST_CALCULATION --> RESOURCE_USAGE
    RECOMMENDATION_ENGINE --> COMPLEXITY_ANALYSIS

    SINGLE_JVM --> AUTO_SCALING
    PARTITIONING_LIMITS --> DISTRIBUTED_PROCESSING
    DATABASE_BOTTLENECKS --> RUNNER_FLEXIBILITY
    DEPLOYMENT_COMPLEXITY --> UNIFIED_MODEL

    classDef bankingStyle fill:#1E40AF,stroke:#1E3A8A,color:#fff
    classDef techStyle fill:#059669,stroke:#047857,color:#fff
    classDef performanceStyle fill:#DC2626,stroke:#B91C1C,color:#fff
    classDef springScaleStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef beamScaleStyle fill:#8B5CF6,stroke:#6D28D9,color:#fff

    class DAILY_RECONCILIATION,INTEREST_CALCULATION,RISK_REPORTING,CUSTOMER_STATEMENTS bankingStyle
    class LOG_ANALYTICS,RECOMMENDATION_ENGINE,DATA_LAKE_ETL,STREAMING_ANALYTICS techStyle
    class THROUGHPUT_COMPARISON,LATENCY_COMPARISON,RESOURCE_USAGE,COMPLEXITY_ANALYSIS performanceStyle
    class SINGLE_JVM,PARTITIONING_LIMITS,DATABASE_BOTTLENECKS,DEPLOYMENT_COMPLEXITY springScaleStyle
    class AUTO_SCALING,DISTRIBUTED_PROCESSING,RUNNER_FLEXIBILITY,UNIFIED_MODEL beamScaleStyle
```

## Production Metrics and Performance

### Performance Benchmarks (Based on Banking vs Tech Company Production)
| Metric | Spring Batch | Apache Beam |
|--------|--------------|-------------|
| **Throughput** | 100K-1M records/min | 1M-10M+ records/min |
| **Latency** | Minutes to hours | Seconds to minutes |
| **Max Workers** | 50-100 threads | 1000+ workers |
| **Memory Usage** | 2-16GB (single JVM) | Auto-scaling |
| **Development Time** | 2-4 weeks | 4-8 weeks |
| **Operational Complexity** | Medium | High |

### Production Reliability Metrics
| Failure Mode | Spring Batch | Apache Beam |
|--------------|--------------|-------------|
| **Job Restart** | Built-in checkpointing | Pipeline restart |
| **Error Handling** | Skip/retry policies | Dead letter queues |
| **Monitoring** | Spring Boot Actuator | Dataflow monitoring |
| **Debugging** | Standard Java tools | Distributed tracing |

## Implementation Examples

### Spring Batch Implementation (Banking-style)
```java
// Production Spring Batch job for financial reconciliation
@Configuration
@EnableBatchProcessing
public class ReconciliationBatchConfig {

    @Autowired
    private JobBuilderFactory jobBuilderFactory;

    @Autowired
    private StepBuilderFactory stepBuilderFactory;

    @Autowired
    private DataSource dataSource;

    // Main reconciliation job
    @Bean
    public Job dailyReconciliationJob() {
        return jobBuilderFactory.get("dailyReconciliationJob")
            .incrementer(new RunIdIncrementer())
            .listener(jobExecutionListener())
            .flow(extractTransactionsStep())
            .next(validateTransactionsStep())
            .next(reconcileAccountsStep())
            .next(generateReportStep())
            .end()
            .build();
    }

    // Step 1: Extract transactions from multiple sources
    @Bean
    public Step extractTransactionsStep() {
        return stepBuilderFactory.get("extractTransactionsStep")
            .<Transaction, Transaction>chunk(1000)
            .reader(transactionReader())
            .processor(transactionProcessor())
            .writer(transactionWriter())
            .faultTolerant()
            .skipLimit(100)
            .skip(DataFormatException.class)
            .retryLimit(3)
            .retry(TransientException.class)
            .listener(stepExecutionListener())
            .taskExecutor(taskExecutor())
            .throttleLimit(10)
            .build();
    }

    @Bean
    @StepScope
    public JdbcCursorItemReader<Transaction> transactionReader() {
        return new JdbcCursorItemReaderBuilder<Transaction>()
            .name("transactionReader")
            .dataSource(dataSource)
            .sql("SELECT * FROM transactions WHERE date = ? AND processed = false")
            .preparedStatementSetter((ps, context) -> {
                String date = context.getJobParameters().getString("businessDate");
                ps.setString(1, date);
            })
            .rowMapper(new BeanPropertyRowMapper<>(Transaction.class))
            .build();
    }

    @Bean
    public ItemProcessor<Transaction, Transaction> transactionProcessor() {
        return new TransactionValidationProcessor();
    }

    @Bean
    public JdbcBatchItemWriter<Transaction> transactionWriter() {
        return new JdbcBatchItemWriterBuilder<Transaction>()
            .dataSource(dataSource)
            .sql("INSERT INTO reconciled_transactions (id, amount, account, status, processed_date) " +
                 "VALUES (:id, :amount, :account, :status, :processedDate)")
            .beanMapped()
            .build();
    }

    // Step 2: Account reconciliation with partitioning
    @Bean
    public Step reconcileAccountsStep() {
        return stepBuilderFactory.get("reconcileAccountsStep")
            .partitioner("accountPartitioner", accountPartitioner())
            .step(reconcileAccountStep())
            .gridSize(10)
            .taskExecutor(taskExecutor())
            .build();
    }

    @Bean
    public Partitioner accountPartitioner() {
        return new AccountPartitioner();
    }

    @Bean
    public Step reconcileAccountStep() {
        return stepBuilderFactory.get("reconcileAccountStep")
            .<Account, ReconciliationResult>chunk(100)
            .reader(accountReader())
            .processor(reconciliationProcessor())
            .writer(reconciliationWriter())
            .build();
    }

    @Bean
    public TaskExecutor taskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(10);
        executor.setMaxPoolSize(20);
        executor.setQueueCapacity(100);
        executor.setThreadNamePrefix("batch-");
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        executor.initialize();
        return executor;
    }

    // Custom processor for complex business logic
    @Component
    public static class TransactionValidationProcessor
            implements ItemProcessor<Transaction, Transaction> {

        @Autowired
        private ValidationService validationService;

        @Override
        public Transaction process(Transaction transaction) throws Exception {
            // Validate transaction data
            if (!validationService.isValidTransaction(transaction)) {
                throw new ValidationException("Invalid transaction: " + transaction.getId());
            }

            // Apply business rules
            transaction.setProcessedDate(LocalDateTime.now());
            transaction.setStatus(TransactionStatus.VALIDATED);

            // Calculate derived fields
            if (transaction.getAmount().compareTo(BigDecimal.valueOf(10000)) > 0) {
                transaction.setRequiresApproval(true);
            }

            return transaction;
        }
    }

    // Job execution listener for monitoring
    @Bean
    public JobExecutionListener jobExecutionListener() {
        return new JobExecutionListener() {
            @Override
            public void beforeJob(JobExecution jobExecution) {
                log.info("Starting reconciliation job for date: {}",
                    jobExecution.getJobParameters().getString("businessDate"));
            }

            @Override
            public void afterJob(JobExecution jobExecution) {
                if (jobExecution.getStatus() == BatchStatus.COMPLETED) {
                    log.info("Job completed successfully. Processed {} transactions",
                        jobExecution.getExecutionContext().getLong("totalTransactions"));
                } else {
                    log.error("Job failed with status: {}", jobExecution.getStatus());
                }
            }
        };
    }
}

// Custom partitioner for account-based processing
@Component
public class AccountPartitioner implements Partitioner {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Override
    public Map<String, ExecutionContext> partition(int gridSize) {
        Map<String, ExecutionContext> partitions = new HashMap<>();

        // Get account ranges for partitioning
        List<String> accountRanges = jdbcTemplate.queryForList(
            "SELECT DISTINCT account_branch FROM accounts ORDER BY account_branch",
            String.class
        );

        int partitionSize = accountRanges.size() / gridSize;
        int index = 0;

        for (int i = 0; i < gridSize; i++) {
            ExecutionContext context = new ExecutionContext();

            if (i < accountRanges.size()) {
                context.putString("accountBranch", accountRanges.get(i));
                context.putInt("partitionNumber", i);
            }

            partitions.put("partition" + i, context);
        }

        return partitions;
    }
}
```

### Apache Beam Implementation (Tech Company-style)
```java
// Production Apache Beam pipeline for log analytics
public class LogAnalyticsPipeline {

    public static void main(String[] args) {
        PipelineOptions options = PipelineOptionsFactory.fromArgs(args)
            .withValidation()
            .as(DataflowPipelineOptions.class);

        Pipeline pipeline = Pipeline.create(options);

        // Define the log analytics pipeline
        PCollection<LogEntry> logs = pipeline
            .apply("Read from Pub/Sub",
                PubsubIO.readStrings()
                    .fromSubscription(options.getInputSubscription()))
            .apply("Parse Log Entries",
                ParDo.of(new ParseLogEntryFn()))
            .apply("Filter Valid Logs",
                Filter.by(LogEntry::isValid));

        // Branch 1: Real-time alerting
        logs.apply("Extract Errors",
                Filter.by(log -> log.getLevel() == LogLevel.ERROR))
            .apply("Window into 1-minute",
                Window.<LogEntry>into(FixedWindows.of(Duration.standardMinutes(1)))
                    .triggering(Repeatedly.forever(
                        AfterWatermark.pastEndOfWindow()
                            .withEarlyFirings(AfterProcessingTime
                                .pastFirstElementInPane()
                                .plusDelayOf(Duration.standardSeconds(30)))))
                    .withAllowedLateness(Duration.standardMinutes(5))
                    .accumulatingFiredPanes())
            .apply("Count Errors",
                Count.perElement())
            .apply("Create Alerts",
                ParDo.of(new CreateAlertFn()))
            .apply("Send to Alert System",
                PubsubIO.writeStrings()
                    .to(options.getAlertTopic()));

        // Branch 2: Analytics aggregation
        logs.apply("Extract User Events",
                Filter.by(log -> log.getEventType() != null))
            .apply("Key by User",
                WithKeys.of((LogEntry log) -> log.getUserId()))
            .apply("Window into 1-hour",
                Window.<KV<String, LogEntry>>into(
                    FixedWindows.of(Duration.standardHours(1))))
            .apply("Group by User",
                GroupByKey.create())
            .apply("Aggregate User Metrics",
                ParDo.of(new AggregateUserMetricsFn()))
            .apply("Write to BigQuery",
                BigQueryIO.writeTableRows()
                    .to(options.getOutputTable())
                    .withWriteDisposition(BigQueryIO.Write.WriteDisposition.WRITE_APPEND)
                    .withCreateDisposition(BigQueryIO.Write.CreateDisposition.CREATE_IF_NEEDED));

        // Branch 3: ML feature extraction
        logs.apply("Extract Features",
                ParDo.of(new ExtractFeaturesFn()))
            .apply("Combine Global Features",
                Combine.globally(new FeatureCombineFn())
                    .withoutDefaults())
            .apply("Write Feature Store",
                ParDo.of(new WriteFeatureStoreFn()));

        pipeline.run().waitUntilFinish();
    }

    // Custom DoFn for parsing log entries
    static class ParseLogEntryFn extends DoFn<String, LogEntry> {
        private static final Gson gson = new Gson();

        @ProcessElement
        public void processElement(ProcessContext context) {
            try {
                String logLine = context.element();
                LogEntry entry = gson.fromJson(logLine, LogEntry.class);

                if (entry != null && entry.getTimestamp() != null) {
                    context.output(entry);
                }
            } catch (JsonSyntaxException e) {
                // Send to dead letter queue
                context.output(PARSE_ERROR_TAG,
                    FailedRecord.of(context.element(), e.getMessage()));
            }
        }
    }

    // Stateful processing for user session analysis
    static class AggregateUserMetricsFn
            extends DoFn<KV<String, Iterable<LogEntry>>, UserMetrics> {

        @StateId("userState")
        private final StateSpec<ValueState<UserSessionState>> userStateSpec =
            StateSpecs.value(AvroCoder.of(UserSessionState.class));

        @TimerId("sessionExpiry")
        private final TimerSpec sessionTimer = TimerSpecs.timer(TimeDomain.EVENT_TIME);

        @ProcessElement
        public void processElement(
                ProcessContext context,
                @StateId("userState") ValueState<UserSessionState> userState,
                @TimerId("sessionExpiry") Timer sessionTimer) {

            String userId = context.element().getKey();
            Iterable<LogEntry> logs = context.element().getValue();

            UserSessionState state = userState.read();
            if (state == null) {
                state = new UserSessionState(userId);
            }

            // Process all log entries for this user in this window
            for (LogEntry log : logs) {
                state.addLogEntry(log);
            }

            // Update state and set timer for session expiry
            userState.write(state);
            sessionTimer.set(context.timestamp().plus(Duration.standardHours(1)));

            // Output current metrics
            UserMetrics metrics = state.computeMetrics();
            context.output(metrics);
        }

        @OnTimer("sessionExpiry")
        public void onSessionExpiry(
                OnTimerContext context,
                @StateId("userState") ValueState<UserSessionState> userState) {

            UserSessionState state = userState.read();
            if (state != null) {
                // Finalize session and output final metrics
                UserMetrics finalMetrics = state.finalizeSession();
                context.output(finalMetrics);

                // Clear state
                userState.clear();
            }
        }
    }

    // Side input pattern for enrichment
    static class EnrichWithUserDataFn extends DoFn<LogEntry, EnrichedLogEntry> {

        private final PCollectionView<Map<String, UserProfile>> userProfilesView;

        public EnrichWithUserDataFn(PCollectionView<Map<String, UserProfile>> view) {
            this.userProfilesView = view;
        }

        @ProcessElement
        public void processElement(ProcessContext context) {
            LogEntry log = context.element();
            Map<String, UserProfile> profiles = context.sideInput(userProfilesView);

            UserProfile profile = profiles.get(log.getUserId());
            if (profile != null) {
                EnrichedLogEntry enriched = EnrichedLogEntry.builder()
                    .fromLogEntry(log)
                    .withUserProfile(profile)
                    .build();
                context.output(enriched);
            } else {
                // Output to dead letter for missing user data
                context.output(MISSING_USER_TAG, log);
            }
        }
    }

    // Custom combine function for feature aggregation
    static class FeatureCombineFn extends CombineFn<LogEntry, FeatureAccumulator, Features> {

        @Override
        public FeatureAccumulator createAccumulator() {
            return new FeatureAccumulator();
        }

        @Override
        public FeatureAccumulator addInput(FeatureAccumulator accumulator, LogEntry input) {
            accumulator.addLogEntry(input);
            return accumulator;
        }

        @Override
        public FeatureAccumulator mergeAccumulators(Iterable<FeatureAccumulator> accumulators) {
            FeatureAccumulator result = createAccumulator();
            for (FeatureAccumulator acc : accumulators) {
                result.merge(acc);
            }
            return result;
        }

        @Override
        public Features extractOutput(FeatureAccumulator accumulator) {
            return accumulator.computeFeatures();
        }
    }
}
```

### Monitoring and Observability
```java
// Comprehensive monitoring for both frameworks
@Component
public class BatchJobMonitoringService {

    private final MeterRegistry meterRegistry;
    private final Timer jobExecutionTimer;
    private final Counter jobFailureCounter;
    private final Gauge activeJobsGauge;

    public BatchJobMonitoringService(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;

        this.jobExecutionTimer = Timer.builder("batch.job.execution.time")
            .description("Batch job execution time")
            .register(meterRegistry);

        this.jobFailureCounter = Counter.builder("batch.job.failures")
            .description("Batch job failure count")
            .register(meterRegistry);

        this.activeJobsGauge = Gauge.builder("batch.jobs.active")
            .description("Number of active batch jobs")
            .register(meterRegistry, this, BatchJobMonitoringService::getActiveJobCount);
    }

    // Spring Batch monitoring
    @EventListener
    public void handleJobExecution(JobExecutionEvent event) {
        JobExecution jobExecution = event.getJobExecution();
        String jobName = jobExecution.getJobInstance().getJobName();

        if (jobExecution.getStatus() == BatchStatus.COMPLETED) {
            long duration = jobExecution.getEndTime().getTime() -
                           jobExecution.getStartTime().getTime();

            jobExecutionTimer
                .withTags("job.name", jobName, "status", "success")
                .record(duration, TimeUnit.MILLISECONDS);

            // Record processing metrics
            long itemsProcessed = jobExecution.getStepExecutions().stream()
                .mapToLong(StepExecution::getWriteCount)
                .sum();

            meterRegistry.counter("batch.items.processed", "job.name", jobName)
                .increment(itemsProcessed);

        } else if (jobExecution.getStatus() == BatchStatus.FAILED) {
            jobFailureCounter.withTags("job.name", jobName).increment();

            // Log failure details
            List<Throwable> failureExceptions = jobExecution.getAllFailureExceptions();
            log.error("Job {} failed with {} exceptions", jobName, failureExceptions.size());
        }
    }

    // Apache Beam monitoring
    public void monitorBeamPipeline(PipelineResult result, String pipelineName) {
        Timer.Sample sample = Timer.start(meterRegistry);

        result.waitUntilFinish().thenRun(() -> {
            sample.stop(jobExecutionTimer.withTags("pipeline.name", pipelineName, "status", "success"));

            // Get pipeline metrics
            MetricResults metrics = result.metrics();

            // Record custom metrics
            for (MetricResult<Long> counter : metrics.getCounters()) {
                meterRegistry.counter("beam.pipeline.counter",
                    "pipeline.name", pipelineName,
                    "counter.name", counter.getName().getName())
                    .increment(counter.getCommitted());
            }

            for (MetricResult<DistributionResult> distribution : metrics.getDistributions()) {
                DistributionResult dist = distribution.getCommitted();
                meterRegistry.timer("beam.pipeline.distribution",
                    "pipeline.name", pipelineName,
                    "distribution.name", distribution.getName().getName())
                    .record(dist.getMean(), TimeUnit.MILLISECONDS);
            }
        });
    }

    private double getActiveJobCount() {
        // Implementation to get active job count
        return 0.0; // Placeholder
    }
}
```

## Cost Analysis

### Infrastructure Costs (Monthly - 100M records)
| Component | Spring Batch | Apache Beam |
|-----------|--------------|-------------|
| **Compute** | $2K (fixed servers) | $5K (auto-scaling) |
| **Storage** | $500 (job repository) | $200 (temp storage) |
| **Network** | $200 | $800 (cloud transfer) |
| **Monitoring** | $300 | $1K (cloud monitoring) |
| **Total** | **$3K** | **$7K** |

### Operational Costs (Monthly)
| Resource | Spring Batch | Apache Beam |
|----------|--------------|-------------|
| **Development** | $10K (simpler) | $20K (complex) |
| **Operations** | $8K (server management) | $5K (managed service) |
| **Debugging** | $3K (standard tools) | $8K (distributed debugging) |
| **Training** | $2K | $8K |
| **Total** | **$23K** | **$41K** |

## Battle-tested Lessons

### Spring Batch in Production (Banking/Financial)
**What Works at 3 AM:**
- Reliable restart capabilities from checkpoints
- Well-understood Java stack and debugging
- Mature ecosystem and extensive documentation
- Predictable resource usage and performance

**Common Failures:**
- Out of memory errors with large datasets
- Database connection pool exhaustion
- Long-running transactions causing locks
- Difficulty scaling beyond single JVM limits

### Apache Beam in Production (Google/Netflix)
**What Works at 3 AM:**
- Auto-scaling handles unexpected load spikes
- Unified batch and streaming processing
- Fault tolerance with automatic retries
- Rich monitoring and observability

**Common Failures:**
- Complex debugging across distributed workers
- Unexpected cost spikes from auto-scaling
- Pipeline compilation and deployment complexity
- Learning curve for developers

## Selection Criteria

### Choose Spring Batch When:
- Traditional ETL workloads with fixed data volumes
- Java-centric organization with existing Spring ecosystem
- Need predictable resource usage and costs
- Simple to moderate complexity transformations
- Strong consistency and transaction requirements

### Choose Apache Beam When:
- Need to handle both batch and streaming data
- Large-scale data processing with auto-scaling
- Complex event-time processing requirements
- Want to leverage managed cloud services
- Can invest in learning distributed systems concepts

### Hybrid Approach When:
- Different workloads have different requirements
- Migration from traditional to cloud-native
- Want to compare performance and costs
- Need gradual team skill development

## Related Patterns
- [Data Pipeline Patterns](./data-pipeline-airflow-vs-dagster.md)
- [Stream Processing](./stream-processing-patterns.md)
- [ETL Patterns](./etl-patterns-production.md)

*Source: Banking Industry Reports, Netflix Tech Blog, Google Cloud Documentation, Spring Batch Reference, Apache Beam Documentation, Production Experience Reports*