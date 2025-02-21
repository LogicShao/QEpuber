import PyQt6.QtWidgets as qtw
import PyQt6.QtGui as qtg
import PyQt6.QtCore as qtc
from logger import logger
from Ebook import EBook
from EBookTabWidget import EBookTabWidget
from Setting import SettingLoader, SettingSaver

index_html_path = "./html/test001.html"


class MainWindow(qtw.QMainWindow):
    _ebook_list: list[EBook] = []

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_last_settings()

    def load_last_settings(self):
        setting_loader = SettingLoader()
        eBooks = setting_loader.get_last_read_ebooks()
        for eBook in eBooks:
            self.load_epub(eBook)
        font = setting_loader.get_last_font()
        for i in range(self._tab_widget.count()):
            cur_widget: EBookTabWidget = self._tab_widget.widget(i)
            cur_widget.setFont(font)
        last_idx = setting_loader.get_last_idx()
        if last_idx is not None:
            self._tab_widget.setCurrentIndex(last_idx)
        logger.info("Last settings loaded")

    def closeEvent(self, event: qtg.QCloseEvent):
        setting_saver = SettingSaver()
        if self._ebook_list:
            setting_saver.add_last_read_ebook(
                self._ebook_list, self._tab_widget.currentIndex())
            setting_saver.add_last_font(
                self._tab_widget.currentWidget().font())
        setting_saver.save()
        logger.info("Settings saved")
        event.accept()

    def setup_ui(self):
        self.setWindowTitle("QEpuber")
        self.setWindowIcon(qtg.QIcon("./figures/book_reader_icon.png"))
        self.setGeometry(100, 100, 800, 600)

        self._central_widget = qtw.QWidget()
        self.setCentralWidget(self._central_widget)

        self._layout = qtw.QVBoxLayout()
        self._central_widget.setLayout(self._layout)

        self._tool_bar = self.make_tool_bar()
        self._layout.addWidget(self._tool_bar)

        splitter = qtw.QSplitter(
            qtc.Qt.Orientation.Horizontal, self._central_widget)

        self._toc_list = qtw.QListWidget()
        self._toc_list.itemClicked.connect(self.load_anchor_by_click_toc)
        splitter.addWidget(self._toc_list)

        self._tab_widget = qtw.QTabWidget()
        self._tab_widget.setTabsClosable(True)
        self._tab_widget.tabCloseRequested.connect(self.remove_tab)
        splitter.addWidget(self._tab_widget)
        self._tab_widget.currentChanged.connect(
            self.on_tab_widget_current_changed)

        splitter.setSizes([200, 600])
        self._layout.addWidget(splitter)

    def remove_tab(self, index):
        self._tab_widget.removeTab(index)
        self._ebook_list.pop(index)

        logger.info(f"Remove tab {index}")

    def load_anchor_by_click_toc(self, item):
        current_idx = self._tab_widget.currentIndex()
        eBook = self._ebook_list[current_idx]
        toc_index = self._toc_list.currentRow()
        eBook._now_toc_idx = toc_index
        current_widget: EBookTabWidget = self._tab_widget.currentWidget()
        current_widget.load_chapter(eBook.get_anchor())
        self._tab_widget.setTabText(current_idx, eBook.get_anchor().title)

    def make_tool_bar(self):
        # TODO: Add more buttons
        tool_bar = qtw.QToolBar()

        # create file menu and add open and exit actions
        file_menu = qtw.QMenu()
        open_action = file_menu.addAction("Open EPUB")
        open_action.triggered.connect(self.load_epub_by_dialog)
        open_action.setShortcut("Ctrl+O")
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut("Ctrl+Q")

        file_button = qtw.QToolButton()
        file_button.setText("File")
        file_button.setMenu(file_menu)
        file_button.setPopupMode(
            qtw.QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        tool_bar.addWidget(file_button)

        # create view menu and add next and previous actions
        view_menu = qtw.QMenu()
        next_action = view_menu.addAction("Next Chapter")
        next_action.triggered.connect(self.next_chapter)
        next_action.setShortcut("]")
        prev_action = view_menu.addAction("Previous Chapter")
        prev_action.triggered.connect(self.prev_chapter)
        prev_action.setShortcut("[")
        select_font_action = view_menu.addAction("Font")
        select_font_action.triggered.connect(self.update_font_for_tabs)
        set_font_color_action = view_menu.addAction("Font Color")
        set_font_color_action.triggered.connect(self.update_tab_text_color)
        set_theme_color_action = view_menu.addAction("Theme Color")
        set_theme_color_action.triggered.connect(self.update_theme_color)

        view_button = qtw.QToolButton()
        view_button.setText("View")
        view_button.setMenu(view_menu)
        view_button.setPopupMode(
            qtw.QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        tool_bar.addWidget(view_button)

        prev_button = qtw.QToolButton()
        prev_button.setIcon(qtg.QIcon("./figures/left_arrow.svg"))
        prev_button.clicked.connect(self.prev_chapter)

        next_button = qtw.QToolButton()
        next_button.setIcon(qtg.QIcon("./figures/right_arrow.svg"))
        next_button.clicked.connect(self.next_chapter)

        tool_bar.addWidget(prev_button)
        tool_bar.addWidget(next_button)

        return tool_bar

    def update_theme_color(self):
        dialog = qtw.QColorDialog()
        if dialog.exec() == qtw.QDialog.DialogCode.Rejected:
            logger.info("Color change canceled")
            return
        color = dialog.selectedColor()
        self.setStyleSheet(f"background-color: {color.name()};")
        logger.info(f"Color changed to {color.name()}")
        self.update()

    def update_tab_text_color(self):
        dialog = qtw.QColorDialog()
        if dialog.exec() == qtw.QDialog.DialogCode.Rejected:
            logger.info("Color change canceled")
            return
        color = dialog.selectedColor()
        for i in range(self._tab_widget.count()):
            cur_widget: EBookTabWidget = self._tab_widget.widget(i)
            cur_widget.setTextColor(color)
        logger.info(f"Color changed to {color.name()}")

    def update_font_for_tabs(self):
        dialog = qtw.QFontDialog()
        dialog.setCurrentFont(self._tab_widget.currentWidget().font())
        if dialog.exec() == qtw.QDialog.DialogCode.Rejected:
            logger.info("Font change canceled")
            return
        font = dialog.selectedFont()
        for i in range(self._tab_widget.count()):
            cur_widget: EBookTabWidget = self._tab_widget.widget(i)
            cur_widget.setFont(font)
        logger.info(f"Font changed to {font.family()} {font.pointSize()}pt")

    def load_epub(self, eBook: EBook):
        self._ebook_list.append(eBook)
        now_anchor = eBook.get_anchor()
        tab_widget = EBookTabWidget(eBook)
        self._tab_widget.addTab(tab_widget, now_anchor.title)
        tab_widget.load_chapter(now_anchor)
        self._tab_widget.setCurrentIndex(self._tab_widget.count() - 1)

        self._toc_list.clear()
        for chapter in eBook.toc:
            self._toc_list.addItem(chapter)
        self._toc_list.setCurrentRow(eBook._now_toc_idx)
        self.setWindowTitle(f"QEpuber - {eBook.book_name}")

    def load_epub_by_path(self, epub_path):
        if not epub_path:
            logger.info("No file selected")
            return

        eBook = EBook(epub_path)
        self.load_epub(eBook)

    def load_epub_by_dialog(self):
        epub_path, _ = qtw.QFileDialog.getOpenFileName(
            self, "Open EPUB", "", "EPUB Files (*.epub)")
        self.load_epub_by_path(epub_path)

    def next_chapter(self):
        if len(self._ebook_list) == 0:
            qtw.QMessageBox.warning(
                self, "Warning", "No eBook loaded", qtw.QMessageBox.StandardButton.Ok)
            return
        current_EBookTabWidget: EBookTabWidget = self._tab_widget.currentWidget()
        current_idx = self._tab_widget.currentIndex()
        eBook = self._ebook_list[current_idx]
        next_chapter = eBook.next_anchor()
        current_EBookTabWidget.load_chapter(next_chapter)
        self._toc_list.setCurrentRow(eBook._now_toc_idx)
        self._tab_widget.setTabText(current_idx, next_chapter.title)

    def prev_chapter(self):
        if len(self._ebook_list) == 0:
            qtw.QMessageBox.warning(
                self, "Warning", "No eBook loaded", qtw.QMessageBox.StandardButton.Ok)
            return
        current_EBookTabWidget: EBookTabWidget = self._tab_widget.currentWidget()
        current_idx = self._tab_widget.currentIndex()
        eBook = self._ebook_list[current_idx]
        prev_chapter = eBook.prev_anchor()
        current_EBookTabWidget.load_chapter(prev_chapter)
        self._toc_list.setCurrentRow(eBook._now_toc_idx)
        self._tab_widget.setTabText(current_idx, prev_chapter.title)

    def on_tab_widget_current_changed(self):
        current_idx = self._tab_widget.currentIndex()
        eBook = self._ebook_list[current_idx]
        self._toc_list.clear()
        for chapter in eBook.toc:
            self._toc_list.addItem(chapter)
        self._toc_list.setCurrentRow(eBook._now_toc_idx)
        self.setWindowTitle(f"QEpuber - {eBook.book_name}")
