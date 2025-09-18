# Shopify Black Friday Outage - November 25, 2022

**The 45-Minute Checkout Service Overload That Cost Merchants $100M+ in Sales**

## Incident Overview

| **Metric** | **Value** |
|------------|-----------||
| **Date** | November 25, 2022 |
| **Duration** | 45 minutes during peak traffic |
| **Impact** | Checkout service overload during Black Friday |
| **Users Affected** | 2M+ concurrent shoppers |
| **Financial Impact** | $100M+ lost sales estimated |
| **Root Cause** | Checkout service capacity exceeded |
| **MTTR** | 45 minutes |
| **Key Issue** | Peak traffic 5x higher than projected |
| **Services Down** | Checkout, payments, cart updates |

## Timeline - Black Friday's Worst Nightmare

```mermaid
gantt
    title Shopify Black Friday Outage - November 25, 2022
    dateFormat HH:mm
    axisFormat %H:%M

    section Peak Traffic
    Normal morning sales  :done, normal1, 08:00, 12:00
    Traffic surge begins  :done, surge1, 12:00, 13:30
    Peak shopping hours   :done, peak1, 13:30, 15:15

    section System Failure
    Checkout slowdowns    :done, slow1, 13:30, 14:00
    Complete checkout fail:done, fail1, 14:00, 14:45
    Recovery begins       :done, rec1, 14:45, 15:15

    section Full Recovery
    Services restored     :done, restore1, 15:15, 16:00
```

## E-commerce Platform Under Black Friday Load

```mermaid
graph TB
    subgraph "Edge Plane - Blue #3B82F6"
        STOREFRONT[Merchant Storefronts<br/>1M+ Stores]
        CDN[Shopify CDN<br/>Global Content Delivery]
        MOBILE[Mobile Apps<br/>Shop App]
    end

    subgraph "Service Plane - Green #10B981"
        CHECKOUT[Checkout Service<br/>Payment Processing<br/>OVERLOADED]
        CART[Shopping Cart<br/>Session Management]
        INVENTORY[Inventory Service<br/>Stock Management]
        SHIPPING[Shipping Service<br/>Logistics Calculation]
    end

    subgraph "State Plane - Orange #F59E0B"
        ORDERS[(Orders Database<br/>Transaction Records)]
        PRODUCTS[(Product Database<br/>Catalog Data)]
        CUSTOMERS[(Customer Database<br/>User Accounts)]
        ANALYTICS[(Analytics Store<br/>Sales Data)]
    end

    subgraph "Control Plane - Red #8B5CF6"
        MONITORING[System Monitoring<br/>Performance Metrics]
        AUTOSCALE[Auto-scaling<br/>Capacity Management]
        ALERTS[Alert System<br/>Incident Management]
    end

    subgraph "External Payment Network"
        STRIPE[Stripe Payments<br/>Card Processing]
        PAYPAL[PayPal<br/>Digital Wallet]
        BANKS[Banking Partners<br/>Transaction Settlement]
        FRAUD[Fraud Detection<br/>Risk Assessment]
    end

    %% Black Friday traffic overload
    STOREFRONT -.->|5x projected traffic<br/>2M+ concurrent users| CHECKOUT
    CDN -.->|Asset delivery strain<br/>High bandwidth usage| CHECKOUT
    MOBILE -.->|Mobile shopping surge<br/>App-based purchases| CHECKOUT

    %% Checkout service collapse
    CHECKOUT -.->|Cannot process orders<br/>Service overwhelmed| CART
    CART -.->|Session timeouts<br/>Cart abandonment| INVENTORY
    INVENTORY -.->|Stock updates failing<br/>Overselling risk| SHIPPING

    %% Database pressure
    CHECKOUT -.->|Order creation backlog<br/>Database write pressure| ORDERS
    ORDERS -.->|Transaction delays<br/>Payment processing slow| PRODUCTS
    PRODUCTS -.->|Catalog queries slow<br/>Product page loading| CUSTOMERS

    %% External payment delays
    CHECKOUT -.->|Payment timeouts<br/>Cannot process cards| STRIPE
    STRIPE -.->|Transaction queues<br/>Payment delays| PAYPAL
    PAYPAL -.->|Settlement delays<br/>Banking network strain| BANKS

    %% Merchant impact
    CHECKOUT -.->|Lost sales opportunity<br/>$100M+ revenue impact| MERCHANTS[E-commerce Stores<br/>Retail Brands<br/>SMB Merchants<br/>Enterprise Clients]

    %% Apply four-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff,stroke-width:3px
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff,stroke-width:3px
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff,stroke-width:3px
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff,stroke-width:3px
    classDef paymentStyle fill:#4B0082,stroke:#301934,color:#fff,stroke-width:4px
    classDef impactStyle fill:#8B0000,stroke:#660000,color:#fff,stroke-width:4px

    class STOREFRONT,CDN,MOBILE edgeStyle
    class CHECKOUT,CART,INVENTORY,SHIPPING serviceStyle
    class ORDERS,PRODUCTS,CUSTOMERS,ANALYTICS stateStyle
    class MONITORING,AUTOSCALE,ALERTS controlStyle
    class STRIPE,PAYPAL,BANKS,FRAUD paymentStyle
    class MERCHANTS impactStyle
```

## Black Friday Sales Impact

### Sales Volume vs Capacity

```mermaid
xychart-beta
    title "Shopify Traffic vs Capacity (Black Friday 2022)"
    x-axis ["12:00", "13:00", "14:00", "14:30", "15:00", "15:30", "16:00"]
    y-axis "Requests/Second (Thousands)" 0 --> 300
    line [150, 200, 280, 350, 320, 250, 180]
    line [180, 180, 180, 180, 180, 200, 220]
```

### Revenue Impact by Hour

```mermaid
xychart-beta
    title "Lost Revenue During Outage ($M)"
    x-axis ["14:00", "14:15", "14:30", "14:45", "15:00", "15:15"]
    y-axis "Lost Revenue ($M)" 0 --> 30
    bar [25, 35, 30, 20, 15, 5]
```

## Recovery Strategy

```mermaid
timeline
    title Emergency Response - 45 Minutes

    section Immediate Response
        14:05 : Auto-scaling triggered
              : 3x checkout capacity
              : Load balancer updates

    section Traffic Management
        14:20 : Queue system activated
              : Rate limiting enabled
              : Priority for existing carts

    section Service Recovery
        14:35 : Database optimization
              : Connection pool scaling
              : Cache warming

    section Full Restoration
        14:45 : All services operational
              : Queue processing complete
              : Normal checkout flow
```

## The Bottom Line

**This incident proved that Black Friday traffic patterns are impossible to predict accurately - and the cost of under-capacity is massive.**

**Key Takeaways:**
- Peak shopping events need 10x normal capacity planning
- Checkout services are the most critical failure point
- Revenue loss during peak hours is exponentially damaging
- Auto-scaling must be instantaneous, not gradual

**The $100M question:** How much over-capacity should e-commerce platforms maintain for unpredictable peak shopping events?

---

*"In e-commerce, your platform goes down exactly when customers have their wallets out."*