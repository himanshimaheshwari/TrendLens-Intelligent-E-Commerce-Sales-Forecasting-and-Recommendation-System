from advanced_forecasting import AdvancedForecastingModule
from advanced_analytics import AdvancedAnalytics
from cross_platform_analyzer import CrossPlatformAnalyzer, RecommendationEngine
from enhanced_gui import TrendLensGUI
from tableau_integration import TableauIntegration
from recommendation_page import _create_recommendations_tab, _generate_recs, _add_recommendation_content, _export_recommendations
from forecasting_page import _create_forecasting_tab, _run_forecast, _display_forecast_results, _export_forecast_results
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from advanced_forecasting_module import AdvancedForecastingModule
from recommendation_page_implementation import RecommendationEngine

class TrendLensApp(tk.Tk):
    """
    Main application window for the TrendLens E-Commerce Analyzer
    """
    def __init__(self):
        super().__init__()
        
        # Configure main window
        self.title("TrendLens E-Commerce Analyzer")
        self.geometry("1200x800")
        self.configure(bg="#f5f5f5")
        
        # Initialize platform data
        self.platform_data = {
            'Meesho': {'data': None, 'analyzer': None},
            'Flipkart': {'data': None, 'analyzer': None},
            'Amazon': {'data': None, 'analyzer': None}
        }
        
        # Create UI components
        self._create_menu()
        self._create_main_frame()
        self._create_forecasting_tab()
        self._create_recommendations_tab()

    def get_transaction_data(self):
        return self.platform_data['Meesho']['data']  # Replace with actual source

    def get_customer_data(self):
        return self.platform_data['Amazon']['data']  # Replace with actual source
    

    def _create_menu(self):
        """Create application menu bar"""
        menubar = tk.Menu(self)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Load Data", command=self._load_data_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Export to Tableau", command=self._export_to_tableau)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Analysis menu
        analysis_menu = tk.Menu(menubar, tearoff=0)
        analysis_menu.add_command(label="Basic Statistics", command=self._show_basic_stats)
        analysis_menu.add_command(label="Time Series Analysis", command=self._run_time_series_analysis)
        analysis_menu.add_command(label="Cross-Platform Comparison", command=self._run_platform_comparison)
        analysis_menu.add_command(label="Advanced Models", command=self._run_advanced_models)
        menubar.add_cascade(label="Analysis", menu=analysis_menu)
        
        # Recommendations menu
        recommendations_menu = tk.Menu(menubar, tearoff=0)
        recommendations_menu.add_command(label="Generate Recommendations", command=self._generate_recommendations)
        recommendations_menu.add_command(label="Performance Insights", command=self._show_performance_insights)
        menubar.add_cascade(label="Recommendations", menu=recommendations_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Documentation", command=self._show_documentation)
        help_menu.add_command(label="About", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.config(menu=menubar)
    
    def _create_main_frame(self):
        """Create main frame with notebook for different views"""
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Dashboard tab
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        self._create_dashboard()
        
        # Analysis tab
        self.analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_frame, text="Analysis")
        self._create_analysis_tab()
        
        # Forecasting tab
        self.forecasting_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.forecasting_frame, text="Forecasting")
        
        # Recommendations tab
        self.recommendations_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.recommendations_frame, text="Recommendations")
    
    def _create_dashboard(self):
        """Create the dashboard view"""
        # Platform selection frame
        platform_frame = ttk.LabelFrame(self.dashboard_frame, text="Platforms")
        platform_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Platform checkboxes
        self.platform_vars = {}
        for i, platform in enumerate(['Meesho', 'Flipkart', 'Amazon']):
            self.platform_vars[platform] = tk.BooleanVar(value=False)
            cb = ttk.Checkbutton(platform_frame, text=platform, variable=self.platform_vars[platform])
            cb.grid(row=0, column=i, padx=20, pady=5)
        
        # Status section
        status_frame = ttk.LabelFrame(self.dashboard_frame, text="Data Status")
        status_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.status_labels = {}
        for i, platform in enumerate(['Meesho', 'Flipkart', 'Amazon']):
            ttk.Label(status_frame, text=f"{platform}:").grid(row=i, column=0, sticky=tk.W, padx=10, pady=5)
            self.status_labels[platform] = ttk.Label(status_frame, text="No data loaded")
            self.status_labels[platform].grid(row=i, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Visualization section
        viz_frame = ttk.LabelFrame(self.dashboard_frame, text="Quick Visualization")
        viz_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        fig = plt.Figure(figsize=(8, 6))
        self.ax = fig.add_subplot(111)
        self.ax.set_title("Sales Trends")
        self.ax.set_xlabel("Date")
        self.ax.set_ylabel("Sales")
        self.ax.text(0.5, 0.5, "No data loaded", 
                    horizontalalignment='center',
                    verticalalignment='center',
                    transform=self.ax.transAxes)
        
        canvas = FigureCanvasTkAgg(fig, master=viz_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_analysis_tab(self):
        """Create the Analysis tab UI and functionality"""
        # Split frame into control panel and visualization area
        control_frame = ttk.Frame(self.analysis_frame)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        viz_frame = ttk.Frame(self.analysis_frame)
        viz_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Analysis type selection
        ttk.Label(control_frame, text="Analysis Type:").pack(anchor=tk.W, pady=(0, 5))
        analysis_types = ["Time Series Decomposition", "Correlation Analysis", 
                        "Platform Comparison", "Seasonality Analysis"]
        analysis_var = tk.StringVar(value=analysis_types[0])
        analysis_combo = ttk.Combobox(control_frame, textvariable=analysis_var, values=analysis_types)
        analysis_combo.pack(fill=tk.X, pady=(0, 15))
        
        # Platform selection
        ttk.Label(control_frame, text="Platforms to Analyze:").pack(anchor=tk.W, pady=(0, 5))
        platform_selections = {}
        for platform in ['Meesho', 'Flipkart', 'Amazon']:
            platform_selections[platform] = tk.BooleanVar(value=True)
            ttk.Checkbutton(control_frame, text=platform, 
                           variable=platform_selections[platform]).pack(anchor=tk.W)
        
        # Parameters frame
        params_frame = ttk.LabelFrame(control_frame, text="Parameters")
        params_frame.pack(fill=tk.X, pady=15)
        
        # Time window
        ttk.Label(params_frame, text="Time Window:").pack(anchor=tk.W, padx=5, pady=(5, 0))
        time_options = ["All Data", "Last 30 Days", "Last 90 Days", "Last Year"]
        time_var = tk.StringVar(value=time_options[0])
        ttk.Combobox(params_frame, textvariable=time_var, values=time_options).pack(
            fill=tk.X, padx=5, pady=5)
        
        # Advanced options toggle
        advanced_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(params_frame, text="Show Advanced Options", 
                       variable=advanced_var).pack(anchor=tk.W, padx=5, pady=5)
        
        # Action buttons
        ttk.Button(control_frame, text="Run Analysis", 
                  command=lambda: self._execute_analysis(
                      analysis_var.get(), 
                      [p for p, v in platform_selections.items() if v.get()], 
                      time_var.get(),
                      advanced_var.get(),
                      viz_frame)).pack(fill=tk.X, pady=(15, 5))
        
        ttk.Button(control_frame, text="Export Results", 
                  command=self._export_analysis_results).pack(fill=tk.X, pady=5)
        
        # Initial visualization area setup
        fig = plt.Figure(figsize=(8, 6))
        self.analysis_ax = fig.add_subplot(111)
        self.analysis_ax.set_title("Analysis Results")
        self.analysis_ax.text(0.5, 0.5, "Run an analysis to see results", 
                             horizontalalignment='center',
                             verticalalignment='center',
                             transform=self.analysis_ax.transAxes)
        
        self.analysis_canvas = FigureCanvasTkAgg(fig, master=viz_frame)
        self.analysis_canvas.draw()
        self.analysis_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Results text area (hidden initially)
        self.analysis_text = tk.Text(viz_frame, height=10, width=50)
        self.analysis_text.pack(fill=tk.X, expand=False, pady=10)
        self.analysis_text.pack_forget()  # Hide initially

    def _execute_analysis(self, analysis_type, platforms, time_window, show_advanced, viz_frame):
      """Execute the selected analysis type"""
      # Check if data is available for selected platforms
      valid_platforms = []
      for platform in platforms:
          if self.platform_data[platform]['data'] is not None:
              valid_platforms.append(platform)
      
      if not valid_platforms:
          messagebox.showwarning("No Data", "No data available for selected platforms.")
          return
      
      # Clear previous visualizations by destroying any existing canvas
      for widget in viz_frame.winfo_children():
          widget.destroy()
      
      # Hide text results initially
      if hasattr(self, 'analysis_text'):
          self.analysis_text.pack_forget()
          
      # Create new text widget for results if needed
      self.analysis_text = tk.Text(viz_frame, height=10, width=50)
      self.analysis_text.pack(fill=tk.X, expand=False, pady=10)
      self.analysis_text.pack_forget()  # Hide initially
      
      # Create an instance of AdvancedAnalytics
      advanced_analytics = AdvancedAnalytics(data_manager=self)

      # Prepare data for analysis
      analysis_data = {}
      for platform in valid_platforms:
          analyzer = self.platform_data[platform]['analyzer']
          if analyzer is None:
              continue  # Skip if analyzer is None
          if analyzer.processed_data is None:
              analyzer.preprocess_data()
          analysis_data[platform] = analyzer.processed_data
      
      # Create new figure for visualization
      fig = plt.Figure(figsize=(10, 6))
      
      # Perform selected analysis
      if analysis_type == "Time Series Decomposition":
          # Get first platform for decomposition
          if not valid_platforms:
              messagebox.showwarning("No Data", "No valid platforms with data available.")
              return
              
          platform = valid_platforms[0]
          
          # Determine period based on time window
          period = 12 if time_window == "All Data" else 7
          
          # Perform decomposition
          try:
              results = advanced_analytics.perform_time_series_decomposition(
                  analysis_data[platform], 
                  period=period)
              
              # Create figure with subplots for decomposition
              fig, axes = plt.subplots(4, 1, figsize=(10, 8), sharex=True)
              
              # Plot each component
              axes[0].plot(results.observed)
              axes[0].set_title('Observed')
              axes[0].set_ylabel('Value')
              
              axes[1].plot(results.trend)
              axes[1].set_title('Trend')
              axes[1].set_ylabel('Value')
              
              axes[2].plot(results.seasonal)
              axes[2].set_title('Seasonal')
              axes[2].set_ylabel('Value')
              
              axes[3].plot(results.resid)
              axes[3].set_title('Residual')
              axes[3].set_ylabel('Value')
              axes[3].set_xlabel('Date')
              
              plt.tight_layout()
              
              # Create new canvas with the figure
              self.analysis_canvas = FigureCanvasTkAgg(fig, master=viz_frame)
              self.analysis_canvas.draw()
              self.analysis_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
              
              # Store the axes for export
              self.analysis_ax = axes
              
          except Exception as e:
              messagebox.showerror("Analysis Error", f"Error performing decomposition: {str(e)}")
              return
      
      elif analysis_type == "Correlation Analysis":
          # Create new figure and axis
          fig = plt.Figure(figsize=(10, 6))
          self.analysis_ax = fig.add_subplot(111)
          
          # Plot correlation heatmap for first platform
          sns.heatmap(analysis_data[valid_platforms[0]].corr(), 
                    ax=self.analysis_ax, annot=True, cmap='coolwarm', fmt=".2f")
          self.analysis_ax.set_title(f"Correlation Heatmap - {valid_platforms[0]}")
          
          # Create canvas
          self.analysis_canvas = FigureCanvasTkAgg(fig, master=viz_frame)
          self.analysis_canvas.draw()
          self.analysis_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
          
          # Show text results for correlations
          self.analysis_text.pack(fill=tk.X, expand=False, pady=10)
          self.analysis_text.delete(1.0, tk.END)
          
          for platform in valid_platforms:
              corr_results = advanced_analytics.calculate_correlations(analysis_data[platform])
              self.analysis_text.insert(tk.END, f"\n{platform} Correlation Analysis:\n")
              self.analysis_text.insert(tk.END, f"{corr_results}\n\n")
      
      elif analysis_type == "Platform Comparison":
          # Create new figure and axis
          fig = plt.Figure(figsize=(10, 6))
          self.analysis_ax = fig.add_subplot(111)
          
          # Use CrossPlatformAnalyzer
          platform_analyzers = [self.platform_data[p]['analyzer'] for p in valid_platforms if self.platform_data[p]['analyzer'] is not None]
          
          try:
              cross_analyzer = CrossPlatformAnalyzer(platform_analyzers)
              
              # First, align the platform data
              cross_analyzer.align_platform_data()
              
              # Generate comparison results text
              comparison_results = "Platform Comparison Summary:\n\n"
              
              # Add correlation information
              try:
                  correlation_matrix = cross_analyzer.compute_correlations()
                  comparison_results += "Correlation Analysis:\n" + str(correlation_matrix) + "\n\n"
              except Exception as e:
                  comparison_results += f"Could not compute correlations: {str(e)}\n\n"
              
              # Add growth trend information
              try:
                  growth_trends = cross_analyzer.identify_growth_trends()
                  comparison_results += "Growth Trends:\n" + str(growth_trends) + "\n\n"
              except Exception as e:
                  comparison_results += f"Could not identify growth trends: {str(e)}\n\n"
              
              # Add recommendations if available
              try:
                  recommendations = cross_analyzer.generate_recommendations()
                  comparison_results += "Key Recommendations:\n"
                  for key, rec in recommendations.items():
                      if 'insight' in rec:
                          comparison_results += f"- {rec['insight']}\n"
              except Exception as e:
                  comparison_results += f"Could not generate recommendations: {str(e)}\n\n"
              
              # Plot comparison of aligned data
              if cross_analyzer.aligned_data is not None:
                  for platform in cross_analyzer.aligned_data.columns:
                      self.analysis_ax.plot(cross_analyzer.aligned_data.index, 
                                          cross_analyzer.aligned_data[platform], 
                                          label=platform)
              else:
                  # Fallback to direct plotting if alignment failed
                  for platform in valid_platforms:
                      self.analysis_ax.plot(analysis_data[platform]['sales'], label=platform)
              
              self.analysis_ax.set_title("Sales Comparison Across Platforms")
              self.analysis_ax.set_xlabel("Date")
              self.analysis_ax.set_ylabel("Sales")
              self.analysis_ax.legend()
              
              # Create canvas
              self.analysis_canvas = FigureCanvasTkAgg(fig, master=viz_frame)
              self.analysis_canvas.draw()
              self.analysis_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
              
              # Show detailed comparison in text
              self.analysis_text.pack(fill=tk.X, expand=False, pady=10)
              self.analysis_text.delete(1.0, tk.END)
              self.analysis_text.insert(tk.END, comparison_results)
              
          except Exception as e:
              # Handle exceptions
              self.analysis_ax.text(0.5, 0.5, f"Error in platform comparison: {str(e)}", 
                                  ha='center', va='center')
              self.analysis_canvas = FigureCanvasTkAgg(fig, master=viz_frame)
              self.analysis_canvas.draw()
              self.analysis_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
      
      elif analysis_type == "Seasonality Analysis":
          # Create new figure and axis
          fig = plt.Figure(figsize=(10, 6))
          self.analysis_ax = fig.add_subplot(111)
          
          # Use the season analysis method from CrossPlatformAnalyzer if possible
          platform_analyzers = [self.platform_data[p]['analyzer'] for p in valid_platforms if self.platform_data[p]['analyzer'] is not None]
          
          try:
              cross_analyzer = CrossPlatformAnalyzer(platform_analyzers)
              seasonal_patterns = cross_analyzer.analyze_seasonal_patterns()
              
              # Plot monthly patterns
              monthly_patterns = seasonal_patterns['monthly']
              for platform in monthly_patterns.columns:
                  self.analysis_ax.plot(monthly_patterns.index, monthly_patterns[platform], label=platform)
                  
              self.analysis_ax.set_title("Monthly Seasonal Patterns")
              self.analysis_ax.set_xlabel("Month")
              self.analysis_ax.set_ylabel("Average Sales")
              self.analysis_ax.set_xticks(range(1, 13))
              self.analysis_ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
              self.analysis_ax.legend()
              
              # Create canvas
              self.analysis_canvas = FigureCanvasTkAgg(fig, master=viz_frame)
              self.analysis_canvas.draw()
              self.analysis_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
              
              # Show detailed seasonality info in text
              self.analysis_text.pack(fill=tk.X, expand=False, pady=10)
              self.analysis_text.delete(1.0, tk.END)
              self.analysis_text.insert(tk.END, "Seasonal Analysis Results:\n\n")
              
              # Weekly patterns
              self.analysis_text.insert(tk.END, "Weekly Patterns:\n")
              self.analysis_text.insert(tk.END, str(seasonal_patterns['weekly']) + "\n\n")
              
              # Monthly patterns
              self.analysis_text.insert(tk.END, "Monthly Patterns:\n")
              self.analysis_text.insert(tk.END, str(seasonal_patterns['monthly']) + "\n\n")
              
          except Exception as e:
              # Fallback to original approach for seasonality
              for platform in valid_platforms:
                  seasonal = advanced_analytics.extract_seasonality(
                      analysis_data[platform]['sales'])
                  self.analysis_ax.plot(seasonal, label=platform)
              
              self.analysis_ax.set_title("Seasonal Patterns Comparison")
              self.analysis_ax.set_xlabel("Season")
              self.analysis_ax.set_ylabel("Seasonal Effect")
              self.analysis_ax.legend()
              
              # Create canvas
              self.analysis_canvas = FigureCanvasTkAgg(fig, master=viz_frame)
              self.analysis_canvas.draw()
              self.analysis_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
              
              # Show error in text
              self.analysis_text.pack(fill=tk.X, expand=False, pady=10)
              self.analysis_text.delete(1.0, tk.END)
              self.analysis_text.insert(tk.END, f"Error using advanced seasonality analysis: {str(e)}\n")
              self.analysis_text.insert(tk.END, "Falling back to basic seasonality extraction.")
      
      # Update the canvas
      if analysis_type != "Time Series Decomposition":  # Already updated for decomposition
          self.analysis_canvas.draw()

    def _export_analysis_results(self):
        """Export analysis results to file"""
        # Check if analysis has been run
        if hasattr(self, 'analysis_ax') and not hasattr(self.analysis_ax, '_no_data'):
            # Ask for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
            )
            
            if file_path:
                # Save figure
                self.analysis_ax.figure.savefig(file_path, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Export Complete", "Analysis results saved successfully!")
        else:
            messagebox.showwarning("No Results", "Run an analysis first before exporting.")
        
    def _load_data_dialog(self):
        """Show dialog to load data for a specific platform"""
        # Create platform selection dialog
        load_dialog = tk.Toplevel(self)
        load_dialog.title("Load Platform Data")
        load_dialog.geometry("400x200")
        load_dialog.resizable(False, False)
        
        ttk.Label(load_dialog, text="Select Platform:").pack(pady=(20, 5))
        
        platform_var = tk.StringVar(value="Meesho")
        platform_combo = ttk.Combobox(load_dialog, textvariable=platform_var)
        platform_combo['values'] = ('Meesho', 'Flipkart', 'Amazon')
        platform_combo.pack(pady=5)
        
        ttk.Button(load_dialog, text="Browse for CSV file", 
                  command=lambda: self._browse_for_file(platform_var.get(), load_dialog)).pack(pady=20)
    
    def _browse_for_file(self, platform, dialog):
        """Browse for CSV file and load it for selected platform"""
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Create analyzer instance for the platform
                analyzer = TrendLensECommerceAnalyzer(platform, file_path)
                data = analyzer.load_data()
                
                if data is not None:
                    self.platform_data[platform]['data'] = data
                    self.platform_data[platform]['analyzer'] = analyzer
                    self.platform_vars[platform].set(True)
                    self.status_labels[platform].config(text=f"Loaded {len(data)} records")
                    
                    # Close dialog
                    dialog.destroy()
                    
                    # Update dashboard
                    self._update_dashboard()
                    
                    messagebox.showinfo("Success", f"Data for {platform} loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load data: {str(e)}")
    
    def _update_dashboard(self):
        """Update dashboard visualizations"""
        self.ax.clear()
        
        # Plot data for each loaded platform
        legend_items = []
        
        for platform, platform_info in self.platform_data.items():
            if platform_info['data'] is not None and self.platform_vars[platform].get():
                analyzer = platform_info['analyzer']
                
                if analyzer.processed_data is None:
                    analyzer.preprocess_data()
                
                if analyzer.processed_data is not None:
                    sales_data = analyzer.processed_data['sales']
                    self.ax.plot(sales_data.index, sales_data, label=platform)
                    legend_items.append(platform)
        
        if legend_items:
            self.ax.set_title("Sales Trends Comparison")
            self.ax.set_xlabel("Date")
            self.ax.set_ylabel("Sales")
            self.ax.legend(legend_items)
        else:
            self.ax.text(0.5, 0.5, "No data loaded or selected", 
                        horizontalalignment='center',
                        verticalalignment='center')
        
        # Redraw the figure
        self.ax.figure.canvas.draw()
    
    def _export_to_tableau(self):
        """Export data for Tableau integration"""
        # Check if any data is loaded
        has_data = any(platform['data'] is not None for platform in self.platform_data.values())
        
        if not has_data:
            messagebox.showwarning("No Data", "Please load data for at least one platform first.")
            return
        
        # Ask for export directory
        export_dir = filedialog.askdirectory(title="Select Export Directory")
        
        if export_dir:
            export_count = 0
            
            for platform, platform_info in self.platform_data.items():
                if platform_info['data'] is not None:
                    analyzer = platform_info['analyzer']
                    
                    # Ensure data is processed
                    if analyzer.processed_data is None:
                        analyzer.preprocess_data()
                    
                    if analyzer.processed_data is not None:
                        # Export processed data
                        export_file = os.path.join(export_dir, f"{platform}_processed.csv")
                        analyzer.processed_data.to_csv(export_file)
                        export_count += 1
            
            if export_count > 0:
                messagebox.showinfo("Export Complete", 
                                   f"Successfully exported {export_count} datasets for Tableau.")
            else:
                messagebox.showwarning("Export Failed", "No processed data available for export.")
    
    def _show_basic_stats(self):
        """Show basic statistics for selected platforms"""
        # Check if any platform is selected
        selected = [p for p, v in self.platform_vars.items() if v.get()]
        
        if not selected:
            messagebox.showwarning("No Selection", "Please select at least one platform.")
            return
        
        # Create stats dialog
        stats_dialog = tk.Toplevel(self)
        stats_dialog.title("Basic Statistics")
        stats_dialog.geometry("800x600")
        
        # Create text widget for output
        text_frame = ttk.Frame(stats_dialog)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, height=25, width=80)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        # Display stats for each selected platform
        for platform in selected:
            if self.platform_data[platform]['analyzer'] is not None:
                analyzer = self.platform_data[platform]['analyzer']
                
                # Make sure data is processed
                if analyzer.processed_data is None:
                    analyzer.preprocess_data()
                
                if analyzer.processed_data is not None:
                    text_widget.insert(tk.END, f"\n{'='*80}\n")
                    text_widget.insert(tk.END, f"  STATISTICS FOR {platform.upper()}\n")
                    text_widget.insert(tk.END, f"{'='*80}\n\n")
                    
                    # Basic stats
                    stats = analyzer.processed_data['sales'].describe()
                    text_widget.insert(tk.END, "Sales Statistics:\n\n")
                    for stat, value in stats.items():
                        text_widget.insert(tk.END, f"{stat}: {value:.2f}\n")
                    
                    text_widget.insert(tk.END, f"\nTotal Records: {len(analyzer.processed_data)}\n")
                    text_widget.insert(tk.END, f"Date Range: {analyzer.processed_data.index.min()} to {analyzer.processed_data.index.max()}\n\n")
        
        # Make text widget read-only
        text_widget.configure(state='disabled')
    
    def _run_time_series_analysis(self):
        """Placeholder for time series analysis function"""
        messagebox.showinfo("Coming Soon", "Time Series Analysis module is under development")
    
    def _run_platform_comparison(self):
        """Placeholder for platform comparison function"""
        messagebox.showinfo("Coming Soon", "Cross-Platform Comparison module is under development")
    
    def _run_advanced_models(self):
        """Placeholder for advanced models function"""
        messagebox.showinfo("Coming Soon", "Advanced Models module is under development")
    
    def _generate_recommendations(self):
        """Placeholder for recommendations generation function"""
        messagebox.showinfo("Coming Soon", "Recommendations module is under development")
    
    def _show_performance_insights(self):
        """Placeholder for performance insights function"""
        messagebox.showinfo("Coming Soon", "Performance Insights module is under development")
    
    def _show_documentation(self):
        """Show application documentation"""
        doc_dialog = tk.Toplevel(self)
        doc_dialog.title("TrendLens Documentation")
        doc_dialog.geometry("800x600")
        
        text_frame = ttk.Frame(doc_dialog)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, height=25, width=80)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        # Insert documentation text
        text_widget.insert(tk.END, """
        TrendLens E-Commerce Analyzer Documentation
        ==========================================
        
        This application allows for advanced analysis of e-commerce sales data across
        multiple platforms (Meesho, Flipkart, and Amazon).
        
        Getting Started
        --------------
        1. Load data for one or more platforms using File → Load Data
        2. Select platforms to visualize in the dashboard
        3. Use the analysis menu to perform different types of analysis
        
        Features
        --------
        - Time series visualization and analysis
        - Cross-platform performance comparison
        - Advanced forecasting models including transformers
        - Actionable recommendations for business decisions
        - Tableau integration for advanced visualization
        
        For more information, please refer to the full documentation.
        """)
        
        # Make text widget read-only
        text_widget.configure(state='disabled')
    
    def _show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About TrendLens",
                           "TrendLens E-Commerce Analyzer\nVersion 2.0\n\n" +
                           "An advanced analytics tool for e-commerce platforms")


class TrendLensECommerceAnalyzer:
    def __init__(self, platform_name, file_path):
        """
        🚀 Initialize the TrendLens Analyzer for a specific e-commerce platform

        Args:
            platform_name (str): Name of the e-commerce platform
            file_path (str): Path to the dataset
        """
        self.platform_name = platform_name
        self.file_path = file_path
        self.raw_data = None
        self.processed_data = None
        self.model = None
        self.forecast_results = None

    def load_data(self):
        """
        📂 Load data with platform-specific handling
        """
        try:
            # Load data
            self.raw_data = pd.read_csv(self.file_path)

            # Platform-specific column mapping
            if self.platform_name == 'Meesho':
                # Use order_date for date, price for sales
                self.raw_data = self.raw_data.rename(columns={
                    'order_date': 'date',
                    'price': 'sales'
                })
            elif self.platform_name == 'Flipkart':
                # Use crawl_timestamp for date, discounted_price for sales
                self.raw_data = self.raw_data.rename(columns={
                    'crawl_timestamp': 'date',
                    'discounted_price': 'sales'
                })
            elif self.platform_name == 'Amazon':
                # Use Date for date, Amount for sales
                self.raw_data = self.raw_data.rename(columns={
                    'Date': 'date',
                    'Amount': 'sales'
                })

            # Convert date column
            self.raw_data['date'] = pd.to_datetime(self.raw_data['date'], errors='coerce')

            # Convert sales to numeric
            self.raw_data['sales'] = pd.to_numeric(self.raw_data['sales'], errors='coerce')

            # Remove rows with invalid dates or sales
            self.raw_data.dropna(subset=['date', 'sales'], inplace=True)

            print(f"\n📊 {self.platform_name} Data Loading Report:")
            print(f"📈 Total Rows: {len(self.raw_data)}")
            print("🔍 Columns:", list(self.raw_data.columns))
            print("\n🏁 First few rows:")
            print(self.raw_data.head())

            return self.raw_data

        except Exception as e:
            print(f"❌ Error loading {self.platform_name} data: {e}")
            return None

    def preprocess_data(self):
        """
        🔧 Advanced data preprocessing with comprehensive feature engineering
        """
        # Check if data is loaded
        if self.raw_data is None:
            print("❗ No data to preprocess. Load data first.")
            return None

        # Group by date and aggregate sales
        processed_data = self.raw_data.groupby('date')['sales'].sum().reset_index()

        # Set date as index
        processed_data.set_index('date', inplace=True)
        processed_data.sort_index(inplace=True)

        # Handle missing values
        processed_data['sales'] = processed_data['sales'].ffill()

        # Feature Engineering
        # Lag features
        processed_data['sales_lag_1'] = processed_data['sales'].shift(1)
        processed_data['sales_lag_3'] = processed_data['sales'].shift(3)
        processed_data['sales_lag_6'] = processed_data['sales'].shift(6)

        # Rolling statistics
        processed_data['rolling_mean_3'] = processed_data['sales'].rolling(window=3).mean()
        processed_data['rolling_std_3'] = processed_data['sales'].rolling(window=3).std()

        # Percentage change
        processed_data['pct_change'] = processed_data['sales'].pct_change()

        # Remove initial NA values from feature engineering
        processed_data.dropna(inplace=True)

        self.processed_data = processed_data

        # Preprocessing Report
        print(f"\n🧩 {self.platform_name} Preprocessing Report:")
        print(f"🔢 Processed Rows: {len(processed_data)}")
        print("✨ Engineered Features:", list(processed_data.columns))

        return processed_data

    # Note: Other methods from the original class (visualize_data, 
    # perform_stationarity_test, etc.) would be included here
    # They are omitted for brevity in this initial setup
TrendLensApp._create_recommendations_tab = _create_recommendations_tab
TrendLensApp._generate_recs = _generate_recs
TrendLensApp._add_recommendation_content = _add_recommendation_content
TrendLensApp._export_recommendations = _export_recommendations

TrendLensApp._create_forecasting_tab = _create_forecasting_tab
TrendLensApp._run_forecast = _run_forecast
TrendLensApp._display_forecast_results = _display_forecast_results
TrendLensApp._export_forecast_results = _export_forecast_results


if __name__ == "__main__":
    app = TrendLensApp()
    app.mainloop()
