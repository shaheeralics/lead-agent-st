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
import gzip
import urllib.parse

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
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(30)
            
            return True
            
        except Exception as e:
            st.error(f"❌ Chrome driver setup failed: {str(e)}")
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
        """Extract Google Maps URLs with fallback to HTTP method"""
        
        progress_container = st.container()
        status_container = st.container()
        error_container = st.container()
        debug_container = st.container()
        
        try:
            with progress_container:
                progress_bar = st.progress(0)
            with status_container:
                status_text = st.empty()
            
            # Try HTTP method directly (more reliable on cloud platforms)
            progress_bar.progress(10)
            status_text.info("🚀 Using HTTP extraction method...")
            
            return self.extract_urls_with_requests(input_url, progress_bar, status_text, error_container, debug_container)
            
        except Exception as main_error:
            with error_container:
                st.error(f"❌ EXTRACTION FAILED: {str(main_error)}")
                error_details = traceback.format_exc()
                with st.expander("🔧 Technical Error Details", expanded=False):
                    st.code(error_details)
            return []
            
        finally:
            progress_bar.progress(100)
            self.close_driver()
    
    def extract_urls_with_requests(self, input_url, progress_bar, status_text, error_container, debug_container):
        """Extract URLs using HTTP requests with proper content handling"""
        try:
            progress_bar.progress(30)
            status_text.info("🌐 Fetching page content...")
            
            # Better headers to avoid being blocked
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'identity',  # Don't request compressed content
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            # Make request
            try:
                session = requests.Session()
                session.headers.update(headers)
                response = session.get(input_url, timeout=30, allow_redirects=True, stream=True)
                response.raise_for_status()
                
                # Get content as text, handling encoding properly
                response.encoding = response.apparent_encoding or 'utf-8'
                page_source = response.text
                
                session.close()
                
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
            
            page_length = len(page_source)
            progress_bar.progress(50)
            status_text.info(f"✅ Page fetched: {page_length:,} characters")
            
            # Debug info
            if self.debug_mode:
                with debug_container:
                    st.success("🔧 Using HTTP method")
                    st.info(f"📄 Content size: {page_length:,} characters")
                    st.info(f"📊 Status: {response.status_code}")
                    st.info(f"📋 Encoding: {response.encoding}")
                    
                    # Check content quality
                    if page_length > 100:
                        sample = page_source[:500]
                        non_ascii = sum(1 for c in sample if ord(c) > 127)
                        quality = (500 - non_ascii) / 500
                        st.info(f"📊 Content quality: {quality:.1%} readable")
                        
                        if quality < 0.7:
                            st.warning("⚠️ Content may be corrupted")
            
            # Extract URLs from content
            return self.extract_urls_from_content(page_source, progress_bar, status_text, error_container, debug_container)
            
        except Exception as e:
            with error_container:
                st.error(f"❌ HTTP extraction failed: {str(e)}")
            return []
    
    def extract_urls_from_content(self, page_source, progress_bar, status_text, error_container, debug_container):
        """Extract Google Maps URLs from page content"""
        try:
            progress_bar.progress(80)
            status_text.info("🔍 Searching for Google Maps URLs...")
            
            found_urls = set()
            
            # Comprehensive URL patterns to find Google Maps URLs
            patterns = [
                # Standard Google Maps URLs
                r'https://www\.google\.com/maps/place/[^\s"\'<>\)]+',
                r'https://www\.google\.com/maps/[^\s"\'<>\)]*@[\d\.,\-]+[^\s"\'<>\)]*',
                r'https://maps\.google\.com/[^\s"\'<>\)]+',
                r'https://goo\.gl/maps/[^\s"\'<>\)]+',
                
                # Additional formats
                r'https://www\.google\.com/maps/search/[^\s"\'<>\)]+',
                r'https://www\.google\.com/maps/dir/[^\s"\'<>\)]+',
                r'https://maps\.app\.goo\.gl/[^\s"\'<>\)]+',
                
                # Encoded versions (common in HTML)
                r'https%3A//www\.google\.com/maps[^\s"\'<>\)]+',
                r'https%3A//maps\.google\.com[^\s"\'<>\)]+',
                
                # Alternative patterns with different delimiters
                r'https://[^/]*google[^/]*/maps/[^\s"\'<>\)]+',
                r'https://[^/]*maps\.google[^/]*/[^\s"\'<>\)]+',
            ]
            
            pattern_results = {}
            total_found = 0
            
            for i, pattern in enumerate(patterns):
                matches = re.findall(pattern, page_source, re.IGNORECASE)
                found_urls.update(matches)
                pattern_count = len(matches)
                total_found += pattern_count
                pattern_results[f"Pattern {i+1}"] = pattern_count
            
            # Also search for URLs in href attributes specifically
            href_pattern = r'href=["\']([^"\']*(?:google\.com/maps|maps\.google\.com|goo\.gl/maps)[^"\']*)["\']'
            href_matches = re.findall(href_pattern, page_source, re.IGNORECASE)
            found_urls.update(href_matches)
            href_count = len(href_matches)
            total_found += href_count
            
            if self.debug_mode:
                with debug_container:
                    st.info(f"🎯 Total raw URLs found: {total_found}")
                    st.info(f"   • From href attributes: {href_count}")
                    for pattern_name, count in pattern_results.items():
                        if count > 0:
                            st.info(f"   • {pattern_name}: {count} URLs")
            
            # Clean and validate URLs
            progress_bar.progress(90)
            status_text.info("🧹 Cleaning and validating URLs...")
            
            clean_urls = []
            invalid_urls = []
            
            for url in found_urls:
                # Decode URL if encoded
                clean_url = self.clean_and_decode_url(url)
                if clean_url and self.is_maps_url(clean_url):
                    clean_urls.append(clean_url)
                elif clean_url:
                    invalid_urls.append(clean_url[:100])  # Keep for debugging
            
            # Remove duplicates while preserving order
            clean_urls = list(dict.fromkeys(clean_urls))
            
            # Results
            progress_bar.progress(100)
            
            if clean_urls:
                status_text.success(f"✅ Found {len(clean_urls)} Google Maps URLs!")
                if self.debug_mode:
                    with debug_container:
                        st.success(f"Sample URL: {clean_urls[0][:80]}...")
            else:
                status_text.error("❌ No Google Maps URLs found on this page")
                
                # Show comprehensive debug info
                with debug_container:
                    st.error("🔍 **Detailed Analysis:**")
                    
                    # Content analysis
                    google_count = page_source.lower().count('google')
                    maps_count = page_source.lower().count('maps')
                    http_count = page_source.lower().count('http')
                    href_count_total = page_source.lower().count('href=')
                    
                    st.write(f"• Page size: {len(page_source):,} characters")
                    st.write(f"• Keywords found: google({google_count}) maps({maps_count}) http({http_count})")
                    st.write(f"• Links in page: {href_count_total} href attributes")
                    st.write(f"• Raw URLs found: {len(found_urls)}")
                    st.write(f"• Invalid URLs rejected: {len(invalid_urls)}")
                    
                    # Show rejected URLs for debugging
                    if invalid_urls:
                        with st.expander(f"🔍 Rejected URLs ({len(invalid_urls)})", expanded=False):
                            for i, url in enumerate(invalid_urls[:5]):
                                st.code(f"{i+1}. {url}")
                            if len(invalid_urls) > 5:
                                st.write(f"... and {len(invalid_urls)-5} more")
                    
                    # Show sample content with better formatting
                    if page_source:
                        sample = page_source[:2000]
                        readable_chars = sum(1 for c in sample if c.isprintable() and ord(c) < 127)
                        readability = readable_chars / len(sample) if sample else 0
                        
                        st.write(f"• Content readability: {readability:.1%}")
                        
                        if readability > 0.6:
                            # Look for business-related content
                            business_terms = ['restaurant', 'business', 'address', 'phone', 'location', 'directory']
                            business_found = [term for term in business_terms if term in sample.lower()]
                            
                            if business_found:
                                st.info(f"✅ Found business terms: {', '.join(business_found)}")
                            else:
                                st.warning("⚠️ No business-related terms found")
                            
                            with st.expander("📄 Page content sample", expanded=False):
                                st.code(sample)
                        else:
                            st.warning("⚠️ Content appears corrupted, compressed, or non-HTML")
                    
                    # Show ALL URLs found in page
                    all_urls = re.findall(r'https?://[^\s"\'<>\)]+', page_source[:5000])
                    if all_urls:
                        google_urls = [url for url in all_urls if 'google' in url.lower()]
                        maps_urls = [url for url in all_urls if 'maps' in url.lower()]
                        
                        st.write(f"• All URLs in page: {len(all_urls)}")
                        st.write(f"• URLs containing 'google': {len(google_urls)}")
                        st.write(f"• URLs containing 'maps': {len(maps_urls)}")
                        
                        with st.expander(f"🔗 All URLs found ({len(all_urls[:10])} shown)", expanded=False):
                            for i, url in enumerate(all_urls[:10]):
                                st.code(f"{i+1}. {url}")
                            if len(all_urls) > 10:
                                st.write(f"... and {len(all_urls)-10} more URLs")
                                
                        if google_urls:
                            with st.expander(f"🎯 Google URLs ({len(google_urls)})", expanded=True):
                                for i, url in enumerate(google_urls):
                                    st.code(f"{i+1}. {url}")
                    
                    else:
                        st.error("❌ No URLs found at all in the page")
                        st.info("**Suggestions:**")
                        st.info("• Try a different business directory website")
                        st.info("• Check if the URL is accessible in a browser")
                        st.info("• Some sites may block automated requests")
            
            return clean_urls
            
        except Exception as e:
            with error_container:
                st.error(f"❌ URL extraction failed: {str(e)}")
            return []
    
    def clean_and_decode_url(self, url):
        """Clean and decode URL properly"""
        if not url:
            return None
        
        # Decode URL if encoded
        try:
            if '%3a' in url.lower() or '%2f' in url.lower():
                url = urllib.parse.unquote(url)
        except:
            pass
        
        # Remove unwanted characters
        for char in ['"', "'", '<', '>', '}', ')', ']', ';', ',', '\\']:
            url = url.split(char)[0]
        
        url = url.strip()
        
        # Must start with http/https
        if not url.startswith(('http://', 'https://')):
            return None
        
        return url
    
    def is_maps_url(self, url):
        """Check if URL is a Google Maps URL"""
        if not url or len(url) < 20:
            return False
            
        url_lower = url.lower()
        
        # Decode if needed
        try:
            if '%3a' in url_lower or '%2f' in url_lower:
                url_lower = urllib.parse.unquote(url_lower)
        except:
            pass
        
        # Maps indicators
        maps_indicators = [
            'google.com/maps',
            'maps.google.com',
            'goo.gl/maps',
            'maps.app.goo.gl',
        ]
        
        has_indicator = any(indicator in url_lower for indicator in maps_indicators)
        has_location = any(pattern in url_lower for pattern in ['@', 'place/', 'search/', 'dir/', '/maps/'])
        
        return has_indicator and (has_location or len(url) > 50)

# Main Streamlit App
def main():
    st.markdown("""
    <div class="main-header">
        <h1>🎯 Lead Generation Agent</h1>
        <p>Extract Google Maps business URLs from any webpage</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 Enter Website URL")
        
        url_input = st.text_input(
            "Website URL to scrape:",
            placeholder="https://example.com/business-directory",
            help="Enter any URL containing business listings or maps"
        )
        
        debug_mode = st.checkbox("🔧 Debug Mode", value=True)
        
        # Test with known working URL
        if st.button("🧪 Test with Sample URL"):
            st.info("Testing with a known business directory page...")
            
            # Use a real webpage that should contain Google Maps URLs
            test_url = "https://www.yellowpages.com/search?search_terms=restaurants&geo_location_terms=New%20York%2C%20NY"
            
            extractor = URLExtractor()
            extractor.debug_mode = debug_mode
            
            st.markdown("---")
            st.subheader("🧪 Test Results")
            
            urls = extractor.extract_google_maps_urls(test_url)
            
            if urls:
                st.success(f"✅ Test passed! Found {len(urls)} URLs from real webpage")
                df = pd.DataFrame({'Google Maps URL': urls})
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("⚠️ Test didn't find URLs - this is normal for some websites")
                st.info("Try entering your own URL in the input field above")
        
        # Extract button
        if st.button("🚀 Extract URLs", disabled=not url_input):
            if not url_input.startswith(('http://', 'https://')):
                st.error("❌ URL must start with http:// or https://")
            else:
                extractor = URLExtractor()
                extractor.debug_mode = debug_mode
                
                st.markdown("---")
                st.subheader("🔄 Extraction Progress")
                
                urls = extractor.extract_google_maps_urls(url_input.strip())
                
                if urls:
                    st.markdown("---")
                    st.subheader("✅ Results")
                    st.success(f"Found {len(urls)} Google Maps URLs")
                    
                    df = pd.DataFrame({'Google Maps URL': urls})
                    st.dataframe(df, use_container_width=True)
                    
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "📥 Download CSV",
                        csv,
                        "google_maps_urls.csv",
                        "text/csv"
                    )
                else:
                    st.warning("No URLs found. Try a different website with business listings.")
    
    with col2:
        st.subheader("ℹ️ How it Works")
        st.info("""
        1. 🌐 Fetches webpage content
        2. 🔍 Searches for Google Maps URLs
        3. 🧹 Cleans and validates results
        4. 📥 Downloads as CSV
        
        **Works best with:**
        • Business directories
        • Restaurant listings
        • Service provider pages
        """)
        
        st.subheader("🎯 Tips")
        st.success("""
        **Try these sites:**
        • Business directories
        • Local chamber sites
        • Yelp-style listings
        • Restaurant guides
        
        **Enable debug mode** to see:
        • Content analysis
        • URL extraction details
        """)

if __name__ == "__main__":
    main()