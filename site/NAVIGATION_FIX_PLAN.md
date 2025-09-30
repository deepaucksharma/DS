# Navigation Fix Plan

## Overview
This document provides a systematic plan to fix all navigation mismatches in the MkDocs site.

## Statistics
- **Missing files (broken links):** 142
- **Orphaned files (not in nav):** 366
- **Total issues:** 508

## Phase 1: Fix Broken Links (142 files) - CRITICAL

These cause 404 errors and must be fixed immediately.

### 1.1 Systems Filename Mismatches (60 files)

#### Issue: `production-operations.md` vs `production-ops.md` (30 files)

**Navigation expects:** `systems/[company]/production-operations.md`
**Actual filename:** `systems/[company]/production-ops.md`

**Affected companies (17):**
1. airbnb
2. amazon
3. cloudflare
4. discord
5. github
6. google
7. linkedin
8. meta
9. microsoft
10. netflix
11. openai
12. shopify
13. spotify
14. stripe
15. twitter
16. uber
17. zoom

**Solution Options:**

**Option A - Rename files (recommended):**
```bash
cd /home/deepak/DS/site/docs/systems

# Rename all production-ops.md to production-operations.md
for dir in airbnb amazon cloudflare discord github google linkedin meta microsoft netflix openai shopify spotify stripe twitter uber zoom; do
  if [ -f "$dir/production-ops.md" ]; then
    mv "$dir/production-ops.md" "$dir/production-operations.md"
    echo "Renamed: $dir/production-ops.md → production-operations.md"
  fi
done
```

**Option B - Update navigation:**
Change all instances in mkdocs.yml from:
```yaml
Production Operations: systems/[company]/production-operations.md
```
to:
```yaml
Production Operations: systems/[company]/production-ops.md
```

---

#### Issue: `storage-architecture.md` vs `storage.md` (30 files)

**Navigation expects:** `systems/[company]/storage-architecture.md`
**Actual filename:** `systems/[company]/storage.md`

**Affected companies (17):** Same as above

**Solution Options:**

**Option A - Rename files (recommended):**
```bash
cd /home/deepak/DS/site/docs/systems

# Rename all storage.md to storage-architecture.md
for dir in airbnb amazon cloudflare discord github google linkedin meta microsoft netflix openai shopify spotify stripe twitter uber zoom; do
  if [ -f "$dir/storage.md" ]; then
    mv "$dir/storage.md" "$dir/storage-architecture.md"
    echo "Renamed: $dir/storage.md → storage-architecture.md"
  fi
done
```

**Option B - Update navigation:**
Change all instances in mkdocs.yml from:
```yaml
Storage Architecture: systems/[company]/storage-architecture.md
```
to:
```yaml
Storage Architecture: systems/[company]/storage.md
```

---

### 1.2 Systems with Numbered Files (75 files)

#### Issue: Files have number prefixes but navigation doesn't

**Systems affected (12 systems × 8 files each = 96 entries but 75 broken):**
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

**Pattern:**
- **Actual files:** `01-complete-architecture.md`, `02-request-flow.md`, etc.
- **Navigation expects:** `architecture.md`, `request-flow.md`, etc.

**Solution for each system:**

**Option A - Create symlinks (quick fix):**
```bash
cd /home/deepak/DS/site/docs/systems/coinbase
ln -s 01-complete-architecture.md architecture.md
ln -s 02-request-flow.md request-flow.md
ln -s 03-storage-architecture.md storage-architecture.md
ln -s 04-failure-domains.md failure-domains.md
ln -s 05-scale-evolution.md scale-evolution.md
ln -s 06-cost-breakdown.md cost-breakdown.md
ln -s 07-novel-solutions.md novel-solutions.md
ln -s 08-production-operations.md production-operations.md
```

**Option B - Update navigation to use numbered files:**
Update mkdocs.yml for each system to reference numbered files:
```yaml
- Coinbase:
  - Complete Architecture: systems/coinbase/01-complete-architecture.md
  - Request Flow: systems/coinbase/02-request-flow.md
  - Storage Architecture: systems/coinbase/03-storage-architecture.md
  - Failure Domains: systems/coinbase/04-failure-domains.md
  - Scale Evolution: systems/coinbase/05-scale-evolution.md
  - Cost Breakdown: systems/coinbase/06-cost-breakdown.md
  - Novel Solutions: systems/coinbase/07-novel-solutions.md
  - Production Operations: systems/coinbase/08-production-operations.md
```

**Option C - Rename files to remove numbers:**
```bash
cd /home/deepak/DS/site/docs/systems/coinbase
mv 01-complete-architecture.md architecture.md
mv 02-request-flow.md request-flow.md
mv 03-storage-architecture.md storage-architecture.md
mv 04-failure-domains.md failure-domains.md
mv 05-scale-evolution.md scale-evolution.md
mv 06-cost-breakdown.md cost-breakdown.md
mv 07-novel-solutions.md novel-solutions.md
mv 08-production-operations.md production-operations.md
```

---

### 1.3 Missing Pattern Files (7 files)

These pattern files are referenced in navigation but don't exist:

1. `patterns/ambassador-gateway-airbnb.md`
2. `patterns/api-composition-netflix-bff.md`
3. `patterns/canary-release-github.md`
4. `patterns/database-per-service-uber.md`
5. `patterns/leader-election-kubernetes.md`
6. `patterns/strangler-fig-monzo.md`
7. `patterns/write-through-cache-facebook.md`

**Solution Options:**

**Option A - Create stub files:**
Create placeholder files with TODO content

**Option B - Remove from navigation:**
Remove these entries from mkdocs.yml until files are created

**Option C - Check for alternative names:**
These files might exist with different names (e.g., `leader-election-consul-etcd.md` instead of `leader-election-kubernetes.md`)

---

## Phase 2: Add Orphaned Files to Navigation (366 files)

### 2.1 Debugging Section (100+ files)

Many production debugging guides exist but aren't in navigation.

**High priority debugging guides to add:**
- `api-gateway-throttling-debugging.md`
- `aws-lambda-cold-start-production-debugging.md`
- `cascading-failure-analysis-guide.md`
- `database-connection-pool-exhaustion-guide.md`
- `distributed-transaction-failures.md`
- `elasticsearch-query-performance-debugging-production.md`
- `graphql-n-plus-one-production-debugging.md`
- `kafka-consumer-lag-debugging-production.md`
- `kubernetes-networking-production-debugging.md`
- `memory-leak-investigation-guide.md`
- `microservices-timeout-cascade-production-debugging.md`
- `rate-limiting-throttling-debugging-production.md`
- `service-mesh-debugging-guide.md`
- `zero-downtime-deployment-failures-production-debugging.md`

**Proposed navigation structure:**
```yaml
- Debugging:
  - Performance Issues:
    # ... existing entries ...
  - Data Issues:
    # ... existing entries ...
  - Infrastructure:
    # ... existing entries ...
  - Application Issues:
    # ... existing entries ...
  - Messaging & Queuing:
    # ... existing entries ...
  - Distributed Systems:
    # ... existing entries ...
  - Production Debugging: # NEW SECTION
    - API Gateway Throttling: debugging/api-gateway-throttling-debugging.md
    - Lambda Cold Starts: debugging/aws-lambda-cold-start-production-debugging.md
    - Cascading Failure Analysis: debugging/cascading-failure-analysis-guide.md
    # ... add remaining files ...
```

---

### 2.2 Incidents Section (30+ orphaned files)

Major incidents documented but not in navigation:

**High-profile incidents to add:**
- `aws-s3-february-28-2017-typo-disaster.md`
- `azure-march-2020-covid-surge.md`
- `cloudflare-july-2-2019-regex-disaster.md`
- `discord-january-2022-api-cascade-failure.md`
- `facebook-2021-bgp.md`
- `github-october-21-2018-database-failure.md`
- `gitlab-2017-database.md`
- `google-december-2020-auth-outage.md`
- `robinhood-january-2021-gamestop-crisis.md`
- `slack-january-4-2021-transit-gateway-collapse.md`
- `twitter-july-2023-rate-limit-crisis.md`
- `uber-september-2016-data-breach.md`

**Security breach incidents:**
- `capital-one-july-2019-data-breach.md`
- `equifax-september-2017-data-breach.md`
- `lastpass-august-2022-december-2022-breaches.md`
- `okta-october-2022-security-breach.md`

**Infrastructure incidents:**
- `british-airways-july-2022-it-system-failure.md`
- `dyn-dns-october-2016-ddos-attack.md`
- `nyse-july-2015-trading-halt.md`
- `rogers-july-2022-canadian-network-outage.md`
- `verizon-june-2020-network-backbone-failure.md`

**Proposed additions to navigation:**
```yaml
- Incidents:
  - High Profile:
    # ... existing entries ...
    - AWS S3 2017 Typo: incidents/aws-s3-february-28-2017-typo-disaster.md
    - Facebook BGP 2021: incidents/facebook-2021-bgp.md
    - GitLab Database 2017: incidents/gitlab-2017-database.md
    # ... add more ...
  - Security Breaches: # NEW SECTION
    - Capital One 2019: incidents/capital-one-july-2019-data-breach.md
    - Equifax 2017: incidents/equifax-september-2017-data-breach.md
    - LastPass 2022: incidents/lastpass-august-2022-december-2022-breaches.md
    - Okta 2022: incidents/okta-october-2022-security-breach.md
```

---

### 2.3 Patterns Section (60+ orphaned files)

Many production pattern implementations exist but not in navigation.

**Categories of orphaned patterns:**

**API & Gateway Patterns:**
- `ambassador-pattern-production.md`
- `api-gateway-kong.md`
- `api-gateway-multi-provider-comparison.md`
- `backend-for-frontend-pattern-production.md`

**Reliability Patterns:**
- `bulkhead-isolation-production.md`
- `circuit-breaker-microservices-production.md`
- `circuit-breaker-production.md`
- `graceful-degradation-netflix-vs-uber.md`
- `retry-exponential-backoff-pattern-production.md`

**Data Patterns:**
- `cache-aside-redis-memcached.md`
- `cqrs-event-sourcing-production.md`
- `cqrs-shopify-implementation.md`
- `distributed-lock-redis.md`
- `distributed-locking-redlock-vs-zookeeper.md`
- `event-sourcing-pattern-production.md`
- `event-sourcing-klarna-implementation.md`
- `event-sourcing/financial-systems-implementation.md`
- `outbox-pattern-production.md`
- `two-phase-commit-financial.md`
- `write-ahead-log-postgresql-kafka.md`

**Transaction Patterns:**
- `saga-distributed-transactions-production.md`
- `saga-pattern-production.md`
- `saga-uber-eats-implementation.md`

**Processing Patterns:**
- `batch-processing-spark.md`
- `batch-processing-spring-batch-vs-apache-beam.md`
- `data-pipeline-airbnb.md`
- `data-pipeline-airflow-vs-dagster.md`
- `message-queue-rabbitmq.md`
- `priority-queue-sqs-fifo-vs-rabbitmq.md`
- `stream-processing-uber.md`

**Infrastructure Patterns:**
- `chaos-engineering-netflix.md`
- `distributed-tracing-jaeger.md`
- `event-bus-linkedin.md`
- `graphql-federation-netflix.md`
- `health-check-kubernetes-vs-custom.md`
- `leader-election-consul-etcd.md`
- `multi-tenancy-salesforce.md`
- `serverless-lambda-netflix.md`
- `service-discovery-consul.md`
- `service-mesh-istio-lyft.md`
- `service-registry-consul-vs-eureka.md`
- `sharding-mongodb-cassandra-vitess.md`
- `sharding-strategy-pinterest.md`
- `sidecar-pattern-production.md`
- `strangler-fig-pattern-production.md`

**Deployment Patterns:**
- `blue-green-deployment-kubernetes-vs-aws.md`
- `feature-toggle-launchdarkly-vs-unleash.md`

**Proposed navigation additions:**
```yaml
- Patterns:
  # ... existing sections ...
  - API & Gateway Patterns: # NEW SECTION
    - Ambassador Pattern: patterns/ambassador-pattern-production.md
    - API Gateway Kong: patterns/api-gateway-kong.md
    - Backend for Frontend: patterns/backend-for-frontend-pattern-production.md
  - Reliability Patterns: # NEW SECTION
    - Bulkhead Isolation: patterns/bulkhead-isolation-production.md
    - Circuit Breaker: patterns/circuit-breaker-production.md
    - Graceful Degradation: patterns/graceful-degradation-netflix-vs-uber.md
  # ... add more sections ...
```

---

### 2.4 Performance Section (17 orphaned files)

Company-specific performance optimizations:

- `airbnb-airflow-batch-processing-optimization.md`
- `datadog-time-series-optimization.md`
- `discord-websocket-voice-scaling.md`
- `elasticsearch-search-relevance-tuning.md`
- `github-graphql-query-optimization.md`
- `google-cloud-grpc-performance-tuning.md`
- `instagram-python-memory-optimization.md`
- `linkedin-cdn-network-optimization.md`
- `lyft-envoy-service-mesh-latency.md`
- `netflix-open-connect-cache-warming.md`
- `paypal-transaction-processing-performance.md`
- `pinterest-cassandra-query-optimization.md`
- `reddit-redis-cache-optimization.md`
- `square-database-connection-pooling.md`
- `twitter-timeline-api-optimization.md`
- `uber-michelangelo-ml-serving-optimization.md`
- `uber-schemaless-query-optimization.md`

**Proposed navigation additions:**
```yaml
- Performance:
  # ... existing sections ...
  - Company-Specific: # NEW SECTION
    - Airbnb Airflow: performance/airbnb-airflow-batch-processing-optimization.md
    - Datadog Time Series: performance/datadog-time-series-optimization.md
    - Discord WebSocket: performance/discord-websocket-voice-scaling.md
    - GitHub GraphQL: performance/github-graphql-query-optimization.md
    - Instagram Python: performance/instagram-python-memory-optimization.md
    - LinkedIn CDN: performance/linkedin-cdn-network-optimization.md
    - Lyft Envoy: performance/lyft-envoy-service-mesh-latency.md
    - Netflix Cache: performance/netflix-open-connect-cache-warming.md
    - PayPal Transactions: performance/paypal-transaction-processing-performance.md
    - Pinterest Cassandra: performance/pinterest-cassandra-query-optimization.md
    - Reddit Redis: performance/reddit-redis-cache-optimization.md
    - Square Pooling: performance/square-database-connection-pooling.md
    - Twitter Timeline: performance/twitter-timeline-api-optimization.md
    - Uber ML Serving: performance/uber-michelangelo-ml-serving-optimization.md
    - Uber Schemaless: performance/uber-schemaless-query-optimization.md
```

---

### 2.5 Scaling Section (25+ orphaned files)

Additional company scale journeys:

- `auth0-identity-rapid-scale.md`
- `coinbase-crypto-boom-scale.md`
- `databricks-analytics-scale.md`
- `elastic-search-scale.md`
- `figma-realtime-design-scale.md`
- `gitlab-devops-scale.md`
- `grammarly-ai-scale.md`
- `hashicorp-devops-scale.md`
- `notion-collaborative-scale.md`
- `okta-identity-scale.md`
- `paypal-monolith-to-scale.md`
- `pinterest-personalization-scale.md`
- `pinterest-visual-discovery-scale.md`
- `roblox-gaming-scale.md`
- `segment-customer-data-scale.md`
- `snapchat-ephemeral-scale.md`
- `snapchat-user-growth-scale.md`
- `snowflake-data-scale.md`
- `square-scale-evolution-enhanced.md`
- `uber-scale-evolution.md`

**Proposed navigation additions:**
Simply add these to the existing Scaling section alphabetically.

---

### 2.6 Capacity Section (10 orphaned files)

- `amazon-prime-day-capacity-planning.md`
- `bereal-daily-notification-surge-capacity.md`
- `cloudflare-ddos-mitigation-capacity.md`
- `github-actions-cicd-capacity-model.md`
- `netflix-new-years-eve-streaming-surge.md`
- `openai-gpt4-launch-capacity-planning.md`
- `shopify-black-friday-cyber-monday-capacity.md`
- `threads-app-launch-100m-users-5-days.md`
- `tiktok-live-streaming-capacity.md`
- `twitter-spaces-live-audio-capacity.md`

**Proposed navigation additions:**
Add to Event-Driven Capacity section in navigation.

---

### 2.7 Costs Section (8 orphaned files)

- `airbnb-database-storage-costs.md`
- `cdn-cost-analysis-optimization.md`
- `database-spend-optimization-strategies.md`
- `discord-voice-video-infrastructure-costs.md`
- `kubernetes-cost-reduction-optimization.md`
- `multi-company-cost-optimization-strategies.md`
- `netflix-annual-spend-breakdown.md`
- `spotify-streaming-cdn-costs.md`

**Proposed navigation additions:**
```yaml
- Costs:
  # ... existing company-specific costs ...
  - Optimization Strategies: # NEW SECTION
    - CDN Cost Analysis: costs/cdn-cost-analysis-optimization.md
    - Database Spend: costs/database-spend-optimization-strategies.md
    - Kubernetes Cost Reduction: costs/kubernetes-cost-reduction-optimization.md
    - Multi-Company Strategies: costs/multi-company-cost-optimization-strategies.md
  - Deep Dives: # NEW SECTION
    - Airbnb Database Storage: costs/airbnb-database-storage-costs.md
    - Discord Voice/Video: costs/discord-voice-video-infrastructure-costs.md
    - Netflix Annual Spend: costs/netflix-annual-spend-breakdown.md
    - Spotify Streaming CDN: costs/spotify-streaming-cdn-costs.md
```

---

### 2.8 Comparisons Section (7 orphaned files)

- `graphql-vs-rest-vs-grpc-performance.md`
- `kafka-vs-pulsar-vs-rabbitmq-production.md`
- `kubernetes-vs-nomad-vs-ecs-production.md`
- `postgresql-vs-mysql-vs-cockroachdb-scale.md`
- `rabbitmq-vs-sqs-vs-pubsub.md`
- `terraform-vs-pulumi-vs-cloudformation-iac.md`

**Proposed navigation additions:**
Add to existing comparison categories in navigation.

---

### 2.9 Migrations Section (8 orphaned files)

- `airbnb-monolith-to-microservices-platform.md`
- `dropbox-aws-to-datacenter-exodus.md`
- `instagram-python2-to-python3-language.md`
- `linkedin-voldemort-to-kafka-storage.md`
- `microservices-to-serverless-migration.md`
- `monorepo-migration-google-meta-strategy.md`
- `twitter-ruby-to-scala-platform.md`

**Proposed navigation additions:**
Add to Company Migrations section in navigation.

---

### 2.10 Production Section (8 NEW files - not in current nav)

New production operations content:
- `cicd-pipeline-optimization.md`
- `disaster-recovery-procedures.md`
- `gitops-argocd-deployment-workflow.md`
- `infrastructure-as-code-workflows.md`
- `kubernetes-operator-patterns.md`
- `observability-stack-prometheus-grafana-jaeger.md`
- `on-call-automation-workflows.md`
- `sre-workflow-optimization.md`

**Proposed new section in navigation:**
```yaml
- Production Operations: # NEW TOP-LEVEL SECTION
  - CI/CD: production/cicd-pipeline-optimization.md
  - Disaster Recovery: production/disaster-recovery-procedures.md
  - GitOps: production/gitops-argocd-deployment-workflow.md
  - Infrastructure as Code: production/infrastructure-as-code-workflows.md
  - Kubernetes Operators: production/kubernetes-operator-patterns.md
  - Observability: production/observability-stack-prometheus-grafana-jaeger.md
  - On-Call Automation: production/on-call-automation-workflows.md
  - SRE Workflows: production/sre-workflow-optimization.md
```

---

### 2.11 Miscellaneous Files (4 files)

- `color-comparison.md` - Probably a design/style reference
- `diagrams/INCIDENT_RESPONSE_TEMPLATES.md` - Template file
- `mermaid-style-guide.md` - Style guide
- `templates/diagram-templates.md` - Template file

**Recommendation:** These are likely internal reference files. Consider:
1. Move to a `/internal/` or `/templates/` directory outside docs
2. Or add to a "Reference" section if useful for users

---

## Execution Priority

### Phase 1: Critical Fixes (Week 1)
1. Fix all 142 broken links in systems directories
   - Rename `production-ops.md` → `production-operations.md` (30 files)
   - Rename `storage.md` → `storage-architecture.md` (30 files)
   - Fix numbered files issue (12 systems, 75 files)
2. Fix or remove 7 missing pattern files

### Phase 2: High-Value Content (Week 2)
1. Add 30 high-profile incidents to navigation
2. Add 50 most critical debugging guides
3. Add 20 most important pattern implementations

### Phase 3: Complete Coverage (Week 3-4)
1. Add all remaining debugging guides (50+)
2. Add all remaining patterns (40+)
3. Add performance, scaling, capacity orphaned files
4. Add production operations section

### Phase 4: Polish (Week 4)
1. Organize navigation for better UX
2. Add section descriptions
3. Create navigation index pages
4. Update CLAUDE.md with naming conventions

---

## Validation

After each phase, run:
```bash
cd /home/deepak/DS/site
python3 analyze_nav_mismatch.py
```

Goal: Reduce mismatches to 0.

---

## Automation Opportunity

Create a pre-commit hook or CI check:
```bash
#!/bin/bash
# .git/hooks/pre-commit

cd site
python3 analyze_nav_mismatch.py > /tmp/nav_check.txt

if grep -q "⚠️" /tmp/nav_check.txt; then
  echo "❌ Navigation mismatches detected!"
  cat /tmp/nav_check.txt
  exit 1
fi

echo "✅ Navigation validation passed"
exit 0
```

This ensures new files are added to navigation before committing.