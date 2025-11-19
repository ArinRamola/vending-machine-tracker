from flask import Flask, render_template, request, redirect, send_file, session, url_for, flash, jsonify
import sqlite3
from datetime import datetime
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
import os
import importlib
import secrets

app = Flask(__name__)
# Generate a secure secret key
app.secret_key = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

DB = "database.db"

def query_db(q, args=(), one=False):
    """
    Lightweight DB helper with better error handling.
    """
    try:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(q, args)
        is_select = q.strip().lower().startswith("select")
        data = cursor.fetchall()
        if not is_select:
            conn.commit()
        conn.close()
        if one:
            return data[0] if data else None
        return data
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None if one else []

def login_required(role=None):
    """
    FIXED: Decorator for role-based access control
    """
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is logged in
            if "user_id" not in session:
                flash("Please login to access this page.", "warning")
                return redirect(url_for("login"))
            
            # If specific role is required, check it
            if role:
                user_role = session.get("role")
                if user_role != role:
                    flash(f"Access Denied! This page is for {role}s only.", "danger")
                    # Redirect based on actual role
                    if user_role == "admin":
                        return redirect(url_for("admin_page"))
                    elif user_role == "vendor":
                        return redirect(url_for("vendor_update"))
                    else:
                        return redirect(url_for("dashboard"))
            
            return f(*args, **kwargs)
        return decorated_function
    return wrapper

# ---------- HOME ----------
@app.route("/")
def home():
    if "user_id" in session:
        role = session.get("role")
        if role == "admin":
            return redirect(url_for("admin_page"))
        elif role == "vendor":
            return redirect(url_for("vendor_update"))
        else:
            return redirect(url_for("dashboard"))
    return render_template("index.html")

# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("home"))
    
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please provide both username and password.", "danger")
            return render_template("login.html")

        user = query_db("SELECT * FROM users WHERE username=?", (username,), one=True)
        
        if user and check_password_hash(user[2], password):  
            # Store user info in session
            session["user_id"] = user[0]
            session["username"] = user[1]
            session["role"] = user[3]
            
            flash(f"Welcome back, {user[1]}! Logged in as {user[3]}.", "success")
            
            # Redirect based on role
            if user[3] == "admin":
                return redirect(url_for("admin_page"))
            elif user[3] == "vendor":
                return redirect(url_for("vendor_update"))
            else:
                return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password!", "danger")

    return render_template("login.html")

# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        
        if not username or not password:
            flash("Username and password are required.", "danger")
            return render_template("register.html")
        
        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return render_template("register.html")
        
        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("register.html")
        
        # Check if username exists
        existing = query_db("SELECT id FROM users WHERE username=?", (username,), one=True)
        if existing:
            flash("Username already exists!", "danger")
            return render_template("register.html")
        
        # Create new employee account
        hashed_pw = generate_password_hash(password)
        query_db("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, hashed_pw, "employee"))
        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))
    
    return render_template("register.html")

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    username = session.get("username", "User")
    session.clear()
    flash(f"Goodbye, {username}!", "info")
    return redirect(url_for("home"))

# ---------- EMPLOYEE DASHBOARD ----------
@app.route("/dashboard")
@login_required(role="employee")
def dashboard():
    snacks = query_db("SELECT id, name, stock, expiry_date FROM snacks ORDER BY name")
    shelf_life_snacks = query_db("""
        SELECT id, name, stock, expiry_date,
        (julianday(expiry_date) - julianday('now')) AS days_left
        FROM snacks
        WHERE (julianday(expiry_date) - julianday('now')) <= 3
        ORDER BY days_left ASC
    """)
    
    # Get total stock count
    total_stock = query_db("SELECT SUM(stock) FROM snacks", one=True)
    total_snacks = total_stock[0] if total_stock and total_stock[0] else 0
    
    return render_template("dashboard.html", 
                         snacks=snacks, 
                         shelf_life_snacks=shelf_life_snacks,
                         total_snacks=total_snacks)

# ---------- ADMIN PANEL ----------
@app.route("/admin")
@login_required(role="admin")
def admin_page():
    machines = query_db("SELECT * FROM machines ORDER BY name")
    snacks = query_db("SELECT * FROM snacks ORDER BY name")
    users = query_db("SELECT id, username, role FROM users ORDER BY role, username")
    
    # Statistics
    total_machines = len(machines)
    total_snacks = query_db("SELECT SUM(stock) FROM snacks", one=True)
    total_stock = total_snacks[0] if total_snacks and total_snacks[0] else 0
    
    expiring_count = query_db("""
        SELECT COUNT(*) FROM snacks
        WHERE (julianday(expiry_date) - julianday('now')) <= 3
    """, one=True)
    expiring = expiring_count[0] if expiring_count else 0
    
    return render_template("admin.html", 
                         machines=machines, 
                         snacks=snacks,
                         users=users,
                         total_machines=total_machines,
                         total_stock=total_stock,
                         expiring=expiring)

# ---------- ADD SNACK ----------
@app.route("/add_snack", methods=["POST"])
@login_required(role="admin")
def add_snack():
    name = request.form.get("name", "").strip()
    expiry = request.form.get("expiry", "").strip()  
    stock = request.form.get("stock", "").strip()

    if not name or not expiry or not stock:
        flash("All fields are required!", "danger")
        return redirect(url_for("admin_page"))

    try:
        stock_int = int(stock)
        if stock_int < 0:
            flash("Stock cannot be negative!", "danger")
            return redirect(url_for("admin_page"))
    except ValueError:
        flash("Stock must be a valid number!", "danger")
        return redirect(url_for("admin_page"))

    query_db("INSERT INTO snacks (name, expiry_date, stock) VALUES (?, ?, ?)",
             (name, expiry, stock_int))
    flash(f"Snack '{name}' added successfully!", "success")
    return redirect(url_for("admin_page"))

# ---------- UPDATE SNACK STOCK ----------
@app.route("/update_snack/<int:snack_id>", methods=["POST"])
@login_required(role="admin")
def update_snack(snack_id):
    new_stock = request.form.get("stock", "").strip()
    
    try:
        stock_int = int(new_stock)
        if stock_int < 0:
            flash("Stock cannot be negative!", "danger")
            return redirect(url_for("admin_page"))
    except ValueError:
        flash("Stock must be a valid number!", "danger")
        return redirect(url_for("admin_page"))
    
    query_db("UPDATE snacks SET stock=? WHERE id=?", (stock_int, snack_id))
    flash("Stock updated successfully!", "success")
    return redirect(url_for("admin_page"))

# ---------- DELETE SNACK ----------
@app.route("/delete_snack/<int:snack_id>", methods=["POST"])
@login_required(role="admin")
def delete_snack(snack_id):
    snack = query_db("SELECT name FROM snacks WHERE id=?", (snack_id,), one=True)
    if snack:
        query_db("DELETE FROM snacks WHERE id=?", (snack_id,))
        flash(f"Snack '{snack[0]}' deleted successfully!", "success")
    else:
        flash("Snack not found!", "danger")
    return redirect(url_for("admin_page"))

# ---------- ADD MACHINE ----------
@app.route("/add_machine", methods=["POST"])
@login_required(role="admin")
def add_machine():
    name = request.form.get("name", "").strip()
    location = request.form.get("location", "").strip()
    
    if not name or not location:
        flash("Machine name and location are required!", "danger")
        return redirect(url_for("admin_page"))
    
    query_db("INSERT INTO machines (name, location) VALUES (?, ?)", (name, location))
    flash(f"Machine '{name}' added successfully!", "success")
    
    # Regenerate QR codes
    try:
        import generate_qr
        importlib.reload(generate_qr)
        flash("QR code generated for the new machine!", "info")
    except Exception as e:
        print(f"QR generation failed: {e}")
        flash("Machine added but QR code generation failed. Run generate_qr.py manually.", "warning")
    
    return redirect(url_for("admin_page"))

# ---------- DELETE MACHINE ----------
@app.route("/delete_machine/<int:machine_id>", methods=["POST"])
@login_required(role="admin")
def delete_machine(machine_id):
    machine = query_db("SELECT name FROM machines WHERE id=?", (machine_id,), one=True)
    if machine:
        query_db("DELETE FROM machines WHERE id=?", (machine_id,))
        # Delete QR code file
        qr_path = f"static/qrcodes/machine_{machine_id}.png"
        if os.path.exists(qr_path):
            os.remove(qr_path)
        flash(f"Machine '{machine[0]}' deleted successfully!", "success")
    else:
        flash("Machine not found!", "danger")
    return redirect(url_for("admin_page"))

# ---------- SHELF LIFE PAGE ----------
@app.route("/shelf_life")
@login_required()
def shelf_life():
    snacks = query_db("""
        SELECT id, name, stock, expiry_date,
        (julianday(expiry_date) - julianday('now')) AS days_left
        FROM snacks
        WHERE (julianday(expiry_date) - julianday('now')) <= 3
        ORDER BY days_left ASC
    """)
    return render_template("shelf_life.html", snacks=snacks)

# ---------- MACHINES ----------
@app.route("/machines")
@login_required()
def machines():
    machines = query_db("SELECT * FROM machines ORDER BY name")
    return render_template("machines.html", machines=machines)

@app.route("/machine/<int:id>")
@login_required()
def machine(id):
    machine = query_db("SELECT * FROM machines WHERE id=?", (id,), one=True)
    if not machine:
        flash("Machine not found!", "danger")
        return redirect(url_for("machines"))
    return render_template("machine.html", machine=machine)

@app.route("/machine_view/<int:id>")
@login_required()
def machine_view(id):
    machine = query_db("SELECT * FROM machines WHERE id=?", (id,), one=True)
    snacks = query_db("SELECT id, name, stock, expiry_date FROM snacks ORDER BY name")
    if not machine:
        flash("Machine not found!", "danger")
        return redirect(url_for("machines"))
    return render_template("machine_view.html", machine=machine, snacks=snacks)

# ---------- VENDOR UPDATE ----------
@app.route("/vendor_update", methods=["GET", "POST"])
@login_required(role="vendor")
def vendor_update():
    if request.method == "POST":
        vendor = session.get("username")
        machine = request.form.get("machine", "").strip()
        info = request.form.get("info", "").strip()
        time_str = datetime.now().isoformat(timespec="seconds")

        if not machine or not info:
            flash("Please select a machine and provide update information!", "danger")
            return redirect(url_for("vendor_update"))

        query_db(
            "INSERT INTO updates (vendor, machine, info, time) VALUES (?, ?, ?, ?)",
            (vendor, machine, info, time_str)
        )
        
        flash("Update submitted successfully!", "success")

        try:
            import generate_chart
            importlib.reload(generate_chart)
        except Exception as e:
            print("Chart regeneration failed:", e)

        return redirect(url_for("vendor_update"))

    machines = query_db("SELECT * FROM machines ORDER BY name")
    recent_updates = query_db("""
        SELECT vendor, machine, info, time 
        FROM updates 
        WHERE vendor=? 
        ORDER BY time DESC 
        LIMIT 10
    """, (session.get("username"),))
    
    return render_template("vendor_update.html", 
                         machines=machines, 
                         recent_updates=recent_updates)

# ---------- VIEW UPDATES ----------
@app.route("/view_updates")
@login_required(role="admin")
def view_updates():
    updates = query_db("""
        SELECT id, vendor, machine, info, time 
        FROM updates 
        ORDER BY time DESC 
        LIMIT 50
    """)
    return render_template("view_updates.html", updates=updates)

# ---------- INVENTORY TRACKING ----------
@app.route("/inventory")
@login_required()
def inventory():
    """Complete inventory tracking view"""
    snacks = query_db("""
        SELECT id, name, stock, expiry_date,
        (julianday(expiry_date) - julianday('now')) AS days_left
        FROM snacks
        ORDER BY name
    """)
    
    # Calculate statistics
    total_items = len(snacks)
    total_stock = query_db("SELECT SUM(stock) FROM snacks", one=True)
    total_stock_count = total_stock[0] if total_stock and total_stock[0] else 0
    
    low_stock = query_db("SELECT COUNT(*) FROM snacks WHERE stock < 10", one=True)
    low_stock_count = low_stock[0] if low_stock else 0
    
    out_of_stock = query_db("SELECT COUNT(*) FROM snacks WHERE stock = 0", one=True)
    out_of_stock_count = out_of_stock[0] if out_of_stock else 0
    
    expiring_soon = query_db("""
        SELECT COUNT(*) FROM snacks 
        WHERE (julianday(expiry_date) - julianday('now')) <= 7
    """, one=True)
    expiring_count = expiring_soon[0] if expiring_soon else 0
    
    return render_template("inventory.html", 
                         snacks=snacks,
                         total_items=total_items,
                         total_stock=total_stock_count,
                         low_stock=low_stock_count,
                         out_of_stock=out_of_stock_count,
                         expiring=expiring_count)

# ---------- ANALYTICS DASHBOARD ----------
@app.route("/analytics")
@login_required()
def analytics():
    """Main analytics dashboard"""
    # Get all vendor updates
    updates = query_db("SELECT * FROM updates ORDER BY time DESC LIMIT 50")
    
    # Get snack popularity
    popularity = query_db("""
        SELECT info, COUNT(*) as count 
        FROM updates 
        GROUP BY info 
        ORDER BY count DESC
    """)
    
    # Get vendor activity
    vendor_activity = query_db("""
        SELECT vendor, COUNT(*) as count 
        FROM updates 
        GROUP BY vendor 
        ORDER BY count DESC
    """)
    
    # Get machine activity
    machine_activity = query_db("""
        SELECT machine, COUNT(*) as count 
        FROM updates 
        GROUP BY machine 
        ORDER BY count DESC
    """)
    
    # Generate chart if updates exist
    chart_path = "static/charts/popularity.png"
    if popularity and len(popularity) > 0:
        try:
            import generate_chart
            importlib.reload(generate_chart)
        except Exception as e:
            print(f"Chart generation failed: {e}")
    
    return render_template("analytics.html",
                         updates=updates,
                         popularity=popularity,
                         vendor_activity=vendor_activity,
                         machine_activity=machine_activity,
                         chart_exists=os.path.exists(chart_path))

# ---------- POPULARITY CHART ----------
@app.route("/popularity_chart")
@login_required()
def popularity_chart():
    """Display snack popularity analytics"""
    chart_path = "static/charts/popularity.png"
    
    # Try to generate chart if it doesn't exist
    if not os.path.exists(chart_path):
        try:
            import generate_chart
            importlib.reload(generate_chart)
        except Exception as e:
            print(f"Chart generation failed: {e}")
            flash("No analytics data available yet. Vendor updates are needed to generate charts.", "info")
            # Redirect based on role
            role = session.get("role")
            if role == "admin":
                return redirect(url_for("admin_page"))
            elif role == "vendor":
                return redirect(url_for("vendor_update"))
            else:
                return redirect(url_for("dashboard"))
    
    # Get update statistics
    stats = query_db("""
        SELECT info, COUNT(*) as count 
        FROM updates 
        GROUP BY info 
        ORDER BY count DESC 
        LIMIT 10
    """)
    
    return render_template("popularity_chart.html", stats=stats, chart_exists=os.path.exists(chart_path))

# ---------- QR ACCESS ----------
@app.route("/qr_access")
@login_required()
def qr_access():
    machines = query_db("SELECT * FROM machines ORDER BY name")
    return render_template("qr_access.html", machines=machines)

# ---------- QR IMAGE FILE ----------
@app.route('/qr_image/<int:machine_id>')
@login_required()
def qr_image(machine_id):
    path = f"static/qrcodes/machine_{machine_id}.png"
    if os.path.exists(path):
        return send_file(path, mimetype='image/png')
    return "QR image not found", 404

@app.route("/qr/<int:machine_id>")
@login_required()
def qr(machine_id):
    machine = query_db("SELECT * FROM machines WHERE id=?", (machine_id,), one=True)
    filepath = f"static/qrcodes/machine_{machine_id}.png"
    
    if not machine:
        flash("Machine not found!", "danger")
        return redirect(url_for("qr_access"))
    
    if os.path.exists(filepath):
        return render_template("qr_display.html", machine=machine, qr_path=filepath)
    
    flash("QR code not found! Please regenerate QR codes.", "warning")
    return redirect(url_for("qr_access"))

# ---------- API ENDPOINTS ----------
@app.route("/api/snacks")
@login_required()
def api_snacks():
    snacks = query_db("SELECT id, name, stock, expiry_date FROM snacks")
    return jsonify([{
        "id": s[0],
        "name": s[1],
        "stock": s[2],
        "expiry_date": s[3]
    } for s in snacks])

# ---------- ERROR HANDLERS ----------
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

# ---------- RUN APP ----------
if __name__ == "__main__":
    if not os.path.exists(DB):
        print(f"Warning: {DB} not found. Running database initialization...")
        import database
    
    # Ensure required directories exist
    os.makedirs("static/qrcodes", exist_ok=True)
    os.makedirs("static/charts", exist_ok=True)
    
    # Check if running in production
    is_production = os.environ.get('FLASK_ENV') == 'production'
    
    # Only show credentials in development
    if not is_production:
        print("\n" + "="*60)
        print("  VENDING MACHINE MANAGEMENT SYSTEM")
        print("="*60)
        print("\nDemo Login Credentials:")
        print("-" * 60)
        print("Admin:    username: admin     password: admin123")
        print("Vendor:   username: vendor1   password: vendor123")
        print("Employee: username: employee1 password: emp123")
        print("="*60 + "\n")
    else:
        print("\n" + "="*60)
        print("  VENDING MACHINE MANAGEMENT SYSTEM")
        print("  Running in PRODUCTION mode")
        print("="*60 + "\n")
    
    # Get port from environment variable (Render/Heroku provide this)
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app
    app.run(debug=not is_production, host='0.0.0.0', port=port)
