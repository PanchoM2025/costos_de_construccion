"""
query_insumos.py — Busca a qué tareas pertenecen los insumos 101243, 101246, 101247
"""
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "Data" / "Master_FINAL.db"
INSUMOS = ("101243", "101246", "101247")

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
cur = con.cursor()

for tabla in ("insumos", "incidencias", "tareas"):
    cols = cur.execute(f"PRAGMA table_info({tabla})").fetchall()
    print(f"{tabla}: {[c['name'] for c in cols]}")

# Ver cómo están guardados los códigos en incidencias (muestra los primeros)
sample = cur.execute("SELECT cod_ins FROM incidencias LIMIT 5").fetchall()
print(f"\nEjemplos cod_ins en incidencias: {[r['cod_ins'] for r in sample]}")

# Verificar si los insumos existen en la tabla
for cod in INSUMOS:
    row = cur.execute("SELECT * FROM insumos WHERE cod_ins = ? OR CAST(cod_ins AS TEXT) = ?",
                      (cod, cod)).fetchone()
    print(f"Insumo {cod} en tabla insumos: {dict(row) if row else 'NO ENCONTRADO'}")

# Buscar en incidencias e incidencias_v2
tablas_inc = [r[0] for r in cur.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'incidencias%'").fetchall()]
print(f"\nTablas de incidencias: {tablas_inc}")

for cod in INSUMOS:
    print(f"\n── Insumo {cod} ──────────────────────────────────────")
    for tabla in tablas_inc:
        rows = cur.execute(f"""
            SELECT inc.cod_tar, t.descripcion AS nombre_tar, inc.cantidad
            FROM   [{tabla}] inc
            JOIN   tareas t ON t.cod_tar = inc.cod_tar
            WHERE  CAST(inc.cod_ins AS TEXT) = ? OR inc.cod_ins = ?
            ORDER  BY inc.cod_tar
        """, (cod, cod)).fetchall()
        if rows:
            print(f"  [{tabla}]")
            print(f"  {'Cód. Tarea':<12} {'Tarea':<55} {'Cantidad':>10}")
            for r in rows:
                print(f"  {r['cod_tar']:<12} {r['nombre_tar'][:55]:<55} {r['cantidad']:>10.4f}")
        else:
            print(f"  [{tabla}] Sin incidencias.")

con.close()
print("\nListo.")
