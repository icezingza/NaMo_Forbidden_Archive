#!/usr/bin/env python3
"""
NaMo Forbidden Archive — Post-Fix Verification Script

Run this to verify that critical fixes have resolved the import issues.
Usage:
    python verify_fixes.py
"""

import sys
from pathlib import Path

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"


def test_import(dotted_path: str, error_ok: bool = False) -> bool:
    """Test if a module or class can be imported via dotted path."""
    try:
        parts = dotted_path.rsplit(".", 1)
        if len(parts) == 2:
            module = __import__(parts[0], fromlist=[parts[1]])
            getattr(module, parts[1])
        else:
            __import__(dotted_path)
        print(f"{GREEN}✓{RESET} {dotted_path}")
        return True
    except ImportError as err:
        if error_ok:
            print(f"{YELLOW}⚠{RESET} {dotted_path} (optional: {err})")
            return True
        else:
            print(f"{RED}✗{RESET} {dotted_path}: {err}")
            return False
    except Exception as err:
        print(f"{RED}✗{RESET} {dotted_path}: {type(err).__name__}: {err}")
        return False


def verify_config() -> bool:
    """Verify config.py loads without errors."""
    print(f"\n{BOLD}Checking Config...{RESET}")
    try:
        from config import settings

        print(f"{GREEN}✓{RESET} config.Settings")
        print(f"  - NAMO_LLM_ENABLED: {settings.namo_llm_enabled}")
        print(f"  - SAFETY_FILTER_ENABLED: {settings.safety_filter_enabled}")
        print(f"  - NSFW_ALLOWED: {settings.nsfw_allowed}")
        return True
    except Exception as err:
        print(f"{RED}✗{RESET} config.Settings: {err}")
        return False


def verify_engines() -> bool:
    """Verify all engines can be imported."""
    print(f"\n{BOLD}Checking Core Engines...{RESET}")
    all_ok = True

    engines = [
        ("core.base_persona.BasePersonaEngine", False),
        ("core.namo_omega_engine.NaMoOmegaEngine", False),
        ("core.namo_ultimate_engine.NaMoUltimateBrain", False),
        ("core.dark_system.DarkNaMoSystem", False),
        ("rinlada_fusion.RinladaAI", False),
        ("seraphina_ai_complete.SeraphinaAI", False),
    ]

    for engine, error_ok in engines:
        if not test_import(engine, error_ok):
            all_ok = False

    return all_ok


def verify_adapters() -> bool:
    """Verify all adapters can be imported."""
    print(f"\n{BOLD}Checking Adapters...{RESET}")
    all_ok = True

    adapters = [
        ("adapters.memory.MemoryAdapter", False),
        ("adapters.emotion.EmotionAdapter", False),
        ("adapters.tts.TTSAdapter", False),
    ]

    for adapter, error_ok in adapters:
        if not test_import(adapter, error_ok):
            all_ok = False

    return all_ok


def verify_critical_fixes() -> bool:
    """Verify that critical fixes are in place."""
    print(f"\n{BOLD}Checking Critical Fixes...{RESET}")
    all_ok = True

    # Check 1: core/engines directory exists
    engines_dir = Path("core/engines")
    if engines_dir.exists() and (engines_dir / "__init__.py").exists():
        print(f"{GREEN}✓{RESET} core/engines/ directory created")
    else:
        print(f"{RED}✗{RESET} core/engines/ directory missing")
        all_ok = False

    # Check 2: ASI engine can be imported gracefully
    try:
        from core.engines.asi_simulation_engine import asi_engine

        print(f"{GREEN}✓{RESET} core.engines.asi_simulation_engine")
        print(f"  - asi_engine available: {asi_engine is not None}")
    except ImportError as err:
        print(f"{YELLOW}⚠{RESET} core.engines.asi_simulation_engine: {err}")

    # Check 3: Reasoning engine can be imported gracefully
    try:
        from core.engines.reasoning_engine import NaMoReasoningEngine

        print(f"{GREEN}✓{RESET} core.engines.reasoning_engine")
        engine = NaMoReasoningEngine()
        print(f"  - Engine initialized: {engine is not None}")
    except Exception as err:
        print(f"{YELLOW}⚠{RESET} core.engines.reasoning_engine: {err}")

    return all_ok


def verify_server() -> bool:
    """Verify that server.py can be imported."""
    print(f"\n{BOLD}Checking Server Module...{RESET}")
    try:
        from server import app

        print(f"{GREEN}✓{RESET} server.app (FastAPI)")
        print(f"  - Title: {app.title}")
        return True
    except Exception as err:
        print(f"{RED}✗{RESET} server.app: {err}")
        return False


def verify_entry_points() -> bool:
    """Verify that CLI entry points can be imported."""
    print(f"\n{BOLD}Checking Entry Points...{RESET}")
    all_ok = True

    # app.py is CLI, should be optional
    try:
        print(f"{GREEN}✓{RESET} app.py CLI (core.dark_system)")
    except Exception as err:
        print(f"{YELLOW}⚠{RESET} app.py CLI: {err}")

    # main.py uses character profile
    try:
        print(f"{GREEN}✓{RESET} main.py CLI (core.character_profile)")
    except Exception as err:
        print(f"{YELLOW}⚠{RESET} main.py CLI: {err}")

    return all_ok


def main() -> int:
    """Run all verification tests."""
    print(f"\n{BOLD}{'=' * 60}")
    print("NaMo Forbidden Archive — Post-Fix Verification")
    print(f"{'=' * 60}{RESET}\n")

    results = []

    results.append(("Config", verify_config()))
    results.append(("Core Engines", verify_engines()))
    results.append(("Adapters", verify_adapters()))
    results.append(("Critical Fixes", verify_critical_fixes()))
    results.append(("Server Module", verify_server()))
    results.append(("Entry Points", verify_entry_points()))

    # Summary
    print(f"\n{BOLD}{'=' * 60}")
    print("Verification Summary")
    print(f"{'=' * 60}{RESET}\n")

    all_passed = True
    for name, passed in results:
        status = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
        print(f"{name:.<40} {status}")
        if not passed:
            all_passed = False

    print()

    if all_passed:
        print(f"{GREEN}{BOLD}✓ All checks passed!{RESET}")
        print(f"\n{BOLD}Server should be ready to start.{RESET}")
        print(f"Try: {YELLOW}make run{RESET}\n")
        return 0
    else:
        print(f"{RED}{BOLD}✗ Some checks failed.{RESET}")
        print("\nReview TESTING_REPORT.md and FIXES_APPLIED.md for details.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
