import sys
import os

# Agrega el directorio raíz del proyecto al PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from scripts.data_downloader import download_file
import os

def test_download_file():
    # Test URL and output path
    test_url = 'https://raw.githubusercontent.com/Digital-IFCO/data-engineering-test/main/resources/orders.csv'
    test_output = '../data/test_orders.csv'

    # Run the download function
    download_file(test_url, test_output)

    # Check if the file was downloaded successfully
    assert os.path.exists(test_output), "File was not downloaded successfully."

    # Clean up
    os.remove(test_output)  # Delete the test file after verification