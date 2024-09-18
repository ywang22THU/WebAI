from locate import Locator
from operate import HtmlOperator
from cache import cache_handler
from selenium import webdriver
from utils import LanguageParser, image_to_base64
from .prompt import get_response_prompt
import re
import time
import os
from tqdm import tqdm
from bs4 import BeautifulSoup

class Chater:
    def __init__(self):
        self.data_url = ''
        self.driver = webdriver.Chrome()
        self.locator = Locator(self.driver)
        self.operator = HtmlOperator(self.driver)
        self.response_parser = LanguageParser(get_response_prompt())
        self.cache_handler = cache_handler
        self.login_button = None
        self.text_input_box = None
        self.send_button = None
        self.dialog_history = []
    
    # 登录
    def login(self):
        need_login = self.cache_handler.get_data(self.data_url, "need_login", True)
        if not need_login:
            return
        url = self.driver.current_url
        if not self.login_button:
            self.login_button = self.locator.locate(self.data_url, url, 'login_button')
        self.login_button.click()
        login_result = input("请登录您的账户，并且登录之后输入[y/n]表示您是否登陆成功\n如果您认为当前界面无需登录，请输入[q]\n")
        if login_result == "y":
            return
        if login_result == "n":
            raise RuntimeError(f"User failed to login in {url}")
        if login_result == "q":
            self.cache_handler.set_data(self.data_url, "need_login", False)
    
    # 输入文本
    def type_in(self, text):
        url = self.driver.current_url
        while True:
            try:
                self.text_input_box.clear()
                self.text_input_box.send_keys(text)
                self.send_button.click()
                break
            except:
                self.text_input_box = self.locator.locate(self.data_url, url, "text_input_box")
                self.send_button = self.locator.locate(self.data_url, url, "send_text_button")
                
    def judge_stable(self):
        if os.path.exists(f'./tmp/last_time.png'):
            os.remove(f'./tmp/last_time.png')
        self.driver.save_screenshot('./tmp/last_time.png')
        last_time_base = image_to_base64('./tmp/last_time.png')
        time.sleep(0.001)
        now_base = self.driver.get_screenshot_as_base64()
        return last_time_base == now_base
    
    # 处理回复
    def get_response(self, text):
        html = self.driver.page_source
        # print(BeautifulSoup(html, 'html.parser').text)
        soups = self.operator.slice_html(html, False)
        resp_parttern = r"Yes\. (.*)"
        for soup in tqdm(soups):
            msg = f"User's word: {text}\nText: {soup}\nHistory: {str(self.dialog_history)}"
            resp = self.response_parser.parse(msg, True)
            try:
                return re.match(resp_parttern, resp).groups()[-1]
            except:
                print(f"模型回复了：{resp}")
        return "模型没有回复"
        
    # 聊天
    def chat(self, url):
        if not os.path.exists(f'./tmp'):
            os.mkdir(f'./tmp')
        self.data_url = url
        self.driver.get(url)
        self.login()
        while True:
            text = input("请输入您要发送的消息：")
            self.type_in(text)
            while not self.judge_stable():
                print("等待回复")
                time.sleep(1)
            response = self.get_response(text)
            print(f"模型的回复是：{response}")    