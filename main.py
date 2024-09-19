from search import SearchEngine
from open import Opener
from cache import cache_handler

keywords = [
    "哈希表",
    "python",
    "邱勇",
    "为祖国健康工作五十年"
]

urls = [
    # "https://developer.mozilla.org/zh-CN/"
    "https://www.bing.com"
    # "https://www.hao123.com/"
    # "https://www.google.com",
    # "https://www.baidu.com",
    # "https://oi-wiki.org/",
    # "https://www.cs.tsinghua.edu.cn/",
    # "https://www.bilibili.com/",
    # "https://www.taobao.com"
    # "https://www.xiaohongshu.com/explore",
]

if __name__ == "__main__":
    
    search_engine = SearchEngine()
    # search_engine.html_generate(urls, keywords)
    # print("html_generate finished")
    search_engine.run(urls, keywords[0])