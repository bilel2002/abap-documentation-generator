import sys
from pathlib import Path

print("Python executable:", sys.executable)
print("Python path:", sys.path)

try:
    print("\n--- Testing imports ---")
    import streamlit as st
    print("✓ streamlit imported")
    
    if Path(__file__).parent not in sys.path:
        sys.path.insert(0, str(Path(__file__).parent))
    print("✓ path set")
    
    from core.extractor import extract_text
    print("✓ extract_text imported")
    
    from core.cleaner import clean_text
    print("✓ clean_text imported")
    
    print("\n✅ All imports passed!")
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {e}")
    import traceback
    print("\nStack trace:")
    traceback.print_exc()
