# 📊 TrendLens: Intelligent E-Commerce Sales Forecasting and Recommendation System

**TrendLens** is a smart desktop GUI application that enables detailed sales forecasting, seasonal pattern detection, and data-driven recommendations for popular Indian e-commerce platforms: **Meesho**, **Flipkart**, and **Amazon**.

Built using Python, Tkinter, and powerful AI models, TrendLens empowers businesses to make data-backed decisions using time series analysis and machine learning.

---

## 🧠 Key Features

### 🔍 Data Analysis & Visualization
- Load and preprocess sales data from all three platforms
- Visualize sales trends, seasonality, and residual components
- Weekly and monthly sales patterns
- Correlation heatmaps and cross-platform comparison

### 📈 Forecasting Engine
Supports multiple models:
- **ARIMA**
- **Exponential Smoothing**
- **Prophet**
- **LSTM**
- **Transformer (Attention-based)**

Generates:
- Performance metrics (MAE, MSE, RMSE, MAPE)
- Forecast visualizations integrated in GUI

### 💡 AI-Powered Recommendations
- Personalized suggestions for:
  - Pricing Strategy
  - Inventory Planning
  - Marketing Tactics
  - Cross-Platform Optimization
- Supports export of reports (HTML/Text)
- Interactive recommendation tabs for every insight type

---

## 🏗️ Tech Stack

- **Frontend**: `Tkinter`, `CustomTkinter`, `matplotlib`
- **Backend / Models**: `pandas`, `scikit-learn`, `statsmodels`, `Prophet`, `TensorFlow`, `plotly`
- **Forecasting Models**: `ARIMA`, `Exponential Smoothing`, `Prophet`, `LSTM`, `Transformer`
- **Visualization**: `matplotlib`, `plotly`, `seaborn`

---

## 📁 Dataset Information

The application uses **synthetic but realistic datasets** for:
- 🛒 **Meesho**
- 📦 **Flipkart**
- 📬 **Amazon**

**Attributes:**
- Common columns: `date`, `state`, `category`, `sales`, `price`, `order_id`, etc.
- Categories covered: `Grocery`, `Clothes`, `Accessories`
- Duration: 6+ months of data across all Indian states

> ✅ Designed to be uniform across platforms to enable **seamless comparative analysis**.

