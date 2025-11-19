"""
Verify that users exist in database with correct roles
Run this to check if your database has the correct user setup
"""

import sqlite3
from werkzeug.security import check_password_hash

DB = "database.db"

print("\n" + "="*70)
print("  CHECKING USER DATABASE")
print("="*70 + "\n")

try:
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    
    # Get all users
    cursor.execute("SELECT id, username, password, role FROM users")
    users = cursor.fetchall()
    
    if not users:
        print("❌ ERROR: No users found in database!")
        print("\nPlease run: python database.py")
        conn.close()
        exit(1)
    
    print(f"Found {len(users)} user(s) in database:\n")
    print("-" * 70)
    print(f"{'ID':<5} {'Username':<15} {'Role':<12} {'Password Check':<20}")
    print("-" * 70)
    
    # Test passwords
    test_passwords = {
        'admin': 'admin123',
        'vendor1': 'vendor123',
        'employee1': 'emp123'
    }
    
    for user in users:
        user_id, username, password_hash, role = user
        
        # Check if password is correct
        if username in test_passwords:
            password_valid = check_password_hash(password_hash, test_passwords[username])
            password_status = "✅ Valid" if password_valid else "❌ Invalid"
        else:
            password_status = "⚠️  Custom"
        
        print(f"{user_id:<5} {username:<15} {role:<12} {password_status:<20}")
    
    print("-" * 70)
    
    # Check for required roles
    print("\n" + "="*70)
    print("  ROLE VERIFICATION")
    print("="*70 + "\n")
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE role='admin'")
    admin_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE role='vendor'")
    vendor_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE role='employee'")
    employee_count = cursor.fetchone()[0]
    
    print(f"Admin users:    {admin_count} {'✅' if admin_count > 0 else '❌'}")
    print(f"Vendor users:   {vendor_count} {'✅' if vendor_count > 0 else '❌'}")
    print(f"Employee users: {employee_count} {'✅' if employee_count > 0 else '❌'}")
    
    print("\n" + "="*70)
    print("  LOGIN TEST CREDENTIALS")
    print("="*70 + "\n")
    
    print("Admin Login:")
    print("  Username: admin")
    print("  Password: admin123")
    print("  Expected: Should redirect to /admin")
    print()
    
    print("Vendor Login:")
    print("  Username: vendor1")
    print("  Password: vendor123")
    print("  Expected: Should redirect to /vendor_update")
    print()
    
    print("Employee Login:")
    print("  Username: employee1")
    print("  Password: emp123")
    print("  Expected: Should redirect to /dashboard")
    print()
    
    conn.close()
    
    if admin_count > 0 and vendor_count > 0 and employee_count > 0:
        print("="*70)
        print("✅ ALL ROLES PRESENT - Database is correctly set up!")
        print("="*70 + "\n")
    else:
        print("="*70)
        print("⚠️  WARNING: Some roles are missing!")
        print("Please run: python database.py")
        print("="*70 + "\n")

except sqlite3.Error as e:
    print(f"❌ Database error: {e}")
    print("\nPlease run: python database.py")
except Exception as e:
    print(f"❌ Error: {e}")