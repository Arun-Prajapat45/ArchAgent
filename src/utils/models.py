from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RequirementModel(BaseModel):
    class Identification(BaseModel):
        archetype: str
        knowledge_references: list[str]

    class Strategic8Metrics(BaseModel):
        class Users(BaseModel):
            persona: str
            count: str

        class IOContract(BaseModel):
            input: list[str]
            output: list[str]

        class DataLoad(BaseModel):
            daily_ingestion: str
            total_storage_5yr: str

        class Throughput(BaseModel):
            avg_rps: int = Field(ge=0)
            peak_rps: int = Field(ge=0)

            @model_validator(mode="after")
            def validate_peak(self) -> RequirementModel.Strategic8Metrics.Throughput:
                if self.peak_rps < self.avg_rps:
                    raise ValueError("peak_rps must be greater than or equal to avg_rps")
                return self

        class SLASLO(BaseModel):
            availability: str
            latency_p99: str

        users: Users
        core_action: str
        io_contract: IOContract
        data_load: DataLoad
        throughput: Throughput
        read_write_ratio: str
        consistency_model: str
        sla_slo: SLASLO

    class RequirementsSummary(BaseModel):
        functional: list[str] = Field(min_length=1)
        non_functional: list[str] = Field(min_length=1)

    identification: Identification
    strategic_8_metrics: Strategic8Metrics
    requirements_summary: RequirementsSummary
    technical_taxonomy: list[str]


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
    model_config = ConfigDict(extra="allow")

    write_request_1: list[str] | None = None
    read_request_1: list[str] | None = None


class SLOEngineering(BaseModel):
    latency_strategy: str
    throughput_strategy: str
    security_compliance: str


class ConnectivityMatrix(BaseModel):
    source: str
    intermediary: str
    destination: str

    @model_validator(mode="before")
    @classmethod
    def accept_three_item_edge(cls, value: Any) -> Any:
        if isinstance(value, list) and len(value) == 3:
            return {"source": value[0], "intermediary": value[1], "destination": value[2]}
        return value


class SystemDesignSchema(BaseModel):
    system_name: str
    system_architecture_style: SystemArchitectureStyle
    communication_strategy: CommunicationStrategy
    deployment_strategy: DeploymentStrategy
    data_management: DataManagement
    processed_information: str
    tech_stack: list[TechStackComponent]
    request_flows: RequestFlow
    slo_engineering: SLOEngineering
    connectivity_matrices: list[ConnectivityMatrix]


class CriticReview(BaseModel):
    data_integrity: list[str] = Field(default_factory=list)
    flow_logic: list[str] = Field(default_factory=list)
    infrastructure: list[str] = Field(default_factory=list)
    security: list[str] = Field(default_factory=list)
    bottlenecks_chokepoints: list[str] = Field(default_factory=list)
    summary: str
