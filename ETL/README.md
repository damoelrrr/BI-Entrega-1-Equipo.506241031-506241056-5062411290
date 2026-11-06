# ETL de RetailBI con Pentaho Data Integration

## Motor y versiones

- **Base de datos:** PostgreSQL 16.15, instalada localmente (Windows).
- **ETL:** Pentaho Data Integration (PDI) 9.4.0.0-343, con el driver JDBC `postgresql-42.2.23.jar` que trae PDI en `lib/`.

## Parámetros de conexión (sin contraseñas)

Todas las transformaciones usan la conexión `retailbi_dw`, definida con variables:

| Variable | Valor por defecto | Dónde se define |
|---|---|---|
| `DB_HOST` | `localhost` | Parámetro del trabajo y de cada transformación |
| `DB_PORT` | `5432` | Parámetro del trabajo y de cada transformación |
| `DB_NAME` | `retailbi_dw` | Parámetro del trabajo y de cada transformación |
| `DB_USER` | `postgres` | Parámetro del trabajo y de cada transformación |
| `DB_PASSWORD` | *(no tiene)* | Archivo `kettle.properties` de cada usuario |

La contraseña **no se guarda en el repositorio**. Cada integrante agrega esta línea en su archivo
`C:\Users\<usuario>\.kettle\kettle.properties` (en Linux o macOS, `~/.kettle/kettle.properties`):

```
DB_PASSWORD=la_contraseña_definida_al_instalar_PostgreSQL
```

Después de editar `kettle.properties` hay que cerrar y volver a abrir Spoon.

## Ubicación esperada de las fuentes

Las rutas son relativas a la carpeta de cada `.ktr`
(`${Internal.Transformation.Filename.Directory}/../..` = raíz del repositorio), así que basta con clonar el
repositorio completo. Las fuentes se leen **en su formato original**, sin modificarlas antes de PDI:

| Fuente | Archivo | Paso que la lee |
|---|---|---|
| F1 DANE EMC | `datos/raw/anex-EMC-ComercioMinorista-ago2026.xlsx` (hoja `2.1`) | `lee_f1_excel` (Microsoft Excel input) |
| F2 Dinámica empresarial | `datos/raw/170b171a-19bb-46ca-83e8-3074fe7d74be.csv` | `lee_f2_csv` (CSV file input) |
| F3 Ventas sintéticas | `datos/inconsistencias/RetailBI_ventas_sinteticas_50000_inconsistencias.csv` | `lee_f3_csv` (CSV file input) |

Las líneas de F3 rechazadas se escriben en `datos/rechazos/f3_rechazos.csv`.

## Orden de ejecución

1. Crear la base y el esquema, conectado a la base `postgres`:
   `CREATE DATABASE retailbi_dw ENCODING 'UTF8';`
2. Conectado a `retailbi_dw`, ejecutar en orden `dw/ddl/01_schema.sql` a `dw/ddl/08_ctx_empresas_bogota.sql`.
   El script `02_dim_fecha.sql` crea y pobla la dimensión de tiempo (1.096 días, de 2023-01-01 a 2025-12-31).
3. Ejecutar el trabajo `etl/trabajos/job_carga_retailbi.kjb`, desde Spoon o con Kitchen:
   ```
   Kitchen.bat /file:"<ruta_del_repo>\etl\trabajos\job_carga_retailbi.kjb" /level:Basic
   ```
   El trabajo ejecuta, en este orden:
   `t_dim_tienda` → `t_dim_producto` → `t_dim_descuento` → `t_ctx_emc` → `t_ctx_empresas` → `t_fact_ventas`.
   Primero se cargan las dimensiones y al final los hechos. Si una transformación falla, el trabajo termina en `Abortar`.
4. Verificar la carga con las consultas de `dw/conciliacion/` (`01` a `05`).

El trabajo se puede volver a ejecutar sin duplicar datos: las dimensiones usan Insert/Update por la llave de
la fuente, y las tablas `fact_ventas` y `ctx_*` se vacían (truncate) antes de cargarse.

## Resultado esperado de una carga completa

| Transformación | Leídos | Escritos | Rechazados o descartados |
|---|---|---|---|
| `t_dim_tienda` | 50.000 | 5 | 0 |
| `t_dim_producto` | 50.000 | 30 | 0 |
| `t_dim_descuento` | 4 | 4 | 0 |
| `t_ctx_emc` | 104 | 92 | 12 filas de notas |
| `t_ctx_empresas` | 39.941 | 39.941 | 0 |
| `t_fact_ventas` | 50.000 | 49.899 | 101 (cantidad vacía) |
