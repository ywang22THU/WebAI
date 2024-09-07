from openai import AzureOpenAI
from handyllm import OpenAIClient
from utils.utils import image_to_base64

class LanguageParser:
    def __init__(self, prompt, key = None):
        self.messages = [{'role': 'system', 'content': prompt}]
        self.client = OpenAIClient(
            api_type='azure',
            api_key= key or "a4982552aedf4162b7582ce9c31aa977",
            api_version="2023-12-01-preview",
            api_base = "https://pcg-east-us-2.openai.azure.com/"
        )
    
    def parse(self, message, clear_history=False):
        if clear_history:
            self.messages = self.messages[:1]
        self.messages.append({'role':'user', 'content':message})
        try:
            response = self.client.chat(
                engine="gpt-4-1106-preview",
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

class PictureParser:
    def __init__(self, prompt, key = None):
        self.prompt = prompt
        self.client = AzureOpenAI(
            api_key= key or "ccc220011aa14b3691ae7969db27aef2",
            api_version="2024-02-01",
            # azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_endpoint="https://pcg-sweden-central.openai.azure.com/",
        )
    
    def parse(self, img, path_or_code, *args, **kwargs):
        url = kwargs.get("url", "")
        img_url = f"data:image/jpeg;base64,{image_to_base64(img) if path_or_code else img}"
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