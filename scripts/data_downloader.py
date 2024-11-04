import requests
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def download_file(url, local_filename):
    """Downloads a file from a URL and saves it to a specified location.
    
    Args:
        url (str): The URL of the file to download.
        local_filename (str): The local path to save the downloaded file.
    
    Raises:
        Exception: If the download fails due to a connection error or invalid URL.
    """
    try:
        logging.info(f"Attempting to download {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raises HTTPError for bad responses
        os.makedirs(os.path.dirname(local_filename), exist_ok=True)  # Ensure directory exists

        with open(local_filename, 'wb') as file:
            file.write(response.content)
        
        logging.info(f"Downloaded {local_filename} successfully.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to download {local_filename}. Error: {e}")
        raise  # Re-raise the exception after logging

# URLs for the files (raw URLs from GitHub)
url_orders = 'https://raw.githubusercontent.com/Digital-IFCO/data-engineering-test/main/resources/orders.csv'
url_invoicing = 'https://raw.githubusercontent.com/Digital-IFCO/data-engineering-test/main/resources/invoicing_data.json'

# Define absolute paths for the files
data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
orders_path = os.path.join(data_dir, 'orders.csv')
invoicing_path = os.path.join(data_dir, 'invoicing_data.json')

# Download the files
download_file(url_orders, orders_path)
download_file(url_invoicing, invoicing_path)