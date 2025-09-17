# 15-CASE-STUDY-SEED-LIST.md
# Comprehensive Case Study Seed List for Massively Scalable Architectures (2020-2025)
# Version 5.0

## Priority Systems for Immediate Documentation (2024-2025 Focus)

### Prioritization Criteria
- **A-Confidence**: Recent detailed blog posts with explicit architecture
- **B-Confidence**: Conference talks + engineering blogs with good details
- **C-Confidence**: Limited sources, requires investigation
- **AVOID**: Companies with only marketing content or stale documentation

### Scale Verification Priority
1. **P0 - Immediate**: A-confidence with verified 2024 scale metrics
2. **P1 - Fast Track**: B-confidence with strong 2023-2024 evidence
3. **P2 - Research**: C-confidence requiring investigation
4. **P3 - Defer**: Insufficient recent documentation

### Q1 2025: Social & Messaging (40 Systems)

#### Social Networks & Feeds (20 Systems)

##### Tier 1 - Verified Scale (Confidence: A)
| System | Organization | Scale Metrics | Key Innovations | Primary Sources |
|--------|--------------|---------------|-----------------|-----------------|
| Discord | Discord Inc. | 10M concurrent, 25M msg/s | Rust service mesh, hybrid push/pull | [Blog 2023](https://discord.com/blog/how-discord-stores-trillions-of-messages) |
| Twitter/X | X Corp | 500M tweets/day, 150B timeline deliveries/day | Graph+timeline, celebrity storm mode | [Blog 2023](https://blog.twitter.com/engineering) |
| Instagram | Meta | 2B users, 95M photos/day | Reels pipeline, explore ML, cassandra at scale | [Engineering 2023](https://instagram-engineering.com/) |
| LinkedIn | Microsoft | 1B members, 2M posts/min | Economic graph, real-time feed, kafka streams | [Engineering 2023](https://engineering.linkedin.com) |
| Reddit | Reddit Inc. | 50M DAU, 100k communities | Community sharding, vote streams, comment trees | [Blog 2024](https://redditblog.com/engineering) |

##### Tier 2 - Strong Evidence (Confidence: B)
| System | Organization | Scale Metrics | Key Innovations | Primary Sources |
|--------|--------------|---------------|-----------------|-----------------|
| Pinterest | Pinterest | 450M MAU, 240B pins | Visual search graph, home feed ML, sharded MySQL | [Medium 2023](https://medium.com/pinterest-engineering) |
| TikTok | ByteDance | 1B MAU, 1B videos/day | For You algorithm, edge CDN, ML pipeline | [Tech talks 2024](https://www.bytedance.com/tech) |
| Snapchat | Snap Inc. | 400M DAU, 5B snaps/day | Ephemeral storage, real-time filters | [Engineering 2023](https://eng.snap.com) |
| Facebook | Meta | 3B MAU, 4PB/day | TAO graph store, region-aware caching | [Engineering 2023](https://engineering.fb.com) |
| Mastodon | Decentralized | 10M users, federated | ActivityPub, distributed moderation | [GitHub 2024](https://github.com/mastodon) |

#### Messaging & Communication (20 Systems)

##### Tier 1 - Verified Scale (Confidence: A)
| System | Organization | Scale Metrics | Key Innovations | Primary Sources |
|--------|--------------|---------------|-----------------|-----------------|
| WhatsApp | Meta | 100B msgs/day, 2B users | E2E at scale, status privacy, multi-device | [Engineering 2023](https://engineering.fb.com/whatsapp) |
| Slack | Salesforce | 20M concurrent, 1B messages/week | WebSocket scale, presence, shared channels | [Blog 2023](https://slack.engineering) |
| Telegram | Telegram | 700M MAU, 15B msgs/day | Distributed storage, channels, bots | [Core docs 2024](https://core.telegram.org) |
| Signal | Signal Foundation | 40M users, E2E everything | Sealed sender, group E2E, private contact discovery | [Blog 2023](https://signal.org/blog) |
| Teams | Microsoft | 280M users, video scale | Real-time collab, meeting infrastructure | [Tech Community 2024](https://techcommunity.microsoft.com/teams) |

##### Tier 2 - Strong Evidence (Confidence: B)
| System | Organization | Scale Metrics | Key Innovations | Primary Sources |
|--------|--------------|---------------|-----------------|-----------------|
| WeChat | Tencent | 1.3B MAU, super app | Mini programs, payments integration | QCon talks 2023 |
| Messenger | Meta | 1B users, 20B msgs/day | Cross-app messaging, business platform | Engineering blog 2023 |
| Viber | Rakuten | 260M users, encrypted | Multi-device sync, communities | Tech talks 2023 |
| Line | Z Holdings | 200M MAU, stickers | Timeline, official accounts | Developer docs 2024 |
| Element | Element | 30M users, Matrix protocol | Decentralized, federated, E2E | Matrix.org specs 2024 |

### Q2 2025: Media & Mobility (40 Systems)

#### Media Streaming & Delivery (20 Systems)

##### Tier 1 - Verified Scale (Confidence: A)
| System | Organization | Scale Metrics | Key Innovations | Primary Sources |
|--------|--------------|---------------|-----------------|-----------------|
| Netflix | Netflix | 238M subs, 2EB/quarter | Open Connect CDN, chaos engineering, ABR | [Tech Blog 2024](https://netflixtechblog.com) |
| YouTube | Google | 2.7B users, 1B hours/day | Transcoding pipeline, Cobalt, recommendations | [Engineering 2023](https://youtube-eng.googleblog.com) |
| Twitch | Amazon | 15M DAU, 2.5M concurrent | Live streaming, low latency, IVS | [Engineering 2023](https://blog.twitch.tv/engineering) |
| Spotify | Spotify | 500M users, 100M tracks | Audio streaming, discovery, personalization | [Engineering 2024](https://engineering.atspotify.com) |
| Disney+ | Disney | 150M subs, global CDN | Multi-CDN strategy, BAMTech platform | [Tech Blog 2023](https://medium.com/disney-streaming) |

##### Tier 2 - Strong Evidence (Confidence: B)
| System | Organization | Scale Metrics | Key Innovations | Primary Sources |
|--------|--------------|---------------|-----------------|-----------------|
| Hulu | Disney | 48M subs, live TV | Dynamic ad insertion, live streaming | Tech talks 2023 |
| HBO Max | Warner Bros | 95M subs, 4K streaming | Multi-region, personalization | Engineering blog 2023 |
| Apple Music | Apple | 100M subs, lossless | Spatial audio, sync across devices | WWDC 2023 |
| SoundCloud | SoundCloud | 30M creators, 320M tracks | Creator tools, real-time comments | Engineering 2023 |
| Vimeo | Vimeo | 260M users, live events | Adaptive streaming, live production | Blog 2024 |

#### Mobility & Logistics (20 Systems)

##### Tier 1 - Verified Scale (Confidence: A)
| System | Organization | Scale Metrics | Key Innovations | Primary Sources |
|--------|--------------|---------------|-----------------|-----------------|
| Uber | Uber | 130M users, 25M trips/day | H3 geo-indexing, marketplace, dispatch | [Engineering 2024](https://www.uber.com/blog/engineering) |
| Lyft | Lyft | 20M riders, 2M drivers | Prime time pricing, routing, Level 5 | [Engineering 2023](https://eng.lyft.com) |
| DoorDash | DoorDash | 25M users, 1M dashers | Assignment algorithm, batching, prediction | [Engineering 2024](https://doordash.engineering) |
| Instacart | Maplebear | 10M users, 500k shoppers | Inventory sync, shopper routing, fulfillment | [Tech Blog 2023](https://tech.instacart.com) |
| Grab | Grab | 200M users, super app | Multi-service platform, GrabMaps | [Engineering 2023](https://engineering.grab.com) |

##### Tier 2 - Strong Evidence (Confidence: B)
| System | Organization | Scale Metrics | Key Innovations | Primary Sources |
|--------|--------------|---------------|-----------------|-----------------|
| Uber Eats | Uber | 85M users, 600k restaurants | Virtual restaurants, dark stores | Engineering 2024 |
| Deliveroo | Deliveroo | 7.5M users, 158k restaurants | Frank algorithm, Editions | Engineering 2023 |
| Gojek | GoTo | 170M users, 20+ services | Super app, GoPay integration | Tech blog 2023 |
| Rappi | Rappi | 30M users, LATAM | Multi-vertical, RappiPay | Engineering 2023 |
| Swiggy | Swiggy | 150M users, India | Hyperlocal, Instamart | Tech talks 2024 |

### Q3 2025: Commerce & FinTech (40 Systems)

#### E-Commerce & Marketplaces (20 Systems)

##### Tier 1 - Verified Scale (Confidence: A)
| System | Organization | Scale Metrics | Key Innovations | Primary Sources |
|--------|--------------|---------------|-----------------|-----------------|
| Shopify | Shopify | 2M merchants, BFCM scale | Cell-based architecture, shop pay, POS | [Engineering 2024](https://shopify.engineering) |
| Amazon | Amazon | 300M users, 12M products | Service mesh, chaos tools, one-click | [Blog 2023](https://aws.amazon.com/blogs/architecture) |
| eBay | eBay | 130M buyers, 1.7B listings | Search infrastructure, Tess platform | [Tech Blog 2023](https://tech.ebayinc.com) |
| MercadoLibre | MercadoLibre | 90M users, LATAM leader | Pix integration, Fury platform | [Engineering 2024](https://medium.com/mercadolibre-tech) |
| Etsy | Etsy | 90M buyers, 5.5M sellers | Search relevance, personalization | [Code as Craft 2023](https://www.etsy.com/codeascraft) |

##### Tier 2 - Strong Evidence (Confidence: B)
| System | Organization | Scale Metrics | Key Innovations | Primary Sources |
|--------|--------------|---------------|-----------------|-----------------|
| Alibaba | Alibaba | 1B users, Singles Day | Distributed transactions, OceanBase | Tech talks 2023 |
| Flipkart | Walmart | 450M users, Big Billion Days | Supply chain, Ekart logistics | Engineering 2023 |
| Target | Target | 100M users, omnichannel | Store fulfillment, same-day | Tech blog 2024 |
| Wayfair | Wayfair | 20M customers, 30M products | Visual search, AR | Engineering 2023 |
| Zalando | Zalando | 50M customers, fashion | Size recommendation, fulfillment | Blog 2024 |

#### FinTech & Payments (20 Systems)

##### Tier 1 - Verified Scale (Confidence: A)
| System | Organization | Scale Metrics | Key Innovations | Primary Sources |
|--------|--------------|---------------|-----------------|-----------------|
| Stripe | Stripe | 3M websites, 135+ currencies | Idempotency, exactly-once, radar fraud | [Blog 2024](https://stripe.com/blog/engineering) |
| Square | Block | 4M sellers, hardware+software | Offline mode, Cash App, crypto | [Blog 2023](https://developer.squareup.com/blog) |
| PayPal | PayPal | 430M users, 25 currencies | Fraud detection, Braintree, Venmo | [Engineering 2023](https://medium.com/paypal-tech) |
| Coinbase | Coinbase | 100M users, crypto exchange | Exchange matching, custody, staking | [Blog 2024](https://blog.coinbase.com/engineering) |
| Klarna | Klarna | 150M users, BNPL leader | Risk scoring, smooth checkout | [Engineering 2023](https://engineering.klarna.com) |

##### Tier 2 - Strong Evidence (Confidence: B)
| System | Organization | Scale Metrics | Key Innovations | Primary Sources |
|--------|--------------|---------------|-----------------|-----------------|
| Adyen | Adyen | 26k merchants, unified commerce | Global acquiring, tokenization | Tech blog 2023 |
| Wise | Wise | 16M users, borderless | Multi-currency, real rate | Engineering 2024 |
| Revolut | Revolut | 35M users, super app | Banking, crypto, stock trading | Blog 2023 |
| Robinhood | Robinhood | 23M users, commission-free | Real-time quotes, options | Engineering 2023 |
| Plaid | Plaid | 8k apps, bank connections | Account linking, open banking | Blog 2024 |

### Q4 2025: Cloud, Data & AI (40 Systems)

#### Cloud & Edge Platforms (15 Systems)

##### Tier 1 - Verified Scale (Confidence: A)
| System | Organization | Scale Metrics | Key Innovations | Primary Sources |
|--------|--------------|---------------|-----------------|-----------------|
| Cloudflare | Cloudflare | 20% of web, 275+ cities | Workers, Durable Objects, R2, D1, KV | [Blog 2024](https://blog.cloudflare.com) |
| Fastly | Fastly | 10% of web, edge cloud | Compute@Edge, WebAssembly, real-time | [Blog 2023](https://www.fastly.com/blog) |
| Fly.io | Fly.io | Global, 30+ regions | Distributed VMs, edge PostgreSQL, Firecracker | [Blog 2024](https://fly.io/blog) |
| Vercel | Vercel | 1M+ sites, edge functions | ISR, edge middleware, serverless | [Blog 2023](https://vercel.com/blog) |
| Netlify | Netlify | 3M+ devs, JAMstack | Edge handlers, build plugins | [Blog 2024](https://www.netlify.com/blog) |

#### Data Platforms (15 Systems)

##### Tier 1 - Verified Scale (Confidence: A)
| System | Organization | Scale Metrics | Key Innovations | Primary Sources |
|--------|--------------|---------------|-----------------|-----------------|
| Snowflake | Snowflake | Exabyte scale, 7k customers | Separation compute/storage, zero-copy | [Blog 2024](https://www.snowflake.com/blog/category/engineering) |
| Databricks | Databricks | 9k customers, lakehouse | Delta Lake, Unity Catalog, Photon | [Blog 2023](https://www.databricks.com/blog/category/engineering) |
| ClickHouse | ClickHouse Inc | PB scale, 200+ companies | Columnar OLAP, MergeTree, real-time | [Blog 2024](https://clickhouse.com/blog) |
| Confluent | Confluent | Kafka cloud, 75% Fortune 500 | KRaft, serverless, Stream Governance | [Blog 2023](https://www.confluent.io/blog) |
| MongoDB | MongoDB | 45k customers, document DB | Sharding, Atlas, vector search | [Blog 2024](https://www.mongodb.com/blog/channel/engineering) |

#### AI/ML Infrastructure (10 Systems)

##### Tier 1 - Verified Scale (Confidence: A)
| System | Organization | Scale Metrics | Key Innovations | Primary Sources |
|--------|--------------|---------------|-----------------|-----------------|
| OpenAI | OpenAI | 100M users, GPT scale | Model serving, RLHF, safety | [Blog 2024](https://openai.com/blog) |
| Anthropic | Anthropic | Claude scale | Constitutional AI, context windows | Research 2024 |
| Pinecone | Pinecone | Vector DB, billion scale | ANN indexing, hybrid search | [Blog 2023](https://www.pinecone.io/blog) |
| Hugging Face | Hugging Face | 1M+ models, inference API | Model hub, Transformers, Spaces | [Blog 2024](https://huggingface.co/blog) |
| Weights & Biases | W&B | ML experiment tracking | Distributed training, sweeps | [Blog 2023](https://wandb.ai/site/blog) |

## Source Discovery Seeds

### Primary Engineering Blogs (RSS Feeds Available)
```yaml
rss_feeds:
  tier_1:
    - https://discord.com/blog/rss
    - https://netflixtechblog.com/feed
    - https://engineering.atspotify.com/feed/
    - https://shopify.engineering/blog.rss
    - https://blog.cloudflare.com/rss/
    - https://stripe.com/blog/feed.rss

  tier_2:
    - https://engineering.linkedin.com/blog.rss
    - https://engineering.fb.com/feed/
    - https://medium.com/feed/pinterest-engineering
    - https://www.uber.com/blog/engineering/feed/
    - https://doordash.engineering/feed/
```

### Conference Sources (2023-2024)
```yaml
conferences:
  must_watch:
    - QCon (InfoQ): Architecture tracks
    - KubeCon: Scale talks
    - Kafka Summit: Streaming architectures
    - AWS re:Invent: Customer architectures
    - Google Cloud Next: Scale stories
    - SREcon: Production insights
    - Strange Loop: Distributed systems
    - VLDB: Data systems at scale
```

### 2024-2025 Verification Priority Matrix

| Priority | Confidence | Documentation Quality | Scale Evidence | Examples | Action |
|----------|------------|----------------------|----------------|----------|--------|
| P0 | A | Detailed engineering blogs 2024 | Explicit metrics | Discord, Netflix, Cloudflare | Immediate implementation |
| P1 | A-B | Good blogs + conference talks | Mostly explicit | Stripe, Shopify, Uber | Fast track (week 1-2) |
| P2 | B | Some recent sources | Partially verified | LinkedIn, Instagram | Research then implement |
| P3 | B-C | Limited recent info | Needs investigation | WeChat, TikTok | Defer or research intensive |
| SKIP | C | Only marketing/old sources | Unverified claims | Many enterprise systems | Avoid until better sources |

## Implementation Sequence

### Wave 1 (Week 1-2: P0 High-Confidence Systems)
**Target: 10 systems with A-confidence**
1. **Discord** - Detailed 2024 Rust service mesh, message storage
2. **Netflix** - Open Connect, chaos engineering, extensive recent blogs
3. **Cloudflare** - Workers, Durable Objects, R2, comprehensive docs
4. **Stripe** - Payment idempotency, fraud detection, well-documented
5. **Shopify** - Cell architecture for BFCM, detailed engineering blog
6. **Uber** - H3 geo-indexing, marketplace dynamics, dispatch system
7. **Spotify** - Audio streaming, discovery, recent architecture updates
8. **Snowflake** - Compute/storage separation, exabyte scale details
9. **WhatsApp** - E2E encryption at 100B msgs/day scale
10. **YouTube** - Transcoding pipeline, recommendation at 1B hours/day

### Wave 2 (Week 3-4: P1 Strong Evidence)
**Target: 15 systems with A-B confidence**
- DoorDash, Lyft, Slack, Signal, Twitch
- LinkedIn, Instagram, PayPal, Coinbase
- Databricks, ClickHouse, MongoDB, Fastly, Vercel

### Wave 3 (Month 2: P2 Research Required)
**Target: 15 systems needing investigation**
- Pinterest, TikTok, Teams, Telegram
- MercadoLibre, eBay, Etsy, Square
- Confluent, Fly.io, Netlify, OpenAI

### Wave 4 (Month 3+: International/Complex)
- WeChat, Grab, Alibaba (requires translation/research)
- Specialized domains requiring deep investigation
- Systems with limited English documentation

## Production-First Quality Assurance

### Must-Have for A-Confidence (P0/P1)
- [ ] **Scale metrics**: Specific numbers with sources (not "millions")
- [ ] **Recent sources**: Primary engineering content from 2023-2024
- [ ] **Failure stories**: How they break and recover in production
- [ ] **Architecture details**: Components, guarantees, mechanisms
- [ ] **Multi-region**: Strategy for global deployment
- [ ] **Production insights**: Real operational challenges

### Warning Signs (Avoid/Defer)
- ❌ **Marketing only**: No technical engineering content
- ❌ **Vague scale**: "Handles millions" without specifics
- ❌ **Stale sources**: Last detailed info > 3 years old
- ❌ **Perfect systems**: No failure modes or challenges discussed
- ❌ **Proprietary**: Claims without verifiable public evidence

### Research Required (P2/P3)
- ⚠️ **Limited sources**: Only 1-2 public references
- ⚠️ **Translation needed**: Non-English primary sources
- ⚠️ **Conference only**: Talks without detailed follow-up blogs
- ⚠️ **Inference heavy**: Architecture requires significant guessing

---

*Version: 1.0.0 | Document 15 of 16 | Last Updated: 2025-03-10*