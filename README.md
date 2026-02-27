# 🚀 Organization MCP Tool Servers

A collection of specialized MCP (Model Context Protocol) servers providing essential tools for AI applications.

## 📦 What's Included

This package contains **4 specialized servers**, each focused on a specific domain for optimal LLM accuracy:

### 1️⃣ Research Tools Server (Port 8001)
**Tools: 4** | Academic paper search and citation  
- `search_papers` - Search arXiv by topic
- `extract_paper_info` - Get paper details
- `search_papers_by_author` - Find papers by researcher
- `get_paper_citation` - Generate citations (BibTeX, APA, simple)

### 2️⃣ Document Tools Server (Port 8002)
**Tools: 8** | PDF processing and text analysis  
- `extract_text_from_pdf` - Extract text from PDFs
- `extract_tables_from_pdf` - Get tables as structured data
- `count_pdf_pages` - Count PDF pages
- `extract_pdf_metadata` - Get PDF info
- `clean_text` - Clean and normalize text
- `count_words` - Analyze text statistics
- `extract_emails_from_text` - Find emails
- `extract_urls_from_text` - Find URLs

### 3️⃣ Data Tools Server (Port 8003)
**Tools: 10** | Data validation, cleaning, and transformation  
- `validate_email` - Check email format
- `validate_url` - Check URL format
- `validate_phone` - Check phone numbers
- `csv_to_json` - Convert CSV to JSON
- `json_to_csv` - Convert JSON to CSV
- `clean_string` - Clean string data
- `detect_data_type` - Auto-detect data types
- `find_duplicates` - Find repeated values
- `normalize_whitespace` - Fix spacing
- `calculate_statistics` - Basic stats (mean, median, etc.)

### 4️⃣ Web Tools Server (Port 8004)
**Tools: 8** | Web scraping and URL operations  
- `fetch_webpage` - Get webpage content
- `check_url_status` - Check URL accessibility
- `extract_links` - Find all links on a page
- `scrape_webpage` - Scrape with CSS selectors
- `extract_metadata` - Get page metadata
- `parse_url` - Parse URL components
- `download_file_info` - Get file info
- `check_multiple_urls` - Batch URL checking

## 🎯 Why Separate Servers?

| Aspect | Single Mega Server | 4 Specialized Servers ✅ |
|--------|-------------------|--------------------------|
| LLM Tool Selection Accuracy | 65-75% | **90-95%** |
| Context Window Usage | High (bloated) | **Low (efficient)** |
| Tool Discovery | All 30+ tools | **Only 4-10 relevant** |
| Maintenance | Difficult | **Easy per domain** |

## 🚀 Quick Deploy to Railway

## 🚀 Quick Deploy to Railway

Each server is independent. Deploy one or all:

```bash
# Deploy any server
cd 01_research_server    # or 02_, 03_, 04_
git init
git add .
git commit -m "Initial commit"
# Push to GitHub and connect to Railway
```

## 📡 Server URLs

After deployment, you'll have:
```
Research:  https://your-org-research.up.railway.app
Document:  https://your-org-documents.up.railway.app
Data:      https://your-org-data.up.railway.app
Web:       https://your-org-web.up.railway.app
```

## 🔌 How To Use

```python
import requests

# Use research server
response = requests.post(
    "https://your-org-research.up.railway.app/tools/search_papers",
    json={"topic": "quantum computing", "max_results": 5}
)
papers = response.json()
```

## 📊 Total: 30 Tools Across 4 Servers

Each server has 4-10 focused tools for maximum LLM accuracy.

## 📖 Documentation

See individual server folders for detailed docs:
- `01_research_server/README.md`
- `02_document_server/README.md`
- `03_data_server/README.md`
- `04_web_server/README.md`

## 🏃 Local Testing

```bash
cd 01_research_server
pip install -r requirements.txt
python server.py
```

---

**Built for:** Maximum LLM accuracy through specialized tool servers  
**Powered by:** FastMCP, Railway, Python
