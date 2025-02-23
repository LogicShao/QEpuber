from PyQt6.QtWidgets import QApplication
from MainWindow import MainWindow
from ThemeManager import ThemeManager, Theme
import sys


def main():
    app = QApplication(sys.argv)
    ThemeManager.load_theme(app, Theme.DARK)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
