import PyQt6.QtWidgets as qtw
import PyQt6.QtGui as qtg
import PyQt6.QtCore as qtc
from logger import logger
from Ebook import EBook, EBookChapter

index_html_path = "./html/test001.html"


class MainWindow(qtw.QMainWindow):
    _book: EBook | None = None

    def __init__(self):
        super().__init__()
        self.setup_ui()

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

        splitter = qtw.QSplitter(
            qtc.Qt.Orientation.Horizontal, self._central_widget)

        self._toc_list = qtw.QListWidget()
        splitter.addWidget(self._toc_list)

        self._html_browser = self.make_html_browser()
        splitter.addWidget(self._html_browser)

        splitter.setSizes([200, 600])

        self._layout.addWidget(splitter)

    def make_menu_bar(self):
        menu_bar = qtw.QMenuBar()

        file_menu = menu_bar.addMenu("File")
        open_action = file_menu.addAction("Open EPUB")
        open_action.triggered.connect(self.load_epub)
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)

        view_menu = menu_bar.addMenu("View")
        next_action = view_menu.addAction("Next Chapter")
        next_action.triggered.connect(self.next_chapter)
        prev_action = view_menu.addAction("Previous Chapter")
        prev_action.triggered.connect(self.prev_chapter)

        return menu_bar

    def make_html_browser(self):
        html_browser = qtw.QTextBrowser()
        html_browser.setOpenExternalLinks(True)
        html_browser.setSource(qtc.QUrl.fromLocalFile(index_html_path))
        return html_browser

    def update_html_browser(self, EBookChapter: EBookChapter | None = None):
        if EBookChapter is None:
            self._html_browser.setSource(
                qtc.QUrl.fromLocalFile(index_html_path))
            self.setWindowTitle("QEpuber")
        else:
            self._html_browser.setSource(
                qtc.QUrl.fromLocalFile(EBookChapter.path))
            self.setWindowTitle(f"QEpuber - {EBookChapter.title}")

    def load_epub(self):
        epub_path, _ = qtw.QFileDialog.getOpenFileName(
            self, "打开 EPUB 文件", "", "EPUB 文件 (*.epub)")
        if not epub_path:
            logger.info("未选择 EPUB 文件")
            return
        logger.info(f"Loading EPUB: {epub_path}")
        self._book = EBook(epub_path)
        self.update_html_browser(self._book.get_chapter())

    def next_chapter(self):
        if self._book is None:
            qtw.QMessageBox.warning(
                self, "Error", "No eBook loaded", qtw.QMessageBox.StandardButton.Ok)
            return
        self._book.next_chapter()
        self.update_html_browser(self._book.get_chapter())

        logger.info(f"chapter changed to: {self._book._now_chapter_idx}")

    def prev_chapter(self):
        if self._book is None:
            qtw.QMessageBox.warning(
                self, "Error", "No eBook loaded", qtw.QMessageBox.StandardButton.Ok)
            return
        self.update_html_browser()
        self._book.prev_chapter()
        self.update_html_browser(self._book.get_chapter())

        logger.info(f"chapter changed to: {self._book._now_chapter_idx}")
