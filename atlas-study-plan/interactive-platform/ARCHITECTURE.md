# Atlas Interactive Learning Platform - System Architecture
## Complete Technical Architecture Document

### Executive Summary

This document provides a comprehensive architectural overview of the Atlas Interactive Learning Platform, detailing how all components integrate to deliver an immersive, scalable, and production-grade learning experience. The architecture is designed for 100,000+ concurrent users, 99.9% uptime, and sub-second response times.

---

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                              │
│  ┌──────────────────┐  ┌──────────────────┐                    │
│  │   Web App        │  │   Mobile App     │                    │
│  │   (React SPA)    │  │   (React Native) │                    │
│  └──────────────────┘  └──────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
                            ↓ HTTPS/WSS
┌─────────────────────────────────────────────────────────────────┐
│                         Edge Layer                               │
│  CloudFront CDN → AWS WAF → Route 53 → ALB                      │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                     API Gateway Layer                            │
│  ┌─────────────────┐  ┌─────────────────┐                      │
│  │  GraphQL API    │  │  WebSocket      │                      │
│  │  (Apollo Server)│  │  (Socket.io)    │                      │
│  └─────────────────┘  └─────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Service Layer                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │   Auth   │ │  Content │ │ Analytics│ │   Labs   │          │
│  │  Service │ │  Service │ │  Service │ │  Service │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                       │
│  │ AI Tutor │ │  Collab  │ │  Notif   │                       │
│  │  Service │ │  Service │ │  Service │                       │
│  └──────────┘ └──────────┘ └──────────┘                       │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                       Data Layer                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │PostgreSQL│ │  Redis   │ │    S3    │ │ InfluxDB │          │
│  │(Primary) │ │ (Cache)  │ │(Storage) │ │(Metrics) │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│  ┌──────────┐ ┌──────────┐                                     │
│  │ Pinecone │ │ RabbitMQ │                                     │
│  │(Vectors) │ │ (Queue)  │                                     │
│  └──────────┘ └──────────┘                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Component Details

### 1. Client Layer

#### Web Application
- **Framework**: React 18 with TypeScript
- **Rendering**: Client-side rendering (CSR) + SSR for landing pages
- **State**: Redux Toolkit + React Query
- **Routing**: React Router v6
- **Build**: Vite with code splitting
- **Deployment**: CloudFront + S3

**Key Features**:
- Interactive diagram viewer
- Lab environment interface
- AI tutor chat interface
- Analytics dashboard
- Study group collaboration

#### Mobile Application
- **Framework**: React Native with TypeScript
- **Navigation**: React Navigation v6
- **State**: Redux Toolkit (shared with web)
- **Storage**: Realm (offline-first)
- **Build**: EAS Build
- **Distribution**: App Store + Play Store

**Key Features**:
- Offline diagram access
- Micro-learning modules
- Push notifications
- Audio explanations
- Flashcard reviews

---

### 2. API Gateway Layer

#### GraphQL API (Apollo Server)
**Purpose**: Primary API for all client requests

**Schema Structure**:
```graphql
type Query {
  # User
  currentUser: User!
  userProgress(userId: ID!): Progress!

  # Content
  diagram(id: ID!): Diagram!
  diagrams(filter: DiagramFilter): [Diagram!]!
  lab(id: ID!): Lab!
  labs(filter: LabFilter): [Lab!]!

  # Analytics
  userMetrics(userId: ID!): Metrics!
  skillHeatmap(userId: ID!): SkillHeatmap!

  # AI Tutor
  conversation(conversationId: ID!): Conversation!
}

type Mutation {
  # Auth
  login(email: String!, password: String!): AuthPayload!
  register(input: RegisterInput!): AuthPayload!

  # Progress
  completeDiagram(diagramId: ID!): Progress!
  completeLab(labId: ID!, solution: String!): LabResult!

  # AI Tutor
  askQuestion(question: String!, context: ContextInput!): Answer!

  # Collaboration
  createStudyGroup(input: StudyGroupInput!): StudyGroup!
  joinStudyGroup(groupId: ID!): StudyGroup!
}

type Subscription {
  # Real-time updates
  progressUpdated(userId: ID!): Progress!
  groupMessageReceived(groupId: ID!): Message!
  labStatusChanged(labId: ID!): LabStatus!
}
```

**Features**:
- Field-level authorization
- DataLoader for N+1 optimization
- Query complexity analysis
- Rate limiting (100 req/min)
- Response caching (Redis)

#### WebSocket Server (Socket.io)
**Purpose**: Real-time collaboration and notifications

**Events**:
```typescript
// Client → Server
socket.emit('join-study-group', { groupId });
socket.emit('whiteboard-update', { groupId, drawing });
socket.emit('cursor-move', { diagramId, position });

// Server → Client
socket.on('group-message', (message) => {});
socket.on('whiteboard-sync', (state) => {});
socket.on('peer-cursor', (cursor) => {});
socket.on('notification', (notif) => {});
```

**Features**:
- Room-based communication
- Redis adapter for scaling
- Automatic reconnection
- Binary data support (whiteboard)

---

### 3. Service Layer

#### Auth Service (Node.js)
**Responsibilities**:
- User registration/login
- JWT generation and validation
- Password reset
- Email verification
- OAuth integration (Google, GitHub)

**API**: Internal gRPC
**Database**: PostgreSQL (users table)
**Cache**: Redis (sessions, tokens)

#### Content Service (Node.js)
**Responsibilities**:
- Diagram CRUD operations
- Lab management
- Content search
- Metadata enrichment

**API**: Internal gRPC + GraphQL resolvers
**Database**: PostgreSQL (diagrams, labs tables)
**Storage**: S3 (diagram images, lab files)
**Search**: PostgreSQL full-text search

#### Analytics Service (Python)
**Responsibilities**:
- Event ingestion
- Metrics calculation
- Predictions (ML models)
- Report generation

**API**: Internal gRPC
**Databases**:
- InfluxDB (time-series events)
- PostgreSQL (aggregated metrics)
**Queue**: RabbitMQ (event processing)

#### Labs Service (Go)
**Responsibilities**:
- Lab environment provisioning
- Kubernetes namespace management
- Resource monitoring
- Auto-cleanup

**API**: Internal gRPC
**Infrastructure**: Kubernetes API
**Monitoring**: Prometheus

#### AI Tutor Service (Python)
**Responsibilities**:
- Claude AI integration
- Context retrieval (RAG)
- Conversation management
- Response streaming

**API**: Internal gRPC + GraphQL resolvers
**AI**: Claude AI (Anthropic)
**Vector DB**: Pinecone
**Database**: PostgreSQL (conversations)

#### Collaboration Service (Node.js)
**Responsibilities**:
- Study group management
- Real-time whiteboard
- Chat message routing
- Peer matching

**API**: Internal gRPC + WebSocket
**Database**: PostgreSQL (groups, messages)
**Cache**: Redis (active sessions)

#### Notification Service (Node.js)
**Responsibilities**:
- Push notification delivery
- Email sending
- In-app notifications
- Notification preferences

**API**: Internal gRPC
**Push**: Firebase Cloud Messaging
**Email**: SendGrid
**Database**: PostgreSQL (notifications table)

---

### 4. Data Layer

#### PostgreSQL (Primary Database)
**Version**: 15+
**Configuration**:
- Instance: db.r6g.xlarge (4 vCPU, 32GB RAM)
- Replication: 1 primary + 2 read replicas
- Backup: Daily snapshots + PITR
- Connection Pooling: PgBouncer (500 connections)

**Tables**:
```sql
-- Core tables
users (id, email, password_hash, created_at, ...)
user_profiles (user_id, skill_level, mastery_score, ...)
progress (user_id, diagram_id, completed_at, ...)
labs_progress (user_id, lab_id, status, attempts, ...)

-- Content tables
diagrams (id, title, category, mermaid_source, ...)
labs (id, title, difficulty, instructions, ...)
incidents (id, company, title, description, ...)

-- Collaboration tables
study_groups (id, name, created_by, ...)
group_members (group_id, user_id, joined_at, ...)
messages (id, group_id, user_id, content, ...)

-- AI Tutor tables
conversations (id, user_id, started_at, ...)
conversation_messages (id, conversation_id, role, content, ...)

-- Analytics tables
user_metrics (user_id, metric_name, value, calculated_at, ...)
```

**Indexes**:
- B-tree on foreign keys
- GIN on full-text search columns
- Partial indexes on filtered queries

#### Redis (Cache & Queue)
**Version**: 7+
**Configuration**:
- Instance: cache.r6g.large (2 vCPU, 13GB RAM)
- Mode: Cluster (3 shards, 1 replica each)
- Eviction: LRU

**Use Cases**:
```
Cache:
  - User sessions (TTL: 1 hour)
  - API responses (TTL: 5 minutes)
  - Diagram metadata (TTL: 1 hour)

Queue:
  - BullMQ job queue
  - Email queue
  - Analytics event queue

Pub/Sub:
  - Real-time notifications
  - Cache invalidation
  - Service coordination
```

#### S3 (Object Storage)
**Buckets**:
```
atlas-content-production:
  - Diagram images
  - Lab files
  - Documentation
  Public: Yes (via CloudFront)
  Versioning: Enabled

atlas-user-data:
  - User uploads
  - Lab solutions
  - Profile images
  Public: No
  Encryption: AES-256

atlas-backups:
  - Database backups
  - Configuration backups
  Public: No
  Lifecycle: Archive to Glacier after 90 days
```

#### InfluxDB (Time-Series Metrics)
**Version**: 2.7+
**Configuration**:
- Instance: t3.medium (2 vCPU, 4GB RAM)
- Retention: 90 days (raw), 2 years (aggregated)

**Measurements**:
```
diagram_interactions:
  - user_id, diagram_id, interaction_type, timestamp

lab_events:
  - user_id, lab_id, event_type, timestamp

ai_tutor_queries:
  - user_id, question, response_time, tokens_used

system_metrics:
  - service_name, metric_name, value, timestamp
```

#### Pinecone (Vector Database)
**Purpose**: Semantic search for AI tutor

**Index Configuration**:
```yaml
Dimensions: 3072 (OpenAI text-embedding-3-large)
Metric: cosine similarity
Pods: 1 (p1.x1, 100K vectors)
Replicas: 2 (high availability)

Vectors:
  - 900 diagram embeddings
  - 100 lab embeddings
  - 100 incident embeddings
  Total: ~1,100 vectors
```

#### RabbitMQ (Message Queue)
**Version**: 3.12+
**Configuration**:
- Instance: t3.small (2 vCPU, 2GB RAM)
- Queues: Durable, persistent messages

**Queues**:
```
analytics-events: Process user activity
email-queue: Send emails asynchronously
lab-provisioning: Provision lab environments
notification-queue: Deliver notifications
ml-predictions: Run ML models
```

---

## 🔐 Security Architecture

### Authentication Flow
```
1. User submits credentials
   ↓
2. Auth Service validates
   ↓
3. Generate JWT (access + refresh)
   ↓
4. Store session in Redis
   ↓
5. Return tokens to client
   ↓
6. Client includes JWT in headers
   ↓
7. API Gateway validates JWT
   ↓
8. Route to appropriate service
```

### Authorization
- **Role-Based Access Control (RBAC)**
- **Attribute-Based Access Control (ABAC)** for fine-grained permissions
- **GraphQL field-level authorization**

### Data Protection
- **Encryption at rest**: AES-256 (PostgreSQL, S3)
- **Encryption in transit**: TLS 1.3
- **PII handling**: Separate encrypted tables
- **Secrets management**: AWS Secrets Manager

---

## 📊 Observability

### Monitoring Stack
```
Metrics Collection:
  - Prometheus (scrape interval: 15s)
  - CloudWatch (AWS resources)

Visualization:
  - Grafana dashboards
  - Custom analytics UI

Alerting:
  - PagerDuty (critical)
  - Slack (warnings)
  - Email (info)
```

### Logging Strategy
```
Application Logs:
  - Structured JSON logging
  - Correlation IDs for tracing
  - Log levels: ERROR, WARN, INFO, DEBUG

Log Aggregation:
  - Elasticsearch
  - Retention: 30 days

Log Analysis:
  - Kibana dashboards
  - Alerting on error patterns
```

### Distributed Tracing
```
Tool: Jaeger
Sampling: 10% in production
Instrumentation: OpenTelemetry

Trace Context:
  - User ID
  - Request ID
  - Service name
  - Operation name
```

---

## 🚀 Deployment Architecture

### Kubernetes Cluster
```yaml
Node Groups:
  General Purpose:
    - Instance: t3.medium
    - Count: 3-10 (autoscaling)
    - Workloads: API, services

  CPU Optimized:
    - Instance: c6i.xlarge
    - Count: 2-5 (autoscaling)
    - Workloads: Labs

  Memory Optimized:
    - Instance: r6i.xlarge
    - Count: 1-3 (autoscaling)
    - Workloads: Analytics, ML

Namespaces:
  - production
  - staging
  - lab-environments (per-user namespaces)

Ingress:
  - NGINX Ingress Controller
  - SSL/TLS termination
  - Rate limiting
```

### Deployment Strategy
```yaml
Strategy: Blue-Green

Steps:
  1. Deploy new version (green)
  2. Run smoke tests
  3. Route 10% traffic to green
  4. Monitor metrics (10 minutes)
  5. Route 50% traffic to green
  6. Monitor metrics (10 minutes)
  7. Route 100% traffic to green
  8. Terminate blue deployment

Rollback:
  - One-click rollback to blue
  - Automatic rollback on error rate spike
```

---

## 💰 Cost Optimization

### Current Costs (10,000 users)
```
Compute (Kubernetes): $3,200/month
Databases: $1,800/month
Storage: $400/month
Networking: $600/month
External Services: $2,000/month
Total: ~$8,000/month ($0.80/user)
```

### Optimization Strategies
1. **Reserved Instances**: 40% savings on compute
2. **Spot Instances**: 70% savings for lab environments
3. **Auto-scaling**: Scale down during off-hours
4. **Content Caching**: Reduce S3 requests by 80%
5. **Query Optimization**: Reduce database load

---

## 🔗 Related Documentation

- [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md) - 12-month implementation plan
- [infrastructure/01-TECH-STACK.md](./infrastructure/01-TECH-STACK.md) - Technology decisions
- [infrastructure/02-DEPLOYMENT.md](./infrastructure/02-DEPLOYMENT.md) - Deployment procedures
- [infrastructure/03-SCALING.md](./infrastructure/03-SCALING.md) - Scaling strategies

---

*"Architecture for scale. Design for resilience. Build for the future."*