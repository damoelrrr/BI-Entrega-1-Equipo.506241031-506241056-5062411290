-- Todas las consultas deben devolver 0
SELECT 'hechos sin fecha'      AS control, COUNT(*) AS filas
FROM dw.fact_ventas f LEFT JOIN dw.dim_fecha d ON d.fecha_key = f.fecha_key
WHERE d.fecha_key IS NULL
UNION ALL
SELECT 'hechos con tienda desconocida', COUNT(*) FROM dw.fact_ventas WHERE tienda_key = -1
UNION ALL
SELECT 'hechos con producto desconocido', COUNT(*) FROM dw.fact_ventas WHERE producto_key = -1
UNION ALL
SELECT 'hechos con descuento desconocido', COUNT(*) FROM dw.fact_ventas WHERE descuento_key = -1
UNION ALL
SELECT 'venta_neta <> bruta - descuento', COUNT(*)
FROM dw.fact_ventas WHERE venta_neta <> venta_bruta - descuento
UNION ALL
SELECT 'venta_id duplicado', COUNT(*) FROM (
    SELECT venta_id FROM dw.fact_ventas GROUP BY venta_id HAVING COUNT(*) > 1) x
UNION ALL
SELECT 'dias sin registro en dim_fecha (2023-2025)', 1096 - COUNT(*)
FROM dw.dim_fecha WHERE fecha BETWEEN DATE '2023-01-01' AND DATE '2025-12-31';
