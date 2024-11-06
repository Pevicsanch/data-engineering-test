# Usa una imagen base de Python
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia el contexto de construcción
COPY . /app

# Crea los directorios de datos y salidas
RUN mkdir -p /app/data /app/output

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Da permisos de ejecución al entrypoint
RUN chmod +x /app/entrypoint.sh

# Define el entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]