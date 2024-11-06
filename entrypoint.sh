#!/bin/bash

set -e  # Terminar el script si algún comando falla

echo "Starting data download..."
python /app/scripts/data_downloader.py

echo "Running data processing scripts..."
python /app/scripts/calculate_crate_distribution.py
python /app/scripts/calculate_sales_performance.py
python /app/scripts/calculate_top_performers.py

echo "Starting the Dash application..."
exec python /app/scripts/dashboard_app.py