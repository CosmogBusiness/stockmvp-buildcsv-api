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

def build_stock_sales_relation(stock_bytes: bytes, ventas_bytes: bytes, overrides: list = None) -> pd.DataFrame:
    """
    Lee los CSV de stock y ventas (en bytes), valida y construye el DataFrame de relación:
    Fecha,SKU,Stock,Unidades_Vendidas,Reposicion,Precio_Unitario,Ingresos_Brutos

    - Stock: stock al inicio de la fecha
    - Unidades_Vendidas: vendidas ese día (0 si no hay)
    - Reposicion: por defecto 0, pero modificable por overrides
    - Precio_Unitario: extraído de stock.csv
    - Ingresos_Brutos: Precio_Unitario * Unidades_Vendidas

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

    # Simular stock día a día y agregar columna Reposicion = 0 por defecto
    historico = []
    for sku in all_skus:
        sku_registros = ventas_full[ventas_full["SKU"] == sku].copy()
        prev_stock = initial_stock_map[sku]
        for i, row in sku_registros.iterrows():
            fecha = row["Fecha"]
            unidades_vendidas = int(row["Unidades_Vendidas"])
            # Aplicar overrides si corresponde
            reposicion = 0
            if overrides:
                for ov in overrides:
                    if ov.get("Fecha") == str(fecha) and ov.get("SKU") == str(sku):
                        if "Unidades_Vendidas" in ov:
                            unidades_vendidas = ov["Unidades_Vendidas"]
                        if "Reposicion" in ov:
                            reposicion = ov["Reposicion"]
            historico.append({
                "Fecha": fecha,
                "SKU": sku,
                "Stock": prev_stock,
                "Unidades_Vendidas": unidades_vendidas,
                "Reposicion": reposicion
            })
            prev_stock = prev_stock - unidades_vendidas + reposicion

    historico_df = pd.DataFrame(historico)

    # Añade la columna Precio_Unitario (del stock original)
    precio_map = stock_df.set_index("SKU")["Precio_Unitario"].to_dict()
    historico_df["Precio_Unitario"] = historico_df["SKU"].map(precio_map)

    # Añade la columna Ingresos_Brutos (Precio_Unitario * Unidades_Vendidas)
    historico_df["Ingresos_Brutos"] = historico_df["Precio_Unitario"] * historico_df["Unidades_Vendidas"]

    # Asegura el orden de columnas original + nuevas
    historico_df = historico_df[
        ["Fecha", "SKU", "Stock", "Unidades_Vendidas", "Reposicion", "Precio_Unitario", "Ingresos_Brutos"]
    ]

    return historico_df
