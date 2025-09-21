# ECS Task Failures Debugging: Container Orchestration Troubleshooting Guide

## Executive Summary

ECS task failures affect 25% of containerized AWS deployments and can cause service outages. This guide provides systematic debugging approaches for task startup failures, service scaling issues, and container health problems.

## Common ECS Task Error Patterns

### Task Failure Investigation
```bash
# Check service status and events
aws ecs describe-services --cluster my-cluster --services my-service

# Get task definition details
aws ecs describe-task-definition --task-definition my-task:1

# List failed tasks
aws ecs list-tasks --cluster my-cluster --service-name my-service --desired-status STOPPED

# Get task failure details
aws ecs describe-tasks --cluster my-cluster --tasks arn:aws:ecs:region:account:task/task-id
```

### Container Logs Analysis
```bash
# Get container logs
aws logs get-log-events --log-group-name /ecs/my-task --log-stream-name ecs/my-container/task-id

# Follow real-time logs
aws logs tail /ecs/my-task --follow

# Search for error patterns
aws logs filter-log-events --log-group-name /ecs/my-task --filter-pattern "ERROR"
```

## Root Cause Analysis

### Resource Constraint Issues
```json
// Task definition with resource constraints
{
  "family": "my-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "my-container",
      "image": "my-app:latest",
      "memory": 512,
      "memoryReservation": 256,
      "cpu": 256,
      "essential": true,
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8080/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

### Service Discovery and Load Balancing
```bash
# Check target group health
aws elbv2 describe-target-health --target-group-arn arn:aws:elasticloadbalancing:region:account:targetgroup/my-targets

# Check service discovery
aws servicediscovery list-services --filters Name=NAMESPACE_ID,Values=ns-12345

# Verify network configuration
aws ec2 describe-security-groups --group-ids sg-12345678
aws ec2 describe-subnets --subnet-ids subnet-12345678
```

### Task Placement and Scaling
```bash
# Check cluster capacity
aws ecs describe-clusters --clusters my-cluster --include STATISTICS

# Check service scaling events
aws application-autoscaling describe-scaling-activities --service-namespace ecs

# Monitor task placement
aws ecs describe-container-instances --cluster my-cluster
```

## Debugging Techniques

### ECS Task Debug Script
```bash
#!/bin/bash
# ecs-task-debug.sh

CLUSTER_NAME="$1"
SERVICE_NAME="$2"

if [ $# -lt 2 ]; then
    echo "Usage: $0 <cluster-name> <service-name>"
    exit 1
fi

echo "🔍 Debugging ECS Service: $SERVICE_NAME in cluster: $CLUSTER_NAME"

# Service status
echo "Service Status:"
aws ecs describe-services --cluster $CLUSTER_NAME --services $SERVICE_NAME \\
  --query 'services[0].{Status:status,RunningCount:runningCount,PendingCount:pendingCount,DesiredCount:desiredCount}'

# Recent service events
echo "\\nRecent Service Events:"
aws ecs describe-services --cluster $CLUSTER_NAME --services $SERVICE_NAME \\
  --query 'services[0].events[:5].[createdAt,message]' --output table

# Failed tasks
echo "\\nRecent Failed Tasks:"
FAILED_TASKS=$(aws ecs list-tasks --cluster $CLUSTER_NAME --service-name $SERVICE_NAME --desired-status STOPPED --query 'taskArns' --output text)

for task in $FAILED_TASKS; do
    echo "Task: $task"
    aws ecs describe-tasks --cluster $CLUSTER_NAME --tasks $task \\
      --query 'tasks[0].{StoppedReason:stoppedReason,StoppedAt:stoppedAt,LastStatus:lastStatus}'
    echo "Container Exit Codes:"
    aws ecs describe-tasks --cluster $CLUSTER_NAME --tasks $task \\
      --query 'tasks[0].containers[].[name,exitCode,reason]' --output table
    echo "---"
done

echo "✅ ECS debug analysis complete"
```

### Container Health Monitoring
```python
import boto3
import json
from datetime import datetime, timedelta

def monitor_ecs_health(cluster_name, service_name):
    ecs = boto3.client('ecs')
    cloudwatch = boto3.client('cloudwatch')

    # Get service details
    services = ecs.describe_services(
        cluster=cluster_name,
        services=[service_name]
    )

    service = services['services'][0]
    print(f"Service: {service['serviceName']}")
    print(f"Status: {service['status']}")
    print(f"Running/Desired: {service['runningCount']}/{service['desiredCount']}")

    # Check recent tasks
    tasks = ecs.list_tasks(
        cluster=cluster_name,
        serviceName=service_name,
        desiredStatus='RUNNING'
    )

    if tasks['taskArns']:
        task_details = ecs.describe_tasks(
            cluster=cluster_name,
            tasks=tasks['taskArns']
        )

        for task in task_details['tasks']:
            print(f"\\nTask: {task['taskArn'].split('/')[-1]}")
            print(f"Health: {task['healthStatus']}")
            print(f"Created: {task['createdAt']}")

            for container in task['containers']:
                print(f"  Container: {container['name']}")
                print(f"  Status: {container['lastStatus']}")
                if 'exitCode' in container:
                    print(f"  Exit Code: {container['exitCode']}")

# Usage
monitor_ecs_health('my-cluster', 'my-service')
```

## Resolution Strategies

### Task Definition Optimization
```json
{
  "family": "optimized-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "app",
      "image": "my-app:v1.0.0",
      "memory": 1024,
      "cpu": 512,
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/my-app",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8080/health || exit 1"],
        "interval": 30,
        "timeout": 10,
        "retries": 3,
        "startPeriod": 120
      },
      "environment": [
        {"name": "NODE_ENV", "value": "production"}
      ],
      "secrets": [
        {"name": "DB_PASSWORD", "valueFrom": "arn:aws:secretsmanager:region:account:secret:db-password"}
      ]
    }
  ]
}
```

### Service Auto Scaling
```bash
# Configure ECS service auto scaling
aws application-autoscaling register-scalable-target \\
  --service-namespace ecs \\
  --scalable-dimension ecs:service:DesiredCount \\
  --resource-id service/my-cluster/my-service \\
  --min-capacity 2 \\
  --max-capacity 10

# Create scaling policy
aws application-autoscaling put-scaling-policy \\
  --service-namespace ecs \\
  --scalable-dimension ecs:service:DesiredCount \\
  --resource-id service/my-cluster/my-service \\
  --policy-name cpu-scaling-policy \\
  --policy-type TargetTrackingScaling \\
  --target-tracking-scaling-policy-configuration file://scaling-policy.json
```

This debugging guide provides essential techniques for identifying and resolving ECS task failures in production AWS container environments.