# S3 Access Denied Debugging: IAM and Bucket Policy Troubleshooting Guide

## Executive Summary

S3 access denied errors affect 45% of AWS deployments and are among the most frustrating AWS issues to debug. This guide provides systematic debugging approaches for IAM policies, bucket policies, ACLs, and cross-account access issues.

## Common S3 Access Denied Patterns

### Error Types and Investigation
```bash
# Common error messages
AccessDenied: Access Denied
AccessDenied: User: arn:aws:iam::123456789012:user/username is not authorized to perform: s3:GetObject
AccessDenied: Invalid according to Policy: Policy Condition failed
Forbidden: The AWS Access Key Id you provided does not exist in our records
```

### Initial Investigation Commands
```bash
# Check AWS credentials
aws sts get-caller-identity

# Test basic S3 access
aws s3 ls s3://your-bucket-name

# Get bucket policy
aws s3api get-bucket-policy --bucket your-bucket-name

# Check bucket ACL
aws s3api get-bucket-acl --bucket your-bucket-name

# Get object ACL (if accessible)
aws s3api get-object-acl --bucket your-bucket-name --key your-object-key
```

## IAM Policy Debugging

### Policy Simulation
```bash
# Simulate IAM policy for specific action
aws iam simulate-principal-policy \\
  --policy-source-arn arn:aws:iam::123456789012:user/testuser \\
  --action-names s3:GetObject \\
  --resource-arns arn:aws:s3:::my-bucket/my-object

# Simulate with context keys
aws iam simulate-principal-policy \\
  --policy-source-arn arn:aws:iam::123456789012:role/my-role \\
  --action-names s3:GetObject \\
  --resource-arns arn:aws:s3:::my-bucket/* \\
  --context-entries ContextKeyName=aws:RequestedRegion,ContextKeyValues=us-east-1,ContextKeyType=string
```

### Common IAM Policy Issues
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ProblematicPolicy",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject"
      ],
      "Resource": [
        "arn:aws:s3:::my-bucket"  // ISSUE: Missing /* for objects
      ]
    }
  ]
}

// Fixed version:
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "CorrectPolicy",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"  // Often needed for operations
      ],
      "Resource": [
        "arn:aws:s3:::my-bucket",      // For bucket operations
        "arn:aws:s3:::my-bucket/*"     // For object operations
      ]
    }
  ]
}
```

## Bucket Policy Analysis

### Policy Conflicts
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowPublicRead",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-bucket/*"
    },
    {
      "Sid": "DenyEverything",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "*",
      "Resource": "arn:aws:s3:::my-bucket/*",
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "false"
        }
      }
    }
  ]
}
```

### Debugging Cross-Account Access
```bash
# Check bucket ownership
aws s3api get-bucket-location --bucket cross-account-bucket

# Verify cross-account role assumption
aws sts assume-role \\
  --role-arn arn:aws:iam::ACCOUNT-B:role/CrossAccountRole \\
  --role-session-name test-session

# Test with assumed role credentials
export AWS_ACCESS_KEY_ID=ASIA...
export AWS_SECRET_ACCESS_KEY=...
export AWS_SESSION_TOKEN=...

aws s3 ls s3://cross-account-bucket
```

## Advanced Debugging Techniques

### CloudTrail Analysis
```bash
# Look for S3 API calls in CloudTrail
aws logs filter-log-events \\
  --log-group-name CloudTrail/S3Access \\
  --start-time 1640995200000 \\
  --filter-pattern '{ $.eventName = "GetObject" && $.errorCode = "AccessDenied" }'

# Check specific bucket events
aws logs filter-log-events \\
  --log-group-name CloudTrail/S3Access \\
  --filter-pattern '{ $.requestParameters.bucketName = "my-bucket" && $.errorCode exists }'
```

### S3 Access Analyzer
```bash
# Generate S3 access analyzer report
aws accessanalyzer create-analyzer \\
  --analyzer-name s3-access-analyzer \\
  --type ACCOUNT

# Check findings
aws accessanalyzer list-findings \\
  --analyzer-arn arn:aws:access-analyzer:region:account:analyzer/s3-access-analyzer
```

## Resolution Strategies

### Complete S3 Policy Debug Script
```bash
#!/bin/bash
# s3-access-debug.sh

BUCKET_NAME="$1"
OBJECT_KEY="$2"
IAM_ENTITY="$3"

if [ $# -lt 2 ]; then
    echo "Usage: $0 <bucket-name> <object-key> [iam-entity-arn]"
    exit 1
fi

echo "🔍 Debugging S3 access for bucket: $BUCKET_NAME"

# Check current identity
echo "Current AWS identity:"
aws sts get-caller-identity

# Check bucket existence and region
echo "\\nBucket information:"
aws s3api head-bucket --bucket $BUCKET_NAME 2>&1
BUCKET_REGION=$(aws s3api get-bucket-location --bucket $BUCKET_NAME --query 'LocationConstraint' --output text)
echo "Bucket region: $BUCKET_REGION"

# Check bucket policy
echo "\\nBucket policy:"
aws s3api get-bucket-policy --bucket $BUCKET_NAME --query 'Policy' --output text 2>/dev/null || echo "No bucket policy found"

# Check bucket ACL
echo "\\nBucket ACL:"
aws s3api get-bucket-acl --bucket $BUCKET_NAME 2>/dev/null || echo "Cannot read bucket ACL"

# Check object existence
echo "\\nObject information:"
aws s3api head-object --bucket $BUCKET_NAME --key $OBJECT_KEY 2>&1

# Test basic operations
echo "\\nTesting S3 operations:"
echo "ListBucket:"
aws s3 ls s3://$BUCKET_NAME/ --page-size 1 2>&1 | head -5

echo "GetObject:"
aws s3 cp s3://$BUCKET_NAME/$OBJECT_KEY /tmp/test-download 2>&1 || echo "GetObject failed"

# If IAM entity provided, simulate policy
if [ ! -z "$IAM_ENTITY" ]; then
    echo "\\nSimulating IAM policy for: $IAM_ENTITY"
    aws iam simulate-principal-policy \\
      --policy-source-arn $IAM_ENTITY \\
      --action-names s3:GetObject s3:ListBucket \\
      --resource-arns arn:aws:s3:::$BUCKET_NAME arn:aws:s3:::$BUCKET_NAME/$OBJECT_KEY
fi

echo "\\n✅ S3 access debug complete"
```

### S3 Policy Generator
```python
# s3_policy_generator.py
import json

def generate_s3_policy(bucket_name, actions, principals=None, conditions=None):
    """Generate S3 bucket policy with proper permissions"""

    policy = {
        "Version": "2012-10-17",
        "Statement": []
    }

    # Bucket-level permissions
    bucket_actions = [action for action in actions if not action.endswith('Object')]
    if bucket_actions:
        policy["Statement"].append({
            "Sid": "BucketPermissions",
            "Effect": "Allow",
            "Principal": principals or "*",
            "Action": bucket_actions,
            "Resource": f"arn:aws:s3:::{bucket_name}"
        })

    # Object-level permissions
    object_actions = [action for action in actions if action.endswith('Object')]
    if object_actions:
        stmt = {
            "Sid": "ObjectPermissions",
            "Effect": "Allow",
            "Principal": principals or "*",
            "Action": object_actions,
            "Resource": f"arn:aws:s3:::{bucket_name}/*"
        }

        if conditions:
            stmt["Condition"] = conditions

        policy["Statement"].append(stmt)

    return json.dumps(policy, indent=2)

# Example usage
policy = generate_s3_policy(
    bucket_name="my-secure-bucket",
    actions=["s3:ListBucket", "s3:GetObject", "s3:PutObject"],
    principals={"AWS": "arn:aws:iam::123456789012:root"},
    conditions={
        "Bool": {"aws:SecureTransport": "true"},
        "StringEquals": {"s3:x-amz-server-side-encryption": "AES256"}
    }
)

print(policy)
```

## Prevention Best Practices

### Least Privilege IAM Policy
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3ReadAccess",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:GetObjectVersion",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::app-data-bucket",
        "arn:aws:s3:::app-data-bucket/app-logs/*"
      ],
      "Condition": {
        "StringEquals": {
          "s3:ExistingObjectTag/Environment": ["production", "staging"]
        },
        "DateGreaterThan": {
          "aws:CurrentTime": "2023-01-01T00:00:00Z"
        }
      }
    }
  ]
}
```

### Monitoring and Alerting
```yaml
# CloudWatch alarm for S3 access denied errors
S3AccessDeniedAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmName: S3-Access-Denied-High
    AlarmDescription: High number of S3 access denied errors
    MetricName: 4xxErrors
    Namespace: AWS/S3
    Statistic: Sum
    Period: 300
    EvaluationPeriods: 2
    Threshold: 10
    ComparisonOperator: GreaterThanThreshold
    Dimensions:
      - Name: BucketName
        Value: !Ref MyBucket
    AlarmActions:
      - !Ref SNSTopicArn
```

This debugging guide provides systematic approaches for identifying and resolving S3 access denied issues in production AWS environments.