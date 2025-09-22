# Dropbox Request Flow

## File Upload/Download and Sync Flow

Dropbox's request flow handles billions of file operations daily through block-level delta sync, achieving 95% bandwidth reduction and sub-second sync latency across 700M+ users.

```mermaid
sequenceDiagram
    participant Client as Desktop Client<br/>Smart Sync Enabled
    participant CDN as Akamai CDN<br/>300+ PoPs
    participant LB as Load Balancer<br/>HAProxy
    participant API as API Gateway<br/>Django/Python
    participant AUTH as Auth Service<br/>OAuth 2.0
    participant SYNC as Sync Engine<br/>Block Delta Sync
    participant NUCLEUS as Nucleus Metadata<br/>Distributed DB
    participant MAGIC as Magic Pocket<br/>Custom Storage
    participant NOTIF as Notification<br/>Real-time Updates

    Note over Client,NOTIF: File Upload Flow (p99: 2 seconds)

    Client->>+CDN: POST /files/upload<br/>Block hashes + metadata<br/>OAuth token
    Note right of Client: Local file chunked<br/>into 4MB blocks<br/>SHA256 hashed

    CDN->>+LB: Route to nearest region<br/>Latency: <50ms
    LB->>+API: Load balance request<br/>Circuit breaker: 5s timeout

    API->>+AUTH: Validate OAuth token<br/>Check user permissions
    AUTH-->>-API: Token valid + user_id<br/>Latency: <10ms

    API->>+SYNC: Process file upload<br/>user_id + file_metadata

    SYNC->>+NUCLEUS: Check existing blocks<br/>Block deduplication query
    NUCLEUS-->>-SYNC: Block existence map<br/>95% blocks already exist
    Note right of NUCLEUS: Global deduplication<br/>across all users<br/>Saves 95% storage

    SYNC->>+MAGIC: Upload new blocks only<br/>5% of original file size
    MAGIC-->>-SYNC: Block storage confirmation<br/>3x replication confirmed

    SYNC->>+NUCLEUS: Update file metadata<br/>Version + block pointers
    NUCLEUS-->>-SYNC: Metadata stored<br/>Atomic transaction

    SYNC-->>-API: Upload complete<br/>File available for sync

    API->>+NOTIF: Trigger sync notification<br/>user_id + file_path
    NOTIF->>Client: Real-time notification<br/>WebSocket/Long-polling
    Note right of NOTIF: <500ms notification<br/>to all user devices

    API-->>-CDN: 200 OK + file_id<br/>p99: 2s total latency
    CDN-->>-Client: Upload confirmation

    Note over Client,NOTIF: File Download/Sync Flow (p99: 1 second)

    Client->>+CDN: GET /files/{file_id}<br/>OAuth token + range headers
    CDN->>+LB: Route request
    LB->>+API: Forward request

    API->>+AUTH: Validate token<br/>Check file permissions
    AUTH-->>-API: Access granted

    API->>+SYNC: Request file content<br/>Check local cache

    alt Cache Hit (99% of requests)
        SYNC->>+NUCLEUS: Get cached metadata<br/>Redis lookup
        NUCLEUS-->>-SYNC: Block pointers<br/>Sub-ms response
    else Cache Miss (1% of requests)
        SYNC->>+NUCLEUS: Query metadata DB<br/>Distributed query
        NUCLEUS-->>-SYNC: File blocks mapping<br/><10ms response
    end

    SYNC->>+MAGIC: Request file blocks<br/>Parallel block retrieval
    MAGIC-->>-SYNC: Block content<br/>Streaming response

    SYNC-->>-API: Assembled file content<br/>Smart Sync optimization

    API-->>-CDN: File content + cache headers<br/>24hr CDN cache
    CDN-->>-Client: File downloaded<br/>p99: 1s total

    Note over Client,NOTIF: Delta Sync Flow (p99: 200ms)

    Client->>Client: File modified locally<br/>Block-level diff calculated
    Client->>+CDN: PATCH /files/{file_id}<br/>Only changed blocks
    Note right of Client: 95% bandwidth savings<br/>vs full file upload

    CDN->>+API: Delta sync request
    API->>+SYNC: Process delta<br/>Block-level merge

    SYNC->>+NUCLEUS: Get current file state<br/>Version check
    NUCLEUS-->>-SYNC: Current block mapping<br/>Conflict detection

    SYNC->>+MAGIC: Store delta blocks<br/>Append-only operation
    MAGIC-->>-SYNC: Delta stored<br/>New version created

    SYNC->>+NUCLEUS: Update file version<br/>Atomic increment
    NUCLEUS-->>-SYNC: Version updated<br/>Conflict resolution

    SYNC-->>-API: Delta sync complete
    API->>+NOTIF: Broadcast file change<br/>All user devices
    NOTIF->>Client: Delta available<br/>Real-time sync trigger

    API-->>-CDN: 200 OK + new version
    CDN-->>-Client: Sync complete<br/>p99: 200ms
```

## Request Flow Metrics

| Operation | P50 Latency | P99 Latency | Throughput | Bandwidth Savings |
|-----------|-------------|-------------|------------|-------------------|
| **File Upload** | 800ms | 2s | 1M+ uploads/hour | 95% via deduplication |
| **File Download** | 300ms | 1s | 10M+ downloads/hour | 99% cache hit rate |
| **Delta Sync** | 50ms | 200ms | 100M+ syncs/hour | 95% vs full file |
| **Real-time Notification** | 100ms | 500ms | 1B+ notifications/day | WebSocket efficiency |

## Critical Path Optimizations

### Block-Level Deduplication
```
Original File: 100MB
After Chunking: 25 × 4MB blocks
Global Dedup Hit: 95% (23 blocks exist)
Upload Required: 5% (2 new blocks = 8MB)
Bandwidth Saved: 95% (92MB saved)
```

### Smart Sync Intelligence
```
User Requests File → Check Local Cache →
Cache Miss → Download Metadata Only →
On-Demand Block Retrieval → Assemble File →
Background Prefetch Related Files
```

### Real-Time Sync Pipeline
```
File Change Detected → Block Diff Calculated →
Delta Upload (2-8MB avg) → Metadata Update →
Push Notification → Device Sync Triggered →
<500ms End-to-End Sync Time
```

## Performance SLAs

- **Upload Latency**: p99 under 2 seconds for files up to 1GB
- **Download Latency**: p99 under 1 second with 99% cache hit
- **Sync Propagation**: <500ms notification to all devices
- **Delta Sync**: p99 under 200ms for incremental changes
- **API Availability**: 99.9% uptime with <100ms baseline latency

## Failure Handling

- **Network Interruption**: Resume upload from last block
- **Auth Token Expiry**: Auto-refresh with exponential backoff
- **Storage Backend Error**: Failover to secondary Magic Pocket
- **Metadata Inconsistency**: Last-writer-wins with conflict resolution
- **Rate Limiting**: Exponential backoff with jitter (max 30s)

*Source: Dropbox Engineering Blog, Sync Protocol Documentation, Performance Engineering Talks*