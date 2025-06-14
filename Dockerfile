# Dockerfile para construir el CSV de relación stock-ventas
FROM python:3.11-slim

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements y script
COPY requirements.txt .
COPY build_stock_sales_relation.py .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Definir /data como volumen para intercambiar archivos con el host
VOLUME ["/data"]

# Comando de ejemplo (puedes cambiar argumentos en docker run)
CMD ["python", "build_stock_sales_relation.py", \
     "--stock", "/data/stock.csv", \
     "--ventas", "/data/ventas.csv", \
     "--output", "/data/historico_stock_ventas.csv"]