#!/usr/bin/env python3
"""
Unified Status Tracker for Atlas Project
Tracks both creation progress and review/update status in one system
"""

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import hashlib
from enum import Enum

class DiagramStatus(Enum):
    """Unified status enum for all diagrams"""
    NOT_CREATED = "not_created"          # Planned but not yet created
    DRAFT = "draft"                       # Initial creation, not reviewed
    NEEDS_UPDATE = "needs_update"        # Created but needs spec updates
    IN_REVIEW = "in_review"              # Currently being reviewed/updated
    UP_TO_DATE = "up_to_date"           # Fully compliant with latest specs
    DEPRECATED = "deprecated"             # No longer needed

class UnifiedStatusTracker:
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.docs_path = self.base_path / "docs"
        self.data_path = self.base_path / "data"
        self.readonly_spec_path = self.base_path.parent / "readonly-spec"

        # Unified tracking file
        self.unified_tracking_file = self.data_path / "unified_diagram_status.json"
        self.spec_compliance_file = self.data_path / "spec_compliance.json"

        # Ensure data directory exists
        self.data_path.mkdir(exist_ok=True)

        # Load or initialize tracking data
        self.tracking_data = self.load_tracking_data()
        self.spec_compliance = self.load_spec_compliance()

        # Define expected diagram distribution with updated navigation structure
        self.expected_distribution = {
            "systems": {
                "total": 240,  # 30 systems × 8 diagrams
                "per_system": 8,
                "systems": ["netflix", "uber", "amazon", "google", "meta", "microsoft",
                           "linkedin", "twitter", "stripe", "spotify", "airbnb", "discord",
                           "cloudflare", "github", "shopify", "doordash", "slack", "pinterest",
                           "twitch", "coinbase", "reddit", "datadog", "robinhood", "zoom",
                           "tiktok", "square", "snap", "dropbox", "instacart", "openai"]
            },
            "incidents": {"total": 100},
            "debugging": {"total": 100},
            "patterns": {"total": 80},  # Includes foundation, guarantees, mechanisms
            "performance": {"total": 80},
            "scaling": {"total": 80},
            "costs": {"total": 60},
            "migrations": {"total": 60},
            "capacity": {"total": 60},
            "comparisons": {"total": 40},
            "production": {"total": 20}  # New top-level production category
        }

    def load_tracking_data(self) -> Dict:
        """Load unified tracking data"""
        if self.unified_tracking_file.exists():
            with open(self.unified_tracking_file, 'r') as f:
                return json.load(f)
        return {
            "metadata": {
                "last_updated": None,
                "last_spec_check": None,
                "total_target": 900,
                "creation_start_date": datetime.now().isoformat()
            },
            "diagrams": {},
            "systems": {},
            "summary": {
                "total_created": 0,
                "total_updated": 0,
                "total_reviewed": 0
            }
        }

    def load_spec_compliance(self) -> Dict:
        """Load spec compliance requirements"""
        if self.spec_compliance_file.exists():
            with open(self.spec_compliance_file, 'r') as f:
                return json.load(f)
        return {
            "requirements": {
                "four_plane_architecture": True,
                "visual_first": True,
                "production_metrics": True,
                "failure_scenarios": True,
                "cost_information": True,
                "slo_labels": True,
                "specific_technologies": True
            },
            "spec_versions": {
                "02-DIAGRAM-SPECIFICATIONS-V3.md": None
                # Visual specs merged into 02-DIAGRAM-SPECIFICATIONS-V3.md
            }
        }

    def save_tracking_data(self):
        """Save unified tracking data"""
        self.tracking_data["metadata"]["last_updated"] = datetime.now().isoformat()
        with open(self.unified_tracking_file, 'w') as f:
            json.dump(self.tracking_data, f, indent=2)

    def save_spec_compliance(self):
        """Save spec compliance data"""
        with open(self.spec_compliance_file, 'w') as f:
            json.dump(self.spec_compliance, f, indent=2)

    def calculate_content_hash(self, content: str) -> str:
        """Calculate hash of diagram content"""
        mermaid_blocks = re.findall(r'```mermaid\n(.*?)\n```', content, re.DOTALL)
        diagram_content = '\n'.join(mermaid_blocks)
        return hashlib.md5(diagram_content.encode()).hexdigest()[:8]

    def scan_all_diagrams(self) -> Dict:
        """Scan all diagrams and update unified status"""
        scan_results = {
            "timestamp": datetime.now().isoformat(),
            "files_scanned": 0,
            "diagrams_found": 0,
            "new_diagrams": 0,
            "updated_diagrams": 0,
            "by_status": {},
            "by_category": {}
        }

        # First, mark all expected diagrams
        self.initialize_expected_diagrams()

        # Scan actual files
        for md_file in self.docs_path.rglob("*.md"):
            if md_file.is_file():
                content = md_file.read_text()
                mermaid_count = len(re.findall(r'```mermaid', content))

                if mermaid_count > 0:
                    rel_path = str(md_file.relative_to(self.docs_path))
                    scan_results["files_scanned"] += 1
                    scan_results["diagrams_found"] += mermaid_count

                    # Update or create diagram entry
                    diagram_id = self.get_diagram_id(rel_path)
                    is_new = diagram_id not in self.tracking_data["diagrams"]

                    if is_new:
                        scan_results["new_diagrams"] += 1

                    diagram_info = self.update_diagram_status(
                        diagram_id,
                        rel_path,
                        content,
                        mermaid_count
                    )

                    # Update category counts
                    category = diagram_info["category"]
                    if category not in scan_results["by_category"]:
                        scan_results["by_category"][category] = 0
                    scan_results["by_category"][category] += mermaid_count

                    # Update status counts
                    status = diagram_info["status"]
                    if status not in scan_results["by_status"]:
                        scan_results["by_status"][status] = 0
                    scan_results["by_status"][status] += 1

        self.save_tracking_data()
        return scan_results

    def initialize_expected_diagrams(self):
        """Initialize entries for all expected diagrams"""
        # Systems diagrams (30 systems × 8 diagrams each)
        for system in self.expected_distribution["systems"]["systems"]:
            system_id = f"systems/{system}"
            if system_id not in self.tracking_data["systems"]:
                self.tracking_data["systems"][system_id] = {
                    "created": 0,
                    "expected": 8,
                    "diagrams": {}
                }

            # Expected diagram types per system
            diagram_types = [
                "architecture", "request-flow", "storage", "failure-domains",
                "scale-evolution", "cost-breakdown", "novel-solutions", "production-ops"
            ]

            for diagram_type in diagram_types:
                diagram_id = f"{system_id}/{diagram_type}"
                if diagram_id not in self.tracking_data["diagrams"]:
                    self.tracking_data["diagrams"][diagram_id] = {
                        "status": DiagramStatus.NOT_CREATED.value,
                        "category": "systems",
                        "system": system,
                        "type": diagram_type,
                        "created_date": None,
                        "last_updated": None,
                        "last_reviewed": None,
                        "spec_version": None,
                        "file_path": None
                    }

    def get_diagram_id(self, file_path: str) -> str:
        """Generate unique diagram ID from file path"""
        # Remove .md extension and normalize path
        return file_path.replace(".md", "").replace("\\", "/")

    def update_diagram_status(self, diagram_id: str, file_path: str,
                             content: str, diagram_count: int) -> Dict:
        """Update status for a specific diagram"""
        content_hash = self.calculate_content_hash(content)
        category = self.get_category(file_path)

        # Check if diagram exists in tracking
        if diagram_id not in self.tracking_data["diagrams"]:
            # New diagram
            self.tracking_data["diagrams"][diagram_id] = {
                "status": DiagramStatus.DRAFT.value,
                "category": category,
                "created_date": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "last_reviewed": None,
                "spec_version": self.get_current_spec_version(),
                "file_path": file_path,
                "diagram_count": diagram_count,
                "content_hash": content_hash,
                "compliance_score": 0,
                "issues": []
            }
        else:
            # Existing diagram - check if content changed
            existing = self.tracking_data["diagrams"][diagram_id]

            # If this was a not_created entry, mark it as found
            if existing["status"] == DiagramStatus.NOT_CREATED.value:
                existing["status"] = DiagramStatus.DRAFT.value
                existing["created_date"] = datetime.now().isoformat()

            if existing.get("content_hash") != content_hash:
                existing["last_updated"] = datetime.now().isoformat()
                existing["content_hash"] = content_hash

                # Check if update addressed spec compliance
                if existing["status"] == DiagramStatus.NEEDS_UPDATE.value:
                    existing["status"] = DiagramStatus.IN_REVIEW.value

            existing["diagram_count"] = diagram_count
            existing["file_path"] = file_path

        # Perform compliance check
        compliance_result = self.check_compliance(content)
        self.tracking_data["diagrams"][diagram_id]["compliance_score"] = compliance_result["score"]
        self.tracking_data["diagrams"][diagram_id]["issues"] = compliance_result["issues"]

        # Update status based on compliance
        self.update_status_from_compliance(diagram_id, compliance_result)

        # Update system tracking if applicable
        if category == "systems":
            self.update_system_tracking(diagram_id, file_path)

        return self.tracking_data["diagrams"][diagram_id]

    def get_category(self, file_path: str) -> str:
        """Determine category from file path with updated navigation structure"""
        parts = Path(file_path).parts
        if len(parts) > 0:
            category = parts[0]
            # Map to standard categories based on new navigation structure
            category_map = {
                "systems": "systems",
                "incidents": "incidents",
                "debugging": "debugging",
                "patterns": "patterns",
                "performance": "performance",
                "scaling": "scaling",
                "costs": "costs",
                "migrations": "migrations",
                "capacity": "capacity",
                "comparisons": "comparisons",
                # Foundation categories now under Home parent
                "guarantees": "patterns",
                "mechanisms": "patterns",
                "foundation": "patterns",
                "getting-started": "patterns",
                # Production is now its own top-level category
                "production": "production",
                "examples": "patterns",
                "reference": "patterns"
            }
            return category_map.get(category, "other")
        return "unknown"

    def check_compliance(self, content: str) -> Dict:
        """Enhanced compliance check with detailed analysis"""
        issues = []
        checks_passed = 0
        total_checks = 7
        detailed_results = {}

        # 1. Visual-first compliance (enhanced)
        visual_result, visual_issues = self.check_visual_first_detailed(content)
        if visual_result:
            checks_passed += 1
        else:
            issues.extend(visual_issues)
        detailed_results["visual_first"] = {"passed": visual_result, "issues": visual_issues}

        # 2. Four-plane architecture (enhanced)
        plane_result, plane_issues = self.check_four_plane_detailed(content)
        if plane_result:
            checks_passed += 1
        else:
            issues.extend(plane_issues)
        detailed_results["four_plane"] = {"passed": plane_result, "issues": plane_issues}

        # 3. Production metrics (enhanced)
        metrics_result, metrics_issues = self.check_production_metrics_detailed(content)
        if metrics_result:
            checks_passed += 1
        else:
            issues.extend(metrics_issues)
        detailed_results["production_metrics"] = {"passed": metrics_result, "issues": metrics_issues}

        # 4. Failure scenarios (enhanced)
        failure_result, failure_issues = self.check_failure_scenarios_detailed(content)
        if failure_result:
            checks_passed += 1
        else:
            issues.extend(failure_issues)
        detailed_results["failure_scenarios"] = {"passed": failure_result, "issues": failure_issues}

        # 5. Cost information (enhanced)
        cost_result, cost_issues = self.check_cost_information_detailed(content)
        if cost_result:
            checks_passed += 1
        else:
            issues.extend(cost_issues)
        detailed_results["cost_information"] = {"passed": cost_result, "issues": cost_issues}

        # 6. SLO labels (enhanced)
        slo_result, slo_issues = self.check_slo_labels_detailed(content)
        if slo_result:
            checks_passed += 1
        else:
            issues.extend(slo_issues)
        detailed_results["slo_labels"] = {"passed": slo_result, "issues": slo_issues}

        # 7. Specific technologies (enhanced)
        tech_result, tech_issues = self.check_specific_technologies_detailed(content)
        if tech_result:
            checks_passed += 1
        else:
            issues.extend(tech_issues)
        detailed_results["specific_technologies"] = {"passed": tech_result, "issues": tech_issues}

        return {
            "score": int((checks_passed / total_checks) * 100),
            "issues": issues,
            "checks_passed": checks_passed,
            "total_checks": total_checks,
            "detailed_results": detailed_results
        }

    def check_visual_first_detailed(self, content: str) -> Tuple[bool, List[str]]:
        """Enhanced visual-first compliance check"""
        issues = []

        # Check for excessive text between diagrams
        sections = content.split("```mermaid")
        for i, section in enumerate(sections[:-1]):
            text_lines = section.split("```")[-1].strip().split("\n")
            text_lines = [line for line in text_lines if line.strip() and not line.startswith("#")]
            if len(text_lines) > 10:
                issues.append(f"Section {i+1}: Excessive text ({len(text_lines)} lines) between diagrams")

        # Check for code blocks that should be tables
        if "```python" in content or "```javascript" in content or "```java" in content:
            issues.append("Contains code blocks that should be visual representations or tables")

        # Check for verbose paragraphs
        paragraphs = re.findall(r'\n\n([^#\n][^\n]{200,})', content)
        if len(paragraphs) > 2:
            issues.append(f"Contains {len(paragraphs)} verbose paragraphs (>200 chars)")

        return len(issues) == 0, issues

    def check_four_plane_detailed(self, content: str) -> Tuple[bool, List[str]]:
        """Enhanced 4-plane architecture check"""
        issues = []

        # Check for obsolete Stream Plane
        if "Stream Plane" in content or "StreamPlane" in content:
            issues.append("Contains obsolete Stream Plane reference")

        # Check for correct plane names and colors
        mermaid_blocks = re.findall(r'```mermaid\n(.*?)\n```', content, re.DOTALL)
        color_mapping = {
            "#3B82F6": "Edge Plane",
            "#10B981": "Service Plane",
            "#F59E0B": "State Plane",
            "#8B5CF6": "Control Plane"
        }

        for block in mermaid_blocks:
            for color, plane in color_mapping.items():
                if plane in block and color not in block:
                    issues.append(f"Missing color {color} for {plane}")

        return len(issues) == 0, issues

    def check_production_metrics_detailed(self, content: str) -> Tuple[bool, List[str]]:
        """Enhanced production metrics check"""
        issues = []

        # Check for placeholders
        placeholders = ["XXX", "TODO", "REPLACE", "Example", "Sample", "Test", "TBD"]
        found_placeholders = [p for p in placeholders if p in content]
        if found_placeholders:
            issues.append(f"Contains placeholder text: {', '.join(found_placeholders)}")

        # Check for metric types
        metric_checks = {
            "throughput": r'\d+[KMB]?\s*(req/s|RPS|QPS|tps|TPS)',
            "latency": r'(p\d+|avg|mean):\s*\d+\s*(ms|μs|ns)',
            "storage": r'\d+\s*(GB|TB|PB|MB)',
            "cost": r'\$[\d,]+[KMB]?'
        }

        missing_metrics = []
        for metric_type, pattern in metric_checks.items():
            if not re.search(pattern, content, re.IGNORECASE):
                missing_metrics.append(metric_type)

        if len(missing_metrics) > 2:
            issues.append(f"Missing metrics: {', '.join(missing_metrics)}")

        return len(issues) == 0, issues

    def check_failure_scenarios_detailed(self, content: str) -> Tuple[bool, List[str]]:
        """Enhanced failure scenario check"""
        issues = []

        failure_keywords = [
            "failure", "outage", "incident", "recovery", "rollback",
            "circuit breaker", "retry", "timeout", "failover", "degradation"
        ]

        found_keywords = [kw for kw in failure_keywords if kw.lower() in content.lower()]
        if len(found_keywords) < 2:
            issues.append(f"Insufficient failure coverage: {', '.join(found_keywords) if found_keywords else 'none'}")

        # Check for MTTR/MTTD metrics
        if not re.search(r'(MTTR|MTTD|recovery time|detection time)', content, re.IGNORECASE):
            issues.append("No MTTR/MTTD metrics documented")

        return len(issues) == 0, issues

    def check_cost_information_detailed(self, content: str) -> Tuple[bool, List[str]]:
        """Enhanced cost and resource check"""
        issues = []

        cost_patterns = [
            r'\$[\d,]+',
            r'(monthly|annual|yearly|daily)\s*cost',
            r'(r\d+|m\d+|c\d+|t\d+)\.\w+',
            r'\d+\s*(vCPU|cores|GB\s*RAM)',
            r'(reserved|on-demand|spot)'
        ]

        found_patterns = sum(1 for pattern in cost_patterns if re.search(pattern, content, re.IGNORECASE))
        if found_patterns < 2:
            issues.append(f"Insufficient cost/resource info (found {found_patterns}/5 patterns)")

        return len(issues) == 0, issues

    def check_slo_labels_detailed(self, content: str) -> Tuple[bool, List[str]]:
        """Enhanced SLO/SLA labels check"""
        issues = []

        mermaid_blocks = re.findall(r'```mermaid\n(.*?)\n```', content, re.DOTALL)
        if not mermaid_blocks:
            return True, []

        for i, block in enumerate(mermaid_blocks):
            if "-->" in block or "---" in block:
                slo_patterns = [r'p\d+:\s*\d+', r'\d+ms', r'SL[OA]:\s*\d+', r'\d+\.?\d*%']
                has_metrics = any(re.search(pattern, block, re.IGNORECASE) for pattern in slo_patterns)
                if not has_metrics:
                    issues.append(f"Diagram {i+1}: Has edges but no SLO labels")

        return len(issues) == 0, issues

    def check_specific_technologies_detailed(self, content: str) -> Tuple[bool, List[str]]:
        """Enhanced specific technology check"""
        issues = []

        generic_terms = ["Database", "Cache", "Queue", "Service", "API", "Storage"]
        for term in generic_terms:
            pattern = f'{term}(?![\\s\\-]*(Redis|MySQL|PostgreSQL|Kafka|RabbitMQ|S3|DynamoDB))'
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(f"Generic term '{term}' without specific technology")

        # Check for version numbers
        if not re.search(r'(Redis|MySQL|PostgreSQL|Kafka|MongoDB)\s+\d+', content):
            issues.append("No technology version numbers found")

        return len(issues) == 0, issues

    def update_status_from_compliance(self, diagram_id: str, compliance_result: Dict):
        """Update diagram status based on compliance score"""
        score = compliance_result["score"]
        current_status = self.tracking_data["diagrams"][diagram_id]["status"]

        # Don't override NOT_CREATED status (but allow DRAFT and others)
        if current_status == DiagramStatus.NOT_CREATED.value:
            return

        if score == 100:
            self.tracking_data["diagrams"][diagram_id]["status"] = DiagramStatus.UP_TO_DATE.value
        elif score >= 80:
            if current_status != DiagramStatus.UP_TO_DATE.value:
                self.tracking_data["diagrams"][diagram_id]["status"] = DiagramStatus.IN_REVIEW.value
        else:
            self.tracking_data["diagrams"][diagram_id]["status"] = DiagramStatus.NEEDS_UPDATE.value

    def update_system_tracking(self, diagram_id: str, file_path: str):
        """Update system-specific tracking"""
        parts = Path(file_path).parts
        if len(parts) >= 2 and parts[0] == "systems":
            system_name = parts[1]
            system_id = f"systems/{system_name}"

            if system_id not in self.tracking_data["systems"]:
                self.tracking_data["systems"][system_id] = {
                    "created": 0,
                    "expected": 8,
                    "diagrams": {}
                }

            # Update diagram reference
            self.tracking_data["systems"][system_id]["diagrams"][diagram_id] = True
            self.tracking_data["systems"][system_id]["created"] = len(
                self.tracking_data["systems"][system_id]["diagrams"]
            )

    def get_current_spec_version(self) -> str:
        """Get current spec version hash"""
        spec_files = [
            self.readonly_spec_path / "02-DIAGRAM-SPECIFICATIONS-V3.md"
            # Visual specs merged into 02-DIAGRAM-SPECIFICATIONS-V3.md
        ]

        version_parts = []
        for spec_file in spec_files:
            if spec_file.exists():
                mtime = spec_file.stat().st_mtime
                version_parts.append(str(int(mtime)))

        return hashlib.md5(''.join(version_parts).encode()).hexdigest()[:8]

    def generate_unified_dashboard(self) -> str:
        """Generate comprehensive unified status dashboard"""
        dashboard = []

        # Header
        dashboard.append("=" * 80)
        dashboard.append("ATLAS PROJECT UNIFIED STATUS DASHBOARD".center(80))
        dashboard.append("=" * 80)
        dashboard.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        dashboard.append("")

        # Overall Progress Bar
        total_created = sum(1 for d in self.tracking_data["diagrams"].values()
                          if d["status"] != DiagramStatus.NOT_CREATED.value)
        total_target = self.tracking_data["metadata"]["total_target"]
        progress_pct = (total_created / total_target) * 100 if total_target > 0 else 0

        progress_bar = self.create_progress_bar(progress_pct)
        dashboard.append("📊 OVERALL PROGRESS")
        dashboard.append(progress_bar)
        dashboard.append(f"Created: {total_created}/{total_target} ({progress_pct:.1f}%)")
        dashboard.append("")

        # Status Distribution
        status_counts = {}
        for diagram in self.tracking_data["diagrams"].values():
            status = diagram["status"]
            status_counts[status] = status_counts.get(status, 0) + 1

        dashboard.append("📈 STATUS DISTRIBUTION")
        dashboard.append("-" * 40)

        status_emojis = {
            DiagramStatus.NOT_CREATED.value: "⬜",
            DiagramStatus.DRAFT.value: "📝",
            DiagramStatus.NEEDS_UPDATE.value: "⚠️",
            DiagramStatus.IN_REVIEW.value: "🔄",
            DiagramStatus.UP_TO_DATE.value: "✅",
            DiagramStatus.DEPRECATED.value: "🚫"
        }

        for status, emoji in status_emojis.items():
            count = status_counts.get(status, 0)
            percentage = (count / len(self.tracking_data["diagrams"])) * 100 if self.tracking_data["diagrams"] else 0
            status_label = status.replace("_", " ").title()
            dashboard.append(f"{emoji} {status_label}: {count} ({percentage:.1f}%)")
        dashboard.append("")

        # Category Progress
        dashboard.append("📂 CATEGORY PROGRESS")
        dashboard.append("-" * 40)

        category_stats = self.calculate_category_stats()
        for category, stats in sorted(category_stats.items()):
            if stats["expected"] > 0:
                progress = (stats["created"] / stats["expected"]) * 100
                bar = self.create_mini_progress_bar(progress)
                dashboard.append(f"{category:15} {bar} {stats['created']:3}/{stats['expected']:3} ({progress:.0f}%)")
        dashboard.append("")

        # System Coverage (Top Priority)
        dashboard.append("🏢 SYSTEM DOCUMENTATION COVERAGE")
        dashboard.append("-" * 40)

        systems_summary = self.get_systems_summary()
        for status, systems in systems_summary.items():
            if systems:
                emoji = {
                    "complete": "✅",
                    "partial": "🔶",
                    "not_started": "⬜"
                }.get(status, "❓")
                dashboard.append(f"{emoji} {status.replace('_', ' ').title()}: {len(systems)} systems")
                if status != "complete":  # Show which systems need work
                    dashboard.append(f"    {', '.join(systems[:5])}")
                    if len(systems) > 5:
                        dashboard.append(f"    ... and {len(systems) - 5} more")
        dashboard.append("")

        # Compliance Summary
        dashboard.append("🔍 COMPLIANCE SUMMARY")
        dashboard.append("-" * 40)

        compliance_stats = self.calculate_compliance_stats()
        dashboard.append(f"Average Compliance Score: {compliance_stats['average_score']:.1f}%")
        dashboard.append(f"Fully Compliant (100%): {compliance_stats['fully_compliant']} diagrams")
        dashboard.append(f"Need Updates (<80%): {compliance_stats['need_updates']} diagrams")

        if compliance_stats["common_issues"]:
            dashboard.append("\nMost Common Issues:")
            for issue, count in compliance_stats["common_issues"][:3]:
                dashboard.append(f"  • {issue}: {count} occurrences")
        dashboard.append("")

        # Action Items
        dashboard.append("⚡ IMMEDIATE ACTION ITEMS")
        dashboard.append("-" * 40)

        action_items = self.generate_action_items()
        for priority, items in action_items.items():
            if items:
                emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(priority, "⚪")
                dashboard.append(f"\n{emoji} {priority} PRIORITY:")
                for item in items[:3]:  # Show top 3 per priority
                    dashboard.append(f"  • {item}")

        # Weekly Stats
        dashboard.append("")
        dashboard.append("📅 WEEKLY STATISTICS")
        dashboard.append("-" * 40)

        week_stats = self.calculate_weekly_stats()
        dashboard.append(f"Created This Week: {week_stats['created_this_week']} diagrams")
        dashboard.append(f"Updated This Week: {week_stats['updated_this_week']} diagrams")
        dashboard.append(f"Reviewed This Week: {week_stats['reviewed_this_week']} diagrams")
        dashboard.append(f"Weekly Velocity: {week_stats['velocity']:.1f} diagrams/week")
        dashboard.append("")

        # Footer
        dashboard.append("=" * 80)
        dashboard.append("Run 'python unified_status_tracker.py --details' for detailed breakdown")

        return "\n".join(dashboard)

    def create_progress_bar(self, percentage: float, width: int = 50) -> str:
        """Create ASCII progress bar"""
        filled = int(width * percentage / 100)
        empty = width - filled
        bar = "█" * filled + "░" * empty
        return f"[{bar}] {percentage:.1f}%"

    def create_mini_progress_bar(self, percentage: float, width: int = 20) -> str:
        """Create mini ASCII progress bar"""
        filled = int(width * percentage / 100)
        empty = width - filled
        bar = "▓" * filled + "░" * empty
        return f"[{bar}]"

    def calculate_category_stats(self) -> Dict:
        """Calculate statistics by category"""
        stats = {}

        for category, expected in self.expected_distribution.items():
            if isinstance(expected, dict) and "total" in expected:
                expected_count = expected["total"]
            else:
                continue

            created_count = sum(1 for d in self.tracking_data["diagrams"].values()
                              if d["category"] == category and
                              d["status"] != DiagramStatus.NOT_CREATED.value)

            stats[category] = {
                "created": created_count,
                "expected": expected_count,
                "up_to_date": sum(1 for d in self.tracking_data["diagrams"].values()
                                 if d["category"] == category and
                                 d["status"] == DiagramStatus.UP_TO_DATE.value)
            }

        return stats

    def get_systems_summary(self) -> Dict:
        """Get summary of system documentation status"""
        summary = {
            "complete": [],
            "partial": [],
            "not_started": []
        }

        for system_name in self.expected_distribution["systems"]["systems"]:
            system_id = f"systems/{system_name}"
            if system_id in self.tracking_data["systems"]:
                created = self.tracking_data["systems"][system_id]["created"]
                if created >= 8:
                    summary["complete"].append(system_name)
                elif created > 0:
                    summary["partial"].append(system_name)
                else:
                    summary["not_started"].append(system_name)
            else:
                summary["not_started"].append(system_name)

        return summary

    def calculate_compliance_stats(self) -> Dict:
        """Calculate compliance statistics"""
        scores = []
        issue_counts = {}

        for diagram in self.tracking_data["diagrams"].values():
            if "compliance_score" in diagram:
                scores.append(diagram["compliance_score"])

                for issue in diagram.get("issues", []):
                    issue_counts[issue] = issue_counts.get(issue, 0) + 1

        return {
            "average_score": sum(scores) / len(scores) if scores else 0,
            "fully_compliant": sum(1 for s in scores if s == 100),
            "need_updates": sum(1 for s in scores if s < 80),
            "common_issues": sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        }

    def generate_action_items(self) -> Dict:
        """Generate prioritized action items"""
        actions = {
            "HIGH": [],
            "MEDIUM": [],
            "LOW": []
        }

        # Check for Stream Plane issues (HIGH priority)
        stream_plane_count = sum(1 for d in self.tracking_data["diagrams"].values()
                                if "Stream Plane" in ' '.join(d.get("issues", [])))
        if stream_plane_count > 0:
            actions["HIGH"].append(f"Remove Stream Plane references from {stream_plane_count} diagrams")

        # Check for missing systems (HIGH priority)
        systems_summary = self.get_systems_summary()
        if len(systems_summary["not_started"]) > 0:
            actions["HIGH"].append(f"Start documentation for {len(systems_summary['not_started'])} systems")

        # Check for low compliance scores (MEDIUM priority)
        low_compliance = sum(1 for d in self.tracking_data["diagrams"].values()
                           if d.get("compliance_score", 100) < 60)
        if low_compliance > 0:
            actions["MEDIUM"].append(f"Fix {low_compliance} diagrams with compliance < 60%")

        # Check for outdated reviews (LOW priority)
        needs_review = sum(1 for d in self.tracking_data["diagrams"].values()
                         if d["status"] == DiagramStatus.NEEDS_UPDATE.value)
        if needs_review > 0:
            actions["LOW"].append(f"Review and update {needs_review} diagrams")

        return actions

    def calculate_weekly_stats(self) -> Dict:
        """Calculate statistics for the past week"""
        one_week_ago = datetime.now() - timedelta(days=7)

        created_this_week = 0
        updated_this_week = 0
        reviewed_this_week = 0

        for diagram in self.tracking_data["diagrams"].values():
            if diagram.get("created_date"):
                created_date = datetime.fromisoformat(diagram["created_date"])
                if created_date >= one_week_ago:
                    created_this_week += 1

            if diagram.get("last_updated"):
                updated_date = datetime.fromisoformat(diagram["last_updated"])
                if updated_date >= one_week_ago:
                    updated_this_week += 1

            if diagram.get("last_reviewed"):
                reviewed_date = datetime.fromisoformat(diagram["last_reviewed"])
                if reviewed_date >= one_week_ago:
                    reviewed_this_week += 1

        # Calculate velocity
        if self.tracking_data["metadata"].get("creation_start_date"):
            start_date = datetime.fromisoformat(self.tracking_data["metadata"]["creation_start_date"])
            weeks_elapsed = (datetime.now() - start_date).days / 7
            total_created = sum(1 for d in self.tracking_data["diagrams"].values()
                              if d["status"] != DiagramStatus.NOT_CREATED.value)
            velocity = total_created / weeks_elapsed if weeks_elapsed > 0 else 0
        else:
            velocity = 0

        return {
            "created_this_week": created_this_week,
            "updated_this_week": updated_this_week,
            "reviewed_this_week": reviewed_this_week,
            "velocity": velocity
        }

    def update_central_metrics(self):
        """Update the central metrics file with current status"""
        central_metrics_file = self.data_path / "CENTRAL_METRICS.json"

        # Calculate all metrics
        total_created = sum(1 for d in self.tracking_data["diagrams"].values()
                          if d["status"] != DiagramStatus.NOT_CREATED.value)

        status_counts = {}
        for diagram in self.tracking_data["diagrams"].values():
            status = diagram["status"]
            status_counts[status] = status_counts.get(status, 0) + 1

        category_stats = self.calculate_category_stats()
        systems_summary = self.get_systems_summary()
        compliance_stats = self.calculate_compliance_stats()
        weekly_stats = self.calculate_weekly_stats()

        # Build central metrics
        central_metrics = {
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "description": "Single source of truth for ALL Atlas project metrics. Updated ONLY by scripts.",
                "update_script": "scripts/unified_status_tracker.py",
                "warning": "DO NOT manually edit this file. All updates must come from automated scripts."
            },
            "targets": {
                "total_diagrams": 900,
                "total_systems": 30,
                "diagrams_per_system": 8,
                "timeline_weeks": 36,
                "team_size": 3,
                "weekly_hours": 60
            },
            "current_status": {
                "diagrams_created": total_created,
                "files_created": len([d for d in self.tracking_data["diagrams"].values() if d.get("file_path")]),
                "systems_documented": {
                    "complete": len(systems_summary["complete"]),
                    "partial": len(systems_summary["partial"]),
                    "not_started": len(systems_summary["not_started"])
                },
                "specifications": {
                    "total": 16,
                    "streamlined_from": 26
                },
                "compliance": {
                    "average_score": compliance_stats["average_score"],
                    "fully_compliant": compliance_stats["fully_compliant"],
                    "needs_updates": compliance_stats["need_updates"],
                    "non_compliant": sum(1 for d in self.tracking_data["diagrams"].values()
                                        if d.get("compliance_score", 100) < 60)
                }
            },
            "progress_percentages": {
                "overall": (total_created / 900) * 100,
                "systems": (len(systems_summary["complete"]) / 30) * 100,
                "specifications": 100.0,
                "quality_compliance": compliance_stats["average_score"]
            },
            "status_distribution": {
                "not_created": status_counts.get(DiagramStatus.NOT_CREATED.value, 0),
                "needs_update": status_counts.get(DiagramStatus.NEEDS_UPDATE.value, 0),
                "in_review": status_counts.get(DiagramStatus.IN_REVIEW.value, 0),
                "up_to_date": status_counts.get(DiagramStatus.UP_TO_DATE.value, 0)
            },
            "category_breakdown": {
                category: stats["created"]
                for category, stats in category_stats.items()
            },
            "timeline": {
                "project_start": self.tracking_data["metadata"].get("creation_start_date", datetime.now().isoformat())[:10],
                "current_week": max(1, min(36, int((datetime.now() - datetime.fromisoformat(
                    self.tracking_data["metadata"].get("creation_start_date", datetime.now().isoformat())
                )).days / 7) + 1)),
                "weeks_remaining": max(0, 36 - int((datetime.now() - datetime.fromisoformat(
                    self.tracking_data["metadata"].get("creation_start_date", datetime.now().isoformat())
                )).days / 7)),
                "estimated_completion": (datetime.now() + timedelta(weeks=max(1, (900 - total_created) / max(1, weekly_stats["velocity"])))).isoformat()[:10],
                "current_velocity": weekly_stats["velocity"],
                "required_velocity": max(1, (900 - total_created) / max(1, 35))
            },
            "quality_metrics": {
                "with_slo_labels": sum(1 for d in self.tracking_data["diagrams"].values()
                                     if "Missing SLO labels" not in d.get("issues", [])),
                "with_cost_data": sum(1 for d in self.tracking_data["diagrams"].values()
                                    if "No cost/resource information" not in d.get("issues", [])),
                "with_failure_scenarios": sum(1 for d in self.tracking_data["diagrams"].values()
                                            if "No failure scenarios" not in d.get("issues", [])),
                "following_4_plane": sum(1 for d in self.tracking_data["diagrams"].values()
                                       if "Stream Plane" not in ' '.join(d.get("issues", []))),
                "production_ready": compliance_stats["fully_compliant"],
                "emergency_ready": sum(1 for d in self.tracking_data["diagrams"].values()
                                     if d.get("compliance_score", 0) >= 80)
            },
            "execution": {
                "last_review": datetime.now().isoformat(),
                "next_milestone": f"Week {min(36, int((datetime.now() - datetime.fromisoformat(self.tracking_data['metadata'].get('creation_start_date', datetime.now().isoformat()))).days / 7) + 2)}: {min(900, total_created + 100)} diagrams",
                "blockers": [],
                "3am_test_time": "< 3 minutes",
                "navigation_clicks": 3
            }
        }

        # Write to central metrics file
        with open(central_metrics_file, 'w') as f:
            json.dump(central_metrics, f, indent=2)

        return central_metrics

    def export_status_report(self, format: str = "json") -> str:
        """Export comprehensive status report"""
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_diagrams": len(self.tracking_data["diagrams"]),
                "total_created": sum(1 for d in self.tracking_data["diagrams"].values()
                                   if d["status"] != DiagramStatus.NOT_CREATED.value),
                "total_target": self.tracking_data["metadata"]["total_target"]
            },
            "by_status": {},
            "by_category": self.calculate_category_stats(),
            "systems": self.get_systems_summary(),
            "compliance": self.calculate_compliance_stats(),
            "weekly_stats": self.calculate_weekly_stats(),
            "action_items": self.generate_action_items()
        }

        # Count by status
        for diagram in self.tracking_data["diagrams"].values():
            status = diagram["status"]
            report_data["by_status"][status] = report_data["by_status"].get(status, 0) + 1

        if format == "json":
            output_file = self.data_path / f"unified_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            return str(output_file)
        else:
            return json.dumps(report_data, indent=2)


def main():
    """Main entry point for unified status tracking"""
    import argparse

    parser = argparse.ArgumentParser(description="Unified status tracking for Atlas project")
    parser.add_argument("--scan", action="store_true", help="Scan all diagrams and update status")
    parser.add_argument("--dashboard", action="store_true", help="Generate unified dashboard")
    parser.add_argument("--details", help="Show detailed status for category or system")
    parser.add_argument("--export", help="Export status report (json format)")
    parser.add_argument("--mark-reviewed", help="Mark diagram as reviewed", metavar="FILE")
    parser.add_argument("--update-status", help="Update status for diagram", metavar="FILE")
    parser.add_argument("--status", help="New status value", choices=[s.value for s in DiagramStatus])
    parser.add_argument("--update-central", action="store_true", help="Update central metrics file")

    args = parser.parse_args()

    tracker = UnifiedStatusTracker()

    if args.scan:
        print("🔍 Scanning all diagrams...")
        results = tracker.scan_all_diagrams()
        print(f"✅ Scanned {results['files_scanned']} files")
        print(f"📊 Found {results['diagrams_found']} diagrams")
        print(f"🆕 New diagrams: {results['new_diagrams']}")
        print(f"🔄 Updated diagrams: {results['updated_diagrams']}")
        # Automatically update central metrics after scan
        tracker.update_central_metrics()
        print("📈 Central metrics updated")
    elif args.update_central:
        print("📈 Updating central metrics...")
        tracker.scan_all_diagrams()  # Ensure data is current
        metrics = tracker.update_central_metrics()
        print(f"✅ Central metrics updated at: data/CENTRAL_METRICS.json")
        print(f"📊 Diagrams: {metrics['current_status']['diagrams_created']}/{metrics['targets']['total_diagrams']}")
        print(f"🎯 Progress: {metrics['progress_percentages']['overall']:.1f}%")
    elif args.dashboard:
        print(tracker.generate_unified_dashboard())
    elif args.details:
        # Show detailed status for specific category or system
        category = args.details
        print(f"\n📊 Detailed Status: {category}")
        print("=" * 60)

        diagrams = [d for d in tracker.tracking_data["diagrams"].items()
                   if category in d[0] or d[1].get("category") == category]

        for diagram_id, info in sorted(diagrams):
            status_emoji = {
                DiagramStatus.NOT_CREATED.value: "⬜",
                DiagramStatus.DRAFT.value: "📝",
                DiagramStatus.NEEDS_UPDATE.value: "⚠️",
                DiagramStatus.IN_REVIEW.value: "🔄",
                DiagramStatus.UP_TO_DATE.value: "✅"
            }.get(info["status"], "❓")

            compliance = info.get("compliance_score", 0)
            print(f"{status_emoji} {diagram_id}")
            print(f"   Status: {info['status']}")
            print(f"   Compliance: {compliance}%")
            if info.get("issues"):
                print(f"   Issues: {', '.join(info['issues'][:2])}")
            print()
    elif args.mark_reviewed:
        # Handle different path formats
        file_path = args.mark_reviewed

        # Try multiple path formats
        possible_ids = [
            tracker.get_diagram_id(file_path),  # As provided
            tracker.get_diagram_id(file_path.replace("docs/", "")),  # Remove docs/ prefix
            tracker.get_diagram_id(Path(file_path).name),  # Just filename
        ]

        # Also try if it's already an ID without .md
        if not file_path.endswith('.md'):
            possible_ids.append(file_path)

        diagram_id = None
        for possible_id in possible_ids:
            if possible_id in tracker.tracking_data["diagrams"]:
                diagram_id = possible_id
                break

        if diagram_id:
            tracker.tracking_data["diagrams"][diagram_id]["last_reviewed"] = datetime.now().isoformat()
            tracker.tracking_data["diagrams"][diagram_id]["status"] = DiagramStatus.UP_TO_DATE.value
            tracker.save_tracking_data()
            print(f"✅ Marked {diagram_id} as reviewed")
        else:
            print(f"❌ Diagram not found: {file_path}")
            print(f"   Tried: {', '.join(possible_ids)}")
            print(f"   Available IDs starting with similar path:")
            for key in tracker.tracking_data["diagrams"].keys():
                if any(pid in key for pid in possible_ids if pid):
                    print(f"     - {key}")
    elif args.update_status and args.status:
        # Handle different path formats
        file_path = args.update_status

        # Try multiple path formats
        possible_ids = [
            tracker.get_diagram_id(file_path),  # As provided
            tracker.get_diagram_id(file_path.replace("docs/", "")),  # Remove docs/ prefix
            tracker.get_diagram_id(Path(file_path).name),  # Just filename
        ]

        # Also try if it's already an ID without .md
        if not file_path.endswith('.md'):
            possible_ids.append(file_path)

        diagram_id = None
        for possible_id in possible_ids:
            if possible_id in tracker.tracking_data["diagrams"]:
                diagram_id = possible_id
                break

        if diagram_id:
            tracker.tracking_data["diagrams"][diagram_id]["status"] = args.status
            tracker.tracking_data["diagrams"][diagram_id]["last_updated"] = datetime.now().isoformat()
            tracker.save_tracking_data()
            print(f"✅ Updated {diagram_id} status to {args.status}")
        else:
            print(f"❌ Diagram not found: {file_path}")
            print(f"   Tried: {', '.join(possible_ids)}")
            print(f"   Available IDs starting with similar path:")
            for key in tracker.tracking_data["diagrams"].keys():
                if any(pid in key for pid in possible_ids if pid):
                    print(f"     - {key}")
    elif args.export:
        output_file = tracker.export_status_report("json")
        print(f"📁 Status report exported to: {output_file}")
    else:
        # Default: show summary
        print(tracker.generate_unified_dashboard())


if __name__ == "__main__":
    main()