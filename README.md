# Handle URL Updater

This script updates the `URL` type entries in a MySQL `handles` table based on data provided in a CSV file.

## Prerequisites

*   Python 3.x
*   Required Python packages:
    *   `mysql-connector-python`
    *   `python-dotenv`
*   Access to a MySQL database with a `handles` table.

Install required packages using pip:
```bash
pip install mysql-connector-python python-dotenv
```

```bash
python main.py path/to/your/data.csv
```

## Configuration

1. Create a file named `.env` in the same directory as the script (`main.py`).
2. Add your database connection details to the `.env` file:
   ```bash
   DB_HOST=your_database_host
   DB_USER=your_database_user
   DB_PASSWORD=your_database_password
   DB_NAME=your_database_name
    ```
    Replace the placeholder values with your actual database credentials.

## CSV File Format

The input CSV file must have exactly two columns:

1. Column 1: The new URL to be set in the data field.
2. Column 2: The handle identifier (e.g., `1961/prefix:suffix` or `http://hdl.handle.net/1961/prefix:suffix`). The script will automatically strip the `http(s)://hdl.handle.net/` prefix if present.

Example CSV (`data.csv`):
```csv
https://new.example.com/item1,http://hdl.handle.net/1961/item:1
https://new.example.com/item2,1961/item:2
```

## Usage

Run the script from the command line, providing the path to your CSV file as an argument:
```bash
python main.py path/to/your/data.csv
```
Replace `path/to/your/data.csv` with the actual path to your input CSV file.

## Logging

* The script prints progress messages to the console (`stdout`).
* Errors (e.g., invalid CSV rows, database connection issues, handles not found) are logged to a timestamped file in the `log/` directory (e.g., `log/errors-YYYY-MM-DD-HHMMSS.log`).
* Warnings for handles not found in the database are also printed to `stderr`.