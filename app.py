import streamlit as st
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import re
import hashlib
import random
import json
from datetime import datetime
from fake_useragent import UserAgent
from io import BytesIO
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Page configuration
st.set_page_config(
    page_title="Lead Generation Agent",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    .main {
        background: linear-gradient(0deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.95) 100%), 
                    radial-gradient(circle at 25px 25px, lightgray 2%, transparent 0%);
        background-size: 50px 50px;
        min-height: 100vh;
    }
    
    .stApp > div:first-child {
        background: linear-gradient(0deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.95) 100%), 
                    radial-gradient(circle at 25px 25px, lightgray 2%, transparent 0%);
        background-size: 50px 50px;
    }
    
    .main-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
        margin: 2rem auto;
        max-width: 800px;
    }
    
    .title {
        text-align: center;
        font-size: 3rem;
        font-weight: 600;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    .secondary-btn {
        background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%) !important;
    }
    
    .dataframe-container {
        background: white;
        border-radius: 15px;
        padding: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-top: 2rem;
    }
    
    .success-box {
        background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fdcb6e 0%, #e17055 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .info-box {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

class LeadScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.driver = None
        self.leads = []
        self.processed_urls = set()
        
    def setup_driver(self):
        """Setup Chrome WebDriver with options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"--user-agent={self.ua.random}")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            
    def random_delay(self, min_seconds=1, max_seconds=3):
        """Add random delay to avoid being detected"""
        time.sleep(random.uniform(min_seconds, max_seconds))
        
    def extract_business_urls(self, search_url, max_results=100):
        """Extract business URLs from Google local search results"""
        if not self.driver:
            self.setup_driver()
            
        business_urls = set()
        page_count = 0
        max_pages = 10  # Limit pagination
        
        try:
            st.info("🔍 Loading Google search results...")
            self.driver.get(search_url)
            self.random_delay(2, 4)
            
            while len(business_urls) < max_results and page_count < max_pages:
                # Scroll to load more results
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                self.random_delay(1, 2)
                
                # Find business links
                business_elements = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="rlfi=hd:;si:"]')
                
                current_count = len(business_urls)
                for element in business_elements:
                    href = element.get_attribute('href')
                    if href and 'rlfi=hd:;si:' in href:
                        business_urls.add(href)
                        
                # Check if we found new URLs
                if len(business_urls) == current_count:
                    # Try to find and click "Next" or "More" button
                    try:
                        next_button = self.driver.find_element(By.CSS_SELECTOR, 'a[aria-label="Next page"]')
                        if next_button and next_button.is_enabled():
                            next_button.click()
                            self.random_delay(2, 4)
                            page_count += 1
                        else:
                            break
                    except:
                        break
                else:
                    page_count += 1
                    
                st.info(f"📍 Found {len(business_urls)} business URLs (Page {page_count})")
                
        except Exception as e:
            st.error(f"Error extracting business URLs: {str(e)}")
            
        return list(business_urls)
    
    def extract_business_details(self, business_url):
        """Extract business details from individual business page"""
        try:
            self.driver.get(business_url)
            self.random_delay(2, 4)
            
            # Extract business information
            business_data = {
                'name': '',
                'address': '',
                'phone': '',
                'website': '',
                'email': '',
                'business_url': business_url,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Business name
            try:
                name_element = self.driver.find_element(By.CSS_SELECTOR, 'h1, .x3AX1-LfntMc-header-title, [data-attrid="title"]')
                business_data['name'] = name_element.text.strip()
            except:
                pass
                
            # Address
            try:
                address_element = self.driver.find_element(By.CSS_SELECTOR, '[data-attrid="kc:/location/location:address"], .LrzXr')
                business_data['address'] = address_element.text.strip()
            except:
                pass
                
            # Phone number
            try:
                phone_element = self.driver.find_element(By.CSS_SELECTOR, '[data-attrid="kc:/collection/knowledge_panels/has_phone:phone"], .z5jxId')
                business_data['phone'] = phone_element.text.strip()
            except:
                pass
                
            # Website
            try:
                website_element = self.driver.find_element(By.CSS_SELECTOR, '[data-attrid="kc:/collection/knowledge_panels/has_url:website"], .CL9Uqc a')
                business_data['website'] = website_element.get_attribute('href')
            except:
                pass
                
            # Extract email from website if available
            if business_data['website']:
                business_data['email'] = self.extract_email_from_website(business_data['website'])
                
            return business_data
            
        except Exception as e:
            st.warning(f"Error extracting details from {business_url}: {str(e)}")
            return None
            
    def extract_email_from_website(self, website_url):
        """Extract email from business website"""
        try:
            headers = {'User-Agent': self.ua.random}
            response = requests.get(website_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Email regex pattern
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                emails = re.findall(email_pattern, response.text)
                
                if emails:
                    # Filter out common non-business emails
                    filtered_emails = [email for email in emails if not any(
                        exclude in email.lower() for exclude in 
                        ['example.com', 'test.com', 'gmail.com', 'yahoo.com', 'hotmail.com', 'noreply', 'no-reply']
                    )]
                    
                    if filtered_emails:
                        return filtered_emails[0]  # Return first valid email
                    elif emails:
                        return emails[0]  # Return first email if no filtered ones
                        
        except Exception as e:
            pass
            
        return ''
        
    def generate_lead_hash(self, name, address):
        """Generate hash for deduplication"""
        return hashlib.md5(f"{name.lower()}{address.lower()}".encode()).hexdigest()
        
    def scrape_leads(self, search_url, max_results=100):
        """Main function to scrape leads"""
        try:
            # Extract business URLs
            business_urls = self.extract_business_urls(search_url, max_results)
            
            if not business_urls:
                st.warning("No business URLs found in the search results.")
                return []
                
            st.success(f"✅ Found {len(business_urls)} business URLs to process")
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            leads = []
            processed_hashes = set()
            
            for i, business_url in enumerate(business_urls):
                status_text.text(f"Processing business {i+1}/{len(business_urls)}...")
                progress_bar.progress((i+1)/len(business_urls))
                
                # Extract business details
                business_data = self.extract_business_details(business_url)
                
                if business_data and business_data['name']:
                    # Check for duplicates
                    lead_hash = self.generate_lead_hash(business_data['name'], business_data['address'])
                    
                    if lead_hash not in processed_hashes:
                        business_data['source_url'] = search_url
                        leads.append(business_data)
                        processed_hashes.add(lead_hash)
                        
                self.random_delay(1, 3)
                
            status_text.text("✅ Scraping completed!")
            return leads
            
        except Exception as e:
            st.error(f"Error during scraping: {str(e)}")
            return []
        finally:
            self.close_driver()

def create_excel_download(leads_df):
    """Create Excel file for download"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        leads_df.to_excel(writer, sheet_name='Leads', index=False)
    
    return output.getvalue()

def save_to_google_sheets(leads_df, sheet_name="Lead Generation"):
    """Save leads to Google Sheets (requires credentials)"""
    try:
        # This would require Google Sheets API credentials
        # For demo purposes, showing the structure
        st.info("📊 Google Sheets integration requires API credentials setup")
        st.code("""
        # To set up Google Sheets integration:
        # 1. Create a Google Cloud Project
        # 2. Enable Google Sheets API
        # 3. Create service account credentials
        # 4. Share your Google Sheet with the service account email
        # 5. Add credentials.json file to your project
        """)
        return True
    except Exception as e:
        st.error(f"Error saving to Google Sheets: {str(e)}")
        return False

def main():
    # Header
    st.markdown('<h1 class="title">🎯 Lead Generation Agent</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Extract business leads from Google Search local results</p>', unsafe_allow_html=True)
    
    # Disclaimer
    st.markdown("""
    <div class="info-box">
        <strong>⚠️ Important Notice:</strong> This tool is for educational and research purposes. 
        Please respect Google's Terms of Service, robots.txt files, and applicable privacy laws. 
        Add appropriate delays and use responsibly.
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'leads' not in st.session_state:
        st.session_state.leads = []
    if 'scraper' not in st.session_state:
        st.session_state.scraper = LeadScraper()
    
    # Main input card
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        
        # URL input
        search_url = st.text_input(
            "📍 Paste Google Search Results URL",
            placeholder="https://www.google.com/search?tbm=lcl&q=restaurants+in+australia...",
            help="Paste a Google Search URL with local results (must include tbm=lcl parameter)"
        )
        
        # Settings
        col1, col2 = st.columns(2)
        with col1:
            max_results = st.number_input("Max Results", min_value=10, max_value=500, value=50)
        with col2:
            st.write("")  # Spacing
        
        # Buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Start Lead Capture", use_container_width=True):
                if search_url and 'tbm=lcl' in search_url:
                    with st.spinner("Scraping leads... This may take a few minutes."):
                        leads = st.session_state.scraper.scrape_leads(search_url, max_results)
                        st.session_state.leads = leads
                        st.rerun()
                else:
                    st.error("Please enter a valid Google Search URL with local results (must include tbm=lcl)")
        
        with col2:
            if st.button("🗑️ Clear Results", use_container_width=True):
                st.session_state.leads = []
                st.success("Results cleared!")
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display results
    if st.session_state.leads:
        st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
        
        # Convert to DataFrame
        leads_df = pd.DataFrame(st.session_state.leads)
        
        # Display summary
        st.markdown(f"""
        <div class="success-box">
            <h3>📊 Scraping Results</h3>
            <p><strong>Total Leads Found:</strong> {len(leads_df)}</p>
            <p><strong>With Phone Numbers:</strong> {len(leads_df[leads_df['phone'] != ''])}</p>
            <p><strong>With Websites:</strong> {len(leads_df[leads_df['website'] != ''])}</p>
            <p><strong>With Email Addresses:</strong> {len(leads_df[leads_df['email'] != ''])}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display data
        st.subheader("📋 Lead Details")
        
        # Add filters
        col1, col2, col3 = st.columns(3)
        with col1:
            name_filter = st.text_input("Filter by Name", "")
        with col2:
            phone_only = st.checkbox("Only with Phone Numbers")
        with col3:
            email_only = st.checkbox("Only with Email Addresses")
        
        # Apply filters
        filtered_df = leads_df.copy()
        if name_filter:
            filtered_df = filtered_df[filtered_df['name'].str.contains(name_filter, case=False, na=False)]
        if phone_only:
            filtered_df = filtered_df[filtered_df['phone'] != '']
        if email_only:
            filtered_df = filtered_df[filtered_df['email'] != '']
        
        # Display filtered data
        st.dataframe(
            filtered_df[['name', 'address', 'phone', 'website', 'email']],
            use_container_width=True,
            hide_index=True
        )
        
        # Download buttons
        col1, col2 = st.columns(2)
        
        with col1:
            # Excel download
            excel_data = create_excel_download(filtered_df)
            st.download_button(
                label="📥 Download as Excel",
                data=excel_data,
                file_name=f"leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col2:
            # Google Sheets integration
            if st.button("📊 Save to Google Sheets", use_container_width=True):
                save_to_google_sheets(filtered_df)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #666;'>Made with ❤️ using Streamlit | "
        "Please use responsibly and respect website terms of service</p>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()