"""
Unit tests untuk module utils/extract.py.

Test ini menggunakan mocking untuk:
    - time.sleep (agar testing berjalan instan)
    - requests.get (untuk simulasi HTTP response)
"""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
import requests

from utils.extract import extract_data


@pytest.fixture
def mock_html_content():
    """Fixture HTML dummy untuk 1 produk."""
    return """
    <html>
    <body>
        <div class="collection-card">
            <h3 class="product-title">Test Product</h3>
            <div class="price-container">$10.00</div>
            <p>Rating: 4.5</p>
            <p>3 Colors</p>
            <p>Size: M</p>
            <p>Gender: Men</p>
        </div>
    </body>
    </html>
    """


class TestExtractData:
    """Test suite untuk fungsi extract_data()."""

    @patch("utils.extract.time.sleep")
    @patch("utils.extract.requests.Session")
    def test_extract_success_single_product(
        self, mock_session_class, mock_sleep, mock_html_content
    ):
        """
        Skenario Sukses: Mock response dengan 1 produk valid.

        Verifikasi:
            - DataFrame tidak kosong
            - Kolom yang diharapkan ada
            - Data produk terparse dengan benar
        """
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = mock_html_content
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        df = extract_data(max_pages=1, delay=0)

        assert df is not None
        assert not df.empty
        assert len(df) == 1
        assert "Title" in df.columns
        assert "Price" in df.columns
        assert "Rating" in df.columns
        assert "Colors" in df.columns
        assert "Size" in df.columns
        assert "Gender" in df.columns
        assert "Timestamp" in df.columns
        assert df.iloc[0]["Title"] == "Test Product"
        assert "10.00" in str(df.iloc[0]["Price"])

        mock_sleep.assert_not_called()

    @patch("utils.extract.time.sleep")
    @patch("utils.extract.requests.Session")
    def test_extract_multiple_pages(self, mock_session_class, mock_sleep, mock_html_content):
        """
        Skenario: Multiple pages dengan data di setiap halaman.

        Verifikasi:
            - Data terkumpul dari semua halaman
            - Iterasi berjalan sesuai max_pages
        """
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = mock_html_content
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        df = extract_data(max_pages=3, delay=0)

        assert df is not None
        assert len(df) == 3
        assert mock_session.get.call_count == 3

    @patch("utils.extract.time.sleep")
    @patch("utils.extract.requests.Session")
    def test_extract_handles_request_exception(
        self, mock_session_class, mock_sleep, mock_html_content
    ):
        """
        Skenario Error: Simulasi requests.exceptions.RequestException.

        Verifikasi:
            - Error ditangkap dan tidak crash
            - Loop berlanjut ke halaman berikutnya
            - Program selesai tanpa exception
        """
        mock_session = MagicMock()

        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.text = mock_html_content
        mock_response_success.raise_for_status = MagicMock()

        mock_session.get.side_effect = [
            requests.exceptions.RequestException("Connection timeout"),
            mock_response_success,
            mock_response_success,
        ]
        mock_session_class.return_value = mock_session

        df = extract_data(max_pages=3, delay=0)

        assert df is not None
        assert len(df) == 2

    @patch("utils.extract.time.sleep")
    @patch("utils.extract.requests.Session")
    def test_extract_empty_html(self, mock_session_class, mock_sleep):
        """
        Skenario: HTML tanpa produk (empty result).

        Verifikasi:
            - DataFrame kosong tetap valid
            - Tidak terjadi error parsing
        """
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>No products</body></html>"
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        df = extract_data(max_pages=1, delay=0)

        assert df is not None
        assert df.empty

    @patch("utils.extract.time.sleep")
    @patch("utils.extract.requests.Session")
    def test_extract_non_200_status(self, mock_session_class, mock_sleep, mock_html_content):
        """
        Skenario: Response status bukan 200 (raise_for_status error).

        Verifikasi:
            - Error HTTP ditangkap
            - Program melanjutkan ke halaman berikutnya
        """
        mock_session = MagicMock()

        mock_response_error = MagicMock()
        mock_response_error.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "404 Not Found"
        )

        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.text = mock_html_content
        mock_response_success.raise_for_status = MagicMock()

        mock_session.get.side_effect = [mock_response_error, mock_response_success]
        mock_session_class.return_value = mock_session

        df = extract_data(max_pages=2, delay=0)

        assert df is not None
        assert len(df) == 1

    def test_extract_default_parameters(self):
        """
        Verifikasi default parameter function signature.
        """
        import inspect

        sig = inspect.signature(extract_data)
        params = sig.parameters

        assert params["base_url"].default == "https://fashion-studio.dicoding.dev"
        assert params["max_pages"].default == 50
        assert params["target_rows"].default == 1000
        assert params["delay"].default == 1.0
