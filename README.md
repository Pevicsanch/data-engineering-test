# Data Engineering Test Solution

This project contains solutions for a Data Engineering test, focusing on various data processing tasks using Python. Each task involves data cleaning, validation, analysis, and output generation. The solutions are modular and documented to facilitate readability and maintainability.

## Project Structure

The project is organized into the following directories:

- `data/`: Contains input data files (`orders.csv`, `invoicing_data.json`).
- `output/`: Stores the processed output files.
- `scripts/`: Includes Python scripts for data processing.
- `notebooks/`: Contains Jupyter Notebooks for exploratory analysis and testing.
- `tests/`: Holds unit tests for the scripts.

Here is the directory tree for better visualization:

```
/data-engineering-test
├── data/
│   ├── orders.csv
│   └── invoicing_data.json
├── output/
├── scripts/
│   ├── data_downloader.py
│   ├── calculate_crate_distribution.py
│   ├── calculate_contact_fullname.py
│   ├── contact_address_processing.py
│   └── calculate_commissions.py
├── notebooks/
│   ├── exercise_1.ipynb
├── tests/
│   ├── test_data_downloader.py
│   ├── test_calculate_crate_distribution.py
│   ├── test_calculate_contact_fullname.py
│   ├── test_contact_address_processing.py
│   └── test_calculate_commissions.py
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.11.5
- Required libraries are listed in `requirements.txt`.

To install the necessary libraries, run:

```bash
pip install -r requirements.txt
```

## Data Download

To start, you need to download the data files (orders.csv and invoicing_data.json) into the data/ directory.

1. **Run the Data Download Script:** The script `scripts/data_downloader.py` downloads the necessary data files from the specified URLs
    
    ```bash
    python scripts/data_downloader.py
    ```
    This will save `orders.csv` and `invoicing_data.json` in the `data/` folder, creating it if it doesn’t exist.

**Testing Data Download:** A unit test is available to verify that the data download function works correctly and saves files as expected.

To run the test for `data_downloader.py`, use:
    
```bash
pytest tests/test_data_downloader.py
```
This will check that the files are downloaded to the correct location and validate their presence after the download completes.

## Task 1: Distribution of Crate Type per Company

This task calculates the distribution of crate types per company, based on the number of orders for each type.

**Solution Summary:**

1. **Data Loading**: Reads data from `orders.csv`.
2. **Data Validation**: 
    - Excludes rows with missing `company_id` or `crate_type`.
    - Converts `company_id` and `crate_type` to strings if necessary.
    - Filters `crate_type` to only include valid values (Plastic, Wood, Metal).
    - Warns about duplicate `order_id` entries.
3. **Distribution Calculation**: Calculates the number of orders per crate type for each company.
4. **Output Generation**: Saves the resulting distribution as `crate_distribution.csv` in the `output/` directory.

**How to run:**

```bash
python scripts/calculate_crate_distribution.py
```

**Example Output:** The output CSV has the following structure:

| company_id                             | crate_type | order_count |
|----------------------------------------|------------|-------------|
| 1e2b47e6-499e-41c6-91d3-09d12dddfbbd   | Plastic    | 10          |
| 34538e39-cd2e-4641-8d24-3c94146e6f16   | Wood       | 5           |

**Running Unit Tests:** Unit tests are provided to ensure the correct functionality of the data processing functions in `scripts/calculate_crate_distribution.py`. The tests cover:
- Data loading and validation to ensure the data is cleaned correctly.
- Calculation of crate type distribution per company.
- Saving of the output distribution file.

**How to run the tests:** To run the tests, use the following command:

```bash
pytest tests/test_calculate_crate_distribution.py
```

If all tests pass, you should see output indicating success:
    
```bash
==================================================================== test session starts ====================================================================
platform darwin -- Python 3.11.5, pytest-8.3.3
collected 4 items

tests/test_calculate_crate_distribution.py ....                                                                                                                                                                                                                                               [100%]
```

## Task 2: DataFrame of Orders with Full Name of the Contact

This task extracts the contact full name from each order and outputs a DataFrame containing `order_id` and `contact_full_name`. If contact information is missing, a placeholder “John Doe” is used.

**Solution Summary:**

1. **Data Extraction**: Reads `contact_data` field from `orders.csv`.
2. **Data Validation and Transformation**:
    - Parses `contact_data` to extract `contact_name` and `contact_surname`.
    - If either name is missing, assigns “John Doe”.
3. **Output Generation**: Saves the resulting DataFrame as `contact_fullname.csv` in the `output/` directory.

**How to Run:**

```bash
python scripts/calculate_contact_fullname.py
```

**Example Output:** The output CSV has the following structure:

| order_id                               | contact_full_name |
|----------------------------------------|-------------------|
| f47ac10b-58cc-4372-a567-0e02b2c3d479   | Curtis Jackson    |
| f47ac10b-58cc-4372-a567-0e02b2c3d480   | Maria Theresa     |

**Running Unit Tests:** Unit tests verify that:

- Full names are correctly extracted.
- Missing or incomplete data defaults to “John Doe”.
- Output CSV is created and matches the expected DataFrame structure.

To run the tests, use:
    
```bash
pytest tests/test_calculate_contact_fullname.py
```

## Task 3: DataFrame of Orders with Contact Address

This task extracts the city and postal code from each order’s contact information and outputs a DataFrame with `order_id` and `contact_address`. If the city name or postal code is missing, default values “Unknown” and “UNK00” are used, respectively.

**Solution Summary:**

1. **Data Extraction**: Reads `contact_data` field from `orders.csv`.
2. **Data Validation and Transformation**:
    - Parses `contact_data` to extract `city` and `postal_code`.
    - If `city` or `postal_code` is missing, assigns “Unknown” or “UNK00” as default values.
3. **Output Generation**: Saves the resulting DataFrame as `contact_address.csv` in the `output/` directory.

**How to Run:**

```bash
python scripts/contact_address_processing.py
```

**Example Output:** The output CSV has the following structure:

| order_id                               | contact_address |
|----------------------------------------|-----------------|
| f47ac10b-58cc-4372-a567-0e02b2c3d479   | New York, 10001 |
| f47ac10b-58cc-4372-a567-0e02b2c3d480   | Unknown, UNK00  |

**Running Unit Tests:** Unit tests are provided to verify:

- The correct extraction of city and postal code.
- Default values are applied for missing data.
- Output CSV matches the expected structure.

To run the tests, use:

```bash
pytest tests/test_contact_address_processing.py
```

If all tests pass, you will see output indicating success.

## Task 4: Calculation of Sales Team Commissions

This task calculates commissions for the sales team based on each order’s net invoiced value. Commissions are allocated as follows:
- **Main Owner**: 6% of the net invoiced value.
- **Co-owner 1**: 2.5% of the net invoiced value.
- **Co-owner 2**: 0.95% of the net invoiced value.
- Any additional co-owners do not receive a commission.

**Solution Summary:**

1. **Data Loading**: Loads data from `orders.csv` and `invoicing_data.json`.
2. **Data Validation**: Ensures required fields are present in both datasets, checking for valid `order_id`, `salesowners`, and `net_invoiced_value_euros`.
3. **Commission Calculation**:
    - Calculates commission based on sales owner position.
    - Adds commission totals for each sales owner.
4. **Output Generation**: Saves the resulting DataFrame as `sales_owner_commissions.csv` in the `output/` directory.

**How to Run:**

```bash
python scripts/calculate_commissions.py
```

This will output a CSV file with the following structure:

| sales_owner      | total_commission |
|------------------|------------------|
| Leonard Cohen    | 629.28           |
| David Henderson  | 465.34           |

**Running Unit Tests:** Unit tests for `calculate_commissions.py` include checks for:

	•	Correctness of calculated commissions.
	•	Validation of required fields.
	•	Proper sorting order of sales owner commissions.
	•	CSV file creation with the expected content.

to run the tests, use:

```bash
pytest tests/test_calculate_commissions.py
```

tt 