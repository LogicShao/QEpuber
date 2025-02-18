from ebookparser import load_epub, parse_toc
import json


class EBookChapter:
    def __init__(self, title, path):
        self.title = title
        self.path = path


class EBook:
    def __init__(self, epub_path, now_chapter_idx=0):
        self.epub_path = epub_path
        self.cache_folder, self.chapter_path_list = load_epub(epub_path)
        self._now_chapter_idx = now_chapter_idx
        self.toc = parse_toc(self.cache_folder)

    def next_chapter(self):
        self._now_chapter_idx = (
            self._now_chapter_idx + 1) % self.get_chapter_count()
        return self.get_chapter()

    def prev_chapter(self):
        self._now_chapter_idx = (
            self._now_chapter_idx - 1) % self.get_chapter_count()
        return self.get_chapter()

    def get_chapter(self, index: int | None = None):
        if index is None:
            index = self._now_chapter_idx
        return EBookChapter(self.toc[index], self.chapter_path_list[index])

    def get_chapter_count(self):
        return len(self.chapter_path_list)


last_read_JSON_path = "eBookCache/last_read.json"


def save_EBook_in_JSON(eBook: EBook | None = None):
    if eBook is None:
        return
    with open(last_read_JSON_path, "w") as f:
        json.dump({"epub_path": eBook.epub_path,
                   "now_chapter_idx": eBook._now_chapter_idx}, f)


def load_EBook_from_JSON() -> EBook | None:
    try:
        with open(last_read_JSON_path, "r") as f:
            last_read = json.load(f)
    except FileNotFoundError:
        return None
    return EBook(last_read["epub_path"], last_read["now_chapter_idx"])
