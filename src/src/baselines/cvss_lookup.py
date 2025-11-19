# src/baselines/cvss_lookup.py
import pandas as pd
import os

# Path to your CSV
DATASET_PATH = os.path.join(os.path.dirname(__file__), "../../data/cve_dataset.csv")

class CVSSBaseline:
    def __init__(self, csv_path=DATASET_PATH):
        try:
            self.df = pd.read_csv(csv_path)
            # Ensure ID column is string and stripped
            self.df['id'] = self.df['id'].astype(str).str.strip()
        except FileNotFoundError:
            print(f"Error: Dataset not found at {csv_path}")
            self.df = pd.DataFrame()

    def get_vulnerability_details(self, cve_id: str):
        """
        Simulates a traditional database lookup for a CVE.
        Returns the Ground Truth data.
        """
        cve_id = cve_id.strip().upper()
        row = self.df[self.df['id'] == cve_id]
        
        if row.empty:
            return None
        
        data = row.iloc[0]
        return {
            "cve_id": data['id'],
            "description": data['description'],
            "cvss_score": data.get('score', 'N/A'),
            "severity": data.get('severity', 'N/A'),
            "published": data.get('published', 'N/A')
        }

if __name__ == "__main__":
    # Test run
    baseline = CVSSBaseline()
    print(baseline.get_vulnerability_details("CVE-2014-3566"))