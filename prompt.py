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
    prompt += "I will provide you two contents, a keyword, a type word, a maybe None hint and a text. \n\n"
    prompt += "The type word means the type of the keyword, you need to decide which infomaition is relavant to the keyword by it. \n\n"
    prompt += "Possible type word and its according info are: \n"
    prompt += "1. Celebrities: name, age, birthplace, occupation, contribution, etc. \n"
    prompt += "2. Products: name, price, brand, category, name of the shop etc. \n"
    prompt += "3. News: title, content, author, date, place, etc. \n"
    prompt += "4. Knowledge: brief introduction, defination, etc. \n"
    prompt += "There will be other types, you can judge what is relavant by yourself. "
    prompt += "If it's hard to decide which info is relavant, you can just return the brief introduction. \n\n"
    prompt += "The hint is the previous information about the keyword. \n\n"
    prompt += "Your tasks are : \n"
    prompt += "Extract the relevant information about the type for the keyword from the text and the hint, "
    prompt += "and replace some of white space to increase the readability for human. \n\n"
    prompt += "Notes: \n"
    prompt += "1. If the text contains some reference links, remove all of them. \n"
    prompt += "2. Try not contain duplicate information in the result, unless the type word is 'Products'. "
    prompt += "In this case you need to include information about all different products. \n"
    prompt += "3. Only provide the extracted information, not extra explanations. \n"
    return prompt

def get_need_login_prompt() -> str:
    prompt =  ""
    prompt += "I will provide you screenshot of a website. "
    prompt += "You need to judge that if the website must the user to login. "
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

def get_website_category_prompt() -> str:
    prompt =  ""
    prompt += "I will provide you a url and a screenshot of a searching page. "
    prompt += "You need to judge the which kind of things the user is searching. "
    prompt += "The possible categories are: "
    prompt += "1. Celebrities "
    prompt += "2. Products "
    prompt += "3. News "
    prompt += "4. Knowledge "
    prompt += "If the website is not related to any of these categories, try to classify it by yourself. "
    prompt += "Give me the most likely category of the information can be gotten from this website. "
    prompt += "Only provide the category, not extra explanations."
    return prompt