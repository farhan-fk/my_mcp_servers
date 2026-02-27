"""
Research Tools REST API Server
Academic paper search, analysis, and citation tools
"""
import arxiv
import json
import os
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

PAPER_DIR = "papers"
port = int(os.getenv("PORT", 8000))

app = FastAPI(title="Research Tools API", version="1.0")


# Request Models
class SearchPapersRequest(BaseModel):
    topic: str
    max_results: int = 5

class ExtractPaperRequest(BaseModel):
    paper_id: str

class SearchByAuthorRequest(BaseModel):
    author_name: str
    max_results: int = 5

class CitationRequest(BaseModel):
    paper_id: str
    format: str = "bibtex"


@app.get("/")
async def root():
    return {
        "service": "Research Tools API",
        "version": "1.0",
        "tools": ["search_papers", "extract_paper_info", "search_papers_by_author", "get_paper_citation"]
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/tools/search_papers")
async def search_papers(request: SearchPapersRequest) -> List[str]:
    """Search for academic papers on arXiv by topic."""
    max_results = min(request.max_results, 20)
        
    client = arxiv.Client()
    search = arxiv.Search(
        query=request.topic,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    
    papers = client.results(search)
    
    # Store papers info
    path = os.path.join(PAPER_DIR, request.topic.lower().replace(" ", "_"))
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


@app.post("/tools/extract_paper_info")
async def extract_paper_info(request: ExtractPaperRequest) -> Dict:
    """Get detailed information about a specific paper."""
    os.makedirs(PAPER_DIR, exist_ok=True)
    
    for item in os.listdir(PAPER_DIR):
        item_path = os.path.join(PAPER_DIR, item)
        if os.path.isdir(item_path):
            file_path = os.path.join(item_path, "papers_info.json")
            if os.path.isfile(file_path):
                try:
                    with open(file_path, "r") as f:
                        papers_info = json.load(f)
                        if request.paper_id in papers_info:
                            return papers_info[request.paper_id]
                except (FileNotFoundError, json.JSONDecodeError):
                    continue
    
    raise HTTPException(status_code=404, detail=f"No information found for paper {request.paper_id}. Try searching first.")


@app.post("/tools/search_papers_by_author")
async def search_papers_by_author(request: SearchByAuthorRequest) -> List[Dict]:
    """Search for papers by a specific author on arXiv."""
    max_results = min(request.max_results, 15)
        
    client = arxiv.Client()
    search = arxiv.Search(
        query=f"au:{request.author_name}",
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


@app.post("/tools/get_paper_citation")
async def get_paper_citation(request: CitationRequest) -> Dict:
    """Generate a citation for a paper in various formats."""
    os.makedirs(PAPER_DIR, exist_ok=True)
    
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
                        if request.paper_id in papers_info:
                            paper_info = papers_info[request.paper_id]
                            break
                except:
                    continue
    
    if not paper_info:
        raise HTTPException(status_code=404, detail=f"Paper {request.paper_id} not found. Search for it first.")
    
    authors = paper_info['authors']
    title = paper_info['title']
    year = paper_info['published'].split('-')[0]
    
    if request.format == "bibtex":
        author_str = " and ".join(authors)
        citation = f"""@article{{{request.paper_id},
  author = {{{author_str}}},
  title = {{{title}}},
  journal = {{arXiv preprint arXiv:{request.paper_id}}},
  year = {{{year}}},
  url = {{{paper_info['pdf_url']}}}
}}"""
    
    elif request.format == "apa":
        if len(authors) == 1:
            author_str = authors[0]
        elif len(authors) == 2:
            author_str = f"{authors[0]} & {authors[1]}"
        else:
            author_str = f"{authors[0]} et al."
        citation = f"{author_str} ({year}). {title}. arXiv preprint arXiv:{request.paper_id}."
    
    else:  # simple
        author_str = authors[0] if authors else "Unknown"
        citation = f"{author_str} ({year}). {title}. arXiv:{request.paper_id}"
    
    return {"citation": citation, "format": request.format}


if __name__ == "__main__":
    print(f"Starting Research Tools REST API Server on port {port}...")
    print("Available endpoints:")
    print("  POST /tools/search_papers")
    print("  POST /tools/extract_paper_info")
    print("  POST /tools/search_papers_by_author")
    print("  POST /tools/get_paper_citation")
    
    uvicorn.run(app, host="0.0.0.0", port=port)
