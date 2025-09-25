@echo off
echo ================================================
echo        Lead Generation Agent Setup
echo ================================================
echo.

echo Step 1: Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Step 2: Installing minimal requirements...
pip install -r requirements-minimal.txt

echo.
echo Step 3: Testing installation...
python test_setup.py

echo.
echo Step 4: Installing optional packages (for enhanced features)...
pip install fake-useragent gspread oauth2client

echo.
echo ================================================
echo Setup complete! Run the app with:
echo streamlit run app.py
echo ================================================
pause