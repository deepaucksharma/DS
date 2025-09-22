# Reddit Failure Domains - The Incident Map

Reddit's failure domains reflect the unique challenges of community-driven platforms: coordinated attacks, vote manipulation, and the viral spread of misinformation at internet scale.

## Complete Failure Domain Map

```mermaid
graph TB
    subgraph ExternalFailures[External Attack Vectors]
        BRIGADE[Vote Brigade<br/>Coordinated Manipulation<br/>Blast Radius: Subreddit<br/>Detection: 2-5 minutes<br/>Recovery: 15-30 minutes]

        DDOS[DDoS Attack<br/>Volumetric + Application<br/>Blast Radius: All users<br/>Mitigation: <1 minute<br/>Cloudflare + Rate Limiting]

        BOT_FARM[Bot Farms<br/>Fake Account Creation<br/>Blast Radius: Vote integrity<br/>Detection: ML models<br/>Cleanup: Hours to days]

        DOXXING[Doxxing Campaign<br/>Personal Info Exposure<br/>Blast Radius: User safety<br/>Response: Manual review<br/>Legal implications]
    end

    subgraph InfraFailures[Infrastructure Failures]
        CDN_FAIL[CDN Failure<br/>Fastly Outage<br/>Blast Radius: Global<br/>Fallback: Origin servers<br/>Recovery: 5-15 minutes]

        CASSANDRA_FAIL[Cassandra Cluster Failure<br/>Comment Tree Corruption<br/>Blast Radius: Read/Write<br/>Recovery: 2-6 hours<br/>Data Loss: Minimal]

        REDIS_FAIL[Redis Cache Failure<br/>Vote Score Loss<br/>Blast Radius: Performance<br/>Recovery: 30 seconds<br/>Rebuild: 10-20 minutes]

        PG_FAIL[PostgreSQL Shard Failure<br/>User/Subreddit Metadata<br/>Blast Radius: Affected shard<br/>Failover: <2 minutes<br/>Manual intervention needed]
    end

    subgraph ApplicationFailures[Application Logic Failures]
        VOTE_BUG[Vote Counting Bug<br/>Score Calculation Error<br/>Blast Radius: All posts<br/>Detection: Monitoring<br/>Rollback: 5-15 minutes]

        SPAM_FILTER[Spam Filter Failure<br/>False Positives/Negatives<br/>Blast Radius: User experience<br/>Manual review required<br/>SLA: 2-4 hours]

        AUTOMOD_FAIL[AutoModerator Failure<br/>Rule Engine Crash<br/>Blast Radius: Moderated subs<br/>Fallback: Manual moderation<br/>Recovery: 1-2 hours]

        FEED_ALGO[Feed Algorithm Error<br/>Personalization Failure<br/>Blast Radius: User engagement<br/>Fallback: Hot sort<br/>Recovery: 30 minutes]
    end

    subgraph SocialFailures[Social Platform Failures]
        MOD_REVOLT[Moderator Revolt<br/>Mass Subreddit Shutdown<br/>Blast Radius: Major subs<br/>Resolution: Negotiations<br/>Duration: Days to weeks]

        VIRAL_MISINFO[Viral Misinformation<br/>False Information Spread<br/>Blast Radius: Public opinion<br/>Response: Content removal<br/>Time-sensitive: Minutes]

        HARASSMENT[Coordinated Harassment<br/>Targeted User Attacks<br/>Blast Radius: Individual users<br/>Response: Account suspension<br/>Legal escalation possible]

        NSFW_LEAK[NSFW Content Leak<br/>Inappropriate Content Spread<br/>Blast Radius: Brand reputation<br/>Response: Immediate removal<br/>PR management needed]
    end

    %% Attack Paths
    BRIGADE --> VOTE_BUG
    BOT_FARM --> SPAM_FILTER
    DDOS --> CDN_FAIL
    VIRAL_MISINFO --> MOD_REVOLT

    %% Cascading Failures
    CASSANDRA_FAIL --> REDIS_FAIL
    PG_FAIL --> AUTOMOD_FAIL
    CDN_FAIL --> REDIS_FAIL

    %% Recovery Dependencies
    VOTE_BUG --> CASSANDRA_FAIL
    SPAM_FILTER --> AUTOMOD_FAIL

    %% Styling
    classDef externalStyle fill:#EF4444,stroke:#DC2626,color:#fff
    classDef infraStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef appStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef socialStyle fill:#EC4899,stroke:#DB2777,color:#fff

    class BRIGADE,DDOS,BOT_FARM,DOXXING externalStyle
    class CDN_FAIL,CASSANDRA_FAIL,REDIS_FAIL,PG_FAIL infraStyle
    class VOTE_BUG,SPAM_FILTER,AUTOMOD_FAIL,FEED_ALGO appStyle
    class MOD_REVOLT,VIRAL_MISINFO,HARASSMENT,NSFW_LEAK socialStyle
```

## Vote Brigade Attack Scenarios

```mermaid
graph TB
    subgraph BrigadeLifecycle[Vote Brigade Attack Lifecycle]
        COORDINATION[Coordination Phase<br/>Discord/4chan Planning<br/>Target Selection<br/>Account Preparation<br/>Timeline: Hours to days]

        INITIAL_ATTACK[Initial Attack<br/>First Wave Voting<br/>50-200 accounts<br/>Pattern: Rapid votes<br/>Detection: 2-5 minutes]

        AMPLIFICATION[Amplification Phase<br/>Secondary Accounts<br/>500-2000 participants<br/>Cross-subreddit spread<br/>Duration: 30-120 minutes]

        DETECTION[Detection & Response<br/>ML Model Triggers<br/>Vote Pattern Analysis<br/>Shadowban Deployment<br/>Response Time: 5-15 minutes]

        CLEANUP[Cleanup Phase<br/>Vote Recomputation<br/>Account Penalties<br/>Score Restoration<br/>Duration: 15-60 minutes]
    end

    subgraph BrigadeDetection[Brigade Detection System]
        VELOCITY_SPIKE[Vote Velocity Spike<br/>Normal: 10 votes/min<br/>Brigade: 100+ votes/min<br/>Confidence: 95%<br/>Trigger: 3σ deviation]

        ACCOUNT_CLUSTERING[Account Clustering<br/>Similar Creation Times<br/>IP Address Patterns<br/>Behavioral Similarity<br/>ML Confidence: 85%]

        CROSS_PLATFORM[Cross-Platform Signals<br/>Discord Link Sharing<br/>Twitter Coordination<br/>External Traffic Spikes<br/>Correlation Analysis]

        VOTE_PATTERNS[Abnormal Vote Patterns<br/>Uniform Timing<br/>No Comment Engagement<br/>Sequential Voting<br/>Anomaly Score: >0.8]
    end

    subgraph ResponseMeasures[Automated Response Measures]
        SHADOWBAN_WAVE[Mass Shadowban<br/>Participating Accounts<br/>Votes Invalidated<br/>Users Unaware<br/>Duration: 24-72 hours]

        RATE_LIMITING[Enhanced Rate Limiting<br/>Target Subreddit<br/>Reduced Vote Velocity<br/>Temporary Measure<br/>Duration: 2-6 hours]

        SCORE_FREEZE[Score Freeze<br/>Halt Vote Processing<br/>Manual Investigation<br/>Moderator Notification<br/>Duration: 30-120 minutes]

        CONTENT_LOCK[Content Lock<br/>Disable New Comments<br/>Prevent Further Spread<br/>Moderator Override<br/>Manual Unlock Required]
    end

    COORDINATION --> INITIAL_ATTACK
    INITIAL_ATTACK --> AMPLIFICATION
    AMPLIFICATION --> DETECTION
    DETECTION --> CLEANUP

    VELOCITY_SPIKE --> SHADOWBAN_WAVE
    ACCOUNT_CLUSTERING --> RATE_LIMITING
    CROSS_PLATFORM --> SCORE_FREEZE
    VOTE_PATTERNS --> CONTENT_LOCK

    %% Styling
    classDef attackStyle fill:#EF4444,stroke:#DC2626,color:#fff
    classDef detectionStyle fill:#10B981,stroke:#047857,color:#fff
    classDef responseStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class COORDINATION,INITIAL_ATTACK,AMPLIFICATION attackStyle
    class DETECTION,CLEANUP,VELOCITY_SPIKE,ACCOUNT_CLUSTERING,CROSS_PLATFORM,VOTE_PATTERNS detectionStyle
    class SHADOWBAN_WAVE,RATE_LIMITING,SCORE_FREEZE,CONTENT_LOCK responseStyle
```

## Database Failure Scenarios

```mermaid
graph TB
    subgraph CassandraFailures[Cassandra Failure Scenarios]
        NODE_FAILURE[Single Node Failure<br/>1 of 200 nodes<br/>Blast Radius: 0.5% capacity<br/>Auto-healing: Yes<br/>Impact: Minimal]

        RACK_FAILURE[Rack Failure<br/>10-15 nodes<br/>Blast Radius: 5-7% capacity<br/>Replication Factor: 3<br/>Recovery: 30-60 minutes]

        DC_FAILURE[Datacenter Failure<br/>50-70 nodes<br/>Blast Radius: Regional users<br/>Cross-DC replication<br/>Failover: 10-15 minutes]

        SPLIT_BRAIN[Split Brain Scenario<br/>Network Partition<br/>Consistency Issues<br/>Manual Intervention<br/>Resolution: 2-6 hours]

        COMPACTION_STORM[Compaction Storm<br/>All nodes overwhelmed<br/>Read/Write degradation<br/>Load shedding required<br/>Recovery: 4-8 hours]
    end

    subgraph PostgreSQLFailures[PostgreSQL Failure Scenarios]
        PRIMARY_FAIL[Primary DB Failure<br/>User metadata shard<br/>Automatic failover<br/>Replica promotion<br/>Recovery: <2 minutes]

        REPLICATION_LAG[Replication Lag<br/>Secondary overwhelmed<br/>Read inconsistency<br/>Route to primary<br/>Performance impact]

        DEADLOCK_CASCADE[Deadlock Cascade<br/>Lock contention<br/>Transaction timeouts<br/>Connection pool exhaustion<br/>Circuit breaker trips]

        SHARD_CORRUPTION[Shard Corruption<br/>Data integrity issues<br/>Point-in-time recovery<br/>Potential data loss<br/>Recovery: 1-4 hours]
    end

    subgraph RecoveryProcedures[Recovery Procedures]
        AUTOMATED_FAILOVER[Automated Failover<br/>Health Check Monitoring<br/>Leader Election<br/>Traffic Rerouting<br/>Time: 30-90 seconds]

        MANUAL_INTERVENTION[Manual Intervention<br/>Engineer Investigation<br/>Root Cause Analysis<br/>Coordinated Recovery<br/>Time: 1-6 hours]

        DATA_RESTORATION[Data Restoration<br/>Backup Recovery<br/>Point-in-time Restore<br/>Consistency Validation<br/>Time: 2-12 hours]

        DISASTER_RECOVERY[Disaster Recovery<br/>Cross-region Failover<br/>Complete Rebuild<br/>Service Degradation<br/>Time: 6-24 hours]
    end

    %% Failure Escalation
    NODE_FAILURE --> RACK_FAILURE
    RACK_FAILURE --> DC_FAILURE
    DC_FAILURE --> SPLIT_BRAIN

    PRIMARY_FAIL --> REPLICATION_LAG
    REPLICATION_LAG --> DEADLOCK_CASCADE
    DEADLOCK_CASCADE --> SHARD_CORRUPTION

    %% Recovery Mapping
    NODE_FAILURE --> AUTOMATED_FAILOVER
    RACK_FAILURE --> AUTOMATED_FAILOVER
    DC_FAILURE --> MANUAL_INTERVENTION
    SPLIT_BRAIN --> DATA_RESTORATION
    COMPACTION_STORM --> DISASTER_RECOVERY

    %% Styling
    classDef cassandraStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef postgresStyle fill:#3B82F6,stroke:#1E40AF,color:#fff
    classDef recoveryStyle fill:#10B981,stroke:#047857,color:#fff

    class NODE_FAILURE,RACK_FAILURE,DC_FAILURE,SPLIT_BRAIN,COMPACTION_STORM cassandraStyle
    class PRIMARY_FAIL,REPLICATION_LAG,DEADLOCK_CASCADE,SHARD_CORRUPTION postgresStyle
    class AUTOMATED_FAILOVER,MANUAL_INTERVENTION,DATA_RESTORATION,DISASTER_RECOVERY recoveryStyle
```

## Social Platform Crisis Scenarios

```mermaid
graph TB
    subgraph ModeratorCrisis[Moderator Crisis Scenarios]
        API_PROTEST[API Pricing Protest<br/>Coordinated Blackout<br/>Major Subreddits Private<br/>Traffic Drop: 80%<br/>Duration: 2-14 days]

        POLICY_REVOLT[Content Policy Revolt<br/>Mass Moderator Resignation<br/>Unmoderated Content<br/>Brand Safety Issues<br/>PR Crisis Management]

        ADMIN_CONFLICT[Admin Conflict<br/>Moderator vs Staff<br/>Community vs Corporation<br/>Media Attention<br/>Executive Intervention]

        AUTOMATION_FAILURE[Moderation Automation Failure<br/>AutoModerator Down<br/>Spam Flood<br/>Human Moderator Overload<br/>Service Degradation]
    end

    subgraph ContentCrisis[Content Crisis Scenarios]
        BREAKING_NEWS[Breaking News Event<br/>Traffic Spike: 10x normal<br/>Misinformation Risk<br/>Server Overload<br/>Real-time Fact-checking]

        CELEBRITY_INCIDENT[Celebrity Incident<br/>AMA Gone Wrong<br/>Privacy Violation<br/>Legal Implications<br/>Reputation Management]

        ELECTION_INTERFERENCE[Election Interference<br/>Foreign Disinformation<br/>Coordinated Campaigns<br/>Government Scrutiny<br/>Platform Liability]

        TERRORIST_CONTENT[Terrorist Content<br/>Extremist Propaganda<br/>Violence Incitement<br/>Law Enforcement Alert<br/>Immediate Removal Required]
    end

    subgraph ResponseProtocols[Crisis Response Protocols]
        ESCALATION_MATRIX[Escalation Matrix<br/>Severity Classification<br/>Response Team Assembly<br/>Communication Plan<br/>Timeline: 15-30 minutes]

        CONTENT_REMOVAL[Mass Content Removal<br/>Automated Flagging<br/>Human Review Queue<br/>False Positive Risk<br/>Appeal Process]

        COMMUNITY_COMMUNICATION[Community Communication<br/>Transparency Report<br/>Moderator Briefing<br/>User Notification<br/>Media Response]

        LEGAL_COMPLIANCE[Legal Compliance<br/>Law Enforcement Cooperation<br/>Government Requests<br/>International Jurisdiction<br/>Privacy Protection]
    end

    %% Crisis Evolution
    API_PROTEST --> POLICY_REVOLT
    POLICY_REVOLT --> ADMIN_CONFLICT
    BREAKING_NEWS --> CELEBRITY_INCIDENT
    CELEBRITY_INCIDENT --> ELECTION_INTERFERENCE

    %% Response Mapping
    API_PROTEST --> ESCALATION_MATRIX
    BREAKING_NEWS --> CONTENT_REMOVAL
    ELECTION_INTERFERENCE --> COMMUNITY_COMMUNICATION
    TERRORIST_CONTENT --> LEGAL_COMPLIANCE

    %% Cross-domain Impact
    AUTOMATION_FAILURE --> BREAKING_NEWS
    ADMIN_CONFLICT --> ELECTION_INTERFERENCE

    %% Styling
    classDef moderatorStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef contentStyle fill:#EF4444,stroke:#DC2626,color:#fff
    classDef responseStyle fill:#10B981,stroke:#047857,color:#fff

    class API_PROTEST,POLICY_REVOLT,ADMIN_CONFLICT,AUTOMATION_FAILURE moderatorStyle
    class BREAKING_NEWS,CELEBRITY_INCIDENT,ELECTION_INTERFERENCE,TERRORIST_CONTENT contentStyle
    class ESCALATION_MATRIX,CONTENT_REMOVAL,COMMUNITY_COMMUNICATION,LEGAL_COMPLIANCE responseStyle
```

## Historical Failure Analysis

## Major Incidents & Lessons Learned

### 2023 API Pricing Protest
- **Trigger**: API pricing changes affecting third-party apps
- **Impact**: 8,000+ subreddits went private, 90% traffic drop
- **Duration**: 14 days of coordinated blackout
- **Resolution**: Policy modifications, improved communication
- **Lessons**: Community governance essential, API strategy alignment

### 2021 WallStreetBets GME Incident
- **Trigger**: GameStop stock manipulation coordination
- **Impact**: 10x traffic surge, media attention, regulatory scrutiny
- **Technical**: Cassandra overload, vote manipulation detection failure
- **Resolution**: Enhanced monitoring, content policies
- **Lessons**: Financial content requires special handling

### 2020 Election Misinformation
- **Trigger**: Coordinated disinformation campaigns
- **Impact**: Democratic process integrity concerns
- **Response**: Real-time fact-checking, account suspensions
- **Result**: Improved ML detection, human review capacity
- **Lessons**: Political content needs proactive monitoring

### 2019 Christchurch Shooting
- **Trigger**: Live-streamed terrorist attack content sharing
- **Impact**: Global platform responsibility questions
- **Response**: Immediate content removal, law enforcement cooperation
- **Timeline**: <30 minutes detection and removal
- **Lessons**: Crisis response protocols essential

## Failure Domain Metrics

| Failure Type | MTTR | MTBF | Blast Radius | Cost Impact |
|--------------|------|------|--------------|-------------|
| **Vote Brigade** | 15 min | 2-3/week | Single post/subreddit | $50K reputation |
| **Cassandra Node** | 30 min | 1/month | 0.5% capacity | $25K/hour |
| **PostgreSQL Shard** | 2 min | 1/quarter | Affected users | $100K/hour |
| **CDN Failure** | 10 min | 1/year | Global | $500K/hour |
| **Moderator Crisis** | 2-14 days | 1/year | Major subreddits | $10M+ brand |
| **Content Crisis** | 30 min | 1/month | Public perception | $1M+ legal/PR |

## Prevention & Mitigation

### Technical Defenses
- **Rate Limiting**: Per-user, per-IP, per-subreddit quotas
- **ML Detection**: Real-time anomaly detection for voting patterns
- **Circuit Breakers**: Automatic service protection during overload
- **Chaos Engineering**: Regular failure injection testing

### Social Defenses
- **Community Guidelines**: Clear content policies with examples
- **Moderator Training**: Crisis response procedures and escalation
- **Transparency Reports**: Regular communication about enforcement
- **Appeal Processes**: Fair review system for moderation decisions

### Operational Defenses
- **24/7 Monitoring**: Real-time alerting for all failure domains
- **Incident Response**: Practiced runbooks for common scenarios
- **Crisis Communication**: Pre-approved templates for fast response
- **Legal Preparedness**: Relationships with law enforcement agencies

Reddit's failure domains uniquely combine technical infrastructure challenges with social platform responsibilities, requiring both robust engineering and nuanced community management at global scale.