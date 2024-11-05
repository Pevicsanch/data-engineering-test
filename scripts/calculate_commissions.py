import pandas as pd
import logging
import os
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_data(orders_path, invoicing_path):
    """Load orders and invoicing data from specified paths."""
    try:
        orders_df = pd.read_csv(orders_path, delimiter=';')
        logging.info(f"Loaded {len(orders_df)} orders from {orders_path}")
    except Exception as e:
        logging.error(f"Failed to load orders data: {e}")
        return None, None

    try:
        with open(invoicing_path, 'r') as f:
            invoicing_data = json.load(f)["data"]["invoices"]
        invoicing_df = pd.DataFrame(invoicing_data)
        invoicing_df['grossValue'] = pd.to_numeric(invoicing_df['grossValue'])
        invoicing_df['vat'] = pd.to_numeric(invoicing_df['vat'])
        invoicing_df['net_invoiced_value_euros'] = invoicing_df['grossValue'] * (1 - invoicing_df['vat'] / 100) / 100
        logging.info(f"Loaded {len(invoicing_df)} invoicing records from {invoicing_path}")
    except Exception as e:
        logging.error(f"Failed to load invoicing data: {e}")
        return None, None

    return orders_df, invoicing_df


def validate_data(orders_df, invoicing_df):
    """Validate that data contains required columns and is not empty."""
    if orders_df.empty or invoicing_df.empty:
        logging.warning("One or more input DataFrames are empty.")
        return False

    required_orders_cols = {'order_id', 'salesowners'}
    required_invoicing_cols = {'orderId', 'net_invoiced_value_euros'}

    if not required_orders_cols.issubset(orders_df.columns):
        logging.error("Orders data is missing required columns: 'order_id' and/or 'salesowners'")
        return False
    if not required_invoicing_cols.issubset(invoicing_df.columns):
        logging.error("Invoicing data is missing required columns: 'orderId' and/or 'net_invoiced_value_euros'")
        return False

    return True


def calculate_commissions(merged_df):
    """Calculate commissions for each sales owner from merged data."""
    # Define commission rates for each position
    commission_rates = {"main_owner": 0.06, "co_owner_1": 0.025, "co_owner_2": 0.0095}
    commission_dict = {}

    for _, row in merged_df.iterrows():
        salesowners = row.get('salesowners', [])
        net_value = row.get('net_invoiced_value_euros', 0)

        # Skip rows where net_invoiced_value_euros is NaN or zero
        if pd.notna(net_value) and net_value > 0:
            if len(salesowners) > 0:  # Main Owner
                main_owner = salesowners[0]
                commission = net_value * commission_rates["main_owner"]
                commission_dict[main_owner] = commission_dict.get(main_owner, 0) + commission

            if len(salesowners) > 1:  # Co-owner 1
                co_owner_1 = salesowners[1]
                commission = net_value * commission_rates["co_owner_1"]
                commission_dict[co_owner_1] = commission_dict.get(co_owner_1, 0) + commission

            if len(salesowners) > 2:  # Co-owner 2
                co_owner_2 = salesowners[2]
                commission = net_value * commission_rates["co_owner_2"]
                commission_dict[co_owner_2] = commission_dict.get(co_owner_2, 0) + commission

    # Convert the commission dictionary into a DataFrame
    commission_df = pd.DataFrame(list(commission_dict.items()), columns=['sales_owner', 'total_commission'])
    commission_df['total_commission'] = commission_df['total_commission'].round(2)
    
    return commission_df.sort_values(by='total_commission', ascending=False).reset_index(drop=True)


def save_commissions(commission_df, output_path):
    """Save the commission DataFrame to the specified path."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    commission_df.to_csv(output_path, index=False)
    logging.info(f"Commission file saved at {output_path}")


def main(orders_path, invoicing_path, output_path):
    """Main function to calculate and save commissions."""
    orders_df, invoicing_df = load_data(orders_path, invoicing_path)
    if orders_df is None or invoicing_df is None:
        logging.error("Data loading failed. Exiting program.")
        return

    if not validate_data(orders_df, invoicing_df):
        logging.error("Data validation failed. Exiting program.")
        return

    # Merge data on order IDs
    merged_df = orders_df.merge(
        invoicing_df[['orderId', 'net_invoiced_value_euros']],
        left_on='order_id',
        right_on='orderId',
        how='left'
    )
    merged_df['salesowners'] = merged_df['salesowners'].apply(lambda x: x.split(', ') if isinstance(x, str) else [])

    commission_df = calculate_commissions(merged_df)
    logging.info("\nSales Owner Commissions:")
    print(commission_df)

    save_commissions(commission_df, output_path)
    logging.info("Commission calculation completed successfully.")


# Run the main function
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    orders_path = os.path.join(script_dir, '..', 'data', 'orders.csv')
    invoicing_path = os.path.join(script_dir, '..', 'data', 'invoicing_data.json')
    output_path = os.path.join(script_dir, '..', 'output', 'sales_owner_commissions.csv')
    
    main(orders_path, invoicing_path, output_path)