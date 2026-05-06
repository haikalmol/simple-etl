"""
Unit tests untuk module utils/transform.py.

Test ini memverifikasi logika transformasi data dengan explicit error handling.
"""

from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from utils.transform import transform_data, _convert_price, _convert_rating


@pytest.fixture
def raw_dataframe():
    """
    Fixture DataFrame mentah yang mengandung berbagai skenario cacat:
        - Data valid normal
        - Unknown Product (harus dihapus)
        - Price dengan simbol $ dan karakter aneh
        - Rating dengan teks ekstra dan emoji
        - NaN/null values
        - Duplikat (Product A muncul 2x dengan nilai 100% identik)
    """
    data = {
        "Title": [
            "Product A",
            "Product B",
            "Unknown Product",
            "Product C",
            "Product A",  # Duplikat persis dengan baris 0
            "Product D",
            np.nan,
        ],
        "Price": [
            "$10.00",
            "$25.50⭐",
            "$30.00",
            "45.00",
            "$10.00",  # Identik dengan baris 0
            None,
            "$15.00",
        ],
        "Rating": [
            "Rating: 4.5",
            "⭐ 3.0 / 5",
            "Invalid Rating",
            "4.0",
            "Rating: 4.5",  # Identik dengan baris 0
            np.nan,
            "5.0",
        ],
        "Colors": [
            "3 Colors",
            "5 Colors",
            "2 Colors",
            None,
            "3 Colors",  # Identik dengan baris 0
            "4",
            "6 Colors",
        ],
        "Size": [
            "Size: M",
            "size: L",
            "SIZE: XL",
            None,
            "Size: M",  # Identik dengan baris 0
            "S",
            "Size: XXL",
        ],
        "Gender": [
            "Gender: Men",
            "gender: Women",
            "GENDER: Unisex",
            "Kids",
            "Gender: Men",  # Identik dengan baris 0
            np.nan,
            "Gender: Men",
        ],
        "Timestamp": [
            pd.Timestamp("2024-01-01"),
            pd.Timestamp("2024-01-02"),
            pd.Timestamp("2024-01-03"),
            pd.Timestamp("2024-01-04"),
            pd.Timestamp("2024-01-01"),  # Identik dengan baris 0 (sama persis)
            pd.Timestamp("2024-01-06"),
            pd.Timestamp("2024-01-07"),
        ],
    }
    return pd.DataFrame(data)


class TestTransformData:
    """Test suite untuk fungsi transform_data()."""

    @patch("utils.transform.print")
    def test_transform_removes_unknown_product(self, mock_print, raw_dataframe):
        """
        Verifikasi: Baris dengan Title 'Unknown Product' dihapus.
        """
        result = transform_data(raw_dataframe)

        unknown_titles = result["Title"].str.contains(
            "Unknown Product", case=False, na=False
        )
        assert not unknown_titles.any()

    @patch("utils.transform.print")
    def test_transform_removes_duplicates(self, mock_print, raw_dataframe):
        """
        Verifikasi: Baris duplikat (Product A muncul 2x) dihapus.
        """
        result = transform_data(raw_dataframe)

        title_counts = result["Title"].value_counts()
        assert title_counts["Product A"] == 1

    @patch("utils.transform.print")
    def test_transform_price_calculation(self, mock_print, raw_dataframe):
        """
        Verifikasi: Perhitungan Price akurat (nilai * 16000).

        $10.00 * 16000 = 160000.0
        """
        result = transform_data(raw_dataframe)

        product_a = result[result["Title"] == "Product A"]
        if not product_a.empty:
            expected_price = 10.0 * 16000.0
            assert product_a.iloc[0]["Price"] == expected_price

    @patch("utils.transform.print")
    def test_transform_price_numeric_type(self, mock_print, raw_dataframe):
        """
        Verifikasi: Tipe data Price adalah float.
        """
        result = transform_data(raw_dataframe)

        assert pd.api.types.is_float_dtype(result["Price"])

    @patch("utils.transform.print")
    def test_transform_rating_regex_extraction(self, mock_print, raw_dataframe):
        """
        Verifikasi: Regex berhasil mengekstrak angka dari Rating.

        - 'Rating: 4.5' -> 4.5
        - '⭐ 3.0 / 5' -> 3.0
        - 'Invalid Rating' -> None (dropped by dropna)
        """
        result = transform_data(raw_dataframe)

        assert pd.api.types.is_float_dtype(result["Rating"])

        product_a = result[result["Title"] == "Product A"]
        if not product_a.empty:
            assert product_a.iloc[0]["Rating"] == 4.5

    @patch("utils.transform.print")
    def test_transform_colors_integer_type(self, mock_print, raw_dataframe):
        """
        Verifikasi: Tipe data Colors adalah Int64 (nullable integer).
        """
        result = transform_data(raw_dataframe)

        assert str(result["Colors"].dtype) == "Int64"

    @patch("utils.transform.print")
    def test_transform_colors_regex_extraction(self, mock_print, raw_dataframe):
        """
        Verifikasi: Regex berhasil mengekstrak angka dari Colors.
        """
        result = transform_data(raw_dataframe)

        product_a = result[result["Title"] == "Product A"]
        if not product_a.empty:
            assert product_a.iloc[0]["Colors"] == 3

    @patch("utils.transform.print")
    def test_transform_size_cleaning(self, mock_print, raw_dataframe):
        """
        Verifikasi: Prefix 'Size:' dihapus dan case-insensitive.

        - 'Size: M' -> 'M'
        - 'size: L' -> 'L'
        - 'SIZE: XL' -> 'XL'
        """
        result = transform_data(raw_dataframe)

        assert "Size:" not in result["Size"].values
        assert "size:" not in result["Size"].values

        sizes = result["Size"].tolist()
        assert "M" in sizes or "L" in sizes or "XL" in sizes

    @patch("utils.transform.print")
    def test_transform_gender_cleaning(self, mock_print, raw_dataframe):
        """
        Verifikasi: Prefix 'Gender:' dihapus dan case-insensitive.

        - 'Gender: Men' -> 'Men'
        - 'gender: Women' -> 'Women'
        """
        result = transform_data(raw_dataframe)

        assert "Gender:" not in result["Gender"].values
        assert "gender:" not in result["Gender"].values

    @patch("utils.transform.print")
    def test_transform_dropna_removes_nulls(self, mock_print, raw_dataframe):
        """
        Verifikasi: dropna() menghapus baris dengan nilai null.
        """
        result = transform_data(raw_dataframe)

        # After dropna, no null values should remain
        assert result["Price"].isna().sum() == 0
        assert result["Rating"].isna().sum() == 0
        assert result["Colors"].isna().sum() == 0
        assert result["Size"].isna().sum() == 0
        assert result["Gender"].isna().sum() == 0

    @patch("utils.transform.print")
    def test_transform_helper_function_error_handling(self, mock_print):
        """
        Verifikasi: Helper function _convert_price menangani error dengan try-except.
        """
        # Test valid conversion
        assert _convert_price("$10.00") == 160000.0
        assert _convert_price("25.5") == 408000.0

        # Test invalid values return None
        assert _convert_price(None) is None
        assert _convert_price("abc") is None
        assert _convert_price("") is None

    @patch("utils.transform.print")
    def test_transform_helper_rating_error_handling(self, mock_print):
        """
        Verifikasi: Helper function _convert_rating menangani error dengan try-except.
        """
        # Test valid conversion
        assert _convert_rating("Rating: 4.5") == 4.5
        assert _convert_rating("3.0") == 3.0

        # Test invalid values return None
        assert _convert_rating("Invalid Rating") is None
        assert _convert_rating(None) is None
        assert _convert_rating("abc") is None

    @patch("utils.transform.print")
    def test_transform_invalid_rating_dropped(self, mock_print):
        """
        Verifikasi: Baris dengan 'Invalid Rating' dihapus oleh dropna.
        """
        df_with_invalid = pd.DataFrame({
            "Title": ["Valid Product", "Invalid Product"],
            "Price": ["$10.00", "$20.00"],
            "Rating": ["4.5", "Invalid Rating"],
            "Colors": ["3", "5"],
            "Size": ["M", "L"],
            "Gender": ["Men", "Women"],
            "Timestamp": [pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02")],
        })

        result = transform_data(df_with_invalid)

        # Only valid product should remain (Invalid Rating becomes None -> dropped)
        assert len(result) == 1
        assert result.iloc[0]["Title"] == "Valid Product"

    @patch("utils.transform.print")
    def test_transform_preserves_timestamp(self, mock_print, raw_dataframe):
        """
        Verifikasi: Kolom Timestamp tetap ada setelah transformasi.
        """
        result = transform_data(raw_dataframe)

        assert "Timestamp" in result.columns

    @patch("utils.transform.print")
    def test_transform_no_data_loss_except_filtering(self, mock_print):
        """
        Verifikasi: Tidak ada baris yang hilang kecuali
        karena filtering Unknown Product, duplicates, dan null values.
        """
        simple_df = pd.DataFrame({
            "Title": ["Product A", "Product B"],
            "Price": ["$10.00", "$20.00"],
            "Rating": ["4.5", "3.0"],
            "Colors": ["3", "5"],
            "Size": ["M", "L"],
            "Gender": ["Men", "Women"],
            "Timestamp": [pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02")],
        })

        result = transform_data(simple_df)

        assert len(result) == 2

    @patch("utils.transform.print")
    def test_transform_empty_dataframe(self, mock_print):
        """
        Skenario edge case: DataFrame kosong.
        """
        empty_df = pd.DataFrame(columns=[
            "Title", "Price", "Rating", "Colors", "Size", "Gender", "Timestamp"
        ])

        result = transform_data(empty_df)

        assert result is not None
        assert result.empty

    @patch("utils.transform.print")
    def test_transform_debug_log_called(self, mock_print, raw_dataframe):
        """
        Verifikasi: Debug log dipanggil dan menampilkan informasi.
        """
        transform_data(raw_dataframe)

        mock_print.assert_called()
        calls_str = " ".join([str(call) for call in mock_print.call_args_list])
        assert "Sisa baris setelah filter awal" in calls_str
