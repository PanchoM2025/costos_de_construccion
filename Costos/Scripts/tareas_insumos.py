"""
tareas_insumos.py  v2
Gestión de insumos por tarea con modo revisión secuencial.

Modos:
  • Árbol  (izquierda) : navegar por Rubros → Tarea como siempre
  • Revisión           : recorre TODAS las tareas de Tareas_Master.xlsx 1 x 1
                         con botones ◀ Anterior / Siguiente ▶

Acciones panel derecho (insumos de la tarea activa):
  ➕ Agregar    → buscar insumo existente en la DB y asignar cantidad
  ✎  Editar     → editar cantidad (doble clic o botón)
  🗑  Quitar     → elimina incidencia
  ★  Nuevo       → crea insumo nuevo en DB + Insumos_Master.xlsx y lo asigna
"""

import sys, os, argparse, sqlite3, shutil, re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd

# ── Rutas por defecto ─────────────────────────────────────────────────────────
DIR      = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(DIR, "..", "Data")
DEFAULT_RUBROS  = os.path.join(DATA_DIR, "Rubros_solos_con_tareas.xlsx")
DEFAULT_TAREAS  = os.path.join(DATA_DIR, "Tareas_Master.xlsx")
DEFAULT_DB      = os.path.join(DATA_DIR, "Master_FINAL.db")
DEFAULT_INSUMOS = os.path.join(DATA_DIR, "Insumos_Master.xlsx")


# ── DB helpers ────────────────────────────────────────────────────────────────

def get_con(path):
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con

def incidencias_de_tarea(con, cod_tar):
    return [dict(r) for r in con.execute("""
        SELECT i.rowid, i.cod_tar, i.cod_ins, i.cantidad,
               COALESCE(ins.descripcion,'') AS descripcion,
               COALESCE(ins.unidad,'')      AS unidad
        FROM   incidencias i
        LEFT JOIN insumos ins ON ins.cod_ins = i.cod_ins
        WHERE  i.cod_tar = ?
        ORDER  BY i.cod_ins
    """, (cod_tar,)).fetchall()]

def todos_insumos(con):
    return [dict(r) for r in con.execute(
        "SELECT cod_ins, descripcion, unidad FROM insumos ORDER BY cod_ins"
    ).fetchall()]

def asegurar_tarea_en_db(con, cod_tar, descripcion, unidad):
    existe = con.execute("SELECT 1 FROM tareas WHERE cod_tar=?", (cod_tar,)).fetchone()
    if not existe:
        con.execute(
            "INSERT INTO tareas (cod_tar, descripcion, unidad, activo) VALUES (?,?,?,1)",
            (cod_tar, descripcion or cod_tar, unidad or ""))
        con.commit()
        return True
    return False


# ── Carga Rubros (árbol) ──────────────────────────────────────────────────────

def cargar_rubros_tareas(path):
    df = pd.read_excel(path, dtype=str).fillna("")
    df.columns = [c.strip() for c in df.columns]
    for c in ("COD_RUBRO", "Designación", "COD_TAR", "Descripción", "Unidad"):
        if c not in df.columns:
            df[c] = ""
    modelo, seen = [], {}
    for _, row in df.iterrows():
        key = (row["COD_RUBRO"].strip(), row["Designación"].strip())
        if key not in seen:
            seen[key] = len(modelo)
            modelo.append({"cod_rubro": key[0], "designacion": key[1], "tareas": []})
        cod = row["COD_TAR"].strip()
        if cod:
            modelo[seen[key]]["tareas"].append({
                "cod_tar": cod,
                "descripcion": row["Descripción"].strip(),
                "unidad": row["Unidad"].strip(),
            })
    return modelo


# ── Carga lista plana de tareas (revisión) ────────────────────────────────────

def cargar_lista_tareas(path):
    df = pd.read_excel(path, dtype=str).fillna("")
    df.columns = [c.strip() for c in df.columns]
    tareas = []
    for _, row in df.iterrows():
        cod = str(row.get("COD_TAR","")).strip()
        if cod:
            tareas.append({
                "cod_tar":     cod,
                "descripcion": str(row.get("Descripción","")).strip(),
                "unidad":      str(row.get("Unidad","")).strip(),
            })
    return tareas


# ── Diálogos ──────────────────────────────────────────────────────────────────

BG, FG, EBG, ACC = "#2b2b2b", "#d4d4d4", "#4a4a4a", "#4e9dde"

def _centrar(win, parent):
    win.update_idletasks()
    px = parent.winfo_rootx() + parent.winfo_width()  // 2
    py = parent.winfo_rooty() + parent.winfo_height() // 2
    w, h = win.winfo_width(), win.winfo_height()
    win.geometry(f"+{px-w//2}+{py-h//2}")

def _mk_btn(parent, text, cmd, fg=None):
    return tk.Button(parent, text=text, command=cmd,
                     bg=EBG, fg=fg or FG,
                     activebackground="#5a5a5a", activeforeground="white",
                     relief="flat", padx=10, pady=4,
                     font=("Segoe UI", 9), cursor="hand2")


class DlgAsignarInsumo(tk.Toplevel):
    def __init__(self, parent, insumos, excluir):
        super().__init__(parent)
        self.title("➕  Agregar insumo a la tarea")
        self.geometry("700x480")
        self.resizable(True, True)
        self.grab_set()
        self.result = None
        self.configure(bg=BG)

        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=10, pady=8)
        tk.Label(top, text="🔍", bg=BG, fg=FG, font=("Segoe UI", 10)).pack(side="left")
        self.var_q = tk.StringVar()
        self.var_q.trace_add("write", lambda *_: self._filtrar())
        tk.Entry(top, textvariable=self.var_q, bg=EBG, fg=FG,
                 insertbackground=FG, relief="flat",
                 font=("Segoe UI", 9)).pack(fill="x", expand=True, padx=6)

        cols = ("COD_INS", "Descripción", "Unidad")
        fr = tk.Frame(self, bg=BG)
        fr.pack(fill="both", expand=True, padx=10)
        self.tree = ttk.Treeview(fr, columns=cols, show="headings", selectmode="browse")
        vsb = ttk.Scrollbar(fr, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        fr.rowconfigure(0, weight=1); fr.columnconfigure(0, weight=1)
        for c, w in zip(cols, (90, 440, 70)):
            self.tree.heading(c, text=c); self.tree.column(c, width=w, minwidth=40)

        self._apply_tree_style()
        self._all = [i for i in insumos if i["cod_ins"] not in excluir]
        self._poblar(self._all)

        bot = tk.Frame(self, bg=BG)
        bot.pack(fill="x", padx=10, pady=8)
        tk.Label(bot, text="Cantidad:", bg=BG, fg=ACC,
                 font=("Segoe UI", 9, "bold")).pack(side="left")
        self.var_cant = tk.StringVar(value="1")
        tk.Entry(bot, textvariable=self.var_cant, width=10,
                 bg=EBG, fg=FG, insertbackground=FG,
                 relief="flat", font=("Segoe UI", 9)).pack(side="left", padx=8)
        _mk_btn(bot, "✔  Aceptar",  self._ok).pack(side="right", padx=4)
        _mk_btn(bot, "✖  Cancelar", self.destroy).pack(side="right", padx=4)

        self.bind("<Return>", lambda e: self._ok())
        self.bind("<Escape>", lambda e: self.destroy())
        _centrar(self, parent)

    def _apply_tree_style(self):
        s = ttk.Style(self); s.theme_use("clam")
        s.configure("Treeview", background="#3c3f41", foreground=FG,
                    fieldbackground="#3c3f41", rowheight=22, font=("Segoe UI", 9))
        s.configure("Treeview.Heading", background=EBG, foreground=ACC,
                    font=("Segoe UI", 9, "bold"), relief="flat")
        s.map("Treeview", background=[("selected","#214283")],
              foreground=[("selected","white")])
        self.tree.tag_configure("par",   background="#383838")
        self.tree.tag_configure("impar", background="#3c3f41")

    def _poblar(self, lista):
        self.tree.delete(*self.tree.get_children())
        for i, ins in enumerate(lista):
            self.tree.insert("", "end",
                             values=(ins["cod_ins"], ins["descripcion"], ins["unidad"]),
                             tags=("par" if i%2==0 else "impar",))

    def _filtrar(self):
        q = self.var_q.get().lower()
        self._poblar(self._all if not q else
                     [i for i in self._all
                      if q in i["cod_ins"].lower() or q in i["descripcion"].lower()])

    def _ok(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Sin selección", "Seleccioná un insumo.", parent=self); return
        try:
            cant = float(self.var_cant.get().replace(",","."))
        except ValueError:
            messagebox.showwarning("Cantidad inválida", "Ingresá un número.", parent=self); return
        v = self.tree.item(sel[0], "values")
        self.result = {"cod_ins": v[0], "descripcion": v[1], "unidad": v[2], "cantidad": cant}
        self.destroy()


class DlgNuevoInsumo(tk.Toplevel):
    def __init__(self, parent, cod_sugerido="", cantidad_sug="1"):
        super().__init__(parent)
        self.title("★  Nuevo insumo")
        self.resizable(False, False)
        self.grab_set()
        self.result = None
        self.configure(bg=BG)

        def lbl(txt):
            return tk.Label(self, text=txt, bg=BG, fg=ACC,
                            font=("Segoe UI", 9, "bold"), anchor="w")
        def ent(var, w=32):
            return tk.Entry(self, textvariable=var, width=w,
                            bg=EBG, fg=FG, insertbackground=FG,
                            relief="flat", font=("Segoe UI", 9))

        self.v_cod  = tk.StringVar(value=cod_sugerido)
        self.v_desc = tk.StringVar()
        self.v_uni  = tk.StringVar()
        self.v_cant = tk.StringVar(value=cantidad_sug)

        pad = {"padx": 12, "pady": 5}
        for i, (label, var, width) in enumerate([
            ("COD_INS",     self.v_cod,  16),
            ("Descripción", self.v_desc, 44),
            ("Unidad",      self.v_uni,  10),
            ("Cantidad",    self.v_cant, 10),
        ]):
            lbl(label + ":").grid(row=i, column=0, sticky="w", **pad)
            ent(var, width).grid(row=i, column=1, sticky="ew", **pad)

        tk.Label(self,
                 text="Se agregará a la DB y a Insumos_Master.xlsx",
                 bg=BG, fg="#888", font=("Segoe UI", 8, "italic")).grid(
            row=4, column=0, columnspan=2, pady=(0,6))

        bf = tk.Frame(self, bg=BG)
        bf.grid(row=5, column=0, columnspan=2, pady=8)
        _mk_btn(bf, "✔  Aceptar",  self._ok).pack(side="left", padx=6)
        _mk_btn(bf, "✖  Cancelar", self.destroy).pack(side="left", padx=6)

        self.columnconfigure(1, weight=1)
        self.bind("<Return>", lambda e: self._ok())
        self.bind("<Escape>", lambda e: self.destroy())
        _centrar(self, parent)

    def _ok(self):
        cod  = self.v_cod.get().strip()
        desc = self.v_desc.get().strip()
        uni  = self.v_uni.get().strip()
        try:
            cant = float(self.v_cant.get().replace(",","."))
        except ValueError:
            messagebox.showwarning("Inválido", "Cantidad debe ser un número.", parent=self); return
        if not cod:
            messagebox.showwarning("Falta código", "COD_INS no puede estar vacío.", parent=self); return
        if not desc:
            messagebox.showwarning("Falta descripción", "Descripción no puede estar vacía.", parent=self); return
        self.result = {"cod_ins": cod, "descripcion": desc, "unidad": uni, "cantidad": cant}
        self.destroy()


class DlgEditarCantidad(tk.Toplevel):
    def __init__(self, parent, cod_ins, desc, cantidad):
        super().__init__(parent)
        self.title("✎  Editar cantidad")
        self.resizable(False, False)
        self.grab_set()
        self.result = None
        self.configure(bg=BG)

        tk.Label(self, text=f"{cod_ins}  —  {desc}",
                 bg=BG, fg=FG, font=("Segoe UI", 9),
                 wraplength=340, justify="left").pack(padx=16, pady=(14,4))
        f = tk.Frame(self, bg=BG); f.pack(padx=16, pady=6)
        tk.Label(f, text="Cantidad:", bg=BG, fg=ACC,
                 font=("Segoe UI", 9, "bold")).pack(side="left")
        self.var = tk.StringVar(value=str(cantidad))
        e = tk.Entry(f, textvariable=self.var, width=14,
                     bg=EBG, fg=FG, insertbackground=FG,
                     relief="flat", font=("Segoe UI", 9))
        e.pack(side="left", padx=8)
        e.select_range(0, "end"); e.focus_set()

        bf = tk.Frame(self, bg=BG); bf.pack(pady=10)
        _mk_btn(bf, "✔  Aceptar",  self._ok).pack(side="left", padx=6)
        _mk_btn(bf, "✖  Cancelar", self.destroy).pack(side="left", padx=6)
        self.bind("<Return>", lambda e: self._ok())
        self.bind("<Escape>", lambda e: self.destroy())
        _centrar(self, parent)

    def _ok(self):
        try:
            self.result = float(self.var.get().replace(",",".")); self.destroy()
        except ValueError:
            messagebox.showwarning("Inválido", "Ingresá un número.", parent=self)


# ── App ───────────────────────────────────────────────────────────────────────

class App(tk.Tk):

    COL_IZQ   = ("COD", "Descripción / Designación", "Unidad")
    COL_IZQ_W = (80, 320, 60)
    COL_DER   = ("COD_INS", "Descripción", "Unidad", "Cantidad")
    COL_DER_W = (90, 340, 60, 80)

    def __init__(self, path_rubros, path_tareas, path_db, path_insumos):
        super().__init__()
        self.title("Tareas — Insumos")
        self.geometry("1380x780")
        self.minsize(1000, 540)
        self.configure(bg=BG)

        self.path_rubros  = path_rubros
        self.path_tareas  = path_tareas
        self.path_db      = path_db
        self.path_insumos = path_insumos

        self.con          = get_con(path_db)
        self.modelo_arbol = cargar_rubros_tareas(path_rubros)
        self.lista_tareas = cargar_lista_tareas(path_tareas)
        self.rev_idx      = 0

        self.tarea_activa = None
        self.incidencias  = []
        self._modo        = "arbol"

        self._build_ui()
        self._poblar_arbol()
        self._poblar_der()

    def _build_ui(self):
        s = ttk.Style(self); s.theme_use("clam")
        s.configure("Treeview", background="#3c3f41", foreground=FG,
                    fieldbackground="#3c3f41", rowheight=22, font=("Segoe UI", 9))
        s.configure("Treeview.Heading", background=EBG, foreground=ACC,
                    font=("Segoe UI", 9, "bold"), relief="flat")
        s.map("Treeview", background=[("selected","#214283")],
              foreground=[("selected","white")])
        s.configure("rev.Horizontal.TProgressbar",
                    troughcolor="#3c3f41", background="#4e9dde", thickness=6)

        top = tk.Frame(self, bg=BG, pady=6)
        top.pack(fill="x", padx=10)
        tk.Label(top, text="Tareas  —  Insumos",
                 bg=BG, fg=ACC, font=("Segoe UI", 13, "bold")).pack(side="left")

        mf = tk.Frame(top, bg=BG)
        mf.pack(side="left", padx=20)
        self.btn_modo_arbol = tk.Button(mf, text="🌳  Árbol",
                                        command=self._modo_arbol,
                                        bg="#214283", fg="white",
                                        relief="flat", padx=10, pady=3,
                                        font=("Segoe UI", 9, "bold"), cursor="hand2")
        self.btn_modo_arbol.pack(side="left", padx=2)
        self.btn_modo_rev   = tk.Button(mf, text="🔄  Revisión",
                                        command=self._modo_revision,
                                        bg=EBG, fg=FG,
                                        relief="flat", padx=10, pady=3,
                                        font=("Segoe UI", 9), cursor="hand2")
        self.btn_modo_rev.pack(side="left", padx=2)

        self.paned = tk.PanedWindow(self, orient=tk.HORIZONTAL,
                                    bg=BG, sashwidth=6, sashrelief="flat")
        self.paned.pack(fill="both", expand=True, padx=10, pady=(0,6))

        self.frame_izq = self._panel(self.paned, "🌐  Rubros / Tareas")
        frame_der      = self._panel(self.paned, "📋  Insumos de la tarea")
        self.paned.add(self.frame_izq, minsize=360)
        self.paned.add(frame_der,      minsize=420)

        self.frm_arbol = tk.Frame(self.frame_izq, bg="#3c3f41")
        self.frm_arbol.pack(fill="both", expand=True)

        sb = self._search_bar(self.frm_arbol, self._filtrar_arbol)
        sb.pack(fill="x", padx=6, pady=4)

        self.tree_izq = self._make_tree(self.frm_arbol, self.COL_IZQ, self.COL_IZQ_W,
                                        selectmode="browse", show="tree headings")
        self.tree_izq._cont.pack(fill="both", expand=True, padx=6, pady=(0,4))
        self.tree_izq.bind("<<TreeviewSelect>>", self._on_sel_arbol)

        self.lbl_izq = tk.Label(self.frm_arbol, text="", bg="#3c3f41", fg=ACC,
                                font=("Segoe UI", 8, "italic"), anchor="w")
        self.lbl_izq.pack(fill="x", padx=6, pady=(0,4))

        self.frm_rev = tk.Frame(self.frame_izq, bg="#3c3f41")

        self.lbl_rev_prog = tk.Label(self.frm_rev, text="",
                                     bg="#3c3f41", fg=ACC,
                                     font=("Segoe UI", 9, "bold"), anchor="w")
        self.lbl_rev_prog.pack(fill="x", padx=8, pady=(10,2))

        self.prog_bar = ttk.Progressbar(self.frm_rev, style="rev.Horizontal.TProgressbar",
                                        orient="horizontal", mode="determinate")
        self.prog_bar.pack(fill="x", padx=8, pady=(0,8))

        self.frm_rev_info = tk.Frame(self.frm_rev, bg="#1e3d5a", bd=0, relief="flat")
        self.frm_rev_info.pack(fill="x", padx=8, pady=(0,6))
        self.lbl_rev_cod  = tk.Label(self.frm_rev_info, text="",
                                     bg="#1e3d5a", fg="#88ccff",
                                     font=("Segoe UI", 11, "bold"), anchor="w", padx=8, pady=4)
        self.lbl_rev_cod.pack(fill="x")
        self.lbl_rev_desc = tk.Label(self.frm_rev_info, text="",
                                     bg="#1e3d5a", fg=FG,
                                     font=("Segoe UI", 9), anchor="w", padx=8, pady=2,
                                     wraplength=320, justify="left")
        self.lbl_rev_desc.pack(fill="x")

        nav = tk.Frame(self.frm_rev, bg="#3c3f41")
        nav.pack(fill="x", padx=8, pady=4)
        self.btn_prev = tk.Button(nav, text="◀  Anterior",
                                  command=self._rev_anterior,
                                  bg=EBG, fg=FG, relief="flat",
                                  padx=12, pady=5,
                                  font=("Segoe UI", 9), cursor="hand2")
        self.btn_prev.pack(side="left", padx=(0,4))
        self.btn_next = tk.Button(nav, text="Siguiente  ▶",
                                  command=self._rev_siguiente,
                                  bg="#214283", fg="white", relief="flat",
                                  padx=12, pady=5,
                                  font=("Segoe UI", 9, "bold"), cursor="hand2")
        self.btn_next.pack(side="left")

        bf = tk.Frame(self.frm_rev, bg="#3c3f41")
        bf.pack(fill="x", padx=8, pady=(8,2))
        tk.Label(bf, text="Ir a COD_TAR:", bg="#3c3f41", fg=ACC,
                 font=("Segoe UI", 9, "bold")).pack(side="left")
        self.var_buscar_rev = tk.StringVar()
        e = tk.Entry(bf, textvariable=self.var_buscar_rev,
                     bg=EBG, fg=FG, insertbackground=FG,
                     relief="flat", width=12, font=("Segoe UI", 9))
        e.pack(side="left", padx=6)
        e.bind("<Return>", self._rev_ir_a)
        _mk_btn(bf, "↵ Ir", self._rev_ir_a).pack(side="left")

        tk.Label(self.frm_rev, text="", bg="#3c3f41").pack(expand=True, fill="both")

        self.lbl_tarea = tk.Label(frame_der,
                                  text="← Seleccioná una tarea",
                                  bg="#1e3d5a", fg="#88ccff",
                                  font=("Segoe UI", 9, "bold"),
                                  anchor="w", padx=8, pady=5)
        self.lbl_tarea.pack(fill="x", padx=6, pady=(4,0))

        sb_der = self._search_bar(frame_der, self._filtrar_der)
        sb_der.pack(fill="x", padx=6, pady=4)

        self.tree_der = self._make_tree(frame_der, self.COL_DER, self.COL_DER_W)
        self.tree_der._cont.pack(fill="both", expand=True, padx=6, pady=(0,4))
        self.tree_der.bind("<Double-1>",        self._editar_cantidad)
        self.tree_der.bind("<<TreeviewSelect>>", lambda e: self._actualizar_btn_sel())

        acc = tk.Frame(frame_der, bg="#3c3f41")
        acc.pack(fill="x", padx=6, pady=(0,4))
        self.btn_agregar = self._btn(acc, "➕  Agregar",        self._agregar_insumo)
        self.btn_editar  = self._btn(acc, "✎  Editar cantidad",  self._editar_cantidad)
        self.btn_quitar  = self._btn(acc, "🗑  Quitar",           self._quitar_insumo)
        self.btn_nuevo   = self._btn(acc, "★  Nuevo insumo",      self._nuevo_insumo, fg="#f0c060")
        for b in (self.btn_agregar, self.btn_editar, self.btn_quitar, self.btn_nuevo):
            b.pack(side="left", padx=2)

        self.lbl_der = tk.Label(frame_der, text="",
                                bg="#3c3f41", fg="#a0c86e",
                                font=("Segoe UI", 8, "italic"), anchor="w")
        self.lbl_der.pack(fill="x", padx=6, pady=(0,4))

        self.statusbar = tk.Label(self, text="Listo.",
                                  bg="#1e1e1e", fg="#888",
                                  font=("Segoe UI", 8), anchor="w", padx=10)
        self.statusbar.pack(fill="x", side="bottom")

        self._set_botones_der(False)

    def _panel(self, parent, title):
        f = tk.Frame(parent, bg="#3c3f41")
        tk.Label(f, text=title, bg="#3c3f41", fg=ACC,
                 font=("Segoe UI", 9, "bold"),
                 anchor="w", padx=6, pady=6).pack(fill="x")
        ttk.Separator(f, orient="horizontal").pack(fill="x")
        return f

    def _btn(self, parent, text, cmd, fg=None):
        return tk.Button(parent, text=text, command=cmd,
                         bg=EBG, fg=fg or FG,
                         activebackground="#5a5a5a", activeforeground="white",
                         relief="flat", padx=8, pady=4,
                         font=("Segoe UI", 9), cursor="hand2")

    def _search_bar(self, parent, cmd):
        f = tk.Frame(parent, bg="#3c3f41")
        tk.Label(f, text="🔍", bg="#3c3f41", fg=FG,
                 font=("Segoe UI", 10)).pack(side="left", padx=(0,4))
        var = tk.StringVar()
        var.trace_add("write", lambda *_: cmd(var.get()))
        tk.Entry(f, textvariable=var, bg=EBG, fg=FG,
                 insertbackground=FG, relief="flat",
                 font=("Segoe UI", 9)).pack(fill="x", expand=True)
        return f

    def _make_tree(self, parent, cols, widths, selectmode="browse", show="headings"):
        frame = tk.Frame(parent, bg="#3c3f41")
        tree  = ttk.Treeview(frame, columns=cols, show=show, selectmode=selectmode)
        vsb   = ttk.Scrollbar(frame, orient="vertical",   command=tree.yview)
        hsb   = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        frame.rowconfigure(0, weight=1); frame.columnconfigure(0, weight=1)
        for col, w in zip(cols, widths):
            tree.heading(col, text=col); tree.column(col, width=w, minwidth=40)
        if show == "tree headings":
            tree.column("#0", width=22, minwidth=22, stretch=False)
        tree.tag_configure("rubro",       background="#2e4a2e", foreground="#b8e0a0",
                           font=("Segoe UI", 9, "bold"))
        tree.tag_configure("tarea",       background="#3c3f41", foreground=FG)
        tree.tag_configure("tarea_nueva", background="#3a2e00", foreground="#f0c060")
        tree.tag_configure("par",         background="#383838", foreground=FG)
        tree.tag_configure("impar",       background="#3c3f41", foreground=FG)
        tree.tag_configure("sin_ins",     background="#3d1e1e", foreground="#f08080")
        tree._cont = frame
        return tree

    def _modo_arbol(self):
        self._modo = "arbol"
        self.btn_modo_arbol.config(bg="#214283", fg="white", font=("Segoe UI", 9, "bold"))
        self.btn_modo_rev  .config(bg=EBG,       fg=FG,      font=("Segoe UI", 9))
        self.frm_rev.pack_forget()
        self.frm_arbol.pack(fill="both", expand=True)

    def _modo_revision(self):
        self._modo = "revision"
        self.btn_modo_rev  .config(bg="#214283", fg="white", font=("Segoe UI", 9, "bold"))
        self.btn_modo_arbol.config(bg=EBG,       fg=FG,      font=("Segoe UI", 9))
        self.frm_arbol.pack_forget()
        self.frm_rev.pack(fill="both", expand=True)
        self._rev_mostrar()

    def _rev_mostrar(self):
        total = len(self.lista_tareas)
        if total == 0:
            return
        idx   = self.rev_idx
        tarea = self.lista_tareas[idx]
        self.lbl_rev_prog.config(text=f"Tarea  {idx+1}  /  {total}")
        self.prog_bar.config(maximum=total, value=idx+1)
        self.lbl_rev_cod .config(text=f"  {tarea['cod_tar']}")
        self.lbl_rev_desc.config(text=f"  {tarea['descripcion']}  [{tarea['unidad']}]")
        self.btn_prev.config(state="normal" if idx > 0       else "disabled")
        self.btn_next.config(state="normal" if idx < total-1 else "disabled")
        self._activar_tarea(tarea)

    def _rev_anterior(self):
        if self.rev_idx > 0:
            self.rev_idx -= 1; self._rev_mostrar()

    def _rev_siguiente(self):
        if self.rev_idx < len(self.lista_tareas) - 1:
            self.rev_idx += 1; self._rev_mostrar()

    def _rev_ir_a(self, event=None):
        q = self.var_buscar_rev.get().strip().upper()
        for i, t in enumerate(self.lista_tareas):
            if t["cod_tar"].upper() == q:
                self.rev_idx = i; self._rev_mostrar(); return
        messagebox.showinfo("No encontrado", f"COD_TAR '{q}' no está en la lista.", parent=self)

    def _poblar_arbol(self, filtro=""):
        self.tree_izq.delete(*self.tree_izq.get_children())
        fl = filtro.lower()
        total_t = 0
        for ri, rubro in enumerate(self.modelo_arbol):
            tareas = rubro["tareas"]
            if fl:
                tareas = [t for t in tareas
                          if fl in t["cod_tar"].lower()
                          or fl in t["descripcion"].lower()
                          or fl in rubro["designacion"].lower()]
            if not tareas and fl:
                continue
            iid_r = f"R_{ri}"
            self.tree_izq.insert("", "end", iid=iid_r,
                                 values=(rubro["cod_rubro"], rubro["designacion"], ""),
                                 tags=("rubro",), open=False)
            for ti, t in enumerate(tareas):
                self.tree_izq.insert(iid_r, "end", iid=f"T_{ri}_{ti}",
                                     values=(t["cod_tar"], t["descripcion"], t["unidad"]),
                                     tags=("tarea",))
                total_t += 1
        self.lbl_izq.config(
            text=f"{len(self.tree_izq.get_children())} rubros  |  {total_t} tareas")

    def _filtrar_arbol(self, txt): self._poblar_arbol(txt)

    def _on_sel_arbol(self, event=None):
        sel = self.tree_izq.selection()
        if not sel: return
        iid = sel[0]
        if not iid.startswith("T_"):
            self.tree_izq.item(iid, open=True); return
        _, ri, ti = iid.split("_")
        tarea = self.modelo_arbol[int(ri)]["tareas"][int(ti)]
        nueva = asegurar_tarea_en_db(self.con, tarea["cod_tar"],
                                     tarea["descripcion"], tarea["unidad"])
        if nueva:
            self.tree_izq.item(iid, tags=("tarea_nueva",))
            self._set_status(f"⚡ Tarea {tarea['cod_tar']} incorporada a la DB")
        self._activar_tarea(tarea)

    def _activar_tarea(self, tarea: dict):
        self.tarea_activa = tarea
        asegurar_tarea_en_db(self.con, tarea["cod_tar"],
                             tarea["descripcion"], tarea["unidad"])
        self.lbl_tarea.config(
            text=f"  {tarea['cod_tar']}  —  {tarea['descripcion']}  [{tarea['unidad']}]")
        self._cargar_incidencias()
        self._set_botones_der(True)

    def _cargar_incidencias(self, filtro=""):
        self.incidencias = incidencias_de_tarea(self.con, self.tarea_activa["cod_tar"])
        self._poblar_der(filtro)

    def _poblar_der(self, filtro=""):
        self.tree_der.delete(*self.tree_der.get_children())
        fl = filtro.lower()
        datos = self.incidencias
        if fl:
            datos = [d for d in datos
                     if fl in d["cod_ins"].lower() or fl in d["descripcion"].lower()]
        for i, d in enumerate(datos):
            cant = f"{d['cantidad']:.4f}".rstrip("0").rstrip(".") if d["cantidad"] else "—"
            self.tree_der.insert("", "end", iid=str(d["rowid"]),
                                 values=(d["cod_ins"], d["descripcion"], d["unidad"], cant),
                                 tags=("par" if i%2==0 else "impar",))
        n = len(datos)
        color = "#f08080" if n == 0 and self.tarea_activa else "#a0c86e"
        msg   = "⚠  Sin insumos" if n == 0 and self.tarea_activa else f"{n} insumo(s)"
        self.lbl_der.config(text=msg, fg=color)

    def _filtrar_der(self, txt):
        if self.tarea_activa: self._poblar_der(txt)

    def _set_botones_der(self, activo):
        s = "normal" if activo else "disabled"
        self.btn_agregar.config(state=s)
        self.btn_nuevo  .config(state=s)
        self._actualizar_btn_sel()

    def _actualizar_btn_sel(self):
        hay = bool(self.tree_der.selection()) and self.tarea_activa is not None
        s = "normal" if hay else "disabled"
        self.btn_editar.config(state=s)
        self.btn_quitar.config(state=s)

    def _agregar_insumo(self):
        if not self.tarea_activa: return
        excluir = {d["cod_ins"] for d in self.incidencias}
        dlg = DlgAsignarInsumo(self, todos_insumos(self.con), excluir)
        self.wait_window(dlg)
        if not dlg.result: return
        r = dlg.result
        self.con.execute(
            "INSERT INTO incidencias (cod_tar, cod_ins, cantidad, unidad) VALUES (?,?,?,NULL)",
            (self.tarea_activa["cod_tar"], r["cod_ins"], r["cantidad"]))
        self.con.commit()
        self._cargar_incidencias()
        self._set_status(f"✔ {r['cod_ins']} → {self.tarea_activa['cod_tar']}")

    def _editar_cantidad(self, event=None):
        sel = self.tree_der.selection()
        if not sel: return
        rowid = int(sel[0])
        v     = self.tree_der.item(sel[0], "values")
        try: cant = float(v[3])
        except ValueError: cant = 0.0
        dlg = DlgEditarCantidad(self, v[0], v[1], cant)
        self.wait_window(dlg)
        if dlg.result is None: return
        self.con.execute("UPDATE incidencias SET cantidad=? WHERE rowid=?", (dlg.result, rowid))
        self.con.commit()
        self._cargar_incidencias()
        self._set_status(f"Cantidad {v[0]} → {dlg.result}")

    def _quitar_insumo(self):
        sel = self.tree_der.selection()
        if not sel: return
        rowid = int(sel[0])
        v     = self.tree_der.item(sel[0], "values")
        if not messagebox.askyesno("Confirmar",
                f"¿Quitar «{v[0]} — {v[1]}» de {self.tarea_activa['cod_tar']}?"):
            return
        self.con.execute("DELETE FROM incidencias WHERE rowid=?", (rowid,))
        self.con.commit()
        self._cargar_incidencias()
        self._set_status(f"Insumo {v[0]} quitado.")

    def _nuevo_insumo(self):
        if not self.tarea_activa: return
        cod_tar = self.tarea_activa["cod_tar"]
        sug = ""
        m = re.match(r'^(\d+)T$', cod_tar)
        if m:
            num = m.group(1)
            sug = f"{num[0]}T{num}"
        dlg = DlgNuevoInsumo(self, cod_sugerido=sug)
        self.wait_window(dlg)
        if not dlg.result: return
        r = dlg.result
        if self.con.execute("SELECT 1 FROM insumos WHERE cod_ins=?", (r["cod_ins"],)).fetchone():
            messagebox.showerror("Código duplicado",
                f"El insumo {r['cod_ins']} ya existe.\nUsá ➕ Agregar para asignarlo.", parent=self)
            return
        self.con.execute(
            "INSERT INTO insumos (cod_ins, descripcion, unidad, activo) VALUES (?,?,?,1)",
            (r["cod_ins"], r["descripcion"], r["unidad"]))
        self.con.execute(
            "INSERT INTO incidencias (cod_tar, cod_ins, cantidad, unidad) VALUES (?,?,?,NULL)",
            (self.tarea_activa["cod_tar"], r["cod_ins"], r["cantidad"]))
        self.con.commit()
        self._agregar_a_excel(r["cod_ins"], r["descripcion"], r["unidad"])
        self._cargar_incidencias()
        self._set_status(f"★ {r['cod_ins']} creado y asignado a {self.tarea_activa['cod_tar']}")

    def _agregar_a_excel(self, cod_ins, descripcion, unidad):
        try:
            path = self.path_insumos
            shutil.copy2(path, path + ".bak")
            df = pd.read_excel(path, dtype=str)
            df.columns = [c.strip() for c in df.columns]
            df = pd.concat([df,
                            pd.DataFrame([{"COD_INS": cod_ins,
                                           "Descripción": descripcion,
                                           "Unidad": unidad}])],
                           ignore_index=True).sort_values("COD_INS")
            df.to_excel(path, index=False)
        except Exception as e:
            messagebox.showwarning("Excel no actualizado",
                f"No se pudo actualizar {self.path_insumos}:\n{e}", parent=self)

    def _set_status(self, msg): self.statusbar.config(text=msg)

    def destroy(self):
        try: self.con.close()
        except Exception: pass
        super().destroy()


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--rubros",  default=DEFAULT_RUBROS)
    p.add_argument("--tareas",  default=DEFAULT_TAREAS)
    p.add_argument("--db",      default=DEFAULT_DB)
    p.add_argument("--insumos", default=DEFAULT_INSUMOS)
    args = p.parse_args()
    for label, path in (("Rubros", args.rubros), ("Tareas", args.tareas),
                        ("DB",     args.db),      ("Insumos", args.insumos)):
        if not os.path.exists(path):
            print(f"[AVISO] No se encontró {label}: {path}")
    App(args.rubros, args.tareas, args.db, args.insumos).mainloop()

if __name__ == "__main__":
    main()
