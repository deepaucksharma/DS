# Getting Started with Atlas Knowledge Graph

## Quick Start (5 Minutes)

### Prerequisites
- Python 3.8+
- Neo4j 5.x (optional, for graph database)
- pip

### Installation

```bash
# Navigate to knowledge graph directory
cd atlas-study-plan/knowledge-graph

# Install Python dependencies
pip install networkx pyyaml neo4j graphql-core

# Optional: Start Neo4j with Docker
docker run -d \
  --name atlas-neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/atlas123 \
  neo4j:latest
```

### Option 1: NetworkX (In-Memory, Python)

```python
# Load sample concepts
import json
import networkx as nx

# Load data
with open('data/sample-concepts.json', 'r') as f:
    data = json.load(f)

# Create graph
G = nx.DiGraph()

# Add concept nodes
for concept in data['concepts']:
    G.add_node(
        concept['id'],
        name=concept['name'],
        learning_hours=concept['learning_hours'],
        difficulty=concept['difficulty']
    )

# Add prerequisite relationships
for rel in data['relationships']['prerequisite_for']:
    G.add_edge(rel['from'], rel['to'], type='prerequisite', strength=rel['strength'])

# Find shortest learning path
import networkx as nx
try:
    path = nx.shortest_path(G, 'FUND-001', 'CNSP-005')
    print("Learning path:", [G.nodes[n]['name'] for n in path])

    # Calculate total hours
    hours = sum(G.nodes[n]['learning_hours'] for n in path)
    print(f"Total hours: {hours}")
except nx.NetworkXNoPath:
    print("No path found")
```

### Option 2: Neo4j (Graph Database)

```bash
# Load schema and data
python scripts/load_to_neo4j.py \
  --uri bolt://localhost:7687 \
  --user neo4j \
  --password atlas123

# Or use Cypher directly
cypher-shell -u neo4j -p atlas123 < queries/load-sample-data.cypher
```

Then query via browser at http://localhost:7474:

```cypher
// Find shortest learning path
MATCH path = shortestPath(
  (start:Concept {name: 'Distributed Systems'})-[:PREREQUISITE_FOR*]->(end:Concept {name: 'Raft Consensus'})
)
RETURN [node in nodes(path) | node.name] AS path,
       reduce(hours = 0, n in nodes(path) | hours + n.learning_hours) AS total_hours
```

## Use Cases

### 1. Optimize Your Learning Path

**Scenario**: You know basics and want to learn Raft Consensus

```python
from algorithms.shortest_path import ShortestPathFinder, LearningNode

# Load your graph
finder = ShortestPathFinder(your_graph)

# Set what you already know
finder.set_current_knowledge(['FUND-001', 'FUND-002', 'FUND-003'])

# Find optimal path
path = finder.find_shortest_path('FUND-001', 'CNSP-005')

print(f"Learning sequence ({path.total_hours} hours):")
print(path.path_description)
```

**Output**:
```
Learning sequence (8.5 hours):
1. Time and Ordering (3.0h, difficulty: 5/10)
2. Lamport Clocks (2.5h, difficulty: 5/10)
3. Vector Clocks (3.0h, difficulty: 6/10)
4. Raft Consensus (6.0h, difficulty: 7/10)
```

### 2. Identify Knowledge Gaps

**Scenario**: Job requires Raft, CQRS, Sharding

```python
# Find what you're missing
gaps = finder.identify_knowledge_gaps('CNSP-005')

print("Knowledge gaps:")
for level, concepts in gaps.items():
    if concepts:
        print(f"{level.upper()}: {', '.join(concepts)}")
```

**Output**:
```
Knowledge gaps:
BEGINNER: Distributed Systems, CAP Theorem
INTERMEDIATE: Time and Ordering, Lamport Clocks, Vector Clocks
ADVANCED: Consensus Problem
```

### 3. Estimate Time to Mastery

**Scenario**: How long to master distributed systems for interview?

```python
# Set learning goals
goals = ['CNSP-005', 'PAT-CQRS-001', 'PART-004']

# Estimate time
estimate = finder.estimate_mastery_time(goals, hours_per_day=8.0)

print(f"Concepts to learn: {estimate['concepts_to_learn']}")
print(f"Total time: {estimate['weeks']} weeks ({estimate['hours']} hours)")
```

**Output**:
```
Concepts to learn: 18
Total time: 4.2 weeks (168 hours)
```

### 4. Find Similar Architectures

**Scenario**: Comparing Netflix and Uber architectures

```cypher
MATCH (netflix:Company {name: 'Netflix'})-[:IMPLEMENTS_PATTERN]->(p:Pattern)<-[:IMPLEMENTS_PATTERN]-(uber:Company {name: 'Uber'})
WITH collect(distinct p.name) AS shared_patterns
RETURN shared_patterns, size(shared_patterns) AS similarity_count
```

**Output**:
```
shared_patterns: ["Circuit Breaker", "Event-Driven Architecture", "Cache-Aside", "Auto-Scaling"]
similarity_count: 4
```

### 5. Learn from Incidents

**Scenario**: Find all configuration error incidents

```cypher
MATCH (i:Incident)-[:CAUSED_BY]->(rc:RootCause {category: 'RC-CONFIG'})
RETURN i.name, i.company, i.duration, rc.description
ORDER BY i.date DESC
LIMIT 10
```

**Output**:
```
AWS S3 Outage 2017 | Amazon | 4 hours | Typo in command
Cloudflare Outage 2019 | Cloudflare | 27 min | Regex performance
Facebook Outage 2021 | Meta | 6 hours | BGP route withdrawal
```

## Common Workflows

### Workflow 1: Building a Learning Plan

**Goal**: Master distributed systems in 16 weeks

```python
from algorithms.shortest_path import create_learning_plan

# Define parameters
current_knowledge = ['FUND-001', 'FUND-002']  # What you know
goals = [
    'CNSP-005',      # Raft
    'PAT-CQRS-001',  # CQRS
    'PART-004',      # Consistent Hashing
    'REPL-006'       # Leaderless Replication
]
hours_per_week = 40.0
max_weeks = 16

# Create plan
plan = create_learning_plan(
    graph=your_graph,
    current_knowledge=current_knowledge,
    goals=goals,
    hours_per_week=hours_per_week,
    max_weeks=max_weeks
)

if plan['feasible']:
    print(f"Plan is feasible! {plan['total_weeks']} weeks")
    for week in plan['weekly_plan']:
        print(f"\nWeek {week['week']} ({week['hours_used']}h):")
        for concept in week['concepts']:
            print(f"  - {concept}")
else:
    print(f"Not feasible: {plan['reason']}")
    print("Suggestions:")
    for suggestion in plan['suggestions']:
        print(f"  - {suggestion}")
```

### Workflow 2: Exploring Pattern Relationships

**Goal**: Find patterns that work well with CQRS

```cypher
MATCH (cqrs:Pattern {name: 'CQRS'})-[r:COMPOSES_WITH]->(other:Pattern)
WHERE r.synergy > 0.8
RETURN other.name AS pattern,
       r.synergy AS synergy,
       r.example_system AS example
ORDER BY r.synergy DESC
```

### Workflow 3: Analyzing Company Evolution

**Goal**: See how Netflix evolved from monolith to microservices

```cypher
MATCH (netflix:Company {name: 'Netflix'})-[:HAS_ARCHITECTURE]->(arch:Architecture)
RETURN arch.year,
       arch.scale_stage,
       arch.users,
       arch.primary_stack
ORDER BY arch.year
```

### Workflow 4: Finding Prevention Strategies

**Goal**: How to prevent cascade failures?

```cypher
MATCH (i:Incident)-[:CAUSED_BY]->(rc:RootCause)-[:PREVENTED_BY]->(p:Prevention)
WHERE i.name CONTAINS 'cascade' OR rc.description CONTAINS 'cascade'
RETURN p.strategy,
       p.effectiveness,
       p.cost,
       count(i) AS prevents_count
ORDER BY p.effectiveness DESC
```

## Interactive Query Console

### Neo4j Browser

1. Open http://localhost:7474
2. Login with neo4j/atlas123
3. Try example queries:

```cypher
// Visualize concept relationships
MATCH (c:Concept)-[r:PREREQUISITE_FOR]->(other:Concept)
WHERE c.category = 'FUNDAMENTALS'
RETURN c, r, other
LIMIT 50
```

### Python Interactive Shell

```python
import json
from algorithms.shortest_path import ShortestPathFinder, LearningNode

# Load sample data
with open('data/sample-concepts.json', 'r') as f:
    data = json.load(f)

# Create graph
graph = {}
for concept in data['concepts']:
    graph[concept['id']] = LearningNode(
        id=concept['id'],
        name=concept['name'],
        type='concept',
        learning_hours=concept['learning_hours'],
        difficulty=concept['difficulty'],
        prerequisites=concept.get('prerequisites', []),
        related_concepts=concept.get('related_to', [])
    )

# Find paths
finder = ShortestPathFinder(graph)
path = finder.find_shortest_path('FUND-001', 'CNSP-005')

print(f"Found path: {path.total_hours} hours")
for node in path.nodes:
    print(f"  {node.name} ({node.learning_hours}h)")
```

## Visualization Examples

### Concept Map Visualization

```python
import networkx as nx
import matplotlib.pyplot as plt

# Create graph
G = nx.DiGraph()
for concept in data['concepts']:
    G.add_node(concept['id'], **concept)

for rel in data['relationships']['prerequisite_for']:
    G.add_edge(rel['from'], rel['to'])

# Visualize
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color='lightblue',
        node_size=500, font_size=8, arrows=True)
plt.title("Concept Prerequisites")
plt.show()
```

### Pattern Network Visualization

```python
# Load pattern data
with open('schemas/pattern-network.yaml', 'r') as f:
    import yaml
    patterns = yaml.safe_load(f)

# Create pattern graph
P = nx.Graph()
for pattern in patterns['patterns']:
    P.add_node(pattern['id'], name=pattern['name'], complexity=pattern['complexity'])

# Add relationships
for comp in patterns['relationships']['compositions']:
    P.add_edge(comp['from'], comp['to'], synergy=comp['synergy'])

# Visualize with colors by complexity
color_map = {'simple': 'green', 'moderate': 'yellow', 'complex': 'orange', 'expert': 'red'}
colors = [color_map[P.nodes[n]['complexity']] for n in P.nodes()]

nx.draw(P, pos=nx.spring_layout(P), with_labels=True, node_color=colors)
plt.title("Pattern Composition Network")
plt.show()
```

## Advanced Topics

### Custom Cost Functions

Modify the cost function to prioritize different learning styles:

```python
class CustomPathFinder(ShortestPathFinder):
    def calculate_cost(self, node, path_so_far):
        # Base cost
        cost = node.learning_hours

        # Prioritize foundational concepts
        if node.category == 'FUNDAMENTALS':
            cost *= 0.5  # 50% discount

        # Penalize jumping difficulty levels
        if path_so_far:
            prev_node = self.graph[path_so_far[-1]]
            if node.difficulty - prev_node.difficulty > 3:
                cost *= 2.0  # 2x cost for big jumps

        return cost
```

### Batch Learning Path Optimization

Find optimal order for multiple goals:

```python
def optimize_learning_sequence(goals, current_knowledge):
    # Find all prerequisites for all goals
    all_required = set()
    for goal in goals:
        prereqs = finder.find_all_prerequisites(goal)
        all_required.update(p.id for p in prereqs)

    # Remove already known
    to_learn = all_required - set(current_knowledge)

    # Sort by difficulty and dependencies
    sorted_concepts = sorted(
        [graph[cid] for cid in to_learn],
        key=lambda c: (c.difficulty, len(c.prerequisites))
    )

    return sorted_concepts
```

### Export to Other Formats

#### GraphML for Gephi
```python
import networkx as nx
G = load_graph()  # Your graph loading function
nx.write_graphml(G, "atlas_graph.graphml")
```

#### JSON for D3.js
```python
import json
import networkx as nx

G = load_graph()
data = nx.node_link_data(G)

with open('atlas_graph.json', 'w') as f:
    json.dump(data, f, indent=2)
```

#### CSV for Excel
```python
import pandas as pd

# Export concepts
concepts_df = pd.DataFrame([
    {
        'id': n,
        'name': G.nodes[n]['name'],
        'category': G.nodes[n]['category'],
        'learning_hours': G.nodes[n]['learning_hours']
    }
    for n in G.nodes()
])
concepts_df.to_csv('concepts.csv', index=False)

# Export relationships
edges_df = pd.DataFrame([
    {
        'from': u,
        'to': v,
        'type': G.edges[u, v].get('type', 'unknown')
    }
    for u, v in G.edges()
])
edges_df.to_csv('relationships.csv', index=False)
```

## Troubleshooting

### Neo4j Connection Issues

```python
from neo4j import GraphDatabase

# Test connection
try:
    driver = GraphDatabase.driver("bolt://localhost:7687",
                                   auth=("neo4j", "atlas123"))
    with driver.session() as session:
        result = session.run("RETURN 1 AS test")
        print("Connection successful:", result.single()['test'])
    driver.close()
except Exception as e:
    print(f"Connection failed: {e}")
```

### NetworkX Performance Issues

For large graphs (>10K nodes), use sparse representations:

```python
import scipy.sparse as sp
import networkx as nx

# Convert to sparse matrix
A = nx.adjacency_matrix(G)
print(f"Sparsity: {A.nnz / (A.shape[0] * A.shape[1]) * 100:.2f}%")
```

### Data Loading Errors

```python
import yaml

try:
    with open('schemas/concept-ontology.yaml', 'r') as f:
        data = yaml.safe_load(f)
    print(f"Loaded {len(data['concepts'])} concepts")
except yaml.YAMLError as e:
    print(f"YAML parsing error: {e}")
except FileNotFoundError:
    print("Schema file not found. Check path.")
```

## Next Steps

1. **Explore Schemas**: Read [Schema Reference](docs/schema-reference.md)
2. **Run Queries**: Try [Query Examples](queries/comprehensive-queries.cypher)
3. **Build Learning Plan**: Use [Learning Path Algorithm](algorithms/shortest_path.py)
4. **Visualize**: Create custom visualizations with sample code
5. **Contribute**: Add new concepts, patterns, or incidents

## Resources

- **Documentation**: `/docs/`
- **Schemas**: `/schemas/`
- **Queries**: `/queries/`
- **Algorithms**: `/algorithms/`
- **Sample Data**: `/data/`

## Support

- **Atlas Study Plan**: See parent directory
- **Issues**: Track in project issue tracker
- **Community**: Join study groups

---

**Happy Learning!**

The shortest path between you and distributed systems mastery is through the knowledge graph.