# Glossary

## A

**Actor Model**
: A mathematical model for concurrent computation where "actors" are primitive units that can send messages, create other actors, and change their behavior.

**Amdahl's Law**
: The theoretical speedup in latency of a task is limited by the sequential fraction of the task.

**Anti-entropy**
: A process for ensuring replicas converge to the same state by comparing and synchronizing data.

**Atomicity**
: The property that a transaction either completes entirely or has no effect at all.

**Availability**
: The percentage of time a system is operational and accessible. Often measured as "number of nines" (99.9%, 99.99%, etc.).

## B

**Backpressure**
: A mechanism to prevent a fast producer from overwhelming a slow consumer by signaling when to slow down.

**Byzantine Failure**
: A failure where a component behaves arbitrarily, potentially including malicious behavior.

**Byzantine Fault Tolerance (BFT)**
: The ability of a system to continue operating correctly even when some nodes fail in arbitrary ways.

## C

**CAP Theorem**
: A theorem stating that a distributed system cannot simultaneously guarantee Consistency, Availability, and Partition tolerance.

**Causal Consistency**
: A consistency model ensuring that operations that are causally related are seen in the same order by all nodes.

**Circuit Breaker**
: A design pattern that prevents cascading failures by failing fast when a dependency is unhealthy.

**Consensus**
: The process of getting distributed nodes to agree on a single value or state.

**Consistency**
: The property that all nodes see the same data at the same time.

**CQRS (Command Query Responsibility Segregation)**
: A pattern that separates read and write operations into different models.

## D

**Data Gravity**
: The tendency for applications and services to be attracted to large datasets due to the cost and complexity of moving data.

**Distributed Hash Table (DHT)**
: A decentralized distributed system providing a lookup service similar to a hash table.

**Durability**
: The property that once a transaction commits, it will remain committed even in the case of system failure.

## E

**Eventually Consistent**
: A consistency model guaranteeing that if no new updates are made, eventually all replicas will converge.

**Event Sourcing**
: A pattern where state changes are stored as a sequence of events.

**Exactly-Once Delivery**
: A message delivery guarantee ensuring each message is delivered exactly one time.

## F

**Fail-Stop**
: A failure model where nodes either operate correctly or stop completely.

**Fault Tolerance**
: The ability of a system to continue operating properly in the event of failures.

**FLP Impossibility**
: A theoretical result proving that in an asynchronous network, consensus cannot be guaranteed if even one node can fail.

## G

**Gossip Protocol**
: A communication protocol where nodes periodically exchange state information with random peers.

## H

**Happens-Before Relation**
: A partial ordering of events in a distributed system based on causal relationships.

**Hot Spot**
: A situation where one node receives disproportionately more load than others.

**Hybrid Logical Clock (HLC)**
: A logical clock that combines physical time with logical counters for ordering events.

## I

**Idempotence**
: The property that applying an operation multiple times has the same effect as applying it once.

**Isolation**
: The property that concurrent transactions appear to execute serially.

## J

**Jepsen**
: A framework for testing distributed systems by simulating network failures and other adverse conditions.

## L

**Leader Election**
: The process of designating a single node as the coordinator among a group of nodes.

**Linearizability**
: A strong consistency model ensuring operations appear to occur atomically at some point between their start and end times.

**Little's Law**
: L = λW, where L is the average number of items in a system, λ is the arrival rate, and W is the average time an item spends in the system.

## M

**Merkle Tree**
: A tree data structure where each leaf is a hash of a data block and each internal node is a hash of its children.

**Microservices**
: An architectural style structuring an application as a collection of loosely coupled services.

**MVCC (Multi-Version Concurrency Control)**
: A concurrency control method that allows multiple versions of data to exist simultaneously.

## N

**Network Partition**
: A situation where network failures divide the cluster into separate groups that cannot communicate.

## O

**Optimistic Locking**
: A concurrency control method that assumes conflicts are rare and checks for conflicts before committing.

**Outbox Pattern**
: A pattern ensuring atomic database updates and event publishing by storing events in a database table.

## P

**Partition Tolerance**
: The ability of a system to continue operating despite network partitions.

**Paxos**
: A consensus algorithm for reaching agreement among distributed nodes.

**Pessimistic Locking**
: A concurrency control method that locks resources before using them to prevent conflicts.

## Q

**Quorum**
: The minimum number of nodes that must agree for an operation to be considered successful.

**Queue**
: A data structure following first-in-first-out (FIFO) principle for message ordering.

## R

**Raft**
: A consensus algorithm designed to be more understandable than Paxos.

**Read Repair**
: A technique for achieving eventual consistency by fixing inconsistencies during read operations.

**Replication**
: The process of maintaining copies of data across multiple nodes.

## S

**Saga Pattern**
: A pattern for managing distributed transactions through a sequence of local transactions with compensating actions.

**Serializability**
: A property ensuring that concurrent transactions produce the same result as some sequential execution.

**Sharding**
: A method of horizontal partitioning where data is split across multiple databases.

**Split-Brain**
: A situation where a distributed system splits into two or more parts that each believe they are the only active system.

## T

**Two-Phase Commit (2PC)**
: A distributed transaction protocol ensuring all participants either commit or abort a transaction.

**Two-Phase Locking (2PL)**
: A concurrency control protocol ensuring serializability by acquiring all locks before releasing any.

## V

**Vector Clock**
: A logical clock used to determine the partial ordering of events in a distributed system.

**Virtual Synchrony**
: A model providing the illusion that messages are delivered to all members of a group simultaneously.

## W

**Write-Ahead Log (WAL)**
: A technique ensuring durability by writing changes to a log before applying them to the main data structure.

## Z

**ZAB (Zookeeper Atomic Broadcast)**
: A consensus protocol used by Apache Zookeeper for maintaining consistency.

**Zipf Distribution**
: A probability distribution where the frequency of an item is inversely proportional to its rank in frequency.