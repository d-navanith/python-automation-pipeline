"""
02_api_to_excel_reporter.py - Lesson 2: API & Data Automation

What this script automates:
1. Calls a live REST API to fetch current foreign exchange rates.
2. Parses raw JSON responses and validates HTTP status codes.
3. Uses pandas to structure, sort, and calculate metrics.
4. Automatically exports a multi-sheet, timestamped Excel report.
"""

from datetime import datetime
from pathlib import Path
import requests
import pandas as pd

# Free, open currency rates API (no API key required)
API_URL = "https://api.frankfurter.app/latest?from=USD"


def fetch_live_rates(base_currency: str = "USD") -> dict:
    """
    Step 1: API Automation.
    Makes an HTTP GET request to the REST API and parses the JSON body.
    """
    url = f"https://api.frankfurter.app/latest?from={base_currency}"
    print(f"[API] Sending GET request to: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        
        # Check HTTP status code (200 means OK)
        if response.status_code == 200:
            print(f"[API] Success! Received HTTP 200 OK")
            return response.json()
        else:
            print(f"[ERROR] API returned error status: {response.status_code}")
            return {}
            
    except requests.RequestException as e:
        print(f"[ERROR] Network request failed: {e}")
        return {}


def process_and_export_to_excel(api_data: dict, output_file: Path) -> Path:
    """
    Step 2: Data Transformation & Excel Generation.
    Converts raw dictionary into a structured pandas DataFrame and saves to Excel.
    """
    if not api_data or "rates" not in api_data:
        raise ValueError("Invalid or missing API data.")

    base = api_data.get("base", "USD")
    date_str = api_data.get("date", str(datetime.now().date()))
    rates = api_data["rates"]

    # 1. Build a clean tabular list of records
    records = []
    for currency, rate in rates.items():
        records.append({
            "Base Currency": base,
            "Target Currency": currency,
            "Exchange Rate (1 USD)": round(rate, 4),
            "Value for 100 USD": round(rate * 100, 2),
            "As Of Date": date_str
        })

    # 2. Convert into a pandas DataFrame
    df = pd.DataFrame(records)
    
    # Sort alphabetically by target currency
    df.sort_values(by="Target Currency", inplace=True)

    # 3. Calculate summary metrics
    summary_data = [
        {"Metric": "Base Currency", "Value": base},
        {"Metric": "Total Currencies Tracked", "Value": len(df)},
        {"Metric": "Date of Rates", "Value": date_str},
        {"Metric": "Strongest Currency vs USD", "Value": df.loc[df["Exchange Rate (1 USD)"].idxmin()]["Target Currency"]},
        {"Metric": "Weakest Currency vs USD", "Value": df.loc[df["Exchange Rate (1 USD)"].idxmax()]["Target Currency"]},
        {"Metric": "Report Generated At", "Value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    ]
    df_summary = pd.DataFrame(summary_data)

    # 4. Save to Excel with multiple sheets
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Exchange_Rates", index=False)
        df_summary.to_excel(writer, sheet_name="Report_Summary", index=False)

    return output_file


if __name__ == "__main__":
    print("=" * 60)
    print(" Lesson 2: Automated API to Excel Pipeline")
    print("=" * 60)

    # 1. Fetch live data
    data = fetch_live_rates(base_currency="USD")
    
    if data:
        # 2. Target output file in reports directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reports_dir = Path(__file__).parent / "reports"
        excel_path = reports_dir / f"Currency_Rates_Report_{timestamp}.xlsx"
        
        # 3. Transform and save to Excel
        saved_path = process_and_export_to_excel(data, excel_path)
        
        print("-" * 60)
        print(f"[SUCCESS] Excel report generated:")
        print(f"  --> Path: {saved_path}")
        print("=" * 60)
