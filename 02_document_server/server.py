"""
Document Tools REST API Server
PDF processing, text extraction, OCR, and document analysis tools
"""
import os
import re
import requests
from typing import Dict, List
from io import BytesIO
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

port = int(os.getenv("PORT", 8000))
app = FastAPI(title="Document Tools API", version="1.0")


# Request Models
class PDFURLRequest(BaseModel):
    pdf_url: str

class ExtractTablesRequest(BaseModel):
    pdf_url: str
    page_number: int = None

class CleanTextRequest(BaseModel):
    text: str
    remove_extra_spaces: bool = True
    remove_special_chars: bool = False

class TextRequest(BaseModel):
    text: str


@app.get("/")
async def root():
    return {
        "service": "Document Tools API",
        "version": "1.0",
        "tools": [
            "extract_text_from_pdf", "extract_tables_from_pdf", "count_pdf_pages",
            "extract_pdf_metadata", "clean_text", "count_words",
            "extract_emails_from_text", "extract_urls_from_text"
        ]
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/tools/extract_text_from_pdf")
async def extract_text_from_pdf(request: PDFURLRequest) -> Dict:
    """Extract all text content from a PDF file."""
    try:
        response = requests.get(request.pdf_url, timeout=30)
        response.raise_for_status()
        
        pdf_file = BytesIO(response.content)
        
        if PyPDF2:
            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n\n"
            return {"text": text.strip()}
        else:
            raise HTTPException(status_code=500, detail="PyPDF2 library not installed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting text from PDF: {str(e)}")


@app.post("/tools/extract_tables_from_pdf")
async def extract_tables_from_pdf(request: ExtractTablesRequest) -> List[Dict]:
    """Extract tables from a PDF file as structured data."""
    try:
        if not pdfplumber:
            raise HTTPException(status_code=500, detail="pdfplumber library not installed")
        
        response = requests.get(request.pdf_url, timeout=30)
        response.raise_for_status()
        
        pdf_file = BytesIO(response.content)
        tables_data = []
        
        with pdfplumber.open(pdf_file) as pdf:
            pages = [pdf.pages[request.page_number - 1]] if request.page_number else pdf.pages
            
            for i, page in enumerate(pages):
                tables = page.extract_tables()
                for j, table in enumerate(tables):
                    if table:
                        tables_data.append({
                            'page': request.page_number if request.page_number else i + 1,
                            'table_index': j + 1,
                            'headers': table[0] if table else [],
                            'rows': table[1:] if len(table) > 1 else []
                        })
        
        return tables_data if tables_data else [{"message": "No tables found in PDF"}]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting tables: {str(e)}")


@app.post("/tools/count_pdf_pages")
async def count_pdf_pages(request: PDFURLRequest) -> Dict:
    """Count the number of pages in a PDF file."""
    try:
        response = requests.get(request.pdf_url, timeout=30)
        response.raise_for_status()
        
        pdf_file = BytesIO(response.content)
        
        if PyPDF2:
            reader = PyPDF2.PdfReader(pdf_file)
            return {"num_pages": len(reader.pages)}
        else:
            raise HTTPException(status_code=500, detail="PyPDF2 library not installed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error counting pages: {str(e)}")


@app.post("/tools/extract_pdf_metadata")
async def extract_pdf_metadata(request: PDFURLRequest) -> Dict:
    """Extract metadata from a PDF file including title, author, creation date, etc."""
    try:
        response = requests.get(request.pdf_url, timeout=30)
        response.raise_for_status()
        
        pdf_file = BytesIO(response.content)
        
        if PyPDF2:
            reader = PyPDF2.PdfReader(pdf_file)
            metadata = reader.metadata
            
            result = {
                'num_pages': len(reader.pages),
                'title': metadata.get('/Title', 'N/A') if metadata else 'N/A',
                'author': metadata.get('/Author', 'N/A') if metadata else 'N/A',
                'subject': metadata.get('/Subject', 'N/A') if metadata else 'N/A',
                'creator': metadata.get('/Creator', 'N/A') if metadata else 'N/A',
                'producer': metadata.get('/Producer', 'N/A') if metadata else 'N/A',
                'creation_date': str(metadata.get('/CreationDate', 'N/A')) if metadata else 'N/A'
            }
            return result
        else:
            raise HTTPException(status_code=500, detail="PyPDF2 library not installed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting metadata: {str(e)}")


@app.post("/tools/clean_text")
async def clean_text(request: CleanTextRequest) -> Dict:
    """Clean and normalize text by removing extra whitespace and optionally special characters."""
    text = request.text
    
    if request.remove_extra_spaces:
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace from lines
        text = '\n'.join(line.strip() for line in text.split('\n'))
    
    if request.remove_special_chars:
        # Keep alphanumeric, spaces, and basic punctuation
        text = re.sub(r'[^a-zA-Z0-9\s\.,;:!?\-\'\"]', '', text)
    
    return {"cleaned_text": text.strip()}


@app.post("/tools/count_words")
async def count_words(request: TextRequest) -> Dict:
    """Count words, characters, sentences, and paragraphs in text."""
    text = request.text
    words = len(text.split())
    characters = len(text)
    characters_no_spaces = len(text.replace(' ', '').replace('\n', ''))
    sentences = len(re.split(r'[.!?]+', text)) - 1
    paragraphs = len([p for p in text.split('\n\n') if p.strip()])
    
    return {
        'words': words,
        'characters': characters,
        'characters_no_spaces': characters_no_spaces,
        'sentences': max(sentences, 1),
        'paragraphs': max(paragraphs, 1),
        'avg_word_length': round(characters_no_spaces / words, 2) if words > 0 else 0
    }


@app.post("/tools/extract_emails_from_text")
async def extract_emails_from_text(request: TextRequest) -> Dict:
    """Extract all email addresses from text."""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, request.text)
    return {"emails": list(set(emails))}


@app.post("/tools/extract_urls_from_text")
async def extract_urls_from_text(request: TextRequest) -> Dict:
    """Extract all URLs from text."""
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, request.text)
    return {"urls": list(set(urls))}


if __name__ == "__main__":
    print(f"Starting Document Tools REST API Server on port {port}...")
    print("Available endpoints:")
    print("  POST /tools/extract_text_from_pdf")
    print("  POST /tools/extract_tables_from_pdf")
    print("  POST /tools/count_pdf_pages")
    print("  POST /tools/extract_pdf_metadata")
    print("  POST /tools/clean_text")
    print("  POST /tools/count_words")
    print("  POST /tools/extract_emails_from_text")
    print("  POST /tools/extract_urls_from_text")
    
    uvicorn.run(app, host="0.0.0.0", port=port)
