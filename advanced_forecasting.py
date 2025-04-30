import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

class TimeSeriesTransformer(nn.Module):
    """
    A transformer model for time series forecasting
    """
    def __init__(self, input_dim, hidden_dim, output_dim, num_layers, num_heads, dropout=0.1):
        super(TimeSeriesTransformer, self).__init__()
        
        self.encoder_embedding = nn.Linear(input_dim, hidden_dim)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_dim, 
            nhead=num_heads,
            dim_feedforward=hidden_dim*4,
            dropout=dropout,
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.decoder = nn.Linear(hidden_dim, output_dim)
        
    def forward(self, x):
        # x shape: [batch, seq_len, features]
        x = self.encoder_embedding(x)
        x = self.transformer_encoder(x)
        # Take only the last output for forecasting
        x = x[:, -1, :]
        x = self.decoder(x)
        return x


class AdvancedForecastingModule:
    """
    Extends the TrendLensECommerceAnalyzer with advanced forecasting capabilities
    """
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.scaler = MinMaxScaler()
        self.transformer_model = None
        self.forecast_data = None
        
    def prepare_data_for_transformer(self, seq_length=12, train_split=0.8):
        """
        Prepare data for transformer model
        """
        if self.analyzer.processed_data is None:
            raise ValueError("No processed data available. Run preprocessing first.")
            
        # Get sales data
        data = self.analyzer.processed_data[['sales'] + 
                                           [col for col in self.analyzer.processed_data.columns 
                                            if col != 'sales']]
        
        # Scale data
        scaled_data = self.scaler.fit_transform(data)
        
        # Create sequences
        X, y = [], []
        for i in range(len(scaled_data) - seq_length):
            X.append(scaled_data[i:i+seq_length])
            y.append(scaled_data[i+seq_length, 0])  # predict sales only
            
        X = np.array(X)
        y = np.array(y).reshape(-1, 1)
        
        # Split into train and test
        train_size = int(len(X) * train_split)
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]
        
        # Convert to torch tensors
        X_train = torch.FloatTensor(X_train).to(self.device)
        y_train = torch.FloatTensor(y_train).to(self.device)
        X_test = torch.FloatTensor(X_test).to(self.device)
        y_test = torch.FloatTensor(y_test).to(self.device)
        
        return X_train, y_train, X_test, y_test, data.columns
    
    def train_transformer_model(self, epochs=100, batch_size=32, learning_rate=0.001):
        """
        Train a transformer model for time series forecasting
        """
        X_train, y_train, X_test, y_test, feature_names = self.prepare_data_for_transformer()
        
        # Define model
        input_dim = X_train.shape[2]  # number of features
        hidden_dim = 64
        output_dim = 1   # predict sales only
        num_layers = 2
        num_heads = 4
        
        model = TimeSeriesTransformer(input_dim, hidden_dim, output_dim, num_layers, num_heads)
        model = model.to(self.device)
        
        # Define loss and optimizer
        criterion = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=learning_rate)
        
        # Create DataLoader
        train_dataset = TensorDataset(X_train, y_train)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        
        # Training loop
        model.train()
        for epoch in range(epochs):
            running_loss = 0.0
            for batch_X, batch_y in train_loader:
                optimizer.zero_grad()
                
                outputs = model(batch_X)
                loss = criterion(outputs, batch_y)
                
                loss.backward()
                optimizer.step()
                
                running_loss += loss.item()
                
            # Print progress every 10 epochs
            if (epoch + 1) % 10 == 0:
                print(f'Epoch {epoch+1}/{epochs}, Loss: {running_loss/len(train_loader):.6f}')
        
        print(f"Training completed for {self.analyzer.platform_name}")
        
        # Evaluate
        model.eval()
        with torch.no_grad():
            y_pred = model(X_test)
            test_loss = criterion(y_pred, y_test)
            print(f"Test Loss: {test_loss.item():.6f}")
            
            # Convert back to original scale
            y_test_np = y_test.cpu().numpy()
            y_pred_np = y_pred.cpu().numpy()
            
            # Create dummy arrays with zeros for all features
            y_test_dummy = np.zeros((len(y_test_np), len(feature_names)))
            y_pred_dummy = np.zeros((len(y_pred_np), len(feature_names)))
            
            # Put the sales values in the first column
            y_test_dummy[:, 0] = y_test_np.flatten()
            y_pred_dummy[:, 0] = y_pred_np.flatten()
            
            # Inverse transform
            y_test_orig = self.scaler.inverse_transform(y_test_dummy)[:, 0]
            y_pred_orig = self.scaler.inverse_transform(y_pred_dummy)[:, 0]
            
            # Calculate metrics
            mae = np.mean(np.abs(y_test_orig - y_pred_orig))
            rmse = np.sqrt(np.mean((y_test_orig - y_pred_orig)**2))
            
            print(f"MAE: {mae:.2f}")
            print(f"RMSE: {rmse:.2f}")
        
        self.transformer_model = model
        return model, (y_test_orig, y_pred_orig)
    
    def forecast_future(self, steps=30):
        """
        Generate forecasts for future time steps
        """
        if self.transformer_model is None:
            raise ValueError("Model not trained. Train model first.")
            
        if self.analyzer.processed_data is None:
            raise ValueError("No processed data available.")
            
        # Get the most recent sequence for prediction
        data = self.analyzer.processed_data[['sales'] + 
                                          [col for col in self.analyzer.processed_data.columns 
                                           if col != 'sales']]
        
        scaled_data = self.scaler.transform(data)
        
        # Use the last sequence as input
        last_sequence = scaled_data[-12:]  # Using seq_length=12
        
        # Convert to tensor
        last_sequence = torch.FloatTensor(last_sequence).unsqueeze(0).to(self.device)
        
        # Set model to eval mode
        self.transformer_model.eval()
        
        # Generate forecasts
        forecasts = []
        input_seq = last_sequence
        
        for _ in range(steps):
            with torch.no_grad():
                # Predict next value
                next_val = self.transformer_model(input_seq)
                
                # Create a full-featured prediction (set other features to 0)
                next_full = torch.zeros(1, 1, input_seq.shape[2]).to(self.device)
                next_full[0, 0, 0] = next_val[0, 0]  # Set sales value
                
                # Remove oldest timestep and append prediction
                input_seq = torch.cat([input_seq[:, 1:, :], next_full], dim=1)
                
                # Convert prediction to original scale for output
                next_val_np = next_val.cpu().numpy()
                next_full_np = np.zeros((1, data.shape[1]))
                next_full_np[0, 0] = next_val_np[0, 0]  # Set sales value
                next_orig = self.scaler.inverse_transform(next_full_np)[0, 0]
                
                forecasts.append(next_orig)
        
        # Create forecast dates
        last_date = self.analyzer.processed_data.index[-1]
        forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=steps)
        
        # Create forecast dataframe
        forecast_df = pd.DataFrame({
            'date': forecast_dates,
            'sales_forecast': forecasts
        })
        forecast_df.set_index('date', inplace=True)
        
        self.forecast_data = forecast_df
        return forecast_df
        
    def visualize_forecast(self):
        """
        Visualize historical data and forecasts
        """
        if self.forecast_data is None:
            raise ValueError("No forecast data available. Run forecast_future first.")
            
        plt.figure(figsize=(12, 6))
        
        # Plot historical data
        plt.plot(self.analyzer.processed_data.index, 
                self.analyzer.processed_data['sales'], 
                label='Historical Sales')
        
        # Plot forecast
        plt.plot(self.forecast_data.index, 
                self.forecast_data['sales_forecast'], 
                color='red', 
                label='Forecast')
        
        # Add confidence interval (simple placeholder, can be improved)
        upper_bound = self.forecast_data['sales_forecast'] * 1.1
        lower_bound = self.forecast_data['sales_forecast'] * 0.9
        plt.fill_between(self.forecast_data.index, 
                        lower_bound, 
                        upper_bound, 
                        color='pink', 
                        alpha=0.3)
        
        plt.title(f'{self.analyzer.platform_name} Sales Forecast with Transformer Model')
        plt.xlabel('Date')
        plt.ylabel('Sales')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        return plt.gcf()
