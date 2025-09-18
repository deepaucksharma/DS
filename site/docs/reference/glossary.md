# Glossary

Key distributed systems terminology with practical examples.

## Core Terms

| Term | Definition | Example |
|------|------------|----------|
| **Actor Model** | Mathematical model for concurrent computation with message-passing actors | Akka framework, Erlang processes |
| **Amdahl's Law** | Theoretical speedup limited by sequential fraction of task | 90% parallel code = max 10x speedup |
| **Anti-entropy** | Process ensuring replica convergence through data synchronization | Cassandra repair operations |
| **Atomicity** | Transaction completes entirely or has no effect | Bank transfer: both debit AND credit |
| **Availability** | Percentage of operational time | 99.9% = 8.77 hours downtime/year |
| **Backpressure** | Mechanism preventing fast producers from overwhelming slow consumers | TCP flow control, Reactive Streams |
| **Byzantine Failure** | Component behaves arbitrarily, potentially maliciously | Corrupted node sending wrong data |
| **Byzantine Fault Tolerance** | System operates correctly despite arbitrary node failures | Blockchain consensus algorithms |
| **CAP Theorem** | Cannot simultaneously guarantee Consistency, Availability, Partition tolerance | Choose 2 of 3 during network splits |
| **Causal Consistency** | Causally related operations seen in same order by all nodes | Social media: see post before comments |
| **Circuit Breaker** | Fail fast pattern preventing cascading failures | Netflix Hystrix, AWS Circuit Breaker |
| **Consensus** | Distributed nodes agreeing on single value or state | Raft leader election, Paxos proposals |
| **Consistency** | All nodes see same data simultaneously | Strong consistency in RDBMS |
| **CQRS** | Separate read and write operations into different models | Event-sourced systems with read projections |

## Data & Storage

| Term | Definition | Example |
|------|------------|----------|
| **Data Gravity** | Applications attracted to large datasets due to movement costs | ML models deployed near training data |
| **Distributed Hash Table** | Decentralized lookup service like hash table | Chord, Kademlia, BitTorrent DHT |
| **Durability** | Committed transactions survive system failures | WAL ensures data persists after crashes |
| **Eventually Consistent** | Replicas converge if no new updates occur | DNS propagation, DynamoDB |
| **Event Sourcing** | State changes stored as sequence of events | Apache Kafka, Event Store |
| **Exactly-Once Delivery** | Each message delivered exactly one time | Kafka with idempotent producers |
| **Merkle Tree** | Tree where leaves are data hashes, internals hash children | Git commits, Bitcoin blockchain |
| **MVCC** | Multiple data versions exist simultaneously | PostgreSQL, InnoDB storage engine |
| **Replication** | Maintaining data copies across multiple nodes | MySQL master-slave, Cassandra N replicas |
| **Sharding** | Horizontal partitioning across multiple databases | MongoDB shards, MySQL Cluster |
| **Write-Ahead Log** | Changes written to log before main data structure | PostgreSQL WAL, MySQL binlog |

## Failure & Reliability

| Term | Definition | Example |
|------|------------|----------|
| **Fail-Stop** | Nodes either operate correctly or stop completely | Process crashes but doesn't send wrong data |
| **Fault Tolerance** | System continues operating despite failures | RAID arrays, N+1 redundancy |
| **FLP Impossibility** | Asynchronous consensus impossible with one node failure | Theoretical limit on distributed consensus |
| **Hot Spot** | One node receives disproportionately more load | Celebrity user on social platform |
| **Network Partition** | Network failures divide cluster into separate groups | Data center connectivity loss |
| **Partition Tolerance** | System operates despite network partitions | Cassandra continues with majority nodes |
| **Split-Brain** | System splits believing each part is the only active system | Two data centers both think they're primary |

## Algorithms & Protocols

| Term | Definition | Example |
|------|------------|----------|
| **Gossip Protocol** | Nodes periodically exchange state with random peers | Cassandra cluster membership |
| **Happens-Before Relation** | Partial event ordering based on causal relationships | Lamport timestamps, vector clocks |
| **Hybrid Logical Clock** | Combines physical time with logical counters | CockroachDB transaction ordering |
| **Leader Election** | Designating single coordinator among node group | Raft leader, Zookeeper master |
| **Linearizability** | Operations appear atomic between start and end times | Strict consistency in etcd |
| **Paxos** | Consensus algorithm for distributed agreement | Google Chubby, Apache Cassandra |
| **Raft** | More understandable consensus algorithm than Paxos | etcd, Consul, TiKV |
| **Vector Clock** | Logical clock for event partial ordering | Riak, Voldemort versioning |
| **ZAB** | Zookeeper Atomic Broadcast consensus protocol | Apache Zookeeper replication |

## Concurrency & Transactions

| Term | Definition | Example |
|------|------------|----------|
| **Idempotence** | Multiple operation applications have same effect as once | HTTP PUT, database upserts |
| **Isolation** | Concurrent transactions appear to execute serially | ACID database transactions |
| **Optimistic Locking** | Assume conflicts are rare, check before committing | Git merge conflicts, ORM optimistic locking |
| **Pessimistic Locking** | Lock resources before use to prevent conflicts | Database row locks, mutex |
| **Quorum** | Minimum nodes that must agree for successful operation | Cassandra R + W > N |
| **Saga Pattern** | Distributed transactions via local transactions + compensations | Order processing with payment/inventory |
| **Serializability** | Concurrent transactions produce same result as sequential | Snapshot isolation, 2PL |
| **Two-Phase Commit** | All participants commit or abort transaction | XA transactions, distributed databases |
| **Two-Phase Locking** | Acquire all locks before releasing any | Traditional RDBMS concurrency |

## Architecture & Patterns

| Term | Definition | Example |
|------|------------|----------|
| **Microservices** | Application as collection of loosely coupled services | Netflix architecture, Amazon services |
| **Outbox Pattern** | Atomic database updates and event publishing via table | Ensuring order events are published |
| **Queue** | FIFO data structure for message ordering | Amazon SQS, RabbitMQ |
| **Read Repair** | Fix inconsistencies during read operations | Cassandra anti-entropy repair |
| **Virtual Synchrony** | Illusion of simultaneous message delivery to group | ISIS toolkit, group communication |

## Performance & Scaling

| Term | Definition | Example |
|------|------------|----------|
| **Little's Law** | L = λW (items = arrival rate × time in system) | Queue length = throughput × latency |
| **Zipf Distribution** | Item frequency inversely proportional to rank | Web page popularity, word frequency |

## Testing & Verification

| Term | Definition | Example |
|------|------------|----------|
| **Jepsen** | Framework testing distributed systems with simulated failures | Database consistency testing |