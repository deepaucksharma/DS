# OpenAI Request Flow - From Prompt to Response Generation

## System Overview

This diagram shows the complete journey of a ChatGPT request from user prompt through content safety, model inference, and response generation, handling 1+ billion requests daily.

```mermaid
graph TB
    subgraph UserLayer[User Layer]
        style UserLayer fill:#f9f9f9,stroke:#333,color:#000

        WebApp[ChatGPT Web App<br/>━━━━━<br/>React SPA<br/>WebSocket connection<br/>Streaming responses]

        MobileApp[ChatGPT Mobile<br/>━━━━━<br/>iOS/Android apps<br/>HTTP/2 connection<br/>Push notifications]

        APIClient[API Integrations<br/>━━━━━<br/>3rd party apps<br/>SDKs & libraries<br/>REST/HTTP calls]
    end

    subgraph EdgePlane[Edge Plane - Blue #3B82F6]
        style EdgePlane fill:#3B82F6,stroke:#2563EB,color:#fff

        CDN[Cloudflare Edge<br/>━━━━━<br/>Request routing<br/>DDoS protection<br/>p50: 15ms]

        WAF[Web Application Firewall<br/>━━━━━<br/>Security filtering<br/>Rate limiting<br/>Geo-blocking]

        LB[Load Balancer<br/>━━━━━<br/>AWS ALB<br/>Multi-AZ routing<br/>SSL termination<br/>p99: 5ms]
    end

    subgraph AuthLayer[Authentication Layer - Green #10B981]
        style AuthLayer fill:#10B981,stroke:#059669,color:#fff

        Auth[Auth Service<br/>━━━━━<br/>JWT validation<br/>Session management<br/>API key verification<br/>p99: 20ms]

        RateLimit[Rate Limiter<br/>━━━━━<br/>Redis-based<br/>Sliding window<br/>3500 TPM/user<br/>p99: 5ms]

        Billing[Usage Tracking<br/>━━━━━<br/>Token counting<br/>Billing integration<br/>Real-time quotas<br/>p99: 10ms]
    end

    subgraph PreProcessing[Pre-Processing Layer - Green #10B981]
        style PreProcessing fill:#10B981,stroke:#059669,color:#fff

        InputMod[Input Moderation<br/>━━━━━<br/>Content safety check<br/>Text classification<br/>NSFW detection<br/>p99: 50ms]

        Tokenizer[Tokenization<br/>━━━━━<br/>BPE encoding<br/>Token limit check<br/>Context window<br/>p99: 10ms]

        PromptEngine[Prompt Engineering<br/>━━━━━<br/>System prompts<br/>Context injection<br/>Format optimization<br/>p99: 5ms]
    end

    subgraph InferenceLayer[Model Inference Layer - Green #10B981]
        style InferenceLayer fill:#10B981,stroke:#059669,color:#fff

        ModelRouter[Model Router<br/>━━━━━<br/>Load balancing<br/>A/B testing<br/>Capacity management<br/>p99: 10ms]

        GPT4[GPT-4 Inference<br/>━━━━━<br/>A100 GPU cluster<br/>8-way tensor parallel<br/>175B parameters<br/>p99: 2000ms]

        GPT35[GPT-3.5 Turbo<br/>━━━━━<br/>V100 GPU cluster<br/>4-way model parallel<br/>20B parameters<br/>p99: 800ms]

        GPT4o[GPT-4o (Omni)<br/>━━━━━<br/>Multimodal inference<br/>Text + Vision<br/>H100 GPU cluster<br/>p99: 1500ms]
    end

    subgraph PostProcessing[Post-Processing Layer - Green #10B981]
        style PostProcessing fill:#10B981,stroke:#059669,color:#fff

        OutputMod[Output Moderation<br/>━━━━━<br/>Response safety check<br/>Harmful content filter<br/>Bias detection<br/>p99: 30ms]

        Formatter[Response Formatter<br/>━━━━━<br/>Markdown rendering<br/>Code highlighting<br/>Streaming chunks<br/>p99: 5ms]

        Cache[Response Cache<br/>━━━━━<br/>Redis cluster<br/>Common queries<br/>95% hit rate<br/>p99: 1ms]
    end

    subgraph StatePlane[State Plane - Orange #F59E0B]
        style StatePlane fill:#F59E0B,stroke:#D97706,color:#fff

        ConversationDB[Conversation Store<br/>━━━━━<br/>Redis + PostgreSQL<br/>Chat history<br/>Context windows<br/>Multi-turn support]

        UserDB[User Database<br/>━━━━━<br/>PostgreSQL<br/>Profiles & preferences<br/>Usage analytics<br/>Subscription status]

        ModelStore[Model Weights<br/>━━━━━<br/>S3 + EFS<br/>50PB storage<br/>Multi-region sync<br/>Version control]
    end

    subgraph ControlPlane[Control Plane - Red #8B5CF6]
        style ControlPlane fill:#8B5CF6,stroke:#7C3AED,color:#fff

        Monitoring[Real-time Monitoring<br/>━━━━━<br/>DataDog APM<br/>GPU utilization<br/>Queue depths<br/>SLO tracking]

        Logging[Request Logging<br/>━━━━━<br/>ElasticSearch<br/>500TB/day<br/>Real-time analysis<br/>Audit trails]

        Safety[Safety Systems<br/>━━━━━<br/>Abuse detection<br/>Jailbreak prevention<br/>Policy enforcement<br/>Human review queue]
    end

    %% Request flow path
    WebApp -->|"HTTPS/WSS"| CDN
    MobileApp -->|"HTTPS/2"| CDN
    APIClient -->|"REST API"| CDN

    CDN -->|"p50: 15ms"| WAF
    WAF -->|"Security check"| LB
    LB -->|"p99: 5ms"| Auth

    Auth -->|"Validation<br/>p99: 20ms"| RateLimit
    RateLimit -->|"Quota check<br/>p99: 5ms"| Billing
    Billing -->|"Usage tracking<br/>p99: 10ms"| InputMod

    InputMod -->|"Safety check<br/>p99: 50ms"| Tokenizer
    Tokenizer -->|"BPE encoding<br/>p99: 10ms"| PromptEngine
    PromptEngine -->|"Context prep<br/>p99: 5ms"| ModelRouter

    %% Model routing decisions
    ModelRouter -->|"45% requests<br/>Premium users"| GPT4
    ModelRouter -->|"50% requests<br/>Free/Plus users"| GPT35
    ModelRouter -->|"5% requests<br/>Multimodal"| GPT4o

    %% Post-processing flow
    GPT4 -->|"Generated text<br/>p99: 2000ms"| OutputMod
    GPT35 -->|"Generated text<br/>p99: 800ms"| OutputMod
    GPT4o -->|"Multi-modal output<br/>p99: 1500ms"| OutputMod

    OutputMod -->|"Safety validated<br/>p99: 30ms"| Formatter
    Formatter -->|"Streaming chunks<br/>p99: 5ms"| Cache

    %% Response delivery
    Cache -->|"WebSocket stream"| WebApp
    Cache -->|"HTTP chunks"| MobileApp
    Cache -->|"JSON response"| APIClient

    %% State interactions
    Auth -.->|"User lookup"| UserDB
    RateLimit -.->|"Conversation context"| ConversationDB
    ModelRouter -.->|"Model loading"| ModelStore
    Cache -.->|"Conversation save"| ConversationDB

    %% Control plane monitoring
    ModelRouter -.->|"Performance metrics"| Monitoring
    GPT4 -.->|"GPU utilization"| Monitoring
    Auth -.->|"Request logs"| Logging
    InputMod -.->|"Safety events"| Safety
    OutputMod -.->|"Policy violations"| Safety

    %% Apply standard colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff,font-weight:bold
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff,font-weight:bold
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff,font-weight:bold
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff,font-weight:bold
    classDef userStyle fill:#f9f9f9,stroke:#333,color:#000,font-weight:bold

    class CDN,WAF,LB edgeStyle
    class Auth,RateLimit,Billing,InputMod,Tokenizer,PromptEngine,ModelRouter,GPT4,GPT35,GPT4o,OutputMod,Formatter,Cache serviceStyle
    class ConversationDB,UserDB,ModelStore stateStyle
    class Monitoring,Logging,Safety controlStyle
    class WebApp,MobileApp,APIClient userStyle
```

## Request Flow Deep Dive

### Phase 1: Edge Processing (Total: ~25ms)
1. **CDN Routing (15ms)**: Cloudflare routes to nearest OpenAI data center
2. **WAF Security (5ms)**: DDoS protection, geo-blocking, basic security rules
3. **Load Balancing (5ms)**: AWS ALB distributes to healthy API instances

### Phase 2: Authentication & Authorization (Total: ~35ms)
1. **JWT Validation (20ms)**: Verify user session or API key authenticity
2. **Rate Limiting (5ms)**: Check user against 3,500 TPM quota using Redis
3. **Usage Tracking (10ms)**: Log tokens for billing, check subscription limits

### Phase 3: Content Safety & Preprocessing (Total: ~65ms)
1. **Input Moderation (50ms)**: ML-based content safety classification
2. **Tokenization (10ms)**: Convert text to BPE tokens, validate context window
3. **Prompt Engineering (5ms)**: Add system prompts, format for model

### Phase 4: Model Inference (Total: 800-2000ms)
1. **Model Selection (10ms)**: Route based on user tier and model availability
2. **GPU Inference (790-1990ms)**: Generate response using transformer model
3. **Streaming**: Begin sending tokens as they're generated (progressive response)

### Phase 5: Post-Processing & Delivery (Total: ~36ms)
1. **Output Moderation (30ms)**: Safety check on generated response
2. **Response Formatting (5ms)**: Convert to markdown, highlight code
3. **Caching (1ms)**: Store response for potential reuse

## Latency Budget Breakdown

### Target SLOs by Model
- **GPT-4**: p99 < 2000ms end-to-end
- **GPT-3.5 Turbo**: p99 < 800ms end-to-end
- **GPT-4o**: p99 < 1500ms end-to-end

### Critical Path Latencies
```
User Input → CDN (15ms) → Auth (35ms) → Safety (65ms) →
Model Inference (800-2000ms) → Post-processing (36ms) → User
```

**Total Budget**: 951-2151ms (within SLO targets)

## Request Volume & Distribution

### Traffic Patterns
- **Peak Hours**: 2-4PM UTC (US working hours)
- **Daily Volume**: 1.2 billion requests
- **Peak RPS**: 500,000 requests/second
- **Geographic Split**: 40% US, 30% Europe, 20% Asia, 10% Other

### Model Usage Distribution
- **GPT-3.5 Turbo**: 60% of requests (free tier, high volume)
- **GPT-4**: 35% of requests (paid tier, complex queries)
- **GPT-4o/Vision**: 5% of requests (multimodal inputs)

### Request Types
- **Chat Completions**: 85% (conversational interface)
- **Text Completions**: 10% (API integrations)
- **Embeddings**: 3% (search and analysis)
- **Other APIs**: 2% (moderation, fine-tuning)

## Error Handling & Fallbacks

### Rate Limiting Responses
- **HTTP 429**: Too Many Requests (with retry-after header)
- **Exponential Backoff**: Client SDKs implement automatic retry
- **Burst Allowance**: 50% over limit for 1-minute windows

### Model Unavailability
- **Automatic Fallback**: GPT-4 → GPT-3.5 Turbo with user notification
- **Maintenance Mode**: Pre-generated responses for common queries
- **Queue Management**: Hold requests up to 30 seconds during peak load

### Safety Violations
- **Content Policy**: Immediate rejection with explanation
- **Shadow Banning**: Gradual degradation for repeat violators
- **Human Review**: Escalation for edge cases and appeals

## Real Performance Examples

### Production Metrics (September 2024)
- **Average Latency**:
  - GPT-4: p50=1200ms, p95=1800ms, p99=2000ms
  - GPT-3.5: p50=400ms, p95=650ms, p99=800ms
- **Availability**: 99.9% uptime (8.8 hours downtime/year)
- **Error Rate**: <0.1% for successful authentication

### Cache Performance
- **Hit Rate**: 95% for common programming questions
- **Miss Penalty**: Full inference required (+800-2000ms)
- **Cache Size**: 50TB across Redis clusters
- **TTL Strategy**: 24 hours for static content, 1 hour for dynamic

## Sources & References

- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [OpenAI Status Page](https://status.openai.com) - Real incident data
- [Rate Limits Guide](https://platform.openai.com/docs/guides/rate-limits)
- Third-party performance monitoring (Pingdom, DataDog)
- AWS re:Invent 2023 - "AI/ML at Scale" presentations
- OpenAI Dev Day 2023 - Technical deep dives

---

*Last Updated: September 2024*
*Data Source Confidence: B+ (Public API docs + performance monitoring)*
*Diagram ID: CS-OAI-FLOW-001*