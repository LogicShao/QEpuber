import json
from Ebook import EBook
from PyQt6.QtGui import QFont

setting_path = "./eBookCache/pre_settings.json"


class SettingSaver:
    def __init__(self):
        self.setting = {}

    def add_last_read_ebook(self, eBooks: list[EBook], last_idx: int = None):
        if last_idx is not None:
            self.setting["last_idx"] = last_idx
        last_read = []
        for eBook in eBooks:
            last_read.append({
                "epub_path": eBook.epub_path,
                "_now_toc_idx": eBook._now_toc_idx
            })
        self.setting["last_read"] = last_read

    def add_last_font(self, font: QFont):
        self.setting["font"] = {
            "family": font.family(),
            "size": font.pointSize(),
            "bold": font.bold(),
            "italic": font.italic()
        }

    def add_opened_ebooks_path(self, eBookPaths: set[str]):
        self.setting["opened_ebooks_path"] = list(eBookPaths)

    def save(self):
        with open(setting_path, "w") as f:
            json.dump(self.setting, f, indent=4)


class SettingLoader:
    def __init__(self):
        self.setting = {}
        self.load()

    def load(self):
        try:
            with open(setting_path, "r") as f:
                self.setting = json.load(f)
        except FileNotFoundError:
            return None

    def get_last_read_ebooks(self) -> list[EBook]:
        if "last_read" not in self.setting:
            return []
        eBooks = []
        for data in self.setting["last_read"]:
            eBooks.append(EBook(data["epub_path"], data["_now_toc_idx"]))
        return eBooks

    def get_last_idx(self) -> int | None:
        if "last_idx" not in self.setting:
            return None
        return self.setting["last_idx"]

    def get_last_font(self) -> QFont:
        if "font" not in self.setting:
            return QFont()
        font_data = self.setting["font"]
        font = QFont(font_data["family"], font_data["size"])
        font.setBold(font_data["bold"])
        font.setItalic(font_data["italic"])
        return font

    def get_opened_ebooks_path(self) -> set[str]:
        if "opened_ebooks_path" not in self.setting:
            return set()
        return set(self.setting["opened_ebooks_path"])
