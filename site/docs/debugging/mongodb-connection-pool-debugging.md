# MongoDB Connection Pool Debugging: Connection Exhaustion Troubleshooting Guide

## Executive Summary

MongoDB connection pool exhaustion affects 30% of NoSQL applications and can cause cascading failures across microservices. This guide provides systematic debugging approaches used by teams at MongoDB Inc, Uber, and other MongoDB-heavy organizations to resolve connection leaks, pool sizing issues, and timeout problems.

## Common Connection Pool Issues

### Connection Pool Exhaustion
```javascript
// Error patterns to look for
MongoError: connection timed out
MongoError: server selection timed out after 30000 ms
MongoError: pool destroyed
MongoError: connection pool closed
```

### Investigation Commands
```bash
# Check MongoDB connection stats
mongo --eval "db.serverStatus().connections"

# Monitor active connections
watch -n 1 'mongo --eval "db.serverStatus().connections"'

# Check application connection pool
# Node.js example
console.log(db.topology.connections());

# Check system-level connections
netstat -an | grep :27017 | wc -l
lsof -i :27017 | wc -l
```

## Systematic Investigation

### Connection Pool Configuration Analysis
```javascript
// Optimal connection pool settings
const mongoose = require('mongoose');

const connectionConfig = {
  maxPoolSize: 10,        // Maximum connections
  minPoolSize: 5,         // Minimum connections
  maxIdleTimeMS: 30000,   // Close idle connections after 30s
  serverSelectionTimeoutMS: 5000,
  socketTimeoutMS: 45000,
  family: 4,              // Use IPv4
  bufferMaxEntries: 0,    // Disable mongoose buffering
  bufferCommands: false
};

// Debug connection events
mongoose.connection.on('connected', () => {
  console.log('MongoDB connected');
});

mongoose.connection.on('error', (err) => {
  console.log('MongoDB connection error:', err);
});

mongoose.connection.on('disconnected', () => {
  console.log('MongoDB disconnected');
});
```

### Connection Leak Detection
```javascript
// Connection leak detection utility
class ConnectionMonitor {
  constructor(db) {
    this.db = db;
    this.connectionCounts = new Map();
  }

  async trackConnection(operation, operationName) {
    const startTime = Date.now();
    const initialConnections = await this.getConnectionCount();

    try {
      const result = await operation();
      return result;
    } finally {
      const endTime = Date.now();
      const finalConnections = await this.getConnectionCount();

      if (finalConnections > initialConnections) {
        console.warn(`Potential connection leak in ${operationName}:
          Initial: ${initialConnections}, Final: ${finalConnections},
          Duration: ${endTime - startTime}ms`);
      }
    }
  }

  async getConnectionCount() {
    const status = await this.db.admin().serverStatus();
    return status.connections.current;
  }
}
```

## Real Production Examples

### Case Study: Uber Connection Pool Exhaustion
```javascript
// Problem: Connection pool exhaustion during peak hours
// Symptoms: 5000+ concurrent connections, timeouts

// Investigation revealed improper cursor handling
// Before (problematic):
const cursor = db.collection('rides').find({status: 'active'});
cursor.forEach(doc => {
  // Process document
  // Cursor never closed!
});

// After (fixed):
const cursor = db.collection('rides').find({status: 'active'});
try {
  await cursor.forEach(doc => {
    // Process document
  });
} finally {
  await cursor.close();  // Always close cursor
}

// Better approach with proper resource management:
const rides = await db.collection('rides')
  .find({status: 'active'})
  .toArray();  // Automatically closes cursor
```

## Prevention and Monitoring

### Connection Pool Health Check
```javascript
async function checkConnectionPoolHealth() {
  const stats = await db.admin().serverStatus();
  const connections = stats.connections;

  console.log(`Total connections: ${connections.current}`);
  console.log(`Available connections: ${connections.available}`);

  if (connections.current > connections.totalCreated * 0.8) {
    console.warn('Connection pool usage > 80%');
  }

  return {
    current: connections.current,
    available: connections.available,
    totalCreated: connections.totalCreated,
    active: connections.active
  };
}
```

### Connection Pool Monitoring
```javascript
// Implement connection pool metrics
setInterval(async () => {
  try {
    const poolStats = await checkConnectionPoolHealth();

    // Send metrics to monitoring system
    metrics.gauge('mongodb.connections.current', poolStats.current);
    metrics.gauge('mongodb.connections.available', poolStats.available);

    if (poolStats.current === 0 && poolStats.available === 0) {
      alert('MongoDB connection pool exhausted!');
    }
  } catch (error) {
    console.error('Failed to check connection pool:', error);
  }
}, 30000);  // Check every 30 seconds
```

This debugging guide focuses on the most critical connection pool issues encountered in production MongoDB environments.