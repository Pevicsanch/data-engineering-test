import sys
import os

# Add the project root to PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pandas as pd
from scripts.calculate_crate_distribution import load_data, validate_data, calculate_distribution, save_distribution

# Mock data for testing
data = {
    'order_id': ['1', '2', '3', '4', '5'],
    'company_id': ['c1', 'c1', 'c2', 'c3', None],
    'crate_type': ['Plastic', 'Wood', 'Metal', 'InvalidType', 'Plastic']
}
df = pd.DataFrame(data)

def test_load_data():
    """Test if the load_data function loads data correctly."""
    # Placeholder test for load_data
    pass

def test_validate_data():
    """Test validate_data to ensure it handles missing values and invalid crate types."""
    validated_df = validate_data(df)
    
    # Check that the row with None in 'company_id' and the invalid crate type are removed
    assert validated_df.shape[0] == 3
    
    # Check that invalid crate types are removed
    assert 'InvalidType' not in validated_df['crate_type'].values
    
    # Check that company_id and crate_type are strings
    assert validated_df['company_id'].dtype == 'object'
    assert validated_df['crate_type'].dtype == 'object'

def test_calculate_distribution():
    """Test calculate_distribution to ensure the distribution calculation is correct."""
    validated_df = validate_data(df)
    distribution = calculate_distribution(validated_df)
    
    # Check distribution DataFrame structure
    assert set(distribution.columns) == {'company_id', 'crate_type', 'order_count'}
    
    # Check sample data: c1 should have 1 Plastic and 1 Wood
    c1_plastic = distribution[(distribution['company_id'] == 'c1') & (distribution['crate_type'] == 'Plastic')]
    assert c1_plastic['order_count'].iloc[0] == 1
    
    c1_wood = distribution[(distribution['company_id'] == 'c1') & (distribution['crate_type'] == 'Wood')]
    assert c1_wood['order_count'].iloc[0] == 1

def test_save_distribution(tmp_path):
    """Test save_distribution to ensure the output file is created correctly."""
    validated_df = validate_data(df)
    distribution = calculate_distribution(validated_df)
    
    # Use a temporary path for saving
    output_file = tmp_path / "test_distribution.csv"
    save_distribution(distribution, output_file)
    
    # Check if the file is created
    assert os.path.exists(output_file)
    
    # Load and verify the content
    saved_df = pd.read_csv(output_file)
    assert saved_df.equals(distribution)