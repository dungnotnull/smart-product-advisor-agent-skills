"""
run_tests.py -- smart-product-advisor

Test runner that walks through each scenario in tests/test-scenarios.md and
guides the user through manual validation. Designed to be run by an AI agent
or a human tester.

Usage:
  python tools/run_tests.py                     # Run all scenarios
  python tools/run_tests.py --scenario 2         # Run specific scenario
  python tools/run_tests.py --list               # List all scenarios
  python tools/run_tests.py --report             # Generate validation report
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent
TESTS_DIR = ROOT / "tests"
REPORT_FILE = ROOT / "tests" / ".test-run-report.json"

SCENARIOS = {
    1: {
        "name": "Flagship Smartphone (No Budget)",
        "input": "Product: iPhone 16 Pro Max\nBrand: Apple\nBudget: none",
        "expected_count": ">= 5 recommended items",
        "essential_items": ["case", "screen protector", "MagSafe charger or case"],
        "gates": ["QG-1", "QG-2", "QG-3", "QG-4", "QG-5", "QG-6"],
        "validation_checks": {
            "QG-1": "Count final recommendations. Must be >= 5.",
            "QG-2": "Every item must have compatibility_confidence (High/Medium/Low).",
            "QG-3": "Every item must have at least one source URL.",
            "QG-4": "At least one item must be in the Essential tier.",
            "QG-5": "Every item must have est_price_range (e.g., '$15-$35').",
            "QG-6": "Product profile must cite a WebSearch source.",
            "essential_case": "Case must appear in Essential tier.",
            "essential_screen_protector": "Screen protector must appear in Essential tier.",
            "no_android_accessories": "No Android-only accessories in final list.",
        },
    },
    2: {
        "name": "Mid-Range Android with Budget ($80)",
        "input": "Product: Samsung Galaxy A55\nBrand: Samsung\nBudget: $80",
        "expected_count": ">= 5 recommended items, with budget filtering",
        "gates": ["QG-1", "QG-2", "QG-3", "QG-4", "QG-5", "QG-6"],
        "validation_checks": {
            "budget_items_visible": "Items > $80 must be labeled over_budget=true but still visible.",
            "no_silent_drop": "No item silently dropped due to budget.",
            "essential_in_budget": "At least 2 Essential items must be within $80 budget.",
            "price_labels": "All items must show est_price_range with USD values.",
        },
    },
    3: {
        "name": "Mirrorless Camera (Photography)",
        "input": "Product: Sony Alpha A7 IV\nBrand: Sony\nBudget: none",
        "expected_count": ">= 5 items with photo-specific accessories",
        "gates": ["QG-1", "QG-2", "QG-3", "QG-4", "QG-5", "QG-6"],
        "validation_checks": {
            "memory_card_speed": "Memory cards must mention V60+ or U3 speed class in compatibility_notes.",
            "extra_batteries_essential": "Extra batteries must be in Essential tier (camera includes only 1).",
            "camera_bag": "Camera bag must appear in Essential or Nice-to-Have.",
            "lens_accessory": "At least one lens accessory in Nice-to-Have or Luxury.",
        },
    },
    4: {
        "name": "Gaming Console with Budget ($150)",
        "input": "Product: PlayStation 5\nBrand: Sony\nBudget: $150",
        "expected_count": ">= 5 items, PS5-specific",
        "gates": ["QG-1", "QG-2", "QG-3", "QG-4", "QG-5", "QG-6"],
        "validation_checks": {
            "dualSense_controller": "Extra DualSense controller must appear (first-party or verified third-party).",
            "nvme_spec": "SSD storage must include PCIe 4.0 M.2 requirement in compatibility_notes.",
            "hdmi_bandwidth": "HDMI cable must note 'HDMI 2.1 required for 4K 120fps' if included.",
            "over_budget_labeled": "Items over $150 labeled over_budget=true but still visible.",
        },
    },
    5: {
        "name": "Laptop with Professional Work Budget ($200)",
        "input": "Product: Apple MacBook Pro 14-inch M4 Pro\nBrand: Apple\nBudget: $200",
        "expected_count": ">= 5 items, work-focused",
        "gates": ["QG-1", "QG-2", "QG-3", "QG-4", "QG-5", "QG-6"],
        "validation_checks": {
            "thunderbolt_dock_essential": "USB-C/Thunderbolt hub/dock in Essential tier (limited ports).",
            "dock_compatibility_notes": "Dock compatibility notes must mention Thunderbolt 4.",
            "sleeve_or_bag": "Laptop sleeve/bag in Essential or Nice-to-Have.",
            "external_ssd_nice": "External SSD in Nice-to-Have tier.",
            "budget_filter": "Items > $200 labeled over_budget=true.",
        },
    },
    6: {
        "name": "Ambiguous Input Error Path",
        "input": "Product: the new phone\nBrand: not provided",
        "expected_count": "0 -- harness should NOT generate recommendations",
        "gates": [],
        "validation_checks": {
            "no_recommendations": "Harness must NOT generate a recommendation list for ambiguous input.",
            "clarification_asked": "Single clarifying question asked: 'Which brand and model is your phone?'",
            "single_question": "Only ONE clarifying question, not multiple.",
            "proceeds_after_clarification": "After clarification, all quality gates pass normally.",
        },
    },
    7: {
        "name": "Fallback Path (WebSearch Unavailable)",
        "input": "Product: Samsung Galaxy S25 Ultra\nBrand: Samsung\nBudget: none\n[Simulate: WebSearch unavailable]",
        "expected_count": ">= 5 recommendations from SECOND-KNOWLEDGE-BRAIN",
        "gates": ["QG-1", "QG-2", "QG-4", "QG-5"],
        "validation_checks": {
            "fallback_notice": "Fallback notice prepended: 'NOTE: WebSearch was unavailable...'",
            "min_5_recommendations": ">= 5 recommendations produced from internal knowledge.",
            "compatibility_labeled_defaults": "Compatibility scores labeled 'based on category defaults'.",
            "no_hallucinated_sources": "No hallucinated source URLs. Source = 'SECOND-KNOWLEDGE-BRAIN.md, v1'.",
        },
    },
}


def list_scenarios():
    print("=== Available Test Scenarios ===\n")
    for num, info in SCENARIOS.items():
        gates = ", ".join(info["gates"]) if info["gates"] else "N/A (error path test)"
        print(f"  Scenario {num}: {info['name']}")
        print(f"    Quality Gates: {gates}")
        print(f"    Expected Items: {info['expected_count']}")
        print()


def run_scenario(num: int) -> dict:
    if num not in SCENARIOS:
        print(f"ERROR: Scenario {num} not found. Use --list to see available scenarios.")
        return {"scenario": num, "status": "error", "message": "Not found"}

    info = SCENARIOS[num]
    print(f"\n{'='*70}")
    print(f"Scenario {num}: {info['name']}")
    print(f"{'='*70}")
    print(f"\nInput to provide:")
    print(f"  {info['input'].replace(chr(10), chr(10)+'  ')}")
    print(f"\nExpected: {info['expected_count']}")

    if info["gates"]:
        print(f"Required Quality Gates: {', '.join(info['gates'])}")
    else:
        print(f"Quality Gates: N/A (error/fallback path)")

    print(f"\nValidation Checklist:")
    results = {}
    for check_id, description in info["validation_checks"].items():
        print(f"  [ ] {description} (check_id: {check_id})")
        results[check_id] = False

    print(f"\nTo validate: invoke `/smart-product-advisor` with the input above.")
    print(f"Mark each check manually or run with --report to generate a tracking file.")

    return {"scenario": num, "status": "listed", "checks": list(info["validation_checks"].keys())}


def generate_report():
    """Generate/update a JSON test progress report."""
    report = {
        "last_updated": date.today().isoformat(),
        "scenarios": {},
    }
    for num, info in SCENARIOS.items():
        report["scenarios"][str(num)] = {
            "name": info["name"],
            "status": "not_run",
            "passed_checks": [],
            "failed_checks": [],
        }
    with open(REPORT_FILE, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Report initialized at {REPORT_FILE}")
    return report


def main():
    if len(sys.argv) < 2:
        # Default: run all scenarios
        print("Running all scenarios in sequence...\n")
        for num in sorted(SCENARIOS.keys()):
            run_scenario(num)
        print(f"\n{'='*70}")
        print(f"All {len(SCENARIOS)} scenarios listed. Run with --report to initialize tracking.")
        return

    if "--list" in sys.argv:
        list_scenarios()
        return

    if "--report" in sys.argv:
        generate_report()
        return

    if "--scenario" in sys.argv:
        idx = sys.argv.index("--scenario")
        if idx + 1 < len(sys.argv):
            try:
                num = int(sys.argv[idx + 1])
                run_scenario(num)
            except ValueError:
                print(f"ERROR: Invalid scenario number: {sys.argv[idx + 1]}")
                sys.exit(1)
        else:
            print("ERROR: --scenario requires a number argument")
            sys.exit(1)
        return

    print("Usage:")
    print("  python tools/run_tests.py                    # List all scenarios with validation steps")
    print("  python tools/run_tests.py --scenario 2       # Show specific scenario")
    print("  python tools/run_tests.py --list             # List all scenario names")
    print("  python tools/run_tests.py --report           # Initialize JSON test report")


if __name__ == "__main__":
    main()
