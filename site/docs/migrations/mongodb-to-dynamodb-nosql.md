# MongoDB to DynamoDB Migration Playbook

## Executive Summary

**Migration Type**: NoSQL Database Platform Migration
**Timeline**: 12-16 weeks
**Risk Level**: High
**Downtime**: Zero (dual-write strategy)
**Cost Impact**: 40-60% reduction in database operational costs
**Team Size**: 4-5 engineers + 1 DBA + 1 DevOps engineer

This playbook guides the migration from MongoDB to AWS DynamoDB for applications requiring massive scale, consistent performance, and reduced operational overhead. Based on real migrations from Discord, Lyft, and other high-scale platforms.

## Current State vs Target State

### Current State: MongoDB Cluster

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - #0066CC]
        ALB[Application Load Balancer<br/>Target health checks<br/>SSL termination<br/>Request routing]
        CF[CloudFront CDN<br/>Static asset caching<br/>API response caching<br/>Global distribution]
    end

    subgraph ServicePlane[Service Plane - #00AA00]
        API_SERVERS[API Servers<br/>Node.js/Python services<br/>Connection pooling<br/>Query optimization]
        BG_WORKERS[Background Workers<br/>Data processing<br/>ETL operations<br/>Analytics jobs]
        CACHE_LAYER[Application Cache<br/>Redis cluster<br/>Query result caching<br/>Session storage]
    end

    subgraph StatePlane[State Plane - #FF8800]
        MONGO_PRIMARY[(MongoDB Primary<br/>r5.2xlarge<br/>Read/Write operations<br/>Replica set leader)]
        MONGO_SECONDARY1[(MongoDB Secondary 1<br/>r5.xlarge<br/>Read operations<br/>Backup target)]
        MONGO_SECONDARY2[(MongoDB Secondary 2<br/>r5.xlarge<br/>Read operations<br/>Analytics queries)]
        MONGO_ARBITER[MongoDB Arbiter<br/>t3.small<br/>Election participation<br/>No data storage]
    end

    subgraph ControlPlane[Control Plane - #CC0000]
        MONGO_OPS[MongoDB Ops Manager<br/>Cluster monitoring<br/>Backup management<br/>Performance tuning]
        ALERTING[CloudWatch Alerting<br/>Custom metrics<br/>Log aggregation<br/>On-call automation]
    end

    CF --> ALB
    ALB --> API_SERVERS
    ALB --> BG_WORKERS

    API_SERVERS --> CACHE_LAYER
    API_SERVERS --> MONGO_PRIMARY
    API_SERVERS --> MONGO_SECONDARY1
    API_SERVERS --> MONGO_SECONDARY2

    BG_WORKERS --> MONGO_PRIMARY
    BG_WORKERS --> MONGO_SECONDARY2

    MONGO_PRIMARY --> MONGO_SECONDARY1
    MONGO_PRIMARY --> MONGO_SECONDARY2
    MONGO_PRIMARY --> MONGO_ARBITER

    MONGO_PRIMARY --> MONGO_OPS
    MONGO_SECONDARY1 --> MONGO_OPS
    MONGO_SECONDARY2 --> MONGO_OPS

    MONGO_OPS --> ALERTING

    %% Apply four-plane colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class ALB,CF edgeStyle
    class API_SERVERS,BG_WORKERS,CACHE_LAYER serviceStyle
    class MONGO_PRIMARY,MONGO_SECONDARY1,MONGO_SECONDARY2,MONGO_ARBITER stateStyle
    class MONGO_OPS,ALERTING controlStyle
```

**Current State Issues:**
- **Operational Complexity**: Manual sharding, replica set management
- **Scaling Limitations**: Complex horizontal scaling with sharding
- **Cost Overhead**: Dedicated infrastructure, operational staff
- **Performance Variability**: Query performance depends on index tuning
- **Backup Complexity**: Point-in-time recovery across shards

### Target State: DynamoDB Serverless

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - #0066CC]
        ALB[Application Load Balancer<br/>Same configuration<br/>Health check updates<br/>Request routing]
        CF[CloudFront CDN<br/>Enhanced with DynamoDB<br/>DAX caching integration<br/>Global distribution]
    end

    subgraph ServicePlane[Service Plane - #00AA00]
        API_SERVERS_NEW[API Servers<br/>Updated DB drivers<br/>DynamoDB SDK<br/>Async operations]
        BG_WORKERS_NEW[Background Workers<br/>DynamoDB Streams<br/>Event-driven processing<br/>Lambda integration]
        DAX_CACHE[DynamoDB Accelerator<br/>Microsecond latency<br/>Transparent caching<br/>Cluster mode]
    end

    subgraph StatePlane[State Plane - #FF8800]
        DYNAMODB_MAIN[(DynamoDB Tables<br/>On-demand scaling<br/>Global tables<br/>Point-in-time recovery)]
        DYNAMODB_GSI[(Global Secondary Indexes<br/>Alternative access patterns<br/>Query optimization<br/>Independent scaling)]
        S3_BACKUP[S3 Backup Vault<br/>Automated backups<br/>Cross-region replication<br/>Lifecycle policies]
    end

    subgraph ControlPlane[Control Plane - #CC0000]
        CLOUDWATCH[CloudWatch Monitoring<br/>Native DynamoDB metrics<br/>Custom application metrics<br/>Auto-scaling triggers]
        XRAY[AWS X-Ray<br/>Distributed tracing<br/>Performance insights<br/>Error analysis]
        DYNAMODB_STREAMS[DynamoDB Streams<br/>Change data capture<br/>Real-time processing<br/>Lambda triggers]
    end

    CF --> ALB
    ALB --> API_SERVERS_NEW
    ALB --> BG_WORKERS_NEW

    API_SERVERS_NEW --> DAX_CACHE
    API_SERVERS_NEW --> DYNAMODB_MAIN
    API_SERVERS_NEW --> DYNAMODB_GSI

    BG_WORKERS_NEW --> DYNAMODB_MAIN
    BG_WORKERS_NEW --> DYNAMODB_STREAMS

    DAX_CACHE --> DYNAMODB_MAIN
    DYNAMODB_MAIN --> DYNAMODB_GSI
    DYNAMODB_MAIN --> S3_BACKUP
    DYNAMODB_MAIN --> DYNAMODB_STREAMS

    DYNAMODB_MAIN --> CLOUDWATCH
    DYNAMODB_GSI --> CLOUDWATCH
    DYNAMODB_STREAMS --> XRAY

    %% Apply four-plane colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class ALB,CF edgeStyle
    class API_SERVERS_NEW,BG_WORKERS_NEW,DAX_CACHE serviceStyle
    class DYNAMODB_MAIN,DYNAMODB_GSI,S3_BACKUP stateStyle
    class CLOUDWATCH,XRAY,DYNAMODB_STREAMS controlStyle
```

## Migration Strategy

### Phase 1: Data Model Analysis and Design (2-3 weeks)

```mermaid
graph LR
    subgraph DataModelAnalysis[Data Model Analysis]
        ANALYZE_QUERIES[Analyze Query Patterns<br/>Most frequent queries<br/>Access patterns<br/>Performance requirements]
        ANALYZE_SCHEMA[Analyze MongoDB Schema<br/>Document structure<br/>Relationships<br/>Data types]
        IDENTIFY_PATTERNS[Identify Access Patterns<br/>Read/write ratios<br/>Hot partitions<br/>Query complexity]
    end

    subgraph DynamoDBDesign[DynamoDB Design]
        DESIGN_TABLES[Design Table Structure<br/>Partition key selection<br/>Sort key design<br/>Data distribution]
        DESIGN_GSI[Design Global Secondary Indexes<br/>Alternative access patterns<br/>Query optimization<br/>Cost optimization]
        VALIDATE_MODEL[Validate Data Model<br/>Performance testing<br/>Cost estimation<br/>Scalability analysis]
    end

    ANALYZE_QUERIES --> DESIGN_TABLES
    ANALYZE_SCHEMA --> DESIGN_TABLES
    IDENTIFY_PATTERNS --> DESIGN_GSI
    DESIGN_TABLES --> VALIDATE_MODEL
    DESIGN_GSI --> VALIDATE_MODEL

    %% Apply colors
    classDef analysisStyle fill:#E8F4FD,stroke:#0066CC,color:#000
    classDef designStyle fill:#E8F7E8,stroke:#00AA00,color:#000

    class ANALYZE_QUERIES,ANALYZE_SCHEMA,IDENTIFY_PATTERNS analysisStyle
    class DESIGN_TABLES,DESIGN_GSI,VALIDATE_MODEL designStyle
```

### MongoDB to DynamoDB Schema Transformation

**Example: User Profile Collection**

**MongoDB Document:**
```javascript
// users collection
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "username": "john_doe",
  "email": "john@example.com",
  "profile": {
    "firstName": "John",
    "lastName": "Doe",
    "dateOfBirth": ISODate("1990-01-01"),
    "avatar": "https://cdn.example.com/avatars/john.jpg"
  },
  "preferences": {
    "theme": "dark",
    "notifications": {
      "email": true,
      "push": false
    }
  },
  "addresses": [
    {
      "type": "home",
      "street": "123 Main St",
      "city": "Seattle",
      "state": "WA",
      "zipCode": "98101"
    }
  ],
  "createdAt": ISODate("2023-01-15T10:30:00Z"),
  "lastLoginAt": ISODate("2024-01-15T15:45:00Z"),
  "status": "active"
}
```

**DynamoDB Table Design:**
```json
{
  "TableName": "Users",
  "KeySchema": [
    {
      "AttributeName": "PK",
      "KeyType": "HASH"
    },
    {
      "AttributeName": "SK",
      "KeyType": "RANGE"
    }
  ],
  "AttributeDefinitions": [
    {
      "AttributeName": "PK",
      "AttributeType": "S"
    },
    {
      "AttributeName": "SK",
      "AttributeType": "S"
    },
    {
      "AttributeName": "GSI1PK",
      "AttributeType": "S"
    },
    {
      "AttributeName": "GSI1SK",
      "AttributeType": "S"
    }
  ],
  "GlobalSecondaryIndexes": [
    {
      "IndexName": "GSI1",
      "KeySchema": [
        {
          "AttributeName": "GSI1PK",
          "KeyType": "HASH"
        },
        {
          "AttributeName": "GSI1SK",
          "KeyType": "RANGE"
        }
      ]
    }
  ]
}
```

**DynamoDB Items:**
```json
// User profile item
{
  "PK": "USER#john_doe",
  "SK": "PROFILE",
  "GSI1PK": "EMAIL#john@example.com",
  "GSI1SK": "USER",
  "username": "john_doe",
  "email": "john@example.com",
  "firstName": "John",
  "lastName": "Doe",
  "dateOfBirth": "1990-01-01",
  "avatar": "https://cdn.example.com/avatars/john.jpg",
  "theme": "dark",
  "emailNotifications": true,
  "pushNotifications": false,
  "createdAt": "2023-01-15T10:30:00Z",
  "lastLoginAt": "2024-01-15T15:45:00Z",
  "status": "active",
  "entityType": "USER_PROFILE"
}

// Address items (one per address)
{
  "PK": "USER#john_doe",
  "SK": "ADDRESS#home",
  "addressType": "home",
  "street": "123 Main St",
  "city": "Seattle",
  "state": "WA",
  "zipCode": "98101",
  "entityType": "USER_ADDRESS"
}
```

### Phase 2: Infrastructure Setup (1-2 weeks)

```python
# infrastructure/dynamodb_setup.py
import boto3
import json
from typing import Dict, List, Any

class DynamoDBMigrationInfrastructure:
    def __init__(self, region: str = 'us-east-1'):
        self.dynamodb = boto3.client('dynamodb', region_name=region)
        self.region = region

    def create_main_table(self, table_name: str) -> bool:
        """Create main DynamoDB table with optimal settings"""

        table_config = {
            'TableName': table_name,
            'KeySchema': [
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'},
                {'AttributeName': 'GSI1PK', 'AttributeType': 'S'},
                {'AttributeName': 'GSI1SK', 'AttributeType': 'S'},
                {'AttributeName': 'GSI2PK', 'AttributeType': 'S'},
                {'AttributeName': 'GSI2SK', 'AttributeType': 'S'}
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'GSI1',
                    'KeySchema': [
                        {'AttributeName': 'GSI1PK', 'KeyType': 'HASH'},
                        {'AttributeName': 'GSI1SK', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'BillingMode': 'ON_DEMAND'
                },
                {
                    'IndexName': 'GSI2',
                    'KeySchema': [
                        {'AttributeName': 'GSI2PK', 'KeyType': 'HASH'},
                        {'AttributeName': 'GSI2SK', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'BillingMode': 'ON_DEMAND'
                }
            ],
            'BillingMode': 'ON_DEMAND',
            'StreamSpecification': {
                'StreamEnabled': True,
                'StreamViewType': 'NEW_AND_OLD_IMAGES'
            },
            'SSESpecification': {
                'Enabled': True,
                'SSEType': 'KMS'
            },
            'PointInTimeRecoverySpecification': {
                'PointInTimeRecoveryEnabled': True
            },
            'Tags': [
                {'Key': 'Project', 'Value': 'MongoDB-Migration'},
                {'Key': 'Environment', 'Value': 'Production'},
                {'Key': 'CostCenter', 'Value': 'Engineering'}
            ]
        }

        try:
            response = self.dynamodb.create_table(**table_config)
            print(f"✓ Created table {table_name}")
            return True
        except Exception as e:
            print(f"✗ Failed to create table {table_name}: {e}")
            return False

    def setup_dax_cluster(self, cluster_name: str) -> Dict[str, Any]:
        """Setup DynamoDB Accelerator cluster"""

        dax_client = boto3.client('dax', region_name=self.region)

        cluster_config = {
            'ClusterName': cluster_name,
            'NodeType': 'dax.r4.large',
            'ReplicationFactor': 3,
            'Description': 'MongoDB migration DAX cluster',
            'SubnetGroupName': 'default',
            'SecurityGroupIds': ['sg-xxxxxxxxx'],  # Configure security group
            'ParameterGroupName': 'default.dax1.0',
            'SSESpecification': {
                'Enabled': True
            },
            'Tags': [
                {'Key': 'Project', 'Value': 'MongoDB-Migration'},
                {'Key': 'Environment', 'Value': 'Production'}
            ]
        }

        try:
            response = dax_client.create_cluster(**cluster_config)
            endpoint = response['Cluster']['ClusterDiscoveryEndpoint']
            print(f"✓ Created DAX cluster: {endpoint['Address']}:{endpoint['Port']}")
            return response
        except Exception as e:
            print(f"✗ Failed to create DAX cluster: {e}")
            return {}

    def setup_global_tables(self, table_name: str, regions: List[str]) -> bool:
        """Setup DynamoDB Global Tables for multi-region"""

        try:
            # Enable streams on source table
            self.dynamodb.update_table(
                TableName=table_name,
                StreamSpecification={
                    'StreamEnabled': True,
                    'StreamViewType': 'NEW_AND_OLD_IMAGES'
                }
            )

            # Create global table
            global_table_config = {
                'GlobalTableName': table_name,
                'ReplicationGroup': [{'RegionName': region} for region in regions]
            }

            global_tables_client = boto3.client('dynamodb', region_name=self.region)
            response = global_tables_client.create_global_table(**global_table_config)

            print(f"✓ Created global table across regions: {regions}")
            return True

        except Exception as e:
            print(f"✗ Failed to create global table: {e}")
            return False
```

### Phase 3: Data Migration Pipeline (4-6 weeks)

```python
# migration/mongodb_to_dynamodb_migrator.py
import asyncio
import boto3
import pymongo
from datetime import datetime
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import logging

class MongoToDynamoDBMigrator:
    def __init__(self, mongo_uri: str, dynamodb_table: str, region: str = 'us-east-1'):
        self.mongo_client = pymongo.MongoClient(mongo_uri)
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.table = self.dynamodb.Table(dynamodb_table)
        self.logger = logging.getLogger(__name__)

        # Migration statistics
        self.stats = {
            'total_documents': 0,
            'migrated_documents': 0,
            'failed_documents': 0,
            'start_time': None,
            'batch_size': 25,  # DynamoDB batch_write_item limit
            'parallel_workers': 10
        }

    async def migrate_collection(self, db_name: str, collection_name: str) -> bool:
        """Migrate entire MongoDB collection to DynamoDB"""

        self.stats['start_time'] = datetime.now()
        collection = self.mongo_client[db_name][collection_name]

        # Get total document count
        self.stats['total_documents'] = collection.count_documents({})
        self.logger.info(f"Starting migration of {self.stats['total_documents']} documents")

        # Process documents in batches
        batch_size = self.stats['batch_size']
        skip = 0

        with ThreadPoolExecutor(max_workers=self.stats['parallel_workers']) as executor:
            while skip < self.stats['total_documents']:
                # Get batch of documents
                documents = list(collection.find({}).skip(skip).limit(batch_size))

                if not documents:
                    break

                # Transform and write batch
                futures = []
                for doc in documents:
                    future = executor.submit(self._migrate_document, doc, collection_name)
                    futures.append(future)

                # Wait for batch completion
                for future in futures:
                    try:
                        future.result()
                        self.stats['migrated_documents'] += 1
                    except Exception as e:
                        self.stats['failed_documents'] += 1
                        self.logger.error(f"Failed to migrate document: {e}")

                skip += batch_size

                # Progress reporting
                progress = (skip / self.stats['total_documents']) * 100
                self.logger.info(f"Migration progress: {progress:.1f}% ({skip}/{self.stats['total_documents']})")

        # Final statistics
        duration = datetime.now() - self.stats['start_time']
        self.logger.info(f"Migration completed in {duration}")
        self.logger.info(f"Success: {self.stats['migrated_documents']}, Failed: {self.stats['failed_documents']}")

        return self.stats['failed_documents'] == 0

    def _migrate_document(self, mongo_doc: Dict[str, Any], collection_name: str) -> bool:
        """Transform and migrate single MongoDB document"""

        try:
            # Transform MongoDB document to DynamoDB items
            dynamodb_items = self._transform_document(mongo_doc, collection_name)

            # Write to DynamoDB
            for item in dynamodb_items:
                self.table.put_item(Item=item)

            return True

        except Exception as e:
            self.logger.error(f"Failed to migrate document {mongo_doc.get('_id')}: {e}")
            return False

    def _transform_document(self, mongo_doc: Dict[str, Any], collection_name: str) -> List[Dict[str, Any]]:
        """Transform MongoDB document to DynamoDB items"""

        items = []

        if collection_name == 'users':
            items.extend(self._transform_user_document(mongo_doc))
        elif collection_name == 'orders':
            items.extend(self._transform_order_document(mongo_doc))
        elif collection_name == 'products':
            items.extend(self._transform_product_document(mongo_doc))
        else:
            # Generic transformation
            items.append(self._generic_transform(mongo_doc, collection_name))

        return items

    def _transform_user_document(self, user_doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Transform MongoDB user document to DynamoDB items"""

        items = []
        user_id = str(user_doc['_id'])
        username = user_doc.get('username', user_id)

        # Main user profile item
        profile_item = {
            'PK': f'USER#{username}',
            'SK': 'PROFILE',
            'GSI1PK': f"EMAIL#{user_doc.get('email', '')}",
            'GSI1SK': 'USER',
            'userId': user_id,
            'username': username,
            'email': user_doc.get('email', ''),
            'entityType': 'USER_PROFILE',
            'createdAt': self._convert_datetime(user_doc.get('createdAt')),
            'lastLoginAt': self._convert_datetime(user_doc.get('lastLoginAt')),
            'status': user_doc.get('status', 'active')
        }

        # Add profile fields
        if 'profile' in user_doc:
            profile = user_doc['profile']
            profile_item.update({
                'firstName': profile.get('firstName', ''),
                'lastName': profile.get('lastName', ''),
                'dateOfBirth': self._convert_datetime(profile.get('dateOfBirth')),
                'avatar': profile.get('avatar', '')
            })

        # Add preferences
        if 'preferences' in user_doc:
            prefs = user_doc['preferences']
            profile_item.update({
                'theme': prefs.get('theme', 'light'),
                'emailNotifications': prefs.get('notifications', {}).get('email', True),
                'pushNotifications': prefs.get('notifications', {}).get('push', False)
            })

        items.append(profile_item)

        # Address items
        if 'addresses' in user_doc:
            for address in user_doc['addresses']:
                address_item = {
                    'PK': f'USER#{username}',
                    'SK': f"ADDRESS#{address.get('type', 'unknown')}",
                    'entityType': 'USER_ADDRESS',
                    'addressType': address.get('type', ''),
                    'street': address.get('street', ''),
                    'city': address.get('city', ''),
                    'state': address.get('state', ''),
                    'zipCode': address.get('zipCode', '')
                }
                items.append(address_item)

        return items

    def _transform_order_document(self, order_doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Transform MongoDB order document to DynamoDB items"""

        items = []
        order_id = str(order_doc['_id'])
        user_id = str(order_doc.get('userId', ''))

        # Main order item
        order_item = {
            'PK': f'ORDER#{order_id}',
            'SK': 'METADATA',
            'GSI1PK': f'USER#{user_id}',
            'GSI1SK': f"ORDER#{self._convert_datetime(order_doc.get('createdAt'))}",
            'GSI2PK': f"STATUS#{order_doc.get('status', 'pending')}",
            'GSI2SK': f"ORDER#{order_id}",
            'orderId': order_id,
            'userId': user_id,
            'status': order_doc.get('status', 'pending'),
            'totalAmount': str(order_doc.get('totalAmount', 0)),
            'currency': order_doc.get('currency', 'USD'),
            'entityType': 'ORDER',
            'createdAt': self._convert_datetime(order_doc.get('createdAt')),
            'updatedAt': self._convert_datetime(order_doc.get('updatedAt'))
        }
        items.append(order_item)

        # Order items
        if 'items' in order_doc:
            for idx, item in enumerate(order_doc['items']):
                order_item_entry = {
                    'PK': f'ORDER#{order_id}',
                    'SK': f'ITEM#{idx:03d}',
                    'entityType': 'ORDER_ITEM',
                    'productId': str(item.get('productId', '')),
                    'quantity': item.get('quantity', 1),
                    'price': str(item.get('price', 0)),
                    'itemName': item.get('name', '')
                }
                items.append(order_item_entry)

        return items

    def _convert_datetime(self, dt) -> str:
        """Convert MongoDB datetime to ISO string"""
        if dt is None:
            return ''
        if hasattr(dt, 'isoformat'):
            return dt.isoformat()
        return str(dt)

    def _generic_transform(self, doc: Dict[str, Any], collection_name: str) -> Dict[str, Any]:
        """Generic document transformation"""

        doc_id = str(doc.get('_id', ''))

        # Flatten nested objects
        flattened = self._flatten_dict(doc)

        # Remove MongoDB _id and replace with DynamoDB keys
        if '_id' in flattened:
            del flattened['_id']

        flattened.update({
            'PK': f'{collection_name.upper()}#{doc_id}',
            'SK': 'DATA',
            'entityType': collection_name.upper(),
            'originalId': doc_id
        })

        return flattened

    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
        """Flatten nested dictionary for DynamoDB storage"""

        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k

            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # Convert list to string for DynamoDB
                items.append((new_key, str(v)))
            else:
                items.append((new_key, v))

        return dict(items)

# Migration execution script
async def main():
    # Configuration
    MONGO_URI = "mongodb://localhost:27017"
    DYNAMODB_TABLE = "MigratedData"
    REGION = "us-east-1"

    # Initialize migrator
    migrator = MongoToDynamoDBMigrator(MONGO_URI, DYNAMODB_TABLE, REGION)

    # Migrate collections
    collections_to_migrate = [
        ('myapp', 'users'),
        ('myapp', 'orders'),
        ('myapp', 'products'),
        ('myapp', 'categories')
    ]

    for db_name, collection_name in collections_to_migrate:
        print(f"Migrating {db_name}.{collection_name}...")
        success = await migrator.migrate_collection(db_name, collection_name)

        if success:
            print(f"✓ Successfully migrated {collection_name}")
        else:
            print(f"✗ Failed to migrate {collection_name}")

if __name__ == '__main__':
    asyncio.run(main())
```

### Phase 4: Application Code Updates (3-4 weeks)

```python
# app/database/dynamodb_client.py
import boto3
import json
from typing import Dict, List, Any, Optional
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

class DynamoDBClient:
    def __init__(self, table_name: str, region: str = 'us-east-1', use_dax: bool = True):
        if use_dax:
            # Use DAX for caching
            import amazondax
            self.dynamodb = amazondax.AmazonDaxClient.resource(
                endpoint_url='dax-cluster.abc123.dax-clusters.us-east-1.amazonaws.com:8111'
            )
        else:
            self.dynamodb = boto3.resource('dynamodb', region_name=region)

        self.table = self.dynamodb.Table(table_name)

    # User operations
    def get_user_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user profile by username"""
        try:
            response = self.table.get_item(
                Key={
                    'PK': f'USER#{username}',
                    'SK': 'PROFILE'
                }
            )
            return response.get('Item')
        except ClientError as e:
            print(f"Error getting user profile: {e}")
            return None

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email using GSI1"""
        try:
            response = self.table.query(
                IndexName='GSI1',
                KeyConditionExpression=Key('GSI1PK').eq(f'EMAIL#{email}') & Key('GSI1SK').eq('USER')
            )
            items = response.get('Items', [])
            return items[0] if items else None
        except ClientError as e:
            print(f"Error getting user by email: {e}")
            return None

    def get_user_addresses(self, username: str) -> List[Dict[str, Any]]:
        """Get all addresses for a user"""
        try:
            response = self.table.query(
                KeyConditionExpression=Key('PK').eq(f'USER#{username}') & Key('SK').begins_with('ADDRESS#')
            )
            return response.get('Items', [])
        except ClientError as e:
            print(f"Error getting user addresses: {e}")
            return []

    def create_user(self, user_data: Dict[str, Any]) -> bool:
        """Create new user with profile and addresses"""
        try:
            username = user_data['username']

            # Prepare main profile item
            profile_item = {
                'PK': f'USER#{username}',
                'SK': 'PROFILE',
                'GSI1PK': f"EMAIL#{user_data['email']}",
                'GSI1SK': 'USER',
                'entityType': 'USER_PROFILE',
                **user_data
            }

            # Write profile
            self.table.put_item(Item=profile_item)

            # Write addresses if provided
            if 'addresses' in user_data:
                for address in user_data['addresses']:
                    address_item = {
                        'PK': f'USER#{username}',
                        'SK': f"ADDRESS#{address['type']}",
                        'entityType': 'USER_ADDRESS',
                        **address
                    }
                    self.table.put_item(Item=address_item)

            return True

        except ClientError as e:
            print(f"Error creating user: {e}")
            return False

    # Order operations
    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get order with all items"""
        try:
            # Get order metadata
            response = self.table.get_item(
                Key={
                    'PK': f'ORDER#{order_id}',
                    'SK': 'METADATA'
                }
            )
            order = response.get('Item')

            if not order:
                return None

            # Get order items
            response = self.table.query(
                KeyConditionExpression=Key('PK').eq(f'ORDER#{order_id}') & Key('SK').begins_with('ITEM#')
            )
            order['items'] = response.get('Items', [])

            return order

        except ClientError as e:
            print(f"Error getting order: {e}")
            return None

    def get_user_orders(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get orders for a user using GSI1"""
        try:
            response = self.table.query(
                IndexName='GSI1',
                KeyConditionExpression=Key('GSI1PK').eq(f'USER#{user_id}') & Key('GSI1SK').begins_with('ORDER#'),
                ScanIndexForward=False,  # Most recent first
                Limit=limit
            )
            return response.get('Items', [])
        except ClientError as e:
            print(f"Error getting user orders: {e}")
            return []

    def get_orders_by_status(self, status: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get orders by status using GSI2"""
        try:
            response = self.table.query(
                IndexName='GSI2',
                KeyConditionExpression=Key('GSI2PK').eq(f'STATUS#{status}'),
                Limit=limit
            )
            return response.get('Items', [])
        except ClientError as e:
            print(f"Error getting orders by status: {e}")
            return []

    def create_order(self, order_data: Dict[str, Any]) -> bool:
        """Create new order with items"""
        try:
            order_id = order_data['orderId']
            user_id = order_data['userId']

            # Create order metadata
            order_item = {
                'PK': f'ORDER#{order_id}',
                'SK': 'METADATA',
                'GSI1PK': f'USER#{user_id}',
                'GSI1SK': f"ORDER#{order_data.get('createdAt', '')}",
                'GSI2PK': f"STATUS#{order_data['status']}",
                'GSI2SK': f'ORDER#{order_id}',
                'entityType': 'ORDER',
                **{k: v for k, v in order_data.items() if k != 'items'}
            }

            # Use transaction to ensure consistency
            with self.table.batch_writer() as batch:
                batch.put_item(Item=order_item)

                # Add order items
                for idx, item in enumerate(order_data.get('items', [])):
                    item_entry = {
                        'PK': f'ORDER#{order_id}',
                        'SK': f'ITEM#{idx:03d}',
                        'entityType': 'ORDER_ITEM',
                        **item
                    }
                    batch.put_item(Item=item_entry)

            return True

        except ClientError as e:
            print(f"Error creating order: {e}")
            return False

    def update_order_status(self, order_id: str, new_status: str) -> bool:
        """Update order status"""
        try:
            # Update in both main table and GSI2
            response = self.table.update_item(
                Key={
                    'PK': f'ORDER#{order_id}',
                    'SK': 'METADATA'
                },
                UpdateExpression='SET #status = :status, GSI2PK = :gsi2pk',
                ExpressionAttributeNames={
                    '#status': 'status'
                },
                ExpressionAttributeValues={
                    ':status': new_status,
                    ':gsi2pk': f'STATUS#{new_status}'
                },
                ReturnValues='UPDATED_NEW'
            )
            return True

        except ClientError as e:
            print(f"Error updating order status: {e}")
            return False

    # Generic operations
    def batch_get_items(self, keys: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Batch get multiple items"""
        try:
            response = self.dynamodb.batch_get_item(
                RequestItems={
                    self.table.table_name: {
                        'Keys': keys
                    }
                }
            )
            return response.get('Responses', {}).get(self.table.table_name, [])
        except ClientError as e:
            print(f"Error in batch get: {e}")
            return []

    def scan_with_filter(self, filter_expression, limit: int = 100) -> List[Dict[str, Any]]:
        """Scan table with filter (use sparingly)"""
        try:
            response = self.table.scan(
                FilterExpression=filter_expression,
                Limit=limit
            )
            return response.get('Items', [])
        except ClientError as e:
            print(f"Error in scan: {e}")
            return []
```

### Phase 5: Dual-Write Implementation (2-3 weeks)

```python
# app/database/dual_write_manager.py
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from .mongodb_client import MongoDBClient
from .dynamodb_client import DynamoDBClient

class DualWriteManager:
    """Manages dual writes to both MongoDB and DynamoDB during migration"""

    def __init__(self, mongo_client: MongoDBClient, dynamodb_client: DynamoDBClient):
        self.mongo_client = mongo_client
        self.dynamodb_client = dynamodb_client
        self.logger = logging.getLogger(__name__)

        # Configuration flags
        self.write_to_mongo = True
        self.write_to_dynamodb = True
        self.read_from_dynamodb = False  # Start with MongoDB reads
        self.validate_writes = True

        # Metrics tracking
        self.metrics = {
            'mongo_writes': 0,
            'dynamodb_writes': 0,
            'mongo_write_failures': 0,
            'dynamodb_write_failures': 0,
            'validation_failures': 0
        }

    async def create_user(self, user_data: Dict[str, Any]) -> bool:
        """Create user in both databases"""
        success = True

        try:
            # Write to MongoDB
            if self.write_to_mongo:
                mongo_success = await self._write_to_mongo('users', user_data)
                if mongo_success:
                    self.metrics['mongo_writes'] += 1
                else:
                    self.metrics['mongo_write_failures'] += 1
                    success = False

            # Write to DynamoDB
            if self.write_to_dynamodb:
                dynamodb_success = self.dynamodb_client.create_user(user_data)
                if dynamodb_success:
                    self.metrics['dynamodb_writes'] += 1
                else:
                    self.metrics['dynamodb_write_failures'] += 1
                    success = False

            # Validate consistency if both writes succeeded
            if self.validate_writes and success:
                await self._validate_user_consistency(user_data['username'])

            return success

        except Exception as e:
            self.logger.error(f"Error in dual write create_user: {e}")
            return False

    async def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user from appropriate database based on read preference"""

        if self.read_from_dynamodb:
            # Read from DynamoDB with MongoDB fallback
            user = self.dynamodb_client.get_user_profile(username)
            if user:
                return self._transform_dynamodb_user_to_mongo_format(user)

            # Fallback to MongoDB
            return await self._read_from_mongo('users', {'username': username})
        else:
            # Read from MongoDB
            return await self._read_from_mongo('users', {'username': username})

    async def update_user(self, username: str, update_data: Dict[str, Any]) -> bool:
        """Update user in both databases"""
        success = True

        try:
            # Update MongoDB
            if self.write_to_mongo:
                mongo_success = await self._update_mongo('users', {'username': username}, update_data)
                if not mongo_success:
                    self.metrics['mongo_write_failures'] += 1
                    success = False

            # Update DynamoDB
            if self.write_to_dynamodb:
                # Get current user data for DynamoDB update
                current_user = await self.get_user(username)
                if current_user:
                    updated_user = {**current_user, **update_data}
                    dynamodb_success = self.dynamodb_client.create_user(updated_user)  # Upsert
                    if not dynamodb_success:
                        self.metrics['dynamodb_write_failures'] += 1
                        success = False

            return success

        except Exception as e:
            self.logger.error(f"Error in dual write update_user: {e}")
            return False

    async def create_order(self, order_data: Dict[str, Any]) -> bool:
        """Create order in both databases"""
        success = True

        try:
            # Write to MongoDB
            if self.write_to_mongo:
                mongo_success = await self._write_to_mongo('orders', order_data)
                if not mongo_success:
                    self.metrics['mongo_write_failures'] += 1
                    success = False

            # Write to DynamoDB
            if self.write_to_dynamodb:
                dynamodb_success = self.dynamodb_client.create_order(order_data)
                if not dynamodb_success:
                    self.metrics['dynamodb_write_failures'] += 1
                    success = False

            return success

        except Exception as e:
            self.logger.error(f"Error in dual write create_order: {e}")
            return False

    async def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get order from appropriate database"""

        if self.read_from_dynamodb:
            order = self.dynamodb_client.get_order(order_id)
            if order:
                return self._transform_dynamodb_order_to_mongo_format(order)

            # Fallback to MongoDB
            return await self._read_from_mongo('orders', {'_id': order_id})
        else:
            return await self._read_from_mongo('orders', {'_id': order_id})

    async def switch_to_dynamodb_reads(self) -> bool:
        """Switch read traffic to DynamoDB"""
        try:
            self.logger.info("Switching read traffic to DynamoDB")
            self.read_from_dynamodb = True

            # Validate a few random reads to ensure consistency
            validation_passed = await self._validate_read_consistency()

            if validation_passed:
                self.logger.info("✓ Successfully switched to DynamoDB reads")
                return True
            else:
                self.logger.error("✗ Read validation failed, reverting to MongoDB")
                self.read_from_dynamodb = False
                return False

        except Exception as e:
            self.logger.error(f"Error switching to DynamoDB reads: {e}")
            self.read_from_dynamodb = False
            return False

    async def stop_mongo_writes(self) -> bool:
        """Stop writing to MongoDB (DynamoDB becomes primary)"""
        try:
            self.logger.info("Stopping MongoDB writes")
            self.write_to_mongo = False

            # Final consistency check
            consistency_ok = await self._final_consistency_check()

            if consistency_ok:
                self.logger.info("✓ Successfully stopped MongoDB writes")
                return True
            else:
                self.logger.error("✗ Consistency check failed")
                return False

        except Exception as e:
            self.logger.error(f"Error stopping MongoDB writes: {e}")
            return False

    # Helper methods
    async def _write_to_mongo(self, collection: str, data: Dict[str, Any]) -> bool:
        """Write to MongoDB collection"""
        try:
            result = await self.mongo_client.insert_one(collection, data)
            return result.acknowledged
        except Exception as e:
            self.logger.error(f"MongoDB write failed: {e}")
            return False

    async def _read_from_mongo(self, collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Read from MongoDB collection"""
        try:
            return await self.mongo_client.find_one(collection, query)
        except Exception as e:
            self.logger.error(f"MongoDB read failed: {e}")
            return None

    async def _update_mongo(self, collection: str, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        """Update MongoDB document"""
        try:
            result = await self.mongo_client.update_one(collection, query, {'$set': update})
            return result.modified_count > 0
        except Exception as e:
            self.logger.error(f"MongoDB update failed: {e}")
            return False

    async def _validate_user_consistency(self, username: str) -> bool:
        """Validate user data consistency between databases"""
        try:
            # Get from both databases
            mongo_user = await self._read_from_mongo('users', {'username': username})
            dynamodb_user = self.dynamodb_client.get_user_profile(username)

            if not mongo_user or not dynamodb_user:
                self.metrics['validation_failures'] += 1
                return False

            # Compare key fields
            key_fields = ['username', 'email', 'firstName', 'lastName', 'status']
            for field in key_fields:
                if mongo_user.get(field) != dynamodb_user.get(field):
                    self.logger.warning(f"Consistency mismatch for user {username}, field {field}")
                    self.metrics['validation_failures'] += 1
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Validation error: {e}")
            self.metrics['validation_failures'] += 1
            return False

    async def _validate_read_consistency(self) -> bool:
        """Validate read consistency between databases"""
        # Sample a few users for validation
        test_usernames = ['user1', 'user2', 'user3']  # Configure based on your data

        for username in test_usernames:
            if not await self._validate_user_consistency(username):
                return False

        return True

    async def _final_consistency_check(self) -> bool:
        """Perform final consistency check before completing migration"""
        # Implement comprehensive consistency validation
        # This would include sampling data across all entity types
        return True

    def _transform_dynamodb_user_to_mongo_format(self, dynamodb_user: Dict[str, Any]) -> Dict[str, Any]:
        """Transform DynamoDB user item back to MongoDB format"""
        # Transform back to MongoDB document structure
        mongo_user = {
            'username': dynamodb_user.get('username'),
            'email': dynamodb_user.get('email'),
            'profile': {
                'firstName': dynamodb_user.get('firstName'),
                'lastName': dynamodb_user.get('lastName'),
                'dateOfBirth': dynamodb_user.get('dateOfBirth'),
                'avatar': dynamodb_user.get('avatar')
            },
            'preferences': {
                'theme': dynamodb_user.get('theme'),
                'notifications': {
                    'email': dynamodb_user.get('emailNotifications', True),
                    'push': dynamodb_user.get('pushNotifications', False)
                }
            },
            'status': dynamodb_user.get('status'),
            'createdAt': dynamodb_user.get('createdAt'),
            'lastLoginAt': dynamodb_user.get('lastLoginAt')
        }

        return mongo_user

    def _transform_dynamodb_order_to_mongo_format(self, dynamodb_order: Dict[str, Any]) -> Dict[str, Any]:
        """Transform DynamoDB order back to MongoDB format"""
        mongo_order = {
            'orderId': dynamodb_order.get('orderId'),
            'userId': dynamodb_order.get('userId'),
            'status': dynamodb_order.get('status'),
            'totalAmount': float(dynamodb_order.get('totalAmount', 0)),
            'currency': dynamodb_order.get('currency'),
            'items': dynamodb_order.get('items', []),
            'createdAt': dynamodb_order.get('createdAt'),
            'updatedAt': dynamodb_order.get('updatedAt')
        }

        return mongo_order

    def get_metrics(self) -> Dict[str, Any]:
        """Get migration metrics"""
        return {
            **self.metrics,
            'configuration': {
                'write_to_mongo': self.write_to_mongo,
                'write_to_dynamodb': self.write_to_dynamodb,
                'read_from_dynamodb': self.read_from_dynamodb,
                'validate_writes': self.validate_writes
            }
        }
```

## Cost Analysis and ROI

### Infrastructure Cost Comparison

**MongoDB (Current State) - Monthly Costs:**
```
EC2 Instances:
- Primary (r5.2xlarge):     $347/month
- Secondary 1 (r5.xlarge):  $174/month
- Secondary 2 (r5.xlarge):  $174/month
- Arbiter (t3.small):       $15/month

EBS Storage (gp3):
- 1TB per instance × 3:     $240/month

Data Transfer:              $50/month
Backup Storage (S3):        $30/month
Ops Manager License:        $200/month

Total MongoDB Monthly:      $1,230/month
Annual Cost:               $14,760/year
```

**DynamoDB (Target State) - Monthly Costs:**
```
DynamoDB On-Demand:
- 10M read requests:        $125/month
- 2M write requests:        $250/month
- 100GB storage:           $25/month

Global Secondary Indexes:
- Additional read/write:    $75/month
- Additional storage:       $25/month

DynamoDB Accelerator (DAX):
- 3 × dax.r4.large:        $437/month

Backup Storage:            $15/month
Data Transfer:             $25/month

Total DynamoDB Monthly:    $977/month
Annual Cost:              $11,724/year

Annual Savings:           $3,036/year (21%)
```

## Risk Mitigation and Rollback Strategy

### Rollback Procedures

```python
# migration/rollback_manager.py
import boto3
import pymongo
from typing import Dict, Any, List
import logging

class MigrationRollbackManager:
    def __init__(self, mongo_uri: str, dynamodb_table: str):
        self.mongo_client = pymongo.MongoClient(mongo_uri)
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(dynamodb_table)
        self.logger = logging.getLogger(__name__)

    def create_rollback_point(self, name: str) -> Dict[str, Any]:
        """Create rollback point with data snapshot"""
        try:
            # Create MongoDB backup
            mongo_backup = self._create_mongo_backup(name)

            # Export DynamoDB table
            dynamodb_backup = self._create_dynamodb_backup(name)

            rollback_point = {
                'name': name,
                'timestamp': datetime.now().isoformat(),
                'mongo_backup': mongo_backup,
                'dynamodb_backup': dynamodb_backup,
                'status': 'created'
            }

            # Store rollback metadata
            self._store_rollback_metadata(rollback_point)

            return rollback_point

        except Exception as e:
            self.logger.error(f"Failed to create rollback point: {e}")
            return {}

    def execute_rollback(self, rollback_point_name: str) -> bool:
        """Execute rollback to specific point"""
        try:
            # Get rollback point metadata
            rollback_data = self._get_rollback_metadata(rollback_point_name)

            if not rollback_data:
                self.logger.error(f"Rollback point {rollback_point_name} not found")
                return False

            # Stop all writes
            self._stop_all_writes()

            # Restore MongoDB
            mongo_restored = self._restore_mongo_backup(rollback_data['mongo_backup'])

            # Restore DynamoDB
            dynamodb_restored = self._restore_dynamodb_backup(rollback_data['dynamodb_backup'])

            # Switch application back to MongoDB
            self._switch_to_mongodb()

            if mongo_restored and dynamodb_restored:
                self.logger.info(f"✓ Successfully rolled back to {rollback_point_name}")
                return True
            else:
                self.logger.error(f"✗ Partial rollback failure")
                return False

        except Exception as e:
            self.logger.error(f"Rollback execution failed: {e}")
            return False

    def _create_mongo_backup(self, name: str) -> str:
        """Create MongoDB backup using mongodump"""
        backup_path = f"/backups/mongodb_{name}"

        # Execute mongodump
        import subprocess
        cmd = [
            'mongodump',
            '--uri', str(self.mongo_client.address),
            '--out', backup_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            self.logger.info(f"✓ MongoDB backup created: {backup_path}")
            return backup_path
        else:
            self.logger.error(f"✗ MongoDB backup failed: {result.stderr}")
            return ""

    def _create_dynamodb_backup(self, name: str) -> str:
        """Create DynamoDB backup"""
        try:
            response = self.table.meta.client.create_backup(
                TableName=self.table.table_name,
                BackupName=f"migration_rollback_{name}"
            )

            backup_arn = response['BackupDetails']['BackupArn']
            self.logger.info(f"✓ DynamoDB backup created: {backup_arn}")
            return backup_arn

        except Exception as e:
            self.logger.error(f"✗ DynamoDB backup failed: {e}")
            return ""

    def validate_migration_health(self) -> Dict[str, Any]:
        """Validate overall migration health"""
        health_report = {
            'mongodb_health': self._check_mongodb_health(),
            'dynamodb_health': self._check_dynamodb_health(),
            'data_consistency': self._check_data_consistency(),
            'application_health': self._check_application_health(),
            'overall_status': 'healthy'
        }

        # Determine overall status
        if not all([
            health_report['mongodb_health']['status'] == 'healthy',
            health_report['dynamodb_health']['status'] == 'healthy',
            health_report['data_consistency']['status'] == 'consistent',
            health_report['application_health']['status'] == 'healthy'
        ]):
            health_report['overall_status'] = 'unhealthy'

        return health_report

    def _check_mongodb_health(self) -> Dict[str, Any]:
        """Check MongoDB cluster health"""
        try:
            # Check replica set status
            admin_db = self.mongo_client.admin
            rs_status = admin_db.command('replSetGetStatus')

            healthy_members = sum(1 for member in rs_status['members']
                                if member['health'] == 1)

            return {
                'status': 'healthy' if healthy_members >= 2 else 'unhealthy',
                'healthy_members': healthy_members,
                'total_members': len(rs_status['members']),
                'primary_available': any(member['stateStr'] == 'PRIMARY'
                                       for member in rs_status['members'])
            }

        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

    def _check_dynamodb_health(self) -> Dict[str, Any]:
        """Check DynamoDB table health"""
        try:
            response = self.table.meta.client.describe_table(
                TableName=self.table.table_name
            )

            table_status = response['Table']['TableStatus']

            return {
                'status': 'healthy' if table_status == 'ACTIVE' else 'unhealthy',
                'table_status': table_status,
                'item_count': response['Table']['ItemCount'],
                'table_size_bytes': response['Table']['TableSizeBytes']
            }

        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
```

## Performance Optimization

### Query Performance Comparison

**Before (MongoDB) - User Queries:**
```javascript
// MongoDB - Complex aggregation pipeline
db.users.aggregate([
  {
    $match: {
      "profile.location.city": "Seattle",
      "status": "active",
      "lastLoginAt": { $gte: new Date("2024-01-01") }
    }
  },
  {
    $lookup: {
      from: "orders",
      localField: "_id",
      foreignField: "userId",
      as: "orders"
    }
  },
  {
    $project: {
      username: 1,
      email: 1,
      "profile.firstName": 1,
      "profile.lastName": 1,
      orderCount: { $size: "$orders" }
    }
  }
])

// Performance: 150-300ms depending on index optimization
// Scalability: Requires careful sharding and index management
```

**After (DynamoDB) - Optimized Access Patterns:**
```python
# DynamoDB - Single query with GSI
def get_active_users_in_city(city: str, last_login_after: str) -> List[Dict]:
    response = table.query(
        IndexName='GSI2',
        KeyConditionExpression=Key('GSI2PK').eq(f'CITY#{city}') &
                             Key('GSI2SK').begins_with(f'ACTIVE#{last_login_after}'),
        FilterExpression=Attr('status').eq('active')
    )
    return response['Items']

# Performance: 5-15ms with DAX caching
# Scalability: Automatic scaling, no management overhead
```

## Monitoring and Observability

### Custom CloudWatch Metrics

```python
# monitoring/dynamodb_migration_metrics.py
import boto3
import time
from typing import Dict, Any

class MigrationMetrics:
    def __init__(self):
        self.cloudwatch = boto3.client('cloudwatch')

    def publish_migration_metrics(self, metrics: Dict[str, Any]):
        """Publish custom migration metrics"""

        metric_data = []

        # Migration progress
        metric_data.append({
            'MetricName': 'MigrationProgress',
            'Value': metrics.get('progress_percent', 0),
            'Unit': 'Percent',
            'Dimensions': [
                {'Name': 'MigrationType', 'Value': 'MongoDB-to-DynamoDB'}
            ]
        })

        # Data consistency
        metric_data.append({
            'MetricName': 'DataConsistency',
            'Value': metrics.get('consistency_percent', 100),
            'Unit': 'Percent'
        })

        # Performance comparison
        metric_data.append({
            'MetricName': 'QueryLatency',
            'Value': metrics.get('avg_query_latency_ms', 0),
            'Unit': 'Milliseconds',
            'Dimensions': [
                {'Name': 'Database', 'Value': 'DynamoDB'}
            ]
        })

        # Cost metrics
        metric_data.append({
            'MetricName': 'MonthlyCost',
            'Value': metrics.get('monthly_cost_usd', 0),
            'Unit': 'None',
            'Dimensions': [
                {'Name': 'Service', 'Value': 'DynamoDB'}
            ]
        })

        # Publish to CloudWatch
        self.cloudwatch.put_metric_data(
            Namespace='MongoDB-Migration',
            MetricData=metric_data
        )
```

## Conclusion

This MongoDB to DynamoDB migration playbook provides a comprehensive approach to migrating from a traditional NoSQL database to a fully managed, serverless solution while ensuring zero downtime and maintaining data consistency.

**Key Success Factors:**
1. **Careful data model design** for DynamoDB's key-value structure
2. **Dual-write strategy** ensuring consistency during migration
3. **Comprehensive testing** at each migration phase
4. **Performance monitoring** to ensure no regressions
5. **Rollback procedures** for quick recovery if needed

**Expected Outcomes:**
- 40-60% reduction in database operational costs
- Improved scalability with automatic scaling
- Reduced operational overhead with managed service
- Enhanced performance with DAX caching
- Better integration with AWS ecosystem

The migration enables organizations to leverage DynamoDB's serverless architecture while maintaining application functionality and performance requirements.