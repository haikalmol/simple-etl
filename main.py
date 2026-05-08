import os
import pandas as pd
from utils.extract import extract_data
from utils.transform import transform_data
from utils.load import load_data # Import fungsi baru

def main():
    print("=== Memulai Pipeline ETL ===")
    raw_path = 'data/raw_fashion_data.csv'
    df_raw = None
    
    # --- FASE 2: EXTRACTION ---
    print("\n[1/3] Mengecek status data mentah (Raw Data)...")
    if os.path.exists(raw_path):
        print(f"✅ File {raw_path} ditemukan! Membaca dari lokal...")
        df_raw = pd.read_csv(raw_path)
    else:
        print("⚠️ File raw data belum ada. Memulai Ekstraksi...")
        df_raw = extract_data()
        if df_raw is not None and not df_raw.empty:
            os.makedirs('data', exist_ok=True)
            df_raw.to_csv(raw_path, index=False)
        else:
            print("❌ Gagal mengekstrak data.")
            return

    # --- FASE 3: TRANSFORMATION ---
    if df_raw is not None and not df_raw.empty:
        print("\n[2/3] Menjalankan Transformasi Data...")
        df_cleaned = transform_data(df_raw)
        
        if df_cleaned is not None and not df_cleaned.empty:
            print(f"✅ Transformasi Selesai: {len(df_cleaned)} baris siap pakai.")
            
            # --- FASE 4: LOADING ---
            print("\n[3/3] Menjalankan Proses Load Data...")
            
            # TODO: ISI DENGAN KREDENSIAL ASLI ANDA
            DB_CONFIG = {
                'dbname': 'postgres',
                # USERNAME HARUS DITAMBAH TITIK DAN ID PROYEK ANDA
                'user': 'postgres.vufkyvieqxcnwsowlfbw', 
                'password': 'yf4GL9Wre5shKJhM',
                'host': 'aws-1-ap-south-1.pooler.supabase.com',
                # PORT HARUS 6543 JIKA MENGGUNAKAN POOLER
                'port': '6543' 
            }
            
            # TODO: ISI DENGAN ID GOOGLE SHEET ANDA
            # Contoh URL: https://docs.google.com/spreadsheets/d/1BxiMVs0X_xyz_xyz/edit
            # Maka ID-nya adalah: 1BxiMVs0X_xyz_xyz
            SPREADSHEET_ID = '1nOMgE4U1KVB4tZqxR6oRCkQ5zZKfTs8RBI1zioNrwvU'
            
            load_data(df_cleaned, DB_CONFIG, SPREADSHEET_ID)
            print("\n=== Pipeline ETL Selesai ===")
            
        else:
            print("❌ Gagal melakukan transformasi.")

if __name__ == "__main__":
    main()