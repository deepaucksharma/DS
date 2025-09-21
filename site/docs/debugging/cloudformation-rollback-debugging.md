# CloudFormation Rollback Debugging: Stack Failure Analysis Guide

## Executive Summary

CloudFormation rollback failures affect 30% of infrastructure deployments and can leave resources in inconsistent states. This guide provides systematic debugging approaches for failed stack deployments, rollback issues, and resource dependency problems.

## Common CloudFormation Error Patterns

### Stack Rollback Investigation
```bash
# Check stack status and events
aws cloudformation describe-stacks --stack-name my-stack

# Get detailed stack events
aws cloudformation describe-stack-events --stack-name my-stack | head -20

# Check for failed resources
aws cloudformation describe-stack-resources --stack-name my-stack --logical-resource-id FailedResource

# Monitor real-time stack events
aws logs tail /aws/cloudformation/my-stack --follow
```

### Resource Dependency Analysis
```bash
# Visualize stack template dependencies
aws cloudformation get-template --stack-name my-stack --query 'TemplateBody' > template.json

# Check resource import status
aws cloudformation describe-stack-resources --stack-name my-stack | jq '.StackResources[] | select(.ResourceStatus | contains("FAILED"))'

# Analyze resource creation order
aws cloudformation describe-stack-events --stack-name my-stack | jq '.StackEvents[] | {Time: .Timestamp, Resource: .LogicalResourceId, Status: .ResourceStatus, Reason: .ResourceStatusReason}' | head -20
```

## Root Cause Investigation

### Permission Issues
```yaml
# Common IAM permission problems in CloudFormation
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-unique-bucket-name

# Error: Access Denied creating bucket
# Solution: Ensure CloudFormation service role has proper permissions
```

### Resource Limit Errors
```bash
# Check service quotas that might cause failures
aws service-quotas get-service-quota --service-code ec2 --quota-code L-1216C47A  # On-Demand instances
aws service-quotas get-service-quota --service-code elasticloadbalancing --quota-code L-E9E9831D  # ALBs per region

# Check current usage vs limits
aws ec2 describe-instances --query 'Reservations[].Instances[?State.Name==`running`] | length(@)'
```

### Dependency and Timing Issues
```yaml
# Problematic resource dependencies
Resources:
  MyVPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16

  MySubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref MyVPC  # Proper dependency
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: us-east-1a

  MyInstance:
    Type: AWS::EC2::Instance
    DependsOn: MyNATGateway  # Explicit dependency when needed
    Properties:
      SubnetId: !Ref MySubnet
      ImageId: ami-12345678
```

## Debugging Techniques

### Stack Drift Detection
```bash
# Detect configuration drift
aws cloudformation detect-stack-drift --stack-name my-stack

# Get drift detection results
aws cloudformation describe-stack-drift-detection-status --stack-drift-detection-id drift-detection-id

# Check individual resource drift
aws cloudformation describe-stack-resource-drifts --stack-name my-stack
```

### Rollback Analysis Script
```bash
#!/bin/bash
# cloudformation-debug.sh

STACK_NAME="$1"

if [ -z "$STACK_NAME" ]; then
    echo "Usage: $0 <stack-name>"
    exit 1
fi

echo "🔍 Debugging CloudFormation Stack: $STACK_NAME"

# Check stack status
STACK_STATUS=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --query 'Stacks[0].StackStatus' --output text)
echo "Stack Status: $STACK_STATUS"

# Get failed resources
echo "\\nFailed Resources:"
aws cloudformation describe-stack-events --stack-name $STACK_NAME \\
  --query 'StackEvents[?ResourceStatus==`CREATE_FAILED` || ResourceStatus==`UPDATE_FAILED` || ResourceStatus==`DELETE_FAILED`].[Timestamp,LogicalResourceId,ResourceStatus,ResourceStatusReason]' \\
  --output table

# Check for circular dependencies
echo "\\nResource Dependencies:"
aws cloudformation describe-stack-resources --stack-name $STACK_NAME \\
  --query 'StackResources[].[LogicalResourceId,ResourceType,ResourceStatus]' \\
  --output table

# Show recent events
echo "\\nRecent Stack Events (last 10):"
aws cloudformation describe-stack-events --stack-name $STACK_NAME \\
  --query 'StackEvents[:10].[Timestamp,LogicalResourceId,ResourceStatus,ResourceStatusReason]' \\
  --output table

echo "\\n✅ Debug analysis complete"
```

## Resolution Strategies

### Manual Resource Cleanup
```bash
# Clean up failed resources before retry
STACK_NAME="failed-stack"

# Get stuck resources
aws cloudformation describe-stack-resources --stack-name $STACK_NAME \\
  --query 'StackResources[?ResourceStatus==`DELETE_FAILED`].PhysicalResourceId' \\
  --output text

# Manual cleanup example for common resources
aws ec2 terminate-instances --instance-ids i-1234567890abcdef0
aws s3 rb s3://stuck-bucket --force
aws iam delete-role --role-name StuckRole

# Retry stack deletion
aws cloudformation delete-stack --stack-name $STACK_NAME
```

### Stack Recovery Procedures
```bash
# Continue rollback for stuck stacks
aws cloudformation continue-update-rollback --stack-name $STACK_NAME

# Cancel update and rollback
aws cloudformation cancel-update-stack --stack-name $STACK_NAME

# Delete and recreate stack
aws cloudformation delete-stack --stack-name $STACK_NAME
aws cloudformation wait stack-delete-complete --stack-name $STACK_NAME
aws cloudformation create-stack --stack-name $STACK_NAME --template-body file://template.yaml
```

This debugging guide provides essential techniques for resolving CloudFormation rollback and deployment issues in production AWS environments.