import streamlit as st
import re
import time
import requests
from bs4 import BeautifulSoup
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
        """Setup Chrome WebDriver with cloud-compatible options"""
        try:
            chrome_options = Options()
            
            # Essential options for cloud environments
            chrome_options.add_argument("--headless=new")  # New headless mode
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")
            chrome_options.add_argument("--disable-javascript")  # We don't need JS for basic scraping
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--single-process")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            
            # User agent
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
            
            # Try to install and setup ChromeDriver
            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as service_error:
                st.warning(f"ChromeDriverManager failed: {service_error}")
                
                # Fallback: try without explicit service
                st.info("Trying fallback Chrome setup...")
                self.driver = webdriver.Chrome(options=chrome_options)
            
            # Set timeouts
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            # Test the driver with a simple page
            st.info("Testing browser setup...")
            self.driver.get("https://httpbin.org/status/200")
            
            return True
            
        except Exception as e:
            error_msg = str(e)
            st.error(f"❌ Chrome driver setup failed: {error_msg}")
            
            # Show more helpful error information
            if "Status code was: 127" in error_msg:
                st.error("🔧 **Chrome binary not found!**")
                st.info("""
                **This error usually means:**
                • Chrome browser is not installed
                • Running in a restricted environment
                
                **Possible solutions:**
                • Try using a different deployment platform
                • Use a platform that supports Chrome (like Heroku, Railway, or local deployment)
                """)
            
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
            
            # Step 1: Try Selenium first, then fallback to requests
            progress_bar.progress(10)
            status_text.info("🚀 Attempting to setup browser...")
            
            selenium_failed = False
            if not self.setup_driver():
                selenium_failed = True
                with status_container:
                    st.warning("⚠️ Browser setup failed. Using HTTP method instead...")
                    st.info("💡 This is normal on cloud platforms - continuing with alternative method...")
                
                # Fallback to requests + BeautifulSoup (more reliable on cloud)
                return self.extract_urls_with_requests(input_url, progress_bar, status_text, error_container, debug_container)
            
            # Step 2: Load page with Selenium
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
            
            # Continue with URL extraction...
            return self.extract_urls_from_content(page_source, progress_bar, status_text, error_container, debug_container)
            
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
    
    def extract_urls_with_requests(self, input_url, progress_bar, status_text, error_container, debug_container):
        """Fallback method using requests instead of Selenium - works better on cloud platforms"""
        try:
            progress_bar.progress(30)
            status_text.info("🌐 Fetching page content via HTTP...")
            
            # Use requests to get page content with proper headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
            }
            
            # Make request with proper error handling
            try:
                response = requests.get(input_url, headers=headers, timeout=30)
                response.raise_for_status()
            except requests.exceptions.Timeout:
                with error_container:
                    st.error("❌ Request timeout - website took too long to respond")
                return []
            except requests.exceptions.ConnectionError:
                with error_container:
                    st.error("❌ Connection failed - check if the URL is accessible")
                return []
            except requests.exceptions.HTTPError as e:
                with error_container:
                    st.error(f"❌ HTTP Error {response.status_code}: {str(e)}")
                return []
            
            page_source = response.text
            page_length = len(page_source)
            
            progress_bar.progress(50)
            status_text.info(f"✅ Page fetched successfully: {page_length:,} characters")
            
            if self.debug_mode:
                with debug_container:
                    st.success("� Using HTTP method (browser-free)")
                    st.info(f"📄 Response size: {page_length:,} characters")
                    st.info(f"📊 Status code: {response.status_code}")
                    google_count = page_source.lower().count('google')
                    maps_count = page_source.lower().count('maps')
                    st.info(f"🔍 Keywords found: 'google'({google_count}) 'maps'({maps_count})")
            
            # Extract URLs from content using the same method
            return self.extract_urls_from_content(page_source, progress_bar, status_text, error_container, debug_container)
            
        except Exception as e:
            with error_container:
                st.error(f"❌ HTTP extraction failed: {str(e)}")
                st.info("💡 **Suggestions:**")
                st.info("• The website might be blocking automated requests")
                st.info("• Try a different URL with public business listings")
                st.info("• Some websites require JavaScript (try a simpler directory site)")
            return []
    
    def extract_urls_from_content(self, page_source, progress_bar, status_text, error_container, debug_container):
        """Extract URLs from page content"""
        try:
            # Step 5: Extract URLs using multiple methods
            progress_bar.progress(80)
            status_text.info("🔍 Extracting Google Maps URLs...")
            
            found_urls = set()
            
            # Method 1: Comprehensive regex patterns on page source
            try:
                patterns = [
                    # Standard Google Maps URLs
                    r'https://www\.google\.com/maps/place/[^\s"\'<>]+',
                    r'https://www\.google\.com/maps/[^\s"\'<>]*@[\d\.,\-]+[^\s"\'<>]*',
                    r'https://maps\.google\.com/[^\s"\'<>]+',
                    r'https://goo\.gl/maps/[^\s"\'<>]+',
                    
                    # Additional patterns for various formats
                    r'https://www\.google\.com/maps/search/[^\s"\'<>]+',
                    r'https://www\.google\.com/maps/dir/[^\s"\'<>]+',
                    r'https://www\.google\.com/maps/@[^\s"\'<>]+',
                    r'https://maps\.app\.goo\.gl/[^\s"\'<>]+',
                    
                    # Encoded versions (sometimes found in HTML)
                    r'https%3A//www\.google\.com/maps[^\s"\'<>]+',
                    r'https%3A//maps\.google\.com[^\s"\'<>]+',
                ]
                
                total_found = 0
                pattern_results = {}
                
                for i, pattern in enumerate(patterns):
                    matches = re.findall(pattern, page_source, re.IGNORECASE)
                    found_urls.update(matches)
                    total_found += len(matches)
                    pattern_results[f"Pattern {i+1}"] = len(matches)
                
                if self.debug_mode:
                    with debug_container:
                        st.info(f"🎯 Total URLs from regex: {total_found}")
                        for pattern_name, count in pattern_results.items():
                            if count > 0:
                                st.info(f"   • {pattern_name}: {count} URLs")
                        
            except Exception as e:
                with error_container:
                    st.error(f"❌ Regex search failed: {str(e)}")
            
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
                
                # Show comprehensive debug information
                with error_container:
                    st.warning("**Possible reasons:**")
                    st.info("• The page might not contain Google Maps business URLs")
                    st.info("• URLs might be loaded dynamically with JavaScript")
                    st.info("• Try a different page with business listings")
                
                # Always show basic debug info when no URLs found
                with debug_container:
                    st.error("🔍 **Debug Information:**")
                    st.write(f"• Content size: {len(page_source):,} characters") 
                    st.write(f"• Contains 'google': {'google' in page_source.lower()}")
                    st.write(f"• Contains 'maps': {'maps' in page_source.lower()}")
                    st.write(f"• Raw URLs found: {len(found_urls)}")
                    
                    # Show some sample URLs if any were found but didn't pass validation
                    if found_urls:
                        st.write("**Raw URLs found (before cleaning):**")
                        sample_raw = list(found_urls)[:3]
                        for i, url in enumerate(sample_raw):
                            st.code(f"{i+1}. {url}")
                    
                    # Always show content sample for debugging
                    st.write("**Sample content analysis:**")
                    
                    # Look for common maps-related terms
                    maps_terms = ['maps', 'google', 'place', 'business', 'location', 'address']
                    term_counts = {term: page_source.lower().count(term) for term in maps_terms}
                    
                    st.write("Terms found:")
                    for term, count in term_counts.items():
                        if count > 0:
                            st.write(f"  • '{term}': {count}")
                    
                    # Show first 1500 characters of content
                    if page_source and len(page_source) > 100:
                        with st.expander("📄 Page content sample (first 1500 chars)", expanded=True):
                            st.code(page_source[:1500])
                            
                        # Also look for any URL patterns in the content
                        with st.expander("🔍 All URLs found in content", expanded=False):
                            all_urls = re.findall(r'https?://[^\s"\'<>]+', page_source[:5000])  # First 5000 chars
                            if all_urls:
                                st.write(f"Found {len(all_urls)} total URLs:")
                                for i, url in enumerate(all_urls[:10]):  # Show first 10
                                    st.code(f"{i+1}. {url}")
                                if len(all_urls) > 10:
                                    st.write(f"... and {len(all_urls) - 10} more URLs")
                            else:
                                st.write("No URLs found in page content")
                    
                    # Suggest better test URLs
                    st.info("**💡 Try testing with these types of URLs:**")
                    st.code("""
Examples of pages that typically work:
• Business directory pages (YellowPages, etc.)
• Local business listing sites
• Pages with embedded Google Maps
• Restaurant/service provider listings
                    """)
            
            return clean_urls
            
        except Exception as e:
            with error_container:
                st.error(f"❌ URL extraction failed: {str(e)}")
            return []
    
    def is_maps_url(self, url):
        """Enhanced check if URL is a Google Maps URL"""
        if not url or len(url) < 20:
            return False
            
        url_lower = url.lower()
        
        # Decode URL if it's encoded
        try:
            import urllib.parse
            if '%3a' in url_lower or '%2f' in url_lower:
                url_lower = urllib.parse.unquote(url_lower)
        except:
            pass
        
        # Check for various Google Maps patterns
        maps_indicators = [
            'google.com/maps',
            'maps.google.com', 
            'goo.gl/maps',
            'maps.app.goo.gl',
        ]
        
        # Must contain at least one maps indicator
        has_maps_indicator = any(indicator in url_lower for indicator in maps_indicators)
        
        # Additional validation: should contain coordinates or place info
        has_location_data = any(pattern in url_lower for pattern in [
            '@',          # Coordinates marker
            'place/',     # Place URL
            'search/',    # Search URL  
            'dir/',       # Directions URL
            '/maps/',     # General maps path
        ])
        
        return has_maps_indicator and (has_location_data or len(url) > 50)
    
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
        debug_mode = st.checkbox("🔧 Debug Mode (show detailed extraction info)", value=True)  # Enable by default for now
        
        # Test with sample data button
        if st.button("🧪 Test with Sample Data"):
            st.info("Testing with mock business directory content...")
            
            # Create a mock extractor for testing
            test_extractor = URLExtractor()
            test_extractor.debug_mode = debug_mode
            
            # Mock HTML content with Google Maps URLs
            test_content = """
            <html>
            <head><title>Local Business Directory</title></head>
            <body>
            <h1>Local Businesses</h1>
            <div class="business">
                <h2>Pizza Palace Downtown</h2>
                <p>Best pizza in the city!</p>
                <a href="https://www.google.com/maps/place/Pizza+Palace/@40.7128,-74.0060,17z/data=!3m1!4b1">View on Maps</a>
            </div>
            <div class="business">
                <h2>Coffee Corner Cafe</h2>
                <p>Great coffee and atmosphere</p>
                <a href="https://maps.google.com/maps?q=coffee+shop&ll=40.7580,-73.9855&z=15">Google Maps</a>
            </div>
            <div class="business">
                <h2>Downtown Auto Repair</h2>
                <p>Reliable car service since 1985</p>
                <a href="https://goo.gl/maps/abc123xyz">Maps Link</a>
            </div>
            </body>
            </html>
            """
            
            st.markdown("---")
            st.subheader("🧪 Test Results")
            
            # Test the extraction
            progress_bar = st.progress(0)
            
            progress_bar.progress(50)
            st.info("📄 Analyzing test content...")
            
            test_urls = test_extractor.extract_urls_from_content(
                test_content, progress_bar, st.empty(), st.container(), st.container()
            )
            
            if test_urls:
                st.success(f"✅ Test successful! Found {len(test_urls)} Google Maps URLs")
                df = pd.DataFrame({
                    'Google Maps URL': test_urls,
                    'Status': ['Valid'] * len(test_urls)
                })
                st.dataframe(df, use_container_width=True)
                
                st.info("🎉 **The extraction logic is working correctly!** Now try with a real URL that contains business listings.")
            else:
                st.error("❌ Test failed - no URLs found in sample content")
        
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