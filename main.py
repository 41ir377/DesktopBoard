import sys
import re
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTextEdit,
    QSystemTrayIcon,
    QMenu,
    QAction,
    QDialog,
    QVBoxLayout,
    QLabel,
    QFontComboBox,
    QSlider,
    QPushButton,
    QHBoxLayout,
)
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PySide6.QtCore import QTimer, Qt, QByteArray

import storage

RTL_RE = re.compile(r"[\u0600-\u06FF]")

def create_icon(text="DB", size=64, bg_color=QColor(40, 40, 40), fg_color=QColor(255, 255, 255)):
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    p.fillRect(0, 0, size, size, bg_color)
    f = QFont("Segoe UI", int(size / 3))
    f.setBold(True)
    p.setFont(f)
    p.setPen(fg_color)
    p.drawText(pix.rect(), Qt.AlignCenter, text)
    p.end()
    return QIcon(pix)


class SettingsDialog(QDialog):
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.settings = settings or {}
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Font:"))
        self.font_combo = QFontComboBox()
        if "font_family" in self.settings:
            self.font_combo.setCurrentFont(QFont(self.settings["font_family"]))
        layout.addWidget(self.font_combo)

        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Font size:"))
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setMinimum(8)
        self.size_slider.setMaximum(48)
        self.size_slider.setValue(self.settings.get("font_size", 12))
        size_layout.addWidget(self.size_slider)
        layout.addLayout(size_layout)

        op_layout = QHBoxLayout()
        op_layout.addWidget(QLabel("Opacity:"))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setMinimum(30)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setValue(self.settings.get("opacity", 100))
        op_layout.addWidget(self.opacity_slider)
        layout.addLayout(op_layout)

        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def get_values(self):
        return {
            "font_family": self.font_combo.currentFont().family(),
            "font_size": self.size_slider.value(),
            "opacity": self.opacity_slider.value(),
        }


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DesktopBoard")
        self.setWindowIcon(create_icon())
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self.text = QTextEdit()
        self.text.setAcceptRichText(True)
        self.setCentralWidget(self.text)

        self.dirty = False
        self.text.textChanged.connect(self.on_text_changed)

        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(create_icon())
        self.tray.setVisible(True)

        menu = QMenu()
        self.show_action = QAction("Show/Hide")
        self.show_action.triggered.connect(self.toggle_visibility)
        menu.addAction(self.show_action)

        settings_action = QAction("Settings")
        settings_action.triggered.connect(self.open_settings)
        menu.addAction(settings_action)

        menu.addSeparator()
        quit_action = QAction("Exit")
        quit_action.triggered.connect(self.close)
        menu.addAction(quit_action)

        self.tray.setContextMenu(menu)

        self.autosave_timer = QTimer(self)
        self.autosave_timer.setInterval(5000)
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start()

        self._drag_pos = None

        # Load state
        state = storage.load_state()
        content = state.get("content", "")
        if content.startswith("<"):
            # assume html
            self.text.setHtml(content)
        else:
            self.text.setPlainText(content)

        geometry_b64 = state.get("geometry")
        if geometry_b64:
            try:
                geom = QByteArray.fromBase64(geometry_b64.encode("utf-8"))
                self.restoreGeometry(geom)
            except Exception:
                pass

        settings = state.get("settings", {})
        font_family = settings.get("font_family")
        font_size = settings.get("font_size")
        if font_family:
            font = self.text.font()
            font.setFamily(font_family)
            if font_size:
                font.setPointSize(int(font_size))
            self.text.setFont(font)

        opacity = settings.get("opacity", 100)
        self.setWindowOpacity(opacity / 100.0)

        # Apply direction if needed
        self.apply_direction()

    def on_text_changed(self):
        self.dirty = True
        self.apply_direction()

    def apply_direction(self):
        plain = self.text.toPlainText()
        if not plain:
            return
        first = plain.strip()[0]
        if RTL_RE.search(first):
            self.text.setLayoutDirection(Qt.RightToLeft)
        else:
            self.text.setLayoutDirection(Qt.LeftToRight)

    def autosave(self):
        if not self.dirty:
            return
        self.save_state()
        self.dirty = False

    def save_state(self):
        content = self.text.toHtml()
        geom = self.saveGeometry().toBase64().data().decode("utf-8")
        settings = {
            "font_family": self.text.font().family(),
            "font_size": self.text.font().pointSize(),
            "opacity": int(self.windowOpacity() * 100),
        }
        state = {
            "content": content,
            "geometry": geom,
            "settings": settings,
        }
        storage.save_state(state)

    def closeEvent(self, event):
        self.save_state()
        event.accept()

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def open_settings(self):
        cur_settings = storage.load_state().get("settings", {})
        dlg = SettingsDialog(self, settings=cur_settings)
        if dlg.exec() == QDialog.Accepted:
            vals = dlg.get_values()
            font = self.text.font()
            font.setFamily(vals["font_family"])
            font.setPointSize(int(vals["font_size"]))
            self.text.setFont(font)
            self.setWindowOpacity(vals["opacity"] / 100.0)
            # persist
            self.save_state()

    # Support dragging when frameless
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        # save geometry on move end
        self.save_state()

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()