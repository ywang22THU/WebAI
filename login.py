import re
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.webdriver import WebDriver
from bs4 import BeautifulSoup
from locator import LocatorHandler
from utils import *
from GPTParser import GPT4Parser

"""
登录事件处理器 用于登录
"""
class LoginHandler:
    def __init__(self, driver: WebDriver, locator_hanlder: LocatorHandler) -> None:
        self.driver = driver
        self.locator_hanlder = locator_hanlder
    
    def find_login_box(self):...
    def login(self):...
    # TODO 大体可以模仿search.py的思路
    # 缓存 -> LLM -> 人工
    # 找到登录框 -> 用户输入账号密码 -> 提交 -> 判断是否登录成功