# Uber Global Outage - March 3, 2023

**The 2-Hour Matching Engine Memory Leak That Broke Ride-Sharing Worldwide**

## Incident Overview

| **Metric** | **Value** |
|------------|-----------||
| **Date** | March 3, 2023 |
| **Duration** | 2 hours globally |
| **Impact** | Rides couldn't be booked |
| **Users Affected** | 130M+ monthly active users |
| **Financial Impact** | $80M+ in lost ride revenue |
| **Root Cause** | Matching engine memory leak |
| **MTTR** | 120 minutes |
| **Key Issue** | Algorithm optimization caused memory exhaustion |
| **Services Down** | Ride booking, driver matching, fare calculation |

```mermaid
graph TB
    subgraph Uber Platform
        RIDERS[Rider App<br/>Trip Requests]
        DRIVERS[Driver App<br/>Trip Acceptance]
        MATCHING[Matching Engine<br/>Rider-Driver Pairing<br/>MEMORY LEAK]
        PRICING[Dynamic Pricing<br/>Surge Calculation]
    end

    subgraph Core Algorithms
        DISPATCH[Dispatch Algorithm<br/>Optimal Matching]
        ETA[ETA Calculation<br/>Arrival Estimation]
        ROUTING[Route Optimization<br/>Trip Planning]
        DEMAND[Demand Prediction<br/>Supply Planning]
    end

    %% Memory leak cascade
    MATCHING -.->|Memory exhaustion<br/>14:20 PST| DISPATCH
    DISPATCH -.->|Cannot allocate memory<br/>Algorithm failure| RIDERS
    RIDERS -.->|Cannot book rides<br/>Request timeouts| DRIVERS
    DRIVERS -.->|No trip assignments<br/>Idle drivers| PRICING

    %% Customer impact
    MATCHING -.->|"No drivers available"<br/>130M+ users affected| CUSTOMERS[Urban Commuters<br/>Airport Travelers<br/>Delivery Customers<br/>Driver Partners]

    classDef algorithmStyle fill:#FF6B6B,stroke:#8B5CF6,color:#fff,stroke-width:3px
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff,stroke-width:3px
    classDef impactStyle fill:#8B0000,stroke:#660000,color:#fff,stroke-width:4px

    class MATCHING,DISPATCH,ETA,ROUTING,DEMAND algorithmStyle
    class RIDERS,DRIVERS,PRICING serviceStyle
    class CUSTOMERS impactStyle
```

## The Bottom Line

**This incident demonstrated that algorithmic optimization can introduce memory leaks that break core business functionality at global scale.**

**Key Takeaways:**
- Matching algorithms need rigorous memory management testing
- Performance optimizations can introduce subtle memory leaks
- Ride-sharing platforms are entirely dependent on real-time matching
- Memory exhaustion in critical services creates cascading failures

---

*"In ride-sharing, matching algorithms are the heart of the business - memory leaks are cardiac arrest."*