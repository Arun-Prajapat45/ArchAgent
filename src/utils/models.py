from pydantic import BaseModel, Field
from typing import List, Optional


##########################################################################
### for requirements Classifier #########################################
#########################################################################

class RequirementModel(BaseModel):
    class Identification(BaseModel):
        archetype: str = Field(description="The architectural pattern (e.g., API gateway–centric)")
        knowledge_references: List[str] = Field(description="List of domain references")

    class Strategic8Metrics(BaseModel):
        class Users(BaseModel):
            persona: str = Field(description="Types of users")
            count: str = Field(description="Volume of users")

        class IOContract(BaseModel):
            input: List[str] = Field(description="Inputs required by the system")
            output: List[str] = Field(description="Outputs produced by the system")

        class DataLoad(BaseModel):
            daily_ingestion: str = Field(description="Daily data volume")
            total_storage_5yr: str = Field(description="5-year projected storage")

        class Throughput(BaseModel):
            avg_rps: int = Field(description="Average Requests Per Second")
            peak_rps: int = Field(description="Peak Requests Per Second")

        class SLASLO(BaseModel):
            availability: str = Field(description="Uptime SLA")
            latency_p99: str = Field(description="P99 Latency SLO")

        users: Users
        core_action: str = Field(description="The primary action/usage pattern")
        io_contract: IOContract
        data_load: DataLoad
        throughput: Throughput
        read_write_ratio: str = Field(description="The R:W ratio string")
        consistency_model: str = Field(description="Consistency type")
        sla_slo: SLASLO

    class RequirementsSummary(BaseModel):
        functional: List[str] = Field(description="Top essential features")
        non_functional: List[str] = Field(description="Top system constraints")

    identification: Identification
    strategic_8_metrics: Strategic8Metrics
    requirements_summary: RequirementsSummary
    technical_taxonomy: List[str] = Field(description="Technical tags and technologies")





###############################################################################
## for hld engine ##################
###############################################################################




class SystemArchitectureStyle(BaseModel):
    pattern: str
    rationale: str

class CommunicationStrategy(BaseModel):
    internal_comms: str
    async_logic: str

class DeploymentStrategy(BaseModel):
    infrastructure: str
    orchestration: str

class DataManagement(BaseModel):
    partitioning: str
    consistency_guarantees: str

class TechStackComponent(BaseModel):
    component: str
    technology: str
    rationale: str

class RequestFlow(BaseModel):
    write_request_1: Optional[List[str]] = None
    read_request_1: Optional[List[str]] = None
    # Add more request types as needed

class SLOEngineering(BaseModel):
    latency_strategy: str
    throughput_strategy: str
    security_compliance: str

class ConnectivityMatrix(BaseModel):
    source: str
    intermediary: str
    destination: str

class SystemDesignSchema(BaseModel):
    system_name: str
    system_architecture_style: SystemArchitectureStyle
    communication_strategy: CommunicationStrategy
    deployment_strategy: DeploymentStrategy
    data_management: DataManagement
    processed_information: str
    tech_stack: List[TechStackComponent]
    request_flows: RequestFlow
    slo_engineering: SLOEngineering
    connectivity_matrices: List[ConnectivityMatrix]



#################################################################################
### hld critic ##################################################################
##################################################################################


class CriticReview(BaseModel):
    data_integrity: List[str] = Field(default_factory=list, description="Review of consistency model appropriateness for core actions")
    flow_logic: List[str] = Field(default_factory=list, description="Analysis of component alignment between request_flows and tech_stack")
    infrastructure: List[str] = Field(default_factory=list, description="Assessment of deployment_strategy supporting throughput requirements")
    security: List[str] = Field(default_factory=list, description="Security risk analysis at critical points and nodes")
    bottlenecks_chokepoints: List[str] = Field(default_factory=list, description="Identification of potential data flow bottlenecks")
    summary: str = Field(description="Overall architectural assessment and recommendations")
