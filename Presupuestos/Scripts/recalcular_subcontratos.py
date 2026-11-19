"""
recalcular_subcontratos.py
Recalcula los precios de los subcontratos S y E de una obra a partir de los
precios básicos de su archivo de precios, y los vuelca en ese mismo archivo.

Uso:
    python recalcular_subcontratos.py 007
    python recalcular_subcontratos.py 007 --archivo "ruta\\PU_xxx.xlsx" --factor-e 0.8
    python recalcular_subcontratos.py 007 --simular      (muestra sin escribir)
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core.obra import Obra, cargar_maestro_desde_db          # noqa: E402
from core.maestro import cargar_precios                      # noqa: E402
from core.subcontratos import (calcular_subcontratos,        # noqa: E402
                               volcar_en_archivo, FACTOR_E)


def main():
    try:
        sys.stdout.reconfigure(errors="replace")   # consola Windows (cp1252)
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("obra", help="número de obra, p.ej. 007")
    ap.add_argument("--archivo", help="archivo de precios (por defecto, el vinculado a la obra)")
    ap.add_argument("--factor-e", type=float, default=FACTOR_E,
                    help=f"proporción del subcontrato E sobre el S (por defecto {FACTOR_E})")
    ap.add_argument("--simular", action="store_true", help="mostrar el cálculo sin escribir")
    a = ap.parse_args()

    obra = Obra.cargar(a.obra)
    if a.archivo:
        ruta = Path(a.archivo)
    elif obra.archivo_precios:
        ruta = obra.carpeta_precios / obra.archivo_precios
    else:
        sys.exit("La obra no tiene archivo de precios vinculado. Usá --archivo.")
    if not ruta.exists():
        sys.exit(f"No existe el archivo de precios: {ruta}")

    maestro = cargar_maestro_desde_db(obra.carpeta_data)
    precios = cargar_precios(str(ruta))
    valores, detalle, avisos = calcular_subcontratos(
        maestro, obra.items_presupuesto, precios, a.factor_e)

    print(f"Obra {obra.numero} — {ruta.name}\n")
    for tar, cod, calc, v in detalle:
        nombre = maestro["insumos"].get(cod, {}).get("nombre", "")[:45]
        print(f"  {tar:7} {cod:7} {nombre:45} {v:>14,.2f}   ({calc})")
    for av in avisos:
        print(f"  ⚠ {av}")
    if not valores:
        print("\nNo hay subcontratos para recalcular.")
        return
    if a.simular:
        print("\n(simulación: no se escribió nada)")
        return
    try:
        act, agr = volcar_en_archivo(ruta, valores, maestro["insumos"])
    except PermissionError:
        sys.exit(f"\nNo se pudo guardar {ruta.name}: cerralo en Excel y volvé a intentar.")
    print(f"\nGuardado en {ruta}\n  cambiados: {act}   agregados: {agr}   "
          f"sin cambios: {len(valores) - act - agr}")


if __name__ == "__main__":
    main()
