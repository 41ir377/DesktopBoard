# storage.py
from pathlib import Path
import json
from appdirs import user_data_dir
from datetime import datetime
import shutil

APP_NAME = "DesktopBoard"
APP_AUTHOR = "41ir377"

DATA_DIR = Path(user_data_dir(APP_NAME, APP_AUTHOR))
DATA_DIR.mkdir(parents=True, exist_ok=True)

STATE_FILE = DATA_DIR / "state.json"
BACKUP_DIR = DATA_DIR / "backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

MAX_BACKUPS = 10

def load_state():
    if not STATE_FILE.exists():
        return {}
    try:
        with STATE_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_state(state: dict, backup: bool = True):
    try:
        # create timestamped backup of existing state
        if backup and STATE_FILE.exists():
            ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
            dst = BACKUP_DIR / f"state-{ts}.json"
            shutil.copy2(STATE_FILE, dst)
            # prune old backups
            backups = sorted(BACKUP_DIR.glob("state-*.json"))
            if len(backups) > MAX_BACKUPS:
                for old in backups[: len(backups) - MAX_BACKUPS]:
                    try:
                        old.unlink()
                    except Exception:
                        pass
        with STATE_FILE.open("w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception:
        # swallow errors for now; could log to a file later
        pass