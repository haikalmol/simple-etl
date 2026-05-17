# 🛒 ETL Pipeline: Fashion Studio Competitor Analysis

A modular Data Engineering project to extract, transform, and load (ETL) competitor product catalog data. This repository is an **Advanced** submission for the "Fundamentals of Data Processing" course at Dicoding.

## 📌 Key Features (Advanced Rubric)

1. **Extract (`utils/extract.py`)**
   - Performs automated web scraping of the catalog at `https://fashion-studio.dicoding.dev` (Pages 1–50, target ~1000 records).
   - Collects attributes: Title, Price, Rating, Colors, Size, Gender.
   - Adds a `timestamp` column with the precise time of extraction.
   - Includes error handling (`try-except`) to catch network failures (e.g., `RequestException`).

2. **Transform (`utils/transform.py`)**
   - Rigorous cleaning: removes duplicate rows, drops null rows (`dropna`), and filters invalid entries (e.g., "Unknown Product").
   - Conversion and standardization:
     - Converts `Price` to IDR using an assumed exchange rate of IDR 16,000.
     - Standardizes `Rating` as `float`, and extracts numeric values from `Colors`.
     - Parses and normalizes `Size` and `Gender` fields.
   - Uses explicit `try-except` blocks during type casting to handle potential `ValueError` or `TypeError`.

3. **Load (`utils/load.py`)**
   - Loads cleaned data concurrently to three data sinks:
     1. **Flat file**: local `products.csv`.
     2. **Relational database**: PostgreSQL.
     3. **Cloud spreadsheet**: Google Sheets via the API.
   - Implements error handling for database connection failures and API limits.

4. **Unit Testing & Coverage**
   - Tested with `pytest` and uses mocking to isolate HTTP requests and database connections.
   - Achieves **~91% test coverage** (Advanced requirement: 80–100%).

---

## 📂 Repository Structure

The project follows a modular layout for easier maintenance and testing:

```text
simple-etl/
├── tests/
│   ├── test_extract.py
   ├── test_transform.py
   └── test_load.py
├── utils/
│   ├── extract.py
│   ├── transform.py
│   └── load.py
├── main.py
├── requirements.txt
├── submission.txt
├── products.csv
├── google-sheets-api.json
└── README.md
```

⚙️ Prerequisites
Ensure your system has:

- Python 3.9+
- PostgreSQL (local or remote)
- Google Service Account credentials (`google-sheets-api.json`)

Install dependencies:

```bash
pip install -r requirements.txt
```

🚀 How to Run

1. Run the ETL orchestrator:

```bash
python main.py
```

2. Run unit tests:

```bash
python -m pytest tests/
```

3. Check test coverage:

```bash
coverage run -m pytest tests/
coverage report -m
```

📊 Google Sheets (result)

The final pipeline output is available live in the Google Sheet:
https://docs.google.com/spreadsheets/d/1nOMgE4U1KVB4tZqxR6oRCkQ5zZKfTs8RBI1zioNrwvU/edit?usp=sharing

✒️ Author

Haikal Fairuzi Maulana

Created to satisfy the "Build an ETL Pipeline" submission requirements — Dicoding Academy (2026).
