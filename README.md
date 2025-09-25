# Lead Generation Agent

A Streamlit web application that scrapes business leads from Google Search local results.

## Features

🎯 **Lead Extraction**: Automatically extracts business information from Google local search results
📊 **Data Collection**: Captures business name, address, phone, website, and email
📥 **Export Options**: Download results as Excel files
🔄 **Deduplication**: Prevents duplicate entries
⚡ **Modern UI**: Beautiful, responsive interface with grid background
📈 **Progress Tracking**: Real-time progress updates during scraping
🛡️ **Error Handling**: Robust error handling with retry logic

## Installation

1. Clone or download this repository
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

3. Run the Streamlit app:

```bash
streamlit run app.py
```

## Usage

1. **Get Google Search URL**: 
   - Go to Google and search for businesses (e.g., "restaurants in New York")
   - Click on "Maps" or add `&tbm=lcl` to the URL for local results
   - Copy the URL from your browser

2. **Paste URL in App**:
   - Paste the Google Search URL in the input field
   - Set your desired maximum results (10-500)
   - Click "Start Lead Capture"

3. **Review Results**:
   - View scraped leads in the interactive table
   - Use filters to find specific businesses
   - Download results as Excel file
   - Optionally save to Google Sheets (requires setup)

## Example Search URLs

```
https://www.google.com/search?tbm=lcl&q=restaurants+in+melbourne
https://www.google.com/search?tbm=lcl&q=dentists+in+sydney
https://www.google.com/search?tbm=lcl&q=plumbers+in+brisbane
```

## Data Schema

The app collects the following information for each business:

- **Name**: Business name
- **Address**: Full business address
- **Phone**: Contact phone number
- **Website**: Business website URL
- **Email**: Email address (extracted from website if available)
- **Business URL**: Original Google search result URL
- **Source URL**: The search results page URL
- **Timestamp**: When the data was scraped

## Google Sheets Integration (Optional)

To enable Google Sheets integration:

1. Create a Google Cloud Project
2. Enable Google Sheets API
3. Create service account credentials
4. Download credentials as `credentials.json`
5. Place `credentials.json` in the project directory
6. Share your target Google Sheet with the service account email

## Important Notes

⚠️ **Terms of Service**: This tool is for educational and research purposes. Please:
- Respect Google's Terms of Service
- Add appropriate delays between requests
- Use responsibly and ethically
- Comply with applicable privacy laws
- Respect website robots.txt files

⚠️ **Rate Limiting**: The app includes random delays and user-agent rotation to avoid being blocked.

## Technical Details

- **Framework**: Streamlit
- **Web Scraping**: Selenium WebDriver + BeautifulSoup
- **Data Processing**: Pandas
- **File Export**: OpenPyXL for Excel files
- **Styling**: Custom CSS for modern UI

## Requirements

- Python 3.7+
- Chrome browser (for Selenium WebDriver)
- Internet connection
- All packages listed in requirements.txt

## Troubleshooting

**Chrome Driver Issues**:
- The app automatically downloads ChromeDriver using webdriver-manager
- Make sure Chrome browser is installed

**No Results Found**:
- Verify the Google Search URL contains `tbm=lcl`
- Try different search terms or locations
- Check if the search results page loaded correctly

**Slow Performance**:
- Reduce the max results limit
- Some websites may be slow to respond
- Network speed affects scraping time

## License

This project is for educational purposes only. Use responsibly and in accordance with applicable laws and terms of service.