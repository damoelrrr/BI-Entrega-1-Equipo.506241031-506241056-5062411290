"""ETL de REFERENCIA en Python (no sustituye a PDI).
Sirve para verificar de forma independiente los conteos y totales que debe mostrar el trabajo de PDI.
Reproduce las mismas reglas: lee las fuentes originales de datos/raw/ y la copia de F3 con
inconsistencias, limpia, rechaza y carga el esquema dw.   Uso:
    python etl/referencia/etl_referencia.py "postgresql://usuario:clave@localhost:5432/retailbi_dw"
(la cadena de conexión se pasa por argumento; nunca se guarda en el repositorio)"""
import sys, os, re, json, datetime as dt
import pandas as pd, openpyxl, psycopg2
from psycopg2.extras import execute_values

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RAW, INC = os.path.join(RAIZ, 'datos', 'raw'), os.path.join(RAIZ, 'datos', 'inconsistencias')
RECH = os.path.join(RAIZ, 'datos', 'rechazos'); os.makedirs(RECH, exist_ok=True)
conn = psycopg2.connect(sys.argv[1]); cur = conn.cursor()
M = {}                                   # métricas por fuente

# ---------- F1: EMC (XLSX hoja 2.1; encabezado fila 8, datos desde la fila 9)
MESES = {m: i for i, m in enumerate(['enero','febrero','marzo','abril','mayo','junio','julio','agosto',
         'septiembre','octubre','noviembre','diciembre'], 1)}
ws = openpyxl.load_workbook(os.path.join(RAW, 'anex-EMC-ComercioMinorista-ago2026.xlsx'), read_only=True)['2.1']
filas = [r for i, r in enumerate(ws.iter_rows(values_only=True), 1) if i >= 9 and any(v is not None for v in r)]
anio, f1, nota = None, [], 0
n_mes_txt = 0
for r in filas:
    if r[1] is not None and isinstance(r[1], (int, float)): anio = int(r[1])
    mes_raw = r[2]
    mes = re.sub(r'[\s.\xa0]+', '', mes_raw).lower() if isinstance(mes_raw, str) else None
    if mes in MESES and isinstance(r[4], (int, float)):
        if mes_raw != mes_raw.strip() or mes_raw.endswith('.'): n_mes_txt += 1
        f1.append((dt.date(anio, MESES[mes], 1), anio, MESES[mes], round(r[4], 2), round(r[6], 2)))
    else: nota += 1
cur.execute('TRUNCATE dw.ctx_emc_comercio_minorista RESTART IDENTITY')
execute_values(cur, 'INSERT INTO dw.ctx_emc_comercio_minorista(fecha,anio,mes,indice_sin_vehiculos,indice_sin_combustibles_vehiculos) VALUES %s', f1)
M['F1'] = dict(leidos=len(filas), cargados=len(f1), descartados=nota, mes_con_espacios_o_punto=n_mes_txt)

# ---------- F2: Dinámica empresarial
LOC = {'Usaquen': 'Usaquén', 'Engativa': 'Engativá', 'Fontibon': 'Fontibón', 'Los Martires': 'Los Mártires',
       'Ciudad Bolivar': 'Ciudad Bolívar', 'San Cristobal': 'San Cristóbal', 'Candelaria': 'La Candelaria',
       'Sin Localidad': 'Sin localidad'}
f2 = pd.read_csv(os.path.join(RAW, '170b171a-19bb-46ca-83e8-3074fe7d74be.csv'), dtype=str, encoding='utf-8-sig')
ciiu = f2['Codigo CIIU Rev. 4 A.C']
corto = ciiu.str.fullmatch(r'\d{1,3}')
f2['ciiu'] = ciiu.where(~corto, ciiu.str.zfill(4))
sin_loc = (f2['Localidad'] == 'Sin Localidad').sum()
con_tilde = f2['Localidad'].isin([k for k in LOC if k != 'Sin Localidad']).sum()
f2['loc'] = f2['Localidad'].replace(LOC)
def ent(s): return None if pd.isna(s) else int(s)
datos = [(int(r._id), r.Periodo, int(r.Mes), r.loc, r._5, r._6, r.ciiu, r._8, ent(r._10), ent(r._11), ent(r._12))
         for r in f2.rename(columns=lambda c: c).itertuples(index=False)] if False else None
cols = ['_id','Periodo','Mes','loc','Tamano empresarial','Rama de actividad economica','ciiu',
        'Organizacion juridica','Numero de empresas vigentes','Numero de empresas creadas ano corrido',
        'Numero de empresas canceladas ano corrido']
datos = [(int(a), b, int(c), d, e, f, g, h, ent(i), ent(j), ent(k)) for a,b,c,d,e,f,g,h,i,j,k in f2[cols].itertuples(index=False)]
cur.execute('TRUNCATE dw.ctx_empresas_bogota RESTART IDENTITY')
execute_values(cur, 'INSERT INTO dw.ctx_empresas_bogota(id_fuente,periodo,mes,localidad,tamano_empresarial,rama_actividad,codigo_ciiu,organizacion_juridica,empresas_vigentes,empresas_creadas,empresas_canceladas) VALUES %s', datos, page_size=5000)
M['F2'] = dict(leidos=len(f2), cargados=len(datos), descartados=0, ciiu_rellenados=int(corto.sum()),
               sin_localidad=int(sin_loc), localidades_sin_tilde_corregidas=int(con_tilde))

# ---------- F3: ventas (copia con inconsistencias)
f3 = pd.read_csv(os.path.join(INC, 'RetailBI_ventas_sinteticas_50000_inconsistencias.csv'), dtype=str, keep_default_na=False)
M['F3'] = dict(leidos=len(f3))
n_esp = sum((f3[c] != f3[c].str.strip()).sum() for c in ('tienda', 'producto'))
for c in ('tienda', 'producto', 'categoria', 'fecha_venta'): f3[c] = f3[c].str.strip()
def parse(s):
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', s): return dt.datetime.strptime(s, '%Y-%m-%d').date(), 0
    if re.fullmatch(r'\d{2}/\d{2}/\d{4}', s): return dt.datetime.strptime(s, '%d/%m/%Y').date(), 1
    if re.fullmatch(r'\d{2}-\d{2}-\d{4}', s): return dt.datetime.strptime(s, '%m-%d-%Y').date(), 1
    return None, 0
pf = f3['fecha_venta'].map(parse); f3['fecha'] = pf.map(lambda x: x[0]); n_fecha = int(pf.map(lambda x: x[1]).sum())
for c in ('cantidad', 'precio_unitario_cop', 'costo_unitario_cop', 'descuento_cop', 'total_venta_cop'):
    f3[c] = pd.to_numeric(f3[c].replace('', pd.NA))
oblig = ['venta_id','fecha','tienda_id','producto_id','cantidad','precio_unitario_cop','costo_unitario_cop','descuento_cop','total_venta_cop']
rech_nulos = f3[f3[oblig].isna().any(axis=1)].copy(); f3 = f3.drop(rech_nulos.index)
dup = f3.duplicated('venta_id', keep='first'); rech_dup = f3[dup]; f3 = f3[~dup]
f3['venta_bruta'] = f3.cantidad * f3.precio_unitario_cop
f3['venta_neta'] = f3.venta_bruta - f3.descuento_cop
bad = f3[f3.venta_neta != f3.total_venta_cop]; f3 = f3.drop(bad.index)
pd.concat([rech_nulos.assign(motivo='nulo en campo obligatorio'), rech_dup.assign(motivo='venta_id duplicado'),
           bad.assign(motivo='total_venta_cop no cuadra')]).to_csv(os.path.join(RECH, 'f3_rechazos.csv'), index=False)

# dimensiones (Insert/Update por llave natural)
tiendas = f3[['tienda_id','tienda']].drop_duplicates('tienda_id')
LOCT = {'Usaquen': 'Usaquén', 'Engativa': 'Engativá'}
execute_values(cur, "INSERT INTO dw.dim_tienda(tienda_id,nombre_tienda,localidad) VALUES %s ON CONFLICT (tienda_id) DO UPDATE SET nombre_tienda=EXCLUDED.nombre_tienda, localidad=EXCLUDED.localidad",
    [(r.tienda_id, LOCT.get(r.tienda, r.tienda), LOCT.get(r.tienda, r.tienda)) for r in tiendas.itertuples()])
prods = f3[['producto_id','producto','categoria']].drop_duplicates('producto_id')
execute_values(cur, "INSERT INTO dw.dim_producto(producto_id,nombre_producto,categoria) VALUES %s ON CONFLICT (producto_id) DO UPDATE SET nombre_producto=EXCLUDED.nombre_producto, categoria=EXCLUDED.categoria", list(prods.itertuples(index=False, name=None)))
execute_values(cur, "INSERT INTO dw.dim_descuento(tiene_descuento,rango_descuento) VALUES %s ON CONFLICT (rango_descuento) DO NOTHING",
    [('No','Sin descuento'),('Sí','Bajo'),('Sí','Medio'),('Sí','Alto')])
cur.execute('SELECT tienda_id,tienda_key FROM dw.dim_tienda'); kt = dict(cur.fetchall())
cur.execute('SELECT producto_id,producto_key FROM dw.dim_producto'); kp = dict(cur.fetchall())
cur.execute('SELECT rango_descuento,descuento_key FROM dw.dim_descuento'); kd = dict(cur.fetchall())
def rango(r):
    if r.descuento_cop == 0: return 'Sin descuento'
    p = r.descuento_cop / r.venta_bruta
    return 'Bajo' if p <= .05 else ('Medio' if p <= .10 else 'Alto')
f3['rango'] = [rango(r) for r in f3.itertuples()]
hechos = [(int(r.fecha.strftime('%Y%m%d')), kt.get(r.tienda_id, -1), kp.get(r.producto_id, -1), kd.get(r.rango, -1),
           r.venta_id, int(r.cantidad), int(r.precio_unitario_cop), int(r.venta_bruta), int(r.descuento_cop),
           int(r.venta_neta), int(r.cantidad * r.costo_unitario_cop), int(r.venta_neta - r.cantidad * r.costo_unitario_cop))
          for r in f3.itertuples()]
cur.execute('TRUNCATE dw.fact_ventas RESTART IDENTITY')
execute_values(cur, 'INSERT INTO dw.fact_ventas(fecha_key,tienda_key,producto_key,descuento_key,venta_id,cantidad,precio_unitario,venta_bruta,descuento,venta_neta,costo_total_sim,margen_sim) VALUES %s', hechos, page_size=5000)
M['F3'].update(cargados=len(hechos), descartados=len(rech_nulos)+len(rech_dup)+len(bad),
               rechazados_por_nulos=len(rech_nulos), duplicados=len(rech_dup), total_inconsistente=len(bad),
               fechas_convertidas=n_fecha, nombres_con_espacios=int(n_esp))
conn.commit()
print(json.dumps(M, indent=1, ensure_ascii=False))
