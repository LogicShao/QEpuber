from ebooklib import epub
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import warnings
import os
import zipfile


def extract_chapters(epub_path):
    """ 解析 EPUB 并提取所有章节 """
    book = epub.read_epub(epub_path, options={'ignore_ncx': False})
    chapters = []
    for item in book.get_items():
        if item.media_type == "application/xhtml+xml":  # 仅处理 HTML 章节
            soup = BeautifulSoup(item.get_content(), "html.parser")
            # 获取章节名和 HTML 内容
            chapters.append((item.get_name(), soup.prettify()))
    return chapters


def extract_epub(epub_path, output_folder):
    """解压 EPUB 到指定文件夹"""
    if os.path.exists(output_folder):
        return output_folder
    os.makedirs(output_folder)
    with zipfile.ZipFile(epub_path, 'r') as zip_ref:
        zip_ref.extractall(output_folder)
    return output_folder


def get_opf_path(cache_folder):
    """获取 content.opf 的路径"""
    container_path = os.path.join(cache_folder, "META-INF", "container.xml")
    tree = ET.parse(container_path)
    root = tree.getroot()
    # 寻找 rootfile 位置
    namespace = {'n': 'urn:oasis:names:tc:opendocument:xmlns:container'}
    opf_path = root.find("n:rootfiles/n:rootfile",
                         namespace).attrib['full-path']
    return os.path.join(cache_folder, opf_path)


def parse_chapters(cache_folder):
    """解析 EPUB 章节并返回章节列表"""
    opf_path = get_opf_path(cache_folder)
    tree = ET.parse(opf_path)
    root = tree.getroot()
    namespace = {'n': 'http://www.idpf.org/2007/opf'}
    manifest = root.find("n:manifest", namespace)
    spine = root.find("n:spine", namespace)
    # 获取所有 HTML 章节
    chapters = []
    for itemref in spine.findall("n:itemref", namespace):
        item_id = itemref.attrib['idref']
        item = manifest.find(f"n:item[@id='{item_id}']", namespace)
        if item is not None and "html" in item.attrib['href']:
            chapter_path = os.path.join(
                os.path.dirname(opf_path), item.attrib['href'])
            chapters.append(chapter_path)
    return chapters


def find_toc_path(cache_folder):
    """查找 toc.ncx 文件路径"""
    # 解析 content.opf
    opf_path = get_opf_path(cache_folder)
    tree = ET.parse(opf_path)
    root = tree.getroot()
    ns = {"opf": "http://www.idpf.org/2007/opf"}

    # 先找 EPUB 2.0 的 toc.ncx
    item = root.find(
        ".//opf:manifest/opf:item[@media-type='application/x-dtbncx+xml']", ns)
    if item is not None:
        return os.path.join(os.path.dirname(opf_path), item.attrib["href"])

    # 再找 EPUB 3.0 的 nav.xhtml
    item = root.find(".//opf:manifest/opf:item[@properties='nav']", ns)
    if item is not None:
        return os.path.join(os.path.dirname(opf_path), item.attrib["href"])

    print("未找到目录文件")
    return None


def load_epub(epub_file):
    """加载 EPUB 并返回缓存目录中的 HTML 章节文件路径"""
    epub_id = os.path.splitext(os.path.basename(epub_file))[0]
    cache_folder = os.path.join("eBookCache", epub_id)
    # 解压 EPUB
    extract_epub(epub_file, cache_folder)
    # 获取章节 HTML 文件列表
    chapter_path_list = parse_chapters(cache_folder)
    return cache_folder, chapter_path_list  # 返回缓存目录和 HTML 文件路径列表


def parse_toc(epub_folder):
    """解析 toc.ncx，返回目录项列表（[标题, ...]）"""
    toc_path = find_toc_path(epub_folder)
    if toc_path is None or not os.path.exists(toc_path):
        return []
    tree = ET.parse(toc_path)
    root = tree.getroot()
    ns = {"ncx": "http://www.daisy.org/z3986/2005/ncx/"}
    toc = []
    for nav_point in root.findall(".//ncx:navPoint", ns):
        title = nav_point.find(".//ncx:text", ns).text
        toc.append(title)
    return toc


warnings.filterwarnings("ignore", category=UserWarning, module="ebooklib.epub")
warnings.filterwarnings(
    "ignore", category=FutureWarning, module="ebooklib.epub")

__all__ = ["load_epub", "parse_toc"]

if __name__ == "__main__":
    # 示例：解析 EPUB 并打印章节
    epub_path = "eBooks\\小逻辑 (黑格尔, 贺麟) (Z-Library).epub"
    ebook_folder, chapter_path_list = load_epub(epub_path)
    print(f"eBook cache folder: {ebook_folder}")
    toc = parse_toc(ebook_folder)
    for i, chapter in enumerate(toc):
        print(f"Chapter {i + 1}: {chapter}")
