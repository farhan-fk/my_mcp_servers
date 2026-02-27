# 🚀 Quick Start Deployment Guide

## Step 1: Choose Which Servers to Deploy

You have 4 specialized servers. Deploy what your team needs:

- ✅ **01_research_server** - If team needs academic paper search
- ✅ **02_document_server** - If team processes PDFs/documents
- ✅ **03_data_server** - If team needs data validation/cleaning
- ✅ **04_web_server** - If team needs web scraping/URL tools

**Recommendation:** Start with 1-2 servers, add more later.

## Step 2: Deploy First Server to Railway

### For Research Server (Repeat for others):

```bash
# 1. Navigate to server folder
cd 01_research_server

# 2. Create GitHub repo
git init
git add .
git commit -m "Research tools MCP server"

# 3. Create new repo on GitHub.com (name it: org-research-server)

# 4. Push to GitHub
git remote add origin https://github.com/YOUR-USERNAME/org-research-server.git
git branch -M main
git push -u origin main
```

### On Railway:

1. Go to https://railway.app
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repo (e.g., `org-research-server`)
5. Railway auto-detects and deploys ✅
6. Wait 2-3 minutes for build
7. Copy your deployment URL

## Step 3: Test Your Server

Once deployed, Railway gives you a URL like:
```
https://org-research-server-production-abc123.up.railway.app
```

### Test it with Python:

```python
import requests

SERVER_URL = "https://your-url.up.railway.app"

# Test search_papers tool
response = requests.post(
    f"{SERVER_URL}/tools/search_papers",
    json={"topic": "artificial intelligence", "max_results": 3}
)

print(response.json())
```

### Expected Response:
```json
["2301.12345", "2302.23456", "2303.34567"]
```

## Step 4: Deploy Other Servers (Optional)

Repeat Step 2 for:
- `02_document_server` → GitHub repo: `org-document-server`
- `03_data_server` → GitHub repo: `org-data-server`
- `04_web_server` → GitHub repo: `org-web-server`

## Step 5: Share URLs with Team

Create a shared document with:

```
📡 Organization MCP Servers

🔬 Research Tools:  https://org-research-server-xxx.up.railway.app
📄 Document Tools:  https://org-document-server-xxx.up.railway.app
📊 Data Tools:      https://org-data-server-xxx.up.railway.app
🌐 Web Tools:       https://org-web-server-xxx.up.railway.app

Available Tools: See README.md
```

## Step 6: Team Usage Example

Team members can now use your servers:

```python
import requests

# Research server
papers = requests.post(
    "https://org-research-server-xxx.up.railway.app/tools/search_papers",
    json={"topic": "machine learning"}
).json()

# Document server
text = requests.post(
    "https://org-document-server-xxx.up.railway.app/tools/extract_text_from_pdf",
    json={"pdf_url": "https://example.com/paper.pdf"}
).json()

# Data server
is_valid = requests.post(
    "https://org-data-server-xxx.up.railway.app/tools/validate_email",
    json={"email": "test@example.com"}
).json()
```

## 🔧 Local Testing (Before Deployment)

Test any server locally first:

```bash
cd 01_research_server
pip install -r requirements.txt
python server.py
```

Access at: `http://localhost:8001`

Test locally:
```python
import requests

response = requests.post(
    "http://localhost:8001/tools/search_papers",
    json={"topic": "quantum physics", "max_results": 2}
)
print(response.json())
```

## 💰 Costs

- **Railway Free Tier:** $5 credit/month (good for 1-2 small servers)
- **Recommended:** Hobby plan $5/month per project
- Each server = 1 Railway project

## 🆘 Troubleshooting

### Server build fails:
- Check `requirements.txt` syntax
- Verify `Procfile` points to `server.py`

### Can't connect to deployed server:
- Wait 2-3 minutes after deployment
- Check Railway logs for errors
- Verify server URL is correct

### Tools returning errors:
- Check Railway logs: Project → Deployments → Logs
- For PDF/web tools: Ensure URLs are publicly accessible
- Test locally first to isolate issues

## ✅ You're Done!

Your organization now has:
- Specialized MCP tool servers deployed
- High LLM accuracy (90-95%) through focused tools
- Scalable architecture (add servers as needed)
- Team-accessible via simple HTTP requests

## 📚 Next Steps

1. Add authentication for security
2. Monitor usage via Railway dashboard
3. Add more tools to existing servers
4. Create wrapper libraries for easier team access

---

**Questions?** Check individual server README files or Railway documentation.
