def get_urls_prompt() -> str:
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
    
def get_result_locator_prompt() -> str:
    return """ 
     You are an expert in Web Interaction. Here is your task: 
    
     I will provide you a html tag. 
     
     Your tasks are:
     1. Judge that if this tag is a appropriate tag. 
     The appropriate tag means that the tag is the wrapper of the list of <a> tags, and it can be located by attributes. 
     2. If it is not appropriate, answer 'Not appropriate' with explanation. 
     3. Otherwise, provide the locator for the appropriate tag, not the locator for the <a> tags. 
     The locator should contain the property to locate and the concrete value of the tag. 
     
     The format of locator should be: 
      If the tag is appropriate:
       answer (METHOD, VALUE), for example (By.CSS_SELECTOR, '#kw'), and the METHOD should start with 'By.'.
      If the tag is not appropriate:
       answer 'Not appropriate, ...', the part ... is the explanation.
     
     Note:
     1. You must provide the hrefs as the format above.
     2. You should not provide any explanations, strictly obey the format.
    """
    
def get_url_judger_prompt() -> str:
    return """
     You are an expert in Web Interaction. Here is your task:
     
     I will give you a url, a screenshot of the website and a target description dictionary.
     
     Your task is:
     1. Judge if the screenshot satisfies the target description.
     
     Answer 'Yes' if the question 1 are satisfied, otherwise answer 'No'.
     
     Your answer should have the format like:
      [Yes/No]. It is beacuse ....
     
     Note:
     1. You should think step by step.
     2. Provide the answer and explanations.
    """