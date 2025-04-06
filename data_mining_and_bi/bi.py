import sqlite3
import pandas as pd
from ydata_profiling import ProfileReport



# Connect to the data warehouse database
dw_conn = sqlite3.connect("../data_warehouse/bike_dw.db")
dw_cursor = dw_conn.cursor()

dw_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = dw_cursor.fetchall()

# Generate html files to visualize data from Data Warehouse
for table in tables:
    table_name = table[0]
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql_query(query, dw_conn)
    profile = ProfileReport(df, title=f" {table_name} Table Profile Report", explorative=True)
    profile.to_file(f"reports/{table_name}_report.html")