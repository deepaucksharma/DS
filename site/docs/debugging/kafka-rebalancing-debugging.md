# Kafka Rebalancing Debugging: Consumer Group Troubleshooting Guide

## Executive Summary

Kafka consumer rebalancing issues cause 35% of stream processing failures and can lead to duplicate processing or data loss. This guide provides systematic debugging approaches for consumer group coordination, partition assignment issues, and rebalancing storms.

## Common Rebalancing Error Patterns

### Consumer Group Issues
```bash
# Check consumer group status
kafka-consumer-groups --bootstrap-server localhost:9092 --group my-group --describe

# Monitor lag and member details
kafka-consumer-groups --bootstrap-server localhost:9092 --group my-group --describe --members --verbose

# Check for rebalancing activity
kafka-consumer-groups --bootstrap-server localhost:9092 --all-groups --describe | grep REBALANCING
```

### Investigation Commands
```bash
# Monitor consumer group state changes
kafka-consumer-groups --bootstrap-server localhost:9092 --group my-group --describe --state

# Check partition assignment
kafka-consumer-groups --bootstrap-server localhost:9092 --group my-group --describe --members

# Monitor broker logs for rebalancing
tail -f /opt/kafka/logs/server.log | grep -i rebalance

# Check consumer lag trends
kafka-consumer-groups --bootstrap-server localhost:9092 --group my-group --describe | awk '{print $5}' | grep -v LAG | sort -n
```

## Rebalancing Storm Investigation

### Symptoms and Causes
```java
// Common causes of rebalancing storms
public class ConsumerExample {
    public static void main(String[] args) {
        Properties props = new Properties();
        props.put("bootstrap.servers", "localhost:9092");
        props.put("group.id", "test-group");
        props.put("enable.auto.commit", "false");

        // ISSUE: Too short session timeout
        props.put("session.timeout.ms", "6000");  // Too short!
        props.put("heartbeat.interval.ms", "2000"); // Too close to session timeout

        // ISSUE: Too long max poll interval
        props.put("max.poll.interval.ms", "300000"); // 5 minutes - too long for quick processing

        KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
        consumer.subscribe(Arrays.asList("my-topic"));

        while (true) {
            ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
            for (ConsumerRecord<String, String> record : records) {
                // ISSUE: Slow processing causes max.poll.interval.ms violation
                processSlowly(record);  // Takes 2 minutes per record!
            }
            consumer.commitSync();  // This may never be reached
        }
    }
}
```

### Optimal Configuration
```java
// Optimized consumer configuration
Properties props = new Properties();
props.put("bootstrap.servers", "localhost:9092");
props.put("group.id", "optimized-group");

// Prevent frequent rebalancing
props.put("session.timeout.ms", "30000");        // 30 seconds
props.put("heartbeat.interval.ms", "10000");     // 10 seconds (1/3 of session timeout)
props.put("max.poll.interval.ms", "600000");     // 10 minutes for batch processing

// Optimize partition assignment
props.put("partition.assignment.strategy", "org.apache.kafka.clients.consumer.RangeAssignor");

// Control fetch behavior
props.put("max.poll.records", "100");            // Smaller batches for faster processing
props.put("fetch.min.bytes", "1024");            // Wait for at least 1KB
props.put("fetch.max.wait.ms", "500");           // Don't wait too long
```

## Debugging Techniques

### Consumer Group Monitoring
```python
from kafka.admin import KafkaAdminClient, ConfigResource, ConfigResourceType
from kafka import KafkaConsumer
import json

def monitor_consumer_group(group_id, bootstrap_servers):
    """Monitor consumer group health and rebalancing activity"""

    admin_client = KafkaAdminClient(
        bootstrap_servers=bootstrap_servers,
        client_id='group_monitor'
    )

    # Get consumer group description
    try:
        group_description = admin_client.describe_consumer_groups([group_id])
        group_info = group_description[group_id]

        print(f"Group State: {group_info.state}")
        print(f"Protocol Type: {group_info.protocol_type}")
        print(f"Protocol: {group_info.protocol}")

        print("\\nMembers:")
        for member in group_info.members:
            print(f"  Member ID: {member.member_id}")
            print(f"  Client ID: {member.client_id}")
            print(f"  Host: {member.host}")
            print(f"  Assignment: {len(member.member_assignment)} bytes")

        # Check for frequent rebalancing
        if group_info.state == 'Rebalancing':
            print("⚠️  Group is currently rebalancing!")

    except Exception as e:
        print(f"Error monitoring group: {e}")

# Usage
monitor_consumer_group('my-consumer-group', ['localhost:9092'])
```

### Partition Assignment Analysis
```bash
#!/bin/bash
# kafka-rebalance-analysis.sh

GROUP_ID="my-group"
BOOTSTRAP_SERVERS="localhost:9092"

echo "🔍 Analyzing Kafka Consumer Group: $GROUP_ID"

# Get current assignment
echo "Current partition assignment:"
kafka-consumer-groups --bootstrap-server $BOOTSTRAP_SERVERS \\
  --group $GROUP_ID --describe --members --verbose

# Check lag per partition
echo "\\nConsumer lag analysis:"
kafka-consumer-groups --bootstrap-server $BOOTSTRAP_SERVERS \\
  --group $GROUP_ID --describe | \\
  awk 'NR>1 {print $2 ":" $3 " lag=" $5}' | \\
  sort -t= -k2 -n

# Monitor rebalancing frequency
echo "\\nMonitoring for rebalancing events..."
timeout 60 kafka-console-consumer --bootstrap-server $BOOTSTRAP_SERVERS \\
  --topic __consumer_offsets \\
  --formatter "kafka.coordinator.group.GroupMetadataManager\\$OffsetsMessageFormatter" \\
  --from-beginning | grep $GROUP_ID | grep -i rebalance

echo "✅ Analysis complete"
```

## Prevention Strategies

### Consumer Health Checks
```java
// Implement consumer health monitoring
public class HealthyConsumer {
    private final KafkaConsumer<String, String> consumer;
    private final AtomicLong lastPollTime = new AtomicLong(System.currentTimeMillis());
    private final AtomicLong processedCount = new AtomicLong(0);

    public void consume() {
        // Start health check thread
        startHealthCheck();

        while (running) {
            try {
                ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(1000));
                lastPollTime.set(System.currentTimeMillis());

                for (ConsumerRecord<String, String> record : records) {
                    processRecord(record);
                    processedCount.incrementAndGet();
                }

                if (!records.isEmpty()) {
                    consumer.commitSync();
                }

            } catch (WakeupException e) {
                break;
            } catch (Exception e) {
                logger.error("Error in consumer loop", e);
                // Don't let exceptions break the poll loop
            }
        }
    }

    private void startHealthCheck() {
        ScheduledExecutorService healthChecker = Executors.newSingleThreadScheduledExecutor();
        healthChecker.scheduleAtFixedRate(() -> {
            long timeSinceLastPoll = System.currentTimeMillis() - lastPollTime.get();
            if (timeSinceLastPoll > 25000) {  // 25 seconds without poll
                logger.warn("Consumer hasn't polled in {} ms", timeSinceLastPoll);
                // Alert or restart consumer
            }
        }, 30, 30, TimeUnit.SECONDS);
    }
}
```

### Graceful Shutdown
```java
// Implement graceful consumer shutdown
public class GracefulConsumerShutdown {
    private volatile boolean running = true;
    private final KafkaConsumer<String, String> consumer;

    public void shutdown() {
        running = false;
        consumer.wakeup();  // Interrupt the poll loop
    }

    public void run() {
        try {
            while (running) {
                ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(1000));

                for (ConsumerRecord<String, String> record : records) {
                    if (!running) break;  // Check for shutdown signal
                    processRecord(record);
                }

                if (!records.isEmpty()) {
                    consumer.commitSync();
                }
            }
        } catch (WakeupException e) {
            // Expected when shutting down
        } finally {
            try {
                consumer.commitSync();  // Final commit
            } finally {
                consumer.close();
            }
        }
    }
}
```

This debugging guide provides essential techniques for identifying and resolving Kafka consumer rebalancing issues in production environments.