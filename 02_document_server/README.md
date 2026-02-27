# 📄 Document Tools MCP Server

PDF processing, text extraction, and document analysis tools.

## 🛠️ Available Tools

### `extract_text_from_pdf(pdf_url)`
Extract all text content from a PDF file.

### `extract_tables_from_pdf(pdf_url, page_number=None)`
Extract tables from PDFs as structured data.

### `count_pdf_pages(pdf_url)`
Count the number of pages in a PDF.

### `extract_pdf_metadata(pdf_url)`
Get PDF metadata (title, author, creation date, etc.).

### `clean_text(text, remove_extra_spaces=True, remove_special_chars=False)`
Clean and normalize text content.

### `count_words(text)`
Count words, characters, sentences, and paragraphs.

### `extract_emails_from_text(text)`
Find all email addresses in text.

### `extract_urls_from_text(text)`
Find all URLs in text.

## 🚀 Deploy to Railway

1. Push this folder to GitHub
2. Connect to Railway
3. Deploy
4. Share URL with team

## 📡 Server URL
`https://your-document-server.up.railway.app`

Port: 8002 (local) / Dynamic (Railway)
