# Step 7: Enhanced GUI Implementation

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
import threading
import webbrowser
from PIL import Image, ImageTk
import io
import plotly.io as pio

class TrendLensGUI:
    def __init__(self, root, data_manager, analytics_engine, tableau_integration):
        """
        Initialize the GUI for TrendLensECommerceAnalyzer
        
        Parameters:
        -----------
        root : tkinter.Tk
            Root window
        data_manager : object
            Data manager instance
        analytics_engine : object
            Analytics engine instance
        tableau_integration : object
            Tableau integration instance
        """
        self.root = root
        self.data_manager = data_manager
        self.analytics_engine = analytics_engine
        self.tableau_integration = tableau_integration
        
        # Set window properties
        self.root.title("TrendLens E-Commerce Analyzer")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Create style object
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use a more modern theme
        
        # Configure colors
        self.bg_color = "#f5f5f5"
        self.accent_color = "#007bff"
        self.text_color = "#333333"
        
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("TLabel", background=self.bg_color, foreground=self.text_color)
        self.style.configure("TButton", background=self.accent_color, foreground="white")
        self.style.map("TButton", background=[("active", "#0069d9")])
        
        # Set root background
        self.root.configure(bg=self.bg_color)
        
        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create navigation sidebar
        self.create_sidebar()
        
        # Create content area
        self.content_frame = ttk.Frame(self.main_container)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Initialize current frame reference
        self.current_frame = None
        
        # Show dashboard initially
        self.show_dashboard()
    
    def create_sidebar(self):
        """Create the navigation sidebar"""
        # Create sidebar frame
        sidebar = ttk.Frame(self.main_container, width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Add logo placeholder
        logo_frame = ttk.Frame(sidebar)
        logo_frame.pack(fill=tk.X, pady=10)
        
        # Create a placeholder logo (would be replaced with actual logo)
        logo_label = ttk.Label(logo_frame, text="TrendLens", font=("Arial", 16, "bold"))
        logo_label.pack(anchor=tk.CENTER)
        
        # Create navigation buttons
        nav_frame = ttk.Frame(sidebar)
        nav_frame.pack(fill=tk.X, pady=20)
        
        # Define navigation buttons
        nav_buttons = [
            ("Dashboard", self.show_dashboard),
            ("Data Import", self.show_data_import),
            ("Advanced Analytics", self.show_advanced_analytics),
            ("Forecasting", self.show_forecasting),
            ("Market Analysis", self.show_market_analysis),
            ("Recommendations", self.show_recommendations),
            ("Tableau Export", self.show_tableau_export),
            ("Settings", self.show_settings)
        ]
        
        # Create and pack buttons
        self.nav_button_style = ttk.Style()
        self.nav_button_style.configure("Nav.TButton", font=("Arial", 12), padding=10)
        
        for text, command in nav_buttons:
            btn = ttk.Button(nav_frame, text=text, command=command, style="Nav.TButton")
            btn.pack(fill=tk.X, pady=5)
        
        # Add help and about buttons at bottom
        bottom_frame = ttk.Frame(sidebar)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)
        
        help_btn = ttk.Button(bottom_frame, text="Help", command=self.show_help)
        help_btn.pack(fill=tk.X, pady=5)
        
        about_btn = ttk.Button(bottom_frame, text="About", command=self.show_about)
        about_btn.pack(fill=tk.X, pady=5)
    
    def clear_content_frame(self):
        """Clear the content frame before showing new content"""
        # Destroy all widgets in the content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Create a new frame for content
        self.current_frame = ttk.Frame(self.content_frame)
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        
        return self.current_frame
    
    def show_dashboard(self):
        """Show the main dashboard"""
        frame = self.clear_content_frame()
        
        # Create header
        header = ttk.Frame(frame)
        header.pack(fill=tk.X, pady=10)
        
        title_label = ttk.Label(header, text="E-Commerce Analytics Dashboard", 
                               font=("Arial", 18, "bold"))
        title_label.pack(side=tk.LEFT, padx=10)
        
        refresh_btn = ttk.Button(header, text="Refresh Data", command=self.refresh_dashboard)
        refresh_btn.pack(side=tk.RIGHT, padx=10)
        
        # Create dashboard content
        content = ttk.Frame(frame)
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create 2x2 grid for dashboard widgets
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)
        content.rowconfigure(1, weight=1)
        
        # Widget 1: Sales Overview
        sales_frame = ttk.LabelFrame(content, text="Sales Overview")
        sales_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # Create a matplotlib figure for the sales chart
        self.create_placeholder_chart(sales_frame, "Monthly Sales Trend")
        
        # Widget 2: Platform Comparison
        platform_frame = ttk.LabelFrame(content, text="Platform Comparison")
        platform_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        self.create_placeholder_chart(platform_frame, "Platform Market Share")
        
        # Widget 3: Recent Recommendations
        rec_frame = ttk.LabelFrame(content, text="Top Recommendations")
        rec_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        rec_tree = ttk.Treeview(rec_frame, columns=("Priority", "Recommendation"), show="headings")
        rec_tree.heading("Priority", text="Priority")
        rec_tree.heading("Recommendation", text="Recommendation")
        rec_tree.column("Priority", width=80)
        rec_tree.column("Recommendation", width=400)
        
        # Add sample recommendations
        sample_recommendations = [
            ("High", "Increase inventory for Product A on Amazon due to predicted demand spike"),
            ("Medium", "Consider price adjustment for Product B on eBay to improve competitiveness"),
            ("Medium", "Investigate declining sales trend for Category C on Shopify"),
            ("Low", "Explore cross-selling opportunities between Products D and E")
        ]
        
        for priority, rec in sample_recommendations:
            rec_tree.insert("", tk.END, values=(priority, rec))
        
        rec_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Widget 4: Key Metrics
        metrics_frame = ttk.LabelFrame(content, text="Key Performance Metrics")
        metrics_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        
        metrics = [
            ("Total Sales", "$1,245,678"),
            ("Growth Rate", "+12.3%"),
            ("Conversion Rate", "3.7%"),
            ("Average Order Value", "$87.50"),
            ("Customer Acquisition Cost", "$22.15")
        ]
        
        for i, (label, value) in enumerate(metrics):
            ttk.Label(metrics_frame, text=label, font=("Arial", 11)).grid(row=i, column=0, sticky=tk.W, padx=10, pady=5)
            ttk.Label(metrics_frame, text=value, font=("Arial", 11, "bold")).grid(row=i, column=1, sticky=tk.E, padx=10, pady=5)
        
        # Make rows expandable
        for i in range(len(metrics)):
            metrics_frame.rowconfigure(i, weight=1)
        
        metrics_frame.columnconfigure(0, weight=1)
        metrics_frame.columnconfigure(1, weight=1)
    
    def create_placeholder_chart(self, parent, title):
        """Create a placeholder chart for the dashboard"""
        fig, ax = plt.subplots(figsize=(5, 3))
        
        # Generate random data
        x = np.arange(1, 13)
        y = np.random.randint(100, 500, size=12)
        
        # Create bar chart
        ax.bar(x, y)
        ax.set_title(title)
        ax.set_xlabel("Month")
        ax.set_ylabel("Sales ($)")
        
        # Embed the plot in the tkinter window
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def refresh_dashboard(self):
        """Refresh dashboard data"""
        messagebox.showinfo("Refresh", "Refreshing dashboard with latest data...")
        self.show_dashboard()
    
    def show_data_import(self):
        """Show data import screen"""
        frame = self.clear_content_frame()
        
        # Create header
        header = ttk.Frame(frame)
        header.pack(fill=tk.X, pady=10)
        
        title_label = ttk.Label(header, text="Data Import and Management", 
                               font=("Arial", 18, "bold"))
        title_label.pack(side=tk.LEFT, padx=10)
        
        # Create data import form
        form_frame = ttk.LabelFrame(frame, text="Import Data Source")
        form_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Data source
        source_frame = ttk.Frame(form_frame)
        source_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(source_frame, text="Data Source:").pack(side=tk.LEFT, padx=5)
        
        source_var = tk.StringVar()
        source_combo = ttk.Combobox(source_frame, textvariable=source_var, width=30)
        source_combo['values'] = ('Amazon', 'eBay', 'Shopify', 'Etsy', 'Walmart', 'Custom')
        source_combo.pack(side=tk.LEFT, padx=5)
        
        # File selection
        file_frame = ttk.Frame(form_frame)
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(file_frame, text="File Path:").pack(side=tk.LEFT, padx=5)
        
        file_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=file_var, width=50)
        file_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        browse_btn = ttk.Button(file_frame, text="Browse", 
                              command=lambda: file_var.set(filedialog.askopenfilename(
                                  filetypes=[("CSV files", "*.csv"), 
                                            ("Excel files", "*.xlsx"), 
                                            ("All files", "*.*")])))
        browse_btn.pack(side=tk.LEFT, padx=5)
        
        # Date range
        date_frame = ttk.Frame(form_frame)
        date_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(date_frame, text="Date Range:").pack(side=tk.LEFT, padx=5)
        
        start_var = tk.StringVar(value="2023-01-01")
        start_entry = ttk.Entry(date_frame, textvariable=start_var, width=15)
        start_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(date_frame, text="to").pack(side=tk.LEFT, padx=5)
        
        end_var = tk.StringVar(value="2023-12-31")
        end_entry = ttk.Entry(date_frame, textvariable=end_var, width=15)
        end_entry.pack(side=tk.LEFT, padx=5)
        
        # Import options
        options_frame = ttk.Frame(form_frame)
        options_frame.pack(fill=tk.X, padx=10, pady=10)
        
        header_var = tk.BooleanVar(value=True)
        header_check = ttk.Checkbutton(options_frame, text="First row as header", variable=header_var)
        header_check.pack(side=tk.LEFT, padx=20)
        
        clean_var = tk.BooleanVar(value=True)
        clean_check = ttk.Checkbutton(options_frame, text="Clean data automatically", variable=clean_var)
        clean_check.pack(side=tk.LEFT, padx=20)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        import_btn = ttk.Button(button_frame, text="Import Data", 
                              command=lambda: self.import_data(source_var.get(), file_var.get()))
        import_btn.pack(side=tk.RIGHT, padx=5)
        
        preview_btn = ttk.Button(button_frame, text="Preview Data", 
                               command=lambda: self.preview_data(file_var.get()))
        preview_btn.pack(side=tk.RIGHT, padx=5)
        
        # Data sources table
        table_frame = ttk.LabelFrame(frame, text="Available Data Sources")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create treeview
        columns = ("Source", "Type", "Records", "Last Updated", "Status")
        self.source_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        # Configure columns
        for col in columns:
            self.source_tree.heading(col, text=col)
            self.source_tree.column(col, width=100)
        
        # Add scrollbar
        tree_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.source_tree.yview)
        self.source_tree.configure(yscrollcommand=tree_scroll.set)
        
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.source_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add sample data
        sample_sources = [
            ("Amazon", "Sales", "5,432", "2023-12-15", "Active"),
            ("eBay", "Sales", "3,211", "2023-12-10", "Active"),
            ("Shopify", "Sales", "2,876", "2023-12-12", "Active"),
            ("Amazon", "Inventory", "1,245", "2023-12-05", "Active"),
            ("Etsy", "Sales", "954", "2023-11-30", "Inactive")
        ]
        
        for source in sample_sources:
            self.source_tree.insert("", tk.END, values=source)
    
    def import_data(self, source, file_path):
        """Import data from file"""
        if not source or not file_path:
            messagebox.showerror("Error", "Please select a data source and file path")
            return
        
        try:
            # This would actually call the data manager's import method
            messagebox.showinfo("Import", f"Importing {source} data from {file_path}")
            
            # Add to treeview (in a real application, this would be actual data)
            import datetime
            today = datetime.date.today().strftime("%Y-%m-%d")
            records = "1,234"  # Placeholder
            
            self.source_tree.insert("", tk.END, values=(source, "Sales", records, today, "Active"))
            
        except Exception as e:
            messagebox.showerror("Import Error", f"Error importing data: {str(e)}")
    
    def preview_data(self, file_path):
        """Preview data from file"""
        if not file_path:
            messagebox.showerror("Error", "Please select a file path")
            return
        
        try:
            # Read data
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path, nrows=10)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path, nrows=10)
            else:
                messagebox.showerror("Error", "Unsupported file format")
                return
            
            # Create preview window
            preview_window = tk.Toplevel(self.root)
            preview_window.title("Data Preview")
            preview_window.geometry("800x400")
            
            # Create treeview for data preview
            columns = list(df.columns)
            preview_tree = ttk.Treeview(preview_window, columns=columns, show="headings")
            
            # Configure columns
            for col in columns:
                preview_tree.heading(col, text=col)
                preview_tree.column(col, width=100)
            
            # Add scrollbars
            x_scroll = ttk.Scrollbar(preview_window, orient="horizontal", command=preview_tree.xview)
            y_scroll = ttk.Scrollbar(preview_window, orient="vertical", command=preview_tree.yview)
            preview_tree.configure(xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)
            
            # Pack components
            y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            preview_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
            
            # Add data rows
            for i, row in df.iterrows():
                values = list(row)
                preview_tree.insert("", tk.END, values=values)
            
        except Exception as e:
            messagebox.showerror("Preview Error", f"Error previewing data: {str(e)}")
    
    def show_advanced_analytics(self):
        """Show advanced analytics screen"""
        frame = self.clear_content_frame()
        
        # Create header
        header = ttk.Frame(frame)
        header.pack(fill=tk.X, pady=10)
        
        title_label = ttk.Label(header, text="Advanced Analytics", 
                              font=("Arial", 18, "bold"))
        title_label.pack(side=tk.LEFT, padx=10)
        
        # Create notebook for different analytics
        notebook = ttk.Notebook(frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Time Series Analysis
        time_series_tab = ttk.Frame(notebook)
        notebook.add(time_series_tab, text="Time Series Analysis")
        
        # Time series options
        ts_options = ttk.LabelFrame(time_series_tab, text="Analysis Options")
        ts_options.pack(fill=tk.X, padx=10, pady=10)
        
        # Data source
        ts_source_frame = ttk.Frame(ts_options)
        ts_source_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(ts_source_frame, text="Data Source:").pack(side=tk.LEFT, padx=5)
        
        ts_source_var = tk.StringVar()
        ts_source = ttk.Combobox(ts_source_frame, textvariable=ts_source_var, width=30)
        ts_source['values'] = ('Amazon Sales', 'eBay Sales', 'Shopify Sales', 'Combined Sales')
        ts_source.pack(side=tk.LEFT, padx=5)
        
        # Model selection
        ts_model_frame = ttk.Frame(ts_options)
        ts_model_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(ts_model_frame, text="Model:").pack(side=tk.LEFT, padx=5)
        
        ts_model_var = tk.StringVar()
        ts_model = ttk.Combobox(ts_model_frame, textvariable=ts_model_var, width=30)
        ts_model['values'] = ('LSTM Neural Network', 'Transformer Model', 'Prophet', 'ARIMA', 'Ensemble')
        ts_model.pack(side=tk.LEFT, padx=5)
        
        # Parameters
        ts_params_frame = ttk.Frame(ts_options)
        ts_params_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(ts_params_frame, text="Forecast Horizon:").pack(side=tk.LEFT, padx=5)
        
        horizon_var = tk.StringVar(value="30")
        horizon_entry = ttk.Entry(ts_params_frame, textvariable=horizon_var, width=10)
        horizon_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(ts_params_frame, text="days").pack(side=tk.LEFT)
        
        # Execute button
        ts_button_frame = ttk.Frame(ts_options)
        ts_button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        analyze_btn = ttk.Button(ts_button_frame, text="Run Analysis",
                              command=lambda: self.run_time_series_analysis(
                                  ts_source_var.get(), ts_model_var.get(), horizon_var.get()))
        analyze_btn.pack(side=tk.RIGHT, padx=5)
        
        # Results area
        ts_results = ttk.LabelFrame(time_series_tab, text="Results")
        ts_results.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create placeholder for results
        self.ts_result_canvas = tk.Canvas(ts_results)
        self.ts_result_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Tab 2: Market Basket Analysis
        basket_tab = ttk.Frame(notebook)
        notebook.add(basket_tab, text="Market Basket Analysis")
        
        # Market basket options
        basket_options = ttk.LabelFrame(basket_tab, text="Analysis Options")
        basket_options.pack(fill=tk.X, padx=10, pady=10)
        
        # Platform selection
        basket_platform_frame = ttk.Frame(basket_options)
        basket_platform_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(basket_platform_frame, text="Platform:").pack(side=tk.LEFT, padx=5)
        
        platform_var = tk.StringVar()
        platform_combo = ttk.Combobox(basket_platform_frame, textvariable=platform_var, width=30)
        platform_combo['values'] = ('Amazon', 'eBay', 'Shopify', 'All Platforms')
        platform_combo.pack(side=tk.LEFT, padx=5)
        
        # Parameters
        basket_params_frame = ttk.Frame(basket_options)
        basket_params_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(basket_params_frame, text="Min Support:").pack(side=tk.LEFT, padx=5)
        
        support_var = tk.StringVar(value="0.01")
        support_entry = ttk.Entry(basket_params_frame, textvariable=support_var, width=10)
        support_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(basket_params_frame, text="Min Confidence:").pack(side=tk.LEFT, padx=20)
        
        confidence_var = tk.StringVar(value="0.5")
        confidence_entry = ttk.Entry(basket_params_frame, textvariable=confidence_var, width=10)
        confidence_entry.pack(side=tk.LEFT, padx=5)
        
        # Execute button
        basket_button_frame = ttk.Frame(basket_options)
        basket_button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        basket_btn = ttk.Button(basket_button_frame, text="Find Associations",
                              command=lambda: self.run_market_basket_analysis(
                                  platform_var.get(), support_var.get(), confidence_var.get()))
        basket_btn.pack(side=tk.RIGHT, padx=5)
        
        # Results area
        basket_results = ttk.LabelFrame(basket_tab, text="Association Rules")
        basket_results.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview for association rules
        columns = ("Antecedent", "Consequent", "Support", "Confidence", "Lift")
        self.rule_tree = ttk.Treeview(basket_results, columns=columns, show="headings")
        
        # Configure columns
        for col in columns:
            self.rule_tree.heading(col, text=col)
            self.rule_tree.column(col, width=100)
        
        # Add scrollbar
        rule_scroll = ttk.Scrollbar(basket_results, orient="vertical", command=self.rule_tree.yview)
        self.rule_tree.configure(yscrollcommand=rule_scroll.set)
        
        rule_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.rule_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Tab 3: Customer Segmentation
        segment_tab = ttk.Frame(notebook)
        notebook.add(segment_tab, text="Customer Segmentation")
        
        # Segmentation options
        segment_options = ttk.LabelFrame(segment_tab, text="Segmentation Options")
        segment_options.pack(fill=tk.X, padx=10, pady=10)
        
        # Features selection
        segment_features_frame = ttk.Frame(segment_options)
        segment_features_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(segment_features_frame, text="Features:").pack(side=tk.LEFT, padx=5)
        
        # Feature checkboxes
        purchase_var = tk.BooleanVar(value=True)
        purchase_check = ttk.Checkbutton(segment_features_frame, text="Purchase Frequency", 
                                        variable=purchase_var)
        purchase_check.pack(side=tk.LEFT, padx=5)
        
        value_var = tk.BooleanVar(value=True)
        value_check = ttk.Checkbutton(segment_features_frame, text="Order Value", 
                                     variable=value_var)
        value_check.pack(side=tk.LEFT, padx=5)
        
        recency_var = tk.BooleanVar(value=True)
        recency_check = ttk.Checkbutton(segment_features_frame, text="Recency", 
                                       variable=recency_var)
        recency_check.pack(side=tk.LEFT, padx=5)
        
        # Cluster count
        segment_params_frame = ttk.Frame(segment_options)
        segment_params_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(segment_params_frame, text="Number of Segments:").pack(side=tk.LEFT, padx=5)
        
        cluster_var = tk.StringVar(value="4")
        cluster_entry = ttk.Entry(segment_params_frame, textvariable=cluster_var, width=10)
        cluster_entry.pack(side=tk.LEFT, padx=5)
        
        # Execute button
        segment_button_frame = ttk.Frame(segment_options)
        segment_button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        segment_btn = ttk.Button(segment_button_frame, text="Create Segments",
                              command=lambda: self.run_customer_segmentation(
                                  cluster_var.get(), [purchase_var.get(), value_var.get(), recency_var.get()]))
        segment_btn.pack(side=tk.RIGHT, padx=5)
        
        # Results area
        segment_results = ttk.LabelFrame(segment_tab, text="Segmentation Results")
        segment_results.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create placeholder for results
        self.segment_result_canvas = tk.Canvas(segment_results)
        self.segment_result_canvas.pack(fill=tk.BOTH, expand=True)
    
    def run_time_series_analysis(self, source, model, horizon):
        """Run time series analysis"""
        if not source or not model or not horizon:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        try:
            horizon = int(horizon)
            if horizon <= 0:
                raise ValueError("Horizon must be positive")
                
            # Show progress
            messagebox.showinfo("Analysis", f"Running {model} analysis on {source} data with {horizon}-day horizon")
            
            # Create a placeholder visualization
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Generate random data for demonstration
            x = np.arange(100)
            y = np.cumsum(np.random.randn(100) * 5) + 100
            
            # Forecast
            forecast_x = np.arange(100, 100 + horizon)
            forecast_y = y[-1] + np.cumsum(np.random.randn(horizon) * 5)
            
            # Plot historical data and forecast
            ax.plot(x, y, 'b-', label='Historical Data')
            ax.plot(forecast_x, forecast_y, 'r--', label='Forecast')
            ax.fill_between(forecast_x, forecast_y - 10, forecast_y + 10, color='r', alpha=0.2)
            
            ax.set_title(f"{source} Forecast using {model}")
            ax.set_xlabel("Time (Days)")
            ax.set_ylabel("Sales")
            ax.legend()
            ax.grid(True)
            
            # Clear previous content
            for widget in self.ts_result_canvas.winfo_children():
                widget.destroy()
            
            # Embed plot in canvas
            canvas = FigureCanvasTkAgg(fig, master=self.ts_result_canvas)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Error running analysis: {str(e)}")
    
    def run_market_basket_analysis(self, platform, min_support, min_confidence):
        """Run market basket analysis"""
        if not platform:
            messagebox.showerror("Error", "Please select a platform")
            return
        
        try:
            min_support = float(min_support)
            min_confidence = float(min_confidence)
            
            if min_support <= 0 or min_support >= 1:
                raise ValueError("Support must be between 0 and 1")
            
            if min_confidence <= 0 or min_confidence > 1:
                raise ValueError("Confidence must be between 0 and 1")
                
            # Show progress
            messagebox.showinfo("Analysis", 
                             f"Finding association rules for {platform} with support={min_support}, confidence={min_confidence}")
            
            # Clear existing items
            for item in self.rule_tree.get_children():
                self.rule_tree.delete(item)
            
            # Add sample rules
            sample_rules = [
                (["Product A"], ["Product B"], 0.15, 0.75, 2.5),
                (["Product C"], ["Product D", "Product E"], 0.12, 0.65, 2.2),
                (["Product F", "Product G"], ["Product H"], 0.08, 0.80, 3.1),
                (["Product I"], ["Product J"], 0.10, 0.60, 1.8),
                (["Product K", "Product L"], ["Product M"], 0.05, 0.70, 2.7)
            ]
            
            for antecedent, consequent, support, confidence, lift in sample_rules:
                ant_str = ", ".join(antecedent)
                con_str = ", ".join(consequent)
                self.rule_tree.insert("", tk.END, values=(
                    ant_str, con_str, f"{support:.3f}", f"{confidence:.3f}", f"{lift:.2f}"))
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Error running analysis: {str(e)}")
    
    def run_customer_segmentation(self, n_clusters, features):
        """Run customer segmentation analysis"""
        try:
            n_clusters = int(n_clusters)
            if n_clusters <= 1:
                raise ValueError("Number of clusters must be at least 2")
                
            # Show progress
            messagebox.showinfo("Analysis", f"Creating {n_clusters} customer segments")
            
            # Create a placeholder visualization
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Generate random cluster data
            np.random.seed(42)
            n_samples = 200
            
            # Create 2D data for visualization
            centers = [[1, 1], [1, -1], [-1, 1], [-1, -1]][:n_clusters]
            data = []
            labels = []
            
            for i, center in enumerate(centers):
                cluster_samples = np.random.randn(n_samples // n_clusters, 2) * 0.3 + center
                data.append(cluster_samples)
                labels.extend([i] * (n_samples // n_clusters))
                
            data = np.vstack(data)
            
            # Color map
            colors = ['blue', 'green', 'red', 'purple', 'orange', 'brown']
            
            # Scatter plot for each cluster
            for i in range(n_clusters):
                cluster_data = data[np.array(labels) == i]
                ax.scatter(cluster_data[:, 0], cluster_data[:, 1], c=colors[i % len(colors)], 
                          label=f'Segment {i+1}', alpha=0.6)
            
            ax.set_title("Customer Segmentation")
            ax.set_xlabel("Purchase Frequency")
            ax.set_ylabel("Average Order Value")
            ax.legend()
            ax.grid(True)
            
            # Clear previous content
            for widget in self.segment_result_canvas.winfo_children():
                widget.destroy()
            
            # Embed plot in canvas
            canvas = FigureCanvasTkAgg(fig, master=self.segment_result_canvas)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Add summary text
            summary_frame = ttk.Frame(self.segment_result_canvas)
            summary_frame.pack(fill=tk.X, padx=10, pady=10)
            
            # Cluster descriptions
            descriptions = [
                "High value, high frequency shoppers (15%)",
                "High value, low frequency shoppers (22%)",
                "Low value, high frequency shoppers (35%)",
                "Low value, low frequency shoppers (28%)"
            ][:n_clusters]
            
            for i, desc in enumerate(descriptions):
                ttk.Label(summary_frame, text=f"Segment {i+1}: {desc}", 
                         font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=2)
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Error running analysis: {str(e)}")
    
    def show_forecasting(self):
        """Show forecasting screen"""
        frame = self.clear_content_frame()
        
        # Implementation details for forecasting screen go here
        ttk.Label(frame, text="Forecasting Module", font=("Arial", 18, "bold")).pack(padx=10, pady=10)
        ttk.Label(frame, text="This section will contain detailed forecasting tools").pack(pady=20)
    
    def show_market_analysis(self):
        """Show market analysis screen"""
        frame = self.clear_content_frame()
        
        # Implementation details for market analysis screen go here
        ttk.Label(frame, text="Market Analysis Module", font=("Arial", 18, "bold")).pack(padx=10, pady=10)
        ttk.Label(frame, text="This section will contain market analysis tools").pack(pady=20)
    
    def show_recommendations(self):
        """Show recommendations screen"""
        frame = self.clear_content_frame()
        
        # Implementation details for recommendations screen go here
        ttk.Label(frame, text="Recommendations Engine", font=("Arial", 18, "bold")).pack(padx=10, pady=10)
        ttk.Label(frame, text="This section will display actionable recommendations").pack(pady=20)
    
    def show_tableau_export(self):
        """Show Tableau export screen"""
        frame = self.clear_content_frame()
        
        # Header
        header = ttk.Frame(frame)
        header.pack(fill=tk.X, pady=10)
        
        title_label = ttk.Label(header, text="Tableau Integration", 
                              font=("Arial", 18, "bold"))
        title_label.pack(side=tk.LEFT, padx=10)
        
        # Export options section
        export_frame = ttk.LabelFrame(frame, text="Export Data to Tableau")
        export_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Dataset selection
        dataset_frame = ttk.Frame(export_frame)
        dataset_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(dataset_frame, text="Dataset:").pack(side=tk.LEFT, padx=5)
        
        dataset_var = tk.StringVar()
        dataset_combo = ttk.Combobox(dataset_frame, textvariable=dataset_var, width=40)
        dataset_combo['values'] = ('Sales Data', 'Customer Segments', 'Product Analysis', 
                                 'Platform Comparison', 'Forecast Results')
        dataset_combo.pack(side=tk.LEFT, padx=5)
        
        # Format selection
        format_frame = ttk.Frame(export_frame)
        format_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(format_frame, text="Export Format:").pack(side=tk.LEFT, padx=5)
        
        format_var = tk.StringVar(value="CSV")
        csv_radio = ttk.Radiobutton(format_frame, text="CSV", variable=format_var, value="CSV")
        csv_radio.pack(side=tk.LEFT, padx=20)
        
        excel_radio = ttk.Radiobutton(format_frame, text="Excel", variable=format_var, value="Excel")
        excel_radio.pack(side=tk.LEFT, padx=20)
        
        # Export buttons
        button_frame = ttk.Frame(export_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        export_btn = ttk.Button(button_frame, text="Export Data", 
                             command=lambda: self.export_to_tableau(dataset_var.get(), format_var.get()))
        export_btn.pack(side=tk.RIGHT, padx=5)
        
        # Tableau templates section
        templates_frame = ttk.LabelFrame(frame, text="Tableau Templates")
        templates_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create a canvas with scrollbar
        templates_canvas = tk.Canvas(templates_frame)
        scrollbar = ttk.Scrollbar(templates_frame, orient="vertical", command=templates_canvas.yview)
        scrollable_frame = ttk.Frame(templates_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: templates_canvas.configure(
                scrollregion=templates_canvas.bbox("all")
            )
        )
        
        templates_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        templates_canvas.configure(yscrollcommand=scrollbar.set)
        
        templates_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add template cards
        templates = [
            {
                "name": "Sales Dashboard",
                "description": "Complete sales overview with trend analysis and forecasting",
                "image": "dashboard_template.png"
            },
            {
                "name": "Product Performance",
                "description": "Detailed product comparison and performance metrics",
                "image": "product_template.png"
            },
            {
                "name": "Customer Insights",
                "description": "Customer segmentation and behavior analysis",
                "image": "customer_template.png"
            },
            {
                "name": "Marketplace Comparison",
                "description": "Compare performance across different marketplaces",
                "image": "marketplace_template.png"
            }
        ]
        
        # Create template cards
        for i, template in enumerate(templates):
            card = ttk.Frame(scrollable_frame, borderwidth=2, relief="groove")
            card.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")
            
            # Template name
            ttk.Label(card, text=template["name"], font=("Arial", 12, "bold")).pack(padx=10, pady=5)
            
            # Template description
            ttk.Label(card, text=template["description"], wraplength=250).pack(padx=10, pady=5)
            
            # Template image placeholder
            image_frame = ttk.Frame(card, width=250, height=150)
            image_frame.pack(padx=10, pady=5)
            image_frame.pack_propagate(False)
            
            ttk.Label(image_frame, text="[Template Preview]").pack(expand=True)
            
            # Use button
            ttk.Button(card, text="Use Template", 
                      command=lambda name=template["name"]: self.use_tableau_template(name)).pack(padx=10, pady=10)

        # Make sure grid cells expand properly
        for i in range(2):
            scrollable_frame.columnconfigure(i, weight=1)
        for i in range(len(templates)//2 + len(templates)%2):
            scrollable_frame.rowconfigure(i, weight=1)
    
    def export_to_tableau(self, dataset, export_format):
        """Export data to Tableau"""
        if not dataset:
            messagebox.showerror("Error", "Please select a dataset")
            return
        
        try:
            # This would call the tableau integration's export method
            messagebox.showinfo("Export", f"Exporting {dataset} in {export_format} format for Tableau")
            
            # Show file save dialog
            file_types = [("CSV files", "*.csv")] if export_format == "CSV" else [("Excel files", "*.xlsx")]
            file_path = filedialog.asksaveasfilename(
                title=f"Save {dataset}",
                filetypes=file_types,
                defaultextension=file_types[0][1]
            )
            
            if file_path:
                # Simulate export process
                messagebox.showinfo("Success", f"Data exported successfully to {file_path}")
        
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting data: {str(e)}")
    
    def use_tableau_template(self, template_name):
        """Use Tableau template"""
        messagebox.showinfo("Template", f"Applying {template_name} template")
        
        # This would open Tableau with the template
        messagebox.showinfo("Tableau", "Launching Tableau with the selected template")
    
    def show_settings(self):
        """Show settings screen"""
        frame = self.clear_content_frame()
        
        # Header
        header = ttk.Frame(frame)
        header.pack(fill=tk.X, pady=10)
        
        title_label = ttk.Label(header, text="Settings", 
                              font=("Arial", 18, "bold"))
        title_label.pack(side=tk.LEFT, padx=10)
        
        # Create notebook for different settings categories
        notebook = ttk.Notebook(frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: General Settings
        general_tab = ttk.Frame(notebook)
        notebook.add(general_tab, text="General")
        
        # General settings
        appearance_frame = ttk.LabelFrame(general_tab, text="Appearance")
        appearance_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Theme selection
        theme_frame = ttk.Frame(appearance_frame)
        theme_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(theme_frame, text="Theme:").pack(side=tk.LEFT, padx=5)
        
        theme_var = tk.StringVar(value="Light")
        theme_combo = ttk.Combobox(theme_frame, textvariable=theme_var, width=20)
        theme_combo['values'] = ('Light', 'Dark', 'System Default')
        theme_combo.pack(side=tk.LEFT, padx=5)
        
        # Chart style
        chart_frame = ttk.Frame(appearance_frame)
        chart_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(chart_frame, text="Chart Style:").pack(side=tk.LEFT, padx=5)
        
        chart_var = tk.StringVar(value="Classic")
        chart_combo = ttk.Combobox(chart_frame, textvariable=chart_var, width=20)
        chart_combo['values'] = ('Classic', 'Modern', 'Minimal')
        chart_combo.pack(side=tk.LEFT, padx=5)
        
        # Data preferences
        data_frame = ttk.LabelFrame(general_tab, text="Data Preferences")
        data_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Date format
        date_frame = ttk.Frame(data_frame)
        date_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(date_frame, text="Date Format:").pack(side=tk.LEFT, padx=5)
        
        date_var = tk.StringVar(value="MM/DD/YYYY")
        date_combo = ttk.Combobox(date_frame, textvariable=date_var, width=20)
        date_combo['values'] = ('MM/DD/YYYY', 'DD/MM/YYYY', 'YYYY-MM-DD')
        date_combo.pack(side=tk.LEFT, padx=5)
        
        # Currency
        currency_frame = ttk.Frame(data_frame)
        currency_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(currency_frame, text="Currency:").pack(side=tk.LEFT, padx=5)
        
        currency_var = tk.StringVar(value="USD ($)")
        currency_combo = ttk.Combobox(currency_frame, textvariable=currency_var, width=20)
        currency_combo['values'] = ('USD ($)', 'EUR (€)', 'GBP (£)', 'JPY (¥)')
        currency_combo.pack(side=tk.LEFT, padx=5)
        
        # Save button
        save_frame = ttk.Frame(general_tab)
        save_frame.pack(fill=tk.X, padx=10, pady=20)
        
        save_btn = ttk.Button(save_frame, text="Save Settings", 
                             command=lambda: messagebox.showinfo("Settings", "Settings saved successfully"))
        save_btn.pack(side=tk.RIGHT, padx=10)
        
        # Tab 2: API Settings
        api_tab = ttk.Frame(notebook)
        notebook.add(api_tab, text="API Connections")
        
        # API keys frame
        api_keys_frame = ttk.LabelFrame(api_tab, text="API Keys")
        api_keys_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Amazon API
        amazon_frame = ttk.Frame(api_keys_frame)
        amazon_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(amazon_frame, text="Amazon API Key:").pack(side=tk.LEFT, padx=5)
        
        amazon_var = tk.StringVar()
        amazon_entry = ttk.Entry(amazon_frame, textvariable=amazon_var, width=40, show="*")
        amazon_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        amazon_show = ttk.Button(amazon_frame, text="Show", 
                               command=lambda: self.toggle_password_visibility(amazon_entry))
        amazon_show.pack(side=tk.LEFT, padx=5)
        
        # eBay API
        ebay_frame = ttk.Frame(api_keys_frame)
        ebay_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(ebay_frame, text="eBay API Key:").pack(side=tk.LEFT, padx=5)
        
        ebay_var = tk.StringVar()
        ebay_entry = ttk.Entry(ebay_frame, textvariable=ebay_var, width=40, show="*")
        ebay_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        ebay_show = ttk.Button(ebay_frame, text="Show", 
                             command=lambda: self.toggle_password_visibility(ebay_entry))
        ebay_show.pack(side=tk.LEFT, padx=5)
        
        # Shopify API
        shopify_frame = ttk.Frame(api_keys_frame)
        shopify_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(shopify_frame, text="Shopify API Key:").pack(side=tk.LEFT, padx=5)
        
        shopify_var = tk.StringVar()
        shopify_entry = ttk.Entry(shopify_frame, textvariable=shopify_var, width=40, show="*")
        shopify_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        shopify_show = ttk.Button(shopify_frame, text="Show", 
                                command=lambda: self.toggle_password_visibility(shopify_entry))
        shopify_show.pack(side=tk.LEFT, padx=5)
        
        # Test connections
        test_frame = ttk.Frame(api_tab)
        test_frame.pack(fill=tk.X, padx=10, pady=20)
        
        test_btn = ttk.Button(test_frame, text="Test Connections", 
                            command=self.test_api_connections)
        test_btn.pack(side=tk.LEFT, padx=10)
        
        save_api_btn = ttk.Button(test_frame, text="Save API Settings", 
                                command=lambda: messagebox.showinfo("API Settings", "API settings saved successfully"))
        save_api_btn.pack(side=tk.RIGHT, padx=10)
    
    def toggle_password_visibility(self, entry):
        """Toggle password visibility in entry fields"""
        if entry.cget('show') == '*':
            entry.config(show='')
        else:
            entry.config(show='*')
    
    def test_api_connections(self):
        """Test API connections"""
        # Simulate connection testing
        messagebox.showinfo("API Connection", "Testing API connections...")
        
        # In a real application, this would actually test the connections
        # For now, just show a success message
        messagebox.showinfo("API Connection", 
                         "All API connections tested successfully:\n\n" +
                         "✓ Amazon API: Connected\n" +
                         "✓ eBay API: Connected\n" +
                         "✓ Shopify API: Connected")
    
    def show_help(self):
        """Show help screen"""
        frame = self.clear_content_frame()
        
        # Header
        header = ttk.Frame(frame)
        header.pack(fill=tk.X, pady=10)
        
        title_label = ttk.Label(header, text="Help & Documentation", 
                              font=("Arial", 18, "bold"))
        title_label.pack(side=tk.LEFT, padx=10)
        
        # Create main help frame
        help_frame = ttk.Frame(frame)
        help_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side: Topics
        topics_frame = ttk.LabelFrame(help_frame, text="Topics")
        topics_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10, expand=False)
        
        topics = [
            "Getting Started",
            "Data Import Guide",
            "Analytics Features",
            "Forecasting Tools",
            "Tableau Integration",
            "Troubleshooting",
            "FAQ"
        ]
        
        topics_listbox = tk.Listbox(topics_frame, width=25, height=len(topics))
        topics_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        for topic in topics:
            topics_listbox.insert(tk.END, topic)
        
        # Select first topic by default
        topics_listbox.selection_set(0)
        
        # Right side: Content
        content_frame = ttk.LabelFrame(help_frame, text="Documentation")
        content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10, expand=True)
        
        # Example content for "Getting Started"
        ttk.Label(content_frame, text="Getting Started with TrendLens", 
                font=("Arial", 14, "bold")).pack(anchor=tk.W, padx=10, pady=10)
        
        help_text = """
        Welcome to TrendLens E-Commerce Analyzer!
        
        This application helps you analyze e-commerce data across multiple platforms,
        identify trends, and make data-driven decisions to optimize your business.
        
        To get started:
        
        1. Import your sales data using the Data Import module
        2. View your analytics dashboard for an overview of performance
        3. Use Advanced Analytics for deeper insights
        4. Generate forecasts to plan inventory and marketing
        5. Export results to Tableau for custom visualizations
        
        For more detailed instructions, select a topic from the list on the left.
        """
        
        text_widget = tk.Text(content_frame, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)  # Make read-only
        
        # Support section
        support_frame = ttk.Frame(frame)
        support_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(support_frame, text="Need additional help?").pack(side=tk.LEFT, padx=10)
        
        docs_btn = ttk.Button(support_frame, text="Online Documentation", 
                            command=lambda: webbrowser.open("https://example.com/docs"))
        docs_btn.pack(side=tk.LEFT, padx=5)
        
        contact_btn = ttk.Button(support_frame, text="Contact Support", 
                              command=lambda: webbrowser.open("mailto:support@example.com"))
        contact_btn.pack(side=tk.LEFT, padx=5)
    
    def show_about(self):
        """Show about screen"""
        frame = self.clear_content_frame()
        
        # Header
        header = ttk.Frame(frame)
        header.pack(fill=tk.X, pady=10)
        
        title_label = ttk.Label(header, text="About TrendLens", 
                              font=("Arial", 18, "bold"))
        title_label.pack(side=tk.LEFT, padx=10)
        
        # Main content
        content_frame = ttk.Frame(frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # App info
        app_frame = ttk.Frame(content_frame)
        app_frame.pack(fill=tk.X, pady=10)
        
        # Logo placeholder
        logo_frame = ttk.Frame(app_frame, width=100, height=100)
        logo_frame.pack(side=tk.LEFT, padx=20)
        logo_frame.pack_propagate(False)
        
        ttk.Label(logo_frame, text="LOGO", font=("Arial", 16)).pack(expand=True)
        
        # App details
        details_frame = ttk.Frame(app_frame)
        details_frame.pack(side=tk.LEFT, padx=20, fill=tk.Y)
        
        ttk.Label(details_frame, text="TrendLens E-Commerce Analyzer", 
                font=("Arial", 16, "bold")).pack(anchor=tk.W, pady=2)
        ttk.Label(details_frame, text="Version 1.0.0").pack(anchor=tk.W, pady=2)
        ttk.Label(details_frame, text="© 2023 TrendLens Analytics Inc.").pack(anchor=tk.W, pady=2)
        
        # Description
        desc_frame = ttk.Frame(content_frame)
        desc_frame.pack(fill=tk.X, pady=20)
        
        description = """
        TrendLens is a comprehensive e-commerce analytics platform designed to help
        businesses make data-driven decisions by analyzing sales across multiple marketplaces.
        
        With advanced AI-powered forecasting, market basket analysis, and customer segmentation,
        TrendLens provides actionable insights to optimize your e-commerce strategy.
        """
        
        ttk.Label(desc_frame, text=description, wraplength=600, justify=tk.LEFT).pack(pady=10)
        
        # Technologies used
        tech_frame = ttk.LabelFrame(content_frame, text="Technologies")
        tech_frame.pack(fill=tk.X, pady=10)
        
        technologies = [
            "Python 3.9", "Pandas", "NumPy", "scikit-learn",
            "Matplotlib", "Plotly", "Tkinter", "LSTM Neural Networks",
            "Association Rules Mining", "K-means Clustering"
        ]
        
        tech_text = ", ".join(technologies)
        ttk.Label(tech_frame, text=tech_text, wraplength=600).pack(padx=10, pady=10)
        
        # Links
        links_frame = ttk.Frame(content_frame)
        links_frame.pack(fill=tk.X, pady=20)
        
        website_btn = ttk.Button(links_frame, text="Visit Website", 
                              command=lambda: webbrowser.open("https://example.com"))
        website_btn.pack(side=tk.LEFT, padx=10)
        
        github_btn = ttk.Button(links_frame, text="GitHub Repository", 
                             command=lambda: webbrowser.open("https://github.com/example/trendlens"))
        github_btn.pack(side=tk.LEFT, padx=10)
        
        license_btn = ttk.Button(links_frame, text="License Information", 
                              command=self.show_license)
        license_btn.pack(side=tk.LEFT, padx=10)
    
    def show_license(self):
        """Show license information"""
        license_window = tk.Toplevel(self.root)
        license_window.title("License Information")
        license_window.geometry("600x400")
        
        license_text = """
        MIT License

        Copyright (c) 2023 TrendLens Analytics Inc.

        Permission is hereby granted, free of charge, to any person obtaining a copy
        of this software and associated documentation files (the "Software"), to deal
        in the Software without restriction, including without limitation the rights
        to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
        copies of the Software, and to permit persons to whom the Software is
        furnished to do so, subject to the following conditions:

        The above copyright notice and this permission notice shall be included in all
        copies or substantial portions of the Software.

        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
        IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
        FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
        AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
        LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
        OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
        SOFTWARE.
        """
        
        text_widget = tk.Text(license_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, license_text)
        text_widget.config(state=tk.DISABLED)  # Make read-only
        
        close_btn = ttk.Button(license_window, text="Close", command=license_window.destroy)
        close_btn.pack(pady=10)
        
