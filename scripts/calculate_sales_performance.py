import pandas as pd
from datetime import timedelta
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_data(file_path, file_type='csv', delimiter=';'):
    """Loads and validates data from CSV or JSON files."""
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")
        
        if file_type == 'csv':
            logging.info(f"Loading data from {file_path}")
            return pd.read_csv(file_path, delimiter=delimiter)
        elif file_type == 'json':
            logging.info(f"Loading JSON data from {file_path}")
            with open(file_path, 'r') as f:
                return json.load(f)["data"]["invoices"]
        else:
            raise ValueError("Unsupported file type. Choose 'csv' or 'json'.")
    except Exception as e:
        logging.error(f"Error loading data from {file_path}: {e}")
        raise

def validate_and_prepare_data(orders_df, invoices_df):
    """Validates and prepares orders and invoices data for merging."""
    logging.info("Validating and preparing data...")

    try:
        # Check and parse date column
        if 'date' not in orders_df.columns:
            raise KeyError("Column 'date' not found in orders data.")
        orders_df['date'] = pd.to_datetime(orders_df['date'], format='%d.%m.%y', errors='coerce')

        # Convert 'grossValue' and 'vat' columns to numeric types
        for col in ['grossValue', 'vat']:
            if col in invoices_df.columns:
                invoices_df[col] = pd.to_numeric(invoices_df[col], errors='coerce').fillna(0)
            else:
                raise KeyError(f"Column '{col}' not found in invoices data.")
        
        # Check for null dates after conversion
        if orders_df['date'].isnull().any():
            logging.warning("Some dates could not be parsed in 'orders.csv' file.")

        return orders_df, invoices_df
    except Exception as e:
        logging.error(f"Error validating data: {e}")
        raise

def merge_and_clean_data(orders_df, invoices_df):
    """Merges orders and invoices data, handles missing values, and removes duplicates."""
    logging.info("Merging and cleaning data...")
    try:
        merged_df = orders_df.merge(
            invoices_df[['orderId', 'grossValue', 'vat']], 
            left_on='order_id', right_on='orderId', how='left'
        )
        
        # Handle missing values in merged_df
        merged_df['grossValue'] = merged_df['grossValue'].fillna(0)
        merged_df['vat'] = merged_df['vat'].fillna(0)
        merged_df['salesowners'] = merged_df['salesowners'].fillna("Unknown")
        
        # Remove rows with missing orderId and duplicates
        merged_df = merged_df[merged_df['orderId'].notna()]
        merged_df_unique = merged_df.drop_duplicates(subset='order_id', keep='first')
        
        logging.info("Data merged and cleaned successfully.")
        return merged_df_unique
    except Exception as e:
        logging.error(f"Error merging and cleaning data: {e}")
        raise

def filter_plastic_orders(merged_df):
    """Filters the merged data for plastic crate orders from the last 12 months."""
    logging.info("Filtering for plastic orders in the last 12 months...")
    try:
        latest_date = merged_df['date'].max()
        one_year_ago = latest_date - timedelta(days=365)
        last_12_months_df = merged_df[merged_df['date'] >= one_year_ago]
        plastic_orders_df = last_12_months_df[last_12_months_df['crate_type'] == 'Plastic'].copy()
        
        logging.info(f"Filtered {plastic_orders_df.shape[0]} plastic orders from the last 12 months.")
        return plastic_orders_df
    except Exception as e:
        logging.error(f"Error filtering plastic orders: {e}")
        raise

def calculate_sales_performance(plastic_orders_df):
    """Calculates gross sales per salesowner and identifies those needing improvement."""
    logging.info("Calculating sales performance for plastic crates...")
    try:
        # Split salesowners and expand rows
        plastic_orders_df['salesowners'] = plastic_orders_df['salesowners'].str.split(', ')
        expanded_orders_df = plastic_orders_df.explode('salesowners')
        
        # Calculate gross value per salesowner
        expanded_orders_df['salesowner_count'] = expanded_orders_df.groupby('order_id')['salesowners'].transform('count')
        expanded_orders_df['gross_per_salesowner'] = (expanded_orders_df['grossValue'] / expanded_orders_df['salesowner_count']).round(2)
        
        # Aggregate sales performance
        sales_performance = expanded_orders_df.groupby('salesowners')['gross_per_salesowner'].sum().reset_index()
        sales_performance = sales_performance.sort_values(by='gross_per_salesowner')
        
        logging.info("Sales performance calculated successfully.")
        return sales_performance
    except Exception as e:
        logging.error(f"Error calculating sales performance: {e}")
        raise

def save_sales_performance(sales_performance, output_path):
    """Saves the calculated sales performance to a CSV file."""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        sales_performance.to_csv(output_path, index=False)
        logging.info(f"Sales performance saved to {output_path}")
    except Exception as e:
        logging.error(f"Error saving sales performance: {e}")
        raise

# Main script execution
if __name__ == "__main__":
    try:
        # Define file paths
        script_dir = os.path.dirname(os.path.abspath(__file__))
        orders_filepath = os.path.join(script_dir, '..', 'data', 'orders.csv')
        invoices_filepath = os.path.join(script_dir, '..', 'data', 'invoicing_data.json')
        output_filepath = os.path.join(script_dir, '..', 'output', 'sales_performance.csv')

        # Load data
        orders_df = load_data(orders_filepath, 'csv')
        invoicing_data = load_data(invoices_filepath, 'json')
        invoices_df = pd.json_normalize(invoicing_data)

        # Validate and prepare data
        orders_df, invoices_df = validate_and_prepare_data(orders_df, invoices_df)

        # Merge and clean data
        merged_df = merge_and_clean_data(orders_df, invoices_df)

        # Filter for plastic orders in the last 12 months
        plastic_orders_df = filter_plastic_orders(merged_df)

        # Calculate sales performance and save to CSV
        sales_performance = calculate_sales_performance(plastic_orders_df)
        save_sales_performance(sales_performance, output_filepath)

        logging.info("Sales performance calculation completed successfully.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")