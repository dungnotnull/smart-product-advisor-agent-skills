"""
test_validator.py — smart-product-advisor

Validates that the smart-product-advisor skill files are syntactically correct,
internally consistent, and that all 6 quality gates are properly defined across
the harness and sub-skills.

Can run in two modes:
  1. `python tools/test_validator.py check-files` — validate skill file structure
  2. `python tools/test_validator.py check-gates` — verify quality gate consistency
  3. `python tools/test_validator.py all` — run all checks

Exit code: 0 = all pass, 1 = any failure.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SKILLS_DIR = ROOT / "skills"
TOOLS_DIR = ROOT / "tools"
TESTS_DIR = ROOT / "tests"

REQUIRED_SKILL_FILES = [
    "main.md",
    "sub-product-analyzer.md",
    "sub-accessory-researcher.md",
    "sub-compatibility-checker.md",
    "sub-recommendation-ranker.md",
]

REQUIRED_TOPLEVEL_FILES = [
    "CLAUDE.md",
    "PROJECT-detail.md",
    "PROJECT-DEVELOPMENT-PHASE-TRACKING.md",
    "SECOND-KNOWLEDGE-BRAIN.md",
    "tools/knowledge_updater.py",
    "tests/test-scenarios.md",
]

# Required sections in each skill file type
REQUIRED_SECTIONS = {
    "main.md": [
        "## Role & Persona",
        "## Workflow",
        "## Sub-skills Available",
        "## Tools",
        "## Output Format",
        "## Quality Gates",
    ],
    "sub-product-analyzer.md": [
        "## Role & Persona",
        "## Inputs",
        "## Workflow",
        "## Outputs",
        "## Tools",
        "## Quality Gate",
    ],
    "sub-accessory-researcher.md": [
        "## Role & Persona",
        "## Inputs",
        "## Workflow",
        "## Outputs",
        "## Tools",
        "## Quality Gate",
    ],
    "sub-compatibility-checker.md": [
        "## Role & Persona",
        "## Inputs",
        "## Workflow",
        "## Outputs",
        "## Tools",
        "## Quality Gate",
    ],
    "sub-recommendation-ranker.md": [
        "## Role & Persona",
        "## Inputs",
        "## Workflow",
        "## Outputs",
        "## Tools",
        "## Quality Gate",
    ],
}

QUALITY_GATES = {
    "QG-1": "≥ 5 recommendations",
    "QG-2": "All items have compatibility score",
    "QG-3": "All items have source URL",
    "QG-4": "At least one Essential item",
    "QG-5": "All items have price range",
    "QG-6": "Product verified via WebSearch",
}


def check_file_exists(path: Path, name: str) -> bool:
    if not path.exists():
        print(f"  FAIL: Missing file: {name}")
        return False
    print(f"  PASS: {name} exists")
    return True


def check_frontmatter(path: Path) -> bool:
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        print(f"  FAIL: No YAML frontmatter in {path.name}")
        return False
    # Check closing ---
    end = content.find("---", 3)
    if end == -1:
        print(f"  FAIL: Unclosed YAML frontmatter in {path.name}")
        return False
    frontmatter = content[3:end].strip()
    if "name:" not in frontmatter:
        print(f"  FAIL: Missing 'name:' in frontmatter of {path.name}")
        return False
    if "description:" not in frontmatter:
        print(f"  FAIL: Missing 'description:' in frontmatter of {path.name}")
        return False
    print(f"  PASS: Frontmatter valid in {path.name}")
    return True


def check_required_sections(path: Path, required: list[str]) -> bool:
    content = path.read_text(encoding="utf-8")
    all_pass = True
    for section in required:
        if section not in content:
            print(f"  FAIL: Missing section '{section}' in {path.name}")
            all_pass = False
    if all_pass:
        print(f"  PASS: All required sections present in {path.name}")
    return all_pass


def check_sub_skill_references(path: Path) -> bool:
    """Verify main.md references all 4 sub-skills."""
    content = path.read_text(encoding="utf-8")
    all_pass = True
    expected_refs = [
        "sub-product-analyzer",
        "sub-accessory-researcher",
        "sub-compatibility-checker",
        "sub-recommendation-ranker",
    ]
    for ref in expected_refs:
        if ref not in content:
            print(f"  FAIL: Missing reference to '{ref}' in main.md")
            all_pass = False
    if all_pass:
        print(f"  PASS: All 4 sub-skills referenced in main.md")
    return all_pass


def check_quality_gates_defined(path: Path) -> bool:
    """Verify all 6 quality gates are defined in the file."""
    content = path.read_text(encoding="utf-8")
    all_pass = True
    for gate_id, gate_desc in QUALITY_GATES.items():
        if gate_id not in content and gate_desc not in content:
            print(f"  FAIL: '{gate_id}' not found in {path.name}")
            all_pass = False
    if all_pass:
        print(f"  PASS: All 6 quality gates ({', '.join(QUALITY_GATES.keys())}) present in {path.name}")
    return all_pass


def check_output_format_tables(path: Path) -> bool:
    """Verify output format tables are defined."""
    content = path.read_text(encoding="utf-8")
    required_tiers = ["### Essential", "### Nice-to-Have", "### Luxury"]
    all_pass = True
    for tier in required_tiers:
        if tier not in content:
            print(f"  FAIL: Missing output tier '{tier}' in {path.name}")
            all_pass = False
    if all_pass:
        print(f"  PASS: All 3 output tiers (Essential, Nice-to-Have, Luxury) present")
    return all_pass


def check_fallback_logic(path: Path) -> bool:
    """Verify fallback path for WebSearch unavailable is documented."""
    content = path.read_text(encoding="utf-8")
    checks = [
        ("WebSearch unavailable fallback", "WebSearch" in content and "SECOND-KNOWLEDGE-BRAIN" in content),
        ("Fallback notice format", "NOTE" in content or "fallback" in content.lower()),
        ("Clarification prompt", "ambiguous" in content.lower() or "clarify" in content.lower()),
    ]
    all_pass = True
    for label, found in checks:
        if not found:
            print(f"  FAIL: {label} not found in {path.name}")
            all_pass = False
    if all_pass:
        print(f"  PASS: Fallback logic and clarification prompt present")
    return all_pass


def check_knowledge_updater() -> bool:
    path = TOOLS_DIR / "knowledge_updater.py"
    content = path.read_text(encoding="utf-8")
    checks = [
        ("crawl4ai integration", "crawl4ai" in content),
        ("Deduplication", "dedup" in content.lower() or "url_hash" in content),
        ("Scoring logic", "score" in content.lower()),
        ("SECOND-KNOWLEDGE-BRAIN append", "BRAIN_FILE" in content),
        ("CLI args (--category, --dry-run)", "--category" in content and "--dry-run" in content),
        ("Multi-category support", "PRODUCT_CATEGORIES" in content),
    ]
    all_pass = True
    print(f"\n  Checking tools/knowledge_updater.py...")
    for label, found in checks:
        if not found:
            print(f"    FAIL: {label}")
            all_pass = False
    if all_pass:
        print(f"    PASS: All knowledge_updater checks passed")
    return all_pass


def check_test_scenarios() -> bool:
    path = TESTS_DIR / "test-scenarios.md"
    content = path.read_text(encoding="utf-8")

    expected_scenarios = [
        "Scenario 1",
        "Scenario 2",
        "Scenario 3",
        "Scenario 4",
        "Scenario 5",
        "Scenario 6",
        "Scenario 7",
    ]

    all_pass = True
    for scenario in expected_scenarios:
        if scenario not in content:
            print(f"  FAIL: Missing '{scenario}' in test-scenarios.md")
            all_pass = False

    # Check budget test variants
    if "$80" not in content and "$150" not in content:
        print(f"  FAIL: No budget-based test scenarios found")
        all_pass = False

    if "Fallback" not in content and "WebSearch" not in content:
        print(f"  FAIL: No fallback path test scenario found")
        all_pass = False

    if all_pass:
        print(f"  PASS: All {len(expected_scenarios)} test scenarios present with budget + fallback coverage")
    return all_pass


def check_cross_skill_api(path: Path) -> bool:
    """Verify PROJECT-detail.md has cross-skill API contract."""
    content = path.read_text(encoding="utf-8")
    checks = [
        ("Input/Output format", "input" in content.lower() and "output" in content.lower()),
        ("Harness architecture", "Harness Architecture" in content),
        ("Sub-skill catalog", "Sub-Skill Catalog" in content),
        ("Error handling", "Error handling" in content or "Error" in content),
        ("Quality gates defined", "Quality Gate" in content),
    ]
    all_pass = True
    for label, found in checks:
        if not found:
            print(f"  FAIL: {label} not found in PROJECT-detail.md")
            all_pass = False
    if all_pass:
        print(f"  PASS: PROJECT-detail.md has complete API documentation")
    return all_pass


def cmd_check_files() -> int:
    print("=== File Structure Check ===\n")
    failures = 0

    # Check required top-level files
    for fname in REQUIRED_TOPLEVEL_FILES:
        if not check_file_exists(ROOT / fname, fname):
            failures += 1

    # Check required skill files
    print()
    for fname in REQUIRED_SKILL_FILES:
        path = SKILLS_DIR / fname
        if not check_file_exists(path, f"skills/{fname}"):
            failures += 1

    # Check frontmatter on all skill files
    print("\n=== Frontmatter Check ===\n")
    for fname in REQUIRED_SKILL_FILES:
        path = SKILLS_DIR / fname
        if path.exists() and not check_frontmatter(path):
            failures += 1

    # Check required sections on all skill files
    print("\n=== Required Sections Check ===\n")
    for fname, sections in REQUIRED_SECTIONS.items():
        path = SKILLS_DIR / fname
        if path.exists() and not check_required_sections(path, sections):
            failures += 1

    # Check sub-skill references in main.md
    print("\n=== Sub-Skill References Check ===\n")
    main_path = SKILLS_DIR / "main.md"
    if not check_sub_skill_references(main_path):
        failures += 1

    # Check output format tables in main.md
    print("\n=== Output Format Check ===\n")
    if not check_output_format_tables(main_path):
        failures += 1

    # Check fallback logic in main.md
    print("\n=== Fallback Logic Check ===\n")
    if not check_fallback_logic(main_path):
        failures += 1

    # Check knowledge_updater.py
    print("\n=== Knowledge Updater Check ===")
    if not check_knowledge_updater():
        failures += 1

    # Check test scenarios
    print("\n=== Test Scenarios Check ===")
    if not check_test_scenarios():
        failures += 1

    # Check PROJECT-detail.md
    print("\n=== PROJECT-detail.md Check ===")
    if not check_cross_skill_api(ROOT / "PROJECT-detail.md"):
        failures += 1

    return failures


def cmd_check_gates() -> int:
    print("=== Quality Gate Consistency Check ===\n")
    failures = 0

    # Check that all 6 quality gates are in main.md
    main_path = SKILLS_DIR / "main.md"
    if not check_quality_gates_defined(main_path):
        failures += 1

    # Check that each sub-skill has its quality gate
    sub_skill_gates = {
        "sub-product-analyzer.md": ["category", "primary_use_cases", "source_url"],
        "sub-accessory-researcher.md": ["10 candidates", "source_url"],
        "sub-compatibility-checker.md": ["compatibility_confidence", "compatibility_notes"],
        "sub-recommendation-ranker.md": ["Essential", "est_price_range", "final_score"],
    }

    print("\n=== Sub-Skill Quality Gate Consistency ===\n")
    for fname, required_terms in sub_skill_gates.items():
        path = SKILLS_DIR / fname
        content = path.read_text(encoding="utf-8")
        missing = [t for t in required_terms if t not in content]
        if missing:
            print(f"  FAIL: {fname} missing quality gate terms: {missing}")
            failures += 1
        else:
            print(f"  PASS: {fname} quality gates consistent")

    # Check that quality gates appear in test scenarios
    print("\n=== Quality Gate Coverage in Tests ===\n")
    test_path = TESTS_DIR / "test-scenarios.md"
    test_content = test_path.read_text(encoding="utf-8")
    for gate_id, gate_desc in QUALITY_GATES.items():
        if gate_id not in test_content:
            print(f"  WARN: {gate_id} not explicitly tested in test-scenarios.md")
    print(f"  PASS: Gate references scanned")

    return failures


def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/test_validator.py [check-files|check-gates|all]")
        sys.exit(1)

    cmd = sys.argv[1]
    failures = 0

    if cmd in ("check-files", "all"):
        failures += cmd_check_files()

    if cmd in ("check-gates", "all"):
        failures += cmd_check_gates()

    print(f"\n{'='*50}")
    if failures == 0:
        print("ALL CHECKS PASSED")
        sys.exit(0)
    else:
        print(f"{failures} CHECK(S) FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
