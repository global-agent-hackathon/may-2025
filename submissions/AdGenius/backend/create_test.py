#!/usr/bin/env python3
"""
Script to create new test files from templates.

Usage:
    python create_test.py --type api --module user_management --class User
    python create_test.py --type unit --module auth --class Authentication
    python create_test.py --type integration --module database --class Repository
"""

import argparse
import re
from pathlib import Path

from utils.test_templates import get_template


def snake_case(s: str) -> str:
    """Convert a string to snake_case"""
    # Replace spaces with underscores
    s = re.sub(r"\s+", "_", s)
    # Insert underscore between camel case
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    # Convert to lowercase
    return s.lower()


def create_test_file():
    """Create a new test file from a template"""
    parser = argparse.ArgumentParser(description="Create a new test file from template")
    parser.add_argument(
        "--type",
        choices=["api", "unit", "integration"],
        required=True,
        help="Type of test to create",
    )
    parser.add_argument(
        "--module", required=True, help="Name of the module being tested"
    )
    parser.add_argument(
        "--class",
        dest="class_name",
        required=True,
        help="Name of the class being tested",
    )
    parser.add_argument(
        "--dir",
        help="Directory to create the test file in (default: determined by test type)",
    )

    args = parser.parse_args()

    # Determine file path
    if args.dir:
        # Use specified directory
        test_dir = Path(args.dir)
    else:
        # Try to find an appropriate test directory
        module_name = snake_case(args.module)
        possible_dirs = [
            Path(f"chat_assistant/{module_name}/tests"),
            Path(f"chat_assistant/tests/{module_name}"),
            Path(f"backend/{module_name}/tests"),
            Path(f"backend/tests/{module_name}"),
            Path(f"{module_name}/tests"),
            Path("tests"),
        ]

        for test_dir in possible_dirs:
            if test_dir.exists() and test_dir.is_dir():
                break
        else:
            # Default to tests/ directory
            test_dir = Path("tests")
            # Create it if it doesn't exist
            if not test_dir.exists():
                test_dir.mkdir(parents=True)

    # Ensure the directory exists
    test_dir.mkdir(parents=True, exist_ok=True)

    # Create the file path
    test_file = test_dir / f"test_{snake_case(args.class_name)}.py"

    # Check if file already exists
    if test_file.exists():
        print(f"Warning: File {test_file} already exists.")
        response = input("Overwrite? (y/n): ").lower()
        if response != "y":
            print("Operation cancelled.")
            return

    # Generate the test file content
    content = get_template(args.type, args.module, args.class_name)

    # Write to file
    with open(test_file, "w") as f:
        f.write(content)

    print(f"Created test file: {test_file}")
    print(f"Type: {args.type}")
    print(f"Module: {args.module}")
    print(f"Class: {args.class_name}")


if __name__ == "__main__":
    create_test_file()
