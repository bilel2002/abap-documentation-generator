# tests/extractor_test.py

import sys
from pathlib import Path

# Add parent directory to sys.path to find core module
tests_dir = Path(__file__).parent
project_dir = tests_dir.parent
sys.path.insert(0, str(project_dir))

from core.extractor import extract_text


def main():
    print("ABAP/PDF/TXT Extractor Test")

    file_name = input("Enter file name: ").strip()

    # assume file is in project root OR data/raw
    base_paths = [
        Path.cwd(),
        Path.cwd() / "data" / "raw"
    ]

    file_path = None

    for base in base_paths:
        candidate = base / file_name
        if candidate.exists():
            file_path = candidate
            break

    if not file_path:
        print("File not found. Checked:")
        for base in base_paths:
            print(" -", base)
        return

    text = extract_text(str(file_path))

    print("\n========== EXTRACTED TEXT ==========\n")
    print(text[:3000])
    print("\nCharacters:", len(text))


if __name__ == "__main__":
    main()