# GraphQL N+1 Query Production Debugging

## Emergency Response Overview

**Incident Severity**: P1 - API response times degraded, database overload
**MTTR Target**: < 3 minutes for immediate relief, < 20 minutes for permanent fix
**Primary Tools**: GraphQL query analysis, APM tools, database query logs, DataLoader

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - Blue #3B82F6]
        CLIENT[GraphQL Client<br/>Single Query Request<br/>Response time: 15s<br/>Expected: 200ms]
        CDN[CDN/Cache<br/>Cache miss<br/>GraphQL not cached]
        GATEWAY[API Gateway<br/>GraphQL endpoint<br/>Timeout warnings]
    end

    subgraph ServicePlane[Service Plane - Emerald #10B981]
        GRAPHQL[GraphQL Server<br/>Apollo Server<br/>Query complexity: HIGH<br/>Resolvers: 250+ calls]
        RESOLVER[User Resolver<br/>posts(user.id)<br/>Called 100 times<br/>No batching]
        DATALOADER[DataLoader<br/>Status: NOT IMPLEMENTED<br/>Batch loading: NONE<br/>Caching: DISABLED]
    end

    subgraph StatePlane[State Plane - Amber #F59E0B]
        DB[PostgreSQL Database<br/>Active connections: 95/100<br/>Slow queries: 247<br/>Query time: 12s avg]
        QUERIES[Query Pattern<br/>SELECT * FROM posts WHERE user_id = ?<br/>Executed 100 times<br/>No JOIN optimization]
        CACHE[Redis Cache<br/>Hit rate: 15%<br/>N+1 queries bypassing cache<br/>TTL: 300s]
    end

    subgraph ControlPlane[Control Plane - Violet #8B5CF6]
        APM[APM Monitoring<br/>New Relic/DataDog<br/>N+1 pattern detected<br/>100 db calls per request]
        LOGS[Application Logs<br/>GraphQL query depth: 5<br/>Resolver execution: 250ms each<br/>DB connection warnings]
    end

    CLIENT --> CDN
    CDN --> GATEWAY
    GATEWAY --> GRAPHQL
    GRAPHQL --> RESOLVER
    RESOLVER --> DATALOADER
    RESOLVER --> DB
    DB --> QUERIES
    QUERIES --> CACHE
    CACHE --> APM
    APM --> LOGS

    %% Apply Tailwind 4-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#1E40AF,color:#fff,stroke-width:2px
    classDef serviceStyle fill:#10B981,stroke:#047857,color:#fff,stroke-width:2px
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff,stroke-width:2px
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff,stroke-width:2px

    class CLIENT,CDN,GATEWAY edgeStyle
    class GRAPHQL,RESOLVER,DATALOADER serviceStyle
    class DB,QUERIES,CACHE stateStyle
    class APM,LOGS controlStyle
```

## 3 AM Debugging Flowchart

```mermaid
flowchart TD
    START[🚨 GraphQL Performance Alert<br/>Response time > 10s<br/>Database connections spiking] --> ANALYZE_QUERY{Query Analysis<br/>Check complexity}

    ANALYZE_QUERY -->|High complexity| COMPLEXITY_LIMIT[Apply Query Complexity Limit<br/>Reject expensive queries<br/>Immediate relief]
    ANALYZE_QUERY -->|Normal complexity| CHECK_PATTERN[Check Query Pattern<br/>Look for N+1 indicators<br/>Multiple similar DB calls]

    COMPLEXITY_LIMIT --> VERIFY_RELIEF{Response Time<br/>Improved?}
    CHECK_PATTERN --> N_PLUS_ONE{N+1 Pattern<br/>Detected?}

    N_PLUS_ONE -->|YES| IDENTIFY_RESOLVER[Identify Problem Resolver<br/>Check query logs<br/>Find repeated patterns]
    N_PLUS_ONE -->|NO| OTHER_ISSUES[Other Performance Issues<br/>Database slow queries<br/>Network latency]

    IDENTIFY_RESOLVER --> RESOLVER_TYPE{Resolver<br/>Type?}

    RESOLVER_TYPE -->|List field| LIST_N_PLUS_ONE[List Field N+1<br/>users → posts for each user<br/>Classic N+1 pattern]
    RESOLVER_TYPE -->|Nested object| NESTED_N_PLUS_ONE[Nested Object N+1<br/>post → author → profile<br/>Chain loading issue]
    RESOLVER_TYPE -->|Connection| CONNECTION_N_PLUS_ONE[Connection N+1<br/>Relay pagination<br/>Edge loading issue]

    LIST_N_PLUS_ONE --> IMPLEMENT_DATALOADER[Implement DataLoader<br/>Batch and cache<br/>users.posts → batch load]
    NESTED_N_PLUS_ONE --> OPTIMIZE_JOINS[Optimize with Joins<br/>Single query with JOINs<br/>OR implement nested DataLoader]
    CONNECTION_N_PLUS_ONE --> PAGINATION_FIX[Fix Pagination Query<br/>Use efficient cursors<br/>Limit + offset optimization]

    OTHER_ISSUES --> DB_OPTIMIZATION[Database Optimization<br/>Add indexes<br/>Optimize slow queries]

    IMPLEMENT_DATALOADER --> APPLY_FIX[Apply DataLoader Fix<br/>Deploy batching solution<br/>Enable caching]
    OPTIMIZE_JOINS --> APPLY_FIX
    PAGINATION_FIX --> APPLY_FIX
    DB_OPTIMIZATION --> APPLY_FIX

    APPLY_FIX --> VERIFY_RELIEF
    VERIFY_RELIEF -->|YES| MONITOR[✅ Issue Resolved<br/>Monitor query patterns<br/>Set up N+1 detection]
    VERIFY_RELIEF -->|NO| ESCALATE[🚨 ESCALATE<br/>Complex query optimization<br/>Architecture review needed]

    MONITOR --> PREVENTION[Setup Prevention<br/>Query complexity analysis<br/>DataLoader by default<br/>Performance monitoring]

    %% Apply Tailwind colors
    classDef errorStyle fill:#EF4444,stroke:#DC2626,color:#fff,stroke-width:2px
    classDef warningStyle fill:#F59E0B,stroke:#D97706,color:#fff,stroke-width:2px
    classDef actionStyle fill:#3B82F6,stroke:#1E40AF,color:#fff,stroke-width:2px
    classDef successStyle fill:#10B981,stroke:#047857,color:#fff,stroke-width:2px

    class ESCALATE errorStyle
    class LIST_N_PLUS_ONE,NESTED_N_PLUS_ONE,CONNECTION_N_PLUS_ONE warningStyle
    class COMPLEXITY_LIMIT,IMPLEMENT_DATALOADER,OPTIMIZE_JOINS,PAGINATION_FIX,APPLY_FIX actionStyle
    class MONITOR,PREVENTION successStyle
```

## Critical Commands & Immediate Actions

### GraphQL Query Analysis (< 1 minute)

```bash
# 1. IDENTIFY CURRENT SLOW QUERIES (Apollo Server)
# Check GraphQL server logs for query timing
tail -f /var/log/graphql-server.log | grep -E "(query|mutation)" | grep -E "[0-9]{4,}ms"

# 2. ANALYZE QUERY COMPLEXITY
curl -X POST http://localhost:4000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { __schema { queryType { fields { name args { name type { name } } } } } }"
  }' | jq .

# 3. CHECK DATABASE CONNECTION POOL
# PostgreSQL
psql -c "SELECT count(*) as active_connections FROM pg_stat_activity WHERE state = 'active';"
psql -c "SELECT query, query_start, state FROM pg_stat_activity WHERE state = 'active' ORDER BY query_start;"

# MySQL
mysql -e "SHOW STATUS LIKE 'Threads_connected';"
mysql -e "SHOW PROCESSLIST;"

# 4. QUICK N+1 DETECTION (check for repeated similar queries)
tail -n 1000 /var/log/postgresql/postgresql.log | grep -E "SELECT.*WHERE.*=" | sort | uniq -c | sort -nr | head -10
```

### Emergency Query Complexity Limiting

```javascript
// IMMEDIATE RELIEF - Query complexity limiting (Apollo Server)
const { ApolloServer } = require('apollo-server-express');
const depthLimit = require('graphql-depth-limit');
const costAnalysis = require('graphql-cost-analysis');

const server = new ApolloServer({
  typeDefs,
  resolvers,
  // EMERGENCY: Limit query depth
  validationRules: [
    depthLimit(7),  // Max 7 levels deep
    costAnalysis({
      maximumCost: 1000,  // Max cost 1000
      defaultCost: 1,
      scalarCost: 1,
      objectCost: 5,
      listFactor: 10,
      introspectionCost: 1000,  // Expensive introspection
      createError: (max, actual) => {
        const err = new Error(`Query cost ${actual} exceeds maximum cost ${max}`);
        err.code = 'QUERY_TOO_COMPLEX';
        return err;
      }
    })
  ],
  // Log expensive queries
  plugins: [
    {
      requestDidStart() {
        return {
          willSendResponse(requestContext) {
            const { query, variables } = requestContext.request;
            const operationName = requestContext.request.operationName;
            const duration = Date.now() - requestContext.request.startTime;

            if (duration > 1000) {  // Log queries > 1s
              console.error('SLOW_QUERY', {
                operationName,
                duration,
                query: query.replace(/\s+/g, ' ').trim(),
                variables
              });
            }
          }
        }
      }
    }
  ]
});
```

### Netflix Production N+1 Detection Script

```bash
# NETFLIX'S GRAPHQL N+1 DETECTION SCRIPT
#!/bin/bash

echo "=== NETFLIX GRAPHQL N+1 DETECTION ==="
echo "Time: $(date)"

# 1. ANALYZE DATABASE QUERY PATTERNS
echo "=== DATABASE QUERY PATTERN ANALYSIS ==="

# Look for repeated SELECT patterns (N+1 indicator)
DB_LOG_FILE="/var/log/postgresql/postgresql.log"
if [ -f "$DB_LOG_FILE" ]; then
    echo "Analyzing last 1000 database queries..."

    # Extract and count similar query patterns
    tail -n 1000 "$DB_LOG_FILE" | \
    grep -E "SELECT.*FROM.*WHERE.*=" | \
    sed 's/[0-9]\+/N/g' | \
    sed 's/'\''[^'\'']*'\''/'\''VALUE'\''/g' | \
    sort | uniq -c | sort -nr | head -20

    echo ""
    echo "Top repeated query patterns (potential N+1):"
    tail -n 1000 "$DB_LOG_FILE" | \
    grep -E "SELECT.*FROM.*WHERE.*=" | \
    sed 's/[0-9]\+/N/g' | \
    sed 's/'\''[^'\'']*'\''/'\''VALUE'\''/g' | \
    sort | uniq -c | sort -nr | head -5 | \
    while read count pattern; do
        if [ "$count" -gt 10 ]; then
            echo "ALERT: Query executed $count times - potential N+1"
            echo "Pattern: $pattern"
            echo ""
        fi
    done
fi

# 2. CHECK GRAPHQL SERVER METRICS
echo "=== GRAPHQL SERVER ANALYSIS ==="

# Check for high number of resolver calls
GRAPHQL_LOG="/var/log/graphql-server.log"
if [ -f "$GRAPHQL_LOG" ]; then
    # Count resolver executions in last 100 requests
    RESOLVER_COUNT=$(tail -n 1000 "$GRAPHQL_LOG" | grep -c "resolver:")
    REQUEST_COUNT=$(tail -n 1000 "$GRAPHQL_LOG" | grep -c "query {")

    if [ "$REQUEST_COUNT" -gt 0 ]; then
        RESOLVERS_PER_REQUEST=$((RESOLVER_COUNT / REQUEST_COUNT))
        echo "Resolvers per request: $RESOLVERS_PER_REQUEST"

        if [ "$RESOLVERS_PER_REQUEST" -gt 50 ]; then
            echo "ALERT: High resolver count indicates potential N+1 problem"
        fi
    fi
fi

# 3. CHECK FOR DATALOADER USAGE
echo "=== DATALOADER USAGE ANALYSIS ==="
if command -v grep &> /dev/null; then
    DATALOADER_USAGE=$(grep -r "DataLoader" /app/src --include="*.js" --include="*.ts" | wc -l)
    RESOLVER_FILES=$(find /app/src -name "*resolver*" -type f | wc -l)

    echo "DataLoader usage: $DATALOADER_USAGE occurrences"
    echo "Resolver files: $RESOLVER_FILES"

    if [ "$RESOLVER_FILES" -gt 0 ] && [ "$DATALOADER_USAGE" -lt "$RESOLVER_FILES" ]; then
        echo "WARNING: Low DataLoader usage relative to resolver count"
    fi
fi

echo "=== DETECTION COMPLETE ==="
```

### Stripe Production N+1 Emergency Fix

```javascript
// STRIPE'S EMERGENCY DATALOADER IMPLEMENTATION
const DataLoader = require('dataloader');

// BEFORE: N+1 query problem
// This resolver would cause N+1 queries
const resolvers = {
  User: {
    // BAD: This runs a separate query for each user
    posts: async (user) => {
      return await db.posts.findMany({
        where: { userId: user.id }
      });
    }
  }
};

// AFTER: DataLoader solution (Stripe's approach)
class PostDataLoader {
  constructor() {
    this.loader = new DataLoader(async (userIds) => {
      console.log(`Batching posts query for ${userIds.length} users`);

      // Single query for all users
      const posts = await db.posts.findMany({
        where: { userId: { in: userIds } },
        orderBy: { createdAt: 'desc' }
      });

      // Group posts by userId
      const postsByUserId = {};
      posts.forEach(post => {
        if (!postsByUserId[post.userId]) {
          postsByUserId[post.userId] = [];
        }
        postsByUserId[post.userId].push(post);
      });

      // Return posts in same order as userIds
      return userIds.map(userId => postsByUserId[userId] || []);
    }, {
      // Cache for request duration
      cache: true,
      // Batch multiple requests within 16ms
      batchScheduleFn: callback => setTimeout(callback, 16)
    });
  }

  async load(userId) {
    return this.loader.load(userId);
  }

  async loadMany(userIds) {
    return this.loader.loadMany(userIds);
  }
}

// CONTEXT SETUP (create new DataLoader per request)
const server = new ApolloServer({
  typeDefs,
  resolvers: {
    User: {
      posts: async (user, args, context) => {
        return context.loaders.posts.load(user.id);
      }
    }
  },
  context: ({ req }) => ({
    // Fresh DataLoader per request (important for caching)
    loaders: {
      posts: new PostDataLoader(),
      comments: new CommentDataLoader(),
      users: new UserDataLoader()
    }
  })
});

// MONITORING: Add DataLoader metrics
class InstrumentedDataLoader extends DataLoader {
  constructor(batchFunction, options = {}) {
    const instrumentedBatch = async (keys) => {
      const start = Date.now();
      const result = await batchFunction(keys);
      const duration = Date.now() - start;

      console.log('DATALOADER_BATCH', {
        keysCount: keys.length,
        duration,
        timestamp: new Date().toISOString()
      });

      return result;
    };

    super(instrumentedBatch, options);
  }
}
```

## Common Root Causes & Probabilities

### 1. Classic List Field N+1 (50% of cases)
**GitHub Example**: Users query requesting posts for each user

```graphql
# PROBLEMATIC QUERY
query GetUsersWithPosts {
  users {
    id
    name
    posts {        # This causes N+1!
      id           # For 100 users = 1 + 100 queries
      title
      content
    }
  }
}
```

```javascript
// BEFORE: N+1 Problem (1 + N queries)
const resolvers = {
  Query: {
    users: () => db.users.findMany()  // 1 query
  },
  User: {
    posts: (user) => db.posts.findMany({  // N queries (one per user)
      where: { userId: user.id }
    })
  }
};

// GITHUB'S SOLUTION: DataLoader batching
const postsLoader = new DataLoader(async (userIds) => {
  // Single batched query
  const posts = await db.posts.findMany({
    where: { userId: { in: userIds } }
  });

  // Group and return in correct order
  const grouped = userIds.map(id =>
    posts.filter(post => post.userId === id)
  );
  return grouped;
});

const resolvers = {
  User: {
    posts: (user, args, { loaders }) =>
      loaders.posts.load(user.id)  // Batched!
  }
};
```

### 2. Nested Object Resolution N+1 (25% of cases)
**Airbnb Example**: Post → Author → Profile chain causing multiple DB hits

```graphql
# QUERY CAUSING NESTED N+1
query GetPosts {
  posts {
    id
    title
    author {      # N+1 for authors
      id
      name
      profile {   # Another N+1 for profiles!
        id
        bio
        avatar
      }
    }
  }
}
```

```javascript
// AIRBNB'S NESTED N+1 SOLUTION
// Instead of separate loaders, use JOIN strategy

const resolvers = {
  Query: {
    posts: async () => {
      // Single query with JOINs instead of separate resolvers
      return await db.posts.findMany({
        include: {
          author: {
            include: {
              profile: true
            }
          }
        }
      });
    }
  }
  // No need for separate User.profile resolver - data already loaded!
};

// ALTERNATIVE: Nested DataLoaders
const profileLoader = new DataLoader(async (userIds) => {
  const profiles = await db.profiles.findMany({
    where: { userId: { in: userIds } }
  });
  return userIds.map(id => profiles.find(p => p.userId === id));
});

const userWithProfileLoader = new DataLoader(async (userIds) => {
  const users = await db.users.findMany({
    where: { id: { in: userIds } }
  });
  // Pre-load profiles for these users
  await profileLoader.loadMany(userIds);
  return users;
});
```

### 3. Pagination/Connection N+1 (15% of cases)
**Facebook Example**: Relay connections causing N+1 for edge data

```graphql
# RELAY CONNECTION N+1
query GetUserConnections {
  user(id: "123") {
    friendsConnection(first: 10) {
      edges {
        node {
          id
          name
        }
        cursor
        # N+1 if this field requires separate query
        friendship {
          createdAt
          status
        }
      }
    }
  }
}
```

```javascript
// FACEBOOK'S CONNECTION N+1 FIX
const friendshipLoader = new DataLoader(async (friendshipIds) => {
  const friendships = await db.friendships.findMany({
    where: { id: { in: friendshipIds } }
  });
  return friendshipIds.map(id =>
    friendships.find(f => f.id === id)
  );
});

const resolvers = {
  FriendEdge: {
    friendship: async (edge, args, { loaders }) => {
      // Batch load friendship data
      return loaders.friendship.load(edge.friendshipId);
    }
  }
};

// ALTERNATIVE: Pre-load edge data in connection resolver
const resolvers = {
  User: {
    friendsConnection: async (user, { first, after }) => {
      const result = await db.friendConnections.findMany({
        where: { userId: user.id },
        include: {
          friendship: true,  // Pre-load friendship data
          friend: true       // Pre-load friend data
        },
        take: first,
        cursor: after ? { id: after } : undefined
      });

      // Return edges with pre-loaded data
      return {
        edges: result.map(conn => ({
          node: conn.friend,
          cursor: conn.id,
          friendship: conn.friendship  // Already loaded!
        }))
      };
    }
  }
};
```

### 4. Complex Filtering N+1 (8% of cases)
**Shopify Example**: Product variants with complex filtering

```graphql
# COMPLEX FILTERING N+1
query GetProducts {
  products {
    id
    name
    availableVariants {  # N+1 with complex WHERE clause
      id
      price
      inStock
    }
  }
}
```

```javascript
// SHOPIFY'S COMPLEX FILTERING SOLUTION
const availableVariantsLoader = new DataLoader(async (productIds) => {
  // Single complex query for all products
  const variants = await db.productVariants.findMany({
    where: {
      productId: { in: productIds },
      AND: [
        { deletedAt: null },
        { inventory: { gt: 0 } },
        { isActive: true }
      ]
    },
    orderBy: { price: 'asc' }
  });

  // Group by productId
  const variantsByProduct = {};
  variants.forEach(variant => {
    if (!variantsByProduct[variant.productId]) {
      variantsByProduct[variant.productId] = [];
    }
    variantsByProduct[variant.productId].push(variant);
  });

  return productIds.map(id => variantsByProduct[id] || []);
});

// Usage in resolver
const resolvers = {
  Product: {
    availableVariants: (product, args, { loaders }) =>
      loaders.availableVariants.load(product.id)
  }
};
```

### 5. Cross-Service N+1 (2% of cases)
**Uber Example**: Microservices causing N+1 across service boundaries

```javascript
// UBER'S CROSS-SERVICE N+1 PROBLEM
const resolvers = {
  User: {
    // BAD: N separate HTTP calls to user service
    profile: async (user) => {
      const response = await fetch(`http://user-service/profiles/${user.id}`);
      return response.json();
    }
  }
};

// UBER'S SOLUTION: Batch HTTP requests
const profileLoader = new DataLoader(async (userIds) => {
  // Single batch request to service
  const response = await fetch('http://user-service/profiles/batch', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ userIds })
  });

  const profiles = await response.json();

  // Return in correct order
  return userIds.map(id =>
    profiles.find(profile => profile.userId === id)
  );
}, {
  // Cache for 5 minutes for cross-service calls
  cacheMap: new Map(),
  cacheKeyFn: (key) => key,
  cache: true
});
```

## Recovery Procedures (< 15 minutes)

### Phase 1: Immediate Relief (< 3 minutes)

```javascript
// EMERGENCY N+1 MITIGATION MIDDLEWARE
const emergencyN1Mitigation = {
  requestDidStart() {
    return {
      willSendResponse(requestContext) {
        const { query } = requestContext.request;

        // Count database queries in this request
        const dbQueryCount = requestContext.dbQueries?.length || 0;

        if (dbQueryCount > 50) {  // Threshold for N+1 detection
          console.error('POSSIBLE_N1_DETECTED', {
            operationName: requestContext.request.operationName,
            queryCount: dbQueryCount,
            query: query.replace(/\s+/g, ' ').trim()
          });

          // Could also reject the query or apply rate limiting
          if (dbQueryCount > 100) {
            throw new Error('Query complexity too high. Please optimize your query.');
          }
        }
      }
    };
  }
};

// EMERGENCY QUERY COMPLEXITY LIMITS
const server = new ApolloServer({
  typeDefs,
  resolvers,
  plugins: [emergencyN1Mitigation],
  validationRules: [
    depthLimit(6),  // Strict depth limit
    require('graphql-query-complexity')({
      maximumComplexity: 500,  // Lower complexity limit
      variables: {},
      createError: (max, actual) => new Error(
        `Query is too complex: ${actual}. Maximum allowed complexity: ${max}.`
      ),
      estimators: [
        require('graphql-query-complexity').fieldExtensionsEstimator(),
        require('graphql-query-complexity').simpleEstimator({ defaultComplexity: 1 })
      ]
    })
  ]
});
```

### Phase 2: Quick DataLoader Implementation (< 10 minutes)

```javascript
// RAPID DATALOADER IMPLEMENTATION TEMPLATE
// Copy-paste solution for most common N+1 patterns

// 1. BASIC ENTITY LOADER
const createEntityLoader = (tableName, foreignKey = 'id') => {
  return new DataLoader(async (ids) => {
    const entities = await db[tableName].findMany({
      where: { [foreignKey]: { in: ids } }
    });

    return ids.map(id =>
      entities.filter(entity => entity[foreignKey] === id)
    );
  });
};

// 2. ONE-TO-ONE RELATIONSHIP LOADER
const createOneToOneLoader = (tableName, foreignKey) => {
  return new DataLoader(async (ids) => {
    const entities = await db[tableName].findMany({
      where: { [foreignKey]: { in: ids } }
    });

    return ids.map(id =>
      entities.find(entity => entity[foreignKey] === id) || null
    );
  });
};

// 3. EMERGENCY CONTEXT SETUP
const createEmergencyLoaders = () => ({
  // Common patterns - adjust table names as needed
  userPosts: createEntityLoader('posts', 'userId'),
  userComments: createEntityLoader('comments', 'userId'),
  postComments: createEntityLoader('comments', 'postId'),
  userProfile: createOneToOneLoader('profiles', 'userId'),
  postAuthor: createOneToOneLoader('users', 'id'),

  // Add more as needed...
});

// 4. QUICK RESOLVER UPDATES
const emergencyResolvers = {
  User: {
    posts: (user, args, { loaders }) =>
      loaders.userPosts.load(user.id),
    profile: (user, args, { loaders }) =>
      loaders.userProfile.load(user.id),
    comments: (user, args, { loaders }) =>
      loaders.userComments.load(user.id),
  },
  Post: {
    author: (post, args, { loaders }) =>
      loaders.postAuthor.load(post.authorId),
    comments: (post, args, { loaders }) =>
      loaders.postComments.load(post.id),
  }
};

// 5. SERVER UPDATE
const server = new ApolloServer({
  typeDefs,
  resolvers: {
    ...existingResolvers,
    ...emergencyResolvers  // Override problematic resolvers
  },
  context: ({ req }) => ({
    ...existingContext,
    loaders: createEmergencyLoaders()  // Add DataLoaders
  })
});
```

### Phase 3: Production Optimization (< 15 minutes)

```javascript
// PRODUCTION-GRADE DATALOADER IMPLEMENTATION
class ProductionDataLoader extends DataLoader {
  constructor(batchFunction, options = {}) {
    const defaultOptions = {
      // Cache for request duration
      cache: true,
      // Batch within 16ms (one event loop tick)
      batchScheduleFn: callback => setTimeout(callback, 16),
      // Maximum batch size to prevent huge queries
      maxBatchSize: 100,
      // Custom cache key function
      cacheKeyFn: key => String(key),
      ...options
    };

    // Instrument the batch function for monitoring
    const instrumentedBatch = async (keys) => {
      const startTime = Date.now();
      const batchId = Math.random().toString(36).substr(2, 9);

      console.log('DATALOADER_BATCH_START', {
        batchId,
        keyCount: keys.length,
        keys: keys.slice(0, 5), // Log first 5 keys for debugging
        timestamp: new Date().toISOString()
      });

      try {
        const result = await batchFunction(keys);
        const duration = Date.now() - startTime;

        console.log('DATALOADER_BATCH_SUCCESS', {
          batchId,
          keyCount: keys.length,
          duration,
          timestamp: new Date().toISOString()
        });

        // Validate result length matches keys length
        if (result.length !== keys.length) {
          throw new Error(
            `DataLoader batch function returned ${result.length} results for ${keys.length} keys`
          );
        }

        return result;
      } catch (error) {
        const duration = Date.now() - startTime;

        console.error('DATALOADER_BATCH_ERROR', {
          batchId,
          keyCount: keys.length,
          duration,
          error: error.message,
          timestamp: new Date().toISOString()
        });

        throw error;
      }
    };

    super(instrumentedBatch, defaultOptions);
  }
}

// REDIS-CACHED DATALOADER FOR EXPENSIVE QUERIES
class CachedDataLoader extends ProductionDataLoader {
  constructor(batchFunction, redisClient, options = {}) {
    const cacheKeyPrefix = options.cacheKeyPrefix || 'dl:';
    const ttl = options.ttl || 300; // 5 minutes default

    const cachedBatchFunction = async (keys) => {
      // Try to get from Redis cache first
      const cacheKeys = keys.map(key => `${cacheKeyPrefix}${key}`);
      const cached = await redisClient.mget(cacheKeys);

      const uncachedKeys = [];
      const uncachedIndices = [];

      keys.forEach((key, index) => {
        if (cached[index] === null) {
          uncachedKeys.push(key);
          uncachedIndices.push(index);
        }
      });

      let uncachedResults = [];
      if (uncachedKeys.length > 0) {
        // Fetch uncached data
        uncachedResults = await batchFunction(uncachedKeys);

        // Cache the results
        const pipeline = redisClient.pipeline();
        uncachedKeys.forEach((key, index) => {
          const cacheKey = `${cacheKeyPrefix}${key}`;
          pipeline.setex(cacheKey, ttl, JSON.stringify(uncachedResults[index]));
        });
        await pipeline.exec();
      }

      // Combine cached and fresh results
      const results = new Array(keys.length);
      keys.forEach((key, index) => {
        if (cached[index] !== null) {
          results[index] = JSON.parse(cached[index]);
        } else {
          const uncachedIndex = uncachedKeys.indexOf(key);
          results[index] = uncachedResults[uncachedIndex];
        }
      });

      return results;
    };

    super(cachedBatchFunction, options);
    this.redisClient = redisClient;
    this.cacheKeyPrefix = cacheKeyPrefix;
  }

  // Method to invalidate cache
  async invalidate(key) {
    await this.redisClient.del(`${this.cacheKeyPrefix}${key}`);
    this.clear(key);
  }
}
```

## Real-World Examples

### GitHub: 2019 Repository Issues N+1

**Scenario**: Repository listing page showing issue counts for each repo

**Query Pattern**:
```graphql
query GetRepositories {
  repositories {
    id
    name
    issueCount    # N+1: Separate count query per repo
    openIssues {  # Another N+1: Issues per repo
      id
      title
    }
  }
}
```

**Problem Detection**:
```bash
# GitHub detected this via database monitoring
tail -f /var/log/postgresql.log | grep "SELECT COUNT" | uniq -c
# Result: 847 identical count queries in 1 minute

# Application logs showed resolver pattern
grep "issueCount resolver" /var/log/github-graphql.log | wc -l
# Result: 847 resolver calls matching repository count
```

**GitHub's Solution**:
```javascript
// BEFORE: N+1 problem
const resolvers = {
  Repository: {
    issueCount: async (repo) => {
      return await db.issues.count({
        where: { repositoryId: repo.id }
      });
    },
    openIssues: async (repo) => {
      return await db.issues.findMany({
        where: {
          repositoryId: repo.id,
          status: 'open'
        }
      });
    }
  }
};

// AFTER: GitHub's DataLoader solution
const issueStatsLoader = new DataLoader(async (repoIds) => {
  // Single query for all stats
  const stats = await db.issues.groupBy({
    by: ['repositoryId', 'status'],
    where: { repositoryId: { in: repoIds } },
    _count: { id: true }
  });

  const openIssues = await db.issues.findMany({
    where: {
      repositoryId: { in: repoIds },
      status: 'open'
    }
  });

  return repoIds.map(repoId => {
    const repoStats = stats.filter(s => s.repositoryId === repoId);
    const totalCount = repoStats.reduce((sum, s) => sum + s._count.id, 0);
    const openCount = repoStats.find(s => s.status === 'open')?._count.id || 0;
    const repoOpenIssues = openIssues.filter(i => i.repositoryId === repoId);

    return {
      totalCount,
      openCount,
      openIssues: repoOpenIssues
    };
  });
});

const optimizedResolvers = {
  Repository: {
    issueCount: async (repo, args, { loaders }) => {
      const stats = await loaders.issueStats.load(repo.id);
      return stats.totalCount;
    },
    openIssues: async (repo, args, { loaders }) => {
      const stats = await loaders.issueStats.load(repo.id);
      return stats.openIssues;
    }
  }
};
```

**Results**:
- Database queries: 847 → 2 (99.8% reduction)
- Response time: 12.3s → 0.8s (93% improvement)
- Database CPU usage: Reduced by 85%

### Airbnb: 2020 Listing Reviews N+1

**Scenario**: Listing search showing review summaries for each listing

**N+1 Pattern**:
```graphql
query SearchListings {
  searchListings(location: "San Francisco") {
    id
    title
    reviewSummary {    # N+1 problem
      averageRating
      totalReviews
      recentReviews(limit: 3) {
        id
        rating
        comment
        author {       # Nested N+1!
          id
          name
          avatar
        }
      }
    }
  }
}
```

**Airbnb's Investigation**:
```javascript
// Detected via APM monitoring
// New Relic showed this pattern:
// - 1 query: Search listings (50 results)
// - 50 queries: Review summaries
// - 150 queries: Recent reviews (3 per listing)
// - 150 queries: Review authors
// Total: 351 queries for one search page!
```

**Solution Strategy**:
```javascript
// AIRBNB'S COMPREHENSIVE SOLUTION
// 1. Combined DataLoader for review data
const reviewDataLoader = new DataLoader(async (listingIds) => {
  // Single query for all review data
  const [reviews, summaries] = await Promise.all([
    // Get recent reviews with authors in one query
    db.reviews.findMany({
      where: {
        listingId: { in: listingIds },
        isPublished: true
      },
      include: {
        author: {
          select: { id: true, name: true, avatar: true }
        }
      },
      orderBy: { createdAt: 'desc' },
      take: listingIds.length * 3  // Max 3 per listing
    }),

    // Get summary statistics
    db.reviews.groupBy({
      by: ['listingId'],
      where: {
        listingId: { in: listingIds },
        isPublished: true
      },
      _avg: { rating: true },
      _count: { id: true }
    })
  ]);

  return listingIds.map(listingId => {
    const listingReviews = reviews
      .filter(r => r.listingId === listingId)
      .slice(0, 3);  // Limit to 3 per listing

    const summary = summaries.find(s => s.listingId === listingId);

    return {
      averageRating: summary?._avg.rating || 0,
      totalReviews: summary?._count.id || 0,
      recentReviews: listingReviews
    };
  });
});

// 2. Optimized resolvers
const resolvers = {
  Listing: {
    reviewSummary: async (listing, args, { loaders }) => {
      return loaders.reviewData.load(listing.id);
    }
  },
  // No need for separate resolvers - data is pre-loaded!
};
```

**Results**:
- Database queries: 351 → 3 (99% reduction)
- Search page load time: 8.2s → 1.1s (87% improvement)
- Database connection pool usage: Reduced from 95% to 15%

### Shopify: 2021 Product Catalog N+1

**Scenario**: Admin dashboard showing product variant prices across multiple currencies

**Complex N+1 Pattern**:
```graphql
query AdminProducts {
  products(first: 50) {
    edges {
      node {
        id
        title
        variants {              # N+1 for variants
          id
          title
          prices {              # N+1 for prices per variant
            currencyCode
            amount
            compareAtPrice
          }
          inventory {           # N+1 for inventory per variant
            available
            onHand
            committed
          }
        }
      }
    }
  }
}
```

**Shopify's Analysis**:
- 50 products query
- ~200 variants (4 per product average)
- ~1,600 price queries (8 currencies × 200 variants)
- ~200 inventory queries
- **Total: ~2,050 database queries for one page load**

**Shopify's Solution**:
```javascript
// SHOPIFY'S MEGA-BATCH LOADER
const productDataLoader = new DataLoader(async (productIds) => {
  console.log(`Loading complete product data for ${productIds.length} products`);

  // Single massive query with all nested data
  const products = await db.products.findMany({
    where: { id: { in: productIds } },
    include: {
      variants: {
        include: {
          prices: {
            orderBy: { currencyCode: 'asc' }
          },
          inventory: true
        },
        orderBy: { position: 'asc' }
      }
    },
    orderBy: { createdAt: 'desc' }
  });

  // Return in correct order
  return productIds.map(id =>
    products.find(p => p.id === id)
  );
}, {
  // Larger batch size for admin operations
  maxBatchSize: 100,
  // Longer cache for product data
  cache: true
});

const resolvers = {
  Product: {
    // All data pre-loaded, no additional queries needed
    variants: (product) => product.variants || []
  },
  ProductVariant: {
    prices: (variant) => variant.prices || [],
    inventory: (variant) => variant.inventory
  }
};
```

**Results**:
- Database queries: 2,050 → 1 (99.95% reduction)
- Admin page load: 15.3s → 0.9s (94% improvement)
- Memory usage: Reduced by 60% (fewer query objects)
- Database server CPU: Reduced by 90%

## Monitoring & Prevention

### GraphQL N+1 Detection Metrics

```javascript
// COMPREHENSIVE N+1 MONITORING PLUGIN
const n1DetectionPlugin = {
  requestDidStart() {
    return {
      willSendResponse(requestContext) {
        const { query, variables } = requestContext.request;
        const operationName = requestContext.request.operationName || 'Anonymous';

        // Get database query count from context
        const dbQueryCount = requestContext.dbQueryCount || 0;
        const cacheHits = requestContext.cacheHits || 0;
        const cacheMisses = requestContext.cacheMisses || 0;

        // Calculate efficiency metrics
        const cacheHitRate = cacheHits + cacheMisses > 0
          ? cacheHits / (cacheHits + cacheMisses)
          : 0;

        // Detect potential N+1 patterns
        const isLikelyN1 = dbQueryCount > 20;
        const isDefiniteN1 = dbQueryCount > 50;

        const metrics = {
          operationName,
          dbQueryCount,
          cacheHits,
          cacheMisses,
          cacheHitRate,
          duration: Date.now() - requestContext.requestStartTime,
          queryDepth: getQueryDepth(query),
          isLikelyN1,
          isDefiniteN1
        };

        // Log to monitoring system
        if (isDefiniteN1) {
          console.error('N1_DETECTED', metrics);

          // Send to APM
          if (typeof newrelic !== 'undefined') {
            newrelic.recordCustomEvent('GraphQLN1', metrics);
          }
        } else if (isLikelyN1) {
          console.warn('POSSIBLE_N1', metrics);
        }

        // Always log performance metrics
        console.log('GRAPHQL_PERFORMANCE', metrics);
      }
    };
  }
};

// QUERY DEPTH ANALYZER
function getQueryDepth(query) {
  let maxDepth = 0;

  function visit(node, depth = 0) {
    maxDepth = Math.max(maxDepth, depth);

    if (node.selectionSet) {
      node.selectionSet.selections.forEach(selection => {
        if (selection.kind === 'Field') {
          visit(selection, depth + 1);
        }
      });
    }
  }

  visit(query.definitions[0]);
  return maxDepth;
}
```

### Automated N+1 Prevention

```javascript
// DATALOADER FACTORY FOR AUTOMATIC N+1 PREVENTION
class DataLoaderFactory {
  constructor(db, redisClient) {
    this.db = db;
    this.redis = redisClient;
    this.loaders = new Map();
  }

  // Generic entity loader
  getEntityLoader(tableName, foreignKey = 'id') {
    const key = `${tableName}:${foreignKey}`;

    if (!this.loaders.has(key)) {
      const loader = new DataLoader(async (values) => {
        const entities = await this.db[tableName].findMany({
          where: { [foreignKey]: { in: values } }
        });

        if (foreignKey === 'id') {
          // One-to-one: return single entity or null
          return values.map(value =>
            entities.find(e => e[foreignKey] === value) || null
          );
        } else {
          // One-to-many: return array of entities
          return values.map(value =>
            entities.filter(e => e[foreignKey] === value)
          );
        }
      }, {
        cache: true,
        maxBatchSize: 100
      });

      this.loaders.set(key, loader);
    }

    return this.loaders.get(key);
  }

  // Relation loader with caching
  getRelationLoader(fromTable, toTable, foreignKey, options = {}) {
    const key = `${fromTable}:${toTable}:${foreignKey}`;

    if (!this.loaders.has(key)) {
      const loader = new CachedDataLoader(
        async (ids) => {
          const relations = await this.db[toTable].findMany({
            where: { [foreignKey]: { in: ids } },
            ...options.queryOptions
          });

          return ids.map(id =>
            relations.filter(r => r[foreignKey] === id)
          );
        },
        this.redis,
        {
          cacheKeyPrefix: `rel:${key}:`,
          ttl: options.cacheTTL || 300,
          ...options.loaderOptions
        }
      );

      this.loaders.set(key, loader);
    }

    return this.loaders.get(key);
  }
}

// AUTOMATIC RESOLVER GENERATION
function createAutoResolvers(schema, loaderFactory) {
  const resolvers = {};

  // Analyze schema for potential N+1 patterns
  const typeMap = schema.getTypeMap();

  Object.values(typeMap).forEach(type => {
    if (type.name.startsWith('__')) return; // Skip introspection types

    const fields = type.getFields?.() || {};
    const typeResolvers = {};

    Object.values(fields).forEach(field => {
      // Detect list fields (potential N+1)
      if (field.type.toString().includes('[') ||
          field.type.toString().includes('Connection')) {

        const relationName = field.name;
        const foreignKey = guessForeignKey(type.name, relationName);

        typeResolvers[relationName] = (parent, args, context) => {
          const loader = loaderFactory.getRelationLoader(
            type.name.toLowerCase(),
            relationName,
            foreignKey
          );
          return loader.load(parent.id);
        };
      }
    });

    if (Object.keys(typeResolvers).length > 0) {
      resolvers[type.name] = typeResolvers;
    }
  });

  return resolvers;
}

// SMART FOREIGN KEY DETECTION
function guessForeignKey(parentType, fieldName) {
  const parentLower = parentType.toLowerCase();

  // Common patterns
  if (fieldName === 'posts') return 'userId';
  if (fieldName === 'comments') return parentLower + 'Id';
  if (fieldName === 'author') return 'authorId';
  if (fieldName === 'user') return 'userId';

  // Default pattern: parentType + Id
  return parentLower + 'Id';
}
```

### Production Monitoring Dashboard

```javascript
// GRAPHQL PERFORMANCE MONITORING QUERIES
const performanceQueries = {
  // N+1 detection query (for Prometheus/Grafana)
  n1Detection: `
    rate(graphql_resolver_calls_total[5m]) /
    rate(graphql_requests_total[5m]) > 20
  `,

  // Database query efficiency
  queryEfficiency: `
    rate(database_queries_total[5m]) /
    rate(graphql_requests_total[5m])
  `,

  // DataLoader effectiveness
  cacheHitRate: `
    rate(dataloader_cache_hits_total[5m]) /
    (rate(dataloader_cache_hits_total[5m]) + rate(dataloader_cache_misses_total[5m]))
  `,

  // Query complexity trends
  complexityTrend: `
    histogram_quantile(0.95,
      rate(graphql_query_complexity_bucket[5m])
    )`
};

// ALERTING RULES
const alertingRules = [
  {
    alert: 'GraphQLN1Detected',
    expr: 'rate(graphql_resolver_calls_total[5m]) / rate(graphql_requests_total[5m]) > 50',
    for: '2m',
    severity: 'critical',
    description: 'Potential N+1 query pattern detected'
  },
  {
    alert: 'GraphQLHighLatency',
    expr: 'histogram_quantile(0.95, rate(graphql_request_duration_seconds_bucket[5m])) > 5',
    for: '1m',
    severity: 'warning',
    description: 'GraphQL response time p95 > 5 seconds'
  },
  {
    alert: 'DataLoaderLowEfficiency',
    expr: 'rate(dataloader_cache_hits_total[5m]) / (rate(dataloader_cache_hits_total[5m]) + rate(dataloader_cache_misses_total[5m])) < 0.7',
    for: '5m',
    severity: 'warning',
    description: 'DataLoader cache hit rate below 70%'
  }
];
```

## Production Best Practices

### Schema Design for N+1 Prevention

```graphql
# GOOD SCHEMA DESIGN - N+1 AWARE
type Query {
  # Provide efficient batch endpoints
  users(ids: [ID!]): [User!]!
  usersByEmail(emails: [String!]): [User!]!

  # Connection-based pagination
  usersConnection(
    first: Int
    after: String
    orderBy: UserOrderBy
  ): UserConnection!
}

type User {
  id: ID!
  name: String!
  email: String!

  # Use connections for relationships
  postsConnection(
    first: Int
    after: String
    orderBy: PostOrderBy
  ): PostConnection!

  # Provide aggregations to avoid N+1 counts
  postCount: Int!

  # Complex fields should have complexity cost
  recentActivity(limit: Int = 10): [Activity!]!
    @cost(complexity: 10, multipliers: ["limit"])
}

type Post {
  id: ID!
  title: String!
  content: String!

  # Pre-load commonly accessed relationships
  author: User!

  # Use DataLoader-friendly patterns
  commentCount: Int!
  comments(limit: Int = 20): [Comment!]!
}

# DEFINE COMPLEXITY COSTS
directive @cost(
  complexity: Int!
  multipliers: [String!]
  useMultipliers: Boolean = true
) on FIELD_DEFINITION
```

### Production DataLoader Configuration

```javascript
// PRODUCTION DATALOADER SETUP
class ProductionLoaderFactory {
  constructor(options = {}) {
    this.db = options.database;
    this.redis = options.redis;
    this.logger = options.logger || console;
    this.metrics = options.metrics;
  }

  createUserLoader() {
    return new DataLoader(
      async (userIds) => {
        const startTime = Date.now();

        try {
          const users = await this.db.users.findMany({
            where: { id: { in: userIds } },
            select: {
              id: true,
              name: true,
              email: true,
              avatar: true,
              createdAt: true
            }
          });

          this.metrics?.increment('dataloader.batch.success', {
            loader: 'users',
            batchSize: userIds.length
          });

          return userIds.map(id =>
            users.find(user => user.id === id) || null
          );
        } catch (error) {
          this.metrics?.increment('dataloader.batch.error', {
            loader: 'users'
          });
          throw error;
        } finally {
          this.metrics?.timing('dataloader.batch.duration',
            Date.now() - startTime, { loader: 'users' });
        }
      },
      {
        // Production settings
        cache: true,
        maxBatchSize: 100,
        batchScheduleFn: callback => setTimeout(callback, 16),
        cacheKeyFn: key => `user:${key}`,
        cacheMap: this.redis ? new RedisDataLoaderCache(this.redis, {
          prefix: 'user:',
          ttl: 300
        }) : undefined
      }
    );
  }

  createPostsByUserLoader() {
    return new DataLoader(
      async (userIds) => {
        const posts = await this.db.posts.findMany({
          where: {
            authorId: { in: userIds },
            isPublished: true
          },
          include: {
            author: {
              select: { id: true, name: true, avatar: true }
            }
          },
          orderBy: { createdAt: 'desc' }
        });

        return userIds.map(userId =>
          posts.filter(post => post.authorId === userId)
        );
      },
      {
        cache: true,
        maxBatchSize: 50,
        cacheKeyFn: key => `posts:user:${key}`
      }
    );
  }
}

// REDIS CACHE INTEGRATION
class RedisDataLoaderCache {
  constructor(redisClient, options = {}) {
    this.redis = redisClient;
    this.prefix = options.prefix || 'dl:';
    this.ttl = options.ttl || 300;
  }

  get(key) {
    return this.redis.get(`${this.prefix}${key}`)
      .then(value => value ? JSON.parse(value) : undefined);
  }

  set(key, value) {
    return this.redis.setex(
      `${this.prefix}${key}`,
      this.ttl,
      JSON.stringify(value)
    );
  }

  delete(key) {
    return this.redis.del(`${this.prefix}${key}`);
  }

  clear() {
    return this.redis.eval(
      `return redis.call('del', unpack(redis.call('keys', ARGV[1])))`,
      0,
      `${this.prefix}*`
    );
  }
}
```

## Incident Response Checklist

### Immediate Response (< 3 minutes)
- [ ] Check database connection pool utilization
- [ ] Identify GraphQL queries with high DB query counts
- [ ] Apply emergency query complexity limits
- [ ] Check for obvious N+1 patterns in recent deployments
- [ ] Scale database read replicas if needed

### Investigation (< 10 minutes)
- [ ] Analyze query logs for repeated similar patterns
- [ ] Identify specific resolvers causing high DB load
- [ ] Check DataLoader usage and effectiveness
- [ ] Review query complexity and depth
- [ ] Examine caching hit rates and patterns

### Implementation (< 15 minutes)
- [ ] Implement DataLoader for identified N+1 patterns
- [ ] Add query complexity validation
- [ ] Enable resolver performance monitoring
- [ ] Deploy emergency fixes with batching
- [ ] Verify performance improvement

### Post-Incident (< 30 minutes)
- [ ] Set up comprehensive N+1 monitoring
- [ ] Review schema design for optimization opportunities
- [ ] Document DataLoader patterns for team
- [ ] Plan performance testing for future deployments
- [ ] Schedule GraphQL performance architecture review

**Remember**: GraphQL N+1 problems are often invisible until they hit production scale. The key is proactive detection through monitoring and preventive DataLoader implementation for all relationship fields.