# SQL to NoSQL Database Migration Playbook

## Executive Summary

**Migration Type**: Database Architecture Modernization  
**Timeline**: 16-20 weeks  
**Risk Level**: High  
**Downtime**: Minimal (with dual-write strategy)  
**Cost Impact**: 30-50% reduction in database costs  
**Team Size**: 4-5 engineers + 1 DBA + 1 DevOps  

Migrate from traditional relational databases to NoSQL for improved scalability, performance, and flexibility while maintaining data consistency.

## Current State vs Target State

### Current State: Traditional SQL Database

```mermaid
graph TB
    subgraph CurrentSQL[Current SQL Architecture]
        APP[Application Layer<br/>Spring Boot + JPA<br/>Complex ORM mappings<br/>N+1 query problems]
        
        POSTGRES[(PostgreSQL 13<br/>Single master instance<br/>Read replicas (2)<br/>Complex JOIN operations<br/>ACID transactions)]
        
        REDIS[Redis Cache<br/>Application-level caching<br/>Cache invalidation issues<br/>Memory limitations]
        
        BACKUP[Database Backups<br/>Daily full backups<br/>Point-in-time recovery<br/>Long restore times]
    end
    
    APP --> POSTGRES
    APP --> REDIS
    POSTGRES --> BACKUP
    
    classDef sqlStyle fill:#ff9800,stroke:#e65100,color:#fff
    class APP,POSTGRES,REDIS,BACKUP sqlStyle
```

**Current State Issues:**
- **Scalability Limits**: Vertical scaling only
- **Performance**: Complex JOINs cause slowdowns
- **Schema Rigidity**: Difficult to evolve data models
- **Operational Overhead**: Manual scaling and optimization
- **Cost**: Expensive enterprise database licensing

### Target State: NoSQL Database Architecture

```mermaid
graph TB
    subgraph TargetNoSQL[Target NoSQL Architecture]
        APP_NEW[Application Layer<br/>Spring Boot + MongoDB<br/>Document-based queries<br/>Aggregation pipelines]
        
        MONGODB[(MongoDB Atlas<br/>Sharded cluster (3 shards)<br/>Auto-scaling<br/>Replica sets<br/>Horizontal scaling)]
        
        REDIS_NEW[Redis Cluster<br/>Distributed caching<br/>Built-in persistence<br/>Automatic failover]
        
        BACKUP_NEW[Automated Backups<br/>Continuous backups<br/>Point-in-time restore<br/>Cross-region replication]
    end
    
    APP_NEW --> MONGODB
    APP_NEW --> REDIS_NEW
    MONGODB --> BACKUP_NEW
    
    classDef nosqlStyle fill:#4caf50,stroke:#1b5e20,color:#fff
    class APP_NEW,MONGODB,REDIS_NEW,BACKUP_NEW nosqlStyle
```

## Migration Strategy

### Data Model Transformation

**Before: Normalized SQL Schema**
```sql
-- Relational schema
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE orders (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    total_amount DECIMAL(10,2),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE order_items (
    id UUID PRIMARY KEY,
    order_id UUID REFERENCES orders(id),
    product_id UUID,
    quantity INTEGER,
    price DECIMAL(10,2)
);

CREATE TABLE products (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    category_id UUID REFERENCES categories(id),
    price DECIMAL(10,2)
);
```

**After: Document-Based NoSQL Schema**
```javascript
// MongoDB document structure
{
  // User document
  "_id": ObjectId("..."),
  "email": "user@example.com",
  "name": "John Doe",
  "profile": {
    "preferences": {
      "theme": "dark",
      "language": "en"
    },
    "address": {
      "street": "123 Main St",
      "city": "New York",
      "country": "US"
    }
  },
  "orders": [
    {
      "orderId": ObjectId("..."),
      "totalAmount": 159.99,
      "status": "completed",
      "items": [
        {
          "productId": ObjectId("..."),
          "productName": "Laptop",
          "quantity": 1,
          "price": 149.99,
          "category": "Electronics"
        }
      ],
      "createdAt": ISODate("2024-01-15T10:30:00Z")
    }
  ],
  "createdAt": ISODate("2024-01-01T00:00:00Z"),
  "updatedAt": ISODate("2024-01-15T10:30:00Z")
}
```

### Migration Implementation

**Spring Boot MongoDB Repository**
```java
// UserDocument.java - MongoDB document model
@Document(collection = "users")
@Data
@Builder
public class UserDocument {
    @Id
    private ObjectId id;
    
    @Indexed(unique = true)
    private String email;
    
    private String name;
    
    private UserProfile profile;
    
    private List<OrderSummary> orders;
    
    @CreatedDate
    private Instant createdAt;
    
    @LastModifiedDate
    private Instant updatedAt;
    
    @Data
    @Builder
    public static class UserProfile {
        private Map<String, Object> preferences;
        private Address address;
    }
    
    @Data
    @Builder
    public static class OrderSummary {
        private ObjectId orderId;
        private BigDecimal totalAmount;
        private OrderStatus status;
        private List<OrderItem> items;
        private Instant createdAt;
    }
    
    @Data
    @Builder
    public static class OrderItem {
        private ObjectId productId;
        private String productName;
        private Integer quantity;
        private BigDecimal price;
        private String category;
    }
}

// UserRepository.java - MongoDB repository
@Repository
public interface UserRepository extends MongoRepository<UserDocument, ObjectId> {
    
    Optional<UserDocument> findByEmail(String email);
    
    @Query("{'orders.status': ?0}")
    List<UserDocument> findByOrderStatus(OrderStatus status);
    
    @Aggregation(pipeline = {
        "{ $match: { 'orders.createdAt': { $gte: ?0, $lte: ?1 } } }",
        "{ $unwind: '$orders' }",
        "{ $group: { _id: '$orders.status', count: { $sum: 1 }, totalAmount: { $sum: '$orders.totalAmount' } } }"
    })
    List<OrderStatsProjection> getOrderStatsByDateRange(Instant startDate, Instant endDate);
    
    @Query("{'profile.address.city': ?0}")
    Page<UserDocument> findByCity(String city, Pageable pageable);
}

// UserService.java - Service layer with dual-write capability
@Service
@Transactional
@Slf4j
public class UserService {
    
    private final UserRepository mongoRepository;
    private final UserJpaRepository sqlRepository;
    private final MigrationProperties migrationProperties;
    
    public UserDocument createUser(CreateUserRequest request) {
        UserDocument mongoUser = UserDocument.builder()
            .email(request.getEmail())
            .name(request.getName())
            .profile(UserProfile.builder()
                .preferences(request.getPreferences())
                .address(request.getAddress())
                .build())
            .orders(new ArrayList<>())
            .build();
            
        // Save to MongoDB
        UserDocument savedUser = mongoRepository.save(mongoUser);
        
        // Dual-write to SQL during migration
        if (migrationProperties.isDualWriteEnabled()) {
            try {
                User sqlUser = mapToSqlEntity(savedUser);
                sqlRepository.save(sqlUser);
                log.info("Dual-write to SQL successful for user: {}", savedUser.getEmail());
            } catch (Exception e) {
                log.error("Dual-write to SQL failed for user: {}", savedUser.getEmail(), e);
                // Don't fail the operation, just log
            }
        }
        
        return savedUser;
    }
    
    public Optional<UserDocument> findByEmail(String email) {
        if (migrationProperties.isReadFromMongo()) {
            Optional<UserDocument> mongoResult = mongoRepository.findByEmail(email);
            if (mongoResult.isPresent()) {
                return mongoResult;
            }
        }
        
        // Fallback to SQL during migration
        if (migrationProperties.isDualReadEnabled()) {
            return sqlRepository.findByEmail(email)
                .map(this::mapFromSqlEntity);
        }
        
        return Optional.empty();
    }
    
    public void addOrderToUser(String userEmail, OrderSummary order) {
        UserDocument user = findByEmail(userEmail)
            .orElseThrow(() -> new UserNotFoundException("User not found: " + userEmail));
            
        user.getOrders().add(order);
        user.setUpdatedAt(Instant.now());
        
        mongoRepository.save(user);
        
        // Update SQL if dual-write is enabled
        if (migrationProperties.isDualWriteEnabled()) {
            updateSqlUserOrders(user);
        }
    }
    
    public List<OrderStatsProjection> getOrderStatsByDateRange(Instant startDate, Instant endDate) {
        return mongoRepository.getOrderStatsByDateRange(startDate, endDate);
    }
    
    private User mapToSqlEntity(UserDocument mongoUser) {
        // Map MongoDB document to SQL entity
        return User.builder()
            .email(mongoUser.getEmail())
            .name(mongoUser.getName())
            .createdAt(mongoUser.getCreatedAt())
            .build();
    }
    
    private UserDocument mapFromSqlEntity(User sqlUser) {
        // Map SQL entity to MongoDB document
        return UserDocument.builder()
            .email(sqlUser.getEmail())
            .name(sqlUser.getName())
            .profile(UserProfile.builder().build())
            .orders(new ArrayList<>())
            .createdAt(sqlUser.getCreatedAt())
            .build();
    }
}
```

### Data Migration Script

```python
#!/usr/bin/env python3
# sql_to_nosql_migration.py

import psycopg2
import pymongo
import json
from datetime import datetime
from typing import Dict, List, Any
import logging
from concurrent.futures import ThreadPoolExecutor
import time

class SQLToNoSQLMigrator:
    def __init__(self, postgres_config: Dict, mongo_config: Dict):
        self.postgres_conn = psycopg2.connect(**postgres_config)
        self.mongo_client = pymongo.MongoClient(**mongo_config)
        self.mongo_db = self.mongo_client.user_database
        
        # Migration statistics
        self.stats = {
            'users_migrated': 0,
            'orders_migrated': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def migrate_data(self, batch_size: int = 1000, max_workers: int = 4):
        """Main migration method"""
        self.stats['start_time'] = datetime.now()
        self.logger.info("Starting SQL to NoSQL migration...")
        
        try:
            # Step 1: Get total count for progress tracking
            total_users = self._get_total_user_count()
            self.logger.info(f"Total users to migrate: {total_users}")
            
            # Step 2: Migrate users in batches
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                for offset in range(0, total_users, batch_size):
                    executor.submit(self._migrate_user_batch, offset, batch_size)
            
            # Step 3: Verify migration
            self._verify_migration()
            
        except Exception as e:
            self.logger.error(f"Migration failed: {e}")
            raise
        finally:
            self.stats['end_time'] = datetime.now()
            self._print_migration_summary()
    
    def _get_total_user_count(self) -> int:
        """Get total number of users to migrate"""
        with self.postgres_conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM users")
            return cursor.fetchone()[0]
    
    def _migrate_user_batch(self, offset: int, batch_size: int):
        """Migrate a batch of users"""
        try:
            # Fetch users with their orders
            users = self._fetch_users_batch(offset, batch_size)
            
            # Convert to MongoDB documents
            mongo_documents = []
            for user in users:
                doc = self._convert_user_to_document(user)
                mongo_documents.append(doc)
            
            # Bulk insert to MongoDB
            if mongo_documents:
                result = self.mongo_db.users.insert_many(mongo_documents)
                self.stats['users_migrated'] += len(result.inserted_ids)
                
                self.logger.info(f"Migrated batch: {len(mongo_documents)} users")
                
        except Exception as e:
            self.stats['errors'] += 1
            self.logger.error(f"Error migrating batch at offset {offset}: {e}")
    
    def _fetch_users_batch(self, offset: int, batch_size: int) -> List[Dict]:
        """Fetch a batch of users with their orders from PostgreSQL"""
        query = """
        SELECT 
            u.id as user_id,
            u.email,
            u.name,
            u.created_at as user_created_at,
            o.id as order_id,
            o.total_amount,
            o.status as order_status,
            o.created_at as order_created_at,
            oi.product_id,
            oi.quantity,
            oi.price as item_price,
            p.name as product_name,
            p.category_id
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        LEFT JOIN order_items oi ON o.id = oi.order_id
        LEFT JOIN products p ON oi.product_id = p.id
        ORDER BY u.id, o.id, oi.id
        LIMIT %s OFFSET %s
        """
        
        with self.postgres_conn.cursor() as cursor:
            cursor.execute(query, (batch_size, offset))
            rows = cursor.fetchall()
            
            # Group by user
            users_dict = {}
            for row in rows:
                user_id = row[0]
                if user_id not in users_dict:
                    users_dict[user_id] = {
                        'id': user_id,
                        'email': row[1],
                        'name': row[2],
                        'created_at': row[3],
                        'orders': {}
                    }
                
                # Add order data if exists
                if row[4]:  # order_id
                    order_id = row[4]
                    if order_id not in users_dict[user_id]['orders']:
                        users_dict[user_id]['orders'][order_id] = {
                            'id': order_id,
                            'total_amount': float(row[5]),
                            'status': row[6],
                            'created_at': row[7],
                            'items': []
                        }
                    
                    # Add order item if exists
                    if row[8]:  # product_id
                        users_dict[user_id]['orders'][order_id]['items'].append({
                            'product_id': row[8],
                            'quantity': row[9],
                            'price': float(row[10]),
                            'product_name': row[11],
                            'category_id': row[12]
                        })
            
            return list(users_dict.values())
    
    def _convert_user_to_document(self, user_data: Dict) -> Dict:
        """Convert SQL user data to MongoDB document"""
        # Convert orders dict to list
        orders_list = list(user_data['orders'].values())
        
        document = {
            'email': user_data['email'],
            'name': user_data['name'],
            'profile': {
                'preferences': {},
                'address': {}
            },
            'orders': orders_list,
            'createdAt': user_data['created_at'],
            'updatedAt': datetime.now()
        }
        
        self.stats['orders_migrated'] += len(orders_list)
        return document
    
    def _verify_migration(self):
        """Verify migration completeness"""
        self.logger.info("Verifying migration...")
        
        # Count users in both databases
        with self.postgres_conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM users")
            sql_user_count = cursor.fetchone()[0]
        
        mongo_user_count = self.mongo_db.users.count_documents({})
        
        self.logger.info(f"SQL users: {sql_user_count}, MongoDB users: {mongo_user_count}")
        
        if sql_user_count == mongo_user_count:
            self.logger.info("✓ Migration verification successful")
        else:
            self.logger.error("✗ Migration verification failed - user count mismatch")
    
    def _print_migration_summary(self):
        """Print migration summary"""
        duration = self.stats['end_time'] - self.stats['start_time']
        
        summary = f"""
=== Migration Summary ===
Users migrated: {self.stats['users_migrated']}
Orders migrated: {self.stats['orders_migrated']}
Errors: {self.stats['errors']}
Duration: {duration}
Average rate: {self.stats['users_migrated'] / duration.total_seconds():.2f} users/second
========================
"""
        
        self.logger.info(summary)

def main():
    postgres_config = {
        'host': 'localhost',
        'database': 'production_db',
        'user': 'postgres',
        'password': 'password'
    }
    
    mongo_config = {
        'host': 'localhost',
        'port': 27017
    }
    
    migrator = SQLToNoSQLMigrator(postgres_config, mongo_config)
    migrator.migrate_data(batch_size=1000, max_workers=4)

if __name__ == '__main__':
    main()
```

## Performance Optimization

### MongoDB Indexing Strategy

```javascript
// Create indexes for optimal query performance
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "orders.status": 1 });
db.users.createIndex({ "orders.createdAt": 1 });
db.users.createIndex({ "profile.address.city": 1 });
db.users.createIndex({ "createdAt": 1 });

// Compound indexes for complex queries
db.users.createIndex({ 
    "orders.status": 1, 
    "orders.createdAt": 1 
});

db.users.createIndex({ 
    "profile.address.country": 1,
    "orders.totalAmount": 1
});

// Text index for search functionality
db.users.createIndex({ 
    "name": "text", 
    "email": "text" 
});
```

## Risk Mitigation

### Dual-Write Validation Script

```python
#!/usr/bin/env python3
# dual_write_validator.py

import psycopg2
import pymongo
import logging
from typing import Dict, List
import json

class DualWriteValidator:
    def __init__(self, postgres_config: Dict, mongo_config: Dict):
        self.postgres_conn = psycopg2.connect(**postgres_config)
        self.mongo_client = pymongo.MongoClient(**mongo_config)
        self.mongo_db = self.mongo_client.user_database
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def validate_consistency(self, sample_size: int = 1000) -> Dict:
        """Validate data consistency between SQL and NoSQL"""
        results = {
            'total_checked': 0,
            'consistent': 0,
            'inconsistent': 0,
            'missing_in_mongo': 0,
            'missing_in_sql': 0,
            'inconsistencies': []
        }
        
        # Get sample of users from SQL
        sql_users = self._get_sql_sample(sample_size)
        
        for sql_user in sql_users:
            results['total_checked'] += 1
            
            # Find corresponding MongoDB document
            mongo_user = self.mongo_db.users.find_one({'email': sql_user['email']})
            
            if not mongo_user:
                results['missing_in_mongo'] += 1
                results['inconsistencies'].append({
                    'type': 'missing_in_mongo',
                    'email': sql_user['email']
                })
                continue
            
            # Compare data
            if self._compare_user_data(sql_user, mongo_user):
                results['consistent'] += 1
            else:
                results['inconsistent'] += 1
                results['inconsistencies'].append({
                    'type': 'data_mismatch',
                    'email': sql_user['email'],
                    'sql_data': sql_user,
                    'mongo_data': mongo_user
                })
        
        # Calculate consistency percentage
        results['consistency_percentage'] = (
            results['consistent'] / results['total_checked'] * 100
            if results['total_checked'] > 0 else 0
        )
        
        return results
    
    def _get_sql_sample(self, sample_size: int) -> List[Dict]:
        """Get sample of users from SQL database"""
        query = """
        SELECT id, email, name, created_at
        FROM users
        ORDER BY RANDOM()
        LIMIT %s
        """
        
        with self.postgres_conn.cursor() as cursor:
            cursor.execute(query, (sample_size,))
            rows = cursor.fetchall()
            
            return [{
                'id': row[0],
                'email': row[1],
                'name': row[2],
                'created_at': row[3]
            } for row in rows]
    
    def _compare_user_data(self, sql_user: Dict, mongo_user: Dict) -> bool:
        """Compare user data between SQL and MongoDB"""
        # Compare basic fields
        if sql_user['email'] != mongo_user.get('email'):
            return False
        
        if sql_user['name'] != mongo_user.get('name'):
            return False
        
        # Compare timestamps (allowing small differences)
        sql_time = sql_user['created_at']
        mongo_time = mongo_user.get('createdAt')
        
        if abs((sql_time - mongo_time).total_seconds()) > 1:
            return False
        
        return True

def main():
    postgres_config = {
        'host': 'localhost',
        'database': 'production_db',
        'user': 'postgres',
        'password': 'password'
    }
    
    mongo_config = {
        'host': 'localhost',
        'port': 27017
    }
    
    validator = DualWriteValidator(postgres_config, mongo_config)
    results = validator.validate_consistency(sample_size=1000)
    
    print(f"Consistency Report:")
    print(f"Total checked: {results['total_checked']}")
    print(f"Consistent: {results['consistent']}")
    print(f"Inconsistent: {results['inconsistent']}")
    print(f"Consistency rate: {results['consistency_percentage']:.2f}%")
    
    if results['inconsistencies']:
        print(f"\nFirst 5 inconsistencies:")
        for inc in results['inconsistencies'][:5]:
            print(f"- {inc['type']}: {inc['email']}")

if __name__ == '__main__':
    main()
```

## Conclusion

This SQL to NoSQL migration playbook provides a comprehensive approach to modernizing database architecture while maintaining data integrity and minimizing business disruption.

**Key Success Factors:**
1. **Dual-write strategy** for zero-downtime migration
2. **Document model design** optimized for application access patterns
3. **Comprehensive validation** of data consistency
4. **Performance optimization** through proper indexing
5. **Gradual transition** with rollback capabilities

**Expected Outcomes:**
- 10x improvement in read performance for document queries
- Horizontal scalability for growing data volumes
- 50% reduction in complex JOIN operations
- Flexible schema evolution capabilities
- Reduced database licensing costs

The migration enables modern application architectures and provides a foundation for microservices and event-driven systems.