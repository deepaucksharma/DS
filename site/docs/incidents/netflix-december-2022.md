# Netflix Christmas Day Outage - December 25, 2022

**The 1-Hour CDN Cache Poisoning That Ruined Christmas Viewing**

## Incident Overview

| **Metric** | **Value** |
|------------|-----------||
| **Date** | December 25, 2022 |
| **Duration** | 1 hour during peak viewing |
| **Impact** | Video streaming failures globally |
| **Users Affected** | 40M+ simultaneous viewers |
| **Financial Impact** | $50M+ in lost engagement |
| **Root Cause** | CDN cache poisoning during deployment |
| **MTTR** | 62 minutes |
| **Key Issue** | Bad metadata cached globally |
| **Services Down** | Video playback, content discovery |

## Timeline - Christmas Day Streaming Crisis

```mermaid
gantt
    title Netflix Christmas Outage - December 25, 2022
    dateFormat HH:mm
    axisFormat %H:%M

    section Peak Viewing
    Christmas morning     :done, peak1, 10:00, 14:00
    Family viewing time   :done, peak2, 14:00, 18:00
    Prime time surge      :done, peak3, 18:00, 22:00

    section System Failure
    CDN deployment        :done, deploy1, 15:30, 15:45
    Cache poisoning       :done, poison1, 15:45, 16:15
    Global video failures :done, fail1, 16:15, 17:17

    section Recovery
    Cache invalidation    :done, fix1, 17:17, 17:30
    Service restoration   :done, restore1, 17:30, 18:00
```

## Streaming Infrastructure Cache Poisoning

```mermaid
graph TB
    subgraph Edge Plane - Blue #3B82F6
        CDN[Netflix CDN<br/>Global Cache Network<br/>POISONED CACHE]
        EDGE[Edge Servers<br/>Regional PoPs]
        DEVICE[Client Devices<br/>Smart TVs, Phones]
    end

    subgraph Service Plane - Green #10B981
        PLAYBACK[Playback Service<br/>Video Streaming]
        METADATA[Metadata Service<br/>Content Information]
        RECOMMENDATION[Recommendation<br/>Content Discovery]
        BILLING[Billing Service<br/>Subscription Management]
    end

    subgraph State Plane - Orange #F59E0B
        CONTENT[(Content Database<br/>Video Metadata)]
        PROFILES[(User Profiles<br/>Viewing History)]
        ANALYTICS[(Analytics Store<br/>Viewing Data)]
        ASSETS[(Video Assets<br/>Encoded Streams)]
    end

    subgraph Control Plane - Red #8B5CF6
        MONITORING[System Monitoring<br/>Performance Metrics]
        DEPLOYMENT[Deployment System<br/>Code & Config Deploy]
        AUTOSCALE[Auto-scaling<br/>Capacity Management]
    end

    %% Cache poisoning cascade
    DEPLOYMENT -.->|Bad metadata deployment<br/>15:30 PST| CDN
    CDN -.->|Corrupted cache entries<br/>Invalid video metadata| EDGE
    EDGE -.->|Cannot serve content<br/>Broken video references| DEVICE

    %% Service impact
    CDN -.->|Cannot load video data<br/>Metadata corruption| PLAYBACK
    PLAYBACK -.->|Video playback fails<br/>Cannot stream content| METADATA
    METADATA -.->|Recommendations broken<br/>Cannot discover content| RECOMMENDATION

    %% Data layer issues
    METADATA -.->|Cache-database mismatch<br/>Inconsistent state| CONTENT
    CONTENT -.->|Cannot serve profiles<br/>User data corrupted| PROFILES
    PROFILES -.->|Analytics broken<br/>Cannot track viewing| ANALYTICS

    %% Customer impact
    PLAYBACK -.->|"Title not available"<br/>40M+ viewers affected| VIEWERS[Christmas Day Families<br/>Holiday Streamers<br/>International Users<br/>Binge Watchers]

    %% Apply four-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff,stroke-width:3px
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff,stroke-width:3px
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff,stroke-width:3px
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff,stroke-width:3px
    classDef impactStyle fill:#8B0000,stroke:#660000,color:#fff,stroke-width:4px

    class CDN,EDGE,DEVICE edgeStyle
    class PLAYBACK,METADATA,RECOMMENDATION,BILLING serviceStyle
    class CONTENT,PROFILES,ANALYTICS,ASSETS stateStyle
    class MONITORING,DEPLOYMENT,AUTOSCALE controlStyle
    class VIEWERS impactStyle
```

## Christmas Day Viewing Impact

### Peak Viewing Hours Lost

```mermaid
xychart-beta
    title "Christmas Day Viewing Impact (Millions)"
    x-axis ["15:00", "15:30", "16:00", "16:30", "17:00", "17:30", "18:00"]
    y-axis "Active Viewers (M)" 0 --> 50
    line [38, 42, 45, 15, 8, 35, 44]
```

### Content Categories Affected

```mermaid
pie title Content Impact by Category
    "Holiday Movies" : 35
    "Family Shows" : 25
    "New Releases" : 20
    "International Content" : 15
    "Documentaries" : 5
```

## Recovery Process

```mermaid
timeline
    title CDN Cache Recovery

    section Problem Identification
        16:20 : Cache corruption detected
              : Bad metadata deployment
              : Global impact confirmed

    section Cache Invalidation
        16:45 : Begin global cache purge
              : Invalidate corrupted entries
              : Restart edge servers

    section Content Restoration
        17:00 : Fresh metadata deployment
              : Video assets re-cached
              : Playback testing

    section Full Recovery
        17:17 : All content accessible
              : Normal viewing restored
              : Cache healthy globally
```

## The Bottom Line

**This incident showed that CDN cache poisoning can instantly break streaming for millions during the most important viewing day of the year.**

**Key Takeaways:**
- CDN deployments need staging environments that match production
- Cache invalidation must be instantaneous for video platforms
- Holiday peak times require extra deployment caution
- Video metadata is as critical as the video content itself

**The $50M question:** How do you test CDN deployments at Christmas Day scale without affecting real users?

---

*"In streaming, cache poisoning doesn't just break websites - it breaks family time."*