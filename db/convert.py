import sqlite3
import pandas as pd
import os

def create_database(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA foreign_keys = ON")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS brands (
        brand_id INTEGER PRIMARY KEY,
        brand_name TEXT NOT NULL
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        category_id INTEGER PRIMARY KEY,
        category_name TEXT NOT NULL
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        phone TEXT,
        email TEXT,
        street TEXT,
        city TEXT,
        state TEXT,
        zip_code TEXT
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT NOT NULL,
        brand_id INTEGER,
        category_id INTEGER,
        model_year INTEGER,
        list_price REAL,
        FOREIGN KEY (brand_id) REFERENCES brands(brand_id),
        FOREIGN KEY (category_id) REFERENCES categories(category_id)
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        order_status INTEGER,
        order_date TEXT,
        required_date TEXT,
        shipped_date TEXT,
        store_id INTEGER,
        staff_id INTEGER,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (store_id) REFERENCES stores(store_id),
        FOREIGN KEY (staff_id) REFERENCES staffs(staff_id)
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        order_id INTEGER,
        item_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        list_price REAL,
        discount REAL,
        PRIMARY KEY (order_id, item_id),
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS staffs (
        staff_id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        email TEXT,
        phone TEXT,
        active INTEGER,
        store_id INTEGER,
        manager_id INTEGER,
        FOREIGN KEY (store_id) REFERENCES stores(store_id),
        FOREIGN KEY (manager_id) REFERENCES staffs(staff_id)
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stores (
        store_id INTEGER PRIMARY KEY,
        store_name TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        street TEXT,
        city TEXT,
        state TEXT,
        zip_code TEXT
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stocks (
        store_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        PRIMARY KEY (store_id, product_id),
        FOREIGN KEY (store_id) REFERENCES stores(store_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )""")
    
    conn.commit()
    conn.close()

def import_csv_to_sqlite(db_name, csv_file, table_name, if_exists="replace"):
    
    if not os.path.exists(csv_file):
        print(f"File not found: {csv_file}")
        return

    conn = sqlite3.connect(db_name)
    df = pd.read_csv(csv_file)
    df.to_sql(table_name, conn, if_exists=if_exists, index=False)
    conn.close()
    print(f"Imported {len(df)} row into table {table_name}")

if __name__ == "__main__":

    db_name = "bike_store.db"
    csv_folder = "data"

    if os.path.exists(db_name):
        os.remove(db_name)
        print(f"Replace: {db_name}")
    else:
        print(f"Create: {db_name}")

    create_database(db_name)
    
    csv_files = {
        "brands.csv": "brands",
        "categories.csv": "categories",
        "customers.csv": "customers",
        "products.csv": "products",
        "orders.csv": "orders",
        "order_items.csv": "order_items",
        "staffs.csv": "staffs",
        "stores.csv": "stores",
        "stocks.csv": "stocks"
    }


    for file_name, table_name in csv_files.items():
        file_path = os.path.join(csv_folder, file_name)
        import_csv_to_sqlite(db_name, file_path, table_name, if_exists="replace")
    
    print("success")
