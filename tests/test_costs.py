from unittest.mock import Mock

import pytest
import requests

from backend.costs import InfracostClient, PricingUnavailable, estimate_monthly


def test_monthly_cost_calculation_uses_explicit_units() -> None:
    assert estimate_monthly(0.25, "hour", hours=730, requests_millions=10) == 182.5
    assert estimate_monthly(3.5, "million requests", hours=730, requests_millions=10) == 35.0


def test_infracost_request_has_timeout_and_parses_price() -> None:
    session = Mock()
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"data": {"products": [{"prices": [{"USD": "0.42", "unit": "hour"}]}]}}
    session.post.return_value = response
    client = InfracostClient("key", timeout_seconds=7.0, session=session)
    assert client.get_price("AmazonEKS", []) == (0.42, "hour")
    assert session.post.call_args.kwargs["timeout"] == 7.0


def test_infracost_timeout_is_not_reported_as_zero() -> None:
    session = Mock()
    session.post.side_effect = requests.Timeout("slow")
    client = InfracostClient("key", timeout_seconds=1.0, session=session)
    with pytest.raises(PricingUnavailable):
        client.get_price("AmazonEKS", [])
