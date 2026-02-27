"""
Research Tools MCP Server
Academic paper search, analysis, and citation tools
"""
import arxiv
import json
import os
from typing import List, Dict
from mcp.server.fastmcp import FastMCP

PAPER_DIR = "papers"
port = int(os.getenv("PORT", 8001))

mcp = FastMCP("research_tools", host="0.0.0.0", port=port)

@mcp.tool()
def search_papers(topic: str, max_results: int = 5) -> List[str]:
    """
    Search for academic papers on arXiv by topic.
    
    Use this when you need to find research papers, scientific articles,
    or academic publications on any topic.
    
    Args:
        topic: The research topic or keywords to search for
        max_results: Maximum number of results to retrieve (default: 5, max: 20)
    
    Returns:
        List of paper IDs that can be used with extract_paper_info
    """
    if max_results > 20:
        max_results = 20
        
    client = arxiv.Client()
    search = arxiv.Search(
        query=topic,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    
    papers = client.results(search)
    
    # Store papers info
    path = os.path.join(PAPER_DIR, topic.lower().replace(" ", "_"))
    os.makedirs(path, exist_ok=True)
    file_path = os.path.join(path, "papers_info.json")
    
    try:
        with open(file_path, "r") as f:
            papers_info = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        papers_info = {}
    
    paper_ids = []
    for paper in papers:
        paper_id = paper.get_short_id()
        paper_ids.append(paper_id)
        papers_info[paper_id] = {
            'title': paper.title,
            'authors': [author.name for author in paper.authors],
            'summary': paper.summary,
            'pdf_url': paper.pdf_url,
            'published': str(paper.published.date()),
            'categories': paper.categories
        }
    
    with open(file_path, "w") as f:
        json.dump(papers_info, f, indent=2)
    
    return paper_ids


@mcp.tool()
def extract_paper_info(paper_id: str) -> str:
    """
    Get detailed information about a specific paper.
    
    Use this after search_papers to get full details about a paper including
    title, authors, abstract, PDF URL, and publication date.
    
    Args:
        paper_id: The arXiv paper ID (e.g., "2301.12345")
    
    Returns:
        JSON string with paper details or error message if not found
    """
    for item in os.listdir(PAPER_DIR):
        item_path = os.path.join(PAPER_DIR, item)
        if os.path.isdir(item_path):
            file_path = os.path.join(item_path, "papers_info.json")
            if os.path.isfile(file_path):
                try:
                    with open(file_path, "r") as f:
                        papers_info = json.load(f)
                        if paper_id in papers_info:
                            return json.dumps(papers_info[paper_id], indent=2)
                except (FileNotFoundError, json.JSONDecodeError):
                    continue
    
    return f"No information found for paper {paper_id}. Try searching first."


@mcp.tool()
def search_papers_by_author(author_name: str, max_results: int = 5) -> List[Dict]:
    """
    Search for papers by a specific author on arXiv.
    
    Use this when you need to find all papers written by a particular researcher.
    
    Args:
        author_name: Full or partial name of the author
        max_results: Maximum number of results (default: 5, max: 15)
    
    Returns:
        List of dictionaries with paper ID, title, and publication date
    """
    if max_results > 15:
        max_results = 15
        
    client = arxiv.Client()
    search = arxiv.Search(
        query=f"au:{author_name}",
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    
    papers = client.results(search)
    results = []
    
    for paper in papers:
        results.append({
            'paper_id': paper.get_short_id(),
            'title': paper.title,
            'published': str(paper.published.date()),
            'authors': [author.name for author in paper.authors]
        })
    
    return results


@mcp.tool()
def get_paper_citation(paper_id: str, format: str = "bibtex") -> str:
    """
    Generate a citation for a paper in various formats.
    
    Use this when you need to cite a paper in your work.
    
    Args:
        paper_id: The arXiv paper ID
        format: Citation format - "bibtex", "apa", or "simple" (default: "bibtex")
    
    Returns:
        Formatted citation string
    """
    # Find paper info
    paper_info = None
    for item in os.listdir(PAPER_DIR):
        item_path = os.path.join(PAPER_DIR, item)
        if os.path.isdir(item_path):
            file_path = os.path.join(item_path, "papers_info.json")
            if os.path.isfile(file_path):
                try:
                    with open(file_path, "r") as f:
                        papers_info = json.load(f)
                        if paper_id in papers_info:
                            paper_info = papers_info[paper_id]
                            break
                except:
                    continue
    
    if not paper_info:
        return f"Paper {paper_id} not found. Search for it first."
    
    authors = paper_info['authors']
    title = paper_info['title']
    year = paper_info['published'].split('-')[0]
    
    if format == "bibtex":
        author_str = " and ".join(authors)
        return f"""@article{{{paper_id},
  author = {{{author_str}}},
  title = {{{title}}},
  journal = {{arXiv preprint arXiv:{paper_id}}},
  year = {{{year}}},
  url = {{{paper_info['pdf_url']}}}
}}"""
    
    elif format == "apa":
        if len(authors) == 1:
            author_str = authors[0]
        elif len(authors) == 2:
            author_str = f"{authors[0]} & {authors[1]}"
        else:
            author_str = f"{authors[0]} et al."
        return f"{author_str} ({year}). {title}. arXiv preprint arXiv:{paper_id}."
    
    else:  # simple
        author_str = authors[0] if authors else "Unknown"
        return f"{author_str} ({year}). {title}. arXiv:{paper_id}"


if __name__ == "__main__":
    print(f"Starting Research Tools MCP Server on port {port}...")
    print("Available tools: search_papers, extract_paper_info, search_papers_by_author, get_paper_citation")
    mcp.run()
