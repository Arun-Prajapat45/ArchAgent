import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List
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





class RequirementsRAG:
    def __init__(
        self,
        raw_data_dir: Path,
        vectorstore_path: str,
        requirement_model,
        requirements_prompt,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        file_name:str="requirements.txt",
        k: int = 5,
    ):
        self.file_name=file_name
        self.raw_data_dir = raw_data_dir
        self.vectorstore_path = vectorstore_path
        self.requirement_model = requirement_model
        self.requirements_prompt = requirements_prompt
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.k = k

        self.embeddings = self._init_embeddings()
        self.vectorstore = self._init_vectorstore()
        self.llm = self._init_llm()
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": self.k}
        )
        self.qa_chain = self._init_qa_chain()
        self.parser = JsonOutputParser(
            pydantic_object=self.requirement_model
        )

    def _init_embeddings(self):
        return OpenAIEmbeddings(
            api_key=os.getenv("LLM_KEY"),
            base_url="https://openrouter.ai/api/v1",
            model="text-embedding-ada-002",
        )

    def _load_and_split_docs(self):
        loader = TextLoader(str(self.raw_data_dir /self.file_name ))
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
            print("Loading vector store from disk...")
            return FAISS.load_local(
                self.vectorstore_path,
                self.embeddings,
                allow_dangerous_deserialization=True,
            )

        print("Creating new vector store...")
        docs = self._load_and_split_docs()
        vectorstore = FAISS.from_documents(docs, self.embeddings)
        vectorstore.save_local(self.vectorstore_path)
        print("Vector store saved to disk.")
        return vectorstore

    def _init_llm(self):
        return ChatOpenAI(
            model="deepseek/deepseek-chat",
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("LLM_KEY"),
            temperature=0.3,
            max_tokens=1024,
        )

    def _init_qa_chain(self):
        return RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
        )

    def generate_requirements(self, user_input: str):
        prompt = self.requirements_prompt.format(query=user_input)
        print("generating requirements...")
        result = self.qa_chain.invoke(prompt)

        try:
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
