def get_response_prompt():
    return """
    
    You are an expert in Web Interaction. Here is your task:
    
    The background information is:
    The user is chating with a llm agent on a website. And the user say something to the agent, waiting for
    the agent's response.
    
    I will give you a sentence, a piece of html and a history dialog. 
    The sentence is said by user this round.
    The html is sliced from the page source of the current website.
    The history dialog is the previous dialog between user and agent, and it may be None.
    
    Your task is: 
    1. Judge if the question can be answered by part of the text inside the html I give you.
    2. If yes, extract all the tags satisfying the condition above from the html and begin processing.
    3. Process: extract the tags that are the response of the agent by their property.
    4. After processing, extract text from the satisified tag and return it as the following format.
    4. If any of the three steps fail, return No with explaination.
    
    The format of your response should be:
    [Yes/No]. [Answer/Explaination]
    The Medium parentheses is just a placeholder, you should not contain it in your response.
    
    Here is two examples, the first one is answer not in text and the second one is answer in text.:
    1. No. [Explaination]
    2. Yes. [Answer]
    
    Note:
    1. Response should strictly obey the format, do not contain '[' or ']' in it.
    2. If the answer is in the text, you should just extract the answer from the text as what it is,
    modification is strictly prohibited.
    3. You must find the text in the html, do not return anything else.
    4. Do not return any answer in the history dialog.
    """