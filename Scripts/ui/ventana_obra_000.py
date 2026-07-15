"""ventana_obra.py"""
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.obra import Obra, CARPETA_DATA, CARPETA_PRECIOS, cargar_maestro_desde_db
from core.maestro import cargar_precios

COLOR_HDR   = "#1a3a5c"
COLOR_SEC   = "#2a6099"
COLOR_VERDE = "#1d7a4a"
COLOR_ROJO  = "#b03030"
COLOR_BG    = "#f5f5f5"
FUENTE      = ("Segoe UI", 10)
FUENTE_B    = ("Segoe UI", 10, "bold")
FUENTE_S    = ("Segoe UI", 9)




class VentanaObra(tk.Toplevel):
    def __init__(self, parent, obra: Obra):
        super().__init__(parent)
        self.obra = obra
        self.title(f"Obra {obra.titulo}")
        self.geometry("1020x660")
        self.minsize(820, 480)
        try:
            self.maestro = cargar_maestro_desde_db(obra.carpeta_data)
        except FileNotFoundError as e:
            messagebox.showerror("Error", str(e), parent=self)
            self.destroy()
            return
        self._precios = {}
        self._nombre_precios = ""
        self._ruta_precios = None
        self._build_ui()

    def _build_ui(self):
        hdr = tk.Frame(self, bg=COLOR_HDR, height=50)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text=f"  Obra {self.obra.titulo}",
                 bg=COLOR_HDR, fg="white", font=("Segoe UI", 13, "bold")
                 ).pack(side="left", padx=12)
        if self.obra.ubicacion:
            tk.Label(hdr, text=f"  |  {self.obra.ubicacion}",
                     bg=COLOR_HDR, fg="#aaccee", font=("Segoe UI", 11)
                     ).pack(side="left")
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=8, pady=8)
        self.tab_rubros = tk.Frame(self.nb, bg=COLOR_BG)
        self.tab_tareas = tk.Frame(self.nb, bg=COLOR_BG)
        self.tab_ins    = tk.Frame(self.nb, bg=COLOR_BG)
        self.tab_ppto   = tk.Frame(self.nb, bg=COLOR_BG)
        self.nb.add(self.tab_rubros, text="  1. Rubros  ")
        self.nb.add(self.tab_tareas, text="  2. Tareas  ")
        self.nb.add(self.tab_ins,    text="  3. Insumos y precios  ")
        self.nb.add(self.tab_ppto,   text="  4. Presupuesto  ")
        self.nb.bind("<<NotebookTabChanged>>", self._on_tab)
        self._build_rubros()
        self._build_tareas()
        self._build_ins()
        self._build_presupuesto()
        bar = tk.Frame(self, bg="#e0e0e0", pady=6)
        bar.pack(fill="x")
        tk.Button(bar, text="Guardar obra", bg=COLOR_VERDE, fg="white",
                  font=FUENTE_B, relief="flat", padx=14, pady=5,
                  cursor="hand2", command=self._guardar
                  ).pack(side="right", padx=12)
        self.lbl_st = tk.Label(bar, text="", bg="#e0e0e0",
                               fg="#444", font=FUENTE_S, anchor="w")
        self.lbl_st.pack(side="left", padx=12)

    # ═════════════════════════════════════════════════════════════════════
    # TAB 1 — RUBROS
    # ═════════════════════════════════════════════════════════════════════
    def _build_rubros(self):
        f = self.tab_rubros

        # ── Canvas + scrollbar ────────────────────────────────────────────
        scr = ttk.Scrollbar(f, orient="vertical")
        canvas = tk.Canvas(f, bg=COLOR_BG, highlightthickness=0,
                           yscrollcommand=scr.set)
        scr.config(command=canvas.yview)
        scr.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=COLOR_BG)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(win_id, width=e.width))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        # ── Título ────────────────────────────────────────────────────────
        tk.Label(inner, text="Seleccioná los rubros a presupuestar:",
                 bg=COLOR_BG, font=FUENTE_B, fg=COLOR_HDR
                 ).grid(row=0, column=0, columnspan=2, sticky="w",
                        padx=16, pady=(12, 4))

        # ── Encabezado ────────────────────────────────────────────────────
        tk.Label(inner, text="Rubro", bg=COLOR_BG, font=FUENTE_B, fg=COLOR_HDR
                 ).grid(row=1, column=0, sticky="w", padx=(16, 0), pady=(0, 2))

        # ── Filas de rubros ───────────────────────────────────────────────
        self.vars_rubros = {}

        for i, rubro in enumerate(self.maestro["rubros"]):
            fila = i + 2
            v = tk.BooleanVar(value=self._rubro_activo(rubro))
            self.vars_rubros[rubro] = v
            tk.Checkbutton(inner, text=f"{i+1:02d}.  {rubro}", variable=v,
                           bg=COLOR_BG, font=FUENTE, activebackground=COLOR_BG,
                           command=lambda r=rubro: self._on_rubro(r)
                           ).grid(row=fila, column=0, sticky="w",
                                  padx=(16, 0), pady=2)

        EXPLICACION = (
            "Tilde el Rubro que va a valorizar.\n\n"
            "El listado de tareas que a continuación se listan, tienen en su Nombre un casillero "
            "para identificar el tipo de contratación a realizar.\n\n"
            "Aquellas en las que el Comitente contrata la Mano de Obra y compra los materiales "
            "directamente, no llevan Indicador.\n\n"
            "Caso de Subcontratos:\n"
            "De Mano de Obra y el comitente compra los materiales. Estas se identifican con una letra \"S\".\n"
            "En el caso que Subcontrate el total (MdeO y Materiales) se indica la letra \"T\".\n\n"
            "Más alternativas tienen las Estructuras de Hormigón Armado, por sus variantes constructivas.\n\n"
            "1- Comitente contrata la Mano de Obra (con elaboración de mezcla manual) y compra los materiales "
            "(Cemento, Hierro, Áridos, maderas, clavos, alambre, aditivos) directamente, no llevan Indicador.\n\n"
            "2- Subcontrata la MdeO (con elaboración manual, Madera, clavos y alambre) y el Comitente compra "
            "los áridos y los hierros, se identifica con una letra \"S\".\n\n"
            "3- Subcontrata la MdeO (sin elaboración manual pero con Madera, clavos y alambre) y el Comitente "
            "compra el Hormigón Elaborado y los hierros, se identifica con una letra \"E\".\n\n"
            "4- Subcontrata la MdeO (sin elaboración manual) y el Comitente compra el Hormigón Elaborado, "
            "hierros, Madera, clavos y alambre, se identifica con una letra \"X\".\n\n"
            "5- Subcontrato es por el total de la Tarea (MdeO y todos los materiales), "
            "se identifica con la letra \"T\"."
        )

        n_rubros = len(self.maestro["rubros"])
        inner.grid_columnconfigure(1, weight=1)

        frm_exp = tk.Frame(inner, bg="#eef4fb", relief="groove", bd=1)
        frm_exp.grid(row=1, column=1,
                     rowspan=n_rubros + 1,
                     sticky="nsew", padx=(20, 16), pady=(0, 4))

        txt = tk.Text(frm_exp, font=("Segoe UI", 10), fg="#1a3a5c",
                      bg="#eef4fb", relief="flat", wrap="word",
                      padx=14, pady=12, cursor="arrow")
        txt.insert("1.0", EXPLICACION)
        txt.tag_configure("justify", justify="left")
        txt.tag_add("justify", "1.0", "end")
        txt.configure(state="disabled")
        txt.pack(fill="both", expand=True)
        txt.pack(fill="both", expand=True)

    def _rubro_activo(self, rubro):
        return any(t["rubro"] == rubro for t in self.obra.tareas.values())

    def _on_rubro(self, rubro):
        if not self.vars_rubros[rubro].get():
            for cod in [c for c, t in self.obra.tareas.items() if t["rubro"] == rubro]:
                self.obra.quitar_tarea(cod)
            self._actualizar_st()

    # ═════════════════════════════════════════════════════════════════════
    # TAB 2 — TAREAS  (layout dividido izq/der)
    # ═════════════════════════════════════════════════════════════════════
    def _build_tareas(self):
        f = self.tab_tareas

        # ── Estado interno ────────────────────────────────────────────────
        # items del presupuesto: lista de dicts con rubro/item/desc/unidad/cantidad/cod_tar/subcontrato
        if not hasattr(self.obra, "items_presupuesto"):
            self.obra.items_presupuesto = []
        self._item_sel_idx = None   # índice de la fila izq seleccionada

        # ── Barra inferior ────────────────────────────────────────────────
        frm_btn = tk.Frame(f, bg=COLOR_BG)
        frm_btn.pack(side="bottom", fill="x", padx=12, pady=6)
        self.lbl_sin_vinculo = tk.Label(frm_btn,
            text="", bg=COLOR_BG, fg=COLOR_ROJO, font=FUENTE_S)
        self.lbl_sin_vinculo.pack(side="left", padx=4)

        # ── PanedWindow horizontal ────────────────────────────────────────
        paned = tk.PanedWindow(f, orient="horizontal", bg="#cccccc",
                               sashwidth=5, sashrelief="flat")
        paned.pack(fill="both", expand=True, padx=6, pady=(6, 0))

        # ════════════════════════════════
        # PANEL IZQUIERDO — Presupuesto
        # ════════════════════════════════
        izq = tk.Frame(paned, bg=COLOR_BG)
        paned.add(izq, minsize=380)

        # cabecera
        frm_iz_top = tk.Frame(izq, bg=COLOR_HDR, height=32)
        frm_iz_top.pack(fill="x")
        frm_iz_top.pack_propagate(False)
        tk.Label(frm_iz_top, text="  Presupuesto de licitación",
                 bg=COLOR_HDR, fg="white", font=FUENTE_B).pack(side="left", padx=8)
        tk.Button(frm_iz_top, text="+ Fila", bg="#2a6099", fg="white",
                  font=FUENTE_S, relief="flat", padx=6, pady=1, cursor="hand2",
                  command=self._agregar_fila
                  ).pack(side="right", padx=6, pady=3)
        tk.Button(frm_iz_top, text="Importar", bg="#2a6099", fg="white",
                  font=FUENTE_S, relief="flat", padx=6, pady=1, cursor="hand2",
                  command=self._importar_presupuesto
                  ).pack(side="right", padx=2, pady=3)

        # treeview izquierdo
        cols_iz = ("rubro", "item", "descripcion", "unidad", "cantidad")
        self.tbl_iz = ttk.Treeview(izq, columns=cols_iz,
                                   show="headings", selectmode="extended")
        anchos_iz = {"rubro": 38, "item": 38, "descripcion": 240,
                     "unidad": 58, "cantidad": 76}
        textos_iz = {"rubro": "Rubro", "item": "Ítem",
                     "descripcion": "Descripción", "unidad": "Unidad", "cantidad": "Cantidad"}
        for c in cols_iz:
            self.tbl_iz.heading(c, text=textos_iz[c])
            self.tbl_iz.column(c, width=anchos_iz[c], minwidth=30,
                               anchor="w" if c == "descripcion" else "center")

        scr_iz = ttk.Scrollbar(izq, orient="vertical", command=self.tbl_iz.yview)
        self.tbl_iz.configure(yscrollcommand=scr_iz.set)
        scr_iz.pack(side="right", fill="y")
        self.tbl_iz.pack(side="left", fill="both", expand=True)

        self.tbl_iz.tag_configure("sel",       background="#cce0ff")
        self.tbl_iz.tag_configure("vinculada", background="#d4edda")
        self.tbl_iz.tag_configure("sin_vnc",   background="#fde8e8")
        self.tbl_iz.tag_configure("rubro_hdr", background="#ddeeff",
                                  font=("Segoe UI", 10, "bold"))

        self.tbl_iz.bind("<ButtonRelease-1>", self._clic_fila_iz)
        self.tbl_iz.bind("<Double-1>",        self._doble_clic_iz)
        self.tbl_iz.bind("<Button-3>",        self._menu_der_iz)

        # ════════════════════════════════
        # PANEL DERECHO — Tareas Standard
        # ════════════════════════════════
        der = tk.Frame(paned, bg=COLOR_BG)
        paned.add(der, minsize=340)

        # cabecera
        frm_der_top = tk.Frame(der, bg=COLOR_HDR, height=32)
        frm_der_top.pack(fill="x")
        frm_der_top.pack_propagate(False)
        tk.Label(frm_der_top, text="  Tareas Standard",
                 bg=COLOR_HDR, fg="white", font=FUENTE_B).pack(side="left", padx=8)

        # búsqueda
        frm_bus = tk.Frame(der, bg=COLOR_BG)
        frm_bus.pack(fill="x", padx=8, pady=(4, 2))
        tk.Label(frm_bus, text="Buscar:", bg=COLOR_BG, font=FUENTE_S).pack(side="left")
        self.var_bus = tk.StringVar()
        self.var_bus.trace_add("write",
            lambda *_: self._cargar_tareas() if hasattr(self, "tbl_der") else None)
        ttk.Entry(frm_bus, textvariable=self.var_bus,
                  font=FUENTE, width=22).pack(side="left", padx=4)
        tk.Button(frm_bus, text="✕", font=FUENTE_S, relief="flat",
                  bg="#ccc", padx=4, cursor="hand2",
                  command=lambda: self.var_bus.set("")
                  ).pack(side="left")

        # treeview derecho
        cols_der = ("subcont", "nombre", "unidad")
        self.tbl_der = ttk.Treeview(der, columns=cols_der,
                                    show="headings", selectmode="browse")
        anchos_der = {"subcont": 38, "nombre": 300, "unidad": 58}
        textos_der = {"subcont": "Subc.", "nombre": "Tarea", "unidad": "Unidad"}
        for c in cols_der:
            self.tbl_der.heading(c, text=textos_der[c])
            self.tbl_der.column(c, width=anchos_der[c], minwidth=28,
                               anchor="center" if c != "nombre" else "w")

        scr_der = ttk.Scrollbar(der, orient="vertical", command=self.tbl_der.yview)
        self.tbl_der.configure(yscrollcommand=scr_der.set)
        scr_der.pack(side="right", fill="y")
        self.tbl_der.pack(side="left", fill="both", expand=True)

        self.tbl_der.tag_configure("sel",     background="#cce0ff")
        self.tbl_der.tag_configure("par",     background="#ffffff")
        self.tbl_der.tag_configure("impar",   background="#f0f4fa")
        self.tbl_der.tag_configure("rub_hdr", background="#ddeeff",
                                   font=("Segoe UI", 10, "bold"))

        self.tbl_der.bind("<Double-1>", self._doble_clic_der)
        self.tbl_der.bind("<ButtonRelease-1>", self._clic_der_subc)
        self.tbl_der.bind("<Button-3>", self._menu_der_der)

        # Entry flotante para editar Subc.
        self._subc_var = tk.StringVar()
        self._subc_entry = ttk.Entry(der, textvariable=self._subc_var,
                                     font=FUENTE, width=4, justify="center")
        self._subc_entry.bind("<Return>",  self._confirmar_subc)
        self._subc_entry.bind("<Escape>",  lambda e: self._subc_entry.place_forget())
        self._subc_entry.bind("<FocusOut>", self._confirmar_subc)
        self._subc_iid = None   # iid de la fila que se está editando

        # Poblar desde datos ya cargados (al abrir una obra existente)
        if getattr(self.obra, "items_presupuesto", []):
            self._poblar_iz()

    def _clic_der_subc(self, event=None):
        """Si el clic fue sobre la columna Subc., abre el Entry inline."""
        region = self.tbl_der.identify_region(event.x, event.y)
        col    = self.tbl_der.identify_column(event.x)
        iid    = self.tbl_der.identify_row(event.y)
        if region != "cell" or col != "#1" or not iid or iid.startswith("__rub_"):
            return
        # posicionar Entry sobre la celda
        x, y, w, h = self.tbl_der.bbox(iid, col)
        if not x:
            return
        vals = self.tbl_der.item(iid, "values")
        self._subc_var.set(vals[0] if vals else "")
        self._subc_iid = iid
        self._subc_entry.place(x=self.tbl_der.winfo_x() + x,
                               y=self.tbl_der.winfo_y() + y,
                               width=w, height=h)
        self._subc_entry.focus_set()
        self._subc_entry.select_range(0, "end")

    def _confirmar_subc(self, event=None):
        """Guarda la letra de subcontrato en la fila derecha."""
        if not self._subc_iid:
            return
        val = self._subc_var.get().strip().upper()[:1]
        LETRAS_VALIDAS = {"", "S", "T", "E", "X"}
        if val not in LETRAS_VALIDAS:
            val = ""
        iid  = self._subc_iid
        vals = list(self.tbl_der.item(iid, "values"))
        vals[0] = val
        self.tbl_der.item(iid, values=vals)
        # guardar en items_presupuesto si esta tarea ya está vinculada
        items = getattr(self.obra, "items_presupuesto", [])
        for it in items:
            if it.get("cod_tar") == iid:
                it["subcontrato"] = val
        self._subc_entry.place_forget()
        self._subc_iid = None

    def _cargar_tareas(self):
        """Puebla ambos paneles."""
        if not hasattr(self, "tbl_iz") or not hasattr(self, "tbl_der"):
            return

        # ── Panel izquierdo ───────────────────────────────────────────────
        self._poblar_iz()

        # ── Panel derecho ─────────────────────────────────────────────────
        for item in self.tbl_der.get_children():
            self.tbl_der.delete(item)

        texto = self.var_bus.get().lower().strip()
        rubros_activos = {r for r, v in self.vars_rubros.items() if v.get()}

        if not rubros_activos:
            self.tbl_der.insert("", "end",
                values=("", "← Seleccioná rubros en la pestaña 1.", ""))
            return

        i = 0
        for rubro in self.maestro["rubros"]:
            if rubro not in rubros_activos:
                continue
            tareas_rubro = [
                t for t in self.maestro["tareas"][rubro]
                if len(t["cod"]) == 4          # excluir subcontratos (5 chars)
                and (not texto
                     or texto in t["nombre"].lower())
            ]
            if not tareas_rubro:
                continue
            # encabezado de rubro
            self.tbl_der.insert("", "end", iid=f"__rub_{rubro}",
                                tags=("rub_hdr",),
                                values=("", rubro, ""))
            for t in sorted(tareas_rubro, key=lambda x: x["cod"]):
                tag = "par" if i % 2 == 0 else "impar"
                self.tbl_der.insert("", "end", iid=t["cod"], tags=(tag,),
                                    values=("", t["nombre"], t["unidad"]))
                i += 1

        self._actualizar_st()

    def _poblar_iz(self):
        """Redibuja el panel izquierdo desde obra.items_presupuesto."""
        for item in self.tbl_iz.get_children():
            self.tbl_iz.delete(item)

        items = getattr(self.obra, "items_presupuesto", [])

        # Ordenar: encabezado de rubro primero, luego items por número dentro del rubro
        def _sort_key(it):
            rub = it.get("rubro", "")
            es_rub = it.get("es_rubro", False)
            item_num = it.get("item", "")
            try:
                item_int = int(item_num) if item_num else 0
            except ValueError:
                item_int = 0
            return (rub, 0 if es_rub else 1, item_int)
        items = sorted(items, key=_sort_key)
        self.obra.items_presupuesto = items

        sin_vnc = 0
        for idx, it in enumerate(items):
            es_rubro = it.get("es_rubro", False)
            if es_rubro:
                self.tbl_iz.insert("", "end", iid=str(idx), tags=("rubro_hdr",),
                    values=(it.get("rubro", ""), "",
                            it.get("descripcion", ""), "", ""))
            else:
                vinculado = bool(it.get("cod_tar"))
                if vinculado:
                    tag = "vinculada"
                else:
                    tag = "sin_vnc"
                    sin_vnc += 1
                rub = it.get("rubro", "")
                ite = it.get("item", "")
                num = f"{rub}.{ite}" if rub and ite else (rub or ite)
                cant = it.get("cantidad", "")
                cant_str = f"{cant:,.2f}" if isinstance(cant, (int, float)) else str(cant)
                self.tbl_iz.insert("", "end", iid=str(idx), tags=(tag,),
                    values=(rub, ite,
                            it.get("descripcion", ""),
                            it.get("unidad", ""),
                            cant_str))

        msg = f"⚠  {sin_vnc} tarea{'s' if sin_vnc!=1 else ''} sin equivalente." if sin_vnc else ""
        self.lbl_sin_vinculo.config(text=msg)

    def _clic_fila_iz(self, event=None):
        """Selecciona fila izq (azul) y scrollea derecha al rubro correspondiente."""
        sel = self.tbl_iz.selection()
        if not sel:
            return
        idx = int(sel[0])
        items = getattr(self.obra, "items_presupuesto", [])
        if idx >= len(items):
            return
        it = items[idx]
        if it.get("es_rubro"):
            return

        self._item_sel_idx = idx

        # remarcar azul
        self._poblar_iz()
        self.tbl_iz.item(str(idx), tags=("sel",))
        self.tbl_iz.see(str(idx))

        # scrollear derecha al rubro del item si hay match
        rubro_it = it.get("rubro_std", "")   # rubro standard guardado al vincular
        if rubro_it:
            hdr_id = f"__rub_{rubro_it}"
            if self.tbl_der.exists(hdr_id):
                self.tbl_der.see(hdr_id)

    def _doble_clic_iz(self, event=None):
        """Doble clic en izquierda: abre diálogo para editar la fila."""
        sel = self.tbl_iz.selection()
        if not sel:
            return
        idx = int(sel[0])
        items = getattr(self.obra, "items_presupuesto", [])
        if idx >= len(items):
            return
        it = items[idx]
        if it.get("es_rubro"):
            self._editar_fila_rubro(idx, it)
        else:
            self._editar_fila_item(idx, it)

    def _doble_clic_der(self, event=None):
        """Doble clic en derecha: vincula la tarea a la fila izq seleccionada."""
        sel_der = self.tbl_der.selection()
        if not sel_der:
            return
        cod = sel_der[0]
        if cod.startswith("__rub_"):
            return   # es encabezado
        if self._item_sel_idx is None:
            messagebox.showinfo("Sin selección",
                "Primero hacé clic en una fila del presupuesto (izquierda).",
                parent=self)
            return

        items = getattr(self.obra, "items_presupuesto", [])
        it = items[self._item_sel_idx]
        t  = self.maestro["tareas_por_cod"].get(cod)
        if not t:
            return

        # Si ya tiene vínculo, preguntar
        if it.get("cod_tar") and it["cod_tar"] != cod:
            ok = messagebox.askyesno(
                "Cambiar vínculo",
                f"Esta fila ya está vinculada a:\n{it['cod_tar']} — {self.maestro['tareas_por_cod'].get(it['cod_tar'],{}).get('nombre','?')}\n\n"
                f"¿La cambiás por:\n{cod} — {t['nombre']}?",
                parent=self)
            if not ok:
                return

        # Guardar subcontrato si hay algo en el entry de la fila derecha
        subcont = it.get("subcontrato", "")

        it["cod_tar"]     = cod
        it["unidad"]      = it.get("unidad") or t["unidad"]
        it["rubro_std"]   = t["rubro"]
        it["subcontrato"] = subcont

        # marcar azul la tarea derecha
        self._refrescar_der_sel(cod)
        # repoblar izquierda
        self._poblar_iz()
        self.tbl_iz.item(str(self._item_sel_idx), tags=("sel",))
        self.tbl_iz.see(str(self._item_sel_idx))
        self._actualizar_st()

    def _refrescar_der_sel(self, cod):
        """Marca azul la fila cod en el panel derecho."""
        for iid in self.tbl_der.get_children():
            if iid.startswith("__rub_"):
                continue
            tags = list(self.tbl_der.item(iid, "tags"))
            tags = [t for t in tags if t not in ("sel","par","impar")]
            i = self.tbl_der.index(iid)
            tags.append("sel" if iid == cod else ("par" if i % 2 == 0 else "impar"))
            self.tbl_der.item(iid, tags=tags)

    def _agregar_fila(self):
        """Agrega una fila vacía al presupuesto."""
        items = getattr(self.obra, "items_presupuesto", [])
        # calcular próximo ítem mirando el máximo real, no el último
        ultimos = [it for it in items if not it.get("es_rubro")]
        if ultimos:
            # tomar el rubro del último ítem
            ul = ultimos[-1]
            rubro = ul.get("rubro", "01")
            # buscar el máximo número de ítem en ese rubro
            items_del_rubro = [
                it for it in ultimos
                if it.get("rubro") == rubro and it.get("item", "").isdigit()
            ]
            if items_del_rubro:
                max_item = max(int(it["item"]) for it in items_del_rubro)
                next_item = f"{max_item + 1:02d}"
            else:
                next_item = "01"
        else:
            rubro, next_item = "01", "01"
        items.append({
            "es_rubro":    False,
            "rubro":       rubro,
            "item":        next_item,
            "descripcion": "",
            "unidad":      "",
            "cantidad":    0.0,
            "cod_tar":     "",
            "subcontrato": "",
            "rubro_std":   "",
        })
        self.obra.items_presupuesto = items
        self._renumerar_items(items)
        self._poblar_iz()
        # seleccionar la nueva fila
        new_idx = len(items) - 1
        self._item_sel_idx = new_idx
        self.tbl_iz.selection_set(str(new_idx))
        self.tbl_iz.see(str(new_idx))
        self._editar_fila_item(new_idx, items[new_idx])

    def _importar_presupuesto(self):
        """Lee PlanillaCotizacion.xlsx de la carpeta de la obra."""
        from tkinter import filedialog
        ruta = filedialog.askopenfilename(
            parent=self,
            title="Importar planilla de cotización",
            initialdir=str(self.obra.carpeta),
            filetypes=[("Excel", "*.xlsx *.XLSX"), ("Todos", "*.*")],
        )
        if not ruta:
            return
        try:
            import openpyxl
            wb = openpyxl.load_workbook(ruta, read_only=True, data_only=True)
            ws = wb.active
            items = []
            for row in ws.iter_rows(min_row=2, values_only=True):
                if not any(row):
                    continue
                rub  = str(row[0]).strip() if row[0] is not None else ""
                ite  = str(row[1]).strip() if row[1] is not None else ""
                desc = str(row[2]).strip() if row[2] is not None else ""
                un   = str(row[3]).strip() if row[3] is not None else ""
                cant = row[4]
                try:
                    cant = float(cant) if cant is not None else 0.0
                except:
                    cant = 0.0
                # fila de rubro: item vacío, sin unidad
                es_rub = bool(rub and not ite and not un)
                items.append({
                    "es_rubro":    es_rub,
                    "rubro":       rub,
                    "item":        ite,
                    "descripcion": desc,
                    "unidad":      un,
                    "cantidad":    cant,
                    "cod_tar":     "",
                    "subcontrato": "",
                    "rubro_std":   "",
                })
            wb.close()
            self.obra.items_presupuesto = items
            self._poblar_iz()
            messagebox.showinfo("Importado",
                f"{len(items)} filas importadas.", parent=self)
        except Exception as e:
            messagebox.showerror("Error al importar", str(e), parent=self)

    def _editar_fila_item(self, idx, it):
        """Diálogo para editar una fila de ítem."""
        dlg = _DlgEditarFila(self, it)
        self.wait_window(dlg)
        if dlg.resultado:
            it.update(dlg.resultado)
            self._poblar_iz()
            self.tbl_iz.item(str(idx), tags=("sel",))
            self.tbl_iz.see(str(idx))

    def _editar_fila_rubro(self, idx, it):
        """Diálogo simple para editar encabezado de rubro."""
        dlg = _DlgEditarFila(self, it, es_rubro=True)
        self.wait_window(dlg)
        if dlg.resultado:
            it.update(dlg.resultado)
            self._poblar_iz()

    # ── Menús contextuales (botón derecho) ────────────────────────────────
    def _menu_der_iz(self, event):
        """Botón derecho en panel izquierdo: Editar / Insertar / Eliminar."""
        iid = self.tbl_iz.identify_row(event.y)
        if not iid:
            return
        self.tbl_iz.selection_set(iid)
        idx = int(iid)
        items = getattr(self.obra, "items_presupuesto", [])
        if idx >= len(items):
            return
        it = items[idx]

        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="✏  Editar",
                         command=lambda: self._doble_clic_iz())
        menu.add_separator()
        menu.add_command(label="⬆  Insertar fila arriba",
                         command=lambda: self._insertar_fila(idx, arriba=True))
        menu.add_command(label="⬇  Insertar fila abajo",
                         command=lambda: self._insertar_fila(idx, arriba=False))
        menu.add_separator()
        menu.add_command(label="🗑  Eliminar fila",
                         command=lambda: self._eliminar_fila_iz(idx))
        menu.tk_popup(event.x_root, event.y_root)

    def _insertar_fila(self, idx: int, arriba: bool):
        """Inserta una fila nueva antes o después de idx y reordena los ítems."""
        items = getattr(self.obra, "items_presupuesto", [])
        it_ref = items[idx]

        # heredar rubro del ítem de referencia
        rubro = it_ref.get("rubro", "01") if not it_ref.get("es_rubro") else it_ref.get("rubro", "01")

        nueva_fila = {
            "es_rubro":    False,
            "rubro":       rubro,
            "item":        "00",   # se renumerará abajo
            "descripcion": "",
            "unidad":      "",
            "cantidad":    0.0,
            "cod_tar":     "",
            "subcontrato": "",
            "rubro_std":   "",
        }

        pos = idx if arriba else idx + 1
        items.insert(pos, nueva_fila)

        # renumerar ítems por rubro manteniendo el orden
        self._renumerar_items(items)

        self.obra.items_presupuesto = items
        self._poblar_iz()
        self._item_sel_idx = pos
        self.tbl_iz.selection_set(str(pos))
        self.tbl_iz.see(str(pos))
        self._editar_fila_item(pos, items[pos])
        self._actualizar_st()

    def _renumerar_items(self, items: list):
        """Renumera correlativamente los ítems dentro de cada rubro."""
        contadores = {}   # rubro -> contador
        for it in items:
            if it.get("es_rubro"):
                continue
            rubro = it.get("rubro", "")
            contadores[rubro] = contadores.get(rubro, 0) + 1
            it["item"] = f"{contadores[rubro]:02d}"

    def _eliminar_fila_iz(self, idx=None):
        """Elimina la fila idx, o todas las seleccionadas si hay seleccion multiple."""
        items = getattr(self.obra, "items_presupuesto", [])

        sel = self.tbl_iz.selection()
        if sel:
            indices = sorted({int(iid) for iid in sel if iid.isdigit()}, reverse=True)
        elif idx is not None and idx < len(items):
            indices = [idx]
        else:
            return

        descs = [items[i].get("descripcion", "") or items[i].get("rubro", "")
                 for i in indices if i < len(items)]
        if not descs:
            return

        if len(descs) == 1:
            msg = f"¿Eliminás la fila:\n{descs[0]}?"
        else:
            lista = "\n".join(f"  • {d}" for d in descs[:8])
            if len(descs) > 8:
                lista += f"\n  ... y {len(descs)-8} más"
            msg = f"¿Eliminás las {len(descs)} filas seleccionadas?\n\n{lista}"

        ok = messagebox.askyesno("Eliminar filas", msg, parent=self)
        if ok:
            for i in indices:
                if i < len(items):
                    items.pop(i)
            self._renumerar_items(items)
            self.obra.items_presupuesto = items
            self._item_sel_idx = None
            for iid in self.tbl_iz.get_children():
                self.tbl_iz.delete(iid)
            self._poblar_iz()
            self._actualizar_st()

    def _menu_der_der(self, event):
        """Botón derecho en panel derecho: ver insumos de la tarea."""
        iid = self.tbl_der.identify_row(event.y)
        if not iid or iid.startswith("__rub_"):
            return
        self.tbl_der.selection_set(iid)
        t = self.maestro["tareas_por_cod"].get(iid)
        if not t:
            return

        # obtener letra de subcontrato de la fila derecha
        vals = self.tbl_der.item(iid, "values")
        subcont = vals[0].strip().upper() if vals else ""

        menu = tk.Menu(self, tearoff=0)
        menu.add_command(
            label=f"📋  Ver insumos de esta tarea",
            command=lambda: self._ver_insumos_tarea(iid, subcont))
        menu.tk_popup(event.x_root, event.y_root)

    def _ver_insumos_tarea(self, cod_tar: str, subcont: str):
        """Muestra ventana con los insumos de la tarea, considerando subcontrato."""
        incidencias = self.maestro["incidencias"]
        insumos_cat = self.maestro["insumos"]

        # si hay subcontrato buscar variante
        cod_buscar = cod_tar + subcont if subcont else cod_tar
        lista = incidencias.get(cod_buscar) or incidencias.get(cod_tar, [])

        t = self.maestro["tareas_por_cod"].get(cod_tar, {})
        titulo = t.get("nombre", cod_tar)
        if subcont:
            titulo += f"  [{subcont}]"

        dlg = _DlgInsumosTarea(self, titulo, lista, insumos_cat)
        dlg.grab_set()
    # ═════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════
    # TAB 3 — INSUMOS Y PRECIOS
    # ═════════════════════════════════════════════════════════════════════
    def _build_ins(self):
        f = self.tab_ins
        frm_top = tk.Frame(f, bg=COLOR_BG)
        frm_top.pack(side="top", fill="x", padx=16, pady=(10, 2))
        tk.Label(frm_top, text="Insumos de la obra:",
                 bg=COLOR_BG, font=FUENTE_B, fg=COLOR_HDR).pack(side="left")
        frm_prc = tk.Frame(f, bg=COLOR_BG)
        frm_prc.pack(side="top", fill="x", padx=16, pady=(0, 6))
        tk.Label(frm_prc, text="Archivo de precios:",
                 bg=COLOR_BG, font=FUENTE_S, fg="#555").pack(side="left")
        self.var_arch_prc = tk.StringVar(value="Sin archivo seleccionado")
        tk.Label(frm_prc, textvariable=self.var_arch_prc,
                 bg=COLOR_BG, font=FUENTE_S, fg=COLOR_HDR).pack(side="left", padx=6)
        tk.Button(frm_prc, text="Seleccionar archivo...",
                  bg=COLOR_SEC, fg="white", font=FUENTE_S,
                  relief="flat", padx=8, pady=3, cursor="hand2",
                  command=self._elegir_precios).pack(side="left", padx=(8, 0))

        # Barra de totales y boton exportar (bottom)
        frm_btn = tk.Frame(f, bg=COLOR_BG)
        frm_btn.pack(side="bottom", fill="x", padx=16, pady=6)
        tk.Button(frm_btn, text="Exportar faltantes (.txt)",
                  bg="#b06000", fg="white", font=FUENTE_S,
                  relief="flat", padx=10, pady=4, cursor="hand2",
                  command=self._exportar_faltantes).pack(side="right")
        tk.Label(frm_btn,
                 text="Verde = con precio  |  Rojo = sin precio  |  Doble clic para cargar precio",
                 bg=COLOR_BG, fg="#777", font=FUENTE_S).pack(side="left")
        self.lbl_total = tk.Label(f, text="", bg="#e8f0f8",
                                  font=FUENTE_B, anchor="e", fg=COLOR_HDR,
                                  pady=4, padx=12)
        self.lbl_total.pack(side="bottom", fill="x", padx=16, pady=(0, 2))
        # Treeview
        cols = ("cod", "nombre", "unidad", "cantidad", "precio", "subtotal", "estado")
        self.tbl_ins = ttk.Treeview(f, columns=cols, show="headings", selectmode="browse")
        anchos = {"cod": 72, "nombre": 285, "unidad": 56,
                  "cantidad": 88, "precio": 100, "subtotal": 110, "estado": 88}
        textos = {"cod": "Codigo", "nombre": "Insumo", "unidad": "Unidad",
                  "cantidad": "Cantidad", "precio": "P. Unit.",
                  "subtotal": "Subtotal", "estado": "Estado"}
        anclas = {"cod": "w", "nombre": "w", "unidad": "center",
                  "cantidad": "e", "precio": "e", "subtotal": "e", "estado": "center"}
        for c in cols:
            self.tbl_ins.heading(c, text=textos[c])
            self.tbl_ins.column(c, width=anchos[c], minwidth=28, anchor=anclas[c])
        scr = ttk.Scrollbar(f, orient="vertical", command=self.tbl_ins.yview)
        self.tbl_ins.configure(yscrollcommand=scr.set)
        scr.pack(side="right", fill="y", padx=(0, 16))
        self.tbl_ins.pack(side="left", fill="both", expand=True, padx=(16, 0))
        self.tbl_ins.tag_configure("ok",       background="#d4edda")
        self.tbl_ins.tag_configure("faltante", background="#fde8e8")
        self.tbl_ins.bind("<Double-1>", lambda _: self._editar_precio())
        self.tbl_ins.bind("<F2>",       lambda _: self._editar_precio())

    def _elegir_precios(self):
        from tkinter import filedialog
        # Primero busca en la carpeta Precios de la obra, luego en Data/Precios global
        carpeta_precios_obra = self.obra.carpeta_precios
        initial = str(carpeta_precios_obra) if carpeta_precios_obra.exists() \
                  else (str(CARPETA_PRECIOS) if CARPETA_PRECIOS.exists() else str(CARPETA_DATA))
        ruta = filedialog.askopenfilename(
            parent=self,
            title="Seleccionar archivo de precios",
            initialdir=initial,
            filetypes=[("Excel", "*.xlsx *.XLSX"), ("Todos", "*.*")],
        )
        if not ruta:
            return
        try:
            self._precios = cargar_precios(ruta)
            self._nombre_precios = Path(ruta).name
            self._ruta_precios = Path(ruta)
            self.var_arch_prc.set(self._nombre_precios)
            self._cargar_ins()
        except Exception as e:
            messagebox.showerror("Error al leer precios", str(e), parent=self)

    def _cargar_ins(self):
        for item in self.tbl_ins.get_children():
            self.tbl_ins.delete(item)
        insumos = self.obra.calcular_insumos(self.maestro["incidencias"])
        if not insumos:
            self.tbl_ins.insert("", "end", values=(
                "", "Sin tareas o sin cantidades cargadas.", "", "", "", "", ""))
            self.lbl_total.config(text="")
            return
        cat   = self.maestro["insumos"]
        total = 0.0
        falt  = 0
        for cod_ins, datos in sorted(insumos.items()):
            nombre = cat.get(cod_ins, {}).get("nombre", cod_ins)
            unidad = datos["unidad"]
            cant   = datos["cantidad_total"]
            precio = self._precios.get(cod_ins)
            if precio and precio > 0:
                sub   = cant * precio
                total += sub
                tag   = "ok"
                p_str = f"$ {precio:,.2f}"
                s_str = f"$ {sub:,.2f}"
                est   = "Con precio"
            else:
                falt += 1
                tag   = "faltante"
                p_str = "-"
                s_str = "-"
                est   = "Sin precio"
            self.tbl_ins.insert("", "end", iid=cod_ins, tags=(tag,),
                                values=(cod_ins, nombre, unidad,
                                        f"{cant:,.2f}", p_str, s_str, est))
        n_total = len(insumos)
        pct = int(100 * (n_total - falt) / n_total) if n_total else 0
        self.lbl_total.config(
            text=f"Total cotizado: $ {total:,.2f}   |   "
                 f"Con precio: {n_total - falt}   |   "
                 f"Sin precio: {falt}   |   "
                 f"Cobertura: {pct}%")

    def _editar_precio(self):
        sel = self.tbl_ins.selection()
        if not sel:
            return
        cod = sel[0]
        nombre = self.maestro["insumos"].get(cod, {}).get("nombre", cod)
        actual = self._precios.get(cod, "")
        dlg = _DlgVal(self, f"Precio - {cod}", nombre, "", actual, es_precio=True)
        self.wait_window(dlg)
        if dlg.resultado is None:
            return
        if dlg.resultado > 0:
            self._precios[cod] = dlg.resultado
        else:
            self._precios.pop(cod, None)
        self._cargar_ins()
        if self.tbl_ins.exists(cod):
            self.tbl_ins.selection_set(cod)

    def _exportar_faltantes(self):
        from tkinter import filedialog
        falt = self.obra.insumos_sin_precio(self.maestro["incidencias"], self._precios)
        if not falt:
            messagebox.showinfo("Sin faltantes", "Todos los insumos tienen precio.",
                                parent=self)
            return
        cat = self.maestro["insumos"]
        lineas = ["Codigo\tInsumo\tUnidad"] + [
            f"{c}\t{cat.get(c,{}).get('nombre','?')}\t{cat.get(c,{}).get('unidad','')}"
            for c in sorted(falt)
        ]
        ruta = filedialog.asksaveasfilename(
            parent=self,
            title="Guardar insumos sin precio",
            initialdir=str(self.obra.carpeta_data),
            initialfile=f"pedir_precios_{self.obra.numero}.txt",
            defaultextension=".txt",
            filetypes=[("Texto", "*.txt"), ("Todos", "*.*")],
        )
        if ruta:
            Path(ruta).write_text("\n".join(lineas), encoding="utf-8")
            messagebox.showinfo("Exportado", f"{len(falt)} insumos exportados.",
                                parent=self)

    # ═════════════════════════════════════════════════════════════════════
    # TAB 4 — PRESUPUESTO VALORIZADO
    # ═════════════════════════════════════════════════════════════════════
    def _build_presupuesto(self):
        f = self.tab_ppto

        # ── Barra superior ────────────────────────────────────────────────
        frm_top = tk.Frame(f, bg=COLOR_BG)
        frm_top.pack(side="top", fill="x", padx=12, pady=(8, 2))
        tk.Label(frm_top, text="Presupuesto valorizado",
                 bg=COLOR_BG, font=FUENTE_B, fg=COLOR_HDR).pack(side="left")
        tk.Button(frm_top, text="↺ Actualizar", bg=COLOR_SEC, fg="white",
                  font=FUENTE_S, relief="flat", padx=8, pady=3, cursor="hand2",
                  command=self._cargar_presupuesto).pack(side="right")

        # ── Treeview con filas expandibles ───────────────────────────────
        cols = ("rubro", "item", "descripcion", "unidad", "cantidad", "precio", "total")
        self.tbl_ppto = ttk.Treeview(f, columns=cols, show="headings",
                                     selectmode="browse")
        anchos = {"rubro": 42, "item": 42, "descripcion": 280,
                  "unidad": 56, "cantidad": 80, "precio": 100, "total": 110}
        textos = {"rubro": "Rubro", "item": "Ítem", "descripcion": "Descripción",
                  "unidad": "Unidad", "cantidad": "Cantidad",
                  "precio": "P. Unit.", "total": "Total"}
        anclas = {"rubro": "center", "item": "center", "descripcion": "w",
                  "unidad": "center", "cantidad": "e", "precio": "e", "total": "e"}
        for c in cols:
            self.tbl_ppto.heading(c, text=textos[c])
            self.tbl_ppto.column(c, width=anchos[c], minwidth=24, anchor=anclas[c])

        scr = ttk.Scrollbar(f, orient="vertical", command=self.tbl_ppto.yview)
        self.tbl_ppto.configure(yscrollcommand=scr.set)
        scr.pack(side="right", fill="y", padx=(0, 8))
        self.tbl_ppto.pack(fill="both", expand=True, padx=(8, 0), pady=(4, 0))

        # tags
        self.tbl_ppto.tag_configure("rub_hdr",
            background="#1a3a5c", foreground="white",
            font=("Segoe UI", 10, "bold"))
        self.tbl_ppto.tag_configure("tarea_ok",
            background="#ffffff")
        self.tbl_ppto.tag_configure("tarea_sinprecio",
            background="#fff3cd")
        self.tbl_ppto.tag_configure("tarea_alt",
            background="#f5f5f5")
        self.tbl_ppto.tag_configure("insumo",
            background="#eef4fb", foreground="#1a3a5c",
            font=("Segoe UI", 9))
        self.tbl_ppto.tag_configure("insumo_alt",
            background="#e4ecf7", foreground="#1a3a5c",
            font=("Segoe UI", 9))
        self.tbl_ppto.tag_configure("total_general",
            background="#1a3a5c", foreground="white",
            font=("Segoe UI", 10, "bold"))

        # click en + para expandir/contraer
        self.tbl_ppto.bind("<ButtonRelease-1>", self._toggle_ppto)

        # ── Total general (pie) ───────────────────────────────────────────
        self.lbl_total_ppto = tk.Label(f, text="", bg="#e8f0f8",
                                       font=FUENTE_B, anchor="e",
                                       fg=COLOR_HDR, pady=5, padx=12)
        self.lbl_total_ppto.pack(side="bottom", fill="x", padx=8, pady=(0, 4))

        self._ppto_expandido = set()   # iids de tareas expandidas

    def _cargar_presupuesto(self):
        if not hasattr(self, "tbl_ppto"):
            return
        for item in self.tbl_ppto.get_children():
            self.tbl_ppto.delete(item)

        items       = getattr(self.obra, "items_presupuesto", [])
        incidencias = self.maestro["incidencias"]
        insumos_cat = self.maestro["insumos"]
        precios     = self._precios

        # ── Pre-calcular totales por rubro ────────────────────────────────
        # Necesitamos saber el total de cada rubro antes de insertar el hdr
        # Hacemos una pasada previa
        totales_rubro = {}   # idx_rubro -> total
        rubro_idx_actual = None
        for idx, it in enumerate(items):
            if it.get("es_rubro"):
                rubro_idx_actual = idx
                totales_rubro[idx] = 0.0
                continue
            if rubro_idx_actual is None:
                continue
            cod_tar = it.get("cod_tar", "")
            subcont = (it.get("subcontrato") or "").strip().upper()
            cant    = it.get("cantidad") or 0.0
            cod_buscar = cod_tar + subcont if (cod_tar and subcont) else cod_tar
            lista_inc  = incidencias.get(cod_buscar) or incidencias.get(cod_tar, [])
            precio_unit = sum(
                (precios.get(inc["cod_ins"], 0.0) or 0.0) * inc["cantidad"]
                for inc in lista_inc
            )
            totales_rubro[rubro_idx_actual] += precio_unit * cant

        # ── Insertar filas ────────────────────────────────────────────────
        total_general = 0.0
        i_tarea = 0

        for idx, it in enumerate(items):
            if it.get("es_rubro"):
                rub  = it.get("rubro", "")
                desc = it.get("descripcion", "")
                sub  = totales_rubro.get(idx, 0.0)
                sub_str = f"$ {sub:,.2f}" if sub else ""
                self.tbl_ppto.insert("", "end",
                    iid=f"rub_{idx}", tags=("rub_hdr",),
                    values=(rub, "", desc, "", "", "", sub_str))
                continue

            cod_tar  = it.get("cod_tar", "")
            subcont  = (it.get("subcontrato") or "").strip().upper()
            cant     = it.get("cantidad") or 0.0
            desc     = it.get("descripcion", "")
            unidad   = it.get("unidad", "")
            rub      = it.get("rubro", "")
            item_num = it.get("item", "")

            cod_buscar = cod_tar + subcont if (cod_tar and subcont) else cod_tar
            lista_inc  = incidencias.get(cod_buscar) or incidencias.get(cod_tar, [])

            precio_unit = 0.0
            todos_con_precio = True
            insumos_detalle  = []

            for inc in lista_inc:
                cod_ins    = inc["cod_ins"]
                p_ins      = precios.get(cod_ins, 0.0) or 0.0
                cant_ins   = inc["cantidad"]
                sub_ins    = cant_ins * p_ins
                precio_unit += sub_ins
                if p_ins == 0:
                    todos_con_precio = False
                nombre_ins = insumos_cat.get(cod_ins, {}).get("nombre", cod_ins)
                insumos_detalle.append({
                    "cod": cod_ins, "nombre": nombre_ins,
                    "unidad": inc.get("unidad", ""),
                    "incidencia": cant_ins,
                    "precio": p_ins, "subtotal": sub_ins,
                })

            total_tarea    = precio_unit * cant
            total_general += total_tarea

            tag = ("tarea_ok" if todos_con_precio and precio_unit > 0
                   else "tarea_sinprecio") if i_tarea % 2 == 0 else \
                  ("tarea_alt" if todos_con_precio and precio_unit > 0
                   else "tarea_sinprecio")

            iid_tarea = f"tar_{idx}"
            expandido = iid_tarea in self._ppto_expandido
            prefijo   = "▼ " if expandido else "▶ "

            p_str = f"$ {precio_unit:,.2f}" if precio_unit else "-"
            t_str = f"$ {total_tarea:,.2f}"  if precio_unit else "-"
            c_str = f"{cant:,.2f}" if cant else "-"

            self.tbl_ppto.insert("", "end", iid=iid_tarea, tags=(tag,),
                values=(rub, item_num, prefijo + desc,
                        unidad, c_str, p_str, t_str))

            if expandido:
                for j, ins in enumerate(insumos_detalle):
                    tag_ins = "insumo" if j % 2 == 0 else "insumo_alt"
                    p_i = f"$ {ins['precio']:,.2f}" if ins['precio'] else "Sin precio"
                    s_i = f"$ {ins['subtotal']:,.2f}" if ins['precio'] else "-"
                    self.tbl_ppto.insert("", "end",
                        iid=f"ins_{idx}_{j}", tags=(tag_ins,),
                        values=("", "",
                                f"    {ins['nombre']}",
                                ins["unidad"],
                                f"{ins['incidencia']:g}",
                                p_i, s_i))
            i_tarea += 1

        # fila total general
        if total_general > 0:
            self.tbl_ppto.insert("", "end", iid="total_gen",
                tags=("total_general",),
                values=("", "", "TOTAL GENERAL", "", "", "",
                        f"$ {total_general:,.2f}"))

        self.lbl_total_ppto.config(
            text=f"Total general:  $ {total_general:,.2f}   "
                 f"({'sin precios completos' if not precios else 'basado en precios cargados'})")

    def _toggle_ppto(self, event=None):
        """Expande o contrae los insumos de una fila de tarea."""
        iid = self.tbl_ppto.identify_row(event.y)
        if not iid or not iid.startswith("tar_"):
            return
        col = self.tbl_ppto.identify_column(event.x)
        # solo reacciona al click en la columna descripcion (#3)
        if col != "#3":
            return
        if iid in self._ppto_expandido:
            self._ppto_expandido.discard(iid)
        else:
            self._ppto_expandido.add(iid)
        self._cargar_presupuesto()

    # ─────────────────────────────────────────────────────────────────────
    def _on_tab(self, _event):
        idx = self.nb.index("current")
        if idx == 1:
            self._cargar_tareas()
        elif idx == 2:
            self._cargar_ins()
        elif idx == 3:
            self._cargar_presupuesto()

    def _actualizar_st(self):
        items = getattr(self.obra, "items_presupuesto", [])
        n_items    = sum(1 for it in items if not it.get("es_rubro"))
        n_vnc      = sum(1 for it in items if not it.get("es_rubro") and it.get("cod_tar"))
        sin_vnc    = n_items - n_vnc
        self.lbl_st.config(
            text=f"  {n_items} ítems  |  {n_vnc} vinculados  |  {sin_vnc} sin vincular")
        msg = f"⚠  {sin_vnc} tarea{'s' if sin_vnc!=1 else ''} sin equivalente." if sin_vnc else ""
        if hasattr(self, "lbl_sin_vinculo"):
            self.lbl_sin_vinculo.config(text=msg)

    def _guardar_precios_xlsx(self):
        precios_validos = {c: p for c, p in self._precios.items() if p and p > 0}
        if not precios_validos:
            return 0
        dlg = _DlgGuardarPrecios(self, self._nombre_precios,
                                  self._ruta_precios, CARPETA_PRECIOS)
        self.wait_window(dlg)
        if dlg.ruta_destino is None:
            return 0
        ruta_origen  = self._ruta_precios
        ruta_destino = dlg.ruta_destino
        try:
            import openpyxl
            if ruta_origen and ruta_origen.exists():
                wb = openpyxl.load_workbook(str(ruta_origen))
                ws = wb["Insumos"]
                actualizados = 0
                for row in ws.iter_rows(min_row=2):
                    if row[0].value is None:
                        continue
                    cod = str(row[0].value).strip()
                    if cod in precios_validos:
                        row[3].value = precios_validos[cod]
                        actualizados += 1
                wb.save(str(ruta_destino))
            else:
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.title = "Insumos"
                ws.append(["Codigo Insumo", "Descripcion", "Unidad", "Precio Unitario"])
                cat = self.maestro["insumos"]
                insumos_obra = self.obra.calcular_insumos(self.maestro["incidencias"])
                actualizados = 0
                for cod in sorted(insumos_obra):
                    ins = cat.get(cod, {})
                    precio = precios_validos.get(cod, None)
                    ws.append([cod, ins.get("nombre", ""),
                               ins.get("unidad", ""), precio])
                    if precio:
                        actualizados += 1
                wb.save(str(ruta_destino))
            self._ruta_precios   = ruta_destino
            self._nombre_precios = ruta_destino.name
            self.var_arch_prc.set(self._nombre_precios)
            return actualizados
        except Exception as e:
            messagebox.showwarning("Precios no guardados", str(e), parent=self)
            return 0

    def _guardar(self, silencioso=False):
        try:
            # reconstruir obra.tareas desde items vinculados (compat)
            self.obra.tareas = {}
            for it in self.obra.items_presupuesto:
                if it.get("es_rubro") or not it.get("cod_tar"):
                    continue
                cod = it["cod_tar"]
                t   = self.maestro["tareas_por_cod"].get(cod, {})
                self.obra.tareas[cod] = {
                    "cod":            cod,
                    "base":           t.get("base", cod),
                    "variante":       t.get("variante", " "),
                    "nombre":         t.get("nombre", ""),
                    "nombre_editado": it.get("descripcion", t.get("nombre", "")),
                    "unidad":         it.get("unidad", t.get("unidad", "")),
                    "rubro":          t.get("rubro", ""),
                    "cantidad":       it.get("cantidad", 0.0),
                    "subcontrato":    it.get("subcontrato", ""),
                }

            # preguntar si pisar o nueva versión
            nueva_version = False
            nota = ""
            if not silencioso and self.obra.ruta_json.exists():
                dlg = _DlgGuardarVersion(self, self.obra.ruta_json.name)
                self.wait_window(dlg)
                if dlg.accion is None:
                    return   # canceló
                nueva_version = dlg.accion == "nueva"
                nota = dlg.nota

            self.obra.guardar(nueva_version=nueva_version, nota=nota)
            if not silencioso:
                ver = f"obra{self.obra.version:03d}.json"
                self.lbl_st.config(text=f"  Guardado en {ver}.")
        except Exception as e:
            messagebox.showerror("Error al guardar", str(e), parent=self)


# ── Diálogo insumos de una tarea ─────────────────────────────────────────
class _DlgInsumosTarea(tk.Toplevel):
    def __init__(self, parent, titulo: str, incidencias: list, insumos_cat: dict):
        super().__init__(parent)
        self.title("Insumos de la tarea")
        self.geometry("620x400")
        self.minsize(480, 300)

        hdr = tk.Frame(self, bg=COLOR_HDR, height=40)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text=f"  {titulo}",
                 bg=COLOR_HDR, fg="white", font=FUENTE_B,
                 wraplength=580, anchor="w").pack(side="left", padx=12)

        cols = ("cod", "nombre", "unidad", "cantidad")
        tbl = ttk.Treeview(self, columns=cols, show="headings", selectmode="none")
        anchos  = {"cod": 72, "nombre": 320, "unidad": 60, "cantidad": 90}
        textos  = {"cod": "Código", "nombre": "Insumo",
                   "unidad": "Unidad", "cantidad": "Incidencia"}
        anclas  = {"cod": "w", "nombre": "w", "unidad": "center", "cantidad": "e"}
        for c in cols:
            tbl.heading(c, text=textos[c])
            tbl.column(c, width=anchos[c], anchor=anclas[c])

        scr = ttk.Scrollbar(self, orient="vertical", command=tbl.yview)
        tbl.configure(yscrollcommand=scr.set)
        scr.pack(side="right", fill="y", padx=(0, 8))
        tbl.pack(fill="both", expand=True, padx=(8, 0), pady=(6, 0))

        tbl.tag_configure("par",   background="#ffffff")
        tbl.tag_configure("impar", background="#f0f4fa")

        for i, inc in enumerate(incidencias):
            cod    = inc["cod_ins"]
            nombre = insumos_cat.get(cod, {}).get("nombre", cod)
            unidad = inc.get("unidad", "")
            cant   = inc.get("cantidad", 0)
            tag    = "par" if i % 2 == 0 else "impar"
            tbl.insert("", "end", tags=(tag,),
                       values=(cod, nombre, unidad, f"{cant:g}"))

        # pie
        frm_pie = tk.Frame(self, bg=COLOR_BG, pady=6)
        frm_pie.pack(fill="x")
        tk.Label(frm_pie,
                 text=f"  {len(incidencias)} insumo{'s' if len(incidencias)!=1 else ''}",
                 bg=COLOR_BG, font=FUENTE_S, fg="#555").pack(side="left", padx=12)
        tk.Button(frm_pie, text="Cerrar", bg="#888", fg="white",
                  font=FUENTE, relief="flat", padx=12, pady=4,
                  command=self.destroy).pack(side="right", padx=12)

        self.bind("<Escape>", lambda _: self.destroy())
        self.update_idletasks()
        self.geometry(
            f"+{parent.winfo_x()+(parent.winfo_width()-self.winfo_width())//2}"
            f"+{parent.winfo_y()+(parent.winfo_height()-self.winfo_height())//2}")


# ── Diálogo guardar versión ───────────────────────────────────────────────
class _DlgGuardarVersion(tk.Toplevel):
    def __init__(self, parent, nombre_actual: str):
        super().__init__(parent)
        self.title("Guardar obra")
        self.resizable(False, False)
        self.grab_set()
        self.accion = None   # "pisar" | "nueva" | None=canceló
        self.nota   = ""

        hdr = tk.Frame(self, bg=COLOR_HDR, height=40)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="  ¿Cómo querés guardar?",
                 bg=COLOR_HDR, fg="white", font=FUENTE_B).pack(side="left", padx=12)

        frm = tk.Frame(self, padx=20, pady=14)
        frm.pack(fill="both", expand=True)

        tk.Button(frm,
                  text=f"Actualizar  {nombre_actual}",
                  bg=COLOR_VERDE, fg="white", font=FUENTE_B,
                  relief="flat", padx=12, pady=8, cursor="hand2", anchor="w",
                  command=lambda: self._elegir("pisar")
                  ).pack(fill="x", pady=(0, 8))

        tk.Label(frm, text="Guardar como nueva versión:",
                 bg="#f5f5f5", font=FUENTE_S, fg="#555", anchor="w"
                 ).pack(fill="x")
        self.var_nota = tk.StringVar()
        ttk.Entry(frm, textvariable=self.var_nota, font=FUENTE, width=38
                  ).pack(fill="x", pady=(2, 6))
        tk.Label(frm, text="(describí los cambios — opcional)",
                 bg="#f5f5f5", font=("Segoe UI", 8), fg="#888"
                 ).pack(anchor="w")
        tk.Button(frm, text="Guardar como nueva versión...",
                  bg=COLOR_SEC, fg="white", font=FUENTE_B,
                  relief="flat", padx=12, pady=8, cursor="hand2",
                  command=lambda: self._elegir("nueva")
                  ).pack(fill="x", pady=(6, 8))
        tk.Button(frm, text="Cancelar",
                  bg="#888", fg="white", font=FUENTE,
                  relief="flat", padx=12, pady=6, cursor="hand2",
                  command=self.destroy).pack(fill="x")

        self.bind("<Escape>", lambda _: self.destroy())
        self.update_idletasks()
        self.geometry(
            f"+{parent.winfo_x()+(parent.winfo_width()-self.winfo_width())//2}"
            f"+{parent.winfo_y()+(parent.winfo_height()-self.winfo_height())//2}")

    def _elegir(self, accion: str):
        self.accion = accion
        self.nota   = self.var_nota.get().strip()
        self.destroy()


# ── Diálogo editar fila del presupuesto ──────────────────────────────────
class _DlgEditarFila(tk.Toplevel):
    def __init__(self, parent, it: dict, es_rubro=False):
        super().__init__(parent)
        self.title("Encabezado de Rubro" if es_rubro else "Editar ítem")
        self.resizable(False, False)
        self.grab_set()
        self.resultado = None
        self._es_rubro = es_rubro

        frm = tk.Frame(self, padx=18, pady=14)
        frm.pack(fill="both", expand=True)

        campos = []

        def fila(label, val, row):
            tk.Label(frm, text=label, font=FUENTE_S, anchor="e", width=12
                     ).grid(row=row, column=0, sticky="e", pady=4)
            var = tk.StringVar(value=str(val) if val else "")
            ent = ttk.Entry(frm, textvariable=var, font=FUENTE, width=28)
            ent.grid(row=row, column=1, sticky="ew", padx=(8, 0), pady=4)
            campos.append((label, var))
            return var, ent

        if es_rubro:
            v_rub, e_rub = fila("Rubro nro:", it.get("rubro", ""), 0)
            v_desc, _    = fila("Descripción:", it.get("descripcion", ""), 1)
            e_rub.focus_set()
        else:
            v_rub,  e_rub = fila("Rubro:",      it.get("rubro", ""), 0)
            v_item, _     = fila("Ítem:",        it.get("item", ""),  1)
            v_desc, _     = fila("Descripción:", it.get("descripcion", ""), 2)
            v_un,   _     = fila("Unidad:",      it.get("unidad", ""), 3)
            v_cant, _     = fila("Cantidad:",    it.get("cantidad", ""), 4)

            # subcont solo si ya está vinculado
            if it.get("cod_tar"):
                v_sub, _ = fila("Subcontrato:", it.get("subcontrato", ""), 5)
            e_rub.focus_set()

        frm.grid_columnconfigure(1, weight=1)

        frm_btn = tk.Frame(self, pady=8)
        frm_btn.pack()

        def _ok():
            res = {"es_rubro": es_rubro}
            if es_rubro:
                res["rubro"]       = v_rub.get().strip()
                res["descripcion"] = v_desc.get().strip()
            else:
                res["rubro"]       = v_rub.get().strip()
                res["item"]        = v_item.get().strip()
                res["descripcion"] = v_desc.get().strip()
                res["unidad"]      = v_un.get().strip()
                try:
                    res["cantidad"] = float(v_cant.get().replace(",", ".")) if v_cant.get().strip() else 0.0
                except ValueError:
                    messagebox.showwarning("Valor inválido", "Cantidad debe ser un número.", parent=self)
                    return
                if it.get("cod_tar"):
                    res["subcontrato"] = v_sub.get().strip().upper()[:1]
            self.resultado = res
            self.destroy()

        tk.Button(frm_btn, text="Aceptar", bg=COLOR_VERDE, fg="white",
                  font=FUENTE_B, relief="flat", padx=12, pady=5,
                  command=_ok).pack(side="left", padx=4)
        tk.Button(frm_btn, text="Cancelar", bg="#888", fg="white",
                  font=FUENTE, relief="flat", padx=12, pady=5,
                  command=self.destroy).pack(side="left")

        self.bind("<Return>", lambda _: _ok())
        self.bind("<Escape>", lambda _: self.destroy())
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(
            f"+{parent.winfo_x()+(parent.winfo_width()-w)//2}"
            f"+{parent.winfo_y()+(parent.winfo_height()-h)//2}")


# ── Diálogo genérico cantidad / precio ────────────────────────────────────
class _DlgVal(tk.Toplevel):
    def __init__(self, parent, titulo, nombre, unidad, valor_actual, es_precio=False):
        super().__init__(parent)
        self.title(titulo)
        self.geometry("380x180")
        self.resizable(False, False)
        self.grab_set()
        self.resultado = None
        tk.Label(self, text=nombre[:58], font=("Segoe UI", 9),
                 fg="#444", wraplength=360).pack(padx=16, pady=(14, 4), anchor="w")
        if unidad:
            tk.Label(self, text=f"Unidad: {unidad}",
                     font=FUENTE_S, fg="#777").pack(padx=16, anchor="w")
        frm = tk.Frame(self, pady=10)
        frm.pack(fill="x", padx=16)
        lbl = "Precio unitario: $" if es_precio else "Cantidad:"
        tk.Label(frm, text=lbl, font=FUENTE).pack(side="left")
        self.var = tk.StringVar(value=str(valor_actual) if valor_actual else "")
        ent = ttk.Entry(frm, textvariable=self.var, font=("Segoe UI", 11), width=14)
        ent.pack(side="left", padx=8)
        ent.select_range(0, "end")
        ent.focus_set()
        frm_btn = tk.Frame(self, pady=6)
        frm_btn.pack()
        tk.Button(frm_btn, text="Aceptar", bg=COLOR_VERDE, fg="white",
                  font=FUENTE_B, relief="flat", padx=12, pady=5,
                  command=self._ok).pack(side="left", padx=4)
        tk.Button(frm_btn, text="Cancelar", bg="#888", fg="white",
                  font=FUENTE, relief="flat", padx=12, pady=5,
                  command=self.destroy).pack(side="left")
        self.bind("<Return>", lambda _: self._ok())
        self.bind("<Escape>", lambda _: self.destroy())
        self.update_idletasks()
        self.geometry(
            f"+{parent.winfo_x()+(parent.winfo_width()-self.winfo_width())//2}"
            f"+{parent.winfo_y()+(parent.winfo_height()-self.winfo_height())//2}")

    def _ok(self):
        txt = self.var.get().replace(",", ".").strip()
        try:
            self.resultado = float(txt) if txt else 0.0
            self.destroy()
        except ValueError:
            messagebox.showwarning("Valor invalido", "Ingresa un numero.", parent=self)


# ── Diálogo guardar archivo de precios ────────────────────────────────────
class _DlgGuardarPrecios(tk.Toplevel):
    def __init__(self, parent, nombre_actual, ruta_actual, carpeta_precios):
        super().__init__(parent)
        self.title("Guardar precios")
        self.geometry("460x220")
        self.resizable(False, False)
        self.grab_set()
        self.ruta_destino = None
        self._carpeta = carpeta_precios
        hdr = tk.Frame(self, bg=COLOR_HDR, height=42)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="  Guardar archivo de precios",
                 bg=COLOR_HDR, fg="white", font=FUENTE_B).pack(side="left", padx=12)
        frm = tk.Frame(self, pady=16, padx=20)
        frm.pack(fill="both", expand=True)
        if ruta_actual and Path(ruta_actual).exists():
            tk.Button(frm,
                      text=f"Actualizar  {nombre_actual}",
                      bg=COLOR_VERDE, fg="white", font=FUENTE_B,
                      relief="flat", padx=12, pady=8, cursor="hand2", anchor="w",
                      command=lambda: self._elegir(Path(ruta_actual))
                      ).pack(fill="x", pady=(0, 8))
        tk.Button(frm, text="Guardar como nuevo archivo...",
                  bg=COLOR_SEC, fg="white", font=FUENTE_B,
                  relief="flat", padx=12, pady=8, cursor="hand2",
                  command=self._guardar_como).pack(fill="x", pady=(0, 8))
        tk.Button(frm, text="Cancelar  (no guardar precios)",
                  bg="#888", fg="white", font=FUENTE,
                  relief="flat", padx=12, pady=6, cursor="hand2",
                  command=self.destroy).pack(fill="x")
        self.update_idletasks()
        self.geometry(
            f"+{parent.winfo_x()+(parent.winfo_width()-self.winfo_width())//2}"
            f"+{parent.winfo_y()+(parent.winfo_height()-self.winfo_height())//2}")

    def _elegir(self, ruta):
        self.ruta_destino = ruta
        self.destroy()

    def _guardar_como(self):
        from tkinter import filedialog
        import datetime
        mes = datetime.date.today().strftime("%m_%Y")
        ruta = filedialog.asksaveasfilename(
            parent=self,
            title="Guardar archivo de precios como...",
            initialdir=str(self._carpeta) if self._carpeta.exists()
                       else str(self._carpeta.parent),
            initialfile=f"PUnitarios_{mes}.xlsx",
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx"), ("Todos", "*.*")],
        )
        if ruta:
            self.ruta_destino = Path(ruta)
            self.destroy()
