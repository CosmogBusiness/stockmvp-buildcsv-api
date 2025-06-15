import pandas as pd

def construir_historico(stock_df, ventas_df):
    """
    Construye el histórico de stock y ventas, incluyendo precio unitario e ingresos brutos.
    Devuelve un DataFrame listo para exportar a CSV.
    """
    # Unimos ventas y stock para obtener el precio unitario de cada venta
    df = ventas_df.merge(stock_df[['SKU', 'Precio_Unitario']], on='SKU', how='left')
    df['Ingresos_Brutos'] = df['Precio_Unitario'] * df['Unidades_Vendidas']

    # Suponemos que tienes stock y reposición por SKU y fecha en ventas_df, si no, adapta aquí
    # Si hace falta obtener "Stock" y "Reposicion" para cada registro de venta, añade tu lógica aquí

    # Reordena las columnas en el orden requerido
    columnas = [
        "Fecha",
        "SKU",
        "Stock",
        "Unidades_Vendidas",
        "Reposicion",
        "Precio_Unitario",
        "Ingresos_Brutos"
    ]
    df = df[columnas]
    return df

if __name__ == "__main__":
    # Ejemplo de lectura de archivos (ajusta rutas o métodos según tu flujo real)
    stock_df = pd.read_csv("stock.csv")
    ventas_df = pd.read_csv("ventas.csv")
    # Asegúrate de que 'Fecha' es de tipo fecha
    ventas_df["Fecha"] = pd.to_datetime(ventas_df["Fecha"])

    historico_df = construir_historico(stock_df, ventas_df)
    historico_df.to_csv("historico_stock_ventas.csv", index=False)
