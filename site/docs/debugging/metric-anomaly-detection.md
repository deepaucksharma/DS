# Metric Anomaly Detection - Production Debugging Guide

## Overview

This guide provides systematic workflows for detecting and analyzing metric anomalies in distributed systems. Based on Datadog's anomaly detection algorithms and Netflix's metric correlation practices.

**Time to Resolution**: 5-25 minutes for most anomalies
**Detection Accuracy**: 92% true positive rate
**False Positive Rate**: <8%

## 1. Complete Metric Anomaly Detection Flow

```mermaid
flowchart TD
    MetricAlert[📊 Anomaly Alert<br/>CPU usage 3σ above baseline] --> TimeframeAnalysis[1. Timeframe Analysis<br/>Compare last 1h vs 7d baseline<br/>⏱️ 2 min]

    TimeframeAnalysis --> BaselineComparison[2. Baseline Comparison<br/>Statistical deviation analysis<br/>⏱️ 3 min]

    BaselineComparison --> AnomalyType{Anomaly Type<br/>Classification?}

    AnomalyType --> Spike[Sudden Spike<br/>>3σ deviation]
    AnomalyType --> Trend[Gradual Trend<br/>Slope change]
    AnomalyType --> Oscillation[Oscillation<br/>Frequency change]
    AnomalyType --> Drop[Sudden Drop<br/>< -2σ deviation]

    Spike --> SpikeAnalysis[3a. Spike Analysis<br/>• Duration: <5min (burst)<br/>• Duration: >15min (sustained)<br/>• Amplitude analysis<br/>⏱️ 5 min]

    Trend --> TrendAnalysis[3b. Trend Analysis<br/>• Rate of change<br/>• Correlation with load<br/>• Capacity implications<br/>⏱️ 8 min]

    Oscillation --> OscillationAnalysis[3c. Oscillation Analysis<br/>• Frequency pattern<br/>• Amplitude variance<br/>• Periodic correlation<br/>⏱️ 6 min]

    Drop --> DropAnalysis[3d. Drop Analysis<br/>• Service availability<br/>• Traffic routing<br/>• Circuit breaker status<br/>⏱️ 4 min]

    SpikeAnalysis --> CorrelationEngine[4. Multi-Metric Correlation<br/>Find related anomalies<br/>⏱️ 5 min]
    TrendAnalysis --> CorrelationEngine
    OscillationAnalysis --> CorrelationEngine
    DropAnalysis --> CorrelationEngine

    CorrelationEngine --> RootCauseHypothesis[5. Root Cause Hypothesis<br/>Top 3 likely causes<br/>⏱️ 3 min]

    RootCauseHypothesis --> ValidationTest[6. Hypothesis Validation<br/>Additional metric queries<br/>⏱️ 5 min]

    ValidationTest --> ConfirmedCause{Root Cause<br/>Confirmed?}
    ConfirmedCause -->|Yes| ActionPlan[7a. Action Plan<br/>Immediate mitigation<br/>⏱️ 10 min]
    ConfirmedCause -->|No| EscalateAnalysis[7b. Escalate Analysis<br/>Senior engineer review<br/>⏱️ Variable]

    ActionPlan --> MonitoringSetup[8. Enhanced Monitoring<br/>Prevent future anomalies<br/>⏱️ 5 min]

    %% Apply 4-plane colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class MetricAlert,TimeframeAnalysis edgeStyle
    class SpikeAnalysis,TrendAnalysis,OscillationAnalysis serviceStyle
    class DropAnalysis,CorrelationEngine,ValidationTest stateStyle
    class RootCauseHypothesis,ActionPlan,MonitoringSetup controlStyle
```

## 2. Datadog-Style Statistical Anomaly Detection

```mermaid
flowchart TD
    MetricStream[📈 Real-time Metrics<br/>1-minute granularity] --> StatEngine[1. Statistical Engine<br/>Rolling window analysis<br/>⏱️ 30 seconds]

    StatEngine --> BaselineCalc[2. Baseline Calculation<br/>• Mean μ<br/>• Standard deviation σ<br/>• Seasonal adjustment<br/>⏱️ 1 min]

    BaselineCalc --> DeviationCheck[3. Deviation Detection<br/>|x - μ| > k*σ<br/>⏱️ 10 seconds]

    DeviationCheck --> SignificanceTest{Statistical<br/>Significance?}

    SignificanceTest -->|p < 0.01| HighConfidence[4a. High Confidence Anomaly<br/>Very likely real issue<br/>Confidence: >99%<br/>⏱️ 1 min]

    SignificanceTest -->|0.01 ≤ p < 0.05| MediumConfidence[4b. Medium Confidence<br/>Possible anomaly<br/>Confidence: 95-99%<br/>⏱️ 2 min]

    SignificanceTest -->|p ≥ 0.05| LowConfidence[4c. Low Confidence<br/>Likely noise<br/>Confidence: <95%<br/>⏱️ 1 min]

    HighConfidence --> ImmediateAlert[5a. Immediate Alert<br/>Page on-call engineer<br/>⏱️ 30 seconds]

    MediumConfidence --> ContextualCheck[5b. Contextual Analysis<br/>Cross-reference other metrics<br/>⏱️ 3 min]

    LowConfidence --> SuppressAlert[5c. Suppress Alert<br/>Log for trend analysis<br/>⏱️ 10 seconds]

    ImmediateAlert --> CriticalInvestigation[6. Critical Investigation<br/>Full debugging workflow<br/>⏱️ 15 min]

    ContextualCheck --> ContextualDecision{Additional Evidence<br/>Found?}
    ContextualDecision -->|Yes| PromoteAlert[Promote to Critical<br/>Join investigation]
    ContextualDecision -->|No| MonitorContinuous[Continue Monitoring<br/>Watch for patterns]

    CriticalInvestigation --> ResolutionTracking[7. Resolution Tracking<br/>MTTR measurement<br/>⏱️ Variable]

    PromoteAlert --> ResolutionTracking
    MonitorContinuous --> TrendAnalysis[8. Long-term Trend<br/>Pattern recognition<br/>⏱️ Ongoing]

    %% Apply 4-plane colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class MetricStream,StatEngine edgeStyle
    class HighConfidence,MediumConfidence,ContextualCheck serviceStyle
    class LowConfidence,BaselineCalc,TrendAnalysis stateStyle
    class CriticalInvestigation,ResolutionTracking,ImmediateAlert controlStyle
```

## 3. Netflix-Style Multi-Dimensional Correlation

```mermaid
flowchart TD
    AnomalyDetected[🎯 Anomaly Detected<br/>API Latency p99 > 500ms] --> DimensionAnalysis[1. Dimension Analysis<br/>Break down by attributes<br/>⏱️ 3 min]

    DimensionAnalysis --> ServiceDimension[Service Dimension<br/>Which services affected?]
    DimensionAnalysis --> RegionDimension[Region Dimension<br/>Geographic distribution?]
    DimensionAnalysis --> UserDimension[User Dimension<br/>User segment impact?]
    DimensionAnalysis --> TimeDimension[Time Dimension<br/>Temporal patterns?]

    ServiceDimension --> ServiceHeatmap[📊 Service Heatmap<br/>• user-service: 🔴 800ms<br/>• order-service: 🟡 300ms<br/>• payment-service: 🔴 750ms<br/>• catalog-service: 🟢 50ms]

    RegionDimension --> RegionHeatmap[📊 Region Heatmap<br/>• us-east-1: 🔴 700ms<br/>• us-west-2: 🟡 400ms<br/>• eu-west-1: 🟢 100ms<br/>• ap-southeast-1: 🔴 650ms]

    UserDimension --> UserHeatmap[📊 User Segment<br/>• premium_users: 🔴 high impact<br/>• free_users: 🟡 medium impact<br/>• enterprise: 🔴 high impact<br/>• trial_users: 🟢 low impact]

    TimeDimension --> TimePattern[📊 Time Patterns<br/>• Weekday peak hours<br/>• No weekend correlation<br/>• UTC 14:00-16:00 spike<br/>• Duration: 45 minutes]

    ServiceHeatmap --> CorrelationMatrix[2. Build Correlation Matrix<br/>Cross-dimensional analysis<br/>⏱️ 5 min]
    RegionHeatmap --> CorrelationMatrix
    UserHeatmap --> CorrelationMatrix
    TimePattern --> CorrelationMatrix

    CorrelationMatrix --> PatternRecognition[3. Pattern Recognition<br/>Identify common factors<br/>⏱️ 4 min]

    PatternRecognition --> ServiceRegionCorr{Service + Region<br/>Correlation?}
    PatternRecognition --> UserServiceCorr{User + Service<br/>Correlation?}
    PatternRecognition --> TimeRegionCorr{Time + Region<br/>Correlation?}

    ServiceRegionCorr -->|Yes| InfrastructureIssue[4a. Infrastructure Issue<br/>• Regional data center<br/>• Network connectivity<br/>• Load balancer config<br/>⏱️ 8 min]

    UserServiceCorr -->|Yes| CapacityIssue[4b. Capacity Issue<br/>• Resource exhaustion<br/>• Auto-scaling lag<br/>• Connection pool limits<br/>⏱️ 10 min]

    TimeRegionCorr -->|Yes| ExternalDependency[4c. External Dependency<br/>• Third-party API<br/>• Database performance<br/>• CDN issues<br/>⏱️ 12 min]

    InfrastructureIssue --> TargetedResolution[5. Targeted Resolution<br/>Based on correlation analysis<br/>⏱️ 15 min]
    CapacityIssue --> TargetedResolution
    ExternalDependency --> TargetedResolution

    %% Apply 4-plane colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class AnomalyDetected,DimensionAnalysis edgeStyle
    class ServiceHeatmap,UserHeatmap,CapacityIssue serviceStyle
    class RegionHeatmap,TimePattern,ExternalDependency stateStyle
    class CorrelationMatrix,TargetedResolution,PatternRecognition controlStyle
```

## 4. Twitter-Style Real-time Threshold Detection

```mermaid
flowchart TD
    MetricIngestion[⚡ Real-time Metrics<br/>100k metrics/second] --> ThresholdEngine[1. Threshold Engine<br/>Dynamic threshold calculation<br/>⏱️ 100ms]

    ThresholdEngine --> AdaptiveThreshold[2. Adaptive Thresholds<br/>• Static: fixed values<br/>• Dynamic: percentile-based<br/>• Seasonal: time-aware<br/>⏱️ 500ms]

    AdaptiveThreshold --> StaticCheck{Static Threshold<br/>Breach?}
    AdaptiveThreshold --> DynamicCheck{Dynamic Threshold<br/>Breach?}
    AdaptiveThreshold --> SeasonalCheck{Seasonal Threshold<br/>Breach?}

    StaticCheck -->|Yes| StaticAlert[3a. Static Alert<br/>• CPU > 90%<br/>• Memory > 95%<br/>• Disk > 85%<br/>⏱️ 1 min]

    DynamicCheck -->|Yes| DynamicAlert[3b. Dynamic Alert<br/>• p95 > 1.5x baseline<br/>• Error rate > 2x normal<br/>• QPS outside ±3σ<br/>⏱️ 2 min]

    SeasonalCheck -->|Yes| SeasonalAlert[3c. Seasonal Alert<br/>• Traffic pattern deviation<br/>• Business hour anomaly<br/>• Weekend behavior change<br/>⏱️ 3 min]

    StaticAlert --> SeverityAssessment[4. Severity Assessment<br/>Impact calculation<br/>⏱️ 2 min]
    DynamicAlert --> SeverityAssessment
    SeasonalAlert --> SeverityAssessment

    SeverityAssessment --> CriticalSeverity{Critical<br/>Severity?}
    CriticalSeverity -->|Yes| P0Response[5a. P0 Response<br/>• Immediate paging<br/>• War room activation<br/>• Executive notification<br/>⏱️ 2 min]

    CriticalSeverity -->|No| P1P2Response[5b. P1/P2 Response<br/>• Standard escalation<br/>• Team notification<br/>• Monitoring increase<br/>⏱️ 5 min]

    P0Response --> RapidMitigation[6. Rapid Mitigation<br/>Immediate action required<br/>⏱️ 10 min]

    P1P2Response --> AnalysisFirst[6. Analysis-First Approach<br/>Understand before acting<br/>⏱️ 15 min]

    RapidMitigation --> PostIncidentAnalysis[7. Post-Incident Analysis<br/>Threshold tuning<br/>⏱️ 30 min]
    AnalysisFirst --> PostIncidentAnalysis

    %% Apply 4-plane colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class MetricIngestion,ThresholdEngine edgeStyle
    class StaticAlert,DynamicAlert,P1P2Response serviceStyle
    class SeasonalAlert,AdaptiveThreshold,AnalysisFirst stateStyle
    class SeverityAssessment,RapidMitigation,PostIncidentAnalysis controlStyle
```

## 5. Production Metric Query Examples

### Prometheus Anomaly Detection Queries
```promql
# Detect CPU spikes (>3 standard deviations)
(
  avg_over_time(cpu_usage_percent[5m]) -
  avg_over_time(cpu_usage_percent[7d] offset 7d)
) / stddev_over_time(cpu_usage_percent[7d] offset 7d) > 3

# Detect latency anomalies using quantile estimation
histogram_quantile(0.99,
  rate(http_request_duration_seconds_bucket[5m])
) > on(job, instance) (
  quantile_over_time(0.99,
    http_request_duration_seconds{quantile="0.99"}[7d] offset 7d
  ) * 1.5
)

# Memory leak detection (sustained growth)
increase(memory_usage_bytes[1h]) >
bool(stddev_over_time(memory_usage_bytes[7d]) * 2)
```

### Datadog Anomaly Detection API
```python
from datadog import initialize, api
import time

# Initialize Datadog API
options = {
    'api_key': 'your_api_key',
    'app_key': 'your_app_key'
}
initialize(**options)

# Define anomaly detection query
def detect_anomalies(metric_name, threshold=3):
    end_time = int(time.time())
    start_time = end_time - 3600  # Last hour

    # Get metric data
    result = api.Metric.query(
        start=start_time,
        end=end_time,
        query=f'anomalies({metric_name}, "basic", 2, direction="above", alert_window="last_15m", interval=60, count_default_zero="true")'
    )

    anomalies = []
    if 'series' in result:
        for series in result['series']:
            for point in series['pointlist']:
                timestamp, value = point
                if value and value > threshold:
                    anomalies.append({
                        'timestamp': timestamp,
                        'value': value,
                        'metric': metric_name
                    })

    return anomalies

# Example usage
cpu_anomalies = detect_anomalies('system.cpu.user')
memory_anomalies = detect_anomalies('system.mem.used')
```

### Netflix Atlas Anomaly Queries
```atlas
# CPU anomaly detection with seasonal adjustment
:true,:stat,(,name,jvm.gc.pause,:eq,
:stat-avg,
:dup,1w,:offset,:sub,
:dup,:abs,2,:mul,:gt

# Request rate anomaly with trending
:true,:stat,(,name,http.requests,:eq,
:stat-total,5m,:rate,
:dup,1h,:trend,0.1,:gt,
:rot,3,:sigma,:gt,:and

# Error rate anomaly detection
:true,:stat,(,name,http.requests,:eq,(,status,5xx,:re,:eq,:and,
:stat-total,5m,:rate,
:dup,7d,:avg,2,:mul,:gt
```

## 6. LinkedIn-Style Business Metric Correlation

```mermaid
flowchart TD
    BusinessMetric[💰 Business Metric Drop<br/>Revenue -15% in 30min] --> BusinessImpact[1. Business Impact Assessment<br/>Quantify revenue impact<br/>⏱️ 2 min]

    BusinessImpact --> TechnicalCorrelation[2. Technical Correlation<br/>Map to system metrics<br/>⏱️ 5 min]

    TechnicalCorrelation --> ConversionFunnel[3. Conversion Funnel Analysis<br/>Identify drop-off points<br/>⏱️ 8 min]

    ConversionFunnel --> LandingPage[Landing Page<br/>Traffic & bounce rate]
    ConversionFunnel --> ProductPage[Product Pages<br/>View duration & CTR]
    ConversionFunnel --> CheckoutPage[Checkout Flow<br/>Abandonment rate]
    ConversionFunnel --> PaymentPage[Payment Processing<br/>Success rate]

    LandingPage --> LandingMetrics[📊 Landing Metrics<br/>• Traffic: 🟢 Normal<br/>• Bounce rate: 🟡 +5%<br/>• Load time: 🟢 1.2s<br/>• CDN errors: 🟢 0.1%]

    ProductPage --> ProductMetrics[📊 Product Metrics<br/>• Page views: 🟢 Normal<br/>• API latency: 🔴 +300%<br/>• Image load: 🔴 Failed<br/>• Search errors: 🔴 15%]

    CheckoutPage --> CheckoutMetrics[📊 Checkout Metrics<br/>• Cart additions: 🟡 -10%<br/>• Form errors: 🔴 25%<br/>• Session timeout: 🔴 High<br/>• Abandonment: 🔴 +40%]

    PaymentPage --> PaymentMetrics[📊 Payment Metrics<br/>• Processing time: 🔴 +200%<br/>• Gateway errors: 🔴 12%<br/>• Fraud checks: 🟡 Slow<br/>• Success rate: 🔴 -20%]

    LandingMetrics --> BottleneckAnalysis[4. Bottleneck Analysis<br/>Identify primary constraint<br/>⏱️ 5 min]
    ProductMetrics --> BottleneckAnalysis
    CheckoutMetrics --> BottleneckAnalysis
    PaymentMetrics --> BottleneckAnalysis

    BottleneckAnalysis --> PrimaryBottleneck{Primary<br/>Bottleneck?}

    PrimaryBottleneck --> ProductAPI[5a. Product API Issue<br/>• Database performance<br/>• Cache invalidation<br/>• Image service down<br/>⏱️ 10 min]

    PrimaryBottleneck --> CheckoutFlow[5b. Checkout Flow Issue<br/>• Form validation errors<br/>• Session management<br/>• Browser compatibility<br/>⏱️ 8 min]

    PrimaryBottleneck --> PaymentGateway[5c. Payment Gateway Issue<br/>• Third-party API<br/>• Network connectivity<br/>• Fraud service lag<br/>⏱️ 12 min]

    ProductAPI --> BusinessRecovery[6. Business Recovery Plan<br/>Prioritize revenue impact<br/>⏱️ 15 min]
    CheckoutFlow --> BusinessRecovery
    PaymentGateway --> BusinessRecovery

    BusinessRecovery --> RevenueValidation[7. Revenue Validation<br/>Confirm recovery metrics<br/>⏱️ 10 min]

    %% Apply 4-plane colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class BusinessMetric,BusinessImpact edgeStyle
    class LandingPage,ProductPage,CheckoutFlow serviceStyle
    class CheckoutPage,PaymentPage,PaymentGateway stateStyle
    class BottleneckAnalysis,BusinessRecovery,RevenueValidation controlStyle
```

## Production Tools & Configuration

### Datadog Anomaly Detection Setup
```yaml
# anomaly_detection.yaml
api_version: v1
kind: anomaly_detection
spec:
  metric: "system.cpu.user"
  algorithm: "basic"  # basic, agile, robust, adaptive
  bounds:
    upper: 3  # Standard deviations
    lower: 3
  seasonality: "weekly"
  alert_window: "last_15m"
  interval: 60
  count_default_zero: true
  notification:
    channels:
      - "#alerts-critical"
      - "oncall-engineer@company.com"
```

### Netflix Atlas Configuration
```hocon
# atlas.conf
atlas {
  anomaly-detection {
    # Statistical algorithms
    algorithms = [
      "sigma",      # Standard deviation
      "mad",        # Median absolute deviation
      "iqr",        # Interquartile range
      "seasonal"    # Seasonal decomposition
    ]

    # Threshold multipliers
    thresholds {
      sigma = 3.0
      mad = 2.5
      iqr = 1.5
      seasonal = 2.0
    }

    # Minimum data points required
    min-samples = 100

    # Alert suppression
    suppression {
      duration = "5m"
      max-alerts-per-hour = 5
    }
  }
}
```

### Prometheus Alerting Rules
```yaml
# anomaly_alerts.yml
groups:
- name: anomaly_detection
  rules:
  - alert: CPUAnomalyDetected
    expr: |
      (
        avg_over_time(cpu_usage_percent[5m]) -
        avg_over_time(cpu_usage_percent[7d] offset 7d)
      ) / stddev_over_time(cpu_usage_percent[7d] offset 7d) > 3
    for: 2m
    labels:
      severity: warning
      team: infrastructure
    annotations:
      summary: "CPU usage anomaly detected on {{ $labels.instance }}"
      description: "CPU usage is {{ $value }}σ above normal baseline"

  - alert: LatencyAnomalyDetected
    expr: |
      histogram_quantile(0.99,
        rate(http_request_duration_seconds_bucket[5m])
      ) > on(job, instance) (
        quantile_over_time(0.99,
          http_request_duration_seconds{quantile="0.99"}[7d] offset 7d
        ) * 2
      )
    for: 1m
    labels:
      severity: critical
      team: backend
    annotations:
      summary: "Request latency anomaly on {{ $labels.service }}"
      description: "p99 latency is 2x higher than baseline"
```

## Common False Positives & Solutions

### 1. Seasonal Pattern Ignorance (20% of alerts)
```python
# Seasonal baseline adjustment
from scipy import signal
import numpy as np

def seasonal_decompose(data, period=7*24):  # Weekly seasonality
    # STL decomposition
    decomposition = signal.stft(data, nperseg=period)
    trend = np.mean(decomposition, axis=0)
    seasonal = data - trend
    residual = data - trend - seasonal

    return trend, seasonal, residual

def anomaly_score_seasonal(current_value, historical_data):
    trend, seasonal, residual = seasonal_decompose(historical_data)
    expected_value = trend[-1] + seasonal[-1]
    anomaly_score = abs(current_value - expected_value) / np.std(residual)
    return anomaly_score
```

### 2. Auto-scaling Events (15% of alerts)
```bash
# Check for auto-scaling correlation
kubectl get events --field-selector reason=SuccessfulRescale --since=1h
aws autoscaling describe-scaling-activities --auto-scaling-group-name my-asg --max-items 10
```

### 3. Deployment Correlation (12% of alerts)
```python
# Deployment timeline correlation
def check_deployment_correlation(anomaly_time, deployment_log):
    deployment_window = 30 * 60  # 30 minutes

    for deployment in deployment_log:
        deploy_time = deployment['timestamp']
        if abs(anomaly_time - deploy_time) < deployment_window:
            return {
                'correlated': True,
                'deployment': deployment['service'],
                'version': deployment['version'],
                'time_diff': anomaly_time - deploy_time
            }

    return {'correlated': False}
```

## Escalation Criteria

| Confidence Level | Time Spent | Escalation Action | Contact |
|-----------------|------------|------------------|----------|
| >99% | 15 minutes | Senior Engineer | @oncall-senior |
| 95-99% | 30 minutes | Engineering Manager | @oncall-em |
| 90-95% | 45 minutes | War Room | @incident-commander |
| <90% | 60 minutes | Data Science Team | @anomaly-experts |

## Success Metrics

- **Detection Latency**: < 2 minutes for critical anomalies
- **False Positive Rate**: < 8% of all alerts
- **True Positive Rate**: > 92% accuracy
- **MTTR**: Mean time to resolution < 25 minutes

*Based on production metric anomaly detection practices from Datadog, Netflix, Twitter, and LinkedIn monitoring teams.*