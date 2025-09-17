# Comparison Matrices: Scale, Technology, and Architecture Patterns

## Scale Comparison Matrix

### User Scale & Traffic
| Company | Daily Active Users | Peak RPS | Data Volume | Geographic Reach |
|---------|-------------------|----------|-------------|------------------|
| **Netflix** | 238M subscribers | 1M+ API calls | 8+ PB/day | 190+ countries |
| **Uber** | 130M monthly | 10M+ peak | 100B+ events/day | 70+ countries |
| **Amazon** | 300M+ customers | 10M+ peak | Multiple PB/day | 200+ countries |
| **Google** | 4B+ users | 8.5B+ searches/day | Exabytes | Global |
| **Meta** | 3.96B users | 50M+ peak | 4+ PB/day | Global |
| **Stripe** | 3M+ websites | 1M+ TPS | TB scale | 135+ countries |
| **Airbnb** | 150M+ users | 100k+ peak | TB scale | 220+ countries |
| **Spotify** | 500M+ users | 500k+ peak | TB scale | 184 countries |
| **LinkedIn** | 950M+ users | 1M+ peak | PB scale | 200+ countries |
| **Discord** | 200M+ users | 25M+ msg/s | TB scale | Global |

### Infrastructure Scale
| Company | Servers/Instances | Data Centers | CDN PoPs | Network Capacity |
|---------|------------------|--------------|----------|------------------|
| **Netflix** | 10,000+ | 3 AWS regions | 13,000+ edge | 200+ Tbps |
| **Uber** | 100,000+ | 8 regions | N/A | 100+ Tbps |
| **Amazon** | 1M+ | 26 regions | 400+ CloudFront | 1000+ Tbps |
| **Google** | 2.5M+ | 35+ regions | 1000+ | 10,000+ Tbps |
| **Meta** | 1M+ | 21 regions | 1000+ | 1000+ Tbps |
| **Stripe** | 10,000+ | Multi-cloud | CDN partners | 10+ Tbps |
| **Airbnb** | 50,000+ | Multi-cloud | CDN partners | 50+ Tbps |
| **Spotify** | 100,000+ | Multi-cloud | CDN partners | 100+ Tbps |
| **LinkedIn** | 50,000+ | 4 regions | CDN partners | 50+ Tbps |
| **Discord** | 100,000+ | 13 regions | CloudFlare | 10+ Tbps |

## Technology Stack Comparison

### Programming Languages
| Company | Primary Languages | Secondary Languages | Specialized Use Cases |
|---------|------------------|--------------------|--------------------|
| **Netflix** | Java, Python | JavaScript, Go, Scala | Java (services), Python (ML) |
| **Uber** | Go, Java | Python, JavaScript, C++ | Go (services), Python (ML), C++ (maps) |
| **Amazon** | Java, C++ | Python, JavaScript | Java (services), C++ (performance) |
| **Google** | C++, Java | Python, Go, JavaScript | C++ (core), Java (services), Go (infrastructure) |
| **Meta** | C++, Python | JavaScript, Rust, Erlang | C++ (core), Python (ML), Rust (performance) |
| **Stripe** | Ruby, Java | JavaScript, Go | Ruby (core), Java (payments) |
| **Airbnb** | Ruby, Java | JavaScript, Python | Ruby (web), Java (services), Python (ML) |
| **Spotify** | Java, Python | JavaScript, C++ | Java (backend), Python (ML), C++ (audio) |
| **LinkedIn** | Java, Scala | Python, JavaScript | Java (services), Scala (data), Python (ML) |
| **Discord** | JavaScript, Rust | Python, Go | JavaScript (Node.js), Rust (performance) |

### Database Technologies
| Company | Primary DB | Time Series | Caching | Search | Analytics |
|---------|-----------|-------------|---------|--------|-----------|
| **Netflix** | Cassandra, MySQL | Cassandra | EVCache, Redis | Elasticsearch | S3, Redshift |
| **Uber** | MySQL, Cassandra | Cassandra | Redis | Elasticsearch | Pinot, HDFS |
| **Amazon** | DynamoDB, MySQL | DynamoDB | ElastiCache | CloudSearch | Redshift, S3 |
| **Google** | Spanner, Bigtable | Bigtable | Memcache | Custom | BigQuery |
| **Meta** | MySQL, Cassandra | Scribe | TAO, Memcache | Custom | Presto, Scuba |
| **Stripe** | PostgreSQL | InfluxDB | Redis | Elasticsearch | BigQuery |
| **Airbnb** | MySQL, Cassandra | InfluxDB | Redis | Elasticsearch | Airflow, Spark |
| **Spotify** | Cassandra, PostgreSQL | Cassandra | Redis | Elasticsearch | BigQuery, Hadoop |
| **LinkedIn** | Espresso, MySQL | Kafka | Couchbase | Galene | Pinot, Hadoop |
| **Discord** | Cassandra, PostgreSQL | Cassandra | Redis | Elasticsearch | ClickHouse |

### Message Queues & Streaming
| Company | Primary Queue | Streaming Platform | Event Processing | Protocol |
|---------|--------------|-------------------|------------------|----------|
| **Netflix** | SQS, Kafka | Kafka, Kinesis | Mantis | HTTP, gRPC |
| **Uber** | Kafka | Kafka | Flink | gRPC, HTTP |
| **Amazon** | SQS | Kinesis | Lambda, Kinesis Analytics | HTTP, gRPC |
| **Google** | Pub/Sub | Dataflow | Dataflow | gRPC, HTTP |
| **Meta** | Custom queues | Streaming systems | Custom processors | Thrift, HTTP |
| **Stripe** | RabbitMQ | Kafka | Custom | HTTP, gRPC |
| **Airbnb** | Kafka | Kafka | Spark Streaming | HTTP, gRPC |
| **Spotify** | Kafka | Kafka | Storm, Flink | HTTP, gRPC |
| **LinkedIn** | Kafka | Kafka | Samza | HTTP, REST |
| **Discord** | Custom queues | Custom streaming | Elixir/Erlang | WebSocket, HTTP |

## Architecture Patterns Comparison

### Primary Architectural Patterns
| Company | Primary Pattern | Service Count | Communication | Data Consistency |
|---------|----------------|---------------|---------------|------------------|
| **Netflix** | Microservices | 1,000+ | HTTP, gRPC | Eventual |
| **Uber** | Event-Driven MS | 4,000+ | gRPC, Events | Mixed |
| **Amazon** | SOA/Microservices | 100,000+ | HTTP, SQS | Mixed |
| **Google** | Distributed Monoliths | 1,000+ | gRPC | Strong (Spanner) |
| **Meta** | Microservices | 10,000+ | Thrift, HTTP | Mixed |
| **Stripe** | Monolith + Services | 100+ | HTTP, gRPC | Strong |
| **Airbnb** | Microservices | 1,000+ | HTTP, gRPC | Eventual |
| **Spotify** | Microservices | 1,000+ | HTTP, gRPC | Eventual |
| **LinkedIn** | Microservices | 1,000+ | HTTP, Kafka | Mixed |
| **Discord** | Actor Model | 100+ | WebSocket, Elixir | Eventual |

### Resilience Patterns
| Company | Circuit Breaker | Load Shedding | Chaos Engineering | Regional Failover |
|---------|----------------|---------------|-------------------|-------------------|
| **Netflix** | Hystrix ✅ | ✅ Advanced | Chaos Monkey ✅ | ✅ Multi-region |
| **Uber** | Custom ✅ | ✅ Advanced | Custom tools ✅ | ✅ Regional |
| **Amazon** | ✅ Built-in | ✅ Advanced | GameDays ✅ | ✅ Multi-region |
| **Google** | ✅ Built-in | ✅ Advanced | DiRT ✅ | ✅ Global |
| **Meta** | ✅ Custom | ✅ Advanced | Custom ✅ | ✅ Multi-region |
| **Stripe** | ✅ Custom | ✅ Basic | Limited ✅ | ✅ Multi-region |
| **Airbnb** | ✅ Standard | ✅ Basic | Basic ✅ | ✅ Multi-region |
| **Spotify** | ✅ Standard | ✅ Basic | Basic ✅ | ✅ Multi-region |
| **LinkedIn** | ✅ Standard | ✅ Advanced | Limited ✅ | ✅ Multi-region |
| **Discord** | ✅ Erlang OTP | ✅ Advanced | Limited ✅ | ✅ Regional |

### Data Management Patterns
| Company | CQRS | Event Sourcing | Sharding Strategy | Caching Layers |
|---------|------|----------------|-------------------|----------------|
| **Netflix** | ✅ Selective | ✅ Limited | Geographic | L1/L2/Edge |
| **Uber** | ✅ Extensive | ✅ Trip data | Geospatial | Multi-tier |
| **Amazon** | ✅ Extensive | ✅ Order data | Hash-based | Multi-tier |
| **Google** | ✅ Built-in | ✅ Limited | Range-based | Multi-tier |
| **Meta** | ✅ Selective | ✅ Social data | User-based | TAO + Edge |
| **Stripe** | ✅ Payment flows | ✅ Transactions | Account-based | Multi-tier |
| **Airbnb** | ✅ Booking flows | ✅ Limited | Geographic | Multi-tier |
| **Spotify** | ✅ Playback | ✅ Limited | User-based | Multi-tier |
| **LinkedIn** | ✅ Social graph | ✅ Activity | Member-based | Multi-tier |
| **Discord** | ✅ Messages | ✅ Guild state | Guild-based | Multi-tier |

## Performance Characteristics

### Latency Requirements
| Company | P95 Latency | P99 Latency | Critical Path | Optimization Focus |
|---------|-------------|-------------|---------------|-------------------|
| **Netflix** | < 100ms | < 200ms | Video start | CDN optimization |
| **Uber** | < 500ms | < 1s | Dispatch | Geospatial queries |
| **Amazon** | < 100ms | < 200ms | Product page | Caching |
| **Google** | < 100ms | < 200ms | Search results | Index efficiency |
| **Meta** | < 100ms | < 300ms | Feed loading | Edge caching |
| **Stripe** | < 50ms | < 100ms | Payment auth | Database optimization |
| **Airbnb** | < 200ms | < 500ms | Search results | Search optimization |
| **Spotify** | < 100ms | < 200ms | Track start | Audio caching |
| **LinkedIn** | < 200ms | < 500ms | Feed loading | Social graph cache |
| **Discord** | < 50ms | < 100ms | Message delivery | WebSocket optimization |

### Availability Targets
| Company | SLA Target | Actual Uptime | Downtime Budget | Recovery Strategy |
|---------|------------|---------------|-----------------|-------------------|
| **Netflix** | 99.99% | 99.97% | 4.3m/month | Regional failover |
| **Uber** | 99.95% | 99.9% | 21.6m/month | Service degradation |
| **Amazon** | 99.95% | 99.99% | 21.6m/month | Cell isolation |
| **Google** | 99.95% | 99.99% | 21.6m/month | Global failover |
| **Meta** | 99.9% | 99.9% | 43.2m/month | Graceful degradation |
| **Stripe** | 99.99% | 99.99% | 4.3m/month | Multi-region |
| **Airbnb** | 99.9% | 99.95% | 43.2m/month | Service isolation |
| **Spotify** | 99.9% | 99.95% | 43.2m/month | Music-first priority |
| **LinkedIn** | 99.9% | 99.9% | 43.2m/month | Core feature priority |
| **Discord** | 99.9% | 99.8% | 43.2m/month | Guild isolation |

## Cost Efficiency Analysis

### Infrastructure Cost per User
| Company | Monthly Cost/User | Primary Cost Driver | Optimization Strategy |
|---------|------------------|--------------------|--------------------|
| **Netflix** | $8-10 | CDN bandwidth | Open Connect CDN |
| **Uber** | $0.50-1.00 | Real-time processing | Algorithm optimization |
| **Amazon** | $2-5 | Storage + compute | Reserved instances |
| **Google** | $5-10 | Index computation | Custom hardware |
| **Meta** | $3-8 | Storage + ML | Efficiency at scale |
| **Stripe** | $0.10-0.50 | Compliance + security | Shared infrastructure |
| **Airbnb** | $1-3 | Search + matching | Caching optimization |
| **Spotify** | $2-5 | Audio delivery | CDN optimization |
| **LinkedIn** | $1-3 | Social graph compute | Graph optimization |
| **Discord** | $0.50-1.50 | Real-time messaging | Efficient protocols |

### Engineering Cost Efficiency
| Company | Engineers per Service | Cost per Feature | Release Frequency |
|---------|----------------------|------------------|-------------------|
| **Netflix** | 3-5 | Medium | 4,000/day |
| **Uber** | 8-12 | High | 1,000/day |
| **Amazon** | 5-8 | Medium | 50M/year |
| **Google** | 10-15 | High | Weekly |
| **Meta** | 8-12 | High | Daily |
| **Stripe** | 15-25 | Very High | Weekly |
| **Airbnb** | 8-12 | High | Daily |
| **Spotify** | 8-12 | Medium | Daily |
| **LinkedIn** | 10-15 | High | Daily |
| **Discord** | 5-8 | Low | Daily |

## Innovation Impact Matrix

### Industry Contributions
| Company | Open Source Impact | Standards Influence | Pattern Innovation | Academic Citations |
|---------|-------------------|--------------------|--------------------|-------------------|
| **Netflix** | High (Hystrix, Zuul) | Medium | Very High | 1,000+ |
| **Uber** | Very High (H3, Jaeger) | High | Very High | 500+ |
| **Amazon** | High (Cloud patterns) | Very High | Very High | 2,000+ |
| **Google** | Very High (K8s, gRPC) | Very High | Very High | 5,000+ |
| **Meta** | High (React, GraphQL) | High | Very High | 1,500+ |
| **Stripe** | Medium | Medium (Payments) | High | 200+ |
| **Airbnb** | Medium (Airflow) | Low | Medium | 300+ |
| **Spotify** | Low | Low | Medium | 100+ |
| **LinkedIn** | High (Kafka, Pinot) | Medium | High | 400+ |
| **Discord** | Low | Low | Medium | 50+ |

### Technology Adoption Trends
| Pattern/Technology | Pioneer | Early Adopters | Current Adoption |
|-------------------|---------|----------------|------------------|
| **Microservices** | Amazon | Netflix, Uber | Universal |
| **Circuit Breakers** | Netflix | Uber, LinkedIn | Universal |
| **Event Sourcing** | Amazon | Uber, Stripe | High |
| **CQRS** | Amazon | Netflix, Uber | High |
| **Chaos Engineering** | Netflix | Uber, Amazon | Medium |
| **Geospatial Indexing** | Uber | Airbnb, Discord | Growing |
| **Real-time ML** | Netflix | Uber, Spotify | Growing |
| **Multi-region Active** | Google | Amazon, Netflix | Growing |

This comparison matrix reveals patterns in how companies at different scales approach similar technical challenges, providing insights for architectural decision-making based on scale, requirements, and organizational context.

*Last Updated: 2024-09-18*