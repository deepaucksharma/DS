# AWS S3 February 28, 2017 - The Typo That Broke The Internet

*"A single character typo in a debugging command removed more servers than intended, bringing down half the internet for 4+ hours"*

## Incident Overview

| Attribute | Value |
|-----------|-------|
| **Date** | February 28, 2017 |
| **Duration** | 4 hours, 17 minutes |
| **Trigger Time** | 09:37 PST (17:37 UTC) |
| **Resolution Time** | 13:54 PST (21:54 UTC) |
| **Impact** | Global internet disruption |
| **Region** | US-EAST-1 (Northern Virginia) |
| **Services Affected** | S3, EC2, EBS, Lambda, Websites |
| **Estimated Economic Impact** | $150M+ in losses |
| **Root Cause** | Human error - typo in operational command |

## The Most Expensive Typo in History

```mermaid
gantt
    title AWS S3 February 28, 2017 - The $150M Typo
    dateFormat HH:mm
    axisFormat %H:%M PST

    section Normal Operations
    Standard S3 Operations :done, normal, 09:00, 09:37
    Billing System Issue :active, issue, 09:30, 09:37

    section The Typo Disaster
    Incorrect Command Executed :crit, typo, 09:37, 09:38
    Index Subsystem Shutdown :crit, index, 09:38, 12:26
    Placement Subsystem Down :crit, place, 09:38, 13:54

    section Internet Collapse
    S3 APIs Unavailable :crit, s3, 09:38, 13:54
    Downstream Services Fail :crit, cascade, 09:40, 13:54
    Dashboard Cannot Update :crit, dash, 09:38, 11:37

    section Recovery Process
    Index Subsystem Recovery :active, idx_rec, 12:26, 13:18
    Placement Recovery :active, place_rec, 13:18, 13:54
    Full Service Restoration :done, restore, 13:54, 14:30
```

## Global Infrastructure Collapse

```mermaid
graph TB
    subgraph Internet[Global Internet Services]
        WEB1[Netflix<br/>❌ Cannot stream<br/>🎬 Video errors]
        WEB2[Slack<br/>❌ File uploads fail<br/>💬 Images broken]
        WEB3[Trello<br/>❌ Board images missing<br/>📋 Attachments gone]
        WEB4[Medium<br/>❌ Articles unreadable<br/>📝 Images broken]
        WEBN[1000+ Other Sites<br/>❌ Broken layouts<br/>🌐 Missing assets]
    end

    subgraph EdgePlane["Edge Plane"]
        CF[CloudFront CDN<br/>❌ Origin fetch fails<br/>📡 502 Bad Gateway]
        ELB[Elastic Load Balancer<br/>❌ Health checks fail<br/>⚖️ Cannot route traffic]
    end

    subgraph ServicePlane["Service Plane"]
        subgraph S3Core[S3 Core Services - TOTAL FAILURE]
            S3API[S3 API Gateway<br/>❌ All endpoints down<br/>🔌 Cannot process requests]
            S3WEB[S3 Web Console<br/>❌ Admin interface dead<br/>🖥️ Cannot manage buckets]
        end

        subgraph AWSServices[AWS Services - CASCADING FAILURE]
            EC2[EC2 Service<br/>❌ Cannot launch instances<br/>🖥️ AMI storage in S3]
            EBS[EBS Service<br/>❌ Snapshot restore fails<br/>💾 Snapshots stored in S3]
            LAMBDA[Lambda Service<br/>❌ Function deployment fails<br/>⚡ Code packages in S3]
        end
    end

    subgraph StatePlane[State Plane - #FF8800 - THE EPICENTER]
        subgraph S3Infrastructure[S3 Storage Infrastructure US-EAST-1]
            subgraph IndexSubsystem[Index Subsystem - DEAD]
                INDEX1[Index Server 1<br/>❌ REMOVED BY MISTAKE<br/>💀 Critical metadata lost]
                INDEX2[Index Server 2<br/>❌ REMOVED BY MISTAKE<br/>💀 Critical metadata lost]
                INDEXN[Index Server N<br/>❌ REMOVED BY MISTAKE<br/>💀 Critical metadata lost]
            end

            subgraph PlacementSubsystem[Placement Subsystem - DEAD]
                PLACE1[Placement Server 1<br/>❌ REMOVED BY MISTAKE<br/>💀 Cannot allocate storage]
                PLACE2[Placement Server 2<br/>❌ REMOVED BY MISTAKE<br/>💀 Cannot allocate storage]
                PLACEN[Placement Server N<br/>❌ REMOVED BY MISTAKE<br/>💀 Cannot allocate storage]
            end

            subgraph BillingSubsystem[Billing Subsystem - TARGET]
                BILL1[Billing Server 1<br/>✅ Successfully removed<br/>🎯 Original target]
                BILL2[Billing Server 2<br/>✅ Successfully removed<br/>🎯 Original target]
            end

            subgraph StorageNodes[Storage Nodes - HEALTHY BUT UNREACHABLE]
                STORAGE[Physical Storage<br/>✅ Data intact<br/>📚 Cannot be accessed]
            end
        end
    end

    subgraph ControlPlane[Control Plane - #CC0000 - BLIND]
        subgraph Monitoring[Monitoring - DEPENDENCY FAILURE]
            DASH[AWS Service Dashboard<br/>❌ Depends on S3<br/>📊 Cannot update status]
            CW[CloudWatch<br/>❌ Metrics storage in S3<br/>📈 Blind to the crisis]
        end

        subgraph Operations[Operations - MANUAL ONLY]
            TWITTER[AWS Twitter Account<br/>✅ Manual updates only<br/>🐦 Primary communication]
            PHONE[Phone Tree<br/>✅ Emergency escalation<br/>📞 All hands on deck]
        end

        subgraph DebugCommand[The Fatal Command]
            OPERATOR[AWS Operator<br/>👤 Debugging billing issue<br/>⌨️ Typo in command]
            TOOL[Capacity Removal Tool<br/>❌ No safeguards<br/>🔧 Removed wrong servers]
        end
    end

    %% The critical failure flow
    OPERATOR -.->|❌ TYPED WRONG COMMAND| TOOL
    TOOL -.->|💥 MASSIVE REMOVAL| INDEX1
    TOOL -.->|💥 MASSIVE REMOVAL| INDEX2
    TOOL -.->|💥 MASSIVE REMOVAL| INDEXN
    TOOL -.->|💥 MASSIVE REMOVAL| PLACE1
    TOOL -.->|💥 MASSIVE REMOVAL| PLACE2
    TOOL -.->|💥 MASSIVE REMOVAL| PLACEN

    %% Cascading failures
    INDEX1 -.->|❌ NO METADATA| S3API
    PLACE1 -.->|❌ NO ALLOCATION| S3API
    S3API -.->|❌ API DOWN| EC2
    S3API -.->|❌ API DOWN| EBS
    S3API -.->|❌ API DOWN| LAMBDA
    S3API -.->|❌ API DOWN| CF
    CF -.->|❌ ORIGIN FAIL| WEB1
    CF -.->|❌ ORIGIN FAIL| WEB2
    CF -.->|❌ ORIGIN FAIL| WEB3

    %% Monitoring dependency failure
    S3API -.->|❌ CANNOT ACCESS| DASH
    DASH -.->|❌ BLIND| TWITTER

    %% Apply four-plane colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class CF,ELB edgeStyle
    class S3API,S3WEB,EC2,EBS,LAMBDA serviceStyle
    class INDEX1,INDEX2,INDEXN,PLACE1,PLACE2,PLACEN,BILL1,BILL2,STORAGE stateStyle
    class DASH,CW,TWITTER,PHONE,OPERATOR,TOOL controlStyle
```

## The Fatal Command Sequence

### Phase 1: The Setup (09:30-09:37 PST)
```mermaid
sequenceDiagram
    participant TEAM as S3 Team
    participant BILLING as Billing System
    participant OPERATOR as AWS Operator
    participant TOOL as Capacity Removal Tool

    Note over TEAM,TOOL: February 28, 2017 - 9:30 AM PST

    BILLING->>TEAM: 🚨 Billing system performance issue
    TEAM->>OPERATOR: Debug the billing subsystem
    OPERATOR->>OPERATOR: Need to remove some billing servers

    Note over OPERATOR: Prepare capacity removal command
    OPERATOR->>TOOL: Prepare command to remove billing servers

    Note over TEAM,TOOL: 9:37 AM PST - The Fatal Moment
    OPERATOR->>TOOL: Execute removal command
    Note over TOOL: ❌ TYPO: Larger server set selected
```

### Phase 2: The Catastrophic Removal (09:37-09:40 PST)
```mermaid
sequenceDiagram
    participant TOOL as Removal Tool
    participant BILLING as Billing Servers
    participant INDEX as Index Subsystem
    parameter PLACEMENT as Placement Subsystem
    participant S3 as S3 API

    Note over TOOL,S3: 9:37 AM PST - Command Execution

    TOOL->>BILLING: ✅ Remove billing servers (intended)
    TOOL->>INDEX: ❌ Remove index servers (MISTAKE)
    TOOL->>PLACEMENT: ❌ Remove placement servers (MISTAKE)

    Note over INDEX: Index subsystem offline
    Note over PLACEMENT: Placement subsystem offline

    INDEX--xS3: ❌ Cannot locate objects
    PLACEMENT--xS3: ❌ Cannot allocate new storage
    S3->>S3: ❌ All operations fail

    Note over TOOL,S3: 9:40 AM PST - S3 completely unavailable
```

### Phase 3: The Internet Breaks (09:40-12:26 PST)
```mermaid
sequenceDiagram
    participant USERS as Internet Users
    participant SITES as Websites/Apps
    participant CDN as CloudFront CDN
    participant S3 as S3 API
    participant AWS_DASH as AWS Dashboard

    Note over USERS,AWS_DASH: 9:40 AM PST - Cascade Begins

    USERS->>SITES: Load website
    SITES->>CDN: Request images/assets
    CDN->>S3: Fetch from S3 origin
    S3--xCDN: ❌ 503 Service Unavailable

    CDN--xSITES: ❌ 502 Bad Gateway
    SITES--xUSERS: ❌ Broken layouts, missing images

    Note over USERS: Websites breaking across the internet

    USERS->>AWS_DASH: Check AWS status
    AWS_DASH->>S3: Load dashboard assets
    S3--xAWS_DASH: ❌ Cannot load
    AWS_DASH--xUSERS: ❌ Dashboard broken too

    Note over USERS,AWS_DASH: 12:26 PM PST - Partial recovery begins
```

### Phase 4: The Long Recovery (12:26-13:54 PST)
```mermaid
sequenceDiagram
    participant SRE as AWS SRE Team
    participant INDEX as Index Subsystem
    participant PLACEMENT as Placement Subsystem
    participant S3 as S3 Services
    participant WORLD as Internet

    Note over SRE,WORLD: 12:26 PM PST - Index Recovery Begins

    SRE->>INDEX: Restart index subsystem
    INDEX->>INDEX: ⚠️ Full restart required (hasn't been done in years)
    INDEX->>INDEX: Validate metadata integrity
    INDEX->>INDEX: Rebuild index structures

    Note over INDEX: Massive growth since last restart
    INDEX->>S3: ✅ GET, LIST, DELETE working
    S3->>WORLD: ⚠️ Read operations restored

    Note over SRE,WORLD: 1:18 PM PST - Index fully recovered

    SRE->>PLACEMENT: Restart placement subsystem
    PLACEMENT->>PLACEMENT: Restart and integrity checks
    PLACEMENT->>S3: ✅ PUT operations working

    Note over SRE,WORLD: 1:54 PM PST - Full S3 recovery
    S3->>WORLD: ✅ All operations normal
```

## Impact Analysis & Economic Damage

### Service Recovery Timeline
```mermaid
graph LR
    subgraph RecoveryPhases[Recovery Phases]
        T1[09:37 PST<br/>100% Operational<br/>Normal S3 service]
        T2[09:40 PST<br/>0% Operational<br/>Complete S3 failure]
        T3[12:26 PST<br/>40% Operational<br/>Read operations only]
        T4[13:18 PST<br/>85% Operational<br/>Most operations work]
        T5[13:54 PST<br/>100% Operational<br/>Full restoration]
    end

    T1 --> T2
    T2 --> T3
    T3 --> T4
    T4 --> T5

    style T1 fill:#00AA00
    style T2 fill:#CC0000
    style T3 fill:#FF8800
    style T4 fill:#FFAA00
    style T5 fill:#00AA00
```

### Economic Impact Assessment
| Sector | Impact Description | Duration | Est. Loss |
|--------|-------------------|----------|-----------|
| **E-commerce** | Online shopping broken | 4h 17m | $75M |
| **Media & Publishing** | Content delivery failed | 4h 17m | $25M |
| **Enterprise SaaS** | Business applications down | 4h 17m | $20M |
| **Startups & SMBs** | Complete service outage | 4h 17m | $15M |
| **Gaming** | Game assets/saves unavailable | 4h 17m | $8M |
| **Financial Services** | Document/image access failed | 4h 17m | $5M |
| **AWS Revenue Loss** | Direct service credits | 4h 17m | $2M |
| **Total Economic Impact** | | | **$150M** |

### The Domino Effect Analysis
```mermaid
graph TD
    A[S3 US-EAST-1 Down] --> B[CloudFront Origins Fail]
    B --> C[CDN Cannot Serve Assets]
    C --> D[Websites Break Globally]

    A --> E[EC2 Launch Failures]
    E --> F[Cannot Deploy New Instances]
    F --> G[Scaling Events Fail]

    A --> H[EBS Snapshot Restore Fails]
    H --> I[Disaster Recovery Broken]

    A --> J[Lambda Deployment Fails]
    J --> K[Serverless Apps Down]

    A --> L[S3 Console Unavailable]
    L --> M[Cannot Manage Storage]

    A --> N[AWS Dashboard Down]
    N --> O[Cannot Report Status]
    O --> P[Twitter Only Communication]

    style A fill:#CC0000
    style D fill:#CC0000
    style K fill:#CC0000
    style P fill:#FF8800
```

## Technical Deep Dive

### S3 Architecture & Subsystem Dependencies
```mermaid
graph TB
    subgraph S3Architecture[S3 Internal Architecture]
        subgraph Frontend[Frontend Layer]
            API[S3 API Endpoints<br/>REST/SOAP Interface]
            WEB[S3 Web Console<br/>Management Interface]
        end

        subgraph Metadata[Metadata Layer - CRITICAL]
            INDEX[Index Subsystem<br/>📍 Object Location Mapping<br/>🗂️ Bucket/Key → Physical Location<br/>❌ REMOVED BY MISTAKE]
        end

        subgraph Allocation[Storage Allocation - CRITICAL]
            PLACE[Placement Subsystem<br/>📦 Storage Allocation<br/>🎯 Where to store new objects<br/>❌ REMOVED BY MISTAKE]
        end

        subgraph Storage[Physical Storage]
            DISK[Storage Nodes<br/>💾 Actual object data<br/>✅ Data intact, just unreachable]
        end

        subgraph Billing[Billing Layer - ORIGINAL TARGET]
            BILL[Billing Subsystem<br/>💰 Usage tracking & billing<br/>✅ Successfully removed]
        end
    end

    API --> INDEX
    API --> PLACE
    WEB --> INDEX
    WEB --> PLACE

    INDEX --> DISK
    PLACE --> DISK

    INDEX -.->|❌ GONE| API
    PLACE -.->|❌ GONE| API

    style INDEX fill:#CC0000
    style PLACE fill:#CC0000
    style API fill:#CC0000
```

### The Command That Broke Everything
```bash
# What was intended (remove small set of billing servers):
aws s3-capacity remove --subsystem=billing --count=small

# What was actually typed (remove large set including critical subsystems):
aws s3-capacity remove --subsystem=billing --count=large
# This expanded to include index and placement subsystems
```

### Restart Complexity Problem
```mermaid
graph TD
    A[Subsystem Restart Required] --> B{Last Restart When?}
    B -->|Years Ago| C[Massive Growth Since Then]
    C --> D[Terabytes of Metadata]
    D --> E[Safety Checks Required]
    E --> F[Integrity Validation]
    F --> G[Index Rebuilding]
    G --> H[Hours of Recovery Time]

    B -->|Recently| I[Quick Restart]
    I --> J[Minutes of Downtime]

    style C fill:#FF8800
    style H fill:#CC0000
    style J fill:#00AA00
```

## Root Cause Analysis

### The Perfect Storm Factors
```mermaid
mindmap
  root)Feb 28 RCA(
    Human Factor
      Operational Pressure
      Debugging Under Stress
      Manual Command Entry
      No Double-Check Process
    Technical Design
      Dangerous Tooling
      No Safeguards
      Broad Server Selection
      Critical Dependencies
    Operational
      No Staged Rollouts
      Single Region Dependency
      Infrequent Restarts
      Limited Testing
    Recovery
      Complex Restart Process
      Massive Scale Growth
      Integrity Checks Required
      Multi-Hour Recovery
```

### The Chain of Errors
```mermaid
graph TD
    A[Billing System Issue] --> B[Need to Remove Servers]
    B --> C[Use Capacity Removal Tool]
    C --> D[Enter Command Manually]
    D --> E[Make Typo in Command]
    E --> F[Tool Selects Wrong Servers]
    F --> G[Remove Critical Subsystems]
    G --> H[S3 Completely Down]
    H --> I[Internet Services Break]
    I --> J[Dashboard Also Broken]
    J --> K[Cannot Communicate Status]
    K --> L[Twitter-Only Updates]
    L --> M[Hours of Recovery]

    style E fill:#CC0000
    style F fill:#CC0000
    style G fill:#CC0000
    style H fill:#CC0000
```

## Remediation & Prevention

### Immediate Actions (Completed during incident)
- [x] **Index Subsystem Recovery**: Full restart with integrity checks
- [x] **Placement Subsystem Recovery**: Rebuild storage allocation maps
- [x] **Communication**: Twitter updates while dashboard down
- [x] **Service Validation**: Extensive testing before declaring recovery

### Short-term Fixes (30 days)
- [x] **Tool Safeguards**: Added confirmation prompts to removal tool
- [x] **Command Validation**: Require explicit server list specification
- [x] **Operational Training**: Enhanced procedures for critical operations
- [x] **Dashboard Independence**: Moved status dashboard off S3 dependency

### Long-term Solutions (6 months)
- [x] **Region Partitioning**: Split index/placement systems across AZs
- [x] **Faster Recovery**: Regular restart testing and optimization
- [x] **Better Tooling**: Safer operational tools with built-in safeguards
- [x] **Incremental Restart**: Capability to restart subsystems incrementally

## Prevention Framework

### Operational Safety Checklist
```mermaid
flowchart TD
    A[Critical Operation Request] --> B{High Impact?}
    B -->|Yes| C[Require Peer Review]
    B -->|No| D[Standard Process]

    C --> E[Dry Run Required]
    E --> F[Command Validation]
    F --> G[Staged Execution]
    G --> H[Monitoring Throughout]

    D --> F

    H --> I{Issues Detected?}
    I -->|Yes| J[Immediate Rollback]
    I -->|No| K[Complete Operation]

    style C fill:#FF8800
    style E fill:#FF8800
    style J fill:#CC0000
```

### Tool Safety Design
```mermaid
graph LR
    A[Dangerous Tool] --> B[Add Confirmation Prompts]
    B --> C[Require Explicit Parameters]
    C --> D[Show Impact Preview]
    D --> E[Time Delay/Cancellation]
    E --> F[Staged Execution]
    F --> G[Monitoring & Rollback]

    style A fill:#CC0000
    style B fill:#FF8800
    style F fill:#00AA00
    style G fill:#00AA00
```

## Engineering Lessons

### The Human Error Amplification Problem
```mermaid
sequenceDiagram
    participant H as Human
    participant T as Tool
    participant S as System
    participant W as World

    Note over H,W: How a Single Typo Became Global Disaster

    H->>T: Command with typo
    T->>T: No validation or safeguards
    T->>S: Execute on wrong targets
    S->>S: Critical subsystems removed
    S->>W: Global service unavailable

    Note over H,W: Better: Defense in Depth

    H->>T: Command with typo
    T->>H: ⚠️ Confirm: This will affect X servers
    H->>T: ❌ Cancel (realizes mistake)
    Note over H,W: Disaster prevented
```

### The Dependency Cascade Visualization
```mermaid
graph TD
    subgraph Level1[Level 1: Core Storage]
        S3[S3 Storage Service]
    end

    subgraph Level2[Level 2: AWS Services]
        EC2[EC2 Instances]
        EBS[EBS Volumes]
        LAMBDA[Lambda Functions]
        CF[CloudFront CDN]
    end

    subgraph Level3[Level 3: Customer Apps]
        WEBAPP[Web Applications]
        MOBILE[Mobile Apps]
        SAAS[SaaS Platforms]
    end

    subgraph Level4[Level 4: End Users]
        USERS[Millions of Users]
    end

    S3 --> EC2
    S3 --> EBS
    S3 --> LAMBDA
    S3 --> CF

    EC2 --> WEBAPP
    EBS --> WEBAPP
    LAMBDA --> MOBILE
    CF --> SAAS

    WEBAPP --> USERS
    MOBILE --> USERS
    SAAS --> USERS

    style S3 fill:#CC0000
    style USERS fill:#CC0000
```

## War Stories & Lessons for 3 AM Engineers

### 🚨 Critical Warning Signs
1. **Manual capacity operations** = potential for human error
2. **Subsystem restart taking hours** = architectural scaling problem
3. **Dashboard depends on failed service** = monitoring blind spot
4. **Single region hosts critical metadata** = single point of failure

### 🛠️ Emergency Procedures
```mermaid
flowchart TD
    A[Major Storage Outage] --> B{Can Access Monitoring?}
    B -->|No| C[Use External Status Sources]
    B -->|Yes| D[Check Subsystem Health]

    C --> E[Social Media Updates]
    E --> F[Phone Tree Activation]

    D --> G{Metadata Systems OK?}
    G -->|No| H[Prepare for Long Recovery]
    G -->|Yes| I[Standard Incident Response]

    H --> J[Multi-Hour Timeline]
    J --> K[Communicate Extended Outage]

    style H fill:#CC0000
    style J fill:#FF8800
    style K fill:#FF8800
```

### 💡 Key Takeaways
- **Human error** is **inevitable** - **design systems** to **contain it**
- **Critical tools** need **multiple confirmation** steps
- **Restart complexity** grows with **system age** and **scale**
- **Monitoring dependencies** create **communication blind spots**
- **Single regions** hosting **metadata** = **global risk**

---

*"We want to apologize for the impact this event caused for our customers. S3 has experienced massive growth over the last several years and the process of restarting these services and running the necessary safety checks to validate the integrity of the metadata took longer than expected."* - AWS Team

**Quote from postmortem**: *"An incorrect input was entered on the command line that intended to remove a small number of servers for one of the S3 subsystems that is used by the S3 billing process. Unfortunately, one of the inputs to the command was entered incorrectly and a larger set of servers was removed than intended."*

**Impact**: This incident led to AWS's comprehensive operational safety improvements and influenced the entire cloud industry's approach to operational tooling and safety procedures. It remains one of the most studied outages in internet history.