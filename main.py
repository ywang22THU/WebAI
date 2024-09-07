from search.search import SearchEngine

if __name__ == "__main__":
    search_engine = SearchEngine()
    keyword = "马嘉祺"
    urls = [
        # "https://developer.mozilla.org/zh-CN/"
        "https://www.bing.com"
        # "https://www.hao123.com/",
        # "https://www.google.com",
        # "https://www.baidu.com"
        # "https://oi-wiki.org/"
        # "https://www.cs.tsinghua.edu.cn/"
        # "https://www.taobao.com"
        # "https://www.xiaohongshu.com/explore"
    ]
    search_engine.run(urls, keyword)