# Spotify Global Outage - March 8, 2024

**The 90-Minute License Server Timeout That Silenced 400M Users**

## Incident Overview

| **Metric** | **Value** |
|------------|-----------||
| **Date** | March 8, 2024 |
| **Duration** | 90 minutes |
| **Impact** | Songs wouldn't play globally |
| **Users Affected** | 400M+ active users |
| **Financial Impact** | $25M+ in lost ad revenue |
| **Root Cause** | License server timeout cascades |
| **MTTR** | 90 minutes |
| **Key Issue** | Music licensing validation failures |
| **Services Down** | Song playback, downloads, podcasts |

## Music Streaming License Crisis

```mermaid
graph TB
    subgraph Edge Plane - Blue #3B82F6
        MOBILE[Spotify Mobile Apps<br/>400M+ Users]
        DESKTOP[Desktop Application<br/>Premium Users]
        WEB[Web Player<br/>Browser-based]
    end

    subgraph Service Plane - Green #10B981
        PLAYBACK[Playback Service<br/>Music Streaming]
        LICENSE[License Validation<br/>Rights Management<br/>TIMEOUT FAILURE]
        DISCOVERY[Music Discovery<br/>Search & Browse]
        SOCIAL[Social Features<br/>Playlists & Sharing]
    end

    subgraph State Plane - Orange #F59E0B
        CATALOG[(Music Catalog<br/>Track Metadata)]
        RIGHTS[(Rights Database<br/>Licensing Data)]
        USERS[(User Database<br/>Accounts & Playlists)]
        ANALYTICS[(Analytics Store<br/>Listening Data)]
    end

    subgraph Control Plane - Red #8B5CF6
        MONITORING[System Monitoring<br/>Performance Metrics]
        FEATURES[Feature Flags<br/>A/B Testing]
        DEPLOYMENT[Deployment System<br/>Release Management]
    end

    subgraph External Music Infrastructure
        LABELS[Record Labels<br/>Content Providers]
        PUBLISHERS[Music Publishers<br/>Rights Holders]
        CDN[Content CDN<br/>Audio File Delivery]
        ROYALTY[Royalty Systems<br/>Payment Processing]
    end

    %% License server failure cascade
    LICENSE -.->|Server timeout errors<br/>11:30 CET| RIGHTS
    RIGHTS -.->|Cannot validate licenses<br/>Rights check failures| CATALOG
    CATALOG -.->|Cannot serve tracks<br/>Music unavailable| PLAYBACK

    %% Service impact cascade
    PLAYBACK -.->|Songs won't play<br/>Licensing validation failed| DISCOVERY
    DISCOVERY -.->|Search results empty<br/>Cannot browse music| SOCIAL
    SOCIAL -.->|Playlists broken<br/>Cannot share tracks| USERS

    %% External dependencies
    LICENSE -.->|Cannot verify rights<br/>Legal compliance required| LABELS
    LABELS -.->|Rights validation timeout<br/>Cannot authorize playback| PUBLISHERS
    PUBLISHERS -.->|Content delivery blocked<br/>No valid license| CDN

    %% Customer impact
    PLAYBACK -.->|"This song is unavailable"<br/>400M+ users affected| LISTENERS[Music Lovers<br/>Podcast Listeners<br/>Premium Subscribers<br/>Free Tier Users]

    %% Apply four-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff,stroke-width:3px
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff,stroke-width:3px
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff,stroke-width:3px
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff,stroke-width:3px
    classDef musicStyle fill:#4B0082,stroke:#301934,color:#fff,stroke-width:4px
    classDef impactStyle fill:#8B0000,stroke:#660000,color:#fff,stroke-width:4px

    class MOBILE,DESKTOP,WEB edgeStyle
    class PLAYBACK,LICENSE,DISCOVERY,SOCIAL serviceStyle
    class CATALOG,RIGHTS,USERS,ANALYTICS stateStyle
    class MONITORING,FEATURES,DEPLOYMENT controlStyle
    class LABELS,PUBLISHERS,CDN,ROYALTY musicStyle
    class LISTENERS impactStyle
```

## Music License Validation Crisis

### License Check Failure Timeline

```mermaid
xychart-beta
    title "License Validation Success Rate (%)"
    x-axis ["11:00", "11:30", "12:00", "12:30", "13:00", "13:30"]
    y-axis "Success Rate %" 0 --> 100
    line [98, 95, 15, 5, 45, 95]
```

### User Impact by Platform

```mermaid
pie title Users Affected by Platform (400M Total)
    "Mobile Apps" : 60
    "Desktop App" : 25
    "Web Player" : 10
    "Smart Speakers" : 3
    "Car Integration" : 2
```

## Recovery Strategy

```mermaid
timeline
    title License Server Recovery

    section Problem Identification
        11:45 : License timeout alerts
              : Rights validation failing
              : Global impact confirmed

    section Emergency Response
        12:00 : License server restart
              : Connection pool reset
              : Rights cache refresh

    section Service Recovery
        12:30 : License validation restored
              : Playback testing successful
              : Cache warming initiated

    section Full Restoration
        13:00 : All music available
              : Normal playback resumed
              : License system stable
```

## The Bottom Line

**This incident highlighted that music streaming is fundamentally dependent on real-time license validation - and when that fails, 400M people lose their soundtrack.**

**Key Takeaways:**
- Music licensing systems need bulletproof redundancy
- License validation timeouts should gracefully degrade, not block
- Music rights management is as critical as the music itself
- Streaming platforms must cache license approvals

**The $25M question:** Should music platforms cache license approvals for hours or days to prevent these outages?

---

*"In music streaming, legal compliance can't break the user experience."*