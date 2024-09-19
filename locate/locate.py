import re
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from .prompt import get_locator_prompt, get_html_handle_prompt
from cache import cache_handler
from utils import LanguageParser
from operate import HtmlOperator

# 定位器，定位某一种元素的位置
class Locator:
    def __init__(self, driver: WebDriver | None = None):
        self.driver = driver or webdriver.Chrome()
        self.cache_handler = cache_handler
        self.html_parser = LanguageParser(get_html_handle_prompt())
        self.locator_parser = LanguageParser(get_locator_prompt())
        self.html_operator = HtmlOperator()
        
    def get_html(self):
        return self.driver.page_source
    
    # 尝试通过locator定位组件的element
    def try_locate(self, url, locator, element):
        if not locator:
            return None
        try:
            print(f"Locating {element} in {url} by {locator}")
            aim = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(locator))
            return aim
        except Exception as e:
            print(e)
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
    def handler_llm(self, url, html, element, need_cache):
        if html is None:
            html = self.get_html()
        if type(html) is not str:
            html = html.get_attribute("outerHTML")
        # 多次定位提高定位成功率
        for _ in range(5):
            locator = self.element_locate_llm(url, html, element)
            if need_cache:
                aim = self.test_and_add_locator(url, locator, element)
            else:
                aim = self.try_locate(url, locator, element)
            if aim:
                print(f"Successfully located the {element} by GPT.")
                return aim
        if not aim:
            return None
    
    def element_locate_llm(self, url, html, element):
        possible_tags = []
        bs_slices = self.html_operator.slice_html(html)
        list_parttern = r'\[(.*?)\]'
        for bs_slice in bs_slices:
            msg = f"target: {element}\nhtml: {bs_slice.prettify(encoding="utf-8").decode()}"
            possible_tags_slice = self.html_parser.parse(msg, True)
            possible_tags_slice = f"[{re.findall(list_parttern, possible_tags_slice)[0]}]"
            possible_tags.extend(eval(possible_tags_slice))
        print(f"element: {element}\nhtml:{possible_tags}")
        response: str = self.locator_parser.parse(f"element: {element}\nhtml:{possible_tags}")
        part_pattern = r'\((.*), (.*)\)'
        parts = re.match(part_pattern, response).groups()
        find_method = eval(parts[0])
        final_tag = parts[1].strip("'").strip("\"")
        result_tuple = (find_method, final_tag)
        print(f"Locator for {element} in {url} is {result_tuple}")
        return result_tuple
        
    # 尝试定位
    def test_and_add_locator(self, url, locator, element):
        aim = self.try_locate(url, locator, element)
        if aim:
            self.cache_handler.set_data(url, element, list(locator))
            self.cache_handler.write_to_file()
            return aim
        else:
            return None
        
    def locate(self, data_url, url, keyword, need_cache=True):
        aim = None
        if need_cache:
            box_locator = self.cache_handler.get_data(data_url, keyword)
        else:
            box_locator = None
        # 先找缓存
        if box_locator:
            # 如果有缓存，则开始在其中找到对应的HTML元素
            print(f"Find pre-defined {keyword} locator for this website {data_url}...")
            aim = self.try_locate(data_url, box_locator, keyword)
        # 如果没有缓存，则利用GPT来定位
        if not aim:
            print(f"Use llm to locate the {keyword}...")
            aim = self.handler_llm(url, None, element=keyword, need_cache=need_cache)
        # GPT定位不成功则进行人工定位
        if not aim:
            print(f"Mannually locate the {keyword}...")
            aim = self.handler_mannul(url, element=keyword)
        return aim