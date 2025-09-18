# PayPal Global Outage - November 8, 2022

**The 2-Hour DNS Resolution Crisis That Broke Global Digital Payments**

## Incident Overview

| **Metric** | **Value** |
|------------|-----------||
| **Date** | November 8, 2022 |
| **Duration** | 2 hours |
| **Impact** | Checkout failures globally |
| **Users Affected** | 400M+ active accounts |
| **Financial Impact** | $500M+ in failed transactions |
| **Root Cause** | DNS resolution issues |
| **MTTR** | 120 minutes |
| **Key Issue** | DNS provider configuration error |
| **Services Down** | Payment processing, checkout, account access |

```mermaid
graph TB
    subgraph PayPal Payment Network
        CHECKOUT[PayPal Checkout<br/>Payment Processing]
        WALLET[PayPal Wallet<br/>Account Management]
        MERCHANT[Merchant Services<br/>Business Payments]
        API[PayPal API<br/>Developer Integration]
    end

    subgraph Infrastructure Layer
        DNS[DNS Service<br/>Domain Resolution<br/>CONFIGURATION ERROR]
        CDN[Content Delivery<br/>Global Distribution]
        LOADBALANCER[Load Balancers<br/>Traffic Distribution]
        SERVERS[Application Servers<br/>Payment Processing]
    end

    %% DNS failure cascade
    DNS -.->|Cannot resolve domains<br/>13:00 PST| CDN
    CDN -.->|Cannot reach origins<br/>Content delivery failed| LOADBALANCER
    LOADBALANCER -.->|Cannot route traffic<br/>No healthy backends| SERVERS
    SERVERS -.->|Services unreachable<br/>Payment processing down| CHECKOUT

    %% Customer impact
    CHECKOUT -.->|"PayPal temporarily unavailable"<br/>400M+ users affected| CUSTOMERS[E-commerce Shoppers<br/>Small Business Owners<br/>Freelance Workers<br/>International Transfers]

    classDef dnsStyle fill:#FF6B6B,stroke:#8B5CF6,color:#fff,stroke-width:3px
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff,stroke-width:3px
    classDef impactStyle fill:#8B0000,stroke:#660000,color:#fff,stroke-width:4px

    class DNS,CDN,LOADBALANCER,SERVERS dnsStyle
    class CHECKOUT,WALLET,MERCHANT,API serviceStyle
    class CUSTOMERS impactStyle
```

## The Bottom Line

**This incident proved that DNS is still a single point of failure for global payment systems, despite decades of internet infrastructure evolution.**

**Key Takeaways:**
- DNS failures can instantly disable global payment processing
- Payment platforms need redundant DNS providers
- Domain resolution is critical infrastructure for digital payments
- DNS configuration changes need staging and validation

---

*"In digital payments, DNS failures don't just break websites - they break the global economy."*