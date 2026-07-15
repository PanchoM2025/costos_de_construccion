"""
obra.py
Clase que representa una obra y maneja su persistencia.

Archivos por obra (Obras/Obra001/data/):
  obra000.json        — presupuesto activo
  obra001.json ...    — variantes/alternativas
  variaciones.txt     — log de versiones
  BaseParticular.db   — tareas/insumos/incidencias propias de esta obra
                        (copiadas desde Master_Obras.db al crear, editables libremente)

Índice central de obras:
  Master_Obras.db (tabla obras, comitentes) — reemplaza obras_db.json
"""
import json
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime


RAIZ            = Path(__file__).resolve().parent.parent.parent
CARPETA_OBRAS   = RAIZ / "Obras"
CARPETA_DATA    = RAIZ / "Data"
CARPETA_PRECIOS = CARPETA_DATA / "Precios"
MASTER_DB       = CARPETA_DATA / "Master_Obras.db"


def _asegurar_carpetas():
    CARPETA_OBRAS.mkdir(parents=True, exist_ok=True)
    CARPETA_DATA.mkdir(parents=True, exist_ok=True)
    (CARPETA_PRECIOS / "Precios_base").mkdir(parents=True, exist_ok=True)


# ═════════════════════════════════════════════════════════════════════════════
# BaseParticular.db — creación y acceso
# ═════════════════════════════════════════════════════════════════════════════

def _base_particular_es_valida(ruta: Path) -> bool:
    """
    Verifica que BaseParticular.db tenga el esquema nuevo.
    Devuelve False si le falta alguna tabla o columna clave → hay que recrearla.
    """
    try:
        conn = sqlite3.connect(str(ruta))
        cur  = conn.cursor()
        # Tablas mínimas requeridas
        for tabla in ("rubros", "tareas", "insumos", "incidencias", "incidencias_v2"):
            cur.execute(f"SELECT 1 FROM [{tabla}] LIMIT 1")
        # Columna clave que cambió entre versiones
        cur.execute("SELECT designacion FROM rubros LIMIT 1")
        cur.execute("SELECT id_tarea FROM tareas LIMIT 1")
        cur.execute("SELECT id_insumo FROM insumos LIMIT 1")
        conn.close()
        return True
    except Exception:
        try: conn.close()
        except: pass
        return False


def crear_base_particular(carpeta_data: Path):
    """
    Crea BaseParticular.db en carpeta_data copiando Master_Obras.db.
    Si ya existe pero tiene esquema viejo, la recrea automáticamente.
    """
    dest = carpeta_data / "BaseParticular.db"
    if not MASTER_DB.exists():
        raise FileNotFoundError(f"No se encontró Master_Obras.db en {CARPETA_DATA}")
    if dest.exists() and _base_particular_es_valida(dest):
        return   # esquema vigente, no hacer nada
    if dest.exists():
        dest.unlink()   # eliminar versión vieja
    shutil.copy2(str(MASTER_DB), str(dest))


def conectar_base_particular(carpeta_data: Path) -> sqlite3.Connection:
    """Devuelve conexión a BaseParticular.db con FK activadas.
    Si no existe o tiene esquema viejo, la recrea desde Master_Obras.db."""
    crear_base_particular(carpeta_data)   # valida esquema y recrea si hace falta
    ruta = carpeta_data / "BaseParticular.db"
    conn = sqlite3.connect(str(ruta))
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def _separar_variante(cod: str) -> tuple[str, str]:
    """Devuelve (codigo_base, indicador). Indicador es ' ' si no tiene sufijo."""
    if cod and cod[-1] in ('S', 'E', 'X', 'T'):
        return cod[:-1], cod[-1]
    return cod, ' '


def _build_id_rs_lookup(cur) -> tuple[list, callable, callable]:
    """
    Construye:
    - rubros_ui: lista ordenada de rubros PADRE (es_padre=1) con tareas
    - id_rs_to_rubro_padre: id_rs → nombre del rubro padre
    - id_rs_to_subrubro: id_rs → nombre del subrubro (hijo)
    """
    todos = cur.execute("""
        SELECT cod_rubro, designacion, id_rs_ini, id_rs_fin, es_padre, cod_padre
        FROM rubros
        WHERE id_rs_ini IS NOT NULL AND id_rs_fin IS NOT NULL
        ORDER BY es_padre DESC, cod_rubro
    """).fetchall()

    hijos  = [r for r in todos if r["es_padre"] == 0]
    padres = [r for r in todos if r["es_padre"] == 1]

    # Mapa cod_rubro_padre → nombre padre
    padre_nombre = {r["cod_rubro"]: r["designacion"] for r in padres}

    # Lista padres ordenada por rango
    rubros_ui = []
    vistos = set()
    for r in sorted(padres, key=lambda x: x["id_rs_ini"]):
        if r["designacion"] not in vistos:
            rubros_ui.append(r["designacion"])
            vistos.add(r["designacion"])

    def id_rs_to_rubro_padre(id_rs_val):
        """Devuelve el nombre del rubro PADRE que cubre este id_rs."""
        if not id_rs_val:
            return None
        # Primero buscar por hijo para obtener su cod_padre
        for r in hijos:
            if r["id_rs_ini"] <= id_rs_val <= r["id_rs_fin"]:
                return padre_nombre.get(r["cod_padre"], r["designacion"])
        # Caer directo a padre
        for r in padres:
            if r["id_rs_ini"] <= id_rs_val <= r["id_rs_fin"]:
                return r["designacion"]
        return None

    def id_rs_to_subrubro(id_rs_val):
        """Devuelve el nombre del subrubro (hijo) que cubre este id_rs, o None."""
        if not id_rs_val:
            return None
        for r in hijos:
            if r["id_rs_ini"] <= id_rs_val <= r["id_rs_fin"]:
                return r["designacion"]
        return None

    return rubros_ui, id_rs_to_rubro_padre, id_rs_to_subrubro


def cargar_maestro_desde_db(carpeta_data: Path) -> dict:
    """
    Lee tareas, insumos e incidencias desde BaseParticular.db
    y devuelve la misma estructura que cargar_maestro() del maestro.py original,
    para que el resto del código no cambie.

    Compatible con el esquema de Master_FINAL.db:
      tareas:      id, cod_tar, descripcion, unidad, activo, id_tarea, id_rs
      rubros:      cod_rubro, id_rs_ini, id_rs_fin, designacion, es_padre, cod_padre
      insumos:     cod_ins, descripcion, unidad, activo, id_insumo
      incidencias: cod_tar, cod_ins, cantidad, unidad
    """
    conn = conectar_base_particular(carpeta_data)
    cur  = conn.cursor()

    # ── Rubros ────────────────────────────────────────────────────────────
    rubros_ui, id_rs_to_padre, id_rs_to_subrubro = _build_id_rs_lookup(cur)

    # ── Tareas agrupadas por rubro PADRE ──────────────────────────────────
    tareas_por_rubro = {r: [] for r in rubros_ui}
    tareas_por_cod   = {}

    for row in cur.execute(
            "SELECT cod_tar, descripcion, unidad, id_rs FROM tareas ORDER BY cod_tar"
    ).fetchall():
        base, variante = _separar_variante(row["cod_tar"])
        rubro_padre    = id_rs_to_padre(row["id_rs"])
        if rubro_padre is None:
            continue
        if rubro_padre not in tareas_por_rubro:
            tareas_por_rubro[rubro_padre] = []
        tarea = {
            "cod":      row["cod_tar"],
            "base":     base,
            "variante": variante,
            "nombre":   row["descripcion"] or "",
            "unidad":   row["unidad"] or "",
            "rubro":    rubro_padre,
            "subrubro": id_rs_to_subrubro(row["id_rs"]) or rubro_padre,
        }
        tareas_por_rubro[rubro_padre].append(tarea)
        tareas_por_cod[row["cod_tar"]] = tarea

    # Solo rubros padre que tienen al menos una tarea
    rubros_con_tareas = [r for r in rubros_ui if tareas_por_rubro.get(r)]

    # ── Insumos ───────────────────────────────────────────────────────────
    insumos = {}
    for row in cur.execute("SELECT cod_ins, descripcion, unidad FROM insumos").fetchall():
        insumos[row["cod_ins"]] = {
            "cod":    row["cod_ins"],
            "nombre": row["descripcion"] or "",
            "unidad": row["unidad"] or "",
        }

    # ── Incidencias ───────────────────────────────────────────────────────
    incidencias = {}
    for row in cur.execute("SELECT cod_tar, cod_ins, cantidad, unidad FROM incidencias").fetchall():
        cod_tar = row["cod_tar"]
        if cod_tar not in incidencias:
            incidencias[cod_tar] = []
        incidencias[cod_tar].append({
            "cod_ins":  row["cod_ins"],
            "unidad":   row["unidad"] or "",
            "cantidad": row["cantidad"] or 0.0,
        })

    conn.close()

    return {
        "rubros":         rubros_con_tareas,
        "tareas":         tareas_por_rubro,
        "tareas_por_cod": tareas_por_cod,
        "insumos":        insumos,
        "incidencias":    incidencias,
    }


# ═════════════════════════════════════════════════════════════════════════════
# Clase Obra
# ═════════════════════════════════════════════════════════════════════════════

class Obra:
    def __init__(self, numero: str, nombre: str, ubicacion: str = ""):
        self.numero          = numero.strip().zfill(3)
        self.nombre          = nombre.strip()
        self.ubicacion       = ubicacion.strip()
        self.comitente       = ""          # nombre (para mostrar)
        self.id_comitente    = None        # FK a comitentes.id_comitente
        self.fecha_creacion  = datetime.now().strftime("%Y-%m-%d")
        self.archivo_precios = ""          # nombre del PUnitarios usado
        self.version         = 0           # 0 = obra000.json
        self.estado          = "activo"    # activo | contratada | finalizada
        # ítems del presupuesto de licitación
        self.items_presupuesto: list = []
        # tareas seleccionadas (compat con código viejo — se reconstruye al guardar)
        self.tareas: dict = {}

    # ── Identidad ─────────────────────────────────────────────────────────
    @property
    def id(self) -> str:
        return f"Obra{self.numero}"

    @property
    def titulo(self) -> str:
        return f"{self.numero} - {self.nombre}"

    @property
    def carpeta(self) -> Path:
        return CARPETA_OBRAS / self.id

    @property
    def carpeta_data(self) -> Path:
        return self.carpeta / "data"

    @property
    def ruta_json(self) -> Path:
        return self.carpeta_data / f"obra{self.version:03d}.json"

    @property
    def carpeta_precios(self) -> Path:
        return self.carpeta / "Precios"

    @property
    def ruta_base_particular(self) -> Path:
        return self.carpeta_data / "BaseParticular.db"

    # ── Insumos calculados ────────────────────────────────────────────────
    def calcular_insumos(self, incidencias: dict) -> dict:
        """
        Dado el dict de incidencias (de BaseParticular o maestro),
        devuelve {cod_ins: {cod_ins, unidad, cantidad_total, tareas_origen}}.
        Respeta el subcontrato: si el ítem tiene subcontrato S/E/X/T,
        usa cod_tar+indicador en lugar del cod_tar base.
        """
        resultado = {}
        for it in self.items_presupuesto:
            if it.get("es_rubro") or not it.get("cod_tar"):
                continue
            cod_tar  = it["cod_tar"]
            subcont  = (it.get("subcontrato") or "").strip().upper()
            cant_tar = it.get("cantidad", 0) or 0

            # si hay subcontrato buscar variante correspondiente
            cod_buscar = cod_tar + subcont if subcont else cod_tar

            lista_inc = incidencias.get(cod_buscar) or incidencias.get(cod_tar, [])

            for inc in lista_inc:
                cod_ins  = inc["cod_ins"]
                cant_ins = inc["cantidad"] * cant_tar
                if cod_ins not in resultado:
                    resultado[cod_ins] = {
                        "cod_ins":       cod_ins,
                        "unidad":        inc["unidad"],
                        "cantidad_total": 0.0,
                        "tareas_origen": [],
                    }
                resultado[cod_ins]["cantidad_total"] += cant_ins
                resultado[cod_ins]["tareas_origen"].append({
                    "cod_tar":     cod_tar,
                    "nombre_tar":  it.get("descripcion", cod_tar),
                    "cantidad_tar": cant_tar,
                    "incidencia":  inc["cantidad"],
                    "subtotal":    cant_ins,
                })
        return resultado

    def insumos_sin_precio(self, incidencias: dict, precios: dict) -> list:
        insumos_obra = self.calcular_insumos(incidencias)
        return [cod for cod in insumos_obra if cod not in precios]

    # ── Persistencia ──────────────────────────────────────────────────────
    def inicializar(self):
        """
        Llamar al CREAR una obra nueva:
        - Crea carpetas
        - Copia Master.db → BaseParticular.db
        - Guarda obra000.json
        """
        _asegurar_carpetas()
        self.carpeta_data.mkdir(parents=True, exist_ok=True)
        self.carpeta_precios.mkdir(parents=True, exist_ok=True)
        crear_base_particular(self.carpeta_data)
        self.version = 0
        self._escribir_json()
        _actualizar_db(self)

    def guardar(self, nueva_version: bool = False, nota: str = ""):
        """
        Guarda la obra.
        nueva_version=True → incrementa el número y registra en variaciones.txt
        """
        _asegurar_carpetas()
        self.carpeta_data.mkdir(parents=True, exist_ok=True)

        if nueva_version:
            self.version += 1
            self._registrar_variacion(nota)

        self._escribir_json()
        _actualizar_db(self)

    def _escribir_json(self):
        datos = {
            "numero":            self.numero,
            "nombre":            self.nombre,
            "ubicacion":         self.ubicacion,
            "comitente":         self.comitente,
            "fecha_creacion":    self.fecha_creacion,
            "version":           self.version,
            "archivo_precios":   self.archivo_precios,
            "items_presupuesto": self.items_presupuesto,
            "tareas":            self.tareas,   # compat
        }
        with open(self.ruta_json, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)

    def _registrar_variacion(self, nota: str):
        ruta = self.carpeta_data / "variaciones.txt"
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
        linea = (f"obra{self.version:03d}.json  —  {fecha}"
                 + (f"  —  {nota}" if nota else "") + "\n")
        with open(ruta, "a", encoding="utf-8") as f:
            if self.version == 1:   # primera variante: agregar encabezado
                f.write(f"obra000.json  —  {self.fecha_creacion}  —  Cotización inicial\n")
            f.write(linea)

    @classmethod
    def cargar(cls, numero: str) -> "Obra":
        """Carga la versión más reciente de la obra."""
        num = numero.strip().zfill(3)
        carpeta_data = CARPETA_OBRAS / f"Obra{num}" / "data"

        # buscar el json de mayor versión
        jsons = sorted(carpeta_data.glob("obra???.json"), reverse=True)
        if not jsons:
            ruta_vieja = carpeta_data / "obra.json"
            if ruta_vieja.exists():
                jsons = [ruta_vieja]
            else:
                raise FileNotFoundError(f"No existe la obra {num}")

        ruta = jsons[0]
        with open(ruta, encoding="utf-8") as f:
            datos = json.load(f)

        obra = cls(datos["numero"], datos["nombre"], datos.get("ubicacion", ""))
        obra.fecha_creacion    = datos.get("fecha_creacion", "")
        obra.version           = datos.get("version", 0)
        obra.archivo_precios   = datos.get("archivo_precios", "")
        obra.items_presupuesto = datos.get("items_presupuesto", [])
        obra.tareas            = datos.get("tareas", {})

        # Completar con datos de Master_Obras.db (comitente, estado, id_comitente)
        _completar_desde_db(obra)

        # si no tiene items_presupuesto pero tiene tareas (formato viejo),
        # convertir al nuevo formato
        if not obra.items_presupuesto and obra.tareas:
            obra.items_presupuesto = _migrar_tareas_a_items(obra.tareas)

        # asegurar BaseParticular.db existe
        if not obra.ruta_base_particular.exists():
            crear_base_particular(obra.carpeta_data)

        return obra

    @classmethod
    def cargar_version(cls, ruta_json) -> "Obra":
        """Carga una versión específica desde su ruta completa."""
        ruta = Path(ruta_json)
        with open(ruta, encoding="utf-8") as f:
            datos = json.load(f)
        obra = cls(datos["numero"], datos["nombre"], datos.get("ubicacion", ""))
        obra.fecha_creacion    = datos.get("fecha_creacion", "")
        obra.version           = datos.get("version", 0)
        obra.archivo_precios   = datos.get("archivo_precios", "")
        obra.items_presupuesto = datos.get("items_presupuesto", [])
        obra.tareas            = datos.get("tareas", {})
        _completar_desde_db(obra)
        if not obra.items_presupuesto and obra.tareas:
            obra.items_presupuesto = _migrar_tareas_a_items(obra.tareas)
        if not obra.ruta_base_particular.exists():
            crear_base_particular(obra.carpeta_data)
        return obra

    @classmethod
    def existe(cls, numero: str) -> bool:
        num = numero.strip().zfill(3)
        conn = _conectar_master()
        row = conn.execute("SELECT 1 FROM obras WHERE numero=?", (num,)).fetchone()
        conn.close()
        return row is not None

    def eliminar(self):
        if self.carpeta.exists():
            shutil.rmtree(self.carpeta)
        _eliminar_de_db(self.numero)

    def listar_versiones(self) -> list[dict]:
        """Devuelve lista de versiones disponibles con fecha y nota."""
        versiones = []
        for j in sorted(self.carpeta_data.glob("obra???.json")):
            with open(j, encoding="utf-8") as f:
                d = json.load(f)
            versiones.append({
                "archivo": j.name,
                "version": d.get("version", 0),
                "fecha":   d.get("fecha_creacion", ""),
            })
        return versiones


# ── Migración formato viejo → nuevo ──────────────────────────────────────────
def _migrar_tareas_a_items(tareas: dict) -> list:
    """Convierte el dict de tareas viejo a lista items_presupuesto."""
    items = []
    rubro_actual = None
    for cod, t in sorted(tareas.items(), key=lambda x: (x[1].get("rubro",""), x[0])):
        rubro = t.get("rubro", "")
        if rubro != rubro_actual:
            rubro_actual = rubro
            items.append({"es_rubro": True, "rubro": "", "descripcion": rubro})
        items.append({
            "es_rubro":    False,
            "rubro":       "",
            "item":        cod,
            "descripcion": t.get("nombre_editado") or t.get("nombre", ""),
            "unidad":      t.get("unidad", ""),
            "cantidad":    t.get("cantidad", 0.0),
            "cod_tar":     cod,
            "subcontrato": t.get("subcontrato", ""),
            "rubro_std":   rubro,
        })
    return items


# ══════════════════════════════════════════════════════════════════════════════
# Índice central de obras — Master_Obras.db
# ══════════════════════════════════════════════════════════════════════════════

def _conectar_master() -> sqlite3.Connection:
    """Conexión a Master_Obras.db con row_factory."""
    if not MASTER_DB.exists():
        raise FileNotFoundError(f"No se encontró Master_Obras.db en {CARPETA_DATA}")
    conn = sqlite3.connect(str(MASTER_DB))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _actualizar_db(obra: "Obra"):
    """INSERT OR REPLACE de la obra en la tabla obras."""
    conn = _conectar_master()
    conn.execute("""
        INSERT INTO obras (numero, nombre, ubicacion, id_comitente, comitente_texto,
                           fecha_creacion, archivo_precios, estado)
        VALUES (:numero,:nombre,:ubicacion,:id_comitente,:comitente_texto,
                :fecha_creacion,:archivo_precios,:estado)
        ON CONFLICT(numero) DO UPDATE SET
            nombre           = excluded.nombre,
            ubicacion        = excluded.ubicacion,
            id_comitente     = excluded.id_comitente,
            comitente_texto  = excluded.comitente_texto,
            fecha_creacion   = excluded.fecha_creacion,
            archivo_precios  = excluded.archivo_precios,
            estado           = excluded.estado
    """, {
        "numero":           obra.numero,
        "nombre":           obra.nombre,
        "ubicacion":        obra.ubicacion,
        "id_comitente":     obra.id_comitente,
        "comitente_texto":  obra.comitente,   # texto libre
        "fecha_creacion":   obra.fecha_creacion,
        "archivo_precios":  obra.archivo_precios,
        "estado":           obra.estado,
    })
    conn.commit()
    conn.close()


def _eliminar_de_db(numero: str):
    """Elimina la obra del índice en Master_Obras.db."""
    conn = _conectar_master()
    conn.execute("DELETE FROM obras WHERE numero=?", (numero,))
    conn.commit()
    conn.close()


def _completar_desde_db(obra: "Obra"):
    """
    Rellena comitente, id_comitente y estado desde Master_Obras.db.
    Si la obra no existe en la DB todavía, no hace nada (valores por defecto).
    """
    try:
        conn = _conectar_master()
        row = conn.execute("""
            SELECT o.id_comitente, o.estado, o.archivo_precios,
                   o.comitente_texto,
                   c.nombre AS nombre_comitente
            FROM obras o
            LEFT JOIN comitentes c ON c.id_comitente = o.id_comitente
            WHERE o.numero = ?
        """, (obra.numero,)).fetchone()
        conn.close()
        if row:
            obra.id_comitente    = row["id_comitente"]
            obra.estado          = row["estado"] or "activo"
            # FK tiene prioridad; sino usa el texto libre
            obra.comitente       = row["nombre_comitente"] or row["comitente_texto"] or ""
            if not obra.archivo_precios:
                obra.archivo_precios = row["archivo_precios"] or ""
    except Exception:
        pass   # si la DB no existe o la obra no está registrada, continuar


def listar_obras() -> list:
    """
    Devuelve lista de dicts con los datos de todas las obras,
    ordenada por número. Comitente: nombre del FK si existe, sino texto libre.
    """
    try:
        conn = _conectar_master()
        rows = conn.execute("""
            SELECT o.numero, o.nombre, o.ubicacion, o.estado,
                   o.fecha_creacion, o.archivo_precios, o.id_comitente,
                   COALESCE(c.nombre, o.comitente_texto, '') AS comitente
            FROM obras o
            LEFT JOIN comitentes c ON c.id_comitente = o.id_comitente
            ORDER BY o.numero
        """).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception:
        return []


# ── Comitentes ────────────────────────────────────────────────────────────────

def listar_comitentes() -> list:
    """Devuelve todos los comitentes ordenados por nombre."""
    conn = _conectar_master()
    rows = conn.execute(
        "SELECT * FROM comitentes ORDER BY nombre"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def crear_comitente(nombre: str, contacto: str = "", telefono: str = "",
                    email: str = "", notas: str = "") -> int:
    """Inserta un comitente nuevo y devuelve su id_comitente."""
    conn = _conectar_master()
    cur = conn.execute(
        "INSERT INTO comitentes(nombre,contacto,telefono,email,notas) VALUES (?,?,?,?,?)",
        (nombre, contacto, telefono, email, notas)
    )
    id_nuevo = cur.lastrowid
    conn.commit()
    conn.close()
    return id_nuevo
