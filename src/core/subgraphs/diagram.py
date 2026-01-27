from typing import TypedDict
from langgraph.graph import StateGraph, START, END
# Ensure you import your prompt template
from src.utils.prompts import DiagrammerPromptTemplate 
from src.agents.diagrammer import ArchitectureDiagrammer


# FIX 1: Must inherit from TypedDict
class diagramState(TypedDict):
    input_design: dict  # Use dict or your SystemDesignSchema
    output_code: str

def createDiagram(state: diagramState):
    # FIX 2: Pass the required prompt template to the class
    # It's better to initialize this inside the node or as a global
    diagrammer = ArchitectureDiagrammer(prompt=DiagrammerPromptTemplate)
    
    # Generate the code
    output_code = diagrammer.generate_code(state['input_design'])
    
    # FIX 3: Return only the update for 'output_code'
    # Avoid storing the whole 'diagrammer' object in state unless necessary
    return {"output_code": output_code}

def diagramBuilder():
    # Correctly initialize the graph with the TypedDict
    workflow = StateGraph(diagramState)
    workflow.add_node("create", createDiagram)
    workflow.add_edge(START, "create")
    workflow.add_edge("create", END)
    
    return workflow.compile()



# architecture_json = {
#     "system_name": "Real-Time Social Interaction Platform",
#     "system_architecture_style": {
#         "pattern": "Microservices",
#         "rationale": "Microservices architecture allows independent scaling of services handling posts, likes, comments, and messaging, meeting the low-latency and high-availability requirements while supporting the 70: 30 read/write ratio."
#     },
#     "communication_strategy": {
#         "internal_comms": "gRPC for service-to-service communication",
#         "async_logic": "Kafka for real-time notifications and feed updates"
#     },
#     "deployment_strategy": {
#         "infrastructure": "AWS EKS (Kubernetes)",
#         "orchestration": "Horizontal pod autoscaling based on CPU and memory usage, managed via Kubernetes HPA"
#     },
#     "data_management": {
#         "partitioning": "Sharding by UserID for user data and PhotoID for posts, with replication for high availability",
#         "consistency_guarantees": "Eventual consistency for feed updates, strong consistency for critical actions like authentication and messaging"
#     },
#     "processed_information": "The system handles user posts, likes, comments, and messages, generating real-time feed updates, notifications, and chat. Services include authentication, feed generation, notification dispatch, messaging, and content moderation. Endpoints include /post, /like, /comment, /message, /feed, and /notifications.",
#     "tech_stack": [
#         {
#             "component": "Ingestion",
#             "technology": "API Gateway (Amazon API Gateway)",
#             "rationale": "Manages high request volumes, provides rate limiting, and routes requests to appropriate microservices."
#         },
#         {
#             "component": "Storage",
#             "technology": "Cassandra (NoSQL)",
#             "rationale": "Distributed database for scalability and high availability, suitable for the high read/write ratio and sharding needs."
#         },
#         {
#             "component": "Compute",
#             "technology": "AWS Lambda (Serverless)",
#             "rationale": "Handles event-driven processing for notifications and feed updates, scaling automatically with traffic spikes."
#         },
#         {
#             "component": "Caching",
#             "technology": "Redis",
#             "rationale": "Reduces latency for frequent read operations (e.g., feed generation) and stores session data for authentication."
#         },
#         {
#             "component": "Messaging",
#             "technology": "Kafka",
#             "rationale": "Ensures reliable, low-latency delivery of real-time updates and notifications."
#         }
#     ],
#     "request_flows": {
#         "write_request_1": [
#             "User submits a post via /post endpoint",
#             "API Gateway routes to Post Service",
#             "Post Service stores post in Cassandra and publishes event to Kafka"
#         ],
#         "write_request_2": [
#             "User likes a post via /like endpoint",
#             "API Gateway routes to Like Service",
#             "Like Service updates Cassandra and triggers notification via Kafka"
#         ],
#         "read_request_1": [
#             "User requests feed via /feed endpoint",
#             "Feed Service retrieves posts from Redis cache (fallback to Cassandra if cache miss)",
#             "Feed Service returns ranked posts to user"
#         ],
#         "read_request_2": [
#             "User checks notifications via /notifications endpoint",
#             "Notification Service fetches from Redis cache (populated by Kafka consumers)",
#             "Notification Service returns real-time updates"
#         ]
#     },
#     "slo_engineering": {
#         "latency_strategy": "Edge caching (CDN) for static content, Redis for metadata, and optimized gRPC calls for service-to-service communication.",
#         "throughput_strategy": "Auto-scaling microservices based on traffic, with Kafka consumers dynamically adjusting to load.",
#         "security_compliance": "TLS encryption for all communications, OAuth 2.0 for authentication, and regular audits for data privacy compliance."
#     },
#     "connectivity_matrices": [
#         [
#             "User",
#             "API Gateway",
#             "Post Service"
#         ],
#         [
#             "User",
#             "API Gateway",
#             "Like Service"
#         ],
#         [
#             "User",
#             "API Gateway",
#             "Feed Service"
#         ],
#         [
#             "User",
#             "API Gateway",
#             "Notification Service"
#         ],
#         [
#             "Post Service",
#             "Kafka",
#             "Feed Service"
#         ],
#         [
#             "Like Service",
#             "Kafka",
#             "Notification Service"
#         ],
#         [
#             "Feed Service",
#             "Redis",
#             "User"
#         ],
#         [
#             "Notification Service",
#             "Redis",
#             "User"
#         ]
#     ]
# }


# graph=builder()

# intial_state={
#     "input_design":architecture_json
# }

# final_state=graph.invoke(intial_state)



# print(final_state['output_code'])