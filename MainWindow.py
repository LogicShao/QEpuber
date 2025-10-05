from commom_import import *
from Ebook import EBook
from EBookTabWidget import EBookChapterDisplay, EBookTabWidget
from Setting import SettingLoader, SettingSaver
from EBookTocDocker import EBookTocDocker
from ThemeManager import ThemeManager, Theme

index_html_path = "./html/test001.html"


class MainWindow(qtw.QMainWindow):
    def __init__(self, theme_manager: ThemeManager):
        super().__init__()
        self.theme_manager = theme_manager
        self.opened_ebooks_path: set[str] = set()
        self.setup_ui()
        self.load_last_settings()

    def center_window(self):
        """将窗口居中显示"""
        screen = qtw.QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())

    def load_last_settings(self):
        setting_loader = SettingLoader()
        eBooks = setting_loader.get_last_read_ebooks()
        for eBook in eBooks:
            self.load_epub(eBook)
        font = setting_loader.get_last_font()
        for i in range(self._tab_widget.count()):
            cur_widget: EBookChapterDisplay = self._tab_widget.widget(i)
            cur_widget.setFont(font)
        last_idx = setting_loader.get_last_idx()
        if last_idx is not None:
            self._tab_widget.setCurrentIndex(last_idx)
        logger.info("Last settings loaded")

    def closeEvent(self, event: qtg.QCloseEvent):
        setting_saver = SettingSaver()
        if self._tab_widget.count() > 0:
            ebook_list = self._tab_widget.get_opened_books()
            setting_saver.add_last_read_ebook(
                ebook_list, self._tab_widget.currentIndex())
            setting_saver.add_last_font(
                self._tab_widget.currentWidget().font())
            setting_saver.add_opened_ebooks_path(self.opened_ebooks_path)
        setting_saver.save()
        logger.info("Settings saved")
        event.accept()

    def setup_ui(self):
        self.setWindowTitle("QEpuber - 现代电子书阅读器")
        self.setWindowIcon(qtg.QIcon("./figures/book_reader_icon.png"))
        # 设置更大的默认窗口尺寸和居中位置
        self.resize(1200, 800)
        self.center_window()
        # 设置最小窗口尺寸
        self.setMinimumSize(800, 600)

        self._central_widget = qtw.QWidget()
        self.setCentralWidget(self._central_widget)

        self._layout = qtw.QVBoxLayout()
        # 设置布局边距和间距
        self._layout.setContentsMargins(8, 8, 8, 8)
        self._layout.setSpacing(6)
        self._central_widget.setLayout(self._layout)

        # 创建工具栏
        toolbar = self.make_tool_bar()
        toolbar.setObjectName("mainToolbar")
        self.addToolBar(qtc.Qt.ToolBarArea.LeftToolBarArea, toolbar)

        # 主分割器
        splitter = qtw.QSplitter(
            qtc.Qt.Orientation.Horizontal, self._central_widget)
        splitter.setObjectName("mainSplitter")
        splitter.setHandleWidth(4)

        # 左侧面板分割器
        left_splitter = qtw.QSplitter(
            qtc.Qt.Orientation.Vertical, self._central_widget)
        left_splitter.setObjectName("leftSplitter")
        left_splitter.setHandleWidth(3)

        # TOC列表
        self._toc_list = qtw.QListWidget()
        self._toc_list.setObjectName("tocList")
        self._toc_list.itemClicked.connect(self.load_anchor_by_click_toc)

        # 创建TOC容器以添加标题
        toc_container = qtw.QWidget()
        toc_layout = qtw.QVBoxLayout(toc_container)
        toc_layout.setContentsMargins(4, 4, 4, 4)
        toc_layout.setSpacing(2)

        toc_label = qtw.QLabel("目录")
        toc_label.setObjectName("tocLabel")
        toc_layout.addWidget(toc_label)
        toc_layout.addWidget(self._toc_list)

        left_splitter.addWidget(toc_container)
        left_splitter.addWidget(EBookTocDocker())
        left_splitter.setSizes([300, 200])
        splitter.addWidget(left_splitter)

        # 右侧标签页
        self._tab_widget = EBookTabWidget()
        self._tab_widget.setObjectName("bookTabWidget")
        splitter.addWidget(self._tab_widget)
        self._tab_widget.currentChanged.connect(
            self.on_tab_widget_current_changed)
        self._tab_widget.tabCloseRequested.connect(self.remove_tab)

        # 设置分割器比例
        splitter.setSizes([300, 900])
        self._layout.addWidget(splitter)

        # 添加状态栏
        self.statusBar().showMessage("就绪")
        self.statusBar().setObjectName("statusBar")

    def remove_tab(self, index):
        self._tab_widget.removeTab(index)
        logger.info(f"Remove tab {index}")

        if self._tab_widget.count() == 0:
            self.setWindowTitle("QEpuber")
            self._toc_list.clear()
            return

        if index == self._tab_widget.count():
            index -= 1
        self._tab_widget.setCurrentIndex(index)
        self.on_tab_widget_current_changed()

    def load_anchor_by_click_toc(self, item):
        current_idx = self._tab_widget.currentIndex()
        eBook: EBook = self._tab_widget.currentWidget().eBook
        toc_index = self._toc_list.currentRow()
        eBook._now_toc_idx = toc_index
        current_widget: EBookChapterDisplay = self._tab_widget.currentWidget()
        current_widget.load_chapter(eBook.get_anchor())
        self._tab_widget.setTabText(current_idx, eBook.get_anchor().title)

    def make_tool_bar(self):
        tool_bar = qtw.QToolBar()
        tool_bar.setAllowedAreas(qtc.Qt.ToolBarArea.LeftToolBarArea)
        tool_bar.setMovable(False)
        tool_bar.setToolButtonStyle(qtc.Qt.ToolButtonStyle.ToolButtonIconOnly)
        tool_bar.setIconSize(qtc.QSize(24, 24))
        # 添加一些间距
        tool_bar.setContentsMargins(4, 8, 4, 8)

        # create file menu and add open and exit actions
        file_menu = qtw.QMenu()
        open_action = file_menu.addAction("Open EPUB")
        open_action.triggered.connect(self.load_epub_by_dialog)
        open_action.setShortcut("Ctrl+O")
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut("Ctrl+Q")

        file_button = qtw.QToolButton()
        file_button.setIcon(qtg.QIcon("./figures/file_menu_bar.svg"))
        file_button.setMenu(file_menu)
        file_button.setPopupMode(
            qtw.QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        file_button.setToolTip("文件操作")
        file_button.setObjectName("toolbarButton")
        tool_bar.addWidget(file_button)

        # 添加分隔符
        tool_bar.addSeparator()

        # create view menu and add next and previous actions
        view_menu = qtw.QMenu()
        select_font_action = view_menu.addAction("字体设置")
        select_font_action.triggered.connect(self.update_font_for_tabs)

        # 添加主题子菜单
        theme_menu = view_menu.addMenu("主题")
        theme_actions = {}
        themes = [
            (Theme.LIGHT, "浅色主题"),
            (Theme.DARK, "深色主题"),
            (Theme.MODERN, "现代主题"),
            (Theme.BLUE, "蓝色主题"),
            (Theme.DEFAULT, "默认主题")
        ]

        for theme, name in themes:
            action = theme_actions[theme] = theme_menu.addAction(name)
            action.triggered.connect(
                lambda checked, t=theme: self.change_theme(t))

        view_button = qtw.QToolButton()
        view_button.setIcon(qtg.QIcon("./figures/view_menu_bar.svg"))
        view_button.setMenu(view_menu)
        view_button.setPopupMode(
            qtw.QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        view_button.setToolTip("视图设置")
        view_button.setObjectName("toolbarButton")
        tool_bar.addWidget(view_button)

        # settings menu
        settings_menu = qtw.QMenu()
        save_pre_setting_action = settings_menu.addAction("Save Settings")
        save_pre_setting_action.setCheckable(True)

        settings_button = qtw.QToolButton()
        settings_button.setIcon(qtg.QIcon("./figures/settings_menu_bar.svg"))
        settings_button.setMenu(settings_menu)
        settings_button.setPopupMode(
            qtw.QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        settings_button.setToolTip("设置")
        settings_button.setObjectName("toolbarButton")
        tool_bar.addWidget(settings_button)

        tool_bar.addSeparator()

        # eBook menu
        ebook_menu = qtw.QMenu()
        next_action = ebook_menu.addAction("Next Chapter")
        next_action.triggered.connect(self.next_chapter)
        next_action.setShortcut("]")
        prev_action = ebook_menu.addAction("Previous Chapter")
        prev_action.triggered.connect(self.prev_chapter)
        prev_action.setShortcut("[")

        ebook_button = qtw.QToolButton()
        ebook_button.setIcon(qtg.QIcon("./figures/ebook_menu_bar.svg"))
        ebook_button.setMenu(ebook_menu)
        ebook_button.setPopupMode(
            qtw.QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        ebook_button.setToolTip("电子书操作")
        ebook_button.setObjectName("toolbarButton")
        tool_bar.addWidget(ebook_button)

        tool_bar.addSeparator()

        prev_button = qtw.QToolButton()
        prev_button.setIcon(qtg.QIcon("./figures/up_arrow.svg"))
        prev_button.clicked.connect(self.prev_chapter)
        prev_button.setToolTip("上一章")
        prev_button.setObjectName("navButton")

        next_button = qtw.QToolButton()
        next_button.setIcon(qtg.QIcon("./figures/down_arrow.svg"))
        next_button.clicked.connect(self.next_chapter)
        next_button.setToolTip("下一章")
        next_button.setObjectName("navButton")

        tool_bar.addWidget(prev_button)
        tool_bar.addWidget(next_button)

        return tool_bar

    def update_font_for_tabs(self):
        dialog = qtw.QFontDialog()
        dialog.setCurrentFont(self._tab_widget.currentWidget().font())
        if dialog.exec() == qtw.QDialog.DialogCode.Rejected:
            logger.info("Font change canceled")
            return
        font = dialog.selectedFont()
        for i in range(self._tab_widget.count()):
            cur_widget: EBookChapterDisplay = self._tab_widget.widget(i)
            cur_widget.setFont(font)
        logger.info(f"Font changed to {font.family()} {font.pointSize()}pt")

    def change_theme(self, theme: Theme):
        """切换主题"""
        self.theme_manager.load_theme(theme)
        logger.info(f"Theme changed to {theme.value}")

    def load_epub(self, eBook: EBook):
        now_anchor = eBook.get_anchor()
        tab_widget = EBookChapterDisplay(eBook)
        self._tab_widget.addTab(tab_widget, now_anchor.title)
        tab_widget.load_chapter(now_anchor)
        self._tab_widget.setCurrentIndex(self._tab_widget.count() - 1)

        self._toc_list.clear()
        for chapter in eBook.toc:
            self._toc_list.addItem(chapter)
        self._toc_list.setCurrentRow(eBook._now_toc_idx)
        self.setWindowTitle(f"QEpuber - {eBook.book_name}")

        self.opened_ebooks_path.add(eBook.epub_path)

    def load_epub_by_path(self, epub_path):
        if not epub_path:
            logger.info("No file selected")
            return
        self.load_epub(EBook(epub_path))

    def load_epub_by_dialog(self):
        epub_path, _ = qtw.QFileDialog.getOpenFileName(
            self, "Open EPUB", "", "EPUB Files (*.epub)")
        ebook = EBook(epub_path)
        if ebook in self._tab_widget.get_opened_books():
            self._tab_widget.setCurrentIndex(
                self._tab_widget.get_opened_books().index(ebook))
            return
        self.load_epub(ebook)

    def next_chapter(self):
        if self._tab_widget.count() == 0:
            qtw.QMessageBox.warning(
                self, "Error", "No eBook loaded", qtw.QMessageBox.StandardButton.Ok)
            return
        current_EBookTabWidget: EBookChapterDisplay = self._tab_widget.currentWidget()
        current_idx = self._tab_widget.currentIndex()
        eBook = current_EBookTabWidget.eBook
        next_chapter = eBook.next_anchor()
        current_EBookTabWidget.load_chapter(next_chapter)
        self._toc_list.setCurrentRow(eBook._now_toc_idx)
        self._tab_widget.setTabText(current_idx, next_chapter.title)

    def prev_chapter(self):
        if self._tab_widget.count() == 0:
            qtw.QMessageBox.warning(
                self, "Error", "No eBook loaded", qtw.QMessageBox.StandardButton.Ok)
            return
        current_EBookTabWidget: EBookChapterDisplay = self._tab_widget.currentWidget()
        current_idx = self._tab_widget.currentIndex()
        eBook = current_EBookTabWidget.eBook
        prev_chapter = eBook.prev_anchor()
        current_EBookTabWidget.load_chapter(prev_chapter)
        self._toc_list.setCurrentRow(eBook._now_toc_idx)
        self._tab_widget.setTabText(current_idx, prev_chapter.title)

    def on_tab_widget_current_changed(self):
        if self._tab_widget.count() == 0:
            self.setWindowTitle("QEpuber")
            self._toc_list.clear()
            return
        eBook: EBook = self._tab_widget.currentWidget().eBook
        self._toc_list.clear()
        for chapter in eBook.toc:
            self._toc_list.addItem(chapter)
        self._toc_list.setCurrentRow(eBook._now_toc_idx)
        self.setWindowTitle(f"QEpuber - {eBook.book_name}")
