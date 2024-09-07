import json
import base64
from selenium.webdriver.common.by import By

def save_to_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
def save_to_txt(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(data)
        
def save_to_html(data, filename):
    if type(data) != str:
        data = str(data)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(data)
        
def read_from_json(filename):
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')