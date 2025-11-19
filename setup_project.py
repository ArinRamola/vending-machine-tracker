import os

folders = [
    "templates",
    "static",
    "static/css",
    "static/js"
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)

files = {
    "app.py": """# Flask app entry point
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
""",

    "templates/index.html": """<!DOCTYPE html>
<html>
<head>
    <title>Home</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <h1>Welcome to the Vending Machine System</h1>
</body>
</html>
""",

    "templates/machine.html": """<!DOCTYPE html>
<html>
<head><title>Machine</title></head>
<body>
<h2>Machine View</h2>
</body>
</html>
""",

    "templates/vendor_update.html": """<!DOCTYPE html>
<html>
<head><title>Vendor Update</title></head>
<body>
<h2>Vendor Update Page</h2>
</body>
</html>
""",

    "templates/admin.html": """<!DOCTYPE html>
<html>
<head><title>Admin Dashboard</title></head>
<body>
<h2>Admin Dashboard</h2>
</body>
</html>
""",

    "static/css/style.css": """body {
    font-family: Arial, sans-serif;
}
"""
}

for file_path, content in files.items():
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write(content)

print("Project structure created successfully!")
