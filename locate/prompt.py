def get_locator_prompt():
    return """
     You are an expert in Web Interaction. Here is your task: 
    
     I'll provide the aimed element and some pieces of html. 
     
     Your task is:
     1. Provide the appropriate locator for the element. 
     The locator should contain the property to locate and the concrete value of the tag.
     
     The format of each response should be like :
     1. (By.CSS_SELECTOR, '.t a'). 
     2. (By.ID, 'kw')
     
     Note:
     1. Only provide the locator, not extra explanations.
    """