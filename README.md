# ArchAgent
Multi-Agent based solution for Project System Design
______________
__________________

### User INPUT:
single prompt containg basic details what project to create
___________
### System OUTPUT:
*A Doc containing*:

1. System Architecture
2. Tech Stack
3. Reasoning for every choice made
4. Cloud and advanced scaling details
5. Cost and quantity estimation

*System Diagram*:
1. Very accurate depiction of Architecture suggested in the above document
__________________
### Current Tech Stack:
1. LangGraph & Langchain
2. FastAPI for backend
3. Streamlit for frontend
4. Marmaid for Diagrams



User input:
basic prompt > 


Requirement classifier (subgraph A):
1. RAG based *Requirements Creation*
2. Meta Tag like: *chat-system*, *social-media*, *streaming*, etc...
3. Uses tools for cost and quantity estimation
4. Data Source: https://github.com/gitgik/distributed-system-design

HLD Engine (subgraph B):
1. Also RAG based system 
2. Get context of the problem and metadata
3. creates a architecture description document
    - What is selected
    - Why is the 'what' selected
4. Data Source: https://github.com/binhnguyennus/awesome-scalability

Auditor (subgraph C):
1. Has predefined question to ask and check for chockepoints and bottleneck
2. Overengineering?
3. How good it really is?
4. If this passes:
    - Move forward
    - Return back to HLD engine with given concerns and problems


Diagram Engine(subgraph D):
1. Creates diagram for the given requirements
2. Evaluates the accuracy of the diagram

Finally to frontend...


