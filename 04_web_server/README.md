# 🌐 Web Tools MCP Server

Web scraping, URL operations, and HTTP utilities.

## 🛠️ Available Tools

### `fetch_webpage(url, timeout=10)`
Fetch the content of a webpage.

### `check_url_status(url, timeout=5)`
Check if a URL is accessible and get HTTP status.

### `extract_links(url, filter_external=False)`
Extract all links from a webpage.

### `scrape_webpage(url, css_selector=None)`
Scrape specific content using CSS selectors.

### `extract_metadata(url)`
Extract page metadata (title, description, Open Graph tags).

### `parse_url(url)`
Parse URL into components (scheme, domain, path, parameters).

### `download_file_info(url)`
Get file information without downloading (size, type).

### `check_multiple_urls(urls, timeout=5)`
Check status of multiple URLs at once.

## 🚀 Deploy to Railway

1. Push this folder to GitHub
2. Connect to Railway
3. Deploy
4. Share URL with team

## 📡 Server URL
`https://your-web-server.up.railway.app`

Port: 8004 (local) / Dynamic (Railway)
