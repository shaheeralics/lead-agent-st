import streamlit as st
import re
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import traceback

# Set page config
st.set_page_config(
    page_title="Lead Generation Agent", 
    page_icon="🎯", 
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .success-box {
        background: #d4edda;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .error-box {
        background: #f8d7da;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class URLExtractor:
    def __init__(self):
        self.driver = None
        self.debug_mode = False
        
    def setup_driver(self):
        """Setup Chrome WebDriver with optimized options"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(30)
            
            return True
            
        except Exception as e:
            st.error(f"❌ Failed to setup Chrome driver: {str(e)}")
            return False
    
    def close_driver(self):
        """Safely close WebDriver"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
        except:
            pass
            
    def extract_google_maps_urls(self, input_url):
        """Extract Google Maps URLs with comprehensive error handling"""
        
        # Create UI elements with unique keys
        progress_container = st.container()
        status_container = st.container()
        error_container = st.container()
        debug_container = st.container()
        
        try:
            with progress_container:
                progress_bar = st.progress(0)
            with status_container:
                status_text = st.empty()
            
            # Step 1: Setup browser
            progress_bar.progress(10)
            status_text.info("🚀 Setting up browser...")
            
            if not self.setup_driver():
                with error_container:
                    st.error("❌ Failed to setup browser")
                return []
            
            # Step 2: Load page
            progress_bar.progress(20)
            status_text.info(f"🌐 Loading page: {input_url}")
            
            try:
                self.driver.get(input_url)
                time.sleep(3)
                status_text.info("✅ Page loaded successfully")
            except Exception as e:
                with error_container:
                    st.error(f"❌ Failed to load page: {str(e)}")
                return []
            
            # Step 3: Get page info
            progress_bar.progress(40)
            status_text.info("📄 Analyzing page content...")
            
            try:
                page_title = self.driver.title or "No title"
                page_source = self.driver.page_source
                page_length = len(page_source)
                
                status_text.info(f"✅ Page analyzed: {page_length:,} characters")
                
                if self.debug_mode:
                    with debug_container:
                        st.info(f"📊 Page: {page_title[:50]} ({page_length:,} chars)")
                        google_count = page_source.lower().count('google')
                        maps_count = page_source.lower().count('maps')
                        st.info(f"🔍 Keywords: 'google'({google_count}) 'maps'({maps_count})")
                
            except Exception as e:
                with error_container:
                    st.error(f"❌ Failed to get page content: {str(e)}")
                return []
            
            # Step 4: Simple scroll to load content
            progress_bar.progress(60)
            status_text.info("📜 Loading dynamic content...")
            
            try:
                for i in range(3):
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1)
                status_text.info("✅ Content loading complete")
            except Exception as e:
                if self.debug_mode:
                    with debug_container:
                        st.warning(f"⚠️ Scroll issue: {str(e)}")
            
            # Step 5: Extract URLs using multiple methods
            progress_bar.progress(80)
            status_text.info("🔍 Extracting Google Maps URLs...")
            
            found_urls = set()
            
            # Method 1: Regex patterns on page source
            try:
                patterns = [
                    r'https://www\.google\.com/maps/place/[^\s"\'<>]+',
                    r'https://www\.google\.com/maps/[^\s"\'<>]*@[\d\.,\-]+[^\s"\'<>]*',
                    r'https://maps\.google\.com/[^\s"\'<>]+',
                    r'https://goo\.gl/maps/[^\s"\'<>]+',
                ]
                
                total_found = 0
                for pattern in patterns:
                    matches = re.findall(pattern, page_source, re.IGNORECASE)
                    found_urls.update(matches)
                    total_found += len(matches)
                
                if self.debug_mode:
                    with debug_container:
                        st.info(f"🎯 Regex patterns found: {total_found} URLs")
                        
            except Exception as e:
                with error_container:
                    st.error(f"❌ Regex search failed: {str(e)}")
            
            # Method 2: Check all links on page
            try:
                links = self.driver.find_elements(By.TAG_NAME, "a")
                link_found = 0
                
                for link in links[:50]:  # Check first 50 links only to avoid timeout
                    try:
                        href = link.get_attribute("href")
                        if href and self.is_maps_url(href):
                            found_urls.add(href)
                            link_found += 1
                    except:
                        continue
                
                if self.debug_mode:
                    with debug_container:
                        st.info(f"🔗 Link analysis: {link_found} URLs from {len(links)} links")
                        
            except Exception as e:
                if self.debug_mode:
                    with debug_container:
                        st.warning(f"⚠️ Link check failed: {str(e)}")
            
            # Step 6: Clean and validate URLs
            progress_bar.progress(90)
            status_text.info("🧹 Cleaning and validating URLs...")
            
            clean_urls = []
            
            try:
                for url in found_urls:
                    clean_url = self.clean_url(url)
                    if clean_url and self.is_maps_url(clean_url):
                        clean_urls.append(clean_url)
                
                # Remove duplicates while preserving order
                clean_urls = list(dict.fromkeys(clean_urls))
                
            except Exception as e:
                with error_container:
                    st.error(f"❌ URL cleaning failed: {str(e)}")
                clean_urls = list(found_urls)  # Use raw URLs as fallback
            
            # Step 7: Show results
            progress_bar.progress(100)
            
            if clean_urls:
                status_text.success(f"✅ Successfully found {len(clean_urls)} Google Maps URLs!")
                if self.debug_mode and clean_urls:
                    with debug_container:
                        st.success(f"Sample URL: {clean_urls[0][:80]}...")
            else:
                status_text.error("❌ No Google Maps URLs found on this page")
                
                # Show debug information
                with error_container:
                    st.warning("**Possible reasons:**")
                    st.info("• The page might not contain Google Maps business URLs")
                    st.info("• URLs might be loaded dynamically with JavaScript")
                    st.info("• Try a different page with business listings")
                
                if self.debug_mode:
                    with debug_container:
                        st.error("🔍 Debug Information:")
                        st.write(f"• Page title: {page_title}")
                        st.write(f"• Content size: {page_length:,} characters") 
                        st.write(f"• Contains 'google': {'google' in page_source.lower()}")
                        st.write(f"• Contains 'maps': {'maps' in page_source.lower()}")
                        st.write(f"• Raw URLs found: {len(found_urls)}")
                        
                        if page_source and len(page_source) > 100:
                            with st.expander("📄 Sample page content (first 1000 chars)"):
                                st.code(page_source[:1000])
            
            return clean_urls
            
        except Exception as main_error:
            # Handle any unexpected errors
            with error_container:
                st.error(f"❌ EXTRACTION FAILED: {str(main_error)}")
                
                # Show detailed error information
                error_details = traceback.format_exc()
                with st.expander("🔧 Technical Error Details", expanded=False):
                    st.code(error_details)
            
            return []
            
        finally:
            # Always cleanup browser
            progress_bar.progress(100)
            self.close_driver()
    
    def is_maps_url(self, url):
        """Check if URL is a Google Maps URL"""
        if not url or len(url) < 20:
            return False
            
        url_lower = url.lower()
        maps_indicators = [
            'google.com/maps',
            'maps.google.com', 
            'goo.gl/maps'
        ]
        
        return any(indicator in url_lower for indicator in maps_indicators)
    
    def clean_url(self, url):
        """Clean URL by removing unwanted trailing characters"""
        if not url:
            return None
            
        # Remove common trailing characters that break URLs
        ending_chars = ['"', "'", '<', '>', '}', ')', ']', ';', ',', '\\']
        for char in ending_chars:
            url = url.split(char)[0]
        
        # Must be a valid URL
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            return None
            
        return url

# Main Streamlit Application
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎯 Lead Generation Agent</h1>
        <p>Extract Google Maps business URLs from any webpage</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create layout columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 Enter Website URL")
        
        # URL input
        url_input = st.text_input(
            "Website URL to scrape:",
            placeholder="https://example.com/business-directory",
            help="Enter any URL that contains Google Maps business listings or embedded maps"
        )
        
        # Debug mode toggle
        debug_mode = st.checkbox("🔧 Debug Mode (show detailed extraction info)", value=False)
        
        # Extract button
        extract_clicked = st.button("🚀 Extract URLs", disabled=not url_input)
        
        if extract_clicked:
            if not url_input.strip():
                st.error("❌ Please enter a valid URL")
            elif not url_input.startswith(('http://', 'https://')):
                st.error("❌ URL must start with http:// or https://")
            else:
                # Create extractor instance
                extractor = URLExtractor()
                extractor.debug_mode = debug_mode
                
                # Show extraction progress
                st.markdown("---")
                st.subheader("🔄 Extraction Progress")
                
                # Extract URLs
                urls = extractor.extract_google_maps_urls(url_input.strip())
                
                if urls:
                    # Show successful results
                    st.markdown("---")
                    st.subheader("✅ Extraction Results")
                    
                    st.success(f"Found {len(urls)} Google Maps URLs")
                    
                    # Create results DataFrame
                    df = pd.DataFrame({
                        'Google Maps URL': urls,
                        'Status': ['Valid'] * len(urls)
                    })
                    
                    # Display results table
                    st.dataframe(df, use_container_width=True)
                    
                    # Download CSV button
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download URLs as CSV",
                        data=csv,
                        file_name="google_maps_urls.csv",
                        mime="text/csv",
                        key='download-csv'
                    )
                else:
                    st.markdown("---")
                    st.subheader("❌ No Results Found")
                    
                    st.warning("**No Google Maps URLs were found on this page.**")
                    
                    st.info("""
                    **Try these suggestions:**
                    • Check if the URL contains business listings or maps
                    • Enable debug mode to see detailed extraction info  
                    • Try a different webpage with business directories
                    • Use pages like Yelp, Google My Business, or local business directories
                    """)
    
    with col2:
        st.subheader("ℹ️ How it Works")
        st.info("""
        **This tool extracts Google Maps business URLs:**
        
        1. 🌐 **Loads webpage** using Chrome browser
        2. 📜 **Scrolls page** to load dynamic content  
        3. 🔍 **Searches content** using multiple methods
        4. 🧹 **Cleans & validates** found URLs
        5. 📥 **Downloads results** as CSV file
        
        **Works best with:**
        • Business directory websites
        • Local listing pages
        • Review sites with embedded maps
        """)
        
        st.subheader("🎯 Tips for Success")
        st.success("""
        **✅ Best URL types:**
        • Business directories
        • Local service listings
        • Restaurant/hotel review pages
        • Chamber of commerce sites
        
        **🔧 Debug mode shows:**
        • Page loading details
        • Content analysis stats
        • URL extraction progress
        """)
        
        st.subheader("🔍 Supported URL Formats")
        st.code("""
        ✅ google.com/maps/place/...
        ✅ maps.google.com/...
        ✅ goo.gl/maps/...
        """)

if __name__ == "__main__":
    main()