import pandas as pd
import json
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define commission rates
COMMISSION_RATES = {
    "main_owner": 0.06,
    "co_owner_1": 0.025,
    "co_owner_2": 0.0095
}

def load_invoicing_data(filepath):
    """Load and process the invoicing JSON file."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)["data"]["invoices"]
        invoicing_df = pd.DataFrame(data)
        invoicing_df['grossValue'] = pd.to_numeric(invoicing_df['grossValue'])
        invoicing_df['vat'] = pd.to_numeric(invoicing_df['vat'])
        invoicing_df['net_invoiced_value_euros'] = invoicing_df['grossValue'] * (1 - invoicing_df['vat'] / 100) / 100
        logging.info(f"Loaded {len(invoicing_df)} invoicing records from {filepath}")
        return invoicing_df
    except FileNotFoundError:
        logging.error(f"File not found: {filepath}")
        return pd.DataFrame()
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON format in file: {filepath}")
        return pd.DataFrame()

def load_orders_data(filepath, delimiter=';'):
    """Load and process the orders CSV file."""
    try:
        orders_df = pd.read_csv(filepath, delimiter=delimiter)
        orders_df['salesowners'] = orders_df['salesowners'].apply(lambda x: x.split(', ') if isinstance(x, str) else [])
        logging.info(f"Loaded {len(orders_df)} order records from {filepath}")
        return orders_df
    except FileNotFoundError:
        logging.error(f"File not found: {filepath}")
        return pd.DataFrame()
    except pd.errors.ParserError:
        logging.error(f"Error reading CSV file: {filepath}")
        return pd.DataFrame()

def calculate_commissions(orders_df, invoicing_df):
    """Calculate commissions per sales owner and return a DataFrame with the results."""
    # Merge orders and invoicing data by order ID
    merged_df = orders_df.merge(
        invoicing_df[['orderId', 'net_invoiced_value_euros']],
        left_on='order_id',
        right_on='orderId',
        how='left'
    )
    
    # Dictionary to accumulate commissions by sales owner
    commission_dict = {}
    
    for _, row in merged_df.iterrows():
        salesowners = row['salesowners']
        net_value = row['net_invoiced_value_euros']
        
        if pd.notna(net_value):
            # Calculate commissions for the main owner and co-owners
            if len(salesowners) > 0:
                main_owner = salesowners[0]
                commission_dict[main_owner] = commission_dict.get(main_owner, 0) + net_value * COMMISSION_RATES["main_owner"]
            if len(salesowners) > 1:
                co_owner_1 = salesowners[1]
                commission_dict[co_owner_1] = commission_dict.get(co_owner_1, 0) + net_value * COMMISSION_RATES["co_owner_1"]
            if len(salesowners) > 2:
                co_owner_2 = salesowners[2]
                commission_dict[co_owner_2] = commission_dict.get(co_owner_2, 0) + net_value * COMMISSION_RATES["co_owner_2"]

    # Convert commission dictionary to DataFrame and sort
    commission_df = pd.DataFrame(list(commission_dict.items()), columns=['sales_owner', 'total_commission'])
    commission_df = commission_df.sort_values(by='total_commission', ascending=False).reset_index(drop=True)
    commission_df['total_commission'] = commission_df['total_commission'].round(2)
    return commission_df

def save_commissions(commission_df, output_path):
    """Save the commission DataFrame to a CSV file."""
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    commission_df.to_csv(output_path, index=False)
    logging.info(f"Commission file saved at {output_path}")

if __name__ == "__main__":
    # Define file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    invoicing_path = os.path.join(script_dir, '../data/invoicing_data.json')
    orders_path = os.path.join(script_dir, '../data/orders.csv')
    output_path = os.path.join(script_dir, '../output/sales_owner_commissions.csv')

    # Load data
    invoicing_df = load_invoicing_data(invoicing_path)
    orders_df = load_orders_data(orders_path)

    # Validate that both DataFrames are not empty before calculating commissions
    if not invoicing_df.empty and not orders_df.empty:
        # Calculate commissions and save the result
        commission_df = calculate_commissions(orders_df, invoicing_df)
        save_commissions(commission_df, output_path)
        logging.info("Commission calculation completed successfully.")
    else:
        logging.error("Calculation could not be completed due to missing or incorrect data.")