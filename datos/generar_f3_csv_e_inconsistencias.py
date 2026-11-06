"""Genera, a partir del GPKG original de F3:
  1) datos/raw/RetailBI_ventas_sinteticas_50000.csv   (mismas 50.000 filas, sin cambios)
  2) datos/inconsistencias/RetailBI_ventas_sinteticas_50000_inconsistencias.csv  (copia de prueba)
  3) datos/inconsistencias/RetailBI_ventas_sinteticas_inconsistencias_log.csv     (cada cambio)
Semilla fija: el resultado es siempre el mismo. Uso:  python datos/generar_f3_csv_e_inconsistencias.py"""
import sqlite3, csv, random, os
BASE = os.path.dirname(os.path.abspath(__file__))
con = sqlite3.connect(os.path.join(BASE, 'raw', 'RetailBI_ventas_sinteticas_50000.gpkg'))
cur = con.execute("SELECT venta_id,fecha_venta,tienda_id,tienda,producto_id,producto,categoria,cantidad,"
                  "precio_unitario_cop,costo_unitario_cop,descuento_cop,total_venta_cop FROM ventas_sinteticas ORDER BY venta_id")
cols = [d[0] for d in cur.description]; rows = [list(r) for r in cur.fetchall()]
def w(path, header, data):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        wr = csv.writer(f); wr.writerow(header); wr.writerows(data)
w(os.path.join(BASE, 'raw', 'RetailBI_ventas_sinteticas_50000.csv'), cols, rows)

random.seed(2026)
idx = {c: i for i, c in enumerate(cols)}
mod = [r[:] for r in rows]; log = []
def cambia(i, campo, nuevo):
    log.append((mod[i][0], campo, mod[i][idx[campo]], nuevo)); mod[i][idx[campo]] = nuevo
def fecha_fmt(iso, fmt):
    y, m, d = iso.split('-'); return f'{d}/{m}/{y}' if fmt == 'dd/mm' else f'{m}-{d}-{y}'
# casos documentados en la Entrega 1 (tabla 2.2)
fijos = {'V000181': ('fecha_venta', 'dd/mm'), 'V000566': ('fecha_venta', 'mm-dd'),
         'V000193': ('tienda', 'esp'), 'V000150': ('cantidad', None)}
pos = {r[0]: i for i, r in enumerate(rows)}
for v, (campo, k) in fijos.items():
    i = pos[v]
    if campo == 'fecha_venta': cambia(i, campo, fecha_fmt(rows[i][idx[campo]], k))
    elif campo == 'tienda': cambia(i, campo, rows[i][idx[campo]] + ' ')
    else: cambia(i, campo, None)
libres = [i for i in range(len(rows)) if rows[i][0] not in fijos]
random.shuffle(libres)
n_fecha, n_esp, n_nulo = 1500, 500, 100
for k, i in enumerate(libres[:n_fecha]):
    cambia(i, 'fecha_venta', fecha_fmt(rows[i][idx['fecha_venta']], 'dd/mm' if k % 2 == 0 else 'mm-dd'))
for k, i in enumerate(libres[n_fecha:n_fecha + n_esp]):
    campo = 'tienda' if k % 2 == 0 else 'producto'
    cambia(i, campo, (' ' + rows[i][idx[campo]]) if k % 4 < 2 else (rows[i][idx[campo]] + ' '))
for i in libres[n_fecha + n_esp:n_fecha + n_esp + n_nulo]:
    cambia(i, 'cantidad', None)
os.makedirs(os.path.join(BASE, 'inconsistencias'), exist_ok=True)
w(os.path.join(BASE, 'inconsistencias', 'RetailBI_ventas_sinteticas_50000_inconsistencias.csv'), cols, mod)
w(os.path.join(BASE, 'inconsistencias', 'RetailBI_ventas_sinteticas_inconsistencias_log.csv'),
  ['venta_id', 'campo', 'valor_original', 'valor_modificado'], log)
print('filas:', len(mod), '| cambios registrados:', len(log))
