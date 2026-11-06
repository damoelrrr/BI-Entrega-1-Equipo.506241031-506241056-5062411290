-- Lado "fuente": se ejecuta con DuckDB (https://duckdb.org) sobre el CSV original,
-- sin pasar por PostgreSQL. Ajustar la ruta al archivo de datos/raw/.
SELECT COUNT(*)                   AS lineas,
       SUM(cantidad)              AS unidades,
       SUM(cantidad * precio_unitario_cop)  AS venta_bruta,
       SUM(descuento_cop)         AS descuento,
       SUM(total_venta_cop)       AS venta_neta
FROM read_csv_auto('datos/raw/RetailBI_ventas_sinteticas_50000.csv');
