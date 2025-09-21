#!/bin/bash

# DS Framework v5.0 Navigation Rollback Script
# This script provides procedures to rollback navigation changes

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SITE_DIR="$(dirname "$SCRIPT_DIR")"
DOCS_DIR="$SITE_DIR/docs"
BACKUP_DIR="$SITE_DIR/backups"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to display help
show_help() {
    cat << EOF
DS Framework v5.0 Navigation Rollback Script

USAGE:
    $0 [COMMAND] [OPTIONS]

COMMANDS:
    backup-current      Create backup of current navigation structure
    list-backups        List available backups
    rollback            Rollback to previous navigation structure
    validate-rollback   Validate rollback was successful
    restore-backup      Restore from specific backup
    help               Show this help message

OPTIONS:
    --backup-name NAME  Specify backup name (default: auto-generated)
    --confirm          Skip confirmation prompts
    --dry-run          Show what would be done without executing

EXAMPLES:
    $0 backup-current --backup-name "pre-v5-migration"
    $0 rollback --confirm
    $0 restore-backup --backup-name "pre-v5-migration"
    $0 validate-rollback

For emergency rollback without confirmation:
    $0 rollback --confirm

EOF
}

# Function to create backup
backup_current_structure() {
    local backup_name="$1"

    if [[ -z "$backup_name" ]]; then
        backup_name="navigation-backup-$(date +%Y%m%d-%H%M%S)"
    fi

    log_info "Creating backup: $backup_name"

    # Create backup directory
    mkdir -p "$BACKUP_DIR"
    local backup_path="$BACKUP_DIR/$backup_name"

    if [[ -d "$backup_path" ]]; then
        log_error "Backup already exists: $backup_path"
        return 1
    fi

    mkdir -p "$backup_path"

    # Backup docs directory
    if [[ -d "$DOCS_DIR" ]]; then
        log_info "Backing up docs directory..."
        cp -r "$DOCS_DIR" "$backup_path/"
    else
        log_warning "Docs directory not found: $DOCS_DIR"
    fi

    # Backup mkdocs.yml
    if [[ -f "$SITE_DIR/mkdocs.yml" ]]; then
        log_info "Backing up mkdocs.yml..."
        cp "$SITE_DIR/mkdocs.yml" "$backup_path/"
    else
        log_warning "mkdocs.yml not found: $SITE_DIR/mkdocs.yml"
    fi

    # Backup Makefile
    if [[ -f "$SITE_DIR/Makefile" ]]; then
        log_info "Backing up Makefile..."
        cp "$SITE_DIR/Makefile" "$backup_path/"
    fi

    # Create backup metadata
    cat > "$backup_path/backup_metadata.json" << EOF
{
    "backup_name": "$backup_name",
    "created_date": "$(date -Iseconds)",
    "created_by": "$USER",
    "hostname": "$(hostname)",
    "git_commit": "$(cd "$SITE_DIR" && git rev-parse HEAD 2>/dev/null || echo 'unknown')",
    "git_branch": "$(cd "$SITE_DIR" && git branch --show-current 2>/dev/null || echo 'unknown')",
    "description": "Navigation structure backup before v5.0 changes"
}
EOF

    log_success "Backup created successfully: $backup_path"
    return 0
}

# Function to list backups
list_backups() {
    log_info "Available backups in $BACKUP_DIR:"

    if [[ ! -d "$BACKUP_DIR" ]]; then
        log_warning "No backup directory found: $BACKUP_DIR"
        return 0
    fi

    local count=0
    for backup in "$BACKUP_DIR"/*/; do
        if [[ -d "$backup" ]]; then
            local backup_name=$(basename "$backup")
            local metadata_file="$backup/backup_metadata.json"

            if [[ -f "$metadata_file" ]]; then
                local created_date=$(grep '"created_date"' "$metadata_file" | cut -d'"' -f4)
                local git_commit=$(grep '"git_commit"' "$metadata_file" | cut -d'"' -f4 | cut -c1-8)
                echo "  📁 $backup_name"
                echo "     Created: $created_date"
                echo "     Git: $git_commit"
                echo ""
            else
                echo "  📁 $backup_name (no metadata)"
                echo ""
            fi
            ((count++))
        fi
    done

    if [[ $count -eq 0 ]]; then
        log_warning "No backups found"
    else
        log_info "Found $count backup(s)"
    fi
}

# Function to validate current structure
validate_current_structure() {
    log_info "Validating current navigation structure..."

    cd "$SITE_DIR"

    # Check if migration validator exists and run it
    if [[ -f "scripts/migration_validator.py" ]]; then
        log_info "Running migration validator..."
        python3 scripts/migration_validator.py
        return $?
    else
        log_warning "Migration validator not found, running basic checks..."

        # Basic validation
        local errors=0

        # Check for expected v5.0 structure
        local v5_dirs=("foundation" "guarantees" "mechanisms" "patterns" "examples" "reference" "debugging" "production" "systems" "incidents" "comparisons")

        for dir in "${v5_dirs[@]}"; do
            if [[ -d "$DOCS_DIR/$dir" ]]; then
                log_success "✅ Found: docs/$dir"
            else
                log_error "❌ Missing: docs/$dir"
                ((errors++))
            fi
        done

        return $errors
    fi
}

# Function to rollback to pre-v5.0 structure
rollback_navigation() {
    local confirm="$1"
    local dry_run="$2"

    if [[ "$confirm" != "true" ]]; then
        echo ""
        log_warning "⚠️  NAVIGATION ROLLBACK WARNING ⚠️"
        echo ""
        echo "This will rollback the navigation structure changes from DS Framework v5.0:"
        echo ""
        echo "CHANGES THAT WILL BE REVERTED:"
        echo "  • Home section (Foundation, Guarantees, Mechanisms, Patterns, Examples, Reference)"
        echo "  • Operations parent structure (Debugging, Production)"
        echo "  • Updated Systems organization"
        echo "  • Navigation hierarchy changes"
        echo ""
        echo "WHAT WILL HAPPEN:"
        echo "  1. Create automatic backup of current state"
        echo "  2. Restore previous mkdocs.yml navigation"
        echo "  3. Restore previous Makefile"
        echo "  4. Move directories back to old structure"
        echo ""
        read -p "Are you sure you want to proceed? (y/N): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Rollback cancelled"
            return 0
        fi
    fi

    # Create automatic backup before rollback
    log_info "Creating automatic backup before rollback..."
    backup_current_structure "pre-rollback-$(date +%Y%m%d-%H%M%S)"

    if [[ "$dry_run" == "true" ]]; then
        log_info "DRY RUN MODE - Would perform rollback operations"
        return 0
    fi

    log_info "Starting navigation rollback..."

    # Find the most recent backup to restore from
    local latest_backup=""
    if [[ -d "$BACKUP_DIR" ]]; then
        latest_backup=$(ls -t "$BACKUP_DIR" | head -n 1)
    fi

    if [[ -z "$latest_backup" ]]; then
        log_error "No backup found to restore from"
        log_info "Please create a backup of the desired state first"
        return 1
    fi

    log_info "Restoring from backup: $latest_backup"
    restore_from_backup "$latest_backup"

    log_success "Navigation rollback completed"

    # Validate rollback
    log_info "Validating rollback..."
    validate_rollback
}

# Function to restore from specific backup
restore_from_backup() {
    local backup_name="$1"

    if [[ -z "$backup_name" ]]; then
        log_error "Backup name required"
        return 1
    fi

    local backup_path="$BACKUP_DIR/$backup_name"

    if [[ ! -d "$backup_path" ]]; then
        log_error "Backup not found: $backup_path"
        return 1
    fi

    log_info "Restoring from backup: $backup_name"

    # Restore docs directory
    if [[ -d "$backup_path/docs" ]]; then
        log_info "Restoring docs directory..."
        rm -rf "$DOCS_DIR"
        cp -r "$backup_path/docs" "$DOCS_DIR"
    fi

    # Restore mkdocs.yml
    if [[ -f "$backup_path/mkdocs.yml" ]]; then
        log_info "Restoring mkdocs.yml..."
        cp "$backup_path/mkdocs.yml" "$SITE_DIR/"
    fi

    # Restore Makefile
    if [[ -f "$backup_path/Makefile" ]]; then
        log_info "Restoring Makefile..."
        cp "$backup_path/Makefile" "$SITE_DIR/"
    fi

    log_success "Restore completed"
}

# Function to validate rollback was successful
validate_rollback() {
    log_info "Validating rollback..."

    cd "$SITE_DIR"

    # Check if we can build the site
    if command -v mkdocs &> /dev/null; then
        log_info "Testing MkDocs build..."
        if mkdocs build --quiet 2>/dev/null; then
            log_success "✅ MkDocs build successful"
        else
            log_error "❌ MkDocs build failed"
            return 1
        fi
    else
        log_warning "MkDocs not available for build test"
    fi

    # Check if basic structure is restored
    if [[ -f "mkdocs.yml" ]]; then
        log_success "✅ mkdocs.yml restored"
    else
        log_error "❌ mkdocs.yml missing"
        return 1
    fi

    if [[ -f "Makefile" ]]; then
        log_success "✅ Makefile restored"
    else
        log_error "❌ Makefile missing"
        return 1
    fi

    log_success "Rollback validation passed"
    return 0
}

# Main script logic
main() {
    local command="$1"
    shift

    local backup_name=""
    local confirm="false"
    local dry_run="false"

    # Parse options
    while [[ $# -gt 0 ]]; do
        case $1 in
            --backup-name)
                backup_name="$2"
                shift 2
                ;;
            --confirm)
                confirm="true"
                shift
                ;;
            --dry-run)
                dry_run="true"
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    case "$command" in
        backup-current)
            backup_current_structure "$backup_name"
            ;;
        list-backups)
            list_backups
            ;;
        rollback)
            rollback_navigation "$confirm" "$dry_run"
            ;;
        validate-rollback)
            validate_rollback
            ;;
        restore-backup)
            if [[ -z "$backup_name" ]]; then
                log_error "Backup name required for restore-backup command"
                show_help
                exit 1
            fi
            restore_from_backup "$backup_name"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi