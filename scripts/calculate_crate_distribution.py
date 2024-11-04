import pandas as pd
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_data(file_path, delimiter=';'):
    """Loads data from a CSV file with a specified delimiter."""
    return pd.read_csv(file_path, delimiter=delimiter)

def validate_data(df):
    """Validates and cleans data by handling missing values, enforcing data types, and filtering invalid crate types."""
    # Handle missing values in 'company_id' and 'crate_type'
    df = df.dropna(subset=['company_id', 'crate_type'])
    
    # Convert 'company_id' and 'crate_type' to string if not already
    df['company_id'] = df['company_id'].astype(str)
    df['crate_type'] = df['crate_type'].astype(str)
    
    # Define valid crate types and filter invalid ones
    valid_crate_types = {"Plastic", "Wood", "Metal"}
    invalid_crates = df[~df['crate_type'].isin(valid_crate_types)]
    if not invalid_crates.empty:
        logging.warning("Invalid crate types found. Excluding these from analysis.")
        df = df[df['crate_type'].isin(valid_crate_types)]
    
    # Check for duplicate 'order_id' entries
    if df['order_id'].duplicated().any():
        logging.warning("Duplicate 'order_id' entries detected. Verify for potential duplicate orders.")
    
    return df

def calculate_distribution(df):
    """Calculates crate type distribution per company."""
    return df.groupby(['company_id', 'crate_type']).size().reset_index(name='order_count')

def save_distribution(distribution_df, output_file):
    """Saves the distribution DataFrame to a CSV file."""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    distribution_df.to_csv(output_file, index=False)
    logging.info(f"Distribution saved to {output_file}")

def main(input_file, output_file='output/crate_distribution.csv'):
    # Load and validate data
    orders = load_data(input_file)
    orders = validate_data(orders)

    # Calculate distribution
    distribution = calculate_distribution(orders)

    # Save and optionally print distribution
    save_distribution(distribution, output_file)
    print(distribution.head())  # Optional: for quick verification

# Run the main function if executed as a script
if __name__ == "__main__":
    main(input_file='../data/orders.csv')