import json
import os
import sys


def get_app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))

    return os.path.dirname(os.path.abspath(__file__))


APP_DIR = get_app_dir()
DATA_DIR = os.path.join(APP_DIR, "data")

NOTES_FILE = os.path.join(DATA_DIR, "notes.json")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")

os.makedirs(DATA_DIR, exist_ok=True)


DEFAULT_CONFIG = {
    "x": 100,
    "y": 100,
    "w": 700,
    "h": 500,

    "opacity": 95,
    "font_size": 22,

    "text_color": "#ffffff"
}


def load_notes():

    if not os.path.exists(NOTES_FILE):
        return ""

    try:
        with open(
            NOTES_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

            return data.get("text", "")

    except Exception:
        return ""


def save_notes(text):

    with open(
        NOTES_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            {
                "text": text
            },
            f,
            ensure_ascii=False,
            indent=2
        )


def load_config():

    if not os.path.exists(CONFIG_FILE):

        save_config(DEFAULT_CONFIG.copy())

        return DEFAULT_CONFIG.copy()

    try:

        with open(
            CONFIG_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        config = DEFAULT_CONFIG.copy()
        config.update(data)

        return config

    except Exception:

        return DEFAULT_CONFIG.copy()


def save_config(config):

    with open(
        CONFIG_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            config,
            f,
            ensure_ascii=False,
            indent=2
        )