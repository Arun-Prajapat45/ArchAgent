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

    return {
        "thread_id": thread_id,
        "output_requirements": requirements_md,
        "output_design": design_md,
        "output_code": final_state["output_code"],
    }