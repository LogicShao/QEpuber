import PyQt6.QtWidgets as qtw
import PyQt6.QtGui as qtg
import PyQt6.QtCore as qtc
from logger import logger
from Ebook import EBook, EBookChapter, save_EBook_in_JSON, load_EBook_from_JSON

index_html_path = "./html/test001.html"


class MainWindow(qtw.QMainWindow):
    _book: EBook | None = None

    def __init__(self):
        super().__init__()
        self.setup_ui()

        try:
            self._book = load_EBook_from_JSON()
        except FileNotFoundError:
            logger.info("Saved EBook not found")
            self._book = None

        if self._book is not None:
            self.update_html_browser(self._book.get_chapter())
            self.update_toc_list()
            self.highlight_current_chapter()
        else:
            self.update_html_browser()

    def closeEvent(self, event: qtg.QCloseEvent):
        if self._book is not None:
            save_EBook_in_JSON(self._book)
        event.accept()

    def setup_ui(self):
        self.setWindowTitle("QEpuber")
        self.setWindowIcon(qtg.QIcon("./figures/book_reader_icon.png"))
        self.setGeometry(100, 100, 800, 600)

        self._central_widget = qtw.QWidget()
        self.setCentralWidget(self._central_widget)

        self._layout = qtw.QVBoxLayout()
        self._central_widget.setLayout(self._layout)

        self._menu_bar = self.make_menu_bar()
        self._layout.setMenuBar(self._menu_bar)

        self._tool_bar = self.make_tool_bar()
        self._layout.addWidget(self._tool_bar)

        splitter = qtw.QSplitter(
            qtc.Qt.Orientation.Horizontal, self._central_widget)

        self._toc_list = qtw.QListWidget()
        self._toc_list.itemClicked.connect(self.load_anchor_by_click_toc)
        splitter.addWidget(self._toc_list)

        self._html_browser = self.make_html_browser()
        splitter.addWidget(self._html_browser)

        splitter.setSizes([200, 600])

        self._layout.addWidget(splitter)

    def make_tool_bar(self):
        tool_bar = qtw.QToolBar()

        prev_button = qtw.QToolButton()
        prev_button.setIcon(qtg.QIcon("./figures/left_arrow.svg"))
        prev_button.clicked.connect(self.prev_chapter)

        next_button = qtw.QToolButton()
        next_button.setIcon(qtg.QIcon("./figures/right_arrow.svg"))
        next_button.clicked.connect(self.next_chapter)

        tool_bar.addWidget(prev_button)
        tool_bar.addWidget(next_button)

        return tool_bar

    def make_menu_bar(self):
        menu_bar = qtw.QMenuBar()

        file_menu = menu_bar.addMenu("File")
        open_action = file_menu.addAction("Open EPUB")
        open_action.triggered.connect(self.load_epub)
        open_action.setShortcut("Ctrl+O")
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut("Ctrl+Q")

        view_menu = menu_bar.addMenu("View")
        next_action = view_menu.addAction("Next Chapter")
        next_action.triggered.connect(self.next_chapter)
        next_action.setShortcut("]")
        prev_action = view_menu.addAction("Previous Chapter")
        prev_action.triggered.connect(self.prev_chapter)
        prev_action.setShortcut("[")
        index_action = view_menu.addAction("Index")
        index_action.triggered.connect(self.change_to_index_page)
        index_action.setShortcut("Ctrl+I")

        return menu_bar

    def change_to_index_page(self):
        self.update_html_browser()
        self.update_toc_list()
        self._book = None

    def highlight_current_chapter(self):
        if self._book is None:
            return
        self._toc_list.setCurrentRow(self._book._now_toc_idx)

    def make_html_browser(self):
        html_browser = qtw.QTextBrowser()
        html_browser.setOpenExternalLinks(True)
        return html_browser

    def update_html_browser(self, eBookChapter: EBookChapter | None = None):
        if eBookChapter is None:
            self._html_browser.setSource(
                qtc.QUrl.fromLocalFile(index_html_path))
            self.setWindowTitle("QEpuber")
            logger.info("Index page loaded")
            return

        self._html_browser.setSource(qtc.QUrl.fromLocalFile(eBookChapter.path))
        self.setWindowTitle(f"QEpuber - {eBookChapter.title}")
        logger.info(f"Chapter loaded: {eBookChapter.title}")

        anchor = eBookChapter.get_anchor()
        if anchor is not None:
            self._html_browser.scrollToAnchor(anchor)
            logger.info(f"Anchor loaded: {anchor}")

    def load_anchor_by_click_toc(self, item: qtw.QListWidgetItem):
        if self._book is None:
            return
        anchor_index = self._toc_list.row(item)
        chapter_index = self._book.archor_idx_to_chapter_idx[anchor_index]
        html_path = self._book.chapter_path_list[chapter_index]
        anchor = self._book.anchor[anchor_index]
        title = self._book.toc[anchor_index]
        self._book._now_toc_idx = anchor_index
        self.update_html_browser(EBookChapter(title, html_path, anchor))
        self.highlight_current_chapter()

    def update_toc_list(self):
        self._toc_list.clear()
        if self._book is None:
            return
        for chapter in self._book.toc:
            self._toc_list.addItem(chapter)

    def load_epub(self):
        epub_path, _ = qtw.QFileDialog.getOpenFileName(
            self, "打开 EPUB 文件", "", "EPUB 文件 (*.epub)")
        if not epub_path:
            logger.info("未选择 EPUB 文件")
            return
        logger.info(f"Loading EPUB: {epub_path}")
        self._book = EBook(epub_path)
        self.update_html_browser(self._book.get_chapter())
        self.update_toc_list()

    def next_chapter(self):
        if self._book is None:
            qtw.QMessageBox.warning(
                self, "Error", "No eBook loaded", qtw.QMessageBox.StandardButton.Ok)
            return
        self._book.next_chapter()
        self.update_html_browser(self._book.get_chapter())
        self.highlight_current_chapter()

        logger.info(f"chapter changed to: {self._book._now_toc_idx}")

    def prev_chapter(self):
        if self._book is None:
            qtw.QMessageBox.warning(
                self, "Error", "No eBook loaded", qtw.QMessageBox.StandardButton.Ok)
            return
        self.update_html_browser()
        self._book.prev_chapter()
        self.update_html_browser(self._book.get_chapter())
        self.highlight_current_chapter()

        logger.info(f"chapter changed to: {self._book._now_toc_idx}")
