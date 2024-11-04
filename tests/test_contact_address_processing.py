import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
from scripts.contact_address_processing import get_contact_address, fix_contact_data_format, create_contact_address_df

def test_fix_contact_data_format():
    # Test normal formatting
    assert fix_contact_data_format('{"city":"Chicago", "cp": "12345"}') == '[{"city":"Chicago", "cp": "12345"}]'

    # Test missing fields with defaults
    assert fix_contact_data_format(None) == '[{"city": "Unknown", "cp": "UNK00"}]'

    # Test malformed JSON
    assert fix_contact_data_format('{ city: "Chicago"') == '[{"city": "Unknown", "cp": "UNK00"}]'

def test_get_contact_address():
    # Valid contact data
    assert get_contact_address('[{"city":"Chicago", "cp": "12345"}]') == "Chicago, 12345"

    # Missing postal code
    assert get_contact_address('[{"city":"New York"}]') == "New York, UNK00"

    # No city or postal code
    assert get_contact_address('') == "Unknown, UNK00"

def test_create_contact_address_df():
    # Mock a sample DataFrame
    data = {
        "order_id": [1, 2],
        "contact_data": ['[{"city":"Chicago", "cp": "12345"}]', None]
    }
    df = pd.DataFrame(data)
    result_df = create_contact_address_df(df)

    # Check if contact_address column was created correctly
    assert result_df.loc[0, "contact_address"] == "Chicago, 12345"
    assert result_df.loc[1, "contact_address"] == "Unknown, UNK00"