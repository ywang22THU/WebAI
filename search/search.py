import re
import os
import shutil
from threading import Thread, Lock
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import WebDriver
from bs4 import BeautifulSoup
from bs4.element import Tag
from search.prompt import *
from locate import Locator
from open import Opener
from cache import cache_handler
from utils import save_to_json, LanguageParser, PictureParser, save_to_html
from concurrent.futures import ThreadPoolExecutor
import requests
import time

catagory_lock = Lock()
tab_lock = Lock()
intro_lock = Lock()

class SearchEngine: 
    """搜索引擎类"""
    def __init__(self, driver: WebDriver | None = None, url: str = ''):
        self.driver: WebDriver = driver or webdriver.Chrome() # 主浏览器
        self.cache_handler = cache_handler # 缓存管理器
        self.catagory = None # 当前搜索的类别
        self.locator = Locator(self.driver) # 元素定位器
        self.opener = Opener(self.driver) # 网页打开器
        self.text_input_box = None
        self.send_button = None
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
        if not os.path.exists(f'./tmp'):
            os.mkdir(f'./tmp')
        self.driver.save_screenshot(f'./tmp/{keyword}_login.png')
        response = self.need_login_parser.parse(f'./tmp/{keyword}_login.png', path_or_code=True, url=url)
        os.remove(f'./tmp/{keyword}_login.png')
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
    
    # 在url界面中找到简介
    def find_introduction(self, url, keyword, html, hints = []):
        soup = BeautifulSoup(html, 'html.parser')
        body: Tag = soup.find('body')
        raw = body.get_text()
        need_login = self.cache_handler.get_data(self.init_url, "need_login")
        if need_login == False:
            resp = requests.get(f"https://r.jina.ai/{url}")
            if resp.status_code != 200:
                content = re.sub(r'\s+', ' ', raw)[:10000]
            else:
                pattern = r'\[(.*?)\]\(.*?\)'
                content = re.sub(pattern, r'\1', raw)[:10000]
        else:
            content = re.sub(r'\s+', ' ', raw)[:10000]
        hint = '\n'.join(hints)
        raw = self.introduction_parser.parse(f"keyword: {keyword}\ncontent: {content}", clear_history=True)
        intro_text = self.introduction_parser.parse(f"keyword: {keyword}\nhint: {hint}\ncontent: {raw}", clear_history=True)
        return intro_text 
    
    def type_in(self, url, keyword):
        if not self.text_input_box:
            self.text_input_box = self.locator.locate(self.init_url, url, "searchbox")
        if not self.send_button:
            self.send_button = self.locator.locate(self.init_url, url, "search_button")
        # 往输入框中输入关键词并提交
        self.text_input_box.send_keys(Keys.CONTROL, 'a')
        self.text_input_box.send_keys(Keys.DELETE)
        self.text_input_box.send_keys(keyword)
        pre_window_num = len(self.driver.window_handles)
        self.send_button.click()
        # TODO 这里需要判断一次enter够不够
        # search_box.send_keys(Keys)
        time.sleep(1.5)
        new_window_num = len(self.driver.window_handles)
        if new_window_num > pre_window_num :
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
        result_urls = self.opener.find_urls(url, {'keyword': keyword})
        intro = []
        def _parse_one_url(result_url, keyword, intro: list):
            tab_lock.acquire()
            print(f"Handling {result_url}")
            self.driver.get(result_url)
            html = self.get_html(result_url)
            tab_lock.release()
            source = f" 来源：{result_url}\n"
            one_intro = self.find_introduction(result_url, keyword, html, intro) + source
            intro_lock.acquire()
            intro.append(one_intro) # 使用列表保证能够正常修改
            intro_lock.release()
        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(lambda result_url: _parse_one_url(result_url, keyword, intro), result_urls)
        intro_lock.acquire()
        introduction = self.introduction_parser.parse(f"keyword: {keyword}\ntype: {self.catagory}\ncontent: {'\n'.join(intro)}", clear_history=True)
        intro_lock.release()
        return result_urls, introduction
    
    # 查询操作
    def search(self, url, keyword):
        self.driver.get(url)
        self.opener.data_url = url
        need_judge_login = True
        while True:
            self.type_in(url, keyword)
            new_url = self.driver.current_url
            if not need_judge_login: break
            go_on = self.judge_login(new_url, keyword)
            if go_on: break
            need_judge_login = False
        self.classify_website(self.init_url, keyword)
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
        
    def html_generate(self, urls, keywords):
        if not os.path.exists('./htmls'):
            os.mkdir('./htmls')
        for url in urls:
            self.init_url = url.strip('/')
            self.open_new_tab()
            self.driver.get(url)
            self.opener.data_url = url
            need_judge_login = True
            url_info = urlparse(url).netloc
            save_to_html(self.driver.page_source, f"./htmls/{url_info}.html")
            for keyword in keywords:
                self.driver.switch_to.window(self.driver.window_handles[0])
                print(f"Generating html for {url} with keyword {keyword}")
                while True:
                    self.type_in(url, keyword)
                    new_url = self.driver.current_url
                    if not need_judge_login: break
                    go_on = self.judge_login(new_url, keyword)
                    if go_on: break
                    need_judge_login = False
                save_to_html(self.driver.page_source, f"./htmls/{url_info}_{keyword}.html")