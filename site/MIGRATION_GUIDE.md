# DS Framework v5.0 Navigation Migration Guide

This guide covers the complete migration process for updating the build system and navigation structure to support DS Framework v5.0.

## 🏗️ Architecture Changes

### New Navigation Structure

The DS Framework v5.0 introduces a reorganized navigation structure:

#### **Home Section** (New Parent)
- **Foundation**: Universal laws, capabilities, primitives
- **Guarantees**: Linearizability, eventual consistency, exactly-once
- **Mechanisms**: Replication, load balancing, partitioning, consensus, caching
- **Patterns**: Production architecture patterns and catalogs
- **Examples**: Case studies and implementation examples
- **Reference**: API reference, glossary, further reading

#### **Operations Section** (New Parent)
- **Debugging**: Moved from top-level to Operations parent
- **Production**: New section for production best practices

#### **Top-Level Sections** (Renamed/Reorganized)
- **Systems**: Architecture deep-dives (30 companies, 8 diagrams each)
- **Incidents**: Incident anatomies and response patterns
- **Comparisons**: Technology comparisons and trade-offs

#### **Existing Sections** (Unchanged Structure)
- **Performance**: Performance profiles and optimization
- **Scaling**: Scale evolution journeys
- **Capacity**: Capacity planning and models
- **Migrations**: Migration playbooks and strategies
- **Costs**: Infrastructure cost breakdowns

## 📋 Updated Build System

### Makefile Enhancements

The updated Makefile includes:

- **Structure validation targets**: `validate-structure`, `validate-home`, `validate-operations`
- **Section-specific validation**: Individual targets for each major section
- **Enhanced error reporting**: Better feedback for validation failures
- **Directory variables**: Configurable paths for all sections

**New Commands:**
```bash
make validate-structure  # Validate complete navigation structure
make validate-home       # Validate Home section structure
make validate-operations # Validate Operations parent structure
make validate-systems    # Validate Systems section (30 companies)
make v                   # Shortcut for validate-structure
```

### Validation Scripts

#### 1. Enhanced Mermaid Validator (`validate_mermaid.py`)
- Section-based reporting (Home, Operations, Systems, etc.)
- Directory structure validation
- Better error categorization and reporting

#### 2. Enhanced Link Checker (`check_links.py`)
- Section-based link validation
- Improved broken link reporting
- Support for new navigation paths

#### 3. Migration Validator (`migration_validator.py`)
- Comprehensive structure validation
- Company diagram validation (8 diagrams per system)
- Configuration file validation
- JSON export for CI/CD integration

#### 4. Migration Validation Suite (`validate_migration.sh`)
- Complete validation pipeline
- Colored output and progress reporting
- Export results to JSON
- Section-specific validation modes

### GitHub Workflow Updates

Enhanced CI/CD pipeline with:

- **Validation job**: Runs before build
- **Structure validation**: Validates directory structure
- **Content validation**: Validates Mermaid and links
- **Pull request validation**: Runs on PRs without deployment
- **Path-based triggers**: Only runs when relevant files change

## 🚀 Migration Process

### Step 1: Pre-Migration Backup

Create a backup of your current structure:

```bash
cd site
./scripts/rollback_navigation.sh backup-current --backup-name "pre-v5-migration"
```

### Step 2: Update Build Files

The following files have been updated:

1. **Makefile**: New validation targets and directory variables
2. **validate_mermaid.py**: Section-based validation
3. **check_links.py**: Enhanced link checking
4. **deploy.yml**: Updated GitHub workflow

### Step 3: Validate Current Structure

Run the migration validation suite:

```bash
cd site

# Full validation
./scripts/validate_migration.sh

# Quick validation (skip build test)
./scripts/validate_migration.sh --quick

# Specific section validation
./scripts/validate_migration.sh --section structure

# Export results
./scripts/validate_migration.sh --export validation_results.json
```

### Step 4: Directory Structure Migration

After updating build files, migrate your directory structure:

1. **Create Home section directories**:
   ```bash
   mkdir -p docs/{foundation,guarantees,mechanisms,patterns,examples,reference}
   ```

2. **Move content to new structure**:
   - Move existing guarantee files to `docs/guarantees/`
   - Move existing mechanism files to `docs/mechanisms/`
   - Organize pattern files under `docs/patterns/`
   - Create foundation content in `docs/foundation/`

3. **Validate Operations structure**:
   - Ensure `docs/debugging/` exists (should already be there)
   - Create `docs/production/` for new production content

### Step 5: Update Navigation Configuration

Update `mkdocs.yml` navigation to reflect new structure:

```yaml
nav:
  - Home:
    - Welcome: index.md
    - Foundation:
      - Universal Laws: foundation/universal-laws.md
      # ... other foundation files
    - Guarantees:
      - Linearizability: guarantees/linearizability/
      # ... other guarantee sections
    # ... other Home sections

  - Operations:
    - Debugging:
      - Performance Issues: debugging/performance-issues/
      # ... debugging sections
    - Production:
      - Best Practices: production/best-practices.md
      # ... production sections

  # ... other top-level sections
```

### Step 6: Validation and Testing

Run comprehensive validation:

```bash
# Validate structure
make validate-structure

# Test build
make build

# Run all validations
make test
```

## 🔧 Validation Commands

### Quick Reference

| Command | Purpose |
|---------|---------|
| `make validate-structure` | Validate complete navigation structure |
| `make validate-home` | Validate Home section structure |
| `make validate-operations` | Validate Operations parent structure |
| `make validate-systems` | Validate Systems section (30 companies) |
| `./scripts/validate_migration.sh` | Complete migration validation |
| `./scripts/migration_validator.py` | Python-based structure validator |

### Validation Sections

The validation system checks:

1. **Directory Structure**: All required directories exist
2. **File Content**: Markdown files present in each section
3. **MkDocs Config**: Navigation structure reflects new organization
4. **Makefile**: New validation targets and variables
5. **Scripts**: Validation scripts exist and are executable
6. **GitHub Workflow**: CI/CD pipeline includes validation steps
7. **Build Test**: MkDocs can successfully build the site

## 🔄 Rollback Procedures

### Emergency Rollback

If issues occur during migration:

```bash
# Quick rollback (with confirmation)
./scripts/rollback_navigation.sh rollback --confirm

# Dry run (see what would happen)
./scripts/rollback_navigation.sh rollback --dry-run
```

### Backup Management

```bash
# List available backups
./scripts/rollback_navigation.sh list-backups

# Restore from specific backup
./scripts/rollback_navigation.sh restore-backup --backup-name "pre-v5-migration"

# Validate rollback was successful
./scripts/rollback_navigation.sh validate-rollback
```

## 📊 Validation Results

### Success Criteria

Migration is successful when:

- ✅ All directory structure checks pass
- ✅ Home section has 6 subsections (foundation, guarantees, mechanisms, patterns, examples, reference)
- ✅ Operations section has 2 subsections (debugging, production)
- ✅ Systems section has 30 company directories
- ✅ Each company has 8 diagram files
- ✅ MkDocs build succeeds
- ✅ All links validate correctly
- ✅ All Mermaid diagrams validate

### Common Issues and Solutions

#### Missing Directories
```bash
# Create missing directories
mkdir -p docs/{foundation,guarantees,mechanisms,patterns,examples,reference}
mkdir -p docs/production
```

#### Validation Script Permissions
```bash
# Fix script permissions
chmod +x scripts/*.py scripts/*.sh
```

#### MkDocs Build Failures
```bash
# Check for syntax errors in mkdocs.yml
mkdocs build --verbose

# Validate configuration
python -c "import yaml; yaml.safe_load(open('mkdocs.yml'))"
```

## 🔍 Troubleshooting

### Validation Failures

1. **Structure validation fails**:
   - Check directory names match expected structure
   - Ensure all required directories exist
   - Verify file permissions

2. **Link validation fails**:
   - Update internal links to new paths
   - Check for broken cross-references
   - Validate anchor links

3. **Build failures**:
   - Check mkdocs.yml syntax
   - Verify all referenced files exist
   - Check for conflicting navigation entries

### Performance Issues

1. **Large validation runs**:
   - Use section-specific validation
   - Run quick mode for rapid feedback
   - Use export feature for CI/CD integration

2. **Build performance**:
   - Enable MkDocs caching
   - Use parallel processing where available
   - Optimize large diagram files

## 📁 File Structure Reference

```
site/
├── Makefile                           # Enhanced with new validation targets
├── mkdocs.yml                         # Updated navigation structure
├── requirements.txt                   # Dependencies
├── scripts/
│   ├── validate_mermaid.py           # Enhanced Mermaid validator
│   ├── check_links.py                # Enhanced link checker
│   ├── migration_validator.py        # New migration validator
│   ├── validate_migration.sh         # Complete validation suite
│   └── rollback_navigation.sh        # Rollback procedures
├── docs/
│   ├── foundation/                    # New: Universal laws, capabilities
│   ├── guarantees/                    # New: Moved from top-level
│   ├── mechanisms/                    # New: Moved from top-level
│   ├── patterns/                      # New: Architecture patterns
│   ├── examples/                      # New: Case studies
│   ├── reference/                     # New: Glossary, API reference
│   ├── debugging/                     # Moved to Operations parent
│   ├── production/                    # New: Production best practices
│   ├── systems/                       # Existing: 30 companies × 8 diagrams
│   ├── incidents/                     # Existing: Incident anatomies
│   ├── comparisons/                   # Existing: Technology comparisons
│   ├── performance/                   # Existing: Performance profiles
│   ├── scaling/                       # Existing: Scale journeys
│   ├── capacity/                      # Existing: Capacity models
│   ├── migrations/                    # Existing: Migration playbooks
│   └── costs/                         # Existing: Cost breakdowns
└── backups/                           # Generated by rollback scripts
```

## 🎯 Next Steps

After successful migration:

1. **Update documentation**: Ensure all references use new paths
2. **Train team**: Familiarize team with new structure and commands
3. **Monitor builds**: Watch for any issues in CI/CD pipeline
4. **Performance optimize**: Use new validation features for faster feedback
5. **Content creation**: Begin populating new sections with content

## 📞 Support

For issues or questions:

1. Run validation with verbose output: `./scripts/validate_migration.sh --export debug.json`
2. Check build logs for specific error messages
3. Use rollback procedures if critical issues occur
4. Consult section-specific validation for targeted debugging

---

**DS Framework v5.0 Migration** - Building production-ready distributed systems documentation at scale.