import time
import random
from jobspy import scrape_jobs
from Core.Unifiedstate import IndigoMasterState 

# This node is responsible for taking the job title suggestions from the Career Path Agent and using jobspy to scrape job listings from various platforms.

def fetch_jobs(state: IndigoMasterState):
    
    suggestions = state.get("search_queries", {}).get("suggestions", [])
    
   
    location = state.get("CandidateProfile", {}).get("jobGeo", "Remote") 
    
  
    search_titles = [s.get("title") for s in suggestions] if suggestions else [state.get("CandidateProfile", {}).get("jobTitle", "Software Engineer")]

    print(f"🚀 AI suggested titles for search: {search_titles}")

    all_scraped_jobs = []

    # LOOP through each title with Human-like delays to avoid bot detection and allow all suggented titles to be scraped
    for index, title in enumerate(search_titles):
        
        if index > 0:
            delay = random.uniform(2.5, 5.5) # Random sleep between 2.5 and 5.5 seconds
            print(f"😴 Mimicking human behavior... waiting {delay:.2f}s before next search.")
            time.sleep(delay)

        print(f"🔍 Searching for: '{title}' in '{location}'...")
        
        try:
            jobs_df = scrape_jobs(
                site_name=["indeed", "linkedin", "zip_recruiter", "google"],
                search_term=title,
                location=location,
                results_wanted=10, 
                hours_old=72,
                country_indeed='USA',
                linkedin_fetch_description=True 
            )

            if not jobs_df.empty:
                for _, row in jobs_df.iterrows():
                    job_object = {
                        "title": str(row.get('title', 'N/A')),
                        "company": str(row.get('company', 'N/A')),
                        "url": str(row.get('job_url', '')),
                        "description": str(row.get('description', 'No description available.')),
                        "source": str(row.get('site', 'Unknown')),
                        "location": str(row.get('location', 'N/A')),
                        "match_score": 0 
                    }
                    all_scraped_jobs.append(job_object)
                    
        except Exception as e:
            print(f"⚠️ JobSpy failed for '{title}': {e}")
            continue 

 
    seen_urls = set()
    unique_jobs = []
    for job in all_scraped_jobs:
        if job['url'] not in seen_urls:
            unique_jobs.append(job)
            seen_urls.add(job['url'])

    print(f"✅ Total Unique Jobs Found: {len(unique_jobs)}")

    return {
        "job_listings": {"results": unique_jobs, "total_found": len(unique_jobs)},
        "retry_count": state.get("retry_count", 0) + 1
    }