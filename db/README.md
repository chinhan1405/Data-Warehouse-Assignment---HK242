Convert csv file to SQLite

convert.py: Creates tables and imports data from CSV files into SQLite.

bike_store.db: The generated SQLite database file.

CSV Files: Source data from https://www.kaggle.com/datasets/dillonmyrick/bike-store-sample-database.

Usage Instructions

Step 1: Install dependencies and prepare sample data

Run the following command to install the required library:

pip install pandas

Create a folder named "data" and place the sample CSV files inside.

csv files are taken from the above source and decompressed

Step 2: Run the data import script

Run the following command to create the database and import data from CSV files:

python convert.py

Make sure to update csv_folder = "data" to match the directory containing your CSV files.


