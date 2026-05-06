"""
Module untuk ekstraksi data melalui web scraping.

Module ini menyediakan fungsi untuk mengekstrak data produk fashion
 dari website fashion-studio.dicoding.dev menggunakan requests dan BeautifulSoup4.
"""

import time
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup


def extract_data(
    base_url: str = "https://fashion-studio.dicoding.dev",
    max_pages: int = 50,
    target_rows: int = 1000,
    delay: float = 1.0,
) -> pd.DataFrame:
    """
    Melakukan ekstraksi data produk fashion dari website target.

    Fungsi ini melakukan iterasi scraping pada halaman 1 hingga max_pages
    dengan format URL pagination yang akurat, mengekstrak atribut produk
    (Title, Price, Rating, Colors, Size, Gender), dan mengembalikan DataFrame
    dengan kolom Timestamp.

    Format URL:
        - Halaman 1: https://fashion-studio.dicoding.dev/
        - Halaman > 1: https://fashion-studio.dicoding.dev/page{page_num}

    Args:
        base_url: URL dasar website target.
        max_pages: Jumlah maksimum halaman yang akan discrape.
        target_rows: Jumlah target baris data yang ingin dikumpulkan.
        delay: Jeda waktu dalam detik antar request (polite scraping).

    Returns:
        pd.DataFrame: DataFrame berisi data produk dengan kolom:
            - Title: Nama produk
            - Price: Harga produk
            - Rating: Rating produk
            - Colors: Warna tersedia
            - Size: Ukuran tersedia
            - Gender: Kategori gender
            - Timestamp: Waktu ekstraksi data

    Raises:
        Tidak melakukan raise exception; error ditangani secara internal
        dengan logging ke console dan melanjutkan ke halaman berikutnya.
    """
    all_products = []
    session = requests.Session()

    for page_num in range(1, max_pages + 1):
        if len(all_products) >= target_rows:
            break

        try:
            if page_num == 1:
                url = f"{base_url}/"
            else:
                url = f"{base_url}/page{page_num}"

            response = session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            products = _parse_products(soup)

            for product in products:
                if len(all_products) >= target_rows:
                    break

                product["Timestamp"] = datetime.now()
                all_products.append(product)

            print(f"[INFO] Halaman {page_num}: Berhasil mengekstrak {len(products)} produk")

        except requests.exceptions.RequestException as e:
            print(f"[WARNING] Halaman {page_num}: Gagal memuat - {str(e)}")
            continue
        except Exception as e:
            print(f"[WARNING] Halaman {page_num}: Error parsing - {str(e)}")
            continue

        if page_num < max_pages:
            time.sleep(delay)

    df = pd.DataFrame(all_products)

    if len(df) < target_rows:
        print(f"[WARNING] Hanya berhasil mengumpulkan {len(df)} dari {target_rows} target baris")
    else:
        print(f"[INFO] Berhasil mengumpulkan {len(df)} baris data")

    return df


def _parse_products(soup: BeautifulSoup) -> list[dict]:
    """
    Parse produk dari BeautifulSoup object berdasarkan struktur DOM website.

    Struktur DOM:
        - Container: div dengan class="collection-card"
        - Title: h3 dengan class="product-title"
        - Price: div dengan class="price-container"
        - Rating/Colors/Size/Gender: dari tag <p> tanpa class (inline style)

    Args:
        soup: BeautifulSoup object yang berisi HTML halaman.

    Returns:
        list[dict]: List berisi dictionary data produk.
    """
    products = []

    product_cards = soup.select("div.collection-card")

    for card in product_cards:
        try:
            title = _get_text_from_element(card, "h3.product-title")

            price_elem = card.select_one("div.price-container")
            price = price_elem.get_text(strip=True) if price_elem else ""

            rating, colors, size, gender = _extract_paragraph_attrs(card)

            product = {
                "Title": title,
                "Price": price,
                "Rating": rating,
                "Colors": colors,
                "Size": size,
                "Gender": gender,
            }
            products.append(product)
        except Exception:
            continue

    return products


def _get_text_from_element(element: BeautifulSoup, selector: str) -> str:
    """
    Ekstrak teks dari element menggunakan CSS selector tunggal.

    Args:
        element: BeautifulSoup element induk.
        selector: CSS selector.

    Returns:
        str: Teks yang diekstrak atau string kosong jika tidak ditemukan.
    """
    found = element.select_one(selector)
    return found.get_text(strip=True) if found else ""


def _extract_paragraph_attrs(card: BeautifulSoup) -> tuple[str, str, str, str]:
    """
    Ekstrak atribut Rating, Colors, Size, Gender dari tag <p> di dalam card.

    Tag <p> tidak memiliki class, hanya inline style. Format teks:
        - "Rating: X": ambil angka X
        - "Colors: Y": ambil angka Y
        - "Size: Z": ambil nilai Z (contoh: 'M', 'L')
        - "Gender: W": ambil nilai W

    Args:
        card: BeautifulSoup element card produk.

    Returns:
        tuple[str, str, str, str]: (Rating, Colors, Size, Gender)
    """
    rating = ""
    colors = ""
    size = ""
    gender = ""

    paragraphs = card.find_all("p")
    for p in paragraphs:
        text = p.get_text(strip=True)

        if "Rating:" in text:
            parts = text.split(":")
            if len(parts) > 1:
                rating = parts[1].strip()
        elif "Colors" in text:
            parts = text.split(":")
            if len(parts) > 1:
                colors = parts[1].strip()
        elif "Size:" in text:
            parts = text.split(":")
            if len(parts) > 1:
                size = parts[1].strip()
        elif "Gender:" in text:
            parts = text.split(":")
            if len(parts) > 1:
                gender = parts[1].strip()

    return rating, colors, size, gender
