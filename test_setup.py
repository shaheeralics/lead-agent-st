"""
Test script for Lead Generation Agent
Run this to test basic functionality before using the main app
"""

import sys
import importlib
import subprocess

def test_imports():
    """Test if all required packages are available"""
    required_packages = [
        'streamlit', 'requests', 'bs4', 'selenium', 
        'pandas', 'openpyxl', 'fake_useragent'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'bs4':
                importlib.import_module('bs4')
            else:
                importlib.import_module(package)
            print(f"✅ {package} - OK")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All packages are available!")
        return True

def test_chrome_driver():
    """Test if Chrome and ChromeDriver are available"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        
        print("🔍 Testing Chrome WebDriver...")
        driver = webdriver.Chrome(
            service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        # Test basic functionality
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        
        print(f"✅ Chrome WebDriver - OK (Loaded: {title})")
        return True
        
    except Exception as e:
        print(f"❌ Chrome WebDriver - ERROR: {str(e)}")
        print("Make sure Chrome browser is installed")
        return False

def test_url_validation():
    """Test URL validation functionality"""
    try:
        # Import our utility functions
        sys.path.append('.')
        from utils import URLValidator
        
        test_urls = [
            ("https://www.google.com/search?tbm=lcl&q=restaurants", True),
            ("https://www.google.com/search?q=restaurants", False),
            ("invalid-url", False),
        ]
        
        validator = URLValidator()
        
        print("🔗 Testing URL validation...")
        for url, expected in test_urls:
            result = validator.is_valid_google_search_url(url)
            status = "✅" if result == expected else "❌"
            print(f"{status} URL validation test: {url[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ URL validation test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Lead Generation Agent Setup")
    print("=" * 50)
    
    tests = [
        ("Package Imports", test_imports),
        ("Chrome WebDriver", test_chrome_driver),
        ("URL Validation", test_url_validation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! You can run the main app.")
        print("Run: streamlit run app.py")
    else:
        print("\n⚠️ Some tests failed. Please fix the issues before running the app.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)