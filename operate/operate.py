import re
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString

MAX_HTML_LEN = 10000
BALCK_TAG = ['script', 'style']
IMG_BLACK_TAG = ['script', 'style', 'img', 'svg', 'symbol']

class HtmlOperator:
    def __init__(self, url: str = None, bs: BeautifulSoup = None):
        self.bs = bs
        self.url = url
    
    def slice_html(self, html: str, general_or_img: bool = True) -> list[BeautifulSoup]:
        html = re.sub(r'<!--(.*?)-->', '', html, flags=re.DOTALL)
        if html == '\n':
            return []
        soup = BeautifulSoup(html, 'html.parser')
        if len(html) < MAX_HTML_LEN:
            return [soup]
        root: Tag = soup.find(True)
        if not root:
            return None
        black = BALCK_TAG if general_or_img else IMG_BLACK_TAG
        res = []
        part = ''
        for child in root.children:
            if child.name in black:
                child.decompose()
                continue
            if isinstance(child, NavigableString):
                part += str(child)
                continue
            if len(child.prettify()) > MAX_HTML_LEN:
                res.extend(self.slice_html(part, general_or_img))
                res.extend(self.slice_html(child.prettify(), general_or_img))
                part = ''
            elif len(part + child.prettify()) > MAX_HTML_LEN:
                res.extend(self.slice_html(part, general_or_img))
                part = child.prettify()
            else:
                part += child.prettify()
        if part != '':
            res.extend(self.slice_html(part, general_or_img))
        return res
            