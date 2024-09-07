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
from utils.utils import *
from prompt import *
from cache.cache import CacheHandler
from utils.parser import LanguageParser, PictureParser
from functools import reduce
import time

# 定位器，定位某一种元素的位置
class Locator:
    def __init__(self, driver: WebDriver | None = None):
        self.driver = driver or webdriver.Chrome()
        self.cache = CacheHandler()
        self.locator_parser = LanguageParser()