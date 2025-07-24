import sqlite3

DB_PATH = 'backend/fusionflow.db'  # Adjust path if needed

def migrate():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Check if the old column exists
    c.execute("PRAGMA table_info(suppliers)")
    columns = [row[1] for row in c.fetchall()]
    if 'status_tag' not in columns:
        print("Column 'status_tag' does not exist or has already been migrated.")
        conn.close()
        return
    # SQLite does not support direct column renaming before v3.25.0, so we recreate the table
    print("Renaming 'status_tag' to 'relationship_tag' in 'suppliers' table...")
    c.execute("""
        ALTER TABLE suppliers RENAME TO suppliers_old;
    """)
    # Get the schema of the old table
    c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='suppliers_old';")
    create_sql = c.fetchone()[0]
    # Replace 'status_tag' with 'relationship_tag' in the schema
    create_sql = create_sql.replace('status_tag', 'relationship_tag')
    c.execute(create_sql)
    # Copy data
    old_columns = ', '.join([col if col != 'status_tag' else 'status_tag AS relationship_tag' for col in columns])
    c.execute(f"INSERT INTO suppliers SELECT {old_columns} FROM suppliers_old;")
    c.execute("DROP TABLE suppliers_old;")
    conn.commit()
    print("Migration complete. 'status_tag' has been renamed to 'relationship_tag'.")
    conn.close()

if __name__ == '__main__':
    migrate() 