"""Update URL for handles in the database from a CSV file."""

import csv
from datetime import datetime
import logging
import os
import sys
from dotenv import load_dotenv
import mysql.connector

load_dotenv()  # Load environment variables from .env file

# Database connection details (replace with your actual credentials)
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'username')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_NAME = os.getenv('DB_NAME', 'your_database_name')

# Logging setup
LOG_FILE = 'errors-' + datetime.now().strftime('%Y-%m-%d-%H%M%S') + '.log'
logging.basicConfig(
    filename='log/' + LOG_FILE,
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a'  # Append to the log file
)


def update_handle_url(csv_filepath):
    """
    Reads a CSV file and updates the 'data' column in the 'handles' table
    for matching handles where type is 'URL'.

    Args:
        csv_filepath (str): The path to the two-column CSV file.
                              Column 1: New URL (data)
                              Column 2: Handle identifier
    """
    conn = None
    cursor = None
    updated_count = 0
    error_count = 0

    try:
        # Connect to the database
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()

        # Prepare the SQL UPDATE statement
        update_sql = "UPDATE handles SET data = %s WHERE handle = %s AND type = 'URL'"

        # Read and process the CSV file
        with open(csv_filepath, newline='', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            line_number = 0
            for row in reader:
                line_number += 1
                if len(row) != 2:
                    error_message = (f"Skipping line {line_number}: Invalid format (expected 2 columns, "
                                     f"found {len(row)})")
                    print(error_message, file=sys.stderr)
                    logging.error(error_message)
                    error_count += 1
                    continue

                new_url, raw_handle = row

                # Clean the handle string
                handle = raw_handle.replace('http://hdl.handle.net/', '').replace('https://hdl.handle.net/', '')

                if not new_url or not handle:
                    error_message = f"Skipping line {line_number}: Empty URL or handle found."
                    print(error_message, file=sys.stderr)
                    logging.error(error_message)
                    error_count += 1
                    continue

                try:
                    # Execute the UPDATE statement
                    cursor.execute(update_sql, (new_url, handle))

                    # Check if any row was actually updated
                    if cursor.rowcount == 0:
                        # No row matched the handle and type='URL'
                        error_message = f"No row found or updated for handle '{handle}' (from line {line_number})"
                        # Log this specific type of error
                        logging.error(error_message)
                        print(f"WARNING: {error_message}", file=sys.stderr)
                        error_count += 1
                    else:
                        # Commit the transaction for the successful update
                        conn.commit()
                        print(f"Successfully updated handle '{handle}' (from line {line_number})")
                        updated_count += 1

                except mysql.connector.Error as db_err:
                    # Handle potential database errors during update execution
                    conn.rollback()  # Rollback the transaction on error
                    error_message = f"Database error updating handle '{handle}' (from line {line_number}): {db_err}"
                    print(error_message, file=sys.stderr)
                    logging.error(error_message)
                    error_count += 1

    except FileNotFoundError:
        error_message = f"FATAL: CSV file not found at '{csv_filepath}'"
        print(error_message, file=sys.stderr)
        logging.critical(error_message)  # Use critical for fatal errors
        sys.exit(1)
    except mysql.connector.Error as conn_err:
        error_message = f"FATAL: Database connection error: {conn_err}"
        print(error_message, file=sys.stderr)
        logging.critical(error_message)
        sys.exit(1)
    except Exception as e:
        error_message = f"FATAL: An unexpected error occurred: {e}"
        print(error_message, file=sys.stderr)
        logging.critical(error_message)
        sys.exit(1)
    finally:
        # Ensure cursor and connection are closed
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
        print(f"\n--- Summary ---")
        print(f"Successfully updated rows: {updated_count}")
        print(f"Rows with errors/not found: {error_count}")
        print(f"Error details logged to: '{LOG_FILE}'")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python update_script.py <path_to_csv_file>", file=sys.stderr)
        sys.exit(1)

    csv_file_path = sys.argv[1]
    update_handle_url(csv_file_path)
