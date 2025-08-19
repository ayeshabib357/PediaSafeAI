# 🛡️ PediaSafeAI

An AI-driven clinical decision support system designed to screen pediatric prescriptions for inappropriate use, omissions, and drug interactions to ensure safer pharmacotherapy.

**Developed by:** Ayesha Bibi, MPhil Pharmacy Practice Student (GCUF)

## Features

- ✅ Inappropriate prescription screening using POPI, PIPc, and KIDs list criteria
- ✅ Prescription omission detection
- ✅ Drug-drug interaction screening using OpenFDA API
- ✅ PDF report generation
- ✅ Professional, medical-grade user interface
- ✅ Free to use and accessible online

## Complete Setup Instructions

### Step 1: Install Anaconda (if not already installed)

1. Go to [https://www.anaconda.com/products/distribution](https://www.anaconda.com/products/distribution)
2. Download the installer for your operating system (Windows/Mac/Linux)
3. Run the installer with default settings
4. Restart your computer after installation

### Step 2: Create Project Directory

1. Create a new folder on your desktop called `PediaSafeAI`
2. Open the folder

### Step 3: Download Project Files

Save the following files in your `PediaSafeAI` folder:

1. `app.py` (the main application code)
2. `requirements.txt` (list of required packages)
3. `README.md` (this file)

### Step 4: Install Required Packages

1. Open **Anaconda Prompt** (search for it in your start menu)
2. Navigate to your project folder by typing:
   ```
   cd Desktop/PediaSafeAI
   ```
3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
4. Wait for all packages to install (this may take a few minutes)

### Step 5: Run the Application Locally

1. In the same Anaconda Prompt, type:
   ```
   streamlit run app.py
   ```
2. The application will open in your web browser automatically
3. If it doesn't open automatically, go to `http://localhost:8501` in your browser

### Step 6: Deploy to the Internet (Free)

#### Option A: Streamlit Cloud (Recommended)

1. Create a GitHub account at [https://github.com](https://github.com)
2. Create a new repository called `PediaSafeAI`
3. Upload your files (`app.py`, `requirements.txt`, `README.md`) to the repository
4. Go to [https://share.streamlit.io](https://share.streamlit.io)
5. Sign in with your GitHub account
6. Click "New app"
7. Select your repository and branch
8. Set the main file path to `app.py`
9. Click "Deploy"
10. Your app will be live at a public URL within a few minutes

#### Option B: Heroku (Alternative)

1. Create a Heroku account at [https://heroku.com](https://heroku.com)
2. Install Heroku CLI
3. Create additional files in your project:
   - `Procfile` (contains: `web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`)
   - `setup.sh` (contains Streamlit configuration)
4. Follow Heroku deployment guide for Python apps

### Step 7: Share Your Application

Once deployed, you'll receive a public URL that you can share with others. Anyone with internet access can use your application for free!

## How to Use the Application

1. **Landing Page**: Click "Enter Application" to start
2. **Patient Information**: Enter patient age in years or months
3. **Clinical Information**: Select the medical condition from dropdown
4. **Medications**: Select all current medications from the dropdown
5. **Screen**: Click "Screen Prescription" to analyze
6. **Results**: Review inappropriate prescriptions, omissions, and interactions
7. **Download**: Generate and download PDF report

## Database Integration

The application integrates:

- **POPI Criteria**: Pediatrics: Omission of Prescriptions and Inappropriate prescriptions
- **PIPc Criteria**: Pediatric Inappropriate Prescribing Criteria
- **KIDs List**: Key potentially Inappropriate Drugs
- **OpenFDA API**: For drug-drug interaction screening

## Technical Details

- **Framework**: Streamlit (Python web framework)
- **Backend**: Python with pandas for data processing
- **PDF Generation**: ReportLab library
- **API Integration**: OpenFDA REST API for drug interactions
- **Hosting**: Can be deployed on Streamlit Cloud, Heroku, or similar platforms

## Troubleshooting

### Common Issues and Solutions:

1. **"Module not found" error**:
   - Make sure you ran `pip install -r requirements.txt`
   - Restart Anaconda Prompt and try again

2. **Application doesn't start**:
   - Check that you're in the correct directory
   - Ensure `app.py` is in the same folder
   - Try running `python --version` to confirm Python is installed

3. **Slow loading**:
   - This is normal on first run as packages load
   - Subsequent runs will be faster

4. **Port already in use**:
   - Close other Streamlit applications
   - Or use: `streamlit run app.py --server.port 8502`

### Getting Help:

1. Check the Streamlit documentation: [https://docs.streamlit.io](https://docs.streamlit.io)
2. For deployment issues, check Streamlit Cloud documentation
3. For Python package issues, search for the specific error message

## Important Notes

- This tool is for educational and screening purposes only
- Always consult healthcare professionals for clinical decisions
- The databases used may not be exhaustive
- Individual patient factors must always be considered

## Future Enhancements

- Integration with more comprehensive drug databases
- Real-time OpenFDA API integration
- Support for additional pediatric screening criteria
- Multi-language support
- Enhanced reporting features

## License

This project is developed for educational purposes. Please ensure compliance with local regulations when using in clinical settings.

---

**Developed for pediatric medication safety • Always consult healthcare professionals for clinical decisions**
