-- Dimensión de tiempo: un registro por día, 2023-01-01 a 2025-12-31 (1.096 días)
CREATE TABLE dw.dim_fecha (
    fecha_key   INTEGER     PRIMARY KEY,          -- AAAAMMDD
    fecha       DATE        NOT NULL UNIQUE,
    dia         SMALLINT    NOT NULL,
    mes         SMALLINT    NOT NULL,
    nombre_mes  VARCHAR(12) NOT NULL,
    trimestre   SMALLINT    NOT NULL,
    anio        SMALLINT    NOT NULL,
    anio_mes    CHAR(7)     NOT NULL              -- AAAA-MM, para ordenar en el tablero
);

INSERT INTO dw.dim_fecha (fecha_key, fecha, dia, mes, nombre_mes, trimestre, anio, anio_mes)
SELECT to_char(d, 'YYYYMMDD')::INTEGER,
       d::DATE,
       EXTRACT(DAY     FROM d)::SMALLINT,
       EXTRACT(MONTH   FROM d)::SMALLINT,
       (ARRAY['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto',
              'Septiembre','Octubre','Noviembre','Diciembre'])[EXTRACT(MONTH FROM d)::INT],
       EXTRACT(QUARTER FROM d)::SMALLINT,
       EXTRACT(YEAR    FROM d)::SMALLINT,
       to_char(d, 'YYYY-MM')
FROM generate_series(DATE '2023-01-01', DATE '2025-12-31', INTERVAL '1 day') AS g(d);
