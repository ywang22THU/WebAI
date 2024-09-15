import re
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString

MAX_HTML_LEN = 10000

class HtmlOperator:
    def __init__(self, url: str = None, bs: BeautifulSoup = None):
        self.bs = bs
        self.url = url
    
    def slice_html(self, html: str) -> list[BeautifulSoup]:
        html = re.sub(r'<!--(.*?)-->', '', html, flags=re.DOTALL)
        if html == '\n':
            return []
        soup = BeautifulSoup(html, 'html.parser')
        if len(html) < MAX_HTML_LEN:
            return [soup]
        root: Tag = soup.find(True)
        if not root:
            return None
        res = []
        part = ''
        for child in root.children:
            if child.name == 'script' or child.name == 'style':
                child.decompose()
                continue
            if isinstance(child, NavigableString):
                part += str(child)
                continue
            if len(child.prettify()) > MAX_HTML_LEN:
                res.extend(self.slice_html(part))
                res.extend(self.slice_html(child.prettify()))
                part = ''
            elif len(part + child.prettify()) > MAX_HTML_LEN:
                res.extend(self.slice_html(part))
                part = child.prettify()
            else:
                part += child.prettify()
        return res
            