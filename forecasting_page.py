import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from advanced_forecasting_module import AdvancedForecastingModule

def _create_forecasting_tab(self):
    """Create the Forecasting tab UI and functionality"""
    # Split frame into control panel and visualization area
    control_frame = ttk.Frame(self.forecasting_frame)
    control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
    
    viz_frame = ttk.Frame(self.forecasting_frame)
    viz_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Platform selection
    ttk.Label(control_frame, text="Platform:").pack(anchor=tk.W, pady=(0, 5))
    platform_var = tk.StringVar(value='Meesho')
    platform_combo = ttk.Combobox(control_frame, textvariable=platform_var)
    platform_combo['values'] = tuple([p for p in self.platform_data.keys() 
                                    if self.platform_data[p]['data'] is not None])
    platform_combo.pack(fill=tk.X, pady=(0, 15))
    
    # Forecasting model selection
    ttk.Label(control_frame, text="Forecasting Model:").pack(anchor=tk.W, pady=(0, 5))
    model_var = tk.StringVar(value="ARIMA")
    models = ["ARIMA", "Exponential Smoothing", "Prophet", "LSTM", "Transformer"]
    model_combo = ttk.Combobox(control_frame, textvariable=model_var, values=models)
    model_combo.pack(fill=tk.X, pady=(0, 15))
    
    # Forecast horizon
    ttk.Label(control_frame, text="Forecast Horizon (days):").pack(anchor=tk.W, pady=(0, 5))
    horizon_var = tk.IntVar(value=30)
    horizon_spinbox = ttk.Spinbox(control_frame, from_=1, to=365, textvariable=horizon_var)
    horizon_spinbox.pack(fill=tk.X, pady=(0, 15))
    
    # Parameters frame
    params_frame = ttk.LabelFrame(control_frame, text="Model Parameters")
    params_frame.pack(fill=tk.X, pady=15)
    
    # Configuration for different models
    self.model_config_frames = {}
    
    # ARIMA parameters
    arima_frame = ttk.Frame(params_frame)
    ttk.Label(arima_frame, text="p:").grid(row=0, column=0, padx=5, pady=5)
    p_var = tk.IntVar(value=1)
    ttk.Spinbox(arima_frame, from_=0, to=10, width=5, textvariable=p_var).grid(row=0, column=1)
    
    ttk.Label(arima_frame, text="d:").grid(row=0, column=2, padx=5, pady=5)
    d_var = tk.IntVar(value=1)
    ttk.Spinbox(arima_frame, from_=0, to=2, width=5, textvariable=d_var).grid(row=0, column=3)
    
    ttk.Label(arima_frame, text="q:").grid(row=0, column=4, padx=5, pady=5)
    q_var = tk.IntVar(value=1)
    ttk.Spinbox(arima_frame, from_=0, to=10, width=5, textvariable=q_var).grid(row=0, column=5)
    
    ttk.Label(arima_frame, text="Auto-ARIMA:").grid(row=1, column=0, columnspan=2, padx=5, pady=5)
    auto_arima_var = tk.BooleanVar(value=True)
    ttk.Checkbutton(arima_frame, variable=auto_arima_var).grid(row=1, column=2)
    
    self.model_config_frames["ARIMA"] = arima_frame
    
    # Exponential Smoothing parameters
    exp_frame = ttk.Frame(params_frame)
    ttk.Label(exp_frame, text="Trend:").grid(row=0, column=0, padx=5, pady=5)
    trend_var = tk.StringVar(value="add")
    ttk.Combobox(exp_frame, values=["add", "mul", "None"], textvariable=trend_var, width=10).grid(
        row=0, column=1)
    
    ttk.Label(exp_frame, text="Seasonal:").grid(row=0, column=2, padx=5, pady=5)
    seasonal_var = tk.StringVar(value="add")
    ttk.Combobox(exp_frame, values=["add", "mul", "None"], textvariable=seasonal_var, width=10).grid(
        row=0, column=3)
    
    ttk.Label(exp_frame, text="Period:").grid(row=1, column=0, padx=5, pady=5)
    period_var = tk.IntVar(value=7)
    ttk.Spinbox(exp_frame, from_=1, to=52, width=10, textvariable=period_var).grid(row=1, column=1)
    
    self.model_config_frames["Exponential Smoothing"] = exp_frame
    
    # Prophet parameters
    prophet_frame = ttk.Frame(params_frame)
    ttk.Label(prophet_frame, text="Yearly Seasonality:").grid(row=0, column=0, padx=5, pady=5)
    yearly_var = tk.BooleanVar(value=True)
    ttk.Checkbutton(prophet_frame, variable=yearly_var).grid(row=0, column=1)
    
    ttk.Label(prophet_frame, text="Weekly Seasonality:").grid(row=1, column=0, padx=5, pady=5)
    weekly_var = tk.BooleanVar(value=True)
    ttk.Checkbutton(prophet_frame, variable=weekly_var).grid(row=1, column=1)
    
    ttk.Label(prophet_frame, text="Daily Seasonality:").grid(row=2, column=0, padx=5, pady=5)
    daily_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(prophet_frame, variable=daily_var).grid(row=2, column=1)
    
    self.model_config_frames["Prophet"] = prophet_frame
    
    # LSTM parameters
    lstm_frame = ttk.Frame(params_frame)
    ttk.Label(lstm_frame, text="Units:").grid(row=0, column=0, padx=5, pady=5)
    units_var = tk.IntVar(value=50)
    ttk.Spinbox(lstm_frame, from_=10, to=200, width=10, textvariable=units_var).grid(row=0, column=1)
    
    ttk.Label(lstm_frame, text="Epochs:").grid(row=1, column=0, padx=5, pady=5)
    epochs_var = tk.IntVar(value=100)
    ttk.Spinbox(lstm_frame, from_=10, to=500, width=10, textvariable=epochs_var).grid(row=1, column=1)
    
    ttk.Label(lstm_frame, text="Sequence Length:").grid(row=0, column=2, padx=5, pady=5)
    seq_var = tk.IntVar(value=7)
    ttk.Spinbox(lstm_frame, from_=1, to=30, width=10, textvariable=seq_var).grid(row=0, column=3)
    
    self.model_config_frames["LSTM"] = lstm_frame
    
    # Transformer parameters
    transformer_frame = ttk.Frame(params_frame)
    ttk.Label(transformer_frame, text="d_model:").grid(row=0, column=0, padx=5, pady=5)
    d_model_var = tk.IntVar(value=64)
    ttk.Spinbox(transformer_frame, from_=16, to=256, width=10, textvariable=d_model_var).grid(row=0, column=1)
    
    ttk.Label(transformer_frame, text="nhead:").grid(row=0, column=2, padx=5, pady=5)
    nhead_var = tk.IntVar(value=8)
    ttk.Spinbox(transformer_frame, from_=1, to=16, width=10, textvariable=nhead_var).grid(row=0, column=3)
    
    ttk.Label(transformer_frame, text="Num Layers:").grid(row=1, column=0, padx=5, pady=5)
    num_layers_var = tk.IntVar(value=3)
    ttk.Spinbox(transformer_frame, from_=1, to=12, width=10, textvariable=num_layers_var).grid(row=1, column=1)
    
    ttk.Label(transformer_frame, text="Epochs:").grid(row=1, column=2, padx=5, pady=5)
    tr_epochs_var = tk.IntVar(value=100)
    ttk.Spinbox(transformer_frame, from_=10, to=500, width=10, textvariable=tr_epochs_var).grid(row=1, column=3)
    
    self.model_config_frames["Transformer"] = transformer_frame
    
    # Show relevant configuration frame based on model selection
    def show_model_config(*args):
        for frame_name, frame in self.model_config_frames.items():
            if frame_name == model_var.get():
                frame.pack(fill=tk.X, padx=5, pady=5)
            else:
                frame.pack_forget()
    
    model_var.trace("w", show_model_config)
    show_model_config()  # Show initial configuration
    
    # Confidence interval settings
    ci_frame = ttk.Frame(control_frame)
    ci_frame.pack(fill=tk.X, pady=15)
    
    ttk.Label(ci_frame, text="Show Confidence Interval:").grid(row=0, column=0, sticky=tk.W)
    ci_var = tk.BooleanVar(value=True)
    ttk.Checkbutton(ci_frame, variable=ci_var).grid(row=0, column=1)
    
    ttk.Label(ci_frame, text="Confidence Level:").grid(row=1, column=0, sticky=tk.W)
    cl_var = tk.DoubleVar(value=0.95)
    ttk.Combobox(ci_frame, values=[0.80, 0.90, 0.95, 0.99], textvariable=cl_var, width=10).grid(row=1, column=1)
    
    # Create variable dictionary for passing parameters
    self.forecast_params = {
        'platform_var': platform_var,
        'model_var': model_var,
        'horizon_var': horizon_var,
        'ci_var': ci_var,
        'cl_var': cl_var,
        # ARIMA params
        'p_var': p_var, 'd_var': d_var, 'q_var': q_var, 'auto_arima_var': auto_arima_var,
        # Exponential Smoothing params
        'trend_var': trend_var, 'seasonal_var': seasonal_var, 'period_var': period_var,
        # Prophet params
        'yearly_var': yearly_var, 'weekly_var': weekly_var, 'daily_var': daily_var,
        # LSTM params
        'units_var': units_var, 'epochs_var': epochs_var, 'seq_var': seq_var,
        # Transformer params
        'd_model_var': d_model_var, 'nhead_var': nhead_var, 
        'num_layers_var': num_layers_var, 'tr_epochs_var': tr_epochs_var
    }
    
    # Action buttons
    ttk.Button(control_frame, text="Run Forecast", 
              command=lambda: self._run_forecast(viz_frame)).pack(fill=tk.X, pady=(15, 5))
    
    ttk.Button(control_frame, text="Export Forecast", 
              command=self._export_forecast_results).pack(fill=tk.X, pady=5)
    
    # Initial visualization area setup
    fig = plt.Figure(figsize=(8, 6))
    self.forecast_ax = fig.add_subplot(111)
    self.forecast_ax.set_title("Forecast Results")
    self.forecast_ax.text(0.5, 0.5, "Configure and run a forecast to see results", 
                         horizontalalignment='center',
                         verticalalignment='center',
                         transform=self.forecast_ax.transAxes)
    
    self.forecast_canvas = FigureCanvasTkAgg(fig, master=viz_frame)
    self.forecast_canvas.draw()
    self.forecast_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    # Results text area
    self.forecast_text = tk.Text(viz_frame, height=10, width=50)
    self.forecast_text.pack(fill=tk.X, expand=False, pady=10)
    self.forecast_text.pack_forget()  # Hide initially

def _run_forecast(self, viz_frame):
    """Run the selected forecasting model and display results"""
    # Get selected platform
    platform = self.forecast_params['platform_var'].get()
    model_type = self.forecast_params['model_var'].get()
    horizon = self.forecast_params['horizon_var'].get()
    
    # Check if data is available
    if self.platform_data[platform]['data'] is None:
        messagebox.showwarning("No Data", f"No data available for {platform}. Please load data first.")
        return
    
    # Get platform analyzer
    analyzer = self.platform_data[platform]['analyzer']
    
    # Make sure data is processed
    if analyzer.processed_data is None:
        analyzer.preprocess_data()
    
    if analyzer.processed_data is None:
        messagebox.showerror("Error", "Failed to process data. Cannot generate forecast.")
        return
    
    # Prepare forecast parameters based on selected model
    forecast_config = {}
    
    if model_type == "ARIMA":
        forecast_config = {
            'p': self.forecast_params['p_var'].get(),
            'd': self.forecast_params['d_var'].get(),
            'q': self.forecast_params['q_var'].get(),
            'auto': self.forecast_params['auto_arima_var'].get()
        }
    elif model_type == "Exponential Smoothing":
        forecast_config = {
            'trend': self.forecast_params['trend_var'].get(),
            'seasonal': self.forecast_params['seasonal_var'].get(),
            'period': self.forecast_params['period_var'].get()
        }
    elif model_type == "Prophet":
        forecast_config = {
            'yearly_seasonality': self.forecast_params['yearly_var'].get(),
            'weekly_seasonality': self.forecast_params['weekly_var'].get(),
            'daily_seasonality': self.forecast_params['daily_var'].get()
        }
    elif model_type == "LSTM":
        forecast_config = {
            'units': self.forecast_params['units_var'].get(),
            'epochs': self.forecast_params['epochs_var'].get(),
            'seq_length': self.forecast_params['seq_var'].get()
        }
    elif model_type == "Transformer":
        forecast_config = {
            'd_model': self.forecast_params['d_model_var'].get(),
            'nhead': self.forecast_params['nhead_var'].get(),
            'layers': self.forecast_params['num_layers_var'].get(),
            'epochs': self.forecast_params['tr_epochs_var'].get()
        }
    
    # Add confidence interval settings
    forecast_config['show_ci'] = self.forecast_params['ci_var'].get()
    forecast_config['confidence_level'] = self.forecast_params['cl_var'].get()
    
    # Create an instance of AdvancedForecastingModule
    forecasting_module = AdvancedForecastingModule(analyzer.processed_data)
    
    try:
        # Show loading indicator
        self.forecast_ax.clear()
        self.forecast_ax.text(0.5, 0.5, f"Generating {model_type} forecast...\nThis may take a moment.", 
                             horizontalalignment='center',
                             verticalalignment='center',
                             transform=self.forecast_ax.transAxes)
        self.forecast_canvas.draw()
        self.update()  # Update the UI
        
        # Run forecast
        forecast_results = forecasting_module.generate_forecast(
            model_type=model_type,
            horizon=horizon,
            **forecast_config
        )
        
        # Store results for export
        self.forecast_results = forecast_results
        
        # Display results
        self._display_forecast_results(forecast_results, platform, model_type)
        
    except Exception as e:
        messagebox.showerror("Forecasting Error", f"Error generating forecast: {str(e)}")
        print(f"Forecasting error details: {e}")

def _display_forecast_results(self, forecast_results, platform, model_type):
    """Display the forecast results in the visualization area"""
    # Clear previous results
    self.forecast_ax.clear()
    
    # Plot historical data
    self.forecast_ax.plot(forecast_results['historical_dates'], forecast_results['historical_values'], 
                         label='Historical Data', color='blue')
    
    # Plot forecast
    self.forecast_ax.plot(forecast_results['forecast_dates'], forecast_results['forecast_values'], 
                         label='Forecast', color='red', linestyle='--')
    
    # Plot confidence intervals if available
    if 'lower_bound' in forecast_results and 'upper_bound' in forecast_results:
        self.forecast_ax.fill_between(forecast_results['forecast_dates'], 
                                     forecast_results['lower_bound'], 
                                     forecast_results['upper_bound'], 
                                     color='red', alpha=0.1, label='Confidence Interval')
    
    # Set labels and title
    self.forecast_ax.set_title(f"{platform} Sales Forecast ({model_type})")
    self.forecast_ax.set_xlabel("Date")
    self.forecast_ax.set_ylabel("Sales")
    self.forecast_ax.legend()
    
    # Format x-axis dates
    self.forecast_ax.figure.autofmt_xdate()
    
    # Redraw canvas
    self.forecast_canvas.draw()
    
    # Display forecast metrics in text area
    self.forecast_text.pack(fill=tk.X, expand=False, pady=10)
    self.forecast_text.delete(1.0, tk.END)
    
    self.forecast_text.insert(tk.END, f"=== {platform} {model_type} Forecast Results ===\n\n")
    
    if 'metrics' in forecast_results:
        self.forecast_text.insert(tk.END, "Performance Metrics:\n")
        for metric, value in forecast_results['metrics'].items():
            self.forecast_text.insert(tk.END, f"- {metric}: {value:.4f}\n")
    
    self.forecast_text.insert(tk.END, f"\nForecast Horizon: {len(forecast_results['forecast_dates'])} days\n")
    self.forecast_text.insert(tk.END, f"Last Historical Date: {forecast_results['historical_dates'][-1].strftime('%Y-%m-%d')}\n")
    self.forecast_text.insert(tk.END, f"Last Forecast Date: {forecast_results['forecast_dates'][-1].strftime('%Y-%m-%d')}\n\n")
    
    # Key insights
    if 'insights' in forecast_results:
        self.forecast_text.insert(tk.END, "Key Insights:\n")
        for insight in forecast_results['insights']:
            self.forecast_text.insert(tk.END, f"- {insight}\n")

def _export_forecast_results(self):
    """Export forecast results to CSV and chart to image file"""
    if not hasattr(self, 'forecast_results') or self.forecast_results is None:
        messagebox.showwarning("No Results", "Please run a forecast first before exporting.")
        return
    
    # Ask for export directory
    export_dir = filedialog.askdirectory(title="Select Export Directory")
    
    if export_dir:
        platform = self.forecast_params['platform_var'].get()
        model_type = self.forecast_params['model_var'].get()
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        
        # Export forecast data to CSV
        csv_path = os.path.join(export_dir, f"{platform}_{model_type}_forecast_{timestamp}.csv")
        
        # Create DataFrame for export
        export_data = pd.DataFrame({
            'Date': self.forecast_results['forecast_dates'],
            'Forecast': self.forecast_results['forecast_values']
        })
        
        if 'lower_bound' in self.forecast_results and 'upper_bound' in self.forecast_results:
            export_data['Lower_Bound'] = self.forecast_results['lower_bound']
            export_data['Upper_Bound'] = self.forecast_results['upper_bound']
        
        export_data.to_csv(csv_path, index=False)
        
        # Export chart to PNG
        img_path = os.path.join(export_dir, f"{platform}_{model_type}_forecast_{timestamp}.png")
        self.forecast_ax.figure.savefig(img_path, dpi=300, bbox_inches='tight')
        
        messagebox.showinfo("Export Complete", 
                           f"Forecast results exported to:\n{csv_path}\n\nChart exported to:\n{img_path}")
