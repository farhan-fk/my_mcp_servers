"""
Data Tools MCP Server
Data validation, cleaning, transformation, and analysis tools
"""
import os
import re
import json
import csv
from typing import Dict, List, Any
from io import StringIO
from mcp.server.fastmcp import FastMCP

port = int(os.getenv("PORT", 8003))
mcp = FastMCP("data_tools", host="0.0.0.0", port=port)


@mcp.tool()
def validate_email(email: str) -> Dict:
    """
    Validate if an email address is properly formatted.
    
    Use this to check email validity before sending messages or storing contact info.
    
    Args:
        email: The email address to validate
    
    Returns:
        Dictionary with 'valid' boolean and 'message' explaining result
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    is_valid = bool(re.match(pattern, email))
    
    return {
        'valid': is_valid,
        'email': email,
        'message': 'Valid email format' if is_valid else 'Invalid email format'
    }


@mcp.tool()
def validate_url(url: str) -> Dict:
    """
    Validate if a URL is properly formatted.
    
    Use this to check URL validity before making requests or storing links.
    
    Args:
        url: The URL to validate
    
    Returns:
        Dictionary with 'valid' boolean, URL components, and validation message
    """
    pattern = r'^https?://[^\s<>"{}|\\^`\[\]]+'
    is_valid = bool(re.match(pattern, url))
    
    result = {
        'valid': is_valid,
        'url': url,
        'message': 'Valid URL format' if is_valid else 'Invalid URL format'
    }
    
    if is_valid:
        # Extract components
        result['protocol'] = 'https' if url.startswith('https') else 'http'
        result['domain'] = url.split('/')[2] if len(url.split('/')) > 2 else ''
    
    return result


@mcp.tool()
def validate_phone(phone: str, country_code: str = "US") -> Dict:
    """
    Validate if a phone number is properly formatted.
    
    Use this to check phone number validity before storing or processing contact info.
    
    Args:
        phone: The phone number to validate
        country_code: Country code for validation (default: "US")
    
    Returns:
        Dictionary with 'valid' boolean and 'message'
    """
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)\.]+', '', phone)
    
    # Basic validation for US numbers (10 digits)
    if country_code == "US":
        is_valid = bool(re.match(r'^\+?1?\d{10}$', cleaned))
        return {
            'valid': is_valid,
            'phone': phone,
            'cleaned': cleaned,
            'message': 'Valid US phone number' if is_valid else 'Invalid US phone number (need 10 digits)'
        }
    else:
        # Generic validation: 7-15 digits
        is_valid = bool(re.match(r'^\+?\d{7,15}$', cleaned))
        return {
            'valid': is_valid,
            'phone': phone,
            'cleaned': cleaned,
            'message': 'Valid phone format' if is_valid else 'Invalid phone format'
        }


@mcp.tool()
def csv_to_json(csv_data: str, has_header: bool = True) -> str:
    """
    Convert CSV data to JSON format.
    
    Use this to transform CSV data into JSON for API consumption or data processing.
    
    Args:
        csv_data: CSV data as a string
        has_header: Whether the first row contains headers (default: True)
    
    Returns:
        JSON string representation of the CSV data
    """
    try:
        csv_file = StringIO(csv_data)
        reader = csv.reader(csv_file)
        
        rows = list(reader)
        if not rows:
            return json.dumps({"error": "No data provided"})
        
        if has_header:
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


@mcp.tool()
def json_to_csv(json_data: str) -> str:
    """
    Convert JSON array to CSV format.
    
    Use this to transform JSON data into CSV for spreadsheet import or reporting.
    
    Args:
        json_data: JSON string (must be an array of objects)
    
    Returns:
        CSV formatted string
    """
    try:
        data = json.loads(json_data)
        
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


@mcp.tool()
def clean_string(text: str, lowercase: bool = False, remove_punctuation: bool = False, 
                 remove_numbers: bool = False, trim: bool = True) -> str:
    """
    Clean and normalize string data with various options.
    
    Use this to prepare text data for analysis, comparison, or storage.
    
    Args:
        text: The text to clean
        lowercase: Convert to lowercase (default: False)
        remove_punctuation: Remove punctuation marks (default: False)
        remove_numbers: Remove numeric characters (default: False)
        trim: Remove leading/trailing whitespace (default: True)
    
    Returns:
        Cleaned string
    """
    result = text
    
    if trim:
        result = result.strip()
    
    if lowercase:
        result = result.lower()
    
    if remove_punctuation:
        result = re.sub(r'[^\w\s]', '', result)
    
    if remove_numbers:
        result = re.sub(r'\d+', '', result)
    
    # Normalize whitespace
    result = re.sub(r'\s+', ' ', result)
    
    return result.strip()


@mcp.tool()
def detect_data_type(value: str) -> Dict:
    """
    Detect the data type of a string value (number, email, url, date, etc.).
    
    Use this to automatically classify and validate data fields.
    
    Args:
        value: The string value to analyze
    
    Returns:
        Dictionary with detected type and confidence
    """
    value = value.strip()
    
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


@mcp.tool()
def find_duplicates(items: List[str]) -> Dict:
    """
    Find duplicate values in a list.
    
    Use this to identify repeated entries in data sets or validate uniqueness.
    
    Args:
        items: List of strings to check for duplicates
    
    Returns:
        Dictionary with duplicates, their counts, and statistics
    """
    from collections import Counter
    
    counts = Counter(items)
    duplicates = {item: count for item, count in counts.items() if count > 1}
    
    return {
        'total_items': len(items),
        'unique_items': len(counts),
        'duplicate_count': len(duplicates),
        'duplicates': duplicates,
        'has_duplicates': len(duplicates) > 0
    }


@mcp.tool()
def normalize_whitespace(text: str) -> str:
    """
    Normalize all whitespace in text to single spaces.
    
    Use this to clean data from various sources with inconsistent spacing.
    
    Args:
        text: Text with irregular whitespace
    
    Returns:
        Text with normalized spacing
    """
    # Replace all whitespace (spaces, tabs, newlines) with single space
    normalized = re.sub(r'\s+', ' ', text)
    return normalized.strip()


@mcp.tool()
def calculate_statistics(numbers: List[float]) -> Dict:
    """
    Calculate basic statistics for a list of numbers.
    
    Use this for quick data analysis and numerical summaries.
    
    Args:
        numbers: List of numbers to analyze
    
    Returns:
        Dictionary with mean, median, min, max, sum, and count
    """
    if not numbers:
        return {'error': 'Empty list provided'}
    
    sorted_numbers = sorted(numbers)
    n = len(numbers)
    
    result = {
        'count': n,
        'sum': sum(numbers),
        'mean': sum(numbers) / n,
        'min': min(numbers),
        'max': max(numbers),
        'range': max(numbers) - min(numbers)
    }
    
    # Calculate median
    if n % 2 == 0:
        result['median'] = (sorted_numbers[n//2 - 1] + sorted_numbers[n//2]) / 2
    else:
        result['median'] = sorted_numbers[n//2]
    
    return result


if __name__ == "__main__":
    print(f"Starting Data Tools MCP Server on port {port}...")
    print("Available tools: validate_email, validate_url, validate_phone,")
    print("                 csv_to_json, json_to_csv, clean_string, detect_data_type,")
    print("                 find_duplicates, normalize_whitespace, calculate_statistics")
    mcp.run()
