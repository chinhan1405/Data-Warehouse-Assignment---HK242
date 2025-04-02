"""This script creates a data warehouse for a bike store database.

It extracts data from the source database, transforms it, and loads it 
into a new SQLite database. The data warehouse consists of dimension tables 
(Dim_Date, Dim_Customer, Dim_Product, Dim_Store, Dim_Staff) and a fact table 
(Fact_Sales).

The script uses SQLite and pandas for data manipulation.

"""
import sqlite3
from datetime import datetime

import pandas as pd


# Connect to the source database
source_conn = sqlite3.connect("../db/bike_store.db")
source_cursor = source_conn.cursor()

# Connect to the data warehouse database
dw_conn = sqlite3.connect("bike_dw.db")
dw_cursor = dw_conn.cursor()

# Determine the date range from orders
source_cursor.execute("SELECT MIN(order_date), MAX(order_date) FROM orders")
min_date, max_date = source_cursor.fetchone()
min_date = datetime.strptime(min_date, "%Y-%m-%d")
max_date = datetime.strptime(max_date, "%Y-%m-%d")

# Generate date range using pandas
date_range = pd.date_range(start=min_date, end=max_date)
dim_date = pd.DataFrame({
    "date_key": date_range.strftime("%Y%m%d").astype(int),
    "full_date": date_range.date,
    "year": date_range.year,
    "quarter": date_range.quarter,
    "month": date_range.month,
    "day": date_range.day,
    "day_of_week": date_range.dayofweek,  # 0 = Monday, 6 = Sunday
    "is_weekend": (
        date_range.dayofweek.isin([5, 6]).astype(int)  
        # 1 if weekend, 0 if weekday
    )
})

# Create Dim_Date table
dw_cursor.execute("""
CREATE TABLE Dim_Date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE,
    year INTEGER,
    quarter INTEGER,
    month INTEGER,
    day INTEGER,
    day_of_week INTEGER,
    is_weekend INTEGER
)
""")
dim_date.to_sql("Dim_Date", dw_conn, if_exists="append", index=False)

# --- Create and Load Dim_Customer ---
customers_df = pd.read_sql_query("SELECT * FROM customers", source_conn)
customers_df["customer_key"] = range(1, len(customers_df) + 1)
dim_customer = customers_df[
    [
        "customer_key",
        "customer_id",
        "first_name",
        "last_name", 
        "phone", 
        "email", 
        "street", 
        "city", 
        "state", 
        "zip_code",
    ]
]

dw_cursor.execute("""
CREATE TABLE Dim_Customer (
    customer_key INTEGER PRIMARY KEY,
    customer_id INTEGER,
    first_name TEXT,
    last_name TEXT,
    phone TEXT,
    email TEXT,
    street TEXT,
    city TEXT,
    state TEXT,
    zip_code TEXT
)
""")
dim_customer.to_sql("Dim_Customer", dw_conn, if_exists="append", index=False)

# --- Create and Load Dim_Product ---
dim_product_df = pd.read_sql_query("""
SELECT p.product_id, p.product_name, p.model_year, p.list_price,
       c.category_name, b.brand_name
FROM products p
LEFT JOIN categories c ON p.category_id = c.category_id
LEFT JOIN brands b ON p.brand_id = b.brand_id
""", source_conn)
dim_product_df["product_key"] = range(1, len(dim_product_df) + 1)
dim_product = dim_product_df[
    [
        "product_key",
        "product_id", 
        "product_name", 
        "model_year", 
        "list_price", 
        "category_name", 
        "brand_name",
    ]
]

dw_cursor.execute("""
CREATE TABLE Dim_Product (
    product_key INTEGER PRIMARY KEY,
    product_id INTEGER,
    product_name TEXT,
    model_year INTEGER,
    list_price REAL,
    category_name TEXT,
    brand_name TEXT
)
""")
dim_product.to_sql("Dim_Product", dw_conn, if_exists="append", index=False)

# --- Create and Load Dim_Store ---
stores_df = pd.read_sql_query("SELECT * FROM stores", source_conn)
stores_df["store_key"] = range(1, len(stores_df) + 1)
dim_store = stores_df[
    [
        "store_key", 
        "store_id", 
        "store_name", 
        "phone", 
        "email", 
        "street", 
        "city", 
        "state", 
        "zip_code",
    ]
]

dw_cursor.execute("""
CREATE TABLE Dim_Store (
    store_key INTEGER PRIMARY KEY,
    store_id INTEGER,
    store_name TEXT,
    phone TEXT,
    email TEXT,
    street TEXT,
    city TEXT,
    state TEXT,
    zip_code TEXT
)
""")
dim_store.to_sql("Dim_Store", dw_conn, if_exists="append", index=False)

# --- Create and Load Dim_Staff ---
staff_df = pd.read_sql_query("SELECT * FROM staffs", source_conn)
staff_df["staff_key"] = range(1, len(staff_df) + 1)
dim_staff = staff_df[
    [
        "staff_key", 
        "staff_id", 
        "first_name", 
        "last_name", 
        "email", 
        "phone", 
        "active", 
        "store_id",
    ]
]

dw_cursor.execute("""
CREATE TABLE Dim_Staff (
    staff_key INTEGER PRIMARY KEY,
    staff_id INTEGER,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    phone TEXT,
    active INTEGER,
    store_id INTEGER
)
""")
dim_staff.to_sql("Dim_Staff", dw_conn, if_exists="append", index=False)

# --- Create and Load Fact_Sales ---
# Create mappings from natural keys to surrogate keys
customer_mapping = dict(
    zip(dim_customer["customer_id"], dim_customer["customer_key"]),
)
product_mapping = dict(
    zip(dim_product["product_id"], dim_product["product_key"]),
)
store_mapping = dict(
    zip(dim_store["store_id"], dim_store["store_key"]),
)
staff_mapping = dict(
    zip(dim_staff["staff_id"], dim_staff["staff_key"]),
)

# Extract sales data
sales_df = pd.read_sql_query("""
SELECT o.order_id, o.customer_id, o.order_date, o.store_id, o.staff_id,
       oi.product_id, oi.quantity, oi.list_price, oi.discount
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
""", source_conn)

# Transform keys
sales_df["date_key"] = pd.to_datetime(
    sales_df["order_date"]
).dt.strftime("%Y%m%d").astype(int)
sales_df["customer_key"] = sales_df["customer_id"].map(customer_mapping)
sales_df["product_key"] = sales_df["product_id"].map(product_mapping)
sales_df["store_key"] = sales_df["store_id"].map(store_mapping)
sales_df["staff_key"] = sales_df["staff_id"].map(staff_mapping)

# Select columns for fact table
fact_sales = sales_df[
    [
        "date_key", 
        "customer_key", 
        "product_key", 
        "store_key", 
        "staff_key", 
        "quantity", 
        "list_price", 
        "discount",
    ]
]

# Create Fact_Sales table with foreign key constraints
dw_cursor.execute("""
CREATE TABLE Fact_Sales (
    date_key INTEGER,
    customer_key INTEGER,
    product_key INTEGER,
    store_key INTEGER,
    staff_key INTEGER,
    quantity INTEGER,
    list_price REAL,
    discount REAL,
    FOREIGN KEY (date_key) REFERENCES Dim_Date(date_key),
    FOREIGN KEY (customer_key) REFERENCES Dim_Customer(customer_key),
    FOREIGN KEY (product_key) REFERENCES Dim_Product(product_key),
    FOREIGN KEY (store_key) REFERENCES Dim_Store(store_key),
    FOREIGN KEY (staff_key) REFERENCES Dim_Staff(staff_key)
)
""")
fact_sales.to_sql("Fact_Sales", dw_conn, if_exists="append", index=False)

# Commit changes and close connections
dw_conn.commit()
source_conn.close()
dw_conn.close()

print("Data warehouse created successfully in bike_dw.db.")