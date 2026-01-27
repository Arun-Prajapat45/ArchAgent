from langgraph.graph import StateGraph,START,END
from typing import TypedDict
from src.utils.models import RequirementModel,SystemDesignSchema
from src.core.subgraphs.diagram import diagramBuilder
from src.core.subgraphs.hld import hldBuilder
from src.core.subgraphs.requirements import requirementBuilder

class mainState(TypedDict):
    user_input:str
    system_requirements:RequirementModel
    system_design:SystemDesignSchema
    output_code:str


def init(state:mainState):
    user_input=input("enter your project description:")
    
    return {"user_input":user_input}


def gatherRequirements(state:mainState):
    intial_state={
        "user_input":state['user_input']
    }

    graph=requirementBuilder()
    final_state=graph.invoke(intial_state)
    return {"system_requirements":final_state['output_model']}

def createDesign(state:mainState):
    hldS={
        "goal":state['system_requirements']
    }

    graph=hldBuilder()

    hldFinalState=graph.invoke(hldS)
    # print(hldFinalState['generator_output'])
    return {"system_design":hldFinalState['generator_output']}

def createDiagram(state:mainState):
    graph=diagramBuilder()

    intial_state={
        "input_design":state['system_design']
    }

    final_state=graph.invoke(intial_state)

    return {"output_code":final_state['output_code']}

def builder():
    workflow=StateGraph(mainState)
    workflow.add_node("init",init)
    workflow.add_node("create_design",createDesign)
    workflow.add_node("gather_requirements",gatherRequirements)
    workflow.add_node("create_diagram",createDiagram)
    workflow.add_edge(START,"init")
    workflow.add_edge("init","gather_requirements")
    workflow.add_edge("gather_requirements","create_design")
    workflow.add_edge("create_design","create_diagram")
    workflow.add_edge("create_diagram",END)

    return workflow.compile()


graph=builder()

initial_state={
    
}

final_state=graph.invoke(initial_state)

print("____________________________________________")
print("requirements:",final_state['system_requirements'])
print("____________________________________________")
print("design:",final_state['system_design'])
print("____________________________________________")
print("code:",final_state['output_code'])
