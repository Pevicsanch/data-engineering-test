#!/bin/bash

# Create directories if they don't exist
mkdir -p /app/data /app/output

# Download data
echo "Starting data download..."
python /app/scripts/data_downloader.py

# Run data processing scripts
echo "Running dash data processing scripts..."
python /app/scripts/calculate_crate_distribution.py
python /app/scripts/calculate_sales_performance.py
python /app/scripts/calculate_top_performers.py

# Run other scripts
echo "Running other scripts..."
python /app/scripts/calculate_contact_fullname.py
python /app/scripts/contact_address_processing.py
python /app/scripts/calculate_commissions.py
python /app/scripts/company_salesowners.py
echo "Ejecutando pruebas unitarias..."
pytest /app/tests
TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -ne 0 ]; then
    echo "Las pruebas unitarias fallaron. Abortando."
    exit $TEST_EXIT_CODE
fi

echo "Iniciando la aplicación Dash..."
python /app/scripts/dashboard_app.py

