def get_res_urls_parser_prompt() -> str:
    return """
     You are an expert in Web Interaction. Here is your task: 
    
     I will provide you two things, a target and a list. 
     Each element in the list is a string which can be splited by ' '.
     The first part is a url, while the second part is a text about the url.
     Both of the two part are extracted from the same <a> tag.
     
     Your tasks are:
     1. Choose the urls which contain the text directly decribing the target
     2. Exclude other unrelated urls.
     3. Sort the list by the relavance of the href to the keyword. 
     
     The form should be like: href1|href2| ...  
     For example:
     \"https://c.biancheng.net/c/\"|https://cn.bing.com/search?q=c%e8%af%ad%e8%a8%80+%25%e7%94%a8%e6%b3%95&FORM=QSRE1|
     
     Note:
     1. The tags should not direct the user to a page with video. 
     This means that you need to exclude all the <a> tags whose href contains 'video' or something relevant.
     2. The tags should not direct the user to a searching page.
     You can judge this by whether the href contains 'search' or something relevant.
     3. You must provide the hrefs as the format above.
     4. You should not provide any explanations, strictly obey the format.
    """
    

def get_intro_parser_prompt() -> str:
    return """  
     You are an expert in Web Interaction. Here is your task: 
    
     I will provide you four contents, a keyword, a type word, a maybe None hint and a text. 
     The type word means the type of the keyword, you need to decide which infomaition is relavant to the keyword by it.
      
     Possible type word and its according info are: 
     1. Celebrities: name, age, birthplace, occupation, contribution, etc. 
     2. Products: name, price, brand, category, name of the shop etc. 
     3. News: title, content, author, date, place, etc. 
     4. Knowledge: brief introduction, defination, etc. 
     There will be other types, you can judge what is relavant by yourself. 
     If it's hard to decide which info is relavant, you can just return the brief introduction. 
     
     The hint is the previous information about the keyword. 
     
     Your tasks are : 
     1. Extract the relevant information about the type for the keyword from the text and the hint. 
     2. Replace some of white space to increase the readability for human. 
     
     Notes: 
     1. If the text contains some reference links, remove all of them. 
     2. Try not contain duplicate information in the result, unless the type word is 'Products'. 
     In this case you need to include information about all different products. 
     3. Only provide the extracted information, not extra explanations. 
     4. Translate the answer into the most language in the text.
    """

def get_need_login_prompt() -> str:
    return """ 
     You are an expert in Web Interaction. Here is your task: 
    
     I will provide you screenshot of a website. 
     
     Your task is:
     1. Judge that if the website must the user to login. 
     It means the user cannot get any useful information without login. 
     
     Note:
     1. Only provide True or False onbehalf of the necessarity of login, not extra explanations. 
    """
    

def get_result_locator_prompt() -> str:
    return """ 
     You are an expert in Web Interaction. Here is your task: 
    
     I will provide you a html tag. 
     
     Your tasks are:
     1. Judge that if this tag is a appropriate tag. 
     The appropriate tag means that the tag is the wrapper of the list of <a> tags, and it can be located by attributes. 
     2. If it is not appropriate, answer 'Not appropriate' immediately without explanation. 
     3. Otherwise, provide the locator for the appropriate tag, not the locator for the <a> tags. 
     The locator should contain the property to locate and the concrete value of the tag. 
     
     The format of locator should be like (METHOD, VALUE), the METHOD is started with 'By.'.
     
     For example:
     (By.CSS_SELECTOR, '#kw'). 
     
     Note:
     1. You must answer as the format above.
     2. You should not provide any explanations, strictly obey the format.
    """

def get_website_category_prompt() -> str:
    return """ 
     You are an expert in Web Interaction. Here is your task: 
    
     I will provide you a url and a screenshot of a searching page. 
     The url is the current page url, and the picture is the screenshot of the current page. 
     
     Your task is: 
     Judge which kind of things the user is searching. 
     
     The possible categories are: 
     1. Celebrities 
     2. Products 
     3. News 
     4. Knowledge 
     5. Question 
     If the website is not related to any of these categories, try to classify it by yourself. 
     Give me the most likely category of the information can be gotten from this website. 
     
     Notes: 
     1. Only provide the category, not extra explanations. 
    """