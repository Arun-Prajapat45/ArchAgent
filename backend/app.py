import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Body
from psycopg_pool import AsyncConnectionPool
# from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from fastapi.middleware.cors import CORSMiddleware

from src.core.graph import builder
from dotenv import load_dotenv
import os

load_dotenv()

DB_URI=os.getenv("POSTGRESS_URI")
# if "sslmode" not in DB_URI:
#     DB_URI += "?sslmode=require"

# --- LIFESPAN MANAGER ---
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # 1. Initialize the Pool and Checkpointer
#     connection_kwargs = {"autocommit": True}
#     async with AsyncConnectionPool(conninfo=DB_URI, kwargs=connection_kwargs) as pool:
#         checkpointer = AsyncPostgresSaver(pool)
        
#         # 2. Create tables if they don't exist
#         await checkpointer.setup()
        
#         # 3. Store the compiled graph in app state so nodes can access it
#         # We assume your builder() function is now async-compatible
#         app.state.agent_graph = builder(checkpointer) 
        
#         yield # Application runs here
#     # Pool closes automatically after yield

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def dict_to_markdown(data, level=2):
    md = ""
    for key, value in data.items():
        title = key.replace("_", " ").title()
        md += f"\n{'#' * level} {title}\n\n"

        if isinstance(value, dict):
            md += dict_to_markdown(value, level + 1)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    md += dict_to_markdown(item, level + 1)
                else:
                    md += f"- {item}\n"
            md += "\n"
        else:
            md += f"**{value}**\n\n"
    return md



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


# --- API ENDPOINT ---
@app.post("/chat")
async def chat_endpoint(
    user_input: str = Body(...), 
    thread_id: str = Body(None) # Client can provide an ID, or we make a new one
):
    # If no thread_id is provided, it's a "New Chat"
    if not thread_id:
        thread_id = str(uuid.uuid4())
    
    # config = {"configurable": {"thread_id": thread_id}}
    
    # Run the graph
    app.graph=builder()
    # Note: Using ainvoker/astream for FastAPI
    final_state = await app.graph.ainvoke(
        {"user_input": user_input}
    )
    print(final_state['system_requirements'])
    print(final_state['system_design'])
    print(final_state['output_code'])
    requirements_md = dict_to_markdown(final_state["system_requirements"])
    design_md = dict_to_markdown(final_state["system_design"])
    api_key = '[REDACTED]' 
    estimator = InfrastructureCostEstimator(api_key=api_key)
    cost, breakdown = estimator.estimate_from_hld(final_state['system_design'])


    # print(f"--- TOTAL ESTIMATED COST: ${cost:.2f}/mo ---")
    # for line in breakdown:
    #     print(line)
    return {
        "thread_id": thread_id,
        "output_requirements": requirements_md,
        "output_design": design_md,
        "output_code": final_state["output_code"],
        "cost_breakdown":breakdown
    }