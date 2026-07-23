"""
seleccion_tareas.py
Interfaz para asignar COD_TAR desde Tareas_Master al Listado de Rubros.

Uso:
    python seleccion_tareas.py
    python seleccion_tareas.py --rubros /ruta/Listado_de_Rubros.xls --tareas /ruta/Tareas_Master.xlsx

Panel izquierdo : Listado_de_Rubros  → columnas: Designación | Unidad | COD_TAR (editable)
Panel derecho   : Tareas_Master      → columnas: COD_TAR | Descripción | Unidad

- Clic simple  en la izquierda  → selecciona la fila destino.
- Doble clic   en la derecha    → agrega el COD_TAR al campo COD_TAR de la fila izquierda activa.
  Si ya hay un valor, lo separa con ":".
- Selección múltiple en la derecha con Ctrl/Shift+clic → al hacer doble clic en cualquiera
  de las seleccionadas, agrega TODOS los COD_TAR seleccionados.
- Botón "Guardar" graba el .xls modificado (nuevo archivo con sufijo _modificado).
- Botón "Limpiar COD_TAR" borra el COD_TAR de la fila izquierda activa.
- Campo de búsqueda en cada panel para filtrar las filas.
"""

import sys
import os
import argparse
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import pandas as pd

# ── Rutas por defecto (mismo directorio que el script o cwd) ──────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

DEFAULT_RUBROS = os.path.join(SCRIPT_DIR, "Listado_de_Rubros_modificado.xlsx")
DEFAULT_TAREAS = os.path.join(SCRIPT_DIR, "Tareas_Master.xlsx")


# ── Carga de datos ─────────────────────────────────────────────────────────────

def cargar_rubros(path: str) -> pd.DataFrame:
    engine = "xlrd" if path.lower().endswith(".xls") else "openpyxl"
    df = pd.read_excel(path, engine=engine)
    # Renombrar primera columna a COD_TAR si no existe
    if "COD_TAR" not in df.columns:
        df = df.rename(columns={df.columns[0]: "COD_TAR"})
    # Asegurarse que COD_TAR existe y es string
    if "COD_TAR" not in df.columns:
        df.insert(0, "COD_TAR", "")
    df["COD_TAR"] = df["COD_TAR"].fillna("").astype(str).str.strip()
    df["COD_TAR"] = df["COD_TAR"].replace("nan", "")
    # Columnas obligatorias
    for col in ("Designación", "Unidad"):
        if col not in df.columns:
            df[col] = ""
    df["Designación"] = df["Designación"].fillna("").astype(str)
    df["Unidad"] = df["Unidad"].fillna("").astype(str)
    return df


def cargar_tareas(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    # Normalizar nombre columna descripción
    rename = {}
    for c in df.columns:
        if c.lower() in ("descripción", "descripcion", "designación", "designacion"):
            rename[c] = "Descripción"
    if rename:
        df = df.rename(columns=rename)
    for col in ("COD_TAR", "Descripción", "Unidad"):
        if col not in df.columns:
            df[col] = ""
    df["COD_TAR"] = df["COD_TAR"].fillna("").astype(str).str.strip()
    df["Descripción"] = df["Descripción"].fillna("").astype(str)
    df["Unidad"] = df["Unidad"].fillna("").astype(str)
    return df


# ── Aplicación ─────────────────────────────────────────────────────────────────

class App(tk.Tk):
    COL_RUBROS = ("Designación", "Unidad", "COD_TAR")
    COL_TAREAS = ("COD_TAR", "Descripción", "Unidad")

    COL_RUBROS_W = (340, 60, 140)
    COL_TAREAS_W = (100, 340, 60)

    def __init__(self, path_rubros: str, path_tareas: str):
        super().__init__()
        self.title("Selección de Tareas")
        self.geometry("1200x700")
        self.minsize(900, 500)
        self.configure(bg="#2b2b2b")

        # Colores
        self.BG       = "#2b2b2b"
        self.BG_FRAME = "#3c3f41"
        self.FG       = "#d4d4d4"
        self.SEL_BG   = "#214283"
        self.ACCENT   = "#4e9dde"
        self.ENTRY_BG = "#4a4a4a"

        self.path_rubros = path_rubros
        self.path_tareas = path_tareas

        self.df_rubros: pd.DataFrame = cargar_rubros(path_rubros)
        self.df_tareas: pd.DataFrame = cargar_tareas(path_tareas)

        # Índice de la fila ORIGINAL seleccionada en rubros (None = ninguna)
        self.fila_rubros_sel: int | None = None

        self._build_ui()
        self._poblar_rubros()
        self._poblar_tareas()

    # ── Construcción de la UI ─────────────────────────────────────────────────

    def _build_ui(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # Treeview general
        self.style.configure("Treeview",
                             background="#3c3f41",
                             foreground=self.FG,
                             fieldbackground="#3c3f41",
                             rowheight=22,
                             font=("Segoe UI", 9))
        self.style.configure("Treeview.Heading",
                             background="#4a4a4a",
                             foreground=self.ACCENT,
                             font=("Segoe UI", 9, "bold"),
                             relief="flat")
        self.style.map("Treeview",
                       background=[("selected", self.SEL_BG)],
                       foreground=[("selected", "white")])
        self.style.configure("TScrollbar",
                             background="#4a4a4a",
                             troughcolor="#2b2b2b",
                             arrowcolor=self.FG)

        # ── Barra superior ────────────────────────────────────────────────────
        top = tk.Frame(self, bg=self.BG, pady=6)
        top.pack(fill="x", padx=10)

        tk.Label(top, text="seleccion_tareas",
                 bg=self.BG, fg=self.ACCENT,
                 font=("Segoe UI", 13, "bold")).pack(side="left")

        btn_frame = tk.Frame(top, bg=self.BG)
        btn_frame.pack(side="right")
        self._btn(btn_frame, "💾  Guardar", self._guardar).pack(side="right", padx=4)
        self._btn(btn_frame, "🗑  Limpiar COD_TAR", self._limpiar_cod).pack(side="right", padx=4)
        self._btn(btn_frame, "📂  Abrir archivos…", self._abrir_archivos).pack(side="right", padx=4)

        # ── Cuerpo principal (paneles) ────────────────────────────────────────
        paned = tk.PanedWindow(self, orient=tk.HORIZONTAL,
                               bg=self.BG, sashwidth=6,
                               sashrelief="flat", sashpad=2)
        paned.pack(fill="both", expand=True, padx=10, pady=(0, 8))

        self.frame_izq = self._panel(paned, "📋  Listado de Rubros  (clic para seleccionar)")
        self.frame_der = self._panel(paned, "📦  Tareas Master  (doble clic para asignar)")
        paned.add(self.frame_izq, minsize=350)
        paned.add(self.frame_der, minsize=350)

        # ── Panel izquierdo ───────────────────────────────────────────────────
        srch_izq = self._search_bar(self.frame_izq, self._filtrar_rubros)
        srch_izq.pack(fill="x", padx=6, pady=4)

        self.tree_izq = self._tree(self.frame_izq, self.COL_RUBROS, self.COL_RUBROS_W,
                                   selectmode="browse")
        self.tree_izq._container.pack(fill="both", expand=True, padx=6, pady=(0, 6))
        self.tree_izq.bind("<ButtonRelease-1>", self._sel_rubro)

        # Barra estado izquierda
        self.lbl_izq_info = tk.Label(self.frame_izq, text="",
                                     bg=self.BG_FRAME, fg=self.ACCENT,
                                     font=("Segoe UI", 8, "italic"), anchor="w")
        self.lbl_izq_info.pack(fill="x", padx=6, pady=(0, 4))

        # ── Panel derecho ─────────────────────────────────────────────────────
        srch_der = self._search_bar(self.frame_der, self._filtrar_tareas)
        srch_der.pack(fill="x", padx=6, pady=4)

        self.tree_der = self._tree(self.frame_der, self.COL_TAREAS, self.COL_TAREAS_W,
                                   selectmode="extended")
        self.tree_der._container.pack(fill="both", expand=True, padx=6, pady=(0, 6))
        self.tree_der.bind("<Double-1>", self._asignar_cod)

        # Barra estado derecha
        self.lbl_der_info = tk.Label(self.frame_der, text="",
                                     bg=self.BG_FRAME, fg="#a0c86e",
                                     font=("Segoe UI", 8, "italic"), anchor="w")
        self.lbl_der_info.pack(fill="x", padx=6, pady=(0, 4))

        # ── Barra de estado global ────────────────────────────────────────────
        self.statusbar = tk.Label(self, text="Listo.",
                                  bg="#1e1e1e", fg="#888",
                                  font=("Segoe UI", 8), anchor="w",
                                  padx=10)
        self.statusbar.pack(fill="x", side="bottom")

    def _panel(self, parent, title: str) -> tk.Frame:
        f = tk.Frame(parent, bg=self.BG_FRAME, bd=0)
        tk.Label(f, text=title,
                 bg=self.BG_FRAME, fg=self.ACCENT,
                 font=("Segoe UI", 9, "bold"),
                 anchor="w", padx=6, pady=6).pack(fill="x")
        ttk.Separator(f, orient="horizontal").pack(fill="x")
        return f

    def _btn(self, parent, text: str, cmd) -> tk.Button:
        return tk.Button(parent, text=text, command=cmd,
                         bg="#4a4a4a", fg=self.FG,
                         activebackground="#5a5a5a", activeforeground="white",
                         relief="flat", padx=10, pady=4,
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
              selectmode: str = "browse") -> ttk.Treeview:
        # frame interno con grid para tree + scrollbars
        # pack() lo hace el caller sobre este frame
        frame = tk.Frame(parent, bg=self.BG_FRAME)

        tree = ttk.Treeview(frame, columns=cols, show="headings",
                             selectmode=selectmode)
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        for col, w in zip(cols, widths):
            tree.heading(col, text=col,
                         command=lambda c=col, t=tree: self._sort(t, c))
            tree.column(col, width=w, minwidth=50)

        tree.tag_configure("activo", background="#1a3a6a", foreground="white")
        tree.tag_configure("par",    background="#383838")
        tree.tag_configure("impar",  background="#3c3f41")

        # Guardar referencia al frame contenedor en el tree para poder hacer pack
        tree._container = frame
        return tree

    # ── Poblar tablas ─────────────────────────────────────────────────────────

    def _poblar_rubros(self, filtro: str = ""):
        self.tree_izq.delete(*self.tree_izq.get_children())
        mask = self.df_rubros["Designación"].str.lower().str.contains(
            filtro.lower(), na=False) if filtro else slice(None)
        sub = self.df_rubros[mask] if filtro else self.df_rubros
        for i, (orig_idx, row) in enumerate(sub.iterrows()):
            tag = "par" if i % 2 == 0 else "impar"
            iid = str(orig_idx)
            self.tree_izq.insert("", "end", iid=iid,
                                 values=(row["Designación"],
                                         row["Unidad"],
                                         row["COD_TAR"]),
                                 tags=(tag,))
        # Re-seleccionar si había algo
        if self.fila_rubros_sel is not None:
            iid = str(self.fila_rubros_sel)
            if self.tree_izq.exists(iid):
                self.tree_izq.selection_set(iid)
                self.tree_izq.focus(iid)
                self.tree_izq.see(iid)
        total = len(sub)
        self.lbl_izq_info.config(text=f"{total} ítems  |  Seleccionado: {self._desc_sel_izq()}")

    def _poblar_tareas(self, filtro: str = ""):
        self.tree_der.delete(*self.tree_der.get_children())
        if filtro:
            mask = (self.df_tareas["COD_TAR"].str.lower().str.contains(filtro.lower(), na=False) |
                    self.df_tareas["Descripción"].str.lower().str.contains(filtro.lower(), na=False))
            sub = self.df_tareas[mask]
        else:
            sub = self.df_tareas
        for i, (orig_idx, row) in enumerate(sub.iterrows()):
            tag = "par" if i % 2 == 0 else "impar"
            iid = str(orig_idx)
            self.tree_der.insert("", "end", iid=iid,
                                 values=(row["COD_TAR"],
                                         row["Descripción"],
                                         row["Unidad"]),
                                 tags=(tag,))
        total = len(sub)
        self.lbl_der_info.config(text=f"{total} tareas")

    # ── Eventos ───────────────────────────────────────────────────────────────

    def _sel_rubro(self, event):
        sel = self.tree_izq.selection()
        if not sel:
            return
        iid = sel[0]
        # Quitar tag activo previo
        if self.fila_rubros_sel is not None:
            prev = str(self.fila_rubros_sel)
            if self.tree_izq.exists(prev):
                orig_tag = "par" if (self.fila_rubros_sel % 2 == 0) else "impar"
                self.tree_izq.item(prev, tags=(orig_tag,))
        self.fila_rubros_sel = int(iid)
        self.tree_izq.item(iid, tags=("activo",))
        desc = self.df_rubros.at[self.fila_rubros_sel, "Designación"]
        cod  = self.df_rubros.at[self.fila_rubros_sel, "COD_TAR"]
        self.lbl_izq_info.config(
            text=f"Seleccionado: {desc}  |  COD_TAR actual: «{cod}»")
        self._set_status(f"Rubro activo: {desc}")

    def _asignar_cod(self, event):
        if self.fila_rubros_sel is None:
            messagebox.showwarning("Sin selección",
                                   "Primero hacé clic en una fila del panel izquierdo.")
            return

        sels = self.tree_der.selection()
        if not sels:
            return

        # Recoger todos los COD_TAR seleccionados a la derecha
        nuevos = []
        for iid in sels:
            vals = self.tree_der.item(iid, "values")
            cod = str(vals[0]).strip()
            if cod:
                nuevos.append(cod)

        if not nuevos:
            return

        actual = self.df_rubros.at[self.fila_rubros_sel, "COD_TAR"].strip()
        existentes = [c for c in actual.split(":") if c] if actual else []

        for c in nuevos:
            if c not in existentes:
                existentes.append(c)

        resultado = ":".join(existentes)
        self.df_rubros.at[self.fila_rubros_sel, "COD_TAR"] = resultado

        # Actualizar celda en treeview izquierdo
        iid = str(self.fila_rubros_sel)
        if self.tree_izq.exists(iid):
            row = self.df_rubros.loc[self.fila_rubros_sel]
            self.tree_izq.item(iid, values=(row["Designación"],
                                            row["Unidad"],
                                            row["COD_TAR"]))

        desc = self.df_rubros.at[self.fila_rubros_sel, "Designación"]
        self.lbl_izq_info.config(
            text=f"Seleccionado: {desc}  |  COD_TAR actual: «{resultado}»")
        self._set_status(
            f"Asignado «{':'.join(nuevos)}» → {desc}  |  COD_TAR: {resultado}")

    def _limpiar_cod(self):
        if self.fila_rubros_sel is None:
            messagebox.showwarning("Sin selección",
                                   "Primero seleccioná una fila en el panel izquierdo.")
            return
        desc = self.df_rubros.at[self.fila_rubros_sel, "Designación"]
        ok = messagebox.askyesno("Confirmar",
                                  f"¿Limpiar COD_TAR de «{desc}»?")
        if not ok:
            return
        self.df_rubros.at[self.fila_rubros_sel, "COD_TAR"] = ""
        iid = str(self.fila_rubros_sel)
        if self.tree_izq.exists(iid):
            row = self.df_rubros.loc[self.fila_rubros_sel]
            self.tree_izq.item(iid, values=(row["Designación"],
                                            row["Unidad"], ""))
        self.lbl_izq_info.config(
            text=f"Seleccionado: {desc}  |  COD_TAR actual: «»")
        self._set_status(f"COD_TAR limpiado en: {desc}")

    # ── Guardar ───────────────────────────────────────────────────────────────

    def _guardar(self):
        base, ext = os.path.splitext(self.path_rubros)
        # Siempre guarda como .xlsx (xlwt no soporta .xls moderno con openpyxl)
        sugerido = base + "_modificado.xlsx"
        dest = filedialog.asksaveasfilename(
            title="Guardar Rubros modificado",
            initialfile=os.path.basename(sugerido),
            initialdir=os.path.dirname(sugerido),
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx"), ("Todos", "*.*")])
        if not dest:
            return
        try:
            self.df_rubros.to_excel(dest, index=False)
            self._set_status(f"✅ Guardado: {dest}")
            messagebox.showinfo("Guardado", f"Archivo guardado:\n{dest}")
        except Exception as e:
            messagebox.showerror("Error al guardar", str(e))

    # ── Abrir archivos ────────────────────────────────────────────────────────

    def _abrir_archivos(self):
        nuevo_rubros = filedialog.askopenfilename(
            title="Seleccioná Listado de Rubros",
            filetypes=[("Excel", "*.xls *.xlsx"), ("Todos", "*.*")])
        if not nuevo_rubros:
            return
        nuevo_tareas = filedialog.askopenfilename(
            title="Seleccioná Tareas Master",
            filetypes=[("Excel", "*.xls *.xlsx"), ("Todos", "*.*")])
        if not nuevo_tareas:
            return
        try:
            engine = "xlrd" if nuevo_rubros.endswith(".xls") else "openpyxl"
            self.path_rubros = nuevo_rubros
            self.path_tareas = nuevo_tareas
            self.df_rubros = cargar_rubros(nuevo_rubros)
            self.df_tareas = cargar_tareas(nuevo_tareas)
            self.fila_rubros_sel = None
            self._poblar_rubros()
            self._poblar_tareas()
            self._set_status("Archivos cargados correctamente.")
        except Exception as e:
            messagebox.showerror("Error al abrir", str(e))

    # ── Filtros ───────────────────────────────────────────────────────────────

    def _filtrar_rubros(self, txt: str):
        self._poblar_rubros(txt)

    def _filtrar_tareas(self, txt: str):
        self._poblar_tareas(txt)

    # ── Ordenar columnas ──────────────────────────────────────────────────────

    def _sort(self, tree: ttk.Treeview, col: str):
        data = [(tree.set(k, col), k) for k in tree.get_children("")]
        data.sort(key=lambda t: t[0].lower())
        for idx, (_, k) in enumerate(data):
            tree.move(k, "", idx)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _desc_sel_izq(self) -> str:
        if self.fila_rubros_sel is None:
            return "(ninguno)"
        return self.df_rubros.at[self.fila_rubros_sel, "Designación"]

    def _set_status(self, msg: str):
        self.statusbar.config(text=msg)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Selección de Tareas")
    parser.add_argument("--rubros", default=DEFAULT_RUBROS,
                        help="Ruta a Listado_de_Rubros.xls")
    parser.add_argument("--tareas", default=DEFAULT_TAREAS,
                        help="Ruta a Tareas_Master.xlsx")
    args = parser.parse_args()

    if not os.path.exists(args.rubros):
        print(f"[AVISO] No se encontró: {args.rubros}")
        print("        Podés especificar la ruta con  --rubros /ruta/archivo.xls")
    if not os.path.exists(args.tareas):
        print(f"[AVISO] No se encontró: {args.tareas}")
        print("        Podés especificar la ruta con  --tareas /ruta/archivo.xlsx")

    app = App(args.rubros, args.tareas)
    app.mainloop()


if __name__ == "__main__":
    main()
