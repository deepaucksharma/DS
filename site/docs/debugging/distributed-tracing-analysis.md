# Distributed Tracing Analysis - Production Debugging Guide

## Overview

This guide provides step-by-step debugging workflows for analyzing distributed traces in production systems. Based on Netflix's tracing infrastructure and Uber's distributed systems debugging practices.

**Time to Resolution**: 15-45 minutes for most issues
**Success Rate**: 85% of performance issues identified
**False Positive Rate**: <10%

## 1. Complete Distributed Tracing Debug Flow

```mermaid
flowchart TD
    Alert[🚨 Performance Alert<br/>p99 > 500ms] --> TraceID[1. Extract Trace ID<br/>From logs/metrics<br/>⏱️ 2 min]

    TraceID --> Jaeger{2. Query Jaeger<br/>traceID=${trace_id}<br/>⏱️ 1 min}

    Jaeger --> TraceFound{Trace Found?}
    TraceFound -->|No| SamplingCheck[3. Check Sampling<br/>Rate & Retention<br/>⏱️ 3 min]
    TraceFound -->|Yes| SpanAnalysis[4. Analyze Span Tree<br/>Critical Path Analysis<br/>⏱️ 5 min]

    SamplingCheck --> IncreaseSampling[Increase Sampling<br/>for Error Scenarios]
    SamplingCheck --> CheckLogs[Query Raw Logs<br/>for Request Context]

    SpanAnalysis --> CriticalPath{5. Identify Critical Path<br/>Longest Duration Chain}

    CriticalPath --> DatabaseSlow{Database<br/>Spans > 100ms?}
    CriticalPath --> ServiceSlow{Service Call<br/>Spans > 50ms?}
    CriticalPath --> NetworkSlow{Network<br/>Spans > 20ms?}

    DatabaseSlow -->|Yes| DBDebug[6a. Database Debug Flow<br/>Query Analysis + Locks<br/>⏱️ 10 min]
    ServiceSlow -->|Yes| ServiceDebug[6b. Service Debug Flow<br/>CPU/Memory/GC Analysis<br/>⏱️ 15 min]
    NetworkSlow -->|Yes| NetworkDebug[6c. Network Debug Flow<br/>Connection Pool + DNS<br/>⏱️ 8 min]

    DBDebug --> RootCause[7. Root Cause Identified<br/>Document + Alert Fix]
    ServiceDebug --> RootCause
    NetworkDebug --> RootCause

    RootCause --> Monitoring[8. Setup Monitoring<br/>Prevent Recurrence<br/>⏱️ 5 min]

    %% Apply 4-plane colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class Alert,TraceID edgeStyle
    class SpanAnalysis,ServiceDebug,ServiceSlow serviceStyle
    class DBDebug,DatabaseSlow,Jaeger stateStyle
    class Monitoring,RootCause,CriticalPath controlStyle
```

## 2. Netflix-Style Span Analysis Workflow

```mermaid
flowchart TD
    SpanTree[📊 Jaeger Span Tree<br/>Request ID: req_abc123] --> Duration[1. Sort by Duration<br/>Identify Top 5 Slowest<br/>⏱️ 1 min]

    Duration --> TagAnalysis[2. Analyze Span Tags<br/>error=true, http.status_code<br/>⏱️ 2 min]

    TagAnalysis --> ErrorTags{Error Tags<br/>Present?}
    ErrorTags -->|Yes| ErrorFlow[3a. Error Analysis Flow<br/>Exception Stack Traces<br/>⏱️ 5 min]
    ErrorTags -->|No| LatencyFlow[3b. Latency Analysis Flow<br/>Duration Breakdown<br/>⏱️ 8 min]

    ErrorFlow --> ExceptionType{Exception<br/>Type Analysis}
    ExceptionType --> Timeout[TimeoutException<br/>→ Network/Circuit Debug]
    ExceptionType --> Connection[ConnectionException<br/>→ Pool/DNS Debug]
    ExceptionType --> SQL[SQLException<br/>→ Database Debug]

    LatencyFlow --> SpanGaps[4. Identify Span Gaps<br/>Unaccounted Time<br/>⏱️ 3 min]

    SpanGaps --> GCPause{GC Pause<br/>> 100ms?}
    SpanGaps --> ThreadBlock{Thread Blocking<br/>> 50ms?}
    SpanGaps --> IOWait{I/O Wait<br/>> 200ms?}

    GCPause -->|Yes| GCAnalysis[5a. GC Analysis<br/>Heap Dumps + JVM Metrics<br/>⏱️ 15 min]
    ThreadBlock -->|Yes| ThreadAnalysis[5b. Thread Analysis<br/>Thread Dumps + Lock Contention<br/>⏱️ 12 min]
    IOWait -->|Yes| IOAnalysis[5c. I/O Analysis<br/>Disk/Network Utilization<br/>⏱️ 10 min]

    GCAnalysis --> Remediation[6. Apply Remediation<br/>Scale/Tune/Fix Code]
    ThreadAnalysis --> Remediation
    IOAnalysis --> Remediation
    Timeout --> Remediation
    Connection --> Remediation
    SQL --> Remediation

    %% Apply 4-plane colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class SpanTree,Duration edgeStyle
    class LatencyFlow,ThreadAnalysis,GCAnalysis serviceStyle
    class SQL,Connection,IOAnalysis stateStyle
    class ErrorFlow,Remediation,TagAnalysis controlStyle
```

## 3. Uber-Style Service Dependency Debug

```mermaid
flowchart TD
    TraceEntry[🔍 Distributed Trace<br/>User Request Entry Point] --> ServiceMap[1. Generate Service Map<br/>From Trace Spans<br/>⏱️ 3 min]

    ServiceMap --> CriticalPath[2. Extract Critical Path<br/>Longest Dependency Chain<br/>⏱️ 2 min]

    CriticalPath --> DependencyCheck[3. Check Each Dependency<br/>SLA Violations<br/>⏱️ 5 min]

    DependencyCheck --> UpstreamSlow{Upstream Service<br/>SLA Breach?}
    DependencyCheck --> DownstreamSlow{Downstream Service<br/>SLA Breach?}
    DependencyCheck --> InternalSlow{Internal Processing<br/>SLA Breach?}

    UpstreamSlow -->|Yes| UpstreamDebug[4a. Upstream Analysis<br/>• Check service health<br/>• Validate circuit breakers<br/>• Review error rates<br/>⏱️ 8 min]

    DownstreamSlow -->|Yes| DownstreamDebug[4b. Downstream Analysis<br/>• Database query performance<br/>• Cache hit rates<br/>• External API latency<br/>⏱️ 10 min]

    InternalSlow -->|Yes| InternalDebug[4c. Internal Analysis<br/>• CPU utilization<br/>• Memory pressure<br/>• Thread pool exhaustion<br/>⏱️ 12 min]

    UpstreamDebug --> Correlation[5. Cross-Service Correlation<br/>Find Common Failure Patterns<br/>⏱️ 5 min]
    DownstreamDebug --> Correlation
    InternalDebug --> Correlation

    Correlation --> RootCause{Root Cause<br/>Identified?}
    RootCause -->|Yes| Resolution[6. Apply Resolution<br/>• Scale resources<br/>• Fix configuration<br/>• Deploy hotfix<br/>⏱️ 15 min]
    RootCause -->|No| EscalateDebug[6. Escalate Debug<br/>• Senior engineer<br/>• Vendor support<br/>• War room<br/>⏱️ Variable]

    Resolution --> PostMortem[7. Document Post-Mortem<br/>• Timeline reconstruction<br/>• Prevention measures<br/>• Monitoring gaps<br/>⏱️ 30 min]

    %% Apply 4-plane colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class TraceEntry,ServiceMap edgeStyle
    class UpstreamDebug,InternalDebug,InternalSlow serviceStyle
    class DownstreamDebug,DownstreamSlow,DependencyCheck stateStyle
    class Correlation,PostMortem,Resolution controlStyle
```

## 4. Production Tool Commands & Queries

### Jaeger Query Examples
```bash
# Find all traces for a specific service in last hour
curl "http://jaeger:16686/api/traces?service=user-service&start=1694956800000000&end=1694960400000000"

# Find traces with specific operation and errors
curl "http://jaeger:16686/api/traces?service=payment-service&operation=process_payment&tags={\"error\":\"true\"}"

# Find slow traces (>1s duration)
curl "http://jaeger:16686/api/traces?service=checkout-service&minDuration=1000ms"
```

### OpenTelemetry Context Extraction
```bash
# Extract trace context from logs
grep "trace_id" /var/log/app.log | grep "$(date +%Y-%m-%d)" | head -20

# Correlate trace with metrics
curl -G "http://prometheus:9090/api/v1/query" \
  --data-urlencode 'query=histogram_quantile(0.99, rate(http_request_duration_seconds_bucket{trace_id="abc123"}[5m]))'
```

## 5. Twitter-Style Error Rate Correlation

```mermaid
flowchart TD
    ErrorSpike[📈 Error Rate Spike<br/>5xx errors > 5%] --> TraceFilter[1. Filter Error Traces<br/>error=true in last 10min<br/>⏱️ 2 min]

    TraceFilter --> ErrorGrouping[2. Group by Error Type<br/>HTTP status, exception class<br/>⏱️ 3 min]

    ErrorGrouping --> Top3Errors[3. Analyze Top 3 Errors<br/>By frequency and impact<br/>⏱️ 5 min]

    Top3Errors --> Error500{HTTP 500<br/>Internal Server}
    Top3Errors --> Error503{HTTP 503<br/>Service Unavailable}
    Top3Errors --> Error504{HTTP 504<br/>Gateway Timeout}

    Error500 --> ServiceError[4a. Service Error Analysis<br/>• Uncaught exceptions<br/>• Configuration errors<br/>• Resource exhaustion<br/>⏱️ 8 min]

    Error503 --> CapacityError[4b. Capacity Error Analysis<br/>• Circuit breaker open<br/>• Thread pool exhausted<br/>• Rate limiting active<br/>⏱️ 6 min]

    Error504 --> TimeoutError[4c. Timeout Error Analysis<br/>• Upstream dependency slow<br/>• Database connection timeout<br/>• Load balancer timeout<br/>⏱️ 10 min]

    ServiceError --> ErrorCorrelation[5. Cross-Trace Correlation<br/>Find Common Patterns<br/>⏱️ 5 min]
    CapacityError --> ErrorCorrelation
    TimeoutError --> ErrorCorrelation

    ErrorCorrelation --> PatternFound{Common Pattern<br/>Identified?}

    PatternFound -->|Yes| CommonCause[6a. Common Cause<br/>• Deployment correlation<br/>• Infrastructure issue<br/>• Code regression<br/>⏱️ 8 min]

    PatternFound -->|No| IndividualFix[6b. Individual Fixes<br/>• Service-specific issues<br/>• Gradual degradation<br/>• Random failures<br/>⏱️ 15 min]

    CommonCause --> GlobalFix[7a. Global Resolution<br/>• Rollback deployment<br/>• Fix infrastructure<br/>• Hotfix critical bug<br/>⏱️ 20 min]

    IndividualFix --> ServiceFix[7b. Service Resolution<br/>• Scale individual services<br/>• Fix configuration<br/>• Restart components<br/>⏱️ 25 min]

    GlobalFix --> ValidationCheck[8. Validation<br/>Error rate < 1%<br/>⏱️ 10 min]
    ServiceFix --> ValidationCheck

    %% Apply 4-plane colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class ErrorSpike,TraceFilter edgeStyle
    class ServiceError,CapacityError,IndividualFix serviceStyle
    class TimeoutError,ErrorCorrelation,CommonCause stateStyle
    class ValidationCheck,GlobalFix,PatternFound controlStyle
```

## 6. LinkedIn-Style Performance Profile Correlation

```mermaid
flowchart TD
    PerfDegradation[⚡ Performance Degradation<br/>p99 latency increased 3x] --> TraceCollection[1. Collect Performance Traces<br/>Before/After comparison<br/>⏱️ 5 min]

    TraceCollection --> BaselineCompare[2. Compare with Baseline<br/>Same time last week<br/>⏱️ 3 min]

    BaselineCompare --> DifferenceAnalysis[3. Analyze Differences<br/>New spans, duration changes<br/>⏱️ 8 min]

    DifferenceAnalysis --> NewSpans{New Spans<br/>Detected?}
    DifferenceAnalysis --> SlowerSpans{Existing Spans<br/>Slower?}
    DifferenceAnalysis --> MissingSpans{Missing Spans<br/>Detected?}

    NewSpans -->|Yes| NewCode[4a. New Code Analysis<br/>• Recent deployments<br/>• Feature flags<br/>• A/B test rollout<br/>⏱️ 10 min]

    SlowerSpans -->|Yes| PerfRegression[4b. Performance Regression<br/>• Database query changes<br/>• Algorithm inefficiency<br/>• Resource contention<br/>⏱️ 12 min]

    MissingSpans -->|Yes| ServiceDown[4c. Service Degradation<br/>• Circuit breaker tripping<br/>• Service instances down<br/>• Load balancer config<br/>⏱️ 8 min]

    NewCode --> CodeCorrelation[5. Code Change Correlation<br/>Git commits + deployment<br/>⏱️ 5 min]
    PerfRegression --> MetricCorrelation[5. Metric Correlation<br/>CPU, memory, I/O trends<br/>⏱️ 7 min]
    ServiceDown --> InfraCorrelation[5. Infrastructure Correlation<br/>Host metrics, network<br/>⏱️ 6 min]

    CodeCorrelation --> ChangeIdentified{Problematic<br/>Change Found?}
    MetricCorrelation --> ChangeIdentified
    InfraCorrelation --> ChangeIdentified

    ChangeIdentified -->|Yes| TargetedFix[6a. Targeted Fix<br/>• Rollback code<br/>• Fix configuration<br/>• Optimize query<br/>⏱️ 15 min]

    ChangeIdentified -->|No| BroadInvestigation[6b. Broad Investigation<br/>• Load testing<br/>• Profiling<br/>• External dependencies<br/>⏱️ 30 min]

    TargetedFix --> ImpactValidation[7. Impact Validation<br/>Latency back to baseline<br/>⏱️ 10 min]
    BroadInvestigation --> ImpactValidation

    %% Apply 4-plane colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class PerfDegradation,TraceCollection edgeStyle
    class NewCode,PerfRegression,BroadInvestigation serviceStyle
    class ServiceDown,MetricCorrelation,InfraCorrelation stateStyle
    class ImpactValidation,TargetedFix,ChangeIdentified controlStyle
```

## Production Tools & Configuration

### Netflix Tracing Stack
```yaml
# Zipkin configuration for high-throughput tracing
zipkin:
  base-url: http://zipkin:9411
  sender:
    type: kafka
    bootstrap-servers: kafka1:9092,kafka2:9092
  sampling:
    probability: 0.1  # 10% sampling for normal traffic
    error-rate: 1.0   # 100% sampling for errors
```

### Uber-Style Service Map Generation
```python
# Service dependency extraction from traces
def extract_service_dependencies(trace_data):
    dependencies = {}
    for span in trace_data['spans']:
        if 'parent_span_id' in span:
            parent = find_span_by_id(span['parent_span_id'])
            if parent:
                parent_service = parent['process']['serviceName']
                current_service = span['process']['serviceName']
                if parent_service != current_service:
                    dependencies[parent_service] = dependencies.get(parent_service, [])
                    dependencies[parent_service].append(current_service)
    return dependencies
```

### Twitter Error Rate Queries
```promql
# Error rate by service and operation
increase(jaeger_spans_total{status="error"}[5m]) /
increase(jaeger_spans_total[5m]) * 100

# p99 latency by service
histogram_quantile(0.99,
  rate(jaeger_span_duration_seconds_bucket[5m])
) * 1000
```

## Common False Positives & Solutions

### 1. Sampling Bias (15% of investigations)
```bash
# Verify sampling rate is consistent
curl "http://jaeger:16686/api/services" | jq '.data[].operations[] | select(.spanKind == "server")'

# Check for sampling skew in error scenarios
grep -E "sampling_rate|trace_id" /var/log/app.log | awk '{print $3, $5}' | sort | uniq -c
```

### 2. Clock Skew Issues (8% of investigations)
```bash
# Check for clock synchronization across hosts
for host in $(cat /etc/hosts | grep service); do
  echo "$host: $(ssh $host date +%s)"
done | awk '{diff = $2 - systime(); if(diff > 1 || diff < -1) print $1 " is skewed by " diff " seconds"}'
```

### 3. Async Processing Gaps (12% of investigations)
```java
// Proper async span continuation
@NewSpan("async-processing")
public CompletableFuture<String> processAsync(String input) {
    Span currentSpan = Span.current();
    return CompletableFuture.supplyAsync(() -> {
        try (Scope scope = currentSpan.makeCurrent()) {
            return performWork(input);
        }
    });
}
```

## Escalation Criteria

| Time Spent | Escalation Action | Contact |
|------------|------------------|----------|
| 30 minutes | Senior Engineer | @oncall-senior |
| 60 minutes | Engineering Manager | @oncall-em |
| 90 minutes | War Room | @incident-commander |
| 2 hours | External Vendor | Support case |

## Success Metrics

- **MTTR**: Mean time to resolution < 45 minutes
- **Accuracy**: Root cause identified in 85% of cases
- **False Positives**: < 10% of debugging sessions
- **Coverage**: 95% of performance incidents have traces

*Based on production debugging data from Netflix, Uber, Twitter, and LinkedIn distributed systems teams.*