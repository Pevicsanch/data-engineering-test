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
│   └── data_downloader.py
├── notebooks/
├── tests/
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

1. **Run the Data Download Script:** The script scripts/data_downloader.py downloads the necessary data files from the specified URLs
    
    ```bash
    python scripts/data_downloader.py
    ```
This will save orders.csv and invoicing_data.json in the data/ folder, creating it if it doesn’t exist.

## Task 1: Distribution of Crate Type per Company

This task calculates the distribution of crate types per company, based on the number of orders for each type.

**Solution Summary:**

1.	**Data Loading**: Reads data from orders.csv.
2.	**Data Validation:**: 
    - 	Excludes rows with missing company_id or crate_type.
	-	Converts company_id and crate_type to strings if necessary.
	-	Filters crate_type to only include valid values (Plastic, Wood, Metal).
	-	Warns about duplicate order_id entries.
3. **Distribution Calculation**: Calculates the number of orders per crate type for each company.
4. **Output Generation**:saves the resulting distribution as crate_distribution.csv in the output/ directory.

**How to run:**

```bash
python scripts/calculate_crate_distribution.py
```

**example output:** The output CSV has the following structure:

| company_id                             | crate_type | order_count |
|----------------------------------------|------------|-------------|
| 1e2b47e6-499e-41c6-91d3-09d12dddfbbd   | Plastic    | 10          |
| 34538e39-cd2e-4641-8d24-3c94146e6f16   | Wood       | 5           |