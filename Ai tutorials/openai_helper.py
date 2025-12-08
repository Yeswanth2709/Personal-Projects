
import json
import pandas as pd

from llm.factory import create_llm_client
# ---------------------------
# LLM setup (uses your wrapper)
# ---------------------------

def get_llm():
    # This will read llm_config.yaml and create the right client
    return create_llm_client()



#SYSTEM_PROMPT = "You are a helpful assistant."


# ---------------------------
# Chat logic
# ---------------------------

def get_response(messages):
    # Build messages = [system] + full chat history
    messages = [{"role": "userr", "content": messages}] 
    llm1 = get_llm()
    reply = llm1.chat(messages)
    print(reply)
    return reply

def clean_json_from_reply(reply: str) -> str:
    """Strip ```json fences and keep only the {...} part."""
    text = reply.strip()

    # If wrapped in ``` ```
    if text.startswith("```"):
        # remove starting and ending ```
        text = text.strip("`")
        # remove possible 'json' after first ```
        if text.lower().startswith("json"):
            text = text[4:].lstrip()

    # Keep only the first {...} block
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start:end+1]

    return text


def extract_financial_data(text):
    prompt = get_prompt_financial() + text
    
    
    content = get_response(prompt)
    try:
        cleaned=clean_json_from_reply(content)
        data = json.loads(cleaned)
        return pd.DataFrame(data.items(), columns=["Measure", "Value"])

    except (json.JSONDecodeError, IndexError):
        pass

    return pd.DataFrame({
        "Measure": ["Company Name", "Stock Symbol", "Revenue", "Net Income", "EPS"],
        "Value": ["", "", "", "", ""]
    })



def get_prompt_financial():
    return '''Please retrieve company name, revenue, net income and earnings per share (a.k.a. EPS)
    from the following news article. If you can't find the information from this article 
    then return "". Do not make things up.    
    Then retrieve a stock symbol corresponding to that company. For this you can use
    your general knowledge (it doesn't have to be from this article). Always return your
    response as a valid JSON string. The format of that string should be this, 
    {
        "Company Name": "Walmart",
        "Stock Symbol": "WMT",
        "Revenue": "12.34 million",
        "Net Income": "34.78 million",
        "EPS": "2.1 $"
    }
    News Article:
    ============

    '''

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    text = '''
    Tesla's Earning news in text format: Tesla's earning this quarter blew all the estimates. They reported 4.5 billion $ profit against a revenue of 30 billion $. Their earnings per share was 2.3 $
    '''
    df = extract_financial_data(text)

    print(df.to_string())