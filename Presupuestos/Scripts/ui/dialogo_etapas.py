"""dialogo_etapas.py — Pantallas que siguen a «Abrir obra»:

- DlgModo: elegir «Obra Original» (el presupuesto, como siempre) o «Etapas».
- DlgEtapas: lista de etapas (y sus variantes) de la obra. Cada una se abre en la
  ventana de obra como si fuera una obra distinta (core/obra_etapa.py).
"""
import json
import tkinter as tk
from tkinter import ttk, messagebox

from core import etapas as E
from core.obra import Obra, CARPETA_OBRAS, cargar_maestro_desde_db
from core.obra_etapa import ObraEtapa

COLOR_HDR   = "#1a3a5c"
COLOR_SEC   = "#2a6099"
COLOR_VERDE = "#1d7a4a"
COLOR_ROJO  = "#b03030"
COLOR_ETAPA = "#6a4c93"
FUENTE_S    = ("Segoe UI", 9)
FUENTE_B    = ("Segoe UI", 10, "bold")


def _fmt_pt(v):
    return f"{round(v or 0):,}".replace(",", ".")


def _centrar(win, parent):
    win.update_idletasks()
    x = parent.winfo_rootx() + max((parent.winfo_width() - win.winfo_width()) // 2, 0)
    y = parent.winfo_rooty() + max((parent.winfo_height() - win.winfo_height()) // 3, 0)
    win.geometry(f"+{x}+{y}")


# ═══════════════════════════════════════════════════════════════════════════
class DlgModo(tk.Toplevel):
    """Devuelve en self.modo: 'original', 'etapas' o None."""

    def __init__(self, parent, numero: str, titulo: str):
        super().__init__(parent)
        self.modo = None
        self.title(f"Obra {numero}")
        self.resizable(False, False)
        self.grab_set()
        hdr = tk.Frame(self, bg=COLOR_HDR, height=44)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text=f"  Obra {titulo}", bg=COLOR_HDR, fg="white",
                 font=("Segoe UI", 12, "bold")).pack(side="left", padx=12)
        cuerpo = tk.Frame(self, padx=24, pady=18)
        cuerpo.pack()
        tk.Label(cuerpo, text="¿Qué querés abrir?", font=("Segoe UI", 11)).pack(pady=(0, 12))
        botones = tk.Frame(cuerpo)
        botones.pack()
        self._boton(botones, "Obra Original",
                    "Presupuesto, versiones\ny seguimiento (Ejecución)",
                    COLOR_SEC, "original").pack(side="left", padx=8)
        self._boton(botones, "Etapas",
                    "Cada etapa como una obra:\nTareas, Insumos, Presupuesto, Informes",
                    COLOR_ETAPA, "etapas").pack(side="left", padx=8)
        tk.Button(self, text="Cancelar", bg="#888", fg="white", font=FUENTE_S,
                  relief="flat", padx=14, pady=4, cursor="hand2",
                  command=self.destroy).pack(pady=(0, 14))
        self.bind("<Escape>", lambda _: self.destroy())
        _centrar(self, parent)

    def _boton(self, parent, titulo, detalle, color, modo):
        return tk.Button(parent, text=f"{titulo}\n\n{detalle}", bg=color, fg="white",
                         font=FUENTE_B, relief="flat", width=26, height=5,
                         cursor="hand2", activebackground=color, activeforeground="white",
                         command=lambda: self._elegir(modo))

    def _elegir(self, modo):
        self.modo = modo
        self.destroy()


# ═══════════════════════════════════════════════════════════════════════════
class DlgEtapas(tk.Toplevel):
    """Lista de etapas de una obra. Abrir / Nueva etapa / Eliminar."""

    def __init__(self, parent, numero: str):
        super().__init__(parent)
        self.parent = parent
        self.base = Obra.cargar(numero)
        self.data = CARPETA_OBRAS / f"Obra{self.base.numero}" / "data"
        self.title(f"Etapas — Obra {self.base.titulo}")
        self.geometry("720x380")
        self.minsize(560, 260)
        hdr = tk.Frame(self, bg=COLOR_ETAPA, height=40)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text=f"  Etapas — Obra {self.base.titulo}", bg=COLOR_ETAPA,
                 fg="white", font=("Segoe UI", 11, "bold")).pack(side="left", padx=12)
        self.lbl = tk.Label(self, text="", font=FUENTE_S, fg="#555", anchor="w",
                            padx=12, pady=6)
        self.lbl.pack(fill="x")
        frm = tk.Frame(self)
        frm.pack(fill="both", expand=True, padx=12)
        cols = ("etapa", "nombre", "fecha", "tareas", "total")
        self.tbl = ttk.Treeview(frm, columns=cols, show="headings", selectmode="browse")
        for c, txt, w, a in [("etapa", "Etapa", 150, "w"), ("nombre", "Nombre", 220, "w"),
                             ("fecha", "Fecha", 90, "center"), ("tareas", "Tareas", 60, "e"),
                             ("total", "Total", 120, "e")]:
            self.tbl.heading(c, text=txt)
            self.tbl.column(c, width=w, minwidth=40, anchor=a)
        scr = ttk.Scrollbar(frm, orient="vertical", command=self.tbl.yview)
        self.tbl.configure(yscrollcommand=scr.set)
        scr.pack(side="right", fill="y")
        self.tbl.pack(side="left", fill="both", expand=True)
        self.tbl.tag_configure("variante", foreground="#6a3d9a")
        self.tbl.bind("<Double-1>", lambda _: self._abrir())
        bar = tk.Frame(self, pady=8)
        bar.pack(fill="x", padx=12)
        for txt, color, cmd in [("Abrir", COLOR_SEC, self._abrir),
                                ("+ Nueva etapa", COLOR_VERDE, self._nueva),
                                ("Eliminar", COLOR_ROJO, self._eliminar)]:
            tk.Button(bar, text=txt, bg=color, fg="white", font=FUENTE_B, relief="flat",
                      padx=14, pady=5, cursor="hand2", command=cmd).pack(side="left", padx=4)
        tk.Button(bar, text="Cerrar", bg="#888", fg="white", font=FUENTE_S, relief="flat",
                  padx=14, pady=5, cursor="hand2", command=self.destroy).pack(side="right")
        self.bind("<Escape>", lambda _: self.destroy())
        self.bind("<FocusIn>", lambda e: self._refrescar() if e.widget is self else None)
        self._refrescar()
        _centrar(self, parent)

    # ── Datos ────────────────────────────────────────────────────────────
    def _ejec(self):
        return E.cargar_ejecucion(self.data)

    def _refrescar(self):
        sel = self.tbl.selection()
        for i in self.tbl.get_children():
            self.tbl.delete(i)
        ejec = self._ejec()
        if not ejec:
            self.lbl.config(text="La obra todavía no tiene Original. Definilo en «Obra "
                                 "Original» → pestaña 5. Ejecución → «Definir Original…».",
                            fg=COLOR_ROJO)
            return
        etapas = E.listar_etapas(self.data)
        self.lbl.config(text=f"{len(etapas)} etapa{'s' if len(etapas) != 1 else ''}. "
                             "Doble clic para abrir. Las variantes (en violeta) no suman "
                             "al ejecutado.", fg="#555")
        for et in etapas:
            self._fila(str(et["numero"]), et)
            for var in E.listar_variantes(self.data, et["numero"]):
                self._fila(f"{et['numero']}v{var['variante']}", var, ("variante",))
        if sel and self.tbl.exists(sel[0]):
            self.tbl.selection_set(sel[0])

    def _fila(self, iid, et, tags=()):
        total = et.get("total")
        if total is None:
            total = sum(i["cantidad"] * i["pu"] for i in et.get("items", []))
        nombre = ("    " if et.get("variante") else "") + E.nombre_etapa(et)
        self.tbl.insert("", "end", iid=iid, tags=tags,
                        values=(nombre, et.get("nombre", ""), et.get("fecha", ""),
                                len(et.get("items", [])), f"$ {_fmt_pt(total)}"))

    def _seleccionada(self):
        sel = self.tbl.selection()
        if not sel:
            messagebox.showinfo("Sin selección", "Seleccioná una etapa de la lista.",
                                parent=self)
            return None
        if "v" in sel[0]:
            num, var = sel[0].split("v")
            ruta = E.ruta_variante(self.data, int(num), int(var))
        else:
            ruta = E.ruta_etapa(self.data, int(sel[0]))
        with open(ruta, encoding="utf-8") as f:
            return json.load(f)

    # ── Acciones ─────────────────────────────────────────────────────────
    def _abrir_ventana(self, etapa, ejec, nueva):
        from ui.ventana_obra import VentanaObra
        maestro = cargar_maestro_desde_db(self.data)
        obra = ObraEtapa(Obra.cargar(self.base.numero), etapa, ejec, maestro, nueva=nueva)
        VentanaObra(self.parent, obra)

    def _abrir(self):
        ejec = self._ejec()
        if not ejec:
            return
        et = self._seleccionada()
        if et:
            self._abrir_ventana(et, ejec, nueva=False)

    def _nueva(self):
        ejec = self._ejec()
        if not ejec:
            messagebox.showinfo("Sin Original", self.lbl.cget("text"), parent=self)
            return
        maestro = cargar_maestro_desde_db(self.data)
        base = Obra.cargar(self.base.numero)
        precios = {**(ejec["original"].get("precios") or {}), **(base.precios or {})}
        etapa = E.nueva_etapa(self.data, ejec, maestro["incidencias"], precios,
                              base.archivo_precios or "", catalogo=maestro.get("insumos"))
        if not etapa["items"] and not messagebox.askyesno("Sin tareas en curso",
                "No hay tareas «En curso». ¿Abrir la etapa vacía igual y agregar "
                "tareas a mano?", parent=self):
            return
        self._abrir_ventana(etapa, ejec, nueva=True)

    def _eliminar(self):
        et = self._seleccionada()
        if not et:
            return
        if et.get("variante"):
            if messagebox.askyesno("Eliminar variante",
                    f"¿Eliminar {E.nombre_etapa(et)}?\n\nLa etapa real no cambia. "
                    "No se puede deshacer.", icon="warning", parent=self):
                E.eliminar_variante(self.data, et["numero"], et["variante"])
                self._refrescar()
            return
        if E.listar_variantes(self.data, et["numero"]):
            messagebox.showinfo("Etapa con variantes",
                f"La Etapa {et['numero']:02d} tiene variantes. Eliminalas primero.",
                parent=self)
            return
        if not messagebox.askyesno("Eliminar etapa",
                f"¿Eliminar la Etapa {et['numero']:02d}?\n\nLas tareas que esa etapa "
                "daba por finalizadas vuelven a «En curso». No se puede deshacer.",
                icon="warning", parent=self):
            return
        E.eliminar_etapa(self.data, self._ejec(), et["numero"])
        self._refrescar()
