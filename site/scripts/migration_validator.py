#!/usr/bin/env python3
"""
Migration Validation Suite for DS Framework v5.0 Navigation Changes

Validates the migration from old structure to new navigation:
- Home section containing Foundation, Guarantees, Mechanisms, Patterns, Examples, Reference
- Operations parent containing Debugging and Production
- Systems (renamed from top-level)
- Incidents (remains top-level)
- Comparisons (renamed from top-level)
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set
import json
from dataclasses import dataclass

@dataclass
class ValidationResult:
    """Represents a validation result."""
    section: str
    status: str
    message: str
    details: List[str] = None

class NavigationMigrationValidator:
    """Validates the navigation structure migration."""

    def __init__(self, docs_dir: Path):
        self.docs_dir = docs_dir
        self.results: List[ValidationResult] = []

        # Expected new structure
        self.expected_structure = {
            'home_sections': ['foundation', 'guarantees', 'mechanisms', 'patterns', 'examples', 'reference'],
            'operations_sections': ['debugging', 'production'],
            'top_level_sections': ['systems', 'incidents', 'comparisons'],
            'systems_companies': [
                'airbnb', 'amazon', 'cloudflare', 'coinbase', 'datadog', 'discord',
                'doordash', 'dropbox', 'github', 'google', 'instacart', 'linkedin',
                'meta', 'microsoft', 'netflix', 'openai', 'pinterest', 'reddit',
                'robinhood', 'shopify', 'slack', 'snap', 'spotify', 'square',
                'stripe', 'tiktok', 'twitch', 'twitter', 'uber', 'zoom'
            ]
        }

    def validate_home_section(self) -> None:
        """Validate Home section structure."""
        missing_dirs = []
        existing_dirs = []

        for section in self.expected_structure['home_sections']:
            section_path = self.docs_dir / section
            if section_path.exists() and section_path.is_dir():
                existing_dirs.append(section)
                # Check for content
                md_files = list(section_path.rglob('*.md'))
                if not md_files:
                    self.results.append(ValidationResult(
                        section='Home',
                        status='warning',
                        message=f'Home section "{section}" exists but has no markdown files',
                        details=[str(section_path)]
                    ))
            else:
                missing_dirs.append(section)

        if missing_dirs:
            self.results.append(ValidationResult(
                section='Home',
                status='error',
                message=f'Missing Home sections: {", ".join(missing_dirs)}',
                details=missing_dirs
            ))

        if existing_dirs:
            self.results.append(ValidationResult(
                section='Home',
                status='success',
                message=f'Found Home sections: {", ".join(existing_dirs)}',
                details=existing_dirs
            ))

    def validate_operations_section(self) -> None:
        """Validate Operations parent section."""
        missing_dirs = []
        existing_dirs = []

        for section in self.expected_structure['operations_sections']:
            section_path = self.docs_dir / section
            if section_path.exists() and section_path.is_dir():
                existing_dirs.append(section)
                # Check for content
                md_files = list(section_path.rglob('*.md'))
                file_count = len(md_files)

                if file_count == 0:
                    self.results.append(ValidationResult(
                        section='Operations',
                        status='warning',
                        message=f'Operations section "{section}" exists but has no markdown files',
                        details=[str(section_path)]
                    ))
                else:
                    self.results.append(ValidationResult(
                        section='Operations',
                        status='info',
                        message=f'Operations section "{section}" has {file_count} files',
                        details=[f'{file_count} markdown files']
                    ))
            else:
                missing_dirs.append(section)

        if missing_dirs:
            self.results.append(ValidationResult(
                section='Operations',
                status='error',
                message=f'Missing Operations sections: {", ".join(missing_dirs)}',
                details=missing_dirs
            ))

        if existing_dirs:
            self.results.append(ValidationResult(
                section='Operations',
                status='success',
                message=f'Found Operations sections: {", ".join(existing_dirs)}',
                details=existing_dirs
            ))

    def validate_systems_section(self) -> None:
        """Validate Systems section with 30 companies."""
        systems_dir = self.docs_dir / 'systems'

        if not systems_dir.exists():
            self.results.append(ValidationResult(
                section='Systems',
                status='error',
                message='Systems directory does not exist',
                details=['Expected: docs/systems/']
            ))
            return

        # Find actual company directories
        actual_companies = []
        for item in systems_dir.iterdir():
            if item.is_dir() and item.name != '__pycache__':
                actual_companies.append(item.name)

        expected_companies = set(self.expected_structure['systems_companies'])
        actual_companies_set = set(actual_companies)

        missing_companies = expected_companies - actual_companies_set
        extra_companies = actual_companies_set - expected_companies

        if missing_companies:
            self.results.append(ValidationResult(
                section='Systems',
                status='error',
                message=f'Missing {len(missing_companies)} companies',
                details=sorted(list(missing_companies))
            ))

        if extra_companies:
            self.results.append(ValidationResult(
                section='Systems',
                status='warning',
                message=f'Extra {len(extra_companies)} companies (not in expected list)',
                details=sorted(list(extra_companies))
            ))

        # Validate each company has required 8 diagrams
        company_validation = []
        for company in actual_companies:
            company_path = systems_dir / company
            md_files = list(company_path.glob('*.md'))

            # Expected files (8 mandatory diagrams)
            expected_files = [
                'architecture.md', 'request-flow.md', 'storage-architecture.md',
                'failure-domains.md', 'scale-evolution.md', 'cost-breakdown.md',
                'novel-solutions.md', 'production-operations.md'
            ]

            # Check with alternative naming patterns
            alternative_patterns = [
                ['01-complete-architecture.md', 'architecture.md'],
                ['02-request-flow.md', 'request-flow.md'],
                ['03-storage-architecture.md', 'storage-architecture.md'],
                ['04-failure-domains.md', 'failure-domains.md'],
                ['05-scale-evolution.md', 'scale-evolution.md'],
                ['06-cost-breakdown.md', 'cost-breakdown.md'],
                ['07-novel-solutions.md', 'novel-solutions.md'],
                ['08-production-operations.md', 'production-operations.md']
            ]

            found_files = [f.name for f in md_files]
            missing_diagrams = []

            for patterns in alternative_patterns:
                found = False
                for pattern in patterns:
                    if pattern in found_files:
                        found = True
                        break
                if not found:
                    missing_diagrams.append(patterns[1])  # Use canonical name

            if len(md_files) < 8:
                company_validation.append(f"{company}: {len(md_files)}/8 diagrams")
                if missing_diagrams:
                    self.results.append(ValidationResult(
                        section='Systems',
                        status='warning',
                        message=f'{company} missing diagrams: {", ".join(missing_diagrams)}',
                        details=missing_diagrams
                    ))
            else:
                company_validation.append(f"{company}: ✅ {len(md_files)} diagrams")

        self.results.append(ValidationResult(
            section='Systems',
            status='info',
            message=f'Systems validation: {len(actual_companies)} companies found',
            details=company_validation[:10]  # Show first 10 to avoid clutter
        ))

    def validate_top_level_sections(self) -> None:
        """Validate top-level sections (incidents, comparisons)."""
        for section in self.expected_structure['top_level_sections']:
            if section == 'systems':
                continue  # Already validated

            section_path = self.docs_dir / section
            if section_path.exists() and section_path.is_dir():
                md_files = list(section_path.rglob('*.md'))
                self.results.append(ValidationResult(
                    section='TopLevel',
                    status='success',
                    message=f'{section.title()} section exists with {len(md_files)} files',
                    details=[f'{len(md_files)} markdown files']
                ))
            else:
                self.results.append(ValidationResult(
                    section='TopLevel',
                    status='error',
                    message=f'{section.title()} section missing',
                    details=[f'Expected: docs/{section}/']
                ))

    def validate_legacy_structure_cleanup(self) -> None:
        """Check if old structure has been properly cleaned up."""
        # Check for old debugging at top level (should now be under operations)
        old_paths_to_check = [
            ('debugging', 'Should be under Operations parent'),
            ('production', 'Should be under Operations parent'),
        ]

        warnings = []
        for old_path, reason in old_paths_to_check:
            old_dir = self.docs_dir / old_path
            if old_dir.exists():
                warnings.append(f'{old_path}: {reason}')

        if warnings:
            self.results.append(ValidationResult(
                section='Migration',
                status='info',
                message='Structure appears to be migrated (debugging/production at top level)',
                details=warnings
            ))

    def validate_mkdocs_config(self) -> None:
        """Validate that mkdocs.yml reflects new navigation structure."""
        mkdocs_path = self.docs_dir.parent / 'mkdocs.yml'

        if not mkdocs_path.exists():
            self.results.append(ValidationResult(
                section='Config',
                status='error',
                message='mkdocs.yml not found',
                details=['Expected: site/mkdocs.yml']
            ))
            return

        try:
            content = mkdocs_path.read_text()

            # Check for Home section in nav
            if 'Home:' in content:
                self.results.append(ValidationResult(
                    section='Config',
                    status='success',
                    message='mkdocs.yml contains Home section',
                    details=['Home section found in navigation']
                ))
            else:
                self.results.append(ValidationResult(
                    section='Config',
                    status='warning',
                    message='mkdocs.yml missing Home section in navigation',
                    details=['Check nav structure in mkdocs.yml']
                ))

            # Check for Operations structure
            if 'Operations:' in content or 'debugging:' in content:
                self.results.append(ValidationResult(
                    section='Config',
                    status='info',
                    message='mkdocs.yml contains Operations-related sections',
                    details=['Operations structure detected']
                ))

        except Exception as e:
            self.results.append(ValidationResult(
                section='Config',
                status='error',
                message=f'Error reading mkdocs.yml: {str(e)}',
                details=[str(e)]
            ))

    def run_validation(self) -> bool:
        """Run all validation checks."""
        print("🔍 Running Migration Validation Suite for DS Framework v5.0")
        print("=" * 60)

        if not self.docs_dir.exists():
            print(f"❌ Documentation directory not found: {self.docs_dir}")
            return False

        # Run all validations
        self.validate_home_section()
        self.validate_operations_section()
        self.validate_systems_section()
        self.validate_top_level_sections()
        self.validate_legacy_structure_cleanup()
        self.validate_mkdocs_config()

        # Report results
        self.report_results()

        # Return success if no errors
        error_count = len([r for r in self.results if r.status == 'error'])
        return error_count == 0

    def report_results(self) -> None:
        """Report validation results in a structured format."""
        sections = {}

        # Group results by section
        for result in self.results:
            if result.section not in sections:
                sections[result.section] = []
            sections[result.section].append(result)

        # Report by section
        for section_name, section_results in sections.items():
            print(f"\n📂 {section_name} Section:")

            for result in section_results:
                icon = {
                    'success': '✅',
                    'error': '❌',
                    'warning': '⚠️',
                    'info': 'ℹ️'
                }.get(result.status, '•')

                print(f"   {icon} {result.message}")

                if result.details and len(result.details) <= 5:
                    for detail in result.details:
                        print(f"      → {detail}")
                elif result.details and len(result.details) > 5:
                    for detail in result.details[:3]:
                        print(f"      → {detail}")
                    print(f"      → ... and {len(result.details) - 3} more")

        # Summary
        total = len(self.results)
        errors = len([r for r in self.results if r.status == 'error'])
        warnings = len([r for r in self.results if r.status == 'warning'])
        success = len([r for r in self.results if r.status == 'success'])

        print("\n" + "=" * 60)
        print("📊 Migration Validation Summary:")
        print(f"   Total checks: {total}")
        print(f"   ✅ Success: {success}")
        print(f"   ⚠️  Warnings: {warnings}")
        print(f"   ❌ Errors: {errors}")

        if errors == 0:
            print("\n🎉 Migration validation passed!")
        else:
            print(f"\n🚨 Migration validation failed with {errors} errors")

    def export_results(self, output_path: Path) -> None:
        """Export results to JSON for CI/CD integration."""
        export_data = {
            'validation_date': str(os.path.datetime.now()),
            'total_checks': len(self.results),
            'errors': [r.__dict__ for r in self.results if r.status == 'error'],
            'warnings': [r.__dict__ for r in self.results if r.status == 'warning'],
            'success': [r.__dict__ for r in self.results if r.status == 'success'],
            'summary': {
                'passed': len([r for r in self.results if r.status == 'error']) == 0,
                'error_count': len([r for r in self.results if r.status == 'error']),
                'warning_count': len([r for r in self.results if r.status == 'warning'])
            }
        }

        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)

        print(f"📄 Results exported to: {output_path}")

def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description='DS Framework v5.0 Migration Validator')
    parser.add_argument('--docs-dir', type=str, default='docs',
                       help='Documentation directory (default: docs)')
    parser.add_argument('--export', type=str,
                       help='Export results to JSON file')
    parser.add_argument('--quiet', action='store_true',
                       help='Suppress detailed output')

    args = parser.parse_args()

    docs_dir = Path(args.docs_dir)
    validator = NavigationMigrationValidator(docs_dir)

    success = validator.run_validation()

    if args.export:
        validator.export_results(Path(args.export))

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())