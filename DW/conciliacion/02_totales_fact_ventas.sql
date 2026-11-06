-- Totales de la tabla de hechos (comparar con la fuente F3, consulta 04)
SELECT COUNT(*)           AS lineas,
       SUM(cantidad)      AS unidades,
       SUM(venta_bruta)   AS venta_bruta,
       SUM(descuento)     AS descuento,
       SUM(venta_neta)    AS venta_neta
FROM dw.fact_ventas;
