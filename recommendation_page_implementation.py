# RecommendationEngine.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import tkinter as tk
import customtkinter as ctk

class RecommendationEngine:
    def __init__(self, analyzers=None):
        """
        Initialize the RecommendationEngine with available data
        
        Parameters:
        analyzers (list): List of data analyzers or raw sales data
        """
        self.analyzers = analyzers
        
        # Extract and combine data if analyzers are provided
        if analyzers:
            self.sales_data = self._extract_sales_data(analyzers)
            self.inventory_data = self._extract_inventory_data(analyzers)
            self.market_data = self._extract_market_data(analyzers)
        else:
            self.sales_data = None
            self.inventory_data = None
            self.market_data = None
        
        self.recommendations = {}
    
    def _extract_sales_data(self, analyzers):
        """Extract sales data from analyzers"""
        # This is a placeholder - implement based on your analyzer structure
        # For demonstration, we'll return a simple DataFrame or None
        try:
            if hasattr(analyzers[0], 'sales_data'):
                return analyzers[0].sales_data
            elif hasattr(analyzers[0], 'data') and isinstance(analyzers[0].data, pd.DataFrame):
                return analyzers[0].data
            else:
                return None
        except (IndexError, AttributeError):
            return None
    
    def _extract_inventory_data(self, analyzers):
        """Extract inventory data from analyzers"""
        # This is a placeholder - implement based on your analyzer structure
        try:
            if hasattr(analyzers[0], 'inventory_data'):
                return analyzers[0].inventory_data
            else:
                return None
        except (IndexError, AttributeError):
            return None
    
    def _extract_market_data(self, analyzers):
        """Extract market data from analyzers"""
        # This is a placeholder - implement based on your analyzer structure
        try:
            if hasattr(analyzers[0], 'market_data'):
                return analyzers[0].market_data
            else:
                return None
        except (IndexError, AttributeError):
            return None
    
    def load_data(self, sales_path=None, inventory_path=None, market_path=None):
        """Load data from specified file paths"""
        if sales_path:
            self.sales_data = pd.read_csv(sales_path)
        if inventory_path:
            self.inventory_data = pd.read_csv(inventory_path)
        if market_path:
            self.market_data = pd.read_csv(market_path)
    
    def generate_recommendations(self, scope, recommendation_types, detail_level, include_market_analysis):
        """
        Generate comprehensive recommendations based on specified parameters
        
        Parameters:
        scope (str): Scope of analysis (e.g., "All", "Platform-A", etc.)
        recommendation_types (list): Types of recommendations to generate (e.g., ["pricing", "inventory", "marketing"])
        detail_level (str): Level of detail for recommendations (e.g., "Standard", "Advanced")
        include_market_analysis (bool): Whether to include market competitor analysis
        
        Returns:
        dict: Dictionary of categorized recommendations
        """
        self.recommendations = {}
        
        try:
            # Generate pricing recommendations if requested
            if "pricing" in recommendation_types:
                pricing_recs = self.generate_pricing_recommendations(
                    platform=scope if scope != "All" else "All",
                    detail_level=detail_level
                )
                
                if pricing_recs:
                    self.recommendations["Pricing Strategy"] = {
                        "summary": "Pricing strategy recommendations based on sales data",
                        "insights": [
                            {"title": "Price Elasticity Analysis", "description": "Products show varying price sensitivity"}
                        ],
                        "recommendations": []
                    }
                    
                    # Convert the list of recommendation objects to the expected format
                    for rec in pricing_recs:
                        if "type" in rec and rec["type"] != "Error":
                            formatted_rec = {
                                "title": rec["title"],
                                "explanation": rec["description"],
                                "priority": rec["priority"],
                                "actions": [rec["suggestion"]]
                            }
                            self.recommendations["Pricing Strategy"]["recommendations"].append(formatted_rec)
            
            # Generate inventory recommendations if requested
            if "inventory" in recommendation_types:
                inventory_recs = self.generate_inventory_recommendations(
                    threshold_days=30 if detail_level == "Standard" else 45
                )
                
                if inventory_recs:
                    self.recommendations["Inventory Management"] = {
                        "summary": "Inventory optimization recommendations based on sales velocity",
                        "insights": [
                            {"title": "Stock Level Analysis", "description": "Current stock levels relative to sales velocity"}
                        ],
                        "recommendations": []
                    }
                    
                    # Convert the list of recommendation objects to the expected format
                    for rec in inventory_recs:
                        if "type" in rec and rec["type"] != "Error":
                            formatted_rec = {
                                "title": rec["title"],
                                "explanation": rec["description"],
                                "priority": rec["priority"],
                                "actions": [rec["suggestion"]]
                            }
                            self.recommendations["Inventory Management"]["recommendations"].append(formatted_rec)
            
            # Generate marketing recommendations if requested
            if "marketing" in recommendation_types:
                marketing_recs = self.generate_marketing_recommendations(
                    conversion_threshold=0.02 if detail_level == "Standard" else 0.03
                )
                
                if marketing_recs:
                    self.recommendations["Marketing Strategy"] = {
                        "summary": "Marketing recommendations to improve sales",
                        "insights": [
                            {"title": "Conversion Analysis", "description": "Identify products with high views but low conversions"}
                        ],
                        "recommendations": []
                    }
                    
                    # Convert the list of recommendation objects to the expected format
                    for rec in marketing_recs:
                        if "type" in rec and rec["type"] != "Error":
                            formatted_rec = {
                                "title": rec["title"],
                                "explanation": rec["description"],
                                "priority": rec["priority"],
                                "actions": [rec["suggestion"]]
                            }
                            self.recommendations["Marketing Strategy"]["recommendations"].append(formatted_rec)
            
            # If we have no valid recommendations, provide a placeholder
            if not self.recommendations:
                self.recommendations = {
                    "General Recommendations": {
                        "summary": "No specific recommendations could be generated with the available data",
                        "insights": [],
                        "recommendations": [
                            {
                                "title": "Insufficient data",
                                "explanation": "Not enough data available to generate meaningful recommendations", 
                                "priority": "Low",
                                "actions": ["Collect more sales data", "Ensure data format is correct"]
                            }
                        ]
                    }
                }
            
            return self.recommendations
            
        except Exception as e:
            # In case of errors, return a simple error structure
            error_message = str(e)
            self.recommendations = {
                "Error": {
                    "summary": "Error generating recommendations",
                    "insights": [],
                    "recommendations": [
                        {
                            "title": "Error encountered",
                            "explanation": f"Error: {error_message}", 
                            "priority": "High",
                            "actions": ["Check data format", "Ensure all required columns are present"]
                        }
                    ]
                }
            }
            return self.recommendations
    
    def generate_pricing_recommendations(self, platform="All", detail_level="Standard"):
        """
        Generate pricing strategy recommendations based on sales data and market trends
        
        Parameters:
        platform (str): The e-commerce platform to analyze
        detail_level (str): Level of detail for recommendations (Standard or Advanced)
        
        Returns:
        list: List of recommendation dictionaries
        """
        recommendations = []
        
        if self.sales_data is None:
            return [{"type": "Error", "message": "No sales data available"}]
        
        try:
            # Filter data by platform if specified
            filtered_data = self.sales_data
            if platform != "All" and "platform" in self.sales_data.columns:
                filtered_data = self.sales_data[self.sales_data["platform"] == platform]
            
            # Basic price elasticity analysis
            if "price" in filtered_data.columns and "quantity_sold" in filtered_data.columns:
                # Group by product and analyze price vs. sales volume
                price_analysis = filtered_data.groupby("product_id").agg({
                    "price": ["mean", "min", "max", "std"],
                    "quantity_sold": ["sum", "mean"]
                })
                
                # Identify price sensitive products
                price_sensitive = []
                price_insensitive = []
                
                for idx, row in price_analysis.iterrows():
                    price_range = row[("price", "max")] - row[("price", "min")]
                    price_std = row[("price", "std")]
                    
                    if price_range > 0:
                        # If we have price variance, check sales correlation
                        product_data = filtered_data[filtered_data["product_id"] == idx]
                        
                        if len(product_data) >= 5:  # Need enough data points
                            corr = np.corrcoef(product_data["price"], product_data["quantity_sold"])[0, 1]
                            
                            if corr < -0.5:  # Strong negative correlation - price sensitive
                                price_sensitive.append({
                                    "product_id": idx,
                                    "elasticity": corr,
                                    "avg_price": row[("price", "mean")],
                                    "sales_volume": row[("quantity_sold", "sum")]
                                })
                            elif corr > -0.2:  # Weak correlation - price insensitive
                                price_insensitive.append({
                                    "product_id": idx,
                                    "elasticity": corr,
                                    "avg_price": row[("price", "mean")],
                                    "sales_volume": row[("quantity_sold", "sum")]
                                })
            
                # Generate recommendations based on elasticity
                if price_sensitive:
                    recommendations.append({
                        "type": "Price Optimization",
                        "title": "Optimize pricing for price-sensitive products",
                        "description": f"Found {len(price_sensitive)} products with high price sensitivity.",
                        "suggestion": "Consider strategic discounting or bundle pricing for these products.",
                        "products": price_sensitive[:5] if detail_level == "Standard" else price_sensitive,
                        "priority": "High"
                    })
                
                if price_insensitive:
                    recommendations.append({
                        "type": "Premium Pricing",
                        "title": "Premium pricing opportunity",
                        "description": f"Found {len(price_insensitive)} products with low price sensitivity.",
                        "suggestion": "Consider gradual price increases or premium positioning for these products.",
                        "products": price_insensitive[:5] if detail_level == "Standard" else price_insensitive,
                        "priority": "Medium"
                    })
            
            # Competitive pricing analysis if market data is available
            if self.market_data is not None and "competitor_price" in self.market_data.columns:
                merged_data = pd.merge(
                    filtered_data, 
                    self.market_data, 
                    on="product_id", 
                    how="inner"
                )
                
                # Find products priced significantly higher or lower than competitors
                merged_data["price_diff"] = merged_data["price"] - merged_data["competitor_price"]
                merged_data["price_diff_pct"] = (merged_data["price_diff"] / merged_data["competitor_price"]) * 100
                
                overpriced = merged_data[merged_data["price_diff_pct"] > 15].groupby("product_id").mean()
                underpriced = merged_data[merged_data["price_diff_pct"] < -15].groupby("product_id").mean()
                
                if len(overpriced) > 0:
                    recommendations.append({
                        "type": "Competitive Pricing",
                        "title": "Overpriced products relative to competitors",
                        "description": f"Found {len(overpriced)} products priced significantly higher than competitors.",
                        "suggestion": "Consider price adjustments or highlighting unique value proposition.",
                        "products": overpriced.index.tolist()[:5] if detail_level == "Standard" else overpriced.index.tolist(),
                        "priority": "High"
                    })
                
                if len(underpriced) > 0:
                    recommendations.append({
                        "type": "Competitive Pricing",
                        "title": "Underpriced products relative to competitors",
                        "description": f"Found {len(underpriced)} products priced significantly lower than competitors.",
                        "suggestion": "Consider price increases to maximize margin or promotional emphasis.",
                        "products": underpriced.index.tolist()[:5] if detail_level == "Standard" else underpriced.index.tolist(),
                        "priority": "Medium"
                    })
            
            # Add advanced analysis if requested
            if detail_level == "Advanced":
                # Time-based pricing recommendations (seasonal, day of week)
                if "date" in filtered_data.columns:
                    # Convert to datetime if not already
                    if not pd.api.types.is_datetime64_any_dtype(filtered_data["date"]):
                        filtered_data["date"] = pd.to_datetime(filtered_data["date"])
                    
                    # Extract time components
                    filtered_data["day_of_week"] = filtered_data["date"].dt.day_name()
                    filtered_data["month"] = filtered_data["date"].dt.month_name()
                    
                    # Day of week analysis
                    dow_analysis = filtered_data.groupby("day_of_week").agg({
                        "quantity_sold": "sum",
                        "revenue": "sum"
                    }).reset_index()
                    
                    # Find best and worst selling days
                    best_day = dow_analysis.loc[dow_analysis["quantity_sold"].idxmax()]
                    worst_day = dow_analysis.loc[dow_analysis["quantity_sold"].idxmin()]
                    
                    if best_day["quantity_sold"] > worst_day["quantity_sold"] * 1.3:  # At least 30% difference
                        recommendations.append({
                            "type": "Dynamic Pricing",
                            "title": "Day-of-week pricing strategy",
                            "description": f"{best_day['day_of_week']} shows {best_day['quantity_sold']/worst_day['quantity_sold']:.1f}x higher sales than {worst_day['day_of_week']}.",
                            "suggestion": f"Consider higher prices on {best_day['day_of_week']} and promotions on {worst_day['day_of_week']}.",
                            "data": dow_analysis.to_dict(orient="records"),
                            "priority": "Medium"
                        })
                    
                    # Monthly/seasonal analysis
                    if "month" in filtered_data.columns:
                        month_analysis = filtered_data.groupby("month").agg({
                            "quantity_sold": "sum",
                            "revenue": "sum"
                        }).reset_index()
                        
                        recommendations.append({
                            "type": "Seasonal Pricing",
                            "title": "Monthly sales pattern analysis",
                            "description": "Sales show seasonal patterns that can inform pricing strategy.",
                            "suggestion": "Adjust pricing based on monthly demand patterns.",
                            "data": month_analysis.to_dict(orient="records"),
                            "priority": "Low"
                        })
            
            return recommendations
            
        except Exception as e:
            return [{"type": "Error", "message": f"Error generating pricing recommendations: {str(e)}"}]
    
    def generate_inventory_recommendations(self, threshold_days=30, safety_stock_percentage=0.2):
        """
        Generate inventory management recommendations based on sales velocity and stock levels
        
        Parameters:
        threshold_days (int): Number of days to consider for stock projection
        safety_stock_percentage (float): Percentage of extra stock to recommend as safety buffer
        
        Returns:
        list: List of recommendation dictionaries
        """
        recommendations = []
        
        if self.sales_data is None or self.inventory_data is None:
            return [{"type": "Error", "message": "Missing sales or inventory data"}]
        
        try:
            # Calculate sales velocity (average daily sales) per product
            if "date" in self.sales_data.columns and "product_id" in self.sales_data.columns:
                # Ensure date column is datetime
                if not pd.api.types.is_datetime64_any_dtype(self.sales_data["date"]):
                    self.sales_data["date"] = pd.to_datetime(self.sales_data["date"])
                
                # Get date range
                date_min = self.sales_data["date"].min()
                date_max = self.sales_data["date"].max()
                date_range = (date_max - date_min).days + 1  # Add 1 to include both start and end dates
                
                # Calculate average daily sales
                product_sales = self.sales_data.groupby("product_id")["quantity_sold"].sum().reset_index()
                product_sales["daily_sales"] = product_sales["quantity_sold"] / date_range
                
                # Merge with inventory data
                inventory_status = pd.merge(
                    product_sales,
                    self.inventory_data,
                    on="product_id",
                    how="inner"
                )
                
                # Calculate days of inventory remaining
                inventory_status["days_remaining"] = inventory_status["current_stock"] / inventory_status["daily_sales"]
                
                # Handle infinite values (no sales)
                inventory_status["days_remaining"] = inventory_status["days_remaining"].replace([np.inf, -np.inf], np.nan)
                
                # Low stock alerts
                low_stock = inventory_status[inventory_status["days_remaining"] < threshold_days]
                if len(low_stock) > 0:
                    recommendations.append({
                        "type": "Stock Alert",
                        "title": "Low stock alert",
                        "description": f"{len(low_stock)} products will run out of stock within {threshold_days} days.",
                        "suggestion": "Reorder these products soon.",
                        "products": low_stock.to_dict(orient="records"),
                        "priority": "High"
                    })
                
                # Overstock alerts
                high_inventory_days = threshold_days * 3  # Example threshold - adjust as needed
                overstock = inventory_status[inventory_status["days_remaining"] > high_inventory_days]
                if len(overstock) > 0:
                    recommendations.append({
                        "type": "Stock Alert",
                        "title": "Potential overstock issue",
                        "description": f"{len(overstock)} products have more than {high_inventory_days} days of inventory.",
                        "suggestion": "Consider promotions or stop purchasing these items temporarily.",
                        "products": overstock.to_dict(orient="records"),
                        "priority": "Medium"
                    })
                
                # Reorder calculations
                inventory_status["reorder_point"] = (inventory_status["daily_sales"] * threshold_days) * (1 + safety_stock_percentage)
                reorder_needed = inventory_status[inventory_status["current_stock"] < inventory_status["reorder_point"]]
                
                if len(reorder_needed) > 0:
                    recommendations.append({
                        "type": "Reorder Planning",
                        "title": "Products to reorder",
                        "description": f"{len(reorder_needed)} products are below the recommended reorder point.",
                        "suggestion": "Place purchase orders based on the recommended quantities.",
                        "products": reorder_needed.to_dict(orient="records"),
                        "priority": "High"
                    })
            
            return recommendations
            
        except Exception as e:
            return [{"type": "Error", "message": f"Error generating inventory recommendations: {str(e)}"}]
    
    def generate_marketing_recommendations(self, conversion_threshold=0.02, traffic_threshold=100):
        """
        Generate marketing recommendations based on product performance metrics
        
        Parameters:
        conversion_threshold (float): Minimum acceptable conversion rate
        traffic_threshold (int): Minimum traffic to be considered for analysis
        
        Returns:
        list: List of recommendation dictionaries
        """
        recommendations = []
        
        if self.sales_data is None:
            return [{"type": "Error", "message": "No sales data available"}]
        
        try:
            # For marketing recommendations, we need product performance metrics
            if all(col in self.sales_data.columns for col in ["product_id", "views", "conversions"]):
                # Calculate conversion rates
                product_metrics = self.sales_data.groupby("product_id").agg({
                    "views": "sum",
                    "conversions": "sum",
                    "revenue": "sum"
                }).reset_index()
                
                product_metrics["conversion_rate"] = product_metrics["conversions"] / product_metrics["views"]
                
                # Filter for products with significant traffic
                product_metrics = product_metrics[product_metrics["views"] >= traffic_threshold]
                
                # Low conversion products with high traffic
                low_conversion = product_metrics[product_metrics["conversion_rate"] < conversion_threshold]
                if len(low_conversion) > 0:
                    recommendations.append({
                        "type": "Conversion Optimization",
                        "title": "Low converting products",
                        "description": f"Found {len(low_conversion)} products with conversion rates below {conversion_threshold*100:.1f}%.",
                        "suggestion": "Improve product pages, photos, or descriptions. Consider price adjustments.",
                        "products": low_conversion.to_dict(orient="records"),
                        "priority": "High"
                    })
                
                # High conversion products - growth opportunities
                high_conversion = product_metrics[product_metrics["conversion_rate"] > (conversion_threshold * 2)]
                if len(high_conversion) > 0:
                    recommendations.append({
                        "type": "Growth Opportunity",
                        "title": "High converting products",
                        "description": f"Found {len(high_conversion)} products with excellent conversion rates.",
                        "suggestion": "Increase marketing spend for these products to drive more traffic.",
                        "products": high_conversion.to_dict(orient="records"),
                        "priority": "Medium"
                    })
                
                # Calculate revenue per view
                product_metrics["revenue_per_view"] = product_metrics["revenue"] / product_metrics["views"]
                
                # Sort by revenue per view to find most effective products
                top_performers = product_metrics.sort_values("revenue_per_view", ascending=False).head(10)
                recommendations.append({
                    "type": "Traffic Allocation",
                    "title": "Top performing products by revenue per view",
                    "description": "These products generate the most revenue per page view.",
                    "suggestion": "Prioritize these products in marketing campaigns and site placement.",
                    "products": top_performers.to_dict(orient="records"),
                    "priority": "High"
                })
            
            return recommendations
            
        except Exception as e:
            return [{"type": "Error", "message": f"Error generating marketing recommendations: {str(e)}"}]

    def export_recommendations(self, file_path, format="json"):
        """
        Export recommendations to a file
        
        Parameters:
        file_path (str): Path to save the recommendations
        format (str): Output format (json or csv)
        
        Returns:
        bool: Success status
        """
        if not self.recommendations:
            return False
        
        try:
            if format.lower() == "json":
                import json
                with open(file_path, 'w') as f:
                    json.dump(self.recommendations, f, indent=2)
            elif format.lower() == "csv":
                # Flatten the nested structure for CSV
                flattened = []
                for category, data in self.recommendations.items():
                    for recommendation in data.get("recommendations", []):
                        row = {
                            "category": category,
                            "title": recommendation.get("title", ""),
                            "explanation": recommendation.get("explanation", ""),
                            "priority": recommendation.get("priority", ""),
                            "actions": ", ".join(recommendation.get("actions", []))
                        }
                        flattened.append(row)
                
                pd.DataFrame(flattened).to_csv(file_path, index=False)
            else:
                return False
            
            return True
        except Exception:
            return False

    def create_dashboard(self):
        """
        Create a simple GUI dashboard to display recommendations
        
        Returns:
        None: Opens a GUI window
        """
        # Create the main window
        root = ctk.CTk()
        root.title("Recommendation Dashboard")
        root.geometry("800x600")
        
        # Set the appearance mode and color theme
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        # Create main frame
        main_frame = ctk.CTkFrame(root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        header_label = ctk.CTkLabel(main_frame, text="E-commerce Recommendations", font=("Arial", 18, "bold"))
        header_label.pack(pady=10)
        
        # Create a tabview for different recommendation types
        tabview = ctk.CTkTabview(main_frame)
        tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs for each recommendation category
        for category in self.recommendations.keys():
            tab = tabview.add(category)
            
            # Add a scrollable frame for recommendations
            scroll_frame = ctk.CTkScrollableFrame(tab)
            scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Add a header with summary
            summary = self.recommendations[category].get("summary", "")
            summary_label = ctk.CTkLabel(scroll_frame, text=summary, font=("Arial", 14))
            summary_label.pack(pady=5, anchor="w")
            
            # Add each recommendation
            for i, rec in enumerate(self.recommendations[category].get("recommendations", [])):
                # Create a frame for each recommendation
                rec_frame = ctk.CTkFrame(scroll_frame)
                rec_frame.pack(fill="x", padx=5, pady=5, anchor="w")
                
                # Add recommendation title
                title_label = ctk.CTkLabel(rec_frame, text=rec.get("title", ""), font=("Arial", 12, "bold"))
                title_label.pack(pady=2, anchor="w")
                
                # Add explanation
                explanation = rec.get("explanation", "")
                if explanation:
                    explanation_label = ctk.CTkLabel(rec_frame, text=explanation, wraplength=700)
                    explanation_label.pack(pady=2, anchor="w")
                
                # Add priority
                priority = rec.get("priority", "")
                if priority:
                    priority_color = "green" if priority == "Low" else "orange" if priority == "Medium" else "red"
                    priority_frame = ctk.CTkFrame(rec_frame, fg_color=priority_color)
                    priority_frame.pack(anchor="w", pady=2)
                    priority_label = ctk.CTkLabel(priority_frame, text=f"Priority: {priority}", text_color="white")
                    priority_label.pack(padx=5, pady=2)
                
                # Add actions if available
                actions = rec.get("actions", [])
                if actions:
                    actions_label = ctk.CTkLabel(rec_frame, text="Actions:", font=("Arial", 11, "bold"))
                    actions_label.pack(pady=2, anchor="w")
                    for action in actions:
                        action_label = ctk.CTkLabel(rec_frame, text=f"• {action}")
                        action_label.pack(pady=1, anchor="w", padx=10)
        
        # Additional buttons (export, refresh, etc.)
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=10)
        
        export_button = ctk.CTkButton(button_frame, text="Export Recommendations", 
                                      command=lambda: self.export_recommendations("recommendations.json"))
        export_button.pack(side="left", padx=10)
        
        refresh_button = ctk.CTkButton(button_frame, text="Refresh Recommendations",
                                       command=lambda: self.generate_recommendations("All", ["pricing", "inventory", "marketing"], "Standard", True))
        refresh_button.pack(side="left", padx=10)
        
        close_button = ctk.CTkButton(button_frame, text="Close", command=root.destroy)
        close_button.pack(side="right", padx=10)
        
        # Start the main loop
        root.mainloop()


# Example usage
if __name__ == "__main__":
    # Create an instance of the RecommendationEngine
    engine = RecommendationEngine()
    
    # Load data
    engine.load_data(
        sales_path="sales_data.csv",
        inventory_path="inventory_data.csv",
        market_path="market_data.csv"
    )
    
    # Generate recommendations
    recommendations = engine.generate_recommendations(
        scope="All", 
        recommendation_types=["pricing", "inventory", "marketing"],
        detail_level="Standard",
        include_market_analysis=True
    )
    
    # Show dashboard
    engine.create_dashboard()
