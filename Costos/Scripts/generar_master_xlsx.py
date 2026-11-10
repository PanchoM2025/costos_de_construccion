"""Genera Master_FAM.xlsx desde Master_FINAL.db.
Hoja Master: mismo formato jerárquico que Master_FINAL.xlsx (rubro / subrubro / tarea / insumos).
Hojas Tareas e Insumos: listados planos.
Uso: python generar_master_xlsx.py [salida.xlsx]
"""
import re
import sqlite3
import sys

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill

DB = r'C:\Dropbox\Analisis_de_costos_y_Presupuestacion\Costos\Data\Master_FINAL.db'
OUT = sys.argv[1] if len(sys.argv) > 1 else r'C:\Dropbox\Analisis_de_costos_y_Presupuestacion\Costos\Z Archivos\Master_FAM.xlsx'

C_HDR, C_RUBRO, C_SUB, C_TAR, C_ODD, C_EVEN = '0D3D6B', '1F5C99', '2E86C1', 'D6E8F5', 'FFFFFF', 'F5F9FF'
FMT_CANT = '#,##0.00##'   # como el original (#,##0.00) pero sin esconder cantidades chicas (0,002)


def fill(c):
    return PatternFill(fill_type='solid', fgColor=c)


F_BLANCA = Font(name='Arial', size=10, bold=True, color='FFFFFF')
F_TAR = Font(name='Arial', size=10, color='1F3A5C')
F_INS = Font(name='Arial', size=10, color='333333')
F_FILA = Font(name='Arial', size=10)


def clave_rubro(cod):
    """Orden natural: 1, 1.a, 1.b, 2, ..., 3.b, 3.b.1, ..., 10, 10.a"""
    return [(0, int(p)) if p.isdigit() else (1, p) for p in re.split(r'\.', cod)]


def encabezado(ws, headers, anchos):
    ws.row_dimensions[1].height = 18
    for col, (h, w) in enumerate(zip(headers, anchos), 1):
        c = ws.cell(row=1, column=col, value=h)
        c.font = F_BLANCA
        c.fill = fill(C_HDR)
        c.alignment = Alignment(horizontal='center', vertical='center')
        ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = w
    ws.freeze_panes = 'A2'


def cargar(conn):
    rubros = conn.execute("SELECT cod_rubro, designacion, es_padre, cod_padre, id_rs_ini, id_rs_fin FROM rubros").fetchall()
    padres = sorted([r for r in rubros if r[2] == 1], key=lambda r: clave_rubro(r[0]))
    subs = [r for r in rubros if r[2] != 1]
    tareas = conn.execute("SELECT cod_tar, id_tarea, id_rs, descripcion, unidad, variante, id_tarea_base, orden FROM tareas ORDER BY orden, cod_tar").fetchall()
    incid = {}
    for cod_tar, cod_ins, desc, unid, cant in conn.execute(
            """SELECT i.cod_tar, i.cod_ins, s.descripcion, COALESCE(s.unidad, i.unidad, ''), i.cantidad
               FROM incidencias i JOIN insumos s ON s.cod_ins = i.cod_ins ORDER BY i.cod_tar, i.cod_ins"""):
        incid.setdefault(cod_tar, []).append((cod_ins, desc, unid, cant))

    def sub_de(id_rs):
        for s in subs:
            if s[4] is not None and s[4] <= id_rs <= s[5]:
                return s
        return None

    def padre_de(id_rs, sub):
        if sub is not None and sub[3]:
            return next(p for p in padres if p[0] == sub[3])
        return next(p for p in padres if p[4] <= id_rs <= p[5])

    ubic = {}                                   # cod_tar -> (padre, sub|None)
    for t in tareas:
        s = sub_de(t[2])
        ubic[t[0]] = (padre_de(t[2], s), s)
    return padres, subs, tareas, incid, ubic


def hoja_master(ws, padres, subs, tareas, incid, ubic):
    headers = ['Rubro', 'Desc. Rubro', 'SubRubro', 'Desc. SubRubro', 'COD_TAR', 'Desc. Tarea', 'Unidad',
               'COD_INS', 'Desc. Insumo', 'Unidad Ins', 'Cantidad']
    encabezado(ws, headers, [8, 16.1, 10, 16.1, 10, 30.3, 10, 13, 45.5, 12, 12])
    fila = [2]

    def linea(color, alto, valores, fuente):
        r = fila[0]
        for c in range(1, 12):
            cell = ws.cell(row=r, column=c)
            cell.fill = fill(color)
            cell.number_format = FMT_CANT if c == 11 else 'General'
        for c, v in valores.items():
            cell = ws.cell(row=r, column=c, value=v)
            cell.font = fuente
        ws.row_dimensions[r].height = alto
        fila[0] += 1
        return r

    def escribir_tareas(lista):
        for t in lista:
            linea(C_TAR, 14, {5: t[0], 6: t[3], 7: t[4]}, F_TAR)
            for n, (cod_ins, desc, unid, cant) in enumerate(incid.get(t[0], [])):
                r = linea(C_ODD if n % 2 == 0 else C_EVEN, 13.1, {8: cod_ins, 9: desc, 10: unid, 11: cant}, F_INS)
                ws.cell(row=r, column=11).alignment = Alignment(horizontal='right', vertical='center')

    for p in padres:
        linea(C_RUBRO, 16.15, {1: p[0], 2: p[1]}, F_BLANCA)
        escribir_tareas([t for t in tareas if ubic[t[0]] == (p, None)])          # tareas directas del rubro
        hijos = sorted([s for s in subs if s[3] == p[0] or (s[3] is None and s[0].split('.')[0] == p[0])],
                       key=lambda s: clave_rubro(s[0]))
        for s in hijos:
            linea(C_SUB, 15, {3: s[0], 4: s[1]}, F_BLANCA)
            escribir_tareas([t for t in tareas if ubic[t[0]][1] == s])
    return fila[0] - 1


def hoja_plana(ws, headers, anchos, filas, centradas=()):
    encabezado(ws, headers, anchos)
    for n, row in enumerate(filas):
        for c, v in enumerate(row, 1):
            cell = ws.cell(row=n + 2, column=c, value=v)
            cell.font = F_FILA
            cell.fill = fill(C_EVEN if n % 2 == 0 else C_ODD)
            if c in centradas:
                cell.alignment = Alignment(horizontal='center')
    ws.auto_filter.ref = f"A1:{openpyxl.utils.get_column_letter(len(headers))}{len(filas) + 1}"


def main():
    conn = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
    padres, subs, tareas, incid, ubic = cargar(conn)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Master'
    ultima = hoja_master(ws, padres, subs, tareas, incid, ubic)

    cod_de_id = {t[1]: t[0] for t in tareas}
    orden_rubro = {p[0]: i for i, p in enumerate(padres)}
    filas_t = []
    for t in sorted(tareas, key=lambda t: (orden_rubro[ubic[t[0]][0][0]],
                                           clave_rubro(ubic[t[0]][1][0]) if ubic[t[0]][1] else [], t[7], t[0])):
        p, s = ubic[t[0]]
        filas_t.append((t[0], t[1], t[2], p[0], p[1], s[0] if s else None, s[1] if s else None, t[3], t[4],
                        t[5] or None, cod_de_id.get(t[6]) if t[6] != t[1] else None, len(incid.get(t[0], []))))
    hoja_plana(wb.create_sheet('Tareas'),
               ['COD_TAR', 'ID_Tarea', 'ID_RS', 'Rubro', 'Desc. Rubro', 'SubRubro', 'Desc. SubRubro', 'Descripción', 'Unidad',
                'Variante', 'Tarea base', 'Cant. insumos'],
               [12, 10, 8, 8, 30, 10, 35, 55, 10, 10, 12, 14], filas_t, centradas=(10, 12))

    usos = dict(conn.execute("SELECT cod_ins, COUNT(*) FROM incidencias GROUP BY cod_ins"))
    filas_i = [(c, i, d, u, usos.get(c, 0)) for c, i, d, u in
               conn.execute("SELECT cod_ins, id_insumo, descripcion, unidad FROM insumos ORDER BY cod_ins")]
    hoja_plana(wb.create_sheet('Insumos'), ['COD_INS', 'ID_Insumo', 'Descripción', 'Unidad', 'Tareas que lo usan'],
               [12, 11, 70, 10, 18], filas_i, centradas=(5,))
    wb.save(OUT)
    print(f'{OUT}\nMaster: {ultima} filas | Tareas: {len(filas_t)} | Insumos: {len(filas_i)}')


if __name__ == '__main__':
    main()
