#!/usr/bin/env python3
"""
build_stock_sales_relation.py

Este script genera el archivo 'historico_stock_ventas.csv' a partir de los archivos de entrada:
- 'stock.csv' con información del inventario inicial
- 'ventas.csv' con el histórico de ventas por fecha y SKU

El archivo de salida tiene las columnas:
Fecha,SKU,Stock,Unidades_Vendidas,Reposicion

- Stock: stock disponible al inicio del día para ese SKU
- Unidades_Vendidas: unidades vendidas ese día (0 si no hubo ventas para ese SKU/día)
- Reposicion: 1 si el stock sube respecto al día anterior (es decir, ha habido reposición), 0 en caso contrario

Uso desde CLI:
$ python build_stock_sales_relation.py --stock stock.csv --ventas ventas.csv --output historico_stock_ventas.csv

Puedes usarlo dentro de Docker tal y como se muestra en el README.md.

@author: blascosmog
"""

import argparse
import pandas as pd
import numpy as np
import sys
import os

def validate_stock_columns(df: pd.DataFrame):
    """
    Valida que stock.csv tenga las columnas necesarias
    """
    expected = [
        "SKU", "Producto", "Categoría", "Talla", "Color", "Stock", "Precio_Unitario", "Umbral"
    ]
    missing = [col for col in expected if col not in df.columns]
    if missing:
        raise ValueError(f"stock.csv - Faltan columnas: {missing}")

def validate_ventas_columns(df: pd.DataFrame):
    """
    Valida que ventas.csv tenga las columnas necesarias
    """
    expected = ["Fecha", "SKU", "Unidades_Vendidas"]
    missing = [col for col in expected if col not in df.columns]
    if missing:
        raise ValueError(f"ventas.csv - Faltan columnas: {missing}")

def build_relation(stock_csv_path: str, ventas_csv_path: str, output_csv_path: str):
    """
    Genera el CSV de relación entre stock y ventas.
    - Para cada día y SKU calcula el stock al inicio, las ventas ese día y si hubo reposición.
    - Guarda el resultado en output_csv_path.
    """
    # Leer y validar entradas
    if not os.path.exists(stock_csv_path):
        raise FileNotFoundError(f"Archivo no encontrado: {stock_csv_path}")
    if not os.path.exists(ventas_csv_path):
        raise FileNotFoundError(f"Archivo no encontrado: {ventas_csv_path}")

    stock_df = pd.read_csv(stock_csv_path)
    validate_stock_columns(stock_df)
    ventas_df = pd.read_csv(ventas_csv_path, parse_dates=["Fecha"])
    validate_ventas_columns(ventas_df)

    # Asegurar tipos correctos
    stock_df["SKU"] = stock_df["SKU"].astype(str)
    ventas_df["SKU"] = ventas_df["SKU"].astype(str)

    # Obtener todas las fechas del histórico de ventas
    fechas = ventas_df["Fecha"].drop_duplicates().sort_values()
    all_skus = stock_df["SKU"].unique()
    idx = pd.MultiIndex.from_product([fechas, all_skus], names=["Fecha", "SKU"])
    ventas_full = ventas_df.set_index(["Fecha", "SKU"]).reindex(idx, fill_value=0).reset_index()

    # Añadir columna de stock inicial por SKU
    initial_stock_map = stock_df.set_index("SKU")["Stock"].to_dict()
    ventas_full["Stock"] = ventas_full["SKU"].map(initial_stock_map)
    ventas_full = ventas_full.sort_values(["SKU", "Fecha"]).reset_index(drop=True)

    # Simular el stock día a día por SKU y marcar reposiciones
    historico = []
    for sku in all_skus:
        sku_registros = ventas_full[ventas_full["SKU"] == sku].copy()
        prev_stock = initial_stock_map[sku]
        for i, row in sku_registros.iterrows():
            fecha = row["Fecha"]
            unidades_vendidas = int(row["Unidades_Vendidas"])
            # Para el primer día, usamos el stock inicial
            if i == sku_registros.index[0]:
                stock = prev_stock
            else:
                # Calculamos el stock restando las ventas del día anterior
                stock = historico[-1]["Stock"] - historico[-1]["Unidades_Vendidas"]
                # No puede haber stock negativo
                if stock < 0:
                    stock = 0
            # Detectar reposición
            if len(historico) > 0 and historico[-1]["SKU"] == sku:
                prev_stock_value = historico[-1]["Stock"] - historico[-1]["Unidades_Vendidas"]
                reposicion = 1 if stock > prev_stock_value else 0
            else:
                reposicion = 0
            historico.append({
                "Fecha": fecha.strftime("%Y-%m-%d") if not isinstance(fecha, str) else fecha,
                "SKU": sku,
                "Stock": stock,
                "Unidades_Vendidas": unidades_vendidas,
                "Reposicion": reposicion
            })

    historico_df = pd.DataFrame(historico, columns=["Fecha", "SKU", "Stock", "Unidades_Vendidas", "Reposicion"])
    historico_df.to_csv(output_csv_path, index=False)
    print(f"Generado {output_csv_path}: {len(historico_df)} filas.")

def main():
    parser = argparse.ArgumentParser(description="Construye histórico stock-ventas.")
    parser.add_argument('--stock', required=True, help="Ruta a stock.csv")
    parser.add_argument('--ventas', required=True, help="Ruta a ventas.csv")
    parser.add_argument('--output', required=True, help="Ruta a historico_stock_ventas.csv")
    args = parser.parse_args()
    try:
        build_relation(args.stock, args.ventas, args.output)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()