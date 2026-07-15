# tests/parser_test.py

import sys
from pathlib import Path

# Add parent directory to sys.path to find core module
tests_dir = Path(__file__).parent
project_dir = tests_dir.parent
sys.path.insert(0, str(project_dir))

from core.extractor import extract_text
from core.cleaner import clean_text
from core.parser_refactored import parse_abap


def main():
    print("ABAP Parser Test")

    file_name = input("Enter file name: ").strip()

    # search file
    possible_paths = [
        Path.cwd() / file_name,
        Path.cwd() / "data" / "raw" / file_name
    ]

    file_path = None
    for p in possible_paths:
        if p.exists():
            file_path = p
            break

    if not file_path:
        print("File not found")
        return

    # pipeline
    raw = extract_text(str(file_path))
    cleaned = clean_text(raw)
    parsed = parse_abap(cleaned)

    print("\n========== CLEANED TEXT ==========\n")
    print(cleaned[:2000])

    print("\n========== PARSED RESULT ==========\n")
    print(parsed)


if __name__ == "__main__":
    main()