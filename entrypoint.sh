#!/bin/bash

# Crear directorios en caso de que no existan
mkdir -p /app/data /app/output

# Descargar los datos
echo "Iniciando la descarga de datos..."
python /app/scripts/data_downloader.py

# Ejecutar los scripts de procesamiento de datos
echo "Ejecutando scripts de procesamiento de datos..."
python /app/scripts/calculate_crate_distribution.py
python /app/scripts/calculate_sales_performance.py
python /app/scripts/calculate_top_performers.py

# Iniciar la aplicación Dash
echo "Iniciando la aplicación Dash..."
exec python /app/scripts/dashboard_app.py