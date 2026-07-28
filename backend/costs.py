from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


class PricingUnavailable(RuntimeError):
    pass


def estimate_monthly(unit_price: float, unit: str, *, hours: int, requests_millions: int) -> float:
    if unit == "hour":
        return round(unit_price * hours, 4)
    if unit in {"million requests", "1M requests", "request"}:
        return round(unit_price * requests_millions, 4)
    raise PricingUnavailable(f"Unsupported pricing unit: {unit}")


class InfracostClient:
    API_URL = "https://pricing.api.infracost.io/graphql"

    def __init__(self, api_key: str, timeout_seconds: float = 15.0, session: Any = None) -> None:
        if not api_key:
            raise ValueError("INFRACOST_API_KEY is required")
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.session = session or requests.Session()

    def get_price(
        self, service_name: str, attributes: list[dict[str, str]], region: str = "us-east-1"
    ) -> tuple[float, str]:
        query = """query ($filter: ProductFilter!) { products(filter: $filter) { prices(filter: { purchaseOption: "on_demand" }) { USD unit } } }"""
        variables = {
            "filter": {
                "vendorName": "aws",
                "service": service_name,
                "region": region,
                "attributeFilters": attributes,
            }
        }
        try:
            response = self.session.post(
                self.API_URL,
                json={"query": query, "variables": variables},
                headers={"X-Api-Key": self.api_key, "Content-Type": "application/json"},
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
            if payload.get("errors"):
                raise PricingUnavailable("Infracost returned GraphQL errors")
            price = payload["data"]["products"][0]["prices"][0]
            return float(price["USD"]), str(price["unit"])
        except (requests.RequestException, KeyError, IndexError, TypeError, ValueError) as exc:
            raise PricingUnavailable("Pricing service is unavailable") from exc


@dataclass(frozen=True)
class Sku:
    service: str
    attributes: list[dict[str, str]]


SKU_MAP = {
    "Cassandra (NoSQL)": Sku("AmazonMCS", []),
    "Kafka": Sku("AmazonMSK", [{"key": "instanceType", "value": "kafka.m5.large"}]),
    "Redis": Sku("AmazonElastiCache", [{"key": "instanceType", "value": "cache.t3.medium"}]),
    "AWS EKS (Kubernetes)": Sku("AmazonEKS", []),
    "API Gateway (Amazon API Gateway)": Sku("AmazonApiGateway", []),
    "AWS Lambda (Serverless)": Sku("AWSLambda", [{"key": "usageType", "value": "Request"}]),
}


class CostEstimator:
    def __init__(self, client: InfracostClient | None) -> None:
        self.client = client

    def estimate(self, design: dict[str, Any]) -> tuple[float | None, list[str]]:
        if self.client is None:
            return None, ["Infrastructure pricing unavailable: INFRACOST_API_KEY is not configured"]
        total = 0.0
        details: list[str] = []
        for component in design.get("tech_stack", []):
            technology = component.get("technology", "")
            sku = SKU_MAP.get(technology)
            if sku is None:
                continue
            try:
                price, unit = self.client.get_price(sku.service, sku.attributes)
                monthly = estimate_monthly(price, unit, hours=730, requests_millions=10)
                total += monthly
                details.append(f"{technology}: ~${monthly:.2f}/month ({unit})")
            except PricingUnavailable:
                details.append(f"{technology}: pricing unavailable")
        return round(total, 2), details
