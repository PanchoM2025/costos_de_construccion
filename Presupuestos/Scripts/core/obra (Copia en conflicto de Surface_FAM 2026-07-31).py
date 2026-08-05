"""
obra.py
Clase que representa una obra y maneja su persistencia.

Archivos por obra (Obras/Obra001/data/):
  obra000.json        — presupuesto activo
  obra001.json ...    — variantes/alternativas
  variaciones.txt     — log de versiones
  BaseParticular.db   — tareas/insumos/incidencias propias de esta obra
                        (copiadas desde Master_FINAL.db al crear, editables libremente)

Bases de datos centrales:
  Master_FINAL.db    — catálogo maestro (rubros, tareas, insumos, incidencias)
                       SOLO LECTURA — nunca se modifica desde acá
  Datos_Obras.db     — índice de obras y comitentes (lectura/escritura)
"""
import json
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime


RAIZ             = Path(__file__).resolve().parent.parent.parent
CARPETA_OBRAS    = RAIZ / "Obras"
CARPETA_DATA     = RAIZ / "Data"
CARPETA_PRECIOS  = CARPETA_DATA / "Precios"
CATALOGO_DB      = CARPETA_DATA / "Master_FINAL.db"
DATOS_OBRAS_DB   = CARPETA_DATA / "Datos_Obras.db"
MASTER_DB        = DATOS_OBRAS_DB


def _asegurar_carpetas():
    CARPETA_OBRAS.mkdir(parents=True, exist_ok=True)
    CARPETA_DATA.mkdir(parents=True, exist_ok=True)
    (CARPETA_PRECIOS / "Precios_base").mkdir(parents=True, exist_ok=True)


_SCHEMA_DATOS_OBRAS = """
CREATE TABLE IF NOT EXISTS comitentes (
    id_comitente INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre       TEXT NOT NULL,
    contacto     TEXT DEFAULT '',
    telefono     TEXT DEFAULT '',
    email        TEXT DEFAULT '',
    notas        TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS obras (
    numero           TEXT PRIMARY KEY,
    nombre           TEXT NOT NULL,
    ubicacion        TEXT DEFAULT '',
    id_comitente     INTEGER REFERENCES comitentes(id_comitente),
    comitente_texto  TEXT DEFAULT '',
    fecha_creacion   TEXT DEFAULT '',
    archivo_precios  TEXT DEFAULT '',
    estado           TEXT DEFAULT 'activo'
);
"""



_SCHEMA_CERTIFICADOS = """
CREATE TABLE IF NOT EXISTS certificados (
    id_certificado  INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre          TEXT    NOT NULL,
    fecha           TEXT    DEFAULT '',
    estado          TEXT    DEFAULT 'borrador',
    notas           TEXT    DEFAULT ''
);

CREATE TABLE IF NOT EXISTS certificado_tareas (
    id_certificado  INTEGER NOT NULL REFERENCES certificados(id_certificado) ON DELETE CASCADE,
    cod_tar         TEXT    NOT NULL,
    subcontrato     TEXT    DEFAULT '',
    porcentaje      REAL    DEFAULT 100.0,
    PRIMARY KEY (id_certificado, cod_tar, subcontrato)
);
"""


def _asegurar_tablas_certificados(conn: sqlite3.Connection):
    conn.executescript(_SCHEMA_CERTIFICADOS)
    conn.commit()


def _inicializar_datos_obras():
    if DATOS_OBRAS_DB.exists():
        try:
            _c = sqlite3.connect(str(DATOS_OBRAS_DB))
            n = _c.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'").fetchone()[0]
            if n > 0:
                _c.close()
                return
            _c.close()
        except Exception:
            pass
        DATOS_OBRAS_DB.unlink()

    conn = sqlite3.connect(str(DATOS_OBRAS_DB))
    conn.executescript(_SCHEMA_DATOS_OBRAS)
    conn.commit()

    master_viejo = CARPETA_DATA / "Master_Obras.db"
    if master_viejo.exists():
        try:
            src = sqlite3.connect(str(master_viejo))
            cur_c = src.execute("SELECT * FROM comitentes ORDER BY id_comitente")
            cols_c = [d[0] for d in cur_c.description]
            for row in cur_c.fetchall():
                c_d = dict(zip(cols_c, row))
                conn.execute(
                    "INSERT OR IGNORE INTO comitentes "
                    "(id_comitente,nombre,contacto,telefono,email,notas) VALUES (?,?,?,?,?,?)",
                    (c_d.get("id_comitente"), c_d.get("nombre",""),
                     c_d.get("contacto",""),  c_d.get("telefono",""),
                     c_d.get("email",""),     c_d.get("notas",""))
                )
            cur_o = src.execute("SELECT * FROM obras ORDER BY numero")
            cols_o = [d[0] for d in cur_o.description]
            for row in cur_o.fetchall():
                o_d = dict(zip(cols_o, row))
                conn.execute(
                    "INSERT OR IGNORE INTO obras "
                    "(numero,nombre,ubicacion,id_comitente,comitente_texto,"
                    "fecha_creacion,archivo_precios,estado) VALUES (?,?,?,?,?,?,?,?)",
                    (o_d.get("numero"),           o_d.get("nombre",""),
                     o_d.get("ubicacion",""),      o_d.get("id_comitente"),
                     o_d.get("comitente_texto",""), o_d.get("fecha_creacion",""),
                     o_d.get("archivo_precios",""), o_d.get("estado","activo"))
                )
            src.close()
            conn.commit()
        except Exception:
            pass

    conn.close()


def _base_particular_es_valida(ruta: Path) -> bool:
    """
    Valida esquema Y sincronía con Master_FINAL.db.
    Si el maestro tiene más tareas o insumos, devuelve False → se recrea la copia.
    """
    try:
        conn = sqlite3.connect(str(ruta))
        cur  = conn.cursor()
        for tabla in ("rubros", "tareas", "insumos", "incidencias", "incidencias_v2"):
            cur.execute(f"SELECT 1 FROM [{tabla}] LIMIT 1")
        cur.execute("SELECT designacion FROM rubros LIMIT 1")
        cur.execute("SELECT id_tarea FROM tareas LIMIT 1")
        cur.execute("SELECT id_insumo FROM insumos LIMIT 1")
        n_tar = cur.execute("SELECT COUNT(*) FROM tareas").fetchone()[0]
        n_ins = cur.execute("SELECT COUNT(*) FROM insumos").fetchone()[0]
        n_inc = cur.execute("SELECT COUNT(*) FROM incidencias").fetchone()[0]
        conn.close()
        # Comparar con el maestro — si tiene más registros, forzar recreación
        if CATALOGO_DB.exists():
            m = sqlite3.connect(str(CATALOGO_DB))
            m_tar = m.execute("SELECT COUNT(*) FROM tareas").fetchone()[0]
            m_ins = m.execute("SELECT COUNT(*) FROM insumos").fetchone()[0]
            m_inc = m.execute("SELECT COUNT(*) FROM incidencias").fetchone()[0]
            m.close()
            if m_tar > n_tar or m_ins > n_ins or m_inc > n_inc:
                return False
        return True
    except Exception:
        try: conn.close()
        except: pass
        return False


def crear_base_particular(carpeta_data: Path):
    dest = carpeta_data / "BaseParticular.db"
    if not CATALOGO_DB.exists():
        raise FileNotFoundError(f"No se encontró Master_FINAL.db en {CARPETA_DATA}")
    if dest.exists() and _base_particular_es_valida(dest):
        return
    if dest.exists():
        dest.unlink()
    shutil.copy2(str(CATALOGO_DB), str(dest))
    _conn = sqlite3.connect(str(dest))
    _asegurar_tablas_certificados(_conn)
    _conn.close()


def conectar_base_particular(carpeta_data: Path) -> sqlite3.Connection:
    crear_base_particular(carpeta_data)
    ruta = carpeta_data / "BaseParticular.db"
    conn = sqlite3.connect(str(ruta))
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    _asegurar_tablas_certificados(conn)  # migración automática para obras existentes
    return conn


def _separar_variante(cod: str) -> tuple[str, str]:
    if cod and cod[-1] in ('S', 'E', 'X', 'T'):
        return cod[:-1], cod[-1]
    return cod, ' '


def _build_id_rs_lookup(cur) -> tuple[list, callable, callable]:
    todos = cur.execute("""
        SELECT cod_rubro, designacion, id_rs_ini, id_rs_fin, es_padre, cod_padre
        FROM rubros
        WHERE id_rs_ini IS NOT NULL AND id_rs_fin IS NOT NULL
        ORDER BY es_padre DESC, cod_rubro
    """).fetchall()

    hijos  = [r for r in todos if r["es_padre"] == 0]
    padres = [r for r in todos if r["es_padre"] == 1]
    padre_nombre = {r["cod_rubro"]: r["designacion"] for r in padres}

    rubros_ui = []
    vistos = set()
    for r in sorted(padres, key=lambda x: x["id_rs_ini"]):
        if r["designacion"] not in vistos:
            rubros_ui.append(r["designacion"])
            vistos.add(r["designacion"])

    def id_rs_to_rubro_padre(id_rs_val):
        if not id_rs_val:
            return None
        for r in hijos:
            if r["id_rs_ini"] <= id_rs_val <= r["id_rs_fin"]:
                return padre_nombre.get(r["cod_padre"], r["designacion"])
        for r in padres:
            if r["id_rs_ini"] <= id_rs_val <= r["id_rs_fin"]:
                return r["designacion"]
        return None

    def id_rs_to_subrubro(id_rs_val):
        if not id_rs_val:
            return None
        for r in hijos:
            if r["id_rs_ini"] <= id_rs_val <= r["id_rs_fin"]:
                return r["designacion"]
        return None

    return rubros_ui, id_rs_to_rubro_padre, id_rs_to_subrubro



def _normalizar_cod_ins(v) -> str:
    """Normaliza cod_ins preservando ceros significativos.
    SQLite INTEGER affinity elimina ceros: '000114' -> 114, '000258' -> 258.
    Regla: codigo numerico de 1-3 digitos -> zero-pad a 6.
    Codigos de 4+ digitos tienen su formato correcto en el DB y no se tocan.
    """
    s = str(v).strip()
    if s.isdigit() and len(s) <= 3:
        return s.zfill(6)
    return s


def cargar_maestro_desde_db(carpeta_data: Path) -> dict:
    conn = conectar_base_particular(carpeta_data)
    cur  = conn.cursor()

    rubros_ui, id_rs_to_padre, id_rs_to_subrubro = _build_id_rs_lookup(cur)

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

    rubros_con_tareas = [r for r in rubros_ui if tareas_por_rubro.get(r)]

    insumos = {}
    for row in cur.execute("SELECT cod_ins, descripcion, unidad FROM insumos").fetchall():
        cod = _normalizar_cod_ins(row["cod_ins"])
        insumos[cod] = {
            "cod":    cod,
            "nombre": row["descripcion"] or "",
            "unidad": row["unidad"] or "",
        }

    incidencias = {}
    for row in cur.execute("SELECT cod_tar, cod_ins, cantidad, unidad FROM incidencias").fetchall():
        cod_tar = row["cod_tar"]
        if cod_tar not in incidencias:
            incidencias[cod_tar] = []
        incidencias[cod_tar].append({
            "cod_ins":  _normalizar_cod_ins(row["cod_ins"]),
            "unidad":   row["unidad"] or "",
            "cantidad": row["cantidad"] or 0.0,
        })

    conn.close()

    # DEBUG — remove after fix
    try:
        _dbg = Path(r"C:\Dropbox\Claude\Costos_de_construccion\DEBUG_MAESTRO.txt")
        with open(_dbg, "w", encoding="utf-8") as _f:
            # Sample of insumos keys
            _f.write(f"=== insumos keys ({len(insumos)}) — first 20 ===\n")
            for _k in sorted(insumos.keys())[:20]:
                _f.write(f"  {repr(_k)}\n")
            # Sample of incidencias cod_ins values
            _f.write(f"\n=== incidencias cod_ins unique values — first 20 ===\n")
            _seen = set()
            for _ct, _lst in incidencias.items():
                for _inc in _lst:
                    _c = _inc["cod_ins"]
                    if _c not in _seen:
                        _seen.add(_c)
                        _raw = _c
                        _f.write(f"  cod_ins={repr(_raw)} type={type(_raw).__name__}\n")
                    if len(_seen) >= 20:
                        break
                if len(_seen) >= 20:
                    break
    except Exception:
        pass
    # END DEBUG

    return {
        "rubros":         rubros_con_tareas,
        "tareas":         tareas_por_rubro,
        "tareas_por_cod": tareas_por_cod,
        "insumos":        insumos,
        "incidencias":    incidencias,
    }


class Obra:
    def __init__(self, numero: str, nombre: str, ubicacion: str = ""):
        self.numero          = numero.strip().zfill(3)
        self.nombre          = nombre.strip()
        self.ubicacion       = ubicacion.strip()
        self.comitente       = ""
        self.id_comitente    = None
        self.fecha_creacion  = datetime.now().strftime("%Y-%m-%d")
        self.archivo_precios = ""
        self.version         = 0
        self.estado          = "activo"
        self.items_presupuesto: list = []
        self.tareas: dict = {}
        self.precios: dict = {}
        self.precios_tarea: dict = {}

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

    def calcular_insumos(self, incidencias: dict) -> dict:
        resultado = {}
        for it in self.items_presupuesto:
            if it.get("es_rubro") or not it.get("cod_tar"):
                continue
            cod_tar  = it["cod_tar"]
            subcont  = (it.get("subcontrato") or "").strip().upper()
            cant_tar = it.get("cantidad", 0) or 0
            cod_buscar = cod_tar + subcont if subcont else cod_tar
            lista_inc = incidencias.get(cod_buscar, []) if subcont else incidencias.get(cod_tar, [])
            for inc in lista_inc:
                cod_ins  = inc["cod_ins"]
                cant_ins = inc["cantidad"] * cant_tar
                if cod_ins not in resultado:
                    resultado[cod_ins] = {
                        "cod_ins":        cod_ins,
                        "unidad":         inc["unidad"],
                        "cantidad_total": 0.0,
                        "tareas_origen":  [],
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

    def inicializar(self):
        _asegurar_carpetas()
        _inicializar_datos_obras()
        self.carpeta_data.mkdir(parents=True, exist_ok=True)
        self.carpeta_precios.mkdir(parents=True, exist_ok=True)
        crear_base_particular(self.carpeta_data)
        self.version = 0
        self._escribir_json()
        _actualizar_db(self)

    def guardar(self, nueva_version: bool = False, nota: str = ""):
        _asegurar_carpetas()
        _inicializar_datos_obras()
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
            "tareas":            self.tareas,
            "precios":           self.precios,
            "precios_tarea":     self.precios_tarea,
        }
        with open(self.ruta_json, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)

    def _registrar_variacion(self, nota: str):
        ruta = self.carpeta_data / "variaciones.txt"
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
        linea = (f"obra{self.version:03d}.json  —  {fecha}"
                 + (f"  —  {nota}" if nota else "") + "\n")
        with open(ruta, "a", encoding="utf-8") as f:
            if self.version == 1:
                f.write(f"obra000.json  —  {self.fecha_creacion}  —  Cotización inicial\n")
            f.write(linea)

    @classmethod
    def cargar(cls, numero: str) -> "Obra":
        _inicializar_datos_obras()
        num = numero.strip().zfill(3)
        carpeta_data = CARPETA_OBRAS / f"Obra{num}" / "data"
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
        obra.precios           = datos.get("precios", {})
        obra.precios_tarea     = datos.get("precios_tarea", {})
        _completar_desde_db(obra)
        if not obra.items_presupuesto and obra.tareas:
            obra.items_presupuesto = _migrar_tareas_a_items(obra.tareas)
        if not obra.ruta_base_particular.exists():
            crear_base_particular(obra.carpeta_data)
        return obra

    @classmethod
    def cargar_version(cls, ruta_json) -> "Obra":
        _inicializar_datos_obras()
        ruta = Path(ruta_json)
        with open(ruta, encoding="utf-8") as f:
            datos = json.load(f)
        obra = cls(datos["numero"], datos["nombre"], datos.get("ubicacion", ""))
        obra.fecha_creacion    = datos.get("fecha_creacion", "")
        obra.version           = datos.get("version", 0)
        obra.archivo_precios   = datos.get("archivo_precios", "")
        obra.items_presupuesto = datos.get("items_presupuesto", [])
        obra.tareas            = datos.get("tareas", {})
        obra.precios           = datos.get("precios", {})
        obra.precios_tarea     = datos.get("precios_tarea", {})
        _completar_desde_db(obra)
        if not obra.items_presupuesto and obra.tareas:
            obra.items_presupuesto = _migrar_tareas_a_items(obra.tareas)
        if not obra.ruta_base_particular.exists():
            crear_base_particular(obra.carpeta_data)
        return obra

    @classmethod
    def existe(cls, numero: str) -> bool:
        _inicializar_datos_obras()
        num = numero.strip().zfill(3)
        conn = _conectar_datos_obras()
        row = conn.execute("SELECT 1 FROM obras WHERE numero=?", (num,)).fetchone()
        conn.close()
        return row is not None

    def eliminar(self):
        if self.carpeta.exists():
            shutil.rmtree(self.carpeta)
        _eliminar_de_db(self.numero)

    def listar_versiones(self) -> list[dict]:
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


def _migrar_tareas_a_items(tareas: dict) -> list:
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


def _conectar_datos_obras() -> sqlite3.Connection:
    _inicializar_datos_obras()
    conn = sqlite3.connect(str(DATOS_OBRAS_DB))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _conectar_master() -> sqlite3.Connection:
    return _conectar_datos_obras()


def _actualizar_db(obra: "Obra"):
    conn = _conectar_datos_obras()
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
        "comitente_texto":  obra.comitente,
        "fecha_creacion":   obra.fecha_creacion,
        "archivo_precios":  obra.archivo_precios,
        "estado":           obra.estado,
    })
    conn.commit()
    conn.close()


def _eliminar_de_db(numero: str):
    conn = _conectar_datos_obras()
    conn.execute("DELETE FROM obras WHERE numero=?", (numero,))
    conn.commit()
    conn.close()


def _completar_desde_db(obra: "Obra"):
    try:
        conn = _conectar_datos_obras()
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
            obra.comitente       = row["nombre_comitente"] or row["comitente_texto"] or ""
            if not obra.archivo_precios:
                obra.archivo_precios = row["archivo_precios"] or ""
    except Exception:
        pass


def listar_obras() -> list:
    try:
        conn = _conectar_datos_obras()
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


def listar_comitentes() -> list:
    conn = _conectar_datos_obras()
    rows = conn.execute("SELECT * FROM comitentes ORDER BY nombre").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def crear_comitente(nombre: str, contacto: str = "", telefono: str = "",
                    email: str = "", notas: str = "") -> int:
    conn = _conectar_datos_obras()
    cur = conn.execute(
        "INSERT INTO comitentes(nombre,contacto,telefono,email,notas) VALUES (?,?,?,?,?)",
        (nombre, contacto, telefono, email, notas)
    )
    id_nuevo = cur.lastrowid
    conn.commit()
    conn.close()
    return id_nuevo


# ---------------------------------------------------------------------------
# Certificados / Etapas
# ---------------------------------------------------------------------------

def listar_certificados(carpeta_data: Path) -> list[dict]:
    """Devuelve todos los certificados de la obra, ordenados por id."""
    conn = conectar_base_particular(carpeta_data)
    rows = conn.execute(
        "SELECT id_certificado, nombre, fecha, estado, notas "
        "FROM certificados ORDER BY id_certificado"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def crear_certificado(carpeta_data: Path, nombre: str,
                      fecha: str = "", notas: str = "") -> int:
    """Crea un certificado nuevo en estado 'borrador'. Devuelve su id."""
    from datetime import date
    conn = conectar_base_particular(carpeta_data)
    cur = conn.execute(
        "INSERT INTO certificados (nombre, fecha, estado, notas) VALUES (?,?,?,?)",
        (nombre, fecha or date.today().isoformat(), "borrador", notas)
    )
    id_nuevo = cur.lastrowid
    conn.commit()
    conn.close()
    return id_nuevo


def agregar_tareas_certificado(carpeta_data: Path, id_certificado: int,
                               tareas: list[dict]):
    """
    Agrega o actualiza tareas en un certificado.
    Cada elemento de `tareas` debe ser:
        {"cod_tar": str, "subcontrato": str (opcional), "porcentaje": float (opcional)}
    """
    conn = conectar_base_particular(carpeta_data)
    for t in tareas:
        conn.execute(
            """INSERT INTO certificado_tareas (id_certificado, cod_tar, subcontrato, porcentaje)
               VALUES (?,?,?,?)
               ON CONFLICT(id_certificado, cod_tar, subcontrato)
               DO UPDATE SET porcentaje = excluded.porcentaje""",
            (id_certificado, t["cod_tar"], t.get("subcontrato", ""), t.get("porcentaje", 100.0))
        )
    conn.commit()
    conn.close()


def listar_tareas_certificado(carpeta_data: Path, id_certificado: int) -> list[dict]:
    """Devuelve las tareas asignadas a un certificado."""
    conn = conectar_base_particular(carpeta_data)
    rows = conn.execute(
        "SELECT cod_tar, subcontrato, porcentaje "
        "FROM certificado_tareas WHERE id_certificado=? ORDER BY cod_tar",
        (id_certificado,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def quitar_tareas_certificado(carpeta_data: Path, id_certificado: int,
                              tareas: list[dict]):
    """Elimina tareas específicas de un certificado."""
    conn = conectar_base_particular(carpeta_data)
    for t in tareas:
        conn.execute(
            "DELETE FROM certificado_tareas "
            "WHERE id_certificado=? AND cod_tar=? AND subcontrato=?",
            (id_certificado, t["cod_tar"], t.get("subcontrato", ""))
        )
    conn.commit()
    conn.close()


def cerrar_certificado(carpeta_data: Path, id_certificado: int):
    """Marca un certificado como 'cerrado' (no editable)."""
    conn = conectar_base_particular(carpeta_data)
    conn.execute(
        "UPDATE certificados SET estado='cerrado' WHERE id_certificado=?",
        (id_certificado,)
    )
    conn.commit()
    conn.close()


def eliminar_certificado(carpeta_data: Path, id_certificado: int):
    """Elimina un certificado y sus tareas (CASCADE)."""
    conn = conectar_base_particular(carpeta_data)
    conn.execute("DELETE FROM certificados WHERE id_certificado=?", (id_certificado,))
    conn.commit()
    conn.close()


def resumen_certificados(carpeta_data: Path, items_presupuesto: list) -> list[dict]:
    """
    Resumen comparativo por certificado.
    Calcula total ejecutado = precio_unitario * cantidad * porcentaje/100
    para cada tarea del certificado, usando los datos del presupuesto activo.

    Retorna lista de dicts:
        {id_certificado, nombre, estado, fecha, total_ejecutado, tareas_count}
    """
    # Índice (cod_tar, subcontrato) -> item del presupuesto
    idx = {}
    for it in items_presupuesto:
        if it.get("es_rubro"):
            continue
        key = (it.get("cod_tar", ""), (it.get("subcontrato") or "").strip())
        idx[key] = it

    conn = conectar_base_particular(carpeta_data)
    certs = conn.execute(
        "SELECT id_certificado, nombre, estado, fecha FROM certificados ORDER BY id_certificado"
    ).fetchall()
    resultado = []
    for c in certs:
        tareas = conn.execute(
            "SELECT cod_tar, subcontrato, porcentaje "
            "FROM certificado_tareas WHERE id_certificado=?",
            (c["id_certificado"],)
        ).fetchall()
        total = 0.0
        for t in tareas:
            key = (t["cod_tar"], (t["subcontrato"] or "").strip())
            it = idx.get(key)
            if it:
                precio = it.get("precio_unitario", 0) or 0
                cant   = it.get("cantidad", 0) or 0
                total += precio * cant * (t["porcentaje"] / 100.0)
        resultado.append({
            "id_certificado":  c["id_certificado"],
            "nombre":          c["nombre"],
            "estado":          c["estado"],
            "fecha":           c["fecha"],
            "total_ejecutado": total,
            "tareas_count":    len(tareas),
        })
    conn.close()
    return resultado
