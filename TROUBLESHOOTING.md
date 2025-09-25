# Deployment Troubleshooting Guide

## Common Installation Errors and Solutions

### Error: "installer returned a non-zero exit code"

This error typically occurs during cloud deployment (Streamlit Cloud, Heroku, etc.) when there are package conflicts.

#### Solution 1: Use Minimal Requirements
Try using the minimal requirements file first:
```bash
pip install -r requirements-minimal.txt
```

#### Solution 2: Fix Package Conflicts
The error you're seeing suggests conflicts with these packages:
- pygments
- mdurl  
- markdown-it-py
- rich

These are dependencies of Streamlit and other packages. To fix:

1. **Clear pip cache:**
   ```bash
   pip cache purge
   ```

2. **Uninstall conflicting packages:**
   ```bash
   pip uninstall pygments mdurl markdown-it-py rich -y
   ```

3. **Reinstall with no-deps flag:**
   ```bash
   pip install --no-deps streamlit
   pip install requests beautifulsoup4 selenium pandas openpyxl webdriver-manager
   ```

#### Solution 3: Use Compatible Versions
Create a new `requirements-fixed.txt`:
```
streamlit==1.25.0
requests==2.28.0
beautifulsoup4==4.11.0
selenium==4.10.0
pandas==1.5.0
openpyxl==3.0.0
webdriver-manager==3.8.0
```

#### Solution 4: Platform-Specific Installation

**For Streamlit Cloud:**
```
# requirements.txt for Streamlit Cloud
streamlit
requests
beautifulsoup4
selenium
pandas
openpyxl
webdriver-manager
```

**For Heroku:**
Add `Aptfile` with:
```
chromium-browser
chromium-chromedriver
```

Add to `requirements.txt`:
```
streamlit
requests
beautifulsoup4
selenium
pandas
openpyxl
webdriver-manager
```

#### Solution 5: Local Development Fix

If you're running locally and getting this error:

1. **Create a fresh virtual environment:**
   ```bash
   python -m venv fresh_env
   fresh_env\Scripts\activate  # Windows
   # or
   source fresh_env/bin/activate  # Linux/Mac
   ```

2. **Install packages one by one:**
   ```bash
   pip install streamlit
   pip install requests
   pip install beautifulsoup4
   pip install selenium
   pip install pandas
   pip install openpyxl
   pip install webdriver-manager
   ```

3. **Test the app:**
   ```bash
   streamlit run app.py
   ```

### Selenium WebDriver Issues

#### Chrome Not Found
```bash
# Install Chrome browser first, then:
pip install webdriver-manager
```

#### ChromeDriver Compatibility
The app automatically downloads the correct ChromeDriver version, but if you get errors:

1. **Update Chrome browser**
2. **Clear webdriver cache:**
   ```bash
   # Delete the folder:
   # Windows: C:\Users\{username}\.wdm
   # Linux: ~/.wdm
   # Mac: ~/.wdm
   ```

### Memory Issues During Installation

If you get memory errors during installation:

1. **Install with no-cache:**
   ```bash
   pip install --no-cache-dir -r requirements-minimal.txt
   ```

2. **Install packages individually:**
   ```bash
   pip install streamlit --no-cache-dir
   pip install selenium --no-cache-dir
   # etc.
   ```

### Alternative: Docker Deployment

Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

# Install Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements-minimal.txt .
RUN pip install -r requirements-minimal.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t lead-generator .
docker run -p 8501:8501 lead-generator
```

### Cloud Platform Specific Solutions

#### Streamlit Cloud
- Use `requirements-minimal.txt`
- Add `packages.txt` with:
  ```
  chromium-browser
  chromium-chromedriver
  ```

#### Heroku
- Use buildpack: `heroku/python`
- Add Chrome buildpack: `heroku buildpacks:add --index 1 heroku-buildpack-google-chrome`
- Add `Procfile`:
  ```
  web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
  ```

#### Railway
- Use `requirements-minimal.txt`
- Set environment variable: `PORT=8501`

### Quick Fix Commands

Run these commands to quickly fix common issues:

```bash
# Clean installation
pip cache purge
pip uninstall streamlit -y
pip install streamlit --no-cache-dir

# Fix Chrome issues
pip uninstall selenium webdriver-manager -y
pip install selenium webdriver-manager

# Test setup
python test_setup.py
```

### Still Having Issues?

1. **Check Python version:** Use Python 3.8-3.11
2. **Update pip:** `pip install --upgrade pip`
3. **Use virtual environment:** Always use a clean virtual environment
4. **Check logs:** Look for specific error messages in the full log
5. **Minimal test:** Try running just `import streamlit; streamlit.hello()`

If none of these solutions work, you can run the app with only basic functionality by installing just the essential packages and commenting out the problematic features.