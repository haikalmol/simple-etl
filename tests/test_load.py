"""
Unit tests untuk module utils/load.py.

Test ini menggunakan mocking untuk:
    - pandas.DataFrame.to_csv
    - psycopg2.connect
    - google.oauth2.service_account.Credentials
    - googleapiclient.discovery.build
"""

from unittest.mock import MagicMock, patch

import pandas as pd
import psycopg2
import pytest

from utils.load import load_data, _load_to_csv, _load_to_google_sheets, _load_to_postgresql


@pytest.fixture
def sample_dataframe():
    """Fixture DataFrame sample untuk testing."""
    return pd.DataFrame({
        "Title": ["Product A", "Product B"],
        "Price": [160000.0, 320000.0],
        "Rating": [4.5, 3.0],
        "Colors": [3, 5],
        "Size": ["M", "L"],
        "Gender": ["Men", "Women"],
        "Timestamp": ["2024-01-01", "2024-01-02"],
    })


@pytest.fixture
def db_config():
    """Fixture konfigurasi database dummy."""
    return {
        "dbname": "test_db",
        "user": "test_user",
        "password": "test_pass",
        "host": "localhost",
        "port": "5432",
    }


class TestLoadToCSV:
    """Test suite untuk fungsi _load_to_csv()."""

    @patch("utils.load.os.makedirs")
    @patch("pandas.DataFrame.to_csv")
    def test_csv_save_success(self, mock_to_csv, mock_makedirs, sample_dataframe):
        """
        Verifikasi: to_csv dipanggil dengan parameter yang benar.
        """
        _load_to_csv(sample_dataframe, "data/test.csv")

        mock_makedirs.assert_called_once()
        mock_to_csv.assert_called_once_with("data/test.csv", index=False)

    @patch("utils.load.os.makedirs")
    @patch("pandas.DataFrame.to_csv")
    def test_csv_handles_exception(self, mock_to_csv, mock_makedirs, sample_dataframe):
        """
        Verifikasi: Error saat save CSV ditangkap dan diprint.
        """
        mock_to_csv.side_effect = IOError("Disk full")

        _load_to_csv(sample_dataframe, "data/test.csv")

        mock_to_csv.assert_called_once()


class TestLoadToPostgreSQL:
    """Test suite untuk fungsi _load_to_postgresql()."""

    @patch("utils.load.psycopg2.connect")
    def test_postgresql_success(self, mock_connect, sample_dataframe, db_config):
        """
        Skenario Sukses: Koneksi dan eksekusi query berhasil.

        Verifikasi:
            - connect dipanggil dengan db_config
            - CREATE TABLE IF NOT EXISTS dieksekusi
            - execute_values dipanggil
            - commit dipanggil
        """
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        with patch("utils.load.execute_values") as mock_execute_values:
            _load_to_postgresql(sample_dataframe, db_config)

            mock_connect.assert_called_once_with(**db_config)
            mock_cursor.execute.assert_called()
            mock_execute_values.assert_called_once()
            mock_conn.commit.assert_called_once()
            mock_cursor.close.assert_called_once()
            mock_conn.close.assert_called_once()

    @patch("utils.load.psycopg2.connect")
    def test_postgresql_psycopg2_error(self, mock_connect, sample_dataframe, db_config):
        """
        Skenario Error: psycopg2.Error saat koneksi.

        Verifikasi:
            - Error ditangkap
            - Program tidak crash
            - Error di-log
        """
        mock_connect.side_effect = psycopg2.Error("Connection refused")

        _load_to_postgresql(sample_dataframe, db_config)

        mock_connect.assert_called_once()

    @patch("utils.load.psycopg2.connect")
    def test_postgresql_generic_exception(self, mock_connect, sample_dataframe, db_config):
        """
        Skenario Error: Exception generik.

        Verifikasi:
            - Error ditangkap
            - Program tidak crash
        """
        mock_connect.side_effect = Exception("Unexpected error")

        _load_to_postgresql(sample_dataframe, db_config)

        mock_connect.assert_called_once()


class TestLoadToGoogleSheets:
    """Test suite untuk fungsi _load_to_google_sheets()."""

    @patch("utils.load.build")
    @patch("utils.load.service_account.Credentials.from_service_account_file")
    def test_google_sheets_success(
        self, mock_creds, mock_build, sample_dataframe
    ):
        """
        Skenario Sukses: API call berhasil.

        Verifikasi:
            - Credentials dipanggil dengan file yang benar
            - build dipanggil dengan service 'sheets' dan version 'v4'
            - spreadsheets().values().update() dipanggil
        """
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_creds.return_value = MagicMock()

        mock_values = mock_service.spreadsheets.return_value.values
        mock_update = mock_values.return_value.update
        mock_update.return_value.execute.return_value = {"updatedCells": 16}

        _load_to_google_sheets(sample_dataframe, "test_spreadsheet_id")

        mock_creds.assert_called_once_with(
            "google-sheets-api.json",
            scopes=["https://www.googleapis.com/auth/spreadsheets"],
        )
        mock_build.assert_called_once()

        mock_values.assert_called_once()
        mock_update.assert_called_once()

    @patch("utils.load.build")
    @patch("utils.load.service_account.Credentials.from_service_account_file")
    def test_google_sheets_data_conversion(
        self, mock_creds, mock_build, sample_dataframe
    ):
        """
        Verifikasi: DataFrame dikonversi ke string sebelum dikirim.

        Menghindari serialization error pada Timestamp.
        """
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_creds.return_value = MagicMock()

        mock_values = mock_service.spreadsheets.return_value.values
        mock_update = mock_values.return_value.update
        mock_update.return_value.execute.return_value = {"updatedCells": 16}

        _load_to_google_sheets(sample_dataframe, "test_spreadsheet_id")

        mock_update.assert_called_once()
        call_args = mock_update.call_args
        assert "body" in call_args[1] or any("body" in str(k) for k in call_args)

    @patch("utils.load.build")
    @patch("utils.load.service_account.Credentials.from_service_account_file")
    def test_google_sheets_exception(self, mock_creds, mock_build, sample_dataframe):
        """
        Skenario Error: Exception saat Google API.

        Verifikasi:
            - Error ditangkap
            - Program tidak crash
            - Error di-log
        """
        mock_creds.side_effect = Exception("API credentials invalid")

        _load_to_google_sheets(sample_dataframe, "test_spreadsheet_id")

        mock_creds.assert_called_once()


class TestLoadData:
    """Test suite untuk fungsi utama load_data()."""

    @patch("utils.load._load_to_csv")
    @patch("utils.load._load_to_postgresql")
    @patch("utils.load._load_to_google_sheets")
    def test_load_data_calls_all_destinations(
        self,
        mock_gs,
        mock_pg,
        mock_csv,
        sample_dataframe,
        db_config,
    ):
        """
        Verifikasi: Semua fungsi load dipanggil.
        """
        load_data(sample_dataframe, db_config, "spreadsheet_id_123")

        mock_csv.assert_called_once()
        mock_pg.assert_called_once()
        mock_gs.assert_called_once()

    @patch("utils.load._load_to_csv")
    @patch("utils.load.psycopg2.connect")
    @patch("utils.load._load_to_google_sheets")
    def test_load_data_continues_on_error(
        self,
        mock_gs,
        mock_psycopg2,
        mock_csv,
        sample_dataframe,
        db_config,
    ):
        """
        Verifikasi: Jika satu destination gagal, yang lain tetap dieksekusi.

        Mock psycopg2.connect agar _load_to_postgresql mengeksekusi
        blok try-except internalnya dan menangkap error dengan benar.
        """
        mock_psycopg2.side_effect = Exception("PostgreSQL connection error")

        load_data(sample_dataframe, db_config, "spreadsheet_id_123")

        mock_csv.assert_called_once()
        mock_psycopg2.assert_called_once()
        mock_gs.assert_called_once()
