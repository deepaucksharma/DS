# Pinterest Request Flow

## The Golden Path: Pin Creation to Discovery

Pinterest's request flow handles three critical user journeys: pin creation with visual analysis, personalized feed generation using graph neural networks, and visual search powered by computer vision.

```mermaid
sequenceDiagram
    participant User as User<br/>(450M MAU)
    participant Mobile as Mobile App<br/>(iOS/Android)
    participant CDN as CloudFlare CDN<br/>(300+ POPs)
    participant LB as Load Balancer<br/>(F5 BigIP)
    participant API as API Gateway<br/>(Kong)
    participant Feed as Feed Service<br/>(Go 1.19)
    participant PinSage as PinSage GNN<br/>(GraphSAGE)
    participant Vision as Visual Search<br/>(PyTorch)
    participant Graph as Graph DB<br/>(Pin Relationships)
    participant HBase as HBase<br/>(Pin Metadata)
    participant Redis as Redis Cache<br/>(Hot Pins)
    participant S3 as AWS S3<br/>(Image Storage)

    Note over User,S3: Pin Creation Flow (Upload → Analysis → Storage)

    User->>Mobile: Upload image + description
    Mobile->>CDN: POST /v3/pins/create<br/>Multipart upload
    Note right of Mobile: SLO: p99 < 2s end-to-end

    CDN->>LB: Route to nearest region
    LB->>API: Authenticate & rate limit<br/>(10 pins/min per user)
    API->>Vision: Extract visual features<br/>ResNet-50 CNN

    Vision->>Vision: Generate embeddings<br/>(2048-dim vector)
    Note right of Vision: GPU inference: p95 < 300ms

    API->>S3: Store original image<br/>+ 5 optimized sizes
    S3-->>API: Return image URLs<br/>CDN-ready paths

    API->>HBase: Store pin metadata<br/>+ visual embeddings
    HBase-->>API: Pin ID + timestamp

    API->>Graph: Update user pin graph<br/>Add edges & weights
    API-->>Mobile: 201 Created<br/>Pin URL + preview
    Mobile-->>User: Pin successfully saved

    Note over User,S3: Personalized Feed Flow (Request → Ranking → Delivery)

    User->>Mobile: Open Pinterest app<br/>Pull to refresh
    Mobile->>CDN: GET /v3/feed/home<br/>Include user context

    CDN->>LB: Check cache miss<br/>(personalized content)
    LB->>API: Route to feed service
    API->>Feed: Get user interests<br/>+ recent interactions

    Feed->>Graph: Fetch user subgraph<br/>(2-hop neighborhood)
    Graph-->>Feed: Related pins + scores<br/>(candidate set: 10k pins)

    Feed->>PinSage: Rank candidates<br/>GraphSAGE inference
    Note right of PinSage: ML inference: p99 < 150ms

    PinSage->>PinSage: Graph convolution<br/>3 layers + attention
    PinSage-->>Feed: Ranked pin list<br/>(top 200 pins)

    Feed->>HBase: Batch fetch metadata<br/>Pin details + stats
    HBase-->>Feed: Pin data + images

    Feed->>Redis: Cache feed response<br/>TTL: 15 minutes
    Feed-->>API: Personalized feed<br/>JSON + image URLs

    API-->>Mobile: 200 OK<br/>Feed data + metadata
    Mobile-->>User: Display personalized pins

    Note over User,S3: Visual Search Flow (Image → Features → Results)

    User->>Mobile: Take photo/upload<br/>Visual search camera
    Mobile->>CDN: POST /v3/search/visual<br/>Image + crop coordinates

    CDN->>API: Route to visual search
    API->>Vision: Extract search features<br/>Multi-scale CNN

    Vision->>Vision: Generate query vector<br/>+ object detection
    Note right of Vision: Feature extraction: p95 < 200ms

    Vision->>Graph: Vector similarity search<br/>Approximate NN (FAISS)
    Graph-->>Vision: Top 1000 matches<br/>Cosine similarity > 0.8

    Vision->>PinSage: Re-rank by context<br/>User preferences + trends
    PinSage-->>Vision: Final ranking<br/>Top 100 results

    Vision->>HBase: Fetch result metadata<br/>Batch read
    HBase-->>Vision: Pin details + images

    Vision-->>API: Search results<br/>Ranked pin list
    API-->>Mobile: 200 OK<br/>Visual search results
    Mobile-->>User: Show similar pins

    Note over User,S3: SLO Summary
    Note right of User: Pin Creation: p99 < 2s
    Note right of User: Feed Load: p99 < 150ms
    Note right of User: Visual Search: p95 < 300ms
```

## Performance Budgets & SLOs

### Pin Creation Flow
- **Image Upload**: p95 < 1.5s (including S3 upload)
- **Visual Analysis**: p95 < 300ms (CNN inference)
- **Metadata Storage**: p99 < 50ms (HBase write)
- **Graph Update**: p99 < 100ms (relationship edges)
- **End-to-End**: p99 < 2s (user perception)

### Feed Generation Flow
- **User Context**: p95 < 20ms (Redis lookup)
- **Candidate Retrieval**: p99 < 80ms (Graph query)
- **PinSage Ranking**: p99 < 150ms (GNN inference)
- **Metadata Fetch**: p95 < 30ms (HBase batch read)
- **Cache Storage**: p99 < 10ms (Redis write)
- **End-to-End**: p99 < 150ms (feed refresh)

### Visual Search Flow
- **Feature Extraction**: p95 < 200ms (GPU inference)
- **Similarity Search**: p99 < 50ms (FAISS query)
- **Result Re-ranking**: p95 < 100ms (PinSage)
- **Metadata Fetch**: p95 < 40ms (HBase batch)
- **End-to-End**: p95 < 300ms (search results)

## Traffic Patterns & Load

### Peak Traffic Characteristics
- **Feed Requests**: 500k RPS during evening hours (US)
- **Pin Uploads**: 50k RPS peak (holiday seasons)
- **Visual Search**: 100k RPS (shopping events)
- **Geographic Distribution**: 40% US, 25% Europe, 35% APAC

### Seasonal Variations
- **Holiday Shopping**: 3x normal traffic (Nov-Dec)
- **Wedding Season**: 2x pin saves (Mar-Jun)
- **Back to School**: 2.5x recipe/DIY pins (Aug-Sep)
- **Summer Travel**: 2x travel pin searches (Jun-Aug)

## Error Handling & Fallbacks

### Feed Generation Failures
- **PinSage Timeout**: Fall back to collaborative filtering
- **Graph DB Unavailable**: Use cached user preferences
- **Redis Cache Miss**: Generate feed without caching
- **Partial Results**: Fill with trending/popular pins

### Visual Search Degradation
- **GPU Overload**: Queue requests, return cached results
- **Model Inference Error**: Fall back to text-based search
- **FAISS Index Corruption**: Rebuild from S3 backup
- **Feature Extraction Timeout**: Return text search results

### Pin Upload Resilience
- **S3 Upload Failure**: Retry with exponential backoff
- **Vision API Timeout**: Store pin without visual features
- **HBase Write Error**: Queue for async retry
- **Graph Update Failure**: Add to reconciliation queue

*Sources: Pinterest Engineering blog posts on PinSage, visual search infrastructure talks, mobile performance optimization case studies*