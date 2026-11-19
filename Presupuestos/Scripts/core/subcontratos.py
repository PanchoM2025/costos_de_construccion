"""
subcontratos.py
Recalcula el precio de los insumos de subcontrato de las variantes S y E
a partir de los precios básicos (oficial, ayudante, equipos).

Criterio:
  - Variante S: lleva los mismos materiales que la tarea base, pero reemplaza
    la mano de obra (y los equipos que trae el subcontratista) por un insumo
    de subcontrato. Su precio = suma de precio x cantidad de los insumos de la
    tarea base que la S no tiene.
  - Variante E: subcontrato sin elaboración de mezcla en obra.
    Su precio = FACTOR_E x precio del subcontrato S.

Lo usan el botón "Recalcular subcontratos" de la ventana de la obra y el
script recalcular_subcontratos.py.
"""
from pathlib import Path

FACTOR_E = 0.80
_PREFIJOS_SUBCONTRATO = ("subcontrato", "m. de obra", "mat. y mdeo")


def _insumo_subcontrato(maestro, cod_variante, cods_base):
    """Código del insumo de subcontrato de una variante (el que no está en la
    tarea base y se llama 'Subcontrato…' / 'M. de Obra…'). None si no hay uno solo."""
    cat = maestro["insumos"]
    cands = [x["cod_ins"] for x in maestro["incidencias"].get(cod_variante, [])
             if x["cod_ins"] not in cods_base
             and cat.get(x["cod_ins"], {}).get("nombre", "").strip().lower()
                    .startswith(_PREFIJOS_SUBCONTRATO)]
    return cands[0] if len(cands) == 1 else None


def calcular_subcontratos(maestro, items_presupuesto, precios, factor_e=FACTOR_E):
    """Devuelve (valores, detalle, avisos).
    valores: {cod_insumo_subcontrato: precio}
    detalle: filas para mostrar (tarea, insumo, cálculo, valor)
    avisos:  tareas que no se pudieron calcular y por qué
    """
    inc = maestro["incidencias"]
    tareas = maestro["tareas_por_cod"]
    bases = sorted({it["cod_tar"] for it in items_presupuesto
                    if not it.get("es_rubro") and it.get("cod_tar")})
    valores, detalle, avisos = {}, [], []
    for b in bases:
        if b not in inc or b + "S" not in tareas:
            continue
        cods_base = {x["cod_ins"] for x in inc[b]}
        cods_s = {x["cod_ins"] for x in inc.get(b + "S", [])}
        sub_s = _insumo_subcontrato(maestro, b + "S", cods_base)
        if not sub_s:
            avisos.append(f"{b}S: no se encontró un único insumo de subcontrato.")
            continue
        reemplazados = [x for x in inc[b] if x["cod_ins"] not in cods_s]
        sin_precio = [x["cod_ins"] for x in reemplazados if not precios.get(x["cod_ins"])]
        if not reemplazados:
            avisos.append(f"{b}S: la tarea base no tiene mano de obra que reemplazar.")
            continue
        if sin_precio:
            avisos.append(f"{b}S: falta el precio de {', '.join(sin_precio)}. "
                          f"No se recalculó {sub_s} (ni su variante E).")
            continue
        v_s = round(sum(precios[x["cod_ins"]] * x["cantidad"] for x in reemplazados), 2)
        valores[sub_s] = v_s
        calc = " + ".join(f"{x['cod_ins']} {x['cantidad']:g}×{precios[x['cod_ins']]:,.0f}"
                          for x in reemplazados)
        detalle.append((b + "S", sub_s, calc, v_s))

        if b + "E" in tareas:
            sub_e = _insumo_subcontrato(maestro, b + "E", cods_base)
            if not sub_e:
                avisos.append(f"{b}E: no se encontró un único insumo de subcontrato.")
                continue
            v_e = round(v_s * factor_e, 2)
            valores[sub_e] = v_e
            detalle.append((b + "E", sub_e, f"{factor_e:.0%} × {v_s:,.2f}", v_e))
    return valores, detalle, avisos


def volcar_en_archivo(ruta, valores, insumos_cat):
    """Escribe los valores en la hoja 'Insumos' del archivo de precios:
    actualiza las filas existentes y agrega al final las que faltan.
    Devuelve (actualizados, agregados). Lanza PermissionError si está abierto en Excel."""
    import openpyxl
    ruta = Path(ruta)
    wb = openpyxl.load_workbook(str(ruta))
    if "Insumos" not in wb.sheetnames:
        raise ValueError(f"{ruta.name} no tiene la hoja 'Insumos'.")
    ws = wb["Insumos"]
    filas = {str(r[0].value).strip(): r for r in ws.iter_rows(min_row=2)
             if r[0].value is not None}
    act = agr = 0
    for cod, v in sorted(valores.items()):
        if cod in filas:
            if filas[cod][3].value != v:
                filas[cod][3].value = v
                act += 1
        else:
            ins = insumos_cat.get(cod, {})
            ws.append([cod, ins.get("nombre", ""), ins.get("unidad", ""), v])
            agr += 1
    wb.save(str(ruta))
    return act, agr
