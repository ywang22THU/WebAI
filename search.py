import requests
import re
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.webdriver import WebDriver
from bs4 import BeautifulSoup
from utils import *
from locator import LocatorHandler
from GPTParser import GPT4Parser
import time

class SearchEngine: 
    """搜索引擎类"""
    def __init__(self):
        self.driver: WebDriver = webdriver.Chrome() # 主浏览器
        self.locator_handler = LocatorHandler("locators.json") # 定位器缓存管理器
        # 元素解析器
        self.introduction_parser = GPT4Parser("I will provide you two contents, a keyword and a long text. Extract the most relevant information that introduce the keyword from the long text and replace some of white space to increase the readability for human. Only provide the extracted information, not extra explanations. ")
        self.result_url_parser = GPT4Parser("I will provide you two things, a target and a list of html a tags. The tags are the results while searching the target in some search engine. You need to choose the tags which contain the text directly decribing the target and extract their hrefs. Sort the list by the relavance of the href to the keyword and make its form be  with form of href1|href2| ... . Only provide the hrefs, not extra explanations.")
        self.parser = GPT4Parser("I'll provide the aimed element and some pieces of html. Provide the appropriate locator for each element. The format of each response should be like (By.CSS_SELECTOR, '.t a'). Only provide the locator, not extra explanations.")

    # 尝试通过locator定位课件的element
    def try_locate(self, url, locator, element):
        try:
            print(f"Locating {element} in {url} by {locator}")
            aim = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(locator))
            return aim
        except:
            return None

    # 人工处理，添加元素定位器
    # 注意是直接返回的HTML元素
    def handler_mannul(self, url, element: str):
        while(True):
            new_locator = input(f"Please enter the {element} locator for the website {url}. The format should be like (By.CSS_SELECTOR, '.t a').")
            aim = self.test_and_add_locator(url, new_locator, element)
            if aim:
                return aim
    
    # GPT添加元素定位器
    # 注意是直接返回的HTML元素
    def handler_llm(self, url, html, element, simple=False):
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
            print(f"Failed to locate the {element} by GPT.")
            return None
    
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
    
    # 查询操作
    def search(self, url, keyword):
        print("Searching for ", keyword, " on ", url)
        self.driver.get(url)
        print("begin search")
        
        search_box = None
        box_locator = self.locator_handler.get_data(url, "searchbox")
        # 先找缓存
        if box_locator:
            # 如果有缓存，则开始在其中找到对应的HTML元素
            print("Find pre-defined search box locator for this website...")
            search_box = self.try_locate(url, box_locator, "searchbox")
        # 如果没有缓存，则利用GPT来定位
        if not search_box:
            print("Use llm to locate the search box...")
            search_box = self.handler_llm(url, None, element="searchbox")
        # GPT定位不成功则进行人工定位
        if not search_box:
            print("Mannually locate the search box...")
            search_box = self.handler_mannul(url, element="searchbox")
        
        # 往输入框中输入关键词并提交
        search_box.send_keys(keyword)
        
        pre_window_num = len(self.driver.window_handles)
        search_box.submit() # submit()模拟按下回车键
        time.sleep(1)
        new_window_num = len(self.driver.window_handles)
        if new_window_num == pre_window_num + 1 :
            self.driver.switch_to.window(self.driver.window_handles[-1])

        new_url = self.driver.current_url
        html = self.driver.page_source
        
        result_urls = self.find_best_results_page(keyword, new_url, html)
        intro = ''
        
        for result_url in result_urls:
            print(f"Handling {result_url}")
            self.driver.get(result_url)
            html = self.get_html(result_url)
            source = f" 来源：{result_url}\n"
            intro += self.find_introduction(keyword, html) + source
        introduction = self.introduction_parser.parse(f"keyword: {keyword}\ncontent: {intro}")
        return result_urls, introduction
    
    # 获取对应网址的HTML
    # 前提是已经将这个网址输入进去了
    def get_html(self, url):
        try:
            html = self.driver.page_source
            return html
        except Exception as e:
            print(f"Failed to get {url}: {e}")
            return None       
    
    # 在搜索后的界面中找到结果界面
    def find_best_results_page(self, keyword: str, url: str, html: str) -> list:
        root = urlparse(url).scheme + "://" + urlparse(url).netloc
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a')
        choices = list(filter(lambda link: keyword in link.text, links))
        hrefs = self.result_url_parser.parse("target: " + keyword + ", list: " + str(choices)).split('|')
        res_urls = list(map(lambda href: href if href.startswith('http') else root + '/' + href, hrefs))
        return res_urls
    
    # 在url界面中找到简介
    def find_introduction(self, keyword, html):
        soup = BeautifulSoup(html, 'html.parser')
        body = soup.find('body')
        raw = body.get_text()
        content = re.sub(r'\s+', ' ', raw)[:10000]
        fs = open('log.txt', 'w', encoding='utf-8')
        fs.write(content)
        raw = self.introduction_parser.parse(f"keyword: {keyword}\ncontent: {content}")
        intro_text = self.introduction_parser.parse(f"keyword: {keyword}\ncontent: {raw}")
        return intro_text 
    
    # 利用GPT找到html中对应的element
    # element都是一些描述性的语句
    def element_locator_gpt(self, url, html, element):
        # 首先预处理html
        soup = BeautifulSoup(html, 'html.parser')
        # 去除所有的脚本
        for script in soup.find_all('script'):
            script.decompose()
        content = str(soup.find('body'))
        name = url.split("//")[-1].split(".")[1].replace("/", "")
        # 保存好html的body
        save_to_html(content, f"../data/html/{name}.html")
        print("The html's body has been saved.")
        # 找到有可能和搜索相关的几种元素
        forms = soup.find_all('form')
        inputs = soup.find_all('input')
        links = soup.find_all('a')
        buttons = soup.find_all('button')
        possible_elements = forms + inputs + links + buttons
        choices = str(possible_elements)
        # 利用GPT找到尽可能符合要求的元素
        # 根据初始化时的规定，格式应该为(By.CSS_SELECTOR, '.t a')
        response = self.parser.parse(f"element: {element}\nhtml:{choices}")
        print(f"Response from GPT: {response}")
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
            self.locator_handler.set_data(url, element, locator)
            return aim
        else:
            return None
    
    # 在很多url中搜索keyword
    def run(self, urls, keyword):
        search_results = {"keyword": keyword}
        for url in urls:
            urls, introduction = self.search(url, keyword)
            self.open_new_tab()
            name = url.split("//")[1].split(".")[1]
            search_results[name] = {"introduction": introduction, "reference": urls}
        self.locator_handler.write_to_file()
        save_to_json(search_results, f"{keyword}.json")
        self.close()
    
            
if __name__ == "__main__":
    search_engine = SearchEngine()
    keyword = "马昱春"
    urls = [
        # "https://developer.mozilla.org/zh-CN/"
        "https://www.bing.com"
        # "https://www.hao123.com/",
        # "https://www.google.com",
        # "https://www.baidu.com"
        # "https://oi-wiki.org/"
        # "https://www.cs.tsinghua.edu.cn/"
    ]
    search_engine.run(urls, keyword)