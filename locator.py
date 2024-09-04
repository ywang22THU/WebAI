from utils import *

class LocatorHandler:
    def __init__(self, file_name: str):
        self.file_name = file_name
        self.data: dict = self.read_from_file()
    
    def __del__(self):
        self.write_to_file()

    def read_from_file(self):
        try:
            return read_from_json(self.file_name)
        except:
            return None
    
    def write_to_file(self):
        try:
            save_to_json(self.data, self.file_name)
        except:
            return None
    
    # 拿到url页面的ele元素
    def get_data(self, url, ele) -> list:
        try:
            return self.data[url][ele]
        except:
            return None
    
    # 设置url页面的ele元素
    def set_data(self, url, ele, val):
        if not self.data:
            return
        if url not in self.data.keys():
            self.data[url] = {}
        self.data[url][ele] = val