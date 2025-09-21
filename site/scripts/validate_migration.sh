#!/bin/bash

# DS Framework v5.0 Migration Validation Script
# Complete validation suite for navigation structure changes

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SITE_DIR="$(dirname "$SCRIPT_DIR")"
DOCS_DIR="$SITE_DIR/docs"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASSED_CHECKS++))
    ((TOTAL_CHECKS++))
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    ((WARNING_CHECKS++))
    ((TOTAL_CHECKS++))
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((FAILED_CHECKS++))
    ((TOTAL_CHECKS++))
}

log_section() {
    echo ""
    echo -e "${PURPLE}=== $1 ===${NC}"
}

# Validation functions
validate_directory_structure() {
    log_section "Directory Structure Validation"

    # Expected Home section directories
    local home_dirs=("foundation" "guarantees" "mechanisms" "patterns" "examples" "reference")
    log_info "Checking Home section directories..."

    for dir in "${home_dirs[@]}"; do
        if [[ -d "$DOCS_DIR/$dir" ]]; then
            log_success "Home directory exists: docs/$dir"
        else
            log_error "Missing Home directory: docs/$dir"
        fi
    done

    # Expected Operations directories
    local ops_dirs=("debugging" "production")
    log_info "Checking Operations section directories..."

    for dir in "${ops_dirs[@]}"; do
        if [[ -d "$DOCS_DIR/$dir" ]]; then
            log_success "Operations directory exists: docs/$dir"
        else
            log_error "Missing Operations directory: docs/$dir"
        fi
    done

    # Systems directory and companies
    log_info "Checking Systems section..."
    if [[ -d "$DOCS_DIR/systems" ]]; then
        log_success "Systems directory exists: docs/systems"

        # Count companies
        local company_count=$(find "$DOCS_DIR/systems" -mindepth 1 -maxdepth 1 -type d | wc -l)
        if [[ $company_count -eq 30 ]]; then
            log_success "Found expected 30 company directories"
        elif [[ $company_count -gt 0 ]]; then
            log_warning "Found $company_count companies (expected 30)"
        else
            log_error "No company directories found in systems/"
        fi
    else
        log_error "Missing Systems directory: docs/systems"
    fi

    # Top-level sections
    local top_sections=("incidents" "comparisons")
    log_info "Checking top-level sections..."

    for section in "${top_sections[@]}"; do
        if [[ -d "$DOCS_DIR/$section" ]]; then
            log_success "Top-level directory exists: docs/$section"
        else
            log_error "Missing top-level directory: docs/$section"
        fi
    done
}

validate_file_content() {
    log_section "File Content Validation"

    log_info "Checking for markdown files in each section..."

    # Check Home sections have content
    local home_dirs=("foundation" "guarantees" "mechanisms" "patterns" "examples" "reference")
    for dir in "${home_dirs[@]}"; do
        if [[ -d "$DOCS_DIR/$dir" ]]; then
            local file_count=$(find "$DOCS_DIR/$dir" -name "*.md" | wc -l)
            if [[ $file_count -gt 0 ]]; then
                log_success "$dir section has $file_count markdown files"
            else
                log_warning "$dir section has no markdown files"
            fi
        fi
    done

    # Check Operations sections have content
    local ops_dirs=("debugging" "production")
    for dir in "${ops_dirs[@]}"; do
        if [[ -d "$DOCS_DIR/$dir" ]]; then
            local file_count=$(find "$DOCS_DIR/$dir" -name "*.md" | wc -l)
            if [[ $file_count -gt 0 ]]; then
                log_success "$dir section has $file_count markdown files"
            else
                log_warning "$dir section has no markdown files"
            fi
        fi
    done

    # Check Systems companies have the required 8 diagrams
    if [[ -d "$DOCS_DIR/systems" ]]; then
        log_info "Validating system company diagrams..."
        local companies_with_8_diagrams=0
        local total_companies=0

        for company_dir in "$DOCS_DIR/systems"/*/; do
            if [[ -d "$company_dir" ]]; then
                local company=$(basename "$company_dir")
                local diagram_count=$(find "$company_dir" -name "*.md" | wc -l)
                ((total_companies++))

                if [[ $diagram_count -eq 8 ]]; then
                    ((companies_with_8_diagrams++))
                elif [[ $diagram_count -gt 0 ]]; then
                    log_warning "$company has $diagram_count/8 diagrams"
                else
                    log_error "$company has no diagrams"
                fi
            fi
        done

        if [[ $companies_with_8_diagrams -eq $total_companies && $total_companies -gt 0 ]]; then
            log_success "All $total_companies companies have 8 diagrams"
        else
            log_warning "$companies_with_8_diagrams/$total_companies companies have complete diagram sets"
        fi
    fi
}

validate_mkdocs_config() {
    log_section "MkDocs Configuration Validation"

    local mkdocs_file="$SITE_DIR/mkdocs.yml"

    if [[ ! -f "$mkdocs_file" ]]; then
        log_error "mkdocs.yml not found"
        return
    fi

    log_success "mkdocs.yml exists"

    # Check for Home section in navigation
    if grep -q "Home:" "$mkdocs_file"; then
        log_success "Home section found in navigation"
    else
        log_warning "Home section not found in navigation"
    fi

    # Check for Operations-related sections
    if grep -q -E "(debugging|production):" "$mkdocs_file"; then
        log_success "Operations sections found in navigation"
    else
        log_warning "Operations sections not found in navigation"
    fi

    # Check for Systems section
    if grep -q "Systems:" "$mkdocs_file"; then
        log_success "Systems section found in navigation"
    else
        log_error "Systems section not found in navigation"
    fi

    # Check for new theme configuration
    if grep -q "name: material" "$mkdocs_file"; then
        log_success "Material theme configured"
    else
        log_warning "Material theme not found"
    fi

    # Check for Mermaid plugin
    if grep -q "mermaid2" "$mkdocs_file"; then
        log_success "Mermaid plugin configured"
    else
        log_error "Mermaid plugin not configured"
    fi
}

validate_makefile() {
    log_section "Makefile Validation"

    local makefile="$SITE_DIR/Makefile"

    if [[ ! -f "$makefile" ]]; then
        log_error "Makefile not found"
        return
    fi

    log_success "Makefile exists"

    # Check for new validation targets
    if grep -q "validate-structure" "$makefile"; then
        log_success "Structure validation target found"
    else
        log_error "Structure validation target missing"
    fi

    if grep -q "validate-home" "$makefile"; then
        log_success "Home validation target found"
    else
        log_error "Home validation target missing"
    fi

    if grep -q "validate-operations" "$makefile"; then
        log_success "Operations validation target found"
    else
        log_error "Operations validation target missing"
    fi

    # Check for directory variables
    if grep -q "HOME_DIRS" "$makefile"; then
        log_success "HOME_DIRS variable defined"
    else
        log_error "HOME_DIRS variable missing"
    fi

    if grep -q "OPERATIONS_DIRS" "$makefile"; then
        log_success "OPERATIONS_DIRS variable defined"
    else
        log_error "OPERATIONS_DIRS variable missing"
    fi
}

validate_scripts() {
    log_section "Validation Scripts"

    # Check validation scripts exist
    local scripts=("validate_mermaid.py" "check_links.py" "migration_validator.py")

    for script in "${scripts[@]}"; do
        if [[ -f "$SCRIPT_DIR/$script" ]]; then
            log_success "Validation script exists: $script"

            # Check if script is executable
            if [[ -x "$SCRIPT_DIR/$script" ]]; then
                log_success "$script is executable"
            else
                log_warning "$script is not executable"
            fi
        else
            log_error "Missing validation script: $script"
        fi
    done

    # Test migration validator if it exists
    if [[ -f "$SCRIPT_DIR/migration_validator.py" ]]; then
        log_info "Testing migration validator..."
        cd "$SITE_DIR"
        if python3 scripts/migration_validator.py --quiet 2>/dev/null; then
            log_success "Migration validator runs successfully"
        else
            log_warning "Migration validator reported issues"
        fi
    fi
}

validate_github_workflow() {
    log_section "GitHub Workflow Validation"

    local workflow_file="$SITE_DIR/../.github/workflows/deploy.yml"

    if [[ -f "$workflow_file" ]]; then
        log_success "GitHub workflow exists"

        # Check for validation steps
        if grep -q "validate-structure" "$workflow_file"; then
            log_success "Structure validation in workflow"
        else
            log_warning "Structure validation not in workflow"
        fi

        if grep -q "validate_mermaid.py" "$workflow_file"; then
            log_success "Mermaid validation in workflow"
        else
            log_warning "Mermaid validation not in workflow"
        fi

        if grep -q "check_links.py" "$workflow_file"; then
            log_success "Link validation in workflow"
        else
            log_warning "Link validation not in workflow"
        fi
    else
        log_warning "GitHub workflow not found (optional)"
    fi
}

run_build_test() {
    log_section "Build Test"

    cd "$SITE_DIR"

    log_info "Testing MkDocs build..."

    if command -v mkdocs &> /dev/null; then
        if mkdocs build --quiet 2>/dev/null; then
            log_success "MkDocs build successful"

            # Check output directory
            if [[ -d "site" ]]; then
                local file_count=$(find site -type f | wc -l)
                log_success "Generated $file_count files in site/"
            else
                log_error "Build output directory not found"
            fi
        else
            log_error "MkDocs build failed"
        fi
    else
        log_warning "MkDocs not installed, skipping build test"
    fi
}

generate_summary() {
    log_section "Validation Summary"

    echo ""
    echo -e "${CYAN}📊 Migration Validation Results:${NC}"
    echo "   Total Checks: $TOTAL_CHECKS"
    echo -e "   ${GREEN}✅ Passed: $PASSED_CHECKS${NC}"
    echo -e "   ${YELLOW}⚠️  Warnings: $WARNING_CHECKS${NC}"
    echo -e "   ${RED}❌ Failed: $FAILED_CHECKS${NC}"
    echo ""

    local success_rate=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))

    if [[ $FAILED_CHECKS -eq 0 ]]; then
        echo -e "${GREEN}🎉 Migration validation PASSED!${NC}"
        echo -e "   Success rate: ${success_rate}%"
        echo ""
        echo "✅ Navigation structure is ready for DS Framework v5.0"
    elif [[ $FAILED_CHECKS -le 3 ]]; then
        echo -e "${YELLOW}⚠️  Migration validation completed with minor issues${NC}"
        echo -e "   Success rate: ${success_rate}%"
        echo ""
        echo "Please address the failed checks before proceeding"
    else
        echo -e "${RED}❌ Migration validation FAILED${NC}"
        echo -e "   Success rate: ${success_rate}%"
        echo ""
        echo "Critical issues found. Please fix before continuing with migration"
        return 1
    fi

    return 0
}

show_help() {
    cat << EOF
DS Framework v5.0 Migration Validation Script

USAGE:
    $0 [OPTIONS]

OPTIONS:
    --quick         Run quick validation (skip build test)
    --section NAME  Run validation for specific section only
    --export FILE   Export results to JSON file
    --help          Show this help message

SECTIONS:
    structure    - Directory structure validation
    content      - File content validation
    config       - MkDocs configuration validation
    makefile     - Makefile validation
    scripts      - Validation scripts check
    workflow     - GitHub workflow validation
    build        - Build test

EXAMPLES:
    $0                           # Full validation
    $0 --quick                   # Quick validation
    $0 --section structure       # Structure only
    $0 --export results.json     # Export results

EOF
}

main() {
    local quick_mode=false
    local specific_section=""
    local export_file=""

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --quick)
                quick_mode=true
                shift
                ;;
            --section)
                specific_section="$2"
                shift 2
                ;;
            --export)
                export_file="$2"
                shift 2
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    echo -e "${PURPLE}🔍 DS Framework v5.0 Migration Validation${NC}"
    echo -e "${PURPLE}=========================================${NC}"

    # Change to site directory
    cd "$SITE_DIR"

    # Run specific section or all validations
    case "$specific_section" in
        structure)
            validate_directory_structure
            ;;
        content)
            validate_file_content
            ;;
        config)
            validate_mkdocs_config
            ;;
        makefile)
            validate_makefile
            ;;
        scripts)
            validate_scripts
            ;;
        workflow)
            validate_github_workflow
            ;;
        build)
            run_build_test
            ;;
        "")
            # Run all validations
            validate_directory_structure
            validate_file_content
            validate_mkdocs_config
            validate_makefile
            validate_scripts
            validate_github_workflow

            if [[ "$quick_mode" != "true" ]]; then
                run_build_test
            fi
            ;;
        *)
            echo "Unknown section: $specific_section"
            show_help
            exit 1
            ;;
    esac

    # Generate summary
    generate_summary

    # Export results if requested
    if [[ -n "$export_file" ]]; then
        cat > "$export_file" << EOF
{
    "validation_date": "$(date -Iseconds)",
    "total_checks": $TOTAL_CHECKS,
    "passed_checks": $PASSED_CHECKS,
    "failed_checks": $FAILED_CHECKS,
    "warning_checks": $WARNING_CHECKS,
    "success_rate": $((PASSED_CHECKS * 100 / TOTAL_CHECKS)),
    "overall_status": "$(if [[ $FAILED_CHECKS -eq 0 ]]; then echo "PASSED"; else echo "FAILED"; fi)"
}
EOF
        log_info "Results exported to: $export_file"
    fi

    # Return appropriate exit code
    if [[ $FAILED_CHECKS -eq 0 ]]; then
        return 0
    else
        return 1
    fi
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi