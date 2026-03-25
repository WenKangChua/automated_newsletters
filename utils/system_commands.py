import subprocess
import sys

def open_file(filepath) -> None:
    """
    Open the file in the OS default text editor.\n
    MacOS - TextEdit\n
    Windows - Notepad\n
    Linux - xdg
    """
    if sys.platform == "darwin":       # macOS
        subprocess.Popen(["open", "-a", "TextEdit", filepath])
    elif sys.platform == "win32":      # Windows
        subprocess.Popen(["notepad.exe", filepath])
    elif sys.platform.startswith("linux"):  # Linux
        subprocess.Popen(["xdg-open", filepath])