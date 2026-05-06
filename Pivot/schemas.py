from pydantic import BaseModel, Field
from typing import List, Optional,Any, TypedDict

# --- Your Original Schema ---
class CandidateProfile(BaseModel):
    jobTitle: str = Field(description="The professional title the candidate is currently holding or targeting.")
    companyName: Optional[str] = Field(description="The candidate's current or most recent employer.")
    jobIndustry: List[str] = Field(description="List of industries the candidate has experience in.")
    jobType: List[str] = Field(description="Preferred work types, e.g., 'Full-Time', 'Freelance'.")
    jobGeo: str = Field(default="Remote", description="The candidate's current location.")
    jobLevel: str = Field(default="Junior", description="Seniority level: 'Junior', 'Midweight', 'Senior', or 'Lead'.")
    skills: List[str] = Field(description="Technical skills found in the resume.")
    years_of_experience: int = Field(description="Total number of years in relevant fields.")
    jobExcerpt: str = Field(description="A 2-3 sentence professional summary.")

# --- The Discovery Output Schema ---
class EmergingRole(BaseModel):
    title: str
    relevance_score: int = Field(description="How well it fits the candidate (1-10)")
    why_it_fits: str
    market_link: Optional[str]

class DiscoveryState(TypedDict):
    profile: Any             # CandidateProfile
    discovery_output: List[Any]
    suggested_paths: List[Any]
    selected_path: Optional[str]      # User choice (Phase 1 -> 2)
    analysis_report: Optional[Any]    # DeepDiveResult (Phase 2)
    learning_roadmap: Optional[str]   # (Phase 3)
    resume_suggestions: Optional[str] # (Phase 4)
    hours_per_day: int                # User input for scheduling

class CareerPath(BaseModel):
    title: str = Field(description="The name of the potential career pivot.")
    description: str = Field(description="A brief pitch on why this path exists in 2026.")
    bridge_skills: List[str] = Field(description="Existing skills from the resume that apply here.")
    gap_skills: List[str] = Field(description="New skills the user needs to acquire.")
    salary_range: str = Field(description="Estimated 2026 market compensation.")

class BrainstormOutput(BaseModel):
    suggested_paths: List[CareerPath]

class SkillAnalysis(BaseModel):
    skill_name: str
    evidence_from_market: str = Field(description="Why this skill is trending in job ads (e.g., 'Required for long-running agents').")
    is_strength: bool = Field(description="True if the user has it, False if it is a gap.")

class DeepDiveResult(BaseModel):
    role_title: str
    score: int = Field(description="Overall match score out of 100.")
    strengths: List[SkillAnalysis]
    gaps: List[SkillAnalysis]
    live_sources: List[str] = Field(description="Links to the job ads or reports analyzed.")

class UniversalGoalsState(TypedDict):
    target_goal: str       # e.g., "Director of Marketing" or "Head Chef"
    current_background: str # e.g., "5 years in sales" or "Recent nursing grad"
    market_requirements: List[dict] # { "skill": str, "complexity": 1-5 }
    effort_estimate: dict   # { "skill": "hours" }
    baseline_truth: str     # The "Reality Check" output

class FindMyCircleState(TypedDict):
    # Existing Fields
    target_goal: str
    search_parameters: dict
    resume_map: dict
    selected_path: str
    gap_report: dict
    
    # New Social Fields
    community_links: List[dict] # [{"platform": "Discord", "name": "AI Builders", "url": "..."}]
    roadmap: str
    calendar_status: str