"""Genera el diagrama del modelo físico leyendo el catálogo de la base de datos (information_schema).
Uso:  python docs/diagramas/generar_modelo_fisico.py "postgresql://usuario:clave@localhost:5432/retailbi_dw"
Requiere: psycopg2 y Graphviz (comando dot). Salida: docs/diagramas/modelo_fisico.png"""
import sys, os, subprocess, psycopg2
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modelo_fisico')
cur = psycopg2.connect(sys.argv[1]).cursor()
cur.execute("""SELECT c.table_name, c.column_name, c.data_type, c.character_maximum_length, c.ordinal_position,
  EXISTS (SELECT 1 FROM information_schema.table_constraints tc JOIN information_schema.key_column_usage k
          ON k.constraint_name=tc.constraint_name AND k.table_schema=tc.table_schema
          WHERE tc.constraint_type='PRIMARY KEY' AND tc.table_schema='dw' AND k.table_name=c.table_name AND k.column_name=c.column_name),
  EXISTS (SELECT 1 FROM information_schema.table_constraints tc JOIN information_schema.key_column_usage k
          ON k.constraint_name=tc.constraint_name AND k.table_schema=tc.table_schema
          WHERE tc.constraint_type='FOREIGN KEY' AND tc.table_schema='dw' AND k.table_name=c.table_name AND k.column_name=c.column_name)
  FROM information_schema.columns c WHERE c.table_schema='dw' ORDER BY c.table_name, c.ordinal_position""")
tablas = {}
for t, col, tipo, ln, _, pk, fk in cur.fetchall():
    tablas.setdefault(t, []).append((col, tipo + (f'({ln})' if ln else ''), pk, fk))
cur.execute("""SELECT tc.table_name, ccu.table_name, kcu.column_name FROM information_schema.table_constraints tc
  JOIN information_schema.key_column_usage kcu ON kcu.constraint_name=tc.constraint_name AND kcu.table_schema=tc.table_schema
  JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name=tc.constraint_name
  WHERE tc.constraint_type='FOREIGN KEY' AND tc.table_schema='dw'""")
fks = cur.fetchall()
def color(t): return '#E2EFDA' if t.startswith('fact') else ('#FFF2CC' if t.startswith('ctx') else '#DDEBF7')
dot = ['digraph G { rankdir=LR; graph [fontname=Helvetica, labelloc=t, label="Modelo físico RetailBI (esquema dw): estrella con fact_ventas; tablas ctx_* de contexto"]; node [shape=plaintext, fontname=Helvetica, fontsize=10]; edge [dir=both, arrowtail=crow, arrowhead=tee, color="#444444"];']
for t, cols in tablas.items():
    rows = ''.join(f'<TR><TD ALIGN="LEFT">{"PK " if pk else ("FK " if fk else "")}{c}</TD><TD ALIGN="LEFT"><FONT COLOR="#666666">{ty}</FONT></TD></TR>' for c, ty, pk, fk in cols)
    dot.append(f'{t} [label=<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="3"><TR><TD COLSPAN="2" BGCOLOR="{color(t)}"><B>{t}</B></TD></TR>{rows}</TABLE>>];')
for o, d, col in fks: dot.append(f'{o} -> {d} [label="{col}", fontsize=8];')
dot.append('}')
open(OUT + '.dot', 'w', encoding='utf-8').write('\n'.join(dot))
subprocess.run(['dot', '-Tpng', '-Gdpi=130', OUT + '.dot', '-o', OUT + '.png'], check=True)
os.remove(OUT + '.dot'); print('listo:', OUT + '.png')
