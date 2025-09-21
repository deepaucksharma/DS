#!/usr/bin/env python3
"""
Progress Tracking System for Atlas Project
Reads from CENTRAL_METRICS.json - the single source of truth
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

class ProgressTracker:
    """Track and report progress from central metrics"""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.data_path = self.base_path / "data"
        self.central_metrics_file = self.data_path / "CENTRAL_METRICS.json"

    def load_metrics(self):
        """Load metrics from central file"""
        if not self.central_metrics_file.exists():
            raise FileNotFoundError(
                f"Central metrics file not found at {self.central_metrics_file}\n"
                "Run: python scripts/unified_status_tracker.py --update-central"
            )

        with open(self.central_metrics_file, 'r') as f:
            return json.load(f)

    def generate_report(self) -> str:
        """Generate comprehensive progress report from central metrics"""
        metrics = self.load_metrics()

        # Extract key values
        current = metrics['current_status']['diagrams_created']
        target = metrics['targets']['total_diagrams']
        progress_pct = metrics['progress_percentages']['overall']

        # Status determination
        if current >= target:
            status = "✅ TARGET ACHIEVED"
        elif progress_pct >= 75:
            status = "🎯 ON TRACK"
        elif progress_pct >= 50:
            status = "⚡ ACCELERATING"
        else:
            status = "🚀 RAMPING UP"

        # Category breakdown
        categories = metrics['category_breakdown']

        # Timeline info
        timeline = metrics['timeline']

        # Compliance info
        compliance = metrics['current_status']['compliance']

        # Status distribution
        status_dist = metrics['status_distribution']

        report = f"""# Atlas Progress Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Source: /site/data/CENTRAL_METRICS.json

## 📊 Overall Progress

### Current Status: {status}

| Metric | Value | Target | Progress |
|--------|-------|--------|----------|
| **Total Diagrams** | {current} | {target} | {progress_pct:.1f}% |
| **Files Created** | {metrics['current_status']['files_created']} | As needed | Active |
| **Compliance Score** | {compliance['average_score']:.1f}% | 100% | In Progress |

## 📈 Progress Visualization

```
Target: {target} diagrams
Current: {'█' * int(progress_pct/5)}{'░' * (20-int(progress_pct/5))} {current}
```

## 🎯 Category Breakdown

| Category | Diagrams | Status |
|----------|----------|--------|
| **Systems** | {categories.get('systems', 0)} | {self._status_indicator(categories.get('systems', 0), 240)} |
| **Patterns** | {categories.get('patterns', 0)} | {self._status_indicator(categories.get('patterns', 0), 80)} |
| **Incidents** | {categories.get('incidents', 0)} | {self._status_indicator(categories.get('incidents', 0), 100)} |
| **Debugging** | {categories.get('debugging', 0)} | {self._status_indicator(categories.get('debugging', 0), 100)} |
| **Performance** | {categories.get('performance', 0)} | {self._status_indicator(categories.get('performance', 0), 80)} |
| **Migrations** | {categories.get('migrations', 0)} | {self._status_indicator(categories.get('migrations', 0), 60)} |
| **Capacity** | {categories.get('capacity', 0)} | {self._status_indicator(categories.get('capacity', 0), 60)} |
| **Comparisons** | {categories.get('comparisons', 0)} | {self._status_indicator(categories.get('comparisons', 0), 40)} |
| **Production** | {categories.get('production', 0)} | {self._status_indicator(categories.get('production', 0), 20)} |

## 📊 Status Distribution

| Status | Count | Percentage |
|--------|-------|------------|
| ✅ **Up to Date** | {status_dist['up_to_date']} | {status_dist['up_to_date']/9:.1f}% |
| 🔄 **In Review** | {status_dist['in_review']} | {status_dist['in_review']/9:.1f}% |
| ⚠️ **Needs Update** | {status_dist['needs_update']} | {status_dist['needs_update']/9:.1f}% |
| ⬜ **Not Created** | {status_dist['not_created']} | {status_dist['not_created']/9:.1f}% |

## ⚡ Timeline Metrics

| Metric | Value |
|--------|-------|
| **Project Start** | {timeline['project_start']} |
| **Current Week** | {timeline['current_week']} of {timeline['weeks_remaining'] + timeline['current_week']} |
| **Velocity Required** | {timeline['required_velocity']:.1f} diagrams/week |
| **Current Velocity** | {timeline['current_velocity']} diagrams/week |
| **Estimated Completion** | {timeline['estimated_completion']} |

## 🏢 Systems Documentation

| Status | Count |
|--------|-------|
| **Complete** | {metrics['current_status']['systems_documented']['complete']} / {metrics['targets']['total_systems']} |
| **Partial** | {metrics['current_status']['systems_documented']['partial']} |
| **Not Started** | {metrics['current_status']['systems_documented']['not_started']} |

## 📋 Quality Metrics

| Metric | Count | Target |
|--------|-------|--------|
| **With SLO Labels** | {metrics['quality_metrics']['with_slo_labels']} | All |
| **With Cost Data** | {metrics['quality_metrics']['with_cost_data']} | All |
| **With Failure Scenarios** | {metrics['quality_metrics']['with_failure_scenarios']} | All |
| **Following 4-Plane** | {metrics['quality_metrics']['following_4_plane']} | All |
| **Production Ready** | {metrics['quality_metrics']['production_ready']} | All |
| **Emergency Ready** | {metrics['quality_metrics']['emergency_ready']} | All |

## 💡 Recommendations

{self._generate_recommendations(metrics)}

---
*Report generated from CENTRAL_METRICS.json*
*Last metrics update: {metrics['metadata']['last_updated']}*
*Target: {target} production-quality diagrams*
*Philosophy: Every diagram must help debug production issues at 3 AM*
"""
        return report

    def _status_indicator(self, current: int, target: int) -> str:
        """Generate status indicator for category"""
        if target == 0:
            return "N/A"
        pct = (current / target) * 100
        if pct >= 100:
            return "✅ Complete"
        elif pct >= 75:
            return "🔵 Good"
        elif pct >= 50:
            return "🟡 Progress"
        elif pct >= 25:
            return "🟠 Started"
        else:
            return "⚪ Planning"

    def _generate_recommendations(self, metrics) -> str:
        """Generate actionable recommendations"""
        recommendations = []

        # Velocity check
        current_velocity = metrics['timeline']['current_velocity']
        required_velocity = metrics['timeline']['required_velocity']

        if current_velocity < required_velocity:
            recommendations.append(
                f"⚡ **Increase velocity**: Need {required_velocity:.1f} diagrams/week, "
                f"currently at {current_velocity}"
            )

        # Compliance check
        compliance = metrics['current_status']['compliance']['average_score']
        if compliance < 90:
            recommendations.append(
                f"📊 **Improve compliance**: Average score {compliance:.1f}% should be >90%"
            )

        # Status distribution check
        not_created = metrics['status_distribution']['not_created']
        needs_update = metrics['status_distribution']['needs_update']

        if not_created > 400:
            recommendations.append(
                f"🚀 **Focus on creation**: {not_created} diagrams not yet created"
            )

        if needs_update > 100:
            recommendations.append(
                f"🔧 **Update existing**: {needs_update} diagrams need updates"
            )

        # Systems check
        systems_not_started = metrics['current_status']['systems_documented']['not_started']
        if systems_not_started > 10:
            recommendations.append(
                f"🏢 **Document systems**: {systems_not_started} systems not started"
            )

        if not recommendations:
            recommendations.append("✅ **On Track**: All metrics looking good!")

        return "\n".join(recommendations)

    def generate_dashboard(self) -> str:
        """Generate simple text dashboard for command line"""
        try:
            metrics = self.load_metrics()
        except FileNotFoundError as e:
            return str(e)

        current = metrics['current_status']['diagrams_created']
        target = metrics['targets']['total_diagrams']
        progress = metrics['progress_percentages']['overall']

        dashboard = f"""
╔══════════════════════════════════════════════════════════╗
║               ATLAS PROJECT DASHBOARD                     ║
╠══════════════════════════════════════════════════════════╣
║  Progress: [{('█' * int(progress/5)).ljust(20)}] {progress:.1f}%
║  Diagrams: {str(current).rjust(4)} / {target}
║  Files:    {str(metrics['current_status']['files_created']).rjust(4)} created
╠══════════════════════════════════════════════════════════╣
║  Systems:       {str(metrics['category_breakdown'].get('systems', 0)).rjust(3)} diagrams
║  Patterns:      {str(metrics['category_breakdown'].get('patterns', 0)).rjust(3)} diagrams
║  Incidents:     {str(metrics['category_breakdown'].get('incidents', 0)).rjust(3)} diagrams
║  Debugging:     {str(metrics['category_breakdown'].get('debugging', 0)).rjust(3)} diagrams
║  Production:    {str(metrics['category_breakdown'].get('production', 0)).rjust(3)} diagrams
╠══════════════════════════════════════════════════════════╣
║  Compliance:    {metrics['current_status']['compliance']['average_score']:.1f}%
║  Velocity:      {metrics['timeline']['current_velocity']} diagrams/week
║  Required:      {metrics['timeline']['required_velocity']:.1f} diagrams/week
╚══════════════════════════════════════════════════════════╝

Source: /site/data/CENTRAL_METRICS.json
Last Updated: {metrics['metadata']['last_updated']}
"""
        return dashboard

def main():
    """Run progress tracking"""
    tracker = ProgressTracker()

    try:
        # Generate and save report
        report = tracker.generate_report()
        with open("progress-report.md", "w") as f:
            f.write(report)
        print("✓ Generated progress-report.md from CENTRAL_METRICS.json")

        # Show dashboard
        dashboard = tracker.generate_dashboard()
        print(dashboard)

        # Show quick stats
        metrics = tracker.load_metrics()
        print(f"\nTotal Diagrams: {metrics['current_status']['diagrams_created']}")
        print(f"Target: {metrics['targets']['total_diagrams']}")
        print(f"Progress: {metrics['progress_percentages']['overall']:.1f}%")
        print(f"\n📊 All metrics from: /site/data/CENTRAL_METRICS.json")

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())