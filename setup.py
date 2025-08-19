#!/usr/bin/env python3
"""
PediaSafeAI Setup Script
Automated setup for the pediatric prescription screening application
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("🔧 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Error installing packages. Please check your internet connection.")
        return False

def check_files():
    """Check if all required files are present"""
    required_files = ["app.py", "requirements.txt"]
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files are present!")
    return True

def run_application():
    """Launch the Streamlit application"""
    print("🚀 Launching PediaSafeAI...")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Application closed by user.")
    except Exception as e:
        print(f"❌ Error running application: {e}")

def main():
    """Main setup function"""
    print("🛡️ PediaSafeAI Setup")
    print("=" * 50)
    print("by Ayesha Bibi, MPhil Pharmacy Practice Student (GCUF)")
    print("=" * 50)
    
    # Check if files exist
    if not check_files():
        print("\n📥 Please ensure all files are in the same directory:")
        print("   - app.py")
        print("   - requirements.txt")
        print("   - setup.py (this file)")
        return
    
    # Install requirements
    if not install_requirements():
        return
    
    print("\n🎉 Setup completed successfully!")
    print("\nTo run the application anytime, use:")
    print("   streamlit run app.py")
    
    # Ask if user wants to run now
    response = input("\n❓ Would you like to run the application now? (y/n): ").lower()
    if response in ['y', 'yes']:
        run_application()
    else:
        print("\n👍 Setup complete! Run 'streamlit run app.py' when ready.")

if __name__ == "__main__":
    main()
