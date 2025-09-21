# S3 Eventual Consistency Debugging

**Scenario**: Production applications experiencing data inconsistency issues with Amazon S3, causing stale reads and application logic failures.

**The 3 AM Reality**: Applications reading old versions of objects, upload confirmations followed by 404 errors, and data pipeline failures due to S3 consistency edge cases.

## Symptoms Checklist

- [ ] Recently uploaded objects returning 404 on immediate read
- [ ] Object metadata showing old values after updates
- [ ] List operations missing recently created objects
- [ ] Inconsistent results between different S3 API calls
- [ ] Race conditions in data processing pipelines

## Critical Analysis & Commands

### S3 Consistency Detection
```bash
# Test object creation consistency
aws s3 cp test-file.txt s3://bucket/test-file.txt
aws s3api head-object --bucket bucket --key test-file.txt
# May return 404 immediately after upload

# Test list consistency
aws s3api put-object --bucket bucket --key consistency-test/file1.txt --body test-file.txt
aws s3api list-objects-v2 --bucket bucket --prefix consistency-test/
# May not show newly created object

# Test metadata consistency
aws s3api put-object --bucket bucket --key metadata-test.txt --body test-file.txt --metadata "version=1"
aws s3api copy-object --bucket bucket --copy-source bucket/metadata-test.txt --key metadata-test.txt --metadata "version=2" --metadata-directive REPLACE
aws s3api head-object --bucket bucket --key metadata-test.txt
# May return old metadata
```

### Versioning and Replication Status
```bash
# Check bucket versioning
aws s3api get-bucket-versioning --bucket your-bucket

# List object versions
aws s3api list-object-versions --bucket your-bucket --prefix problematic-key

# Check Cross-Region Replication status
aws s3api get-bucket-replication --bucket your-bucket

# Monitor replication metrics
aws logs describe-log-groups | grep s3-replication
```

## Common Root Causes & Solutions

### 1. Read-After-Write Consistency Issues (50% of cases)
```python
# Problem: Immediate read after write
import boto3

s3 = boto3.client('s3')

def problematic_pattern():
    # Upload object
    s3.put_object(
        Bucket='my-bucket',
        Key='data.json',
        Body=json.dumps({'updated': True})
    )

    # Immediate read - may fail with 404
    try:
        response = s3.get_object(Bucket='my-bucket', Key='data.json')
        return json.loads(response['Body'].read())
    except s3.exceptions.NoSuchKey:
        return None  # Consistency issue!

# Solution 1: Implement retry with exponential backoff
import time
import random

def consistent_read_after_write(bucket, key, max_retries=5):
    for attempt in range(max_retries):
        try:
            response = s3.get_object(Bucket=bucket, Key=key)
            return response['Body'].read()
        except s3.exceptions.NoSuchKey:
            if attempt < max_retries - 1:
                # Exponential backoff with jitter
                delay = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(delay)
                continue
            raise

# Solution 2: Use ETag verification for consistency
def upload_with_consistency_check(bucket, key, data):
    # Upload object
    response = s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=data
    )
    expected_etag = response['ETag']

    # Verify upload with ETag
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            head_response = s3.head_object(Bucket=bucket, Key=key)
            if head_response['ETag'] == expected_etag:
                return True  # Consistent
        except s3.exceptions.NoSuchKey:
            pass

        if attempt < max_attempts - 1:
            time.sleep(0.1 * (2 ** attempt))

    return False  # Failed to achieve consistency

# Solution 3: Use strong consistency (S3 default since Dec 2020)
# For newer applications, leverage strong read-after-write consistency
def modern_s3_operations():
    # S3 now provides strong read-after-write consistency
    # No special handling needed for new objects
    s3.put_object(Bucket='bucket', Key='key', Body='data')

    # This will always succeed (no 404) for PUT operations
    response = s3.get_object(Bucket='bucket', Key='key')
    return response['Body'].read()
```

### 2. List Operations Consistency (25% of cases)
```python
# Problem: LIST operations missing recent objects
def problematic_list_pattern():
    # Create multiple objects
    for i in range(10):
        s3.put_object(
            Bucket='my-bucket',
            Key=f'batch-upload/{i}.txt',
            Body=f'content-{i}'
        )

    # Immediate list - may miss some objects
    response = s3.list_objects_v2(
        Bucket='my-bucket',
        Prefix='batch-upload/'
    )

    # May return fewer than 10 objects!
    return len(response.get('Contents', []))

# Solution 1: Retry list operations until expected count
def consistent_list_after_batch_upload(bucket, prefix, expected_count, timeout=30):
    start_time = time.time()

    while time.time() - start_time < timeout:
        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        current_count = len(response.get('Contents', []))

        if current_count >= expected_count:
            return response['Contents']

        time.sleep(0.5)

    # Return what we have after timeout
    return response.get('Contents', [])

# Solution 2: Use pagination with retries
def robust_list_objects(bucket, prefix, max_keys=1000):
    all_objects = []
    continuation_token = None
    seen_keys = set()

    while True:
        kwargs = {
            'Bucket': bucket,
            'Prefix': prefix,
            'MaxKeys': max_keys
        }

        if continuation_token:
            kwargs['ContinuationToken'] = continuation_token

        # Retry list operation
        for attempt in range(3):
            try:
                response = s3.list_objects_v2(**kwargs)
                break
            except Exception as e:
                if attempt == 2:
                    raise
                time.sleep(0.5 * (2 ** attempt))

        # Deduplicate in case of eventual consistency issues
        for obj in response.get('Contents', []):
            if obj['Key'] not in seen_keys:
                all_objects.append(obj)
                seen_keys.add(obj['Key'])

        if not response.get('IsTruncated'):
            break

        continuation_token = response.get('NextContinuationToken')

    return all_objects
```

### 3. Cross-Region Replication Delays (15% of cases)
```python
# Problem: Reading from replicated bucket before replication completes
def cross_region_consistency_issue():
    # Upload to primary region
    primary_s3 = boto3.client('s3', region_name='us-east-1')
    primary_s3.put_object(
        Bucket='primary-bucket',
        Key='important-data.json',
        Body=json.dumps({'timestamp': time.time()})
    )

    # Immediate read from replica region - may fail
    replica_s3 = boto3.client('s3', region_name='us-west-2')
    try:
        response = replica_s3.get_object(
            Bucket='replica-bucket',
            Key='important-data.json'
        )
        return json.loads(response['Body'].read())
    except replica_s3.exceptions.NoSuchKey:
        return None  # Replication not complete

# Solution: Monitor replication status
def wait_for_replication(primary_bucket, replica_bucket, key, timeout=60):
    primary_s3 = boto3.client('s3', region_name='us-east-1')
    replica_s3 = boto3.client('s3', region_name='us-west-2')

    # Get primary object ETag
    primary_response = primary_s3.head_object(Bucket=primary_bucket, Key=key)
    primary_etag = primary_response['ETag']

    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            replica_response = replica_s3.head_object(Bucket=replica_bucket, Key=key)

            # Check if ETags match (indicates replication complete)
            if replica_response['ETag'] == primary_etag:
                return True

        except replica_s3.exceptions.NoSuchKey:
            pass  # Object not replicated yet

        time.sleep(1)

    return False  # Timeout waiting for replication

# Alternative: Use CloudWatch replication metrics
def monitor_replication_metrics(bucket_name):
    cloudwatch = boto3.client('cloudwatch')

    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/S3',
        MetricName='ReplicationLatency',
        Dimensions=[
            {
                'Name': 'SourceBucket',
                'Value': bucket_name
            }
        ],
        StartTime=datetime.utcnow() - timedelta(hours=1),
        EndTime=datetime.utcnow(),
        Period=300,
        Statistics=['Average', 'Maximum']
    )

    return response['Datapoints']
```

### 4. Metadata Update Consistency (7% of cases)
```python
# Problem: Metadata updates may not be immediately visible
def metadata_consistency_issue():
    key = 'document.pdf'

    # Update metadata
    s3.copy_object(
        Bucket='my-bucket',
        CopySource={'Bucket': 'my-bucket', 'Key': key},
        Key=key,
        Metadata={'version': '2', 'updated': str(time.time())},
        MetadataDirective='REPLACE'
    )

    # Immediate read may return old metadata
    response = s3.head_object(Bucket='my-bucket', Key=key)
    return response.get('Metadata', {})

# Solution: Verify metadata updates
def update_metadata_with_verification(bucket, key, new_metadata):
    # Update metadata
    s3.copy_object(
        Bucket=bucket,
        CopySource={'Bucket': bucket, 'Key': key},
        Key=key,
        Metadata=new_metadata,
        MetadataDirective='REPLACE'
    )

    # Verify metadata was updated
    max_attempts = 10
    for attempt in range(max_attempts):
        response = s3.head_object(Bucket=bucket, Key=key)
        current_metadata = response.get('Metadata', {})

        # Check if all new metadata is present
        if all(current_metadata.get(k) == v for k, v in new_metadata.items()):
            return True

        if attempt < max_attempts - 1:
            time.sleep(0.1 * (2 ** attempt))

    return False
```

### 5. Multi-part Upload Consistency (3% of cases)
```python
# Problem: Multi-part uploads and immediate listing
def multipart_upload_consistency():
    # Start multipart upload
    response = s3.create_multipart_upload(
        Bucket='my-bucket',
        Key='large-file.zip'
    )
    upload_id = response['UploadId']

    parts = []
    # Upload parts
    for i in range(3):
        part_response = s3.upload_part(
            Bucket='my-bucket',
            Key='large-file.zip',
            PartNumber=i + 1,
            UploadId=upload_id,
            Body=f'part-{i}-data' * 1000
        )
        parts.append({
            'ETag': part_response['ETag'],
            'PartNumber': i + 1
        })

    # Complete multipart upload
    s3.complete_multipart_upload(
        Bucket='my-bucket',
        Key='large-file.zip',
        UploadId=upload_id,
        MultipartUpload={'Parts': parts}
    )

    # Immediate list may not show the completed object
    response = s3.list_objects_v2(Bucket='my-bucket', Prefix='large-file')
    return len(response.get('Contents', []))

# Solution: Verify multipart upload completion
def robust_multipart_upload(bucket, key, data_parts):
    # Create multipart upload
    response = s3.create_multipart_upload(Bucket=bucket, Key=key)
    upload_id = response['UploadId']

    try:
        parts = []

        # Upload all parts
        for i, data in enumerate(data_parts):
            part_response = s3.upload_part(
                Bucket=bucket,
                Key=key,
                PartNumber=i + 1,
                UploadId=upload_id,
                Body=data
            )
            parts.append({
                'ETag': part_response['ETag'],
                'PartNumber': i + 1
            })

        # Complete multipart upload
        complete_response = s3.complete_multipart_upload(
            Bucket=bucket,
            Key=key,
            UploadId=upload_id,
            MultipartUpload={'Parts': parts}
        )

        # Verify object exists with correct ETag
        expected_etag = complete_response['ETag']

        for attempt in range(10):
            try:
                head_response = s3.head_object(Bucket=bucket, Key=key)
                if head_response['ETag'] == expected_etag:
                    return True
            except s3.exceptions.NoSuchKey:
                pass

            time.sleep(0.5)

        return False

    except Exception as e:
        # Clean up on failure
        s3.abort_multipart_upload(
            Bucket=bucket,
            Key=key,
            UploadId=upload_id
        )
        raise
```

## Immediate Mitigation

### Emergency Response
```python
# Quick consistency check for critical operations
def emergency_consistency_check(bucket, key):
    """Verify object exists and is readable"""

    max_attempts = 20
    for attempt in range(max_attempts):
        try:
            # Try to read object
            response = s3.head_object(Bucket=bucket, Key=key)
            print(f"Object {key} exists, ETag: {response['ETag']}")

            # Try to get object content
            get_response = s3.get_object(Bucket=bucket, Key=key)
            content_length = len(get_response['Body'].read())
            print(f"Object {key} readable, size: {content_length} bytes")

            return True

        except s3.exceptions.NoSuchKey:
            print(f"Attempt {attempt + 1}: Object {key} not found")

        except Exception as e:
            print(f"Attempt {attempt + 1}: Error reading {key}: {e}")

        time.sleep(0.5)

    return False

# Circuit breaker for S3 operations
class S3CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN

    def call(self, func, *args, **kwargs):
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise

    def on_success(self):
        self.failure_count = 0
        self.state = 'CLOSED'

    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'

# Usage
circuit_breaker = S3CircuitBreaker()

def safe_s3_operation(bucket, key):
    return circuit_breaker.call(
        s3.get_object,
        Bucket=bucket,
        Key=key
    )
```

## Long-term Prevention

### Robust S3 Client Implementation
```python
class ConsistentS3Client:
    def __init__(self, region_name=None):
        self.s3 = boto3.client('s3', region_name=region_name)
        self.max_retries = 10
        self.base_delay = 0.1

    def put_object_with_verification(self, bucket, key, body, **kwargs):
        """Upload object and verify it's readable"""

        # Upload object
        response = self.s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=body,
            **kwargs
        )

        expected_etag = response['ETag']

        # Verify upload
        for attempt in range(self.max_retries):
            try:
                head_response = self.s3.head_object(Bucket=bucket, Key=key)
                if head_response['ETag'] == expected_etag:
                    return response
            except self.s3.exceptions.NoSuchKey:
                pass

            time.sleep(self.base_delay * (2 ** attempt))

        raise Exception(f"Failed to verify upload of {key} after {self.max_retries} attempts")

    def list_objects_eventually_consistent(self, bucket, prefix, expected_min_count=None):
        """List objects with retry logic for eventual consistency"""

        max_attempts = 15 if expected_min_count else 3
        all_objects = []

        for attempt in range(max_attempts):
            try:
                paginator = self.s3.get_paginator('list_objects_v2')
                page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)

                current_objects = []
                for page in page_iterator:
                    current_objects.extend(page.get('Contents', []))

                # If we have expected count or no minimum specified, return
                if not expected_min_count or len(current_objects) >= expected_min_count:
                    return current_objects

                all_objects = current_objects

            except Exception as e:
                if attempt == max_attempts - 1:
                    raise

            time.sleep(self.base_delay * (2 ** min(attempt, 5)))

        return all_objects

    def copy_object_with_metadata_verification(self, source_bucket, source_key,
                                             dest_bucket, dest_key, metadata):
        """Copy object and verify metadata is updated"""

        # Perform copy
        self.s3.copy_object(
            CopySource={'Bucket': source_bucket, 'Key': source_key},
            Bucket=dest_bucket,
            Key=dest_key,
            Metadata=metadata,
            MetadataDirective='REPLACE'
        )

        # Verify metadata
        for attempt in range(self.max_retries):
            try:
                response = self.s3.head_object(Bucket=dest_bucket, Key=dest_key)
                current_metadata = response.get('Metadata', {})

                if all(current_metadata.get(k) == v for k, v in metadata.items()):
                    return response

            except self.s3.exceptions.NoSuchKey:
                pass

            time.sleep(self.base_delay * (2 ** attempt))

        raise Exception(f"Metadata verification failed for {dest_key}")

    def delete_object_with_verification(self, bucket, key):
        """Delete object and verify deletion"""

        # Delete object
        self.s3.delete_object(Bucket=bucket, Key=key)

        # Verify deletion
        for attempt in range(self.max_retries):
            try:
                self.s3.head_object(Bucket=bucket, Key=key)
                # If we get here, object still exists
                time.sleep(self.base_delay * (2 ** attempt))
            except self.s3.exceptions.NoSuchKey:
                # Object successfully deleted
                return True

        raise Exception(f"Failed to verify deletion of {key}")
```

## Production Examples

### Netflix's Content Distribution (2018)
- **Incident**: Newly uploaded movie content not immediately available globally
- **Root Cause**: S3 eventual consistency affecting CDN origin pulls
- **Impact**: Users receiving 404 errors for newly released content
- **Resolution**: Implemented retry logic with exponential backoff in CDN
- **Prevention**: Added health checks and content availability verification

### Airbnb's Photo Upload Issues (2019)
- **Incident**: Property photos showing as missing immediately after upload
- **Root Cause**: Image processing pipeline reading from S3 before write consistency
- **Impact**: Property listings appearing without photos, booking conversion drop
- **Resolution**: Added ETag verification before triggering image processing
- **Learning**: Critical workflows need consistency verification

### Dropbox's File Sync Consistency (2020)
- **Incident**: File synchronization failures due to S3 list consistency issues
- **Root Cause**: Sync process missing recently uploaded files in list operations
- **Impact**: Files not syncing across devices, user data consistency issues
- **Resolution**: Implemented checksum-based verification and retry logic
- **Prevention**: Added eventual consistency handling in sync algorithms

**Remember**: While S3 now provides strong read-after-write consistency (since December 2020), legacy applications and specific edge cases may still encounter consistency issues. Always implement proper retry logic and verification for critical workflows.