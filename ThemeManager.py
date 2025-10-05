from commom_import import *
from enum import Enum


class Theme(Enum):
    DARK = 'dark'
    LIGHT = 'light'
    DEFAULT = 'default'
    MODERN = 'modern'
    BLUE = 'blue'


class ThemeManager:
    # 主题颜色配置字典
    THEME_COLORS = {
        Theme.DARK: {
            "window": "#2B2B2B",
            "window_text": "#FFFFFF",
            "button": "#555555",
            "button_text": "#FFFFFF",
            "accent": "#0078D7"
        },
        Theme.LIGHT: {
            "window": "#F5F5F5",
            "window_text": "#333333",
            "button": "#DDDDDD",
            "button_text": "#000000",
            "accent": "#0078D7"
        },
        Theme.DEFAULT: {
            "window": "#FFFFFF",
            "window_text": "#000000",
            "button": "#F0F0F0",
            "button_text": "#000000",
            "accent": "#0078D7"
        },
        Theme.MODERN: {
            "window": "#FAFAFA",
            "window_text": "#2C3E50",
            "button": "#ECF0F1",
            "button_text": "#2C3E50",
            "accent": "#3498DB"
        },
        Theme.BLUE: {
            "window": "#E3F2FD",
            "window_text": "#1565C0",
            "button": "#BBDEFB",
            "button_text": "#0D47A1",
            "accent": "#2196F3"
        }
    }

    # QSS 文件路径
    QSS_PATHS = {
        Theme.DARK: "./qss/dark_theme.qss",
        Theme.LIGHT: "./qss/light_theme.qss",
        Theme.DEFAULT: "./qss/default_theme.qss",
        Theme.MODERN: "./qss/modern_theme.qss",
        Theme.BLUE: "./qss/blue_theme.qss"
    }

    def __init__(self, app: qtw.QApplication):
        self.app = app

    def load_theme(self, theme: Theme = Theme.DEFAULT):
        """根据传入的枚举值加载主题"""
        # 首先设置调色板
        self.set_theme_palette(theme)

        # 然后加载QSS文件
        if theme in self.QSS_PATHS:
            self.load_qss(self.QSS_PATHS[theme])
        else:
            self.load_qss(self.QSS_PATHS[Theme.DEFAULT])

        logger.info(f"Loaded theme: {theme.value}")

    def set_theme_palette(self, theme: Theme):
        """根据主题设置调色板"""
        palette = qtg.QPalette()
        colors = self.THEME_COLORS[theme]

        palette.setColor(qtg.QPalette.ColorRole.Window,
                         qtg.QColor(colors["window"]))
        palette.setColor(qtg.QPalette.ColorRole.WindowText,
                         qtg.QColor(colors["window_text"]))
        palette.setColor(qtg.QPalette.ColorRole.Button,
                         qtg.QColor(colors["button"]))
        palette.setColor(qtg.QPalette.ColorRole.ButtonText,
                         qtg.QColor(colors["button_text"]))
        palette.setColor(qtg.QPalette.ColorRole.Highlight,
                         qtg.QColor(colors["accent"]))
        palette.setColor(qtg.QPalette.ColorRole.HighlightedText,
                         qtg.QColor("#FFFFFF"))

        self.app.setPalette(palette)

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
        with open(theme_file, "r", encoding='utf-8') as f:
            style = f.read()
            self.app.setStyleSheet(style)
