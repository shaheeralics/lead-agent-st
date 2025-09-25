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
        """Extract Google Maps place URLs from any webpage with progress tracking"""
        progress_placeholder = st.empty()
        status_placeholder = st.empty()
        debug_placeholder = st.empty()
        
        try:
            # Step 1: Setup WebDriver
            with progress_placeholder.container():
                progress_bar = st.progress(0)
                status_placeholder.info("🚀 Setting up Chrome browser...")
                
            if not self.driver:
                self.setup_driver()
            
            # Step 2: Load webpage
            with progress_placeholder.container():
                progress_bar.progress(20)
                status_placeholder.info(f"🌐 Loading webpage: {input_url}")
            
            self.driver.get(input_url)
            
            # Wait for initial load and check if page loaded successfully
            time.sleep(5)  # Increased wait time
            page_title = self.driver.title
            current_url = self.driver.current_url
            
            if hasattr(self, 'debug_mode') and self.debug_mode:
                debug_placeholder.info(f"📄 Page Title: {page_title}")
                debug_placeholder.info(f"📍 Current URL: {current_url}")
            
            # Step 3: Aggressive content loading
            with progress_placeholder.container():
                progress_bar.progress(40)
                status_placeholder.info("� Loading all dynamic content...")
            
            # More aggressive scrolling and waiting
            for i in range(10):  # Increased scroll attempts
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                
                # Scroll up a bit
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.7);")
                time.sleep(1)
                
                # Try clicking "Load more" type buttons
                try:
                    load_more_buttons = self.driver.find_elements(By.XPATH, 
                        "//button[contains(text(), 'Load') or contains(text(), 'More') or contains(text(), 'Show')]")
                    for btn in load_more_buttons[:2]:  # Click first 2 buttons found
                        try:
                            btn.click()
                            time.sleep(2)
                        except:
                            pass
                except:
                    pass
                
                if i % 3 == 0:
                    status_placeholder.info(f"� Loading content... ({i+1}/10)")
            
            # Step 4: Extract ALL content
            with progress_placeholder.container():
                progress_bar.progress(60)
                status_placeholder.info("� Extracting all page content...")
                
            page_source = self.driver.page_source
            page_length = len(page_source)
            
            if hasattr(self, 'debug_mode') and self.debug_mode:
                debug_placeholder.info(f"📏 Page source length: {page_length:,} characters")
                
                # Count occurrences of key terms
                google_count = page_source.lower().count('google')
                maps_count = page_source.lower().count('maps')
                place_count = page_source.lower().count('place')
                data_count = page_source.lower().count('data=')
                
                debug_placeholder.info(f"� Content analysis: 'google'({google_count}) 'maps'({maps_count}) 'place'({place_count}) 'data='({data_count})")
            
            # Step 5: SUPER AGGRESSIVE URL EXTRACTION
            with progress_placeholder.container():
                progress_bar.progress(80)
                status_placeholder.info("�️ Super aggressive URL search...")
            
            all_possible_urls = set()
            
            # Method 1: Regex patterns (comprehensive)
            patterns = [
                # Standard patterns
                r'https?://(?:www\.)?google\.com/maps/[^\s"\'<>})\]]+',
                r'https?://maps\.google\.com/[^\s"\'<>})\]]+',
                r'https?://goo\.gl/maps/[^\s"\'<>})\]]+',
                
                # Any URL containing both 'google' and 'maps'
                r'https?://[^\s"\'<>})\]]*google[^\s"\'<>})\]]*maps[^\s"\'<>})\]]+',
                r'https?://[^\s"\'<>})\]]*maps[^\s"\'<>})\]]*google[^\s"\'<>})\]]+',
                
                # Encoded versions
                r'https?%3A//[^\s"\'<>})\]]*google[^\s"\'<>})\]]*maps[^\s"\'<>})\]]+',
                r'https?%3A//[^\s"\'<>})\]]*maps[^\s"\'<>})\]]*google[^\s"\'<>})\]]+',
            ]
            
            for i, pattern in enumerate(patterns):
                found_urls = re.findall(pattern, page_source, re.IGNORECASE)
                all_possible_urls.update(found_urls)
                
                if hasattr(self, 'debug_mode') and self.debug_mode:
                    debug_placeholder.info(f"🎯 Pattern {i+1}: Found {len(found_urls)} URLs")
            
            # Method 2: Search in ALL attributes
            status_placeholder.info("� Searching all HTML attributes...")
            
            # Get all elements and check all their attributes
            try:
                all_elements = self.driver.find_elements(By.XPATH, "//*[@*[contains(., 'google') or contains(., 'maps')]]")
                
                for element in all_elements[:200]:  # Limit to first 200 elements to avoid timeout
                    try:
                        # Get all attributes
                        attrs = self.driver.execute_script("""
                            var items = {};
                            for (index = 0; index < arguments[0].attributes.length; ++index) { 
                                items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value 
                            }; 
                            return items;
                        """, element)
                        
                        for attr_name, attr_value in attrs.items():
                            if attr_value and ('google' in attr_value.lower() and 'maps' in attr_value.lower()):
                                # Try to extract URL from attribute value
                                url_matches = re.findall(r'https?://[^\s"\'<>})\]]+', attr_value)
                                for url in url_matches:
                                    if 'google' in url.lower() and 'maps' in url.lower():
                                        all_possible_urls.add(url)
                    except:
                        continue
                        
            except Exception as e:
                if hasattr(self, 'debug_mode') and self.debug_mode:
                    debug_placeholder.warning(f"Attribute search error: {e}")
            
            # Method 3: Search page text content for any maps-related URLs
            status_placeholder.info("📝 Searching visible text content...")
            
            try:
                page_text = self.driver.find_element(By.TAG_NAME, "body").text
                text_urls = re.findall(r'https?://[^\s]+', page_text)
                
                for url in text_urls:
                    if ('google' in url.lower() and 'maps' in url.lower()) or 'goo.gl/maps' in url.lower():
                        all_possible_urls.add(url)
                        
                if hasattr(self, 'debug_mode') and self.debug_mode:
                    debug_placeholder.info(f"📝 Found {len([u for u in text_urls if 'maps' in u.lower()])} maps URLs in visible text")
                        
            except:
                pass
            
            # Step 6: Clean and validate ALL found URLs
            with progress_placeholder.container():
                progress_bar.progress(90)
                status_placeholder.info(f"🧹 Cleaning and validating {len(all_possible_urls)} potential URLs...")
            
            valid_urls = set()
            
            for url in all_possible_urls:
                # Decode URL if encoded
                try:
                    import urllib.parse
                    if '%3A' in url or '%2F' in url:
                        url = urllib.parse.unquote(url)
                except:
                    pass
                
                # Clean URL
                clean_url = url
                
                # Remove common trailing characters
                for char in ['"', "'", '<', '>', '}', ')', ']', ';', ',']:
                    clean_url = clean_url.split(char)[0]
                
                # Basic validation: must be a proper URL with google/maps
                if (clean_url.startswith(('http://', 'https://')) and 
                    len(clean_url) > 25 and
                    'google' in clean_url.lower() and 
                    ('maps' in clean_url.lower() or 'goo.gl' in clean_url.lower())):
                    
                    valid_urls.add(clean_url)
            
            if hasattr(self, 'debug_mode') and self.debug_mode:
                debug_placeholder.info(f"✅ Valid URLs after cleaning: {len(valid_urls)}")
                
                # Show first few URLs found
                if valid_urls:
                    sample_urls = list(valid_urls)[:3]
                    for i, url in enumerate(sample_urls):
                        debug_placeholder.info(f"🔗 Sample URL {i+1}: {url[:100]}...")
            
            # Step 7: Complete
            with progress_placeholder.container():
                progress_bar.progress(100)
                if valid_urls:
                    status_placeholder.success(f"✅ Extraction complete! Found {len(valid_urls)} Google Maps URLs")
                else:
                    status_placeholder.error("❌ No Google Maps URLs found")
                    
                    # Show detailed debug info if no URLs found
                    if hasattr(self, 'debug_mode') and self.debug_mode:
                        debug_placeholder.error("🔍 DEBUG INFO:")
                        debug_placeholder.info(f"• Page loaded: {page_title[:50] if page_title else 'No title'}")
                        debug_placeholder.info(f"• Content size: {page_length:,} chars")
                        debug_placeholder.info(f"• Contains 'google': {google_count > 0}")
                        debug_placeholder.info(f"• Contains 'maps': {maps_count > 0}")
                        debug_placeholder.info(f"• Raw URLs found: {len(all_possible_urls)}")
                        
                        # Show a sample of the page content
                        if page_length > 100:
                            sample_content = page_source[:1000]
                            with st.expander("📄 Page Content Sample (first 1000 chars)", expanded=False):
                                st.code(sample_content)
            
            return list(valid_urls)
            
        except Exception as e:
            with progress_placeholder.container():
                status_placeholder.error(f"❌ Error during extraction: {str(e)}")
            st.error(f"Full error details: {str(e)}")
            return []
        finally:
            self.close_driver()
    
    def is_valid_maps_url_flexible(self, url):
        """More flexible validation for Google Maps URLs"""
        if not url or len(url) < 15:
            return False
            
        url_lower = url.lower()
        
        # Must contain google and maps
        if not ('google' in url_lower and 'maps' in url_lower):
            return False
            
        # Must be a valid HTTP/HTTPS URL
        if not url.startswith(('http://', 'https://')):
            return False
            
        # Should contain location indicators
        location_indicators = [
            'place/',           # Direct place URLs
            '@',               # Coordinate URLs
            'data=',           # Data parameter URLs
            'search/',         # Search results
            'dir/',            # Directions
        ]
        
        has_location = any(indicator in url_lower for indicator in location_indicators)
        
        # Additional check: if it's a google.com/maps URL, it's likely valid
        if 'google.com/maps' in url_lower and len(url) > 30:
            return True
            
        return has_location

    def is_valid_maps_url(self, url):
        """Check if URL is a valid Google Maps place URL"""
        if not url or len(url) < 10:
            return False
            
        # Check for Google Maps patterns (including the format you showed)
        maps_patterns = [
            r'google\.com/maps/place/',           # Standard place URLs
            r'maps\.google\.com.*place',          # Alternative maps URLs
            r'goo\.gl/maps/',                     # Short URLs
            r'google\.com/maps/.*data=',          # URLs with data parameters (like your example)
            r'google\.com/maps/.*@\d+\.\d+',      # URLs with coordinates
        ]
        
        for pattern in maps_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                # Additional validation: must contain coordinates or place identifier
                if ('/@' in url and re.search(r'@\d+\.\d+', url)) or '/place/' in url or 'data=' in url:
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
        
        # Quick test URLs
        st.markdown("**🧪 Quick Test URLs:**")
        test_urls = [
            "https://www.google.com/search?tbm=lcl&q=restaurants+in+new+york",
            "https://www.google.com/search?tbm=lcl&q=dentists+in+chicago", 
            "https://www.yelp.com/nyc/restaurants"
        ]
        
        cols = st.columns(3)
        for i, test_url in enumerate(test_urls):
            with cols[i]:
                url_name = test_url.split('q=')[1].split('&')[0].replace('+', ' ') if 'q=' in test_url else f"Test {i+1}"
                if st.button(f"🔗 {url_name[:20]}...", key=f"test_{i}", use_container_width=True):
                    st.session_state.test_url = test_url
                    st.rerun()
        
        # Use test URL if selected
        if hasattr(st.session_state, 'test_url'):
            input_url = st.session_state.test_url
            st.info(f"🧪 Using test URL: {input_url}")
            delattr(st.session_state, 'test_url')
        
        # Buttons
        col1, col2, col3 = st.columns(3)
        
        # Debug mode toggle
        debug_mode = st.checkbox("🔧 Debug Mode (show detailed extraction info)", value=False)
        
        with col1:
            if st.button("🔍 Extract URLs", use_container_width=True):
                if input_url:
                    # Validate URL format
                    if not input_url.startswith(('http://', 'https://')):
                        input_url = 'https://' + input_url
                    
                    # Clear previous results
                    st.session_state.extracted_urls = []
                    
                    # Show extraction in progress
                    with st.spinner("🕸️ Starting extraction process..."):
                        try:
                            # Pass debug mode to extractor
                            st.session_state.extractor.debug_mode = debug_mode
                            
                            urls = st.session_state.extractor.extract_google_maps_urls(input_url)
                            st.session_state.extracted_urls = urls
                            st.session_state.extraction_attempted = True
                            
                            # Show final result
                            if urls:
                                st.balloons()
                                st.success(f"🎉 Successfully extracted {len(urls)} Google Maps URLs!")
                            else:
                                st.warning("🔍 No Google Maps URLs found. The page may not contain business listings with Maps links.")
                                if debug_mode:
                                    st.info("💡 Debug mode is ON - check the detailed logs above for more information.")
                                else:
                                    st.info("💡 Try enabling Debug Mode for more detailed information about what was found on the page.")
                                
                        except Exception as e:
                            st.error(f"❌ Extraction failed: {str(e)}")
                            st.info("💡 Try checking if the URL is correct and accessible.")
                            
                    st.rerun()
                else:
                    st.error("Please enter a URL first!")
        
        with col2:
            if st.button("🗑️ Clear Results", use_container_width=True):
                st.session_state.extracted_urls = []
                st.success("Results cleared!")
                st.rerun()
                
        with col3:
            if st.button("📝 Save Page Source", use_container_width=True):
                if input_url:
                    # Quick page source save for debugging
                    try:
                        extractor = URLExtractor()
                        extractor.setup_driver()
                        extractor.driver.get(input_url if input_url.startswith(('http://', 'https://')) else 'https://' + input_url)
                        time.sleep(3)
                        
                        page_source = extractor.driver.page_source
                        extractor.close_driver()
                        
                        st.download_button(
                            label="💾 Download Page Source",
                            data=page_source,
                            file_name=f"page_source_{int(time.time())}.html",
                            mime="text/html"
                        )
                        st.success("✅ Page source ready for download!")
                        
                    except Exception as e:
                        st.error(f"❌ Failed to get page source: {e}")
                else:
                    st.error("Please enter a URL first!")
        
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