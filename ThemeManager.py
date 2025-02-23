import PyQt6.QtWidgets as qtw
import PyQt6.QtGui as qtg
import PyQt6.QtCore as qtc
from logger import logger
from enum import Enum


class Theme(Enum):
    DARK = 'dark'
    LIGHT = 'light'
    DEFAULT = 'default'


class ThemeManager:
    # 主题颜色配置字典
    THEME_COLORS = {
        Theme.DARK: {
            "window": "#2B2B2B",
            "window_text": "#FFFFFF",
            "button": "#555555",
            "button_text": "#FFFFFF"
        },
        Theme.LIGHT: {
            "window": "#F5F5F5",
            "window_text": "#333333",
            "button": "#DDDDDD",
            "button_text": "#000000"
        },
        Theme.DEFAULT: {
            "window": "#FFFFFF",
            "window_text": "#000000",
            "button": "#F0F0F0",
            "button_text": "#000000"
        }
    }

    # QSS 文件路径
    QSS_PATHS = {
        Theme.DARK: "./qss/dark_theme.qss",
        Theme.LIGHT: "./qss/light_theme.qss",
        Theme.DEFAULT: "./qss/default_theme.qss"
    }

    def __init__(self, app: qtw.QApplication):
        self.app = app

    def load_theme(self, theme: Theme = Theme.DEFAULT):
        """根据传入的枚举值加载主题"""
        if theme == Theme.DARK:
            self.set_dark_theme()
            self.load_qss(self.QSS_PATHS[Theme.DARK])
        elif theme == Theme.LIGHT:
            self.set_light_theme()
            self.load_qss(self.QSS_PATHS[Theme.LIGHT])
        else:
            self.load_qss(self.QSS_PATHS[Theme.DEFAULT])

        logger.info(f"Loaded theme: {theme.value}")

    def set_dark_theme(self):
        """设置深色主题"""
        palette = qtg.QPalette()
        palette.setColor(qtg.QPalette.ColorRole.Window, qtg.QColor(
            self.THEME_COLORS[Theme.DARK]["window"]))
        palette.setColor(qtg.QPalette.ColorRole.WindowText,
                         qtg.QColor(self.THEME_COLORS[Theme.DARK]["window_text"]))
        palette.setColor(qtg.QPalette.ColorRole.Button, qtg.QColor(
            self.THEME_COLORS[Theme.DARK]["button"]))
        palette.setColor(qtg.QPalette.ColorRole.ButtonText,
                         qtg.QColor(self.THEME_COLORS[Theme.DARK]["button_text"]))
        self.app.setPalette(palette)

    def set_light_theme(self):
        """设置浅色主题"""
        palette = qtg.QPalette()
        palette.setColor(qtg.QPalette.ColorRole.Window, qtg.QColor(
            self.THEME_COLORS[Theme.LIGHT]["window"]))
        palette.setColor(qtg.QPalette.ColorRole.WindowText,
                         qtg.QColor(self.THEME_COLORS[Theme.LIGHT]["window_text"]))
        palette.setColor(qtg.QPalette.ColorRole.Button, qtg.QColor(
            self.THEME_COLORS[Theme.LIGHT]["button"]))
        palette.setColor(qtg.QPalette.ColorRole.ButtonText,
                         qtg.QColor(self.THEME_COLORS[Theme.LIGHT]["button_text"]))
        self.app.setPalette(palette)

    def load_qss(self, theme_file: str):
        """加载 QSS 样式文件"""
        with open(theme_file, "r") as f:
            style = f.read()
            self.app.setStyleSheet(style)
