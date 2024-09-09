from search import SearchEngine
from open import Opener
from cache import cache_handler

if __name__ == "__main__":
    
    description = {
        'page_info': '视频',
        'keyword': '刘知远',
        'about': '视频内容是介绍大模型的'
    }
    url = 'https://www.bilibili.com'
    search_engine = SearchEngine(url=url)
    opener = Opener(search_engine.driver)
    search_engine.driver.get(url)
    search_engine.type_in(url, description['keyword'])
    print(opener.open_page(url, description))
    cache_handler.write_to_file()
    # search_engine = SearchEngine()
    # keyword = "C语言"
    # urls = [
    #     # "https://developer.mozilla.org/zh-CN/"
    #     "https://www.bing.com"
    #     # "https://www.hao123.com/",
    #     # "https://www.google.com",
    #     # "https://www.baidu.com"
    #     # "https://oi-wiki.org/"
    #     # "https://www.cs.tsinghua.edu.cn/"
    #     # "https://www.taobao.com"
    #     # "https://www.xiaohongshu.com/explore"
    # ]
    # search_engine.run(urls, keyword)