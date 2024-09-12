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
from bs4.element import Tag
from open.prompt import *
from locate import Locator
from utils import LCA, LCS
from cache import cache_handler
from utils import save_to_json, LanguageParser, PictureParser
from functools import reduce
import time

# 给定一段文本描述，打开相应的网页
class Opener:
    def __init__(self, driver: WebDriver | None = None):
        self.driver = driver or webdriver.Chrome()
        self.locator = Locator(self.driver)
        self.cache_handler = cache_handler
        self.url_getter = LanguageParser(get_urls_prompt())
        self.result_locator_parser = LanguageParser(get_result_locator_prompt())
        self.url_judger = PictureParser(get_url_judger_prompt())
        self.data_url = ''
    
    def save_ancestor(self, url, tags: list[WebElement]):
        print(f"Saving ancestor for {self.data_url}")
        ancestors: list[WebElement] = []
        for i in range(len(tags)):
            ancestors.append(LCA(tags[i], tags[i-1]))
        if len(ancestors) == 0:
            return
        most_possible_ancestor = Counter(ancestors).most_common(1)[0][0]
        msa_html = most_possible_ancestor.get_attribute('outerHTML')
        most_possible_ancestor_locator = None
        while True: 
            try: 
                most_possible_ancestor_locator = self.result_locator_parser.parse(f"target: {url}\ncontent: {msa_html}", clear_history=True)
            except:
                break
            if not most_possible_ancestor_locator.startswith('Not'):
                break
            try:
                most_possible_ancestor = most_possible_ancestor.find_element(By.XPATH, '..')
                msa_html = most_possible_ancestor.get_attribute('outerHTML')
            except:
                break
        try:
            trimmed_str = most_possible_ancestor_locator.strip("() ")
            parts = [part.strip() for part in trimmed_str.split(",")]
            if not parts[0].startswith('By.'):
                return
            find_method = eval(parts[0])
            final_tag = parts[1].strip("'").strip("\"")
            results = [find_method, final_tag]
            self.cache_handler.set_data(self.data_url, 'seacher_results', results)
            print(f"Successfully save results list in {url} with {results}")
        except:
            print(f"Failed to save wrapper of searching results list in {url}")
    
    def handle_possible_links(self, url, keyword) -> list:
        def get_relavent(keyword: str, title) -> bool:
            if title == '':
                return False
            words = keyword.split(' ')
            lcs = reduce(lambda x, word: x + LCS(word, title), words, 0)
            if lcs >= len(keyword) * 0.5:
                return True
            return False
        urls = []
        should_lca = False
        results = self.cache_handler.get_data(self.data_url, keyword)
        if results is not None:
            urls_wrapper: WebElement = self.locator.try_locate(url, results, 'urls_wrapper')
            links = urls_wrapper.find_elements(by=By.TAG_NAME, value='a')
        else:
            links = self.driver.find_elements(by=By.TAG_NAME, value='a')
            should_lca = True
        relavent_links = list(filter(lambda link: get_relavent(keyword, link.find_element(By.XPATH, '..').text), links))
        # 找到最合适的LCA存起来
        if should_lca:
            self.save_ancestor(url, relavent_links)
        urls = list(map(lambda link: link.get_attribute('href') + link.text, relavent_links))
        return urls
    
    def find_urls(self, url: str, description: dict):
        def url_formater(url: str, next_url: str) -> str:
            root = urlparse(url).scheme + "://" + urlparse(url).netloc
            if next_url.startswith('http'):
                return next_url
            if next_url.startswith('://'):
                return urlparse(url).scheme + next_url
            if next_url.startswith('//'):
                return urlparse(url).scheme + ':' + next_url
            if next_url.startswith('/'):
                return root + next_url
            return root + '/' + next_url
        page_info = description.get('page_info', None)
        keyword = description.get('keyword', '')
        all_hrefs = self.handle_possible_links(url, page_info or keyword)
        hrefs = self.url_getter.parse(f"url: {url}\ndescription: {description}\nlist: {all_hrefs}").split('|')
        res_urls = list(map(lambda href: url_formater(url, href), hrefs))
        return res_urls
    
    # data_url是保存的缓存的url，一般是根url
    def open_page(self, url: str, description: dict):
        self.data_url = url
        urls = self.find_urls(url, description)
        pattern = r"\[(Yes)\]\. (.*)"
        for url in urls:
            self.driver.get(url)
            time.sleep(1)
            # TODO 等url加载好
            img64 = self.driver.get_screenshot_as_base64()
            resp = self.url_judger.parse(img64, False, description=description)
            if re.match(pattern, resp):
                return url
            