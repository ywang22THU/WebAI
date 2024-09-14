import re
import os
import shutil
from threading import Thread, Lock
from collections import Counter
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString
from search.prompt import *
from locate import Locator
from cache import cache_handler
from utils import save_to_json, LanguageParser, PictureParser, LCA, LCS
from functools import reduce
import time

MAX_HTML_LEN = 10000

class HtmlOperator:
    def __init__(self, url: str, bs: BeautifulSoup = None):
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
            