# import base64
# from IPython.display import Image, display
# import json
# from langchain_openai import ChatOpenAI
# from langchain.prompts import ChatPromptTemplate
# from langchain.schema import StrOutputParser
# from dotenv import load_dotenv
# import os
# load_dotenv()


# llm = ChatOpenAI(
#     model="deepseek/deepseek-chat",
#     base_url="https://openrouter.ai/api/v1",
#     api_key=os.getenv("LLM_KEY"),
#     temperature=0.3,
#     max_tokens=1024
# )

# architecture_json = {'system_name': 'Real-Time Social Media Platform', 'system_architecture_style': {'pattern': 'Microservices', 'rationale': 'Microservices allow independent scaling of components like feed generation, notifications, and messaging, which is critical for handling the high read/write ratio and ensuring low latency.'}, 'communication_strategy': {'internal_comms': 'gRPC for service-to-service communication due to its low latency and high performance', 'async_logic': 'Apache Kafka for real-time event processing and notifications'}, 'deployment_strategy': {'infrastructure': 'AWS EKS (Kubernetes)', 'orchestration': 'Horizontal pod autoscaling based on CPU and memory usage, with cluster autoscaling for traffic spikes'}, 'data_management': {'partitioning': 'Sharding by UserID for user data and PhotoID for content data, with replication for high availability', 'consistency_guarantees': 'Hybrid consistency model: causal consistency for feed updates to reduce staleness, strong consistency for critical actions like post creation and messaging'}, 'processed_information': 'The system handles user posts, likes, comments, and messages, generating real-time feed updates, notifications, and chat. It includes services for authentication, feed generation, notifications, messaging, and content moderation. All original functional features were preserved, including real-time chat, feed updates, notifications, and messaging.', 'tech_stack': [{'component': 'Ingestion', 'technology': 'Multi-region API Gateway (Amazon API Gateway)', 'rationale': 'Manages high request volumes and provides throttling and caching, with failover mechanisms for high availability'}, {'component': 'Storage', 'technology': 'Cassandra (NoSQL)', 'rationale': 'Scalable and distributed database for handling high write throughput and eventual consistency'}, {'component': 'Compute', 'technology': 'Kubernetes-managed services', 'rationale': 'Predictable latency for real-time processing of events like likes and comments, avoiding Lambda cold starts'}, {'component': 'Caching', 'technology': 'Redis', 'rationale': 'Reduces latency for frequently accessed data like user feeds and notifications, with persistence mechanisms to prevent data loss'}, {'component': 'Messaging', 'technology': 'WebSocket (API Gateway WebSocket API)', 'rationale': 'Enables real-time bidirectional communication for chat and notifications'}, {'component': 'Event Processing', 'technology': 'Apache Kafka with Dead-Letter Queue (DLQ)', 'rationale': 'Handles real-time event processing and notifications, with DLQ for failed event processing'}], 'request_flows': {'write_request_1': ['User posts content', 'Multi-region API Gateway routes to Post Service', 'Post Service writes to Cassandra and publishes event to Kafka'], 'write_request_2': ['User likes a post', 'Multi-region API Gateway routes to Like Service', 'Like Service updates Cassandra and triggers notification via Kafka'], 'read_request_1': ['User requests feed', 'Multi-region API Gateway routes to Feed Service', 'Feed Service retrieves data from Redis (cache) or Cassandra (fallback)'], 'read_request_2': ['User checks notifications', 'Multi-region API Gateway routes to Notification Service', 'Notification Service fetches from Redis and returns to client']}, 'slo_engineering': {'latency_strategy': 'Edge caching (CloudFront), in-memory caching (Redis), and optimized query patterns to meet P99 latency targets', 'throughput_strategy': 'Auto-scaling for read-heavy services, sharding for write-heavy databases, and load balancing', 'security_compliance': 'OAuth 2.0 for authentication, TLS for encryption, and regular audits for compliance'}, 'connectivity_matrices': [['User', 'Multi-region API Gateway', 'Post Service'], ['User', 'Multi-region API Gateway', 'Feed Service'], ['Post Service', 'Kafka', 'Notification Service'], ['Like Service', 'Kafka', 'Notification Service'], ['Feed Service', 'Redis', 'User'], ['Notification Service', 'WebSocket', 'User']]}

# chain=DiagrammerPromptTemplate | llm | StrOutputParser()


# mermaid_code = chain.invoke({
#     "arch_json": json.dumps(architecture_json, indent=2)
# })

# print(mermaid_code)



# def render_mermaid(mermaid_code):
#     """Encodes mermaid string and fetches image from mermaid.ink"""
#     graphbytes = mermaid_code.encode("ascii")
#     base64_bytes = base64.b64encode(graphbytes)
#     base64_string = base64_bytes.decode("ascii")
#     display(Image(url="https://mermaid.ink/img/" + base64_string))

# # Example usage with your connectivity matrix logic
# mermaid_graph = mermaid_code

# render_mermaid(mermaid_graph)

import base64
import json
import os
# from IPython.display import Image, display
# from langchain_openai import ChatOpenAI
from langchain_classic.schema import StrOutputParser
from ..utils.prompts import DiagrammerPromptTemplate
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

class ArchitectureDiagrammer:
    def __init__(self, prompt, model_name="", temperature=0.3):
        """
        Initializes the diagrammer.
        
        Args:
            prompt: The LangChain prompt template imported from your utils.
            model_name: The model string for OpenRouter.
            temperature: LLM temperature setting.
        """
        load_dotenv()
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            api_key=os.getenv("GEMINI_KEY"),
            temperature=0
        )

        
        # The prompt is now a dynamic input
        self.chain = prompt | self.llm | StrOutputParser()

    def _clean_code(self, text: str) -> str:
        """Removes markdown wrappers if present."""
        return text.replace("```mermaid", "").replace("```", "").strip()

    def generate_code(self, architecture_json: dict) -> str:
        """Runs the chain to get Mermaid syntax."""
        return self.chain.invoke({
            "arch_json": json.dumps(architecture_json, indent=2)
        })

    # def render(self, mermaid_code: str):
    #     """Displays the diagram via mermaid.ink API."""
    #     clean_code = self._clean_code(mermaid_code)
    #     try:
    #         graphbytes = clean_code.encode("ascii")
    #         base64_bytes = base64.b64encode(graphbytes)
    #         base64_string = base64_bytes.decode("ascii")
    #         display(Image(url="https://mermaid.ink/img/" + base64_string))
    #     except Exception as e:
    #         print(f"Error rendering: {e}")

    def run(self, architecture_json: dict):
        """Executes the full flow."""
        code = self.generate_code(architecture_json)
        # self.render(code)
        return code

# --- Test Input and Execution ---

# 1. Import your specific prompt (uncomment in your local environment)
# from ..utils.prompts import DiagrammerPromptTemplate

# 2. Mocking the architecture_json
# test_json = {'system_name': 'Real-Time Social Media Platform', 'system_architecture_style': {'pattern': 'Microservices', 'rationale': 'Microservices allow independent scaling of components like feed generation, notifications, and messaging, which is critical for handling the high read/write ratio and ensuring low latency.'}, 'communication_strategy': {'internal_comms': 'gRPC for service-to-service communication due to its low latency and high performance', 'async_logic': 'Apache Kafka for real-time event processing and notifications'}, 'deployment_strategy': {'infrastructure': 'AWS EKS (Kubernetes)', 'orchestration': 'Horizontal pod autoscaling based on CPU and memory usage, with cluster autoscaling for traffic spikes'}, 'data_management': {'partitioning': 'Sharding by UserID for user data and PhotoID for content data, with replication for high availability', 'consistency_guarantees': 'Hybrid consistency model: causal consistency for feed updates to reduce staleness, strong consistency for critical actions like post creation and messaging'}, 'processed_information': 'The system handles user posts, likes, comments, and messages, generating real-time feed updates, notifications, and chat. It includes services for authentication, feed generation, notifications, messaging, and content moderation. All original functional features were preserved, including real-time chat, feed updates, notifications, and messaging.', 'tech_stack': [{'component': 'Ingestion', 'technology': 'Multi-region API Gateway (Amazon API Gateway)', 'rationale': 'Manages high request volumes and provides throttling and caching, with failover mechanisms for high availability'}, {'component': 'Storage', 'technology': 'Cassandra (NoSQL)', 'rationale': 'Scalable and distributed database for handling high write throughput and eventual consistency'}, {'component': 'Compute', 'technology': 'Kubernetes-managed services', 'rationale': 'Predictable latency for real-time processing of events like likes and comments, avoiding Lambda cold starts'}, {'component': 'Caching', 'technology': 'Redis', 'rationale': 'Reduces latency for frequently accessed data like user feeds and notifications, with persistence mechanisms to prevent data loss'}, {'component': 'Messaging', 'technology': 'WebSocket (API Gateway WebSocket API)', 'rationale': 'Enables real-time bidirectional communication for chat and notifications'}, {'component': 'Event Processing', 'technology': 'Apache Kafka with Dead-Letter Queue (DLQ)', 'rationale': 'Handles real-time event processing and notifications, with DLQ for failed event processing'}], 'request_flows': {'write_request_1': ['User posts content', 'Multi-region API Gateway routes to Post Service', 'Post Service writes to Cassandra and publishes event to Kafka'], 'write_request_2': ['User likes a post', 'Multi-region API Gateway routes to Like Service', 'Like Service updates Cassandra and triggers notification via Kafka'], 'read_request_1': ['User requests feed', 'Multi-region API Gateway routes to Feed Service', 'Feed Service retrieves data from Redis (cache) or Cassandra (fallback)'], 'read_request_2': ['User checks notifications', 'Multi-region API Gateway routes to Notification Service', 'Notification Service fetches from Redis and returns to client']}, 'slo_engineering': {'latency_strategy': 'Edge caching (CloudFront), in-memory caching (Redis), and optimized query patterns to meet P99 latency targets', 'throughput_strategy': 'Auto-scaling for read-heavy services, sharding for write-heavy databases, and load balancing', 'security_compliance': 'OAuth 2.0 for authentication, TLS for encryption, and regular audits for compliance'}, 'connectivity_matrices': [['User', 'Multi-region API Gateway', 'Post Service'], ['User', 'Multi-region API Gateway', 'Feed Service'], ['Post Service', 'Kafka', 'Notification Service'], ['Like Service', 'Kafka', 'Notification Service'], ['Feed Service', 'Redis', 'User'], ['Notification Service', 'WebSocket', 'User']]}


# # 3. Execution
# # We pass 'DiagrammerPromptTemplate' as the first argument
# diagrammer = ArchitectureDiagrammer(prompt=DiagrammerPromptTemplate)
# print(diagrammer.run(test_json))