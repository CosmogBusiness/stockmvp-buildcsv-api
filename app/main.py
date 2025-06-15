"""
main.py

API FastAPI para construir el CSV histórico de stock-ventas desde dos archivos CSV subidos.
"""

import os
import json
from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
from fastapi.responses import FileResponse
from app.logic import build_stock_sales_relation, RelationCSVError
import pandas as pd

TMP_OUTPUT = "/tmp/historico_stock_ventas.csv"
# Puedes migrar esto a una lista/set desde base de datos para múltiples claves
API_KEYS = {"4p1k3y_53cr3t4Oc05m06bu51n355"}

app = FastAPI(
    title="Stock Sales Relation API",
    description="API para construir el histórico de relación stock-ventas combinando stock.csv y ventas.csv.",
    version="1.0.0"
)

# Middleware para verificar clave API en header x-api-key (más seguro, estándar)
@app.middleware("http")
async def verificar_api_key(request: Request, call_next):
    if request.url.path.startswith("/build-relation"):
        apikey = request.headers.get("x-api-key")
        if apikey not in API_KEYS:
            raise HTTPException(status_code=401, detail="Acceso no autorizado. API key inválida.")
    return await call_next(request)


@app.get("/", tags=["Healthcheck"])
async def root():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/build-relation/", tags=["Generador CSV"], responses={
    200: {
        "content": {"text/csv": {}},
        "description": "Archivo CSV de histórico stock-ventas"
    },
    401: {"description": "No autorizado, clave API inválida"},
    400: {"description": "Error de validación o procesamiento"}
})
async def build_relation_endpoint(
    stock_file: UploadFile = File(..., description="Archivo stock.csv"),
    ventas_file: UploadFile = File(..., description="Archivo ventas.csv"),
    overrides: str = Form(None, description="JSON con overrides para Reposicion y Unidades_Vendidas")
):
    """
    Sube stock.csv y ventas.csv y descarga historico_stock_ventas.csv generado.
    Permite overrides para campos de Reposicion y Unidades_Vendidas en combinaciones Fecha y SKU.

    El parámetro overrides debe ser un JSON tipo:
    {
      "overrides": [
        {"Fecha": "2025-06-24", "SKU": "1001", "Reposicion": 8, "Unidades_Vendidas": 3}
      ]
    }

    Para acceder, añade el header:
      x-api-key: 4p1k3y_53cr3t4Oc05m06bu51n355
    """
    try:
        stock_bytes = await stock_file.read()
        ventas_bytes = await ventas_file.read()
        overrides_obj = json.loads(overrides) if overrides else None
        override_list = overrides_obj["overrides"] if overrides_obj and "overrides" in overrides_obj else None
        df = build_stock_sales_relation(stock_bytes, ventas_bytes, override_list)
        df.to_csv(TMP_OUTPUT, index=False)
    except RelationCSVError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error procesando los archivos: {e}")

    if not os.path.exists(TMP_OUTPUT):
        raise HTTPException(status_code=500, detail="No se pudo generar el archivo de salida.")
    return FileResponse(TMP_OUTPUT, media_type="text/csv", filename="historico_stock_ventas.csv")
