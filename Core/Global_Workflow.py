from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# 1. IMPORT YOUR UNIFIED STATE
from Core.Unifiedstate import ElevateMasterState 

# 2. IMPORT NODES & CONDITIONS
from services.parser.pdf_reader_n_clearner import pdf_reader
from Job_match.agents.Resume_extraction_agent import Resume_extaction
from Job_match.agents.suggested_Job_formating import suggested_Job_formating
from services.scraper.Job_scraper import fetch_jobs
from Core.Nodes.select_job import select_job_details
from Job_match.agents.resume_rewrite_agent import resume_rewrite
from Job_match.agents.human_rewritter_agent import human_rewritter_agent
from Agents.Pivot.discovery import discovery_search_node
from Agents.Pivot.brainstormer import path_brainstormer_node
from Agents.Pivot.validator import market_validation_node
from Agents.Pivot.roadmap import roadmap_generator_node
from Agents.Pivot.loopback import resume_loopback_node
from Core.Nodes.human_gate import human_decision_gate
from Agents.Goals.goals import goal_analysis_node
from Agents.Goals.estimator import universal_reality_check_node
from Core.Nodes.Conditions import route_user_intent
from Agents.Find_my_cycle.social_discovery import generate_circle_parameters_node
from Agents.Find_my_cycle.soial_search import real_social_search_node

from Core.Nodes.Conditions import (
    critic_resume_rewrite_condition,
    skill_extraction_condition,
    ingestion_condition
)

def build_unified_graph():
    builder = StateGraph(ElevateMasterState)

    # 1. ADD NODES
    builder.add_node('pdf_reader', pdf_reader)
    builder.add_node('Resume_extaction', Resume_extaction)
    builder.add_node("human_decision_gate", human_decision_gate)

    # Spoke A: Job Match
    builder.add_node('suggested_Job_formating', suggested_Job_formating)
    builder.add_node('fetch_jobs', fetch_jobs)
    builder.add_node('select_job_details', select_job_details) 
    builder.add_node('resume_rewrite', resume_rewrite)
    builder.add_node('human_rewritter_agent', human_rewritter_agent)

    # Spoke B: Pivot
    builder.add_node("discovery", discovery_search_node)
    builder.add_node("validator", market_validation_node)
    builder.add_node("roadmap", roadmap_generator_node)
    builder.add_node("loopback", resume_loopback_node)
    builder.add_node("brainstormer", path_brainstormer_node)
    # Spoke C: Goals
    builder.add_node("analyze_goal", goal_analysis_node)
    builder.add_node("reality_check", universal_reality_check_node)
    
    # Spoke D: Find My Circle (Networking)
    builder.add_node("generate_params", generate_circle_parameters_node)
    builder.add_node("find_links", real_social_search_node)

    # 2. DEFINE EDGES
    builder.add_edge(START, 'pdf_reader')
    builder.add_edge('pdf_reader', 'Resume_extaction')


    builder.add_conditional_edges(
        "Resume_extaction", 
        ingestion_condition, 
        {
            "passed": "human_decision_gate", 
            "go_to_pivots": "brainstormer",  
            "retry": "Resume_extaction",
            "failed": END
        }
    )

    builder.add_conditional_edges(
        "human_decision_gate", 
        route_user_intent, 
        {
            "job_search": "suggested_Job_formating",
            "pivot": "discovery",
            "goal": "analyze_goal",
            "circle": "generate_params"
        }
    )
    # --- SPOKE A FLOW ---
    builder.add_conditional_edges('suggested_Job_formating', skill_extraction_condition, {
        "passed": 'fetch_jobs', 
        "retry": 'suggested_Job_formating',
        "failed": END
    })

    builder.add_edge('fetch_jobs', 'select_job_details')
    
    builder.add_conditional_edges('select_job_details', critic_resume_rewrite_condition, {
        "Procced": 'resume_rewrite', 
        "retry": 'fetch_jobs',
        "waiting": END 
    })

    builder.add_edge('resume_rewrite', 'human_rewritter_agent')
    builder.add_edge('human_rewritter_agent', END)

    # --- SPOKE B FLOW ---
    builder.add_edge("discovery", "brainstormer")
    builder.add_edge("brainstormer", "validator")
    builder.add_edge("validator", "roadmap")
    builder.add_edge("roadmap", "loopback")
    builder.add_edge("loopback", END)

    # --- SPOKE C FLOW (Goals Only) ---
    builder.add_edge("analyze_goal", "reality_check")
    builder.add_edge("reality_check", END)

    # --- SPOKE D FLOW (Networking Only) ---
    builder.add_edge("generate_params", "find_links")
    builder.add_edge("find_links", END)

    # 3. COMPILE
    memory = MemorySaver()
    return builder.compile(
        checkpointer=memory, 
        interrupt_before=["human_decision_gate", "select_job_details"] 
    )