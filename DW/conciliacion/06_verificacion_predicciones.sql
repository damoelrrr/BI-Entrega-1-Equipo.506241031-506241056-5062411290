-- Verificación de las predicciones cargadas (Entrega 3)
SELECT COUNT(*)                         AS filas,            -- esperado: 1800
       ROUND(AVG(error_abs), 2)         AS mae,              -- esperado: 7,22
       SUM(unidades_real)               AS unidades_reales,
       ROUND(SUM(unidades_pred), 0)     AS unidades_pronosticadas
FROM dw.pred_ventas_unidades;

-- Llaves sin dimensión (debe devolver 0)
SELECT COUNT(*) AS predicciones_sin_dimension
FROM dw.pred_ventas_unidades p
LEFT JOIN dw.dim_fecha    d ON d.fecha_key    = p.fecha_key
LEFT JOIN dw.dim_tienda   t ON t.tienda_key   = p.tienda_key
LEFT JOIN dw.dim_producto r ON r.producto_key = p.producto_key
WHERE d.fecha_key IS NULL OR t.tienda_key IS NULL OR r.producto_key IS NULL;
