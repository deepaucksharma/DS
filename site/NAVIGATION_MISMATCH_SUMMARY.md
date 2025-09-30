# Navigation vs Files Mismatch Analysis

**Analysis Date:** 2025-09-30
**Location:** `/home/deepak/DS/site`

## Executive Summary

- **Total files in navigation:** 697
- **Total actual .md files:** 921
- **Navigation entries pointing to missing files:** 142
- **Files not referenced in navigation:** 366

## Critical Issues

### 1. Navigation Entries Pointing to Missing Files (142 files)

These are broken links in the navigation that will cause 404 errors when users click on them.

#### Pattern Files (7 files)
- `patterns/ambassador-gateway-airbnb.md`
- `patterns/api-composition-netflix-bff.md`
- `patterns/canary-release-github.md`
- `patterns/database-per-service-uber.md`
- `patterns/leader-election-kubernetes.md`
- `patterns/strangler-fig-monzo.md`
- `patterns/write-through-cache-facebook.md`

#### Systems Files (135 files)

**Naming Convention Issue:**
The navigation references files with different naming conventions than what actually exists:

##### Systems with `-operations` vs `-ops` mismatch (30 files):
Navigation expects: `production-operations.md`
Files actually named: `production-ops.md`

**Affected systems:**
- airbnb, amazon, cloudflare, discord, github, google, linkedin, meta, microsoft, netflix, openai, shopify, spotify, stripe, twitter, uber, zoom

##### Systems with `storage-architecture` vs `storage` mismatch (30 files):
Navigation expects: `storage-architecture.md`
Files actually named: `storage.md`

**Affected systems:**
- airbnb, amazon, cloudflare, discord, github, google, linkedin, meta, microsoft, netflix, openai, shopify, spotify, stripe, twitter, uber, zoom

##### Systems with numbered vs non-numbered files (75 files):
Some systems have files like `01-complete-architecture.md` but navigation references them without numbers.

**Affected systems with numbered files (9 systems × 8 files each = 72 files):**
- coinbase
- datadog
- doordash
- dropbox
- instacart
- pinterest
- robinhood
- slack
- snap
- square
- tiktok
- twitch

### 2. Files Not Referenced in Navigation (366 files)

These files exist but are "orphaned" - users cannot reach them through navigation.

#### By Category:

**Capacity (10 orphaned files):**
- amazon-prime-day-capacity-planning.md
- bereal-daily-notification-surge-capacity.md
- cloudflare-ddos-mitigation-capacity.md
- github-actions-cicd-capacity-model.md
- netflix-new-years-eve-streaming-surge.md
- openai-gpt4-launch-capacity-planning.md
- shopify-black-friday-cyber-monday-capacity.md
- threads-app-launch-100m-users-5-days.md
- tiktok-live-streaming-capacity.md
- twitter-spaces-live-audio-capacity.md

**Comparisons (7 orphaned files):**
- graphql-vs-rest-vs-grpc-performance.md
- kafka-vs-pulsar-vs-rabbitmq-production.md
- kubernetes-vs-nomad-vs-ecs-production.md
- postgresql-vs-mysql-vs-cockroachdb-scale.md
- rabbitmq-vs-sqs-vs-pubsub.md
- terraform-vs-pulumi-vs-cloudformation-iac.md

**Costs (5 orphaned files):**
- airbnb-database-storage-costs.md
- cdn-cost-analysis-optimization.md
- database-spend-optimization-strategies.md
- discord-voice-video-infrastructure-costs.md
- kubernetes-cost-reduction-optimization.md
- multi-company-cost-optimization-strategies.md
- netflix-annual-spend-breakdown.md
- spotify-streaming-cdn-costs.md

**Debugging (100+ orphaned files):**
Many production debugging guides exist but aren't in navigation, including:
- api-gateway-throttling-debugging.md
- aws-lambda-cold-start-production-debugging.md
- cascading-failure-analysis-guide.md
- database-connection-pool-exhaustion-guide.md
- distributed-transaction-failures.md
- elasticsearch-query-performance-debugging-production.md
- graphql-n-plus-one-production-debugging.md
- kafka-consumer-lag-debugging-production.md
- kubernetes-networking-production-debugging.md
- memory-leak-investigation-guide.md
- microservices-timeout-cascade-production-debugging.md
- rate-limiting-throttling-debugging-production.md
- service-mesh-debugging-guide.md
- zero-downtime-deployment-failures-production-debugging.md
- And 80+ more...

**Incidents (30 orphaned files):**
Major incidents documented but not in navigation:
- aws-s3-february-28-2017-typo-disaster.md
- azure-march-2020-covid-surge.md
- british-airways-july-2022-it-system-failure.md
- capital-one-july-2019-data-breach.md
- cloudflare-july-2-2019-regex-disaster.md
- discord-january-2022-api-cascade-failure.md
- equifax-september-2017-data-breach.md
- facebook-2021-bgp.md
- github-october-21-2018-database-failure.md
- gitlab-2017-database.md
- google-december-2020-auth-outage.md
- lastpass-august-2022-december-2022-breaches.md
- okta-october-2022-security-breach.md
- robinhood-january-2021-gamestop-crisis.md
- slack-january-4-2021-transit-gateway-collapse.md
- twitter-july-2023-rate-limit-crisis.md
- uber-september-2016-data-breach.md
- And more...

**Migrations (8 orphaned files):**
- airbnb-monolith-to-microservices-platform.md
- dropbox-aws-to-datacenter-exodus.md
- instagram-python2-to-python3-language.md
- linkedin-voldemort-to-kafka-storage.md
- microservices-to-serverless-migration.md
- monorepo-migration-google-meta-strategy.md
- twitter-ruby-to-scala-platform.md

**Patterns (60+ orphaned files):**
Many production pattern implementations exist but not in navigation:
- ambassador-pattern-production.md
- api-gateway-kong.md
- backend-for-frontend-pattern-production.md
- batch-processing-spark.md
- circuit-breaker-microservices-production.md
- cqrs-event-sourcing-production.md
- distributed-lock-redis.md
- event-sourcing-pattern-production.md
- saga-pattern-production.md
- service-mesh-istio-lyft.md
- strangler-fig-pattern-production.md
- And 50+ more...

**Performance (17 orphaned files):**
Company-specific performance optimizations:
- airbnb-airflow-batch-processing-optimization.md
- datadog-time-series-optimization.md
- discord-websocket-voice-scaling.md
- github-graphql-query-optimization.md
- instagram-python-memory-optimization.md
- linkedin-cdn-network-optimization.md
- lyft-envoy-service-mesh-latency.md
- netflix-open-connect-cache-warming.md
- pinterest-cassandra-query-optimization.md
- reddit-redis-cache-optimization.md
- square-database-connection-pooling.md
- twitter-timeline-api-optimization.md
- uber-michelangelo-ml-serving-optimization.md
- And more...

**Production (8 orphaned files):**
- cicd-pipeline-optimization.md
- disaster-recovery-procedures.md
- gitops-argocd-deployment-workflow.md
- infrastructure-as-code-workflows.md
- kubernetes-operator-patterns.md
- observability-stack-prometheus-grafana-jaeger.md
- on-call-automation-workflows.md
- sre-workflow-optimization.md

**Scaling (25+ orphaned files):**
Additional company scale journeys:
- auth0-identity-rapid-scale.md
- coinbase-crypto-boom-scale.md
- databricks-analytics-scale.md
- figma-realtime-design-scale.md
- gitlab-devops-scale.md
- grammarly-ai-scale.md
- hashicorp-devops-scale.md
- notion-collaborative-scale.md
- okta-identity-scale.md
- paypal-monolith-to-scale.md
- pinterest-personalization-scale.md
- roblox-gaming-scale.md
- snapchat-ephemeral-scale.md
- snowflake-data-scale.md
- And more...

**Systems (All 135 misnamed files):**
Every system directory has correctly named files that navigation can't find:
- All systems use `production-ops.md` but nav expects `production-operations.md`
- All systems use `storage.md` but nav expects `storage-architecture.md`
- 12 systems use numbered files (01-, 02-, etc.) but nav expects non-numbered names

**Other (2 files):**
- color-comparison.md
- diagrams/INCIDENT_RESPONSE_TEMPLATES.md
- mermaid-style-guide.md
- templates/diagram-templates.md

## Root Causes

### 1. Filename Inconsistency
- **Production Operations:** Navigation uses `production-operations.md` but files are named `production-ops.md`
- **Storage:** Navigation uses `storage-architecture.md` but files are named `storage.md`

### 2. Numbering Convention Mismatch
- Some systems (Coinbase, Datadog, DoorDash, Dropbox, Instacart, Pinterest, Robinhood, Slack, Snap, Square, TikTok, Twitch) use numbered files (`01-`, `02-`, etc.)
- Navigation references them without numbers

### 3. Incomplete Navigation Updates
- Many new files added but not added to navigation
- 366 orphaned files suggest significant content creation without navigation updates

## Recommended Actions

### Priority 1: Fix Broken Links (142 files)
**Impact:** High - Users see 404 errors

**Option A - Rename files to match navigation (Recommended):**
```bash
# For all systems, rename:
production-ops.md → production-operations.md
storage.md → storage-architecture.md

# For numbered systems, create non-numbered symlinks or rename
```

**Option B - Update navigation to match files:**
Update mkdocs.yml to reference correct filenames (production-ops.md, storage.md, etc.)

### Priority 2: Add Orphaned Content to Navigation (366 files)
**Impact:** Medium - Content exists but is undiscoverable

Review and organize these categories:
1. **Debugging guides** (100+ files) - Create comprehensive debugging section
2. **Incidents** (30 files) - Add to incidents section
3. **Patterns** (60+ files) - Expand patterns section
4. **Performance** (17 files) - Add company-specific performance sections
5. **Scaling** (25+ files) - Add to scaling section
6. **Production workflows** (8 files) - Create production/operations section
7. **Capacity, Costs, Migrations, Comparisons** - Add remaining files to respective sections

### Priority 3: Establish Naming Convention
**Impact:** Low - Prevents future issues

Document and enforce:
- Use `production-operations.md` (not `production-ops.md`)
- Use `storage-architecture.md` (not `storage.md`)
- Use numbered prefixes consistently OR don't use them at all
- Update CLAUDE.md with file naming standards

## Quick Wins

1. **Batch rename systems files** (30 systems × 2 files = 60 files):
   - Rename all `production-ops.md` → `production-operations.md`
   - Rename all `storage.md` → `storage-architecture.md`

2. **Add top incidents to navigation** (30 high-profile incidents):
   - These are well-documented, production-ready content

3. **Add production debugging guides** (~50 most critical):
   - High-value content for 3 AM debugging scenarios

## Files Reference

Full lists available in:
- `/home/deepak/DS/site/navigation_mismatch_report.txt` - Complete analysis output
- `/home/deepak/DS/site/analyze_nav_mismatch.py` - Analysis script (reusable)

## Next Steps

1. Decide on naming convention approach (Option A or B above)
2. Execute batch renames or navigation updates
3. Systematically add orphaned files to navigation by category
4. Update CLAUDE.md with file naming standards
5. Create pre-commit hook to validate navigation completeness
6. Re-run analysis to verify: `python3 analyze_nav_mismatch.py`

---

**Analysis Script Location:** `/home/deepak/DS/site/analyze_nav_mismatch.py`
**Run command:** `cd /home/deepak/DS/site && python3 analyze_nav_mismatch.py`