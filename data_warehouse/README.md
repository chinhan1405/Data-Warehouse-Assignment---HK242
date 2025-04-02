# Bike Store Data Warehouse Documentation

## Overview
This document describes a data warehouse built from the Bike Store Sample Database (available on [Kaggle](https://www.kaggle.com/datasets/dillonmyrick/bike-store-sample-database)). The data warehouse is implemented in SQLite (`bike_dw.db`) and follows a **star schema** design, optimized for analytical queries and data mining. It includes dimension tables and a central fact table to support sales analysis.

### Purpose
The data warehouse consolidates transactional data from the Bike Store database into a structure suitable for:
- Aggregating sales metrics (e.g., total revenue, quantities sold).
- Analyzing trends over time, by customer, product, store, or staff.
- Supporting business intelligence and data mining tasks.

### Schema Design
The data warehouse uses a star schema with the following tables:

#### Dimension Tables
1. **Dim_Date**
   - **Purpose**: Enables time-based analysis of sales.
   - **Columns**:
     - `date_key` (INTEGER, PK): YYYYMMDD format (e.g., 20250401).
     - `full_date` (DATE): Full date (e.g., 2025-04-01).
     - `year` (INTEGER): Year of the date.
     - `quarter` (INTEGER): Quarter (1-4).
     - `month` (INTEGER): Month (1-12).
     - `day` (INTEGER): Day of the month (1-31).
     - `day_of_week` (INTEGER): 0 (Monday) to 6 (Sunday).
     - `is_weekend` (INTEGER): 1 if weekend, 0 if weekday.
   - **Source**: Derived from `orders.order_date`.

2. **Dim_Customer**
   - **Purpose**: Stores customer information for segmentation and profiling.
   - **Columns**:
     - `customer_key` (INTEGER, PK): Surrogate key.
     - `customer_id` (INTEGER): Original customer ID.
     - `first_name`, `last_name`, `phone`, `email`, `street`, `city`, `state`, `zip_code` (TEXT): Customer details.
   - **Source**: `customers` table.

3. **Dim_Product**
   - **Purpose**: Provides product details, including category and brand, for product analysis.
   - **Columns**:
     - `product_key` (INTEGER, PK): Surrogate key.
     - `product_id` (INTEGER): Original product ID.
     - `product_name` (TEXT): Name of the product.
     - `model_year` (INTEGER): Year of the product model.
     - `list_price` (REAL): Original list price.
     - `category_name` (TEXT): Product category.
     - `brand_name` (TEXT): Product brand.
   - **Source**: `products`, joined with `categories` and `brands`.

4. **Dim_Store**
   - **Purpose**: Stores store information for location-based analysis.
   - **Columns**:
     - `store_key` (INTEGER, PK): Surrogate key.
     - `store_id` (INTEGER): Original store ID.
     - `store_name`, `phone`, `email`, `street`, `city`, `state`, `zip_code` (TEXT): Store details.
   - **Source**: `stores` table.

5. **Dim_Staff**
   - **Purpose**: Stores staff information for performance analysis.
   - **Columns**:
     - `staff_key` (INTEGER, PK): Surrogate key.
     - `staff_id` (INTEGER): Original staff ID.
     - `first_name`, `last_name`, `email`, `phone` (TEXT): Staff details.
     - `active` (INTEGER): 1 if active, 0 if inactive.
     - `store_id` (INTEGER): Store where staff works.
   - **Source**: `staff` table.

#### Fact Table
- **Fact_Sales**
  - **Purpose**: Stores sales transactions at the order item level for quantitative analysis.
  - **Columns**:
    - `date_key` (INTEGER, FK): Links to `Dim_Date`.
    - `customer_key` (INTEGER, FK): Links to `Dim_Customer`.
    - `product_key` (INTEGER, FK): Links to `Dim_Product`.
    - `store_key` (INTEGER, FK): Links to `Dim_Store`.
    - `staff_key` (INTEGER, FK): Links to `Dim_Staff`.
    - `quantity` (INTEGER): Number of items sold.
    - `list_price` (REAL): Price per item before discount.
    - `discount` (REAL): Discount applied per item.
  - **Source**: `orders` joined with `order_items`.

## How to use
We assume you have Python 3.8+ and SQLite installed. The data warehouse is built using Python and SQLite, and the data is loaded from the original Bike Store database.
You are currently in the `data_warehouse` directory.
1. Install dependencies:
   ```bash
   pip install pandas
   ```
2. Load the data warehouse:
   ```bash
   python load_data.py
   ```
3. Query the data warehouse:

## Conclusion
The Bike Store Data Warehouse provides a robust foundation for data mining and business intelligence. Its star schema enables fast, flexible querying, making it ideal for uncovering insights into sales performance, customer behavior, and operational efficiency. Extend the warehouse by adding more derived attributes or integrating additional data sources as needed.