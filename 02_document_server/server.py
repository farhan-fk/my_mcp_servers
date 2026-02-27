"""
Document Tools MCP Server
PDF processing, text extraction, OCR, and document analysis tools
"""
import os
import re
import requests
from typing import Dict, List
from io import BytesIO
from mcp.server.fastmcp import FastMCP

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

port = int(os.getenv("PORT", 8002))
mcp = FastMCP("document_tools", host="0.0.0.0", port=port)


@mcp.tool()
def extract_text_from_pdf(pdf_url: str) -> str:
    """
    Extract all text content from a PDF file.
    
    Use this when you need to read text from PDF documents, extract content
    for analysis, or convert PDFs to plain text format.
    
    Args:
        pdf_url: Direct URL to the PDF file (must be publicly accessible)
    
    Returns:
        Extracted text content with preserved line breaks
    """
    try:
        response = requests.get(pdf_url, timeout=30)
        response.raise_for_status()
        
        pdf_file = BytesIO(response.content)
        
        if PyPDF2:
            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n\n"
            return text.strip()
        else:
            return "Error: PyPDF2 library not installed"
            
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"


@mcp.tool()
def extract_tables_from_pdf(pdf_url: str, page_number: int = None) -> List[Dict]:
    """
    Extract tables from a PDF file as structured data.
    
    Use this when you need to get tabular data from PDFs, such as
    financial reports, research data tables, or statistical information.
    
    Args:
        pdf_url: Direct URL to the PDF file
        page_number: Specific page number to extract from (optional, 1-indexed)
    
    Returns:
        List of tables as dictionaries with headers and rows
    """
    try:
        if not pdfplumber:
            return [{"error": "pdfplumber library not installed"}]
        
        response = requests.get(pdf_url, timeout=30)
        response.raise_for_status()
        
        pdf_file = BytesIO(response.content)
        tables_data = []
        
        with pdfplumber.open(pdf_file) as pdf:
            pages = [pdf.pages[page_number - 1]] if page_number else pdf.pages
            
            for i, page in enumerate(pages):
                tables = page.extract_tables()
                for j, table in enumerate(tables):
                    if table:
                        tables_data.append({
                            'page': page_number if page_number else i + 1,
                            'table_index': j + 1,
                            'headers': table[0] if table else [],
                            'rows': table[1:] if len(table) > 1 else []
                        })
        
        return tables_data if tables_data else [{"message": "No tables found in PDF"}]
        
    except Exception as e:
        return [{"error": f"Error extracting tables: {str(e)}"}]


@mcp.tool()
def count_pdf_pages(pdf_url: str) -> int:
    """
    Count the number of pages in a PDF file.
    
    Use this to determine PDF length before processing or to validate documents.
    
    Args:
        pdf_url: Direct URL to the PDF file
    
    Returns:
        Number of pages in the PDF
    """
    try:
        response = requests.get(pdf_url, timeout=30)
        response.raise_for_status()
        
        pdf_file = BytesIO(response.content)
        
        if PyPDF2:
            reader = PyPDF2.PdfReader(pdf_file)
            return len(reader.pages)
        else:
            return -1  # Error indicator
            
    except Exception as e:
        return -1


@mcp.tool()
def extract_pdf_metadata(pdf_url: str) -> Dict:
    """
    Extract metadata from a PDF file including title, author, creation date, etc.
    
    Use this to get information about a PDF document without reading its full content.
    
    Args:
        pdf_url: Direct URL to the PDF file
    
    Returns:
        Dictionary with PDF metadata (title, author, subject, creator, creation_date, etc.)
    """
    try:
        response = requests.get(pdf_url, timeout=30)
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
            return {"error": "PyPDF2 library not installed"}
            
    except Exception as e:
        return {"error": f"Error extracting metadata: {str(e)}"}


@mcp.tool()
def clean_text(text: str, remove_extra_spaces: bool = True, remove_special_chars: bool = False) -> str:
    """
    Clean and normalize text by removing extra whitespace and optionally special characters.
    
    Use this to prepare text for analysis, remove formatting artifacts, or standardize text data.
    
    Args:
        text: The text to clean
        remove_extra_spaces: Remove multiple spaces and normalize whitespace (default: True)
        remove_special_chars: Remove special characters, keeping only alphanumeric and basic punctuation (default: False)
    
    Returns:
        Cleaned text string
    """
    if remove_extra_spaces:
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace from lines
        text = '\n'.join(line.strip() for line in text.split('\n'))
    
    if remove_special_chars:
        # Keep alphanumeric, spaces, and basic punctuation
        text = re.sub(r'[^a-zA-Z0-9\s\.,;:!?\-\'\"]', '', text)
    
    return text.strip()


@mcp.tool()
def count_words(text: str) -> Dict:
    """
    Count words, characters, sentences, and paragraphs in text.
    
    Use this for document analysis, content metrics, or readability assessment.
    
    Args:
        text: The text to analyze
    
    Returns:
        Dictionary with word count, character count, sentence count, and paragraph count
    """
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


@mcp.tool()
def extract_emails_from_text(text: str) -> List[str]:
    """
    Extract all email addresses from text.
    
    Use this to find contact information in documents or extract recipient lists.
    
    Args:
        text: The text to search for emails
    
    Returns:
        List of unique email addresses found
    """
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return list(set(emails))  # Return unique emails


@mcp.tool()
def extract_urls_from_text(text: str) -> List[str]:
    """
    Extract all URLs from text.
    
    Use this to find links in documents, collect references, or analyze web content.
    
    Args:
        text: The text to search for URLs
    
    Returns:
        List of unique URLs found
    """
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, text)
    return list(set(urls))  # Return unique URLs


if __name__ == "__main__":
    print(f"Starting Document Tools MCP Server on port {port}...")
    print("Available tools: extract_text_from_pdf, extract_tables_from_pdf, count_pdf_pages,")
    print("                 extract_pdf_metadata, clean_text, count_words,")
    print("                 extract_emails_from_text, extract_urls_from_text")
    mcp.run()
