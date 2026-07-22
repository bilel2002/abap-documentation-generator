"""
run_pyinstaller.py
==================
Wrapper that runs PyInstaller inside a thread with a 64 MB stack.

WHY THIS IS NEEDED:
  PyInstaller's analysis phase recursively processes hundreds of module hooks
  for heavy ML packages (torch, scipy, pandas, matplotlib). On Windows, the
  default thread stack size is only 1 MB, which causes a native stack overflow
  (exit code 0xC00000FD = -1073741571) long before analysis completes.

  sys.setrecursionlimit only controls Python's own guard — it cannot increase
  the underlying Windows thread stack. threading.stack_size() does.

USAGE:
  python run_pyinstaller.py
"""

import threading
import sys
import os

STACK_SIZE_MB = 64
SPEC_FILE = "abap_doc_generator.spec"

# Shared result — thread writes exit code here so main thread can read it
_exit_code = 0

def run_pyinstaller():
    global _exit_code
    try:
        import PyInstaller.__main__
        PyInstaller.__main__.run([
            SPEC_FILE,
            "--clean",
            "--noconfirm",
        ])
        _exit_code = 0
    except SystemExit as e:
        _exit_code = e.code if isinstance(e.code, int) else 1
    except Exception as e:
        print(f"[ERROR] PyInstaller raised an exception: {e}", file=sys.stderr)
        _exit_code = 1


if __name__ == "__main__":
    # Must be called BEFORE the thread is created
    threading.stack_size(STACK_SIZE_MB * 1024 * 1024)

    t = threading.Thread(target=run_pyinstaller)
    t.start()
    t.join()

    # Exit with PyInstaller's actual exit code — build.bat checks %ERRORLEVEL%
    sys.exit(_exit_code)
