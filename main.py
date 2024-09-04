from search import SearchEngine

if __name__ == "__main__":
    search_engine = SearchEngine()
    keyword = "第一次去坐飞机有什么流程"
    urls = [
        # "https://developer.mozilla.org/zh-CN/"
        # "https://www.bing.com",
        # "https://www.hao123.com/",
        # "https://www.google.com",
        # "https://www.baidu.com"
        # "https://oi-wiki.org/"
        # "https://www.cs.tsinghua.edu.cn/"
        # "https://www.taobao.com"
        "https://www.xiaohongshu.com/explore"
    ]
    search_engine.run(urls, keyword)