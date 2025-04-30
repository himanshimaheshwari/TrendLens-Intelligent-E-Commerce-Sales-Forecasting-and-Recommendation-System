# Step 6: Tableau Integration

import pandas as pd
import os
import subprocess
import tableauserverclient as TSC
from pathlib import Path
import datetime
import json

class TableauIntegration:
    def __init__(self, data_manager, output_dir='tableau_data'):
        """
        Initialize the Tableau integration module
        
        Parameters:
        -----------
        data_manager : object
            Data manager class instance with access to the application data
        output_dir : str
            Directory to save Tableau extract files
        """
        self.data_manager = data_manager
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def export_data_for_tableau(self, dataset_name, data=None):
        """
        Export data to CSV format for Tableau consumption
        
        Parameters:
        -----------
        dataset_name : str
            Name of the dataset to export
        data : DataFrame, optional
            Data to export. If None, retrieve from data manager
            
        Returns:
        --------
        str : Path to the exported file
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{dataset_name}_{timestamp}.csv"
        file_path = os.path.join(self.output_dir, file_name)
        
        # Get data if not provided
        if data is None:
            data = self.data_manager.get_dataset(dataset_name)
        
        # Export to CSV
        data.to_csv(file_path, index=False)
        
        print(f"Data exported to {file_path} for Tableau")
        return file_path
    
    def create_metadata_json(self, dataset_name, file_path, column_descriptions=None):
        """
        Create metadata JSON file for Tableau
        
        Parameters:
        -----------
        dataset_name : str
            Name of the dataset
        file_path : str
            Path to the CSV file
        column_descriptions : dict, optional
            Dictionary of column descriptions
            
        Returns:
        --------
        str : Path to the metadata file
        """
        metadata = {
            "dataset_name": dataset_name,
            "source_file": file_path,
            "created_at": datetime.datetime.now().isoformat(),
            "columns": {}
        }
        
        # Get data to extract column information
        data = pd.read_csv(file_path)
        
        # Add column information
        for column in data.columns:
            metadata["columns"][column] = {
                "data_type": str(data[column].dtype),
                "description": column_descriptions.get(column, "") if column_descriptions else ""
            }
        
        # Write metadata to file
        metadata_file = file_path.replace(".csv", "_metadata.json")
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=4)
            
        return metadata_file
    
    def generate_tableau_template(self, dataset_name, template_type='dashboard'):
        """
        Generate a basic Tableau template based on the dataset
        
        Parameters:
        -----------
        dataset_name : str
            Name of the dataset for the template
        template_type : str
            Type of template to generate (dashboard, report, etc.)
            
        Returns:
        --------
        str : Message about the template generation
        """
        # This would typically involve TabPy or Tableau's command-line tools
        # For now, we'll provide instructions for manual template creation
        
        template_instructions = f"""
        Tableau Template Generation for {dataset_name}
        
        1. Launch Tableau Desktop
        2. Connect to the CSV file: {os.path.join(self.output_dir, f"{dataset_name}_*.csv")}
        3. Create a new {template_type}
        4. Save the workbook as {dataset_name}_{template_type}.twb in your project directory
        """
        
        # Write instructions to a file
        instructions_file = os.path.join(self.output_dir, f"{dataset_name}_tableau_instructions.txt")
        with open(instructions_file, 'w') as f:
            f.write(template_instructions)
            
        return f"Template instructions generated at {instructions_file}"
    
    def publish_to_tableau_server(self, file_path, project_name, workbook_name, 
                                 server_url, username, password, site=''):
        """
        Publish a workbook to Tableau Server
        
        Parameters:
        -----------
        file_path : str
            Path to the Tableau workbook file (.twb or .twbx)
        project_name : str
            Name of the project on Tableau Server
        workbook_name : str
            Name to give the workbook on the server
        server_url : str
            URL of the Tableau Server
        username : str
            Tableau Server username
        password : str
            Tableau Server password
        site : str, optional
            Tableau Server site name
            
        Returns:
        --------
        str : URL to the published workbook
        """
        try:
            # Set up authentication
            tableau_auth = TSC.TableauAuth(username, password, site)
            server = TSC.Server(server_url)
            
            # Sign in to server
            with server.auth.sign_in(tableau_auth):
                # Get project ID
                all_projects, pagination_item = server.projects.get()
                project_id = None
                
                for project in all_projects:
                    if project.name == project_name:
                        project_id = project.id
                        break
                
                if project_id is None:
                    raise ValueError(f"Project '{project_name}' not found on the server")
                
                # Create workbook item
                new_workbook = TSC.WorkbookItem(project_id=project_id, name=workbook_name)
                
                # Publish workbook
                published_workbook = server.workbooks.publish(
                    new_workbook, 
                    file_path, 
                    mode=TSC.Server.PublishMode.Overwrite
                )
                
                # Get the workbook URL
                workbook_url = f"{server_url}/#/site/{site}/workbooks/{published_workbook.id}"
                return f"Workbook published successfully. URL: {workbook_url}"
            
        except Exception as e:
            return f"Error publishing to Tableau Server: {str(e)}"
    
    def setup_tabpy_connection(self):
        """
        Set up TabPy connection for Tableau to use Python functions
        
        Returns:
        --------
        str : Instructions for connecting Tableau to TabPy
        """
        # Check if TabPy is installed
        try:
            import tabpy
            tabpy_installed = True
        except ImportError:
            tabpy_installed = False
        
        if not tabpy_installed:
            return "TabPy not installed. Please install with: pip install tabpy"
        
        # Instructions for running TabPy and connecting from Tableau
        instructions = """
        TabPy Connection Instructions:
        
        1. Run TabPy server:
           - Open a command prompt/terminal
           - Execute: tabpy
           
        2. In Tableau Desktop:
           - Help > Settings and Performance > Manage Analytics Extension Connection
           - Select TabPy
           - Server: localhost
           - Port: 9004
           - Click Test Connection and then OK
           
        3. For calculated fields using Python:
           - Create a calculated field
           - Use SCRIPT_* functions like:
             SCRIPT_REAL("import numpy as np; return np.mean(x)", SUM([Sales]))
        """
        
        # Save instructions to file
        instructions_file = os.path.join(self.output_dir, "tabpy_connection_instructions.txt")
        with open(instructions_file, 'w') as f:
            f.write(instructions)
            
        return f"TabPy connection instructions saved to {instructions_file}"
    
    def create_custom_tableau_functions(self):
        """
        Define custom functions to be exposed to Tableau via TabPy
        
        Returns:
        --------
        list : Names of deployed functions
        """
        try:
            from tabpy.tabpy_tools.client import Client
            
            # Connect to local TabPy server
            client = Client('http://localhost:9004/')
            
            # Define a function for sentiment analysis
            def sentiment_analysis(text):
                """Simple sentiment analysis function"""
                # This would typically use NLTK, TextBlob, or other NLP libraries
                # For demonstration, using a simple approach
                positive_words = ['good', 'great', 'excellent', 'positive', 'happy']
                negative_words = ['bad', 'poor', 'negative', 'sad', 'unhappy']
                
                text = text.lower()
                pos_count = sum(word in text for word in positive_words)
                neg_count = sum(word in text for word in negative_words)
                
                if pos_count > neg_count:
                    return 1  # Positive
                elif neg_count > pos_count:
                    return -1  # Negative
                else:
                    return 0  # Neutral
            
            # Define a function for anomaly detection
            def detect_anomalies(values, threshold=3):
                """Detect anomalies using z-score method"""
                import numpy as np
                
                mean = np.mean(values)
                std = np.std(values)
                z_scores = [(y - mean) / std for y in values]
                
                return [1 if abs(z) > threshold else 0 for z in z_scores]
            
            # Deploy functions to TabPy
            client.deploy('sentiment_analysis', sentiment_analysis, 
                         'Returns sentiment score: 1 (positive), 0 (neutral), -1 (negative)')
            
            client.deploy('detect_anomalies', detect_anomalies,
                         'Identifies anomalies in a series of values using z-score method')
            
            return ['sentiment_analysis', 'detect_anomalies']
            
        except Exception as e:
            return f"Error setting up custom functions: {str(e)}"
