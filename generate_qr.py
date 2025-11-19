"""
Enhanced QR Code Generator with detailed error handling
Generates QR codes for all vending machines in the database
"""

import qrcode
import os
import sqlite3
import sys

DB = "database.db"
QR_DIR = "static/qrcodes"

print("\n" + "="*70)
print("  QR CODE GENERATOR")
print("="*70 + "\n")

# Step 1: Check if qrcode library is installed
try:
    import qrcode
    from PIL import Image
    print("✅ QR code libraries installed")
except ImportError as e:
    print("❌ ERROR: Required libraries not installed!")
    print("\n🔧 Solution: Install required packages:")
    print("   pip install qrcode[pil]")
    print("   pip install Pillow")
    sys.exit(1)

# Step 2: Create QR codes directory
try:
    os.makedirs(QR_DIR, exist_ok=True)
    print(f"✅ Directory created/verified: {QR_DIR}")
except Exception as e:
    print(f"❌ ERROR: Cannot create directory: {e}")
    sys.exit(1)

# Step 3: Connect to database
try:
    if not os.path.exists(DB):
        print(f"❌ ERROR: Database '{DB}' not found!")
        print("\n🔧 Solution: Run 'python database.py' to create database")
        sys.exit(1)
    
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    print(f"✅ Connected to database: {DB}")
except Exception as e:
    print(f"❌ ERROR: Cannot connect to database: {e}")
    sys.exit(1)

# Step 4: Get all machines
try:
    cursor.execute("SELECT id, name, location FROM machines")
    machines = cursor.fetchall()
    
    if not machines:
        print("\n⚠️  WARNING: No machines found in database!")
        print("\n🔧 Solution: Add machines via admin panel or run:")
        print("   python database.py")
        conn.close()
        sys.exit(0)
    
    print(f"✅ Found {len(machines)} machine(s) in database\n")
    
except Exception as e:
    print(f"❌ ERROR: Cannot query machines: {e}")
    conn.close()
    sys.exit(1)

# Step 5: Generate QR codes
print("="*70)
print("  GENERATING QR CODES")
print("="*70 + "\n")

success_count = 0
failed_count = 0

for machine_id, machine_name, location in machines:
    try:
        # Create URL for machine
        url = f"http://127.0.0.1:5000/machine_view/{machine_id}"
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code
        qr_path = os.path.join(QR_DIR, f"machine_{machine_id}.png")
        img.save(qr_path)
        
        print(f"✅ Machine {machine_id}: {machine_name}")
        print(f"   Location: {location}")
        print(f"   QR Code: {qr_path}")
        print(f"   URL: {url}\n")
        
        success_count += 1
        
    except Exception as e:
        print(f"❌ FAILED - Machine {machine_id}: {machine_name}")
        print(f"   Error: {e}\n")
        failed_count += 1

conn.close()

# Step 6: Summary
print("="*70)
print("  GENERATION COMPLETE")
print("="*70 + "\n")

print(f"✅ Successfully generated: {success_count} QR code(s)")
if failed_count > 0:
    print(f"❌ Failed: {failed_count} QR code(s)")

print("\n📱 QR codes saved in: " + os.path.abspath(QR_DIR))
print("\n🔍 To view QR codes:")
print("   1. Start your app: python app.py")
print("   2. Login and go to: http://127.0.0.1:5000/qr_access")
print("   3. Or check the 'static/qrcodes/' folder directly")

print("\n" + "="*70 + "\n")

# Verify files exist
print("Verifying generated files:")
for machine_id, machine_name, _ in machines:
    qr_path = os.path.join(QR_DIR, f"machine_{machine_id}.png")
    if os.path.exists(qr_path):
        file_size = os.path.getsize(qr_path)
        print(f"  ✅ machine_{machine_id}.png ({file_size} bytes)")
    else:
        print(f"  ❌ machine_{machine_id}.png (NOT FOUND)")

print("\n" + "="*70 + "\n")