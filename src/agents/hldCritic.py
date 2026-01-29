# import os
# from dotenv import load_dotenv
# from langchain_openai import ChatOpenAI, OpenAIEmbeddings
# from langchain_community.document_loaders import TextLoader
# from langchain.text_splitter import CharacterTextSplitter
# from langchain_community.vectorstores import FAISS
# from langchain.chains import RetrievalQA
# from langchain_core.output_parsers import JsonOutputParser
# from pydantic import BaseModel, Field
# from typing import List
# import json
# from pydantic import BaseModel, Field
# from typing import List
# from ..utils.models import CriticReview
# from ..utils.prompts import CriticPromptTemplate
# from pathlib import Path


# ROOT_DIR = Path(__file__).resolve().parents[2]
# DATA_DIR = ROOT_DIR / "data"
# RAW_DATA_DIR = DATA_DIR / "raw"




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
# vectorstore_path="../../data/db/faiss_index_critic"
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
# # parser = JsonOutputParser(pydantic_object=ExpectedOutput)
# qa_chain = RetrievalQA.from_chain_type(
#     llm=llm,
#     chain_type="stuff",
#     retriever=retriever
# )
# print("QA chain set up.")



# 

# parser = JsonOutputParser(pydantic_object=CriticReview)

# prompt=CriticPromptTemplate.format(
#     hld_json=json.dumps(hld_json, indent=2)
# )


# result = qa_chain.invoke(prompt)

# retrieved_docs = retriever.invoke(prompt)

# # print("Fetched documents:")
# # for doc in retrieved_docs:
# #     print(doc.page_content)
# #     print("---")

# # # result = qa_chain.invoke(prompt)


# try:
#     response = parser.parse(result['result'])
#     print("Parsed successfully:")
#     print(response)
#     print("\n=== Detailed Review ===")
#     print(f"Data Integrity: {response['data_integrity']}\n")
#     print(f"Flow Logic: {response['flow_logic']}\n")
#     # print(f"Infrastructure: {response.infrastructure}\n")
#     # print(f"Security: {response.security}\n")
#     # print(f"Bottlenecks & Chokepoints: {response.bottlenecks_chokepoints}\n")
#     # print(f"Summary: {response.summary}\n")
# except Exception as e:
#     print(f"Error parsing JSON: {e}")
#     print("Raw result:")
#     print(result["result"])



import os
import json
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI,OpenAIEmbeddings
# from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_classic.chains import RetrievalQA
from langchain_core.output_parsers import JsonOutputParser
from langchain_classic.chains.retrieval import create_retrieval_chain
# from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
# from langchain_community.embeddings import HuggingFaceEmbeddings

from ..utils.models import CriticReview
from ..utils.prompts import CriticPromptTemplate

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"


load_dotenv()


class SystemDesignCriticRAG:
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
            pydantic_object=CriticReview
        )
        self.vectorstore_path="faiss_index_hld_x"

    # -------------------- Initialization --------------------

    def _init_embeddings(self):
        embeddings = OpenAIEmbeddings(
            model="openai/text-embedding-3-small", # Or your preferred model
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        )
        return embeddings

    def _load_and_split_docs(self):
        loader = TextLoader(str(self.raw_data_dir / "combined.txt"))
        documents = loader.load()

        splitter = CharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )
        docs = splitter.split_documents(documents)
        print(f"Loaded {len(docs)} document chunks.")
        return docs

    def _init_vectorstore(self):
        
        if os.path.exists(self.vectorstore_path):
            print("Loading critic vector store from disk...")
            return FAISS.load_local(
                self.vectorstore_path,
                self.embeddings,
                allow_dangerous_deserialization=True,
            )

        print("Creating critic vector store...")
        docs = self._load_and_split_docs()
        vectorstore = FAISS.from_documents(docs, self.embeddings)
        vectorstore.save_local(self.vectorstore_path)
        print("Critic vector store created and saved.")
        return vectorstore

    def _init_llm(self):
        return ChatOpenAI(
            # The specific ID for the free version on OpenRouter
            model="meta-llama/llama-3.3-70b-instruct:free", 
            
            # Your OpenRouter API Key
            api_key=os.getenv("OPENROUTER_API_KEY"),
            
            # Point LangChain to OpenRouter's servers
            base_url="https://openrouter.ai/api/v1",
            
            # Model specific settings
            temperature=0.15 # Recommended for Trinity Mini
        )

    def _init_qa_chain(self):
        return RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
        )

    # -------------------- Public API --------------------

    def review_design(self, hld_json: dict) -> CriticReview:
        """
        Reviews a system design HLD JSON and returns a structured critique.
        """

        prompt = CriticPromptTemplate.format(
            hld_json=json.dumps(hld_json, indent=2)
        )

        result = self.qa_chain.invoke(prompt)

        try:
            return self.parser.parse(result["result"])
        except Exception as e:
            raise ValueError(
                "Failed to parse critic JSON output.\n"
                f"Raw output:\n{result['result']}"
            ) from e



# hld_json={
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



# critic = SystemDesignCriticRAG(
#     raw_data_dir=RAW_DATA_DIR,
#     vectorstore_path="../../data/db/faiss_index_critic",
# )

# review = critic.review_design(hld_json)

# print("Parsed successfully:")
# print(review)

# print("\n=== Detailed Review ===")
# # print(f"Data Integrity: {review['data_integrity']}\n")
# # print(f"Flow Logic: {['review.flow_logic']}\n")
