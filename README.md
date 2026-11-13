# RetailBI — Business Intelligence

**Proyecto académico de Inteligencia de Negocios (BI)**  
**Repositorio de trabajo:** [`damoelrrr/BI-Entrega-2-Equipo.506241031-506241056-506241129`](https://github.com/damoelrrr/BI-Entrega-2-Equipo.506241031-506241056-506241129)

RetailBI implementa una solución de Business Intelligence para una empresa minorista ficticia con cinco tiendas en Bogotá, Colombia. El proyecto integra fuentes públicas y datos sintéticos, prepara la información mediante procesos ETL de Pentaho Data Integration, almacena los datos en PostgreSQL bajo un modelo dimensional en estrella y permite consultar indicadores comerciales mediante un tablero de Power BI.

## Entregas

| Entrega | Contenido | Documento |
|---|---|---|
| 1 | Diagnóstico, estrategia y diseño del modelo dimensional | — |
| 2 | Data warehouse en PostgreSQL, ETL con PDI y tablero de Power BI | `docs/entregas/` |
| 3 | Modelo predictivo de unidades vendidas (pregunta P4 de la Entrega 1) y despliegue de sus predicciones en el DW y en el tablero | `docs/entregas/BI-Entrega-3-Equipo506241031.pdf` |

> **Alcance de los datos:** las ventas de F3 son sintéticas y se utilizan con fines académicos. Los resultados no representan ventas reales de una empresa.

## Equipo de trabajo

| Integrante | Código |
|---|---:|
| Juan David Pardo Gutierrez | 506241031 |
| Linda Valentina Quintero Quiroga | 506241056 |
| Daniel Felipe Rodríguez Angulo | 506241129 |

## Objetivo

Integrar y transformar información comercial y contextual para construir un almacén de datos que permita analizar ventas netas, unidades vendidas, descuentos, productos, categorías, tiendas y comportamiento temporal.

## Arquitectura y tecnologías

| Componente | Tecnología / herramienta |
|---|---|
| Base de datos | PostgreSQL 16.15 |
| Integración y transformación | Pentaho Data Integration (PDI) 9.4.0.0-343 |
| Conector de base de datos | PostgreSQL JDBC |
| Visualización | Power BI Desktop |
| Modelo | Esquema dimensional en estrella |

La solución se organiza en fuentes de datos, integración y transformación, almacén de datos, consumo y visualización, y gobierno/calidad de datos.

## Fuentes de información

| Código | Fuente | Uso en el proyecto |
|---|---|---|
| F1 | Encuesta Mensual de Comercio (EMC), DANE | Contexto mensual del comercio minorista. Se utiliza la hoja `2.1` del archivo Excel. |
| F2 | Datos Abiertos Bogotá — Dinámica empresarial, recurso Empresas 2026 | Contexto de empresas por periodo y localidad. |
| F3 | Ventas minoristas sintéticas RetailBI | Hechos de ventas para el periodo 2023–2025; contiene 50.000 registros en el archivo original. |

Los archivos originales se encuentran en `datos/raw/`. Las muestras están en `datos/muestras/`, los diccionarios en `datos/diccionarios/`, los datos preparados con inconsistencias en `datos/inconsistencias/` y los registros rechazados en `datos/rechazos/`. La trazabilidad y procedencia de las fuentes se documenta en [`datos/descarga.md`](datos/descarga.md).

## Modelo dimensional

El almacén utiliza la base `retailbi_dw` y el esquema `dw`.

- **Tabla de hechos:** `dw.fact_ventas`, con granularidad de una línea de venta.
- **Dimensiones:** `dw.dim_fecha`, `dw.dim_tienda`, `dw.dim_producto` y `dw.dim_descuento`.
- **Tablas contextuales:** `dw.ctx_emc_comercio_minorista` y `dw.ctx_empresas_bogota`.

Los scripts de creación se encuentran en `DW/ddl/`. Las consultas para conciliación e integridad se encuentran en `DW/conciliacion/`.

## Estructura del repositorio

```text
BI-Entrega-2-Equipo.506241031-506241056-506241129/
├── README.md
├── modelo/                  # Entrega 3: modelo predictivo
│   ├── modelo_prediccion_unidades.ipynb   # Notebook de principio a fin
│   ├── extraccion.sql       # Consulta que extrae el conjunto de datos del DW
│   └── requirements.txt     # Librerías y versiones
├── DW/
│   ├── ddl/                 # Esquema, dimensiones, hechos y pred_ventas_unidades (09)
│   └── conciliacion/        # Conteos, totales, integridad y verificación de predicciones (06)
├── ETL/
│   ├── trabajos/            # job_carga_retailbi.kjb
│   ├── transformaciones/    # Transformaciones .ktr
│   ├── referencia/          # Referencia técnica
│   └── README.md            # Configuración y ejecución del ETL
├── dashboard/
│   ├── RetailBI_tablero.pbix   # Incluye la página de predicciones (Entrega 3)
│   └── capturas/               # Capturas del tablero, incluida la página de predicciones
├── datos/
│   ├── raw/                 # Fuentes originales
│   ├── inconsistencias/     # Copia de F3 con inconsistencias de prueba
│   ├── rechazos/            # Registros rechazados durante el ETL
│   ├── muestras/
│   ├── diccionarios/
│   └── descarga.md          # Procedencia y trazabilidad
└── docs/
    ├── diagramas/           # Diagramas de arquitectura y modelo
    └── entregas/            # PDF de cada entrega
```

## Requisitos previos

1. PostgreSQL 16.x instalado y en ejecución.
2. Pentaho Data Integration (PDI) 9.4.0.0-343.
3. Java compatible con la instalación de PDI.
4. Driver JDBC de PostgreSQL disponible para PDI (el proyecto se configuró con `postgresql-42.2.23.jar`).
5. Power BI Desktop para abrir el tablero.
6. Para el modelo predictivo (Entrega 3): Python 3 con Jupyter, o Google Colab, y las librerías de `modelo/requirements.txt`.

Las rutas y los nombres de carpetas distinguen mayúsculas y minúsculas en sistemas Linux. Utiliza exactamente `DW/` y `ETL/`.

## Instalación y ejecución

### 1. Obtener el proyecto

Clona el repositorio o descarga el ZIP y conserva la estructura de carpetas:

```bash
git clone https://github.com/damoelrrr/BI-Entrega-2-Equipo.506241031-506241056-506241129.git
cd BI-Entrega-2-Equipo.506241031-506241056-506241129
```

### 2. Crear la base de datos

Desde PostgreSQL, conectado inicialmente a la base `postgres`, ejecuta:

```sql
CREATE DATABASE retailbi_dw ENCODING 'UTF8';
```

Después, conéctate a `retailbi_dw` y ejecuta los scripts SQL en el siguiente orden:

```text
DW/ddl/01_schema.sql
DW/ddl/02_dim_fecha.sql
DW/ddl/03_dim_tienda.sql
DW/ddl/04_dim_producto.sql
DW/ddl/05_dim_descuento.sql
DW/ddl/06_fact_ventas.sql
DW/ddl/07_ctx_emc_comercio_minorista.sql
DW/ddl/08_ctx_empresas_bogota.sql
DW/ddl/09_pred_ventas_unidades.sql   # Entrega 3: tabla de predicciones
```

El script `02_dim_fecha.sql` genera la dimensión de fechas desde el 1 de enero de 2023 hasta el 31 de diciembre de 2025.

### 3. Configurar la conexión de PDI

Las transformaciones utilizan la conexión `retailbi_dw` y los siguientes parámetros por defecto:

| Variable | Valor por defecto |
|---|---|
| `DB_HOST` | `localhost` |
| `DB_PORT` | `5432` |
| `DB_NAME` | `retailbi_dw` |
| `DB_USER` | `postgres` |
| `DB_PASSWORD` | Se configura localmente; no se almacena en Git. |

Configura la contraseña en el archivo local `kettle.properties`:

- Windows: `C:\Users\<usuario>\.kettle\kettle.properties`
- Linux/macOS: `~/.kettle/kettle.properties`

Agrega la propiedad:

```properties
DB_PASSWORD=TU_CONTRASENA_LOCAL
```

No publiques contraseñas ni credenciales en el repositorio. Después de modificar `kettle.properties`, reinicia Spoon.

### 4. Ejecutar el proceso ETL

Abre Spoon y ejecuta el trabajo:

```text
ETL/trabajos/job_carga_retailbi.kjb
```

También puede ejecutarse desde la consola de PDI con Kitchen:

```bat
Kitchen.bat /file:"<ruta_del_repositorio>\ETL\trabajos\job_carga_retailbi.kjb" /level:Basic
```

El trabajo coordina las transformaciones en este orden:

1. `t_dim_tienda`
2. `t_dim_producto`
3. `t_dim_descuento`
4. `t_ctx_emc`
5. `t_ctx_empresas`
6. `t_fact_ventas`

Las fuentes utilizadas por las transformaciones son:

- F1: `datos/raw/anex-EMC-ComercioMinorista-ago2026.xlsx`, hoja `2.1`.
- F2: `datos/raw/170b171a-19bb-46ca-83e8-3074fe7d74be.csv`.
- F3: `datos/inconsistencias/RetailBI_ventas_sinteticas_50000_inconsistencias.csv`.

Las líneas rechazadas de F3 se registran en `datos/rechazos/f3_rechazos.csv`. La carga documentada incorpora 49.899 registros a `fact_ventas`; 101 filas se rechazan por tener la cantidad vacía. Consulta `ETL/README.md` para los detalles de configuración, rutas y resultados esperados.

### 5. Validar la carga

Ejecuta las consultas de `DW/conciliacion/` en orden. Estos archivos permiten revisar conteos, totales, integridad referencial y preguntas de negocio:

- `01_conteo_tablas_dw.sql`
- `02_totales_fact_ventas.sql`
- `03_integridad_fact_ventas.sql`
- `04_totales_fuente_f3_duckdb.sql`
- `05_verificacion_preguntas_negocio.sql`
- `06_verificacion_predicciones.sql` (Entrega 3; ejecutar después del paso 6)

### 6. Ejecutar el modelo predictivo (Entrega 3)

El modelo responde la pregunta P4 de la Entrega 1: cuántas unidades de cada producto se venderán en cada tienda el próximo mes. Es un problema de regresión; se comparan una regresión lineal y un bosque aleatorio, entrenados con abril de 2023 a diciembre de 2024 y evaluados con los 12 meses de 2025. Se eligió la regresión lineal (MAE = 7,22 unidades por tienda, producto y mes).

1. Crea un entorno e instala las librerías:

   ```bash
   cd modelo
   python -m venv .venv
   .venv\Scripts\activate          # Windows  (Linux/macOS: source .venv/bin/activate)
   pip install -r requirements.txt
   ```

2. Asegúrate de que `retailbi_dw` está cargada (pasos 2 a 5) y de que existe la tabla `dw.pred_ventas_unidades` (`DW/ddl/09_pred_ventas_unidades.sql`).
3. Abre `modelo/modelo_prediccion_unidades.ipynb` con Jupyter (`jupyter notebook`) y ejecuta todas las celdas en orden (*Run All*). El notebook se conecta a PostgreSQL con SQLAlchemy usando los mismos parámetros de la tabla del paso 3; la contraseña se escribe localmente y no se guarda en el repositorio.
4. El notebook ejecuta la consulta de `modelo/extraccion.sql` (5.400 registros: 5 tiendas × 30 productos × 36 meses), prepara los datos, entrena y evalúa los dos algoritmos y escribe las 1.800 predicciones del modelo elegido en `dw.pred_ventas_unidades`.
5. Comprueba la carga con `DW/conciliacion/06_verificacion_predicciones.sql`: debe devolver 1.800 filas, MAE 7,22 y 0 predicciones sin dimensión.

### 7. Abrir el tablero y ver las predicciones

Abre `dashboard/RetailBI_tablero.pbix` con Power BI Desktop. Si Power BI solicita credenciales o la ubicación del servidor, configura la conexión hacia la instancia PostgreSQL local y la base `retailbi_dw`, utilizando el esquema `dw`. Actualiza los datos después de confirmar que la carga ETL y el notebook terminaron correctamente.

- Páginas 1 y 2: preguntas de negocio P0 a P3 (Entrega 2).
- Página 3, «Predicción de unidades vendidas frente a valores reales (2025)»: unidades reales frente a pronosticadas y MAE, por mes, tienda y producto, con segmentadores de tienda y categoría. Lee la tabla `dw.pred_ventas_unidades`, unida a `dim_fecha`, `dim_tienda` y `dim_producto`.

## Documentación y evidencias

- [`ETL/README.md`](ETL/README.md): parámetros, fuentes, ejecución y resultados esperados del proceso ETL.
- [`datos/descarga.md`](datos/descarga.md): procedencia y trazabilidad de las fuentes.
- `docs/diagramas/`: diagramas de arquitectura, esquema estrella y modelo físico.
- `DW/conciliacion/`: consultas SQL para validar la información cargada.
- `modelo/`: notebook, consulta de extracción y librerías del modelo predictivo.
- `docs/entregas/`: informes en PDF de cada entrega.

## Consideraciones

- La base de datos y las rutas de conexión se configuran localmente; no se incluyen contraseñas.
- Los resultados de F3 son demostrativos porque la fuente es sintética.
- Para reproducir el proceso se deben conservar las rutas relativas y la estructura de carpetas.
- La disponibilidad y actualización de las fuentes públicas depende de sus respectivos portales.


