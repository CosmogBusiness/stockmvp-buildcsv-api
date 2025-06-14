# stock-sales-relation

Generador de histórico de stock y ventas listo para consumir por tu API FastAPI.

## Descripción

Este proyecto incluye un script en Python que, a partir de dos archivos CSV (`stock.csv` y `ventas.csv`), genera `historico_stock_ventas.csv` con la estructura y lógica necesaria para ser usado como input en tu backend de gestión de inventario en FastAPI (como el desplegado en Render.com).

## Estructura del proyecto

```
stock-sales-relation/
├── build_stock_sales_relation.py
├── Dockerfile
├── requirements.txt
└── README.md
```

## Formato de los archivos CSV

### Entrada 1: `stock.csv`
Columnas obligatorias (cabecera y orden):
```
SKU,Producto,Categoría,Talla,Color,Stock,Precio_Unitario,Umbral
```

Ejemplo:
```csv
SKU,Producto,Categoría,Talla,Color,Stock,Precio_Unitario,Umbral
1001,Camiseta Básica,Camiseta,M,Negro,15,5.99,5
1002,Pantalón Chino,Pantalón,L,Beige,30,12.50,10
```

### Entrada 2: `ventas.csv`
Columnas obligatorias:
```
Fecha,SKU,Unidades_Vendidas
```

Ejemplo:
```csv
Fecha,SKU,Unidades_Vendidas
2024-06-01,1001,2
2024-06-01,1002,1
2024-06-02,1001,3
```

### Salida: `historico_stock_ventas.csv`
Columnas generadas:
```
Fecha,SKU,Stock,Unidades_Vendidas,Reposicion
```

Ejemplo:
```csv
Fecha,SKU,Stock,Unidades_Vendidas,Reposicion
2024-06-01,1001,15,2,0
2024-06-02,1001,13,3,0
2024-06-01,1002,30,1,0
2024-06-02,1002,29,0,0
```

- **Stock**: stock disponible al inicio de cada fecha/SKU
- **Unidades_Vendidas**: unidades vendidas ese día (0 si no hubo ventas)
- **Reposicion**: 1 si el stock sube respecto al día anterior, 0 en caso contrario

## Cómo construir y ejecutar con Docker

1. Coloca tus CSV de entrada en una carpeta local, por ejemplo `./data`.

2. Construye la imagen:
   ```bash
   docker build -t stock-rel .
   ```

3. Ejecuta el script con tus archivos montados:
   ```bash
   docker run --rm -v "$(pwd)/data:/data" stock-rel \
     --stock /data/stock.csv \
     --ventas /data/ventas.csv \
     --output /data/historico_stock_ventas.csv
   ```

4. El archivo de salida `historico_stock_ventas.csv` estará disponible en tu carpeta `./data`.

## Notas

- El script validará que los CSV tengan todas las columnas necesarias y mostrará errores claros si falta alguna.
- El CSV generado es compatible con el endpoint `/procesar-todos/` de tu API FastAPI.
- Puedes modificar los nombres de los archivos y las rutas según tu conveniencia.