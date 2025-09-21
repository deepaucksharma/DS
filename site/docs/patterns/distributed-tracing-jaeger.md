# Distributed Tracing: Jaeger at Uber

## Overview

Uber's Jaeger handles 1 billion traces daily across 2,000+ microservices, providing end-to-end request visibility for debugging, performance optimization, and dependency analysis. Their deployment processes 50 million spans per second with 1% sampling rate and sub-second query performance.

## Production Architecture

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - #3B82F6]
        MOBILE[Mobile Apps<br/>Trace origins<br/>User requests]
        WEB[Web Applications<br/>Browser tracing<br/>Frontend spans]
        API_GW[API Gateway<br/>Request entry point<br/>Trace ID generation]
    end

    subgraph ServicePlane[Service Plane - #10B981]
        subgraph JaegerComponents[Jaeger Components]
            JAEGER_AGENT[Jaeger Agent<br/>Local trace collection<br/>UDP batching<br/>Co-located with apps]
            JAEGER_COLLECTOR[Jaeger Collector<br/>Trace aggregation<br/>Kafka producer<br/>Auto-scaling]
            JAEGER_QUERY[Jaeger Query<br/>UI & API service<br/>Search interface<br/>Load balanced]
            JAEGER_UI[Jaeger UI<br/>Web interface<br/>Trace visualization<br/>Dependency graphs]
        end

        subgraph MicroservicesCluster[Microservices with Tracing]
            USER_SERVICE[User Service<br/>OpenTracing<br/>Span creation]
            RIDE_SERVICE[Ride Service<br/>Business logic<br/>Child spans]
            PAYMENT_SERVICE[Payment Service<br/>External calls<br/>Error tracking]
            NOTIFICATION_SERVICE[Notification Service<br/>Async processing<br/>Background traces]
        end
    end

    subgraph StatePlane[State Plane - #F59E0B]
        subgraph TracePipeline[Trace Processing Pipeline]
            KAFKA[Kafka Cluster<br/>Trace streaming<br/>50M spans/sec<br/>Real-time processing]
            SPARK[Spark Streaming<br/>Trace analysis<br/>Dependency extraction<br/>Aggregations]
        end

        subgraph TraceStorage[Trace Storage]
            CASSANDRA[(Cassandra Cluster<br/>Trace storage<br/>100TB+ data<br/>7-day retention)]
            ELASTICSEARCH[(Elasticsearch<br/>Trace indexing<br/>Full-text search<br/>Service maps)]
        end

        subgraph Dependencies[Dependency Data]
            SERVICE_DEPS[(Service Dependencies<br/>Relationship mapping<br/>Call patterns<br/>Performance metrics)]
        end
    end

    subgraph ControlPlane[Control Plane - #8B5CF6]
        PROMETHEUS[Prometheus<br/>Jaeger metrics<br/>System health<br/>Performance monitoring]
        GRAFANA[Grafana<br/>Operational dashboards<br/>SLA tracking<br/>Capacity planning]
        ALERTS[AlertManager<br/>Trace ingestion alerts<br/>Query performance<br/>Storage capacity]
    end

    %% Request flow
    MOBILE --> API_GW
    WEB --> API_GW
    API_GW --> USER_SERVICE

    %% Service calls
    USER_SERVICE --> RIDE_SERVICE
    RIDE_SERVICE --> PAYMENT_SERVICE
    PAYMENT_SERVICE --> NOTIFICATION_SERVICE

    %% Tracing flow
    USER_SERVICE --> JAEGER_AGENT
    RIDE_SERVICE --> JAEGER_AGENT
    PAYMENT_SERVICE --> JAEGER_AGENT
    NOTIFICATION_SERVICE --> JAEGER_AGENT

    JAEGER_AGENT --> JAEGER_COLLECTOR
    JAEGER_COLLECTOR --> KAFKA

    %% Processing pipeline
    KAFKA --> SPARK
    SPARK --> CASSANDRA
    SPARK --> ELASTICSEARCH
    SPARK --> SERVICE_DEPS

    %% Query path
    JAEGER_UI --> JAEGER_QUERY
    JAEGER_QUERY --> CASSANDRA
    JAEGER_QUERY --> ELASTICSEARCH

    %% Monitoring
    PROMETHEUS --> JAEGER_COLLECTOR
    PROMETHEUS --> JAEGER_QUERY
    PROMETHEUS --> CASSANDRA
    GRAFANA --> PROMETHEUS
    ALERTS --> PROMETHEUS

    %% Apply four-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#1E40AF,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#047857,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#6D28D9,color:#fff

    class MOBILE,WEB,API_GW edgeStyle
    class JAEGER_AGENT,JAEGER_COLLECTOR,JAEGER_QUERY,JAEGER_UI,USER_SERVICE,RIDE_SERVICE,PAYMENT_SERVICE,NOTIFICATION_SERVICE serviceStyle
    class KAFKA,SPARK,CASSANDRA,ELASTICSEARCH,SERVICE_DEPS stateStyle
    class PROMETHEUS,GRAFANA,ALERTS controlStyle
```

## Trace Lifecycle and Sampling

```mermaid
graph TB
    subgraph TraceLifecycle[Distributed Trace Lifecycle]
        subgraph SpanCreation[Span Creation]
            REQUEST_START[Request Initiated<br/>Trace ID generated<br/>Root span created<br/>Sampling decision]
            CHILD_SPANS[Child Spans<br/>Service calls<br/>Database queries<br/>Cache operations]
            SPAN_CONTEXT[Span Context<br/>Trace propagation<br/>HTTP headers<br/>gRPC metadata]
        end

        subgraph SamplingStrategy[Sampling Strategy]
            PROBABILISTIC[Probabilistic Sampling<br/>1% base rate<br/>Random selection<br/>Volume control]
            ADAPTIVE[Adaptive Sampling<br/>Service-specific rates<br/>Error rate boost<br/>Slow request boost]
            RATE_LIMITING[Rate Limiting<br/>Max spans/second<br/>Per-service limits<br/>Burst protection]
        end

        subgraph SpanCollection[Span Collection]
            LOCAL_BUFFER[Local Buffer<br/>Agent batching<br/>UDP transport<br/>Memory management]
            COMPRESSION[Compression<br/>Thrift protocol<br/>Bandwidth optimization<br/>CPU trade-off]
            RELIABILITY[Reliability<br/>Drop on overflow<br/>Circuit breaker<br/>Metrics tracking]
        end

        subgraph ProcessingPipeline[Processing Pipeline]
            VALIDATION[Validation<br/>Schema checking<br/>Data sanitization<br/>Error handling]
            ENRICHMENT[Enrichment<br/>Service metadata<br/>Environment tags<br/>Version info]
            INDEXING[Indexing<br/>Search optimization<br/>Query acceleration<br/>Partition strategy]
        end
    end

    REQUEST_START --> CHILD_SPANS
    CHILD_SPANS --> SPAN_CONTEXT

    SPAN_CONTEXT --> PROBABILISTIC
    PROBABILISTIC --> ADAPTIVE
    ADAPTIVE --> RATE_LIMITING

    RATE_LIMITING --> LOCAL_BUFFER
    LOCAL_BUFFER --> COMPRESSION
    COMPRESSION --> RELIABILITY

    RELIABILITY --> VALIDATION
    VALIDATION --> ENRICHMENT
    ENRICHMENT --> INDEXING

    classDef creationStyle fill:#10B981,stroke:#047857,color:#fff
    classDef samplingStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef collectionStyle fill:#8B5CF6,stroke:#6D28D9,color:#fff
    classDef processingStyle fill:#DC2626,stroke:#B91C1C,color:#fff

    class REQUEST_START,CHILD_SPANS,SPAN_CONTEXT creationStyle
    class PROBABILISTIC,ADAPTIVE,RATE_LIMITING samplingStyle
    class LOCAL_BUFFER,COMPRESSION,RELIABILITY collectionStyle
    class VALIDATION,ENRICHMENT,INDEXING processingStyle
```

## Service Dependency Analysis

```mermaid
graph TB
    subgraph DependencyMapping[Service Dependency Analysis]
        subgraph CallGraph[Service Call Graph]
            FRONTEND[Frontend Service<br/>Entry point<br/>User requests<br/>Authentication]

            subgraph BusinessLayer[Business Logic Layer]
                USER_SVC[User Service<br/>Profile management<br/>Authentication<br/>Preferences]
                RIDE_SVC[Ride Service<br/>Booking logic<br/>Trip management<br/>State machine]
                DRIVER_SVC[Driver Service<br/>Location tracking<br/>Availability<br/>Matching]
                PAYMENT_SVC[Payment Service<br/>Transaction processing<br/>Billing<br/>Refunds]
            end

            subgraph DataLayer[Data Access Layer]
                USER_DB[(User Database<br/>PostgreSQL<br/>Read replicas<br/>Connection pooling)]
                RIDE_DB[(Ride Database<br/>MongoDB<br/>Sharded<br/>Real-time updates)]
                CACHE[(Redis Cache<br/>Session data<br/>Location cache<br/>Configuration)]
            end

            subgraph ExternalServices[External Services]
                MAPS_API[Maps API<br/>Google Maps<br/>Route calculation<br/>ETA prediction]
                PAYMENT_GATEWAY[Payment Gateway<br/>Stripe/Braintree<br/>Credit card processing<br/>Fraud detection]
                SMS_SERVICE[SMS Service<br/>Twilio<br/>Notifications<br/>OTP delivery]
            end
        end

        subgraph DependencyMetrics[Dependency Metrics]
            CALL_VOLUME[Call Volume<br/>Requests/second<br/>Peak traffic<br/>Growth trends]
            LATENCY_ANALYSIS[Latency Analysis<br/>P50, P95, P99<br/>SLA compliance<br/>Performance degradation]
            ERROR_RATES[Error Rates<br/>4xx/5xx responses<br/>Timeout failures<br/>Circuit breaker trips]
            CRITICALITY[Criticality Score<br/>Business impact<br/>Failure blast radius<br/>Recovery complexity]
        end
    end

    FRONTEND --> USER_SVC
    FRONTEND --> RIDE_SVC
    USER_SVC --> USER_DB
    USER_SVC --> CACHE
    RIDE_SVC --> DRIVER_SVC
    RIDE_SVC --> RIDE_DB
    DRIVER_SVC --> CACHE
    DRIVER_SVC --> MAPS_API
    RIDE_SVC --> PAYMENT_SVC
    PAYMENT_SVC --> PAYMENT_GATEWAY
    PAYMENT_SVC --> SMS_SERVICE

    USER_SVC --> CALL_VOLUME
    RIDE_SVC --> LATENCY_ANALYSIS
    DRIVER_SVC --> ERROR_RATES
    PAYMENT_SVC --> CRITICALITY

    classDef frontendStyle fill:#3B82F6,stroke:#1E40AF,color:#fff
    classDef businessStyle fill:#10B981,stroke:#047857,color:#fff
    classDef dataStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef externalStyle fill:#8B5CF6,stroke:#6D28D9,color:#fff
    classDef metricsStyle fill:#DC2626,stroke:#B91C1C,color:#fff

    class FRONTEND frontendStyle
    class USER_SVC,RIDE_SVC,DRIVER_SVC,PAYMENT_SVC businessStyle
    class USER_DB,RIDE_DB,CACHE dataStyle
    class MAPS_API,PAYMENT_GATEWAY,SMS_SERVICE externalStyle
    class CALL_VOLUME,LATENCY_ANALYSIS,ERROR_RATES,CRITICALITY metricsStyle
```

## Performance Optimization and Query Patterns

```mermaid
graph TB
    subgraph QueryOptimization[Jaeger Query Optimization]
        subgraph QueryTypes[Common Query Patterns]
            TRACE_LOOKUP[Trace ID Lookup<br/>Direct access<br/>Partition key<br/>Sub-ms response]
            SERVICE_SEARCH[Service Search<br/>Time range + service<br/>Index scan<br/>Pagination support]
            ERROR_ANALYSIS[Error Analysis<br/>Error tag filtering<br/>Exception traces<br/>Root cause analysis]
            LATENCY_INVESTIGATION[Latency Investigation<br/>Duration filtering<br/>Slow trace detection<br/>Performance bottlenecks]
        end

        subgraph IndexingStrategy[Indexing Strategy]
            PRIMARY_INDEX[Primary Index<br/>Trace ID<br/>Partition by time<br/>Cassandra row key]
            SERVICE_INDEX[Service Index<br/>Service name + time<br/>Secondary index<br/>Query acceleration]
            OPERATION_INDEX[Operation Index<br/>Span operation<br/>Method-level tracing<br/>Fine-grained analysis]
            TAG_INDEX[Tag Index<br/>Custom tags<br/>Business context<br/>Flexible querying]
        end

        subgraph CachingLayer[Caching Layer]
            QUERY_CACHE[Query Cache<br/>Redis-backed<br/>Popular queries<br/>5-minute TTL]
            METADATA_CACHE[Metadata Cache<br/>Service list<br/>Operation list<br/>Tag values]
            DEPENDENCY_CACHE[Dependency Cache<br/>Service graph<br/>Daily refresh<br/>Background updates]
        end

        subgraph PerformanceTuning[Performance Tuning]
            PARTITION_PRUNING[Partition Pruning<br/>Time-based filtering<br/>Reduce scan scope<br/>Query planning]
            PARALLEL_EXECUTION[Parallel Execution<br/>Multi-node queries<br/>Scatter-gather<br/>Result merging]
            RESULT_LIMITING[Result Limiting<br/>Max trace count<br/>Time window limits<br/>Resource protection]
        end
    end

    TRACE_LOOKUP --> PRIMARY_INDEX
    SERVICE_SEARCH --> SERVICE_INDEX
    ERROR_ANALYSIS --> OPERATION_INDEX
    LATENCY_INVESTIGATION --> TAG_INDEX

    PRIMARY_INDEX --> QUERY_CACHE
    SERVICE_INDEX --> METADATA_CACHE
    OPERATION_INDEX --> DEPENDENCY_CACHE
    TAG_INDEX --> QUERY_CACHE

    QUERY_CACHE --> PARTITION_PRUNING
    METADATA_CACHE --> PARALLEL_EXECUTION
    DEPENDENCY_CACHE --> RESULT_LIMITING

    classDef queryStyle fill:#10B981,stroke:#047857,color:#fff
    classDef indexStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef cacheStyle fill:#8B5CF6,stroke:#6D28D9,color:#fff
    classDef tuningStyle fill:#DC2626,stroke:#B91C1C,color:#fff

    class TRACE_LOOKUP,SERVICE_SEARCH,ERROR_ANALYSIS,LATENCY_INVESTIGATION queryStyle
    class PRIMARY_INDEX,SERVICE_INDEX,OPERATION_INDEX,TAG_INDEX indexStyle
    class QUERY_CACHE,METADATA_CACHE,DEPENDENCY_CACHE cacheStyle
    class PARTITION_PRUNING,PARALLEL_EXECUTION,RESULT_LIMITING tuningStyle
```

## Production Metrics

### Trace Volume and Performance
- **Daily Traces**: 1 billion traces
- **Peak Span Rate**: 50 million spans/second
- **Sampling Rate**: 1% (adaptive per service)
- **Storage Size**: 100TB+ in Cassandra

### Query Performance
- **Trace Lookup**: P99 < 100ms
- **Service Search**: P99 < 500ms
- **Complex Queries**: P99 < 2 seconds
- **UI Response Time**: P95 < 1 second

### System Reliability
- **Ingestion Availability**: 99.99%
- **Query Availability**: 99.95%
- **Data Loss Rate**: <0.01%
- **False Positive Sampling**: <0.1%

## Implementation Details

### OpenTracing Integration
```java
// Uber's OpenTracing implementation
@RestController
public class RideController {

    @Autowired
    private Tracer tracer;

    @PostMapping("/rides")
    public ResponseEntity<Ride> createRide(@RequestBody RideRequest request) {
        Span span = tracer.nextSpan()
            .name("create-ride")
            .tag("operation", "create")
            .tag("user.id", request.getUserId())
            .tag("ride.type", request.getRideType())
            .start();

        try (Tracer.SpanInScope ws = tracer.withSpanInScope(span)) {
            // Validate request
            Span validationSpan = tracer.nextSpan()
                .name("validate-ride-request")
                .start();

            try (Tracer.SpanInScope vs = tracer.withSpanInScope(validationSpan)) {
                validateRideRequest(request);
            } catch (ValidationException e) {
                validationSpan.tag("error", true)
                    .tag("error.message", e.getMessage());
                throw e;
            } finally {
                validationSpan.end();
            }

            // Create ride
            Ride ride = rideService.createRide(request);

            span.tag("ride.id", ride.getId())
                .tag("ride.status", ride.getStatus());

            return ResponseEntity.ok(ride);

        } catch (Exception e) {
            span.tag("error", true)
                .tag("error.message", e.getMessage())
                .log(Map.of("event", "error", "message", e.getMessage()));
            throw e;
        } finally {
            span.end();
        }
    }
}

// Automatic instrumentation for HTTP clients
@Configuration
public class TracingConfig {

    @Bean
    public RestTemplate restTemplate() {
        RestTemplate restTemplate = new RestTemplate();
        restTemplate.getInterceptors().add(new TracingRestTemplateInterceptor(tracer));
        return restTemplate;
    }

    @Bean
    public Tracer jaegerTracer() {
        Configuration config = Configuration.fromEnv("ride-service");
        return config.getTracer();
    }
}
```

### Jaeger Configuration
```yaml
# Jaeger collector configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: jaeger-collector-config
data:
  collector.yaml: |
    receivers:
      jaeger:
        protocols:
          grpc:
            endpoint: 0.0.0.0:14250
          thrift_http:
            endpoint: 0.0.0.0:14268
          thrift_compact:
            endpoint: 0.0.0.0:14269

    processors:
      batch:
        timeout: 1s
        send_batch_size: 1024
        send_batch_max_size: 2048

      memory_limiter:
        check_interval: 1s
        limit_mib: 512

    exporters:
      kafka:
        brokers:
          - kafka-1:9092
          - kafka-2:9092
          - kafka-3:9092
        topic: jaeger-spans
        encoding: protobuf
        producer:
          max_message_bytes: 1000000
          required_acks: 1
          compression: gzip

    service:
      pipelines:
        traces:
          receivers: [jaeger]
          processors: [memory_limiter, batch]
          exporters: [kafka]

---
# Jaeger query service
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jaeger-query
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: jaeger-query
        image: jaegertracing/jaeger-query:1.35
        env:
        - name: SPAN_STORAGE_TYPE
          value: cassandra
        - name: CASSANDRA_SERVERS
          value: cassandra-1,cassandra-2,cassandra-3
        - name: CASSANDRA_KEYSPACE
          value: jaeger_v1_dc1
        - name: QUERY_MAX_CLOCK_SKEW_ADJUSTMENT
          value: 30s
        ports:
        - containerPort: 16686
        resources:
          requests:
            memory: "512Mi"
            cpu: "200m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

### Sampling Configuration
```json
{
  "service_strategies": [
    {
      "service": "user-service",
      "type": "probabilistic",
      "param": 0.01,
      "max_traces_per_second": 100
    },
    {
      "service": "payment-service",
      "type": "adaptive",
      "max_traces_per_second": 50,
      "operation_strategies": [
        {
          "operation": "process-payment",
          "type": "probabilistic",
          "param": 0.1
        }
      ]
    }
  ],
  "default_strategy": {
    "type": "probabilistic",
    "param": 0.001
  },
  "per_operation_strategies": [
    {
      "service": "ride-service",
      "operation": "create-ride",
      "type": "probabilistic",
      "param": 0.05
    }
  ]
}
```

## Cost Analysis

### Infrastructure Costs
- **Cassandra Cluster**: $40K/month (100TB storage, 50 nodes)
- **Kafka Infrastructure**: $15K/month (high-throughput streaming)
- **Jaeger Components**: $10K/month (collectors, agents, query)
- **Elasticsearch**: $8K/month (indexing and search)
- **Total Monthly**: $73K

### Operational Benefits
- **Debug Time Reduction**: 70% faster incident resolution
- **Performance Optimization**: $5M/year efficiency gains
- **Service Reliability**: 40% reduction in MTTR
- **Developer Productivity**: $10M/year faster development cycles

## Battle-tested Lessons

### What Works at 3 AM
1. **Trace ID Propagation**: Every log entry includes trace ID for correlation
2. **Error Span Tagging**: Failed spans clearly marked with error details
3. **Critical Path Monitoring**: Key business flows always sampled
4. **Dependency Visualization**: Service maps show blast radius immediately

### Common Tracing Pitfalls
1. **Over-sampling**: Too much data overwhelms storage and analysis
2. **Context Loss**: Missing span context breaks trace continuity
3. **High Cardinality Tags**: Unbounded tag values cause storage explosion
4. **Agent Resource Limits**: Under-provisioned agents drop spans

### Operational Best Practices
1. **Adaptive Sampling**: Dynamic rates based on service importance
2. **Span Enrichment**: Add business context to technical traces
3. **Privacy Compliance**: Sanitize PII from trace data
4. **Archive Strategy**: Move old traces to cheaper storage

## Related Patterns
- [Observability](./observability.md)
- [Microservices](./microservices.md)
- [Circuit Breaker](./circuit-breaker.md)

*Source: Uber Engineering Blog, Jaeger Documentation, OpenTracing Specification, Personal Production Experience*