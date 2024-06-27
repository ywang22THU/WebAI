from GPTParser import GPT4Parser
from utils import *
from bs4 import BeautifulSoup as BS
from datetime import datetime
import json

# 打开一个标签页
def open_tab(url):
    return format_data(
        type="tab_open", 
        url="", 
        urlTarget=url
    )

# 关闭一个标签页
def close_tab(url):
    return format_data(
        type="tab_close",
        url=url,
    )

def change_tab(url, urlTarget):
    return format_data(
        type="tab_change",
        url=url,
        urlTarget=urlTarget
    )
# 输入操作
def input_msg(url, path, msg):
    return format_data(
        type="input",
        url=url,
        path=path,
        value=msg
    )

# 点击操作
def click(url, urlTarget, path):
    return format_data(
        type="click",
        url=url,
        path=path,
        urlTarget=urlTarget
    )