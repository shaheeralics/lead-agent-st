# Lead Generation Agent - Usage Guide

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the App**
   ```bash
   streamlit run app.py
   ```
   Or double-click `run.bat` on Windows

3. **Open in Browser**
   The app will automatically open in your browser at `http://localhost:8501`

## 📋 Step-by-Step Usage

### Step 1: Get Google Search URL
1. Go to [Google.com](https://google.com)
2. Search for local businesses, e.g., "restaurants in New York"
3. Click on "Maps" or add `&tbm=lcl` to the URL
4. Copy the URL from your address bar

**Example URLs:**
```
https://www.google.com/search?tbm=lcl&q=restaurants+in+melbourne
https://www.google.com/search?tbm=lcl&q=dentists+in+sydney
https://www.google.com/search?tbm=lcl&q=plumbers+in+toronto
```

### Step 2: Configure Settings
- **Max Results**: Set how many businesses to scrape (10-500)
- The app will automatically handle pagination and scrolling

### Step 3: Start Scraping
1. Paste your Google Search URL
2. Click "🚀 Start Lead Capture"
3. Wait for the scraping to complete (progress bar shows status)

### Step 4: Review Results
- View leads in the interactive table
- Use filters to find specific businesses
- Sort by any column

### Step 5: Export Data
- **Excel Download**: Click "📥 Download as Excel"
- **Google Sheets**: Click "📊 Save to Google Sheets" (requires setup)

## 🎯 What Gets Extracted

For each business, the app attempts to extract:

| Field | Description | Source |
|-------|-------------|---------|
| **Name** | Business name | Google listing |
| **Address** | Full address | Google listing |
| **Phone** | Phone number | Google listing |
| **Website** | Business website URL | Google listing |
| **Email** | Email address | Scraped from business website |
| **Business URL** | Original Google listing URL | Google search results |
| **Source URL** | Search results page URL | Input URL |
| **Timestamp** | When data was collected | System generated |

## 🔧 Advanced Features

### Filtering Results
- **Name Filter**: Search for specific business names
- **Phone Only**: Show only businesses with phone numbers
- **Email Only**: Show only businesses with email addresses

### Data Quality
- **Deduplication**: Automatically removes duplicate entries
- **Data Cleaning**: Cleans phone numbers, addresses, and URLs
- **Email Validation**: Filters out invalid/generic email addresses

### Error Handling
- **Retry Logic**: Automatically retries failed requests
- **Rate Limiting**: Adds delays to avoid being blocked
- **Progress Tracking**: Shows real-time progress updates

## 🛠️ Troubleshooting

### Common Issues

**1. "No business URLs found"**
- Check if your URL contains `tbm=lcl`
- Try a different search term or location
- Verify the search results page loads in a regular browser

**2. "ChromeDriver issues"**
- Make sure Chrome browser is installed
- The app automatically downloads ChromeDriver
- Try restarting the app if driver fails

**3. "Slow scraping"**
- Reduce max results setting
- Some websites are naturally slow to load
- Network speed affects performance

**4. "No email addresses found"**
- Not all businesses have public email addresses
- Some websites block automated email detection
- Business websites may not contain contact emails

### Testing Your Setup

Run the test script to verify everything is working:
```bash
python test_setup.py
```

This will check:
- ✅ Required packages are installed
- ✅ Chrome WebDriver works
- ✅ URL validation functions

## ⚙️ Configuration

### Environment Variables
Set these in your system environment or `.env` file:

```bash
DEBUG=False
PRODUCTION=False
GOOGLE_SHEET_ID=your_sheet_id_here
```

### Rate Limiting
Modify delays in `config.py`:
```python
MIN_DELAY = 1.0  # Minimum delay (seconds)
MAX_DELAY = 3.0  # Maximum delay (seconds)
```

## 📊 Google Sheets Integration

### Setup Required
1. Create Google Cloud Project
2. Enable Google Sheets API
3. Create service account credentials
4. Download `credentials.json`
5. Share your sheet with service account email

See `google_sheets_setup.md` for detailed instructions.

### Usage
Once configured:
1. Create a Google Sheet
2. Share it with your service account
3. Click "📊 Save to Google Sheets" in the app

## 🎨 UI Customization

### Changing Colors
Edit `config.py`:
```python
UI_CONFIG = {
    'primary_color': '#667eea',    # Main button color
    'secondary_color': '#764ba2',  # Accent color
    'success_color': '#00b894',    # Success messages
    'warning_color': '#fdcb6e',    # Warning messages
}
```

### Custom CSS
Modify the CSS in `app.py` to change:
- Background patterns
- Button styles
- Card layouts
- Typography

## 📈 Performance Tips

### Optimize Scraping Speed
1. **Reduce Max Results**: Start with 50-100 businesses
2. **Filter Search**: Use specific search terms
3. **Good Network**: Ensure stable internet connection

### Improve Success Rate
1. **Use Specific Locations**: "restaurants in downtown chicago"
2. **Popular Business Types**: restaurants, dentists, plumbers work well
3. **Avoid Competitive Terms**: Very broad searches may have less data

### Handle Large Datasets
1. **Batch Processing**: Scrape in smaller batches
2. **Regular Exports**: Download results periodically
3. **Clear Results**: Use "Clear Results" between sessions

## ⚖️ Legal and Ethical Usage

### Terms of Service
- This tool is for educational/research purposes
- Respect Google's Terms of Service
- Follow robots.txt guidelines
- Add appropriate delays between requests

### Data Privacy
- Only collect publicly available information
- Comply with GDPR, CCPA, and local privacy laws
- Don't store sensitive personal information
- Respect business privacy preferences

### Best Practices
- Use reasonable request delays
- Don't overload servers
- Respect website rate limits
- Be transparent about data collection
- Only collect data you actually need

## 🔄 Updates and Maintenance

### Keeping Updated
- Web scraping selectors may change
- Update Chrome and ChromeDriver regularly
- Check for Streamlit updates
- Monitor Google's structure changes

### Backup and Recovery
- Regular backups of collected data
- Export important datasets
- Keep credentials secure
- Test functionality periodically

## 💡 Tips for Success

### Good Search Queries
```
✅ "restaurants in downtown seattle"
✅ "dentists in brooklyn new york"  
✅ "auto repair shops in phoenix"
❌ "restaurants" (too broad)
❌ "businesses" (too generic)
```

### Maximizing Email Collection
- Businesses with websites are more likely to have emails
- Professional services (lawyers, doctors) often list emails
- Local businesses may have contact forms instead

### Quality Over Quantity
- Better to get complete data for 50 businesses
- Than incomplete data for 500 businesses
- Use filters to focus on your target criteria

## 🆘 Support

### Getting Help
1. Check this usage guide first
2. Run `python test_setup.py` to diagnose issues
3. Check the console output for error messages
4. Verify your Google Search URL format

### Common Solutions
- Restart the Streamlit app
- Clear browser cache
- Update Chrome browser
- Reinstall requirements
- Check network connectivity

---

**Happy Lead Generation! 🎯**