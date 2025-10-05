from PyQt6.QtWidgets import QApplication
from MainWindow import MainWindow
from ThemeManager import ThemeManager, Theme
import sys


def main():
    app = QApplication(sys.argv)
    theme_manager = ThemeManager(app)
    theme_manager.load_theme(Theme.MODERN)  # 使用现代主题作为默认主题
    window = MainWindow(theme_manager)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
