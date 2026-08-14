import sys
import os

from PySide6.QtWidgets import (
    QApplication
)

from board import Board
from startup import enable


def resource_path(relative_path):

    if getattr(sys, "frozen", False):

        base_path = os.path.dirname(
            os.path.abspath(
                sys.executable
            )
        )

    else:

        base_path = os.path.dirname(
            os.path.abspath(
                __file__
            )
        )

    return os.path.join(
        base_path,
        relative_path
    )


# ==================================================
# Application
# ==================================================

app = QApplication(
    sys.argv
)

# بسیار مهم برای Tray
app.setQuitOnLastWindowClosed(
    False
)


# ==================================================
# Load Stylesheet
# ==================================================

style_path = resource_path(
    "styles.qss"
)

if os.path.isfile(
    style_path
):

    with open(
        style_path,
        "r",
        encoding="utf-8"
    ) as f:

        app.setStyleSheet(
            f.read()
        )


# ==================================================
# Create Board
# ==================================================

board = Board()

board.show()


# ==================================================
# Windows Startup
# ==================================================

if getattr(
    sys,
    "frozen",
    False
):

    try:

        enable(
            sys.executable
        )

    except Exception as error:

        print(
            "Startup error:",
            error
        )


# ==================================================
# Run
# ==================================================

sys.exit(
    app.exec()
)