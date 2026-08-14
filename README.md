# DesktopBoard

Minimal MVP scaffold for DesktopBoard — a Windows-focused desktop sticky-note / productivity widget.

This initial commit contains:

- A minimal PySide6 application (main.py) with a frameless window, rich-text editor, autosave, and system tray icon.
- A simple storage helper using appdirs to persist note content and window geometry.
- requirements.txt listing runtime deps.

Run (create a venv first):

pip install -r requirements.txt
python main.py

Goals for next steps
- Add task/checklist support
- Add multi-board handling
- Add settings dialog and hotkey handling

License: MIT (add license file if desired)
