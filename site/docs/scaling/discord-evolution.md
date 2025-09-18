# Discord Scale Evolution: From 10 Gamers to 600M Users in 8 Years

## Executive Summary
Discord scaled from 10 friends gaming together (2015) to 600M users (2024) by reimagining infrastructure at each 10x growth phase. This is the story of scaling real-time voice/text to billions of messages daily.

## Phase 1: The Garage Startup (2015)
**Scale**: 10-1,000 users | **Cost**: $99/month

```mermaid
graph TB
    subgraph "MVP Architecture - 10 Users"
        subgraph EdgePlane[Edge - Single Server]
            NGINX[Nginx<br/>1 VPS<br/>$20/month]
        end

        subgraph ServicePlane[Service - Monolith]
            APP[Python App<br/>Flask + Socket.io<br/>1 core, 2GB RAM]
        end

        subgraph StatePlane[State - Simple Storage]
            PG[PostgreSQL<br/>10GB<br/>$20/month]
            REDIS[Redis<br/>1GB<br/>In-memory]
        end

        NGINX --> APP
        APP --> PG
        APP --> REDIS
    end

    %% Apply four-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class NGINX edgeStyle
    class APP serviceStyle
    class PG,REDIS stateStyle
```

**Technical Decisions**:
```python
# Original Discord MVP (2015)
class DiscordMVP:
    def __init__(self):
        self.stack = {
            "language": "Python",  # Founder's expertise
            "framework": "Flask + Socket.io",
            "database": "PostgreSQL",
            "voice": "WebRTC peer-to-peer",
            "hosting": "Single DigitalOcean droplet"
        }

    def handle_message(self, channel_id, message):
        # Simple approach - worked for 10 users
        self.postgres.insert(message)
        self.socketio.emit(f'channel:{channel_id}', message)
        # Latency: 50ms, perfectly fine for 10 users
```

## Phase 2: First Growth Spurt (2016)
**Scale**: 1K-100K users | **Cost**: $5K/month

```mermaid
graph TB
    subgraph "Growing Pains Architecture"
        subgraph EdgePlane[Edge - Load Balanced]
            CF[CloudFlare<br/>Free tier]
            LB[HAProxy<br/>2 instances]
        end

        subgraph ServicePlane[Service - Split Services]
            API[REST API<br/>4 instances<br/>Python]
            WS[WebSocket<br/>4 instances<br/>Erlang]
            VOICE[Voice Server<br/>2 instances<br/>C++]
        end

        subgraph StatePlane[State - Scaled Storage]
            PG2[PostgreSQL<br/>Primary + Replica<br/>100GB]
            REDIS2[Redis Cluster<br/>16GB RAM]
            CASSANDRA[Cassandra<br/>3 nodes<br/>Messages]
        end

        CF --> LB
        LB --> API
        LB --> WS
        API --> PG2
        WS --> REDIS2
        WS --> CASSANDRA
    end

    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class CF,LB edgeStyle
    class API,WS,VOICE serviceStyle
    class PG2,REDIS2,CASSANDRA stateStyle
```

**Key Learning**: Python couldn't handle 100K concurrent WebSockets
```python
# The Python WebSocket problem
python_limitations = {
    "gil_issues": "Global Interpreter Lock killed concurrency",
    "memory_per_connection": "50KB per WebSocket",
    "100k_connections": "5GB RAM just for connections!",
    "cpu_usage": "100% CPU at 10K connections"
}

# Solution: Switched to Erlang/Elixir
elixir_benefits = {
    "memory_per_connection": "2KB per WebSocket",  # 25x improvement
    "100k_connections": "200MB RAM",
    "cpu_usage": "10% CPU at 100K connections",
    "actor_model": "Perfect for millions of concurrent users"
}
```

## Phase 3: The Erlang Rewrite (2017)
**Scale**: 100K-10M users | **Cost**: $50K/month

```mermaid
graph TB
    subgraph "Elixir-Powered Architecture"
        subgraph EdgePlane[Edge - Global CDN]
            CDN[CloudFlare<br/>Pro $200/mo]
            LB3[AWS ALB<br/>Multi-region]
        end

        subgraph ServicePlane[Service - Microservices]
            GATEWAY[API Gateway<br/>10 nodes<br/>Elixir]
            GUILD[Guild Service<br/>20 nodes<br/>Elixir]
            PRESENCE[Presence Service<br/>30 nodes<br/>Elixir]
            VOICE2[Voice Service<br/>50 nodes<br/>Rust]
        end

        subgraph StatePlane[State - Distributed Storage]
            SCYLLA[ScyllaDB<br/>20 nodes<br/>2B messages/day]
            REDIS3[Redis<br/>100GB<br/>Sessions]
            PG3[PostgreSQL<br/>10TB<br/>Metadata]
        end

        CDN --> LB3
        LB3 --> GATEWAY
        GATEWAY --> GUILD
        GATEWAY --> PRESENCE
        GUILD --> SCYLLA
        PRESENCE --> REDIS3
        GUILD --> PG3
    end

    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class CDN,LB3 edgeStyle
    class GATEWAY,GUILD,PRESENCE,VOICE2 serviceStyle
    class SCYLLA,REDIS3,PG3 stateStyle
```

**The Erlang/Elixir Advantage**:
```elixir
# Discord's Guild (Server) GenServer
defmodule Discord.Guild do
  use GenServer

  # Each guild is an isolated process
  def handle_cast({:message, message}, state) do
    # Broadcast to all online members (could be 100K+)
    state.members
    |> Enum.filter(&(&1.online))
    |> Enum.each(&send_message(&1, message))

    # Store in ScyllaDB (async)
    Task.start(fn ->
      ScyllaDB.insert(state.guild_id, message)
    end)

    {:noreply, state}
  end

  # Handles 1M+ messages/sec across all guilds
  # Each guild process isolated - one crash doesn't affect others
end
```

## Phase 4: Hypergrowth (2018-2020)
**Scale**: 10M-100M users | **Cost**: $2M/month

```mermaid
graph TB
    subgraph "Pandemic-Scale Architecture"
        subgraph EdgePlane[Edge - Multi-Region]
            CLOUDFLARE[CloudFlare Enterprise<br/>500TB/month<br/>$50K/month]
            GSLB[Global LB<br/>5 regions]
        end

        subgraph ServicePlane[Service - Region-Aware]
            subgraph USWest[US-West]
                GW_W[Gateway<br/>100 nodes]
                GUILD_W[Guilds<br/>200 nodes]
            end
            subgraph USEast[US-East]
                GW_E[Gateway<br/>80 nodes]
                GUILD_E[Guilds<br/>150 nodes]
            end
            subgraph EU[Europe]
                GW_EU[Gateway<br/>60 nodes]
                GUILD_EU[Guilds<br/>120 nodes]
            end
        end

        subgraph StatePlane[State - Geo-Distributed]
            SCYLLA2[ScyllaDB<br/>100 nodes<br/>50B msgs/day]
            VITESS[Vitess<br/>50 shards<br/>User data]
            S3[S3<br/>500TB<br/>Media]
        end

        CLOUDFLARE --> GSLB
        GSLB --> USWest
        GSLB --> USEast
        GSLB --> EU
        USWest --> SCYLLA2
        USEast --> VITESS
        EU --> S3
    end

    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class CLOUDFLARE,GSLB edgeStyle
    class GW_W,GUILD_W,GW_E,GUILD_E,GW_EU,GUILD_EU serviceStyle
    class SCYLLA2,VITESS,S3 stateStyle
```

**COVID-19 Explosion (March 2020)**:
```yaml
pandemic_surge:
  march_1_2020:
    daily_users: 30M
    voice_minutes: 500M
    messages: 10B/day

  march_31_2020:
    daily_users: 100M  # 233% increase
    voice_minutes: 4B   # 700% increase
    messages: 50B/day  # 400% increase

  emergency_scaling:
    - added_capacity: 500 servers in 2 weeks
    - cost_spike: $500K unplanned spend
    - engineering: 24/7 war room for 3 weeks

  bottlenecks_hit:
    - "Erlang VM scheduling at 10K+ processes/node"
    - "ScyllaDB compaction storms"
    - "Redis connection pool exhaustion"
    - "S3 rate limiting for uploads"
```

## Phase 5: Current Architecture (2024)
**Scale**: 600M users | **Cost**: $15M/month

```mermaid
graph TB
    subgraph "Modern Discord Infrastructure"
        subgraph EdgePlane[Edge - Global Presence]
            CF2[CloudFlare<br/>1PB/day<br/>$200K/mo]
            POP[280 PoPs<br/>WebRTC SFU]
        end

        subgraph ServicePlane[Service - Rust + Elixir]
            subgraph CoreServices[Core Services]
                GATEWAY3[Gateway Fleet<br/>1000 nodes<br/>Rust]
                SESSION[Session Service<br/>500 nodes<br/>Elixir]
            end

            subgraph RealtimeServices[Realtime]
                MSG[Message Service<br/>2000 nodes<br/>Elixir]
                VOICE3[Voice Service<br/>3000 nodes<br/>Rust]
                VIDEO[Video Service<br/>1000 nodes<br/>Rust]
            end
        end

        subgraph StatePlane[State - Multi-DB Strategy]
            SCYLLA3[ScyllaDB<br/>500 nodes<br/>200B msgs/day]
            CRDB[CockroachDB<br/>100 nodes<br/>User data]
            REDIS4[Redis<br/>1000 nodes<br/>1TB RAM]
            S3_2[S3 + Backblaze<br/>10PB media]
        end

        subgraph ControlPlane[Control - Observability]
            PROMETHEUS[Prometheus<br/>100M metrics/sec]
            JAEGER[Jaeger<br/>Distributed tracing]
            CUSTOM[Custom monitoring<br/>Real-time analytics]
        end

        CF2 --> POP
        POP --> GATEWAY3
        GATEWAY3 --> SESSION
        SESSION --> MSG
        SESSION --> VOICE3
        MSG --> SCYLLA3
        SESSION --> REDIS4
        VOICE3 --> S3_2
    end

    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class CF2,POP edgeStyle
    class GATEWAY3,SESSION,MSG,VOICE3,VIDEO serviceStyle
    class SCYLLA3,CRDB,REDIS4,S3_2 stateStyle
    class PROMETHEUS,JAEGER,CUSTOM controlStyle
```

## Key Scaling Innovations

### 1. Consistent Hashing for Guild Distribution
```python
class GuildDistribution:
    """Discord's guild-to-server mapping"""

    def __init__(self):
        self.ring = ConsistentHashRing(replicas=150)
        self.servers = {}  # server_id -> load

    def assign_guild(self, guild_id, member_count):
        # Find best server based on consistent hash
        candidates = self.ring.get_nodes(guild_id, count=3)

        # Pick least loaded candidate
        best_server = min(candidates, key=lambda s: self.servers[s])

        # Large guilds get dedicated resources
        if member_count > 100000:
            best_server = self.assign_dedicated_server(guild_id)

        return best_server

    # Result: 15M guilds distributed across 2000 servers
    # Rebalancing on failure takes < 5 seconds
```

### 2. Message Fanout Optimization
```elixir
# Original: O(n) fanout to all members
defmodule Discord.SlowFanout do
  def broadcast(guild_id, message) do
    Guild.get_members(guild_id)  # Could be 500K members
    |> Enum.each(&send_message(&1, message))  # RIP server
  end
end

# Optimized: Lazy loading + pagination
defmodule Discord.FastFanout do
  def broadcast(guild_id, message) do
    # Only send to online members viewing the channel
    Guild.get_active_sessions(guild_id, message.channel_id)
    |> Stream.chunk_every(1000)  # Batch for efficiency
    |> Task.async_stream(&batch_send(&1, message))
    |> Stream.run()
  end

  # Reduced fanout by 95% for large servers
  # From 500K messages to 25K for typical large guild
end
```

### 3. ScyllaDB Optimization for Messages
```yaml
# Discord's ScyllaDB Schema Evolution

# v1: Simple but slow for pagination
messages_v1:
  table: messages
  partition_key: channel_id
  clustering_key: message_id
  problem: "Scanning 10M messages for pagination"

# v2: Time-bucketed partitions
messages_v2:
  table: messages_by_day
  partition_key: (channel_id, day_bucket)
  clustering_key: timestamp
  improvement: "100x faster pagination"

# v3: Hybrid hot/cold storage
messages_v3:
  hot_table: recent_messages  # Last 7 days, SSD
  cold_table: archived_messages  # Older, HDD
  cache: redis_message_cache  # Last 1 hour

  performance:
    hot_read_latency: 1ms
    cold_read_latency: 50ms
    cache_hit_rate: 85%
    storage_cost_reduction: 60%
```

## Cost Evolution

```mermaid
graph LR
    subgraph "Infrastructure Spend Growth"
        Y2015[$99/mo<br/>10 users<br/>$9.90/user]
        Y2016[$5K/mo<br/>100K users<br/>$0.05/user]
        Y2017[$50K/mo<br/>1M users<br/>$0.05/user]
        Y2018[$500K/mo<br/>10M users<br/>$0.05/user]
        Y2020[$2M/mo<br/>100M users<br/>$0.02/user]
        Y2024[$15M/mo<br/>600M users<br/>$0.025/user]
    end

    Y2015 --> Y2016 --> Y2017 --> Y2018 --> Y2020 --> Y2024

    style Y2015 fill:#10B981
    style Y2016 fill:#10B981
    style Y2017 fill:#10B981
    style Y2018 fill:#F59E0B
    style Y2020 fill:#F59E0B
    style Y2024 fill:#8B5CF6
```

**Unit Economics Analysis**:
```python
unit_economics = {
    "2015": {
        "cost_per_user": "$9.90",
        "reason": "Unoptimized, single server"
    },
    "2016-2018": {
        "cost_per_user": "$0.05",
        "reason": "Basic economies of scale"
    },
    "2020": {
        "cost_per_user": "$0.02",
        "reason": "Massive scale efficiencies"
    },
    "2024": {
        "cost_per_user": "$0.025",
        "reason": "Premium features (video, streaming)"
    },

    "revenue_per_user": {
        "free_users": "$0",
        "nitro_users": "$9.99/month",
        "nitro_percentage": "3%",
        "effective_arpu": "$0.30"
    },

    "profit_margin": "$0.275/user/month"
}
```

## Major Incidents and Lessons

### The Great Gateway Outage (2018)
```python
# What happened
incident_2018 = {
    "date": "October 29, 2018",
    "duration": "47 minutes",
    "impact": "100% of users unable to connect",

    "root_cause": {
        "trigger": "Routine config update",
        "bug": "Race condition in Erlang supervisor",
        "cascade": "All gateways restarted simultaneously"
    },

    "fixes": {
        "immediate": "Manual restart with staggered timing",
        "long_term": [
            "Canary deployments",
            "Chaos engineering program",
            "Circuit breakers everywhere"
        ]
    }
}
```

### The Cloudflare Outage (2020)
```python
# Discord's multi-CDN strategy born from this
incident_2020 = {
    "date": "July 17, 2020",
    "duration": "27 minutes",
    "impact": "Global Discord unreachable",

    "problem": "Single point of failure on Cloudflare",

    "solution": {
        "multi_cdn": {
            "primary": "Cloudflare (70%)",
            "secondary": "Fastly (20%)",
            "tertiary": "Akamai (10%)"
        },
        "auto_failover": "DNS-based in 30 seconds",
        "cost": "+$100K/month",
        "worth_it": "Absolutely"
    }
}
```

## Scaling Philosophy

### Discord's 10 Scaling Commandments
1. **Let it crash** - Erlang philosophy, isolated failures
2. **Consistent hashing** - For everything distributed
3. **Read from cache, write to queue** - Never block users
4. **Lazy load everything** - Don't fetch until needed
5. **Paginate aggressively** - No unbounded queries
6. **Regional isolation** - EU outage shouldn't affect US
7. **Gradual rollouts** - 1% → 10% → 50% → 100%
8. **Measure everything** - 100M metrics/sec
9. **Automate recovery** - Self-healing systems
10. **Keep it simple** - Complexity kills at scale

## Current Challenges (2024)

```yaml
ongoing_challenges:
  ai_features:
    problem: "AI chat summarization needs GPUs"
    scale: "100M+ requests/day"
    solution: "Building GPU clusters, $5M investment"

  video_streaming:
    problem: "Screen sharing for 1M concurrent users"
    bandwidth: "10Gbps per region"
    solution: "WebRTC SFU + VP9 codec"

  mobile_optimization:
    problem: "Battery drain from persistent connections"
    solution: "Adaptive heartbeat, push notifications"

  compliance:
    problem: "GDPR, COPPA, content moderation"
    scale: "1B messages/day to scan"
    solution: "ML-based moderation, 10K human moderators"
```

## The 3 AM Story

**December 31, 2020 - New Year's Eve Midnight Surge**
```python
nye_incident = {
    "23:45": "Normal load, 50M active users",
    "23:55": "Spike begins, 70M users",
    "00:00": "EXPLOSION - 150M concurrent users",
    "00:01": "Gateway layer at 400% capacity",
    "00:02": "Auto-scaling triggered",
    "00:05": "500 new instances online",
    "00:10": "Service restored, 150M users stable",

    "records_broken": {
        "concurrent_users": "150M (previous: 100M)",
        "messages_per_second": "25M (previous: 15M)",
        "voice_participants": "20M (previous: 10M)"
    },

    "engineering_response": {
        "on_call": "15 engineers in war room",
        "decision": "Let auto-scaling handle it",
        "result": "System self-healed in 10 minutes"
    },

    "lesson": "Trust your automation at 3 AM"
}
```

## Future Scale Targets

```yaml
2025_goals:
  users: 1_000_000_000
  messages_per_day: 500_000_000_000
  voice_concurrent: 100_000_000
  infrastructure_budget: $30M/month

  key_initiatives:
    - "Rust rewrite of remaining Elixir services"
    - "Custom protocol replacing WebSocket"
    - "Edge computing for voice processing"
    - "Blockchain for decentralized identity"

  motto: "Scale like gaming, reliable like banking"
```

*"We went from 10 gamers to 600M users by never being satisfied with 'good enough'. Every 10x growth forced us to reimagine everything."* - Discord CTO