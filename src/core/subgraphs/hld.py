from typing import TypedDict,Literal
from langgraph.graph import StateGraph, START,END
from pathlib import Path
from src.agents.hldCritic import SystemDesignCriticRAG
from src.agents.hldEngine import SystemDesignRAG
from src.utils.models import SystemDesignSchema,CriticReview,RequirementModel
from src.utils.prompts import DesignGeneratorTemplate,DesignUpdateTemplate,CriticPromptTemplate


ROOT_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"



# 1. Fixed the typos in the State definition
class hldState(TypedDict):
    generator: SystemDesignRAG
    critic: SystemDesignCriticRAG
    goal: RequirementModel
    num_iterations: int  # Fixed spelling
    base_summary: str
    generator_output: SystemDesignSchema
    critic_output: CriticReview

def _init(state: hldState) -> dict: # Return dict, not hldState object
    """Initialize objects and return only the new keys."""
    return {
        "generator": SystemDesignRAG(
            raw_data_dir=RAW_DATA_DIR,
            vectorstore_path="../../data/db/faiss_index_design",
        ),
        "critic": SystemDesignCriticRAG(
            raw_data_dir=RAW_DATA_DIR,
            vectorstore_path="../../data/db/faiss_index_critic",
        ),
        "num_iterations": 0
    }

def Design(state: hldState) -> dict:
    """Build or update the design."""
    current_iteration = state.get('num_iterations', 0) + 1
    
    if current_iteration == 1:
        print("creating first design...")
        output = state['generator'].generate_design(state['goal'])
    else:
        print(f"update the design... iteration:{current_iteration}",current_iteration)
        output = state['generator'].update_design(
            state['goal'], 
            state['generator_output'], 
            state['critic_output']
        )
    
    return {
        "generator_output": output,
        "num_iterations": current_iteration
    }

def evaluate(state: hldState) -> dict:
    """Review the design."""
    print("reviewing design...")
    review = state['critic'].review_design(state['generator_output'])
    return {"critic_output": review}

def should_continue(state: hldState) -> Literal["continue", "end"]:
    # Use the consistent variable name here
    if state["num_iterations"] >= 3:
        return "end"
    return "continue"

    


def hldBuilder():
    workflow=StateGraph(hldState);
    workflow.add_node("init",_init)
    workflow.add_node("evaluate",evaluate)
    workflow.add_node("design",Design)
    workflow.add_edge(START,"init")
    workflow.add_conditional_edges(
        "init",
        should_continue,
        {
            "continue":"design",
            "end":END
        }
    )
    return workflow.compile()



# specs = {'identification': {'archetype': 'Real-time interactive low-latency systems', 'knowledge_references': ['WebSockets', 'gRPC', 'in-memory databases', 'pub-sub messaging']}, 'strategic_8_metrics': {'users': {'persona': 'Social media users', 'count': '100,000 to 1,000,000 concurrent users'}, 'core_action': 'Posting, liking, commenting, and real-time interactions', 'io_contract': {'input': ['User posts', 'Likes', 'Comments', 'Messages'], 'output': ['Feed updates', 'Notifications', 'Real-time chat']}, 'data_load': {'daily_ingestion': '10-100 TB', 'total_storage_5yr': '10-100 PB'}, 'throughput': {'avg_rps': 5000, 'peak_rps': 50000}, 'read_write_ratio': '70:30', 'consistency_model': 'Eventual consistency with strong consistency for critical actions', 'sla_slo': {'availability': '99.99%', 'latency_p99': '50ms'}}, 'requirements_summary': {'functional': ['User authentication and authorization', 'Real-time feed updates', 'Notifications', 'Messaging', 'Content moderation'], 'non_functional': ['Low latency', 'High availability', 'Scalability', 'Security', 'Resilience to traffic spikes']}, 'technical_taxonomy': ['WebSockets', 'gRPC', 'Redis', 'Kafka', 'Microservices', 'CDN', 'Edge computing']}


# hldS={
#     "goal":specs
# }

# graph=hldBuilder()

# hldFinalState=graph.invoke(hldS)
# print(hldFinalState['generator_output'])

