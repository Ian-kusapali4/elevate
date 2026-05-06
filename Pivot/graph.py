from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver # For state persistence
from Pivot.schemas import DiscoveryState
from Pivot.discovery import discovery_search_node
from Pivot.brainstormer import path_brainstormer_node
from Pivot.validator import market_validation_node
from Pivot.roadmap import roadmap_generator_node
from Pivot.loopback import resume_loopback_node
import dataclasses

from langchain_core.messages import BaseMessage

# 1. Initialize the StateGraph with your schema
workflow = StateGraph(DiscoveryState)

# 2. Add the nodes you already built
workflow.add_node("discovery", discovery_search_node)
workflow.add_node("brainstormer", path_brainstormer_node)
workflow.add_node("validator", market_validation_node)
workflow.add_node("roadmap", roadmap_generator_node)
workflow.add_node("loopback", resume_loopback_node)

# 3. Define the Edges (The Connections)
workflow.add_edge(START, "discovery")
workflow.add_edge("discovery", "brainstormer")

# --- HUMAN-IN-THE-LOOP BREAK ---
# We pause after brainstorming so the user can select a path.
# In LangGraph, we can use a 'breakpoint' or a conditional edge.
workflow.add_edge("brainstormer", "validator") 

workflow.add_edge("validator", "roadmap")
workflow.add_edge("roadmap", "loopback")
workflow.add_edge("loopback", END)

# 4. Compile the Graph
# We add a checkpointer so the agent remembers where it is after you pick a path
memory = MemorySaver()
app = workflow.compile(checkpointer=memory, interrupt_before=["validator"])