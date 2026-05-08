from services.parser.pdf_reader_n_clearner import pdf_reader
from Agents.Job_match.agents.Job_ranker import start_career_optimization
from services.scraper.Job_scraper import fetch_jobs
from Agents.Job_match.agents.Resume_extraction_agent import Resume_extaction
from Agents.Job_match.agents.resume_rewrite_agent import resume_rewrite
from Agents.Job_match.agents.suggested_Job_formating import suggested_Job_formating
from Agents.Job_match.agents.human_rewritter_agent import human_rewritter_agent
from Agents.Job_match.core.Nodes.select_job import select_job_details

from Agents.Job_match.core.Nodes.Conditions import ingestion_condition, skill_extraction_condition, job_search_condition, critic_resume_rewrite_condition
from Agents.Job_match.core.Nodes.GraphState import GraphState
from langgraph.checkpoint.memory import MemorySaver

from langgraph.graph import StateGraph,START,END

# This file defines the nodes and edges of the graph, as well as the conditions for transitioning between nodes. Each node corresponds to a specific agent or function that performs a task in the career optimization process, such as reading the resume, extracting skills, fetching job listings, rewriting the resume, etc. The edges define the flow of data and control between these nodes, and the conditions determine whether the graph can proceed to the next node or if it needs to retry or end with an error message.
def nodes():
    graph = StateGraph(GraphState)

    # 1. ADD NODES
    graph.add_node('pdf_reader', pdf_reader)
    graph.add_node('Resume_extaction', Resume_extaction)
    graph.add_node('fetch_jobs', fetch_jobs)
    # NEW: This node prunes the 60 jobs down to 1
    graph.add_node('select_job_details', select_job_details) 
    
    graph.add_node('suggested_Job_formating', suggested_Job_formating)
    graph.add_node('resume_rewrite', resume_rewrite)
    graph.add_node('human_rewritter_agent', human_rewritter_agent)

    # 2. DEFINE EDGES
    graph.add_edge(START, 'pdf_reader')
    graph.add_edge('pdf_reader', 'Resume_extaction')

    # Extraction -> Formatting
    graph.add_conditional_edges('Resume_extaction', ingestion_condition, {
        "passed": 'suggested_Job_formating',
        "retry": 'Resume_extaction',
        "failed": END
    })

    # Formatting -> Scraper
    graph.add_conditional_edges('suggested_Job_formating', skill_extraction_condition, {
        "passed": 'fetch_jobs', 
        "retry": 'suggested_Job_formating',
        "failed": END
    })

    # Scraper -> Selection (NEW FLOW)
   
    graph.add_edge('fetch_jobs', 'select_job_details')

    # Selection -> Rewrite (The Pruned Path)
    graph.add_conditional_edges('select_job_details', critic_resume_rewrite_condition, {
        "Procced": 'resume_rewrite',
        "retry": 'fetch_jobs' 
    })

    graph.add_edge('resume_rewrite', 'human_rewritter_agent')
    graph.add_edge('human_rewritter_agent', END)

    # 3. COMPILE WITH INTERRUPT
    memory = MemorySaver()
    # We interrupt BEFORE select_job_details so the user can provide the ID
    app = graph.compile(
        checkpointer=memory,
        interrupt_before=["select_job_details"]
    )

    return app