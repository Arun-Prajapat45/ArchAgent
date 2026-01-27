from langchain.prompts import ChatPromptTemplate


################################################################
#### for requirements classifier ##############################
###############################################################



RequirementsQuery = """Role: Senior Systems Architect 
Task: Generate a Technical Requirements Document (TRD) for a requested system in strict JSON format.

Input: {query}

Instructions:
Match Archetype: Identify the system design pattern strictly from the fetched documents only
Infer Metrics: Use industry-standard benchmarks for a system of this scale (assume mid-to-large enterprise scale unless specified).

Output Format: You must respond only with a valid JSON object. Do not include markdown headers or conversational filler.

JSON Schema Requirements:
{{
  "identification": {{
    "archetype": "string",
    "knowledge_references": ["string"]
  }},
  "strategic_8_metrics": {{
    "users": {{
      "persona": "string",
      "count": "string"
    }},
    "core_action": "string",
    "io_contract": {{
      "input": ["string"],
      "output": ["string"]
    }},
    "data_load": {{
      "daily_ingestion": "string",
      "total_storage_5yr": "string"
    }},
    "throughput": {{
      "avg_rps": "number",
      "peak_rps": "number"
    }},
    "read_write_ratio": "string",
    "consistency_model": "string",
    "sla_slo": {{
      "availability": "string",
      "latency_p99": "string"
    }}
  }},
  "requirements_summary": {{
    "functional": ["string"],
    "non_functional": ["string"]
  }},
  "technical_taxonomy": ["string"]
}}"""



















###############################################################################
######### for hld engine ######################################################
###############################################################################

DesignGeneratorTemplate="""
Role: Principal Infrastructure Architect.

Task: Architect a production-ready system based strictly on the provided technical specifications and documents fetched by the retriver

Constraint: Output ONLY a valid JSON object. Do not include conversational text, markdown formatting outside the JSON, or explanations.

Technical_Spec: >
Architecture type: {archetype}
Core Actions: {core_action}
Inputs: {input}
Outputs: {output}
read_write_ratio: {read_write_ratio}
Consistency: {consistency_model}
Functional Requirements: {functional}
Non-functional Requirements: {non_functional}


JSON Schema Requirement: Your output must follow this exact structure:
{{
  "system_name": "[Insert official name of the system being designed]",
  
  "system_architecture_style": {{
    "pattern": "e.g., Microservices / Monolith / Serverless",
    "rationale": "Why this pattern fits the RPS/User requirements"
  }},
  "communication_strategy": {{
    "internal_comms": "e.g., gRPC for service-to-service",
    "async_logic": "e.g., Message Broker for Notifications"
  }},
  "deployment_strategy": {{
    "infrastructure": "e.g., AWS EKS (Kubernetes)",
    "orchestration": "How containers are managed and scaled"
  }},
  "data_management": {{
    "partitioning": "Strategy for database sharding or replication",
    "consistency_guarantees": "How CAP theorem trade-offs are handled"
  }},
  "processed_information": "[information about how the system should work, all endpoints, all services, components and all in brief]",
  "tech_stack": [
    {{
      "component": "[Core Infrastructure Layer, e.g., Ingestion, Storage, Compute]",
      "technology": "[Specific Tool or Service name]",
      "rationale": "[Detailed engineering justification mapped to the provided metrics]"
    }}
  ],
  "request_flows": {{
    "write_request_1": [
      "[Step 1: Origin]",
      "[Step 2: Middleware/Processing]",
      "[Step 3: Persistence]"
    ],
    // add other write requests requests
    "read_request_1": [
      "[Step 1: Origin]",
      "[Step 2: Retrieval/Cache Logic]",
      "[Step 3: Client Response]"
    ], 
    // add other read requests requests
  }},
  "slo_engineering": {{
    "latency_strategy": "[Describe technical mechanisms used to meet the P99 latency target]",
    "throughput_strategy": "[Describe scaling and concurrency logic to handle peak RPS]",
    "security_compliance": "[Describe encryption, auth, and regulatory measures]"
  }},
  "connectivity_matrices": [
    ["[Source (eg: user/ service/ any gateway)]", "[Intermediary service/node (eg: API Gateway/ Load balancer)]", "[Destination (eg: any service/ database/ external api)]"],
    ["[Source (eg: user/ service/ any gateway)]", "[Intermediary service/node (eg: API Gateway/ Load balancer)]", "[Destination (eg: any service/ database/ external api)]"],
    //add other connections...
  ],

}}
"""



# DesignUpdateTemplate="""

# Role: Senior Systems Architect (Refinement Mode)

# Context: > You previously generated an HLD that was reviewed by a Critic. There are architectural inconsistencies that must be resolved to reach a "Production-Ready" state.

# Inputs:

# Original Goal: {user_input}

# Current HLD: {hld_output_json}

# Critic Feedback: {critic_feedback_json}

# Instructions:

# Prioritize Severities: Address all "Critical" and "Warning" items from the Critic.

# Update Matrices: Synchronize the connectivity_matrices with any changes made to the request_flows.

# Strict Adherence: Do not ignore the Critic's remediation suggestions unless they violate the core action of the system.

# JSON Schema Requirement: Your output must follow this exact structure: 
# {{
#   "system_name": "[Insert official name of the system being designed]",
  
#   "system_architecture_style": {{
#     "pattern": "e.g., Microservices / Monolith / Serverless",
#     "rationale": "Why this pattern fits the RPS/User requirements"
#   }},
#   "communication_strategy": {{
#     "internal_comms": "e.g., gRPC for service-to-service",
#     "async_logic": "e.g., Message Broker for Notifications"
#   }},
#   "deployment_strategy": {{
#     "infrastructure": "e.g., AWS EKS (Kubernetes)",
#     "orchestration": "How containers are managed and scaled"
#   }},
#   "data_management": {{
#     "partitioning": "Strategy for database sharding or replication",
#     "consistency_guarantees": "How CAP theorem trade-offs are handled"
#   }},
#   "processed_information": "[information about how the system should work, all endpoints, all services, components and all in brief]",
#   "tech_stack": [
#     {{
#       "component": "[Core Infrastructure Layer, e.g., Ingestion, Storage, Compute]",
#       "technology": "[Specific Tool or Service name]",
#       "rationale": "[Detailed engineering justification mapped to the provided metrics]"
#     }}
#   ],
#   "request_flows": {{
#     "write_request_1": [
#       "[Step 1: Origin]",
#       "[Step 2: Middleware/Processing]",
#       "[Step 3: Persistence]"
#     ],
#     // add other write requests requests
#     "read_request_1": [
#       "[Step 1: Origin]",
#       "[Step 2: Retrieval/Cache Logic]",
#       "[Step 3: Client Response]"
#     ], 
#     // add other read requests requests
#   }},
#   "slo_engineering": {{
#     "latency_strategy": "[Describe technical mechanisms used to meet the P99 latency target]",
#     "throughput_strategy": "[Describe scaling and concurrency logic to handle peak RPS]",
#     "security_compliance": "[Describe encryption, auth, and regulatory measures]"
#   }},
#   "connectivity_matrices": [
#     ["[Source (eg: user/ service/ any gateway)]", "[Intermediary service/node (eg: API Gateway/ Load balancer)]", "[Destination (eg: any service/ database/ external api)]"],
#     ["[Source (eg: user/ service/ any gateway)]", "[Intermediary service/node (eg: API Gateway/ Load balancer)]", "[Destination (eg: any service/ database/ external api)]"],
#     //add other connections...
#   ],

# }}
# """





DesignUpdateTemplate="""
Role: Senior Systems Architect (Surgical Refinement Mode)

Context: 
You are applying a high-precision architectural patch. You have an HLD that contains the core business logic, and a Critic Review that identifies technical flaws. Your mission is to fix the technical flaws WITHOUT losing any functional features or services from the original design.

Inputs:
- Original Goal: {user_input}
- Current HLD: {hld_output_json} (This contains the full functional scope)
- Critic Feedback: {critic_feedback_json} (This contains the required technical fixes)

CORE OPERATING CONSTRAINTS:
1. **Functional Parity (Zero-Loss Rule):** You are FORBIDDEN from removing any services or request flows present in the Current HLD unless the Critic explicitly states that the service itself is the cause of a failure. 
   - *Example:* If the original has "Feed Service" and "Post Service," and the critic only mentions "Cassandra latency," keep BOTH services and fix the Cassandra configuration.
2. **Surgical Precision:** Change only the specific nodes (tech_stack, data_management, etc.) that the Critic flagged as problematic. 
3. **Requirement Anchoring:** Cross-reference your output with the "Original Goal." If the goal requires "Real-time Chat," ensure WebSockets/Messaging remain in the Tech Stack.
4. **No Omission:** Do not summarize. If the original design had 5 request flows, the update must have 5 request flows, even if only 1 was changed.
5. **Internal Consistency Check:** Before finalizing, verify that:
   - [ ] Every component in `request_flows` has a corresponding entry in `tech_stack`.
   - [ ] Every edge in `connectivity_matrices` references a technology defined in `tech_stack`.
   - [ ] The `processed_information` lists every original functional requirement that was preserved.
6. **Ghost Node Prevention:** Check specifically for infrastructure like "API Gateway", "Load Balancers", or "CDNs". If they appear in your flow or matrix, create a tech_stack entry for them immediately.

Instructions:
- Prioritize: Address all "Critical" and "Warning" items from the Critic.
- Sync: Ensure the `connectivity_matrices` reflect any new infrastructure added to fix bottlenecks.
- Consistency: If the critic flags data integrity, update `data_management` logic while keeping the underlying services.
- If the critic suggests a new component (e.g., a Load Balancer or Cache), update ALL three sections: `tech_stack`, `request_flows`, and `connectivity_matrices`.
- Make sure no components are left alone/unconnected or the system has unconnected components in the 'connectivity_matrices'
- Make sure you differenciate between adminsistrator, user and other external systems/users

JSON Schema Requirement: 
Your output must follow the exact structure below. 
Note: The "processed_information" field MUST now include a list of what original features were preserved to ensure no functional loss.

JSON Schema Requirement: Your output must follow this exact structure: 
{{
  "system_name": "[Insert official name of the system being designed]",
  
  "system_architecture_style": {{
    "pattern": "e.g., Microservices / Monolith / Serverless",
    "rationale": "Why this pattern fits the RPS/User requirements"
  }},
  "communication_strategy": {{
    "internal_comms": "e.g., gRPC for service-to-service",
    "async_logic": "e.g., Message Broker for Notifications"
  }},
  "deployment_strategy": {{
    "infrastructure": "e.g., AWS EKS (Kubernetes)",
    "orchestration": "How containers are managed and scaled"
  }},
  "data_management": {{
    "partitioning": "Strategy for database sharding or replication",
    "consistency_guarantees": "How CAP theorem trade-offs are handled"
  }},
  "processed_information": "[information about how the system should work, all endpoints, all services, components and all in brief]",
  "tech_stack": [
    {{
      "component": "[Core Infrastructure Layer, e.g., Ingestion, Storage, Compute]",
      "technology": "[Specific Tool or Service name]",
      "rationale": "[Detailed engineering justification mapped to the provided metrics]"
    }}
  ],
  "request_flows": {{
    "write_request_1": [
      "[Step 1: Origin]",
      "[Step 2: Middleware/Processing]",
      "[Step 3: Persistence]"
    ],
    // add other write requests requests
    "read_request_1": [
      "[Step 1: Origin]",
      "[Step 2: Retrieval/Cache Logic]",
      "[Step 3: Client Response]"
    ], 
    // add other read requests requests
  }},
  "slo_engineering": {{
    "latency_strategy": "[Describe technical mechanisms used to meet the P99 latency target]",
    "throughput_strategy": "[Describe scaling and concurrency logic to handle peak RPS]",
    "security_compliance": "[Describe encryption, auth, and regulatory measures]"
  }},
  "connectivity_matrices": [
    ["[Source (eg: user/ service/ any gateway)]", "[Intermediary service/node (eg: API Gateway/ Load balancer)]", "[Destination (eg: any service/ database/ external api)]"],
    ["[Source (eg: user/ service/ any gateway)]", "[Intermediary service/node (eg: API Gateway/ Load balancer)]", "[Destination (eg: any service/ database/ external api)]"],
    //add other connections...
  ],

}}


"""





###################################################################################
### hld critic #############################################################
##################################################################################


# CriticPromptTemplate="""
# Role: You are a Principal Systems Architect. 
# Review the following HLD JSON and provide a detailed architectural critique. Your goal is to find 'Architectural Hallucinations' and 'Scaling Anti-patterns'.

# Evaluate the HLD based on these criteria:

# 1. Data Integrity: Is the consistency model appropriate for the core actions?
# 2. Flow Logic: Does every component in the request_flows exist in the tech_stack?
# 3. Infrastructure: Does the deployment_strategy support the throughput requirements?
# 4. Security: Is the security of the system at risk at any point or node?
# 5. Bottlenecks & Chokepoints: Does any flow of data lead to a potential chokepoint or bottleneck?

# HLD JSON:
# <HLD_JSON>
# {hld_json}
# </HLD_JSON>

# Output your review ONLY as a valid JSON object with the following structure (no additional text):
# {{
#   "data_integrity": [
#     "Your analysis of the consistency model appropriateness for core actions in points..."
#   ],
#   "flow_logic": [
#     "Your analysis of component alignment between request_flows and tech_stack in points..."
#   ],
#   "infrastructure": [
#     "Your assessment of deployment_strategy supporting throughput requirements in points..."
#   ],
#   "security": [
#     "Your security risk analysis at critical points and nodes in points..."
#   ],
#   "bottlenecks_chokepoints": [
#     "Your identification of potential data flow bottlenecks in points..."
#   ],
#   "summary": "Overall architectural assessment and recommendations in points..."
# }}


# """


CriticPromptTemplate="""
Role: Principal Systems Architect (Quality Assurance)

Review the HLD JSON to identify specific architectural failures. Use a "First, do no harm" approach.

- HLD json: {hld_json}

Evaluation Criteria:
1. Data Integrity: Is the consistency model appropriate?
2. Flow Logic: Is there a 1:1 match between tech_stack and request_flows?
3. Infrastructure: Does it meet the specific RPS/Throughput in the Original Goal?
4. Security: Is there a specific vulnerability?
5. Bottlenecks: Identify the single point of failure (SPOF).

Output JSON Structure:
{{
  "critical_fixes_required": [
    {{ "location": "Node Name", "issue": "Specific failure", "remediation": "Technical fix" }}
  ],
  "warnings": ["Low-impact improvements"],
  "validated_components": ["List of things that are PERFECT and MUST NOT be changed"],
  "functional_checklist": {{
    "Requirement_1": "Pass/Fail - Reason",
    "Requirement_2": "Pass/Fail - Reason"
  }}
}}

"""






#######################################################################################################
## for Diagrammer####################################################################################
#======================================================================================================


# DiagrammerPromptTemplate=ChatPromptTemplate.from_template("""
# You are an expert in system architecture visualization using Mermaid flowcharts.

# Generate a valid Mermaid FLOWCHART diagram that represents the system architecture.

# Strict rules (do not break):

# Follow the Architecture JSON exactly. Do not invent, omit, or rename components.

# Use Mermaid flowchart syntax only:
# - flowchart TD or LR
# - Nodes using square brackets or rounded brackets
# - Directed edges using --> only

# Do NOT use:
# - C4 diagrams
# - architecture-beta
# - classDiagram, sequenceDiagram, or stateDiagram
# - Subgraphs unless grouping is necessary

# NODE RULES:
# - User must be a single node
# - API Gateway must be a single node
# - Backend services must be individual nodes
# - Databases / caches must be individual nodes
# - External systems must be individual nodes

# NAMING RULES:
# - Node IDs must be lowercase or camelCase
# - No spaces or special characters in IDs
# - Labels must be human-readable

# FLOW RULES:
# - Show only high-level request flow
# - Prefer logical flow over physical accuracy
# - Avoid bidirectional arrows unless required
# - Keep the diagram small and readable

# STYLING REQUIREMENTS:
# - User: light blue
# - API Gateway: orange
# - Backend services: green
# - Databases / caches: purple
# - External systems: gray

# STYLING SYNTAX:
# Use Mermaid classDef and class assignments.
# Do not use inline styles.

# STRUCTURE:
# 1. Declare flowchart direction
# 2. Define all nodes
# 3. Define all edges
# 4. Define classDef styles
# 5. Assign classes to nodes

# Output ONLY valid Mermaid code.
# Do not include explanations, comments, or markdown fences.

# Architecture JSON:
# <ARCH_JSON>
# {arch_json}
# </ARCH_JSON>
# """

# )

DiagrammerPromptTemplate=ChatPromptTemplate.from_template("""

You are an expert in system architecture visualization using Mermaid flowcharts.
Generate a valid Mermaid FLOWCHART diagram based on the Architecture JSON.

### ARCHITECTURE LOGIC RULES
1. DIRECTION: Use 'flowchart TD' (Top-Down).
2. ACCURACY: Nodes must represent the exact structural role defined in the JSON.
3. SEMANTIC SHAPES:
   - Databases/Caches: Use cylinder syntax: `id[(Label)]`
   - Queues/Streams (Kafka/RabbitMQ): Use subroutine syntax: `id[[Label]]`
   - External APIs/WebSockets: Use rhomboid or stadium shapes: `id([Label])`
   - Standard Services: Use square brackets: `id[Label]`

### FLOW RULES
1. Use directed edges `-->` for request flow.
2. For async processes (e.g., Kafka to Service), use dotted lines `-.->` to distinguish from synchronous API calls.
3. Ensure the 'User' is the entry point at the top.

### STYLING & APPEARANCE (PRIORITY)
1. Use specific hex codes for professional look:
   - User: #ADD8E6 (Light Blue)
   - API Gateway: #FFA500 (Orange)
   - Services: #90EE90 (Light Green)
   - Storage: #9370DB (Medium Purple)
   - Messaging/External: #D3D3D3 (Light Gray)
2. Always include `stroke:#333,stroke-width:2px` in classDefs for visual "pop."
3. Use grouping (subgraphs) if the JSON indicates a logical boundary (e.g., "Data Layer" or "Microservices").

### STYLING SYNTAX
1. Declare flowchart TD.
2. Define Nodes with semantic shapes.
3. Define Edges (using dotted lines for async).
4. Define classDefs with stroke properties.
5. Assign classes.

Output ONLY valid Mermaid code. No markdown fences, no comments.

Architecture JSON:
<ARCH_JSON>
{arch_json}
</ARCH_JSON>

""")