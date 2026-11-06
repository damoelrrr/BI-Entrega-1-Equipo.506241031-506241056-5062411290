-- Cifras de contraste para el tablero (P0 a P3). Deben coincidir con los visuales de Power BI.
-- P0: venta neta y unidades por año
SELECT d.anio, SUM(f.venta_neta) AS venta_neta, SUM(f.cantidad) AS unidades
FROM dw.fact_ventas f JOIN dw.dim_fecha d USING (fecha_key) GROUP BY d.anio ORDER BY d.anio;
-- P1: venta neta por categoría (y top 5 productos)
SELECT p.categoria, SUM(f.venta_neta) AS venta_neta
FROM dw.fact_ventas f JOIN dw.dim_producto p USING (producto_key) GROUP BY p.categoria ORDER BY 2 DESC;
SELECT p.nombre_producto, SUM(f.venta_neta) AS venta_neta
FROM dw.fact_ventas f JOIN dw.dim_producto p USING (producto_key) GROUP BY p.nombre_producto ORDER BY 2 DESC LIMIT 5;
-- P2: unidades por tienda
SELECT t.nombre_tienda, SUM(f.cantidad) AS unidades
FROM dw.fact_ventas f JOIN dw.dim_tienda t USING (tienda_key) GROUP BY t.nombre_tienda ORDER BY 2 DESC;
-- P3: variación mensual de la venta neta
WITH m AS (SELECT d.anio_mes, SUM(f.venta_neta) AS vn FROM dw.fact_ventas f JOIN dw.dim_fecha d USING (fecha_key) GROUP BY d.anio_mes)
SELECT anio_mes, vn, ROUND(100.0 * (vn - LAG(vn) OVER (ORDER BY anio_mes)) / LAG(vn) OVER (ORDER BY anio_mes), 1) AS var_pct
FROM m ORDER BY anio_mes;
