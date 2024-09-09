def get_urls_prompt() -> str:
    return """
     You are an expert in Web Interaction. Here is your task: 
    
     I will provide you three things, a web url, a target description dictionary and a list of html <a> tags. 
     The tags are the results while looking for the target in the website. 
     
     Your tasks are:
     1. Choose the tags which are directly about target.
     2. Extract their hrefs. 
     3. Sort the list by the relavance of the href to the keyword. 
     
     The form should be like: href1|href2| ...  
     
     Note:
     1. Only provide the hrefs, not extra explanations.
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
     
     The format of locator should be like (METHOD, VALUE), for example (By.CSS_SELECTOR, '#kw'). 
     
     Note:
     1. Only provide the 'Not appropriate' or the locator, not extra explanations.
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