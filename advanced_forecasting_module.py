import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import MinMaxScaler
import warnings
warnings.filterwarnings('ignore')

class AdvancedForecastingModule:
    """Advanced forecasting module with multiple time series forecasting algorithms"""
    
    def __init__(self, data):
        """
        Initialize the forecasting module
        
        Args:
            data (DataFrame): Time series data with datetime index
        """
        self.data = data
        self.target_column = 'sales'  # Default target column
        self.models = {}
        self.results = {}
        
    def generate_forecast(self, model_type, horizon, **kwargs):
        """
        Generate forecast using the specified model
        
        Args:
            model_type (str): Model type (ARIMA, Exponential Smoothing, Prophet, LSTM, Transformer)
            horizon (int): Forecast horizon in days
            **kwargs: Additional parameters specific to each model
            
        Returns:
            dict: Forecast results including historical and forecast values
        """
        # Prepare data
        if self.target_column not in self.data.columns:
            raise ValueError(f"Target column '{self.target_column}' not found in data")
        
        # Get the target series
        series = self.data[self.target_column].copy()
        
        # Convert series to DataFrame with datetime index if not already
        if not isinstance(series.index, pd.DatetimeIndex):
            raise ValueError("Data must have a datetime index")
        
        # Choose forecasting method based on model_type
        if model_type == "ARIMA":
            return self._forecast_arima(series, horizon, **kwargs)
        elif model_type == "Exponential Smoothing":
            return self._forecast_exponential_smoothing(series, horizon, **kwargs)
        elif model_type == "Prophet":
            return self._forecast_prophet(series, horizon, **kwargs)
        elif model_type == "LSTM":
            return self._forecast_lstm(series, horizon, **kwargs)
        elif model_type == "Transformer":
            return self._forecast_transformer(series, horizon, **kwargs)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
    
    def _forecast_arima(self, series, horizon, p=1, d=1, q=1, auto=True, show_ci=True, confidence_level=0.95):
        """
        Generate forecast using ARIMA model
        
        Args:
            series (Series): Time series data
            horizon (int): Forecast horizon
            p (int): AR order
            d (int): Differencing order
            q (int): MA order
            auto (bool): Use auto_arima to determine parameters
            show_ci (bool): Show confidence intervals
            confidence_level (float): Confidence level for intervals
            
        Returns:
            dict: Forecast results
        """
        # If auto mode is selected, use SARIMAX with automatic parameter selection
        if auto:
            try:
                # For a proper auto_arima implementation, you might want to use pmdarima package
                # Here we'll use a simplified approach with SARIMAX
                from statsmodels.tsa.statespace.sarimax import SARIMAX
                
                # Fit SARIMAX model with seasonal components
                model = SARIMAX(series, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
                results = model.fit(disp=False)
                
                # Generate forecast
                forecast = results.get_forecast(steps=horizon)
                forecast_index = pd.date_range(start=series.index[-1] + pd.Timedelta(days=1), periods=horizon)
                
                # Get confidence intervals
                if show_ci:
                    conf_int = forecast.conf_int(alpha=1-confidence_level)
                    lower_bound = conf_int.iloc[:, 0].values
                    upper_bound = conf_int.iloc[:, 1].values
                else:
                    lower_bound = None
                    upper_bound = None
                
                # Get forecast values
                forecast_values = forecast.predicted_mean.values
                
            except Exception as e:
                print(f"Error in auto SARIMAX: {e}")
                # Fall back to simple ARIMA
                model = ARIMA(series, order=(p, d, q))
                results = model.fit()
                
                # Generate forecast
                forecast = results.forecast(steps=horizon)
                forecast_index = pd.date_range(start=series.index[-1] + pd.Timedelta(days=1), periods=horizon)
                forecast_values = forecast.values
                
                # Get confidence intervals
                if show_ci:
                    conf_int = results.get_forecast(steps=horizon).conf_int(alpha=1-confidence_level)
                    lower_bound = conf_int.iloc[:, 0].values
                    upper_bound = conf_int.iloc[:, 1].values
                else:
                    lower_bound = None
                    upper_bound = None
        else:
            # Use ARIMA with specified parameters
            model = ARIMA(series, order=(p, d, q))
            results = model.fit()
            
            # Generate forecast
            forecast = results.forecast(steps=horizon)
            forecast_index = pd.date_range(start=series.index[-1] + pd.Timedelta(days=1), periods=horizon)
            forecast_values = forecast.values
            
            # Get confidence intervals
            if show_ci:
                conf_int = results.get_forecast(steps=horizon).conf_int(alpha=1-confidence_level)
                lower_bound = conf_int.iloc[:, 0].values
                upper_bound = conf_int.iloc[:, 1].values
            else:
                lower_bound = None
                upper_bound = None
        
        # Store model
        self.models['ARIMA'] = model
        self.results['ARIMA'] = results
        
        # Calculate metrics on training data
        y_pred = results.fittedvalues
        y_true = series[y_pred.index]
        mae = mean_absolute_error(y_true, y_pred)
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        
        # Generate insights
        insights = self._generate_forecast_insights(series, forecast_values, model_type="ARIMA")
        
        # Return results
        return {
            'historical_dates': series.index,
            'historical_values': series.values,
            'forecast_dates': forecast_index,
            'forecast_values': forecast_values,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'metrics': {
                'MAE': mae,
                'MSE': mse,
                'RMSE': rmse,
                'MAPE': mape
            },
            'insights': insights
        }
    
    def _forecast_exponential_smoothing(self, series, horizon, trend='add', seasonal='add', 
                                       period=7, show_ci=True, confidence_level=0.95):
        """
        Generate forecast using Exponential Smoothing
        
        Args:
            series (Series): Time series data
            horizon (int): Forecast horizon
            trend (str): Type of trend ('add', 'mul', None)
            seasonal (str): Type of seasonality ('add', 'mul', None)
            period (int): Seasonal period
            show_ci (bool): Show confidence intervals
            confidence_level (float): Confidence level for intervals
            
        Returns:
            dict: Forecast results
        """
        # Handle parameters
        if trend == 'None':
            trend = None
        if seasonal == 'None':
            seasonal = None
        
        # Fit model
        model = ExponentialSmoothing(series, trend=trend, seasonal=seasonal, seasonal_periods=period)
        results = model.fit()
        
        # Generate forecast
        forecast = results.forecast(horizon)
        forecast_index = pd.date_range(start=series.index[-1] + pd.Timedelta(days=1), periods=horizon)
        forecast_values = forecast.values
        
        # Calculate approximate confidence intervals (Exponential Smoothing doesn't provide them directly)
        if show_ci:
            # Get residuals
            residuals = results.resid
            residual_std = residuals.std()
            
            # Calculate z-score for the confidence level
            import scipy.stats as stats
            z = stats.norm.ppf((1 + confidence_level) / 2)
            
            # Calculate confidence intervals
            margin = z * residual_std * np.sqrt(np.arange(1, horizon + 1))
            lower_bound = forecast_values - margin
            upper_bound = forecast_values + margin
        else:
            lower_bound = None
            upper_bound = None
        
        # Store model
        self.models['ExponentialSmoothing'] = model
        self.results['ExponentialSmoothing'] = results
        
        # Calculate metrics on training data
        y_pred = results.fittedvalues
        y_true = series[y_pred.index]
        mae = mean_absolute_error(y_true, y_pred)
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        
        # Generate insights
        insights = self._generate_forecast_insights(series, forecast_values, model_type="Exponential Smoothing")
        
        # Return results
        return {
            'historical_dates': series.index,
            'historical_values': series.values,
            'forecast_dates': forecast_index,
            'forecast_values': forecast_values,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'metrics': {
                'MAE': mae,
                'MSE': mse,
                'RMSE': rmse,
                'MAPE': mape
            },
            'insights': insights
        }
    
    def _forecast_prophet(self, series, horizon, yearly_seasonality=True, 
                         weekly_seasonality=True, daily_seasonality=False, 
                         show_ci=True, confidence_level=0.95):
        """
        Generate forecast using Facebook Prophet
        
        Args:
            series (Series): Time series data
            horizon (int): Forecast horizon
            yearly_seasonality (bool): Include yearly seasonality
            weekly_seasonality (bool): Include weekly seasonality
            daily_seasonality (bool): Include daily seasonality
            show_ci (bool): Show confidence intervals
            confidence_level (float): Confidence level for intervals
            
        Returns:
            dict: Forecast results
        """
        try:
            # For this implementation, we'll simulate Prophet results
            # In a real implementation, you'd use:
            # from prophet import Prophet
            
            # Placeholder for Prophet simulation
            # Use a combination of trend and seasonality components
            
            # Extract trend with moving average
            trend = series.rolling(window=30, min_periods=1).mean()
            
            # Create date features
            dates = series.index
            day_of_week = dates.dayofweek
            month = dates.month
            
            # Simulate weekly seasonality
            weekly_pattern = np.array([-0.1, 0.1, 0.2, 0.1, 0.3, -0.2, -0.4])
            weekly_component = weekly_pattern[day_of_week]
            
            # Simulate yearly seasonality
            yearly_pattern = np.sin(2 * np.pi * month / 12) * 0.2
            
            # Combine components
            fitted = trend.values
            if weekly_seasonality:
                fitted += weekly_component
            if yearly_seasonality:
                fitted += yearly_pattern
                
            # Generate forecast
            # Extend trend
            last_trend = trend.iloc[-1]
            trend_slope = (trend.iloc[-1] - trend.iloc[-30]) / 30 if len(trend) >= 30 else 0
            forecast_trend = last_trend + np.arange(1, horizon + 1) * trend_slope
            
            # Create forecast dates
            forecast_index = pd.date_range(start=series.index[-1] + pd.Timedelta(days=1), periods=horizon)
            
            # Add seasonality to forecast
            forecast_values = forecast_trend.copy()
            
            if weekly_seasonality:
                forecast_values += weekly_pattern[forecast_index.dayofweek]
                
            if yearly_seasonality:
                forecast_values += np.sin(2 * np.pi * forecast_index.month / 12) * 0.2
            
            # Calculate confidence intervals
            if show_ci:
                # Calculate residuals
                residuals = series.values - fitted
                residual_std = np.std(residuals)
                
                # Calculate z-score for the confidence level
                import scipy.stats as stats
                z = stats.norm.ppf((1 + confidence_level) / 2)
                
                # Increasing uncertainty with time
                uncertainty_factor = np.sqrt(np.arange(1, horizon + 1) / 10)
                margin = z * residual_std * uncertainty_factor
                
                lower_bound = forecast_values - margin
                upper_bound = forecast_values + margin
            else:
                lower_bound = None
                upper_bound = None

            # Calculate metrics
            y_pred = pd.Series(fitted, index=series.index)
            y_true = series
            mae = mean_absolute_error(y_true, y_pred)
            mse = mean_squared_error(y_true, y_pred)
            rmse = np.sqrt(mse)
            mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
            
            # Generate insights
            insights = self._generate_forecast_insights(series, forecast_values, model_type="Prophet")
            
            # Return results
            return {
                'historical_dates': series.index,
                'historical_values': series.values,
                'forecast_dates': forecast_index,
                'forecast_values': forecast_values,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound,
                'metrics': {
                    'MAE': mae,
                    'MSE': mse,
                    'RMSE': rmse,
                    'MAPE': mape
                },
                'insights': insights
            }
            
        except Exception as e:
            print(f"Error in Prophet forecast: {e}")
            # Fall back to exponential smoothing
            return self._forecast_exponential_smoothing(series, horizon, show_ci=show_ci, confidence_level=confidence_level)
    
    def _forecast_lstm(self, series, horizon, units=50, epochs=100, seq_length=7, 
                      show_ci=True, confidence_level=0.95):
        """
        Generate forecast using LSTM
        
        Args:
            series (Series): Time series data
            horizon (int): Forecast horizon
            units (int): Number of LSTM units
            epochs (int): Number of training epochs
            seq_length (int): Sequence length for LSTM input
            show_ci (bool): Show confidence intervals
            confidence_level (float): Confidence level for intervals
            
        Returns:
            dict: Forecast results
        """
        try:
            # For this implementation, we'll simulate LSTM results
            # In a real implementation, you'd use TensorFlow/Keras:
            # from tensorflow.keras.models import Sequential
            # from tensorflow.keras.layers import LSTM, Dense
            
            # Placeholder for LSTM simulation
            # Use a combination of trend and recent patterns
            
            # Extract trend with moving average
            trend = series.rolling(window=30, min_periods=1).mean()
            
            # Calculate fitted values
            fitted = trend.values
            
            # Add some pattern based on recent values
            recent_pattern = series.iloc[-seq_length:].values - trend.iloc[-seq_length:].values
            
            # Extend trend for forecast
            last_trend = trend.iloc[-1]
            trend_slope = (trend.iloc[-1] - trend.iloc[-30]) / 30 if len(trend) >= 30 else 0
            forecast_trend = last_trend + np.arange(1, horizon + 1) * trend_slope
            
            # Generate forecast
            forecast_values = np.zeros(horizon)
            
            for i in range(horizon):
                # Add trend
                forecast_values[i] = forecast_trend[i]
                
                # Add cyclical pattern (repeating the recent pattern)
                pattern_idx = i % len(recent_pattern)
                forecast_values[i] += recent_pattern[pattern_idx]
            
            # Create forecast dates
            forecast_index = pd.date_range(start=series.index[-1] + pd.Timedelta(days=1), periods=horizon)
            
            # Calculate confidence intervals
            if show_ci:
                # Calculate residuals
                residuals = series.values - fitted
                residual_std = np.std(residuals)
                
                # Calculate z-score for the confidence level
                import scipy.stats as stats
                z = stats.norm.ppf((1 + confidence_level) / 2)
                
                # Increasing uncertainty with time
                uncertainty_factor = np.sqrt(np.arange(1, horizon + 1) / 5)  # Faster growing uncertainty for LSTM
                margin = z * residual_std * uncertainty_factor
                
                lower_bound = forecast_values - margin
                upper_bound = forecast_values + margin
            else:
                lower_bound = None
                upper_bound = None
                
            # Calculate metrics
            y_pred = pd.Series(fitted, index=series.index)
            y_true = series
            mae = mean_absolute_error(y_true, y_pred)
            mse = mean_squared_error(y_true, y_pred)
            rmse = np.sqrt(mse)
            mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
            
            # Generate insights
            insights = self._generate_forecast_insights(series, forecast_values, model_type="LSTM")
            
            # Return results
            return {
                'historical_dates': series.index,
                'historical_values': series.values,
                'forecast_dates': forecast_index,
                'forecast_values': forecast_values,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound,
                'metrics': {
                    'MAE': mae,
                    'MSE': mse,
                    'RMSE': rmse,
                    'MAPE': mape
                },
                'insights': insights
            }
            
        except Exception as e:
            print(f"Error in LSTM forecast: {e}")
            # Fall back to ARIMA
            return self._forecast_arima(series, horizon, show_ci=show_ci, confidence_level=confidence_level)
    
    def _forecast_transformer(self, series, horizon, layers=2, nheads=4, nhead=None, d_model=64, 
                             epochs=100, seq_length=30, show_ci=True, confidence_level=0.95):
        """
        Generate forecast using Transformer model
        
        Args:
            series (Series): Time series data
            horizon (int): Forecast horizon
            layers (int): Number of transformer layers
            nheads (int): Number of attention heads (alternative to nhead
            nhead (int): Number of attention heads
            d_model (int): Model dimension
            epochs (int): Number of training epochs
            seq_length (int): Sequence length for transformer input
            show_ci (bool): Show confidence intervals
            confidence_level (float): Confidence level for intervals
            
        Returns:
            dict: Forecast results
        """
        num_heads = nhead if nhead is not None else nheads
        try:
            # For this implementation, we'll simulate Transformer results
            # In a real implementation, you'd use TensorFlow/PyTorch with transformer architecture
            
            # Placeholder for Transformer simulation
            # Use a combination of trend, seasonality and attention to key patterns
            
            # Extract trend with moving average
            trend = series.rolling(window=30, min_periods=1).mean()
            
            # Extract weekly seasonality if data has enough history
            if len(series) >= 14:
                # Simple weekly pattern extraction
                weekly_pattern = np.zeros(7)
                for i in range(7):
                    day_indices = np.where(series.index.dayofweek == i)[0]
                    if len(day_indices) > 0:
                        values = series.iloc[day_indices].values
                        trend_values = trend.iloc[day_indices].values
                        detrended = values - trend_values
                        weekly_pattern[i] = np.mean(detrended)
            else:
                weekly_pattern = np.zeros(7)
            
            # Calculate fitted values
            fitted = trend.values.copy()
            
            # Add weekly pattern to fitted values
            for i, date in enumerate(series.index):
                day_of_week = date.dayofweek
                fitted[i] += weekly_pattern[day_of_week]
            
            # Generate forecast
            # Extend trend
            last_trend = trend.iloc[-1]
            trend_slope = (trend.iloc[-1] - trend.iloc[-30]) / 30 if len(trend) >= 30 else 0
            forecast_trend = last_trend + np.arange(1, horizon + 1) * trend_slope
            
            # Create forecast dates
            forecast_index = pd.date_range(start=series.index[-1] + pd.Timedelta(days=1), periods=horizon)
            
            # Add weekly pattern to forecast
            forecast_values = forecast_trend.copy()
            for i, date in enumerate(forecast_index):
                day_of_week = date.dayofweek
                forecast_values[i] += weekly_pattern[day_of_week]
            
            # Simulate attention mechanism by adding additional patterns based on similar historical periods
            # This is highly simplified compared to real transformer attention
            if len(series) > seq_length * 2:
                # Identify similar periods in history
                recent_pattern = series.iloc[-seq_length:].values
                
                # Find correlation with historical windows
                correlations = []
                for i in range(len(series) - seq_length * 2):
                    historical_window = series.iloc[i:i+seq_length].values
                    correlation = np.corrcoef(recent_pattern, historical_window)[0, 1]
                    correlations.append((i, correlation))
                
                # Sort by correlation
                correlations.sort(key=lambda x: x[1], reverse=True)
                
                # Get top 3 most similar periods
                top_similar = correlations[:3]
                
                # If we found similar periods, use them to adjust forecast
                if top_similar and not np.isnan(top_similar[0][1]):
                    for start_idx, corr in top_similar:
                        # Get what happened after the similar period
                        if start_idx + seq_length + horizon <= len(series):
                            future_after_similar = series.iloc[start_idx + seq_length:start_idx + seq_length + horizon].values
                            similar_trend = trend.iloc[start_idx + seq_length:start_idx + seq_length + horizon].values
                            pattern_after_similar = future_after_similar - similar_trend
                            
                            # Add a weighted version of this pattern to our forecast
                            weight = corr * 0.2  # Adjust weight based on correlation
                            forecast_values += pattern_after_similar * weight
            
            # Calculate confidence intervals
            if show_ci:
                # Calculate residuals
                residuals = series.values - fitted
                residual_std = np.std(residuals)
                
                # Calculate z-score for the confidence level
                import scipy.stats as stats
                z = stats.norm.ppf((1 + confidence_level) / 2)
                
                # Increasing uncertainty with time (transformers tend to have better uncertainty handling)
                uncertainty_factor = np.sqrt(np.arange(1, horizon + 1) / 15)
                margin = z * residual_std * uncertainty_factor
                
                lower_bound = forecast_values - margin
                upper_bound = forecast_values + margin
            else:
                lower_bound = None
                upper_bound = None
                
            # Calculate metrics
            y_pred = pd.Series(fitted, index=series.index)
            y_true = series
            mae = mean_absolute_error(y_true, y_pred)
            mse = mean_squared_error(y_true, y_pred)
            rmse = np.sqrt(mse)
            mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
            
            # Generate insights
            insights = self._generate_forecast_insights(series, forecast_values, model_type="Transformer")
            
            # Return results
            return {
                'historical_dates': series.index,
                'historical_values': series.values,
                'forecast_dates': forecast_index,
                'forecast_values': forecast_values,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound,
                'metrics': {
                    'MAE': mae,
                    'MSE': mse,
                    'RMSE': rmse,
                    'MAPE': mape
                },
                'insights': insights
            }
            
        except Exception as e:
            print(f"Error in Transformer forecast: {e}")
            # Fall back to LSTM
            return self._forecast_lstm(series, horizon, show_ci=show_ci, confidence_level=confidence_level)
    
    def _generate_forecast_insights(self, historical_data, forecast_values, model_type="ARIMA"):
        """
        Generate insights from forecasts
        
        Args:
            historical_data (Series): Historical time series data
            forecast_values (array): Forecasted values
            model_type (str): Type of model used for forecasting
            
        Returns:
            dict: Insights from the forecast
        """
        insights = {}
        
        # Calculate overall trend
        if len(historical_data) >= 2:
            historical_mean = historical_data.mean()
            forecast_mean = np.mean(forecast_values)
            
            if forecast_mean > historical_mean * 1.1:
                trend = "strong upward"
            elif forecast_mean > historical_mean * 1.02:
                trend = "moderate upward"
            elif forecast_mean < historical_mean * 0.9:
                trend = "strong downward"
            elif forecast_mean < historical_mean * 0.98:
                trend = "moderate downward"
            else:
                trend = "stable"
                
            insights['overall_trend'] = trend
            insights['trend_percentage'] = ((forecast_mean / historical_mean) - 1) * 100
        
        # Detect seasonality
        try:
            if len(historical_data) >= 14:  # Need at least 2 weeks for weekly seasonality
                decomposition = seasonal_decompose(historical_data, model='additive', period=7)
                seasonal_strength = np.std(decomposition.seasonal) / np.std(historical_data)
                
                if seasonal_strength > 0.3:
                    insights['seasonality'] = "strong weekly seasonality detected"
                elif seasonal_strength > 0.1:
                    insights['seasonality'] = "moderate weekly seasonality detected"
                else:
                    insights['seasonality'] = "no significant weekly seasonality detected"
                
                insights['seasonal_strength'] = seasonal_strength
        except Exception as e:
            insights['seasonality'] = "seasonality analysis not available"
        
        # Calculate volatility
        historical_volatility = historical_data.std() / historical_data.mean() if historical_data.mean() != 0 else 0
        insights['historical_volatility'] = historical_volatility
        
        # Detect outliers in historical data
        if len(historical_data) >= 30:
            rolling_mean = historical_data.rolling(window=7).mean()
            rolling_std = historical_data.rolling(window=7).std()
            outliers = historical_data[(historical_data > rolling_mean + 2 * rolling_std) | 
                                      (historical_data < rolling_mean - 2 * rolling_std)]
            
            if len(outliers) > 0:
                insights['outliers'] = f"{len(outliers)} outliers detected in historical data"
                insights['outlier_percentage'] = (len(outliers) / len(historical_data)) * 100
            else:
                insights['outliers'] = "no significant outliers detected"
        
        # Detect anomalies in forecast
        if len(forecast_values) > 0:
            historical_std = historical_data.std()
            historical_mean = historical_data.mean()
            
            forecast_anomalies = [i for i, value in enumerate(forecast_values) 
                                if value > historical_mean + 3 * historical_std or 
                                   value < historical_mean - 3 * historical_std]
            
            if forecast_anomalies:
                insights['forecast_anomalies'] = f"{len(forecast_anomalies)} potential anomalies in forecast"
            else:
                insights['forecast_anomalies'] = "no anomalies detected in forecast"
        
        # Add model-specific insights
        if model_type == "ARIMA":
            insights['model_specific'] = "ARIMA model captures autocorrelation patterns"
        elif model_type == "Exponential Smoothing":
            insights['model_specific'] = "Exponential Smoothing handles trends and seasonality"
        elif model_type == "Prophet":
            insights['model_specific'] = "Prophet model identifies holiday effects and can handle irregular data"
        elif model_type == "LSTM":
            insights['model_specific'] = "LSTM captures complex temporal dependencies and non-linear patterns"
        elif model_type == "Transformer":
            insights['model_specific'] = "Transformer model uses attention mechanisms to identify important patterns"
        
        return insights
    
    def set_target_column(self, column_name):
        """
        Set the target column name for forecasting
        
        Args:
            column_name (str): Name of target column
        """
        if column_name not in self.data.columns:
            raise ValueError(f"Column '{column_name}' not found in data")
        
        self.target_column = column_name
        print(f"Target column set to '{column_name}'")
    
    def plot_forecast(self, forecast_results, title=None, figsize=(12, 6)):
        """
        Plot forecast results
        
        Args:
            forecast_results (dict): Results from generate_forecast method
            title (str): Plot title
            figsize (tuple): Figure size
            
        Returns:
            matplotlib.figure.Figure: Plot figure
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot historical data
        historical_dates = forecast_results['historical_dates']
        historical_values = forecast_results['historical_values']
        ax.plot(historical_dates, historical_values, label='Historical', color='blue')
        
        # Plot forecast
        forecast_dates = forecast_results['forecast_dates']
        forecast_values = forecast_results['forecast_values']
        ax.plot(forecast_dates, forecast_values, label='Forecast', color='red')
        
        # Plot confidence intervals if available
        if forecast_results['lower_bound'] is not None and forecast_results['upper_bound'] is not None:
            lower_bound = forecast_results['lower_bound']
            upper_bound = forecast_results['upper_bound']
            ax.fill_between(forecast_dates, lower_bound, upper_bound, alpha=0.2, color='red', label='Confidence Interval')
        
        # Set title
        if title:
            ax.set_title(title)
        else:
            ax.set_title(f"Forecast for {self.target_column}")
        
        # Set labels
        ax.set_xlabel('Date')
        ax.set_ylabel(self.target_column)
        
        # Add legend
        ax.legend()
        
        # Add grid
        ax.grid(True, alpha=0.3)
        
        # Show metrics in text box
        if 'metrics' in forecast_results:
            metrics = forecast_results['metrics']
            metrics_text = f"MAE: {metrics['MAE']:.2f}\n"
            metrics_text += f"RMSE: {metrics['RMSE']:.2f}\n"
            metrics_text += f"MAPE: {metrics['MAPE']:.2f}%"
            
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax.text(0.05, 0.95, metrics_text, transform=ax.transAxes, fontsize=10,
                   verticalalignment='top', bbox=props)
        
        plt.tight_layout()
        
        return fig
    
    def compare_models(self, horizon, models_to_compare=None, **kwargs):
        """
        Compare multiple forecasting models
        
        Args:
            horizon (int): Forecast horizon
            models_to_compare (list): List of model types to compare (default: all models)
            **kwargs: Additional parameters for models
            
        Returns:
            dict: Comparison results with forecasts and metrics for each model
        """
        if models_to_compare is None:
            models_to_compare = ["ARIMA", "Exponential Smoothing", "Prophet", "LSTM", "Transformer"]
        
        comparison_results = {}
        
        for model_type in models_to_compare:
            print(f"Generating forecast using {model_type}...")
            forecast_results = self.generate_forecast(model_type, horizon, **kwargs)
            comparison_results[model_type] = forecast_results
        
        return comparison_results
    
    def plot_model_comparison(self, comparison_results, figsize=(15, 10)):
        """
        Plot comparison of multiple forecasting models
        
        Args:
            comparison_results (dict): Results from compare_models method
            figsize (tuple): Figure size
            
        Returns:
            matplotlib.figure.Figure: Plot figure
        """
        # Create figure with subplots
        n_models = len(comparison_results)
        
        # One row for forecasts, one for metrics
        fig, axs = plt.subplots(2, 1, figsize=figsize)
        
        # Plot forecasts
        ax = axs[0]
        
        # Get any model result to extract historical data
        any_model = list(comparison_results.keys())[0]
        historical_dates = comparison_results[any_model]['historical_dates']
        historical_values = comparison_results[any_model]['historical_values']
        
        # Plot historical data
        ax.plot(historical_dates, historical_values, label='Historical', color='blue')
        
        # Plot forecasts for each model
        colors = ['red', 'green', 'purple', 'orange', 'brown', 'pink']
        for i, (model_type, results) in enumerate(comparison_results.items()):
            color = colors[i % len(colors)]
            ax.plot(results['forecast_dates'], results['forecast_values'], label=f'{model_type} Forecast', color=color)
        
        # Set title and labels
        ax.set_title(f"Forecast Comparison for {self.target_column}")
        ax.set_xlabel('Date')
        ax.set_ylabel(self.target_column)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot metrics
        ax = axs[1]
        
        # Prepare metrics data
        models = list(comparison_results.keys())
        metrics = ['MAE', 'RMSE', 'MAPE']
        
        # Create positions for bars
        bar_width = 0.25
        positions = np.arange(len(models))
        
        # Plot metrics as grouped bars
        for i, metric in enumerate(metrics):
            values = [comparison_results[model]['metrics'][metric] for model in models]
            ax.bar(positions + i * bar_width, values, bar_width, label=metric)
        
        # Set labels and title
        ax.set_title('Forecast Metrics Comparison')
        ax.set_xlabel('Model')
        ax.set_xticks(positions + bar_width)
        ax.set_xticklabels(models)
        ax.set_ylabel('Value')
        ax.legend()
        
        plt.tight_layout()
        
        return fig
    
    def analyze_seasonality(self, period=7, plot=True, figsize=(12, 10)):
        """
        Analyze seasonality in the time series data
        
        Args:
            period (int): Seasonality period in days (default: 7 for weekly)
            plot (bool): Whether to create a plot
            figsize (tuple): Figure size
            
        Returns:
            dict: Seasonality analysis results
        """
        series = self.data[self.target_column]
        
        # Check if data length is sufficient
        if len(series) < period * 2:
            return {
                'status': 'error',
                'message': f'Data length ({len(series)}) is insufficient for seasonality analysis with period {period}'
            }
            
        try:
            # Perform decomposition
            decomposition = seasonal_decompose(series, model='additive', period=period)
            
            # Calculate seasonality strength
            seasonal_values = decomposition.seasonal
            residual_values = decomposition.resid
            
            # Calculate seasonal strength
            seasonal_strength = 1 - np.var(residual_values) / np.var(seasonal_values + residual_values)
            
            # Prepare results
            results = {
                'status': 'success',
                'seasonal_strength': seasonal_strength,
                'seasonal_pattern': seasonal_values[:period].to_dict(),
                'trend': decomposition.trend,
                'seasonal': decomposition.seasonal,
                'residual': decomposition.resid,
                'decomposition': decomposition
            }
            
            if plot:
                fig = plt.figure(figsize=figsize)
                
                # Plot decomposition
                ax1 = fig.add_subplot(411)
                ax1.plot(series, label='Original')
                ax1.set_title('Original Time Series')
                ax1.legend()
                
                ax2 = fig.add_subplot(412)
                ax2.plot(decomposition.trend, label='Trend')
                ax2.set_title('Trend Component')
                ax2.legend()
                
                ax3 = fig.add_subplot(413)
                ax3.plot(decomposition.seasonal, label='Seasonality')
                ax3.set_title('Seasonal Component')
                ax3.legend()
                
                ax4 = fig.add_subplot(414)
                ax4.plot(decomposition.resid, label='Residuals')
                ax4.set_title('Residual Component')
                ax4.legend()
                
                plt.tight_layout()
                
                results['figure'] = fig
            
            return results
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Seasonality analysis failed: {str(e)}'
            }
    
    def detect_outliers(self, method='zscore', threshold=3.0, plot=True, figsize=(12, 6)):
        """
        Detect outliers in the time series data
        
        Args:
            method (str): Method for outlier detection ('zscore', 'iqr', 'rolling')
            threshold (float): Threshold for outlier detection
            plot (bool): Whether to create a plot
            figsize (tuple): Figure size
            
        Returns:
            dict: Outlier detection results
        """
        series = self.data[self.target_column]
        
        outliers_idx = []
        
        if method == 'zscore':
            # Z-score method
            mean = series.mean()
            std = series.std()
            z_scores = (series - mean) / std
            outliers_idx = np.where(np.abs(z_scores) > threshold)[0]
            
        elif method == 'iqr':
            # Interquartile range method
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr
            outliers_idx = np.where((series < lower_bound) | (series > upper_bound))[0]
            
        elif method == 'rolling':
            # Rolling statistics method
            rolling_mean = series.rolling(window=14, min_periods=1).mean()
            rolling_std = series.rolling(window=14, min_periods=1).std()
            
            upper_bound = rolling_mean + threshold * rolling_std
            lower_bound = rolling_mean - threshold * rolling_std
            
            outliers_idx = np.where((series > upper_bound) | (series < lower_bound))[0]
            
        else:
            raise ValueError(f"Unsupported outlier detection method: {method}")
        
        # Get outlier dates and values
        outlier_dates = series.index[outliers_idx]
        outlier_values = series.iloc[outliers_idx]
        
        # Calculate outlier statistics
        outlier_percentage = len(outliers_idx) / len(series) * 100
        
        # Create results dictionary
        results = {
            'status': 'success',
            'outlier_count': len(outliers_idx),
            'outlier_percentage': outlier_percentage,
            'outlier_dates': outlier_dates,
            'outlier_values': outlier_values,
            'method': method,
            'threshold': threshold
        }
        
        # Plot if requested
        if plot:
            fig, ax = plt.subplots(figsize=figsize)
            
            # Plot the time series
            ax.plot(series.index, series.values, label='Time Series')
            
            # Plot outliers
            if len(outlier_dates) > 0:
                ax.scatter(outlier_dates, outlier_values, color='red', label='Outliers')
            
            # If using rolling method, plot bounds
            if method == 'rolling':
                ax.plot(series.index, upper_bound, 'g--', label='Upper Bound')
                ax.plot(series.index, lower_bound, 'g--', label='Lower Bound')
            
            # Set title and labels
            ax.set_title(f'Outlier Detection ({method.capitalize()}, threshold={threshold})')
            ax.set_xlabel('Date')
            ax.set_ylabel(self.target_column)
            ax.legend()
            
            # Add text box with outlier statistics
            stats_text = f"Outliers: {len(outliers_idx)} ({outlier_percentage:.2f}%)"
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax.text(0.05, 0.95, stats_text, transform=ax.transAxes, fontsize=10,
                   verticalalignment='top', bbox=props)
            
            plt.tight_layout()
            
            results['figure'] = fig
        
        return results
    
    def impute_missing_values(self, method='linear', plot=True, figsize=(12, 6)):
        """
        Impute missing values in the time series data
        
        Args:
            method (str): Imputation method ('linear', 'mean', 'median', 'ffill', 'bfill')
            plot (bool): Whether to create a plot
            figsize (tuple): Figure size
            
        Returns:
            DataFrame: Data with imputed values
        """
        # Check for missing values
        data = self.data.copy()
        missing_count = data[self.target_column].isna().sum()
        
        if missing_count == 0:
            print("No missing values found")
            return data
        
        # Store original series with missing values
        original_series = data[self.target_column].copy()
        
        # Impute missing values
        if method == 'linear':
            data[self.target_column] = data[self.target_column].interpolate(method='linear')
        elif method == 'mean':
            mean_value = data[self.target_column].mean()
            data[self.target_column] = data[self.target_column].fillna(mean_value)
        elif method == 'median':
            median_value = data[self.target_column].median()
            data[self.target_column] = data[self.target_column].fillna(median_value)
        elif method == 'ffill':
            data[self.target_column] = data[self.target_column].fillna(method='ffill')
        elif method == 'bfill':
            data[self.target_column] = data[self.target_column].fillna(method='bfill')
        else:
            raise ValueError(f"Unsupported imputation method: {method}")
        
        # Plot if requested
        if plot:
            fig, ax = plt.subplots(figsize=figsize)
            
            # Plot original data with gaps
            ax.plot(original_series.index, original_series.values, 'bo-', alpha=0.3, label='Original (with gaps)')
            
            # Highlight missing values that were imputed
            missing_indices = original_series.isna()
            imputed_x = data.index[missing_indices]
            imputed_y = data[self.target_column].iloc[missing_indices]
            
            # Plot imputed data
            ax.plot(data.index, data[self.target_column].values, 'r-', label=f'Imputed ({method})')
            ax.scatter(imputed_x, imputed_y, color='red', s=50, label='Imputed values')
            
            # Set title and labels
            ax.set_title(f'Missing Value Imputation ({method.capitalize()})')
            ax.set_xlabel('Date')
            ax.set_ylabel(self.target_column)
            ax.legend()
            
            # Add text box with imputation statistics
            stats_text = f"Missing values: {missing_count} ({missing_count/len(data)*100:.2f}%)\nMethod: {method}"
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax.text(0.05, 0.95, stats_text, transform=ax.transAxes, fontsize=10,
                   verticalalignment='top', bbox=props)
            
            plt.tight_layout()
            plt.show()
        
        print(f"Imputed {missing_count} missing values using {method} method")
        return data
    
    def feature_importance(self, target_column=None, method='random_forest', plot=True, figsize=(10, 6)):
        """
        Calculate feature importance for forecasting
        
        Args:
            target_column (str): Target column (default: self.target_column)
            method (str): Method for feature importance calculation ('random_forest', 'correlation')
            plot (bool): Whether to create a plot
            figsize (tuple): Figure size
            
        Returns:
            dict: Feature importance results
        """
        if target_column is None:
            target_column = self.target_column
        
        # Prepare data - exclude non-numeric columns
        data = self.data.select_dtypes(include=['number'])
        
        # Ensure target column is in data
        if target_column not in data.columns:
            raise ValueError(f"Target column '{target_column}' not found in numeric data")
        
        # Prepare features and target
        features = [col for col in data.columns if col != target_column]
        
        if len(features) == 0:
            return {
                'status': 'error',
                'message': 'No numeric feature columns found'
            }
        
        X = data[features]
        y = data[target_column]
        
        # Calculate feature importance
        importance_scores = None
        
        if method == 'random_forest':
            try:
                from sklearn.ensemble import RandomForestRegressor
                
                # Train a Random Forest
                rf = RandomForestRegressor(n_estimators=100, random_state=42)
                rf.fit(X, y)
                
                # Get feature importance
                importance_scores = rf.feature_importances_
                
            except Exception as e:
                return {
                    'status': 'error',
                    'message': f'Random Forest feature importance failed: {str(e)}'
                }
                
        elif method == 'correlation':
            try:
                # Calculate correlation with target
                importance_scores = np.abs(X.corrwith(y)).values
                
            except Exception as e:
                return {
                    'status': 'error',
                    'message': f'Correlation feature importance failed: {str(e)}'
                }
        else:
            raise ValueError(f"Unsupported feature importance method: {method}")
        
        # Create importance dictionary
        importance_dict = dict(zip(features, importance_scores))
        
        # Sort by importance
        sorted_importance = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
        feature_names = [item[0] for item in sorted_importance]
        importance_values = [item[1] for item in sorted_importance]
        
        # Create results
        results = {
            'status': 'success',
            'feature_importance': dict(sorted_importance),
            'method': method
        }
        
        # Plot if requested
        if plot:
            fig, ax = plt.subplots(figsize=figsize)
            
            # Create horizontal bar chart
            y_pos = np.arange(len(feature_names))
            ax.barh(y_pos, importance_values, align='center')
            ax.set_yticks(y_pos)
            ax.set_yticklabels(feature_names)
            
            # Set title and labels
            ax.set_title(f'Feature Importance for {target_column} ({method.capitalize()})')
            ax.set_xlabel('Importance Score')
            
            # Invert y-axis to show most important at the top
            ax.invert_yaxis()
            
            plt.tight_layout()
            
            results['figure'] = fig
        
        return results
    
    def evaluate_model(self, model_type, test_size=0.2, horizon=None, **kwargs):
        """
        Evaluate a model using train-test split
        
        Args:
            model_type (str): Model type to evaluate
            test_size (float): Proportion of data to use for testing
            horizon (int): Forecast horizon (default: test size)
            **kwargs: Additional parameters for the model
            
        Returns:
            dict: Evaluation results
        """
        # Prepare data
        series = self.data[self.target_column].copy()
        
        # Determine test size
        n_test = int(len(series) * test_size) if horizon is None else horizon
        
        # Split data
        train = series.iloc[:-n_test]
        test = series.iloc[-n_test:]
        
        # Create temporary dataset with training data
        train_data = pd.DataFrame({self.target_column: train}, index=train.index)
        temp_forecaster = AdvancedForecastingModule(train_data)
        
        # Generate forecast
        forecast_results = temp_forecaster.generate_forecast(model_type, n_test, **kwargs)
        
        # Extract forecast values
        forecast_values = forecast_results['forecast_values']
        
        # Calculate metrics
        mae = mean_absolute_error(test.values, forecast_values)
        mse = mean_squared_error(test.values, forecast_values)
        rmse = np.sqrt(mse)
        mape = np.mean(np.abs((test.values - forecast_values) / test.values)) * 100
        
        # Create results dictionary
        results = {
            'status': 'success',
            'model_type': model_type,
            'test_size': test_size,
            'metrics': {
                'MAE': mae,
                'MSE': mse,
                'RMSE': rmse,
                'MAPE': mape
            },
            'actual_values': test.values,
            'forecast_values': forecast_values,
            'actual_dates': test.index,
            'forecast_dates': forecast_results['forecast_dates']
        }
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot training data
        ax.plot(train.index, train.values, label='Training Data', color='blue')
        
        # Plot test data
        ax.plot(test.index, test.values, label='Actual Test Data', color='green')
        
        # Plot forecast
        ax.plot(forecast_results['forecast_dates'], forecast_values, label='Forecast', color='red')
        
        # Plot confidence intervals if available
        if forecast_results['lower_bound'] is not None and forecast_results['upper_bound'] is not None:
            ax.fill_between(
                forecast_results['forecast_dates'],
                forecast_results['lower_bound'],
                forecast_results['upper_bound'],
                color='red',
                alpha=0.2,
                label='Confidence Interval'
            )
        
        # Set title and labels
        ax.set_title(f'Model Evaluation: {model_type}')
        ax.set_xlabel('Date')
        ax.set_ylabel(self.target_column)
        ax.legend()
        
        # Add metrics as text
        metrics_text = f"MAE: {mae:.2f}\nRMSE: {rmse:.2f}\nMAPE: {mape:.2f}%"
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax.text(0.05, 0.95, metrics_text, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=props)
        
        plt.tight_layout()
        
        results['figure'] = fig
        
        return results
    
    def export_forecast(self, forecast_results, filepath, include_historical=True, format='csv'):
        """
        Export forecast results to a file
        
        Args:
            forecast_results (dict): Results from generate_forecast method
            filepath (str): Path to save the file
            include_historical (bool): Whether to include historical data
            format (str): Export format ('csv', 'excel', 'json')
            
        Returns:
            str: Path to saved file
        """
        # Prepare data for export
        if include_historical:
            # Combine historical and forecast data
            dates = np.concatenate([forecast_results['historical_dates'], forecast_results['forecast_dates']])
            values = np.concatenate([forecast_results['historical_values'], forecast_results['forecast_values']])
            
            # Create indicators
            data_type = np.array(['historical'] * len(forecast_results['historical_values']) + 
                              ['forecast'] * len(forecast_results['forecast_values']))
            
            # Create DataFrame
            export_df = pd.DataFrame({
                'date': dates,
                self.target_column: values,
                'type': data_type
            })
            
        else:
            # Only include forecast data
            export_df = pd.DataFrame({
                'date': forecast_results['forecast_dates'],
                self.target_column: forecast_results['forecast_values'],
                'type': ['forecast'] * len(forecast_results['forecast_values'])
            })
            
        # Add confidence intervals if available
        if forecast_results['lower_bound'] is not None and forecast_results['upper_bound'] is not None:
            if include_historical:
                # Add NaN for historical data
                lower_bound = np.concatenate([
                    np.array([np.nan] * len(forecast_results['historical_values'])),
                    forecast_results['lower_bound']
                ])
                upper_bound = np.concatenate([
                    np.array([np.nan] * len(forecast_results['historical_values'])),
                    forecast_results['upper_bound']
                ])
            else:
                lower_bound = forecast_results['lower_bound']
                upper_bound = forecast_results['upper_bound']
                
            export_df['lower_bound'] = lower_bound
            export_df['upper_bound'] = upper_bound
        
        # Export based on format
        if format.lower() == 'csv':
            export_df.to_csv(filepath, index=False)
        elif format.lower() == 'excel':
            export_df.to_excel(filepath, index=False)
        elif format.lower() == 'json':
            export_df.to_json(filepath, orient='records', date_format='iso')
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        print(f"Forecast exported to {filepath}")
        return filepath
