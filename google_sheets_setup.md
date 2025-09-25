# Google Sheets Integration Setup

This file contains instructions and code for setting up Google Sheets integration.

## Setup Instructions

### 1. Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google Sheets API

### 2. Create Service Account
1. Go to "Credentials" in the Google Cloud Console
2. Click "Create Credentials" -> "Service Account"
3. Fill in the service account details
4. Click "Create and Continue"

### 3. Generate Key
1. Click on your created service account
2. Go to "Keys" tab
3. Click "Add Key" -> "Create New Key"
4. Choose JSON format
5. Download the JSON file and rename it to `credentials.json`
6. Place it in your project root directory

### 4. Share Google Sheet
1. Create a new Google Sheet or use existing one
2. Share the sheet with your service account email (found in credentials.json)
3. Give "Editor" permission

### 5. Update Configuration
Add your Google Sheet ID and worksheet name to the configuration below:

```python
# Configuration
GOOGLE_SHEET_ID = "your_google_sheet_id_here"  # From the sheet URL
WORKSHEET_NAME = "Lead Generation"  # Name of the worksheet tab
```

## Example Implementation

```python
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

def setup_google_sheets():
    """Setup Google Sheets connection"""
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'credentials.json', scope
    )
    
    client = gspread.authorize(credentials)
    return client

def save_leads_to_sheets(leads_df, sheet_id, worksheet_name="Leads"):
    """Save leads DataFrame to Google Sheets"""
    try:
        client = setup_google_sheets()
        sheet = client.open_by_key(sheet_id)
        
        # Try to get existing worksheet or create new one
        try:
            worksheet = sheet.worksheet(worksheet_name)
            worksheet.clear()  # Clear existing data
        except gspread.WorksheetNotFound:
            worksheet = sheet.add_worksheet(
                title=worksheet_name, 
                rows=len(leads_df) + 1, 
                cols=len(leads_df.columns)
            )
        
        # Convert DataFrame to list of lists
        data = [leads_df.columns.tolist()] + leads_df.values.tolist()
        
        # Update worksheet with data
        worksheet.update('A1', data)
        
        return True
    except Exception as e:
        print(f"Error saving to Google Sheets: {e}")
        return False
```

## Troubleshooting

### Common Issues:

1. **Permission Denied**: Make sure you've shared the sheet with the service account email
2. **API Not Enabled**: Enable Google Sheets API in Google Cloud Console
3. **Invalid Credentials**: Check that credentials.json is valid and in the correct location
4. **Quota Exceeded**: Google Sheets API has usage limits

### Testing Connection:

```python
def test_google_sheets_connection():
    """Test Google Sheets connection"""
    try:
        client = setup_google_sheets()
        sheets = client.openall()
        print(f"Successfully connected! Found {len(sheets)} accessible sheets.")
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False
```

## Security Notes

- Never commit `credentials.json` to version control
- Add `credentials.json` to your `.gitignore` file
- Use environment variables for sensitive data in production
- Regularly rotate service account keys

## Alternative: Environment Variables

For production deployment, use environment variables:

```python
import os
import json
from google.oauth2.service_account import Credentials

def get_credentials_from_env():
    """Get credentials from environment variable"""
    creds_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
    if creds_json:
        creds_dict = json.loads(creds_json)
        return Credentials.from_service_account_info(creds_dict)
    return None
```