-- Registros cargados en cada tabla del data warehouse
SELECT 'dim_fecha'                  AS tabla, COUNT(*) AS registros FROM dw.dim_fecha
UNION ALL SELECT 'dim_tienda',                COUNT(*) FROM dw.dim_tienda
UNION ALL SELECT 'dim_producto',              COUNT(*) FROM dw.dim_producto
UNION ALL SELECT 'dim_descuento',             COUNT(*) FROM dw.dim_descuento
UNION ALL SELECT 'fact_ventas',               COUNT(*) FROM dw.fact_ventas
UNION ALL SELECT 'ctx_emc_comercio_minorista',COUNT(*) FROM dw.ctx_emc_comercio_minorista
UNION ALL SELECT 'ctx_empresas_bogota',       COUNT(*) FROM dw.ctx_empresas_bogota
ORDER BY tabla;
