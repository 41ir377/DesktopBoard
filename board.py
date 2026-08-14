import os

from PySide6.QtWidgets import (
    QWidget,
    QTextEdit,
    QSystemTrayIcon,
    QMenu,
    QApplication,
    QStyle
)

from PySide6.QtCore import (
    Qt,
    QRect
)

from PySide6.QtGui import (
    QPixmap,
    QPainter,
    QColor,
    QAction
)

from storage import (
    load_notes,
    save_notes,
    load_config,
    save_config,
    get_app_dir
)


class Board(QWidget):

    BORDER = 10

    MIN_WIDTH = 350
    MIN_HEIGHT = 250

    def __init__(self):

        super().__init__()

        self.config = load_config()

        self.drag_position = None
        self.resize_mode = None
        self.resizing = False

        # ==========================================
        # Window
        # ==========================================

        self.setMinimumSize(
            self.MIN_WIDTH,
            self.MIN_HEIGHT
        )

        self.resize(
            self.config.get("w", 700),
            self.config.get("h", 500)
        )

        self.move(
            self.config.get("x", 100),
            self.config.get("y", 100)
        )

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.Tool
        )

        self.setAttribute(
            Qt.WA_TranslucentBackground
        )

        self.setWindowOpacity(
            self.config.get(
                "opacity",
                95
            ) / 100
        )

        # ==========================================
        # Background
        # ==========================================

        self.background = self.find_background()

        # ==========================================
        # Editor
        # ==========================================

        self.editor = QTextEdit(self)

        self.editor.setLayoutDirection(
            Qt.RightToLeft
        )

        self.editor.setPlainText(
            load_notes()
        )

        self.editor.textChanged.connect(
            self.save
        )

        self.update_editor_style()

        # ==========================================
        # Tray
        # ==========================================

        self.create_tray()

        # ==========================================
        # Initial geometry
        # ==========================================

        self.update_editor_geometry()

    # ==================================================
    # Background
    # ==================================================

    def find_background(self):

        assets_dir = os.path.join(
            get_app_dir(),
            "assets"
        )

        preferred = os.path.join(
            assets_dir,
            "chalkboard.png"
        )

        if os.path.isfile(preferred):

            return preferred

        if os.path.isdir(assets_dir):

            for filename in os.listdir(
                assets_dir
            ):

                if filename.lower().endswith(
                    (
                        ".png",
                        ".jpg",
                        ".jpeg",
                        ".webp"
                    )
                ):

                    return os.path.join(
                        assets_dir,
                        filename
                    )

        return None

    # ==================================================
    # Paint Background
    # ==================================================

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.SmoothPixmapTransform
        )

        rect = self.rect()

        # ------------------------------------------
        # Image
        # ------------------------------------------

        if self.background:

            pixmap = QPixmap(
                self.background
            )

            if not pixmap.isNull():

                scaled = pixmap.scaled(
                    rect.size(),
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )

                x = (
                    scaled.width()
                    - rect.width()
                ) // 2

                y = (
                    scaled.height()
                    - rect.height()
                ) // 2

                painter.drawPixmap(
                    -x,
                    -y,
                    scaled
                )

            else:

                painter.fillRect(
                    rect,
                    QColor("#1b281d")
                )

        else:

            painter.fillRect(
                rect,
                QColor("#1b281d")
            )

        # ------------------------------------------
        # Slight dark overlay
        # ------------------------------------------

        painter.fillRect(
            rect,
            QColor(
                0,
                0,
                0,
                25
            )
        )

        # ------------------------------------------
        # Border
        # ------------------------------------------

        painter.setPen(
            QColor(
                255,
                255,
                255,
                35
            )
        )

        painter.drawRoundedRect(
            1,
            1,
            self.width() - 2,
            self.height() - 2,
            18,
            18
        )

    # ==================================================
    # Resize Event
    # ==================================================

    def resizeEvent(self, event):

        self.update_editor_geometry()

        self.save_geometry()

        super().resizeEvent(event)

    # ==================================================
    # Editor Geometry
    # ==================================================

    def update_editor_geometry(self):

        margin = 25

        self.editor.setGeometry(
            margin,
            margin,
            max(
                100,
                self.width() - margin * 2
            ),
            max(
                100,
                self.height() - margin * 2
            )
        )

    # ==================================================
    # Editor Style
    # ==================================================

    def update_editor_style(self):

        font_size = self.config.get(
            "font_size",
            22
        )

        text_color = self.config.get(
            "text_color",
            "#ffffff"
        )

        self.editor.setStyleSheet(
            f"""
            QTextEdit {{
                background: transparent;
                border: none;

                color: {text_color};

                font-family:
                    "Segoe UI",
                    "Tahoma";

                font-size: {font_size}px;

                padding: 15px;

                selection-background-color:
                    rgba(255,255,255,50);
            }}
            """
        )

    # ==================================================
    # Save Notes
    # ==================================================

    def save(self):

        save_notes(
            self.editor.toPlainText()
        )

    # ==================================================
    # Save Geometry
    # ==================================================

    def save_geometry(self):

        self.config["x"] = self.x()
        self.config["y"] = self.y()

        self.config["w"] = self.width()
        self.config["h"] = self.height()

        save_config(
            self.config
        )

    # ==================================================
    # Resize Mode
    # ==================================================

    def get_resize_mode(self, pos):

        x = pos.x()
        y = pos.y()

        width = self.width()
        height = self.height()

        left = x <= self.BORDER
        right = x >= width - self.BORDER

        top = y <= self.BORDER
        bottom = y >= height - self.BORDER

        if top and left:
            return "top-left"

        if top and right:
            return "top-right"

        if bottom and left:
            return "bottom-left"

        if bottom and right:
            return "bottom-right"

        if left:
            return "left"

        if right:
            return "right"

        if top:
            return "top"

        if bottom:
            return "bottom"

        return None

    # ==================================================
    # Mouse Press
    # ==================================================

    def mousePressEvent(self, event):

        if event.button() != Qt.LeftButton:

            return

        position = (
            event.position().toPoint()
        )

        self.resize_mode = (
            self.get_resize_mode(
                position
            )
        )

        # ------------------------------------------
        # Resize
        # ------------------------------------------

        if self.resize_mode:

            self.resizing = True

            self.start_geometry = (
                self.geometry()
            )

            self.start_mouse = (
                event.globalPosition().toPoint()
            )

            return

        # ------------------------------------------
        # Move
        # ------------------------------------------

        self.drag_position = (
            event.globalPosition().toPoint()
            -
            self.frameGeometry().topLeft()
        )

    # ==================================================
    # Mouse Move
    # ==================================================

    def mouseMoveEvent(self, event):

        position = (
            event.position().toPoint()
        )

        mode = self.get_resize_mode(
            position
        )

        # ------------------------------------------
        # Cursor
        # ------------------------------------------

        if not self.resizing:

            if mode in (
                "top-left",
                "bottom-right"
            ):

                self.setCursor(
                    Qt.SizeFDiagCursor
                )

            elif mode in (
                "top-right",
                "bottom-left"
            ):

                self.setCursor(
                    Qt.SizeBDiagCursor
                )

            elif mode in (
                "left",
                "right"
            ):

                self.setCursor(
                    Qt.SizeHorCursor
                )

            elif mode in (
                "top",
                "bottom"
            ):

                self.setCursor(
                    Qt.SizeVerCursor
                )

            else:

                self.setCursor(
                    Qt.ArrowCursor
                )

        # ------------------------------------------
        # Resize
        # ------------------------------------------

        if self.resizing:

            self.perform_resize(
                event.globalPosition().toPoint()
            )

            return

        # ------------------------------------------
        # Move
        # ------------------------------------------

        if (
            self.drag_position is not None
            and
            event.buttons() & Qt.LeftButton
        ):

            self.move(
                event.globalPosition().toPoint()
                -
                self.drag_position
            )

    # ==================================================
    # Perform Resize
    # ==================================================

    def perform_resize(self, current_position):

        delta = (
            current_position
            -
            self.start_mouse
        )

        geometry = QRect(
            self.start_geometry
        )

        mode = self.resize_mode

        # ------------------------------------------
        # Right
        # ------------------------------------------

        if "right" in mode:

            geometry.setRight(
                geometry.right()
                +
                delta.x()
            )

        # ------------------------------------------
        # Bottom
        # ------------------------------------------

        if "bottom" in mode:

            geometry.setBottom(
                geometry.bottom()
                +
                delta.y()
            )

        # ------------------------------------------
        # Left
        # ------------------------------------------

        if "left" in mode:

            new_left = (
                geometry.left()
                +
                delta.x()
            )

            if (
                geometry.right()
                -
                new_left
                >= self.MIN_WIDTH
            ):

                geometry.setLeft(
                    new_left
                )

        # ------------------------------------------
        # Top
        # ------------------------------------------

        if "top" in mode:

            new_top = (
                geometry.top()
                +
                delta.y()
            )

            if (
                geometry.bottom()
                -
                new_top
                >= self.MIN_HEIGHT
            ):

                geometry.setTop(
                    new_top
                )

        self.setGeometry(
            geometry
        )

    # ==================================================
    # Mouse Release
    # ==================================================

    def mouseReleaseEvent(self, event):

        self.drag_position = None

        self.resizing = False

        self.resize_mode = None

        self.save_geometry()

        self.setCursor(
            Qt.ArrowCursor
        )

    # ==================================================
    # Create Tray
    # ==================================================

    def create_tray(self):

        self.tray = QSystemTrayIcon(
            self
        )

        # ------------------------------------------
        # Tray Icon
        # ------------------------------------------

        icon = self.style().standardIcon(
            QStyle.SP_ComputerIcon
        )

        self.tray.setIcon(
            icon
        )

        self.tray.setToolTip(
            "ChalkDesk"
        )

        # ------------------------------------------
        # Menu
        # ------------------------------------------

        menu = QMenu()

        # Show / Hide
        show_action = QAction(
            "نمایش / مخفی کردن تخته",
            self
        )

        show_action.triggered.connect(
            self.toggle_visibility
        )

        menu.addAction(
            show_action
        )

        menu.addSeparator()

        # ------------------------------------------
        # Font Menu
        # ------------------------------------------

        font_menu = menu.addMenu(
            "اندازه فونت"
        )

        font_sizes = [
            14,
            16,
            18,
            20,
            22,
            24,
            28,
            32,
            36,
            42
        ]

        for size in font_sizes:

            action = QAction(
                f"{size}px",
                self
            )

            action.triggered.connect(
                lambda checked=False,
                selected_size=size:
                self.set_font_size(
                    selected_size
                )
            )

            font_menu.addAction(
                action
            )

        # ------------------------------------------
        # Opacity Menu
        # ------------------------------------------

        opacity_menu = menu.addMenu(
            "شفافیت"
        )

        opacity_values = [
            100,
            95,
            90,
            85,
            80,
            70,
            60
        ]

        for opacity in opacity_values:

            action = QAction(
                f"{opacity}%",
                self
            )

            action.triggered.connect(
                lambda checked=False,
                selected_opacity=opacity:
                self.set_opacity(
                    selected_opacity
                )
            )

            opacity_menu.addAction(
                action
            )

        menu.addSeparator()

        # ------------------------------------------
        # Exit
        # ------------------------------------------

        exit_action = QAction(
            "خروج",
            self
        )

        exit_action.triggered.connect(
            QApplication.quit
        )

        menu.addAction(
            exit_action
        )

        # ------------------------------------------
        # Tray
        # ------------------------------------------

        self.tray.setContextMenu(
            menu
        )

        self.tray.activated.connect(
            self.tray_clicked
        )

        self.tray.show()

    # ==================================================
    # Tray Click
    # ==================================================

    def tray_clicked(self, reason):

        if (
            reason
            ==
            QSystemTrayIcon.Trigger
        ):

            self.toggle_visibility()

    # ==================================================
    # Toggle Visibility
    # ==================================================

    def toggle_visibility(self):

        if self.isVisible():

            self.hide()

        else:

            self.show()

            self.raise_()

            self.activateWindow()

    # ==================================================
    # Font Size
    # ==================================================

    def set_font_size(self, size):

        self.config["font_size"] = size

        save_config(
            self.config
        )

        self.update_editor_style()

    # ==================================================
    # Opacity
    # ==================================================

    def set_opacity(self, opacity):

        self.config["opacity"] = opacity

        self.setWindowOpacity(
            opacity / 100
        )

        save_config(
            self.config
        )

    # ==================================================
    # Close
    # ==================================================

    def closeEvent(self, event):

        self.save()

        self.save_geometry()

        self.tray.hide()

        event.accept()