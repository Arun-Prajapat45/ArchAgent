from src.utils.models import RequestFlow, SystemDesignSchema


def test_request_flow_preserves_multiple_named_flows() -> None:
    flows = RequestFlow.model_validate(
        {"write_request_1": ["a"], "write_request_2": ["b"], "read_request_1": ["c"]}
    )
    assert flows.model_dump()["write_request_2"] == ["b"]


def test_system_design_accepts_three_item_connectivity_edges() -> None:
    design = SystemDesignSchema.model_validate(
        {
            "system_name": "Chat",
            "system_architecture_style": {"pattern": "services", "rationale": "scale"},
            "communication_strategy": {"internal_comms": "HTTP", "async_logic": "Kafka"},
            "deployment_strategy": {"infrastructure": "AWS", "orchestration": "ECS"},
            "data_management": {"partitioning": "tenant", "consistency_guarantees": "strong"},
            "processed_information": "messages",
            "tech_stack": [{"component": "API", "technology": "FastAPI", "rationale": "typed"}],
            "request_flows": {"write_request_1": ["client", "api", "db"]},
            "slo_engineering": {
                "latency_strategy": "cache",
                "throughput_strategy": "scale",
                "security_compliance": "TLS",
            },
            "connectivity_matrices": [["Client", "API", "DB"]],
        }
    )
    assert design.connectivity_matrices[0].intermediary == "API"
