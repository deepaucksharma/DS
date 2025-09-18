# Disk Space Exhaustion Emergency Response

> **3 AM Emergency Protocol**: Disk space exhaustion can cause immediate service failures, data corruption, and cascading outages. This diagram shows how to quickly identify, free space, and restore operations.

## Quick Detection Checklist
- [ ] Check disk usage: `df -h` and identify filesystems >90% full
- [ ] Find large files: `find / -type f -size +1G 2>/dev/null | head -10`
- [ ] Monitor inode usage: `df -i` for inode exhaustion
- [ ] Alert on disk trends: `disk_usage_percent > 85%` with growth rate monitoring

## Disk Space Exhaustion Detection and Recovery

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - Data Sources]
        LOGS[Log Generation<br/>Rate: 1GB/hour<br/>Retention: 30 days<br/>Compression: None]
        UPLOADS[File Uploads<br/>User content: 500MB/min<br/>Temp processing: 2GB/job<br/>Cleanup: Manual]
        BACKUPS[Backup Jobs<br/>Database dumps: 50GB/day<br/>File backups: 100GB/day<br/>Retention: 7 days]
    end

    subgraph ServicePlane[Service Plane - Disk Consumers]
        subgraph APP_SERVICES[Application Services]
            API[API Service<br/>Log volume: /var/log<br/>Size: 45GB/50GB (90%)<br/>Status: WARNING]
            WORKER[Worker Service<br/>Temp files: /tmp<br/>Size: 18GB/20GB (90%)<br/>Status: CRITICAL]
            DB_APP[Database Service<br/>Data volume: /var/lib/mysql<br/>Size: 180GB/200GB (90%)<br/>Status: CRITICAL]
        end

        subgraph MONITORING[Monitoring Stack]
            PROMETHEUS[Prometheus<br/>Metrics storage: /prometheus<br/>Size: 95GB/100GB (95%)<br/>Status: CRITICAL]
            GRAFANA[Grafana<br/>Dashboard storage: /var/lib/grafana<br/>Size: 8GB/10GB (80%)<br/>Status: OK]
        end
    end

    subgraph StatePlane[State Plane - Storage Systems]
        subgraph ROOT_FS[Root Filesystem]
            ROOT_DISK[/ (Root)<br/>Total: 50GB<br/>Used: 45GB (90%)<br/>Available: 5GB<br/>Status: CRITICAL]
            VAR_DISK[/var (Logs)<br/>Total: 100GB<br/>Used: 95GB (95%)<br/>Available: 5GB<br/>Status: CRITICAL]
        end

        subgraph DATA_FS[Data Filesystems]
            DATA_DISK[/data (Application)<br/>Total: 500GB<br/>Used: 450GB (90%)<br/>Available: 50GB<br/>Status: WARNING]
            BACKUP_DISK[/backup (Backups)<br/>Total: 1TB<br/>Used: 950GB (95%)<br/>Available: 50GB<br/>Status: CRITICAL]
        end

        subgraph TEMP_FS[Temporary Filesystems]
            TMP_DISK[/tmp (Temporary)<br/>Total: 20GB<br/>Used: 18GB (90%)<br/>Available: 2GB<br/>Status: CRITICAL]
            DOCKER_DISK[/var/lib/docker<br/>Total: 100GB<br/>Used: 85GB (85%)<br/>Available: 15GB<br/>Status: WARNING]
        end
    end

    subgraph ControlPlane[Control Plane - Disk Management]
        MONITOR[Disk Monitoring<br/>Check interval: 1 minute<br/>Alert threshold: 85%<br/>Critical threshold: 90%]

        subgraph CLEANUP[Emergency Cleanup]
            LOG_ROTATE[Log Rotation<br/>Compress logs >7 days<br/>Delete logs >30 days<br/>Priority: HIGH]
            TEMP_CLEAN[Temp File Cleanup<br/>Remove files >24 hours<br/>Clear /tmp and /var/tmp<br/>Priority: IMMEDIATE]
            DOCKER_CLEAN[Docker Cleanup<br/>Remove unused images<br/>Clean build cache<br/>Prune containers]
        end

        subgraph SCALING[Capacity Management]
            VOLUME_EXPAND[Volume Expansion<br/>EBS/Disk resize<br/>Filesystem extension<br/>Online operation: Yes]
            DATA_ARCHIVE[Data Archiving<br/>Move old data to S3<br/>Compress large files<br/>Automated cleanup]
        end
    end

    %% Data flow causing disk pressure
    LOGS --> VAR_DISK
    UPLOADS --> TMP_DISK
    BACKUPS --> BACKUP_DISK

    %% Service disk usage
    API --> VAR_DISK
    WORKER --> TMP_DISK
    DB_APP --> DATA_DISK
    PROMETHEUS --> DATA_DISK
    GRAFANA --> ROOT_DISK

    %% Docker usage
    API --> DOCKER_DISK
    WORKER --> DOCKER_DISK

    %% Monitoring and alerts
    ROOT_DISK --> MONITOR
    VAR_DISK --> MONITOR
    DATA_DISK --> MONITOR
    BACKUP_DISK --> MONITOR
    TMP_DISK --> MONITOR
    DOCKER_DISK --> MONITOR

    %% Emergency responses
    MONITOR -->|"Critical threshold"| LOG_ROTATE
    MONITOR -->|"Immediate action"| TEMP_CLEAN
    MONITOR -->|"Container cleanup"| DOCKER_CLEAN
    MONITOR -->|"Capacity expansion"| VOLUME_EXPAND
    MONITOR -->|"Archive old data"| DATA_ARCHIVE

    %% Cleanup actions
    LOG_ROTATE -.->|"Free space"| VAR_DISK
    TEMP_CLEAN -.->|"Clear temp files"| TMP_DISK
    DOCKER_CLEAN -.->|"Remove images"| DOCKER_DISK
    VOLUME_EXPAND -.->|"Increase capacity"| DATA_DISK
    DATA_ARCHIVE -.->|"Move to S3"| BACKUP_DISK

    %% Service impact prevention
    LOG_ROTATE --> API
    TEMP_CLEAN --> WORKER
    VOLUME_EXPAND --> DB_APP

    %% 4-plane styling
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef criticalStyle fill:#FF0000,stroke:#8B5CF6,color:#fff
    classDef warningStyle fill:#FFA500,stroke:#CC8800,color:#fff

    class LOGS,UPLOADS,BACKUPS edgeStyle
    class API,WORKER,DB_APP,PROMETHEUS,GRAFANA serviceStyle
    class ROOT_DISK,VAR_DISK,DATA_DISK,BACKUP_DISK,TMP_DISK,DOCKER_DISK stateStyle
    class MONITOR,LOG_ROTATE,TEMP_CLEAN,DOCKER_CLEAN,VOLUME_EXPAND,DATA_ARCHIVE controlStyle
    class VAR_DISK,BACKUP_DISK,TMP_DISK,PROMETHEUS,WORKER,DB_APP criticalStyle
    class DATA_DISK,DOCKER_DISK,API warningStyle
```

## 3 AM Emergency Response Commands

### 1. Immediate Disk Assessment (30 seconds)
```bash
# Check disk space across all filesystems
df -h | grep -E "(9[0-9]%|100%)"

# Check inode usage (can cause failures even with free space)
df -i | grep -E "(9[0-9]%|100%)"

# Find largest directories quickly
du -h --max-depth=1 / 2>/dev/null | sort -hr | head -10

# Check for rapidly growing files
find /var/log -name "*.log" -size +1G -exec ls -lh {} \; 2>/dev/null
```

### 2. Emergency Space Recovery (60 seconds)
```bash
# Immediate log cleanup
find /var/log -name "*.log" -mtime +7 -exec gzip {} \;
find /var/log -name "*.log.gz" -mtime +30 -delete
journalctl --vacuum-time=7d
journalctl --vacuum-size=1G

# Clear temporary files
find /tmp -type f -mtime +1 -delete
find /var/tmp -type f -mtime +1 -delete
rm -rf /tmp/* /var/tmp/* 2>/dev/null

# Docker cleanup (if using Docker)
docker system prune -af --volumes
docker image prune -af
```

### 3. Rapid Capacity Expansion (90 seconds)
```bash
# Expand EBS volume (AWS) or equivalent
aws ec2 modify-volume --volume-id vol-12345678 --size 200

# Expand filesystem online (for ext4/xfs)
resize2fs /dev/xvdf1  # For ext4
xfs_growfs /data      # For XFS

# Mount additional temporary storage
mount -t tmpfs -o size=10G tmpfs /mnt/emergency
ln -sf /mnt/emergency /tmp/overflow

# Archive large files to S3 (if available)
aws s3 cp /var/log/large.log s3://backup-bucket/logs/
rm /var/log/large.log
```

## Disk Exhaustion Pattern Recognition

### Gradual Disk Fill Pattern
```
Time    Disk_Usage    Available    Growth_Rate    ETA_Full
06:00   70% (350GB)   150GB       1GB/hour       6 days
12:00   75% (375GB)   125GB       4GB/hour       1.3 days
18:00   85% (425GB)   75GB        8GB/hour       9 hours
00:00   95% (475GB)   25GB        5GB/hour       5 hours
03:00   98% (490GB)   10GB        3GB/hour       3 hours
```

### Sudden Disk Spike Pattern
```
Time    Event                 Disk_Usage    Cause
10:00   Normal operations     60% (300GB)   Baseline
10:30   Backup job starts     65% (325GB)   Expected growth
11:00   Log rotation fails    80% (400GB)   Logs accumulating
11:15   Temp files created    90% (450GB)   Processing job
11:20   CRITICAL ALERT        95% (475GB)   IMMEDIATE ACTION NEEDED
```

### Inode Exhaustion Pattern
```
Filesystem    Inodes_Used    Inodes_Total    Usage    Files_Pattern
/var/log      950,000        1,000,000       95%      Many small log files
/tmp          480,000        500,000         96%      Temp file accumulation
/data         120,000        2,000,000       6%       Normal usage
Status: Inode exhaustion preventing new file creation
```

## Error Message Patterns

### No Space Left on Device
```
ERROR: No space left on device
PATTERN: "ENOSPC" errors in system logs
LOCATION: Application logs, system logs, dmesg
ACTION: Free disk space immediately
IMPACT: Cannot write files, databases may corrupt
COMMAND: df -h; find / -size +1G -type f 2>/dev/null
```

### Inode Exhaustion
```
ERROR: No space left on device (but df shows free space)
PATTERN: Cannot create files despite available disk space
LOCATION: File creation operations, system calls
ACTION: Clean up small files, increase inode count
COMMAND: df -i; find / -type f | wc -l
```

### Database Disk Full
```
ERROR: Disk full (/var/lib/mysql); waiting for someone to free space
PATTERN: MySQL/PostgreSQL stops accepting writes
LOCATION: Database error logs
ACTION: Free space immediately, may need emergency restart
IMPACT: Database read-only mode, transaction failures
```

## Emergency Disk Cleanup Scripts

### Comprehensive Log Cleanup
```bash
#!/bin/bash
# Emergency log cleanup script

LOG_DIR="/var/log"
TEMP_DIRS="/tmp /var/tmp"
DOCKER_CLEANUP=true

echo "Starting emergency disk cleanup..."

# Compress old logs
find $LOG_DIR -name "*.log" -mtime +1 -size +100M -exec gzip {} \;

# Delete old compressed logs
find $LOG_DIR -name "*.log.gz" -mtime +7 -delete
find $LOG_DIR -name "*.log.*" -mtime +30 -delete

# Systemd journal cleanup
journalctl --vacuum-time=3d
journalctl --vacuum-size=500M

# Clear temporary directories
for dir in $TEMP_DIRS; do
    find $dir -type f -mtime +0 -delete 2>/dev/null
    find $dir -type d -empty -delete 2>/dev/null
done

# Docker cleanup if enabled
if [ "$DOCKER_CLEANUP" = true ] && command -v docker &> /dev/null; then
    docker system prune -af --volumes
    docker image prune -af
fi

# Clear core dumps
find /var/core -name "core.*" -mtime +1 -delete 2>/dev/null

# Clear old package caches
apt-get clean 2>/dev/null || yum clean all 2>/dev/null

echo "Cleanup completed. Current disk usage:"
df -h
```

### Kubernetes Pod Cleanup
```bash
#!/bin/bash
# Kubernetes emergency disk cleanup

# Clean up completed pods
kubectl delete pods --field-selector=status.phase=Succeeded --all-namespaces

# Clean up failed pods
kubectl delete pods --field-selector=status.phase=Failed --all-namespaces

# Remove old replica sets
kubectl get rs --all-namespaces | grep "0         0         0" | awk '{print $2 " -n " $1}' | xargs -L1 kubectl delete rs

# Clean up unused config maps and secrets (careful with this)
kubectl get configmaps --all-namespaces | grep -v "NAME" | awk '{print $2 " -n " $1}' | while read cm; do
    if ! kubectl get pods -o yaml --all-namespaces | grep -q "$cm"; then
        echo "Unused ConfigMap: $cm"
    fi
done

echo "Kubernetes cleanup completed"
```

## Automated Disk Monitoring

### Prometheus Disk Monitoring
```yaml
# Prometheus rules for disk monitoring
groups:
- name: disk_space
  rules:
  - alert: DiskSpaceCritical
    expr: (node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100 < 10
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Disk space critical on {{ $labels.instance }}"
      description: "Disk space on {{ $labels.instance }} is below 10%"

  - alert: DiskSpaceWarning
    expr: (node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100 < 20
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Disk space low on {{ $labels.instance }}"
      description: "Disk space on {{ $labels.instance }} is below 20%"

  - alert: InodeExhaustion
    expr: (node_filesystem_files_free / node_filesystem_files) * 100 < 10
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Inode exhaustion on {{ $labels.instance }}"
      description: "Inodes on {{ $labels.instance }} are below 10%"
```

### Automated Cleanup Cron Jobs
```bash
# /etc/cron.hourly/disk-cleanup
#!/bin/bash
# Automated disk cleanup - runs every hour

THRESHOLD=85  # Start cleanup at 85% usage

# Check each mounted filesystem
df -h | awk 'NR>1 {print $5 " " $6}' | while read usage mountpoint; do
    usage_num=$(echo $usage | sed 's/%//')

    if [ $usage_num -gt $THRESHOLD ]; then
        echo "$(date): Disk usage on $mountpoint is $usage, starting cleanup"

        case $mountpoint in
            "/var/log"|"/var")
                # Log cleanup
                find /var/log -name "*.log" -mtime +7 -exec gzip {} \;
                find /var/log -name "*.log.gz" -mtime +30 -delete
                ;;
            "/tmp")
                # Temp file cleanup
                find /tmp -type f -mtime +1 -delete
                ;;
            "/var/lib/docker")
                # Docker cleanup
                docker system prune -af --volumes
                ;;
        esac
    fi
done
```

## Disk Performance Optimization

### Log Rotation Configuration
```bash
# /etc/logrotate.d/application
/var/log/application/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 app app
    postrotate
        systemctl reload application
    endscript
}

# /etc/logrotate.d/nginx
/var/log/nginx/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 644 nginx nginx
    postrotate
        systemctl reload nginx
    endscript
}
```

### Systemd Journal Configuration
```ini
# /etc/systemd/journald.conf
[Journal]
Storage=persistent
Compress=yes
SystemMaxUse=1G
SystemMaxFileSize=100M
SystemMaxFiles=10
MaxRetentionSec=1week
ForwardToSyslog=no
```

## Recovery Verification Procedures

### Phase 1: Space Recovery (0-5 minutes)
- [ ] Verify disk usage below 85% on critical filesystems
- [ ] Confirm services can write files successfully
- [ ] Test database write operations
- [ ] Check application log generation

### Phase 2: Service Restoration (5-15 minutes)
- [ ] Restart any services that failed due to disk full
- [ ] Verify all applications are logging properly
- [ ] Check database integrity and replication
- [ ] Monitor for any delayed write failures

### Phase 3: Prevention Setup (15+ minutes)
- [ ] Configure automated cleanup scripts
- [ ] Set up enhanced disk monitoring
- [ ] Plan capacity expansion if needed
- [ ] Review and optimize log retention policies

## Real-World Disk Exhaustion Incidents

### GitLab Database Disk Full (2017)
- **Trigger**: PostgreSQL WAL files accumulated, filled disk
- **Impact**: Complete GitLab.com outage for 6 hours
- **Detection**: Database stopped accepting writes
- **Resolution**: Emergency disk expansion + WAL cleanup
- **Prevention**: Automated WAL archiving + monitoring

### Reddit Comment Storage Exhaustion (2019)
- **Trigger**: Viral thread generated massive comment volume
- **Impact**: Comment service degraded, users couldn't post
- **Detection**: Disk usage alerts + application errors
- **Resolution**: Emergency cleanup + storage scaling
- **Lesson**: Plan for viral content scenarios

### Slack Message Storage Crisis (2020)
- **Trigger**: Message retention policy not enforced
- **Impact**: Message search degraded, new messages delayed
- **Detection**: ElasticSearch disk full alerts
- **Resolution**: Data archiving + index optimization
- **Prevention**: Automated data lifecycle management

---
*Last Updated: Based on GitLab, Reddit, Slack disk exhaustion incidents*
*Next Review: Monitor for new disk management patterns and optimization strategies*