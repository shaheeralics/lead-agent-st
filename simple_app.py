import streamlit as st
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import re
import time
import random
from urllib.parse import urljoin, urlparse

# Page configuration
st.set_page_config(
    page_title="URL Extractor",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background: linear-gradient(0deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.95) 100%), 
                    radial-gradient(circle at 25px 25px, lightgray 2%, transparent 0%);
        background-size: 50px 50px;
        min-height: 100vh;
    }
    
    .main-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 2rem auto;
        max-width: 900px;
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
    
    .url-box {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 8px 12px;
        font-family: monospace;
        font-size: 0.9rem;
        word-break: break-all;
        margin: 5px 0;
    }
    
    .url-box:hover {
        background: #e9ecef;
        cursor: pointer;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

class URLExtractor:
    def __init__(self):
        self.driver = None
        
    def setup_driver(self):
        """Setup Chrome WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
    def close_driver(self):
        """Close WebDriver"""
        if self.driver:
            self.driver.quit()
            
    def extract_google_maps_urls(self, input_url):
        """Extract Google Maps place URLs from any webpage"""
        try:
            if not self.driver:
                self.setup_driver()
                
            st.info("🔍 Loading webpage...")
            self.driver.get(input_url)
            time.sleep(3)  # Wait for page to load
            
            # Scroll to load more content
            st.info("📜 Scrolling to load more content...")
            for i in range(3):  # Scroll 3 times
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
            # Get page source
            page_source = self.driver.page_source
            
            # Find all Google Maps place URLs
            google_maps_urls = set()
            
            # Pattern 1: Direct Google Maps place URLs
            pattern1 = r'https://www\.google\.com/maps/place/[^"\s<>]+'
            urls1 = re.findall(pattern1, page_source)
            
            # Pattern 2: Google Maps URLs with various formats
            pattern2 = r'https://maps\.google\.com/[^"\s<>]*place[^"\s<>]*'
            urls2 = re.findall(pattern2, page_source)
            
            # Pattern 3: Short Google Maps URLs
            pattern3 = r'https://goo\.gl/maps/[^"\s<>]+'
            urls3 = re.findall(pattern3, page_source)
            
            # Combine all URLs
            all_urls = urls1 + urls2 + urls3
            
            # Clean and deduplicate URLs
            for url in all_urls:
                # Remove any trailing characters that might be HTML artifacts
                url = re.sub(r'[&"\'<>].*$', '', url)
                if self.is_valid_maps_url(url):
                    google_maps_urls.add(url)
            
            # Also check href attributes of all links
            st.info("🔗 Checking all links on the page...")
            try:
                links = self.driver.find_elements(By.TAG_NAME, "a")
                for link in links:
                    href = link.get_attribute("href")
                    if href and self.is_valid_maps_url(href):
                        google_maps_urls.add(href)
            except Exception as e:
                st.warning(f"Error checking links: {e}")
                
            return list(google_maps_urls)
            
        except Exception as e:
            st.error(f"Error extracting URLs: {str(e)}")
            return []
        finally:
            self.close_driver()
    
    def is_valid_maps_url(self, url):
        """Check if URL is a valid Google Maps place URL"""
        if not url:
            return False
            
        # Check for Google Maps patterns
        maps_patterns = [
            r'google\.com/maps/place/',
            r'maps\.google\.com.*place',
            r'goo\.gl/maps/',
        ]
        
        for pattern in maps_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
                
        return False

def main():
    st.markdown('<h1 class="title">🔍 Google Maps URL Extractor</h1>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'extractor' not in st.session_state:
        st.session_state.extractor = URLExtractor()
    if 'extracted_urls' not in st.session_state:
        st.session_state.extracted_urls = []
    
    # Main input card
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        
        st.markdown("### 📝 Instructions")
        st.markdown("""
        1. Paste **any webpage URL** below
        2. Click **Extract URLs** 
        3. The app will find all Google Maps place URLs from that page
        4. URLs will be listed below for you to review
        """)
        
        st.markdown("---")
        
        # URL input
        input_url = st.text_input(
            "🌐 Enter any webpage URL:",
            placeholder="https://example.com/page-with-business-listings",
            help="Paste any URL - could be Google search results, business directories, or any page with Google Maps links"
        )
        
        # Buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔍 Extract URLs", use_container_width=True):
                if input_url:
                    with st.spinner("Extracting Google Maps URLs... This may take a minute."):
                        urls = st.session_state.extractor.extract_google_maps_urls(input_url)
                        st.session_state.extracted_urls = urls
                        st.rerun()
                else:
                    st.error("Please enter a URL first!")
        
        with col2:
            if st.button("🗑️ Clear Results", use_container_width=True):
                st.session_state.extracted_urls = []
                st.success("Results cleared!")
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display results
    if st.session_state.extracted_urls:
        st.markdown("---")
        st.markdown("## 📍 Found Google Maps URLs")
        
        # Summary
        st.success(f"✅ Found **{len(st.session_state.extracted_urls)}** Google Maps place URLs")
        
        # Display URLs
        st.markdown("### 🔗 URL List")
        
        for i, url in enumerate(st.session_state.extracted_urls, 1):
            with st.expander(f"URL #{i}", expanded=False):
                st.markdown(f'<div class="url-box">{url}</div>', unsafe_allow_html=True)
                
                # Extract business name from URL if possible
                try:
                    import urllib.parse
                    parsed = urllib.parse.urlparse(url)
                    if '/place/' in url:
                        place_part = url.split('/place/')[1].split('/')[0]
                        business_name = urllib.parse.unquote(place_part).replace('+', ' ')
                        st.write(f"**Likely Business:** {business_name}")
                except:
                    pass
                
                # Copy button
                st.code(url, language=None)
        
        # Download as text file
        st.markdown("### 💾 Export URLs")
        
        # Create downloadable text file
        urls_text = "\n".join(st.session_state.extracted_urls)
        
        st.download_button(
            label="📥 Download URLs as Text File",
            data=urls_text,
            file_name=f"google_maps_urls_{len(st.session_state.extracted_urls)}_urls.txt",
            mime="text/plain",
            use_container_width=True
        )
        
    elif st.session_state.get('extraction_attempted'):
        st.warning("No Google Maps URLs found on this page. Try a different URL with business listings.")
    
    # Footer
    st.markdown("---")
    st.markdown("**💡 Tip:** This works best with pages that contain business listings, search results, or directories with Google Maps links.")

if __name__ == "__main__":
    main()