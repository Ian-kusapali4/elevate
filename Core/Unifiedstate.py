from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict, TypedDict, Annotated
import operator

# --- 1. DATA MODELS (Pydantic) ---
# Keeping your original profile schema for the parser
class CandidateProfile(BaseModel):
    jobTitle: str = Field(description="Current or target title")
    companyName: Optional[str] = None
    jobIndustry: List[str]
    jobType: List[str]
    jobGeo: str = "Remote"
    jobLevel: str = "Junior"
    skills: List[str]
    years_of_experience: int = 0
    jobExcerpt: str

# --- 2. THE UNIFIED GRAPH STATE ---
# This merges your original Indigo GraphState with the new features
class IndigoMasterState(TypedDict):
    # --- SECTION A: Original Indigo Inputs & Extraction ---
    file: str                           # Path to uploaded resume
    raw_resume: Optional[str]           # Extracted raw text
    profile: Optional[CandidateProfile] # The structured profile object
    CandidateProfile: Optional[Dict]    # Original dict format for backward compatibility
    entry_type: str
    

    # --- SECTION B: Discovery & Paths (Path A/B) ---
    title_suggestions: Optional[List[Dict]] = None
    search_queries: Optional[Dict] = None
    suggested_paths: List[Any]          # List of CareerPath objects
    selected_path: Optional[str]        # The chosen trajectory
    
    # --- SECTION C: Find My Circle (Social) ---
    target_goal: Optional[str]          # User's specific goal (e.g. "$200k salary")
    search_parameters: List[str]        # Niche queries for Tavily
    community_links: List[dict]
    current_background: str         
    
    # --- SECTION D: Analysis & Reality Check ---
    market_requirements: List[dict]     # Complexity-based skills
    gap_report: Optional[Any]           # DeepDiveResult (Strengths vs Gaps)
    effort_estimate: dict               # {skill: hours}
    baseline_truth: str                 # The grounded reality report
    
    # --- SECTION E: Original Indigo Final Outputs ---
    selected_job_id: Optional[str] = None
    rewritten_resume: Optional[str] = None
    final_resume: Optional[str] = None
    target_job_description: Optional[str] = None
    
    # --- SECTION F: Orchestration & Feedback (From Original Indigo) ---
    retry_count: int
    ingestion_retries: int
    search_retries: int
    error_message: Optional[str]
    feedback: Optional[str]
    feedback_score: Optional[int]
    hours_per_day: float                # For scheduling

class CircleState(TypedDict):
    
    target_goal: str
    search_parameters: List[str]
    curated_circles: List[dict]