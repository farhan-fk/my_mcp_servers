"""
Data Tools REST API Server
Data validation, cleaning, transformation, and analysis tools
"""
import os
import re
import json
import csv
from typing import Dict, List, Any
from io import StringIO
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Get port from environment
port = int(os.getenv("PORT", 8000))

app = FastAPI(title="Data Tools API", version="1.0")


# Request/Response Models
class EmailValidationRequest(BaseModel):
    email: str

class URLValidationRequest(BaseModel):
    url: str

class PhoneValidationRequest(BaseModel):
    phone: str
    country_code: str = "US"

class CSVToJSONRequest(BaseModel):
    csv_data: str
    has_header: bool = True

class JSONToCSVRequest(BaseModel):
    json_data: str

class CleanStringRequest(BaseModel):
    text: str
    lowercase: bool = False
    remove_punctuation: bool = False
    remove_numbers: bool = False
    trim: bool = True

class DetectDataTypeRequest(BaseModel):
    value: str

class FindDuplicatesRequest(BaseModel):
    items: List[str]

class NormalizeWhitespaceRequest(BaseModel):
    text: str

class CalculateStatisticsRequest(BaseModel):
    numbers: List[float]


@app.get("/")
async def root():
    return {
        "service": "Data Tools API",
        "version": "1.0",
        "tools": [
            "validate_email", "validate_url", "validate_phone",
            "csv_to_json", "json_to_csv", "clean_string",
            "detect_data_type", "find_duplicates",
            "normalize_whitespace", "calculate_statistics"
        ]
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/tools/validate_email")
async def validate_email(request: EmailValidationRequest) -> Dict:
    """Validate if an email address is properly formatted."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    is_valid = bool(re.match(pattern, request.email))
    
    return {
        'valid': is_valid,
        'email': request.email,
        'message': 'Valid email format' if is_valid else 'Invalid email format'
    }


@app.post("/tools/validate_url")
async def validate_url(request: URLValidationRequest) -> Dict:
    """Validate if a URL is properly formatted."""
    pattern = r'^https?://[^\s<>"{}|\\^`\[\]]+'
    is_valid = bool(re.match(pattern, request.url))
    
    result = {
        'valid': is_valid,
        'url': request.url,
        'message': 'Valid URL format' if is_valid else 'Invalid URL format'
    }
    
    if is_valid:
        result['protocol'] = 'https' if request.url.startswith('https') else 'http'
        result['domain'] = request.url.split('/')[2] if len(request.url.split('/')) > 2 else ''
    
    return result


@app.post("/tools/validate_phone")
async def validate_phone(request: PhoneValidationRequest) -> Dict:
    """Validate if a phone number is properly formatted."""
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)\.]+', '', request.phone)
    
    # Basic validation for US numbers (10 digits)
    if request.country_code == "US":
        is_valid = bool(re.match(r'^\+?1?\d{10}$', cleaned))
        return {
            'valid': is_valid,
            'phone': request.phone,
            'cleaned': cleaned,
            'message': 'Valid US phone number' if is_valid else 'Invalid US phone number (need 10 digits)'
        }
    else:
        # Generic validation: 7-15 digits
        is_valid = bool(re.match(r'^\+?\d{7,15}$', cleaned))
        return {
            'valid': is_valid,
            'phone': request.phone,
            'cleaned': cleaned,
            'message': 'Valid phone format' if is_valid else 'Invalid phone format'
        }


@app.post("/tools/csv_to_json")
async def csv_to_json(request: CSVToJSONRequest) -> str:
    """Convert CSV data to JSON format."""
    try:
        csv_file = StringIO(request.csv_data)
        reader = csv.reader(csv_file)
        
        rows = list(reader)
        if not rows:
            return json.dumps({"error": "No data provided"})
        
        if request.has_header:
            headers = rows[0]
            data = []
            for row in rows[1:]:
                row_dict = {headers[i]: row[i] if i < len(row) else '' for i in range(len(headers))}
                data.append(row_dict)
        else:
            data = [{"col_" + str(i): val for i, val in enumerate(row)} for row in rows]
        
        return json.dumps(data, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to convert CSV: {str(e)}"})


@app.post("/tools/json_to_csv")
async def json_to_csv(request: JSONToCSVRequest) -> str:
    """Convert JSON array to CSV format."""
    try:
        data = json.loads(request.json_data)
        
        if not isinstance(data, list) or not data:
            return "Error: JSON must be a non-empty array of objects"
        
        # Get all unique keys from all objects
        keys = set()
        for item in data:
            if isinstance(item, dict):
                keys.update(item.keys())
        
        keys = sorted(keys)
        
        # Create CSV
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
        
        return output.getvalue()
        
    except json.JSONDecodeError:
        return "Error: Invalid JSON format"
    except Exception as e:
        return f"Error converting JSON to CSV: {str(e)}"


@app.post("/tools/clean_string")
async def clean_string(request: CleanStringRequest) -> str:
    """Clean and normalize string data with various options."""
    result = request.text
    
    if request.trim:
        result = result.strip()
    
    if request.lowercase:
        result = result.lower()
    
    if request.remove_punctuation:
        result = re.sub(r'[^\w\s]', '', result)
    
    if request.remove_numbers:
        result = re.sub(r'\d+', '', result)
    
    # Normalize whitespace
    result = re.sub(r'\s+', ' ', result)
    
    return result.strip()


@app.post("/tools/detect_data_type")
async def detect_data_type(request: DetectDataTypeRequest) -> Dict:
    """Detect the data type of a string value."""
    value = request.value.strip()
    
    # Check for empty
    if not value:
        return {'type': 'empty', 'confidence': 'high'}
    
    # Check for boolean
    if value.lower() in ['true', 'false', 'yes', 'no', '0', '1']:
        return {'type': 'boolean', 'confidence': 'medium', 'value': value}
    
    # Check for number
    try:
        float(value)
        if '.' in value:
            return {'type': 'float', 'confidence': 'high', 'value': float(value)}
        else:
            return {'type': 'integer', 'confidence': 'high', 'value': int(value)}
    except ValueError:
        pass
    
    # Check for email
    if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
        return {'type': 'email', 'confidence': 'high', 'value': value}
    
    # Check for URL
    if re.match(r'^https?://[^\s]+$', value):
        return {'type': 'url', 'confidence': 'high', 'value': value}
    
    # Check for date (simple patterns)
    date_patterns = [
        r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
        r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
        r'\d{2}-\d{2}-\d{4}'   # DD-MM-YYYY
    ]
    for pattern in date_patterns:
        if re.match(pattern, value):
            return {'type': 'date', 'confidence': 'medium', 'value': value}
    
    # Default to string
    return {'type': 'string', 'confidence': 'high', 'value': value}


@app.post("/tools/find_duplicates")
async def find_duplicates(request: FindDuplicatesRequest) -> Dict:
    """Find duplicate values in a list."""
    from collections import Counter
    
    counts = Counter(request.items)
    duplicates = {item: count for item, count in counts.items() if count > 1}
    
    return {
        'total_items': len(request.items),
        'unique_items': len(counts),
        'duplicate_count': len(duplicates),
        'duplicates': duplicates,
        'has_duplicates': len(duplicates) > 0
    }


@app.post("/tools/normalize_whitespace")
async def normalize_whitespace(request: NormalizeWhitespaceRequest) -> str:
    """Normalize all whitespace in text to single spaces."""
    # Replace all whitespace (spaces, tabs, newlines) with single space
    normalized = re.sub(r'\s+', ' ', request.text)
    return normalized.strip()


@app.post("/tools/calculate_statistics")
async def calculate_statistics(request: CalculateStatisticsRequest) -> Dict:
    """Calculate basic statistics for a list of numbers."""
    if not request.numbers:
        return {'error': 'Empty list provided'}
    
    sorted_numbers = sorted(request.numbers)
    n = len(request.numbers)
    
    result = {
        'count': n,
        'sum': sum(request.numbers),
        'mean': sum(request.numbers) / n,
        'min': min(request.numbers),
        'max': max(request.numbers),
        'range': max(request.numbers) - min(request.numbers)
    }
    
    # Calculate median
    if n % 2 == 0:
        result['median'] = (sorted_numbers[n//2 - 1] + sorted_numbers[n//2]) / 2
    else:
        result['median'] = sorted_numbers[n//2]
    
    return result


if __name__ == "__main__":
    print(f"Starting Data Tools REST API Server on port {port}...")
    print("Available endpoints:")
    print("  POST /tools/validate_email")
    print("  POST /tools/validate_url")
    print("  POST /tools/validate_phone")
    print("  POST /tools/csv_to_json")
    print("  POST /tools/json_to_csv")
    print("  POST /tools/clean_string")
    print("  POST /tools/detect_data_type")
    print("  POST /tools/find_duplicates")
    print("  POST /tools/normalize_whitespace")
    print("  POST /tools/calculate_statistics")
    
    uvicorn.run(app, host="0.0.0.0", port=port)
