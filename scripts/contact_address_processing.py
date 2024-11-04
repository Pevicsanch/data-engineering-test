import pandas as pd
import json
import os
import logging
import re

# Set logging level to INFO to reduce verbosity
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_orders(file_path, delimiter=';'):
    """Loads order data from a CSV file."""
    try:
        df = pd.read_csv(file_path, delimiter=delimiter)
        logging.info(f"Loaded {len(df)} rows from {file_path}")
        return df
    except FileNotFoundError:
        logging.error(f"Error: File {file_path} not found.")
        return pd.DataFrame()

def fix_contact_data_format(contact_data):
    """Attempts to fix common formatting issues in contact_data strings."""
    if pd.isna(contact_data) or not isinstance(contact_data, str):
        return '[{"city": "Unknown", "cp": "UNK00"}]'
    
    # Normalization
    contact_data = re.sub(r'([{,])\s*([a-zA-Z_]+)\s*:', r'\1 "\2":', contact_data)
    contact_data = contact_data.replace("'", '"').strip()
    
    # Ensure JSON list format
    if not contact_data.startswith('['):
        contact_data = f"[{contact_data}"
    if not contact_data.endswith(']'):
        contact_data += ']'
    
    try:
        json.loads(contact_data)
    except json.JSONDecodeError:
        contact_data = '[{"city": "Unknown", "cp": "UNK00"}]'
    
    return contact_data

def get_contact_address(contact_data):
    """Extracts city and postal code or returns defaults if missing."""
    contact_data = fix_contact_data_format(contact_data)
    try:
        contact_info = json.loads(contact_data)[0]
        city = contact_info.get("city", "Unknown").strip() if isinstance(contact_info.get("city"), str) else "Unknown"
        postal_code = contact_info.get("cp", "UNK00").strip() if isinstance(contact_info.get("cp"), str) else "UNK00"
        return f"{city}, {postal_code}"
    except (json.JSONDecodeError, IndexError, TypeError, KeyError):
        return "Unknown, UNK00"

def create_contact_address_df(df):
    """Creates a DataFrame with order_id and contact_address."""
    if df.empty:
        logging.warning("The DataFrame is empty. No contact names to process.")
        return pd.DataFrame(columns=['order_id', 'contact_address'])
    
    df['contact_address'] = df['contact_data'].apply(get_contact_address)
    logging.info("contact_address column created successfully.")
    return df[['order_id', 'contact_address']]

def save_contact_address_df(df, output_path):
    """Saves the contact address DataFrame to a CSV file."""
    if df.empty:
        logging.warning("The DataFrame is empty. Nothing to save.")
        return
    absolute_path = os.path.abspath(output_path)
    logging.info(f"Saving DataFrame to {absolute_path}")
    output_dir = os.path.dirname(absolute_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    df.to_csv(absolute_path, index=False)
    logging.info(f"DataFrame saved successfully at {absolute_path}")

if __name__ == "__main__":
    # Get the absolute path of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, '..', 'data', 'orders.csv')
    output_path = os.path.join(script_dir, '..', 'output', 'contact_address.csv')

    logging.info(f"Current working directory: {os.getcwd()}")
    logging.info(f"Input path: {input_path}")
    logging.info(f"Output path: {output_path}")

    orders_df = load_orders(input_path)
    if not orders_df.empty:
        contact_address_df = create_contact_address_df(orders_df)
        save_contact_address_df(contact_address_df, output_path)
    else:
        logging.error("No data loaded. Exiting.")