"""
main.py

API FastAPI para construir el CSV histórico de stock-ventas desde dos archivos CSV subidos.
"""

import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from app.logic import build_stock_sales_relation, RelationCSVError
import pandas as pd

TMP_OUTPUT = "/tmp/historico_stock_ventas.csv"

app = FastAPI(
    title="Stock Sales Relation API",
    description="API para construir el histórico de relación stock-ventas combinando stock.csv y ventas.csv.",
    version="1.0.0"
)

@app.get("/", tags=["Healthcheck"])
async def root():
    """Health check endpoint."""
    return {"status": "ok"}

@app.post("/build-relation/", tags=["Generador CSV"])
async def build_relation_endpoint(
    stock_file: UploadFile = File(..., description="Archivo stock.csv"),
    ventas_file: UploadFile = File(..., description="Archivo ventas.csv")
):
    """
    Sube stock.csv y ventas.csv y descarga historico_stock_ventas.csv generado.
    """
    try:
        stock_bytes = await stock_file.read()
        ventas_bytes = await ventas_file.read()
        df = build_stock_sales_relation(stock_bytes, ventas_bytes)
        df.to_csv(TMP_OUTPUT, index=False)
    except RelationCSVError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error procesando los archivos: {e}")

    if not os.path.exists(TMP_OUTPUT):
        raise HTTPException(status_code=500, detail="No se pudo generar el archivo de salida.")
    return FileResponse(TMP_OUTPUT, media_type="text/csv", filename="historico_stock_ventas.csv")