from ebookparser import load_epub, parse_toc
import json


class EBookChapter:
    def __init__(self, title, path, anchor=None):
        self.title = title
        self.path = path  # HTML file path
        self.anchor = anchor  # HTML file path with anchor

    def get_anchor(self):
        if self.anchor is None:
            return None
        anchor_split = self.anchor.split("#")
        if len(anchor_split) == 1:
            return None
        return anchor_split[1]


class EBook:
    def __init__(self, epub_path, now_toc_idx=0):
        self.epub_path = epub_path
        self.cache_folder, self.chapter_path_list = load_epub(epub_path)
        self._now_toc_idx = now_toc_idx
        self.toc, self.anchor = zip(*parse_toc(self.cache_folder))
        self.archor_idx_to_chapter_idx = []
        for i in range(len(self.anchor)):
            self.archor_idx_to_chapter_idx.append(
                self.chapter_path_list.index(self.anchor[i].split("#")[0]))

    def next_chapter(self):
        self._now_toc_idx = (
            self._now_toc_idx + 1) % self.get_chapter_count()
        return self.get_chapter()

    def prev_chapter(self):
        self._now_toc_idx = (
            self._now_toc_idx - 1) % self.get_chapter_count()
        return self.get_chapter()

    def get_chapter(self, toc_index: int | None = None):
        if toc_index is None:
            toc_index = self._now_toc_idx
        chapter_index = self.archor_idx_to_chapter_idx[toc_index]
        return EBookChapter(self.toc[toc_index], self.chapter_path_list[chapter_index], self.anchor[toc_index])

    def get_chapter_count(self):
        return len(self.chapter_path_list)


last_read_JSON_path = "eBookCache/last_read.json"


def save_EBook_in_JSON(eBook: EBook | None = None):
    if eBook is None:
        return
    with open(last_read_JSON_path, "w") as f:
        json.dump({"epub_path": eBook.epub_path,
                   "now_toc_idx": eBook._now_toc_idx}, f)


def load_EBook_from_JSON() -> EBook | None:
    try:
        with open(last_read_JSON_path, "r") as f:
            last_read = json.load(f)
    except FileNotFoundError:
        return None
    return EBook(last_read["epub_path"], last_read["now_toc_idx"])


if __name__ == "__main__":
    # Test
    eBook = EBook("eBooks\\小逻辑 (黑格尔, 贺麟) (Z-Library).epub")
    for chapter in eBook.chapter_path_list:
        print(chapter)
    for anchor, idx in zip(eBook.anchor, eBook.archor_idx_to_chapter_idx):
        print(f"{anchor} -> {idx}")
