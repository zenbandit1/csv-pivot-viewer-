#!/usr/bin/env python3
"""
Helper script to capture screenshots for the CSV Pivot Table Viewer README.

Instructions:
1. Run the CSV Pivot Table Viewer: streamlit run csv_pivot_web.py
2. Navigate to the URL in your browser (typically http://localhost:8501)
3. Capture screenshots manually or use tools like:
   - Screenshot tools built into your OS
   - Browser extensions like "Full Page Screen Capture"
   - Tools like Selenium for automated screenshots

4. Save your screenshots as:
   - screenshots/main_view.png (Main interface)
   - screenshots/date_filter.png (Timeline chart with date filter)
   - screenshots/multiple_values.png (Multiple value fields)

Suggested screenshot contents:
1. main_view.png: 
   - Complete interface with sample data loaded
   - Row field set to "Region"
   - Column field set to "Product"
   - Value field set to "Sales"

2. date_filter.png:
   - Filter panel expanded for the "Date" field
   - Timeline chart visible showing data distribution
   - Date range selected (partial range to show filtering)

3. multiple_values.png:
   - Multiple values selected (e.g., both "Sales" and "Quantity")
   - Pivot table showing multiple metrics side by side
"""

import os
import sys
import webbrowser
import time

def main():
    """Open browser and provide screenshot instructions."""
    # Create screenshots directory if it doesn't exist
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")
    
    print("\n=== CSV Pivot Table Viewer Screenshot Helper ===\n")
    print("1. Make sure your CSV Pivot Table Viewer is running:")
    print("   streamlit run csv_pivot_web.py")
    
    # Try to open the browser to the Streamlit app
    try:
        print("\n2. Opening browser to http://localhost:8501")
        webbrowser.open("http://localhost:8501")
    except:
        print("   Could not open browser automatically.")
        print("   Please open http://localhost:8501 manually")
    
    print("\n3. Capture the following screenshots:")
    print("   - Main view (screenshots/main_view.png)")
    print("   - Date filter with timeline chart (screenshots/date_filter.png)")
    print("   - Multiple value fields (screenshots/multiple_values.png)")
    
    print("\n4. Update README.md to reference your screenshots")
    
    print("\nAfter capturing screenshots, you can push to GitHub:")
    print("git add screenshots/*.png")
    print("git commit -m \"Add application screenshots\"")
    print("git push\n")

if __name__ == "__main__":
    main()