import json
from langchain_openai import ChatOpenAI

llm = ChatOpenAI()

def get_score(
        amount: str,
        merchant: str,
        location: str,
        time: str,
        spend_average: str,
        locations: list[str],
        merchants: list[str],
        recent_activity: list[dict]
):
    prompt = f"""
    Transaction Details: 
      amount: {amount}
      merchant: {merchant}
      location: {location}
      timestamp: {time}
    User Profile:
      average spending: {spend_average}, 
      locations: {', '.join(locations)},
      merchants: {', '.join(merchants)}
    Recent Activity:
    {json.dumps(recent_activity, indent=2)}
    Fraud Indicators (use these as hints as to what could be fraudulent):
     Online transactions should be from a recognized merchant
     Online transactions should be scrutinized more than in-person transactions
     Transactions for a large amount from an unusual merchant
     Transactions for things like gift cards or TikTok if the users does not typically spend money from these merchants
    
    Analyze for fraud risk. Provide a response only in JSON format with the following structure:
    {{
     "risk_score": 0,
     "fraud_indicators": [],
     "reasoning": ""
    }}
    
    If there are no fraud indicators set fraud_indicators to an empty list. Otherwise set it to a list of strings.
    Reasoning should be a short sentence justifying the risk score. 
    The risk score should be a number between 0 and 1 with 1 being the highest risk.
    Everything should have a score. A Score greater than or equal to 0.5 is considered fraudulent.
    """

    response = llm.invoke(prompt)

    return response.content
