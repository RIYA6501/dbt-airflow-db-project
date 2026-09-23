import os
import psycopg2

DEFAULT_CONN_STRING = "postgresql://tsdbadmin:tjdy844mk5jfpog2@ye0kcduyu7.s7nc8i1v1d.db.ghost.build:5432/tsdb?sslmode=require"
conn_string = os.getenv("POSTGRES_CONNECTION") or DEFAULT_CONN_STRING

csv_files = {
    "customers.csv": "raw.customers",
    "stores.csv": "raw.stores",
    "products.csv": "raw.products",
    "employees.csv": "raw.employees",
    "orders.csv": "raw.orders",
    "order_items.csv": "raw.order_items",
}

data_dir = os.path.join(os.path.dirname(__file__), "data")

create_schema_sql = "CREATE SCHEMA IF NOT EXISTS raw;"

create_tables_sql = """
CREATE TABLE IF NOT EXISTS raw.customers (
    customer_id BIGINT PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(50),
    city VARCHAR(100),
    province VARCHAR(100),
    country VARCHAR(100),
    created_timestamp TIMESTAMP,
    updated_timestamp TIMESTAMP,
    is_active CHAR(1)
);

CREATE TABLE IF NOT EXISTS raw.stores (
    store_id BIGINT PRIMARY KEY,
    store_name VARCHAR(255),
    city VARCHAR(100),
    province VARCHAR(100),
    country VARCHAR(100),
    created_timestamp TIMESTAMP,
    updated_timestamp TIMESTAMP,
    is_active CHAR(1)
);

CREATE TABLE IF NOT EXISTS raw.products (
    product_id BIGINT PRIMARY KEY,
    product_name VARCHAR(255),
    category VARCHAR(100),
    brand VARCHAR(100),
    price NUMERIC(10,2),
    created_timestamp TIMESTAMP,
    updated_timestamp TIMESTAMP,
    is_active CHAR(1)
);

CREATE TABLE IF NOT EXISTS raw.employees (
    employee_id BIGINT PRIMARY KEY,
    store_id BIGINT,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    job_title VARCHAR(100),
    salary NUMERIC(10,2),
    created_timestamp TIMESTAMP,
    updated_timestamp TIMESTAMP,
    is_active CHAR(1)
);

CREATE TABLE IF NOT EXISTS raw.orders (
    order_id BIGINT PRIMARY KEY,
    customer_id BIGINT,
    store_id BIGINT,
    order_timestamp TIMESTAMP,
    payment_method VARCHAR(50),
    order_status VARCHAR(50),
    total_amount NUMERIC(12,2),
    created_timestamp TIMESTAMP,
    updated_timestamp TIMESTAMP,
    is_active CHAR(1)
);

CREATE TABLE IF NOT EXISTS raw.order_items (
    order_item_id BIGINT PRIMARY KEY,
    order_id BIGINT,
    product_id BIGINT,
    quantity INT,
    unit_price NUMERIC(10,2),
    line_amount NUMERIC(12,2),
    created_timestamp TIMESTAMP,
    updated_timestamp TIMESTAMP,
    is_active CHAR(1)
);
"""

conn = None

try:
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    cursor.execute(create_schema_sql)
    cursor.execute(create_tables_sql)
    conn.commit()

    for csv_file, table_name in csv_files.items():
        csv_path = os.path.join(data_dir, csv_file)

        if os.path.exists(csv_path):
            print(f"Loading {csv_file} into {table_name}...")

            with open(csv_path, "r", encoding="utf-8-sig") as f:
                cursor.copy_expert(f"COPY {table_name} FROM STDIN WITH (FORMAT CSV, HEADER TRUE)", f)

            conn.commit()
            print(f"✓ Successfully loaded {csv_file}")
        else:
            print(f"✗ File not found: {csv_path}")

    cursor.close()
    conn.close()
    print("\n✓ All data loaded successfully!")

except Exception as e:
    print(f"Error: {e}")
    if conn is not None:
        conn.rollback()
        conn.close()
