def get_input_prompt() -> str:
    prompt =  ""
    prompt += "I'll provide the aimed element and some pieces of html. "
    prompt += "Provide the appropriate locator for each element. "
    prompt += "The locator should contain the property to locate and the concrete value of the tag."
    prompt += "The format of each response should be like (By.CSS_SELECTOR, '.t a'). "
    prompt += "Only provide the locator, not extra explanations."
    return prompt

def get_res_urls_parser_prompt() -> str:
    prompt =  ""
    prompt += "I will provide you two things, a target and a list of html <a> tags. "
    prompt += "The tags are the results while searching the target in some search websites. "
    prompt += "You need to choose the tags which contain the text directly decribing the target, "
    prompt += "and extract their hrefs. "
    prompt += "The tags should not direct the user to a page with video. "
    prompt += "This means that you need to exclude all the <a> tags whose href contains 'video' or something relevant. "
    prompt += "Sort the list by the relavance of the href to the keyword. "
    prompt += "Make sure their form is href1|href2| ... . "
    prompt += "Only provide the hrefs, not extra explanations."
    return prompt

def get_intro_parser_prompt() -> str:
    prompt =  ""
    prompt += "I will provide you two contents, a keyword and a long text. "
    prompt += "The content in the text may be relavant or not to the keyword. "
    prompt += "Extract the most relevant information that introduce the keyword from the long text, "
    prompt += "and replace some of white space to increase the readability for human. "
    prompt += "If the text contains some reference links, remove all of them. "
    prompt += "Only provide the extracted information, not extra explanations."
    return prompt

def get_need_login_prompt() -> str:
    prompt =  ""
    prompt += "I will provide you a list of html tags extracted from a source code of a website. "
    prompt += "You need to judge that if the website need the user to login. "
    prompt += "You can judge this by the class name or id name of the tags. "
    prompt += "If these information is not enough, you can also judge by other things in the tags. "
    prompt += "Attention, need login means that the website force the user to login. "
    prompt += "It means the user cannot get any useful information without login. "
    prompt += "Only provide \"True\" or \"False\" onbehalf of the necessarity of login, not extra explanations. "
    return prompt

def get_result_locator_prompt() -> str:
    prompt =  ""
    prompt += "I will provide you a html tag. "
    prompt += "At first, judge that if this tag is a appropriate tag. "
    prompt += "The appropriate tag means that the tag is the wrapper of the list of <a> tags, and it can be located by attributes. "
    prompt += "If it is not appropriate, answer 'Not appropriate' immediately without explanation. "
    prompt += "Otherwise, provide the locator for the appropriate tag, not the locator for the <a> tags. "
    prompt += "The locator should contain the property to locate and the concrete value of the tag. "
    prompt += "The format of locator should be like (METHOD, VALUE), for example (By.CSS_SELECTOR, '#kw'). "
    prompt += "Only provide the 'Not appropriate' or the locator, not extra explanations."
    return prompt