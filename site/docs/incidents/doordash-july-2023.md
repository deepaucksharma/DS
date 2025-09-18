# DoorDash Outage During Dinner Rush - July 15, 2023

**The 3-Hour Location Service Failure That Left Drivers and Orders Stranded**

## Incident Overview

| **Metric** | **Value** |
|------------|-----------||
| **Date** | July 15, 2023 |
| **Duration** | 3 hours during dinner rush |
| **Impact** | Orders stuck, drivers stranded |
| **Users Affected** | 25M+ customers and drivers |
| **Financial Impact** | $150M+ in lost orders and refunds |
| **Root Cause** | Location service failure |
| **MTTR** | 180 minutes |
| **Key Issue** | GPS and mapping service breakdown |
| **Services Down** | Order tracking, driver navigation, delivery estimates |

```mermaid
graph TB
    subgraph "DoorDash Platform"
        ORDERS[Order Management<br/>Customer Orders]
        DRIVERS[Driver App<br/>Delivery Management]
        TRACKING[Location Tracking<br/>GPS Service<br/>FAILED]
        ROUTING[Route Optimization<br/>Delivery Planning]
    end

    subgraph "Location Infrastructure"
        GPS[GPS Service<br/>Location Data<br/>PRIMARY FAILURE]
        MAPS[Mapping Service<br/>Route Calculation]
        GEOFENCE[Geofencing<br/>Delivery Zones]
        ETA[ETA Calculation<br/>Time Estimation]
    end

    %% Location service failure
    GPS -.->|Service unavailable<br/>18:30 PST| TRACKING
    TRACKING -.->|Cannot track drivers<br/>Location unknown| DRIVERS
    DRIVERS -.->|Cannot navigate<br/>Lost drivers| ORDERS
    ORDERS -.->|Cannot fulfill deliveries<br/>Orders stuck| ROUTING

    %% Customer impact
    TRACKING -.->|"Driver location unknown"<br/>25M+ users affected| CUSTOMERS[Hungry Customers<br/>Delivery Drivers<br/>Restaurant Partners<br/>Corporate Customers]

    classDef locationStyle fill:#FF6B6B,stroke:#8B5CF6,color:#fff,stroke-width:3px
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff,stroke-width:3px
    classDef impactStyle fill:#8B0000,stroke:#660000,color:#fff,stroke-width:4px

    class GPS,MAPS,GEOFENCE,ETA locationStyle
    class ORDERS,DRIVERS,TRACKING,ROUTING serviceStyle
    class CUSTOMERS impactStyle
```

## The Bottom Line

**This incident showed that delivery platforms are entirely dependent on location services - when GPS fails, the entire logistics network breaks down.**

**Key Takeaways:**
- Location services are critical infrastructure for delivery platforms
- GPS failures during peak hours create maximum customer impact
- Delivery platforms need redundant location data sources
- Driver navigation failures cascade to customer experience

---

*"In delivery platforms, location is everything - lose GPS, lose the business."*