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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.webdriver import WebDriver
from bs4 import BeautifulSoup
from bs4.element import Tag
from errors import *
from utils import *
from prompt import *
from locator import LocatorHandler
from GPTParser import GPT4Parser, PictureParser
from functools import reduce
import time

classify_lock = Lock()
get_html_lock = Lock()
intro_parse_lock = Lock()

class SearchEngine: 
    """搜索引擎类"""
    def __init__(self):
        self.init_url = ''
        self.driver: WebDriver = webdriver.Chrome() # 主浏览器
        self.locator_handler = LocatorHandler("locators.json") # 定位器缓存管理器
        self.catagory = None # 当前搜索的类别
        # 元素解析器
        self.input_parser = GPT4Parser(get_input_prompt())
        self.result_url_parser = GPT4Parser(get_res_urls_parser_prompt())
        self.introduction_parser = GPT4Parser(get_intro_parser_prompt())
        self.result_locator_parser = GPT4Parser(get_result_locator_prompt())
        self.need_login_parser = PictureParser(get_need_login_prompt())
        self.info_classifier = PictureParser(get_website_category_prompt())
    
    # 获取对应网址的HTML
    def get_html(self, url):
        try:
            html = self.driver.page_source
            return html
        except Exception as e:
            raise fail_to_get_url(url, e)
        
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
    
    # 尝试通过locator定位组件的element
    def try_locate(self, url, locator, element):
        if not locator:
            return None
        try:
            print(f"Locating {element} in {url} by {locator}")
            aim = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(locator))
            return aim
        except:
            return None

    # 人工处理，添加元素定位器
    # 注意是直接返回的HTML元素
    def handler_mannul(self, url, element: str):
        while True:
            new_locator = input(f"Please enter the {element} locator for the website {url}. The format should be like (By.CSS_SELECTOR, '.t a').")
            aim = self.test_and_add_locator(url, new_locator, element)
            if aim:
                return aim
    
    # GPT添加元素定位器
    # 注意是直接返回的HTML元素
    def handler_llm(self, url, html, element):
        if html is None:
            html = self.get_html(url)
        if type(html) is not str:
            html = html.get_attribute("outerHTML")
        # 多次定位提高定位成功率
        for _ in range(5):
            locator = self.element_locator_gpt(url, html, element)
            aim = self.test_and_add_locator(url, locator, element)
            if aim:
                print(f"Successfully located the {element} by GPT.")
                return aim
        if not aim:
            return None
        
    # 利用GPT找到html中对应的element
    # element都是一些描述性的语句
    def element_locator_gpt(self, url, html, element):
        # 首先预处理html
        soup = BeautifulSoup(html, 'html.parser')
        # 去除所有的脚本
        for script in soup.find_all('script'):
            script.decompose()
        # 找到有可能和搜索相关的几种元素
        forms = soup.find_all('form')
        inputs = soup.find_all('input')
        buttons = soup.find_all('button')
        possible_elements = forms + inputs + buttons
        choices = str(possible_elements)
        # 利用GPT找到尽可能符合要求的元素
        # 根据初始化时的规定，格式应该为(By.CSS_SELECTOR, '.t a')
        response: str = self.input_parser.parse(f"element: {element}\nhtml:{choices}")
        # 将结果进行处理
        trimmed_str = response.strip("() ")
        parts = [part.strip() for part in trimmed_str.split(",")]
        find_method = eval(parts[0])
        final_tag = parts[1].strip("'").strip("\"")
        result_tuple = (find_method, final_tag)
        print(f"Locator for {element} in {url} is {result_tuple}")
        return result_tuple
    
    # 尝试定位
    def test_and_add_locator(self, url, locator, element):
        aim = self.try_locate(url, locator, element)
        if aim:
            self.locator_handler.set_data(url, element, list(locator))
            self.locator_handler.write_to_file()
            return aim
        else:
            return None
        
    def need_login_or_not(self, url, keyword):
        self.driver.save_screenshot(f'./tmp/{keyword}_login.png')
        response = self.need_login_parser.parse(f'./tmp/{keyword}_login.png', url=url)
        return True if response == 'True' else False
    
    def classify_website(self, url, keyword):
        def get_result():
            classify_lock.acquire()
            self.catagory = self.info_classifier.parse(img_path=f'./tmp/{keyword}.png', url=url)
            classify_lock.release()
        self.driver.save_screenshot(f'./tmp/{keyword}.png')
        Thread(target=get_result).start()
    
    def save_ancestor(self, url, tags: list[WebElement]):
        print(f"Saving ancestor for {self.init_url}")
        ancestors: list[WebElement] = []
        for i in range(len(tags)):
            ancestors.append(LCA(tags[i], tags[i-1]))
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
            self.locator_handler.set_data(self.init_url, 'results', results)
            print(f"Successfully save results list in {url} with {results}")
        except:
            print(f"Failed to save wrapper of searching results list in {url}")
    
    def handle_possible_links(self, url, keyword) -> list:
        # 将搜索结果的By保存在locator.json中，防止因为link过多导致API调用爆炸 TODO
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
        results = self.locator_handler.get_data(self.init_url, 'results')
        if results is not None:
            urls_wrapper: WebElement = self.try_locate(url, results, 'urls_wrapper')
            links = urls_wrapper.find_elements(by=By.TAG_NAME, value='a')
        else:
            links = self.driver.find_elements(by=By.TAG_NAME, value='a')
            should_lca = True
        relavent_links = list(filter(lambda link: get_relavent(keyword, link.find_element(By.XPATH, '..').text), links))
        # 找到最合适的LCA存起来
        if should_lca:
            self.save_ancestor(url, relavent_links)
        urls = list(map(lambda link: link.get_attribute('href'), relavent_links))
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
    
    # 查询操作
    def search(self, url, keyword, submitted=False, should_judge_login=True):
        if not submitted:
            self.driver.get(url)
        search_box = None
        box_locator = self.locator_handler.get_data(self.init_url, "searchbox")
        # 先找缓存
        if box_locator:
            # 如果有缓存，则开始在其中找到对应的HTML元素
            print("Find pre-defined search box locator for this website...")
            search_box = self.try_locate(self.init_url, box_locator, "searchbox")
        # 如果没有缓存，则利用GPT来定位
        if not search_box:
            print("Use llm to locate the search box...")
            search_box = self.handler_llm(url, None, element="searchbox")
        # GPT定位不成功则进行人工定位
        if not search_box:
            print("Mannually locate the search box...")
            search_box = self.handler_mannul(url, element="searchbox")
        
        # 往输入框中输入关键词并提交
        search_box.clear()
        search_box.send_keys(keyword)
        pre_window_num = len(self.driver.window_handles)
        search_box.send_keys(Keys.ENTER) # submit()模拟按下回车键
        time.sleep(2)
        new_window_num = len(self.driver.window_handles)
        if new_window_num == pre_window_num + 1 :
            self.driver.switch_to.window(self.driver.window_handles[-1])
        new_url = self.driver.current_url
        
        if should_judge_login:
            need_login = self.locator_handler.get_data(self.init_url, "need_login")
            should_write = False
            if need_login is None:
                should_write = True
                need_login = self.need_login_or_not(new_url, keyword)
            if need_login:
                login_result = input("请登录您的账户，并且登录之后输入[y/n]表示您是否登陆成功\n如果您认为当前界面无需登录，请输入[q]\n")
                if login_result == "n":
                    raise login_failed(url)
                if login_result == "q":
                    need_login = False
            if should_write:
                self.locator_handler.set_data(self.init_url, "need_login", need_login)
            return self.search(self.init_url, keyword, True, False)
        
        self.classify_website(new_url, keyword)
        result_urls = self.find_best_results_page(keyword, new_url)
        intro = ''
        for result_url in result_urls:
            print(f"Handling {result_url}")
            self.driver.get(result_url)
            html = self.get_html(result_url)
            source = f" 来源：{result_url}\n"
            intro += self.find_introduction(keyword, html, intro) + source
        introduction = self.introduction_parser.parse(f"keyword: {keyword}\ncontent: {intro}", clear_history=True)
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
                print(e)
                ref_urls, introduction = [], f"We catch an error while searching: \n {e}"
            search_results[url] = {"introduction": introduction, "reference": ref_urls}
        save_to_json(search_results, f"{keyword}.json")
        self.close()
        shutil.rmtree('./tmp')