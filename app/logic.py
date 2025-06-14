"""
logic.py

Funciones de negocio para la generación del histórico de stock-ventas.
"""

import pandas as pd
import numpy as np

class RelationCSVError(Exception):
    """Excepción personalizada para errores de formato de CSV."""
    pass

def validate_stock_df(df: pd.DataFrame):
    """
    Valida que el DataFrame de stock tenga las columnas requeridas.
    Lanza RelationCSVError si falta alguna columna.
    """
    expected = [
        "SKU", "Producto", "Categoría", "Talla", "Color", "Stock", "Precio_Unitario", "Umbral"
    ]
    missing = [col for col in expected if col not in df.columns]
    if missing:
        raise RelationCSVError(f"stock.csv - Faltan columnas: {missing}")

def validate_ventas_df(df: pd.DataFrame):
    """
    Valida que el DataFrame de ventas tenga las columnas requeridas.
    Lanza RelationCSVError si falta alguna columna.
    """
    expected = ["Fecha", "SKU", "Unidades_Vendidas"]
    missing = [col for col in expected if col not in df.columns]
    if missing:
        raise RelationCSVError(f"ventas.csv - Faltan columnas: {missing}")

def build_stock_sales_relation(stock_bytes: bytes, ventas_bytes: bytes) -> pd.DataFrame:
    """
    Lee los CSV de stock y ventas (en bytes), valida y construye el DataFrame de relación:
    Fecha,SKU,Stock,Unidades_Vendidas

    - Stock: stock al inicio de la fecha
    - Unidades_Vendidas: vendidas ese día (0 si no hay)

    Lanza RelationCSVError si los formatos no son correctos.
    """

    # Leer archivos
    try:
        stock_df = pd.read_csv(pd.io.common.BytesIO(stock_bytes))
        ventas_df = pd.read_csv(pd.io.common.BytesIO(ventas_bytes), parse_dates=["Fecha"])
    except Exception as e:
        raise RelationCSVError(f"Error leyendo los archivos CSV: {e}")

    validate_stock_df(stock_df)
    validate_ventas_df(ventas_df)

    # Normalizar SKU
    stock_df["SKU"] = stock_df["SKU"].astype(str)
    ventas_df["SKU"] = ventas_df["SKU"].astype(str)

    # Todas las fechas ordenadas
    fechas = ventas_df["Fecha"].drop_duplicates().sort_values()
    all_skus = stock_df["SKU"].unique()
    idx = pd.MultiIndex.from_product([fechas, all_skus], names=["Fecha", "SKU"])
    ventas_full = ventas_df.set_index(["Fecha", "SKU"]).reindex(idx, fill_value=0).reset_index()

    # Stock inicial de cada SKU
    initial_stock_map = stock_df.set_index("SKU")["Stock"].to_dict()
    ventas_full["Stock"] = ventas_full["SKU"].map(initial_stock_map)
    ventas_full = ventas_full.sort_values(["SKU", "Fecha"]).reset_index(drop=True)

    # Simular stock día a día
    historico = []
    for sku in all_skus:
        sku_registros = ventas_full[ventas_full["SKU"] == sku].copy()
        prev_stock = initial_stock_map[sku]
        for i, row in sku_registros.iterrows():
            fecha = row["Fecha"]
            unidades_vendidas = int(row["Unidades_Vendidas"])
            # Primer día: stock inicial
            if i == sku_registros.index[0]:
                stock = prev_stock
            else:
                stock = historico[-1]["Stock"] - historico[-1]["Unidades_Vendidas"]
                stock = max(stock, 0)
            historico.append({
                "Fecha": fecha.strftime("%Y-%m-%d") if not isinstance(fecha, str) else fecha,
                "SKU": sku,
                "Stock": stock,
                "Unidades_Vendidas": unidades_vendidas
            })

    historico_df = pd.DataFrame(historico, columns=["Fecha", "SKU", "Stock", "Unidades_Vendidas"])
    return historico_df