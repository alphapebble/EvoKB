#!/usr/bin/env python3
"""Onboarding wizard for EvoKB."""

import os
import sys
from pathlib import Path


def check_python():
    print("[PYTHON] Checking Python version...")
    v = sys.version_info
    if v.major >= 3 and v.minor >= 9:
        print(f"   ✅ Python {v.major}.{v.minor}.{v.micro}")
        return True
    print(f"   ❌ Python 3.9+ required, got {v.major}.{v.minor}")
    return False


def check_dependencies():
    print("\n[DEPS] Checking dependencies...")
    try:
        import litellm

        print("   ✅ litellm")
    except ImportError:
        print("   ❌ litellm missing - run: pip install litellm")
        return False

    try:
        import fastapi

        print("   ✅ fastapi")
    except ImportError:
        print("   ❌ fastapi missing - run: pip install fastapi")
        return False

    return True


def setup_directories():
    print("\n[DIR] Setting up directories...")
    dirs = ["raw", "wiki", "clusters"]
    for d in dirs:
        Path(d).mkdir(exist_ok=True)
        print(f"   ✅ {d}/")
    return True


def check_config():
    print("\n⚙️  Checking config...")
    if Path("config.yaml").exists():
        print("   ✅ config.yaml exists")
    else:
        print("   ⚠️  config.yaml not found (will use defaults)")
    return True


def check_schema():
    print("\n[CFG] Checking schema...")
    if Path("EVOKB_SCHEMA.md").exists():
        print("   ✅ EVOKB_SCHEMA.md exists")
    else:
        print("   ❌ EVOKB_SCHEMA.md missing!")
        return False
    return True


def create_sample():
    print("\n[FILE] Creating sample source...")
    sample = Path("raw/sample.md")
    if sample.exists():
        print("   ✅ sample.md already exists")
    else:
        sample.write_text("""# Sample Note

This is a sample note to test EvoKB.

## Key Points
- Knowledge graphs represent information as interconnected entities
- They enable semantic search and reasoning
- EvoKB compiles raw notes into structured wiki pages

Sources: https://en.wikipedia.org/wiki/Knowledge_graph
""")
        print("   ✅ Created raw/sample.md")
    return True


def check_ollama():
    print("\n[OLLAMA] Checking Ollama...")
    try:
        import requests

        r = requests.get("http://localhost:11434/api/tags", timeout=2)
        if r.ok:
            models = r.json().get("models", [])
            print(f"   ✅ Ollama running with {len(models)} models")
            if models:
                print(f"      Available: {', '.join([m['name'] for m in models[:3]])}")
            return True
    except Exception:
        pass

    print("   ⚠️  Ollama not running")
    print("      Install: curl -fsSL https://ollama.com/install.sh | bash")
    print("      Start:   ollama serve")
    return True


def main():
    print("=" * 50)
    print("[INFO] EvoKB Onboarding Wizard")
    print("=" * 50)

    checks = [
        check_python,
        check_dependencies,
        setup_directories,
        check_config,
        check_schema,
        create_sample,
        check_ollama,
    ]

    results = []
    for check in checks:
        results.append(check())

    print("\n" + "=" * 50)
    print("[STATS] Setup Status")
    print("=" * 50)

    if all(results):
        print("✅ All checks passed! You're ready to go.")
        print("\nNext steps:")
        print("  1. Start Ollama: ollama serve")
        print("  2. Run librarian: python -m evokb.agents.librarian")
        print(
            "  3. Query: python -c \"from evokb.core.retriever import query_evo_kb; print(query_evo_kb('What is EvoKB?'))\""
        )
    else:
        print("⚠️  Some checks failed. Fix the issues above.")

    print()


if __name__ == "__main__":
    main()
