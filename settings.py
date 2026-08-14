import json
import os

DATA_DIR = "data"
FILE = os.path.join(DATA_DIR, "notes.json")

os.makedirs(DATA_DIR, exist_ok=True)

def load_text():
    if not os.path.exists(FILE):
        return ""
    with open(FILE, "r", encoding="utf-8") as f:
        return json.load(f).get("text", "")

def save_text(text):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump({"text": text}, f, ensure_ascii=False, indent=2)