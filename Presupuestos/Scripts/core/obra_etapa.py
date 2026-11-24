"""obra_etapa.py — Una Etapa (etapaNN.json o etapaNN_varianteMM.json) vista como si
fuera una obra, para abrirla en la misma ventana que el presupuesto (pestañas 1-4 e
Informes).

- Las tareas de la etapa pasan a `items_presupuesto`, agrupadas por los rubros del
  Original. Cada tarea conserva sus campos de etapa (clave, finaliza, insumos…).
- Incidencias: las de la propia tarea en la etapa (lista "insumos"), que pueden estar
  modificadas a mano. Si en la ventana se cambia la tarea o su variante, se usan las
  del análisis.
- Precios: uno por insumo (pestaña 3). Al guardar, solo los insumos cuyo precio se
  cambió en la ventana se escriben en las tareas; el resto conserva el de la etapa.
- Se guarda con `armar_etapa()` + core.etapas (nunca en obraNNN.json).
"""
import copy

from core.obra import Obra
from core import etapas as E


def _float(v) -> float:
    try:
        return float(v or 0.0)
    except (TypeError, ValueError):
        return 0.0


class ObraEtapa(Obra):
    es_etapa = True

    def __init__(self, base: Obra, etapa: dict, ejec: dict, maestro: dict,
                 nueva: bool = False):
        super().__init__(base.numero, base.nombre, base.ubicacion)
        self.comitente      = base.comitente
        self.id_comitente   = base.id_comitente
        self.fecha_creacion = base.fecha_creacion
        self.estado         = base.estado
        self.version        = base.version
        self.ejec           = ejec
        self.es_nueva       = nueva
        self._precios_obra  = {**(ejec["original"].get("precios") or {}),
                               **(base.precios or {})}
        self._cargar(etapa, maestro)

    # ── Datos de la etapa → "obra" ──────────────────────────────────────────
    def _cargar(self, etapa: dict, maestro: dict):
        self.etapa = {k: v for k, v in etapa.items() if not k.startswith("_")}
        etapa_items = copy.deepcopy(self.etapa.get("items", []))
        self.archivo_precios = self.etapa.get("archivo_precios", "") or ""
        if self.archivo_precios == "(los de la obra)":
            self.archivo_precios = ""
        reg  = E.registro(self.ejec)
        inc  = maestro["incidencias"]
        cat  = maestro.get("insumos") or {}
        tpc  = maestro.get("tareas_por_cod", {})
        base_precios = {**self._precios_obra, **(self.etapa.get("precios") or {})}
        for i in etapa_items:              # etapas guardadas sin lista de insumos
            E.asegurar_insumos(i, reg.get(i["clave"], i), inc, base_precios, cat)
        # Un precio por insumo: el de la etapa (el primero que aparece) o el de la obra
        precios = dict(base_precios)
        vistos = set()
        for i in etapa_items:
            for x in i.get("insumos") or []:
                c = x["cod_ins"]
                if c not in vistos and x.get("precio"):
                    precios[c] = x["precio"]
                    vistos.add(c)
        self.precios = precios
        self.precios_ini = dict(precios)   # para saber qué se cambió en la ventana
        # Rubros del Original, en orden; las tareas de cada uno debajo
        rubros = dict(self.ejec["original"].get("rubros") or {})
        orden = sorted({i.get("rubro", "") for i in etapa_items},
                       key=lambda r: (r not in rubros, r))
        items = []
        for r in orden:
            items.append({"es_rubro": True, "rubro": r,
                          "descripcion": rubros.get(r, "Adicionales" if not r else "")})
            for i in etapa_items:
                if i.get("rubro", "") != r:
                    continue
                if i.get("pu_manual"):
                    i["precio_manual"] = i["pu_manual"]
                i["rubro_std"] = tpc.get(i.get("cod_tar", ""), {}).get("rubro", "")
                i["_ins_de"] = E.cod_incidencias(i.get("cod_tar", ""), i.get("subcontrato", ""))
                items.append(i)
        self.items_presupuesto = items
        self.diferencias_precio = self._precios_distintos(etapa_items)

    @staticmethod
    def _precios_distintos(items: list) -> list:
        """Insumos que tienen precios distintos según la tarea."""
        por_cod = {}
        for i in items:
            for x in i.get("insumos") or []:
                if x.get("precio"):
                    por_cod.setdefault(x["cod_ins"], set()).add(round(x["precio"], 4))
        return sorted(c for c, ps in por_cod.items() if len(ps) > 1)

    # ── Lo que usa la ventana ───────────────────────────────────────────────
    @property
    def titulo(self) -> str:
        return f"{self.numero} - {self.nombre}  —  {self.nombre_etapa}"

    @property
    def nombre_etapa(self) -> str:
        txt = E.nombre_etapa(self.etapa) if "numero" in self.etapa else "Etapa"
        if self.etapa.get("nombre"):
            txt += f"  {self.etapa['nombre']}"
        return txt + ("  (nueva)" if self.es_nueva else "")

    def incidencias_item(self, it: dict, incidencias: dict, fallback: bool = False) -> list:
        """Las incidencias propias de la tarea en la etapa, mientras la tarea y su
        variante sean las mismas con las que se armó la lista."""
        if "insumos" in it and it.get("_ins_de") == E.cod_incidencias(
                it.get("cod_tar", ""), it.get("subcontrato", "")):
            return [{"cod_ins": x["cod_ins"], "cantidad": x["incid"],
                     "unidad": x.get("unidad", "")}
                    for x in it["insumos"] if x.get("incid")]
        return super().incidencias_item(it, incidencias, fallback)

    def guardar(self, *a, **k):
        raise RuntimeError("Una etapa se guarda con armar_etapa(), no como versión de obra.")

    # ── "Obra" → datos de la etapa ──────────────────────────────────────────
    def armar_etapa(self, maestro: dict, precios: dict) -> tuple[dict, list]:
        """Devuelve (etapa, filas_omitidas). No escribe nada."""
        inc = maestro["incidencias"]
        cat = maestro.get("insumos") or {}
        reg = E.registro(self.ejec)
        cambiados = {c for c in set(precios) | set(self.precios_ini)
                     if abs(_float(precios.get(c)) - _float(self.precios_ini.get(c))) > 1e-9}
        filas = [it for it in self.items_presupuesto if not it.get("es_rubro")]
        usadas = {it["clave"] for it in filas if it.get("clave")}
        nuevas_adic = []
        items, omitidas = [], []
        for it in filas:
            cod_tar = it.get("cod_tar", "")
            if not cod_tar and not it.get("precio_manual"):
                omitidas.append(it.get("descripcion", "") or "(fila vacía)")
                continue
            x = copy.deepcopy({k: v for k, v in it.items()
                               if not k.startswith("_")
                               and k not in ("es_rubro", "rubro_std", "precio_manual")})
            x["pu_manual"] = _float(it.get("precio_manual")) or None
            x["subcontrato"] = (x.get("subcontrato") or "").strip().upper()
            x["cod_tar"] = cod_tar
            x["cantidad"] = _float(x.get("cantidad"))
            x.setdefault("finaliza", False)
            x.setdefault("sin_precio", [])
            x.setdefault("pu", 0.0)
            if not x.get("clave"):
                x["clave"] = self._clave_para(cod_tar, x["subcontrato"], usadas)
                if not x["clave"]:
                    x["clave"] = E.nueva_clave_adicional(self.ejec, nuevas_adic)
                    nuevas_adic.append(x["clave"])
                usadas.add(x["clave"])
            x["adicional"] = E.es_adicional(x["clave"])
            it_orig = reg.get(x["clave"], x)
            clave_ins = E.cod_incidencias(cod_tar, x["subcontrato"])
            if "insumos" in it and it.get("_ins_de") == clave_ins:
                for ins in x["insumos"]:
                    c = ins["cod_ins"]
                    if c in cambiados and _float(precios.get(c)):
                        ins["precio"] = _float(precios[c])
                        ins["mod_precio"] = abs(ins["precio"] - _float(ins.get("precio_base"))) > 1e-9
            elif not cod_tar:
                x["insumos"] = []
            else:
                # Tarea nueva en la etapa o cambiada de tarea/variante: análisis de la base
                previos = {i["cod_ins"]: i for i in it.get("insumos") or []}
                x["insumos"] = E.armar_insumos(cod_tar, x["subcontrato"], inc,
                                               {**self._precios_obra, **precios}, cat)
                for ins in x["insumos"]:
                    p = previos.get(ins["cod_ins"])
                    if p and p.get("mod_precio") and ins["cod_ins"] not in cambiados:
                        ins["precio"], ins["mod_precio"] = p["precio"], True
            E.recalcular_item(x, it_orig)
            items.append(x)
        etapa = dict(self.etapa)
        etapa["items"] = items
        etapa["archivo_precios"] = self.archivo_precios
        etapa["precios"] = E.precios_usados(items, inc, {**self._precios_obra, **precios})
        return etapa, omitidas

    def _clave_para(self, cod_tar: str, subcontrato: str, usadas: set) -> str:
        """Tarea agregada en la ventana: si está en el Original (y no está ya en la
        etapa) toma esa clave, prefiriendo la de la misma variante; si no, será un
        adicional."""
        libres = [i for i in self.ejec["original"]["items"]
                  if i.get("cod_tar") == cod_tar and i["clave"] not in usadas]
        for i in libres:
            if (i.get("subcontrato") or "").strip().upper() == subcontrato:
                return i["clave"]
        return libres[0]["clave"] if libres else ""

    def saldo_para(self, it: dict) -> float:
        """Cantidad propuesta para una fila nueva vinculada a una tarea del Original:
        su saldo (Original − lo ejecutado en las otras etapas)."""
        usadas = {i["clave"] for i in self.items_presupuesto
                  if not i.get("es_rubro") and i.get("clave")}
        clave = self._clave_para(it.get("cod_tar", ""),
                                 (it.get("subcontrato") or "").strip().upper(), usadas)
        if not clave:
            return 0.0
        orig = next(i for i in self.ejec["original"]["items"] if i["clave"] == clave)
        hecho = E.acumulado(self.carpeta_data, excluir=self.etapa.get("numero")) \
                 .get(clave, {}).get("cantidad", 0.0)
        return max((orig.get("cantidad") or 0.0) - hecho, 0.0)

    def variantes_cambiadas(self, etapa: dict) -> list:
        reg = E.registro(self.ejec)
        return [i for i in etapa["items"] if E.variante_cambiada(i, reg.get(i["clave"], i))]

    def recargar(self, etapa: dict, ejec: dict, maestro: dict):
        """Después de guardar: vuelve a armar la etapa desde lo guardado."""
        self.ejec = ejec
        self.es_nueva = False
        self._cargar(etapa, maestro)
