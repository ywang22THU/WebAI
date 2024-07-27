import requests
import re
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from utils import *
from GPTParser import GPT4Parser
import time

class SearchEngine: 
    """搜索引擎类"""
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless") # 无头模式
        options.add_argument("--disable-gpu") # 禁用GPU加速
        self.driver = webdriver.Chrome(options=options) # 主浏览器
        tmp = read_from_json("locators.json") 
        if tmp:
            self.locators = tmp # 定位器缓存
        else:
            self.locators = {}
        print(self.locators)
        # 元素解析器
        self.introduction_parser = GPT4Parser("I will provide you two contents, a keyword and a long text. Extract the most relevant information that introduce the keyword from the long text and replace some of white space to increase the readability for human. Only provide the extracted information, not extra explanations. ")
        self.result_url_parser = GPT4Parser("I will provide you two things, a target and a list of website urls. The urls are the results while searching the target in some search engine. You need to choose the best url which contains the most text directly decribing the target. Only provide the url, not extra explanations.")
        self.parser = GPT4Parser("I'll provide the aimed element and some pieces of html. Provide the appropriate locator for each element. The format of each response should be like (By.CSS_SELECTOR, '.t a'). Only provide the locator, not extra explanations.")
    
    # 将定位器添加到缓存中
    # 添加url网页element元素的定位器locator
    def add_locator(self, url, locator, element: str):
        if url not in self.locators:
            self.locators[url] = {"locators": {}}
        if element not in self.locators[url]["locators"]:
            self.locators[url]["locators"][element] = locator
            print("Successfully added the locator: ", locator)
        else:
            print("Locator already exists.")
    
    # 尝试通过locator定位elements
    def try_locate_many(self, url, locator, element):
        try:
            print(f"Locating {element} in {url} by {locator}")
            aim = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located(locator))
            return aim
        except:
            return None

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
            if simple:
                locator = self.element_locator_gpt_simple(url, html, element)
            else:
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
        
        search_box = None
        # 先找缓存
        if self.locators and url in self.locators and "searchbox" in self.locators[url]["locators"]:
            print("Find pre-defined search box locator for this website...")
            box_locator = self.locators[url]["locators"]["searchbox"] or None
            # 如果有缓存，则开始在其中找到对应的HTML元素
            if box_locator:
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
        
        result_url = self.find_best_results_page(new_url, html)
        
        self.driver.get(result_url)
        html = self.get_html(result_url)
        
        # print(result_url)
        
        introduction = self.find_introduction(keyword, html)
        source = f"来源：{result_url}"
        
        return introduction + '\n' + source

    
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
    def find_best_results_page(self, url: str, html: str) -> str:
        root = urlparse(url).scheme + "://" + urlparse(url).netloc
        print(root)
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a')
        choices = [url]
        for link in links:
            href = link.get('href', '')
            href = href if href.startswith('http') else root + '/' + href
            name = link.text
            if keyword in name:
                choices.append(href)
        res_url = self.result_url_parser.parse("target: " + keyword + ", list: " + str(choices))
        return res_url
    
    # 在url界面中找到简介
    def find_introduction(self, keyword, html):
        soup = BeautifulSoup(html, 'html.parser')
        body = soup.find('body')
        raw = body.get_text()
        content = re.sub(r'\s+', ' ', raw)[:10000]
        fs = open('log.txt', 'w', encoding='utf-8')
        fs.write(content)
        intro_text = self.introduction_parser.parse(f"keyword: {keyword}\ncontent: {content}")
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
        # 将其保存在文件中
        save_to_txt(choices, 'choices.txt')
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
    
    # 不能将整个HTML直接输入！
    # 利用GPT找到html中对应的element，但是预处理更少，对于GPT的负担更大
    # element都是一些描述性的语句
    def element_locator_gpt_simple(self, url, html, element):
        soup = BeautifulSoup(html, 'html.parser')
        for script in soup.find_all('script'):
            script.decompose()
        # save_to_html(html, './log.html')
        fs = open('log.txt', 'a', encoding='utf-8')
        fs.truncate(0)
        links = soup.find_all('a')
        possible_elements = links
        choices = str(possible_elements)
        # 将其保存在文件中
        save_to_txt(choices, 'choices.txt')
        # 利用GPT找到尽可能符合要求的元素
        # 根据初始化时的规定，格式应该为(By.CSS_SELECTOR, '.t a')
        response = self.parser.parse(f"element: {element}\nhtml:{choices}")
        print(f"Response from GPT: {response}")
        # 将结果进行处理
        trimmed_str = response.strip("() ")
        parts = [part.strip() for part in trimmed_str.split(",")]
        find_method = eval(parts[0])
        final_tag = parts[1].strip("'")
        result_tuple = (find_method, final_tag)
        print(f"Locator for {element} in {url} is {result_tuple}")
        return result_tuple
    
    # 尝试定位
    def test_and_add_locator(self, url, locator, element):
        aim = self.try_locate(url, locator, element)
        if aim:
            self.add_locator(url, locator, element)
            return aim
        else:
            return None
    
    # 在很多url中搜索keyword
    def run(self, urls, keyword):
        search_results = {"keyword": keyword}
        for url in urls:
            print(f"Searching for {keyword} in {url}")
            search_result = self.search(url, keyword)
            self.open_new_tab()
            name = url.split("//")[1].split(".")[1]
            search_results[name] = search_result
            save_to_json(self.locators, "locators.json")
            # print(search_result)
        save_to_json(search_results, f"{keyword}.json")
        self.close()
    
            
if __name__ == "__main__":
    search_engine = SearchEngine()
    keyword = "清华大学"
    urls = [
        # "https://developer.mozilla.org/zh-CN/"
        "https://www.bing.com",
        "https://www.hao123.com/",
        # "https://www.google.com",
        "https://www.baidu.com"
        # "https://oi-wiki.org/"
    ]
    search_engine.run(urls, keyword)