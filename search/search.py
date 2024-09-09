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
from search.prompt import *
from locate import Locator
from cache import cache_handler
from utils import save_to_json, LanguageParser, PictureParser, LCA, LCS
from functools import reduce
import time

catagory_lock = Lock()

class SearchEngine: 
    """搜索引擎类"""
    def __init__(self, driver: WebDriver | None = None, url: str = ''):
        self.driver: WebDriver = driver or webdriver.Chrome() # 主浏览器
        self.cache_handler = cache_handler # 缓存管理器
        self.catagory = None # 当前搜索的类别
        self.locator = Locator(self.driver) # 元素定位器
        # 元素解析器
        self.result_url_parser = LanguageParser(get_res_urls_parser_prompt())
        self.introduction_parser = LanguageParser(get_intro_parser_prompt())
        self.result_locator_parser = LanguageParser(get_result_locator_prompt())
        self.need_login_parser = PictureParser(get_need_login_prompt())
        self.info_classifier = PictureParser(get_website_category_prompt())
        self.init_url = url
    
    # 获取对应网址的HTML
    def get_html(self, url):
        try:
            html = self.driver.page_source
            return html
        except Exception as e:
            raise RuntimeError(f"Failed to get URL: {url}\n{e}")
        
    # 关闭驱动器
    def close(self):
        self.driver.quit()
    
    # 关闭当前所有标签页并且打开一个新标签页
    def open_new_tab(self):
        self.driver.execute_script("window.open('about:blank', '_blank');")
        new_tab = self.driver.window_handles[-1]
        self.driver.switch_to.window(new_tab)
        for tab in self.driver.window_handles[:-1]:
            self.driver.switch_to.window(tab)
            self.driver.close()
        self.driver.switch_to.window(new_tab)
    
    def need_login_or_not(self, url, keyword):
        self.driver.save_screenshot(f'./tmp/{keyword}_login.png')
        response = self.need_login_parser.parse(f'./tmp/{keyword}_login.png', url=url)
        return True if response == 'True' else False
    
    def classify_website(self, url, keyword):
        def _get_classification():
            catagories: dict = self.cache_handler.get_data(url, 'catagories', {})
            catagory_lock.acquire()
            if keyword not in catagories:
                img64 = self.driver.get_screenshot_as_base64()
                self.catagory = self.info_classifier.parse(img=img64, path_or_code=False, url=url)
                self.cache_handler.set_data(url, 'catagories', {keyword: self.catagory})
            else:
                self.catagory = catagories.get(keyword)
            catagory_lock.release()
        Thread(target=_get_classification).start()

    def save_ancestor(self, url, tags: list[WebElement]):
        print(f"Saving ancestor for {self.init_url}")
        ancestors: list[WebElement] = []
        for i in range(len(tags)):
            ancestors.append(LCA(tags[i], tags[i-1]))
        if len(ancestors) == 0:
            return
        most_possible_ancestor = Counter(ancestors).most_common(1)[0][0]
        msa_html = most_possible_ancestor.get_attribute('outerHTML')
        most_possible_ancestor_locator = None
        while True: 
            most_possible_ancestor_locator = self.result_locator_parser.parse(f"target: {url}\ncontent: {msa_html}", clear_history=True)
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
            self.cache_handler.set_data(self.init_url, 'results', results)
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
        results = self.cache_handler.get_data(self.init_url, 'search_results')
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
        # urls = list(map(lambda link: link.get_attribute('href'), relavent_links))
        return urls
    
    # 在搜索后的界面中找到结果界面
    def find_best_results_page(self, keyword: str, url: str) -> list:
        root = urlparse(url).scheme + "://" + urlparse(url).netloc
        all_hrefs = self.handle_possible_links(url, keyword)
        hrefs = self.result_url_parser.parse(f"target: {keyword}\nlist: {all_hrefs}").split('|')
        res_urls = list(map(lambda href: href if href.startswith('http') else root + '/' + href, hrefs))
        return res_urls
    
    # 在url界面中找到简介
    def find_introduction(self, keyword, html, hint = ''):
        soup = BeautifulSoup(html, 'html.parser')
        body: Tag = soup.find('body')
        raw = body.get_text()
        content = re.sub(r'\s+', ' ', raw)[:10000]
        raw = self.introduction_parser.parse(f"keyword: {keyword}\ncontent: {content}", clear_history=True)
        intro_text = self.introduction_parser.parse(f"keyword: {keyword}\nhint: {hint}\ncontent: {raw}", clear_history=True)
        return intro_text 
    
    def type_in(self, url, keyword):
        search_box = self.locator.locate(self.init_url, url, "searchbox")
        # 往输入框中输入关键词并提交
        search_box.clear()
        search_box.send_keys(keyword)
        pre_window_num = len(self.driver.window_handles)
        search_box.send_keys(Keys.ENTER) # submit()模拟按下回车键
        time.sleep(1.5)
        new_window_num = len(self.driver.window_handles)
        if new_window_num == pre_window_num + 1 :
            self.driver.switch_to.window(self.driver.window_handles[-1])
    
    def judge_login(self, url, keyword):
        need_login = self.cache_handler.get_data(self.init_url, "need_login")
        go_on = True
        should_write = False
        if need_login is None:
            should_write = True
            need_login = self.need_login_or_not(url, keyword)
        if need_login:
            login_result = input("请登录您的账户，并且登录之后输入[y/n]表示您是否登陆成功\n如果您认为当前界面无需登录，请输入[q]\n")
            if login_result == "y":
                go_on = False
            if login_result == "n":
                raise RuntimeError(f"User failed to login in {url}")
            if login_result == "q":
                need_login = False
        if should_write:
            self.cache_handler.set_data(self.init_url, "need_login", need_login)
        return go_on
    
    def result_parse(self, url, keyword):
        self.classify_website(self.init_url, keyword)
        result_urls = self.find_best_results_page(keyword, url)
        intro = ''
        for result_url in result_urls:
            print(f"Handling {result_url}")
            self.driver.get(result_url)
            html = self.get_html(result_url)
            source = f" 来源：{result_url}\n"
            intro += self.find_introduction(keyword, html, intro) + source
        introduction = self.introduction_parser.parse(f"keyword: {keyword}\ncontent: {intro}", clear_history=True)
        return result_urls, introduction
    
    # 查询操作
    def search(self, url, keyword):
        self.driver.get(url)
        need_judge_login = True
        while True:
            self.type_in(url, keyword)
            new_url = self.driver.current_url
            if not need_judge_login: break
            go_on = self.judge_login(new_url, keyword)
            if go_on: break
            need_judge_login = False
        result_urls, introduction = self.result_parse(new_url, keyword)
        return result_urls, introduction
    
    # 在很多url中搜索keyword
    def run(self, urls, keyword):
        if not os.path.exists('./tmp'):
            os.mkdir('./tmp')
        search_results = {"keyword": keyword}
        for url in urls:
            self.open_new_tab()
            try:
                self.init_url = url
                ref_urls, introduction = self.search(url, keyword)
            except Exception as e:
                raise e
            search_results[url] = {"introduction": introduction, "reference": ref_urls}
        print(f"Data saved to ./data/{keyword}.json")
        save_to_json(search_results, f"./data/{keyword}.json")
        self.close()
        shutil.rmtree('./tmp')