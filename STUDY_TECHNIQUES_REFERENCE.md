# Atlas Study Techniques Quick Reference

## Cognitive Science-Based Learning Methods

### 1. The Feynman Technique (For Deep Understanding)
```yaml
Steps:
  1. Choose a diagram/concept
  2. Explain it in simple terms to a child
  3. Identify gaps where you struggled
  4. Go back and re-learn those gaps
  5. Simplify and use analogies

Example with Kafka Architecture:
  Simple: "Kafka is like a post office that never loses mail"
  - Producers = People sending letters
  - Topics = Different mailbox categories
  - Partitions = Multiple sorting bins
  - Consumers = People picking up mail
  - Offset = Receipt number for tracking
```

### 2. The Memory Palace (For Diagram Memorization)
```yaml
Technique:
  1. Choose a familiar location (your home)
  2. Create a mental walk-through path
  3. Place diagram components at locations
  4. Add vivid, unusual imagery
  5. Practice the walk repeatedly

Example for Netflix Architecture:
  Front Door: CDN (Akamai) - Giant cache of movies
  Living Room: Load Balancer - Traffic cop directing viewers
  Kitchen: API Gateway (Zuul) - Chef taking orders
  Bedroom: Microservices - Individual workers
  Basement: Cassandra - Underground movie vault
  Garage: Kafka - Message delivery trucks
```

### 3. The ADEPT Method (For Complex Concepts)
```yaml
A - Analogy: Find a similar concept from everyday life
D - Diagram: Draw it multiple ways
E - Example: Create concrete instances
P - Plain English: Explain without jargon
T - Technical: Give the precise definition

Example for Consensus:
  A: "Like friends agreeing on a restaurant"
  D: Draw Raft, Paxos, PBFT diagrams
  E: "5 servers voting on next database write"
  P: "Getting computers to agree on something"
  T: "Algorithm for distributed agreement with f failures"
```

### 4. Spaced Repetition Algorithms
```yaml
SuperMemo Algorithm (SM-2):
  Intervals: 1, 6, 16, 35, 82 days

  After each review, rate 0-5:
  5 - Perfect recall → Increase interval × 2.5
  4 - Good recall → Increase interval × 2.0
  3 - Okay recall → Increase interval × 1.3
  2 - Hard recall → Reset to 1 day
  1 - Failed → Reset to immediate
  0 - Complete blank → Re-learn from scratch

Tracking Template:
  Diagram: Uber Dispatch System
  Reviews: [Day 1: 5] [Day 6: 4] [Day 16: 5] [Day 35: 3]
  Next: Day 45
```

### 5. Active Recall Testing
```yaml
Progressive Difficulty Levels:

Level 1 - Recognition (Multiple Choice):
  "Which consistency model does Cassandra use?"
  a) Strong  b) Eventual  c) Causal  d) Linear

Level 2 - Cued Recall (Fill in Blanks):
  "Netflix uses _____ for CDN and _____ for streaming"

Level 3 - Free Recall (Open Questions):
  "Draw Netflix's complete architecture from memory"

Level 4 - Application (Problem Solving):
  "Design a system like Netflix for 10M users"

Level 5 - Synthesis (Creation):
  "Combine Netflix and Uber patterns for new system"
```

### 6. Interleaved Practice Schedule
```yaml
Anti-Pattern (Blocked):
  Monday: All AWS diagrams (8 hours)
  Tuesday: All Google diagrams (8 hours)
  ❌ Lower retention, poor discrimination

Optimal Pattern (Interleaved):
  Monday AM: 2 AWS + 2 Google + 2 Azure
  Monday PM: 1 incident + 1 debug + 1 scale
  Tuesday AM: 2 Meta + 2 Netflix + 2 Uber
  Tuesday PM: 1 performance + 1 cost + 1 capacity
  ✅ 40% better retention and discrimination
```

### 7. Elaborative Interrogation
```yaml
For each component, ask "Why?":

Example: Uber Uses H3 Hexagonal Grid
  Why hexagons? → Equal distance to neighbors
  Why equal distance? → Fair surge pricing zones
  Why zones? → Can't calculate per-point
  Why not squares? → Diagonal distance varies
  Why does distance matter? → Driver dispatch time

This creates a causal chain that aids memory
```

### 8. The Generation Effect
```yaml
Don't just read - generate:

Passive: Read about Kafka partitions
Active: List 5 reasons for partitioning
Better: Design partitioning for your use case
Best: Predict partition failure modes

Generation Exercises:
  - Before seeing answer, predict the design
  - Create your own examples
  - Generate test questions
  - Produce counter-examples
  - Design variations
```

### 9. Dual Coding Theory
```yaml
Combine verbal and visual:

Visual Elements:
  - Color code by plane (Edge=Blue, Service=Green)
  - Use consistent shapes (DB=cylinder, API=rectangle)
  - Add emoji markers 🔄 for sync, ⚡ for async
  - Draw data flow arrows with latency labels

Verbal Elements:
  - Create acronyms (CALM = Consistency As Logical Monotonicity)
  - Use rhymes ("When in doubt, scale out")
  - Build stories around architectures
  - Develop catchphrases for patterns
```

### 10. Cognitive Load Management
```yaml
Chunking Strategy:
  Instead of: 30 individual services
  Chunk into: 5 service groups × 6 services

  Instead of: 240 company diagrams
  Chunk into: 30 companies × 8 standard diagrams

Progressive Complexity:
  Week 1: Just component names
  Week 2: Add connections
  Week 3: Add technologies
  Week 4: Add metrics
  Week 5: Add failure modes
  Week 6: Add costs

Working Memory Rules:
  - Maximum 7±2 items at once
  - Break after 25 minutes focus
  - Switch topics every 90 minutes
  - Full reset every 4 hours
```

### 11. Deliberate Practice Protocols
```yaml
Requirements for Deliberate Practice:
  1. Well-defined specific goal
  2. Full focus and effort
  3. Immediate feedback
  4. Repetition with refinement

Example Session (30 minutes):
  Goal: Draw Cassandra's architecture in 5 minutes

  Attempt 1 (5 min): Draw from memory
  Feedback (2 min): Check against reference
  Attempt 2 (5 min): Fix mistakes
  Feedback (2 min): Identify remaining gaps
  Attempt 3 (5 min): Include all details
  Feedback (2 min): Verify accuracy
  Reflection (9 min): What patterns help memory?
```

### 12. Metacognitive Strategies
```yaml
Before Learning - Planning:
  - What do I already know about this?
  - What's my specific goal?
  - How will I know I've learned it?
  - What's my strategy?

During Learning - Monitoring:
  - Am I understanding this?
  - What's confusing me?
  - Should I change approach?
  - Am I focused or distracted?

After Learning - Evaluation:
  - Can I explain this to someone?
  - What are the key points?
  - Where are my knowledge gaps?
  - What should I review tomorrow?

Metacognitive Prompts:
  "How do I know this is correct?"
  "What would happen if this failed?"
  "Why did they choose this over alternatives?"
  "When would this not be appropriate?"
```

### 13. The Testing Effect
```yaml
Testing Schedule (Per Diagram):

Immediate Test (0 min after study):
  - Close eyes, recreate mentally

Short Delay (10 min):
  - Sketch main components

Medium Delay (1 hour):
  - Draw complete diagram

Long Delay (1 day):
  - Recreate with all details

Retention Test (1 week):
  - Draw and explain to someone

Testing > Restudying:
  - 10 minutes testing = 30 minutes restudying
  - Errors during testing improve learning
  - Harder retrieval = stronger memory
```

### 14. Desirable Difficulties
```yaml
Make It Harder (Intelligently):

Spacing: Don't review immediately
  Bad: Study Kafka 10 times today
  Good: Study Kafka once daily for 10 days

Interleaving: Mix different patterns
  Bad: All database patterns together
  Good: Database, messaging, caching, repeat

Testing: Retrieve from memory
  Bad: Re-read diagrams repeatedly
  Good: Draw from memory, then check

Generation: Create, don't copy
  Bad: Trace existing diagrams
  Good: Design similar system yourself

Variation: Change context
  Bad: Always study at desk
  Good: Vary location, time, method
```

### 15. Peer Learning Protocols
```yaml
Think-Pair-Share:
  Think (5 min): Design solution alone
  Pair (10 min): Compare with partner
  Share (5 min): Present best solution

Jigsaw Method:
  - Divide 30 companies among 3 people
  - Each becomes expert on 10
  - Teach others your companies
  - Everyone learns all 30

Peer Review Checklist:
  □ Are all components present?
  □ Is data flow clear?
  □ Are trade-offs identified?
  □ Are metrics realistic?
  □ Are failures handled?
  □ Is cost considered?
```

### 16. Error-Based Learning
```yaml
Productive Failure Protocol:

1. Attempt without help (struggle is good)
2. Make predictions about design
3. Identify where you went wrong
4. Understand why the error occurred
5. Create rule to prevent repetition

Error Journal Entry:
  Date: _____
  Diagram: Uber Dispatch
  Error: Forgot to partition by geography
  Why: Didn't consider geographic scale
  Rule: Always consider data locality
  Prevention: Check geographic distribution
```

### 17. The 3-2-1 Summary Technique
```yaml
After each study session:

3 Key Concepts:
  1. _____
  2. _____
  3. _____

2 Connections to Previous Knowledge:
  1. _____
  2. _____

1 Question Still Unanswered:
  1. _____

Example:
  3: Kafka uses logs, partitions, offsets
  2: Similar to database WAL, Like distributed queue
  1: How does exactly-once delivery work?
```

### 18. Progressive Visualization
```yaml
Building Mental Models in Stages:

Stage 1: Boxes and Arrows
  - Just component relationships

Stage 2: Add Technologies
  - Specific tech choices

Stage 3: Add Metrics
  - Latencies, throughput

Stage 4: Add Failures
  - Failure modes, recovery

Stage 5: Add Evolution
  - How it scales over time

Each stage builds on previous, creating layers
```

### 19. The SQ3R Method
```yaml
For Reading Documentation:

Survey (2 min):
  - Skim headings and diagrams
  - Note structure and length

Question (2 min):
  - What problems does this solve?
  - How does it work?
  - What are trade-offs?

Read (10 min):
  - Active reading with notes
  - Highlight key concepts

Recite (5 min):
  - Explain in own words
  - Without looking at notes

Review (5 min):
  - Check understanding
  - Identify gaps
  - Plan re-reading
```

### 20. Contextual Interference
```yaml
Random vs Blocked Practice:

Blocked (Less Effective):
  - Study all Redis patterns
  - Then all Memcached patterns
  - Then all Hazelcast patterns

Random (More Effective):
  - Redis caching pattern
  - Memcached session storage
  - Hazelcast distributed map
  - Redis pub/sub
  - Memcached consistent hashing
  - Hazelcast cluster management

Random feels harder but produces 2x retention
```

---

## Quick Reference Matrix

| Technique | Best For | Time Required | Difficulty |
|-----------|----------|---------------|------------|
| Feynman | Deep understanding | 30 min | Medium |
| Memory Palace | Memorizing structure | 45 min | High |
| ADEPT | Complex concepts | 20 min | Medium |
| Spaced Repetition | Long-term retention | 5 min/day | Low |
| Active Recall | Knowledge testing | 15 min | Medium |
| Interleaving | Pattern discrimination | No extra | Low |
| Elaboration | Causal understanding | 20 min | Medium |
| Generation | Active learning | 15 min | Medium |
| Dual Coding | Memory encoding | 10 min | Low |
| Deliberate Practice | Skill building | 30 min | High |

---

## Daily Technique Rotation

```yaml
Monday: Memory Palace + Testing
Tuesday: Feynman + Generation
Wednesday: ADEPT + Peer Learning
Thursday: Deliberate Practice + Errors
Friday: Synthesis + Review
Weekend: Spaced Repetition + Fun Projects
```

---

## Emergency Cramming Protocol
(Not recommended, but if you must...)

```yaml
24 Hours Before:
  - Focus on 20% that covers 80%
  - Use memory palace for critical paths
  - Practice 10 most common patterns
  - Sleep 7+ hours (critical!)

12 Hours Before:
  - Active recall all key concepts
  - Draw 20 diagrams from memory
  - Review error journal

3 Hours Before:
  - Light review only
  - Confidence building
  - Relaxation exercises

1 Hour Before:
  - Stop studying
  - Light walk
  - Positive visualization
```

Remember: These techniques compound. Using multiple techniques together produces superior results to any single technique alone.

**The secret:** Consistency + Active Practice + Proper Rest = Mastery