from locate import Locator
from operate import HtmlOperator
from cache import cache_handler
from selenium import webdriver
from utils import LanguageParser, PictureParser
from .prompt import get_response_prompt, get_first_sentence_prompt, get_judge_response_prompt
import re
import time
import os
import shutil
from typing import Literal
from bs4 import BeautifulSoup
from utils import save_to_html

class Chater:
    def __init__(self):
        self.data_url = ''
        self.driver = webdriver.Chrome()
        self.locator = Locator(self.driver)
        self.operator = HtmlOperator(self.driver)
        self.response_parser = LanguageParser(get_response_prompt())
        self.first_sentence_parser = PictureParser(get_first_sentence_prompt())
        self.reply_parser = LanguageParser(get_judge_response_prompt())
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
    
    # 判断模型的回复是否完成  
    def judge_stable(self):
        last_time_base = self.driver.get_screenshot_as_base64()
        time.sleep(0.001)
        now_base = self.driver.get_screenshot_as_base64()
        return last_time_base == now_base
    
    # 处理回复
    def get_response(self, text):
        html = self.driver.page_source
        self.driver.save_screenshot("./tmp/screenshot.png")
        soups = self.operator.slice_html(html)
        resp_parttern = re.compile(r"Yes\. (.*)", re.DOTALL)
        possible_replies = []
        for soup in soups:
            if len(re.sub(r"\s+", "", soup.text)) < 10:
                continue
            msg = f"User's word: {text}\nHtml slice: {soup.prettify()}\nHistory: {str(self.dialog_history)}"
            resp = self.response_parser.parse(msg, True)
            print(f"模型的回复是：{resp}")
            try:
                tags = re.match(resp_parttern, resp).groups()[-1].split('|')
                for tag in tags:
                    raw = BeautifulSoup(tag, 'html.parser').text
                    possible_replies.append(re.sub(r"\s+", " ", raw))
            except:
                pass
        return possible_replies
    
    def append_history(self, text, who: Literal["user", "agent"]):
        self.dialog_history.append(f"{who}: {text}")
        self.dialog_history = self.dialog_history[-20:]
    
    def one_round(self, first = False):
        text = input("请输入您要发送的消息：")
        if text == "q":
            return False
        self.type_in(text)
        self.append_history(text, "user")
        while not self.judge_stable():
            print("等待回复")
            time.sleep(1)
        if first:
            self.driver.save_screenshot("./tmp/first.png")
            first_sentence = self.first_sentence_parser.parse(self.driver.get_screenshot_as_base64(), False)
            print(f"模型的提示词是：{first_sentence}")
            if first_sentence != "No":
                self.append_history(first_sentence, "agent")
        possible_replies = self.get_response(text)
        msg = f"User's word: {text}\nPossible replies: {possible_replies}\nHistory: {self.dialog_history}"
        response = self.reply_parser.parse(msg, True)
        self.append_history(response, "agent")
        print(f"模型的回复是：{response}")
        return True
    
    # 聊天
    def chat(self, url):
        if not os.path.exists(f'./tmp'):
            os.mkdir(f'./tmp')
        self.data_url = url.strip('/')
        self.driver.get(url)
        self.login()
        self.one_round(first=True)
        # 之后开始循环问答
        while self.one_round():
            pass
        shutil.rmtree("./tmp")