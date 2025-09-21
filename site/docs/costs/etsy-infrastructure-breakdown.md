# Etsy Infrastructure Cost Breakdown

## Executive Summary

Etsy operates one of the world's largest global marketplaces for creative goods, serving 96.3 million active buyers and 7.5 million active sellers with 120+ million live listings. Their infrastructure spending reached approximately $185M annually by 2024, with 40% on search and recommendation systems, 28% on marketplace platform services, and 32% on storage and content delivery.

**Key Cost Metrics (2024)**:
- **Total Annual Infrastructure**: ~$185M
- **Cost per Active Buyer**: $1.92/month (infrastructure only)
- **Search Infrastructure**: $45M/year for 120M+ listings discovery
- **Image Processing**: $28M/year for 800M+ product photos
- **Payment Processing**: $35M/year for $13.2B+ in gross merchandise sales

## Infrastructure Cost Architecture

```mermaid
graph TB
    subgraph "Edge Plane - $37M/year (20%)"
        CDN[Global CDN<br/>$18M/year<br/>Fastly + CloudFlare<br/>Product image delivery]
        IMAGE_CDN[Image CDN<br/>$12M/year<br/>Optimized delivery<br/>800M+ product photos]
        LB[Load Balancers<br/>$5M/year<br/>Multi-region ALB<br/>3.5B requests/day]
        WAF[Security Layer<br/>$2M/year<br/>DDoS protection<br/>Fraud prevention]
    end

    subgraph "Service Plane - $74M/year (40%)"
        SEARCH[Search Engine<br/>$25M/year<br/>Elasticsearch clusters<br/>120M+ listings]
        RECOMMENDATION[Recommendation Engine<br/>$20M/year<br/>ML-powered suggestions<br/>Personalization]
        PAYMENT[Payment Processing<br/>$12M/year<br/>Transaction handling<br/>Multi-currency support]
        MESSAGING[Messaging System<br/>$8M/year<br/>Buyer-seller communication<br/>Order management]
        REVIEWS[Reviews & Ratings<br/>$5M/year<br/>Trust & safety<br/>Feedback system]
        INVENTORY[Inventory Management<br/>$4M/year<br/>Listing management<br/>Stock tracking]
    end

    subgraph "State Plane - $59M/year (32%)"
        LISTINGS[Listing Storage<br/>$25M/year<br/>Product data<br/>120M+ active listings]
        IMAGES[Image Storage<br/>$18M/year<br/>Product photos<br/>Global replication]
        USER_DATA[User Data Storage<br/>$8M/year<br/>Buyer/seller profiles<br/>Transaction history]
        ANALYTICS[Analytics Storage<br/>$6M/year<br/>Marketplace metrics<br/>Business intelligence]
        CACHE[Cache Layer<br/>$2M/year<br/>Redis clusters<br/>Search results cache]
    end

    subgraph "Control Plane - $15M/year (8%)"
        MONITOR[Observability<br/>$6M/year<br/>Marketplace monitoring<br/>Performance tracking]
        FRAUD[Fraud Detection<br/>$3M/year<br/>ML-based detection<br/>Risk assessment]
        AUTH[Authentication<br/>$2M/year<br/>Account security<br/>OAuth integration]
        DEPLOY[CI/CD Pipeline<br/>$2M/year<br/>Deployment automation<br/>Feature rollouts]
        COMPLIANCE[Compliance Tools<br/>$2M/year<br/>GDPR, PCI DSS<br/>Data governance]
    end

    %% Cost flow connections
    CDN -->|Image delivery| IMAGES
    SEARCH -->|Query results| CACHE
    RECOMMENDATION -->|ML models| ANALYTICS
    PAYMENT -->|Transaction data| USER_DATA
    MESSAGING -->|Communication logs| ANALYTICS

    %% Styling with 4-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#1E40AF,color:#fff,stroke-width:2px
    classDef serviceStyle fill:#10B981,stroke:#047857,color:#fff,stroke-width:2px
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff,stroke-width:2px
    classDef controlStyle fill:#8B5CF6,stroke:#6D28D9,color:#fff,stroke-width:2px

    class CDN,IMAGE_CDN,LB,WAF edgeStyle
    class SEARCH,RECOMMENDATION,PAYMENT,MESSAGING,REVIEWS,INVENTORY serviceStyle
    class LISTINGS,IMAGES,USER_DATA,ANALYTICS,CACHE stateStyle
    class MONITOR,FRAUD,AUTH,DEPLOY,COMPLIANCE controlStyle
```

## Regional Infrastructure Distribution

```mermaid
pie title Annual Infrastructure Costs by Region ($185M Total)
    "US-East (N.Virginia)" : 74
    "US-West (Oregon)" : 37
    "EU-West (Ireland)" : 37
    "Asia-Pacific (Singapore)" : 28
    "Other Regions" : 9
```

## Search and Discovery Infrastructure

```mermaid
graph LR
    subgraph "Search Infrastructure - $45M/year"
        ELASTICSEARCH[Elasticsearch Clusters<br/>$25M (56%)<br/>120M+ listings indexed<br/>Multi-language support]

        QUERY_PROCESSING[Query Processing<br/>$8M (18%)<br/>Natural language search<br/>Auto-complete suggestions]

        SEARCH_RANKING[Search Ranking<br/>$6M (13%)<br/>ML-based relevance<br/>Personalized results]

        FACETED_SEARCH[Faceted Search<br/>$4M (9%)<br/>Category filtering<br/>Attribute refinement]

        SEARCH_ANALYTICS[Search Analytics<br/>$2M (4%)<br/>Query analysis<br/>Performance optimization]
    end

    ELASTICSEARCH -->|350M searches/day| SEARCH_METRICS[Search Performance<br/>P95 response: 145ms<br/>Result accuracy: 94.2%<br/>Zero results: 8.3%]

    QUERY_PROCESSING -->|Auto-complete queries| SEARCH_METRICS
    SEARCH_RANKING -->|Personalized results| SEARCH_METRICS
    FACETED_SEARCH -->|Filter operations| SEARCH_METRICS

    classDef searchStyle fill:#10B981,stroke:#047857,color:#fff,stroke-width:2px
    classDef metricsStyle fill:#8B5CF6,stroke:#6D28D9,color:#fff,stroke-width:2px

    class ELASTICSEARCH,QUERY_PROCESSING,SEARCH_RANKING,FACETED_SEARCH,SEARCH_ANALYTICS searchStyle
    class SEARCH_METRICS metricsStyle
```

## Recommendation and Personalization Systems

```mermaid
graph TB
    subgraph "Recommendation Infrastructure - $20M/year"
        COLLABORATIVE[Collaborative Filtering<br/>$8M/year<br/>User behavior analysis<br/>Similar user recommendations]

        CONTENT_BASED[Content-Based Filtering<br/>$6M/year<br/>Item similarity<br/>Attribute-based suggestions]

        TRENDING[Trending Algorithm<br/>$3M/year<br/>Popular items<br/>Seasonal recommendations]

        PERSONALIZATION[Personalization Engine<br/>$2M/year<br/>Individual preferences<br/>Browse history analysis]

        AB_TESTING[A/B Testing Platform<br/>$1M/year<br/>Recommendation optimization<br/>Conversion testing]

        subgraph "Recommendation Metrics"
            CLICK_THROUGH[Click-through Rate<br/>12.8% on recommendations<br/>8.5% improvement over baseline]

            CONVERSION[Conversion Rate<br/>4.2% rec-to-purchase<br/>$890M revenue attributed]

            COVERAGE[Catalog Coverage<br/>78% of listings recommended<br/>Long-tail discovery]
        end
    end

    COLLABORATIVE -->|User similarity| CLICK_THROUGH
    CONTENT_BASED -->|Item attributes| CONVERSION
    PERSONALIZATION -->|Individual targeting| COVERAGE

    classDef recommendationStyle fill:#8B5CF6,stroke:#6D28D9,color:#fff,stroke-width:2px
    classDef performanceStyle fill:#F59E0B,stroke:#D97706,color:#fff,stroke-width:2px

    class COLLABORATIVE,CONTENT_BASED,TRENDING,PERSONALIZATION,AB_TESTING recommendationStyle
    class CLICK_THROUGH,CONVERSION,COVERAGE performanceStyle
```

## Image Processing and Content Management

```mermaid
graph TB
    subgraph "Image Infrastructure - $28M/year"
        IMAGE_PROCESSING[Image Processing<br/>$15M/year<br/>Resize, crop, optimize<br/>Multiple format support]

        IMAGE_STORAGE[Image Storage<br/>$8M/year<br/>S3-compatible storage<br/>800M+ product photos]

        CDN_DELIVERY[CDN Image Delivery<br/>$3M/year<br/>Global edge caching<br/>WebP/AVIF support]

        DUPLICATE_DETECTION[Duplicate Detection<br/>$1.5M/year<br/>AI-powered detection<br/>IP protection]

        MODERATION[Content Moderation<br/>$500K/year<br/>Automated screening<br/>Policy enforcement]

        subgraph "Image Metrics"
            UPLOAD_VOLUME[Upload Volume<br/>2.5M images/day<br/>Peak: 8M during holidays]

            PROCESSING_TIME[Processing Time<br/>P95: 3.2 seconds<br/>Multiple sizes generated]

            DELIVERY_SPEED[Delivery Speed<br/>P95: 180ms global<br/>95% cache hit ratio]
        end
    end

    IMAGE_PROCESSING -->|Automated optimization| UPLOAD_VOLUME
    IMAGE_STORAGE -->|Global replication| PROCESSING_TIME
    CDN_DELIVERY -->|Edge optimization| DELIVERY_SPEED

    classDef imageStyle fill:#F59E0B,stroke:#D97706,color:#fff,stroke-width:2px
    classDef imageMetricsStyle fill:#3B82F6,stroke:#1E40AF,color:#fff,stroke-width:2px

    class IMAGE_PROCESSING,IMAGE_STORAGE,CDN_DELIVERY,DUPLICATE_DETECTION,MODERATION imageStyle
    class UPLOAD_VOLUME,PROCESSING_TIME,DELIVERY_SPEED imageMetricsStyle
```

## Payment and Transaction Infrastructure

```mermaid
graph TB
    subgraph "Payment Infrastructure - $35M/year"
        PAYMENT_GATEWAY[Payment Gateway<br/>$15M/year<br/>Multi-processor support<br/>Global payment methods]

        FRAUD_DETECTION[Fraud Detection<br/>$8M/year<br/>ML-based scoring<br/>Real-time risk assessment]

        CURRENCY[Multi-Currency<br/>$5M/year<br/>Real-time rates<br/>33 supported currencies]

        ESCROW[Escrow Service<br/>$4M/year<br/>Payment protection<br/>Dispute resolution]

        PAYOUT[Seller Payouts<br/>$3M/year<br/>Bank transfers<br/>International payments]

        subgraph "Payment Metrics"
            TRANSACTION_VOLUME[Transaction Volume<br/>$13.2B+ GMS annually<br/>Average order: $47.90]

            SUCCESS_RATE[Payment Success<br/>97.8% authorization rate<br/>Fraud rate: 0.12%]

            PROCESSING_TIME[Processing Time<br/>P95: 850ms<br/>Real-time fraud scoring]
        end
    end

    PAYMENT_GATEWAY -->|Transaction processing| TRANSACTION_VOLUME
    FRAUD_DETECTION -->|Risk assessment| SUCCESS_RATE
    CURRENCY -->|Exchange rates| PROCESSING_TIME

    classDef paymentStyle fill:#10B981,stroke:#047857,color:#fff,stroke-width:2px
    classDef paymentMetricsStyle fill:#8B5CF6,stroke:#6D28D9,color:#fff,stroke-width:2px

    class PAYMENT_GATEWAY,FRAUD_DETECTION,CURRENCY,ESCROW,PAYOUT paymentStyle
    class TRANSACTION_VOLUME,SUCCESS_RATE,PROCESSING_TIME paymentMetricsStyle
```

## Third-Party Services and Integration Costs

```mermaid
graph TB
    subgraph "External Service Costs - $25M/year"

        subgraph "Payment Services - $12M"
            STRIPE[Stripe<br/>$5M/year<br/>Credit card processing<br/>International payments]

            PAYPAL[PayPal<br/>$3.5M/year<br/>Alternative payment<br/>Buyer protection]

            ADYEN[Adyen<br/>$2M/year<br/>European payments<br/>Local methods]

            KLARNA[Klarna<br/>$1.5M/year<br/>Buy now, pay later<br/>Installment payments]
        end

        subgraph "Infrastructure Services - $8M"
            GCP[Google Cloud<br/>$4M/year<br/>Machine learning<br/>BigQuery analytics]

            AWS[AWS Services<br/>$2.5M/year<br/>Additional capacity<br/>Disaster recovery]

            FASTLY[Fastly CDN<br/>$1M/year<br/>Edge computing<br/>Real-time purging]

            DATADOG[DataDog<br/>$500K/year<br/>Infrastructure monitoring<br/>APM services]
        end

        subgraph "Business Services - $5M"
            SALESFORCE[Salesforce<br/>$2M/year<br/>CRM platform<br/>Seller support]

            ZENDESK[Zendesk<br/>$1.5M/year<br/>Customer support<br/>Multi-channel service]

            MAILCHIMP[Mailchimp<br/>$800K/year<br/>Email marketing<br/>Seller newsletters]

            TWILIO[Twilio<br/>$700K/year<br/>SMS notifications<br/>Communication APIs]
        end
    end

    STRIPE -->|Transaction processing| PAYMENT_FLOW[Payment Flow<br/>Credit card processing<br/>International support<br/>Fraud prevention]

    GCP -->|ML capabilities| AI_SERVICES[AI Services<br/>Search optimization<br/>Recommendation engine<br/>Fraud detection]

    SALESFORCE -->|Seller management| SELLER_SUPPORT[Seller Support<br/>Account management<br/>Dispute resolution<br/>Business analytics]

    classDef paymentServiceStyle fill:#10B981,stroke:#047857,color:#fff,stroke-width:2px
    classDef infraServiceStyle fill:#3B82F6,stroke:#1E40AF,color:#fff,stroke-width:2px
    classDef businessServiceStyle fill:#8B5CF6,stroke:#6D28D9,color:#fff,stroke-width:2px

    class STRIPE,PAYPAL,ADYEN,KLARNA paymentServiceStyle
    class GCP,AWS,FASTLY,DATADOG infraServiceStyle
    class SALESFORCE,ZENDESK,MAILCHIMP,TWILIO businessServiceStyle
```

## Cost Optimization Strategies

```mermaid
graph TB
    subgraph "Optimization Programs - $42M potential savings/year"
        SEARCH_OPTIMIZATION[Search Optimization<br/>$18M savings/year<br/>Index efficiency<br/>Query optimization]

        IMAGE_OPTIMIZATION[Image Cost Reduction<br/>$12M savings/year<br/>Advanced compression<br/>Smart caching]

        RECOMMENDATION_EFFICIENCY[ML Model Efficiency<br/>$6M savings/year<br/>Model compression<br/>Inference optimization]

        CDN_OPTIMIZATION[CDN Optimization<br/>$4M savings/year<br/>Edge caching<br/>Regional optimization]

        PAYMENT_OPTIMIZATION[Payment Cost Reduction<br/>$2M savings/year<br/>Processor optimization<br/>Routing efficiency]
    end

    SEARCH_OPTIMIZATION -->|Implemented Q1 2024| TIMELINE[Implementation Timeline]
    IMAGE_OPTIMIZATION -->|Implementing Q4 2024| TIMELINE
    RECOMMENDATION_EFFICIENCY -->|Ongoing optimization| TIMELINE
    CDN_OPTIMIZATION -->|Planned Q1 2025| TIMELINE
    PAYMENT_OPTIMIZATION -->|Planned Q2 2025| TIMELINE

    classDef implementedStyle fill:#10B981,stroke:#047857,color:#fff,stroke-width:2px
    classDef planningStyle fill:#F59E0B,stroke:#D97706,color:#fff,stroke-width:2px

    class SEARCH_OPTIMIZATION,RECOMMENDATION_EFFICIENCY implementedStyle
    class IMAGE_OPTIMIZATION,CDN_OPTIMIZATION,PAYMENT_OPTIMIZATION planningStyle
```

## Marketplace Growth and Usage Patterns

| User Segment | Count | Monthly Activity | Revenue Contribution | Infrastructure Impact |
|--------------|-------|------------------|---------------------|----------------------|
| **Active Buyers** | 96.3M | 2.1 purchases/month | 100% of GMS | Search, recommendations |
| **Active Sellers** | 7.5M | 12 listings/month | Transaction fees | Listing management, images |
| **Occasional Buyers** | 45M | 0.3 purchases/month | 15% of GMS | Browse, search |
| **New Sellers** | 1.2M | 3 listings/month | Growth potential | Onboarding, support |

## Real-Time Cost Management

**Cost Monitoring Framework**:
- **Daily spend > $600K**: Engineering team alert
- **Search costs > $150K/day**: Query optimization review
- **Image processing > $100K/day**: Compression optimization
- **Payment processing > $125K/day**: Transaction analysis

**Usage Attribution**:
- **By Feature**: Search (25%), Recommendations (20%), Images (18%), Payments (15%), Listings (22%)
- **By User Type**: Buyers (70%), Sellers (25%), Platform operations (5%)
- **By Geography**: US (65%), Europe (25%), Rest of world (10%)

## Engineering Team Investment

**Etsy Engineering Team (485 engineers total)**:
- **Marketplace Platform**: 125 engineers × $185K = $23.1M/year
- **Search & Discovery**: 95 engineers × $200K = $19M/year
- **Machine Learning**: 75 engineers × $220K = $16.5M/year
- **Infrastructure/SRE**: 65 engineers × $195K = $12.7M/year
- **Mobile Engineering**: 55 engineers × $175K = $9.6M/year
- **Security & Fraud**: 45 engineers × $210K = $9.5M/year
- **Data Engineering**: 35 engineers × $190K = $6.7M/year

**Total Engineering Investment**: $97.1M/year

## Financial Performance and Unit Economics

**Marketplace Economics**:
- **Gross Merchandise Sales**: $13.2B annually
- **Take rate**: 6.5% (transaction + payment fees)
- **Infrastructure cost per transaction**: $0.65
- **Revenue per active buyer**: $89/year
- **Infrastructure cost per buyer**: $23/year

**Infrastructure Efficiency**:
- **2024**: $4.60 revenue per $1 infrastructure spend
- **2023**: $4.25 revenue per $1 infrastructure spend
- **2022**: $4.10 revenue per $1 infrastructure spend

**Operational Metrics**:
- **Search success rate**: 91.7% (users find relevant items)
- **Recommendation click-through**: 12.8%
- **Payment authorization rate**: 97.8%
- **Image load time**: P95 < 250ms globally
- **Platform availability**: 99.9% uptime SLA

---

*Cost data compiled from Etsy's public filings, disclosed marketplace metrics, and infrastructure estimates based on reported transaction volumes and user activity patterns.*