import PyQt6.QtWidgets as qtw
import PyQt6.QtGui as qtg
import PyQt6.QtCore as qtc
from logger import logger
from Ebook import EBook, EBookChapter, save_EBooks_in_JSON, load_EBooks_from_JSON
from EBookTabWidget import EBookTabWidget

index_html_path = "./html/test001.html"


class MainWindow(qtw.QMainWindow):
    _ebook_list: list[EBook] = []

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_last_read()

    def load_last_read(self):
        last_read = load_EBooks_from_JSON()
        for eBook in last_read:
            self.load_epub_by_path(eBook.epub_path)
            self._ebook_list[-1]._now_toc_idx = eBook._now_toc_idx

    def closeEvent(self, event: qtg.QCloseEvent):
        if self._ebook_list:
            save_EBooks_in_JSON(self._ebook_list)
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

        self._tab_widget = qtw.QTabWidget()
        splitter.addWidget(self._tab_widget)
        self._tab_widget.currentChanged.connect(
            self.on_tab_widget_current_changed)

        splitter.setSizes([200, 600])

        self._layout.addWidget(splitter)

    def load_anchor_by_click_toc(self, item):
        pass

    def make_tool_bar(self):
        # TODO: Add more buttons
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
        open_action.triggered.connect(self.load_epub_by_dialog)
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

    def load_epub_by_path(self, epub_path):
        if not epub_path:
            logger.info("No file selected")
            return

        eBook = EBook(epub_path)
        self._ebook_list.append(eBook)
        now_chapter = eBook.get_chapter()
        self._tab_widget.addTab(EBookTabWidget(now_chapter), now_chapter.title)
        self._tab_widget.setCurrentIndex(self._tab_widget.count() - 1)

        self._toc_list.clear()
        for chapter in eBook.toc:
            self._toc_list.addItem(chapter)

        self._toc_list.setCurrentRow(eBook._now_toc_idx)
        self.setWindowTitle(f"QEpuber - {eBook.book_name}")

    def load_epub_by_dialog(self):
        epub_path, _ = qtw.QFileDialog.getOpenFileName(
            self, "Open EPUB", "", "EPUB Files (*.epub)")
        self.load_epub_by_path(epub_path)

    def next_chapter(self):
        current_EBookTabWidget: EBookTabWidget = self._tab_widget.currentWidget()
        current_idx = self._tab_widget.currentIndex()
        eBook = self._ebook_list[current_idx]
        next_chapter = eBook.next_chapter()
        current_EBookTabWidget.load_chapter(next_chapter)
        self._toc_list.setCurrentRow(eBook._now_toc_idx)
        self._tab_widget.setTabText(current_idx, next_chapter.title)

    def prev_chapter(self):
        current_EBookTabWidget: EBookTabWidget = self._tab_widget.currentWidget()
        current_idx = self._tab_widget.currentIndex()
        eBook = self._ebook_list[current_idx]
        prev_chapter = eBook.prev_chapter()
        current_EBookTabWidget.load_chapter(prev_chapter)
        self._toc_list.setCurrentRow(eBook._now_toc_idx)
        self._tab_widget.setTabText(current_idx, prev_chapter.title)

    def change_to_index_page(self):
        pass

    def on_tab_widget_current_changed(self):
        current_idx = self._tab_widget.currentIndex()
        eBook = self._ebook_list[current_idx]
        self._toc_list.clear()
        for chapter in eBook.toc:
            self._toc_list.addItem(chapter)
        self._toc_list.setCurrentRow(eBook._now_toc_idx)
        self.setWindowTitle(f"QEpuber - {eBook.book_name}")
