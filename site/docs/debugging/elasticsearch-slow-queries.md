# Elasticsearch Slow Queries - Optimization and Performance Guide

## Overview

Comprehensive strategies for identifying and optimizing slow Elasticsearch queries. Based on production experiences from Netflix's search infrastructure, GitHub's code search, and Shopify's product search optimization.

## Debugging Commands

### Query Performance Analysis
```bash
# Enable slow query logging
curl -X PUT "localhost:9200/_cluster/settings" -H 'Content-Type: application/json' -d'
{
  "persistent": {
    "index.search.slowlog.threshold.query.warn": "2s",
    "index.search.slowlog.threshold.query.info": "1s",
    "index.search.slowlog.threshold.fetch.warn": "1s"
  }
}'

# Check slow queries in logs
tail -f /var/log/elasticsearch/elasticsearch_index_search_slowlog.log

# Get cluster stats
curl -X GET "localhost:9200/_cluster/stats?pretty"

# Check query performance
curl -X GET "localhost:9200/my-index/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "profile": true,
  "query": {
    "match": {
      "title": "search term"
    }
  }
}'
```

## Production Examples

### Netflix Search Optimization
```python
# Netflix-style search optimization with query profiling
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import time
import json

class NetflixSearchOptimizer:
    def __init__(self, es_client):
        self.es = es_client
        self.slow_query_threshold = 1.0  # 1 second

    def optimize_content_search(self, query_text, user_preferences=None):
        """Optimized content search with multiple strategies"""

        # Strategy 1: Try cached/simple query first
        start_time = time.time()

        simple_query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query_text,
                                "fields": ["title^3", "description", "actors", "directors"],
                                "type": "best_fields",
                                "fuzziness": "AUTO"
                            }
                        }
                    ],
                    "filter": self.build_filters(user_preferences)
                }
            },
            "size": 20,
            "_source": ["id", "title", "thumbnail", "rating", "year"],
            "sort": [{"popularity_score": {"order": "desc"}}]
        }

        try:
            response = self.es.search(
                index="content-v2",
                body=simple_query,
                timeout="500ms"  # Fast timeout for simple query
            )

            query_time = time.time() - start_time

            if query_time < self.slow_query_threshold:
                return self.format_search_results(response)

        except Exception as e:
            print(f"Simple query failed: {e}")

        # Strategy 2: Fallback to comprehensive search
        return self.comprehensive_search(query_text, user_preferences)

    def comprehensive_search(self, query_text, user_preferences):
        """Comprehensive search with advanced features"""

        # Use function_score for personalization
        comprehensive_query = {
            "query": {
                "function_score": {
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "multi_match": {
                                        "query": query_text,
                                        "fields": [
                                            "title^3",
                                            "description^2",
                                            "actors.name^2",
                                            "directors.name^2",
                                            "genres^1.5",
                                            "keywords"
                                        ],
                                        "type": "cross_fields",
                                        "operator": "and"
                                    }
                                }
                            ],
                            "should": [
                                # Boost exact title matches
                                {
                                    "match_phrase": {
                                        "title": {
                                            "query": query_text,
                                            "boost": 5
                                        }
                                    }
                                },
                                # Boost recent content
                                {
                                    "range": {
                                        "release_date": {
                                            "gte": "2020-01-01",
                                            "boost": 2
                                        }
                                    }
                                }
                            ],
                            "filter": self.build_filters(user_preferences)
                        }
                    },
                    "functions": [
                        # Personalization boost
                        {
                            "filter": {"terms": {"genres": user_preferences.get("preferred_genres", [])}},
                            "weight": 1.5
                        },
                        # Popularity boost
                        {
                            "field_value_factor": {
                                "field": "popularity_score",
                                "factor": 1.2,
                                "modifier": "log1p",
                                "missing": 0
                            }
                        },
                        # Recency boost
                        {
                            "gauss": {
                                "release_date": {
                                    "origin": "now",
                                    "scale": "365d",
                                    "decay": 0.8
                                }
                            }
                        }
                    ],
                    "score_mode": "sum",
                    "boost_mode": "multiply"
                }
            },
            "size": 50,
            "timeout": "2s",
            "_source": {
                "includes": ["id", "title", "description", "thumbnail", "rating", "year", "genres"]
            },
            "highlight": {
                "fields": {
                    "title": {"number_of_fragments": 0},
                    "description": {"fragment_size": 100, "number_of_fragments": 2}
                }
            },
            "aggregations": {
                "genres": {
                    "terms": {"field": "genres.keyword", "size": 10}
                },
                "release_years": {
                    "date_histogram": {
                        "field": "release_date",
                        "calendar_interval": "year",
                        "format": "yyyy"
                    }
                }
            }
        }

        response = self.es.search(
            index="content-v2",
            body=comprehensive_query,
            request_timeout=5
        )

        return self.format_search_results(response)

    def build_filters(self, user_preferences):
        """Build filters based on user preferences"""
        filters = []

        if user_preferences:
            # Content rating filter
            if user_preferences.get("max_rating"):
                filters.append({
                    "range": {
                        "content_rating_score": {
                            "lte": user_preferences["max_rating"]
                        }
                    }
                })

            # Language filter
            if user_preferences.get("languages"):
                filters.append({
                    "terms": {
                        "languages.keyword": user_preferences["languages"]
                    }
                })

            # Exclude watched content
            if user_preferences.get("exclude_watched"):
                filters.append({
                    "bool": {
                        "must_not": {
                            "terms": {
                                "id": user_preferences["watched_content_ids"]
                            }
                        }
                    }
                })

        return filters

    def analyze_slow_queries(self, index_name="content-v2"):
        """Analyze slow queries and suggest optimizations"""

        # Get index stats
        stats = self.es.indices.stats(index=index_name)
        search_stats = stats["indices"][index_name]["total"]["search"]

        analysis = {
            "total_queries": search_stats["query_total"],
            "query_time_ms": search_stats["query_time_in_millis"],
            "avg_query_time": search_stats["query_time_in_millis"] / max(search_stats["query_total"], 1),
            "suggestions": []
        }

        # Check for common performance issues
        if analysis["avg_query_time"] > 500:
            analysis["suggestions"].append("Consider adding more specific filters")
            analysis["suggestions"].append("Review field mappings for search optimization")

        # Get field mappings for analysis
        mappings = self.es.indices.get_mapping(index=index_name)
        field_analysis = self.analyze_field_usage(mappings)
        analysis["field_analysis"] = field_analysis

        return analysis

    def optimize_index_settings(self, index_name):
        """Optimize index settings for search performance"""

        optimized_settings = {
            "settings": {
                "refresh_interval": "30s",  # Reduce refresh frequency
                "number_of_replicas": 1,
                "index": {
                    "search": {
                        "idle": {
                            "after": "30s"  # Mark shards idle faster
                        }
                    },
                    "translog": {
                        "flush_threshold_size": "1gb",
                        "sync_interval": "30s"
                    }
                }
            }
        }

        # Apply optimizations
        self.es.indices.put_settings(
            index=index_name,
            body=optimized_settings
        )

        return optimized_settings

    def create_optimized_mapping(self):
        """Create optimized field mappings for search"""

        mapping = {
            "mappings": {
                "properties": {
                    "title": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {
                            "keyword": {"type": "keyword"},
                            "suggest": {"type": "completion"}
                        }
                    },
                    "description": {
                        "type": "text",
                        "analyzer": "standard"
                    },
                    "actors": {
                        "type": "nested",
                        "properties": {
                            "name": {
                                "type": "text",
                                "fields": {"keyword": {"type": "keyword"}}
                            },
                            "popularity": {"type": "float"}
                        }
                    },
                    "genres": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}}
                    },
                    "release_date": {"type": "date"},
                    "popularity_score": {"type": "float"},
                    "rating": {"type": "float"},
                    "year": {"type": "integer"},
                    "content_rating": {"type": "keyword"},
                    "languages": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}}
                    }
                }
            },
            "settings": {
                "number_of_shards": 3,
                "number_of_replicas": 1,
                "analysis": {
                    "analyzer": {
                        "content_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "stop", "snowball"]
                        }
                    }
                }
            }
        }

        return mapping
```

### GitHub Code Search Optimization
```go
// GitHub-style code search with query optimization
package main

import (
    "context"
    "encoding/json"
    "fmt"
    "time"

    "github.com/elastic/go-elasticsearch/v8"
    "github.com/elastic/go-elasticsearch/v8/esapi"
)

type GitHubCodeSearchOptimizer struct {
    client *elasticsearch.Client
    cfg    SearchConfig
}

type SearchConfig struct {
    DefaultTimeout    time.Duration
    SlowQueryThreshold time.Duration
    MaxResultSize     int
}

type CodeSearchQuery struct {
    Query        string   `json:"query"`
    Language     string   `json:"language,omitempty"`
    Repository   string   `json:"repository,omitempty"`
    User         string   `json:"user,omitempty"`
    Organization string   `json:"organization,omitempty"`
    Filename     string   `json:"filename,omitempty"`
    Extension    string   `json:"extension,omitempty"`
    Size         int      `json:"size,omitempty"`
}

func (g *GitHubCodeSearchOptimizer) OptimizedCodeSearch(ctx context.Context, searchQuery CodeSearchQuery) (*SearchResponse, error) {
    // Build optimized Elasticsearch query
    esQuery := g.buildOptimizedQuery(searchQuery)

    // Execute with profiling
    startTime := time.Now()
    response, err := g.executeSearchWithProfiling(ctx, esQuery)
    queryDuration := time.Since(startTime)

    // Log slow queries for analysis
    if queryDuration > g.cfg.SlowQueryThreshold {
        g.logSlowQuery(searchQuery, esQuery, queryDuration)
    }

    if err != nil {
        return nil, fmt.Errorf("search execution failed: %w", err)
    }

    return g.parseSearchResponse(response), nil
}

func (g *GitHubCodeSearchOptimizer) buildOptimizedQuery(searchQuery CodeSearchQuery) map[string]interface{} {
    // Start with basic structure
    query := map[string]interface{}{
        "size": g.getOptimalSize(searchQuery.Size),
        "timeout": "2s",
        "_source": []string{
            "repository.full_name",
            "path",
            "content",
            "language",
            "sha",
            "size",
            "url"
        },
        "query": map[string]interface{}{
            "bool": map[string]interface{}{
                "must":   []interface{}{},
                "filter": []interface{}{},
                "should": []interface{}{},
            },
        },
        "highlight": map[string]interface{}{
            "fields": map[string]interface{}{
                "content": map[string]interface{}{
                    "fragment_size":       200,
                    "number_of_fragments": 3,
                    "pre_tags":           []string{"<mark>"},
                    "post_tags":          []string{"</mark>"},
                },
            },
        },
    }

    boolQuery := query["query"].(map[string]interface{})["bool"].(map[string]interface{})

    // Add content search
    if searchQuery.Query != "" {
        // Use different strategies based on query length and type
        if len(searchQuery.Query) > 50 {
            // Long queries: use match with minimum_should_match
            boolQuery["must"] = append(boolQuery["must"].([]interface{}), map[string]interface{}{
                "match": map[string]interface{}{
                    "content": map[string]interface{}{
                        "query":                searchQuery.Query,
                        "minimum_should_match": "75%",
                        "operator":            "and",
                    },
                },
            })
        } else {
            // Short queries: use multi_match with boosting
            boolQuery["must"] = append(boolQuery["must"].([]interface{}), map[string]interface{}{
                "multi_match": map[string]interface{}{
                    "query": searchQuery.Query,
                    "fields": []string{
                        "content^1",
                        "path^3",
                        "repository.name^2",
                    },
                    "type":      "best_fields",
                    "fuzziness": "AUTO",
                },
            })
        }

        // Add phrase boost for exact matches
        boolQuery["should"] = append(boolQuery["should"].([]interface{}), map[string]interface{}{
            "match_phrase": map[string]interface{}{
                "content": map[string]interface{}{
                    "query": searchQuery.Query,
                    "boost": 3,
                },
            },
        })
    }

    // Add filters (these are cached and don't affect scoring)
    filters := boolQuery["filter"].([]interface{})

    if searchQuery.Language != "" {
        filters = append(filters, map[string]interface{}{
            "term": map[string]interface{}{
                "language.keyword": searchQuery.Language,
            },
        })
    }

    if searchQuery.Repository != "" {
        filters = append(filters, map[string]interface{}{
            "term": map[string]interface{}{
                "repository.full_name.keyword": searchQuery.Repository,
            },
        })
    }

    if searchQuery.User != "" {
        filters = append(filters, map[string]interface{}{
            "term": map[string]interface{}{
                "repository.owner.login.keyword": searchQuery.User,
            },
        })
    }

    if searchQuery.Filename != "" {
        filters = append(filters, map[string]interface{}{
            "wildcard": map[string]interface{}{
                "path.keyword": fmt.Sprintf("*%s*", searchQuery.Filename),
            },
        })
    }

    if searchQuery.Extension != "" {
        filters = append(filters, map[string]interface{}{
            "term": map[string]interface{}{
                "extension.keyword": searchQuery.Extension,
            },
        })
    }

    boolQuery["filter"] = filters

    // Add aggregations for faceted search
    query["aggregations"] = map[string]interface{}{
        "languages": map[string]interface{}{
            "terms": map[string]interface{}{
                "field": "language.keyword",
                "size":  10,
            },
        },
        "repositories": map[string]interface{}{
            "terms": map[string]interface{}{
                "field": "repository.full_name.keyword",
                "size":  10,
            },
        },
        "file_extensions": map[string]interface{}{
            "terms": map[string]interface{}{
                "field": "extension.keyword",
                "size":  15,
            },
        },
    }

    // Add sorting
    query["sort"] = []interface{}{
        map[string]interface{}{
            "_score": map[string]interface{}{
                "order": "desc",
            },
        },
        map[string]interface{}{
            "repository.stargazers_count": map[string]interface{}{
                "order": "desc",
            },
        },
    }

    return query
}

func (g *GitHubCodeSearchOptimizer) executeSearchWithProfiling(ctx context.Context, query map[string]interface{}) (map[string]interface{}, error) {
    // Add profiling for performance analysis
    query["profile"] = true

    // Convert to JSON
    queryJSON, err := json.Marshal(query)
    if err != nil {
        return nil, fmt.Errorf("failed to marshal query: %w", err)
    }

    // Execute search
    req := esapi.SearchRequest{
        Index: []string{"code-search-v2"},
        Body:  strings.NewReader(string(queryJSON)),
    }

    res, err := req.Do(ctx, g.client)
    if err != nil {
        return nil, fmt.Errorf("search request failed: %w", err)
    }
    defer res.Body.Close()

    if res.IsError() {
        return nil, fmt.Errorf("search returned error: %s", res.Status())
    }

    // Parse response
    var response map[string]interface{}
    if err := json.NewDecoder(res.Body).Decode(&response); err != nil {
        return nil, fmt.Errorf("failed to decode response: %w", err)
    }

    return response, nil
}

func (g *GitHubCodeSearchOptimizer) logSlowQuery(searchQuery CodeSearchQuery, esQuery map[string]interface{}, duration time.Duration) {
    slowQueryLog := map[string]interface{}{
        "timestamp":       time.Now(),
        "duration_ms":     duration.Milliseconds(),
        "search_query":    searchQuery,
        "elasticsearch_query": esQuery,
        "type":           "slow_code_search",
    }

    // Log to structured logging system
    logJSON, _ := json.Marshal(slowQueryLog)
    fmt.Printf("SLOW_QUERY: %s\n", logJSON)

    // Send to monitoring system
    g.sendToMonitoring(slowQueryLog)
}

func (g *GitHubCodeSearchOptimizer) AnalyzeQueryPerformance(ctx context.Context) (*PerformanceAnalysis, error) {
    // Get search slow log
    slowLogQuery := map[string]interface{}{
        "query": map[string]interface{}{
            "range": map[string]interface{}{
                "@timestamp": map[string]interface{}{
                    "gte": "now-1h",
                },
            },
        },
        "size": 100,
        "sort": []interface{}{
            map[string]interface{}{
                "took": map[string]interface{}{
                    "order": "desc",
                },
            },
        },
    }

    // Execute analysis query
    response, err := g.executeAnalysisQuery(ctx, slowLogQuery)
    if err != nil {
        return nil, err
    }

    analysis := &PerformanceAnalysis{
        SlowQueries:        g.extractSlowQueries(response),
        CommonPatterns:     g.identifyCommonPatterns(response),
        OptimizationHints: g.generateOptimizationHints(response),
    }

    return analysis, nil
}

type PerformanceAnalysis struct {
    SlowQueries        []SlowQuery        `json:"slow_queries"`
    CommonPatterns     []Pattern          `json:"common_patterns"`
    OptimizationHints  []OptimizationHint `json:"optimization_hints"`
}

type SlowQuery struct {
    Query      string        `json:"query"`
    Duration   time.Duration `json:"duration"`
    Timestamp  time.Time     `json:"timestamp"`
    UserQuery  string        `json:"user_query"`
}

func (g *GitHubCodeSearchOptimizer) generateOptimizationHints(response map[string]interface{}) []OptimizationHint {
    hints := []OptimizationHint{}

    // Analyze query patterns
    hits := response["hits"].(map[string]interface{})["hits"].([]interface{})

    for _, hit := range hits {
        hitMap := hit.(map[string]interface{})
        source := hitMap["_source"].(map[string]interface{})

        // Check for common performance issues
        if query, ok := source["query"].(string); ok {
            if strings.Contains(query, "wildcard") {
                hints = append(hints, OptimizationHint{
                    Type:        "wildcard_optimization",
                    Description: "Consider using prefix queries instead of wildcards for better performance",
                    Query:       query,
                })
            }

            if strings.Contains(query, "regexp") {
                hints = append(hints, OptimizationHint{
                    Type:        "regexp_optimization",
                    Description: "Regular expressions are expensive - consider term or prefix queries",
                    Query:       query,
                })
            }
        }
    }

    return hints
}

type OptimizationHint struct {
    Type        string `json:"type"`
    Description string `json:"description"`
    Query       string `json:"query"`
}
```

## Success Metrics

- **Query Response Time**: P95 < 500ms, P99 < 2s
- **Search Accuracy**: > 85% relevant results in top 10
- **Index Optimization**: > 70% reduction in index size after optimization
- **Cache Hit Rate**: > 80% for frequent search patterns
- **Slow Query Rate**: < 1% of total queries

## The 3 AM Test

**Scenario**: Your Elasticsearch cluster is struggling with search queries taking 10+ seconds, users are complaining about timeouts, and the cluster CPU is at 90%+ utilization.

**This guide provides**:
1. **Query profiling**: Tools to identify expensive query operations and bottlenecks
2. **Index optimization**: Strategies to optimize mappings, settings, and shard allocation
3. **Query rewriting**: Techniques to transform slow queries into performant ones
4. **Caching strategies**: Implementation of multi-level caching for frequent searches
5. **Monitoring setup**: Automated detection and alerting for search performance degradation

**Expected outcome**: Slow queries identified within 15 minutes, immediate optimizations applied within 1 hour, comprehensive performance improvements deployed within 4 hours.