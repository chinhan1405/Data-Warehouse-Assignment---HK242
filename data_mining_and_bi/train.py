import sqlite3
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from gunicorn.config import validate_list_string
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import numpy as np
import joblib
from model import SalesPredictor

dw_conn = sqlite3.connect("../data_warehouse/bike_dw.db")

query = """
SELECT 
    fs.date_key, 
    dd.year, 
    dd.month, 
    dd.quarter, 
    fs.product_key, 
    dp.list_price as product_price, 
    fs.store_key, 
    fs.quantity, 
    fs.discount
FROM Fact_Sales fs
JOIN Dim_Date dd ON fs.date_key = dd.date_key
JOIN Dim_Product dp ON fs.product_key = dp.product_key
JOIN Dim_Store ds ON fs.store_key = ds.store_key
"""
data = pd.read_sql_query(query, dw_conn)
dw_conn.close()

data['revenue'] = data['quantity'] * data['product_price'] * (1 - data['discount'])

features = ['year', 'month', 'quarter', 'product_key', 'store_key', 'product_price', 'discount', 'revenue']
X = data[features].values
y = data['quantity'].values

scaler = StandardScaler()
X = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

X_train = torch.FloatTensor(X_train)
X_test = torch.FloatTensor(X_test)
y_train = torch.FloatTensor(y_train).view(-1, 1)
y_test = torch.FloatTensor(y_test).view(-1, 1)


def calculate_accuracy(y_true, y_pred):
    y_pred_rounded = np.round(y_pred).astype(int)
    y_true = y_true.astype(int)

    correct_predictions = np.sum(y_pred_rounded == y_true)
    total_predictions = len(y_true)

    accuracy = correct_predictions / total_predictions
    return accuracy

input_size = X_train.shape[1]
model = SalesPredictor(input_size)

criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

num_epochs = 1000
train_losses = []
val_losses = []
for epoch in range(num_epochs):
    model.train()
    optimizer.zero_grad()
    outputs = model(X_train)
    loss = criterion(outputs, y_train)
    train_losses.append(loss.item())
    loss.backward()
    optimizer.step()

    train_acc = calculate_accuracy(y_train.numpy(), outputs.detach().numpy())
    if (epoch + 1) % 100 == 0:
        print(f"Epoch [{epoch + 1}/{num_epochs}]")
        print(f"Train_Loss: {loss.item():.4f}")
        print(f"Train_Accuracy: {train_acc:.4f}")

    model.eval()
    with torch.no_grad():
        y_pred = model(X_test)
        val_loss = criterion(y_pred, y_test)
        val_losses.append(val_loss.item())
        val_acc = calculate_accuracy(y_test.numpy(), y_pred.numpy())
        if (epoch + 1) % 100 == 0:
            print(f"Val_Loss (MSE): {val_loss.item():.4f}")
            print(f"Val_Accuracy: {val_acc:.4f}")


torch.save(model.state_dict(), "checkpoint/sales_predictor.pth")
joblib.dump(scaler, "checkpoint/scaler.pkl")

plt.plot(train_losses, label='Training Loss')
plt.plot(val_losses, label='Validation Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('Training and Validation Loss Over Time')
plt.legend()
plt.show()



