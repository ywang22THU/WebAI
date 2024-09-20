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
    1. Judge if the sentence can be replied by part of the text inside the html I give you.
    2. If yes, extract all the tags satisfying the condition above from the html and begin processing.
    3. Process: extract the tags that are the response of the agent by their property.
    4. If any of the three steps fail, return No with explaination.
    
    The format of your response should be:
    [Yes/No]. [Tags/Explaination]
    The Medium parentheses is just a placeholder, you should not contain it in your response.
    Use '|' to separate the tags. 
    For example, if there are more than one tags, the format should be:
    Yes. Tag1|Tag2|... .
    
    Here is two examples, the first one is answer not in text and the second one is answer in text.:
    1. No. It seems that the provide html is the part of tool bar above, instead of the agent's reply.
    2. Yes. <p class="last-node">你好！有什么可以帮助你的吗？</p>|<p class="MuiTypography-root MuiTypography-text css-p94avn">Hi，我是 Kimi～很高兴遇见你！你可以随时把网址🔗或者文件📃发给我，我来帮你看看</p>
    
    Note:
    1. Response should strictly obey the format, do not contain '[' or ']' in it.
    2. If the answer is in the text, you should just extract the tag which contains the answer,
    modification is strictly prohibited.
    3. You must return the tag in the html if the answer is in the text., do not return anything else.
    4. Do not return any answer in the history dialog.
    """
    
def get_first_sentence_prompt():
    return """
    You are an expert in Web Interaction. Here is your task:
    
    The background information is:
    The user is chating with a llm agent on a website. And the user say something to the agent, waiting for
    the agent's response.
    
    I will give you a snapshot of the current website and the sentence user said.
    
    Your task is:
    1. Judge whether the agent has said something before the user.
    This means that you should judge whether the dialog starts at the user's sentence I give you.
    2. If the agent has said something before the user, return the agent's sentence.
    
    The format of your response should be:
    If the agent has said something before the user, return the agent's sentence without modification.
    Else, return 'No'.
    
    Note:
    1. Response should strictly obey the format, do not contain '[' or ']' or anything similar in it.
    2. Any modification on the agent's sentence is strictly prohibited.
    """
    
def get_judge_response_prompt():
    return """
    You are an expert in Web Interaction. Here is your task:
    
    I will give you a sentence, a response list and a history dialog.
    
    The sentence is said by user this round.
    The html is sliced from the page source of the current website.
    The history dialog is the previous dialog between user and agent, and it may be None.
    """