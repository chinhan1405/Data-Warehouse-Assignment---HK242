# app.py
from flask import Flask, render_template, request, send_from_directory
import os
import torch
import torch.nn as nn
import joblib
import numpy as np
from inference import predict_sales

app = Flask(__name__)
REPORTS_FOLDER = 'reports'


@app.route('/', methods=['GET', 'POST'])
def index():
    # Lấy danh sách báo cáo
    reports = [f for f in os.listdir(REPORTS_FOLDER) if f.endswith('.html')]
    prediction = None

    # Xử lý form dự đoán
    if request.method == 'POST':
        try:
            year = float(request.form['year'])
            month = float(request.form['month'])
            quarter = float(request.form['quarter'])
            product_key = float(request.form['product_key'])
            store_key = float(request.form['store_key'])
            product_price = float(request.form['product_price'])
            discount = float(request.form['discount'])
            revenue = float(request.form['revenue'])

            prediction = predict_sales(year, month, quarter, product_key, store_key, product_price, discount, revenue)
        except Exception as e:
            prediction = f"Lỗi: {str(e)}"

    return render_template('index.html', reports=reports, prediction=prediction)


@app.route('/report/<filename>')
def report(filename):
    return send_from_directory(REPORTS_FOLDER, filename)


if __name__ == '__main__':
    app.run(port=8080, debug=True)