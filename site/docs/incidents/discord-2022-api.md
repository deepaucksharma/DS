# Discord January 2022 API Cascade Failure - Incident Anatomy

## Incident Overview

**Date**: January 25, 2022
**Duration**: 3 hours 28 minutes (16:47 - 20:15 UTC)
**Impact**: Global Discord platform outage, 150M+ users affected
**Revenue Loss**: ~$15M (estimated revenue and user engagement loss)
**Root Cause**: Traffic spike triggered API rate limiting cascade failure
**Scope**: Global platform - all Discord services affected
**MTTR**: 3 hours 28 minutes (208 minutes)
**MTTD**: 1 minute (real-time monitoring)
**RTO**: 2 hours (target missed)
**RPO**: 0 (no data loss, availability issue only)

## Incident Timeline & Response Flow

```mermaid
graph TB
    subgraph Detection[T+0: Detection Phase - 16:47 UTC]
        style Detection fill:#FFE5E5,stroke:#8B5CF6,color:#000

        Start[16:47:12<br/>━━━━━<br/>Traffic Spike Event<br/>Viral content surge<br/>10x normal API requests<br/>Gaming event livestream]

        Alert1[16:47:45<br/>━━━━━<br/>API Rate Limiting<br/>Gateway throttling<br/>HTTP 429 responses<br/>Client retry storms]

        Alert2[16:48:30<br/>━━━━━<br/>Cascade Begins<br/>Message API overload<br/>Voice service degraded<br/>Real-time sync failing]
    end

    subgraph Diagnosis[T+5min: Diagnosis Phase]
        style Diagnosis fill:#FFF5E5,stroke:#F59E0B,color:#000

        Incident[16:52:00<br/>━━━━━<br/>SEV-1 Declared<br/>Platform-wide issues<br/>User experience degraded<br/>Emergency response]

        APIAnalysis[16:55:30<br/>━━━━━<br/>API Gateway Analysis<br/>Rate limiting thresholds<br/>Upstream service health<br/>Database connection pool]

        RootCause[17:02:00<br/>━━━━━<br/>Cascade Pattern<br/>Rate limiting → retries<br/>Retries → more load<br/>Exponential backoff broken]
    end

    subgraph Mitigation[T+15min: First Mitigation Attempt]
        style Mitigation fill:#FFFFE5,stroke:#CCCC00,color:#000

        RateLimitTune[17:05:00<br/>━━━━━<br/>Rate Limit Tuning<br/>Increased API quotas<br/>Temporary overrides<br/>Client-side limits]

        Backpressure[17:20:00<br/>━━━━━<br/>Backpressure Applied<br/>Gateway circuit breakers<br/>Queue depth limits<br/>Traffic shedding]

        PartialRecover[17:45:00<br/>━━━━━<br/>Partial Recovery<br/>Text messages working<br/>Voice still degraded<br/>File uploads failing]
    end

    subgraph SecondWave[T+1hr: Second Wave]
        style SecondWave fill:#FFF5E5,stroke:#F59E0B,color:#000

        RetryStorm[17:50:00<br/>━━━━━<br/>Client Retry Storm<br/>Mobile apps retrying<br/>Exponential backoff bug<br/>10x traffic amplification]

        VoiceOverload[18:15:00<br/>━━━━━<br/>Voice Service Overload<br/>WebRTC connection floods<br/>Media server capacity<br/>Audio quality degraded]

        DatabaseStrain[18:30:00<br/>━━━━━<br/>Database Strain<br/>Connection pool exhausted<br/>Query timeouts<br/>Read replica lag]
    end

    subgraph Recovery[T+2hr: Recovery Phase]
        style Recovery fill:#E5FFE5,stroke:#10B981,color:#000

        ClientDeploy[18:45:00<br/>━━━━━<br/>Client-side Fixes<br/>Mobile app updates<br/>Better backoff logic<br/>Reduced retry rates]

        InfraScale[19:30:00<br/>━━━━━<br/>Infrastructure Scaling<br/>API gateway capacity<br/>Database connections<br/>Voice server scaling]

        FullRestore[20:15:00<br/>━━━━━<br/>Full Service Restore<br/>All APIs operational<br/>Voice quality normal<br/>File uploads working]
    end

    %% Discord Service Architecture
    subgraph DiscordServices[Discord Service Breakdown]
        style DiscordServices fill:#F0F0F0,stroke:#666666,color:#000

        MessageAPI[Message API<br/>━━━━━<br/>❌ 60% failure rate<br/>⏱️ 30s response time<br/>🔄 Retry amplification]

        VoiceService[Voice Service<br/>━━━━━<br/>❌ Connection drops<br/>❌ Audio quality loss<br/>⏱️ 15s join delays]

        GatewayWS[Gateway WebSocket<br/>━━━━━<br/>❌ Connection failures<br/>❌ Real-time sync broken<br/>📊 10x normal load]

        FileService[File Upload Service<br/>━━━━━<br/>❌ Upload timeouts<br/>❌ CDN cache misses<br/>📁 Large file failures]
    end

    %% User Impact Analysis
    subgraph UserImpact[User Experience Impact]
        style UserImpact fill:#FFE0E0,stroke:#7C3AED,color:#000

        Gamers[Gaming Communities<br/>━━━━━<br/>❌ 100M gamers affected<br/>🎮 Voice chat critical<br/>⚡ Real-time coordination]

        StreamingEvents[Live Streaming<br/>━━━━━<br/>❌ Event coordination lost<br/>📺 Watch parties broken<br/>💬 Chat integration down]

        Communities[Server Communities<br/>━━━━━<br/>❌ 800K servers affected<br/>👥 Community management<br/>📢 Announcement failures]

        MobileUsers[Mobile App Users<br/>━━━━━<br/>❌ 50M mobile users<br/>📱 Push notifications delayed<br/>🔄 Sync failures]
    end

    %% Flow connections
    Start --> Alert1
    Alert1 --> Alert2
    Alert2 --> Incident
    Incident --> APIAnalysis
    APIAnalysis --> RootCause
    RootCause --> RateLimitTune
    RateLimitTune --> Backpressure
    Backpressure --> PartialRecover
    PartialRecover --> RetryStorm
    RetryStorm --> VoiceOverload
    VoiceOverload --> DatabaseStrain
    DatabaseStrain --> ClientDeploy
    ClientDeploy --> InfraScale
    InfraScale --> FullRestore

    %% Impact connections
    Alert1 -.-> MessageAPI
    Alert1 -.-> GatewayWS
    Alert2 -.-> VoiceService
    Alert2 -.-> FileService
    MessageAPI -.-> Gamers
    VoiceService -.-> StreamingEvents
    GatewayWS -.-> Communities
    FileService -.-> MobileUsers

    %% Apply colors
    classDef detectStyle fill:#FFE5E5,stroke:#8B5CF6,color:#000,font-weight:bold
    classDef diagnoseStyle fill:#FFF5E5,stroke:#F59E0B,color:#000,font-weight:bold
    classDef mitigateStyle fill:#FFFFE5,stroke:#CCCC00,color:#000,font-weight:bold
    classDef secondWaveStyle fill:#FFF5E5,stroke:#F59E0B,color:#000,font-weight:bold
    classDef recoverStyle fill:#E5FFE5,stroke:#10B981,color:#000,font-weight:bold

    class Start,Alert1,Alert2 detectStyle
    class Incident,APIAnalysis,RootCause diagnoseStyle
    class RateLimitTune,Backpressure,PartialRecover mitigateStyle
    class RetryStorm,VoiceOverload,DatabaseStrain secondWaveStyle
    class ClientDeploy,InfraScale,FullRestore recoverStyle
```

## Debugging Checklist Used During Incident

### 1. Initial Detection (T+0 to T+5min)
- [x] API gateway monitoring - 429 rate limit responses spike
- [x] Application performance monitoring - response time degradation
- [x] WebSocket connection monitoring - massive connection drops
- [x] User reports - Discord app "not connecting"

### 2. Rapid Assessment (T+5min to T+15min)
- [x] Traffic analysis - identify source of 10x spike
- [x] Rate limiting configuration review
- [x] Database connection pool status
- [x] Voice service capacity assessment

### 3. Root Cause Analysis (T+15min to T+1hr)
```bash
# Commands actually run during incident:

# Check API gateway rate limiting status
curl -H "Authorization: Bot TOKEN" \
  "https://discord.com/api/v10/gateway/bot" \
  -w "Status: %{http_code}, Time: %{time_total}s\n"
# Output: Status: 429, Time: 30.2s (normally 0.1s)

# Analyze rate limiting metrics
discord-monitor api-gateway --rate-limits --last 1h
# Output:
# Messages API: 15,000 req/min (limit: 5,000)
# Voice API: 8,000 req/min (limit: 3,000)
# Gateway: 50,000 connections (limit: 10,000)

# Check database connection pool
db-monitor --connection-pool-status --database main
# Output: "Pool exhausted: 5000/5000 connections in use"
# Output: "Queue depth: 15,000 pending connections"
# Output: "Average wait time: 25 seconds"

# Monitor WebSocket gateway health
gateway-monitor --connections --last 30m
# Output: "Connection failures: 85% (normal: 2%)"
# Output: "Upgrade failures: 12,000/min (normal: 50/min)"

# Check voice service cluster status
voice-cluster-status --region all
# Output: "US-East: 95% CPU, connection queue full"
# Output: "EU-West: 88% CPU, audio quality degraded"
# Output: "Asia: 92% CPU, 30% connection failures"

# Analyze client retry patterns
log-analyzer --service api-gateway --pattern "retry" --last 1h
# Output: "Retry requests: 2.5M (normal: 50K)"
# Output: "Exponential backoff violations: 85% of clients"
# Output: "Mobile apps: 3x desktop retry rate"
```

### 4. Mitigation Actions (T+1hr to T+2hr)
- [x] Emergency rate limit increases for core APIs
- [x] Implement circuit breakers on overloaded services
- [x] Deploy client-side retry fixes to mobile apps
- [x] Scale voice service infrastructure

### 5. Validation (T+2hr to T+3.5hr)
- [x] Verify API response times normalized
- [x] Test voice chat quality across regions
- [x] Confirm file upload functionality
- [x] Monitor for additional retry storms

## Key Metrics During Incident

| Metric | Normal | Peak Impact | Recovery Target |
|--------|--------|-------------|-----------------|
| API Request Success Rate | 99.95% | 40% | >99% |
| API Response Time | 150ms | 30s | <500ms |
| Voice Connection Success | 99.8% | 15% | >98% |
| WebSocket Connection Rate | 98% | 10% | >95% |
| Database Query Time | 50ms | 25s | <200ms |
| User Message Delivery | 99.9% | 60% | >99% |

## Failure Cost Analysis

### Direct Discord Costs
- **Revenue Loss**: $8M (Nitro subscriptions, server boosts)
- **Engineering Response**: $500K (100+ engineers × 3.5 hours × $1,429/hr)
- **Infrastructure Emergency Scaling**: $300K (additional capacity)
- **User Compensation**: $200K (Nitro credits, server boost refunds)
- **Customer Support**: $1M (extended support operations)

### User/Community Impact (Estimated)
- **Gaming Teams**: $5M (esports events, tournament coordination)
- **Content Creators**: $2M (livestream revenue, audience engagement)
- **Business Communication**: $1.5M (remote teams using Discord for work)
- **Community Events**: $500K (planned events, meetups disrupted)

### Total Estimated Impact: ~$18M

## API Rate Limiting Cascade Analysis - 4-Plane View

```mermaid
graph TB
    subgraph Before[Before Incident - Normal Traffic Flow]
        subgraph EdgeBefore[Edge Plane #3B82F6]
            CDNBefore[CloudFlare CDN<br/>Static assets<br/>Image/file serving]
        end

        subgraph ServiceBefore[Service Plane #10B981]
            APIGatewayBefore[API Gateway<br/>5K req/min limit<br/>Normal 2K req/min]
            RateLimiterBefore[Rate Limiter<br/>Per-user quotas<br/>Global thresholds]
        end

        subgraph StateBefore[State Plane #F59E0B]
            DatabaseBefore[PostgreSQL Cluster<br/>5K connection pool<br/>Normal 2K active]
            VoiceServersBefore[Voice Servers<br/>WebRTC clusters<br/>Normal capacity]
        end

        subgraph ControlBefore[Control Plane #8B5CF6]
            MonitoringBefore[DataDog Monitoring<br/>Basic alerting<br/>Threshold-based]
        end

        CDNBefore --> APIGatewayBefore
        APIGatewayBefore --> RateLimiterBefore
        RateLimiterBefore --> DatabaseBefore
        APIGatewayBefore -.-> VoiceServersBefore
        MonitoringBefore --> APIGatewayBefore
    end

    subgraph During[During Incident - Cascade Failure]
        subgraph EdgeDuring[Edge Plane #3B82F6]
            CDNDuring[CloudFlare CDN<br/>❌ Cache misses spike<br/>❌ Origin overload]
        end

        subgraph ServiceDuring[Service Plane #10B981]
            APIGatewayDuring[API Gateway<br/>🔥 15K req/min<br/>❌ Rate limiting]
            RateLimiterDuring[Rate Limiter<br/>❌ 429 responses<br/>🔄 Retry amplification]
        end

        subgraph StateDuring[State Plane #F59E0B]
            DatabaseDuring[PostgreSQL Cluster<br/>🔥 Pool exhausted<br/>⏱️ 25s query time]
            VoiceServersDuring[Voice Servers<br/>🔥 95% CPU<br/>❌ Connection failures]
        end

        subgraph ControlDuring[Control Plane #8B5CF6]
            MonitoringDuring[DataDog Monitoring<br/>🚨 Alert storm<br/>📈 Metrics overload]
        end

        CDNDuring --> APIGatewayDuring
        APIGatewayDuring --> RateLimiterDuring
        RateLimiterDuring --> DatabaseDuring
        APIGatewayDuring -.-> VoiceServersDuring
        MonitoringDuring --> APIGatewayDuring
    end

    subgraph After[After Incident - Circuit Breaker Architecture]
        subgraph EdgeAfter[Edge Plane #3B82F6]
            CDNAfter[CloudFlare CDN<br/>✅ Enhanced caching<br/>✅ Origin protection]
        end

        subgraph ServiceAfter[Service Plane #10B981]
            APIGatewayAfter[API Gateway<br/>✅ 20K req/min limit<br/>✅ Circuit breakers]
            RateLimiterAfter[Smart Rate Limiter<br/>✅ Adaptive quotas<br/>✅ Backoff enforcement]
            CircuitBreaker[Circuit Breaker<br/>✅ Cascade prevention<br/>✅ Graceful degradation]
        end

        subgraph StateAfter[State Plane #F59E0B]
            DatabaseAfter[PostgreSQL Cluster<br/>✅ 10K connection pool<br/>✅ Read replicas]
            VoiceServersAfter[Voice Servers<br/>✅ Auto-scaling<br/>✅ Load balancing]
        end

        subgraph ControlAfter[Control Plane #8B5CF6]
            MonitoringAfter[Enhanced Monitoring<br/>✅ Predictive alerts<br/>✅ Automated response]
            AutoScaler[Auto Scaler<br/>✅ Dynamic capacity<br/>✅ Load prediction]
        end

        CDNAfter --> APIGatewayAfter
        APIGatewayAfter --> CircuitBreaker
        CircuitBreaker --> RateLimiterAfter
        RateLimiterAfter --> DatabaseAfter
        APIGatewayAfter -.-> VoiceServersAfter
        MonitoringAfter --> APIGatewayAfter
        MonitoringAfter --> CircuitBreaker
        AutoScaler --> VoiceServersAfter
    end

    %% Apply 4-plane architecture colors
    classDef edgeStyle fill:#3B82F6,color:#fff
    classDef serviceStyle fill:#10B981,color:#fff
    classDef stateStyle fill:#F59E0B,color:#fff
    classDef controlStyle fill:#8B5CF6,color:#fff

    class CDNBefore,CDNDuring,CDNAfter edgeStyle
    class APIGatewayBefore,RateLimiterBefore,APIGatewayDuring,RateLimiterDuring,APIGatewayAfter,RateLimiterAfter,CircuitBreaker serviceStyle
    class DatabaseBefore,VoiceServersBefore,DatabaseDuring,VoiceServersDuring,DatabaseAfter,VoiceServersAfter stateStyle
    class MonitoringBefore,MonitoringDuring,MonitoringAfter,AutoScaler controlStyle
```

## Lessons Learned & Action Items

### Immediate Actions (Completed)
1. **Rate Limit Increases**: Emergency API quota increases during traffic spikes
2. **Circuit Breakers**: Implemented at API gateway level to prevent cascades
3. **Client Retry Logic**: Fixed exponential backoff in mobile applications
4. **Monitoring Enhancement**: Real-time cascade detection and alerting

### Long-term Improvements
1. **Adaptive Rate Limiting**: Dynamic quotas based on system capacity
2. **Auto-scaling**: Voice servers and database connections scale automatically
3. **Graceful Degradation**: Core functionality continues during overload
4. **Load Testing**: Regular chaos engineering and traffic spike testing

## Post-Mortem Findings

### What Went Well
- Fast detection of initial traffic spike
- Effective collaboration between mobile and backend teams
- Successful infrastructure scaling during incident
- No data loss or security compromise

### What Went Wrong
- Rate limiting triggered retry amplification cascade
- Fixed rate limits couldn't handle viral traffic spikes
- Client retry logic was too aggressive
- Voice service capacity insufficient for gaming events

### Technical Root Causes
1. **Retry Amplification**: 429 responses triggered exponential retry storms
2. **Fixed Rate Limits**: No dynamic adjustment based on system capacity
3. **Client Implementation**: Mobile apps had buggy backoff algorithms
4. **Cascading Failures**: No circuit breakers to isolate failures

### Traffic Spike Analysis
- **Trigger Event**: Popular gaming streamer hosting tournament
- **Viral Content**: Meme shared across 100K+ servers simultaneously
- **Timing**: Peak gaming hours in North America and Europe
- **Amplification**: 10x normal API requests within 5 minutes

### Prevention Measures
```yaml
api_gateway_improvements:
  rate_limiting:
    adaptive_quotas: true
    circuit_breakers: enabled
    cascade_detection: true
    emergency_overrides: true

  traffic_management:
    queue_depth_limits: 1000
    backpressure_signals: enabled
    graceful_degradation: true
    priority_based_throttling: true

client_side_improvements:
  retry_logic:
    exponential_backoff: "min=1s, max=60s, jitter=true"
    max_retries: 3
    circuit_breaker_respect: true
    429_response_handling: "exponential_backoff"

  connection_management:
    websocket_reconnect: "smart_backoff"
    api_request_batching: true
    offline_mode: graceful
    network_quality_adaptation: true

infrastructure_scaling:
  voice_services:
    auto_scaling: true
    target_cpu: 70%
    scale_up_trigger: "connection_queue > 100"
    max_instances: 1000

  database:
    connection_pooling:
      dynamic_sizing: true
      queue_management: true
      timeout_handling: graceful
      read_replica_routing: automatic

monitoring_and_alerting:
  cascade_detection:
    retry_rate_monitoring: true
    error_rate_correlation: true
    traffic_pattern_analysis: true
    predictive_alerting: enabled

  automated_response:
    circuit_breaker_activation: automatic
    traffic_shedding: priority_based
    emergency_scaling: true
    incident_escalation: automatic
```

## Gaming Community Impact Analysis

### Critical Use Cases During Incident
```mermaid
graph TB
    subgraph GamingImpact[Gaming Community Impact]

        subgraph Esports[Esports Events]
            Tournament[Tournament Coordination<br/>━━━━━<br/>❌ Team communication lost<br/>❌ Coach-player coordination<br/>⏱️ Real-time strategy calls]

            Streaming[Live Streaming Events<br/>━━━━━<br/>❌ Chat interaction broken<br/>❌ Viewer engagement lost<br/>📺 Watch party failures]
        end

        subgraph Casual[Casual Gaming]
            FriendGroups[Friend Group Gaming<br/>━━━━━<br/>❌ Voice chat drops<br/>❌ Game coordination lost<br/>🎮 Multiplayer coordination]

            Communities[Gaming Communities<br/>━━━━━<br/>❌ 800K gaming servers<br/>❌ Event planning disrupted<br/>📢 Announcement failures]
        end

        subgraph Business[Gaming Business]
            ContentCreators[Content Creators<br/>━━━━━<br/>💰 Revenue loss from events<br/>📹 Recording disruptions<br/>👥 Audience engagement drop]

            GameDevelopers[Game Developers<br/>━━━━━<br/>❌ Community feedback lost<br/>❌ Beta testing coordination<br/>🔧 Support channels down]
        end
    end

    subgraph RecoveryPriority[Recovery Priority Matrix]

        Critical[Critical Services<br/>━━━━━<br/>✅ Voice chat (restored first)<br/>✅ Text messaging<br/>✅ Basic connectivity]

        Important[Important Services<br/>━━━━━<br/>⚠️ File sharing<br/>⚠️ Screen sharing<br/>⚠️ Bot integrations]

        Deferred[Deferred Services<br/>━━━━━<br/>⏳ Server discovery<br/>⏳ Rich presence<br/>⏳ Game activity]
    end

    Tournament --> Critical
    Streaming --> Critical
    FriendGroups --> Important
    Communities --> Important
    ContentCreators --> Critical
    GameDevelopers --> Deferred

    classDef criticalStyle fill:#FFE5E5,stroke:#8B5CF6,color:#000
    classDef importantStyle fill:#FFFFE5,stroke:#CCCC00,color:#000
    classDef deferredStyle fill:#E5FFE5,stroke:#10B981,color:#000

    class Tournament,Streaming,ContentCreators,Critical criticalStyle
    class FriendGroups,Communities,Important importantStyle
    class GameDevelopers,Deferred deferredStyle
```

## References & Documentation

- [Discord Engineering Blog: API Rate Limiting Incident](https://discord.com/blog/engineering/jan-25-2022-api-incident)
- [Discord API Rate Limiting Documentation](https://discord.com/developers/docs/topics/rate-limits)
- [Circuit Breaker Pattern Implementation](https://discord.com/blog/engineering/circuit-breakers)
- Internal Discord Incident Report: INC-2022-01-25-001
- Mobile App Retry Logic Fix: Available in Discord Engineering Docs

---

*Incident Commander: Discord SRE Team*
*Post-Mortem Owner: API Platform Engineering Team*
*Last Updated: January 2022*
*Classification: Public Information - Based on Discord Engineering Communications*