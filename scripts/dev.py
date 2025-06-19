#!/usr/bin/env python3
"""
Development helper script for PDF to Markdown converter
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and handle errors"""
    if description:
        print(f"🔄 {description}...")

    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(e.stderr)
        return False


def format_code():
    """Format code using black and isort"""
    print("🎨 Formatting code...")
    run_command("black src/ main.py", "Running black")
    run_command("isort src/ main.py", "Running isort")


def lint_code():
    """Lint code using flake8 and mypy"""
    print("🔍 Linting code...")
    run_command("flake8 src/ main.py", "Running flake8")
    run_command("mypy src/ main.py", "Running mypy")


def test_code():
    """Run tests"""
    print("🧪 Running tests...")
    run_command("pytest", "Running pytest")


def install_deps():
    """Install dependencies"""
    print("📦 Installing dependencies...")
    run_command("uv pip install -e .[dev]", "Installing with uv")


def clean_project():
    """Clean build artifacts"""
    print("🧹 Cleaning project...")

    # Remove common build artifacts
    artifacts = [
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".pytest_cache",
        ".coverage",
        "htmlcov",
        "dist",
        "build",
        "*.egg-info",
    ]

    for pattern in artifacts:
        run_command(f"rm -rf {pattern}", f"Removing {pattern}")


def main():
    """Main CLI for development tasks"""
    if len(sys.argv) < 2:
        print("""
🛠️  PDF to Markdown Converter - Development Helper

Usage: python scripts/dev.py <command>

Commands:
  format    - Format code with black and isort
  lint      - Lint code with flake8 and mypy  
  test      - Run tests with pytest
  install   - Install dependencies with uv
  clean     - Clean build artifacts
  all       - Run format, lint, and test
  
Examples:
  python scripts/dev.py format
  python scripts/dev.py lint
  python scripts/dev.py all
        """)
        return

    command = sys.argv[1].lower()

    if command == "format":
        format_code()
    elif command == "lint":
        lint_code()
    elif command == "test":
        test_code()
    elif command == "install":
        install_deps()
    elif command == "clean":
        clean_project()
    elif command == "all":
        format_code()
        lint_code()
        test_code()
    else:
        print(f"❌ Unknown command: {command}")
        print("Run 'python scripts/dev.py' for help")


if __name__ == "__main__":
    main()
