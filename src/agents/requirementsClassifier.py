# import os
from dotenv import load_dotenv
# # from langchain_openai import ChatOpenAI, OpenAIEmbeddings
# from langchain_community.document_loaders import TextLoader
# from langchain.text_splitter import CharacterTextSplitter
# from langchain_community.vectorstores import FAISS
# from langchain.chains import RetrievalQA
# from langchain_core.output_parsers import JsonOutputParser
# from pydantic import BaseModel, Field
# from typing import List
from src.utils.prompts import RequirementsQuery
from src.utils.models import RequirementModel

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"

load_dotenv()

# Load and process text data
# loader = TextLoader(str(RAW_DATA_DIR / "requirements.txt"))
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
# vectorstore_path = "../../data/db/faiss_index_requirements"
# if os.path.exists(vectorstore_path):
#     print(vectorstore_path)
#     vectorstore = FAISS.load_local(vectorstore_path, embeddings, allow_dangerous_deserialization=True)
#     print("Vector store loaded from disk.")
# else:
#     vectorstore = FAISS.from_documents(docs, embeddings)
#     vectorstore.save_local(vectorstore_path)
#     print(vectorstore_path)
#     print("Vector store created and saved to disk.")



# # Set up retriever and language model
# llm = ChatOpenAI(
#     model="deepseek/deepseek-chat",
#     base_url="https://openrouter.ai/api/v1",
#     api_key=os.getenv("LLM_KEY"),
#     temperature=0.3,
#     max_tokens=1024
# )

# retriever = vectorstore.as_retriever(search_kwargs={"k": 5})  # Retrieve top 3 relevant chunks
# parser = JsonOutputParser(pydantic_object=RequirementModel)
# qa_chain = RetrievalQA.from_chain_type(
#     llm=llm,
#     chain_type="stuff",
#     retriever=retriever
# )
# print("QA chain set up.")


# user_input = "i want to create a social media application"
# prompt = RequirementsQuery.format(query=user_input)

# result = qa_chain.invoke(prompt)



# try:
#     response = parser.parse(result["result"])
#     print("Parsed successfully:")
#     print(response)
# except Exception as e:
#     print(f"Error parsing JSON: {e}")
#     print("Raw result:")
#     print(result["result"])





# class RequirementsRAG:
#     def __init__(
#         self,
#         raw_data_dir: Path,
#         vectorstore_path: str,
#         requirement_model,
#         requirements_prompt,
#         chunk_size: int = 500,
#         chunk_overlap: int = 50,
#         file_name:str="requirements2.txt",
#         k: int = 5,
#     ):
#         self.file_name=file_name
#         self.raw_data_dir = raw_data_dir
#         self.vectorstore_path = vectorstore_path
#         self.requirement_model = requirement_model
#         self.requirements_prompt = requirements_prompt
#         self.chunk_size = chunk_size
#         self.chunk_overlap = chunk_overlap
#         self.k = k

#         self.embeddings = self._init_embeddings()
#         self.vectorstore = self._init_vectorstore()
#         self.llm = self._init_llm()
#         self.retriever = self.vectorstore.as_retriever(
#             search_kwargs={"k": self.k}
#         )
#         self.qa_chain = self._init_qa_chain()
#         self.parser = JsonOutputParser(
#             pydantic_object=self.requirement_model
#         )

#     def _init_embeddings(self):
#         return OpenAIEmbeddings(
#             api_key=os.getenv("LLM_KEY"),
#             base_url="https://openrouter.ai/api/v1",
#             model="text-embedding-ada-002",
#         )

#     def _load_and_split_docs(self):
#         loader = TextLoader(str(self.raw_data_dir /self.file_name ))
#         documents = loader.load()

#         splitter = CharacterTextSplitter(
#             chunk_size=self.chunk_size,
#             chunk_overlap=self.chunk_overlap,
#         )
#         docs = splitter.split_documents(documents)
#         print(f"Loaded {len(docs)} document chunks.")
#         return docs

#     def _init_vectorstore(self):
#         if os.path.exists(self.vectorstore_path):
#             print("Loading vector store from disk...")
#             return FAISS.load_local(
#                 self.vectorstore_path,
#                 self.embeddings,
#                 allow_dangerous_deserialization=True,
#             )

#         print("Creating new vector store...")
#         docs = self._load_and_split_docs()
#         vectorstore = FAISS.from_documents(docs, self.embeddings)
#         vectorstore.save_local(self.vectorstore_path)
#         print("Vector store saved to disk.")
#         return vectorstore

#     def _init_llm(self):
#         return ChatOpenAI(
#             model="deepseek/deepseek-chat",
#             base_url="https://openrouter.ai/api/v1",
#             api_key=os.getenv("LLM_KEY"),
#             temperature=0.3,
#             max_tokens=1024,
#         )

#     def _init_qa_chain(self):
#         return RetrievalQA.from_chain_type(
#             llm=self.llm,
#             chain_type="stuff",
#             retriever=self.retriever,
#         )

#     def generate_requirements(self, user_input: str):
#         prompt = self.requirements_prompt.format(query=user_input)
#         print("generating requirements...")
#         result = self.qa_chain.invoke(prompt)

#         try:
#             return self.parser.parse(result["result"])
#         except Exception as e:
#             raise ValueError(
#                 f"Failed to parse JSON output.\nRaw output:\n{result['result']}"
#             ) from e


# rag = RequirementsRAG(
#     raw_data_dir=RAW_DATA_DIR,
#     vectorstore_path="../../data/db/faiss_index_requirements",
#     requirement_model=RequirementModel,
#     requirements_prompt=RequirementsQuery,
# )

# response = rag.generate_requirements(
#     "I want to create a multiplayer gaming application"
# )

# print(response)








#################################################################################################################################################





import os
import pickle
from pathlib import Path
from langchain_openai import ChatOpenAI,OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
# from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_classic.retrievers import ParentDocumentRetriever
from langchain_classic.storage import InMemoryStore
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain_classic.chains import RetrievalQA
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.document_loaders import TextLoader
# from langch
# from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
# from langchain_community.embeddings import HuggingFaceEmbeddings

class RequirementsRAG:
    def __init__(
        self,
        raw_data_dir: Path,
        vectorstore_path: str,
        requirement_model,
        requirements_prompt,
        file_name: str = "requirements2.txt",
        k: int = 5,
    ):
        self.file_name = file_name
        self.raw_data_dir = raw_data_dir
        self.vectorstore_path = vectorstore_path
        self.requirement_model = requirement_model
        self.requirements_prompt = requirements_prompt
        self.k = k

        # 1. Initialize core components
        self.embeddings = self._init_embeddings()
        self.llm = self._init_llm()
        self.parser = JsonOutputParser(pydantic_object=self.requirement_model)
        
        # 2. Setup Splitters
        self.header_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[("#", "Archetype")])
        self.child_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
        
        # 3. Initialize specialized Parent-Child components
        self.store = InMemoryStore()
        # Initialize an empty or existing vectorstore
        self.vectorstore = self._init_vectorstore_base()
        
        # 4. Initialize specialized Retriever
        self.retriever = ParentDocumentRetriever(
            vectorstore=self.vectorstore,
            docstore=self.store,
            child_splitter=self.child_splitter,
            search_kwargs={"k": self.k}
        )

        # 5. Ingest data (This builds the Parent-Child mapping)
        self._ingest_data()

        # 6. Final Chain setup
        self.qa_chain = self._init_qa_chain()
        self.vectorstore_path="faiss_idx_requirments_2"

    def _init_embeddings(self):
        embeddings = OpenAIEmbeddings(
            model="openai/text-embedding-3-small", # Or your preferred model
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        )
        return embeddings

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

    # def _init_vectorstore_base(self):
    #     """Initializes a blank vectorstore to be managed by the ParentDocumentRetriever."""
    #     # FAISS needs at least one document to initialize if loading is not an option
    #     return FAISS.from_texts(["initialization"], self.embeddings)

    # def _ingest_data(self):
    #     """Handles the manual parent-child ingestion logic."""
    #     file_path = self.raw_data_dir / self.file_name
    #     print(f"Ingesting data from {file_path}...")
        
    #     with open(file_path, "r", encoding="utf-8") as f:
    #         raw_text = f.read()

    #     # Split into parent documents based on Markdown headers
    #     parent_docs = self.header_splitter.split_text(raw_text)
        
    #     # This creates the child chunks and maps them to parents in self.store
    #     self.retriever.add_documents(parent_docs, ids=None)
    #     print(f"Successfully indexed {len(parent_docs)} archetypes.")


    def _init_vectorstore_base(self):
        """Loads vectorstore from disk or initializes a blank one."""
        self.vectorstore_path="faiss_index_requirements_x"
        if os.path.exists(self.vectorstore_path):
            print("Loading existing vectorstore from disk...")
            return FAISS.load_local(
                self.vectorstore_path, 
                self.embeddings, 
                allow_dangerous_deserialization=True # Required for loading FAISS files
            )
        
        print("No vectorstore found. Initializing new one.")
        return FAISS.from_texts(["initialization"], self.embeddings)

    def _ingest_data(self):
        """Ingests data only if the vectorstore is new."""
        store_file = Path(self.vectorstore_path) / "parent_store.pkl"
        
        # Check if we already have data
        if os.path.exists(self.vectorstore_path) and store_file.exists():
            print("Loading parent documents from disk...")
            with open(store_file, "rb") as f:
                full_dict = pickle.load(f)
                # Re-populate the InMemoryStore
                self.store.mset(list(full_dict.items()))
            return

        # Otherwise, perform the ingestion
        file_path = self.raw_data_dir / self.file_name
        print(f"Ingesting data from {file_path}...")
        
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        parent_docs = self.header_splitter.split_text(raw_text)
        self.retriever.add_documents(parent_docs)
        
        # --- SAVE TO DISK ---
        # 1. Save the FAISS index
        self.vectorstore.save_local(self.vectorstore_path)
        
        # 2. Save the Parent Store (InMemoryStore)
        os.makedirs(self.vectorstore_path, exist_ok=True)
        with open(store_file, "wb") as f:
            # We access the underlying dict of the InMemoryStore to pickle it
            pickle.dump(self.store.store, f)
            
        print(f"Successfully indexed and saved to {self.vectorstore_path}")

    def _init_qa_chain(self):
        return RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            return_source_documents=True 
        )

    def generate_requirements(self, user_input: str):
        # We format the prompt with the query
        formatted_prompt = self.requirements_prompt.format(query=user_input)
        print("Generating requirements via Parent-Child RAG...")
        
        # RetrievalQA handles the context injection from our specialized retriever
        result = self.qa_chain.invoke(formatted_prompt)

        try:
            # result["result"] contains the LLM output string
            return self.parser.parse(result["result"])
        except Exception as e:
            raise ValueError(
                f"Failed to parse JSON output.\nRaw output:\n{result['result']}"
            ) from e
        

# rag = RequirementsRAG(
#     raw_data_dir=RAW_DATA_DIR,
#     vectorstore_path="../../data/db/faiss_index_requirements",
#     requirement_model=RequirementModel,
#     requirements_prompt=RequirementsQuery,
# )

# response = rag.generate_requirements(
#     "I want to create a multiplayer gaming application"
# )

# print(response)