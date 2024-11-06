import pandas as pd
import json
from datetime import timedelta
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_orders_data(filepath):
    """Loads and processes orders data from a CSV file."""
    try:
        orders_df = pd.read_csv(filepath, delimiter=';')
        orders_df['date'] = pd.to_datetime(orders_df['date'], format='%d.%m.%y', errors='coerce')
        if orders_df['date'].isnull().any():
            raise ValueError("Some dates could not be parsed.")
        logging.info("Orders data loaded successfully.")
        return orders_df
    except Exception as e:
        logging.error(f"Error loading orders data: {e}")
        raise

def load_invoices_data(filepath):
    """Loads and processes invoicing data from a JSON file."""
    try:
        with open(filepath, 'r') as f:
            invoicing_data = json.load(f).get("data", {}).get("invoices", [])
            if not invoicing_data:
                raise ValueError("No invoices data found.")
        invoices_df = pd.json_normalize(invoicing_data)
        invoices_df['grossValue'] = pd.to_numeric(invoices_df['grossValue'], errors='coerce').fillna(0)
        invoices_df['vat'] = pd.to_numeric(invoices_df['vat'], errors='coerce').fillna(0)
        logging.info("Invoicing data loaded successfully.")
        return invoices_df
    except Exception as e:
        logging.error(f"Error loading invoicing data: {e}")
        raise

def prepare_data(orders_df, invoices_df):
    """Prepares the merged dataset of orders and invoices."""
    try:
        merged_df = orders_df.merge(invoices_df[['orderId', 'grossValue', 'vat']], left_on='order_id', right_on='orderId', how='left')
        merged_df['grossValue'] = merged_df['grossValue'].fillna(0)
        merged_df['vat'] = merged_df['vat'].fillna(0)
        merged_df['salesowners'] = merged_df['salesowners'].fillna("Unknown")
        plastic_orders_df = merged_df[merged_df['crate_type'] == 'Plastic'].dropna(subset=['orderId']).copy()
        logging.info("Data prepared and filtered for plastic orders.")
        return plastic_orders_df
    except KeyError as e:
        logging.error(f"Missing expected column: {e}")
        raise
    except Exception as e:
        logging.error(f"Error preparing data: {e}")
        raise

def expand_salesowners(plastic_orders_df):
    """Expands salesowner data for each order."""
    try:
        plastic_orders_df['salesowners'] = plastic_orders_df['salesowners'].str.split(', ')
        expanded_orders_df = plastic_orders_df.explode('salesowners').copy()
        expanded_orders_df['salesowner_count'] = expanded_orders_df.groupby('order_id')['salesowners'].transform('count')
        expanded_orders_df['gross_per_salesowner'] = (expanded_orders_df['grossValue'] / expanded_orders_df['salesowner_count']).round(2)
        expanded_orders_df['year_month'] = expanded_orders_df['date'].dt.to_period('M').astype(str)
        logging.info("Salesowners data expanded.")
        return expanded_orders_df
    except Exception as e:
        logging.error(f"Error expanding salesowners data: {e}")
        raise

def calculate_top_performers(expanded_orders_df):
    """Calculates the top 5 salesowners based on a rolling 3-month window."""
    try:
        monthly_sales_performance = (
            expanded_orders_df.groupby(['salesowners', 'year_month'])['gross_per_salesowner']
            .sum()
            .reset_index()
        )
        monthly_sales_performance['year_month'] = pd.to_datetime(monthly_sales_performance['year_month'], format='%Y-%m')
        monthly_sales_performance = monthly_sales_performance.sort_values(by=['salesowners', 'year_month'])
        
        monthly_sales_performance['gross_rolling_3m'] = (
            monthly_sales_performance.groupby('salesowners')['gross_per_salesowner']
            .rolling(window=3, min_periods=1)
            .sum()
            .reset_index(drop=True)
        )
        
        monthly_sales_performance['year_month'] = monthly_sales_performance['year_month'].dt.to_period('M').astype(str)
        top_5_performers_3m = (
            monthly_sales_performance.sort_values(by=['year_month', 'gross_rolling_3m'], ascending=[True, False])
            .groupby('year_month')
            .head(5)
        )
        top_5_performers_3m['rank'] = top_5_performers_3m.groupby('year_month')['gross_rolling_3m'].rank(ascending=False, method='first')
        logging.info("Top 5 performers calculated for each 3-month rolling window.")
        return top_5_performers_3m.reset_index(drop=True)
    except Exception as e:
        logging.error(f"Error calculating top performers: {e}")
        raise

def main():
    """Main function to execute the script."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        orders_filepath = os.path.join(script_dir, '..', 'data', 'orders.csv')
        invoices_filepath = os.path.join(script_dir, '..', 'data', 'invoicing_data.json')
        output_filepath = os.path.join(script_dir, '..', 'output', 'top_5_performers.csv')

        orders_df = load_orders_data(orders_filepath)
        invoices_df = load_invoices_data(invoices_filepath)
        plastic_orders_df = prepare_data(orders_df, invoices_df)
        expanded_orders_df = expand_salesowners(plastic_orders_df)
        top_5_performers = calculate_top_performers(expanded_orders_df)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
        # Save results to CSV
        top_5_performers.to_csv(output_filepath, index=False)
        logging.info(f"Top 5 performers saved to {output_filepath}")
    except Exception as e:
        logging.error(f"An error occurred during script execution: {e}")

if __name__ == "__main__":
    main()