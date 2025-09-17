#!/usr/bin/env python3
"""
Progress Tracking System for Atlas Project
Tracks progress toward 900-1500 diagram goal
Based on readonly-spec requirements
"""

import json
import yaml
import glob
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from pathlib import Path

class ProgressTracker:
    """Track and report progress on diagram generation"""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.docs_path = self.base_path / "docs"
        self.data_path = self.base_path / "data"
        self.data_path.mkdir(exist_ok=True)
        self.progress_file = self.data_path / "progress.json"

    def scan_diagrams(self) -> Dict:
        """Scan all markdown files for Mermaid diagrams"""
        stats = {
            "guarantees": {"files": 0, "diagrams": 0},
            "mechanisms": {"files": 0, "diagrams": 0},
            "patterns": {"files": 0, "diagrams": 0},
            "case_studies": {"files": 0, "diagrams": 0},
            "total": {"files": 0, "diagrams": 0}
        }

        # Scan all markdown files
        for md_file in self.docs_path.rglob("*.md"):
            content = md_file.read_text()
            mermaid_count = content.count("```mermaid")

            if mermaid_count > 0:
                # Categorize by path
                category = self._categorize_file(md_file)
                stats[category]["files"] += 1
                stats[category]["diagrams"] += mermaid_count
                stats["total"]["files"] += 1
                stats["total"]["diagrams"] += mermaid_count

        return stats

    def _categorize_file(self, file_path: Path) -> str:
        """Categorize file based on path"""
        path_str = str(file_path).lower()
        if "guarantee" in path_str:
            return "guarantees"
        elif "mechanism" in path_str:
            return "mechanisms"
        elif "pattern" in path_str:
            return "patterns"
        elif "case" in path_str or "example" in path_str:
            return "case_studies"
        else:
            return "patterns"  # default

    def calculate_velocity(self) -> Dict:
        """Calculate velocity based on historical progress"""
        history = self.load_history()

        if len(history) < 2:
            return {"weekly": 0, "monthly": 0, "projected_completion": "N/A"}

        # Calculate weekly velocity (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_entries = [h for h in history if datetime.fromisoformat(h["date"]) > week_ago]

        if recent_entries:
            start_count = recent_entries[0]["total_diagrams"]
            end_count = recent_entries[-1]["total_diagrams"]
            weekly_velocity = end_count - start_count
        else:
            weekly_velocity = 0

        # Calculate monthly velocity (last 30 days)
        month_ago = datetime.now() - timedelta(days=30)
        monthly_entries = [h for h in history if datetime.fromisoformat(h["date"]) > month_ago]

        if monthly_entries:
            start_count = monthly_entries[0]["total_diagrams"]
            end_count = monthly_entries[-1]["total_diagrams"]
            monthly_velocity = end_count - start_count
        else:
            monthly_velocity = 0

        # Project completion
        current = history[-1]["total_diagrams"] if history else 0
        target = 1200  # mid-range target
        remaining = target - current

        if weekly_velocity > 0:
            weeks_to_complete = remaining / weekly_velocity
            completion_date = datetime.now() + timedelta(weeks=weeks_to_complete)
            projected = completion_date.strftime("%Y-%m-%d")
        else:
            projected = "N/A - No velocity"

        return {
            "weekly": weekly_velocity,
            "monthly": monthly_velocity,
            "projected_completion": projected
        }

    def load_history(self) -> List[Dict]:
        """Load historical progress data"""
        if self.progress_file.exists():
            with open(self.progress_file) as f:
                return json.load(f)
        return []

    def save_snapshot(self, stats: Dict):
        """Save current progress snapshot"""
        history = self.load_history()

        snapshot = {
            "date": datetime.now().isoformat(),
            "total_diagrams": stats["total"]["diagrams"],
            "total_files": stats["total"]["files"],
            "breakdown": {
                "guarantees": stats["guarantees"]["diagrams"],
                "mechanisms": stats["mechanisms"]["diagrams"],
                "patterns": stats["patterns"]["diagrams"],
                "case_studies": stats["case_studies"]["diagrams"]
            }
        }

        history.append(snapshot)

        # Keep only last 90 days of history
        cutoff = datetime.now() - timedelta(days=90)
        history = [h for h in history if datetime.fromisoformat(h["date"]) > cutoff]

        with open(self.progress_file, "w") as f:
            json.dump(history, f, indent=2)

    def generate_report(self) -> str:
        """Generate comprehensive progress report"""
        stats = self.scan_diagrams()
        velocity = self.calculate_velocity()
        self.save_snapshot(stats)

        # Calculate progress percentages
        target_min, target_max, target_mid = 900, 1500, 1200
        current = stats["total"]["diagrams"]
        progress_pct = (current / target_mid) * 100

        # Determine status
        if current >= target_min:
            status = "✅ TARGET ACHIEVED"
            status_color = "green"
        elif progress_pct >= 75:
            status = "🎯 ON TRACK"
            status_color = "blue"
        elif progress_pct >= 50:
            status = "⚡ ACCELERATING"
            status_color = "yellow"
        else:
            status = "🚀 RAMPING UP"
            status_color = "orange"

        report = f"""# Atlas Progress Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Overall Progress

### Current Status: {status}

| Metric | Value | Target | Progress |
|--------|-------|--------|----------|
| **Total Diagrams** | {current} | {target_min}-{target_max} | {progress_pct:.1f}% |
| **Files with Diagrams** | {stats['total']['files']} | 75-125 | {(stats['total']['files']/100)*100:.0f}% |
| **Average per File** | {current/max(stats['total']['files'],1):.1f} | 10-15 | Good |

## 📈 Progress Visualization

```
Target Range: {target_min} ━━━━━━━━━━━━━━━━━━━━ {target_max}
Current:      {'█' * int(progress_pct/5)}{' ' * (20-int(progress_pct/5))} {current}
```

## 🎯 Category Breakdown

| Category | Files | Diagrams | Target | Status |
|----------|-------|----------|--------|--------|
| **Guarantees** | {stats['guarantees']['files']} | {stats['guarantees']['diagrams']} | 180 (18×10) | {self._status_indicator(stats['guarantees']['diagrams'], 180)} |
| **Mechanisms** | {stats['mechanisms']['files']} | {stats['mechanisms']['diagrams']} | 200 (20×10) | {self._status_indicator(stats['mechanisms']['diagrams'], 200)} |
| **Patterns** | {stats['patterns']['files']} | {stats['patterns']['diagrams']} | 210 (21×10) | {self._status_indicator(stats['patterns']['diagrams'], 210)} |
| **Case Studies** | {stats['case_studies']['files']} | {stats['case_studies']['diagrams']} | 600+ | {self._status_indicator(stats['case_studies']['diagrams'], 600)} |

## ⚡ Velocity Metrics

| Period | Diagrams Added | Rate | Projection |
|--------|---------------|------|------------|
| **Last Week** | {velocity['weekly']} | {velocity['weekly']/7:.1f}/day | {velocity['weekly']*4}/month |
| **Last Month** | {velocity['monthly']} | {velocity['monthly']/30:.1f}/day | {velocity['monthly']*12}/year |
| **Completion** | {target_mid - current} remaining | - | {velocity['projected_completion']} |

## 🎯 Milestones

| Milestone | Diagrams | Status | ETA |
|-----------|----------|--------|-----|
| 🏗️ Foundation | 300 | {'✅ Complete' if current >= 300 else f'⏳ {300-current} to go'} | {self._calculate_eta(current, 300, velocity['weekly'])} |
| 🔧 Core Systems | 600 | {'✅ Complete' if current >= 600 else f'⏳ {600-current} to go'} | {self._calculate_eta(current, 600, velocity['weekly'])} |
| 🎯 **Minimum Target** | 900 | {'✅ Complete' if current >= 900 else f'⏳ {900-current} to go'} | {self._calculate_eta(current, 900, velocity['weekly'])} |
| 🚀 Optimal Coverage | 1200 | {'✅ Complete' if current >= 1200 else f'⏳ {1200-current} to go'} | {self._calculate_eta(current, 1200, velocity['weekly'])} |
| 🌟 Stretch Goal | 1500 | {'✅ Complete' if current >= 1500 else f'⏳ {1500-current} to go'} | {self._calculate_eta(current, 1500, velocity['weekly'])} |

## 📋 Next Actions

### Immediate (This Week)
- [ ] Complete {max(0, 30 - velocity['weekly'])} more diagrams to hit 30/week target
- [ ] Review and validate existing diagrams for schema compliance
- [ ] Identify high-priority gaps in coverage

### Short Term (This Month)
- [ ] Add {max(0, 120 - velocity['monthly'])} diagrams to achieve 120/month rate
- [ ] Complete all foundation guarantees and mechanisms
- [ ] Start 2-3 new case studies

### Long Term (This Quarter)
- [ ] Reach {min(target_mid, current + 300)} total diagrams
- [ ] Complete 10+ production case studies
- [ ] Achieve comprehensive pattern coverage

## 💡 Recommendations

{self._generate_recommendations(stats, velocity, current, target_mid)}

## 📊 Quality Metrics

- **Schema Compliance**: All diagrams must validate against spec
- **Size Limit**: All diagrams < 500KB uncompressed
- **Accessibility**: WCAG 2.1 AA compliant
- **Performance**: < 2s render time
- **Coverage**: {(stats['total']['files']/100)*100:.0f}% of planned content areas

---
*Report generated by progress_tracker.py*
*Target: 900-1500 production-quality diagrams*
*Philosophy: Every diagram must help debug production issues at 3 AM*
"""
        return report

    def _status_indicator(self, current: int, target: int) -> str:
        """Generate status indicator for category"""
        pct = (current / target) * 100 if target > 0 else 0
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

    def _calculate_eta(self, current: int, target: int, weekly_velocity: int) -> str:
        """Calculate ETA for milestone"""
        if current >= target:
            return "Completed"
        if weekly_velocity <= 0:
            return "TBD"
        weeks = (target - current) / weekly_velocity
        eta = datetime.now() + timedelta(weeks=weeks)
        return eta.strftime("%Y-%m-%d")

    def _generate_recommendations(self, stats: Dict, velocity: Dict, current: int, target: int) -> str:
        """Generate actionable recommendations"""
        recommendations = []

        # Velocity recommendations
        if velocity['weekly'] < 20:
            recommendations.append("⚡ **Increase velocity**: Current rate below 20 diagrams/week target")
        if velocity['weekly'] > 40:
            recommendations.append("✅ **Excellent velocity**: Maintaining over 40 diagrams/week!")

        # Category balance recommendations
        if stats['guarantees']['diagrams'] < 50:
            recommendations.append("📘 **Focus on Guarantees**: Need more guarantee flow diagrams")
        if stats['mechanisms']['diagrams'] < 50:
            recommendations.append("🔧 **Focus on Mechanisms**: Need more mechanism detail diagrams")
        if stats['case_studies']['diagrams'] < stats['total']['diagrams'] * 0.4:
            recommendations.append("📚 **Add Case Studies**: Case studies should be 40%+ of total")

        # Progress recommendations
        remaining = target - current
        if remaining > 0:
            weeks_needed = remaining / max(velocity['weekly'], 20)
            recommendations.append(f"📅 **Timeline**: Need {weeks_needed:.1f} weeks at current/target velocity")

        if not recommendations:
            recommendations.append("✅ **On Track**: All metrics looking good!")

        return "\n".join(recommendations)

    def generate_dashboard(self) -> str:
        """Generate simple text dashboard for command line"""
        stats = self.scan_diagrams()
        current = stats["total"]["diagrams"]
        target = 1200
        progress = (current / target) * 100

        dashboard = f"""
╔══════════════════════════════════════════════════════════╗
║               ATLAS PROJECT DASHBOARD                     ║
╠══════════════════════════════════════════════════════════╣
║  Progress: [{('█' * int(progress/5)).ljust(20)}] {progress:.1f}%
║  Diagrams: {str(current).rjust(4)} / {target} (Target: 900-1500)
║  Files:    {str(stats['total']['files']).rjust(4)} with diagrams
╠══════════════════════════════════════════════════════════╣
║  Guarantees:    {str(stats['guarantees']['diagrams']).rjust(3)} diagrams
║  Mechanisms:    {str(stats['mechanisms']['diagrams']).rjust(3)} diagrams
║  Patterns:      {str(stats['patterns']['diagrams']).rjust(3)} diagrams
║  Case Studies:  {str(stats['case_studies']['diagrams']).rjust(3)} diagrams
╚══════════════════════════════════════════════════════════╝
"""
        return dashboard

def main():
    """Run progress tracking"""
    tracker = ProgressTracker()

    # Generate and save report
    report = tracker.generate_report()
    with open("progress-report.md", "w") as f:
        f.write(report)
    print("✓ Generated progress-report.md")

    # Show dashboard
    dashboard = tracker.generate_dashboard()
    print(dashboard)

    # Show quick stats
    stats = tracker.scan_diagrams()
    print(f"Total Diagrams: {stats['total']['diagrams']}")
    print(f"Target Range: 900-1500")
    print(f"Progress: {(stats['total']['diagrams']/1200)*100:.1f}%")

if __name__ == "__main__":
    main()