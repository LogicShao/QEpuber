import PyQt6.QtWidgets as qtw
import PyQt6.QtGui as qtg
import PyQt6.QtCore as qtc
from logger import logger
from Ebook import EBook, EBookChapter


class EBookTabWidget(qtw.QTextBrowser):
    def __init__(self, eBook: EBook, parent=None):
        super().__init__(parent)
        self.eBook = eBook
        self.setOpenExternalLinks(False)
        self.setOpenLinks(False)
        self.setAcceptRichText(True)
        self.setOpenExternalLinks(False)
        self.setOpenLinks(False)
        self.setAcceptRichText(True)
        self.setReadOnly(True)
        self.setContextMenuPolicy(qtc.Qt.ContextMenuPolicy.NoContextMenu)

    def load_chapter(self, eBookChapter: EBookChapter):
        local_url = qtc.QUrl.fromLocalFile(eBookChapter.path)
        self.setSource(local_url)
        self.scrollToAnchor(eBookChapter.get_anchor())
        logger.debug(f"Load chapter: {eBookChapter.title}")
