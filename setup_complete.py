"""
Complete Setup Script for Vending Machine System
Run this script to set up the entire project automatically
"""

import os
import subprocess
import sys

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def create_directories():
    """Create necessary directories"""
    print_header("Creating Project Directories")
    
    directories = [
        "templates",
        "static",
        "static/css",
        "static/js",
        "static/qrcodes",
        "static/charts",
        "static/uploads"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created: {directory}")
    
    print("\n✅ All directories created successfully!")

def check_python_version():
    """Check if Python version is adequate"""
    print_header("Checking Python Version")
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Error: Python 3.7 or higher is required!")
        sys.exit(1)
    
    print("✅ Python version is compatible!")

def install_dependencies():
    """Install required Python packages"""
    print_header("Installing Dependencies")
    
    packages = [
        "Flask==3.0.0",
        "Werkzeug==3.0.1",
        "matplotlib==3.8.2",
        "qrcode==7.4.2",
        "Pillow==10.1.0"
    ]
    
    print("Installing packages...")
    for package in packages:
        print(f"\nInstalling {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package} installed successfully")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False
    
    print("\n✅ All dependencies installed successfully!")
    return True

def initialize_database():
    """Initialize the database"""
    print_header("Initializing Database")
    
    try:
        import database
        print("✅ Database initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def generate_qr_codes():
    """Generate QR codes for machines"""
    print_header("Generating QR Codes")
    
    try:
        import generate_qr
        print("✅ QR codes generated successfully!")
        return True
    except Exception as e:
        print(f"⚠️  QR code generation failed: {e}")
        print("You can generate them later by running: python generate_qr.py")
        return False

def print_final_instructions():
    """Print final setup instructions"""
    print_header("Setup Complete!")
    
    print("""
🎉 Your Vending Machine System is ready!

📋 Next Steps:
    
1. Start the application:
   python app.py

2. Open your browser and go to:
   http://127.0.0.1:5000

3. Login with demo credentials:
   
   Admin:
   - Username: admin
   - Password: admin123
   
   Vendor:
   - Username: vendor1
   - Password: vendor123
   
   Employee:
   - Username: employee1
   - Password: emp123

4. Or register a new employee account!

📚 Additional Scripts:
   - Regenerate QR codes: python generate_qr.py
   - Regenerate charts: python generate_chart.py
   - Reset database: python database.py

⚙️  Configuration:
   - Database: database.db
   - Secret key: Auto-generated (secure)
   - Debug mode: Enabled (disable in production)

🔒 Security Notes:
   - Change default passwords in production
   - Set SECRET_KEY environment variable in production
   - Enable HTTPS for production deployment

📖 Documentation:
   - Check the change summary document for complete details
   - All templates are in the templates/ folder
   - Static files in static/ folder

Happy coding! 🚀
""")

def main():
    """Main setup function"""
    print_header("Vending Machine System - Complete Setup")
    
    print("This script will:")
    print("1. Check Python version")
    print("2. Create necessary directories")
    print("3. Install dependencies")
    print("4. Initialize database")
    print("5. Generate QR codes")
    
    input("\nPress Enter to continue...")
    
    # Step 1: Check Python version
    check_python_version()
    
    # Step 2: Create directories
    create_directories()
    
    # Step 3: Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed! Please install dependencies manually.")
        sys.exit(1)
    
    # Step 4: Initialize database
    if not initialize_database():
        print("\n❌ Setup failed! Please check database.py file.")
        sys.exit(1)
    
    # Step 5: Generate QR codes
    generate_qr_codes()
    
    # Final instructions
    print_final_instructions()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ An error occurred: {e}")
        sys.exit(1)