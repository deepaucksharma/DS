-- ============================================
-- Atlas Knowledge Graph - Comprehensive Query Library
-- Neo4j Cypher Queries for exploring the knowledge graph
-- ============================================

-- ============================================
-- CONCEPT EXPLORATION QUERIES
-- ============================================

-- 1. Find shortest learning path between two concepts
MATCH path = shortestPath(
  (start:Concept {name: 'CAP Theorem'})-[:PREREQUISITE_FOR*]->(end:Concept {name: 'Raft Consensus'})
)
RETURN [node in nodes(path) | node.name] AS learning_path,
       reduce(hours = 0, n in nodes(path) | hours + n.learning_hours) AS total_hours,
       length(path) AS steps;

-- 2. Find all prerequisites for a concept (recursive)
MATCH path = (target:Concept {name: 'Distributed Transactions'})<-[:PREREQUISITE_FOR*]-(prereq:Concept)
RETURN prereq.name AS prerequisite,
       prereq.level AS difficulty_level,
       prereq.learning_hours AS hours,
       length(path) AS depth
ORDER BY depth, prereq.learning_hours;

-- 3. Find concepts by difficulty level
MATCH (c:Concept)
WHERE c.level = 'beginner'
RETURN c.name, c.category, c.learning_hours, c.importance
ORDER BY c.importance DESC, c.learning_hours
LIMIT 20;

-- 4. Find most important foundational concepts
MATCH (c:Concept)
WHERE c.importance >= 9
RETURN c.name, c.category, c.level, c.importance, c.real_world_usage
ORDER BY c.importance DESC, c.real_world_usage DESC;

-- 5. Find concepts that enable multiple others
MATCH (c:Concept)-[:ENABLES]->(enabled:Concept)
WITH c, count(enabled) as enables_count
WHERE enables_count > 5
RETURN c.name, c.category, enables_count, c.learning_hours
ORDER BY enables_count DESC;

-- 6. Find related concepts by similarity
MATCH (c1:Concept {name: 'Linearizability'})-[r:RELATED_TO]-(c2:Concept)
RETURN c2.name, c2.category, r.similarity, c2.learning_hours
ORDER BY r.similarity DESC;

-- 7. Find concepts by category with total learning time
MATCH (c:Concept)
WHERE c.category = 'CONSENSUS'
RETURN c.name, c.level, c.learning_hours, c.difficulty
ORDER BY c.difficulty, c.learning_hours;

-- 8. Calculate total learning time for a category
MATCH (c:Concept)
WHERE c.category = 'CONSENSUS'
RETURN c.category AS category,
       count(c) AS total_concepts,
       sum(c.learning_hours) AS total_hours,
       avg(c.difficulty) AS avg_difficulty;

-- 9. Find learning path with time constraint
MATCH path = (start:Concept {name: 'Distributed Systems'})-[:PREREQUISITE_FOR*1..5]->(end:Concept)
WHERE reduce(hours = 0, n in nodes(path) | hours + n.learning_hours) <= 20
RETURN [node in nodes(path) | node.name] AS path,
       reduce(hours = 0, n in nodes(path) | hours + n.learning_hours) AS total_hours
ORDER BY total_hours
LIMIT 10;

-- 10. Find concepts with conflicting approaches
MATCH (c1:Concept)-[r:CONFLICTS_WITH]->(c2:Concept)
RETURN c1.name AS concept_a,
       c2.name AS concept_b,
       r.reason AS conflict_reason
ORDER BY c1.name;

-- ============================================
-- PATTERN DISCOVERY QUERIES
-- ============================================

-- 11. Find patterns that work well together
MATCH (p1:Pattern)-[r:COMPOSES_WITH]->(p2:Pattern)
WHERE r.synergy > 0.8
RETURN p1.name AS pattern_1,
       p2.name AS pattern_2,
       r.synergy AS synergy_score,
       r.example_system AS example
ORDER BY r.synergy DESC;

-- 12. Find pattern evolution paths
MATCH path = (simple:Pattern)-[:EVOLVES_TO*]->(complex:Pattern)
WHERE simple.complexity = 'simple' AND complex.complexity = 'expert'
RETURN [node in nodes(path) | node.name] AS evolution_path,
       reduce(complexity = 0, rel in relationships(path) | complexity + rel.complexity_increase) AS total_complexity_increase;

-- 13. Find patterns by use case
MATCH (p:Pattern)
WHERE p.when_to_use CONTAINS 'high availability'
RETURN p.name, p.complexity, p.learning_hours, p.real_world_usage
ORDER BY p.real_world_usage DESC;

-- 14. Find alternative patterns for same problem
MATCH (p1:Pattern)-[r:ALTERNATIVE_TO]->(p2:Pattern)
RETURN p1.name AS option_1,
       p2.name AS option_2,
       r.trade_off AS key_difference,
       r.use_case AS decision_guide;

-- 15. Find most commonly used patterns
MATCH (p:Pattern)
RETURN p.name, p.category, p.real_world_usage, p.complexity
ORDER BY p.real_world_usage DESC
LIMIT 20;

-- 16. Find patterns that require other patterns
MATCH (p1:Pattern)-[r:REQUIRES]->(p2:Pattern)
WHERE r.necessity > 0.8
RETURN p1.name AS dependent_pattern,
       p2.name AS required_pattern,
       r.necessity AS necessity_score
ORDER BY r.necessity DESC;

-- 17. Find patterns that optimize others
MATCH (optimizer:Pattern)-[r:OPTIMIZES]->(base:Pattern)
RETURN optimizer.name AS optimization_pattern,
       base.name AS base_pattern,
       r.metric AS optimized_metric,
       r.improvement AS typical_improvement;

-- 18. Calculate pattern learning roadmap
MATCH (p:Pattern)
WHERE p.complexity IN ['simple', 'moderate']
WITH p
ORDER BY p.complexity, p.learning_hours
RETURN p.name, p.complexity, p.learning_hours, p.category
LIMIT 15;

-- ============================================
-- COMPANY ARCHITECTURE QUERIES
-- ============================================

-- 19. Find companies using specific pattern
MATCH (c:Company)-[:IMPLEMENTS_PATTERN]->(p:Pattern {name: 'Circuit Breaker'})
RETURN c.name, c.tier, c.scale, c.engineering_team_size
ORDER BY c.scale DESC;

-- 20. Compare architectures of similar companies
MATCH (c1:Company {name: 'Netflix'})-[:IMPLEMENTS_PATTERN]->(p:Pattern)<-[:IMPLEMENTS_PATTERN]-(c2:Company)
WITH c2, count(p) as shared_patterns
WHERE shared_patterns > 5 AND c2.name <> 'Netflix'
RETURN c2.name, shared_patterns, c2.tier, c2.industry
ORDER BY shared_patterns DESC;

-- 21. Find architecture evolution timeline
MATCH (c:Company {name: 'Netflix'})-[:HAS_ARCHITECTURE]->(a:Architecture)
RETURN a.year, a.scale_stage, a.users, a.requests_per_second
ORDER BY a.year;

-- 22. Find technology migration patterns
MATCH (c:Company)-[m:MIGRATED_FROM_TO]->()
RETURN m.from_tech, m.to_tech, count(c) AS companies, avg(m.duration_months) AS avg_duration
GROUP BY m.from_tech, m.to_tech
ORDER BY companies DESC;

-- 23. Find companies by scale stage
MATCH (c:Company)-[:HAS_ARCHITECTURE]->(a:Architecture)
WHERE a.scale_stage = 'hyper_scale'
RETURN c.name, c.industry, a.users, a.requests_per_second
ORDER BY a.users DESC;

-- 24. Find similar architectures by technology stack
MATCH (c1:Company)-[:USES_TECHNOLOGY]->(t:Technology)<-[:USES_TECHNOLOGY]-(c2:Company)
WHERE c1.name = 'Uber'
WITH c2, collect(distinct t.name) AS shared_tech, count(t) AS tech_count
WHERE tech_count > 5
RETURN c2.name, tech_count, shared_tech
ORDER BY tech_count DESC;

-- 25. Find cost evolution for company
MATCH (c:Company {name: 'Netflix'})-[:HAS_ARCHITECTURE]->(a:Architecture)
RETURN a.year, a.users, a.cost_monthly
ORDER BY a.year;

-- 26. Find companies that open-sourced patterns
MATCH (c:Company)-[r:IMPLEMENTS_PATTERN]->(p:Pattern)
WHERE r.open_sourced = true
RETURN c.name, collect(p.name) AS open_sourced_patterns
ORDER BY size(open_sourced_patterns) DESC;

-- ============================================
-- INCIDENT ANALYSIS QUERIES
-- ============================================

-- 27. Find incidents by root cause category
MATCH (i:Incident)-[:CAUSED_BY]->(rc:RootCause)
WHERE rc.category = 'RC-CONFIG'
RETURN i.name, i.company, i.date, i.duration, rc.description
ORDER BY i.date DESC;

-- 28. Find similar incidents across companies
MATCH (i1:Incident {name: 'AWS S3 Outage 2017'})-[:CAUSED_BY]->(rc:RootCause)<-[:CAUSED_BY]-(i2:Incident)
WHERE i2.name <> i1.name
RETURN i2.name, i2.company, i2.date, rc.category AS shared_root_cause;

-- 29. Find incident propagation chains
MATCH path = (i:Incident)-[:PROPAGATED_TO*]->(affected)
WHERE i.name = 'AWS S3 Outage 2017'
RETURN [node in nodes(path) | node.name] AS propagation_chain;

-- 30. Find preventable incidents
MATCH (i:Incident)-[:CAUSED_BY]->(rc:RootCause)-[:PREVENTED_BY]->(p:Prevention)
WHERE p.effectiveness > 8
RETURN i.name, i.company, rc.category, p.strategy, p.effectiveness
ORDER BY p.effectiveness DESC;

-- 31. Calculate incident statistics by company
MATCH (i:Incident)
RETURN i.company AS company,
       count(i) AS total_incidents,
       avg(i.severity) AS avg_severity
GROUP BY i.company
ORDER BY total_incidents DESC;

-- 32. Find root cause frequency
MATCH (i:Incident)-[:CAUSED_BY]->(rc:RootCause)
RETURN rc.category AS root_cause,
       count(i) AS incident_count,
       avg(rc.frequency) AS avg_frequency
GROUP BY rc.category
ORDER BY incident_count DESC;

-- 33. Find lessons learned from similar incidents
MATCH (i1:Incident)-[:SIMILAR_TO]-(i2:Incident)
WHERE i1.name = 'GitHub 24-Hour Outage'
RETURN i2.name, i2.company, i2.lessons_learned;

-- 34. Find most effective prevention strategies
MATCH (rc:RootCause)-[r:PREVENTED_BY]->(p:Prevention)
WITH p, avg(r.effectiveness) AS avg_effectiveness, count(rc) AS applicable_to
WHERE applicable_to > 3
RETURN p.strategy, avg_effectiveness, applicable_to, p.cost
ORDER BY avg_effectiveness DESC, applicable_to DESC;

-- ============================================
-- LEARNING PATH OPTIMIZATION QUERIES
-- ============================================

-- 35. Generate personalized learning path
// Given current knowledge: ['FUND-001', 'FUND-002']
// Target: Master Raft Consensus
MATCH path = shortestPath(
  (known:Concept)-[:PREREQUISITE_FOR*]->(target:Concept {name: 'Raft Consensus'})
)
WHERE known.id IN ['FUND-001', 'FUND-002']
WITH path, reduce(hours = 0, n in nodes(path) | hours + n.learning_hours) AS total_hours
ORDER BY total_hours
LIMIT 1
RETURN [node in nodes(path) | {name: node.name, hours: node.learning_hours}] AS learning_sequence,
       total_hours;

-- 36. Find knowledge gaps for job requirements
// Job requires: Raft, CQRS, Sharding
// Current knowledge: ['FUND-001', 'FUND-002', 'CONS-001']
MATCH (target:Concept)
WHERE target.name IN ['Raft Consensus', 'CQRS', 'Database Sharding']
MATCH (target)<-[:PREREQUISITE_FOR*]-(prereq:Concept)
WHERE NOT prereq.id IN ['FUND-001', 'FUND-002', 'CONS-001']
RETURN prereq.name AS missing_concept,
       prereq.level AS difficulty,
       prereq.learning_hours AS hours
ORDER BY prereq.level, prereq.learning_hours;

-- 37. Estimate time to expertise level
MATCH (c:Concept)
WHERE c.level IN ['advanced', 'expert']
RETURN c.level,
       count(c) AS concept_count,
       sum(c.learning_hours) AS total_hours,
       avg(c.difficulty) AS avg_difficulty;

-- 38. Find parallel learning opportunities
MATCH (c1:Concept), (c2:Concept)
WHERE c1.id <> c2.id
  AND NOT (c1)-[:PREREQUISITE_FOR]-(c2)
  AND NOT (c1)-[:CONFLICTS_WITH]-(c2)
  AND c1.category = 'CONSENSUS'
  AND c2.category = 'CONSENSUS'
RETURN c1.name, c2.name
LIMIT 10;

-- 39. Calculate progress percentage
// Given completed concepts: ['FUND-001', 'FUND-002', 'CONS-001', 'CONS-002']
MATCH (c:Concept)
WITH count(c) AS total_concepts
MATCH (completed:Concept)
WHERE completed.id IN ['FUND-001', 'FUND-002', 'CONS-001', 'CONS-002']
RETURN count(completed) AS completed_count,
       total_concepts,
       (count(completed) * 100.0 / total_concepts) AS completion_percentage;

-- 40. Find optimal 16-week study plan
MATCH (c:Concept)
WHERE c.level IN ['beginner', 'intermediate']
WITH c
ORDER BY c.importance DESC, c.difficulty ASC
LIMIT 60
RETURN collect({
  week: toInteger(sum(c.learning_hours) / 40) + 1,
  concept: c.name,
  hours: c.learning_hours
});

-- ============================================
-- ADVANCED GRAPH ANALYTICS
-- ============================================

-- 41. Find most central concepts (PageRank-style)
MATCH (c:Concept)
OPTIONAL MATCH (c)-[:ENABLES|PREREQUISITE_FOR]->(other:Concept)
WITH c, count(other) AS outgoing
OPTIONAL MATCH (c)<-[:ENABLES|PREREQUISITE_FOR]-(other2:Concept)
WITH c, outgoing, count(other2) AS incoming
RETURN c.name,
       c.category,
       (incoming + outgoing) AS centrality_score
ORDER BY centrality_score DESC
LIMIT 20;

-- 42. Identify concept clusters
MATCH (c:Concept)-[:RELATED_TO]-(related:Concept)
WHERE c.category = related.category
WITH c.category AS cluster, collect(distinct c.name) AS concepts
RETURN cluster, size(concepts) AS cluster_size, concepts
ORDER BY cluster_size DESC;

-- 43. Find longest learning chains
MATCH path = (start:Concept)-[:PREREQUISITE_FOR*]->(end:Concept)
WHERE NOT (end)-[:PREREQUISITE_FOR]->()
RETURN [node in nodes(path) | node.name] AS chain,
       length(path) AS depth,
       reduce(hours = 0, n in nodes(path) | hours + n.learning_hours) AS total_hours
ORDER BY depth DESC
LIMIT 10;

-- 44. Calculate concept importance by connections
MATCH (c:Concept)
OPTIONAL MATCH (c)-[r]-(other)
WITH c, count(r) AS total_connections
RETURN c.name, c.category, total_connections, c.importance
ORDER BY total_connections DESC
LIMIT 30;

-- 45. Find bottleneck concepts (high prerequisite count)
MATCH (c:Concept)<-[:PREREQUISITE_FOR]-(prereq:Concept)
WITH c, count(prereq) AS prereq_count
WHERE prereq_count > 5
RETURN c.name, c.category, prereq_count, c.learning_hours
ORDER BY prereq_count DESC;

-- ============================================
-- CROSS-DOMAIN QUERIES
-- ============================================

-- 46. Connect concepts to real incidents
MATCH (c:Concept)<-[:INVOLVES_CONCEPT]-(i:Incident)
RETURN c.name AS concept,
       collect(i.name) AS related_incidents,
       size(collect(i.name)) AS incident_count
ORDER BY incident_count DESC;

-- 47. Find patterns used by companies that had incidents
MATCH (c:Company)-[:HAD_INCIDENT]->(i:Incident),
      (c)-[:IMPLEMENTS_PATTERN]->(p:Pattern)
RETURN c.name, i.name, collect(p.name) AS patterns_at_time_of_incident;

-- 48. Map concepts to company implementations
MATCH (concept:Concept)-[:IMPLEMENTED_BY]->(company:Company)
RETURN concept.name AS concept,
       collect(company.name) AS companies_using,
       size(collect(company.name)) AS usage_count
ORDER BY usage_count DESC
LIMIT 20;

-- 49. Find technology choices for specific patterns
MATCH (p:Pattern)<-[:IMPLEMENTS_PATTERN]-(c:Company)-[:USES_TECHNOLOGY]->(t:Technology)
WHERE p.name = 'Database Sharding'
RETURN t.name AS technology,
       t.category,
       collect(c.name) AS companies
ORDER BY size(companies) DESC;

-- 50. Comprehensive learning profile
MATCH (c:Concept)
OPTIONAL MATCH (c)-[:PREREQUISITE_FOR]->(enabled:Concept)
OPTIONAL MATCH (c)<-[:PREREQUISITE_FOR]-(required:Concept)
OPTIONAL MATCH (c)-[:RELATED_TO]-(related:Concept)
RETURN c.name,
       c.category,
       c.level,
       c.learning_hours,
       count(distinct enabled) AS enables_count,
       count(distinct required) AS prereq_count,
       count(distinct related) AS related_count
ORDER BY (enables_count + prereq_count + related_count) DESC
LIMIT 30;

-- ============================================
-- DATA QUALITY QUERIES
-- ============================================

-- 51. Find orphaned concepts (no connections)
MATCH (c:Concept)
WHERE NOT (c)-[]-()
RETURN c.name, c.category, c.level;

-- 52. Find circular dependencies
MATCH path = (c:Concept)-[:PREREQUISITE_FOR*2..10]->(c)
RETURN [node in nodes(path) | node.name] AS circular_chain;

-- 53. Validate prerequisite chains (no difficulty inversions)
MATCH (easy:Concept)-[:PREREQUISITE_FOR]->(hard:Concept)
WHERE easy.difficulty > hard.difficulty
RETURN easy.name, easy.difficulty, hard.name, hard.difficulty;

-- 54. Find concepts missing Atlas diagrams
MATCH (c:Concept)
WHERE c.atlas_diagrams = [] OR c.atlas_diagrams IS NULL
RETURN c.name, c.category, c.importance
ORDER BY c.importance DESC;

-- 55. Count concepts by category and level
MATCH (c:Concept)
RETURN c.category AS category,
       c.level AS level,
       count(c) AS concept_count,
       sum(c.learning_hours) AS total_hours
ORDER BY category, level;

-- ============================================
-- EXPORT QUERIES
-- ============================================

-- 56. Export all concepts with details (JSON format)
MATCH (c:Concept)
RETURN {
  id: c.id,
  name: c.name,
  category: c.category,
  level: c.level,
  learning_hours: c.learning_hours,
  difficulty: c.difficulty,
  importance: c.importance
} AS concept
ORDER BY c.category, c.difficulty;

-- 57. Export learning path as graph
MATCH path = (start:Concept {name: 'Distributed Systems'})-[:PREREQUISITE_FOR*1..5]->(end:Concept)
RETURN path;

-- 58. Export pattern network
MATCH (p1:Pattern)-[r]-(p2:Pattern)
RETURN p1.name AS source,
       type(r) AS relationship,
       p2.name AS target,
       r AS properties;

-- 59. Export company architecture evolution
MATCH (c:Company)-[:HAS_ARCHITECTURE]->(a:Architecture)-[e:EVOLVED_TO]->(next:Architecture)
RETURN c.name AS company,
       a.year AS from_year,
       next.year AS to_year,
       e.trigger AS evolution_trigger,
       e.scale_multiplier AS growth;

-- 60. Export incident causality graph
MATCH (i:Incident)-[:CAUSED_BY]->(rc:RootCause)-[:PREVENTED_BY]->(p:Prevention)
RETURN i.name AS incident,
       rc.category AS root_cause,
       p.strategy AS prevention,
       p.effectiveness AS effectiveness
ORDER BY i.date DESC;

-- ============================================
-- END OF QUERY LIBRARY
-- Total: 60 production-ready queries
-- ============================================