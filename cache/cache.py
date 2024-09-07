from utils.utils import *
from threading import Thread, Lock

file_locker = Lock()

class CacheHandler:
    def __init__(self, file_name: str):
        self.file_name = file_name
        file_locker.acquire()
        self.data: dict = self.read_from_file()
        file_locker.release()
    
    def __del__(self):
        self.write_to_file()

    def read_from_file(self):
        try:
            return read_from_json(self.file_name)
        except:
            return None
    
    def write_to_file(self):
        try:
            file_locker.acquire()
            save_to_json(self.data, self.file_name)
            file_locker.release()
        except:
            return None
    
    # 拿到url页面的ele元素
    def get_data(self, url, ele, default=None) -> list:
        try:
            return self.data[url][ele]
        except:
            self.set_data(url, ele, default)
            return default
    
    # 设置url页面的ele元素
    def set_data(self, url, ele, val):
        if not self.data:
            return
        if url not in self.data.keys():
            self.data[url] = {}
        file_locker.acquire()
        self.data[url][ele] = val
        file_locker.release()