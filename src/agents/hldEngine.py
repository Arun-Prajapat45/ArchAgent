# import os
# from dotenv import load_dotenv
# from langchain_openai import ChatOpenAI, OpenAIEmbeddings
# from langchain.prompts import ChatPromptTemplate
# from langchain.document_loaders import TextLoader
# from langchain.text_splitter import CharacterTextSplitter
# from langchain.vectorstores import FAISS
# from langchain.chains import RetrievalQA
# from langchain_core.output_parsers import JsonOutputParser
# from pydantic import BaseModel, Field
# from ..utils.models import SystemDesignSchema
# from ..utils.prompts import DesignGeneratorTemplate
# # from typing import List
# import json
# # from pydantic import BaseModel
# from typing import List, Dict, Optional


# from pathlib import Path


# load_dotenv()



# # Load and process text data
# loader = TextLoader(str(RAW_DATA_DIR / "combined.txt"))

# documents = loader.load()

# text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
# docs = text_splitter.split_documents(documents)

# print(f"Loaded {len(docs)} document chunks.")


# # Create embeddings and vector store
# embeddings = OpenAIEmbeddings(
#     api_key=os.getenv("LLM_KEY"),
#     base_url="https://openrouter.ai/api/v1",
#     model="text-embedding-ada-002"  # Assuming OpenRouter supports this
# )

# # Check if vectorstore already exists on disk
# vectorstore_path="../../data/db/faiss_index_design"
# if os.path.exists(vectorstore_path):
#     vectorstore = FAISS.load_local(vectorstore_path, embeddings, allow_dangerous_deserialization=True)
#     print("Vector store loaded from disk.")
# else:
#     vectorstore = FAISS.from_documents(docs, embeddings)
#     vectorstore.save_local(vectorstore_path)
#     print("Vector store created and saved to disk.")


# # Set up retriever and language model
# llm = ChatOpenAI(
#     model="deepseek/deepseek-chat",
#     base_url="https://openrouter.ai/api/v1",
#     api_key=os.getenv("LLM_KEY"),
#     temperature=0.3,
#     max_tokens=1024
# )

# retriever = vectorstore.as_retriever(search_kwargs={"k": 3})  # Retrieve top 3 relevant chunks
# parser = JsonOutputParser(pydantic_object=SystemDesignSchema)
# qa_chain = RetrievalQA.from_chain_type(
#     llm=llm,
#     chain_type="stuff",
#     retriever=retriever
# )
# print("QA chain set up.")




# prompt = DesignGeneratorTemplate.format(
#     archetype=specs["identification"]["archetype"],
#     core_action=specs["strategic_8_metrics"]["core_action"],
#     input=json.dumps(
#         specs["strategic_8_metrics"]["io_contract"]["input"],
#         indent=2
#     ),
#     output=json.dumps(
#         specs["strategic_8_metrics"]["io_contract"]["output"],
#         indent=2
#     ),
#     read_write_ratio=specs["strategic_8_metrics"]["read_write_ratio"],
#     consistency_model=specs["strategic_8_metrics"]["consistency_model"],
#     functional=json.dumps(
#         specs["requirements_summary"]["functional"],
#         indent=2
#     ),
#     non_functional=json.dumps(
#         specs["requirements_summary"]["non_functional"],
#         indent=2
#     )
# )

# # print(prompt)

# result = qa_chain.invoke(prompt)

# retrieved_docs = retriever.invoke(prompt)

# # print("Fetched documents:")
# # for doc in retrieved_docs:
# #     print(doc.page_content)
# #     print("---")

# # result = qa_chain.invoke(prompt)


# try:
#     response = parser.parse(result["result"])
#     print("Parsed successfully:")
#     print(response)
#     # print(result)
# except Exception as e:
#     print(f"Error parsing JSON: {e}")
#     print("Raw result:")
#     print(result["result"])


# import os
import json
from pathlib import Path
# from dotenv import load_dotenv

# from langchain_openai import ChatOpenAI, OpenAIEmbeddings
# from langchain_community.document_loaders import TextLoader
# from langchain.text_splitter import CharacterTextSplitter
# from langchain_community.vectorstores import FAISS
# from langchain.chains import RetrievalQA
# from langchain_core.output_parsers import JsonOutputParser


import os
from dotenv import load_dotenv

# 1. Partner Packages (Vendor-specific logic)
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# 2. Core (Abstract interfaces and LCEL)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

# 3. Community (Third-party integrations like FAISS and Loaders)
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS

# 4. Text Splitters (Moved to a dedicated package)
from langchain_text_splitters import CharacterTextSplitter, MarkdownHeaderTextSplitter

# OLD: from langchain.chains import RetrievalQA
# NEW (v1.0 compatibility):
from langchain_classic.chains import RetrievalQA
from langchain_classic.chains.retrieval import create_retrieval_chain

from ..utils.models import SystemDesignSchema
from ..utils.prompts import DesignGeneratorTemplate, DesignUpdateTemplate
ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"

load_dotenv()


class SystemDesignRAG:
    def __init__(
        self,
        raw_data_dir: Path,
        vectorstore_path: str,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        top_k: int = 3,
    ):
        self.raw_data_dir = raw_data_dir
        self.vectorstore_path = vectorstore_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.top_k = top_k

        self.embeddings = self._init_embeddings()
        self.vectorstore = self._init_vectorstore()
        self.llm = self._init_llm()
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": self.top_k}
        )
        self.qa_chain = self._init_qa_chain()
        self.parser = JsonOutputParser(
            pydantic_object=SystemDesignSchema
        )

    # -------------------- Initialization --------------------

    def _init_embeddings(self):
        return GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001", # ✅ Stable and supported
            google_api_key=os.getenv("GEMINI_KEY"),
            task_type="retrieval_document"
        )

    def _load_and_split_docs(self):
        loader = TextLoader(str(self.raw_data_dir / "combined.txt"))
        documents = loader.load()
        headers_to_split_on = [
            ("#", "Header 1"),
        ]

        markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        docs = markdown_splitter.split_text(documents[0].page_content)
        # docs = splitter.split_documents(documents)
        print(f"Loaded {len(docs)} document chunks.")
        return docs

    def _init_vectorstore(self):
        if os.path.exists(self.vectorstore_path):
            print("Loading vector store from disk...")
            return FAISS.load_local(
                self.vectorstore_path,
                self.embeddings,
                allow_dangerous_deserialization=True,
            )

        print("Creating vector store...")
        docs = self._load_and_split_docs()
        vectorstore = FAISS.from_documents(docs, self.embeddings)
        vectorstore.save_local(self.vectorstore_path)
        print("Vector store created and saved.")
        return vectorstore

    def _init_llm(self):
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            api_key=os.getenv("GEMINI_KEY"),
            temperature=0
        )


    def _init_qa_chain(self):
        return RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
        )

    # -------------------- Public API --------------------

    def generate_design(self, specs: dict):
        """
        Generates a system design JSON from structured specs.
        Returns a validated SystemDesignSchema object.
        """

        prompt = DesignGeneratorTemplate.format(
            archetype=specs["identification"]["archetype"],
            core_action=specs["strategic_8_metrics"]["core_action"],
            input=json.dumps(
                specs["strategic_8_metrics"]["io_contract"]["input"],
                indent=2,
            ),
            output=json.dumps(
                specs["strategic_8_metrics"]["io_contract"]["output"],
                indent=2,
            ),
            read_write_ratio=specs["strategic_8_metrics"]["read_write_ratio"],
            consistency_model=specs["strategic_8_metrics"]["consistency_model"],
            functional=json.dumps(
                specs["requirements_summary"]["functional"],
                indent=2,
            ),
            non_functional=json.dumps(
                specs["requirements_summary"]["non_functional"],
                indent=2,
            ),
        )

        result = self.qa_chain.invoke(prompt)

        try:
            return self.parser.parse(result["result"])
        except Exception as e:
            raise ValueError(
                "Failed to parse system design JSON.\n"
                f"Raw output:\n{result['result']}"
            ) from e
    

    def update_design(
        self,
        user_input: dict,
        hld_output_json: dict,
        critic_feedback_json: dict
    ):
        """
        Updates an existing system design based on user input, 
        initial HLD output, and critic feedback.
        
        Args:
            user_input: Original user specifications/requirements
            hld_output_json: The initial high-level design output
            critic_feedback_json: Feedback from the critic review
            
        Returns:
            A validated SystemDesignSchema object with the updated design
        """
        
        prompt = DesignUpdateTemplate.format(
            user_input=user_input,
            hld_output_json=hld_output_json,
            critic_feedback_json=critic_feedback_json
        )
        
        result = self.qa_chain.invoke(prompt)
        
        try:
            parsed_result = self.parser.parse(result["result"])
            print("Parsed successfully:")
            return parsed_result
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            print("Raw result:")
            print(result["result"])
            raise ValueError(
                "Failed to parse updated system design JSON.\n"
                f"Raw output:\n{result['result']}"
            ) from e





# rag = SystemDesignRAG(
#     raw_data_dir=RAW_DATA_DIR,
#     vectorstore_path="../../data/db/faiss_index_design",
# )
# specs={
#     "identification": {
#         "archetype": "arch_02",
#         "knowledge_references": [
#             "horizontal scaling",
#             "WebSockets",
#             "gRPC",
#             "Pub-Sub"
#         ]
#     },
#     "strategic_8_metrics": {
#         "users": {
#             "persona": "general public",
#             "count": "100k+ concurrent users"
#         },
#         "core_action": "real-time bidirectional communication",
#         "io_contract": {
#             "input": [
#                 "user posts",
#                 "messages",
#                 "media uploads"
#             ],
#             "output": [
#                 "feed updates",
#                 "notifications",
#                 "chat messages"
#             ]
#         },
#         "data_load": {
#             "daily_ingestion": "10TB+",
#             "total_storage_5yr": "PB scale"
#         },
#         "throughput": {
#             "avg_rps": 50000,
#             "peak_rps": 200000
#         },
#         "read_write_ratio": "50: 50",
#         "consistency_model": "eventual consistency with strong consistency for critical paths",
#         "sla_slo": {
#             "availability": "99.99%",
#             "latency_p99": "<50ms"
#         }
#     },
#     "requirements_summary": {
#         "functional": [
#             "real-time feed updates",
#             "direct messaging",
#             "media sharing",
#             "user authentication"
#         ],
#         "non_functional": [
#             "horizontal scalability",
#             "low-latency bidirectional communication",
#             "high availability",
#             "secure user data handling"
#         ]
#     },
#     "technical_taxonomy": [
#         "WebSockets",
#         "gRPC",
#         "In-memory DBs",
#         "Pub-Sub"
#     ]
# }

# design = rag.generate_design(specs)
# print(design)
# specs = {'identification': {'archetype': 'Real-time interactive low-latency systems', 'knowledge_references': ['WebSockets', 'gRPC', 'in-memory databases', 'pub-sub messaging']}, 'strategic_8_metrics': {'users': {'persona': 'Social media users', 'count': '100,000 to 1,000,000 concurrent users'}, 'core_action': 'Posting, liking, commenting, and real-time interactions', 'io_contract': {'input': ['User posts', 'Likes', 'Comments', 'Messages'], 'output': ['Feed updates', 'Notifications', 'Real-time chat']}, 'data_load': {'daily_ingestion': '10-100 TB', 'total_storage_5yr': '10-100 PB'}, 'throughput': {'avg_rps': 5000, 'peak_rps': 50000}, 'read_write_ratio': '70:30', 'consistency_model': 'Eventual consistency with strong consistency for critical actions', 'sla_slo': {'availability': '99.99%', 'latency_p99': '50ms'}}, 'requirements_summary': {'functional': ['User authentication and authorization', 'Real-time feed updates', 'Notifications', 'Messaging', 'Content moderation'], 'non_functional': ['Low latency', 'High availability', 'Scalability', 'Security', 'Resilience to traffic spikes']}, 'technical_taxonomy': ['WebSockets', 'gRPC', 'Redis', 'Kafka', 'Microservices', 'CDN', 'Edge computing']}
# specs={}













############################################################################################################
#############################################################################################












# critic_review={'critical_fixes_required': [{'location': 'Data Management', 'issue': 'Eventual consistency for feed updates may lead to stale data in high-traffic scenarios, impacting user experience.', 'remediation': 'Consider hybrid consistency models (e.g., causal consistency) or introduce a short-lived cache for feed updates to reduce staleness.'}, {'location': 'Tech Stack - Compute', 'issue': 'AWS Lambda may introduce cold start latency, affecting real-time processing for likes and comments.', 'remediation': 'Use provisioned concurrency for critical Lambda functions or replace with Kubernetes-managed services for predictable latency.'}, {'location': 'Connectivity Matrices', 'issue': 'API Gateway is a single point of failure (SPOF) for all user requests.', 'remediation': 'Implement multi-region API Gateway deployments with failover mechanisms or use a distributed API gateway solution.'}], 'warnings': ['Consider adding a dead-letter queue (DLQ) in Kafka for handling failed event processing.', 'Evaluate Redis persistence mechanisms to prevent data loss during failures.', 'Add detailed monitoring for Cassandra shard distribution to detect hot shards early.'], 'validated_components': ['Microservices architecture style for independent scaling and fault isolation.', 'gRPC for internal service-to-service communication due to its low latency and efficiency.', 'Sharding by UserID and PhotoID for scalable data partitioning.', 'Redis caching for reducing latency in feed and notification retrieval.'], 'functional_checklist': {'Data Integrity': 'Pass - Eventual consistency is acceptable for feed updates, but remediation is suggested for edge cases.', 'Flow Logic': 'Pass - Tech stack components align with request flows as described.', 'Infrastructure': 'Pass - Auto-scaling and sharding strategies meet high RPS/throughput requirements.', 'Security': 'Pass - OAuth 2.0, TLS, and regular audits provide robust security.', 'Bottlenecks': 'Fail - API Gateway is identified as a SPOF; remediation is required.'}}




# temp_hld_output={
#   "system_name": "Real-Time Social Media Platform",
  
#   "system_architecture_style": {
#     "pattern": "Microservices",
#     "rationale": "Microservices allow independent scaling of components like feed generation, notifications, and messaging, which is critical for handling the high read/write ratio and ensuring low latency."
#   },
#   "communication_strategy": {
#     "internal_comms": "gRPC for service-to-service communication due to its low latency and high performance",
#     "async_logic": "Apache Kafka for real-time event processing and notifications"
#   },
#   "deployment_strategy": {
#     "infrastructure": "AWS EKS (Kubernetes)",
#     "orchestration": "Horizontal pod autoscaling based on CPU and memory usage, with cluster autoscaling for traffic spikes"
#   },
#   "data_management": {
#     "partitioning": "Sharding by UserID for user data and PhotoID for content data, with replication for high availability",
#     "consistency_guarantees": "Eventual consistency for feed updates, strong consistency for critical actions like post creation and messaging"
#   },
#   "processed_information": "The system handles user posts, likes, comments, and messages, generating real-time feed updates, notifications, and chat. It includes services for authentication, feed generation, notifications, messaging, and content moderation.",
#   "tech_stack": [
#     {
#       "component": "Ingestion",
#       "technology": "API Gateway (Amazon API Gateway)",
#       "rationale": "Manages high request volumes and provides throttling and caching"
#     },
#     {
#       "component": "Storage",
#       "technology": "Cassandra (NoSQL)",
#       "rationale": "Scalable and distributed database for handling high write throughput and eventual consistency"
#     },
#     {
#       "component": "Compute",
#       "technology": "AWS Lambda (Serverless)",
#       "rationale": "Efficiently scales for real-time processing of events like likes and comments"
#     },
#     {
#       "component": "Caching",
#       "technology": "Redis",
#       "rationale": "Reduces latency for frequently accessed data like user feeds and notifications"
#     },
#     {
#       "component": "Messaging",
#       "technology": "WebSocket (API Gateway WebSocket API)",
#       "rationale": "Enables real-time bidirectional communication for chat and notifications"
#     }
#   ],
#   "request_flows": {
#     "write_request_1": [
#       "User posts content",
#       "API Gateway routes to Post Service",
#       "Post Service writes to Cassandra and publishes event to Kafka"
#     ],
#     "write_request_2": [
#       "User likes a post",
#       "API Gateway routes to Like Service",
#       "Like Service updates Cassandra and triggers notification via Kafka"
#     ],
#     "read_request_1": [
#       "User requests feed",
#       "API Gateway routes to Feed Service",
#       "Feed Service retrieves data from Redis (cache) or Cassandra (fallback)"
#     ],
#     "read_request_2": [
#       "User checks notifications",
#       "API Gateway routes to Notification Service",
#       "Notification Service fetches from Redis and returns to client"
#     ]
#   },
#   "slo_engineering": {
#     "latency_strategy": "Edge caching (CloudFront), in-memory caching (Redis), and optimized query patterns to meet P99 latency targets",
#     "throughput_strategy": "Auto-scaling for read-heavy services, sharding for write-heavy databases, and load balancing",
#     "security_compliance": "OAuth 2.0 for authentication, TLS for encryption, and regular audits for compliance"
#   },
#   "connectivity_matrices": [
#     ["User", "API Gateway", "Post Service"],
#     ["User", "API Gateway", "Feed Service"],
#     ["Post Service", "Kafka", "Notification Service"],
#     ["Like Service", "Kafka", "Notification Service"],
#     ["Feed Service", "Redis", "User"],
#     ["Notification Service", "WebSocket", "User"]
#   ]
# }


# DesignUpdateTemplate.format(user_input=specs,hld_output_json=temp_hld_output,critic_feedback_json=critic_review)

# Load and process text data
# loader = TextLoader(str(RAW_DATA_DIR / "combined.txt"))
# documents = loader.load()

# text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
# docs = text_splitter.split_documents(documents)

# print(f"Loaded {len(docs)} document chunks.")

# # Create embeddings and vector store
# embeddings = OpenAIEmbeddings(
#     api_key=os.getenv("LLM_KEY"),
#     base_url="https://openrouter.ai/api/v1",
#     model="text-embedding-ada-002"  # Assuming OpenRouter supports this
# )

# # Check if vectorstore already exists on disk
# vectorstore_path = "faiss_index_hld"
# if os.path.exists(vectorstore_path):
#     vectorstore = FAISS.load_local(vectorstore_path, embeddings, allow_dangerous_deserialization=True)
#     print("Vector store loaded from disk.")
# else:
#     vectorstore = FAISS.from_documents(docs, embeddings)
#     vectorstore.save_local(vectorstore_path)
#     print("Vector store created and saved to disk.")

# llm = ChatOpenAI(
#     model="deepseek/deepseek-chat",
#     base_url="https://openrouter.ai/api/v1",
#     api_key=os.getenv("LLM_KEY"),
#     temperature=0.3,
#     max_tokens=1024
# )

# retriever = vectorstore.as_retriever(search_kwargs={"k": 3})  # Retrieve top 3 relevant chunks
# parser = JsonOutputParser(pydantic_object=SystemDesignSchema)
# qa_chain = RetrievalQA.from_chain_type(
#     llm=llm,
#     chain_type="stuff",
#     retriever=retriever
# )
# result = qa_chain.invoke(DesignUpdateTemplate)

# try:
#     # response = parser.parse(result["result"])
#     print("Parsed successfully:")
#     print(result['result'])
#     # print(result)
# except Exception as e:
#     print(f"Error parsing JSON: {e}")
#     print("Raw result:")
#     print(result["result"])


# rag = SystemDesignRAG(
#     raw_data_dir=RAW_DATA_DIR,
#     vectorstore_path="../../data/db/faiss_index_design",
# )


# design = rag.update_design(specs,temp_hld_output,critic_review)

# print(design)