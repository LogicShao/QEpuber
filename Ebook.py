from EBookParser import load_epub, parse_toc
import os


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
        self.book_name = os.path.splitext(os.path.basename(epub_path))[0]
        self.cache_folder, self.chapter_path_list = load_epub(epub_path)
        self._now_toc_idx = now_toc_idx
        self.toc, self.anchor = zip(*parse_toc(self.cache_folder))
        self.archor_idx_to_chapter_idx = []
        for i in range(len(self.anchor)):
            chapter_idx = self.chapter_path_list.index(
                self.anchor[i].split("#")[0])
            self.archor_idx_to_chapter_idx.append(chapter_idx)

    def next_anchor(self):
        """get next anchor in toc"""
        self._now_toc_idx = (
            self._now_toc_idx + 1) % self.get_anchor_count()
        return self.get_anchor()

    def prev_anchor(self):
        """get previous anchor in toc"""
        self._now_toc_idx = (
            self._now_toc_idx - 1) % self.get_anchor_count()
        return self.get_anchor()

    def get_anchor(self, toc_index: int | None = None) -> EBookChapter:
        """get anchor by toc index"""
        if toc_index is None:
            toc_index = self._now_toc_idx
        chapter_index = self.archor_idx_to_chapter_idx[toc_index]
        return EBookChapter(
            title=self.toc[toc_index],
            path=self.chapter_path_list[chapter_index],
            anchor=self.anchor[toc_index]
        )

    def get_anchor_count(self):
        return len(self.toc)

    def __eq__(self, value):
        if isinstance(value, EBook):
            return self.epub_path == value.epub_path
        raise TypeError("EBook can only compare with EBook")


if __name__ == "__main__":
    # Test
    eBook = EBook("eBooks/小逻辑 (黑格尔, 贺麟) (Z-Library).epub")
    print('toc_len', len(eBook.toc))
    print('chapter_len', len(eBook.chapter_path_list))
    print('anchor_len', len(eBook.anchor))
    for chapter in eBook.chapter_path_list:
        print(chapter)
    for anchor, idx in zip(eBook.anchor, eBook.archor_idx_to_chapter_idx):
        print(f"{anchor} -> {idx}")
