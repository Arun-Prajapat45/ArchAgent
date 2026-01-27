from typing import TypedDict
from langgraph.graph import StateGraph, START,END
from pathlib import Path
from src.utils.models import RequirementModel
from src.utils.prompts import RequirementsQuery
from src.agents.requirementsClassifier import RequirementsRAG


ROOT_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"

class RequirementsState(TypedDict):
    """Requirements State"""
    vectorstore_path: str
    output_model: RequirementModel
    file_name:str
    user_input:str
    model:RequirementsRAG



def _init(state: RequirementsState):
    state['model']=RequirementsRAG(
        raw_data_dir=RAW_DATA_DIR,
        vectorstore_path="../../data/db/faiss_index_requirements",
        requirement_model=RequirementModel,
        requirements_prompt=RequirementsQuery,
    )
    return state

def generate(state: RequirementsState)->RequirementsState:
    output=state['model'].generate_requirements(state['user_input'])
    state['output_model']=output
    return state

def requirementBuilder():
    workflow=StateGraph(RequirementsState)
    workflow.add_node("init",_init)
    workflow.add_node("generate",generate)

    workflow.add_edge(START,"init")
    workflow.add_edge("init","generate")
    workflow.add_edge("generate",END)
    return workflow.compile()


intial_state:RequirementsState={
    "user_input":"i want to create a social media application, with feeds, posts, likes and messages and payment system integrated!"
}

graph=requirementBuilder()
final_state=graph.invoke(intial_state)

print(final_state['output_model'])