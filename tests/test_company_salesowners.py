import sys
import os
import pytest
import pandas as pd
import logging

# Configure logging in the test
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Check the paths (for debugging purposes)
#print("Current PYTHONPATH:")
#print(sys.path)

try:
    from scripts.company_salesowners import create_df3, normalize_company_name
except ImportError:
    raise ImportError("Ensure that 'company_salesowners.py' is in the 'scripts' directory and the path is correctly added to sys.path.")

# Test output file path
output_path = os.path.join('..', 'output', 'df3_test.csv')

# Test data to simulate `orders.csv`
test_data = pd.DataFrame({
    'company_id': ['1', '2', '1', '3'],
    'company_name': ['Fresh Fruits Co', 'Veggies Inc', 'Fresh Fruits Ltd', 'Healthy Snacks Ltd'],
    'salesowners': ['Alice Smith, Bob Brown', 'Charlie Green', 'Alice Smith', 'Dave White']
})

@pytest.fixture(scope="module")
def setup_output_file():
    # Clean up the output file before tests
    if os.path.exists(output_path):
        os.remove(output_path)
    yield
    # Clean up the output file after tests
    if os.path.exists(output_path):
        os.remove(output_path)

def test_normalize_company_name():
    # Test normalization with various cases
    assert normalize_company_name("Fresh Fruits Ltd.") == "fresh fruit"
    assert normalize_company_name("Veggies Inc.") == "veggie"
    assert normalize_company_name("Healthy Snacks Co.") == "healthy snack"

def test_create_df3_structure(setup_output_file):
    # Test creation of df3 and correct structure
    df3 = create_df3(test_data, output_path)
    
    # Check expected columns
    expected_columns = ['company_id', 'company_name', 'list_salesowners']
    assert all(col in df3.columns for col in expected_columns)
    
    # Check if salesowners are sorted and unique
    sorted_salesowners = df3[df3['company_name'] == 'fresh fruit']['list_salesowners'].values[0]
    assert sorted_salesowners == 'Alice Smith, Bob Brown', f"Expected sorted list, got {sorted_salesowners}"

def test_output_file_creation(setup_output_file):
    # Run the function and verify if the output file has been created
    create_df3(test_data, output_path)
    assert os.path.exists(output_path)

def test_duplicate_handling():
    # Test duplicate handling with a more complex case
    test_data_dup = pd.DataFrame({
        'company_id': ['1', '2', '3', '4', '1'],
        'company_name': ['Tropical Fruits Co', 'Tropical Fruits Ltd', 'Tropical Fruits', 'Fresh Fruits', 'Tropical Fruits Co'],
        'salesowners': ['Alice Smith', 'Bob Brown', 'Alice Smith, Dave White', 'Charlie Green', 'Bob Brown']
    })
    df3 = create_df3(test_data_dup, output_path)
    assert len(df3['company_id'].unique()) < len(test_data_dup['company_id'].unique()), \
        "Duplicate company IDs should be handled and grouped."