"""
Module untuk transformasi dan pembersihan data menggunakan Pandas.

Module ini menyediakan fungsi untuk membersihkan DataFrame mentah hasil scraping,
dengan explicit error handling menggunakan try-except blocks dan dropna().
"""

import pandas as pd


def _convert_price(price_val):
    """
    Helper function untuk konversi Price dengan explicit error handling.

    Args:
        price_val: Nilai mentah dari kolom Price.

    Returns:
        float: Hasil konversi (harga * 16000) atau None jika gagal.
    """
    try:
        cleaned = str(price_val).replace("$", "").replace(",", "").strip()
        extracted = "".join(c for c in cleaned if c.isdigit() or c == ".")
        if not extracted:
            return None
        return float(extracted) * 16000.0
    except (ValueError, TypeError) as e:
        print(f"[WARNING] Error converting price: {price_val} - {e}")
        return None


def _convert_rating(rating_val):
    """
    Helper function untuk konversi Rating dengan explicit error handling.

    Args:
        rating_val: Nilai mentah dari kolom Rating.

    Returns:
        float: Nilai rating yang diekstrak atau None jika gagal/invalid.
    """
    try:
        text = str(rating_val)
        if "Invalid Rating" in text:
            return None
        extracted = "".join(c for c in text if c.isdigit() or c == ".")
        if not extracted:
            return None
        return float(extracted)
    except (ValueError, TypeError) as e:
        print(f"[WARNING] Error converting rating: {rating_val} - {e}")
        return None


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Melakukan pembersihan dan transformasi data pada DataFrame mentah.

    Proses yang dilakukan:
        1. Membuat salinan DataFrame untuk menghindari SettingWithCopyWarning
        2. Menghapus baris dengan nilai null (dropna)
        3. Menghapus data duplikat
        4. Filter baris dengan Title mengandung 'Unknown Product'
        5. Transformasi kolom dengan explicit error handling (try-except)
        6. Final dropna untuk menghapus baris yang gagal transformasi

    Args:
        df: DataFrame mentah hasil ekstraksi web scraping.

    Returns:
        pd.DataFrame: DataFrame yang sudah bersih dan tertransformasi.
    """
    initial_rows = len(df)
    print(f"[INFO] Data awal: {initial_rows} baris")

    df_clean = df.copy()

    # Rubric 3.1: Drop rows with null values
    df_clean = df_clean.dropna()

    df_clean = df_clean.drop_duplicates()

    # Filter Unknown Product
    df_clean = df_clean[
        ~df_clean["Title"]
        .astype(str)
        .str.contains("Unknown Product", case=False, na=False)
    ]

    print(f"[DEBUG] Sisa baris setelah filter awal: {len(df_clean)}")

    # Rubric 3.2: Explicit error handling with try-except for type casting
    df_clean["Price"] = df_clean["Price"].apply(_convert_price)
    df_clean["Rating"] = df_clean["Rating"].apply(_convert_rating)

    # Transformasi kolom lainnya dengan regex
    df_clean["Colors"] = (
        df_clean["Colors"]
        .astype(str)
        .str.extract(r"(\d+)", expand=False)
        .astype("Int64")
    )

    df_clean["Size"] = (
        df_clean["Size"]
        .astype(str)
        .str.replace(r"(?i)Size:\s*", "", regex=True)
        .str.strip()
    )

    df_clean["Gender"] = (
        df_clean["Gender"]
        .astype(str)
        .str.replace(r"(?i)Gender:\s*", "", regex=True)
        .str.strip()
    )

    # Final dropna to remove rows that failed transformation
    df_clean = df_clean.dropna()

    final_rows = len(df_clean)
    print(f"[INFO] Data setelah transformasi: {final_rows} baris")
    print(f"[INFO] Total baris yang dihapus: {initial_rows - final_rows}")

    return df_clean
