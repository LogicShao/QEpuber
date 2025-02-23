import PyQt6.QtWidgets as qtw
import PyQt6.QtGui as qtg
import PyQt6.QtCore as qtc
from logger import logger
from enum import Enum


class Theme(Enum):
    DARK = 'dark'
    LIGHT = 'light'


class ThemeManager:
    @staticmethod
    def load_theme(app: qtw.QApplication, theme: Theme):
        """根据传入的枚举值加载主题"""
        if theme == Theme.DARK:
            ThemeManager.set_dark_theme(app)
            ThemeManager.load_qss(app, "./qss/dark_theme.qss")
        elif theme == Theme.LIGHT:
            ThemeManager.set_light_theme(app)
            ThemeManager.load_qss(app, "./qss/light_theme.qss")

    @staticmethod
    def set_dark_theme(app: qtw.QApplication):
        """设置深色主题"""
        palette = qtg.QPalette()
        palette.setColor(qtg.QPalette.ColorRole.Window, qtg.QColor("#2B2B2B"))
        palette.setColor(qtg.QPalette.ColorRole.WindowText,
                         qtg.QColor("#FFFFFF"))
        palette.setColor(qtg.QPalette.ColorRole.Button, qtg.QColor("#555555"))
        palette.setColor(qtg.QPalette.ColorRole.ButtonText,
                         qtg.QColor("#FFFFFF"))
        app.setPalette(palette)

    @staticmethod
    def set_light_theme(app: qtw.QApplication):
        """设置浅色主题"""
        palette = qtg.QPalette()
        palette.setColor(qtg.QPalette.ColorRole.Window, qtg.QColor("#F5F5F5"))
        palette.setColor(qtg.QPalette.ColorRole.WindowText,
                         qtg.QColor("#333333"))
        palette.setColor(qtg.QPalette.ColorRole.Button, qtg.QColor("#DDDDDD"))
        palette.setColor(qtg.QPalette.ColorRole.ButtonText,
                         qtg.QColor("#000000"))
        app.setPalette(palette)

    @staticmethod
    def load_qss(app: qtw.QApplication, theme_file: str):
        """加载 QSS 样式文件"""
        with open(theme_file, "r") as f:
            style = f.read()
            app.setStyleSheet(style)
