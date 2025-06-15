import pandas as pd

def construir_historico(stock_df, ventas_df):
    """
    Construye el histórico de stock y ventas, incluyendo precio unitario e ingresos brutos.
    Devuelve un DataFrame listo para exportar a CSV.
    """

    # Unir ventas con stock para traer Precio_Unitario
    df = ventas_df.merge(stock_df[['SKU', 'Precio_Unitario']], on='SKU', how='left')

    # Si Stock no está en ventas_df, intenta traerlo de stock_df (puedes adaptar esto según tu lógica real)
    if 'Stock' not in df.columns:
        stock_map = dict(zip(stock_df['SKU'], stock_df['Stock']))
        df['Stock'] = df['SKU'].map(stock_map)
    # Si Reposicion no existe, la ponemos a 0 por defecto
    if 'Reposicion' not in df.columns:
        df['Reposicion'] = 0

    # Calcula los ingresos brutos
    df['Ingresos_Brutos'] = df['Precio_Unitario'] * df['Unidades_Vendidas']

    # Asegúrate de que las columnas están en el orden correcto
    columnas = [
        'Fecha',
        'SKU',
        'Stock',
        'Unidades_Vendidas',
        'Reposicion',
        'Precio_Unitario',
        'Ingresos_Brutos'
    ]
    df = df[columnas]

    # Opcional: ordena por fecha y SKU
    df = df.sort_values(['Fecha', 'SKU'])

    return df

if __name__ == "__main__":
    # Lee los archivos (ajusta la ruta si hace falta)
    stock_df = pd.read_csv("stock.csv")
    ventas_df = pd.read_csv("ventas.csv")
    ventas_df["Fecha"] = pd.to_datetime(ventas_df["Fecha"]).dt.strftime("%Y-%m-%d")

    historico_df = construir_historico(stock_df, ventas_df)
    historico_df.to_csv("historico_stock_ventas.csv", index=False)
    print("historico_stock_ventas.csv generado correctamente con columnas:", historico_df.columns.tolist())
