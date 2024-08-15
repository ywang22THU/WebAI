def get_input_prompt() -> str:
    prompt =  ""
    prompt += "I'll provide the aimed element and some pieces of html. "
    prompt += "Provide the appropriate locator for each element. "
    prompt += "The format of each response should be like (By.CSS_SELECTOR, '.t a'). "
    prompt += "Only provide the locator, not extra explanations."
    return prompt

def get_res_urls_parser_prompt() -> str:
    prompt =  ""
    prompt += "I will provide you two things, a target and a list of html a tags. "
    prompt += "The tags are the results while searching the target in some search engine. "
    prompt += "You need to choose the tags which contain the text directly decribing the target, "
    prompt += "and extract their hrefs. "
    prompt += "Sort the list by the relavance of the href to the keyword. "
    prompt += "Make sure their form is href1|href2| ... . "
    prompt += "Only provide the hrefs, not extra explanations."
    return prompt

def get_intro_parser_prompt() -> str:
    prompt =  ""
    prompt += "I will provide you two contents, a keyword and a long text. "
    prompt += "Extract the most relevant information that introduce the keyword from the long text, "
    prompt += "and replace some of white space to increase the readability for human. "
    prompt += "Only provide the extracted information, not extra explanations."
    return prompt

def get_relavence_parser_prompt() -> str:
    prompt =  ""
    prompt += "I will provide you two contents, a keyword and a title of a website. "
    prompt += "You need to judge the relavance of the keyword to the title. "
    prompt += "Provide a integer between 0 and 100 on behalf of the relavance."
    prompt += "The bigger the integer, the more relavance the keyword has to the title. "
    prompt += "Only provide the number, not extra explanations."
    return prompt