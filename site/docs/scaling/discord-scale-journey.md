# Discord Scale Journey: 10 → 150 Million Users

## From Gaming Chat to Internet Infrastructure (2015-2024)

Discord's evolution from a gaming voice chat to serving 150M+ monthly active users showcases modern scaling with Elixir, Rust, and ScyllaDB.

## Phase 1: The Gaming Pivot (2015) - 0 to 10,000 Users

```mermaid
graph TB
    subgraph MVP[Minimum Viable Product]
        CLIENT[Desktop Client<br/>Electron<br/>React]
        WEBRTC[WebRTC<br/>Voice chat<br/>P2P initially]
        NODEJS[Node.js Backend<br/>Single server<br/>Socket.io]
        MONGODB[(MongoDB<br/>All data<br/>Single instance)]
        REDIS[(Redis<br/>Sessions<br/>Pub/sub)]
    end

    CLIENT --> WEBRTC
    CLIENT --> NODEJS
    NODEJS --> MONGODB
    NODEJS --> REDIS

    %% Apply colors
    classDef clientStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class CLIENT,WEBRTC clientStyle
    class NODEJS serviceStyle
    class MONGODB,REDIS stateStyle
```

**Origin Story**:
- Founded by Jason Citron (previously Hammer & Chisel)
- Pivot from game "Fates Forever" to chat platform
- Focus: Low-latency voice for gamers
- Initial funding: $20M Series A

**Technical Choices**:
- Electron for cross-platform desktop
- WebRTC for voice (later replaced)
- MongoDB for flexibility (later regretted)
- Real-time via WebSockets

## Phase 2: The Elixir Rewrite (2016) - 100,000 Users

```mermaid
graph TB
    subgraph ElixirArch[The Elixir Revolution]
        subgraph EdgePlane[Edge - Real-time]
            WS[WebSocket Gateway<br/>Elixir<br/>1M connections/node]
            VOICE[Voice Servers<br/>C++<br/>Opus codec]
        end

        subgraph ServicePlane[Service - Distributed]
            GUILD[Guild Service<br/>Elixir GenServers<br/>Stateful]
            PRESENCE[Presence Service<br/>CRDT-based<br/>Eventually consistent]
            MESSAGE[Message Service<br/>Python<br/>History]
        end

        subgraph StatePlane[State - Hybrid]
            CASSANDRA[(Cassandra<br/>Messages<br/>3 nodes)]
            POSTGRES[(PostgreSQL<br/>Metadata<br/>Master-slave)]
            REDIS[(Redis<br/>Hot data<br/>10GB)]
        end
    end

    %% Apply colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class WS,VOICE edgeStyle
    class GUILD,PRESENCE,MESSAGE serviceStyle
    class CASSANDRA,POSTGRES,REDIS stateStyle

    WS --> GUILD
    GUILD --> PRESENCE
    GUILD --> MESSAGE
    MESSAGE --> CASSANDRA
    GUILD --> POSTGRES
    PRESENCE --> REDIS
```

**The Big Decision: Elixir/Erlang**
```elixir
# Why Elixir worked for Discord
defmodule Discord.Guild do
  use GenServer

  # Each guild (server) is an Erlang process
  def handle_cast({:message, msg}, state) do
    # Broadcast to all connected users
    Phoenix.PubSub.broadcast(
      Discord.PubSub,
      "guild:#{state.guild_id}",
      {:new_message, msg}
    )
    {:noreply, state}
  end
end
# Result: 5M concurrent users on single server
```

**Key Achievements**:
- 1M WebSocket connections per server
- 2ms message delivery latency
- Fault tolerance via OTP
- Hot code reloading

## Phase 3: Hypergrowth (2017-2018) - 10 Million Users

```mermaid
graph TB
    subgraph HyperScale[Scaling Everything]
        subgraph Gateway[Gateway Layer]
            GW1[Gateway 1<br/>2M connections]
            GW2[Gateway 2<br/>2M connections]
            GW3[Gateway N...<br/>2M each]
            ZLBS[zLBS<br/>Custom LB<br/>Consistent hash]
        end

        subgraph Services[Microservices]
            API[API Service<br/>Python/Rust<br/>100 instances]
            GUILDS[Guild Service<br/>Elixir<br/>10K guilds/node]
            VOICE_NEW[Voice Service<br/>Rust rewrite<br/>Low latency]
        end

        subgraph Storage[Storage Evolution]
            CASS[(Cassandra<br/>100TB messages<br/>12 nodes)]
            SCYLLA[(ScyllaDB test<br/>C++ Cassandra<br/>3x performance)]
            PG[(PostgreSQL<br/>Sharded<br/>User data)]
        end

        subgraph Problems[Growing Pains]
            HOTSPOTS[Hot Servers<br/>Popular guilds]
            CASSANDRA_GC[Cassandra GC<br/>Java pauses]
            VOICE_QUALITY[Voice drops<br/>During spikes]
        end
    end

    %% Apply colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef problemStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class GW1,GW2,GW3,ZLBS edgeStyle
    class API,GUILDS,VOICE_NEW serviceStyle
    class CASS,SCYLLA,PG stateStyle
    class HOTSPOTS,CASSANDRA_GC,VOICE_QUALITY problemStyle
```

**Scaling Challenges**:
1. **Hot Servers**: Ninja's Fortnite streams (100K+ concurrent)
2. **Message History**: Billions of messages, slow queries
3. **Voice Quality**: Jitter during peak gaming hours
4. **Presence Updates**: O(n²) problem for large servers

## Phase 4: The Rust Revolution (2019-2020) - 50 Million Users

```mermaid
graph TB
    subgraph RustEra[Performance Revolution]
        subgraph Edge[Edge - Optimized]
            GATEWAY_RUST[Gateway<br/>Rust rewrite<br/>5M connections/node]
            VOICE_RUST[Voice<br/>Rust + WebRTC<br/>< 20ms latency]
            CDN[Custom CDN<br/>Image proxy<br/>Cloudflare]
        end

        subgraph Core[Core Services]
            GUILD_RUST[Guild Service v2<br/>Rust async<br/>100K guilds/node]
            PUBSUB[PubSub Service<br/>Custom protocol<br/>10M msg/sec]
            CONSISTENT[Consistent Store<br/>etcd cluster<br/>Config & routing]
        end

        subgraph Data[Data Layer - ScyllaDB]
            SCYLLA1[(ScyllaDB Cluster<br/>177 nodes<br/>Trillions of messages)]
            CACHE[Cache Layer<br/>Redis + Custom<br/>1TB RAM total]
            S3[S3/Backblaze<br/>Media storage<br/>Petabytes]
        end

        subgraph Innovation[Key Innovations]
            READ_STATES[Read States<br/>Per-user tracking<br/>Billions of records]
            LAZY_GUILDS[Lazy Guild Loading<br/>On-demand hydration]
            VOICE_REGIONS[Voice Regions<br/>Global deployment]
        end
    end

    %% Apply colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef innovationStyle fill:#9900CC,stroke:#6600AA,color:#fff

    class GATEWAY_RUST,VOICE_RUST,CDN edgeStyle
    class GUILD_RUST,PUBSUB,CONSISTENT serviceStyle
    class SCYLLA1,CACHE,S3 stateStyle
    class READ_STATES,LAZY_GUILDS,VOICE_REGIONS innovationStyle
```

**The Rust Rewrite Success**:
```rust
// Before: Go implementation
// 13ms p99 latency, 30% CPU

// After: Rust implementation
pub async fn handle_message(msg: Message) -> Result<()> {
    // Zero-copy deserialization
    let parsed = bincode::deserialize(&msg.data)?;

    // Lock-free concurrent processing
    tokio::spawn(async move {
        process_message(parsed).await
    });

    Ok(())
}
// Result: 1ms p99 latency, 5% CPU
```

**ScyllaDB Migration**:
- From Cassandra (Java) to ScyllaDB (C++)
- Same API, 10x performance
- Reduced nodes: 372 → 177
- Latency: p99 40ms → 15ms
- Cost savings: $1.5M/year

## Phase 5: Pandemic Explosion (2020-2021) - 140 Million Users

```mermaid
graph TB
    subgraph Pandemic[COVID-19 Scale]
        subgraph Load[10x Load Increase]
            USERS[140M MAU<br/>300% growth]
            VOICE_PEAK[15M concurrent<br/>voice users]
            MESSAGES[4B messages/day]
            STREAMS[1M+ Go Live streams]
        end

        subgraph Emergency[Emergency Scaling]
            CAPACITY[3x infrastructure<br/>in 3 months]
            HIRING[100+ engineers<br/>hired remotely]
            ONCALL[24/7 war room<br/>3 months straight]
        end

        subgraph Features[New Features Under Load]
            STAGE[Stage Channels<br/>Clubhouse competitor]
            SCREEN[Screen Share<br/>1080p 60fps]
            ACTIVITIES[Activities<br/>Games in voice]
            THREADS[Threads<br/>Conversation branches]
        end

        subgraph Infrastructure[Infrastructure Response]
            MULTICLOUD[Multi-cloud<br/>AWS + GCP]
            GLOBAL[30+ PoPs<br/>Global presence]
            AUTOSC[Auto-scaling<br/>10x capacity]
        end
    end

    %% Apply colors
    classDef loadStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef emergencyStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef featureStyle fill:#10B981,stroke:#059669,color:#fff
    classDef infraStyle fill:#3B82F6,stroke:#2563EB,color:#fff

    class USERS,VOICE_PEAK,MESSAGES,STREAMS loadStyle
    class CAPACITY,HIRING,ONCALL emergencyStyle
    class STAGE,SCREEN,ACTIVITIES,THREADS featureStyle
    class MULTICLOUD,GLOBAL,AUTOSC infraStyle
```

**Pandemic Challenges**:
1. **Education**: Entire schools on Discord
2. **Work**: Companies using for remote work
3. **Social**: Friend groups migrating
4. **Load**: 10x growth in 3 months

**Emergency Response**:
- Disabled non-essential features temporarily
- Rate limiting on API endpoints
- Aggressive caching everywhere
- Read replica multiplication

## Phase 6: Modern Platform (2022-2024) - 150M+ Users

```mermaid
graph TB
    subgraph Current[Current Architecture 2024]
        subgraph EdgeNetwork[Global Edge]
            CLOUDFLARE[Cloudflare<br/>DDoS protection<br/>1Tbps capacity]
            WEBRTC_NEXT[WebRTC Next<br/>AV1 codec<br/>4K support]
            QUIC[QUIC Protocol<br/>Mobile optimized]
        end

        subgraph Services[Service Mesh]
            GATEWAY_FLEET[Gateway Fleet<br/>1000+ nodes<br/>Rust]
            API_GRAPHQL[GraphQL API<br/>Type-safe<br/>Federated]
            WORKER_FLEET[Worker Fleet<br/>Background jobs<br/>100K workers]
        end

        subgraph DataPlatform[Data Platform]
            SCYLLA_FLEET[(ScyllaDB<br/>500+ nodes<br/>10PB data)]
            CRDB[(CockroachDB<br/>Transactional data<br/>Multi-region)]
            ANALYTICS[(ClickHouse<br/>Analytics<br/>1PB processed/day)]
            ML_PLATFORM[ML Platform<br/>Safety & recommendations]
        end

        subgraph Features[Platform Features]
            FORUMS[Forum Channels<br/>Reddit-style]
            SUBSCRIPTION[Server Subscriptions<br/>Creator economy]
            SHOP[Shop<br/>Digital goods]
            AI_SUMMARY[AI Summaries<br/>Conversation digest]
        end
    end

    %% Apply colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef dataStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef featureStyle fill:#9900CC,stroke:#6600AA,color:#fff

    class CLOUDFLARE,WEBRTC_NEXT,QUIC edgeStyle
    class GATEWAY_FLEET,API_GRAPHQL,WORKER_FLEET serviceStyle
    class SCYLLA_FLEET,CRDB,ANALYTICS,ML_PLATFORM dataStyle
    class FORUMS,SUBSCRIPTION,SHOP,AI_SUMMARY featureStyle
```

## The Architecture That Scales

### Message Flow Architecture
```mermaid
graph LR
    subgraph MessagePath[Message Path - 2ms e2e]
        USER[User Types]
        GATEWAY[Gateway<br/>Rust<br/>0.1ms]
        GUILD[Guild Service<br/>Elixir<br/>0.3ms]
        PERSIST[ScyllaDB<br/>Write<br/>1ms]
        FANOUT[Fanout<br/>To users<br/>0.5ms]
        DELIVER[Delivery<br/>WebSocket<br/>0.1ms]
    end

    USER --> GATEWAY
    GATEWAY --> GUILD
    GUILD --> PERSIST
    GUILD --> FANOUT
    FANOUT --> DELIVER

    %% Parallel path
    GUILD --> CACHE[Cache Update<br/>0.2ms]
```

### Voice Architecture Evolution
```mermaid
graph TB
    subgraph VoiceEvolution[Voice Server Evolution]
        V1[2015: WebRTC P2P<br/>High latency]
        V2[2016: Server relay<br/>C++, 50ms]
        V3[2018: Rust rewrite<br/>20ms p99]
        V4[2020: Regional servers<br/>15ms p99]
        V5[2024: Edge compute<br/>8ms p99]
    end

    V1 --> V2
    V2 --> V3
    V3 --> V4
    V4 --> V5

    style V1 fill:#ffcccc
    style V2 fill:#ffddcc
    style V3 fill:#ffffcc
    style V4 fill:#ccffcc
    style V5 fill:#ccffff
```

## Scale Numbers (2024)

| Metric | Value | Notes |
|--------|-------|-------|
| **Monthly Active Users** | 150M+ | 200M registered |
| **Daily Active Users** | 19M | High engagement |
| **Messages/Day** | 4 billion | 50K/second peak |
| **Voice Minutes/Day** | 2.5 billion | 30K concurrent channels |
| **Servers (Guilds)** | 19 million | Some with 500K+ members |
| **API Requests/Day** | 50 billion | 600K/second peak |
| **Data Stored** | 10+ PB | Growing 1PB/quarter |
| **Infrastructure Nodes** | 5000+ | Across 13 regions |

## Technical Innovations

### 1. Lazy Guild Loading
```elixir
# Problem: Loading 500K member servers = OOM
# Solution: Load on demand

defmodule Discord.LazyGuild do
  def get_member(guild_id, user_id) do
    case Cache.get({guild_id, user_id}) do
      nil ->
        # Load single member from database
        member = Database.get_member(guild_id, user_id)
        Cache.put({guild_id, user_id}, member, ttl: 300)
        member
      cached ->
        cached
    end
  end
end
# Result: 100x memory reduction
```

### 2. Read States at Scale
```rust
// Tracking what each user has read in each channel
// Challenge: 150M users × 1000 channels = 150B records

struct ReadState {
    user_id: u64,
    channel_id: u64,
    last_message_id: u64,
    mention_count: u32,
}

// Solution: Compact binary format + aggressive compression
// 150B records in just 2TB (13 bytes per record)
```

### 3. Consistent Hashing for Guilds
```python
# Guild to server mapping
def get_guild_node(guild_id):
    # Consistent hash ring with virtual nodes
    hash = mmh3.hash(str(guild_id))
    node = hash_ring.get_node(hash)

    # Handle hot guilds (>10K active)
    if is_hot_guild(guild_id):
        # Spread across multiple nodes
        return get_dedicated_nodes(guild_id)

    return node
```

## Production War Stories

### The Fortnite Launch (2018)
- **Event**: Ninja streams with Drake
- **Load**: 600K concurrent viewers in Discord
- **Problem**: Single guild overwhelming node
- **Solution**: Emergency guild sharding
- **Result**: Invented "Stage Channels" concept

### The Area 51 Raid (2019)
- **Event**: Meme event planning
- **Load**: 500K member server created
- **Problem**: Guild size limits hit
- **Solution**: Lazy loading implementation
- **Long-term**: Rearchitected guild storage

### GameStop/WallStreetBets (2021)
- **Event**: WSB Discord explosion
- **Growth**: 50K → 500K members in 24 hours
- **Problem**: Moderation tools overwhelmed
- **Response**: Emergency moderation features
- **Banned**: Then unbanned after backlash

### COVID School Migration (2020)
- **Event**: Schools adopting Discord
- **Challenge**: Different privacy requirements
- **Solution**: Created education features
- **Scale**: 1M+ students in first month

## Cost Structure

### Infrastructure Costs (Estimated)
```mermaid
pie title Monthly Infrastructure Costs ($8M total)
    "Bandwidth/CDN" : 3000000
    "Compute (AWS/GCP)" : 2500000
    "Storage (ScyllaDB/S3)" : 1500000
    "Voice Infrastructure" : 700000
    "Monitoring/Analytics" : 300000
```

### Cost Optimizations
1. **ScyllaDB**: Saved $1.5M/year vs Cassandra
2. **Rust Rewrites**: 80% reduction in compute
3. **Backblaze B2**: 80% cheaper than S3
4. **Custom CDN**: 50% cost reduction
5. **Spot Instances**: 40% of batch workloads

## Lessons Learned

### What Worked
1. **Elixir/Erlang**: Perfect for real-time chat
2. **Rust**: Massive performance gains
3. **ScyllaDB**: Cassandra compatible, 10x performance
4. **Microservices**: Allowed parallel scaling
5. **WebRTC**: Good enough for voice

### What Didn't Work
1. **MongoDB**: Terrible at scale
2. **Go**: GC pauses unacceptable
3. **Cassandra**: Java GC nightmares
4. **GraphQL initially**: Too complex
5. **P2P voice**: Quality issues

### Key Decisions
1. **2015**: Electron for desktop (enabled rapid development)
2. **2016**: Elixir rewrite (enabled massive concurrency)
3. **2017**: Consistent hashing (solved hot guild problem)
4. **2019**: Rust adoption (performance breakthrough)
5. **2020**: ScyllaDB migration (cost and performance win)

## Future Architecture (2025+)

### Planned Improvements
- **Edge Computing**: Voice servers at ISP edge
- **WASM Plugins**: User customization
- **Federation**: Interop with Matrix
- **E2E Encryption**: Optional for DMs
- **AI Integration**: Smart moderation, summaries

### Scale Targets
- 500M MAU by 2025
- 10B messages/day
- 50M concurrent voice
- Sub-5ms global latency
- 99.99% availability

## Key Takeaways

1. **Choose the right language**: Elixir for concurrency, Rust for performance
2. **Migrate databases carefully**: MongoDB → Cassandra → ScyllaDB
3. **Cache aggressively**: 99% cache hit rate target
4. **Shard by design**: Plan for horizontal scaling
5. **Optimize hot paths**: Rewrite in Rust when needed
6. **Monitor everything**: Can't fix what you can't see
7. **Prepare for viral growth**: 10x capacity minimum
8. **Listen to users**: Features drive adoption

## References

- "How Discord Stores Billions of Messages" - Discord Engineering 2017
- "Why Discord is Switching from Go to Rust" - Discord Blog 2020
- "How Discord Handles Two and Half Million Concurrent Voice Users" - 2020
- "ScyllaDB at Discord: 177 Nodes and Counting" - ScyllaDB Summit 2023
- "Scaling Discord's Real-time Communications" - InfoQ 2024

---

*Last Updated: September 2024*
*Data Sources: Discord Engineering Blog, Conference Talks, Public Metrics*