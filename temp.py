

temp_hld_output={
  "system_name": "Real-Time Social Media Platform",
  
  "system_architecture_style": {
    "pattern": "Microservices",
    "rationale": "Microservices allow independent scaling of components like feed generation, notifications, and messaging, which is critical for handling the high read/write ratio and ensuring low latency."
  },
  "communication_strategy": {
    "internal_comms": "gRPC for service-to-service communication due to its low latency and high performance",
    "async_logic": "Apache Kafka for real-time event processing and notifications"
  },
  "deployment_strategy": {
    "infrastructure": "AWS EKS (Kubernetes)",
    "orchestration": "Horizontal pod autoscaling based on CPU and memory usage, with cluster autoscaling for traffic spikes"
  },
  "data_management": {
    "partitioning": "Sharding by UserID for user data and PhotoID for content data, with replication for high availability",
    "consistency_guarantees": "Eventual consistency for feed updates, strong consistency for critical actions like post creation and messaging"
  },
  "processed_information": "The system handles user posts, likes, comments, and messages, generating real-time feed updates, notifications, and chat. It includes services for authentication, feed generation, notifications, messaging, and content moderation.",
  "tech_stack": [
    {
      "component": "Ingestion",
      "technology": "API Gateway (Amazon API Gateway)",
      "rationale": "Manages high request volumes and provides throttling and caching"
    },
    {
      "component": "Storage",
      "technology": "Cassandra (NoSQL)",
      "rationale": "Scalable and distributed database for handling high write throughput and eventual consistency"
    },
    {
      "component": "Compute",
      "technology": "AWS Lambda (Serverless)",
      "rationale": "Efficiently scales for real-time processing of events like likes and comments"
    },
    {
      "component": "Caching",
      "technology": "Redis",
      "rationale": "Reduces latency for frequently accessed data like user feeds and notifications"
    },
    {
      "component": "Messaging",
      "technology": "WebSocket (API Gateway WebSocket API)",
      "rationale": "Enables real-time bidirectional communication for chat and notifications"
    }
  ],
  "request_flows": {
    "write_request_1": [
      "User posts content",
      "API Gateway routes to Post Service",
      "Post Service writes to Cassandra and publishes event to Kafka"
    ],
    "write_request_2": [
      "User likes a post",
      "API Gateway routes to Like Service",
      "Like Service updates Cassandra and triggers notification via Kafka"
    ],
    "read_request_1": [
      "User requests feed",
      "API Gateway routes to Feed Service",
      "Feed Service retrieves data from Redis (cache) or Cassandra (fallback)"
    ],
    "read_request_2": [
      "User checks notifications",
      "API Gateway routes to Notification Service",
      "Notification Service fetches from Redis and returns to client"
    ]
  },
  "slo_engineering": {
    "latency_strategy": "Edge caching (CloudFront), in-memory caching (Redis), and optimized query patterns to meet P99 latency targets",
    "throughput_strategy": "Auto-scaling for read-heavy services, sharding for write-heavy databases, and load balancing",
    "security_compliance": "OAuth 2.0 for authentication, TLS for encryption, and regular audits for compliance"
  },
  "connectivity_matrices": [
    ["User", "API Gateway", "Post Service"],
    ["User", "API Gateway", "Feed Service"],
    ["Post Service", "Kafka", "Notification Service"],
    ["Like Service", "Kafka", "Notification Service"],
    ["Feed Service", "Redis", "User"],
    ["Notification Service", "WebSocket", "User"]
  ]
}


import os
import requests

class InfrastructureCostEstimator:
    def __init__(self, api_key):
        self.api_url = "https://pricing.api.infracost.io/graphql"
        # FIXED: Removed quotes around api_key variable
        self.headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}
        
        # Mapping with specific filters to ensure the API finds a valid product
        self.sku_map = {
            "Cassandra (NoSQL)": {"service": "AmazonMCS", "attr": []},
            "Kafka": {"service": "AmazonMSK", "attr": [{"key": "instanceType", "value": "kafka.m5.large"}]},
            "Redis": {"service": "AmazonElastiCache", "attr": [{"key": "instanceType", "value": "cache.t3.medium"}]},
            "AWS EKS (Kubernetes)": {"service": "AmazonEKS", "attr": []},
            "API Gateway (Amazon API Gateway)": {"service": "AmazonApiGateway", "attr": []},
            "AWS Lambda (Serverless)": {"service": "AWSLambda", "attr": [{"key": "usageType", "value": "Request"}]}
        }

    def get_price(self, service_name, attributes, region="us-east-1"):
        query = """
        query ($filter: ProductFilter!) {
          products(filter: $filter) {
            prices(filter: { purchaseOption: "on_demand" }) {
              USD
              unit
            }
          }
        }
        """
        # Inject custom attribute filters (like instanceType) to get a real result
        variables = {
            "filter": {
                "vendorName": "aws", 
                "service": service_name, 
                "region": region,
                "attributeFilters": attributes
            }
        }
        
        try:
            response = requests.post(self.api_url, json={'query': query, 'variables': variables}, headers=self.headers)
            data = response.json()
            # Most prices come back as strings, convert to float
            price_str = data['data']['products'][0]['prices'][0]['USD']
            return float(price_str)
        except (IndexError, KeyError, Exception):
            return 0.0

    def estimate_from_hld(self, hld_json):
        total_monthly = 0
        details = []
        
        for item in hld_json.get("tech_stack", []):
            tech = item['technology']
            config = self.sku_map.get(tech)
            
            if config:
                unit_price = self.get_price(config['service'], config['attr'])
                
                # Logic to estimate a "Monthly" cost from unit price
                if tech == "AWS Lambda (Serverless)":
                    # Estimate based on 10 Million requests
                    monthly = unit_price * 10 
                elif tech == "API Gateway (Amazon API Gateway)":
                    # Estimate based on 10 Million requests (usually $3.50 per 1M)
                    monthly = unit_price * 10
                else:
                    # Standard 730 hours for an instance
                    monthly = unit_price * 730
                
                if monthly > 0:
                    total_monthly += monthly
                    details.append(f"✅ {tech}: ~${monthly:.2f}/mo")
                else:
                    details.append(f"⚠️ {tech}: Price not found (using default $0)")
        
        return total_monthly, details

# Run the estimator
# Replace with your actual key if the one provided is expired
api_key = '[REDACTED]' 
estimator = InfrastructureCostEstimator(api_key=api_key)
cost, breakdown = estimator.estimate_from_hld(temp_hld_output)

print(f"--- TOTAL ESTIMATED COST: ${cost:.2f}/mo ---")
for line in breakdown:
    print(line)