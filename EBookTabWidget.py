from Ebook import EBook, EBookChapter
from commom_import import *


class EBookTabCloseButton(qtw.QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(qtc.QSize(20, 20))  # 稍微增大按钮尺寸
        self.hovered = False  # 记录鼠标悬停状态
        self.setObjectName("tabCloseButton")  # 设置对象名称以应用样式
        self.setIcon(qtg.QIcon("./figures/close_icon.svg"))  # 设置图标
        self.setToolTip("关闭标签页")
        self.setFlat(True)  # 扁平样式

    def enterEvent(self, event):
        """鼠标进入按钮时"""
        self.hovered = True
        self.setIcon(qtg.QIcon("./figures/close_icon_hover.svg"))
        self.update()

    def leaveEvent(self, event):
        """鼠标离开按钮时"""
        self.hovered = False
        self.setIcon(qtg.QIcon("./figures/close_icon.svg"))
        self.update()


class EBookTabBar(qtw.QTabBar):
    def __init__(self):
        super().__init__()
        self.setTabsClosable(True)  # 允许关闭按钮
        self.setMovable(True)  # 允许拖拽标签页
        self.setExpanding(False)  # 不自动扩展标签页宽度
        self.setElideMode(qtc.Qt.TextElideMode.ElideRight)  # 文本过长时省略号在右侧
        self.setUsesScrollButtons(True)  # 当标签页过多时显示滚动按钮

    def tabInserted(self, index):
        """在插入标签时自定义关闭按钮"""
        button = EBookTabCloseButton(self)
        button.clicked.connect(self.on_tab_close_requested)
        self.setTabButton(
            index, qtw.QTabBar.ButtonPosition.RightSide, button)  # 右侧放置关闭按钮

    def on_tab_close_requested(self):
        index = self.tabAt(self.sender().pos())
        self.tabCloseRequested.emit(index)


class EBookChapterDisplay(qtw.QTextBrowser):
    def __init__(self, eBook: EBook, parent=None):
        super().__init__(parent)
        self.eBook = eBook
        self.setOpenExternalLinks(True)
        self.setOpenLinks(True)
        self.setAcceptRichText(True)
        self.setContextMenuPolicy(qtc.Qt.ContextMenuPolicy.DefaultContextMenu)
        self.setObjectName("bookDisplay")  # 设置对象名称以应用样式

        # 设置更好的阅读体验
        self.setLineWrapMode(qtw.QTextEdit.LineWrapMode.WidgetWidth)
        self.setVerticalScrollBarPolicy(
            qtc.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(
            qtc.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def load_chapter(self, eBookChapter: EBookChapter):
        local_url = qtc.QUrl.fromLocalFile(eBookChapter.path)
        self.setSource(local_url)
        self.scrollToAnchor(eBookChapter.get_anchor())
        self.setWindowTitle(eBookChapter.title)
        logger.info(
            f"Load chapter: {eBookChapter.title} from anchor: {eBookChapter.anchor}")

    def loadResource(self, type, name):
        """拦截资源加载，动态缩放图片"""
        resource = super().loadResource(type, name)
        if type == qtg.QTextDocument.ResourceType.ImageResource and isinstance(resource, qtg.QPixmap):
            max_width = self.width() * 0.95  # 让图片最大宽度适应 QTextBrowser
            return resource.scaledToWidth(max_width, qtc.Qt.TransformationMode.SmoothTransformation)
        return resource


class EBookTabWidget(qtw.QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setTabBar(EBookTabBar())

    def add_tab(self, eBook: EBook, eBookChapter: EBookChapter):
        tab = EBookChapterDisplay(eBook)
        tab.load_chapter(eBookChapter)
        self.addTab(tab, eBookChapter.title)
        self.setCurrentWidget(tab)

    def close_tab(self, index):
        self.removeTab(index)

    def currentWidget(self) -> EBookChapterDisplay:
        return super().currentWidget()

    def widget(self, index) -> EBookChapterDisplay:
        return super().widget(index)

    def get_opened_books(self):
        return [self.widget(i).eBook for i in range(self.count())]
