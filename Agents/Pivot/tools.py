from langchain_core.tools import tool
from tavily import TavilyClient
import os


tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def career_discovery_search(query: str):
    """
    Searches for high-growth, hybrid, and emerging career paths trending in 2026.
    Use this for broad trend discovery.
    """
    # Use .search() for the raw Tavily Python client
    return tavily_client.search(query=query, max_results=5)

@tool
def deep_dive_market_scraper(role_title: str):
    """
    Scrapes specific job boards and industry reports for technical
    requirements for a target job title. Use this for specific validation.
    """
    query = f"technical requirements and responsibilities for {role_title} 2026 job postings"
    return tavily_client.search(query=query, search_depth="advanced")

if __name__ == "__main__":
    # Test the raw client functionality
    print("Executing test search...")
    try:
        response = tavily_client.search(query="Latest AI engineering roles 2026")
        print("Search successful. Results found.")
        # To test the tool specifically:
        # print(career_discovery_search.invoke("Top 2026 tech trends"))
    except Exception as e:
        print(f"Error: {e}")