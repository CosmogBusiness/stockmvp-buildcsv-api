# Stock Sales Relation API

API y utilidad para generar automáticamente un CSV de relación stock‑ventas, listo para alimentar sistemas de análisis o dashboards.

## 🚀 ¿Qué hace este proyecto?

- Expone una API HTTP (FastAPI) para subir dos archivos CSV (`stock.csv`, `ventas.csv`) y recibir como respuesta un CSV `historico_stock_ventas.csv` con la relación diaria de stock y ventas, detectando reposiciones.
- Permite integración fácil con Render y cualquier plataforma Docker.

## 📦 Estructura del proyecto

```
stock-sales-relation/
├── app/
│   ├── main.py
│   └── logic.py
├── Dockerfile
├── requirements.txt
└── README.md
```

## 📈 Formato de los archivos

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
- **Stock**: stock al inicio de cada día/SKU
- **Unidades_Vendidas**: vendidas ese día (0 si no hubo ventas)
- **Reposicion**: 1 si el stock sube respecto al día anterior, 0 en caso contrario

## 🚢 Cómo construir y ejecutar con Docker

1. **Construye la imagen Docker:**
   ```bash
   docker build -t stock-rel-api .
   ```

2. **Ejecuta la API en el puerto 10000:**
   ```bash
   docker run --rm -p 10000:10000 stock-rel-api
   ```

3. **Usa la API desde Swagger UI (documentación interactiva):**
   Abre [http://localhost:10000/docs](http://localhost:10000/docs) en tu navegador.

4. **O desde consola, por ejemplo:**
   ```bash
   curl -F "stock_file=@stock.csv" -F "ventas_file=@ventas.csv" http://localhost:10000/build-relation/ --output historico.csv
   ```

## 🩺 Healthcheck

- Visita [http://localhost:10000/](http://localhost:10000/) para comprobar que el servicio está vivo (`{"status":"ok"}`).

---

### 🚀 ¡Proyecto listo para producción, subir a GitHub y desplegar en Render!

- El endpoint principal es `/build-relation/`
- Documentación interactiva (Swagger UI): `/docs`
- Valida errores de formato y devuelve mensajes claros (HTTP 400).
