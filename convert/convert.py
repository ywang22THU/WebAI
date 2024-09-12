from utils import LanguageParser
from .prompt import get_converter_prompt
import json

class Converter:
    def __init__(self) -> None:
        self.converter = LanguageParser(get_converter_prompt())
    
    def convert(self, url, description) -> dict:
        msg = f"url: {url}\n description: {description}"
        return json.loads(self.converter.parse(msg))
