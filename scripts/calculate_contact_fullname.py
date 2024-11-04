import pandas as pd
import json
import os
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_orders(file_path, delimiter=';'):
    """Loads order data from a CSV file."""
    try:
        df = pd.read_csv(file_path, delimiter=delimiter)
        logging.info(f"Loaded {len(df)} rows from {file_path}")
        return df
    except FileNotFoundError:
        logging.error(f"Error: The file {file_path} was not found.")
        return pd.DataFrame()

def fix_contact_data_format(contact_data):
    """Attempts to fix known format issues in contact_data strings."""
    if pd.isna(contact_data):
        return None
    # Ensure JSON-compatible format
    contact_data = re.sub(r'([{,])\s*([a-zA-Z_]+)\s*:', r'\1 "\2":', contact_data)
    contact_data = contact_data.replace("'", '"')  # Convert single quotes to double quotes

    # Handle specific issues like missing brackets
    if not contact_data.startswith('['):
        contact_data = f"[{contact_data}]"
    contact_data = re.sub(r'}\s*{', '},{', contact_data)
    
    # Ensure closing bracket if missing
    if contact_data[-1] != "]":
        contact_data += "]"
    
    logging.info(f"Formatted contact_data: {contact_data}")
    return contact_data

def get_full_name(contact_data):
    """Extracts full name from contact data or returns 'John Doe' if incomplete."""
    contact_data = fix_contact_data_format(contact_data)
    if contact_data is None:
        return "John Doe"
    try:
        contact_info = json.loads(contact_data)[0]
        first_name = contact_info.get("contact_name", "").strip()
        last_name = contact_info.get("contact_surname", "").strip()
        if not first_name or not last_name:
            return "John Doe"
        return f"{first_name} {last_name}"
    except (json.JSONDecodeError, IndexError, TypeError, KeyError) as e:
        logging.warning(f"Unexpected structure in contact data: {contact_data}. Error: {e}. Using 'John Doe'.")
        return "John Doe"

def create_contact_fullname_df(df):
    """Creates a DataFrame with order_id and contact_full_name."""
    if df.empty:
        logging.warning("The DataFrame is empty. No contact full names to process.")
        return pd.DataFrame(columns=['order_id', 'contact_full_name'])
    df['contact_full_name'] = df['contact_data'].apply(get_full_name)
    logging.info("Successfully created contact_full_name column.")
    return df[['order_id', 'contact_full_name']]

def save_contact_fullname_df(df, output_path):
    """Saves the contact full name DataFrame to a CSV file."""
    if df.empty:
        logging.warning("The DataFrame is empty. Nothing to save.")
        return
    absolute_path = os.path.abspath(output_path)
    logging.info(f"Saving DataFrame to {absolute_path}")
    output_dir = os.path.dirname(absolute_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    df.to_csv(absolute_path, index=False)
    logging.info(f"DataFrame successfully saved to {absolute_path}")
    if os.path.exists(absolute_path):
        logging.info(f"File {absolute_path} was created successfully.")
    else:
        logging.error(f"File {absolute_path} was not created.")

if __name__ == "__main__":
    # Get the absolute path of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct absolute paths
    input_path = os.path.join(script_dir, '..', 'data', 'orders.csv')
    output_path = os.path.join(script_dir, '..', 'output', 'contact_fullname.csv')
    
    logging.info(f"Current working directory: {os.getcwd()}")
    logging.info(f"Input path: {input_path}")
    logging.info(f"Output path: {output_path}")
    
    # Load and process data
    orders_df = load_orders(input_path)
    if not orders_df.empty:
        contact_fullname_df = create_contact_fullname_df(orders_df)
        save_contact_fullname_df(contact_fullname_df, output_path)
    else:
        logging.error("No data loaded. Exiting.")