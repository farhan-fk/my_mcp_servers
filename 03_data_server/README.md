# 📊 Data Tools MCP Server

Data validation, cleaning, transformation, and analysis tools.

## 🛠️ Available Tools

### `validate_email(email)`
Validate email address format.

### `validate_url(url)`
Validate URL format and extract components.

### `validate_phone(phone, country_code="US")`
Validate phone number format.

### `csv_to_json(csv_data, has_header=True)`
Convert CSV data to JSON format.

### `json_to_csv(json_data)`
Convert JSON array to CSV format.

### `clean_string(text, lowercase, remove_punctuation, remove_numbers, trim)`
Clean and normalize string data.

### `detect_data_type(value)`
Automatically detect data type (number, email, url, date, etc.).

### `find_duplicates(items)`
Find duplicate values in a list.

### `normalize_whitespace(text)`
Normalize all whitespace to single spaces.

### `calculate_statistics(numbers)`
Calculate mean, median, min, max, and other statistics.

## 🚀 Deploy to Railway

1. Push this folder to GitHub
2. Connect to Railway
3. Deploy
4. Share URL with team

## 📡 Server URL
`https://your-data-server.up.railway.app`

Port: 8003 (local) / Dynamic (Railway)
