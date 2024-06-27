from GPTParser import GPT4Parser
from utils import *
from base import *
from bs4 import BeautifulSoup as BS
from datetime import datetime
import json

# 第一遍初筛
def static_init_extract_search_boxes(html, url):
    soup = BS(html, 'html.parser')
    for script in soup.find_all('script'):
        script.decompose()
    content = str(soup.find('body'))
    if url is not None:
        name = url.split("//")[-1].split(".")[1]
        save_to_html(content, f"../data/html/{name}.html")
        print("The html's body has been saved.")
    textareas = soup.find_all('textarea')
    inputs = soup.find_all('input')
    buttons = soup.find_all('button')
    possible = (str(textareas) + str(inputs) + str(buttons)).replace('[]', '')
    return possible

# GPT筛查
def gpt_extract_search_boxes(init_extraction):
    parser = GPT4Parser("I want to extract the main search box of a page. For example, the box where we input what we want to search in google-chrome. I'll provide the some pieces of the target html, includes all of the 'form' tags, 'input' tags and 'button' tags. Please tell me which one is the most important search box and the submit button of it, sparated by the special signal '|'. Just give me their ids in order, without any information!")
    response = parser.parse(init_extraction)
    return response

# 找到到达某个组件的path
def find_path(soup: BS, target_id):
    path = []
    node = soup.find(id = target_id)
    while node is not None:
        step = node.name
        if step == "body":
            break
        index = node.parent.index(node)
        path.append(f"{step}:{index}")
        node = node.parent
    return path[::-1]

# 将结果转化为json格式
def search(html, url, msg):
    response = static_init_extract_search_boxes(html, url)
    response = gpt_extract_search_boxes(response).replace(' ', '')
    print(response)
    box_id = response.split("|")[0]
    submit_id = response.split("|")[1]
    soup = BS(html, 'html.parser')
    box_path = find_path(soup, box_id)
    submit_path = find_path(soup, submit_id)
    open_step = open_tab(url)
    input_step = input_msg(url, box_path, msg)
    # TODO 使用了webdriver之后这里的urlTarget理应非空
    submit_step = click(url, urlTarget="", path=submit_path)
    task_name = f"Search {msg} in {url}."
    return json.dumps({"task": task_name, "steps":[open_step, input_step, submit_step]})
    
    
if __name__ == '__main__':
    html = open("./baidu.html", 'r').read()
    api = search(html, "www.baidu.com", "Tsinghua University")
    print("Begin saving!")
    save_to_html(api, './api.json')
    print("Done!")
    # print("Begin checking")
    # input_path = json.loads(api)["steps"][1]["path"]
    # ver = BS(html, 'html.parser').find("body")
    # for node in input_path:
    #     name = node.split(":")[0]
    #     index = (int)(node.split(":")[1])
    #     ver = ver.contents[index]
    #     if ver.name != name:
    #         print("Error! The name on the path is wrong!")
    #         break
    # if ver.get("id") != 'kw':
    #     print("Error! The id on the final is wrong!")
    # print("Wonderful!")
        
        