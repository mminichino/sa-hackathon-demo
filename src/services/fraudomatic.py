import json
from langchain_openai import ChatOpenAI

llm = ChatOpenAI()

def get_score(
        amount: float,
        merchant: str,
        location: str,
        time: str,
        spend_average: float,
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
    
    Analyze for fraud risk. Provide a response only in JSON format with the following structure:
    {
     "risk_score": 0,
     "fraud_indicators": [],
     "reasoning": ""
    }
    
    If there are no fraud indicators set fraud_indicators to an empty list. Otherwise set it to a list of strings.
    Reasoning should be a short sentence justifying the risk score. 
    The risk score should be a number between 0 and 1 with 1 being the highest risk.
    """

    response = llm.invoke(prompt)

    return response.content
