import os
import sys
from PyQt5 import uic

def convert_ui_file(ui_path: str):
    """Compile a single .ui to .py with the -x (executable) flag."""
    py_path = os.path.splitext(ui_path)[0] + ".py"
    print(f"Converting {ui_path!r} → {py_path!r}…")
    with open(ui_path, 'r', encoding='utf-8') as ui_file, \
         open(py_path, 'w', encoding='utf-8') as py_file:
        # execute=True equals the -x flag on the command-line
        uic.compileUi(ui_file, py_file, execute=True)
    print("  done.")

def main():
    # the folder containing this script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # scan for all .ui files
    ui_files = [f for f in os.listdir(base_dir) if f.lower().endswith('.ui')]
    if not ui_files:
        print("No .ui files found in", base_dir)
        sys.exit(1)

    for ui in ui_files:
        convert_ui_file(os.path.join(base_dir, ui))

if __name__ == "__main__":
    main()