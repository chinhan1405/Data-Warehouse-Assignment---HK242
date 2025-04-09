# inference.py
import torch
import torch.nn as nn
import joblib
import numpy as np
from model import SalesPredictor

def predict_sales(year, month, quarter, product_key, store_key, product_price, discount, revenue):
    scaler = joblib.load("checkpoint/scaler.pkl")
    model = SalesPredictor(input_size=8)
    model.load_state_dict(torch.load("checkpoint/sales_predictor.pth"))
    model.eval()

    input_data = np.array([[year, month, quarter, product_key, store_key, product_price, discount, revenue]])
    input_data = scaler.transform(input_data)
    input_tensor = torch.FloatTensor(input_data)

    with torch.no_grad():
        prediction = model(input_tensor)
    return  np.round(prediction.item()).astype(int)

