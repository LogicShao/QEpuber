from ebookparser import load_epub, parse_toc


class EBookChapter:
    def __init__(self, title, path):
        self.title = title
        self.path = path


class EBook:
    def __init__(self, epub_path):
        self.epub_path = epub_path
        self.cache_folder, self.chapter_path_list = load_epub(epub_path)
        self._now_chapter_idx = 0
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
