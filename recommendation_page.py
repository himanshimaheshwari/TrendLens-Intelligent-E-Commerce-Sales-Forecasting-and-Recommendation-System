import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from recommendation_page_implementation import RecommendationEngine
import pandas as pd

def _create_recommendations_tab(self):
    """Create the Recommendations tab UI and functionality"""
    # Split frame into control panel and recommendations display area
    control_frame = ttk.Frame(self.recommendations_frame)
    control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
    
    recs_frame = ttk.Frame(self.recommendations_frame)
    recs_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Platform selection
    ttk.Label(control_frame, text="Select Platforms:").pack(anchor=tk.W, pady=(0, 5))
    
    # Platform checkboxes
    platform_vars = {}
    for platform in ['Meesho', 'Flipkart', 'Amazon']:
        platform_vars[platform] = tk.BooleanVar(value=self.platform_data[platform]['data'] is not None)
        ttk.Checkbutton(control_frame, text=platform, variable=platform_vars[platform]).pack(anchor=tk.W, pady=2)
    
    # Analysis scope
    ttk.Label(control_frame, text="Analysis Scope:").pack(anchor=tk.W, pady=(15, 5))
    scope_var = tk.StringVar(value="All Data")
    scope_options = ["All Data", "Last Month", "Last Quarter", "Last Year"]
    ttk.Combobox(control_frame, textvariable=scope_var, values=scope_options).pack(fill=tk.X, pady=(0, 15))
    
    # Recommendation types
    types_frame = ttk.LabelFrame(control_frame, text="Recommendation Types")
    types_frame.pack(fill=tk.X, pady=10)
    
    rec_type_vars = {}
    for rec_type in ["Pricing Strategy", "Inventory Planning", "Marketing", "Cross-Platform"]:
        rec_type_vars[rec_type] = tk.BooleanVar(value=True)
        ttk.Checkbutton(types_frame, text=rec_type, variable=rec_type_vars[rec_type]).pack(anchor=tk.W, pady=3, padx=5)
    
    # Advanced options
    advanced_frame = ttk.LabelFrame(control_frame, text="Advanced Options")
    advanced_frame.pack(fill=tk.X, pady=10)
    
    ttk.Label(advanced_frame, text="Detail Level:").pack(anchor=tk.W, padx=5, pady=(5, 0))
    detail_var = tk.StringVar(value="Standard")
    ttk.Combobox(advanced_frame, textvariable=detail_var, values=["Basic", "Standard", "Detailed"]).pack(
        fill=tk.X, padx=5, pady=5)
    
    ttk.Label(advanced_frame, text="Include Market Analysis:").pack(anchor=tk.W, padx=5, pady=(5, 0))
    market_var = tk.BooleanVar(value=True)
    ttk.Checkbutton(advanced_frame, variable=market_var).pack(anchor=tk.W, padx=5, pady=2)
    
    # Action buttons
    ttk.Button(control_frame, text="Generate Recommendations", 
              command=lambda: self._generate_recs(platform_vars, scope_var.get(), 
                                                 [k for k, v in rec_type_vars.items() if v.get()],
                                                 detail_var.get(), market_var.get(), recs_frame)).pack(
        fill=tk.X, pady=(15, 5))
    
    ttk.Button(control_frame, text="Export Recommendations", 
              command=self._export_recommendations).pack(fill=tk.X, pady=5)
    
    # Create notebook for recommendations display
    self.recs_notebook = ttk.Notebook(recs_frame)
    self.recs_notebook.pack(fill=tk.BOTH, expand=True)
    
    # Initial tabs
    initial_frame = ttk.Frame(self.recs_notebook)
    self.recs_notebook.add(initial_frame, text="Welcome")
    
    # Welcome message
    welcome_text = tk.Text(initial_frame, wrap=tk.WORD)
    welcome_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    welcome_text.insert(tk.END, """
    Welcome to the TrendLens Recommendations Engine!
    
    This module analyzes your e-commerce data to provide actionable insights and recommendations.
    
    To get started:
    1. Select one or more platforms to analyze
    2. Choose the analysis scope (time period)
    3. Select which types of recommendations you'd like to see
    4. Click "Generate Recommendations"
    
    The system will then analyze your data to provide:
    - Pricing recommendations
    - Inventory planning insights
    - Marketing strategies
    - Cross-platform optimization opportunities
    
    All recommendations are based on data-driven analysis of your sales patterns and market trends.
    """)
    welcome_text.config(state=tk.DISABLED)  # Make read-only
    self.fastest_label = ctk.CTkLabel(self.recommendations_frame, text="", font=ctk.CTkFont(size=14))
    self.fastest_label.pack(pady=10)

def _generate_recs(self, platform_vars, scope, rec_types, detail_level, include_market, recs_frame):
    """Generate and display recommendations"""
    # Check which platforms have data and are selected
    selected_platforms = [p for p, v in platform_vars.items() if v.get() and self.platform_data[p]['data'] is not None]
    
    if not selected_platforms:
        messagebox.showwarning("No Data", "Please select at least one platform with loaded data.")
        return
    
    # Get platform analyzers
    analyzers = [self.platform_data[p]['analyzer'] for p in selected_platforms]
    
    # Process data if needed
    for analyzer in analyzers:
        if analyzer.processed_data is None:
            analyzer.preprocess_data()
    
    # Show loading message
    self.recs_notebook.forget(0)  # Remove existing tabs
    loading_frame = ttk.Frame(self.recs_notebook)
    self.recs_notebook.add(loading_frame, text="Loading...")
    
    loading_label = ttk.Label(loading_frame, text="Generating recommendations...\nThis may take a moment.")
    loading_label.pack(pady=50)
    self.update()  # Update UI to show loading message
    
    try:
        # Create recommendation engine
        rec_engine = RecommendationEngine(analyzers)
        
        # Map UI recommendation types to implementation types
        rec_type_mapping = {
            "Pricing Strategy": "pricing",
            "Inventory Planning": "inventory",
            "Marketing": "marketing",
            "Cross-Platform": "marketing"  # Adjust this based on what "Cross-Platform" should map to
        }
        
        # Map scope values
        scope_mapping = {
            "All Data": "All",
            "Last Month": "Last Month",
            "Last Quarter": "Last Quarter",
            "Last Year": "Last Year"
        }
        
        # Generate recommendations - FIXED LINE
        raw_recommendations = rec_engine.generate_recommendations(
            scope=scope_mapping.get(scope, "All"),
            recommendation_types=[rec_type_mapping.get(rec_type, "pricing") for rec_type in rec_types],
            detail_level=detail_level,
            include_market_analysis=include_market
        )
        
        # Format recommendations into proper structure if they're not already
        recommendations = {}
        for rec_type, rec_items in raw_recommendations.items():
            # Create a properly structured dictionary for each recommendation type
            formatted_data = _format_recommendation_data(self, rec_type, rec_items)
            recommendations[rec_type] = formatted_data
        
        # Store recommendations for export
        self.current_recommendations = recommendations
        
        # Clear existing tabs from the notebook
        for tab in self.recs_notebook.tabs():
            self.recs_notebook.forget(tab)
        
        # Create a tab for each recommendation type
        for rec_type, rec_data in recommendations.items():
            tab_frame = ttk.Frame(self.recs_notebook)
            self.recs_notebook.add(tab_frame, text=rec_type)
            
            # Create a canvas with scrollbar for large content
            canvas = tk.Canvas(tab_frame)
            scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Add recommendations content
            self._add_recommendation_content(scrollable_frame, rec_type, rec_data)
        
    except Exception as e:
        messagebox.showerror("Recommendation Error", f"Error generating recommendations: {str(e)}")
        print(f"Recommendation error details: {e}")
        import traceback
        traceback.print_exc()
        
        # Add back the welcome tab if error occurred
        if len(self.recs_notebook.tabs()) == 0:
            initial_frame = ttk.Frame(self.recs_notebook)
            self.recs_notebook.add(initial_frame, text="Welcome")
            
            error_label = ttk.Label(initial_frame, text=f"Error generating recommendations. Please try again.\n\nError: {str(e)}")
            error_label.pack(pady=50)

def _format_recommendation_data(self, rec_type, rec_items):
    """Format recommendation data into the expected structure"""
    # Initialize with the standard structure
    formatted_data = {
        "summary": f"Summary of {rec_type} recommendations",
        "insights": [],
        "recommendations": []
    }
    
    # If rec_items is already a dictionary with the right structure, return it
    if isinstance(rec_items, dict) and all(key in rec_items for key in ["summary", "insights", "recommendations"]):
        return rec_items
    
    # If rec_items is a list, convert it to the expected format
    if isinstance(rec_items, list):
        # Group recommendations by category if present
        categories = {}
        for item in rec_items:
            # Skip error messages
            if "type" in item and item["type"] == "Error":
                formatted_data["summary"] = item["message"]
                continue
                
            # Create insight from each recommendation
            if "recommendation" in item and "reasoning" in item:
                insight = {
                    "title": item.get("recommendation", "Recommendation"),
                    "description": item.get("reasoning", "No details provided")
                }
                formatted_data["insights"].append(insight)
                
            # Create recommendation entry
            recommendation = {
                "title": item.get("recommendation", "Recommendation"),
                "explanation": item.get("reasoning", "No details provided"),
                "priority": item.get("priority", "Medium")
            }
            
            # Add actions if present
            if "suggested_action" in item:
                recommendation["actions"] = [item["suggested_action"]]
            elif "suggested_order" in item:
                recommendation["actions"] = [f"Order {item['suggested_order']} units"]
                
            formatted_data["recommendations"].append(recommendation)
                
    return formatted_data

def display_results(self):
    if hasattr(self, "fastest_solution"):
        self.fastest_label.configure(text=f"Fastest Solution: {self.fastest_solution}")

def _add_recommendation_content(self, parent_frame, rec_type, rec_data):
    """Add recommendation content to the specified frame"""
    # Add title
    title_label = ttk.Label(parent_frame, text=rec_type, font=("Helvetica", 14, "bold"))
    title_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
    
    ttk.Separator(parent_frame).pack(fill=tk.X, padx=10, pady=5)
    
    # Summary section
    if 'summary' in rec_data:
        summary_frame = ttk.LabelFrame(parent_frame, text="Summary")
        summary_frame.pack(fill=tk.X, padx=10, pady=5, expand=True)
        
        summary_text = tk.Text(summary_frame, wrap=tk.WORD, height=4)
        summary_text.pack(fill=tk.X, padx=5, pady=5, expand=True)
        summary_text.insert(tk.END, rec_data['summary'])
        summary_text.config(state=tk.DISABLED)  # Make read-only
    
    # Key insights
    if 'insights' in rec_data:
        insights_frame = ttk.LabelFrame(parent_frame, text="Key Insights")
        insights_frame.pack(fill=tk.X, padx=10, pady=5, expand=True)
        
        for i, insight in enumerate(rec_data['insights']):
            insight_box = ttk.Frame(insights_frame, borderwidth=1, relief="groove")
            insight_box.pack(fill=tk.X, padx=5, pady=3, expand=True)
            
            # Ensure insight is a dictionary with required keys
            if isinstance(insight, dict) and 'title' in insight:
                insight_label = ttk.Label(insight_box, text=f"{i+1}. {insight['title']}", font=("Helvetica", 10, "bold"))
                insight_label.pack(anchor=tk.W, padx=5, pady=(5, 0))
                
                desc_label = ttk.Label(insight_box, text=insight.get('description', 'No description available'), wraplength=600)
                desc_label.pack(anchor=tk.W, padx=5, pady=(0, 5))
            else:
                # Handle case where insight is not properly formatted
                insight_label = ttk.Label(insight_box, text=f"{i+1}. Insight", font=("Helvetica", 10, "bold"))
                insight_label.pack(anchor=tk.W, padx=5, pady=(5, 0))
                
                if isinstance(insight, str):
                    desc_label = ttk.Label(insight_box, text=insight, wraplength=600)
                    desc_label.pack(anchor=tk.W, padx=5, pady=(0, 5))
                else:
                    desc_label = ttk.Label(insight_box, text="No description available", wraplength=600)
                    desc_label.pack(anchor=tk.W, padx=5, pady=(0, 5))
    
    # Recommendations
    if 'recommendations' in rec_data:
        recs_frame = ttk.LabelFrame(parent_frame, text="Recommendations")
        recs_frame.pack(fill=tk.X, padx=10, pady=5, expand=True)
        
        for i, recommendation in enumerate(rec_data['recommendations']):
            rec_box = ttk.Frame(recs_frame, borderwidth=1, relief="groove")
            rec_box.pack(fill=tk.X, padx=5, pady=3, expand=True)
            
            # Ensure recommendation is a dictionary with required keys
            if isinstance(recommendation, dict):
                # Add recommendation header with priority indicator
                header_frame = ttk.Frame(rec_box)
                header_frame.pack(fill=tk.X, expand=True)
                
                # Get priority with a default value if not present
                priority = recommendation.get('priority', 'Medium')
                priority_label = ttk.Label(header_frame, text=priority)
                priority_label.pack(side=tk.RIGHT, padx=5)
                
                # Get title with a default value if not present
                title = recommendation.get('title', f'Recommendation {i+1}')
                title_label = ttk.Label(header_frame, text=f"{i+1}. {title}", 
                                       font=("Helvetica", 10, "bold"))
                title_label.pack(side=tk.LEFT, anchor=tk.W, padx=5)
                
                # Add explanation
                explanation = recommendation.get('explanation', 'No explanation available')
                desc_label = ttk.Label(rec_box, text=explanation, wraplength=600)
                desc_label.pack(anchor=tk.W, padx=5, pady=5)
                
                # Add action items if present
                if 'actions' in recommendation and recommendation['actions']:
                    action_label = ttk.Label(rec_box, text="Suggested Actions:", font=("Helvetica", 9, "italic"))
                    action_label.pack(anchor=tk.W, padx=5, pady=(5, 0))
                    
                    for action in recommendation['actions']:
                        action_item = ttk.Label(rec_box, text=f"• {action}", wraplength=580)
                        action_item.pack(anchor=tk.W, padx=15, pady=(0, 3))
            else:
                # Handle case where recommendation is not properly formatted
                title_label = ttk.Label(rec_box, text=f"{i+1}. Recommendation", font=("Helvetica", 10, "bold"))
                title_label.pack(anchor=tk.W, padx=5, pady=5)
                
                if isinstance(recommendation, str):
                    desc_label = ttk.Label(rec_box, text=recommendation, wraplength=600)
                    desc_label.pack(anchor=tk.W, padx=5, pady=5)
    
    # Visualization if available
    if 'visualization' in rec_data:
        viz_frame = ttk.LabelFrame(parent_frame, text="Visual Analysis")
        viz_frame.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)
        
        fig = plt.Figure(figsize=(8, 4))
        ax = fig.add_subplot(111)
        
        # Create the chart based on visualization type
        viz_data = rec_data['visualization']
        
        if viz_data['type'] == 'line':
            for line in viz_data['lines']:
                ax.plot(line['x'], line['y'], label=line['label'])
                
            ax.set_title(viz_data['title'])
            ax.set_xlabel(viz_data['xlabel'])
            ax.set_ylabel(viz_data['ylabel'])
            ax.legend()
            
        elif viz_data['type'] == 'bar':
            ax.bar(viz_data['x'], viz_data['y'])
            ax.set_title(viz_data['title'])
            ax.set_xlabel(viz_data['xlabel'])
            ax.set_ylabel(viz_data['ylabel'])
            
        elif viz_data['type'] == 'pie':
            ax.pie(viz_data['values'], labels=viz_data['labels'], autopct='%1.1f%%')
            ax.set_title(viz_data['title'])
            
        canvas = FigureCanvasTkAgg(fig, master=viz_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

def _export_recommendations(self):
    """Export recommendations to a formatted report"""
    if not hasattr(self, 'current_recommendations') or self.current_recommendations is None:
        messagebox.showwarning("No Recommendations", 
                               "Please generate recommendations first before exporting.")
        return
    
    # Ask for export file location
    file_path = filedialog.asksaveasfilename(
        defaultextension=".html",
        filetypes=[("HTML files", "*.html"), ("Text files", "*.txt"), ("All files", "*.*")]
    )
    
    if file_path:
        try:
            # Create HTML or text report based on extension
            if file_path.endswith('.html'):
                with open(file_path, 'w') as f:
                    # Generate HTML report
                    f.write('<html><head>')
                    f.write('<title>TrendLens Recommendations Report</title>')
                    f.write('<style>')
                    f.write('body { font-family: Arial, sans-serif; margin: 20px; }')
                    f.write('h1 { color: #2C3E50; }')
                    f.write('h2 { color: #3498DB; margin-top: 30px; border-bottom: 1px solid #BDC3C7; padding-bottom: 5px; }')
                    f.write('.summary { background-color: #F8F9F9; padding: 15px; border-left: 5px solid #3498DB; margin-bottom: 20px; }')
                    f.write('.recommendation { background-color: #F8F9F9; padding: 10px; margin: 10px 0; border-left: 5px solid #27AE60; }')
                    f.write('.priority-high { border-left: 5px solid #E74C3C; }')
                    f.write('.priority-medium { border-left: 5px solid #F39C12; }')
                    f.write('.priority-low { border-left: 5px solid #27AE60; }')
                    f.write('.action { margin-left: 20px; color: #7F8C8D; }')
                    f.write('</style></head><body>')
                    f.write(f'<h1>TrendLens Recommendations Report</h1>')
                    f.write(f'<p>Generated on {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")}</p>')
                    
                    # Add each recommendation type
                    for rec_type, rec_data in self.current_recommendations.items():
                        f.write(f'<h2>{rec_type}</h2>')
                        
                        # Summary
                        if 'summary' in rec_data:
                            f.write(f'<div class="summary">{rec_data["summary"]}</div>')
                        
                        # Key insights
                        if 'insights' in rec_data:
                            f.write('<h3>Key Insights</h3>')
                            for i, insight in enumerate(rec_data['insights']):
                                if isinstance(insight, dict) and 'title' in insight:
                                    f.write(f'<p><strong>{i+1}. {insight["title"]}</strong><br>')
                                    f.write(f'{insight.get("description", "")}</p>')
                                else:
                                    f.write(f'<p><strong>{i+1}. Insight</strong><br>')
                                    if isinstance(insight, str):
                                        f.write(f'{insight}</p>')
                        
                        # Recommendations
                        if 'recommendations' in rec_data:
                            f.write('<h3>Recommendations</h3>')
                            for i, recommendation in enumerate(rec_data['recommendations']):
                                if isinstance(recommendation, dict):
                                    priority = recommendation.get('priority', 'Medium').lower()
                                    priority_class = f'priority-{priority}'
                                    f.write(f'<div class="recommendation {priority_class}">')
                                    f.write(f'<p><strong>{i+1}. {recommendation.get("title", "Recommendation")}</strong> ')
                                    f.write(f'<span style="float:right">Priority: {recommendation.get("priority", "Medium")}</span></p>')
                                    f.write(f'<p>{recommendation.get("explanation", "")}</p>')
                                    
                                    if 'actions' in recommendation and recommendation['actions']:
                                        f.write('<p><em>Suggested Actions:</em></p><ul>')
                                        for action in recommendation['actions']:
                                            f.write(f'<li class="action">{action}</li>')
                                        f.write('</ul>')
                                    
                                    f.write('</div>')
                                else:
                                    f.write(f'<div class="recommendation">')
                                    f.write(f'<p><strong>{i+1}. Recommendation</strong></p>')
                                    if isinstance(recommendation, str):
                                        f.write(f'<p>{recommendation}</p>')
                                    f.write('</div>')
                    
                    f.write('</body></html>')
            else:
                # Create text report
                with open(file_path, 'w') as f:
                    f.write('TrendLens Recommendations Report\n')
                    f.write('================================\n\n')
                    f.write(f'Generated on {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")}\n\n')
                    
                    for rec_type, rec_data in self.current_recommendations.items():
                        f.write(f'\n{rec_type}\n')
                        f.write('=' * len(rec_type) + '\n\n')
                        
                        # Summary
                        if 'summary' in rec_data:
                            f.write('SUMMARY:\n')
                            f.write(f'{rec_data["summary"]}\n\n')
                        
                        # Key insights
                        if 'insights' in rec_data:
                            f.write('KEY INSIGHTS:\n')
                            for i, insight in enumerate(rec_data['insights']):
                                if isinstance(insight, dict) and 'title' in insight:
                                    f.write(f'{i+1}. {insight["title"]}\n')
                                    f.write(f'   {insight.get("description", "")}\n\n')
                                else:
                                    f.write(f'{i+1}. Insight\n')
                                    if isinstance(insight, str):
                                        f.write(f'   {insight}\n\n')
                        
                        # Recommendations
                        if 'recommendations' in rec_data:
                            f.write('RECOMMENDATIONS:\n')
                            for i, recommendation in enumerate(rec_data['recommendations']):
                                if isinstance(recommendation, dict):
                                    f.write(f'{i+1}. {recommendation.get("title", "Recommendation")} (Priority: {recommendation.get("priority", "Medium")})\n')
                                    f.write(f'   {recommendation.get("explanation", "")}\n\n')
                                    
                                    if 'actions' in recommendation and recommendation['actions']:
                                        f.write('   Suggested Actions:\n')
                                        for action in recommendation['actions']:
                                            f.write(f'   - {action}\n')
                                        f.write('\n')
                                else:
                                    f.write(f'{i+1}. Recommendation\n')
                                    if isinstance(recommendation, str):
                                        f.write(f'   {recommendation}\n\n')
            
            messagebox.showinfo("Export Complete", "Recommendations report exported successfully!")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting recommendations: {str(e)}")
