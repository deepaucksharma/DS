# Production Data Verification Framework
## Ensuring Every Metric is Real and Current

### 🎯 The Verification Mandate

**Every production metric must be:**
- ✅ Sourced from official engineering content (blog, talk, documentation)
- ✅ Dated within last 24 months (exceptions require justification)
- ✅ Cross-referenced when possible
- ✅ Attributed with URL and access date
- ✅ Contextualized (peak vs average, region, conditions)

---

## 📊 Data Categories and Standards

### 1. Performance Metrics

#### Latency
```yaml
standard:
  required:
    - percentile (p50, p95, p99, p99.9)
    - measurement point (client, server, database)
    - time period (peak, average, off-peak)

  example:
    metric: "API latency"
    value: "p99: 50ms"
    context: "Peak traffic (Black Friday 2023)"
    source: "https://stripe.com/blog/black-friday-2023"
    accessed: "2024-01-15"

  red_flags:
    - Round numbers without percentiles ("~100ms")
    - No context provided
    - Older than 24 months
```

#### Throughput
```yaml
standard:
  required:
    - unit (requests/sec, messages/day, transactions/hour)
    - scale qualifier (per node, per cluster, total)
    - conditions (normal, peak, degraded)

  example:
    metric: "Kafka throughput"
    value: "7 trillion messages/day"
    context: "LinkedIn production cluster (2024)"
    source: "Kafka Summit 2024 keynote"
    accessed: "2024-02-01"
```

### 2. Scale Metrics

#### User Scale
```yaml
standard:
  required:
    - active definition (MAU, DAU, concurrent)
    - geographic distribution
    - growth trajectory

  example:
    metric: "Discord concurrent users"
    value: "15 million"
    context: "Peak concurrent voice users"
    source: "Discord Engineering Blog Q1 2024"
    accessed: "2024-03-15"
```

#### Infrastructure Scale
```yaml
standard:
  required:
    - instance types (specific: r5.24xlarge)
    - quantities (exact or range)
    - cloud provider

  example:
    metric: "Netflix EC2 instances"
    value: "100,000+"
    context: "Across all regions, 60% are g4dn.* for encoding"
    source: "AWS re:Invent 2023 - Netflix presentation"
    accessed: "2023-12-01"
```

### 3. Cost Metrics

```yaml
standard:
  required:
    - currency and period ($/month, €/year)
    - breakdown if available
    - date of pricing

  example:
    metric: "Uber infrastructure cost"
    value: "$20M/month"
    context: "AWS services only, excluding Uber-owned DCs"
    source: "Uber Investor Day 2024"
    accessed: "2024-02-20"
```

### 4. Incident Metrics

```yaml
standard:
  required:
    - date and duration
    - impact (users affected, revenue lost)
    - root cause
    - recovery time

  example:
    incident: "AWS S3 Outage"
    date: "2017-02-28"
    duration: "4 hours"
    impact: "~$150M in losses across affected companies"
    source: "AWS Service Health Dashboard + media reports"
    accessed: "2024-01-10"
```

---

## 🔍 Verification Process

### Step 1: Source Discovery

```python
# Priority sources (check weekly)
tier_1_sources = [
    "https://netflixtechblog.com",
    "https://eng.uber.com",
    "https://stripe.com/blog/engineering",
    "https://discord.com/blog/engineering",
    "https://engineering.fb.com"
]

# Conference sources (check after events)
conferences = [
    "AWS re:Invent",
    "QCon (London/SF/NY)",
    "KubeCon",
    "Kafka Summit",
    "DockerCon"
]

# Documentation sources (check quarterly)
official_docs = [
    "AWS Architecture Center",
    "Google Cloud Architecture Framework",
    "Azure Architecture Center"
]
```

### Step 2: Data Extraction

```yaml
extraction_template:
  source_metadata:
    url: "Full URL"
    title: "Article/talk title"
    author: "Author name and role"
    company: "Company"
    date_published: "YYYY-MM-DD"
    date_accessed: "YYYY-MM-DD"

  metrics_extracted:
    - metric_name: "Requests per second"
      value: "100,000"
      context: "Peak during Super Bowl"
      confidence: "high"  # high/medium/low

  verification_notes:
    - "Cross-referenced with conference talk"
    - "Confirmed by job posting mentioning scale"
    - "Consistent with previous year's data"
```

### Step 3: Cross-Reference Validation

```yaml
validation_matrix:
  netflix_scale:
    source_1:
      value: "260M subscribers"
      source: "Netflix Q2 2024 earnings"
      date: "2024-07-15"

    source_2:
      value: "~260M users"
      source: "AWS re:Invent 2024"
      date: "2024-12-01"

    status: "✅ VALIDATED - Multiple sources agree"
```

### Step 4: Staleness Detection

```python
def check_data_freshness(metric_date):
    """Flag data older than 24 months"""
    months_old = (datetime.now() - metric_date).days / 30

    if months_old > 24:
        return "🔴 STALE - Needs update"
    elif months_old > 18:
        return "🟡 AGING - Consider updating"
    else:
        return "🟢 FRESH - Current data"
```

---

## 📋 Verification Checklist

For each metric in a diagram:

### Mandatory Checks
- [ ] Source URL provided and accessible
- [ ] Publication date within 24 months
- [ ] Context explains measurement conditions
- [ ] Units are specific and clear
- [ ] Instance types/configurations are specific

### Quality Checks
- [ ] Cross-referenced with another source
- [ ] Consistent with known industry standards
- [ ] Author/speaker has credibility
- [ ] Company has officially shared this data
- [ ] No obvious errors or typos

### Red Flags to Investigate
- [ ] Suspiciously round numbers
- [ ] Claims that seem too good/bad
- [ ] Inconsistent with other sources
- [ ] From unofficial or personal blogs
- [ ] No date on source material

---

## 🚨 Dispute Resolution

When sources conflict:

### Priority Order
1. **Official earnings/investor reports** (highest trust)
2. **Engineering blog posts** (company sanctioned)
3. **Conference presentations** (speaker credibility matters)
4. **Documentation** (may be outdated)
5. **Media reports** (often inaccurate on technical details)

### Conflict Resolution Process
```yaml
example_conflict:
  metric: "Uber daily rides"

  source_a:
    value: "25 million"
    source: "Uber Engineering Blog"
    date: "2024-01"

  source_b:
    value: "23 million"
    source: "TechCrunch article"
    date: "2024-02"

  resolution:
    chosen: "25 million"
    reason: "Engineering blog is primary source"
    note: "Media often reports outdated numbers"
```

---

## 📊 Tracking Verification Status

```markdown
| Diagram | Metrics | Verified | Stale | Updated | Reviewer |
|---------|---------|----------|-------|---------|----------|
| Netflix Architecture | 12 | 12 | 0 | 2024-01 | @john |
| Uber Geo-Index | 8 | 6 | 2 | 2024-02 | @sarah |
| Discord WebSocket | 15 | 15 | 0 | 2024-03 | @mike |
```

---

## 🔄 Maintenance Schedule

### Weekly
- Check tier-1 engineering blogs
- Update any metrics from new posts

### Monthly
- Review conference content
- Update case studies with new data

### Quarterly
- Full staleness review
- Update all metrics >18 months old
- Deprecate diagrams with unverifiable data

---

## 📝 Documentation Template

Every diagram must include:

```yaml
# Production Data Sources
last_verified: 2024-03-15
reviewer: @username

metrics:
  throughput:
    value: "100K requests/sec"
    context: "Peak traffic, 99th percentile"
    source: "https://engineering.example.com/scaling-2024"
    accessed: 2024-03-10
    confidence: high

  latency:
    value: "p99: 50ms"
    context: "API gateway, US-East region"
    source: "Example Tech Talk - QCon 2024"
    accessed: 2024-03-12
    confidence: high

  cost:
    value: "$50K/month"
    context: "AWS infrastructure only"
    source: "Company blog post on cost optimization"
    accessed: 2024-03-01
    confidence: medium
    note: "Estimated from instance types mentioned"
```

---

## ✅ Verification Success Criteria

A diagram's data is considered verified when:
- 100% of metrics have sources
- 100% of sources are dated
- 90%+ of sources are <24 months old
- 80%+ of critical metrics are cross-referenced
- 0% placeholder or example data

**Remember: Bad data is worse than no data. When in doubt, leave it out.**