"""
rubros_tareas.py
Interfaz para asignar Tareas (COD_TAR, Descripción, Unidad) a Rubros.

Uso:
    python rubros_tareas.py
    python rubros_tareas.py --rubros /ruta/Rubros_solos.xlsx --tareas /ruta/Tareas_Master.xlsx

Panel izquierdo : Rubros_solos   → columnas: COD_RUBRO | Designación | Tareas asignadas
Panel derecho   : Tareas_Master  → columnas: COD_TAR | Descripción | Unidad

- Clic en un Rubro (izquierda)      → selecciona el rubro destino y expande sus tareas.
- Doble clic / Ctrl+clic en tareas  → selección múltiple en la derecha.
- Botón "➕ Asignar"  o doble clic  → copia COD_TAR + Descripción + Unidad al rubro activo.
- Clic en tarea hija (izquierda)    → habilita edición o eliminación de esa tarea.
- Botón "✏ Editar tarea"           → abre ventana para editar COD_TAR/Descripción/Unidad.
- Botón "➕ Agregar manual"         → agrega una tarea nueva debajo de la tarea seleccionada
                                      (o al final del rubro si no hay tarea seleccionada).
- Botón "🗑 Quitar tarea"          → elimina la tarea hija seleccionada del rubro.
- Botón "💾 Guardar"               → graba el resultado como Excel.
"""

import sys
import os
import argparse
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog

import pandas as pd

# ── Rutas por defecto ──────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_RUBROS = os.path.join(SCRIPT_DIR, "Rubros_solos.xlsx")
DEFAULT_TAREAS = os.path.join(SCRIPT_DIR, "Tareas_Master.xlsx")


# ── Carga de datos ─────────────────────────────────────────────────────────────

def cargar_rubros(path: str) -> pd.DataFrame:
    engine = "xlrd" if path.lower().endswith(".xls") else "openpyxl"
    df = pd.read_excel(path, engine=engine)
    df.columns = [c.strip() for c in df.columns]
    for col in ("COD_RUBRO", "Designación", "COD_TAR"):
        if col not in df.columns:
            df[col] = ""
    df["COD_RUBRO"]   = df["COD_RUBRO"].fillna("").astype(str).str.strip()
    df["Designación"] = df["Designación"].fillna("").astype(str)
    df["COD_TAR"]     = df["COD_TAR"].fillna("").astype(str).str.strip()
    df["COD_TAR"]     = df["COD_TAR"].replace("nan", "")

    # Si el archivo tiene una fila por tarea (formato guardado), agrupar
    # Detectamos esto cuando hay filas repetidas de COD_RUBRO
    if df["COD_RUBRO"].duplicated().any():
        grupos = {}  # cod_rubro -> {"designacion": str, "cod_tars": [str]}
        orden  = []  # para mantener el orden original
        for _, row in df.iterrows():
            key = (str(row["COD_RUBRO"]).strip(), str(row["Designación"]).strip())
            if key not in grupos:
                grupos[key] = []
                orden.append(key)
            cod = str(row["COD_TAR"]).strip()
            if cod and cod.lower() != "nan":
                grupos[key].append(cod)
        rows = []
        for key in orden:
            cod_rubro, designacion = key
            rows.append({
                "COD_RUBRO":   cod_rubro,
                "Designación": designacion,
                "COD_TAR":     ":".join(grupos[key]),
            })
        df = pd.DataFrame(rows)

    return df.reset_index(drop=True)


def cargar_tareas(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    df.columns = [c.strip() for c in df.columns]
    rename = {}
    for c in df.columns:
        cl = c.lower()
        if cl in ("descripción", "descripcion", "designación", "designacion"):
            rename[c] = "Descripción"
    if rename:
        df = df.rename(columns=rename)
    for col in ("COD_TAR", "Descripción", "Unidad"):
        if col not in df.columns:
            df[col] = ""
    df["COD_TAR"]     = df["COD_TAR"].fillna("").astype(str).str.strip()
    df["Descripción"] = df["Descripción"].fillna("").astype(str)
    df["Unidad"]      = df["Unidad"].fillna("").astype(str)
    return df.reset_index(drop=True)


# ── Modelo de datos del lado izquierdo ────────────────────────────────────────
# Estructura: list of dict
#   { "cod_rubro": str, "designacion": str,
#     "tareas": [ {"cod_tar": str, "descripcion": str, "unidad": str}, ... ] }

def rubros_a_modelo(df: pd.DataFrame) -> list:
    tiene_desc = "Descripción" in df.columns
    tiene_uni  = "Unidad"      in df.columns
    modelo = []
    for _, row in df.iterrows():
        tareas = []
        cod_tar_raw = str(row["COD_TAR"]).strip()
        if cod_tar_raw and cod_tar_raw.lower() != "nan":
            for c in cod_tar_raw.split(":"):
                c = c.strip()
                if c:
                    desc = str(row.get("Descripción", "")) if tiene_desc else ""
                    uni  = str(row.get("Unidad",      "")) if tiene_uni  else ""
                    tareas.append({"cod_tar": c, "descripcion": desc, "unidad": uni})
        modelo.append({
            "cod_rubro":   str(row["COD_RUBRO"]).strip(),
            "designacion": str(row["Designación"]).strip(),
            "tareas":      tareas,
        })
    return modelo


def modelo_a_df(modelo: list) -> pd.DataFrame:
    """Reconstruye un DataFrame con una fila por (rubro, tarea).
    Si un rubro no tiene tareas, igual aparece con una fila vacía."""
    rows = []
    for rubro in modelo:
        if rubro["tareas"]:
            for t in rubro["tareas"]:
                rows.append({
                    "COD_RUBRO":   rubro["cod_rubro"],
                    "Designación": rubro["designacion"],
                    "COD_TAR":     t["cod_tar"],
                    "Descripción": t["descripcion"],
                    "Unidad":      t["unidad"],
                })
        else:
            rows.append({
                "COD_RUBRO":   rubro["cod_rubro"],
                "Designación": rubro["designacion"],
                "COD_TAR":     "",
                "Descripción": "",
                "Unidad":      "",
            })
    return pd.DataFrame(rows)


# ── Diálogo de edición ────────────────────────────────────────────────────────

class DialogoTarea(tk.Toplevel):
    """Ventana modal para editar/agregar una tarea."""

    def __init__(self, parent, titulo: str,
                 cod_tar: str = "", descripcion: str = "", unidad: str = ""):
        super().__init__(parent)
        self.title(titulo)
        self.resizable(False, False)
        self.grab_set()
        self.configure(bg="#2b2b2b")
        self.result = None

        BG   = "#2b2b2b"
        FG   = "#d4d4d4"
        EBG  = "#4a4a4a"
        ACC  = "#4e9dde"

        pad = {"padx": 10, "pady": 5}

        def lbl(text):
            return tk.Label(self, text=text, bg=BG, fg=ACC,
                            font=("Segoe UI", 9, "bold"), anchor="w")
        def ent(var, width=30):
            return tk.Entry(self, textvariable=var, width=width,
                            bg=EBG, fg=FG, insertbackground=FG,
                            relief="flat", font=("Segoe UI", 9))

        self.v_cod  = tk.StringVar(value=cod_tar)
        self.v_desc = tk.StringVar(value=descripcion)
        self.v_uni  = tk.StringVar(value=unidad)

        lbl("COD_TAR:").grid(row=0, column=0, sticky="w", **pad)
        ent(self.v_cod, 16).grid(row=0, column=1, sticky="ew", **pad)

        lbl("Descripción:").grid(row=1, column=0, sticky="w", **pad)
        ent(self.v_desc, 40).grid(row=1, column=1, sticky="ew", **pad)

        lbl("Unidad:").grid(row=2, column=0, sticky="w", **pad)
        ent(self.v_uni, 10).grid(row=2, column=1, sticky="ew", **pad)

        btn_f = tk.Frame(self, bg=BG)
        btn_f.grid(row=3, column=0, columnspan=2, pady=10)

        def _ok():
            cod  = self.v_cod.get().strip()
            desc = self.v_desc.get().strip()
            uni  = self.v_uni.get().strip()
            if not cod:
                messagebox.showwarning("Campo vacío", "COD_TAR no puede estar vacío.",
                                       parent=self)
                return
            self.result = {"cod_tar": cod, "descripcion": desc, "unidad": uni}
            self.destroy()

        def _cancel():
            self.destroy()

        def _btn(parent, text, cmd):
            return tk.Button(parent, text=text, command=cmd,
                             bg="#4a4a4a", fg=FG,
                             activebackground="#5a5a5a", activeforeground="white",
                             relief="flat", padx=12, pady=4,
                             font=("Segoe UI", 9), cursor="hand2")

        _btn(btn_f, "✔  Aceptar", _ok).pack(side="left", padx=6)
        _btn(btn_f, "✖  Cancelar", _cancel).pack(side="left", padx=6)

        self.columnconfigure(1, weight=1)
        self.bind("<Return>", lambda e: _ok())
        self.bind("<Escape>", lambda e: _cancel())

        # Centrar sobre la ventana padre
        self.update_idletasks()
        pw = parent.winfo_rootx() + parent.winfo_width()  // 2
        ph = parent.winfo_rooty() + parent.winfo_height() // 2
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{pw - w//2}+{ph - h//2}")


# ── Aplicación ─────────────────────────────────────────────────────────────────

class App(tk.Tk):

    # Columnas del tree izquierdo (padre = rubro, hijos = tareas)
    COL_IZQ  = ("COD_RUBRO", "Designación / Descripción", "COD_TAR", "Unidad")
    COL_IZQ_W = (70, 340, 90, 60)

    # Columnas del tree derecho
    COL_DER  = ("COD_TAR", "Descripción", "Unidad")
    COL_DER_W = (90, 360, 60)

    def __init__(self, path_rubros: str, path_tareas: str):
        super().__init__()
        self.title("Rubros ↔ Tareas")
        self.geometry("1300x750")
        self.minsize(960, 520)

        # Paleta
        self.BG       = "#2b2b2b"
        self.BG_FRAME = "#3c3f41"
        self.FG       = "#d4d4d4"
        self.SEL_BG   = "#214283"
        self.ACCENT   = "#4e9dde"
        self.ENTRY_BG = "#4a4a4a"
        self.GREEN    = "#a0c86e"
        self.configure(bg=self.BG)

        self.path_rubros = path_rubros
        self.path_tareas = path_tareas

        # Modelo
        df_r = cargar_rubros(path_rubros)
        self.modelo: list = rubros_a_modelo(df_r)
        self.df_tareas: pd.DataFrame = cargar_tareas(path_tareas)

        # Enriquecer descripciones de tareas ya asignadas desde Tareas_Master
        self._enriquecer_modelo()

        # Estado de selección
        self.rubro_sel_idx:  int | None = None  # índice en self.modelo
        self.tarea_sel_idx:  int | None = None  # índice en rubro["tareas"]

        self._build_ui()
        self._poblar_rubros()
        self._poblar_tareas()

    # ── Enriquecimiento ───────────────────────────────────────────────────────

    def _enriquecer_modelo(self):
        """Completa descripción y unidad de tareas ya asignadas buscando en df_tareas."""
        lookup = {}
        for _, row in self.df_tareas.iterrows():
            c = str(row["COD_TAR"]).strip()
            if c:
                lookup[c] = {
                    "descripcion": str(row["Descripción"]),
                    "unidad":      str(row["Unidad"]),
                }
        for rubro in self.modelo:
            for t in rubro["tareas"]:
                if t["cod_tar"] in lookup and not t["descripcion"]:
                    t["descripcion"] = lookup[t["cod_tar"]]["descripcion"]
                    t["unidad"]      = lookup[t["cod_tar"]]["unidad"]

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self.style.configure("Treeview",
                             background="#3c3f41", foreground=self.FG,
                             fieldbackground="#3c3f41", rowheight=22,
                             font=("Segoe UI", 9))
        self.style.configure("Treeview.Heading",
                             background="#4a4a4a", foreground=self.ACCENT,
                             font=("Segoe UI", 9, "bold"), relief="flat")
        self.style.map("Treeview",
                       background=[("selected", self.SEL_BG)],
                       foreground=[("selected", "white")])
        self.style.configure("TScrollbar",
                             background="#4a4a4a", troughcolor="#2b2b2b",
                             arrowcolor=self.FG)

        # ── Barra superior ────────────────────────────────────────────────────
        top = tk.Frame(self, bg=self.BG, pady=6)
        top.pack(fill="x", padx=10)

        tk.Label(top, text="Rubros  ↔  Tareas",
                 bg=self.BG, fg=self.ACCENT,
                 font=("Segoe UI", 13, "bold")).pack(side="left")

        btn_f = tk.Frame(top, bg=self.BG)
        btn_f.pack(side="right")
        self._btn(btn_f, "💾  Guardar",       self._guardar).pack(side="right", padx=4)
        self._btn(btn_f, "📂  Abrir archivos…", self._abrir_archivos).pack(side="right", padx=4)

        # ── Cuerpo ────────────────────────────────────────────────────────────
        paned = tk.PanedWindow(self, orient=tk.HORIZONTAL,
                               bg=self.BG, sashwidth=6,
                               sashrelief="flat", sashpad=2)
        paned.pack(fill="both", expand=True, padx=10, pady=(0, 8))

        frame_izq = self._panel(paned, "📋  Rubros  (clic para seleccionar)")
        frame_der = self._panel(paned, "📦  Tareas Master  (doble clic para asignar)")
        paned.add(frame_izq, minsize=380)
        paned.add(frame_der, minsize=380)

        # ── Panel izquierdo ───────────────────────────────────────────────────
        srch_izq = self._search_bar(frame_izq, self._filtrar_rubros)
        srch_izq.pack(fill="x", padx=6, pady=4)

        self.tree_izq = self._tree(frame_izq, self.COL_IZQ, self.COL_IZQ_W,
                                   selectmode="browse", show="tree headings")
        self.tree_izq._container.pack(fill="both", expand=True, padx=6, pady=(0, 4))
        self.tree_izq.bind("<<TreeviewSelect>>", self._on_sel_izq)
        self.tree_izq.bind("<Double-1>",         self._on_doble_izq)

        # Botones de acción izquierda
        acc_f = tk.Frame(frame_izq, bg=self.BG_FRAME)
        acc_f.pack(fill="x", padx=6, pady=(0, 4))
        self.btn_editar  = self._btn(acc_f, "✏  Editar tarea",    self._editar_tarea)
        self.btn_agregar = self._btn(acc_f, "➕  Agregar manual",  self._agregar_manual)
        self.btn_quitar  = self._btn(acc_f, "🗑  Quitar tarea",    self._quitar_tarea)
        self.btn_editar .pack(side="left", padx=2)
        self.btn_agregar.pack(side="left", padx=2)
        self.btn_quitar .pack(side="left", padx=2)
        self._actualizar_botones()

        self.lbl_izq = tk.Label(frame_izq, text="",
                                bg=self.BG_FRAME, fg=self.ACCENT,
                                font=("Segoe UI", 8, "italic"), anchor="w")
        self.lbl_izq.pack(fill="x", padx=6, pady=(0, 4))

        # ── Panel derecho ─────────────────────────────────────────────────────
        srch_der = self._search_bar(frame_der, self._filtrar_tareas)
        srch_der.pack(fill="x", padx=6, pady=4)

        self.tree_der = self._tree(frame_der, self.COL_DER, self.COL_DER_W,
                                   selectmode="extended")
        self.tree_der._container.pack(fill="both", expand=True, padx=6, pady=(0, 4))
        self.tree_der.bind("<Double-1>", self._asignar_tareas)

        # Botón asignar
        der_acc = tk.Frame(frame_der, bg=self.BG_FRAME)
        der_acc.pack(fill="x", padx=6, pady=(0, 4))
        self._btn(der_acc, "➕  Asignar al rubro", self._asignar_tareas).pack(side="left", padx=2)

        self.lbl_der = tk.Label(frame_der, text="",
                                bg=self.BG_FRAME, fg=self.GREEN,
                                font=("Segoe UI", 8, "italic"), anchor="w")
        self.lbl_der.pack(fill="x", padx=6, pady=(0, 4))

        # ── Barra de estado ───────────────────────────────────────────────────
        self.statusbar = tk.Label(self, text="Listo.",
                                  bg="#1e1e1e", fg="#888",
                                  font=("Segoe UI", 8), anchor="w", padx=10)
        self.statusbar.pack(fill="x", side="bottom")

    def _panel(self, parent, title: str) -> tk.Frame:
        f = tk.Frame(parent, bg=self.BG_FRAME, bd=0)
        tk.Label(f, text=title, bg=self.BG_FRAME, fg=self.ACCENT,
                 font=("Segoe UI", 9, "bold"),
                 anchor="w", padx=6, pady=6).pack(fill="x")
        ttk.Separator(f, orient="horizontal").pack(fill="x")
        return f

    def _btn(self, parent, text: str, cmd) -> tk.Button:
        return tk.Button(parent, text=text, command=cmd,
                         bg="#4a4a4a", fg=self.FG,
                         activebackground="#5a5a5a", activeforeground="white",
                         relief="flat", padx=8, pady=4,
                         font=("Segoe UI", 9), cursor="hand2")

    def _search_bar(self, parent, cmd) -> tk.Frame:
        f = tk.Frame(parent, bg=self.BG_FRAME)
        tk.Label(f, text="🔍", bg=self.BG_FRAME, fg=self.FG,
                 font=("Segoe UI", 10)).pack(side="left", padx=(0, 4))
        var = tk.StringVar()
        var.trace_add("write", lambda *_: cmd(var.get()))
        e = tk.Entry(f, textvariable=var,
                     bg=self.ENTRY_BG, fg=self.FG,
                     insertbackground=self.FG,
                     relief="flat", font=("Segoe UI", 9))
        e.pack(fill="x", expand=True)
        return f

    def _tree(self, parent, cols: tuple, widths: tuple,
              selectmode: str = "browse", show: str = "headings") -> ttk.Treeview:
        frame = tk.Frame(parent, bg=self.BG_FRAME)
        tree = ttk.Treeview(frame, columns=cols, show=show, selectmode=selectmode)
        vsb  = ttk.Scrollbar(frame, orient="vertical",   command=tree.yview)
        hsb  = ttk.Scrollbar(frame, orient="horizontal",  command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        for col, w in zip(cols, widths):
            tree.heading(col, text=col,
                         command=lambda c=col, t=tree: self._sort_col(t, c))
            tree.column(col, width=w, minwidth=40)

        # Ajuste primera columna en tree izquierdo (con árbol)
        if show == "tree headings":
            tree.column("#0", width=22, minwidth=22, stretch=False)

        tree.tag_configure("rubro",    background="#2e4a2e", foreground="#b8e0a0",
                           font=("Segoe UI", 9, "bold"))
        tree.tag_configure("tarea",    background="#3c3f41", foreground=self.FG)
        tree.tag_configure("par",      background="#383838")
        tree.tag_configure("impar",    background="#3c3f41")
        # Tareas ya asignadas en algún rubro (naranja suave)
        tree.tag_configure("asignada", background="#4a3a1a", foreground="#f0c060")
        # Tareas asignadas al rubro actualmente seleccionado (verde)
        tree.tag_configure("en_rubro", background="#1e3d1e", foreground="#88e070")

        tree._container = frame
        return tree

    # ── Poblar árboles ────────────────────────────────────────────────────────

    def _iid_rubro(self, ri: int) -> str:
        return f"R_{ri}"

    def _iid_tarea(self, ri: int, ti: int) -> str:
        return f"T_{ri}_{ti}"

    def _poblar_rubros(self, filtro: str = ""):
        self.tree_izq.delete(*self.tree_izq.get_children())
        fl = filtro.lower()
        for ri, rubro in enumerate(self.modelo):
            if fl and fl not in rubro["designacion"].lower() and \
               fl not in rubro["cod_rubro"].lower():
                # Verificar si alguna tarea hija coincide
                if not any(fl in t["cod_tar"].lower() or
                           fl in t["descripcion"].lower()
                           for t in rubro["tareas"]):
                    continue

            iid_r = self._iid_rubro(ri)
            n_tar = len(rubro["tareas"])
            label_tar = f"  [{n_tar} tarea{'s' if n_tar != 1 else ''}]" if n_tar else ""
            self.tree_izq.insert(
                "", "end", iid=iid_r,
                values=(rubro["cod_rubro"],
                        rubro["designacion"] + label_tar,
                        "", ""),
                tags=("rubro",), open=False
            )
            for ti, t in enumerate(rubro["tareas"]):
                self.tree_izq.insert(
                    iid_r, "end",
                    iid=self._iid_tarea(ri, ti),
                    values=("", t["descripcion"], t["cod_tar"], t["unidad"]),
                    tags=("tarea",)
                )

        # Restaurar selección visual
        self._restaurar_sel()
        total = len(self.tree_izq.get_children())
        self.lbl_izq.config(text=f"{total} rubros mostrados")

    def _restaurar_sel(self):
        if self.rubro_sel_idx is not None:
            iid_r = self._iid_rubro(self.rubro_sel_idx)
            if self.tree_izq.exists(iid_r):
                self.tree_izq.selection_set(iid_r)
                self.tree_izq.see(iid_r)
                self.tree_izq.item(iid_r, open=True)
            if self.tarea_sel_idx is not None:
                iid_t = self._iid_tarea(self.rubro_sel_idx, self.tarea_sel_idx)
                if self.tree_izq.exists(iid_t):
                    self.tree_izq.selection_set(iid_t)
                    self.tree_izq.see(iid_t)

    def _todos_asignados(self) -> set:
        """COD_TAR asignados en cualquier rubro del modelo."""
        s = set()
        for r in self.modelo:
            for t in r["tareas"]:
                if t["cod_tar"]:
                    s.add(t["cod_tar"])
        return s

    def _asignados_rubro_activo(self) -> set:
        """COD_TAR del rubro actualmente seleccionado."""
        if self.rubro_sel_idx is None:
            return set()
        return {t["cod_tar"] for t in self.modelo[self.rubro_sel_idx]["tareas"]}

    def _poblar_tareas(self, filtro: str = ""):
        self.tree_der.delete(*self.tree_der.get_children())
        fl = filtro.lower()
        sub = self.df_tareas
        if fl:
            mask = (sub["COD_TAR"].str.lower().str.contains(fl, na=False) |
                    sub["Descripción"].str.lower().str.contains(fl, na=False))
            sub = sub[mask]

        todos    = self._todos_asignados()
        en_rubro = self._asignados_rubro_activo()
        cnt_rubro  = 0
        cnt_otros  = 0

        for i, (_, row) in enumerate(sub.iterrows()):
            cod = str(row["COD_TAR"]).strip()
            if cod in en_rubro:
                tag = "en_rubro"
                cnt_rubro += 1
            elif cod in todos:
                tag = "asignada"
                cnt_otros += 1
            else:
                tag = "par" if i % 2 == 0 else "impar"
            self.tree_der.insert("", "end",
                                 values=(row["COD_TAR"],
                                         row["Descripción"],
                                         row["Unidad"]),
                                 tags=(tag,))

        total  = len(sub)
        libres = total - cnt_rubro - cnt_otros
        self.lbl_der.config(
            text=f"{total} tareas  |  🟢 {cnt_rubro} en este rubro  "
                 f"🟡 {cnt_otros} en otros rubros  ⬜ {libres} libres")

    # ── Eventos árbol izquierdo ────────────────────────────────────────────────

    def _on_sel_izq(self, event=None):
        sel = self.tree_izq.selection()
        if not sel:
            return
        iid = sel[0]
        if iid.startswith("R_"):
            ri = int(iid[2:])
            self.rubro_sel_idx = ri
            self.tarea_sel_idx = None
            self.tree_izq.item(iid, open=True)
            rubro = self.modelo[ri]
            self.lbl_izq.config(
                text=f"Rubro: {rubro['cod_rubro']} — {rubro['designacion']}  "
                     f"| {len(rubro['tareas'])} tarea(s)")
            self._set_status(f"Rubro activo: {rubro['designacion']}")
            self._poblar_tareas(self._filtro_der_actual())
        elif iid.startswith("T_"):
            _, ri, ti = iid.split("_")
            ri, ti = int(ri), int(ti)
            self.rubro_sel_idx = ri
            self.tarea_sel_idx = ti
            t = self.modelo[ri]["tareas"][ti]
            self.lbl_izq.config(
                text=f"Tarea: {t['cod_tar']} — {t['descripcion']}  [{t['unidad']}]")
            self._set_status(f"Tarea seleccionada: {t['cod_tar']} — {t['descripcion']}")
        self._actualizar_botones()

    def _on_doble_izq(self, event=None):
        """Doble clic en tarea hija → editar."""
        sel = self.tree_izq.selection()
        if sel and sel[0].startswith("T_"):
            self._editar_tarea()

    def _actualizar_botones(self):
        hay_rubro = self.rubro_sel_idx is not None
        hay_tarea = hay_rubro and self.tarea_sel_idx is not None
        state_t = "normal" if hay_tarea  else "disabled"
        state_r = "normal" if hay_rubro  else "disabled"
        self.btn_editar .config(state=state_t)
        self.btn_quitar .config(state=state_t)
        self.btn_agregar.config(state=state_r)

    # ── Asignar tareas desde la derecha ───────────────────────────────────────

    def _asignar_tareas(self, event=None):
        if self.rubro_sel_idx is None:
            messagebox.showwarning("Sin rubro",
                                   "Primero seleccioná un Rubro en el panel izquierdo.")
            return
        sels = self.tree_der.selection()
        if not sels:
            return

        rubro = self.modelo[self.rubro_sel_idx]
        existentes = {t["cod_tar"] for t in rubro["tareas"]}
        nuevas = []
        for iid in sels:
            vals = self.tree_der.item(iid, "values")
            cod, desc, uni = vals[0], vals[1], vals[2]
            if cod and cod not in existentes:
                nuevas.append({"cod_tar": cod, "descripcion": desc, "unidad": uni})
                existentes.add(cod)

        if not nuevas:
            self._set_status("Las tareas seleccionadas ya estaban asignadas.")
            return

        rubro["tareas"].extend(nuevas)
        self._poblar_rubros()
        self._poblar_tareas(self._filtro_der_actual())
        # Expandir rubro y seleccionar la última tarea agregada
        iid_r = self._iid_rubro(self.rubro_sel_idx)
        if self.tree_izq.exists(iid_r):
            self.tree_izq.item(iid_r, open=True)
        self._set_status(
            f"✅ {len(nuevas)} tarea(s) asignadas a «{rubro['designacion']}»")

    # ── Editar tarea ──────────────────────────────────────────────────────────

    def _editar_tarea(self):
        if self.rubro_sel_idx is None or self.tarea_sel_idx is None:
            messagebox.showwarning("Sin tarea", "Seleccioná una tarea en el árbol izquierdo.")
            return
        t = self.modelo[self.rubro_sel_idx]["tareas"][self.tarea_sel_idx]
        dlg = DialogoTarea(self, "✏  Editar tarea",
                           cod_tar=t["cod_tar"],
                           descripcion=t["descripcion"],
                           unidad=t["unidad"])
        self.wait_window(dlg)
        if dlg.result:
            t.update(dlg.result)
            self._poblar_rubros()
            self._set_status(
                f"Tarea editada: {dlg.result['cod_tar']} — {dlg.result['descripcion']}")

    # ── Agregar manual ────────────────────────────────────────────────────────

    def _agregar_manual(self):
        if self.rubro_sel_idx is None:
            messagebox.showwarning("Sin rubro", "Seleccioná un rubro primero.")
            return
        dlg = DialogoTarea(self, "➕  Nueva tarea manual")
        self.wait_window(dlg)
        if dlg.result:
            rubro = self.modelo[self.rubro_sel_idx]
            # Insertar DEBAJO de la tarea seleccionada, o al final
            if self.tarea_sel_idx is not None:
                pos = self.tarea_sel_idx + 1
            else:
                pos = len(rubro["tareas"])
            rubro["tareas"].insert(pos, dlg.result)
            # Actualizar índice de selección de tarea
            self.tarea_sel_idx = pos
            self._poblar_rubros()
            self._set_status(
                f"Tarea manual agregada: {dlg.result['cod_tar']} — {dlg.result['descripcion']}")

    # ── Quitar tarea ──────────────────────────────────────────────────────────

    def _quitar_tarea(self):
        if self.rubro_sel_idx is None or self.tarea_sel_idx is None:
            messagebox.showwarning("Sin tarea", "Seleccioná una tarea en el árbol izquierdo.")
            return
        t = self.modelo[self.rubro_sel_idx]["tareas"][self.tarea_sel_idx]
        ok = messagebox.askyesno("Confirmar",
                                  f"¿Quitar «{t['cod_tar']} — {t['descripcion']}» del rubro?")
        if not ok:
            return
        self.modelo[self.rubro_sel_idx]["tareas"].pop(self.tarea_sel_idx)
        self.tarea_sel_idx = None
        self._poblar_rubros()
        self._actualizar_botones()
        self._set_status("Tarea eliminada del rubro.")

    # ── Guardar ───────────────────────────────────────────────────────────────

    def _guardar(self):
        df_out = modelo_a_df(self.modelo)
        base, _ = os.path.splitext(self.path_rubros)
        sugerido = base + "_con_tareas.xlsx"
        dest = filedialog.asksaveasfilename(
            title="Guardar Rubros con Tareas",
            initialfile=os.path.basename(sugerido),
            initialdir=os.path.dirname(sugerido),
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx"), ("Todos", "*.*")])
        if not dest:
            return
        try:
            df_out.to_excel(dest, index=False)
            self._set_status(f"✅ Guardado: {dest}")
            messagebox.showinfo("Guardado", f"Archivo guardado:\n{dest}")
        except Exception as e:
            messagebox.showerror("Error al guardar", str(e))

    # ── Abrir archivos ────────────────────────────────────────────────────────

    def _abrir_archivos(self):
        nr = filedialog.askopenfilename(
            title="Seleccioná Rubros_solos",
            filetypes=[("Excel", "*.xls *.xlsx"), ("Todos", "*.*")])
        if not nr:
            return
        nt = filedialog.askopenfilename(
            title="Seleccioná Tareas_Master",
            filetypes=[("Excel", "*.xls *.xlsx"), ("Todos", "*.*")])
        if not nt:
            return
        try:
            self.path_rubros = nr
            self.path_tareas = nt
            df_r = cargar_rubros(nr)
            self.modelo = rubros_a_modelo(df_r)
            self.df_tareas = cargar_tareas(nt)
            self._enriquecer_modelo()
            self.rubro_sel_idx = None
            self.tarea_sel_idx = None
            self._poblar_rubros()
            self._poblar_tareas()
            self._actualizar_botones()
            self._set_status("Archivos cargados correctamente.")
        except Exception as e:
            messagebox.showerror("Error al abrir", str(e))

    # ── Filtros ───────────────────────────────────────────────────────────────

    def _filtrar_rubros(self, txt: str):
        self._poblar_rubros(txt)

    def _filtrar_tareas(self, txt: str):
        self._filtro_der = txt
        self._poblar_tareas(txt)

    def _filtro_der_actual(self) -> str:
        return getattr(self, "_filtro_der", "")

    # ── Ordenar columnas (solo árbol derecho) ─────────────────────────────────

    def _sort_col(self, tree: ttk.Treeview, col: str):
        data = [(tree.set(k, col), k) for k in tree.get_children("")]
        data.sort(key=lambda t: t[0].lower())
        for idx, (_, k) in enumerate(data):
            tree.move(k, "", idx)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _set_status(self, msg: str):
        self.statusbar.config(text=msg)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Rubros ↔ Tareas")
    parser.add_argument("--rubros", default=DEFAULT_RUBROS,
                        help="Ruta a Rubros_solos.xlsx")
    parser.add_argument("--tareas", default=DEFAULT_TAREAS,
                        help="Ruta a Tareas_Master.xlsx")
    args = parser.parse_args()

    for label, path in (("Rubros", args.rubros), ("Tareas", args.tareas)):
        if not os.path.exists(path):
            print(f"[AVISO] No se encontró {label}: {path}")

    app = App(args.rubros, args.tareas)
    app.mainloop()


if __name__ == "__main__":
    main()
