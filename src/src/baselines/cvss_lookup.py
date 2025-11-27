import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.abspath(os.path.join(BASE_DIR, "../../../data/cve_dataset.csv"))

class CVSSBaseline:
    def __init__(self, csv_path=DATASET_PATH):
        # Debugging: Cek apakah file benar-benar ada
        if not os.path.exists(csv_path):
            print(f"\n❌ CRITICAL ERROR: Dataset TIDAK ditemukan di:")
            print(f"   {csv_path}")
            print(f"   (Script berjalan di: {BASE_DIR})\n")
            # Buat DataFrame kosong agar tidak langsung crash, tapi akan error nanti jika dipanggil
            self.df = pd.DataFrame()
            return

        try:
            self.df = pd.read_csv(csv_path)
            # Bersihkan kolom ID
            if 'id' in self.df.columns:
                self.df['id'] = self.df['id'].astype(str).str.strip()
            else:
                print(f"❌ Error: Kolom 'id' tidak ditemukan. Kolom yang ada: {list(self.df.columns)}")
        except Exception as e:
            print(f"❌ Error saat membaca CSV: {e}")
            self.df = pd.DataFrame()

    def get_vulnerability_details(self, cve_id: str):
        # Jika DF kosong (gagal load), langsung return None
        if self.df.empty:
            return None

        cve_id = cve_id.strip().upper()
        
        # Pastikan kolom id ada
        if 'id' not in self.df.columns:
            return None

        row = self.df[self.df['id'] == cve_id]
        
        if row.empty:
            return None
        
        data = row.iloc[0]
        return {
            "cve_id": data['id'],
            "description": data.get('description', 'N/A'),
            "cvss_score": data.get('score', 'N/A'),
            "severity": data.get('severity', 'N/A'),
            "published": data.get('published', 'N/A')
        }

if __name__ == "__main__":
    # Test kecil untuk memastikan path benar
    baseline = CVSSBaseline()
    print("Test Lookup:", baseline.get_vulnerability_details("CVE-2014-3566"))