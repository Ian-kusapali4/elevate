from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool

# Initialize Tavily with your API key
# Tavily is a search engine optimized specifically for LLMs and Agents
tavily_search = TavilySearchResults(
    max_results=3,
    tavily_api_key="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" 
    )

@tool
def career_discovery_search(query: str):
    """
    Searches for high-growth, hybrid, and emerging career paths trending in 2026.
    Use this for broad trend discovery.
    """
    return tavily_search.invoke({"query": query})

@tool
def deep_dive_market_scraper(role_title: str):
    """
    Scrapes specific job boards and industry reports for technical
    requirements for a target job title. Use this for specific validation.
    """
    query = f"technical requirements and responsibilities for {role_title} 2026 job postings"
    return tavily_search.invoke({"query": query})

if __name__ == "__main__":
    # Internal test to ensure the Tavily connection is active
    print("Executing test search...")
    print(tavily_search.invoke("Latest AI engineering roles 2026"))