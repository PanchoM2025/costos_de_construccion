"""
etapas.py
Seguimiento de la ejecución de una obra por etapas (Etapas XX).

Archivos en Obras/ObraNNN/data/:
  ejecucion.json  — Original congelado (la versión obraNNN.json contratada, con sus
                    precios unitarios calculados al momento de definirlo) + estado
                    de cada tarea: "a_realizar" | "en_curso" | "realizada".
  etapaXX.json    — Etapa XX: tareas ejecutadas en esa etapa, con la cantidad de
                    la etapa, el precio unitario y los precios de insumos usados.

Una tarea puede repartirse en varias etapas (por cantidad). Pasa a "realizada"
cuando se la marca como finalizada en una etapa.

Al cierre se suman todas las etapas y se comparan con el Original:
  diferencia     = total ejecutado − total original
  efecto cantidad = (cant. ejecutada − cant. original) × PU original
  efecto precio   = total ejecutado − cant. ejecutada × PU original
"""
import json
import re
from datetime import date, datetime
from pathlib import Path

ESTADOS = ("a_realizar", "en_curso", "realizada")
ESTADO_TXT = {"a_realizar": "A realizar", "en_curso": "En curso", "realizada": "Realizada"}

_RE_ETAPA = re.compile(r"etapa(\d+)\.json$")
_RE_VARIANTE = re.compile(r"etapa(\d+)_variante(\d+)\.json$")


# ─────────────────────────────────────────────────────────────────────────────
#  Precio unitario de una tarea (mismo cálculo que la pestaña Presupuesto)
# ─────────────────────────────────────────────────────────────────────────────

def cod_incidencias(cod_tar: str, subcontrato: str) -> str:
    sub = (subcontrato or "").strip().upper()
    return cod_tar + sub if (cod_tar and sub) else cod_tar


def calcular_pu(cod_tar: str, subcontrato: str, incidencias: dict,
                precios: dict) -> tuple[float, list]:
    """(precio unitario, [insumos sin precio])."""
    pu, falt = 0.0, []
    for inc in incidencias.get(cod_incidencias(cod_tar, subcontrato), []):
        p = precios.get(inc["cod_ins"]) or 0.0
        if not p:
            falt.append(inc["cod_ins"])
        pu += p * inc["cantidad"]
    return pu, falt


def insumos_de(cod_tar: str, subcontrato: str, incidencias: dict) -> list:
    return [inc["cod_ins"] for inc in
            incidencias.get(cod_incidencias(cod_tar, subcontrato), [])]


# ─────────────────────────────────────────────────────────────────────────────
#  Ejecución (Original + estados)
# ─────────────────────────────────────────────────────────────────────────────

def ruta_ejecucion(carpeta_data: Path) -> Path:
    return Path(carpeta_data) / "ejecucion.json"


def cargar_ejecucion(carpeta_data: Path) -> dict | None:
    r = ruta_ejecucion(carpeta_data)
    if not r.exists():
        return None
    with open(r, encoding="utf-8") as f:
        return json.load(f)


def guardar_ejecucion(carpeta_data: Path, ejec: dict):
    with open(ruta_ejecucion(carpeta_data), "w", encoding="utf-8") as f:
        json.dump(ejec, f, ensure_ascii=False, indent=2)


def definir_original(carpeta_data: Path, ruta_version: Path, incidencias: dict,
                     catalogo: dict | None = None) -> dict:
    """Congela la versión obraNNN.json elegida como Original de la ejecución.
    Calcula y guarda el precio unitario de cada tarea con los precios de esa versión,
    y la lista de insumos (incidencia y precio) para poder calcular saldos."""
    ruta_version = Path(ruta_version)
    with open(ruta_version, encoding="utf-8") as f:
        d = json.load(f)
    precios = d.get("precios", {}) or {}
    items, rubros = [], {}
    claves = set()
    rubro_actual = ""
    for idx, it in enumerate(d.get("items_presupuesto", []) or []):
        if it.get("es_rubro"):
            rubro_actual = it.get("rubro", "")
            rubros[rubro_actual] = it.get("descripcion", "")
            continue
        rub = it.get("rubro", "") or rubro_actual
        clave = f"{rub}.{it.get('item', '')}"
        if not it.get("item") or clave in claves:
            clave = f"#{idx}"
        claves.add(clave)
        cod, sub = it.get("cod_tar", ""), it.get("subcontrato", "") or ""
        if it.get("precio_manual"):
            pu, falt = float(it["precio_manual"]), []
        else:
            pu, falt = calcular_pu(cod, sub, incidencias, precios)
        items.append({
            "clave": clave, "rubro": rub, "item": it.get("item", ""),
            "descripcion": it.get("descripcion", ""), "unidad": it.get("unidad", ""),
            "cod_tar": cod, "subcontrato": sub,
            "cantidad": float(it.get("cantidad") or 0.0),
            "pu": pu, "precio_manual": bool(it.get("precio_manual")),
            "sin_precio": falt,
        })
        items[-1]["insumos"] = insumos_original(items[-1], incidencias, precios, catalogo)
    ejec = {
        "original": {
            "archivo": ruta_version.name,
            "version": d.get("version", 0),
            "archivo_precios": d.get("archivo_precios", ""),
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "rubros": rubros,
            "items": items,
            "precios": precios,
        },
        "estados": {it["clave"]: "a_realizar" for it in items},
    }
    guardar_ejecucion(carpeta_data, ejec)
    return ejec


def cambios_precios_original(ejec: dict, precios: dict, incidencias: dict,
                             catalogo: dict | None = None) -> list:
    """Insumos de las tareas del Original cuyo precio difiere del actual de la obra:
    [{cod_ins, nombre, unidad, antes, nuevo}] (antes = 0 → no tenía precio).
    Las tareas con precio manual no se tocan."""
    o = ejec["original"]
    cat = catalogo or {}
    vistos, res = set(), []
    for it in o["items"]:
        if it.get("precio_manual"):
            continue
        for x in insumos_original(it, incidencias, o.get("precios") or {}, cat):
            c = x["cod_ins"]
            nuevo = float(precios.get(c) or 0.0)
            if c in vistos or not nuevo or abs(nuevo - float(x["precio"] or 0.0)) < 1e-9:
                continue
            vistos.add(c)
            res.append({"cod_ins": c, "nombre": x.get("nombre") or cat.get(c, {}).get("nombre", ""),
                        "unidad": x.get("unidad", ""), "antes": float(x["precio"] or 0.0),
                        "nuevo": nuevo})
    return sorted(res, key=lambda r: r["cod_ins"])


def actualizar_precios_original(carpeta_data: Path, ejec: dict, nuevos: dict,
                                incidencias: dict, catalogo: dict | None = None) -> Path:
    """Aplica `nuevos` {cod_ins: precio} a los insumos del Original y recalcula el PU
    de cada tarea. No toca estados ni etapas. Deja copia previa de ejecucion.json."""
    ruta = ruta_ejecucion(carpeta_data)
    bak = ruta.with_name(f"ejecucion_antes_precios_{datetime.now():%Y-%m-%d_%H%M}.json")
    bak.write_bytes(ruta.read_bytes())
    o = ejec["original"]
    for it in o["items"]:
        if it.get("precio_manual") or not it.get("cod_tar"):
            continue
        # Congela la lista de insumos (con las incidencias de hoy si no estaba congelada)
        it["insumos"] = insumos_original(it, incidencias, o.get("precios") or {}, catalogo)
        for x in it["insumos"]:
            if x["cod_ins"] in nuevos:
                x["precio"] = float(nuevos[x["cod_ins"]])
        it["pu"] = sum(x["incid"] * x["precio"] for x in it["insumos"])
        it["sin_precio"] = [x["cod_ins"] for x in it["insumos"] if not x["precio"]]
    o.setdefault("precios", {}).update({c: float(v) for c, v in nuevos.items()})
    o["precios_actualizados"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    guardar_ejecucion(carpeta_data, ejec)
    return bak


def insumos_original(it: dict, incidencias: dict, precios: dict,
                     catalogo: dict | None = None) -> list:
    """Insumos previstos de una tarea del Original: [{cod_ins, nombre, unidad, incid,
    precio}]. Si el Original los congeló se usan esos; si no (Originales definidos
    antes), se toman de las incidencias actuales de la obra."""
    if "insumos" in it:
        return it["insumos"]
    if it.get("precio_manual") or not it.get("cod_tar"):
        return []
    cat = catalogo or {}
    return [{"cod_ins": x["cod_ins"], "nombre": cat.get(x["cod_ins"], {}).get("nombre", ""),
             "unidad": x.get("unidad") or cat.get(x["cod_ins"], {}).get("unidad", ""),
             "incid": float(x["cantidad"] or 0.0),
             "precio": float(precios.get(x["cod_ins"]) or 0.0)}
            for x in incidencias.get(cod_incidencias(it["cod_tar"], it.get("subcontrato", "")), [])]


def consumo_insumos(carpeta_data: Path, incidencias: dict) -> dict:
    """{clave: {cod_ins: {"q", "pesos", "unidad", "nombre"}}}: lo usado de cada insumo
    en todas las etapas (incidencia de la etapa × cantidad de la tarea)."""
    res = {}
    for e in listar_etapas(carpeta_data):
        prec = e.get("precios") or {}
        for i in e.get("items", []):
            if "insumos" in i:
                lista = [(x["cod_ins"], x["incid"], x["precio"], x.get("unidad", ""),
                          x.get("nombre", "")) for x in i["insumos"]]
            elif i.get("cod_tar"):   # etapa guardada sin lista: según el análisis
                lista = [(x["cod_ins"], x["cantidad"], float(prec.get(x["cod_ins"]) or 0.0),
                          x.get("unidad", ""), "")
                         for x in incidencias.get(cod_incidencias(i["cod_tar"],
                                                                  i.get("subcontrato", "")), [])]
            else:
                lista = []
            d = res.setdefault(i["clave"], {})
            for c, inc, p, uni, nom in lista:
                q = inc * i["cantidad"]
                a = d.setdefault(c, {"q": 0.0, "pesos": 0.0, "unidad": uni, "nombre": nom})
                a["q"] += q
                a["pesos"] += q * p
                if nom and not a["nombre"]:
                    a["nombre"] = nom
    return res


def saldo_insumos(ejec: dict, it: dict, incidencias: dict, consumo: dict,
                  catalogo: dict | None = None) -> list:
    """Por insumo de la tarea: previsto en el Original, ejecutado en las etapas y saldo
    (previsto − ejecutado; negativo = se usó de más o no estaba previsto)."""
    cat = catalogo or {}
    orig = insumos_original(it, incidencias, ejec["original"].get("precios") or {}, cat)
    usado = consumo.get(it["clave"], {})
    filas = []
    for x in orig:
        q_o = x["incid"] * it["cantidad"]
        u = usado.get(x["cod_ins"], {})
        filas.append({"cod_ins": x["cod_ins"],
                      "nombre": x.get("nombre") or u.get("nombre")
                                or cat.get(x["cod_ins"], {}).get("nombre", ""),
                      "unidad": x.get("unidad") or u.get("unidad", ""),
                      "q_orig": q_o, "precio": x["precio"],
                      "q_ejec": u.get("q", 0.0), "pesos_ejec": u.get("pesos", 0.0),
                      "saldo": q_o - u.get("q", 0.0), "previsto": True})
    previstos = {x["cod_ins"] for x in orig}
    for c, u in usado.items():
        if c in previstos or not u["q"]:
            continue
        filas.append({"cod_ins": c, "nombre": u.get("nombre") or cat.get(c, {}).get("nombre", ""),
                      "unidad": u.get("unidad", ""), "q_orig": 0.0, "precio": 0.0,
                      "q_ejec": u["q"], "pesos_ejec": u["pesos"], "saldo": -u["q"],
                      "previsto": False})
    return filas


def estado(ejec: dict, clave: str) -> str:
    return ejec.get("estados", {}).get(clave, "a_realizar")


def cambiar_estado(carpeta_data: Path, ejec: dict, claves: list, nuevo: str):
    if nuevo not in ESTADOS:
        raise ValueError(nuevo)
    for c in claves:
        ejec.setdefault("estados", {})[c] = nuevo
    guardar_ejecucion(carpeta_data, ejec)


# ─────────────────────────────────────────────────────────────────────────────
#  Etapas XX
# ─────────────────────────────────────────────────────────────────────────────

def listar_etapas(carpeta_data: Path) -> list[dict]:
    res = []
    for p in sorted(Path(carpeta_data).glob("etapa*.json")):
        m = _RE_ETAPA.search(p.name)
        if not m:
            continue
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        d["_ruta"] = str(p)
        res.append(d)
    res.sort(key=lambda e: e.get("numero", 0))
    return res


def proximo_numero(carpeta_data: Path) -> int:
    nums = [e.get("numero", 0) for e in listar_etapas(carpeta_data)]
    return max(nums, default=0) + 1


def ruta_etapa(carpeta_data: Path, numero: int) -> Path:
    return Path(carpeta_data) / f"etapa{numero:02d}.json"


# ─────────────────────────────────────────────────────────────────────────────
#  Variantes de una etapa (etapaNN_varianteMM.json)
#  Son alternativas para comparar: no suman al ejecutado, no cambian estados ni
#  saldos, y listar_etapas() no las incluye.
# ─────────────────────────────────────────────────────────────────────────────

VARIANTE_TXT = {"": "Personal propio", "S": "Subcontrato de MdeO",
                "E": "Hormigón elaborado", "T": "Subcontrato total"}


def nombre_etapa(etapa: dict) -> str:
    """'Etapa 02' o 'Etapa 02 Variante 01'."""
    txt = f"Etapa {etapa['numero']:02d}"
    return txt + (f" Variante {etapa['variante']:02d}" if etapa.get("variante") else "")


def ruta_variante(carpeta_data: Path, numero: int, variante: int) -> Path:
    return Path(carpeta_data) / f"etapa{numero:02d}_variante{variante:02d}.json"


def listar_variantes(carpeta_data: Path, numero: int) -> list[dict]:
    res = []
    for p in Path(carpeta_data).glob(f"etapa{numero:02d}_variante*.json"):
        if not _RE_VARIANTE.search(p.name):
            continue
        with open(p, encoding="utf-8") as f:
            res.append(json.load(f))
    return sorted(res, key=lambda v: v.get("variante", 0))


def guardar_variante(carpeta_data: Path, etapa: dict, variante: int | None = None) -> int:
    """Guarda la etapa como variante (None = la próxima libre) y devuelve su número.
    No toca la etapa real, los estados ni ejecucion.json."""
    numero = etapa["numero"]
    if variante is None:
        variante = max((v.get("variante", 0) for v in listar_variantes(carpeta_data, numero)),
                       default=0) + 1
    d = {k: v for k, v in etapa.items() if not k.startswith("_")}
    d["variante"] = variante
    d["total"] = sum(i["cantidad"] * i["pu"] for i in d["items"])
    d["guardado"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(ruta_variante(carpeta_data, numero, variante), "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    return variante


def eliminar_variante(carpeta_data: Path, numero: int, variante: int):
    ruta = ruta_variante(carpeta_data, numero, variante)
    if ruta.exists():
        ruta.unlink()


def variantes_tarea(cod_tar: str, incidencias: dict) -> list:
    """Variantes que se pueden elegir: S, E y T en hormigón (las tareas que tienen E);
    solo S en las demás. Incluye '' (personal propio) para poder volver."""
    letras = ("S", "E", "T") if f"{cod_tar}E" in incidencias else ("S",)
    return [v for v in ("",) + letras if cod_incidencias(cod_tar, v) in incidencias]


def cambiar_variante(item: dict, it_orig: dict, variante: str, incidencias: dict,
                     precios: dict, catalogo: dict | None = None):
    """Pasa la tarea a otra variante con los insumos de su análisis. Conserva los precios
    cambiados a mano de los insumos que siguen; el PU vuelve a salir de los insumos."""
    previos = {x["cod_ins"]: x for x in item.get("insumos") or []}
    nuevos = armar_insumos(item["cod_tar"], variante, incidencias, precios, catalogo)
    for x in nuevos:
        p = previos.get(x["cod_ins"])
        if p and p.get("mod_precio"):
            x["precio"], x["mod_precio"] = p["precio"], True
    item["subcontrato"] = variante
    item["insumos"] = nuevos
    item["pu_manual"] = None
    recalcular_item(item, it_orig)


def variante_cambiada(item: dict, it_orig: dict) -> bool:
    """True si la tarea usa una variante distinta de la del Original."""
    return ((item.get("subcontrato") or "").strip().upper()
            != (it_orig.get("subcontrato") or "").strip().upper())


# ─────────────────────────────────────────────────────────────────────────────
#  Adicionales (tareas que no estaban en el Original)
#  Clave "A01", "A02"… Se registran en ejecucion.json["adicionales"] al guardar la
#  primera etapa que las usa, y pueden seguir en etapas siguientes.
# ─────────────────────────────────────────────────────────────────────────────

def es_adicional(clave: str) -> bool:
    return str(clave).startswith("A")


def adicionales(ejec: dict) -> list:
    return ejec.setdefault("adicionales", [])


def registro(ejec: dict) -> dict:
    """{clave: tarea} de las tareas del Original y de las adicionales registradas."""
    reg = {i["clave"]: i for i in ejec["original"]["items"]}
    reg.update({a["clave"]: a for a in adicionales(ejec)})
    return reg


def nueva_clave_adicional(ejec: dict, otras: list = ()) -> str:
    nums = [int(c[1:]) for c in [a["clave"] for a in adicionales(ejec)] + list(otras)
            if es_adicional(c) and c[1:].isdigit()]
    return f"A{max(nums, default=0) + 1:02d}"


def nuevo_adicional(clave: str, descripcion: str, unidad: str, rubro: str,
                    cod_tar: str = "", pu_manual: float | None = None) -> dict:
    """Ficha de una tarea adicional (cantidad y PU del Original = 0)."""
    return {
        "clave": clave, "rubro": rubro, "item": clave, "descripcion": descripcion,
        "unidad": unidad, "cod_tar": cod_tar, "subcontrato": "", "cantidad": 0.0,
        "pu": float(pu_manual or 0.0), "precio_manual": not cod_tar,
        "sin_precio": [], "adicional": True,
    }


def _registrar_adicionales(ejec: dict, items: list):
    reg = {a["clave"]: a for a in adicionales(ejec)}
    for i in items:
        if not es_adicional(i["clave"]):
            continue
        a = reg.get(i["clave"])
        if a is None:
            a = nuevo_adicional(i["clave"], i["descripcion"], i["unidad"], i["rubro"],
                                i["cod_tar"], i.get("pu_manual"))
            adicionales(ejec).append(a)
            reg[a["clave"]] = a
        else:
            a.update(descripcion=i["descripcion"], unidad=i["unidad"], rubro=i["rubro"])


def _finalizadas_en_otras(carpeta_data: Path, numero: int) -> set:
    """Claves que alguna etapa distinta de `numero` da por finalizadas."""
    return {i["clave"] for e in listar_etapas(carpeta_data) if e.get("numero") != numero
            for i in e.get("items", []) if i.get("finaliza")}


def _depurar_adicionales(carpeta_data: Path, ejec: dict):
    """Saca del registro las adicionales que ya no aparecen en ninguna etapa."""
    usadas = {i["clave"] for e in listar_etapas(carpeta_data) for i in e.get("items", [])}
    ejec["adicionales"] = [a for a in adicionales(ejec) if a["clave"] in usadas]
    for c in list(ejec.get("estados", {})):
        if es_adicional(c) and c not in usadas:
            del ejec["estados"][c]


def guardar_etapa(carpeta_data: Path, ejec: dict, etapa: dict):
    """etapa = {numero, nombre, fecha, archivo_precios, precios, items:[{clave, cantidad,
    pu, pu_manual, finaliza, ...}]}. Las tareas con finaliza=True pasan a 'realizada';
    las que se finalizaban en un guardado anterior de esta misma etapa y ya no, vuelven
    a 'en_curso'. Las adicionales nuevas quedan registradas en ejecucion.json."""
    ruta = ruta_etapa(carpeta_data, etapa["numero"])
    antes = set()
    if ruta.exists():
        with open(ruta, encoding="utf-8") as f:
            antes = {i["clave"] for i in json.load(f).get("items", []) if i.get("finaliza")}
    ahora = {i["clave"] for i in etapa["items"] if i.get("finaliza")}
    etapa = {k: v for k, v in etapa.items() if not k.startswith("_")}
    etapa["total"] = sum(i["cantidad"] * i["pu"] for i in etapa["items"])
    etapa["guardado"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(etapa, f, ensure_ascii=False, indent=2)
    for c in antes - ahora - _finalizadas_en_otras(carpeta_data, etapa["numero"]):
        if estado(ejec, c) == "realizada":
            ejec["estados"][c] = "en_curso"
    for c in ahora:
        ejec.setdefault("estados", {})[c] = "realizada"
    for i in etapa["items"]:
        if es_adicional(i["clave"]) and i["clave"] not in ahora:
            ejec.setdefault("estados", {})[i["clave"]] = "en_curso" \
                if estado(ejec, i["clave"]) == "a_realizar" else estado(ejec, i["clave"])
    _registrar_adicionales(ejec, etapa["items"])
    _depurar_adicionales(carpeta_data, ejec)
    guardar_ejecucion(carpeta_data, ejec)


def eliminar_etapa(carpeta_data: Path, ejec: dict, numero: int):
    """Borra la etapa. Las tareas que esa etapa finalizaba vuelven a 'en_curso'."""
    ruta = ruta_etapa(carpeta_data, numero)
    if not ruta.exists():
        return
    with open(ruta, encoding="utf-8") as f:
        fin = {i["clave"] for i in json.load(f).get("items", []) if i.get("finaliza")}
    ruta.unlink()
    for c in fin - _finalizadas_en_otras(carpeta_data, numero):
        if estado(ejec, c) == "realizada":
            ejec["estados"][c] = "en_curso"
    _depurar_adicionales(carpeta_data, ejec)
    guardar_ejecucion(carpeta_data, ejec)


def acumulado(carpeta_data: Path, excluir: int | None = None) -> dict:
    """{clave: {"cantidad": suma, "total": suma}} de todas las etapas
    (opcionalmente sin contar la etapa `excluir`)."""
    acc = {}
    for e in listar_etapas(carpeta_data):
        if excluir is not None and e.get("numero") == excluir:
            continue
        for i in e.get("items", []):
            a = acc.setdefault(i["clave"], {"cantidad": 0.0, "total": 0.0})
            if not i.get("solo_insumos"):     # las filas "solo insumos" no suman cantidad
                a["cantidad"] += i["cantidad"]
            a["total"] += i["cantidad"] * i["pu"]
    return acc


def nueva_etapa(carpeta_data: Path, ejec: dict, incidencias: dict, precios: dict,
                archivo_precios: str = "", catalogo: dict | None = None) -> dict:
    """Arma (sin guardar) una etapa nueva con las tareas 'en_curso'.
    - Si a la tarea le queda cantidad: cantidad propuesta = saldo, con todos sus insumos.
    - Si la cantidad ya está completa pero faltan insumos del Original: fila "solo
      insumos" con los que faltan (no suma cantidad a la tarea)."""
    acc = acumulado(carpeta_data)
    cons = None
    items = []
    for it in ejec["original"]["items"]:
        if estado(ejec, it["clave"]) != "en_curso":
            continue
        saldo = max(it["cantidad"] - acc.get(it["clave"], {}).get("cantidad", 0.0), 0.0)
        if saldo > 1e-9 or not it["cantidad"]:
            items.append(item_etapa(it, saldo, incidencias, precios, catalogo=catalogo))
            continue
        if cons is None:
            cons = consumo_insumos(carpeta_data, incidencias)
        pend = [f for f in saldo_insumos(ejec, it, incidencias, cons, catalogo)
                if f["previsto"] and f["saldo"] > 1e-9]
        if pend:
            items.append(item_pendientes(it, pend, incidencias, precios, catalogo))
    for a in adicionales(ejec):   # adicionales en curso: sin cantidad prevista
        if estado(ejec, a["clave"]) == "en_curso":
            items.append(item_etapa(a, 0.0, incidencias, precios, catalogo=catalogo))
    return {
        "numero": proximo_numero(carpeta_data),
        "nombre": "",
        "fecha": date.today().isoformat(),
        "archivo_precios": archivo_precios,
        "precios": {},
        "items": items,
    }


def item_etapa(it_orig: dict, cantidad: float, incidencias: dict, precios: dict,
               pu_manual: float | None = None, finaliza: bool = False,
               catalogo: dict | None = None) -> dict:
    """Tarea de una etapa. Lleva su propia lista de insumos ("insumos"), que se puede
    modificar en la etapa (incidencia y precio de cada uno) sin tocar el análisis."""
    item = {
        "clave": it_orig["clave"], "rubro": it_orig["rubro"], "item": it_orig["item"],
        "descripcion": it_orig["descripcion"], "unidad": it_orig["unidad"],
        "cod_tar": it_orig["cod_tar"], "subcontrato": it_orig["subcontrato"],
        "cantidad": float(cantidad), "pu": 0.0,
        "pu_manual": float(pu_manual) if pu_manual else None,
        "finaliza": bool(finaliza), "sin_precio": [],
        "adicional": es_adicional(it_orig["clave"]),
        "insumos": [] if it_orig.get("precio_manual") else
                   armar_insumos(it_orig["cod_tar"], it_orig["subcontrato"],
                                 incidencias, precios, catalogo),
    }
    recalcular_item(item, it_orig)
    return item


# ── Insumos de una tarea dentro de la etapa ──────────────────────────────────
#  Cada insumo: cod_ins, nombre, unidad,
#    incid_base / precio_base  → lo que sale del análisis y del archivo de precios
#    incid / precio            → lo que se usa en la etapa (editable)
#    mod_incid / mod_precio    → True si se cambió a mano en la etapa

def armar_insumos(cod_tar: str, subcontrato: str, incidencias: dict, precios: dict,
                  catalogo: dict | None = None) -> list:
    cat = catalogo or {}
    res = []
    for inc in incidencias.get(cod_incidencias(cod_tar, subcontrato), []):
        c = inc["cod_ins"]
        p = float(precios.get(c) or 0.0)
        q = float(inc["cantidad"] or 0.0)
        res.append({
            "cod_ins": c, "nombre": cat.get(c, {}).get("nombre", ""),
            "unidad": inc.get("unidad") or cat.get(c, {}).get("unidad", ""),
            "incid_base": q, "incid": q, "precio_base": p, "precio": p,
            "mod_incid": False, "mod_precio": False,
        })
    return res


def pu_insumos(insumos: list) -> tuple[float, list]:
    """(precio unitario, [insumos sin precio]) a partir de la lista de la etapa."""
    return (sum(x["incid"] * x["precio"] for x in insumos),
            [x["cod_ins"] for x in insumos if not x["precio"]])


def recalcular_item(item: dict, it_orig: dict):
    """Recalcula pu y sin_precio. Orden: PU manual > PU del Original (tareas sin
    insumos) > suma de los insumos de la etapa."""
    if item.get("pu_manual"):
        item["pu"], item["sin_precio"] = float(item["pu_manual"]), []
    elif it_orig.get("precio_manual") and not item.get("insumos"):
        item["pu"], item["sin_precio"] = float(it_orig.get("pu") or 0.0), []
    else:
        item["pu"], item["sin_precio"] = pu_insumos(item.get("insumos") or [])


def aplicar_precios(item: dict, precios: dict):
    """Nuevo archivo de precios: actualiza los insumos cuyo precio no se tocó a mano."""
    for x in item.get("insumos") or []:
        p = float(precios.get(x["cod_ins"]) or 0.0)
        x["precio_base"] = p
        if not x.get("mod_precio"):
            x["precio"] = p


def asegurar_insumos(item: dict, it_orig: dict, incidencias: dict, precios: dict,
                     catalogo: dict | None = None):
    """Etapas guardadas antes de que existiera la lista de insumos: la arma."""
    if "insumos" in item:
        return
    item["insumos"] = [] if it_orig.get("precio_manual") else armar_insumos(
        item["cod_tar"], item["subcontrato"], incidencias, precios, catalogo)
    recalcular_item(item, it_orig)


def nuevo_insumo(cod_ins: str, catalogo: dict, precios: dict, incid: float,
                 precio: float | None = None) -> dict:
    """Insumo agregado en la etapa (no está en el análisis de la tarea)."""
    c = (catalogo or {}).get(cod_ins, {})
    p_base = float(precios.get(cod_ins) or 0.0)
    p = p_base if precio is None else float(precio)
    return {
        "cod_ins": cod_ins, "nombre": c.get("nombre", ""), "unidad": c.get("unidad", ""),
        "incid_base": 0.0, "incid": float(incid), "precio_base": p_base, "precio": p,
        "mod_incid": True, "mod_precio": abs(p - p_base) > 1e-9, "agregado": True,
    }


def restaurar_insumo(x: dict):
    x.update(incid=x["incid_base"], precio=x["precio_base"],
             mod_incid=False, mod_precio=False)


def item_pendientes(it_orig: dict, pend: list, incidencias: dict, precios: dict,
                    catalogo: dict | None = None) -> dict:
    """Fila "solo insumos": completa los insumos que faltan de una tarea cuya cantidad
    ya se ejecutó. Usa la cantidad del Original como referencia (incidencia = saldo del
    insumo / cantidad) y NO suma cantidad a la tarea."""
    q = it_orig["cantidad"]
    i = item_etapa(it_orig, q, incidencias, precios, catalogo=catalogo)
    por_cod = {f["cod_ins"]: f for f in pend}
    nuevos = []
    for x in i["insumos"]:
        f = por_cod.pop(x["cod_ins"], None)
        if f:
            x["incid"] = x["incid_base"] = f["saldo"] / q
            nuevos.append(x)
    for f in por_cod.values():        # previsto en el Original pero ya no en el análisis
        x = nuevo_insumo(f["cod_ins"], catalogo, precios, f["saldo"] / q)
        x.update(incid_base=x["incid"], mod_incid=False, agregado=False)
        nuevos.append(x)
    i["insumos"] = nuevos
    i["solo_insumos"] = True
    recalcular_item(i, it_orig)
    return i


def precios_usados(items: list, incidencias: dict, precios: dict) -> dict:
    """Solo los precios (del archivo, no los cambiados a mano) de los insumos que
    usan las tareas de la etapa."""
    res = {}
    for i in items:
        if "insumos" in i:
            for x in i["insumos"]:
                if x.get("precio_base"):
                    res[x["cod_ins"]] = x["precio_base"]
            continue
        for c in insumos_de(i["cod_tar"], i["subcontrato"], incidencias):
            if precios.get(c):
                res[c] = precios[c]
    return res


# ─────────────────────────────────────────────────────────────────────────────
#  Cierre: total de las etapas vs Original
# ─────────────────────────────────────────────────────────────────────────────

def comparar(carpeta_data: Path, ejec: dict, solo_con_avance: bool = False) -> dict:
    """solo_con_avance: deja afuera las tareas 'A realizar' sin nada ejecutado
    (útil mientras la obra está en marcha)."""
    etapas = listar_etapas(carpeta_data)
    por_etapa = {}   # clave -> {numero: cantidad}
    for e in etapas:
        for i in e.get("items", []):
            d = por_etapa.setdefault(i["clave"], {})
            if not i.get("solo_insumos"):
                d[e["numero"]] = d.get(e["numero"], 0.0) + i["cantidad"]
    acc = acumulado(carpeta_data)
    filas, rubros = [], {}
    tot = dict(orig=0.0, ejec=0.0, dif=0.0, ef_cant=0.0, ef_prec=0.0)
    for it in ejec["original"]["items"]:
        a = acc.get(it["clave"], {"cantidad": 0.0, "total": 0.0})
        if (solo_con_avance and not a["cantidad"]
                and estado(ejec, it["clave"]) == "a_realizar"):
            continue
        t_orig = it["cantidad"] * it["pu"]
        q_ej, t_ej = a["cantidad"], a["total"]
        f = {
            **{k: it[k] for k in ("clave", "rubro", "item", "descripcion", "unidad")},
            "estado": estado(ejec, it["clave"]),
            "cant_orig": it["cantidad"], "pu_orig": it["pu"], "total_orig": t_orig,
            "cant_ejec": q_ej, "pu_ejec": (t_ej / q_ej) if q_ej else 0.0,
            "total_ejec": t_ej, "dif": t_ej - t_orig,
            "ef_cant": (q_ej - it["cantidad"]) * it["pu"],
            "ef_prec": t_ej - q_ej * it["pu"],
            "por_etapa": por_etapa.get(it["clave"], {}),
        }
        filas.append(f)
        r = rubros.setdefault(it["rubro"], dict(orig=0.0, ejec=0.0, dif=0.0,
                                                 ef_cant=0.0, ef_prec=0.0))
        for k, v in (("orig", t_orig), ("ejec", t_ej), ("dif", f["dif"]),
                     ("ef_cant", f["ef_cant"]), ("ef_prec", f["ef_prec"])):
            r[k] += v
            tot[k] += v

    # Adicionales: no estaban en el Original → toda su ejecución es diferencia.
    filas_adic, t_adic = [], 0.0
    for a in sorted(adicionales(ejec), key=lambda x: (x["rubro"], x["clave"])):
        ac = acc.get(a["clave"], {"cantidad": 0.0, "total": 0.0})
        q_ej, t_ej = ac["cantidad"], ac["total"]
        filas_adic.append({
            **{k: a[k] for k in ("clave", "rubro", "item", "descripcion", "unidad")},
            "estado": estado(ejec, a["clave"]),
            "cant_orig": 0.0, "pu_orig": 0.0, "total_orig": 0.0,
            "cant_ejec": q_ej, "pu_ejec": (t_ej / q_ej) if q_ej else 0.0,
            "total_ejec": t_ej, "dif": t_ej, "ef_cant": 0.0, "ef_prec": 0.0,
            "por_etapa": por_etapa.get(a["clave"], {}), "adicional": True,
        })
        t_adic += t_ej
    gen = dict(orig=tot["orig"], ejec=tot["ejec"] + t_adic,
               dif=tot["dif"] + t_adic, ef_cant=tot["ef_cant"],
               ef_prec=tot["ef_prec"], adic=t_adic)
    return {
        "filas": filas,
        "rubros": rubros,
        "rubros_desc": ejec["original"].get("rubros", {}),
        "total": tot,                 # solo tareas del Original
        "filas_adic": filas_adic,
        "total_adic": t_adic,
        "total_general": gen,         # Original + adicionales
        "solo_con_avance": solo_con_avance,
        "etapas": [{"numero": e["numero"], "nombre": e.get("nombre", ""),
                    "fecha": e.get("fecha", ""),
                    "archivo_precios": e.get("archivo_precios", ""),
                    "total": sum(i["cantidad"] * i["pu"] for i in e.get("items", [])),
                    "total_adic": sum(i["cantidad"] * i["pu"] for i in e.get("items", [])
                                      if es_adicional(i["clave"])),
                    "n_tareas": len(e.get("items", []))} for e in etapas],
    }


# ─────────────────────────────────────────────────────────────────────────────
#  Incidencias reales → BaseParticular.db
#  Incidencia real de un insumo = consumo total en todas las etapas / cantidad de
#  tarea ejecutada (promedio ponderado por cantidad). Se agrupa por código de
#  incidencias (cod_tar + variante): las tareas que comparten código comparten fila.
# ─────────────────────────────────────────────────────────────────────────────

TOL_INCID = 1e-6


def incidencias_reales(carpeta_data: Path, ejec: dict, incidencias: dict,
                       catalogo: dict | None = None, solo_realizadas: bool = True) -> list:
    cat = catalogo or {}
    grupos = {}   # cod -> {"q": cant. tarea, "tareas": {clave: desc}, "cons": {cod_ins: q}, "uni": {}}
    for e in listar_etapas(carpeta_data):
        for i in e.get("items", []):
            if not i.get("cod_tar") or not i.get("cantidad"):
                continue
            if solo_realizadas and estado(ejec, i["clave"]) != "realizada":
                continue
            cod = cod_incidencias(i["cod_tar"], i.get("subcontrato", ""))
            g = grupos.setdefault(cod, {"q": 0.0, "tareas": {}, "cons": {}, "uni": {},
                                        "nom": {}})
            if not i.get("solo_insumos"):
                g["q"] += i["cantidad"]
            g["tareas"][i["clave"]] = f"{i['item']} {i['descripcion']}"
            if "insumos" in i:
                lista = [(x["cod_ins"], x["incid"], x.get("unidad", ""), x.get("nombre", ""))
                         for x in i["insumos"]]
            else:   # etapa guardada sin lista de insumos: se ejecutó según el análisis
                lista = [(x["cod_ins"], x["cantidad"], x.get("unidad", ""), "")
                         for x in incidencias.get(cod, [])]
            for c, inc, uni, nom in lista:
                g["cons"][c] = g["cons"].get(c, 0.0) + inc * i["cantidad"]
                g["uni"].setdefault(c, uni)
                if nom:
                    g["nom"].setdefault(c, nom)
    res = []
    for cod in sorted(grupos):
        g = grupos[cod]
        if g["q"] <= 1e-9:
            continue
        base = {x["cod_ins"]: x for x in incidencias.get(cod, [])}
        filas = []
        for c in list(base) + [c for c in g["cons"] if c not in base]:
            b = float(base[c]["cantidad"]) if c in base else None
            r = g["cons"].get(c, 0.0) / g["q"]
            if b is None:
                acc = "nuevo" if r > TOL_INCID else "sin cambio"
            elif r <= TOL_INCID:
                acc = "quitar" if b > TOL_INCID else "sin cambio"
            elif abs(r - b) > TOL_INCID * max(1.0, abs(b)):
                acc = "actualizar"
            else:
                acc = "sin cambio"
            filas.append({
                "cod_ins": c,
                "nombre": g["nom"].get(c) or cat.get(c, {}).get("nombre", ""),
                "unidad": (base[c].get("unidad") if c in base else "") or g["uni"].get(c, "")
                          or cat.get(c, {}).get("unidad", ""),
                "base": b, "real": r, "accion": acc,
            })
        res.append({"cod": cod, "cantidad": g["q"], "tareas": g["tareas"], "insumos": filas,
                    "cambios": sum(1 for f in filas if f["accion"] != "sin cambio")})
    return res


def aplicar_incidencias(carpeta_data: Path, grupos: list) -> Path:
    """Escribe en BaseParticular.db las filas con cambios de los grupos recibidos.
    Hace antes un backup BaseParticular_antes_cierre_<fecha>.db y lo devuelve."""
    import shutil
    import sqlite3
    db = Path(carpeta_data) / "BaseParticular.db"
    bak = db.with_name(f"BaseParticular_antes_cierre_{date.today().isoformat()}.db")
    if bak.exists():
        bak = db.with_name(f"BaseParticular_antes_cierre_"
                           f"{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.db")
    shutil.copy2(db, bak)
    conn = sqlite3.connect(str(db))
    try:
        with conn:
            for g in grupos:
                for f in g["insumos"]:
                    if f["accion"] == "actualizar":
                        conn.execute("UPDATE incidencias SET cantidad=? WHERE cod_tar=? AND "
                                     "cod_ins=?", (f["real"], g["cod"], f["cod_ins"]))
                    elif f["accion"] == "nuevo":
                        conn.execute("INSERT OR REPLACE INTO incidencias (cod_tar, cod_ins, "
                                     "cantidad, unidad) VALUES (?,?,?,?)",
                                     (g["cod"], f["cod_ins"], f["real"], f["unidad"]))
                    elif f["accion"] == "quitar":
                        conn.execute("DELETE FROM incidencias WHERE cod_tar=? AND cod_ins=?",
                                     (g["cod"], f["cod_ins"]))
    finally:
        conn.close()
    return bak


def exportar_comparacion(ruta: Path, obra_titulo: str, ejec: dict, comp: dict):
    import openpyxl
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    F_H = Font(name="Arial", size=10, bold=True, color="FFFFFF")
    F_B = Font(name="Arial", size=10, bold=True)
    F_N = Font(name="Arial", size=10)
    P_H = PatternFill("solid", fgColor="1A3A5C")
    P_R = PatternFill("solid", fgColor="D6E8F5")
    P_T = PatternFill("solid", fgColor="1D5A2A")
    NUM, PES, PCT = "#,##0.00", "$ #,##0", "0.0%"

    wb = openpyxl.Workbook()

    # ── Hoja Resumen ─────────────────────────────────────────────
    ws = wb.active
    ws.title = "Resumen"
    o = ejec["original"]
    ws.append([f"Obra {obra_titulo} — Cierre de ejecución"])
    ws["A1"].font = Font(name="Arial", size=13, bold=True)
    ws.append([f"Original: {o['archivo']} (precios {o.get('archivo_precios') or '-'}), "
               f"definido {o['fecha']}"])
    if comp.get("solo_con_avance"):
        ws.cell(ws.max_row, 1).value += "  —  SOLO TAREAS CON AVANCE (sin las «A realizar»)"
    ws.append([])
    ws.append(["Etapa", "Nombre", "Fecha", "Archivo de precios", "Tareas",
               "Tareas originales", "Adicionales", "Total"])
    for c in ws[ws.max_row]:
        c.font, c.fill = F_H, P_H
    for e in comp["etapas"]:
        ws.append([f"Etapa {e['numero']:02d}", e["nombre"], e["fecha"],
                   e["archivo_precios"], e["n_tareas"], e["total"] - e["total_adic"],
                   e["total_adic"], e["total"]])
        for k in (6, 7, 8):
            ws.cell(ws.max_row, k).number_format = PES
    t, g = comp["total"], comp["total_general"]
    ws.append([])
    filas_res = (
        ("TAREAS DEL ORIGINAL", None, True),
        ("  Total Original", t["orig"], False),
        ("  Ejecutado (suma de etapas)", t["ejec"], False),
        ("  Diferencia", t["dif"], True),
        ("      por cantidades", t["ef_cant"], False),
        ("      por precios", t["ef_prec"], False),
        ("ADICIONALES (no previstas en el Original)", g["adic"], True),
        ("TOTAL", None, True),
        ("  Total Original", g["orig"], False),
        ("  Total ejecutado (originales + adicionales)", g["ejec"], False),
        ("  Diferencia total", g["dif"], True),
        ("      por cantidades", g["ef_cant"], False),
        ("      por precios", g["ef_prec"], False),
        ("      por adicionales", g["adic"], False),
    )
    for lbl, v, neg in filas_res:
        ws.append([lbl, None, None, None, None, None, None, v])
        if neg:
            ws.cell(ws.max_row, 1).font = F_B
            ws.cell(ws.max_row, 8).font = F_B
        ws.cell(ws.max_row, 8).number_format = PES
    ws.append(["  Variación %", None, None, None, None, None, None,
               (g["dif"] / g["orig"]) if g["orig"] else None])
    ws.cell(ws.max_row, 1).font = F_B
    ws.cell(ws.max_row, 8).number_format = PCT
    for col, w in zip("ABCDEFGH", (44, 22, 12, 26, 8, 18, 16, 18)):
        ws.column_dimensions[col].width = w

    # ── Hoja Comparación (por tarea) ─────────────────────────────
    ws = wb.create_sheet("Comparacion")
    nums = [e["numero"] for e in comp["etapas"]]
    hdr = (["Rubro", "Ítem", "Descripción", "Unidad", "Estado",
            "Cant. Original", "PU Original", "Total Original"]
           + [f"Cant. E{n:02d}" for n in nums]
           + ["Cant. Ejecutada", "PU medio ejec.", "Total Ejecutado",
              "Diferencia", "Dif. por cantidad", "Dif. por precio", "Var. %"])
    ws.append(hdr)
    for c in ws[1]:
        c.font, c.fill = F_H, P_H
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[1].height = 30
    n0 = 9 + len(nums)   # primera columna después de las cantidades por etapa
    fmt = {6: NUM, 7: PES, 8: PES, n0: NUM, n0 + 1: PES, n0 + 2: PES,
           n0 + 3: PES, n0 + 4: PES, n0 + 5: PES, n0 + 6: PCT}
    for k in range(9, n0):
        fmt[k] = NUM
    P_S = PatternFill("solid", fgColor="2A6099")   # títulos de sección
    P_A = PatternFill("solid", fgColor="EDE3F5")   # filas de adicionales
    vacias = [None] * len(nums)

    def fila_total(texto, t, fill, pct=True):
        ws.append(["", "", texto, "", "", None, None, t["orig"] or None] + vacias
                  + [None, None, t["ejec"], t["dif"], t["ef_cant"] or None,
                     t["ef_prec"] or None,
                     (t["dif"] / t["orig"]) if (pct and t["orig"]) else None])
        for c in ws[ws.max_row]:
            c.font, c.fill = F_H, fill

    def titulo(texto):
        ws.append([texto])
        for c in ws[ws.max_row]:
            c.font, c.fill = F_H, P_S

    def fila_tarea(f, fill=None):
        ws.append([f["rubro"], f["item"], f["descripcion"], f["unidad"],
                   ESTADO_TXT.get(f["estado"], f["estado"]),
                   f["cant_orig"] or None, f["pu_orig"] or None, f["total_orig"] or None]
                  + [f["por_etapa"].get(n) for n in nums]
                  + [f["cant_ejec"], f["pu_ejec"] or None, f["total_ejec"], f["dif"],
                     f["ef_cant"] or None, f["ef_prec"] or None,
                     (f["dif"] / f["total_orig"]) if f["total_orig"] else None])
        for c in ws[ws.max_row]:
            c.font = F_N
            if fill:
                c.fill = fill

    titulo("TAREAS DEL ORIGINAL")
    rub_actual = None
    for f in comp["filas"]:
        if f["rubro"] != rub_actual:
            rub_actual = f["rubro"]
            r = comp["rubros"][rub_actual]
            ws.append([rub_actual, "", comp["rubros_desc"].get(rub_actual, ""), "", "",
                       None, None, r["orig"]] + vacias +
                      [None, None, r["ejec"], r["dif"], r["ef_cant"], r["ef_prec"],
                       (r["dif"] / r["orig"]) if r["orig"] else None])
            for c in ws[ws.max_row]:
                c.font, c.fill = F_B, P_R
        fila_tarea(f)
    t = comp["total"]
    fila_total("SUBTOTAL TAREAS DEL ORIGINAL", t, P_H)
    if comp["filas_adic"]:
        ws.append([])
        titulo("ADICIONALES (no previstas en el Original)")
        for f in comp["filas_adic"]:
            fila_tarea(f, P_A)
        a = comp["total_adic"]
        fila_total("SUBTOTAL ADICIONALES",
                   dict(orig=0.0, ejec=a, dif=a, ef_cant=0.0, ef_prec=0.0), P_H, pct=False)
    ws.append([])
    fila_total("TOTAL GENERAL (Original + adicionales)", comp["total_general"], P_T)
    for row in ws.iter_rows(min_row=2):
        for c in row:
            if c.column in fmt:
                c.number_format = fmt[c.column]
    anchos = [7, 6, 46, 7, 11, 12, 14, 16] + [10] * len(nums) + [12, 14, 16, 16, 16, 16, 9]
    for i, w in enumerate(anchos, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "D2"
    wb.save(str(ruta))


def exportar_etapa(ruta: Path, obra_titulo: str, etapa: dict, ejec: dict):
    """Excel de una Etapa XX: tareas, cantidades, PU y totales por rubro."""
    import openpyxl
    from openpyxl.styles import Alignment, Font, PatternFill

    F_H = Font(name="Arial", size=10, bold=True, color="FFFFFF")
    F_B = Font(name="Arial", size=10, bold=True)
    P_H = PatternFill("solid", fgColor="1A3A5C")
    P_R = PatternFill("solid", fgColor="D6E8F5")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = nombre_etapa(etapa)
    ws.append([f"Obra {obra_titulo} — {nombre_etapa(etapa)}"
               + (f" — {etapa['nombre']}" if etapa.get("nombre") else "")])
    reg = registro(ejec)
    ws["A1"].font = Font(name="Arial", size=13, bold=True)
    ws.append([f"Fecha: {etapa.get('fecha', '')}   Precios: {etapa.get('archivo_precios') or '-'}"])
    ws.append([])
    ws.append(["Rubro", "Ítem", "Descripción", "Unidad", "Cantidad", "P. Unit.", "Total", "Finaliza"])
    for c in ws[4]:
        c.font, c.fill = F_H, P_H
        c.alignment = Alignment(horizontal="center")
    desc_r = {**ejec["original"].get("rubros", {}), "AD": "Adicionales varios"}
    P_S = PatternFill("solid", fgColor="2A6099")
    P_A = PatternFill("solid", fgColor="EDE3F5")
    total = 0.0
    secciones = (("TAREAS DEL ORIGINAL", [i for i in etapa["items"] if not es_adicional(i["clave"])], None),
                 ("ADICIONALES (no previstas en el Original)",
                  [i for i in etapa["items"] if es_adicional(i["clave"])], P_A))
    for titulo, items, fill in secciones:
        if not items:
            continue
        ws.append([titulo])
        for c in ws[ws.max_row]:
            c.font, c.fill = F_H, P_S
        rub, sub_sec = None, 0.0
        for i in items:
            if i["rubro"] != rub:
                rub = i["rubro"]
                sub = sum(x["cantidad"] * x["pu"] for x in items if x["rubro"] == rub)
                ws.append([rub, "", desc_r.get(rub, ""), "", None, None, sub, ""])
                for c in ws[ws.max_row]:
                    c.font, c.fill = F_B, P_R
            t = i["cantidad"] * i["pu"]
            sub_sec += t
            marca = (f"  [{i.get('subcontrato') or 'Propio'}: "
                     f"{VARIANTE_TXT.get(i.get('subcontrato') or '', '')}]"
                     if variante_cambiada(i, reg.get(i["clave"], i)) else "")
            ws.append([i["rubro"], i["item"], i["descripcion"] + marca
                       + ("  (solo insumos pendientes, no suma cantidad)"
                          if i.get("solo_insumos") else ""), i["unidad"], i["cantidad"],
                       i["pu"], t, "Sí" if i.get("finaliza") else ""])
            if fill:
                for c in ws[ws.max_row]:
                    c.fill = fill
        total += sub_sec
        ws.append(["", "", f"Subtotal {titulo.split(' (')[0].lower()}", "", None, None, sub_sec, ""])
        for c in ws[ws.max_row]:
            c.font = F_B
    ws.append(["", "", "TOTAL ETAPA", "", None, None, total, ""])
    for c in ws[ws.max_row]:
        c.font = F_B
    for row in ws.iter_rows(min_row=5):
        row[4].number_format = "#,##0.00"
        row[5].number_format = "$ #,##0.00"
        row[6].number_format = "$ #,##0"
    for col, w in zip("ABCDEFGH", (7, 6, 50, 8, 12, 15, 16, 9)):
        ws.column_dimensions[col].width = w

    # ── Hoja Insumos: composición de cada tarea en la etapa ─────────
    ws = wb.create_sheet("Insumos")
    ws.append(["Ítem", "Tarea / Insumo", "Unidad", "Incid. x unidad", "Cantidad etapa",
               "Precio", "Total", "Modificado"])
    for c in ws[1]:
        c.font, c.fill = F_H, P_H
        c.alignment = Alignment(horizontal="center")
    F_M = Font(name="Arial", size=10, color="1F5FBF")
    for i in etapa["items"]:
        ws.append([i["item"], i["descripcion"], i["unidad"], None, i["cantidad"],
                   i["pu"], i["cantidad"] * i["pu"],
                   "PU manual" if i.get("pu_manual") else ""])
        for c in ws[ws.max_row]:
            c.font, c.fill = F_B, P_R
        for x in i.get("insumos") or []:
            if abs(x["incid"] * i["cantidad"]) < 1e-9:
                continue                   # quitado en la etapa (o tarea sin cantidad)
            mod = (["agregado"] if x.get("agregado") else
                   [t for t, k in (("incidencia", "mod_incid"), ("precio", "mod_precio"))
                    if x.get(k)])
            q = x["incid"] * i["cantidad"]
            ws.append(["", f"   {x['cod_ins']}  {x.get('nombre', '')}", x["unidad"],
                       x["incid"], q, x["precio"], q * x["precio"], ", ".join(mod)])
            if mod:
                for c in ws[ws.max_row]:
                    c.font = F_M
    for row in ws.iter_rows(min_row=2):
        row[3].number_format = "#,##0.0000"
        row[4].number_format = "#,##0.00"
        row[5].number_format = "$ #,##0.00"
        row[6].number_format = "$ #,##0"
    for col, w in zip("ABCDEFGH", (6, 55, 8, 14, 14, 15, 16, 20)):
        ws.column_dimensions[col].width = w
    ws.freeze_panes = "A2"
    wb.save(str(ruta))
