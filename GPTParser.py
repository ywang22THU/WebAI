import httpx
import openai
import requests
import json
import time
import base64
# from flask import jsonify
from openai import OpenAI
from openai import AzureOpenAI
from handyllm import OpenAIClient

MAX_RECURSION_TIME = 5

client = AzureOpenAI(
    api_key="a4982552aedf4162b7582ce9c31aa977",
    api_version="2023-12-01-preview",
    azure_endpoint = "https://pcg-east-us-2.openai.azure.com/"
)

deployment_name = "gpt-4-1106-preview" # 在 Azure OpenAI Studio 里创建的模型名称

def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        base64_image = base64.b64encode(img_file.read()).decode('utf-8')
        # print(base64_image)
        return base64_image


class GPT4Parser:
    def __init__(self, prompt, local = True):
        self.local = local
        # if local:
        #     self.client = OpenAI(http_client=httpx.Client(proxies={'http://':'http://localhost:7890','https://':'https://localhost:7890'},transport=httpx.HTTPTransport(local_address="0.0.0.0")),
        #                          organization='org-veTDIexYdGbOKcYt8GW4SNOH',api_key= "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" )
        self.messages = [{'role':'system','content':prompt}]
        self.client = OpenAIClient(
            api_type='azure',
            api_key="a4982552aedf4162b7582ce9c31aa977",
            api_version="2023-12-01-preview",
            api_base = "https://pcg-east-us-2.openai.azure.com/"
        )
        self.recursion_time = 0

    def parse(self, message, clear_history=False):
        if clear_history:
            self.messages = self.messages[:1]
        self.recursion_time = 0
        self.messages.append({'role':'user', 'content':message})
        response = self.chat_local(self.messages) if self.local else self.chat(self.messages)
        return response
        

    def chat(self, message):
        url = "http://101.6.41.93:22288/chat"
        data = {"message":message}
        response = requests.post(url=url, json=data)
        return json.loads(response.text)['result']['content']

    def chat_local(self, message):
        self.recursion_time += 1
        try:
            response = self.client.chat(
                engine="gpt-4o",
                messages = message
            ).call()
            if "error" not in response:
                usage = response["usage"]
                prompt_tokens = usage["prompt_tokens"]
                completion_tokens = usage["completion_tokens"]
                print(f"Prompt tokens: {prompt_tokens}, Completion tokens: {completion_tokens}")
            else:
                return response["error"]["message"]
            return response['choices'][0]['message']['content']
        except Exception as e:
            raise e

    def add_examples(self, examples):
        self.messages += examples

    def add_history(self, query, answer):
        self.messages.append({'role':'user', 'content':query})
        self.messages.append({'role':'system', 'content':answer})

class PictureParser:
    def __init__(self, prompt, key = None):
        self.prompt = prompt
        self.client = AzureOpenAI(
            api_key= key or "ccc220011aa14b3691ae7969db27aef2",
            api_version="2024-02-01",
            # azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_endpoint="https://pcg-sweden-central.openai.azure.com/",
        )
    
    def parse(self, img_path, *args, **kwargs):
        url = kwargs.get("url", "")
        img_url = f"data:image/jpeg;base64,{image_to_base64(img_path)}"
        messages = [
            {
                'role':'system',
                'content': self.prompt,
            },
            {
                'role':'user', 
                'content':[
                    {
                        "type": "text",
                        "text": f"The url of the website is: {url}",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": img_url},
                    }
                ]
            }
        ]
        try:
            response = self.client.chat.completions.create(
                model='gpt-4o',
                messages=messages,
                max_tokens=1024
            )
            usage = response.usage
            prompt_tokens = usage.prompt_tokens
            completion_tokens = usage.completion_tokens
            print(f"Prompt tokens: {prompt_tokens}, Completion tokens: {completion_tokens}")
            return response.choices[0].message.content
        except Exception as e:
            raise e
class AzureParser:
    def __init__(self, prompt, local = True):
        self.local = local
        # if local:
        #     self.client = OpenAI(http_client=httpx.Client(proxies={'http://':'http://localhost:7890','https://':'https://localhost:7890'},transport=httpx.HTTPTransport(local_address="0.0.0.0")),
        #                          organization='org-veTDIexYdGbOKcYt8GW4SNOH',api_key= "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" )
        self.messages = [{'role':'system','content':prompt}]
        self.client = AzureOpenAI(
            api_key="ccc220011aa14b3691ae7969db27aef2",
            api_version="2024-02-01",
            # azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_endpoint="https://pcg-sweden-central.openai.azure.com/",
        )

    def parse(self, message):
        tmp_messages = self.messages
        tmp_messages.append({'role':'user', 'content':message})
        if self.local:
            return self.chat_local(tmp_messages)
        else:
            return self.chat(tmp_messages)

    def chat(self, message):
        url = "http://101.6.41.93:22288/chat"
        data = {"message":message}
        response = requests.post(url=url, json=data)
        return json.loads(response.text)['result']['content']

    def chat_local(self, message):
        # deployment_name = "vision" # 在 Azure OpenAI Studio 里创建的模型名称
        deployment_name = "gpt-4o"
        response = client.chat.completions.create(
            model=deployment_name,
            messages = message
        )
        return response.choices[0].message.content
        #except Exception:
        #    return self.chat_local(message)

    def add_examples(self, examples):
        self.messages += examples

    def add_history(self, query, answer):
        self.messages.append({'role':'user', 'content':query})
        self.messages.append({'role':'system', 'content':answer})


if __name__ == "__main__":
    a = time.time()
    parser = AzureParser("我会给你一段语言描述的电脑操作，请你将这段操作转化为若干个基础步骤，并分行表示。请注意，有些描述时作为一步的步骤可能包含不止一个基础步骤，请你将这类步骤也拆分为若干步骤。")
    response = parser.parse("1.在桌面点击文件管理图表，右键点击“文件管理器”2.点击起动器（或者：win键），打开文件管理器3.反复快速打开多个窗口"
    )
    b = time.time()
    print(b-a)
    print(response)
