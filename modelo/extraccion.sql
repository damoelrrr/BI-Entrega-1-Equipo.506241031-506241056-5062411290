-- Conjunto de datos del modelo: unidades vendidas por tienda, producto y mes.
-- Granularidad: una fila por tienda x producto x mes (5 x 30 x 36 = 5.400 filas).
-- Se parte de todas las combinaciones (LEFT JOIN) para que los meses sin ventas
-- aparezcan con 0 unidades y no se pierdan.
-- Ejecutar conectado a retailbi_dw (esquema dw).
WITH meses AS (
    SELECT anio, mes, anio_mes, MIN(fecha_key) AS fecha_key   -- fecha_key del primer día del mes
    FROM dw.dim_fecha
    GROUP BY anio, mes, anio_mes
),
ventas AS (
    SELECT d.anio_mes, f.tienda_key, f.producto_key,
           SUM(f.cantidad)    AS unidades,
           SUM(f.venta_bruta) AS venta_bruta,
           SUM(f.descuento)   AS descuento
    FROM dw.fact_ventas f
    JOIN dw.dim_fecha d ON d.fecha_key = f.fecha_key
    GROUP BY d.anio_mes, f.tienda_key, f.producto_key
)
SELECT m.fecha_key, m.anio, m.mes, m.anio_mes,
       t.tienda_key,   t.nombre_tienda,
       p.producto_key, p.nombre_producto, p.categoria,
       COALESCE(v.unidades, 0)    AS unidades,
       COALESCE(v.venta_bruta, 0) AS venta_bruta,
       COALESCE(v.descuento, 0)   AS descuento
FROM meses m
CROSS JOIN dw.dim_tienda   t
CROSS JOIN dw.dim_producto p
LEFT JOIN ventas v ON v.anio_mes = m.anio_mes
                  AND v.tienda_key = t.tienda_key
                  AND v.producto_key = p.producto_key
WHERE t.tienda_key <> -1
  AND p.producto_key <> -1
ORDER BY t.tienda_key, p.producto_key, m.anio_mes;
