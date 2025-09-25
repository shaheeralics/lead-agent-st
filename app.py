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
            time.sleep(3)
            page_title = self.driver.title
            if not page_title or "error" in page_title.lower():
                status_placeholder.warning("⚠️ Page may not have loaded correctly, but continuing...")
            else:
                status_placeholder.success(f"✅ Page loaded successfully: {page_title[:50]}...")
            
            # Step 3: Scroll to load dynamic content
            with progress_placeholder.container():
                progress_bar.progress(40)
                status_placeholder.info("📜 Scrolling to load all content...")
            
            # Scroll multiple times to load dynamic content
            scroll_attempts = 5
            for i in range(scroll_attempts):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1.5)
                
                # Update progress for scrolling
                scroll_progress = 40 + (i + 1) * 10
                with progress_placeholder.container():
                    progress_bar.progress(min(scroll_progress, 60))
                    status_placeholder.info(f"📜 Scrolling... ({i + 1}/{scroll_attempts})")
            
            # Step 4: Extract page content
            with progress_placeholder.container():
                progress_bar.progress(70)
                status_placeholder.info("🔍 Extracting page content...")
                
            page_source = self.driver.page_source
            page_length = len(page_source)
            
            if page_length < 1000:
                status_placeholder.warning(f"⚠️ Page content seems small ({page_length} chars). May be incomplete.")
            else:
                status_placeholder.info(f"📄 Page content extracted ({page_length:,} characters)")
            
            # Step 5: Find Google Maps URLs using multiple patterns
            with progress_placeholder.container():
                progress_bar.progress(80)
                status_placeholder.info("🗺️ Searching for Google Maps URLs...")
            
            google_maps_urls = set()
            
            # More comprehensive patterns
            patterns = [
                # Standard Google Maps URLs
                r'https://www\.google\.com/maps/place/[^"\s<>\]]+',
                r'https://maps\.google\.com/[^"\s<>\]]*place[^"\s<>\]]*',
                r'https://goo\.gl/maps/[^"\s<>\]]+',
                
                # URLs with data parameters (like your example)
                r'https://www\.google\.com/maps/[^"\s<>\]]*data=[^"\s<>\]]+',
                
                # URLs with coordinates
                r'https://www\.google\.com/maps/[^"\s<>\]]*@\d+\.\d+[^"\s<>\]]*',
                
                # More flexible patterns
                r'https://[^"\s<>\]]*google[^"\s<>\]*/maps[^"\s<>\]]+',
                r'https://[^"\s<>\]]*maps\.google[^"\s<>\]]+',
            ]
            
            all_found_urls = []
            
            for i, pattern in enumerate(patterns):
                found = re.findall(pattern, page_source)
                all_found_urls.extend(found)
                status_placeholder.info(f"🔍 Pattern {i+1}/7: Found {len(found)} URLs")
            
            status_placeholder.info(f"🔍 Total URLs found from patterns: {len(all_found_urls)}")
            
            # Debug: Show some sample URLs found
            if all_found_urls:
                status_placeholder.info(f"📝 Sample URLs found: {all_found_urls[0][:100]}...")
            
            # Clean and validate URLs
            valid_count = 0
            for url in all_found_urls:
                # More aggressive cleaning
                clean_url = url
                
                # Remove common ending characters
                for char in ['"', "'", '<', '>', ']', ')', '}']:
                    if char in clean_url:
                        clean_url = clean_url.split(char)[0]
                
                # Remove URL parameters that might break the link (but keep data parameter)
                if '&' in clean_url and 'data=' in clean_url:
                    # Keep everything up to but not including parameters after data
                    parts = clean_url.split('&')
                    cleaned_parts = [parts[0]]  # Keep base URL
                    for part in parts[1:]:
                        if part.startswith(('data=', 'tbm=', 'q=')):
                            cleaned_parts.append(part)
                    clean_url = '&'.join(cleaned_parts)
                
                if self.is_valid_maps_url_flexible(clean_url):
                    google_maps_urls.add(clean_url)
                    valid_count += 1
            
            status_placeholder.info(f"✅ Valid Google Maps URLs after cleaning: {valid_count}")
            
            # If still no results, try a more aggressive search
            if not google_maps_urls:
                status_placeholder.info("🔍 No results yet, trying more aggressive search...")
                
                # Search for any URL containing 'maps' and 'google'
                aggressive_pattern = r'https://[^"\s<>\]]*(?:google[^"\s<>\]]*maps|maps[^"\s<>\]]*google)[^"\s<>\]]*'
                aggressive_urls = re.findall(aggressive_pattern, page_source)
                
                status_placeholder.info(f"🔍 Aggressive search found: {len(aggressive_urls)} URLs")
                
                for url in aggressive_urls:
                    clean_url = url.split('"')[0].split("'")[0].split('<')[0]
                    if 'google' in clean_url and 'maps' in clean_url:
                        google_maps_urls.add(clean_url)
                
                # Also try searching in the raw HTML for common patterns
                if not google_maps_urls:
                    # Look for URLs in href attributes specifically
                    href_pattern = r'href=["\']([^"\']*(?:google[^"\']*maps|maps[^"\']*google)[^"\']*)["\']'
                    href_urls = re.findall(href_pattern, page_source)
                    
                    status_placeholder.info(f"🔍 Found {len(href_urls)} URLs in href attributes")
                    
                    for url in href_urls:
                        if 'google' in url and 'maps' in url:
                            google_maps_urls.add(url)
            
            # Debug information
            if google_maps_urls:
                status_placeholder.info(f"🎯 Final results: {len(google_maps_urls)} unique URLs")
            else:
                status_placeholder.warning("⚠️ No Google Maps URLs found. Checking page content...")
                
                # Debug: Check if the page has any maps-related content
                maps_keywords = ['maps.google', 'google.com/maps', 'goo.gl/maps', '@', 'place/', 'data=']
                found_keywords = [kw for kw in maps_keywords if kw in page_source.lower()]
                
                if found_keywords:
                    status_placeholder.warning(f"🔍 Found maps-related content: {found_keywords}")
                    status_placeholder.info("📝 The page contains maps content but URLs may be encoded or dynamically loaded")
                else:
                    status_placeholder.error("❌ No maps-related content found in the page source")
            
            # Step 6: Check href attributes of all links
            with progress_placeholder.container():
                progress_bar.progress(90)
                status_placeholder.info("🔗 Checking all clickable links on the page...")
            
            try:
                links = self.driver.find_elements(By.TAG_NAME, "a")
                status_placeholder.info(f"🔗 Found {len(links)} clickable links on the page...")
                
                link_urls_found = 0
                for i, link in enumerate(links):
                    if i % 50 == 0:  # Update every 50 links
                        status_placeholder.info(f"🔗 Checked {i}/{len(links)} links... ({link_urls_found} maps URLs found)")
                        
                    try:
                        href = link.get_attribute("href")
                        if href:
                            # Try both validation methods
                            if self.is_valid_maps_url(href) or self.is_valid_maps_url_flexible(href):
                                google_maps_urls.add(href)
                                link_urls_found += 1
                                
                            # Also check onclick and other attributes that might contain URLs
                            onclick = link.get_attribute("onclick")
                            if onclick and 'google' in onclick and 'maps' in onclick:
                                # Extract URL from onclick
                                url_match = re.search(r'https://[^\'"\s]+', onclick)
                                if url_match:
                                    onclick_url = url_match.group()
                                    if self.is_valid_maps_url_flexible(onclick_url):
                                        google_maps_urls.add(onclick_url)
                                        link_urls_found += 1
                    except:
                        continue  # Skip broken links
                
                status_placeholder.info(f"🔗 Link checking complete: {link_urls_found} maps URLs found from links")
                        
            except Exception as e:
                status_placeholder.warning(f"⚠️ Error checking links: {e}")
            
            # Step 7: Final attempt - check for encoded URLs and JavaScript
            if not google_maps_urls:
                with progress_placeholder.container():
                    progress_bar.progress(95)
                    status_placeholder.info("🕵️ Final attempt - checking for encoded URLs and JavaScript...")
                
                # Look for URL-encoded URLs
                import urllib.parse
                encoded_pattern = r'https%3A//[^"\'&\s]*google[^"\'&\s]*maps[^"\'&\s]*'
                encoded_urls = re.findall(encoded_pattern, page_source)
                
                for encoded_url in encoded_urls:
                    try:
                        decoded_url = urllib.parse.unquote(encoded_url)
                        if self.is_valid_maps_url_flexible(decoded_url):
                            google_maps_urls.add(decoded_url)
                    except:
                        continue
                
                status_placeholder.info(f"🕵️ Found {len(encoded_urls)} encoded URLs")
                
                # Look for URLs in JavaScript variables or data attributes
                js_patterns = [
                    r'"(https://[^"]*google[^"]*maps[^"]*)"',
                    r"'(https://[^']*google[^']*maps[^']*)'",
                    r'data-[^=]*="([^"]*google[^"]*maps[^"]*)"',
                    r"data-[^=]*='([^']*google[^']*maps[^']*)'"
                ]
                
                for pattern in js_patterns:
                    js_urls = re.findall(pattern, page_source)
                    for js_url in js_urls:
                        if self.is_valid_maps_url_flexible(js_url):
                            google_maps_urls.add(js_url)
                
                status_placeholder.info(f"🕵️ JavaScript/data attribute search complete")
                
            # Final debug info
            if not google_maps_urls:
                with progress_placeholder.container():
                    status_placeholder.error("🚫 Still no URLs found. Providing debug information...")
                    
                    # Show a sample of the page content for debugging
                    sample_content = page_source[:2000]  # First 2000 characters
                    if 'google' in sample_content.lower() or 'maps' in sample_content.lower():
                        st.expander("🔍 Debug: Page content sample", expanded=False).code(sample_content)
                        status_placeholder.info("📝 The page contains 'google' or 'maps' text. URLs might be dynamically loaded or in a different format.")
                    else:
                        status_placeholder.info("📝 The page doesn't seem to contain Google Maps content in the HTML source.")
            
            # Step 7: Complete
            with progress_placeholder.container():
                progress_bar.progress(100)
                if google_maps_urls:
                    status_placeholder.success(f"✅ Extraction complete! Found {len(google_maps_urls)} Google Maps URLs")
                else:
                    status_placeholder.error("❌ No Google Maps URLs found on this page")
            
            return list(google_maps_urls)
            
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