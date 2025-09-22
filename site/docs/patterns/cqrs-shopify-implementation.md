# CQRS Pattern: Shopify's Implementation

## Pattern Overview

Shopify implements Command Query Responsibility Segregation (CQRS) to handle **5 million+ stores** and **billions of transactions** annually, separating read and write operations across different data models optimized for their specific use cases.

## Production Implementation Architecture

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane]
        LB[Load Balancer<br/>F5 BigIP<br/>$3,500/month]
        CDN[CDN<br/>Fastly<br/>Global distribution<br/>$12,000/month]
        WAF[WAF<br/>CloudFlare<br/>Security filtering<br/>$2,000/month]
    end

    subgraph ServicePlane[Service Plane]
        subgraph CommandSide[Command Side - Write Operations]
            ORDER_CMD[Order Command Service<br/>Ruby on Rails<br/>c5.4xlarge×50<br/>$60,000/month]
            PRODUCT_CMD[Product Command Service<br/>Ruby on Rails<br/>c5.2xlarge×30<br/>$21,600/month]
            INVENTORY_CMD[Inventory Command Service<br/>Go<br/>c5.xlarge×20<br/>$7,200/month]
            PAYMENT_CMD[Payment Command Service<br/>Ruby on Rails<br/>c5.2xlarge×40<br/>$28,800/month]
        end

        subgraph QuerySide[Query Side - Read Operations]
            ORDER_QUERY[Order Query Service<br/>GraphQL<br/>r5.2xlarge×100<br/>$96,000/month]
            PRODUCT_QUERY[Product Query Service<br/>ElasticSearch<br/>r5.4xlarge×30<br/>$57,600/month]
            ANALYTICS_QUERY[Analytics Query Service<br/>BigQuery<br/>Custom pricing<br/>$15,000/month]
            STOREFRONT_QUERY[Storefront Query<br/>Redis Cluster<br/>r6g.2xlarge×50<br/>$48,000/month]
        end

        subgraph EventProcessing[Event Processing]
            EVENT_BUS[Event Bus<br/>Apache Kafka<br/>r5.xlarge×12<br/>$8,640/month]
            PROJECTOR[Event Projector<br/>Ruby Sidekiq<br/>c5.large×25<br/>$4,500/month]
            DENORMALIZER[Denormalizer<br/>Stream processing<br/>c5.xlarge×15<br/>$5,400/month]
        end
    end

    subgraph StatePlane[State Plane]
        subgraph WriteStores[Write Stores - Normalized]
            ORDER_WRITE[(Orders Write DB<br/>MySQL 8.0<br/>db.r6g.8xlarge<br/>$15,000/month)]
            PRODUCT_WRITE[(Products Write DB<br/>MySQL 8.0<br/>db.r6g.4xlarge<br/>$7,500/month)]
            INVENTORY_WRITE[(Inventory Write DB<br/>MySQL 8.0<br/>db.r6g.2xlarge<br/>$3,750/month)]
        end

        subgraph ReadStores[Read Stores - Denormalized]
            ORDER_READ[(Orders Read DB<br/>PostgreSQL<br/>db.r6g.4xlarge×3<br/>$22,500/month)]
            PRODUCT_SEARCH[Product Search<br/>ElasticSearch<br/>r5.xlarge×20<br/>$14,400/month]
            ANALYTICS_STORE[(Analytics Store<br/>ClickHouse<br/>r5.2xlarge×10<br/>$9,600/month)]
            CACHE_LAYER[(Cache Layer<br/>Redis Enterprise<br/>r6g.xlarge×30<br/>$14,400/month)]
        end

        subgraph EventStore[Event Store]
            EVENT_STORE[(Event Store<br/>MySQL/Kafka<br/>Immutable log<br/>$8,000/month)]
        end
    end

    subgraph ControlPlane[Control Plane]
        PROMETHEUS[Prometheus<br/>Metrics collection<br/>$5,000/month]
        GRAFANA[Grafana<br/>CQRS dashboards<br/>$1,000/month]
        DATADOG[DataDog<br/>APM monitoring<br/>$25,000/month]
        BUGSNAG[Bugsnag<br/>Error tracking<br/>$3,000/month]
    end

    %% Traffic Flow - Commands
    CDN --> LB
    LB --> ORDER_CMD
    LB --> PRODUCT_CMD
    LB --> INVENTORY_CMD
    LB --> PAYMENT_CMD

    %% Traffic Flow - Queries
    CDN --> ORDER_QUERY
    CDN --> PRODUCT_QUERY
    CDN --> ANALYTICS_QUERY
    CDN --> STOREFRONT_QUERY

    %% Command Side Data Flow
    ORDER_CMD --> ORDER_WRITE
    PRODUCT_CMD --> PRODUCT_WRITE
    INVENTORY_CMD --> INVENTORY_WRITE
    PAYMENT_CMD --> ORDER_WRITE

    %% Event Flow
    ORDER_CMD --> EVENT_BUS
    PRODUCT_CMD --> EVENT_BUS
    INVENTORY_CMD --> EVENT_BUS
    EVENT_BUS --> EVENT_STORE
    EVENT_BUS --> PROJECTOR
    PROJECTOR --> DENORMALIZER

    %% Read Model Updates
    DENORMALIZER --> ORDER_READ
    DENORMALIZER --> PRODUCT_SEARCH
    DENORMALIZER --> ANALYTICS_STORE
    DENORMALIZER --> CACHE_LAYER

    %% Query Side Data Flow
    ORDER_QUERY --> ORDER_READ
    PRODUCT_QUERY --> PRODUCT_SEARCH
    ANALYTICS_QUERY --> ANALYTICS_STORE
    STOREFRONT_QUERY --> CACHE_LAYER

    %% Monitoring
    PROMETHEUS --> ORDER_CMD
    PROMETHEUS --> ORDER_QUERY
    PROMETHEUS --> EVENT_BUS
    GRAFANA --> PROMETHEUS
    DATADOG --> ORDER_CMD
    DATADOG --> PRODUCT_CMD

    %% Apply 4-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#1E40AF,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#047857,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class LB,CDN,WAF edgeStyle
    class ORDER_CMD,PRODUCT_CMD,INVENTORY_CMD,PAYMENT_CMD,ORDER_QUERY,PRODUCT_QUERY,ANALYTICS_QUERY,STOREFRONT_QUERY,EVENT_BUS,PROJECTOR,DENORMALIZER serviceStyle
    class ORDER_WRITE,PRODUCT_WRITE,INVENTORY_WRITE,ORDER_READ,PRODUCT_SEARCH,ANALYTICS_STORE,CACHE_LAYER,EVENT_STORE stateStyle
    class PROMETHEUS,GRAFANA,DATADOG,BUGSNAG controlStyle
```

## Command Processing Flow

```mermaid
graph TB
    subgraph CommandFlow[Order Creation Command Flow]
        CLIENT[Shopify Admin/API<br/>Create Order Request]
        VALIDATOR[Command Validator<br/>Business rules<br/>Data validation]
        HANDLER[Order Command Handler<br/>Domain logic<br/>State changes]
        AGGREGATE[Order Aggregate<br/>Domain model<br/>Business invariants]

        subgraph Events[Domain Events]
            ORDER_CREATED[OrderCreated<br/>Order ID, Customer<br/>Items, Total]
            INVENTORY_RESERVED[InventoryReserved<br/>SKU, Quantity<br/>Reservation ID]
            PAYMENT_INITIATED[PaymentInitiated<br/>Amount, Gateway<br/>Transaction ID]
        end

        PUBLISHER[Event Publisher<br/>Kafka producer<br/>Guaranteed delivery]
        ACK[Command Acknowledgment<br/>Order ID<br/>Status: Processing]
    end

    subgraph WriteModel[Write Model Storage]
        ORDER_ENTITY[Order Entity<br/>Normalized schema<br/>ACID compliance]
        INVENTORY_ENTITY[Inventory Entity<br/>Stock levels<br/>Reservations]
        AUDIT_LOG[Audit Log<br/>Command history<br/>Compliance tracking]
    end

    CLIENT --> VALIDATOR
    VALIDATOR --> HANDLER
    HANDLER --> AGGREGATE
    AGGREGATE --> ORDER_CREATED
    AGGREGATE --> INVENTORY_RESERVED
    AGGREGATE --> PAYMENT_INITIATED
    ORDER_CREATED --> PUBLISHER
    INVENTORY_RESERVED --> PUBLISHER
    PAYMENT_INITIATED --> PUBLISHER
    HANDLER --> ORDER_ENTITY
    HANDLER --> INVENTORY_ENTITY
    HANDLER --> AUDIT_LOG
    HANDLER --> ACK
    ACK --> CLIENT

    classDef commandStyle fill:#DC2626,stroke:#B91C1C,color:#fff
    classDef eventStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef storeStyle fill:#10B981,stroke:#047857,color:#fff

    class CLIENT,VALIDATOR,HANDLER,AGGREGATE,PUBLISHER,ACK commandStyle
    class ORDER_CREATED,INVENTORY_RESERVED,PAYMENT_INITIATED eventStyle
    class ORDER_ENTITY,INVENTORY_ENTITY,AUDIT_LOG storeStyle
```

## Query Processing Flow

```mermaid
graph TB
    subgraph QueryFlow[Order Analytics Query Flow]
        QUERY_CLIENT[Analytics Dashboard<br/>Order metrics request]
        QUERY_HANDLER[Query Handler<br/>GraphQL resolver<br/>Aggregation logic]

        subgraph ReadModels[Read Models]
            ORDER_SUMMARY[Order Summary View<br/>Daily/Monthly aggregates<br/>Pre-computed totals]
            PRODUCT_ANALYTICS[Product Analytics<br/>Sales by SKU<br/>Revenue breakdown]
            CUSTOMER_INSIGHTS[Customer Insights<br/>Purchase patterns<br/>Lifetime value]
        end

        subgraph CacheLayer[Caching Strategy]
            REDIS_CACHE[Redis Cache<br/>Hot data<br/>Sub-second access]
            MEMCACHED[Memcached<br/>Session data<br/>Temporary results]
            CDN_CACHE[CDN Cache<br/>Static aggregates<br/>Edge locations]
        end

        RESULT[Query Result<br/>JSON response<br/>Formatted data]
    end

    subgraph EventProjection[Event Projection Process]
        EVENT_STREAM[Event Stream<br/>Order events<br/>Real-time updates]
        PROJECTOR_SERVICE[Projector Service<br/>Event replay<br/>View updates]

        subgraph ViewUpdates[View Update Strategy]
            IMMEDIATE[Immediate Update<br/>Critical metrics<br/>Real-time views]
            BATCH[Batch Update<br/>Analytics data<br/>Hourly/Daily jobs]
            SNAPSHOT[Snapshot Rebuild<br/>Full refresh<br/>Weekly maintenance]
        end
    end

    QUERY_CLIENT --> QUERY_HANDLER
    QUERY_HANDLER --> ORDER_SUMMARY
    QUERY_HANDLER --> PRODUCT_ANALYTICS
    QUERY_HANDLER --> CUSTOMER_INSIGHTS
    ORDER_SUMMARY --> REDIS_CACHE
    PRODUCT_ANALYTICS --> MEMCACHED
    CUSTOMER_INSIGHTS --> CDN_CACHE
    REDIS_CACHE --> RESULT
    MEMCACHED --> RESULT
    CDN_CACHE --> RESULT
    RESULT --> QUERY_CLIENT

    EVENT_STREAM --> PROJECTOR_SERVICE
    PROJECTOR_SERVICE --> IMMEDIATE
    PROJECTOR_SERVICE --> BATCH
    PROJECTOR_SERVICE --> SNAPSHOT
    IMMEDIATE --> ORDER_SUMMARY
    BATCH --> PRODUCT_ANALYTICS
    SNAPSHOT --> CUSTOMER_INSIGHTS

    classDef queryStyle fill:#3B82F6,stroke:#1E40AF,color:#fff
    classDef readStyle fill:#10B981,stroke:#047857,color:#fff
    classDef cacheStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef projectionStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class QUERY_CLIENT,QUERY_HANDLER,RESULT queryStyle
    class ORDER_SUMMARY,PRODUCT_ANALYTICS,CUSTOMER_INSIGHTS readStyle
    class REDIS_CACHE,MEMCACHED,CDN_CACHE cacheStyle
    class EVENT_STREAM,PROJECTOR_SERVICE,IMMEDIATE,BATCH,SNAPSHOT projectionStyle
```

## Event Sourcing Integration

```mermaid
graph TB
    subgraph EventSourcing[Event Sourcing with CQRS]
        subgraph CommandHandling[Command Handling]
            COMMAND[Order Command<br/>Create/Update/Cancel<br/>Business operation]
            DOMAIN_MODEL[Domain Model<br/>Order Aggregate<br/>Business logic]
            EVENTS[Domain Events<br/>OrderCreated<br/>OrderUpdated<br/>OrderCancelled]
        end

        subgraph EventStorage[Event Storage]
            EVENT_STREAM_STORE[Event Stream<br/>Immutable log<br/>Append-only]
            SNAPSHOT_STORE[Snapshot Store<br/>Aggregate state<br/>Performance optimization]
            METADATA[Event Metadata<br/>Timestamps<br/>Correlation IDs<br/>Causation chains]
        end

        subgraph ReadModelProjection[Read Model Projection]
            EVENT_HANDLERS[Event Handlers<br/>When OrderCreated<br/>When OrderUpdated]
            PROJECTION_ENGINE[Projection Engine<br/>Event replay<br/>View rebuilding]

            subgraph ReadViews[Read Views]
                ORDER_LIST[Order List View<br/>Searchable index<br/>ElasticSearch]
                ORDER_DETAIL[Order Detail View<br/>Denormalized data<br/>PostgreSQL]
                ANALYTICS_VIEW[Analytics View<br/>Aggregated metrics<br/>ClickHouse]
            end
        end

        subgraph EventReplay[Event Replay Capabilities]
            HISTORICAL_REPLAY[Historical Replay<br/>Point-in-time rebuild<br/>Audit capabilities]
            BUG_REPRODUCTION[Bug Reproduction<br/>Replay specific events<br/>Debug scenarios]
            NEW_PROJECTIONS[New Projections<br/>Add read models<br/>Replay all events]
        end
    end

    COMMAND --> DOMAIN_MODEL
    DOMAIN_MODEL --> EVENTS
    EVENTS --> EVENT_STREAM_STORE
    EVENTS --> SNAPSHOT_STORE
    EVENTS --> METADATA
    EVENTS --> EVENT_HANDLERS
    EVENT_HANDLERS --> PROJECTION_ENGINE
    PROJECTION_ENGINE --> ORDER_LIST
    PROJECTION_ENGINE --> ORDER_DETAIL
    PROJECTION_ENGINE --> ANALYTICS_VIEW
    EVENT_STREAM_STORE --> HISTORICAL_REPLAY
    EVENT_STREAM_STORE --> BUG_REPRODUCTION
    EVENT_STREAM_STORE --> NEW_PROJECTIONS

    classDef commandStyle fill:#DC2626,stroke:#B91C1C,color:#fff
    classDef eventStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef projectionStyle fill:#10B981,stroke:#047857,color:#fff
    classDef replayStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class COMMAND,DOMAIN_MODEL commandStyle
    class EVENTS,EVENT_STREAM_STORE,SNAPSHOT_STORE,METADATA eventStyle
    class EVENT_HANDLERS,PROJECTION_ENGINE,ORDER_LIST,ORDER_DETAIL,ANALYTICS_VIEW projectionStyle
    class HISTORICAL_REPLAY,BUG_REPRODUCTION,NEW_PROJECTIONS replayStyle
```

## Production Metrics & Performance

### Scale Numbers (2024)
- **Total Stores**: 5+ million active stores
- **Orders Processed**: 3 billion+ annually
- **Command Throughput**: 100,000 commands/second peak
- **Query Throughput**: 2 million queries/second peak
- **Read Model Lag**: <100ms average from event to query availability
- **Command Response Time**: <50ms p99

### Cost Breakdown (Monthly)
```
Command Services:           $117,600
Query Services:            $216,600
Event Processing:           $18,540
Write Databases:            $26,250
Read Databases:             $60,900
Event Store:                $8,000
Caching Layer:              $14,400
Monitoring & Alerting:      $34,000
CDN & Load Balancing:       $17,500
------------------------
Total Monthly Cost:        $513,790
Cost per Order:            $0.002
```

### Business Impact
- **Query Performance**: 10x faster than normalized database queries
- **Write Scalability**: Independent scaling of read/write workloads
- **Development Velocity**: 40% faster feature development
- **System Availability**: 99.99% uptime for both read and write operations

## Configuration Examples

### Command Handler Implementation
```ruby
# app/commands/orders/create_order_command.rb
class Orders::CreateOrderCommand
  include ActiveModel::Model
  include ActiveModel::Validations

  attr_accessor :customer_id, :line_items, :shipping_address, :billing_address

  validates :customer_id, presence: true
  validates :line_items, presence: true, length: { minimum: 1 }
  validate :sufficient_inventory

  def execute
    return false unless valid?

    ActiveRecord::Base.transaction do
      order = create_order_aggregate
      events = order.handle_create_command(self)

      persist_order(order)
      publish_events(events)

      CommandResult.success(order_id: order.id)
    end
  rescue => e
    CommandResult.failure(error: e.message)
  end

  private

  def create_order_aggregate
    Order.new(
      customer_id: customer_id,
      status: 'pending',
      created_at: Time.current
    )
  end

  def persist_order(order)
    # Write to normalized database
    OrderWriteModel.create!(
      id: order.id,
      customer_id: order.customer_id,
      status: order.status,
      total_amount: order.total_amount,
      created_at: order.created_at
    )

    order.line_items.each do |item|
      LineItemWriteModel.create!(
        order_id: order.id,
        product_id: item.product_id,
        quantity: item.quantity,
        price: item.price
      )
    end
  end

  def publish_events(events)
    events.each do |event|
      EventBus.publish(
        topic: event.class.name.underscore,
        event: event.to_h,
        metadata: {
          correlation_id: SecureRandom.uuid,
          timestamp: Time.current.iso8601,
          version: event.version
        }
      )
    end
  end

  def sufficient_inventory
    line_items.each do |item|
      available = InventoryService.available_quantity(item.product_id)
      if available < item.quantity
        errors.add(:line_items, "Insufficient inventory for product #{item.product_id}")
      end
    end
  end
end
```

### Query Handler Implementation
```ruby
# app/queries/orders/order_analytics_query.rb
class Orders::OrderAnalyticsQuery
  include ActiveModel::Model

  attr_accessor :store_id, :date_range, :group_by, :filters

  def execute
    cached_result || compute_and_cache_result
  end

  private

  def cached_result
    cache_key = generate_cache_key
    Rails.cache.read(cache_key)
  end

  def compute_and_cache_result
    result = case group_by
    when 'day'
      daily_order_metrics
    when 'product'
      product_performance_metrics
    when 'customer_segment'
      customer_segment_metrics
    else
      overall_metrics
    end

    Rails.cache.write(generate_cache_key, result, expires_in: cache_ttl)
    result
  end

  def daily_order_metrics
    # Query denormalized read model
    OrderAnalyticsReadModel
      .where(store_id: store_id)
      .where(date: date_range)
      .group(:date)
      .select(
        :date,
        'SUM(order_count) as total_orders',
        'SUM(revenue) as total_revenue',
        'AVG(average_order_value) as avg_order_value'
      )
  end

  def product_performance_metrics
    ProductAnalyticsReadModel
      .joins(:store)
      .where(store_id: store_id)
      .where(date: date_range)
      .group(:product_id, :product_name)
      .order('total_revenue DESC')
      .limit(50)
      .select(
        :product_id,
        :product_name,
        'SUM(quantity_sold) as units_sold',
        'SUM(revenue) as total_revenue',
        'AVG(conversion_rate) as avg_conversion_rate'
      )
  end

  def cache_ttl
    case group_by
    when 'day'
      1.hour    # Daily metrics cached for 1 hour
    when 'product'
      30.minutes # Product metrics cached for 30 minutes
    else
      15.minutes # Other metrics cached for 15 minutes
    end
  end

  def generate_cache_key
    "order_analytics:#{store_id}:#{date_range.hash}:#{group_by}:#{filters.hash}"
  end
end
```

### Event Projection Implementation
```ruby
# app/projectors/order_analytics_projector.rb
class OrderAnalyticsProjector
  def self.handle_order_created(event)
    date = Date.parse(event[:created_at])

    analytics_record = OrderAnalyticsReadModel.find_or_initialize_by(
      store_id: event[:store_id],
      date: date
    )

    analytics_record.assign_attributes(
      order_count: analytics_record.order_count + 1,
      revenue: analytics_record.revenue + event[:total_amount],
      average_order_value: calculate_average_order_value(analytics_record),
      updated_at: Time.current
    )

    analytics_record.save!

    # Update real-time dashboard
    ActionCable.server.broadcast(
      "store_analytics_#{event[:store_id]}",
      {
        type: 'order_created',
        date: date.iso8601,
        new_totals: {
          order_count: analytics_record.order_count,
          revenue: analytics_record.revenue,
          average_order_value: analytics_record.average_order_value
        }
      }
    )
  end

  def self.handle_order_cancelled(event)
    date = Date.parse(event[:created_at])

    analytics_record = OrderAnalyticsReadModel.find_by(
      store_id: event[:store_id],
      date: date
    )

    return unless analytics_record

    analytics_record.assign_attributes(
      order_count: analytics_record.order_count - 1,
      revenue: analytics_record.revenue - event[:total_amount],
      average_order_value: calculate_average_order_value(analytics_record),
      cancellation_count: analytics_record.cancellation_count + 1,
      updated_at: Time.current
    )

    analytics_record.save!
  end

  private

  def self.calculate_average_order_value(record)
    return 0 if record.order_count.zero?
    record.revenue / record.order_count
  end
end
```

## Failure Scenarios & Recovery

### Scenario 1: Read Model Lag
```
Problem: Event processing delays cause stale read models
Impact: Analytics show outdated data for 30+ minutes
MTTR: 10 minutes (restart projectors + catch up)
Recovery:
1. Restart event processors (2 minutes)
2. Enable catch-up processing (5 minutes)
3. Validate data consistency (3 minutes)
Prevention: Monitor event lag, auto-scaling projectors
```

### Scenario 2: Event Store Failure
```
Problem: Kafka cluster failure prevents event publishing
Impact: New commands cannot be processed
MTTR: 5 minutes (failover to backup region)
Recovery:
1. Detect failure via health checks (30 seconds)
2. Route traffic to DR region (2 minutes)
3. Restore primary cluster (2.5 minutes)
Prevention: Multi-region event store, automatic failover
```

### Scenario 3: Command Side Database Outage
```
Problem: MySQL write database becomes unavailable
Impact: Cannot process new orders, payments
MTTR: 3 minutes (promote read replica)
Recovery:
1. Promote read replica to primary (90 seconds)
2. Update connection strings (60 seconds)
3. Resume command processing (30 seconds)
Prevention: Multi-AZ deployment, automated failover
```

## Production Incidents & Lessons

### Incident: Read Model Corruption (March 2024)
**Problem**: Bug in projector corrupted analytics aggregates
**Impact**: Wrong revenue reports for 2 hours affecting 10K stores
**Root Cause**: Race condition in concurrent event processing
**Resolution**: Rolled back projector, rebuilt read models from events
**Prevention**: Added event ordering guarantees, idempotent projections

### Incident: Event Replay Performance (July 2024)
**Problem**: Adding new read model caused 6-hour event replay
**Impact**: All analytics queries showed stale data
**Root Cause**: Inefficient event batching during replay
**Resolution**: Implemented parallel replay with checkpointing
**Prevention**: Optimized replay algorithms, pre-built read models

## Monitoring & Alerting

### Critical Metrics
```yaml
# DataDog monitoring configuration
cqrs_command_latency:
  metric: cqrs.command.duration.p99
  threshold: 100ms
  alert: PagerDuty Critical

cqrs_event_lag:
  metric: cqrs.event.processing_lag
  threshold: 5 minutes
  alert: PagerDuty High Priority

cqrs_read_model_freshness:
  metric: cqrs.read_model.last_update
  threshold: 10 minutes
  alert: Slack Warning

cqrs_query_performance:
  metric: cqrs.query.duration.p95
  threshold: 200ms
  alert: DataDog Dashboard
```

### Production Runbooks
```bash
# Event replay for corrupted read model
./scripts/event_replay.rb --read-model OrderAnalytics --from 2024-01-01 --to 2024-01-31

# Validate read model consistency
./scripts/validate_read_models.rb --model OrderAnalytics --sample-size 1000

# Emergency command processing bypass
./scripts/emergency_bypass.rb --route-commands-to dr-region --duration 30m
```

## Real-World Performance Data

### Command Processing Performance
```
Simple Commands (Create Order):     p99 < 50ms
Complex Commands (Bulk Update):     p99 < 200ms
Command Validation:                 p99 < 10ms
Event Publishing:                   p99 < 25ms
```

### Query Performance by Complexity
```
Simple Queries (Order Details):     p99 < 10ms
Aggregate Queries (Daily Totals):   p99 < 50ms
Complex Analytics:                  p99 < 200ms
Cross-Store Analytics:              p99 < 500ms
```

### Event Processing Throughput
```
Event Publishing Rate:              1M events/minute peak
Event Processing Rate:              800K events/minute sustained
Projection Update Latency:         p99 < 100ms
Read Model Refresh Rate:            Real-time to 1 hour depending on criticality
```

This CQRS implementation enables Shopify to maintain high performance across both command and query operations while handling massive scale, with the flexibility to optimize each side independently for their specific use cases.