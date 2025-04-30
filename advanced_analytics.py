# Step 5: Advanced Analytics Integration

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from mlxtend.frequent_patterns import apriori, association_rules
import plotly.express as px
import plotly.graph_objects as go
from prophet import Prophet
from statsmodels.tsa.statespace.varmax import VARMAX
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
import seaborn as sns
from scipy import stats
from statsmodels.tsa.seasonal import seasonal_decompose


class AdvancedAnalytics:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.scaler = StandardScaler()

    def perform_time_series_decomposition(self, data, column='sales', model='additive', period=7):
        # Check if data is a Series or DataFrame
        if isinstance(data, pd.Series):
            result = seasonal_decompose(data, model=model, period=period)
        else:
            result = seasonal_decompose(data[column], model=model, period=period)
        return result

    def calculate_correlations(self, data):
        return data.corr()

    def extract_seasonality(self, data, column='sales', period=12):
        # Check if data is a Series or DataFrame
        if isinstance(data, pd.Series):
            result = seasonal_decompose(data, model='additive', period=period)
        else:
            result = seasonal_decompose(data[column], model='additive', period=period)
        return result.seasonal

    def perform_market_basket_analysis(self, min_support=0.01, min_threshold=0.5):
        transaction_data = self.data_manager.get_transaction_data()
        encoded_data = pd.get_dummies(transaction_data)
        frequent_itemsets = apriori(encoded_data, min_support=min_support, use_colnames=True)
        rules = association_rules(frequent_itemsets, metric="lift", min_threshold=min_threshold)
        rules.sort_values('lift', ascending=False, inplace=True)
        return rules

    def customer_segmentation(self, n_clusters=4):
        customer_data = self.data_manager.get_customer_data()
        features = customer_data[['purchase_frequency', 'average_order_value', 'recency', 'total_spend']]
        scaled_features = self.scaler.fit_transform(features)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        customer_data['cluster'] = kmeans.fit_predict(scaled_features)
        cluster_stats = customer_data.groupby('cluster').agg({
            'purchase_frequency': 'mean',
            'average_order_value': 'mean',
            'recency': 'mean',
            'total_spend': 'mean'
        })
        return customer_data, cluster_stats, kmeans

    def visualize_customer_segments(self, customer_data, kmeans):
        fig = px.scatter_3d(customer_data, x='purchase_frequency', y='average_order_value', z='total_spend',
                            color='cluster', hover_name=customer_data.index, title='Customer Segments')
        cluster_profiles = customer_data.groupby('cluster').mean()
        categories = cluster_profiles.columns.tolist()
        radar_fig = go.Figure()
        for i in range(len(cluster_profiles)):
            radar_fig.add_trace(go.Scatterpolar(
                r=cluster_profiles.iloc[i].values,
                theta=categories,
                fill='toself',
                name=f'Cluster {i}'
            ))
        radar_fig.update_layout(
            polar=dict(radialaxis=dict(visible=True)),
            showlegend=True,
            title="Cluster Profiles"
        )
        return fig, radar_fig

    def price_optimization(self, product_data):
        product_data['elasticity'] = product_data['sales_pct_change'] / product_data['price_pct_change']
        product_data['price_sensitivity'] = np.where(abs(product_data['elasticity']) > 1, 'High', 'Low')
        product_data['optimal_price'] = product_data.apply(
            lambda x: x['current_price'] * 0.95 if x['elasticity'] < -1 else
                      (x['current_price'] * 1.05 if x['elasticity'] > -1 else x['current_price']), axis=1)
        return product_data

    def external_data_integration(self, sales_data, external_data):
        merged_data = pd.merge(sales_data, external_data, on='date', how='inner')
        correlation_matrix = merged_data.corr()
        plt.figure(figsize=(12, 10))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
        plt.title('Correlation between Sales and External Factors')
        causality_results = {}
        for column in external_data.columns:
            if column != 'date':
                test_result = self._granger_causality_test(external_data[column], sales_data['sales'])
                causality_results[column] = test_result
        return correlation_matrix, causality_results

    def _granger_causality_test(self, x, y, max_lag=5):
        results = {}
        for lag in range(1, max_lag + 1):
            test = stats.grangercausalitytests(pd.concat([y, x], axis=1).values, maxlag=lag, verbose=False)
            results[lag] = test[lag][0]['ssr_ftest'][1]  # p-value
        return results

    def build_lstm_forecasting_model(self, data, sequence_length=30, forecast_horizon=14):
        X_train, y_train = self._prepare_lstm_data(data, sequence_length)
        model = Sequential([
            LSTM(50, activation='relu', return_sequences=True, input_shape=(sequence_length, X_train.shape[1], X_train.shape[2])),
            Dropout(0.2),
            LSTM(50, activation='relu'),
            Dropout(0.2),
            Dense(forecast_horizon)
        ])
        model.compile(optimizer='adam', loss='mse')
        early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
        history = model.fit(X_train, y_train, epochs=100, batch_size=32,
                            validation_split=0.2, callbacks=[early_stopping], verbose=1)
        return model, history

    def _prepare_lstm_data(self, data, sequence_length):
        X, y = [], []
        for i in range(len(data) - sequence_length - 14):
            X.append(data.iloc[i:i+sequence_length].values)
            y.append(data.iloc[i+sequence_length:i+sequence_length+14]['sales'].values)
        return np.array(X), np.array(y)

    def anomaly_detection(self, time_series):
        rolling_mean = time_series.rolling(window=7).mean()
        rolling_std = time_series.rolling(window=7).std()
        z_scores = (time_series - rolling_mean) / rolling_std
        anomalies = np.abs(z_scores) > 3
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=time_series.index, y=time_series.values,
                                 mode='lines', name='Time Series'))
        anomaly_indices = time_series.index[anomalies]
        anomaly_values = time_series.values[anomalies]
        fig.add_trace(go.Scatter(x=anomaly_indices, y=anomaly_values,
                                 mode='markers', marker=dict(color='red', size=10), name='Anomalies'))
        fig.update_layout(title='Time Series Anomaly Detection',
                          xaxis_title='Date', yaxis_title='Value')
        return anomalies, fig
