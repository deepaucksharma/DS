#!/usr/bin/env python3
"""
Batch Diagram Reviewer
Analyzes multiple diagrams for compliance with Atlas specifications.
This functionality has been integrated into unified_status_tracker.py
but this wrapper is maintained for backward compatibility.
"""

import argparse
import subprocess
import sys
import json
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Batch review diagrams for compliance')
    parser.add_argument('--category', type=str, help='Category to review (systems, incidents, etc.)')
    parser.add_argument('--report', action='store_true', help='Generate compliance report')
    parser.add_argument('--fix-suggestions', action='store_true', help='Generate fix suggestions')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    # Redirect to unified_status_tracker.py with appropriate flags
    cmd = ['python3', str(Path(__file__).parent / 'unified_status_tracker.py')]

    if args.report:
        # Show dashboard with focus on compliance
        cmd.extend(['--dashboard'])
        print(f"Generating compliance report{' for ' + args.category if args.category else ''}...")
    elif args.fix_suggestions:
        # Show dashboard and extract suggestions
        cmd.extend(['--dashboard'])
        print("Analyzing diagrams for improvement suggestions...")
    else:
        # Default to showing dashboard
        cmd.extend(['--dashboard'])

    if args.verbose:
        cmd.append('--verbose')

    # Execute the unified tracker
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        print(f"Error running unified_status_tracker: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: unified_status_tracker.py not found", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()