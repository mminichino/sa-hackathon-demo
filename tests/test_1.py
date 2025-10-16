import json
from unittest.mock import patch, MagicMock
from src.services.fraudomatic import get_score


@patch('src.services.fraudomatic.llm')
def test_get_score_low_risk(mock_llm):
    mock_response = MagicMock()
    expected_dict = {
        "risk_score": 0.1,
        "fraud_indicators": [],
        "reasoning": "Transaction is consistent with user's spending habits."
    }
    mock_response.content = json.dumps(expected_dict)
    mock_llm.invoke.return_value = mock_response

    result = get_score(
        amount=50.0,
        merchant="Familiar Store",
        location="Familiar Location",
        time="2025-10-16T10:00:00Z",
        spend_average=55.0,
        locations=["Familiar Location"],
        merchants=["Familiar Store"],
        recent_activity=[]
    )

    assert json.loads(result) == expected_dict
    mock_llm.invoke.assert_called_once()


@patch('src.services.fraudomatic.llm')
def test_get_score_high_risk(mock_llm):
    mock_response = MagicMock()
    expected_dict = {
        "risk_score": 0.9,
        "fraud_indicators": ["Unusual location", "High amount"],
        "reasoning": "Transaction from an unusual location with an amount significantly higher than average."
    }
    mock_response.content = json.dumps(expected_dict)
    mock_llm.invoke.return_value = mock_response

    result = get_score(
        amount=5000.0,
        merchant="Unknown Merchant",
        location="Unusual Location",
        time="2025-10-16T22:00:00Z",
        spend_average=100.0,
        locations=["Familiar Location"],
        merchants=["Familiar Store"],
        recent_activity=[]
    )

    assert json.loads(result) == expected_dict
    mock_llm.invoke.assert_called_once()
