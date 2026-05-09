
from pydantic import BaseModel, Field, ConfigDict, AliasChoices
from typing import List, Optional, Any, Dict, TypedDict, Annotated
import operator

# --- 1. Candidate Profile (Resume Extraction) ---
class CandidateProfile(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    jobTitle: str = Field(description="Current or targeted professional title.")
    companyName: Optional[str] = None
    jobIndustry: List[str] = Field(default_factory=list)
    jobType: List[str] = Field(default_factory=list)
    jobGeo: str = Field(default="Remote")
    jobLevel: str = Field(default="Junior")
    skills: List[str] = Field(default_factory=list)
    years_of_experience: float = Field(default=0.0)
    jobExcerpt: str = Field(default="")

# --- 2. THE UNIFIED GRAPH STATE ---
class IndigoMasterState(TypedDict):
    # --- SECTION A: Original Indigo Inputs & Extraction ---
    file: str
    raw_resume: Optional[str]
    profile: Optional[CandidateProfile]
    CandidateProfile: Optional[Dict]
    entry_type: str
    
    # --- SECTION B: Discovery & Paths ---
    title_suggestions: Optional[List[Dict]] = None
    search_queries: Optional[Dict] = None
    selected_path: Optional[str]
    
    # ADD THIS LINE RIGHT HERE:
    suggested_paths: Optional[List[Dict]] = None
    
    # --- SECTION C: Find My Circle (Social) ---
    target_goal: Optional[str]
    search_parameters: List[str]
    curated_circles: List[dict]         # Matches return {"curated_circles": ...}
    current_background: str 
    
    # --- SECTION D: Analysis & Reality Check ---
    market_requirements: List[dict] 
    gap_report: Optional[Any] 
    effort_estimate: dict 
    learning_roadmap: str               # Matches return {"learning_roadmap": ...}
    target_gap_skills: List[str]        # Added to capture roadmap gaps
    
    # --- SECTION E: Job Matching & Outputs ---
    job_matches: List[dict]             # CRITICAL: Added to capture the 51+ jobs found
    selected_job_id: Optional[str] = None
    resume_suggestions: Optional[str] = None # Matches return {"resume_suggestions": ...}
    final_resume: Optional[str] = None
    target_job_description: Optional[str] = None
    
    # --- SECTION F: Orchestration ---
    retry_count: int
    ingestion_retries: int
    search_retries: int
    error_message: Optional[str]
    feedback: Optional[str]
    feedback_score: Optional[int]
    hours_per_day: float



# --- 2. Discovery & Brainstorming Output ---
class CareerPath(BaseModel):
    """The structure for individual career pivot suggestions."""
    model_config = ConfigDict(populate_by_name=True)

    # AliasChoices checks multiple variations!
    title: str = Field(..., validation_alias=AliasChoices("path_name", "pathName", "title", "name"))
    description: str = Field(default="No description provided.")
    
    pitch: Optional[Any] = Field(None, validation_alias=AliasChoices("potential_roles", "pitch", "roles"))
    market_context: Optional[Any] = Field(None, validation_alias=AliasChoices("growth_potential", "growthPotential", "market_context"))
    
    # Catches 'requiredSkills' from your latest log
    bridge_skills: List[Any] = Field(default_factory=list, validation_alias=AliasChoices("skills_to_develop", "requiredSkills", "bridge_skills", "skills"))
    gap_skills: List[Any] = Field(default_factory=list, validation_alias=AliasChoices("skill_gaps", "gap_skills"))
    
    salary_range: str = Field(default="TBD", validation_alias=AliasChoices("estimated_salary_range", "salary_range", "pay_scale"))

# --- 3. Market Validation (Deep Dive) ---
class SkillAnalysis(BaseModel):
    """Simplified for stability when parsing LLM strings into objects."""
    model_config = ConfigDict(populate_by_name=True)
    skill: str = Field(..., alias="name")
    relevance: str = Field(default="High relevance for this pivot")
# Core/Unifiedstate.py

class BrainstormOutput(BaseModel):
    """Container for the list of career paths."""
    suggested_paths: List[CareerPath]
    
class DeepDiveResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    # Use aliases to catch both variations found in your logs
    role_title: Optional[Any] = Field(None, alias="path_name") 
    score: Optional[int] = Field(0, alias="market_fit_score")
    strengths: List[Any] = Field(default_factory=list) 
    gaps: List[Any] = Field(default_factory=list)
    live_sources: List[Any] = Field(default_factory=list)
# --- 4. State Definitions (LangGraph) ---

class UniversalGoalsState(TypedDict):
    """Fixes the ImportError in your goals.py"""
    target_goal: str
    current_background: str
    market_requirements: List[dict]
    effort_estimate: dict
    learning_roadmap: str

class DiscoveryState(TypedDict):
    """The global state for the Pivot Graph."""
    model_config = ConfigDict(populate_by_name=True)
    
    profile: Any 
    learning_roadmap: Optional[str]
    resume_suggestions: Optional[str]
    hours_per_day: int
    CandidateProfile: Optional[dict]
    discovery_output: Optional[List[dict]]
    suggested_paths: Optional[List[CareerPath]]
    selected_path: Optional[str]
    analysis_report: Optional[DeepDiveResult]
    entry_type: Optional[str]

class FindMyCircleState(TypedDict):
    target_goal: str
    search_parameters: dict
    selected_path: str
    gap_report: dict
    curated_circles: List[dict]
    roadmap: str
    calendar_status: str