import json
from datetime import datetime

def save_to_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Data saved to {filename}.")
    
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

def format_data(type, url, time = "", path = [], value = "", urlTarget = ""):
    if time is None or "":
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "type": type,
        "url": url,
        "time": time,
        "path": path,
        "value": value,
        "urlTarget": urlTarget
    }