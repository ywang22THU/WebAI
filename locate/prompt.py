def get_locator_prompt():
    return """
     You are an expert in Web Interaction. Here is your task: 
    
     I'll provide the aimed element and some pieces of html. 
     
     Your task is:
     1. Provide the appropriate locator for the element. 
     The locator should contain the property to locate and the concrete value of the tag.
     
     The format of each response should be like :
        (By.CSS_SELECTOR, '.t a'). 
     
     Note:
     1. Only provide the locator, not extra explanations.
    """
    
def get_html_handle_prompt():
   return """
    You are an expert in Web Interaction. Here is your task:
    
    I'll provide your an aimed target and a prettified part of html.
    
    Your task is:
    1. Go through the html and find the tag which matches the target.
    2. Provide at most five tags which are most likely to be the target.
    
    The format of response should satisfy :
    1. Each tag should be a string in the format of <tag_name>content</tag_name>.
    2. The response should be a list of tags.
    3. The response should be in the format of [TAG1, TAG2, ...].
    
    Here is an example for your response:
    ['<a>content</a>', '<p>test</p>', '<div class=\"name\"><br>Harry Potter</br></div>']
    
    Notes:
    1. Only provide the tags with the format above, not extra explanations.
    2. If the html is empty or not sufficient, return [].
    3. Do not contain the symbol ` in your response.
   """