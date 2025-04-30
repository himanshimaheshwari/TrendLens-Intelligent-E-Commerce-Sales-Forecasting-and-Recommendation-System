import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import statsmodels.api as sm
from datetime import datetime, timedelta

class CrossPlatformAnalyzer:
    """
    Advanced cross-platform analysis and recommendation engine
    """
    def __init__(self, platform_analyzers):
        """
        Initialize with a list of TrendLensECommerceAnalyzer objects
        """
        self.platform_analyzers = platform_analyzers
        self.comparison_data = None
        self.aligned_data = None
        self.correlation_matrix = None
        self.recommendations = None
        
    def align_platform_data(self):
        """
        Align data from different platforms to a common date range
        """
        # Check if we have data for all platforms
        for analyzer in self.platform_analyzers:
            if analyzer.processed_data is None:
                analyzer.preprocess_data()
        
        # Find common date range
        start_dates = [analyzer.processed_data.index.min() for analyzer in self.platform_analyzers]
        end_dates = [analyzer.processed_data.index.max() for analyzer in self.platform_analyzers]
        
        common_start = max(start_dates)
        common_end = min(end_dates)
        
        # Create aligned dataframe
        aligned_data = pd.DataFrame(index=pd.date_range(common_start, common_end))
        
        # Add sales data for each platform
        for analyzer in self.platform_analyzers:
            platform_sales = analyzer.processed_data['sales']
            aligned_data[analyzer.platform_name] = platform_sales.reindex(aligned_data.index)
        
        # Fill any missing values
        aligned_data.fillna(method='ffill', inplace=True)
        aligned_data.fillna(method='bfill', inplace=True)
        
        self.aligned_data = aligned_data
        return aligned_data
        
    def compute_correlations(self):
        """
        Compute sales correlations between platforms
        """
        if self.aligned_data is None:
            self.align_platform_data()
            
        self.correlation_matrix = self.aligned_data.corr()
        return self.correlation_matrix
    
    def analyze_seasonal_patterns(self):
        """
        Identify and compare seasonal patterns across platforms
        """
        if self.aligned_data is None:
            self.align_platform_data()
            
        # Add date components
        data = self.aligned_data.copy()
        data['month'] = data.index.month
        data['day_of_week'] = data.index.dayofweek
        data['quarter'] = data.index.quarter
        
        # Monthly patterns
        monthly_patterns = {}
        for platform in self.platform_analyzers:
            name = platform.platform_name
            if name in data.columns:
                monthly_patterns[name] = data.groupby('month')[name].mean()
        
        # Weekly patterns
        weekly_patterns = {}
        for platform in self.platform_analyzers:
            name = platform.platform_name
            if name in data.columns:
                weekly_patterns[name] = data.groupby('day_of_week')[name].mean()
                
        return {
            'monthly': pd.DataFrame(monthly_patterns),
            'weekly': pd.DataFrame(weekly_patterns)
        }
    
    def identify_growth_trends(self):
        """
        Calculate and compare growth trends across platforms
        """
        if self.aligned_data is None:
            self.align_platform_data()
            
        growth_metrics = {}
        
        for platform in self.platform_analyzers:
            name = platform.platform_name
            if name in self.aligned_data.columns:
                sales = self.aligned_data[name]
                
                # Calculate metrics
                growth_metrics[name] = {
                    'mean': sales.mean(),
                    'std': sales.std(),
                    'min': sales.min(),
                    'max': sales.max(),
                    'growth_rate': ((sales.iloc[-1] / sales.iloc[0]) - 1) * 100 if sales.iloc[0] != 0 else np.nan,
                    'volatility': sales.std() / sales.mean() if sales.mean() != 0 else np.nan
                }
                
                # Add linear trend
                X = np.arange(len(sales)).reshape(-1, 1)
                y = sales.values
                model = sm.OLS(y, sm.add_constant(X)).fit()
                growth_metrics[name]['trend_coefficient'] = model.params[1]
                growth_metrics[name]['trend_p_value'] = model.pvalues[1]
                
        return pd.DataFrame(growth_metrics).T
    
    def generate_recommendations(self):
        """
        Generate actionable recommendations based on cross-platform analysis
        """
        if self.aligned_data is None:
            self.align_platform_data()
            
        growth_trends = self.identify_growth_trends()
        seasonal_patterns = self.analyze_seasonal_patterns()
        correlations = self.compute_correlations()
        
        # Dictionary to store recommendations
        recommendations = {}
        
        # 1. Overall performance comparison
        best_performer = growth_trends['growth_rate'].idxmax()
        worst_performer = growth_trends['growth_rate'].idxmin()
        
        recommendations['overall_performance'] = {
            'best_platform': best_performer,
            'worst_platform': worst_performer,
            'insight': f"{best_performer} shows the highest growth rate at {growth_trends.loc[best_performer, 'growth_rate']:.2f}%. "
                      f"Consider analyzing its marketing and product strategies for insights that could be applied to other platforms."
        }
        
        # 2. Volatility analysis
        most_stable = growth_trends['volatility'].idxmin()
        most_volatile = growth_trends['volatility'].idxmax()
        
        recommendations['volatility_insights'] = {
            'most_stable': most_stable,
            'most_volatile': most_volatile,
            'insight': f"{most_stable} shows the most stable sales patterns. If other platforms are more volatile, "
                      f"consider adopting {most_stable}'s inventory or pricing strategies to stabilize performance."
        }
        
        # 3. Seasonal strategy recommendations
        monthly_patterns = seasonal_patterns['monthly']
        best_months = {}
        
        for platform in monthly_patterns.columns:
            best_month = monthly_patterns[platform].idxmax()
            best_months[platform] = best_month
        
        # Find platforms with different peak months
        unique_peak_months = set(best_months.values())
        
        seasonal_insight = "Each platform has different peak sales months: "
        for platform, month in best_months.items():
            month_name = datetime(2020, month, 1).strftime('%B')
            seasonal_insight += f"{platform} peaks in {month_name}, "
        
        seasonal_insight = seasonal_insight[:-2] + "."
        if len(unique_peak_months) > 1:
            seasonal_insight += " Consider staggering marketing campaigns to capitalize on different seasonal peaks."
            
        recommendations['seasonal_insights'] = {
            'best_months': best_months,
            'insight': seasonal_insight
        }
        
        # 4. Correlation-based recommendations
        # If platforms are highly correlated, they might be competing for the same customers
        if correlations.shape[0] > 1:  # Need at least 2 platforms for correlation
            for i in range(len(correlations.columns)):
                for j in range(i+1, len(correlations.columns)):
                    platform1 = correlations.columns[i]
                    platform2 = correlations.columns[j]
                    corr_value = correlations.iloc[i, j]
                    
                    if corr_value > 0.7:
                        key = f"correlation_{platform1}_{platform2}"
                        recommendations[key] = {
                            'platforms': [platform1, platform2],
                            'correlation': corr_value,
                            'insight': f"High correlation ({corr_value:.2f}) between {platform1} and {platform2} "
                                      f"suggests they may be competing for the same customer base. "
                                      f"Consider differentiating product offerings or targeting different demographics."
                        }
                    elif corr_value < -0.3:
                        key = f"negative_correlation_{platform1}_{platform2}"
                        recommendations[key] = {
                            'platforms': [platform1, platform2],
                            'correlation': corr_value,
                            'insight': f"Negative correlation ({corr_value:.2f}) between {platform1} and {platform2} "
                                      f"suggests they may be complementary. Consider cross-platform promotions "
                                      f"or bundling strategies."
                        }
        
        self.recommendations = recommendations
        return recommendations
    
    def visualize_platform_comparison(self):
        """
        Create visualization for platform comparison
        """
        if self.aligned_data is None:
            self.align_platform_data()
            
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Sales trends over time
        self.aligned_data.plot(ax=axes[0, 0])
        axes[0, 0].set_title('Sales Trends Comparison')
        axes[0, 0].set_ylabel('Sales')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Correlation heatmap
        if self.correlation_matrix is None:
            self.compute_correlations()
            
        sns.heatmap(self.correlation_matrix, annot=True, cmap='coolwarm', ax=axes[0, 1])
        axes[0, 1].set_title('Platform Sales Correlation')
        
        # 3. Monthly patterns
        seasonal_patterns = self.analyze_seasonal_patterns()
        monthly_df = seasonal_patterns['monthly']
        monthly_df.plot(ax=axes[1, 0])
        axes[1, 0].set_title('Monthly Sales Patterns')
        axes[1, 0].set_xlabel('Month')
        axes[1, 0].set_ylabel('Average Sales')
        axes[1, 0].set_xticks(range(1, 13))
        axes[1, 0].set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Growth rates and volatility
        growth_metrics = self.identify_growth_trends()
        
        x = growth_metrics['growth_rate']
        y = growth_metrics['volatility']
        
        # Ensure we have valid data
        valid_mask = ~(np.isnan(x) | np.isnan(y))
        platforms = growth_metrics.index[valid_mask]
        x = x[valid_mask]
        y = y[valid_mask]
        
        if len(platforms) > 0:
            axes[1, 1].scatter(x, y)
            
            # Add platform labels
            for i, platform in enumerate(platforms):
                axes[1, 1].annotate(platform, (x.iloc[i], y.iloc[i]))
                
            axes[1, 1].set_title('Growth vs. Volatility')
            axes[1, 1].set_xlabel('Growth Rate (%)')
            axes[1, 1].set_ylabel('Volatility (CoV)')
            axes[1, 1].grid(True, alpha=0.3)
        else:
            axes[1, 1].text(0.5, 0.5, 'Insufficient data', 
                           horizontalalignment='center', 
                           verticalalignment='center')
        
        plt.tight_layout()
        return fig

class RecommendationEngine:
    """
    Advanced recommendation engine for e-commerce platforms
    """
    def __init__(self, cross_platform_analyzer):
        self.analyzer = cross_platform_analyzer
        self.recommendations = None
        
    def generate_detailed_recommendations(self):
        """
        Generate detailed, actionable recommendations
        """
        # Ensure we have base recommendations
        if self.analyzer.recommendations is None:
            self.analyzer.generate_recommendations()
            
        base_recommendations = self.analyzer.recommendations
        growth_trends = self.analyzer.identify_growth_trends()
        
        detailed_recommendations = {
            'strategic': [],
            'operational': [],
            'marketing': [],
            'inventory': []
        }
        
        # 1. Strategic Recommendations
        best_platform = base_recommendations['overall_performance']['best_platform']
        worst_platform = base_recommendations['overall_performance']['worst_platform']
        
        detailed_recommendations['strategic'].append({
            'title': 'Platform Strategy Optimization',
            'description': f"Focus resources on {best_platform} which shows the highest growth rate at {growth_trends.loc[best_platform, 'growth_rate']:.2f}%.",
            'action_items': [
                f"Analyze {best_platform}'s product mix and pricing strategy",
                f"Consider similar product selections for {worst_platform}",
                "Implement cross-platform analytics to monitor performance changes"
            ],
            'priority': 'High',
            'estimated_impact': 'High'
        })
        
        # 2. Operational Recommendations
        most_stable = base_recommendations['volatility_insights']['most_stable']
        
        detailed_recommendations['operational'].append({
            'title': 'Sales Stability Enhancement',
            'description': f"Adopt inventory and pricing strategies from {most_stable} to stabilize performance across all platforms.",
            'action_items': [
                f"Analyze {most_stable}'s inventory management approach",
                "Implement dynamic pricing based on platform-specific demand patterns",
                "Create a unified inventory system across platforms to optimize stock levels"
            ],
            'priority': 'Medium',
            'estimated_impact': 'Medium'
        })
        
        # 3. Marketing Recommendations
        best_months = base_recommendations['seasonal_insights']['best_months']
        
        marketing_rec = {
            'title': 'Platform-Specific Seasonal Marketing',
            'description': "Optimize marketing spend by focusing on peak months for each platform.",
            'action_items': [],
            'priority': 'High',
            'estimated_impact': 'High'
        }
        
        for platform, month in best_months.items():
            month_name = datetime(2020, month, 1).strftime('%B')
            marketing_rec['action_items'].append(f"Increase {platform} marketing budget in {month_name}")
            
        detailed_recommendations['marketing'].append(marketing_rec)
        
        # 4. Inventory Recommendations
        # Find periods of high sales across all platforms
        if self.analyzer.aligned_data is not None:
            # Calculate rolling mean of sum across platforms
            platform_sum = self.analyzer.aligned_data.sum(axis=1)
            platform_sum_ma = platform_sum.rolling(window=7).mean()
            
            # Find top 10% of sales days
            threshold = platform_sum_ma.quantile(0.9)
            high_demand_periods = platform_sum_ma[platform_sum_ma > threshold]
            
            # Group by month to identify seasonal patterns
            high_demand_months = high_demand_periods.groupby(high_demand_periods.index.month).count()
            top_month = high_demand_months.idxmax()
            top_month_name = datetime(2020, top_month, 1).strftime('%B')
            
            detailed_recommendations['inventory'].append({
                'title': 'Inventory Optimization',
                'description': f"Prepare for peak demand periods across all platforms, especially in {top_month_name}.",
                'action_items': [
                    f"Increase inventory levels by 20% before {top_month_name}",
                    "Implement cross-platform inventory sharing to mitigate stockouts",
                    "Develop contingency relationships with suppliers for rapid restocking"
                ],
                'priority': 'High',
                'estimated_impact': 'High'
            })
        
        self.recommendations = detailed_recommendations
        return detailed_recommendations
    
    def generate_executive_summary(self):
        """
        Generate an executive summary of recommendations
        """
        if self.recommendations is None:
            self.generate_detailed_recommendations()
            
        # Create summary
        summary = {
            'title': 'E-Commerce Platform Optimization: Executive Summary',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'key_findings': [],
            'top_recommendations': [],
            'estimated_impact': ""
        }
        
        # Get base analytics
        if self.analyzer.recommendations is not None:
            base_recs = self.analyzer.recommendations
            
            # Add key findings
            if 'overall_performance' in base_recs:
                summary['key_findings'].append(
                    f"{base_recs['overall_performance']['best_platform']} is the best performing platform "
                    f"with highest growth rate."
                )
            
            if 'volatility_insights' in base_recs:
                summary['key_findings'].append(
                    f"{base_recs['volatility_insights']['most_stable']} shows the most stable sales patterns."
                )
            
            if 'seasonal_insights' in base_recs:
                seasons = []
                for platform, month in base_recs['seasonal_insights']['best_months'].items():
                    month_name = datetime(2020, month, 1).strftime('%B')
                    seasons.append(f"{platform}: {month_name}")
                
                summary['key_findings'].append(
                    f"Peak sales months vary by platform: {', '.join(seasons)}"
                )
        
        # Add top recommendations from each category
        for category, recs in self.recommendations.items():
            if recs:
                # Get highest priority recommendation
                high_priority = [r for r in recs if r['priority'] == 'High']
                if high_priority:
                    summary['top_recommendations'].append(
                        f"{category.capitalize()}: {high_priority[0]['title']} - {high_priority[0]['description']}"
                    )
        
        # Estimate overall impact
        high_impact_count = 0
        for category, recs in self.recommendations.items():
            for rec in recs:
                if rec['estimated_impact'] == 'High':
                    high_impact_count += 1
        
        if high_impact_count >= 3:
            impact = "Implementation of these recommendations is expected to significantly improve overall platform performance."
        else:
            impact = "Implementation of these recommendations should lead to moderate improvements in platform performance."
            
        summary['estimated_impact'] = impact
        
        return summary
    
    def visualize_recommendations(self):
        """
        Create visual summary of recommendations
        """
        if self.recommendations is None:
            self.generate_detailed_recommendations()
            
        # Count recommendations by category and priority
        categories = list(self.recommendations.keys())
        high_priority = []
        medium_priority = []
        
        for category in categories:
            high_count = len([r for r in self.recommendations[category] if r['priority'] == 'High'])
            medium_count = len([r for r in self.recommendations[category] if r['priority'] == 'Medium'])
            
            high_priority.append(high_count)
            medium_priority.append(medium_count)
        
        # Create stacked bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        
        bar_width = 0.35
        x = np.arange(len(categories))
        
        ax.bar(x, high_priority, bar_width, label='High Priority', color='crimson')
        ax.bar(x, medium_priority, bar_width, bottom=high_priority, label='Medium Priority', color='orange')
        
        ax.set_xlabel('Recommendation Categories')
        ax.set_ylabel('Number of Recommendations')
        ax.set_title('Recommendations by Category and Priority')
        ax.set_xticks(x)
        ax.set_xticklabels([c.capitalize() for c in categories])
        ax.legend()
        
        plt.tight_layout()
        return fig
