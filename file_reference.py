import datetime
import psycopg2

DB_CONFIG = {
    "dbname": "logistics_db",
    "user": "postgres",
    "password": "admin",
    "host": "localhost",
    "port": "5432",
}

# Mapping modes to codes
MODE_CODES = {
    "Air Freight": "AA",
    "Road Freight": "KA",
    "Sea Freight": "SA",
    "Bond": "KB",
    "Export": "KE"
}

def generate_file_reference(mode, route):
    """Generates a structured file reference."""
    today = datetime.datetime.today().strftime("%m/%y")  # Example: "02/25"
    mode_code = MODE_CODES.get(mode, "XX")  # Default to XX if not found

    # Connect to DB and count existing files for the mode & route
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM file_references WHERE mode=%s AND route=%s", (mode, route))
    count = cur.fetchone()[0] + 1
    conn.close()

    # Generate file reference
    return f"{mode_code}{count:03}/{today}"

def save_file_reference(mode, route, file_reference, document_path):
    """Saves file reference to the database."""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("INSERT INTO file_references (mode, route, reference_id, document_path, date_created) VALUES (%s, %s, %s, %s, NOW())",
                (mode, route, file_reference, document_path))
    conn.commit()
    conn.close()
