import sys
import os
import pytest
import pandas as pd
import logging

# Configurar logging en el test
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Añadir la carpeta "scripts" al sys.path si no está ya en él
scripts_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

try:
    from company_salesowners import create_df3, normalize_company_name
except ImportError:
    raise ImportError("Ensure that 'company_salesowners.py' is in the 'scripts' directory and the path is correctly added to sys.path.")

# Ruta de prueba para el archivo de salida
output_path = os.path.join('..', 'output', 'df3_test.csv')

# Datos de prueba para simular `orders.csv`
test_data = pd.DataFrame({
    'company_id': ['1', '2', '1', '3'],
    'company_name': ['Fresh Fruits Co', 'Veggies Inc', 'Fresh Fruits Ltd', 'Healthy Snacks Ltd'],
    'salesowners': ['Alice Smith, Bob Brown', 'Charlie Green', 'Alice Smith', 'Dave White']
})

@pytest.fixture(scope="module")
def setup_output_file():
    # Limpiar el archivo de salida antes de las pruebas
    if os.path.exists(output_path):
        os.remove(output_path)
    yield
    # Eliminar el archivo de salida después de las pruebas
    if os.path.exists(output_path):
        os.remove(output_path)

def test_normalize_company_name():
    # Test de normalización con múltiples casos
    assert normalize_company_name("Fresh Fruits Ltd.") == "fresh fruit"
    assert normalize_company_name("Veggies Inc.") == "veggie"
    assert normalize_company_name("Healthy Snacks Co.") == "healthy snack"

def test_create_df3_structure(setup_output_file):
    # Test de creación de df3 y de la estructura correcta
    df3 = create_df3(test_data, output_path)
    
    # Verificar las columnas esperadas
    expected_columns = ['company_id', 'company_name', 'list_salesowners']
    assert all(col in df3.columns for col in expected_columns)
    
    # Verificar si los salesowners están ordenados y únicos
    sorted_salesowners = df3[df3['company_name'] == 'fresh fruit']['list_salesowners'].values[0]
    assert sorted_salesowners == 'Alice Smith, Bob Brown', f"Expected sorted list, got {sorted_salesowners}"

def test_output_file_creation(setup_output_file):
    # Ejecutar la función y verificar si el archivo de salida se ha creado
    create_df3(test_data, output_path)
    assert os.path.exists(output_path)

def test_duplicate_handling():
    # Probar la gestión de duplicados con un caso más complejo
    test_data_dup = pd.DataFrame({
        'company_id': ['1', '2', '3', '4', '1'],
        'company_name': ['Tropical Fruits Co', 'Tropical Fruits Ltd', 'Tropical Fruits', 'Fresh Fruits', 'Tropical Fruits Co'],
        'salesowners': ['Alice Smith', 'Bob Brown', 'Alice Smith, Dave White', 'Charlie Green', 'Bob Brown']
    })
    df3 = create_df3(test_data_dup, output_path)
    assert len(df3['company_id'].unique()) < len(test_data_dup['company_id'].unique()), \
        "Duplicate company IDs should be handled and grouped."