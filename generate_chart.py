import sqlite3
import matplotlib
matplotlib.use("Agg")  
import matplotlib.pyplot as plt
import os

DB = "database.db"

# Ensure charts directory exists
os.makedirs("static/charts", exist_ok=True)

try:
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        SELECT info, COUNT(*) as cnt
        FROM updates
        GROUP BY info
        ORDER BY cnt DESC
        LIMIT 10
    """)

    data = c.fetchall()
    conn.close()

    if data and len(data) > 0:
        snacks = [row[0] for row in data]
        counts = [row[1] for row in data]

        # Create figure with better size
        plt.figure(figsize=(12, 7))
        
        # Create bar chart with colors
        colors = plt.cm.viridis([i/len(snacks) for i in range(len(snacks))])
        bars = plt.bar(snacks, counts, color=colors, edgecolor='black', linewidth=1.2)
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontweight='bold', fontsize=10)
        
        plt.xlabel("Snack / Item", fontsize=12, fontweight='bold')
        plt.ylabel("Number of Updates", fontsize=12, fontweight='bold')
        plt.title("Snack Popularity Dashboard - Most Updated Items", fontsize=14, fontweight='bold', pad=20)
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3, linestyle='--')
        plt.tight_layout()

        # Save the chart
        chart_path = "static/charts/popularity.png"
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"✅ Snack popularity chart generated successfully: {chart_path}")
        print(f"📊 Total items in chart: {len(data)}")

    else:
        print("⚠️  No vendor update data available for chart generation.")
        print("📝 Ask vendors to submit updates to generate analytics.")
        
        # Create a placeholder chart
        plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, 'No Data Available\n\nSubmit vendor updates to generate chart', 
                ha='center', va='center', fontsize=16, transform=plt.gca().transAxes)
        plt.axis('off')
        plt.tight_layout()
        plt.savefig("static/charts/popularity.png", dpi=150, bbox_inches='tight')
        plt.close()
        print("📋 Placeholder chart created.")

except Exception as e:
    print(f"❌ Error generating chart: {e}")
    import traceback
    traceback.print_exc()