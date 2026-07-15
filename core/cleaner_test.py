# tests/cleaner_test.py

from pathlib import Path
from core.extractor import extract_text
from core.cleaner import clean_text


def main():
    print("ABAP Cleaner Test")

    file_name = input("Enter file name: ").strip()

    # Search in root and data/raw
    possible_paths = [
        Path.cwd() / file_name,
        Path.cwd() / "data" / "raw" / file_name
    ]

    file_path = None

    for path in possible_paths:
        if path.exists():
            file_path = path
            break

    if not file_path:
        print("File not found.")
        return

    # Step 1: extract
    raw_text = extract_text(str(file_path))

    # Step 2: clean
    cleaned_text = clean_text(raw_text)

    print("\n========== CLEANED OUTPUT ==========\n")
    print(cleaned_text[:5000])

    print("\nCharacters:", len(cleaned_text))


if __name__ == "__main__":
    main()