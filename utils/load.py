"""
Module untuk memuat (load) data bersih ke berbagai destinasi penyimpanan.

Module ini menyediakan fungsi untuk:
    1. Menyimpan data ke flat file (CSV)
    2. Memuat data ke PostgreSQL database
    3. Memuat data ke Google Sheets
"""

import os
from typing import Any

import pandas as pd
import psycopg2
from google.oauth2 import service_account
from googleapiclient.discovery import build
from psycopg2.extras import execute_values


def load_data(
    df: pd.DataFrame,
    db_config: dict[str, Any],
    spreadsheet_id: str,
    csv_path: str = "data/products.csv",
) -> None:
    """
    Memuat DataFrame ke tiga destinasi: CSV, PostgreSQL, dan Google Sheets.

    Args:
        df: DataFrame bersih yang akan dimuat.
        db_config: Dictionary konfigurasi koneksi PostgreSQL.
        spreadsheet_id: ID Google Sheet target.
        csv_path: Path untuk menyimpan file CSV (default: data/products.csv).
    """
    _load_to_csv(df, csv_path)
    _load_to_postgresql(df, db_config)
    _load_to_google_sheets(df, spreadsheet_id)


def _load_to_csv(df: pd.DataFrame, csv_path: str) -> None:
    """
    Menyimpan DataFrame ke file CSV.

    Args:
        df: DataFrame yang akan disimpan.
        csv_path: Path file CSV target.
    """
    try:
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        df.to_csv(csv_path, index=False)
        print(f"[INFO] Data berhasil disimpan ke CSV: {csv_path}")
    except Exception as e:
        print(f"[WARNING] Gagal menyimpan ke CSV: {str(e)}")


def _load_to_postgresql(df: pd.DataFrame, db_config: dict[str, Any]) -> None:
    """
    Memuat DataFrame ke PostgreSQL database.

    Membuat tabel fashion_products jika belum ada dan melakukan
    batch insert menggunakan execute_values.

    Args:
        df: DataFrame yang akan dimuat.
        db_config: Dictionary konfigurasi koneksi PostgreSQL.
    """
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS fashion_products (
            id SERIAL PRIMARY KEY,
            Title VARCHAR(255),
            Price FLOAT,
            Rating FLOAT,
            Colors INT,
            Size VARCHAR(50),
            Gender VARCHAR(50),
            Timestamp TIMESTAMP
        );
        """
        cursor.execute(create_table_sql)

        columns = list(df.columns)
        values = df.values.tolist()

        insert_sql = f"""
        INSERT INTO fashion_products ({', '.join(columns)})
        VALUES %s
        """
        execute_values(cursor, insert_sql, values)

        conn.commit()
        cursor.close()
        conn.close()

        print(f"[INFO] Data berhasil dimuat ke PostgreSQL: {len(df)} baris")

    except psycopg2.Error as e:
        print(f"[WARNING] Error PostgreSQL: {str(e)}")
    except Exception as e:
        print(f"[WARNING] Gagal memuat ke PostgreSQL: {str(e)}")


def _load_to_google_sheets(df: pd.DataFrame, spreadsheet_id: str) -> None:
    """
    Memuat DataFrame ke Google Sheets.

    Menggunakan Google Sheets API untuk menimpa data di sheet target.
    Semua nilai dikonversi ke string untuk menghindari serialization error.

    Args:
        df: DataFrame yang akan dimuat.
        spreadsheet_id: ID Google Sheet target.
    """
    try:
        creds_path = "google-sheets-api.json"
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]

        credentials = service_account.Credentials.from_service_account_file(
            creds_path, scopes=scopes
        )
        service = build("sheets", "v4", credentials=credentials)

        df_str = df.astype(str)
        values = [df_str.columns.tolist()] + df_str.values.tolist()

        body = {"values": values}

        result = (
            service.spreadsheets()
            .values()
            .update(
                spreadsheetId=spreadsheet_id,
                range="Sheet1!A1",
                valueInputOption="RAW",
                body=body,
            )
            .execute()
        )

        updated_cells = result.get("updatedCells", 0)
        print(f"[INFO] Data berhasil dimuat ke Google Sheets: {updated_cells} cells")

    except Exception as e:
        print(f"[WARNING] Gagal memuat ke Google Sheets: {str(e)}")
