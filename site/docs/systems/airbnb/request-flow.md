# Airbnb - Request Flow Architecture

## The Guest Journey: From Search to Stay in 12 Steps

This diagram shows how Airbnb processes a complete booking flow, from initial search through payment confirmation, handling millions of searches and thousands of bookings daily.

```mermaid
sequenceDiagram
    participant G as Guest<br/>Mobile/Web App<br/>200M+ registered users
    participant CF as CloudFlare<br/>Global CDN<br/>200+ PoPs<br/>Image optimization
    participant ALB as AWS ALB<br/>Load Balancer<br/>Multi-AZ<br/>Health checks
    participant API as API Gateway<br/>Kong Enterprise<br/>Rate limiting<br/>Authentication
    participant S as Search Service<br/>Elasticsearch<br/>ML ranking<br/>100M+ searches/day
    participant L as Listing Service<br/>MySQL cluster<br/>7M+ listings<br/>Real-time data
    participant R as Recommendation<br/>ML Engine<br/>TensorFlow<br/>Personalization
    participant P as Pricing Service<br/>Dynamic pricing<br/>Market analysis<br/>Revenue optimization
    participant B as Booking Service<br/>State machine<br/>12-step flow<br/>Transaction coordination
    participant Pay as Payment Service<br/>Multi-currency<br/>PCI compliant<br/>$50B+ GMV
    participant N as Notification<br/>Real-time messaging<br/>Push notifications<br/>Email/SMS
    participant A as Analytics<br/>Kafka pipeline<br/>Real-time events<br/>Business metrics

    Note over G,A: Search & Discovery Flow - p99: 300ms

    %% Search Request
    G->>+CF: Search request<br/>"Paris, 2 guests, Dec 15-20"
    CF->>+ALB: Route to nearest region<br/>Geographic optimization
    ALB->>+API: Load balance request<br/>Health check validation

    %% Authentication & Session
    API->>+API: Validate session<br/>JWT token verification<br/>User context loading
    API->>+S: Execute search query<br/>Location + dates + filters

    %% Search Processing
    S->>+L: Get available listings<br/>Geographic bounds + date range
    L-->>S: Return 2000+ candidates<br/>Basic availability check

    S->>+R: Request personalization<br/>User preferences + history
    R-->>S: Return ML rankings<br/>Personalized scoring

    %% Pricing & Results
    S->>+P: Get dynamic pricing<br/>Market rates + demand
    P-->>S: Return optimized prices<br/>Host revenue + guest value

    S-->>API: Return search results<br/>Top 50 ranked listings
    API-->>ALB: Search response<br/>JSON + image URLs
    ALB-->>CF: Cache & optimize<br/>CDN edge caching
    CF-->>G: Deliver results<br/>Sub-300ms response

    Note over G,A: Booking Request Flow - Critical Business Transaction

    %% Booking Initiation
    G->>+CF: Book listing request<br/>Listing ID + dates + guests
    CF->>+ALB: Route booking request<br/>Sticky session routing
    ALB->>+API: Forward to booking API<br/>Authentication required

    %% Booking Validation
    API->>+B: Start booking flow<br/>12-step state machine
    B->>+L: Validate availability<br/>Real-time availability check
    L-->>B: Confirm availability<br/>Lock calendar dates

    %% Pricing Calculation
    B->>+P: Calculate total price<br/>Base + fees + taxes
    P-->>B: Return breakdown<br/>Transparent pricing

    %% Payment Processing
    B->>+Pay: Process payment<br/>Guest payment method
    Pay->>Pay: Fraud detection<br/>ML risk assessment
    Pay->>Pay: Authorization<br/>Credit card/bank validation
    Pay-->>B: Payment confirmed<br/>Transaction reference

    %% Booking Confirmation
    B->>+N: Send confirmations<br/>Guest + host notifications
    N->>N: Generate messages<br/>Booking details + instructions
    N-->>G: Push notification<br/>Booking confirmed
    N->>Host: Host notification<br/>New booking alert

    %% Analytics & Tracking
    par Analytics Events
        B->>A: Booking completion<br/>Revenue tracking
    and Host Earnings
        B->>Host: Earnings update<br/>Payout scheduling
    and Guest Experience
        B->>Trip: Trip creation<br/>Itinerary management
    end

    Note over G,A: Response Time Breakdown (p99)
    Note over CF,ALB: CDN + Load Balancing: 50ms
    Note over API,S: Authentication + Search: 200ms
    Note over R,P: ML + Pricing: 100ms
    Note over B,Pay: Booking + Payment: 400ms
    Note over N,A: Notifications: 50ms
    Note over G,A: Total End-to-End: 800ms
```

## Search & Discovery Deep Dive

### ML-Powered Search Ranking

```mermaid
graph TB
    subgraph SearchPipeline[Search & Ranking Pipeline]
        subgraph QueryProcessing[Query Processing]
            QueryParser[Query Parser<br/>Location extraction<br/>Date normalization<br/>Filter validation<br/>Intent understanding]

            LocationService[Location Service<br/>Geocoding<br/>Boundary expansion<br/>Neighborhood mapping<br/>Points of interest]

            InventoryFilter[Inventory Filter<br/>Availability check<br/>Capacity matching<br/>Price range filter<br/>Amenity requirements]
        end

        subgraph CandidateGeneration[Candidate Generation]
            GeoSearch[Geographic Search<br/>Elasticsearch geo queries<br/>Distance sorting<br/>Boundary constraints<br/>10K+ candidates]

            AvailabilityCheck[Availability Check<br/>Calendar service lookup<br/>Real-time inventory<br/>Booking conflicts<br/>Instant book eligible]

            InitialRanking[Initial Ranking<br/>Basic scoring<br/>Distance + price<br/>Photo quality<br/>Host response rate]
        end

        subgraph MLRanking[ML-Powered Ranking]
            FeatureExtraction[Feature Extraction<br/>Listing features: 200+<br/>Host features: 50+<br/>Guest features: 100+<br/>Contextual features: 30+]

            RankingModel[Ranking Model<br/>XGBoost ensemble<br/>Click-through prediction<br/>Booking probability<br/>Revenue optimization]

            PersonalizationLayer[Personalization<br/>User preferences<br/>Search history<br/>Booking patterns<br/>Similar guest behavior]
        end

        subgraph ResultOptimization[Result Optimization]
            DiversityEngine[Diversity Engine<br/>Price range spread<br/>Property type mix<br/>Neighborhood variety<br/>Booking probability balance]

            BusinessRules[Business Rules<br/>Superhost promotion<br/>New listing boost<br/>Quality filters<br/>Policy compliance]

            FinalRanking[Final Ranking<br/>Top 50 results<br/>A/B test variants<br/>Business metrics<br/>User experience optimization]
        end
    end

    QueryParser --> LocationService
    LocationService --> InventoryFilter
    InventoryFilter --> GeoSearch

    GeoSearch --> AvailabilityCheck
    AvailabilityCheck --> InitialRanking
    InitialRanking --> FeatureExtraction

    FeatureExtraction --> RankingModel
    RankingModel --> PersonalizationLayer
    PersonalizationLayer --> DiversityEngine

    DiversityEngine --> BusinessRules
    BusinessRules --> FinalRanking

    classDef queryStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef candidateStyle fill:#10B981,stroke:#059669,color:#fff
    classDef mlStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef optimizeStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class QueryParser,LocationService,InventoryFilter queryStyle
    class GeoSearch,AvailabilityCheck,InitialRanking candidateStyle
    class FeatureExtraction,RankingModel,PersonalizationLayer mlStyle
    class DiversityEngine,BusinessRules,FinalRanking optimizeStyle
```

## Booking State Machine Architecture

### 12-Step Booking Process

```mermaid
stateDiagram-v2
    [*] --> SearchInitiated
    SearchInitiated --> ListingSelected: User clicks listing
    ListingSelected --> DetailsViewed: Load listing details
    DetailsViewed --> AvailabilityChecked: Select dates

    AvailabilityChecked --> BookingInitiated: Click "Reserve"
    BookingInitiated --> GuestInfoCollected: Enter guest details
    GuestInfoCollected --> PaymentInfoAdded: Add payment method
    PaymentInfoAdded --> PricingCalculated: Calculate total cost

    PricingCalculated --> HostApprovalRequired: Manual approval listing
    PricingCalculated --> PaymentProcessed: Instant Book listing

    HostApprovalRequired --> PaymentProcessed: Host approves
    HostApprovalRequired --> BookingCancelled: Host declines/timeout

    PaymentProcessed --> BookingConfirmed: Payment successful
    PaymentProcessed --> PaymentFailed: Payment declined

    PaymentFailed --> PaymentRetry: Update payment method
    PaymentRetry --> PaymentProcessed: Retry payment
    PaymentRetry --> BookingCancelled: Max retries exceeded

    BookingConfirmed --> TripCreated: Generate itinerary
    TripCreated --> NotificationsSent: Notify guest & host
    NotificationsSent --> [*]

    BookingCancelled --> [*]

    note right of AvailabilityChecked
        Real-time calendar check
        Prevent double bookings
        Lock dates for 15 minutes
    end note

    note right of PaymentProcessed
        PCI compliant processing
        Fraud detection ML
        Multi-currency support
        Host payout scheduling
    end note

    note right of HostApprovalRequired
        24-hour approval window
        Auto-decline after timeout
        Host notification queue
        Guest alternative suggestions
    end note
```

## Real-Time Availability Management

### Calendar Synchronization System

```mermaid
graph TB
    subgraph AvailabilitySystem[Real-Time Availability System]
        subgraph CalendarSources[Calendar Sources]
            AirbnbCalendar[Airbnb Calendar<br/>Primary source<br/>Real-time updates<br/>Instant Book rules]

            ExternalCalendars[External Calendars<br/>VRBO, Booking.com<br/>HomeAway sync<br/>iCal imports<br/>2-way sync]

            ManualBlocks[Manual Blocks<br/>Host maintenance<br/>Personal use<br/>Seasonal closures<br/>Price updates]
        end

        subgraph SyncEngine[Synchronization Engine]
            CalendarMerger[Calendar Merger<br/>Conflict resolution<br/>Priority rules<br/>Overlap detection<br/>Data validation]

            RealTimeUpdater[Real-Time Updater<br/>WebSocket updates<br/>Event streaming<br/>Cache invalidation<br/>Search reindexing]

            ConflictResolver[Conflict Resolver<br/>Booking conflicts<br/>Cancellation handling<br/>Date modifications<br/>Host communication]
        end

        subgraph AvailabilityAPI[Availability API]
            QuickCheck[Quick Availability Check<br/>Cache-first lookup<br/>Redis cluster<br/><10ms response<br/>99.9% accuracy]

            DetailedCheck[Detailed Availability<br/>Database verification<br/>Rule engine validation<br/>Pricing calculation<br/>Booking constraints]

            InventoryLocking[Inventory Locking<br/>15-minute booking holds<br/>Payment processing time<br/>Concurrent booking prevention<br/>Automatic release]
        end
    end

    AirbnbCalendar --> CalendarMerger
    ExternalCalendars --> CalendarMerger
    ManualBlocks --> CalendarMerger

    CalendarMerger --> RealTimeUpdater
    RealTimeUpdater --> ConflictResolver
    ConflictResolver --> QuickCheck

    QuickCheck --> DetailedCheck
    DetailedCheck --> InventoryLocking

    classDef sourceStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef syncStyle fill:#10B981,stroke:#059669,color:#fff
    classDef apiStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class AirbnbCalendar,ExternalCalendars,ManualBlocks sourceStyle
    class CalendarMerger,RealTimeUpdater,ConflictResolver syncStyle
    class QuickCheck,DetailedCheck,InventoryLocking apiStyle
```

## Performance Optimization Strategies

### CDN & Caching Strategy
- **CloudFlare CDN**: 95% cache hit rate for images and static content
- **Application Cache**: Redis cluster with 99% hit rate for search results
- **Database Query Cache**: MySQL query cache with 85% hit rate
- **API Response Cache**: 15-minute TTL for listing details

### Search Performance Optimization
- **Elasticsearch Sharding**: Geographic-based sharding for search performance
- **Index Warming**: Pre-warm search indices for popular destinations
- **Result Pagination**: Infinite scroll with 20 results per page
- **Predictive Caching**: Cache popular search queries regionally

### Booking Flow Optimization
- **Optimistic Locking**: Reduce booking conflicts with optimistic concurrency
- **Payment Caching**: Cache payment method validation for faster processing
- **Host Auto-Response**: ML-powered auto-approval for trusted guests
- **Mobile Optimization**: Streamlined mobile booking flow (8 steps vs 12)

## Critical Business Metrics

### Search Performance Metrics
- **Daily Searches**: 100M+ search queries globally
- **Search Conversion**: 3% of searches lead to bookings
- **Search Response Time**: p99 < 300ms globally
- **Search Relevance**: 85% click-through rate on top 3 results

### Booking Performance Metrics
- **Daily Bookings**: 15K+ bookings per day peak (summer)
- **Booking Success Rate**: 94% of initiated bookings complete
- **Payment Success Rate**: 97% first-attempt payment success
- **Host Approval Rate**: 89% for manual approval listings

### Revenue Impact Metrics
- **Gross Merchandise Value**: $50B+ annually
- **Average Booking Value**: $650 per booking
- **Revenue per Search**: $0.32 average
- **Host Payout Processing**: $40B+ paid to hosts since 2008

This request flow architecture enables Airbnb to handle millions of searches and thousands of bookings daily while maintaining a seamless user experience for both guests and hosts across the global marketplace.