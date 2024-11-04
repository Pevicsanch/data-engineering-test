import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pandas as pd
from scripts.calculate_contact_fullname import load_orders, create_contact_fullname_df, save_contact_fullname_df


# Sample test data
test_data = {
    'order_id': ['1', '2', '3', '4'],
    'contact_data': [
        '[{ "contact_name":"Alice", "contact_surname":"Smith"}]',
        '[{ "contact_name":"Bob", "contact_surname":""}]',  # Missing last name
        '[{ "contact_name":"", "contact_surname":"Jones"}]',  # Missing first name
        '[{ "contact_surname":"Williams", "city":"New York"}]'  # Missing first name
    ]
}
df_test = pd.DataFrame(test_data)

def test_create_contact_fullname_df():
    """Test full name creation and placeholder for missing names."""
    result_df = create_contact_fullname_df(df_test)

    # Check structure
    assert 'order_id' in result_df.columns
    assert 'contact_full_name' in result_df.columns

    # Check name generation with placeholders
    assert result_df.loc[result_df['order_id'] == '1', 'contact_full_name'].values[0] == "Alice Smith"
    assert result_df.loc[result_df['order_id'] == '2', 'contact_full_name'].values[0] == "John Doe"
    assert result_df.loc[result_df['order_id'] == '3', 'contact_full_name'].values[0] == "John Doe"
    assert result_df.loc[result_df['order_id'] == '4', 'contact_full_name'].values[0] == "John Doe"

def test_save_contact_fullname_df(tmp_path):
    """Test saving the contact full name DataFrame to a CSV file."""
    output_file = tmp_path / "contact_fullname_test.csv"
    result_df = create_contact_fullname_df(df_test)
    save_contact_fullname_df(result_df, output_file)

    # Verify file creation
    assert os.path.exists(output_file)

    # Load and validate saved content with specific dtype for `order_id`
    saved_df = pd.read_csv(output_file, dtype={'order_id': str})
    pd.testing.assert_frame_equal(result_df.reset_index(drop=True), saved_df)