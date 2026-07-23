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
        self._precios = dict(getattr(obra, "precios", {}) or {})
        raw_pt = getattr(obra, "precios_tarea", {}) or {}
        self._precios_tarea = {int(k): v for k, v in raw_pt.items()}
        self._nombre_precios = getattr(obra, "archivo_precios", "") or ""
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
        # ── Barra de tabs personalizada ──────────────────────────────
        self._build_custom_tabbar()
        # Frame contenedor de tabs (reemplaza ttk.Notebook — sin barra nativa)
        self._nb_cont = tk.Frame(self, bg=COLOR_BG)
        self._nb_cont.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.tab_rubros  = tk.Frame(self._nb_cont, bg=COLOR_BG)
        self.tab_tareas  = tk.Frame(self._nb_cont, bg=COLOR_BG)
        self.tab_ins     = tk.Frame(self._nb_cont, bg=COLOR_BG)
        self.tab_ppto    = tk.Frame(self._nb_cont, bg=COLOR_BG)
        self.tab_rpt_ins = tk.Frame(self._nb_cont, bg=COLOR_BG)
        self.tab_rpt_mat = tk.Frame(self._nb_cont, bg=COLOR_BG)
        self.tab_rpt_mdo = tk.Frame(self._nb_cont, bg=COLOR_BG)
        self.tab_rpt_det = tk.Frame(self._nb_cont, bg=COLOR_BG)
        self._tab_frames = [
            self.tab_rubros, self.tab_tareas, self.tab_ins, self.tab_ppto,
            self.tab_rpt_ins, self.tab_rpt_mat, self.tab_rpt_mdo, self.tab_rpt_det,
        ]
        # Mostrar tab inicial (Rubros)
        self.tab_rubros.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._build_rubros()
        self._build_tareas()
        self._build_ins()
        self._build_presupuesto()
        self._build_rpt_insumos()
        self._build_rpt_materiales()
        self._build_rpt_mdo()
        self._build_rpt_detalle()
        bar = tk.Frame(self, bg="#e0e0e0", pady=6)
        bar.pack(fill="x")
        tk.Button(bar, text="Guardar obra", bg=COLOR_VERDE, fg="white",
                  font=FUENTE_B, relief="flat", padx=14, pady=5,
                  cursor="hand2", command=self._guardar
                  ).pack(side="right", padx=12)
        self.lbl_st = tk.Label(bar, text="", bg="#e0e0e0",
                               fg="#444", font=FUENTE_S, anchor="w")
        self.lbl_st.pack(side="left", padx=12)
    def _build_rubros(self):
        f = self.tab_rubros
        hdr = tk.Frame(f, bg=COLOR_HDR, height=36)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="Seleccioná los Rubros a presupuestar",
                 bg=COLOR_HDR, fg="white", font=FUENTE_B).place(relx=0.5, rely=0.5, anchor="center")
        outer = tk.Frame(f, bg=COLOR_BG)
        outer.pack(fill="both", expand=True, padx=16, pady=10)
        # Panel izquierdo: dos columnas de rubros
        frm_rubros = tk.Frame(outer, bg=COLOR_BG)
        frm_rubros.grid(row=0, column=0, sticky="nsew")
        ttk.Separator(outer, orient="vertical").grid(row=0, column=1, sticky="ns", padx=10)
        # Panel derecho: referencia de modalidades de subcontrato
        frm_modal = tk.Frame(outer, bg=COLOR_BG)
        frm_modal.grid(row=0, column=2, sticky="nsew", padx=(0, 4))
        outer.grid_columnconfigure(0, weight=3)
        outer.grid_columnconfigure(2, weight=1)
        # --- Rubros ---
        rubros = self.maestro["rubros"]
        mitad  = (len(rubros) + 1) // 2
        self.vars_rubros = {}
        def _hacer_columna(parent, rubros_lista, offset):
            tk.Label(parent, text="#",      bg=COLOR_BG, font=FUENTE_B, fg=COLOR_HDR,
                     width=4, anchor="e").grid(row=0, column=0, padx=(8,4),  pady=(8,2))
            tk.Label(parent, text="Rubro",  bg=COLOR_BG, font=FUENTE_B, fg=COLOR_HDR,
                     anchor="w").grid(row=0, column=1, sticky="w", padx=(0,8), pady=(8,2))
            tk.Label(parent, text="Tareas", bg=COLOR_BG, font=FUENTE_B, fg=COLOR_HDR,
                     width=6, anchor="e").grid(row=0, column=2, padx=(0,8), pady=(8,2))
            ttk.Separator(parent, orient="horizontal").grid(
                row=1, column=0, columnspan=3, sticky="ew", padx=4, pady=(0,4))
            for j, rubro in enumerate(rubros_lista):
                fila = j + 2
                v = tk.BooleanVar(value=self._rubro_activo(rubro))
                self.vars_rubros[rubro] = v
                n_tar = len(self.maestro["tareas"].get(rubro, []))
                tk.Label(parent, text=f"{offset+j+1:02d}", bg=COLOR_BG, font=FUENTE,
                         fg="#666", width=4, anchor="e").grid(
                    row=fila, column=0, padx=(8,4), pady=2)
                tk.Checkbutton(parent, text=rubro, variable=v,
                               bg=COLOR_BG, font=FUENTE, activebackground=COLOR_BG,
                               command=lambda r=rubro: self._on_rubro(r)
                               ).grid(row=fila, column=1, sticky="w", padx=(0,8), pady=2)
                tk.Label(parent, text=str(n_tar), bg=COLOR_BG, font=FUENTE,
                         fg="#888", width=6, anchor="e").grid(
                    row=fila, column=2, padx=(0,8), pady=2)
        col_izq = tk.Frame(frm_rubros, bg=COLOR_BG)
        col_der = tk.Frame(frm_rubros, bg=COLOR_BG)
        sep_v2  = ttk.Separator(frm_rubros, orient="vertical")
        col_izq.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        sep_v2 .grid(row=0, column=1, sticky="ns",   padx=4)
        col_der.grid(row=0, column=2, sticky="nsew", padx=(8, 0))
        frm_rubros.grid_columnconfigure(0, weight=1)
        frm_rubros.grid_columnconfigure(2, weight=1)
        _hacer_columna(col_izq, rubros[:mitad],  0)
        _hacer_columna(col_der, rubros[mitad:], mitad)
        # --- Modalidades de Subcontrato ---
        tk.Label(frm_modal, text="Modalidades de Subcontrato",
                 bg=COLOR_BG, font=FUENTE_B, fg=COLOR_HDR,
                 anchor="w").pack(anchor="w", pady=(8, 4))
        ttk.Separator(frm_modal, orient="horizontal").pack(fill="x", pady=(0, 8))
        def _bloque(titulo, items):
            tk.Label(frm_modal, text=titulo, bg=COLOR_BG,
                     font=("Segoe UI", 9, "bold"), fg=COLOR_SEC,
                     anchor="w").pack(anchor="w", pady=(6, 2))
            for letra, desc in items:
                fila = tk.Frame(frm_modal, bg=COLOR_BG)
                fila.pack(anchor="w", padx=4, pady=1)
                tk.Label(fila, text=f"  {letra if letra else ' '}  ",
                         bg="#e8f0f8", font=("Segoe UI", 9, "bold"),
                         fg=COLOR_HDR, width=3, relief="flat").pack(side="left")
                tk.Label(fila, text=desc, bg=COLOR_BG,
                         font=FUENTE_S, fg="#333",
                         anchor="w").pack(side="left", padx=6)
        _bloque("Rubro 3 — Estructuras Resistentes:", [
            ("",  "MdeO propia"),
            ("S", "MdeO c/elabor. manual (Madera, clavos y alambre)"),
            ("E", "MdeO sin elabor. manual (Madera, clavos y alambre)"),
            ("X", "MdeO sin elaboración manual"),
            ("T", "MdeO y Materiales"),
        ])
        _bloque("Todos los demás Rubros:", [
            ("",  "Mano de Obra propia"),
            ("S", "Subcontrato — Mano de Obra"),
            ("T", "Subcontrato TOTAL"),
        ])
    def _rubro_activo(self, rubro):
        return any(
            it.get("rubro_std") == rubro
            for it in getattr(self.obra, "items_presupuesto", [])
            if not it.get("es_rubro") and it.get("cod_tar")
        )
    def _on_rubro(self, rubro):
        self._actualizar_st()
    def _build_tareas(self):
        f = self.tab_tareas
        if not hasattr(self.obra, "items_presupuesto"):
            self.obra.items_presupuesto = []
        self._item_sel_idx = None
        frm_btn = tk.Frame(f, bg=COLOR_BG)
        frm_btn.pack(side="bottom", fill="x", padx=12, pady=6)
        self.lbl_sin_vinculo = tk.Label(frm_btn,
            text="", bg=COLOR_BG, fg=COLOR_ROJO, font=FUENTE_S)
        self.lbl_sin_vinculo.pack(side="left", padx=4)
        paned = tk.PanedWindow(f, orient="horizontal", bg="#cccccc",
                               sashwidth=5, sashrelief="flat")
        paned.pack(fill="both", expand=True, padx=6, pady=(6, 0))
        izq = tk.Frame(paned, bg=COLOR_BG)
        paned.add(izq, minsize=380)
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
        der = tk.Frame(paned, bg=COLOR_BG)
        paned.add(der, minsize=340)
        frm_der_top = tk.Frame(der, bg=COLOR_HDR, height=32)
        frm_der_top.pack(fill="x")
        frm_der_top.pack_propagate(False)
        tk.Label(frm_der_top, text="  Tareas Standard",
                 bg=COLOR_HDR, fg="white", font=FUENTE_B).pack(side="left", padx=8)
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
        self._SUBC_DESC_R3 = {
            "":  "   MdeO propia",
            "S": "S  MdeO (c/elabor. manual, Madera, clavos y alambre)",
            "E": "E  MdeO (sin elabor. manual, Madera, clavos y alambre)",
            "X": "X  MdeO (sin elabor. manual)",
            "T": "T  MdeO y Materiales",
        }
        self._subc_opts = {}  # desc → letra, rebuilt per combo open
        self._subc_var = tk.StringVar()
        self._subc_combo = ttk.Combobox(der, textvariable=self._subc_var,
                                        font=FUENTE, width=46, state="readonly")
        self._subc_combo.bind("<<ComboboxSelected>>", self._confirmar_subc)
        self._subc_combo.bind("<Escape>",  lambda e: self._subc_combo.place_forget())
        self._subc_iid   = None
        self._subc_cache = {}   # cod_tar → letra confirmada
        if getattr(self.obra, "items_presupuesto", []):
            self._poblar_iz()
    def _auto_variante(self, cod: str) -> str:
        """Detecta la variante de subcontrato por defecto para una tarea.
        Rubro 3: prefiere X (sin elaboracion manual). Demas rubros: prefiere S."""
        tareas_por_cod     = self.maestro.get("tareas_por_cod", {})
        incidencias_master = self.maestro.get("incidencias", {})
        if (cod + "X") in tareas_por_cod or (cod + "X") in incidencias_master:
            return "X"
        if (cod + "S") in tareas_por_cod or (cod + "S") in incidencias_master:
            return "S"
        return ""

    def _clic_der_subc(self, event=None):
        region = self.tbl_der.identify_region(event.x, event.y)
        col    = self.tbl_der.identify_column(event.x)
        iid    = self.tbl_der.identify_row(event.y)
        if region != "cell" or not iid or iid.startswith("__rub_"):
            return
        # Clic en columna nombre/unidad con item del pliego seleccionado -> asignar directo
        if col != "#1":
            if hasattr(self, "_subc_combo"):
                self._subc_combo.place_forget()
            if self._item_sel_idx is not None:
                self._asignar_tarea_der(iid)
            return
        bbox = self.tbl_der.bbox(iid, col)
        if not bbox:
            return
        x, y, w, h = bbox
        tareas_por_cod     = self.maestro.get("tareas_por_cod", {})
        incidencias_master = self.maestro.get("incidencias", {})
        t      = tareas_por_cod.get(iid, {})
        nombre = t.get("nombre", iid)
        # Rubro 3 (Estructuras Resistentes) tiene variantes E y X; los demás no
        es_r3 = any(
            (iid + l) in tareas_por_cod or (iid + l) in incidencias_master
            for l in ("E", "X")
        )
        if es_r3:
            desc_map          = self._SUBC_DESC_R3
            letras_a_chequear = ("S", "E", "X", "T")
        else:
            desc_map = {
                "":  "   Mano de Obra propia",
                "S": f"S  M. de Obra para {nombre}",
                "T": "T  Subcontrato TOTAL",
            }
            letras_a_chequear = ("S", "T")
        letras_opciones = [""]
        for letra in letras_a_chequear:
            if (iid + letra) in tareas_por_cod or (iid + letra) in incidencias_master:
                letras_opciones.append(letra)
        opciones = [desc_map[l] for l in letras_opciones]
        self._subc_opts = {desc_map[l]: l for l in letras_opciones}
        self._subc_combo["values"] = opciones
        vals = self.tbl_der.item(iid, "values")
        letra_actual = (vals[0] if vals else "").strip().upper()
        desc_actual  = desc_map.get(letra_actual, desc_map[""])
        self._subc_var.set(desc_actual)
        self._subc_iid = iid
        combo_w = max(w, 340)
        # Cerrar el dropdown anterior antes de reposicionar
        self._subc_combo.place_forget()
        self._subc_combo.update_idletasks()
        self._subc_combo.place(x=self.tbl_der.winfo_x() + x,
                               y=self.tbl_der.winfo_y() + y,
                               width=combo_w, height=h)
        self._subc_combo.focus_set()
        self._subc_combo.after(50, lambda: self._subc_combo.event_generate("<Button-1>"))
    def _asignar_tarea_der(self, cod: str):
        """Vincula la tarea cod a la fila del pliego seleccionada, con variante automatica."""
        items = getattr(self.obra, "items_presupuesto", [])
        if self._item_sel_idx is None or self._item_sel_idx >= len(items):
            return
        it = items[self._item_sel_idx]
        t  = self.maestro["tareas_por_cod"].get(cod)
        if not t:
            return
        if it.get("cod_tar") and it["cod_tar"] != cod:
            desc_actual = self.maestro["tareas_por_cod"].get(it["cod_tar"], {}).get("nombre", "?")
            ok = messagebox.askyesno(
                "Cambiar vinculo",
                f"Esta fila ya esta vinculada a:\n{it['cod_tar']} - {desc_actual}\n\n"
                f"Cambiala por:\n{cod} - {t['nombre']}?",
                parent=self)
            if not ok:
                return
        subcont = self._auto_variante(cod)
        it["cod_tar"]     = cod
        it["unidad"]      = it.get("unidad") or t["unidad"]
        it["rubro_std"]   = t["rubro"]
        it["subcontrato"] = subcont
        if not hasattr(self, "_subc_cache"):
            self._subc_cache = {}
        self._subc_cache[cod] = subcont
        vals = list(self.tbl_der.item(cod, "values"))
        if vals:
            vals[0] = subcont
            self.tbl_der.item(cod, values=vals)
        self._refrescar_der_sel(cod)
        self._poblar_iz()
        self.tbl_iz.item(str(self._item_sel_idx), tags=("sel",))
        self.tbl_iz.see(str(self._item_sel_idx))
        self._actualizar_st()

    def _confirmar_subc(self, event=None):
        if not self._subc_iid:
            return
        desc = self._subc_var.get()
        val  = self._subc_opts.get(desc, "")
        iid  = self._subc_iid
        vals = list(self.tbl_der.item(iid, "values"))
        vals[0] = val
        self.tbl_der.item(iid, values=vals)
        items = getattr(self.obra, "items_presupuesto", [])
        for it in items:
            if it.get("cod_tar") == iid:
                it["subcontrato"] = val
        if not hasattr(self, "_subc_cache"):
            self._subc_cache = {}
        self._subc_cache[iid] = val
        if not hasattr(self, "_subc_cache"): self._subc_cache = {}
        self._subc_cache[iid] = val
        self._subc_combo.place_forget()
        self._subc_iid = None
    def _cargar_tareas(self):
        if not hasattr(self, "tbl_iz") or not hasattr(self, "tbl_der"):
            return
        self._subc_cache = {}
        self._subc_cache = {}
        self._poblar_iz()
        for item in self.tbl_der.get_children():
            self.tbl_der.delete(item)
        texto = self.var_bus.get().lower().strip()
        rubros_activos = {r for r, v in self.vars_rubros.items() if v.get()}
        if not rubros_activos:
            self.tbl_der.insert("", "end",
                values=("", "← Seleccioná rubros en la pestaña 1.", ""))
            return
        i = 0
        tareas_por_cod = self.maestro["tareas_por_cod"]
        for rubro in self.maestro["rubros"]:
            if rubro not in rubros_activos:
                continue
            # FIX: mostrar tareas base (sin sufijo) O tareas con sufijo que no tienen versión base
            tareas_rubro = [
                t for t in self.maestro["tareas"][rubro]
                if (t["variante"] == " " or t["base"] not in tareas_por_cod)
                and (not texto or texto in t["nombre"].lower())
            ]
            if not tareas_rubro:
                continue
            self.tbl_der.insert("", "end", iid=f"__rub_{rubro}",
                                tags=("rub_hdr",), values=("", rubro, ""))
            for t in sorted(tareas_rubro, key=lambda x: x["cod"]):
                tag = "par" if i % 2 == 0 else "impar"
                self.tbl_der.insert("", "end", iid=t["cod"], tags=(tag,),
                                    values=("", t["nombre"], t["unidad"]))
                i += 1
        self._actualizar_st()
    def _poblar_iz(self):
        for item in self.tbl_iz.get_children():
            self.tbl_iz.delete(item)
        items = getattr(self.obra, "items_presupuesto", [])
        sin_vnc = 0
        item_counter = 0
        cur_rubro_idx = None
        rubro_counts  = {}
        for idx, it in enumerate(items):
            es_rubro = it.get("es_rubro", False)
            if es_rubro:
                cur_rubro_idx = idx
                rubro_counts[cur_rubro_idx] = 0
                self.tbl_iz.insert("", "end", iid=str(idx), tags=("rubro_hdr",),
                    values=(it.get("rubro", ""), "",
                            it.get("descripcion", ""), "", ""))
                continue
            else:
                rubro_counts[cur_rubro_idx] = rubro_counts.get(cur_rubro_idx, 0) + 1
                display_item = f"{rubro_counts[cur_rubro_idx]:02d}"
                rub = it.get("rubro", "")
                vinculado = bool(it.get("cod_tar"))
                tag = "vinculada" if vinculado else "sin_vnc"
                if not vinculado:
                    sin_vnc += 1
                cant = it.get("cantidad", "")
                cant_str = self._fmt_q(cant, 2) if isinstance(cant, (int, float)) else str(cant)
                self.tbl_iz.insert("", "end", iid=str(idx), tags=(tag,),
                    values=(rub, display_item,
                            it.get("descripcion", ""),
                            it.get("unidad", ""), cant_str))
        msg = f"⚠  {sin_vnc} tarea{'s' if sin_vnc!=1 else ''} sin equivalente." if sin_vnc else ""
        self.lbl_sin_vinculo.config(text=msg)
    def _clic_fila_iz(self, event=None):
        if hasattr(self, "_subc_combo"):
            self._subc_combo.place_forget()
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
        self.tbl_iz.see(str(idx))
        rubro_it = it.get("rubro_std", "")
        if rubro_it:
            hdr_id = f"__rub_{rubro_it}"
            if self.tbl_der.exists(hdr_id):
                self.tbl_der.see(hdr_id)
    def _doble_clic_iz(self, event=None):
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
        sel_der = self.tbl_der.selection()
        if not sel_der:
            return
        cod = sel_der[0]
        if cod.startswith("__rub_"):
            return
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
        if it.get("cod_tar") and it["cod_tar"] != cod:
            ok = messagebox.askyesno(
                "Cambiar vínculo",
                f"Esta fila ya está vinculada a:\n{it['cod_tar']} — {self.maestro['tareas_por_cod'].get(it['cod_tar'],{}).get('nombre','?')}\n\n"
                f"¿La cambiás por:\n{cod} — {t['nombre']}?",
                parent=self)
            if not ok:
                return
        cache         = getattr(self, "_subc_cache", {})
        subcont_cache = cache.get(cod, "").strip().upper()
        vals_der      = self.tbl_der.item(cod, "values")
        subcont_tbl   = (vals_der[0] if vals_der else "").strip().upper()
        subcont = subcont_cache or subcont_tbl or it.get("subcontrato", "")
        if not subcont:
            subcont = self._auto_variante(cod)
        it["cod_tar"]     = cod
        it["unidad"]      = it.get("unidad") or t["unidad"]
        it["rubro_std"]   = t["rubro"]
        it["subcontrato"] = subcont
        self._refrescar_der_sel(cod)
        self._poblar_iz()
        self.tbl_iz.item(str(self._item_sel_idx), tags=("sel",))
        self.tbl_iz.see(str(self._item_sel_idx))
        self._actualizar_st()
    def _refrescar_der_sel(self, cod):
        for iid in self.tbl_der.get_children():
            if iid.startswith("__rub_"):
                continue
            tags = list(self.tbl_der.item(iid, "tags"))
            tags = [t for t in tags if t not in ("sel","par","impar")]
            i = self.tbl_der.index(iid)
            tags.append("sel" if iid == cod else ("par" if i % 2 == 0 else "impar"))
            self.tbl_der.item(iid, tags=tags)
    def _agregar_fila(self):
        items = getattr(self.obra, "items_presupuesto", [])
        ultimos = [it for it in items if not it.get("es_rubro")]
        if ultimos:
            ul = ultimos[-1]
            rubro = ul.get("rubro", "01")
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
        new_idx = len(items) - 1
        self._item_sel_idx = new_idx
        self.tbl_iz.selection_set(str(new_idx))
        self.tbl_iz.see(str(new_idx))
        self._editar_fila_item(new_idx, items[new_idx])
    def _importar_presupuesto(self):
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
        cod_tar = it.get("cod_tar", "")
        if cod_tar:
            t = self.maestro["tareas_por_cod"].get(cod_tar, {})
            subcont = (it.get("subcontrato") or "").strip().upper()
            cod_label = f"{cod_tar}{subcont}" if subcont else cod_tar
            nombre_tar = t.get("nombre", "")
            cod_tar_label = f"{cod_label}  —  {nombre_tar}" if nombre_tar else cod_label
        else:
            cod_tar_label = None
        dlg = _DlgEditarFila(self, it, cod_tar_label=cod_tar_label)
        self.wait_window(dlg)
        if dlg.resultado:
            it.update(dlg.resultado)
            self._poblar_iz()
            self.tbl_iz.item(str(idx), tags=("sel",))
            self.tbl_iz.see(str(idx))
    def _editar_fila_rubro(self, idx, it):
        dlg = _DlgEditarFila(self, it, es_rubro=True)
        self.wait_window(dlg)
        if dlg.resultado:
            it.update(dlg.resultado)
            self._poblar_iz()
    def _menu_der_iz(self, event):
        iid = self.tbl_iz.identify_row(event.y)
        if not iid:
            return
        idx = int(iid)
        items = getattr(self.obra, "items_presupuesto", [])
        if idx >= len(items):
            return
        it = items[idx]
        sel_actual = self.tbl_iz.selection()
        if str(idx) not in sel_actual:
            self.tbl_iz.selection_set(str(idx))
        n_sel = len(self.tbl_iz.selection())
        lbl_elim = f"🗑  Eliminar {n_sel} filas" if n_sel > 1 else "🗑  Eliminar fila"
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="✏  Editar",
                         command=lambda: self._doble_clic_iz())
        menu.add_separator()
        menu.add_command(label="⬆  Insertar fila arriba",
                         command=lambda: self._insertar_fila(idx, arriba=True))
        menu.add_command(label="⬇  Insertar fila abajo",
                         command=lambda: self._insertar_fila(idx, arriba=False))
        menu.add_separator()
        menu.add_command(label=lbl_elim,
                         command=lambda: self._eliminar_fila_iz())
        menu.tk_popup(event.x_root, event.y_root)
    def _insertar_fila(self, idx: int, arriba: bool):
        items = getattr(self.obra, "items_presupuesto", [])
        it_ref = items[idx]
        rubro = it_ref.get("rubro", "01")
        nueva_fila = {
            "es_rubro":    False,
            "rubro":       rubro,
            "item":        "00",
            "descripcion": "",
            "unidad":      "",
            "cantidad":    0.0,
            "cod_tar":     "",
            "subcontrato": "",
            "rubro_std":   "",
        }
        pos = idx if arriba else idx + 1
        items.insert(pos, nueva_fila)
        self._renumerar_items(items)
        self.obra.items_presupuesto = items
        self._poblar_iz()
        self._item_sel_idx = pos
        self.tbl_iz.selection_set(str(pos))
        self.tbl_iz.see(str(pos))
        self._editar_fila_item(pos, items[pos])
        self._actualizar_st()
    def _renumerar_items(self, items: list):
        contadores = {}
        for it in items:
            if it.get("es_rubro"):
                continue
            rubro = it.get("rubro", "")
            contadores[rubro] = contadores.get(rubro, 0) + 1
            it["item"] = f"{contadores[rubro]:02d}"
    def _eliminar_fila_iz(self, idx=None):
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
        iid = self.tbl_der.identify_row(event.y)
        if not iid or iid.startswith("__rub_"):
            return
        self.tbl_der.selection_set(iid)
        t = self.maestro["tareas_por_cod"].get(iid)
        if not t:
            return
        vals = self.tbl_der.item(iid, "values")
        subcont = vals[0].strip().upper() if vals else ""
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(
            label="📋  Ver insumos de esta tarea",
            command=lambda: self._ver_insumos_tarea(iid, subcont))
        menu.tk_popup(event.x_root, event.y_root)
    def _ver_insumos_tarea(self, cod_tar: str, subcont: str):
        incidencias = self.maestro["incidencias"]
        insumos_cat = self.maestro["insumos"]
        cod_buscar = cod_tar + subcont if subcont else cod_tar
        lista = incidencias.get(cod_buscar) or incidencias.get(cod_tar, [])
        t = self.maestro["tareas_por_cod"].get(cod_tar, {})
        titulo = t.get("nombre", cod_tar)
        if subcont:
            titulo += f"  [{subcont}]"
        dlg = _DlgInsumosTarea(self, titulo, lista, insumos_cat)
        dlg.grab_set()
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
        self.var_arch_prc = tk.StringVar(value=self._nombre_precios or "Sin archivo seleccionado")
        tk.Label(frm_prc, textvariable=self.var_arch_prc,
                 bg=COLOR_BG, font=FUENTE_S, fg=COLOR_HDR).pack(side="left", padx=6)
        tk.Button(frm_prc, text="Seleccionar archivo...",
                  bg=COLOR_SEC, fg="white", font=FUENTE_S,
                  relief="flat", padx=8, pady=3, cursor="hand2",
                  command=self._elegir_precios).pack(side="left", padx=(8, 0))
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
            unidad = datos["unidad"] or cat.get(cod_ins, {}).get("unidad", "")
            cant   = datos["cantidad_total"]
            precio = self._precios.get(cod_ins)
            if precio and precio > 0:
                sub   = cant * precio
                total += sub
                tag   = "ok"
                p_str = f"$ {self._fmt_pu(precio)}"
                s_str = f"$ {self._fmt_pt(sub)}"
                est   = "Con precio"
            else:
                falt += 1
                tag   = "faltante"
                p_str = "-"
                s_str = "-"
                est   = "Sin precio"
            self.tbl_ins.insert("", "end", iid=cod_ins, tags=(tag,),
                                values=(cod_ins, nombre, unidad,
                                        self._fmt_q(cant, 2), p_str, s_str, est))
        n_total = len(insumos)
        pct = int(100 * (n_total - falt) / n_total) if n_total else 0
        self.lbl_total.config(
            text=f"Total cotizado: $ {self._fmt_pt(total)}   |   "
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
    def _build_presupuesto(self):
        f = self.tab_ppto
        frm_top = tk.Frame(f, bg=COLOR_BG)
        frm_top.pack(side="top", fill="x", padx=12, pady=(8, 2))
        tk.Label(frm_top, text="Presupuesto valorizado",
                 bg=COLOR_BG, font=FUENTE_B, fg=COLOR_HDR).pack(side="left")
        tk.Button(frm_top, text="📄 Exportar Excel", bg=COLOR_VERDE, fg="white",
                  font=FUENTE_S, relief="flat", padx=8, pady=3, cursor="hand2",
                  command=self._exportar_presupuesto).pack(side="right")
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
        self.tbl_ppto.tag_configure("rub_hdr",
            background="#1a3a5c", foreground="white",
            font=("Segoe UI", 10, "bold"))
        self.tbl_ppto.tag_configure("tarea_ok",        background="#ffffff")
        self.tbl_ppto.tag_configure("tarea_sinprecio", background="#fff3cd")
        self.tbl_ppto.tag_configure("tarea_alt",       background="#f5f5f5")
        self.tbl_ppto.tag_configure("insumo",
            background="#eef4fb", foreground="#1a3a5c", font=("Segoe UI", 9))
        self.tbl_ppto.tag_configure("insumo_alt",
            background="#e4ecf7", foreground="#1a3a5c", font=("Segoe UI", 9))
        self.tbl_ppto.tag_configure("total_general",
            background="#1a3a5c", foreground="white",
            font=("Segoe UI", 10, "bold"))
        self.tbl_ppto.bind("<ButtonRelease-1>", self._toggle_ppto)
        self.tbl_ppto.bind("<Double-1>", self._editar_precio_tarea)
        self.lbl_total_ppto = tk.Label(f, text="", bg="#e8f0f8",
                                       font=FUENTE_B, anchor="e",
                                       fg=COLOR_HDR, pady=5, padx=12)
        self.lbl_total_ppto.pack(side="bottom", fill="x", padx=8, pady=(0, 4))
        self._ppto_expandido = set()
    def _cargar_presupuesto(self):
        if not hasattr(self, "tbl_ppto"):
            return
        for item in self.tbl_ppto.get_children():
            self.tbl_ppto.delete(item)
        items       = getattr(self.obra, "items_presupuesto", [])
        incidencias = self.maestro["incidencias"]
        insumos_cat = self.maestro["insumos"]
        precios     = self._precios
        totales_rubro = {}
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
            cod_buscar  = cod_tar + subcont if (cod_tar and subcont) else cod_tar
            lista_inc   = incidencias.get(cod_buscar, []) if subcont else incidencias.get(cod_tar, [])
            precio_unit = (self._precios_tarea.get(idx) or
                           sum((precios.get(inc["cod_ins"], 0.0) or 0.0) * inc["cantidad"]
                               for inc in lista_inc))
            totales_rubro[rubro_idx_actual] += precio_unit * cant
        total_general = 0.0
        i_tarea = 0
        for idx, it in enumerate(items):
            if it.get("es_rubro"):
                rub  = it.get("rubro", "")
                desc = it.get("descripcion", "")
                sub  = totales_rubro.get(idx, 0.0)
                sub_str = f"$ {self._fmt_pt(sub)}" if sub else ""
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
            lista_inc  = incidencias.get(cod_buscar, []) if subcont else incidencias.get(cod_tar, [])
            precio_unit      = 0.0
            todos_con_precio = True
            insumos_detalle  = []
            precio_manual    = self._precios_tarea.get(idx)
            if precio_manual:
                precio_unit      = precio_manual
                todos_con_precio = True
            else:
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
            p_str = f"$ {self._fmt_pu(precio_unit)}" if precio_unit else "-"
            t_str = f"$ {self._fmt_pt(total_tarea)}"  if precio_unit else "-"
            c_str = self._fmt_q(cant, 2) if cant else "-"
            self.tbl_ppto.insert("", "end", iid=iid_tarea, tags=(tag,),
                values=(rub, item_num, prefijo + desc,
                        unidad, c_str, p_str, t_str))
            if expandido:
                for j, ins in enumerate(insumos_detalle):
                    tag_ins = "insumo" if j % 2 == 0 else "insumo_alt"
                    p_i = f"$ {self._fmt_pu(ins['precio'])}" if ins['precio'] else "Sin precio"
                    s_i = f"$ {self._fmt_pt(ins['subtotal'])}" if ins['precio'] else "-"
                    self.tbl_ppto.insert("", "end",
                        iid=f"ins_{idx}_{j}", tags=(tag_ins,),
                        values=("", "", f"    {ins['nombre']}",
                                ins["unidad"], f"{ins['incidencia']:g}", p_i, s_i))
            i_tarea += 1
        if total_general > 0:
            self.tbl_ppto.insert("", "end", iid="total_gen",
                tags=("total_general",),
                values=("", "", "TOTAL GENERAL", "", "", "",
                        f"$ {self._fmt_pt(total_general)}"))
        self.lbl_total_ppto.config(
            text=f"Total general:  $ {self._fmt_pt(total_general)}   "
                 f"({'sin precios completos' if not precios else 'basado en precios cargados'})")
    def _toggle_ppto(self, event=None):
        iid = self.tbl_ppto.identify_row(event.y)
        if not iid or not iid.startswith("tar_"):
            return
        col = self.tbl_ppto.identify_column(event.x)
        if col != "#3":
            return
        if iid in self._ppto_expandido:
            self._ppto_expandido.discard(iid)
        else:
            self._ppto_expandido.add(iid)
        self._cargar_presupuesto()
    def _exportar_presupuesto(self):
        from tkinter import filedialog
        import openpyxl
        from openpyxl.styles import (Font, PatternFill, Alignment,
                                     Border, Side, numbers)
        ruta = filedialog.asksaveasfilename(
            parent=self,
            title="Exportar Presupuesto",
            initialdir=str(self.obra.carpeta),
            initialfile=f"Presupuesto_{self.obra.numero}_{self.obra.nombre}.xlsx",
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx"), ("Todos", "*.*")],
        )
        if not ruta:
            return
        try:
            items       = getattr(self.obra, "items_presupuesto", [])
            incidencias = self.maestro["incidencias"]
            precios     = self._precios
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Presupuesto"
            # Estilos
            COLOR_H  = "1A3A5C"
            COLOR_S  = "2A6099"
            COLOR_IT = "FFFFFF"
            COLOR_A  = "F5F5F5"
            COLOR_T  = "1D7A4A"
            ft_hdr   = Font(name="Segoe UI", bold=True, color="FFFFFF", size=10)
            ft_rub   = Font(name="Segoe UI", bold=True, color="FFFFFF", size=10)
            ft_tar   = Font(name="Segoe UI", size=10)
            ft_tot   = Font(name="Segoe UI", bold=True, color="FFFFFF", size=10)
            fill_hdr = PatternFill("solid", fgColor=COLOR_H)
            fill_rub = PatternFill("solid", fgColor=COLOR_H)
            fill_sec = PatternFill("solid", fgColor=COLOR_S)
            fill_alt = PatternFill("solid", fgColor="EEF4FB")
            fill_tot = PatternFill("solid", fgColor=COLOR_T)
            al_c     = Alignment(horizontal="center", vertical="center")
            al_l     = Alignment(horizontal="left",   vertical="center", wrap_text=True)
            al_r     = Alignment(horizontal="right",  vertical="center")
            thin     = Side(style="thin", color="CCCCCC")
            brd      = Border(bottom=thin)
            fmt_num  = '#,##0.00'
            fmt_mon  = '"$"#,##0.00'
            # Cabecera
            headers = ["Rubro", "Ítem", "Descripción", "Unidad",
                       "Cantidad", "P. Unit.", "Total"]
            widths  = [8, 8, 55, 10, 12, 14, 14]
            cols    = ["A","B","C","D","E","F","G"]
            for i, (h, w, c) in enumerate(zip(headers, widths, cols), 1):
                cell = ws.cell(row=1, column=i, value=h)
                cell.font      = ft_hdr
                cell.fill      = fill_hdr
                cell.alignment = al_c
                ws.column_dimensions[c].width = w
            ws.row_dimensions[1].height = 22
            row = 2
            total_general = 0.0
            i_tar = 0
            for idx, it in enumerate(items):
                if it.get("es_rubro"):
                    desc = it.get("descripcion", "")
                    ws.merge_cells(f"A{row}:G{row}")
                    cell = ws.cell(row=row, column=1,
                                   value=f"  {it.get('rubro','')}  —  {desc}")
                    cell.font      = ft_rub
                    cell.fill      = fill_rub
                    cell.alignment = al_l
                    ws.row_dimensions[row].height = 18
                    row += 1
                    continue
                cod_tar  = it.get("cod_tar", "")
                subcont  = (it.get("subcontrato") or "").strip().upper()
                cant     = it.get("cantidad") or 0.0
                desc     = it.get("descripcion", "")
                unidad   = it.get("unidad", "")
                rub      = it.get("rubro", "")
                item_num = it.get("item", "")
                cod_buscar = cod_tar + subcont if (cod_tar and subcont) else cod_tar
                lista_inc  = (incidencias.get(cod_buscar, []) if subcont
                              else incidencias.get(cod_tar, []))
                precio_unit = (self._precios_tarea.get(idx) or
                               sum((precios.get(inc["cod_ins"], 0.0) or 0.0) * inc["cantidad"]
                                   for inc in lista_inc))
                total_tar = precio_unit * cant
                total_general += total_tar
                fill_row = PatternFill("solid", fgColor=(COLOR_IT if i_tar % 2 == 0 else "F5F5F5"))
                vals = [rub, item_num, desc, unidad,
                        cant if cant else None,
                        precio_unit if precio_unit else None,
                        total_tar if precio_unit else None]
                fmts = [None, None, None, None, fmt_num, fmt_mon, fmt_mon]
                alns = [al_c, al_c, al_l, al_c, al_r, al_r, al_r]
                for ci, (v, fmt, aln) in enumerate(zip(vals, fmts, alns), 1):
                    cell = ws.cell(row=row, column=ci, value=v)
                    cell.font      = ft_tar
                    cell.fill      = fill_row
                    cell.alignment = aln
                    cell.border    = brd
                    if fmt and v is not None:
                        cell.number_format = fmt
                ws.row_dimensions[row].height = 16
                row += 1
                i_tar += 1
            # Total general
            ws.merge_cells(f"A{row}:F{row}")
            cell = ws.cell(row=row, column=1, value="TOTAL GENERAL")
            cell.font      = ft_tot
            cell.fill      = fill_tot
            cell.alignment = al_r
            cell = ws.cell(row=row, column=7, value=total_general)
            cell.font          = ft_tot
            cell.fill          = fill_tot
            cell.alignment     = al_r
            cell.number_format = fmt_mon
            ws.row_dimensions[row].height = 20
            # Freeze header
            ws.freeze_panes = "A2"
            wb.save(ruta)
            messagebox.showinfo("Exportado",
                f"Presupuesto exportado:\n{Path(ruta).name}", parent=self)
        except Exception as e:
            messagebox.showerror("Error al exportar", str(e), parent=self)
    def _editar_precio_tarea(self, event=None):
        iid = self.tbl_ppto.identify_row(event.y)
        if not iid or not iid.startswith("tar_"):
            return
        col = self.tbl_ppto.identify_column(event.x)
        if col != "#6":   # columna P.Unit.
            return
        idx = int(iid.split("_")[1])
        items = getattr(self.obra, "items_presupuesto", [])
        if idx >= len(items):
            return
        it     = items[idx]
        desc   = it.get("descripcion", "") or it.get("cod_tar", "")
        unidad = it.get("unidad", "")
        actual = self._precios_tarea.get(idx, "")
        dlg = _DlgVal(self, f"Precio directo — ítem {it.get('item','')}", desc, unidad, actual, es_precio=True)
        self.wait_window(dlg)
        if dlg.resultado is None:
            return
        if dlg.resultado > 0:
            self._precios_tarea[idx] = dlg.resultado
        else:
            self._precios_tarea.pop(idx, None)
        self._cargar_presupuesto()
    def _on_tab_switch(self, idx: int):
        """Carga el contenido del tab activo."""
        if idx == 1:
            self._cargar_tareas()
        elif idx == 2:
            self._cargar_ins()
        elif idx == 3:
            self._cargar_presupuesto()
        elif idx == 4:
            self._cargar_rpt_insumos()
        elif idx == 5:
            self._cargar_rpt_materiales()
        elif idx == 6:
            self._cargar_rpt_mdo()
        elif idx == 7:
            self._cargar_rpt_detalle()
    def _actualizar_st(self):
        items = getattr(self.obra, "items_presupuesto", [])
        n_items = sum(1 for it in items if not it.get("es_rubro"))
        n_vnc   = sum(1 for it in items if not it.get("es_rubro") and it.get("cod_tar"))
        sin_vnc = n_items - n_vnc
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
            self.obra.precios          = dict(self._precios)
            self.obra.precios_tarea    = {str(k): v for k, v in self._precios_tarea.items()}
            self.obra.archivo_precios  = self._nombre_precios
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
            nueva_version = False
            nota = ""
            if not silencioso and self.obra.ruta_json.exists():
                dlg = _DlgGuardarVersion(self, self.obra.ruta_json.name)
                self.wait_window(dlg)
                if dlg.accion is None:
                    return
                nueva_version = dlg.accion == "nueva"
                nota = dlg.nota
            self.obra.guardar(nueva_version=nueva_version, nota=nota)
            if not silencioso:
                ver = f"obra{self.obra.version:03d}.json"
                self.lbl_st.config(text=f"  Guardado en {ver}.")
        except Exception as e:
            messagebox.showerror("Error al guardar", str(e), parent=self)


    # ═══════════════════════════════════════════════════════════════
    #  Exportar Detalle de Tareas (valores numéricos)
    # ═══════════════════════════════════════════════════════════════

    def _exportar_rpt_detalle(self):
        """Exporta Detalle de Tareas a Excel con valores numéricos."""
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment
        import os

        items_ppto  = getattr(self.obra, "items_presupuesto", [])
        incidencias = self.maestro["incidencias"]
        cat         = self.maestro["insumos"]

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Detalle de Tareas"

        headers = ["Rubro", "Item", "Descripcion", "Unidad",
                   "Cantidad", "P.Unitario", "P.Total"]
        ws.append(headers)
        for cell in ws[1]:
            cell.font      = Font(bold=True, color="FFFFFF")
            cell.fill      = PatternFill("solid", fgColor="1D5A2A")
            cell.alignment = Alignment(horizontal="center", vertical="center")

        COLOR_RUB  = "D4EDDA"
        COLOR_TOT  = "1D5A2A"
        COLOR_PAR  = "FFFFFF"
        COLOR_IMPAR = "F0F4FA"
        COLOR_INSA  = "EEF4FB"
        COLOR_INSB  = "E4ECF7"
        COLOR_SIN   = "FDE8E8"

        def _add(vals, bg, fg="000000", bold=False):
            ws.append(vals)
            ri = ws.max_row
            for cell in ws[ri]:
                cell.fill = PatternFill("solid", fgColor=bg)
                cell.font = Font(bold=bold, color=fg)
            # Alinear columnas numéricas a la derecha
            for ci in (5, 6, 7):
                ws.cell(ri, ci).alignment = Alignment(horizontal="right")

        i_tar      = 0
        rub_counts = {}
        cur_rub_idx = None
        suma_total  = 0.0

        for idx, it in enumerate(items_ppto):
            if it.get("es_rubro"):
                cur_rub_idx = idx
                rub_counts[cur_rub_idx] = 0
                _add([it.get("rubro", ""), "", it.get("descripcion", ""),
                      "", "", "", ""],
                     COLOR_RUB, bold=True)
                continue

            cod_tar = it.get("cod_tar", "")
            subcont = (it.get("subcontrato") or "").strip().upper()
            cant    = it.get("cantidad") or 0.0
            desc    = it.get("descripcion", "")
            unidad  = it.get("unidad", "")
            rub     = it.get("rubro", "")
            rub_counts[cur_rub_idx] = rub_counts.get(cur_rub_idx, 0) + 1
            item_num = f"{rub_counts[cur_rub_idx]:02d}"

            if not cod_tar:
                _add([rub, item_num, f"[sin vincular]  {desc}",
                      unidad, cant or None, None, None],
                     COLOR_SIN)
                continue

            cod_buscar = cod_tar + subcont if (cod_tar and subcont) else cod_tar
            lista_inc  = incidencias.get(cod_buscar) or incidencias.get(cod_tar, [])
            p_unit = self._precios_tarea.get(idx)
            if p_unit is None:
                p_unit = sum(
                    (self._precios.get(inc["cod_ins"], 0.0) or 0.0)
                    * inc.get("cantidad", 0.0)
                    for inc in lista_inc
                ) or None
            p_total = (p_unit * cant) if (p_unit is not None and cant) else None
            if p_total is not None:
                suma_total += p_total

            bg = COLOR_PAR if i_tar % 2 == 0 else COLOR_IMPAR
            cod_label = cod_tar + subcont if subcont else cod_tar
            _add([rub, item_num, f"{desc}  [{cod_label}]",
                  unidad, cant or None, p_unit, p_total], bg)

            # Insumos expandidos
            for j, inc in enumerate(lista_inc):
                cod_ins    = inc["cod_ins"]
                nombre_ins = cat.get(cod_ins, {}).get("nombre", cod_ins)
                unidad_ins = inc.get("unidad") or cat.get(cod_ins, {}).get("unidad", "")
                inc_cant   = inc.get("cantidad", 0)
                total_ins  = inc_cant * cant
                p_ins_u    = self._precios.get(cod_ins)
                p_ins_t    = (p_ins_u * total_ins) if p_ins_u is not None else None
                bg_ins = COLOR_INSA if j % 2 == 0 else COLOR_INSB
                _add(["", "", f"    {nombre_ins}",
                      unidad_ins, total_ins or None, p_ins_u, p_ins_t],
                     bg_ins, fg="1A3A5C")
            i_tar += 1

        # Fila TOTAL
        _add(["", "TOTAL", "", "", "", "", suma_total or None],
             COLOR_TOT, fg="FFFFFF", bold=True)

        # Ancho automático de columnas
        col_widths = [10, 6, 50, 10, 12, 14, 14]
        for i, w in enumerate(col_widths, 1):
            ws.column_dimensions[
                openpyxl.utils.get_column_letter(i)].width = w

        obra_nombre = (getattr(self.obra, "nombre", None) or
                       getattr(self.obra, "titulo", None) or "obra")
        nombre_safe = "".join(c for c in obra_nombre if c.isalnum() or c in " _-")
        nombre_archivo = f"{nombre_safe}_Detalle_de_Tareas.xlsx"
        from pathlib import Path
        ruta = Path(str(self.obra.carpeta)) / nombre_archivo
        try:
            wb.save(str(ruta))
            os.startfile(str(ruta))
        except Exception as e:
            messagebox.showerror("Error al exportar", str(e), parent=self)

    # ═══════════════════════════════════════════════════════════════
    #  Barra de tabs personalizada
    # ═══════════════════════════════════════════════════════════════

    def _build_custom_tabbar(self):
        """Frame con botones tk coloreados — reemplaza la tira de tabs nativa."""
        tabbar = tk.Frame(self, bg="#c0c0c0", height=30)
        tabbar.pack(fill="x", padx=8, pady=(8, 0))
        tabbar.pack_propagate(False)
        tabbar.grid_columnconfigure(4, weight=1)   # col INFORMES se expande

        self._tab_btns  = {}
        self._tab_activo = 0

        TRABAJO = [
            (0, "  1. Rubros  "),
            (1, "  2. Tareas  "),
            (2, "  3. Insumos y precios  "),
            (3, "  4. Presupuesto  "),
        ]
        INFORMES_TABS = [
            (4, "  Insumos  "),
            (5, "  Materiales  "),
            (6, "  Mano de Obra  "),
            (7, "  Detalle Tareas  "),
        ]

        for col, text in TRABAJO:
            btn = tk.Button(tabbar, text=text, font=FUENTE_S,
                            relief="flat", borderwidth=0, cursor="hand2",
                            command=lambda i=col: self._select_nb(i))
            btn.grid(row=0, column=col, sticky="nsew", ipadx=4, ipady=3)
            self._tab_btns[col] = btn

        # Lengueta INFORMES — amarilla, columna con weight=1
        lbl_inf = tk.Label(tabbar, text="  INFORMES  ",
                           bg="#f5c400", fg="#333333",
                           font=("Segoe UI", 9, "bold"), anchor="center")
        lbl_inf.grid(row=0, column=4, sticky="nsew")

        for col, text in INFORMES_TABS:
            btn = tk.Button(tabbar, text=text, font=FUENTE_S,
                            relief="flat", borderwidth=0, cursor="hand2",
                            command=lambda i=col: self._select_nb(i))
            btn.grid(row=0, column=col + 4, sticky="nsew", ipadx=4, ipady=3)
            self._tab_btns[col] = btn

        self._actualizar_estilos_tabbar()

    def _select_nb(self, idx: int):
        """Muestra el frame del tab idx y oculta los demas."""
        for i, frm in enumerate(self._tab_frames):
            if i == idx:
                frm.place(relx=0, rely=0, relwidth=1, relheight=1)
                frm.lift()
            else:
                frm.place_forget()
        self._tab_activo = idx
        self._actualizar_estilos_tabbar()
        self._on_tab_switch(idx)

    def _actualizar_estilos_tabbar(self):
        idx = getattr(self, "_tab_activo", 0)
        for i, btn in self._tab_btns.items():
            if i < 4:   # trabajo
                bg = COLOR_HDR  if i == idx else "#dce8f0"
                fg = "white"    if i == idx else COLOR_HDR
            else:       # informe
                bg = COLOR_VERDE if i == idx else "#d4e8d4"
                fg = "white"     if i == idx else "#1d5a2a"
            btn.config(bg=bg, fg=fg)

    # ═══════════════════════════════════════════════════════════════
    #  INFORMES
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    @staticmethod
    def _fmt_q(v, dec=3) -> str:
        """Cantidad: notación argentina, `dec` decimales."""
        s = f"{v:,.{dec}f}"                          # "1,234.567"
        return s.replace(",", "\x00").replace(".", ",").replace("\x00", ".")  # "1.234,567"

    @staticmethod
    def _fmt_pu(v) -> str:
        """Precio Unitario: #.##0,00  (notación argentina, 2 decimales)."""
        s = f"{v:,.2f}"                          # "1,234.56"
        return s.replace(",", "\x00").replace(".", ",").replace("\x00", ".")  # "1.234,56"

    @staticmethod
    def _fmt_pt(v) -> str:
        """Precio Total: #.##0  (notación argentina, sin decimales)."""
        return f"{round(v):,}".replace(",", ".")  # "1.234"

    @staticmethod
    def _tipo_insumo(desc: str) -> str:
        """Clasifica un insumo: 'mdo', 'subcontrato' o 'material'."""
        d = desc.strip()
        if any(d.startswith(p) for p in ("M. de Obra", "Oficial", "Ayudante",
                                          "Prestaci\u00f3n Mano", "Prestacion Mano")):
            return "mdo"
        if d.startswith("Subcontrato"):
            return "subcontrato"
        return "material"

    def _make_rpt_tabla(self, parent, titulo, cols, anchos, textos, anclas,
                        cmd_actualizar, export_fn=None):
        """Arma la estructura estandar de una pestana de informe."""
        hdr = tk.Frame(parent, bg=COLOR_VERDE, height=36)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text=f"  {titulo}", bg=COLOR_VERDE, fg="white",
                 font=FUENTE_B).pack(side="left", padx=8)
        # Botón Exportar — se conecta al tbl después de crearlo (via lista mutable)
        _tbl_ref = [None]
        def _exportar():
            if export_fn is not None:
                export_fn()
            else:
                self._exportar_rpt(_tbl_ref[0], titulo, textos, cols)
        tk.Button(hdr, text="Exportar", bg="#155c38", fg="white",
                  font=FUENTE_S, relief="flat", padx=8, pady=2,
                  cursor="hand2", command=_exportar
                  ).pack(side="right", padx=8, pady=4)
        lbl = tk.Label(parent, text="", bg="#e8f0f8",
                       font=FUENTE_B, anchor="e", fg=COLOR_HDR, pady=4, padx=12)
        lbl.pack(side="bottom", fill="x", padx=8, pady=(0, 4))
        tbl = ttk.Treeview(parent, columns=cols, show="headings", selectmode="browse")
        _tbl_ref[0] = tbl
        for c in cols:
            tbl.heading(c, text=textos[c])
            tbl.column(c, width=anchos[c], minwidth=24, anchor=anclas.get(c, "center"))
        scr = ttk.Scrollbar(parent, orient="vertical", command=tbl.yview)
        tbl.configure(yscrollcommand=scr.set)
        scr.pack(side="right", fill="y", padx=(0, 8))
        tbl.pack(fill="both", expand=True, padx=(8, 0), pady=(4, 0))
        tbl.tag_configure("par",     background="#ffffff")
        tbl.tag_configure("impar",   background="#f0f4fa")
        tbl.tag_configure("rub_hdr", background="#d4edda",
                          font=("Segoe UI", 10, "bold"))
        tbl.tag_configure("sin_vnc", background="#fde8e8")
        tbl.tag_configure("ins_a",   background="#eef4fb",
                          foreground="#1a3a5c", font=("Segoe UI", 9))
        tbl.tag_configure("ins_b",   background="#e4ecf7",
                          foreground="#1a3a5c", font=("Segoe UI", 9))
        tbl.tag_configure("total_row", background="#1d5a2a", foreground="white",
                          font=("Segoe UI", 10, "bold"))
        return tbl, lbl

    def _exportar_rpt(self, tbl, titulo, textos, cols):
        """Exporta el contenido de una pestaña de informe a un archivo Excel."""
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment
        import os
        from pathlib import Path
        from tkinter import messagebox

        if tbl is None:
            return

        # Recolectar filas: adjuntas + hijos detachados (Detalle Tareas)
        all_rows = []
        for iid in tbl.get_children(""):
            vals = list(tbl.item(iid)["values"])
            tags = list(tbl.item(iid).get("tags") or [])
            all_rows.append((vals, tags))
            if hasattr(self, "_det_children") and iid in self._det_children:
                for child in self._det_children[iid]:
                    try:
                        cvals = list(tbl.item(child)["values"])
                        ctags = list(tbl.item(child).get("tags") or [])
                        all_rows.append((cvals, ctags))
                    except Exception:
                        pass

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = titulo[:31]

        # Encabezado
        headers = [textos[c] for c in cols]
        ws.append(headers)
        for cell in ws[1]:
            cell.font      = Font(bold=True, color="FFFFFF")
            cell.fill      = PatternFill("solid", fgColor="1D5A2A")
            cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 18

        # Filas de datos
        COLOR_RUB  = "D4EDDA"
        COLOR_TOT  = "1D5A2A"
        COLOR_JOR  = "C8E6C9"
        COLOR_PAR  = "FFFFFF"
        COLOR_IMPAR = "F0F4FA"
        COLOR_INSA  = "EEF4FB"
        COLOR_INSB  = "E4ECF7"
        COLOR_SIN   = "FDE8E8"

        fill_map = {
            "total_row": (COLOR_TOT, "FFFFFF", True),
            "jornal_row": (COLOR_JOR, "1B5E20", True),
            "rub_hdr":   (COLOR_RUB,  "000000", True),
            "par":       (COLOR_PAR,  "000000", False),
            "impar":     (COLOR_IMPAR,"000000", False),
            "ins_a":     (COLOR_INSA, "1A3A5C", False),
            "ins_b":     (COLOR_INSB, "1A3A5C", False),
            "sin_vnc":   (COLOR_SIN,  "000000", False),
        }

        for vals, tags in all_rows:
            ws.append(vals)
            ri = ws.max_row
            bg, fg, bold = COLOR_PAR, "000000", False
            for tag in tags:
                if tag in fill_map:
                    bg, fg, bold = fill_map[tag]
                    break
            for cell in ws[ri]:
                cell.fill = PatternFill("solid", fgColor=bg)
                cell.font = Font(bold=bold, color=fg)

        # Anchos de columna automáticos
        for col_cells in ws.columns:
            max_len = max((len(str(c.value or "")) for c in col_cells), default=8)
            ws.column_dimensions[col_cells[0].column_letter].width = min(max_len + 4, 55)

        # Guardar en carpeta de la obra
        obra_nombre = (getattr(self.obra, "nombre", None) or
                       getattr(self.obra, "titulo", None) or "obra")
        nombre_safe = "".join(c for c in obra_nombre if c.isalnum() or c in " _-")
        titulo_safe = titulo.replace(" ", "_")
        nombre_archivo = f"{nombre_safe}_{titulo_safe}.xlsx"
        carpeta = Path(str(self.obra.carpeta))
        ruta = carpeta / nombre_archivo

        try:
            wb.save(str(ruta))
            os.startfile(str(ruta))
        except Exception as e:
            messagebox.showerror("Error al exportar", str(e))

    # ── Insumos (todos) ─────────────────────────────────────────────
    def _build_rpt_insumos(self):
        cols    = ("cod", "nombre", "unidad", "cantidad", "p_unitario", "p_total", "acum")
        anchos  = {"cod": 80, "nombre": 270, "unidad": 60, "cantidad": 90,
                   "p_unitario": 100, "p_total": 100, "acum": 72}
        textos  = {"cod": "Codigo", "nombre": "Insumo",
                   "unidad": "Unidad", "cantidad": "Cantidad",
                   "p_unitario": "P.Unitario", "p_total": "P.Total", "acum": "% Acum."}
        anclas  = {"cod": "w", "nombre": "w", "unidad": "center", "cantidad": "e",
                   "p_unitario": "e", "p_total": "e", "acum": "e"}
        self.tbl_rpt_ins, self.lbl_rpt_ins = self._make_rpt_tabla(
            self.tab_rpt_ins, "Listado de Insumos",
            cols, anchos, textos, anclas, self._cargar_rpt_insumos)
        self._ins_ptmap = {}
        self._ins_stot  = 0.0
        _asc_ins = [True]
        def _sort_ins():
            tbl  = self.tbl_rpt_ins
            kids = list(tbl.get_children(""))
            data = [(tbl.item(k)["values"], k)
                    for k in kids if "total_row" not in (tbl.item(k)["tags"] or [])]
            def _n(v):
                try: return float(str(v[-2]).replace(".", "").replace(",", "."))
                except: return -1
            data.sort(key=lambda x: _n(x[0]), reverse=not _asc_ins[0])
            _asc_ins[0] = not _asc_ins[0]
            for i, (_, k) in enumerate(data):
                tbl.move(k, "", i)
            for k in kids:
                if "total_row" in (tbl.item(k)["tags"] or []):
                    tbl.move(k, "", "end")
            # recalcular % acumulado en el nuevo orden
            acum = 0.0
            for k in tbl.get_children(""):
                if "total_row" in (tbl.item(k)["tags"] or []):
                    continue
                pt = self._ins_ptmap.get(k, 0.0)
                if self._ins_stot:
                    acum += pt / self._ins_stot * 100
                vals = list(tbl.item(k)["values"])
                vals[-1] = f"{acum:.1f}%" if self._ins_stot else ""
                tbl.item(k, values=vals)
        self.tbl_rpt_ins.heading("p_total", text="P.Total ↕", command=_sort_ins)

    def _cargar_rpt_insumos(self, tipo=None):
        for item in self.tbl_rpt_ins.get_children():
            self.tbl_rpt_ins.delete(item)
        insumos_raw = self.obra.calcular_insumos(self.maestro["incidencias"])
        if not insumos_raw:
            self.tbl_rpt_ins.insert("", "end",
                values=("", "Sin tareas o cantidades cargadas.", "", "", "", ""))
            self.lbl_rpt_ins.config(text="")
            return
        cat = self.maestro["insumos"]
        i = 0
        suma_total = 0.0
        rows_pt    = []   # [(iid, p_total_num)]
        for cod_ins, datos in sorted(insumos_raw.items()):
            nombre = cat.get(cod_ins, {}).get("nombre", cod_ins)
            unidad = datos.get("unidad") or cat.get(cod_ins, {}).get("unidad", "")
            cant   = datos["cantidad_total"]
            if tipo and self._tipo_insumo(nombre) != tipo:
                continue
            p_unit  = self._precios.get(cod_ins)
            p_total = p_unit * cant if p_unit is not None else None
            pt_num  = p_total if p_total is not None else 0.0
            if p_total is not None:
                suma_total += p_total
            p_u_str = self._fmt_pu(p_unit)  if p_unit  is not None else ""
            p_t_str = self._fmt_pt(p_total) if p_total is not None else ""
            tag     = "par" if i % 2 == 0 else "impar"
            orig_vals = [cod_ins, nombre, unidad, self._fmt_q(cant, 2), p_u_str, p_t_str, ""]
            iid = self.tbl_rpt_ins.insert("", "end", tags=(tag,), values=orig_vals)
            rows_pt.append((iid, pt_num, orig_vals))
            i += 1
        # calcular % acumulado
        self._ins_ptmap = {iid: pt for iid, pt, _ in rows_pt}
        self._ins_stot  = suma_total
        acum = 0.0
        for iid, pt, orig_vals in rows_pt:
            if suma_total:
                acum += pt / suma_total * 100
            orig_vals[-1] = f"{acum:.1f}%" if suma_total else ""
            self.tbl_rpt_ins.item(iid, values=orig_vals)
        self.tbl_rpt_ins.insert("", "end", iid="ins_total_row", tags=("total_row",),
            values=("", "TOTAL", "", "", "", self._fmt_pt(suma_total), "100%"))
        label = {None: "Todos", "material": "Materiales",
                 "mdo": "M. de Obra", "subcontrato": "Subcontratos"}.get(tipo, tipo)
        self.lbl_rpt_ins.config(text=f"{label}: {i} insumos")

    # ── Materiales ──────────────────────────────────────────────────
    def _build_rpt_materiales(self):
        cols    = ("cod", "nombre", "unidad", "cantidad", "p_unitario", "p_total", "acum")
        anchos  = {"cod": 80, "nombre": 270, "unidad": 60, "cantidad": 90,
                   "p_unitario": 100, "p_total": 100, "acum": 72}
        textos  = {"cod": "Codigo", "nombre": "Material",
                   "unidad": "Unidad", "cantidad": "Cantidad",
                   "p_unitario": "P.Unitario", "p_total": "P.Total", "acum": "% Acum."}
        anclas  = {"cod": "w", "nombre": "w", "unidad": "center", "cantidad": "e",
                   "p_unitario": "e", "p_total": "e", "acum": "e"}
        self.tbl_rpt_mat, self.lbl_rpt_mat = self._make_rpt_tabla(
            self.tab_rpt_mat, "Materiales",
            cols, anchos, textos, anclas, self._cargar_rpt_materiales)
        self._mat_ptmap = {}
        self._mat_stot  = 0.0
        _asc_mat = [True]
        def _sort_mat():
            tbl  = self.tbl_rpt_mat
            kids = list(tbl.get_children(""))
            data = [(tbl.item(k)["values"], k)
                    for k in kids if "total_row" not in (tbl.item(k)["tags"] or [])]
            def _n(v):
                try: return float(str(v[-2]).replace(".", "").replace(",", "."))
                except: return -1
            data.sort(key=lambda x: _n(x[0]), reverse=not _asc_mat[0])
            _asc_mat[0] = not _asc_mat[0]
            for i, (_, k) in enumerate(data):
                tbl.move(k, "", i)
            for k in kids:
                if "total_row" in (tbl.item(k)["tags"] or []):
                    tbl.move(k, "", "end")
            acum = 0.0
            for k in tbl.get_children(""):
                if "total_row" in (tbl.item(k)["tags"] or []):
                    continue
                pt = self._mat_ptmap.get(k, 0.0)
                if self._mat_stot:
                    acum += pt / self._mat_stot * 100
                vals = list(tbl.item(k)["values"])
                vals[-1] = f"{acum:.1f}%" if self._mat_stot else ""
                tbl.item(k, values=vals)
        self.tbl_rpt_mat.heading("p_total", text="P.Total ↕", command=_sort_mat)

    def _cargar_rpt_materiales(self):
        for item in self.tbl_rpt_mat.get_children():
            self.tbl_rpt_mat.delete(item)
        insumos_raw = self.obra.calcular_insumos(self.maestro["incidencias"])
        if not insumos_raw:
            self.tbl_rpt_mat.insert("", "end",
                values=("", "Sin tareas o cantidades cargadas.", "", "", "", ""))
            self.lbl_rpt_mat.config(text="")
            return
        cat = self.maestro["insumos"]
        i = 0
        suma_total = 0.0
        rows_pt    = []
        for cod_ins, datos in sorted(insumos_raw.items()):
            nombre = cat.get(cod_ins, {}).get("nombre", cod_ins)
            if self._tipo_insumo(nombre) != "material":
                continue
            unidad  = datos.get("unidad") or cat.get(cod_ins, {}).get("unidad", "")
            cant    = datos["cantidad_total"]
            p_unit  = self._precios.get(cod_ins)
            p_total = p_unit * cant if p_unit is not None else None
            pt_num  = p_total if p_total is not None else 0.0
            if p_total is not None:
                suma_total += p_total
            p_u_str = self._fmt_pu(p_unit)  if p_unit  is not None else ""
            p_t_str = self._fmt_pt(p_total) if p_total is not None else ""
            tag     = "par" if i % 2 == 0 else "impar"
            orig_vals = [cod_ins, nombre, unidad, self._fmt_q(cant, 2), p_u_str, p_t_str, ""]
            iid = self.tbl_rpt_mat.insert("", "end", tags=(tag,), values=orig_vals)
            rows_pt.append((iid, pt_num, orig_vals))
            i += 1
        self._mat_ptmap = {iid: pt for iid, pt, _ in rows_pt}
        self._mat_stot  = suma_total
        acum = 0.0
        for iid, pt, orig_vals in rows_pt:
            if suma_total:
                acum += pt / suma_total * 100
            orig_vals[-1] = f"{acum:.1f}%" if suma_total else ""
            self.tbl_rpt_mat.item(iid, values=orig_vals)
        self.tbl_rpt_mat.insert("", "end", iid="mat_total_row", tags=("total_row",),
            values=("", "TOTAL", "", "", "", self._fmt_pt(suma_total), "100%"))
        self.lbl_rpt_mat.config(text=f"Materiales: {i} items")

    # ── Mano de Obra ────────────────────────────────────────────────
    def _build_rpt_mdo(self):
        cols    = ("cod", "nombre", "unidad", "cantidad", "p_unitario", "p_total")
        anchos  = {"cod": 80, "nombre": 310, "unidad": 60, "cantidad": 100,
                   "p_unitario": 110, "p_total": 110}
        textos  = {"cod": "Codigo", "nombre": "Categoria M. de Obra",
                   "unidad": "Unidad", "cantidad": "Cantidad",
                   "p_unitario": "P.Unitario", "p_total": "P.Total"}
        anclas  = {"cod": "w", "nombre": "w", "unidad": "center", "cantidad": "e",
                   "p_unitario": "e", "p_total": "e"}
        self.tbl_rpt_mdo, self.lbl_rpt_mdo = self._make_rpt_tabla(
            self.tab_rpt_mdo, "Mano de Obra",
            cols, anchos, textos, anclas, self._cargar_rpt_mdo)
        _asc_mdo = [True]
        def _sort_mdo():
            tbl = self.tbl_rpt_mdo
            kids = list(tbl.get_children(""))
            _fixed = {"total_row", "jornal_row"}
            data = [(tbl.item(k)["values"], k)
                    for k in kids if not (_fixed & set(tbl.item(k)["tags"] or []))]
            def _n(v):
                try: return float(str(v[-1]).replace(".", "").replace(",", "."))
                except: return -1
            data.sort(key=lambda x: _n(x[0]), reverse=not _asc_mdo[0])
            _asc_mdo[0] = not _asc_mdo[0]
            for i, (_, k) in enumerate(data):
                tbl.move(k, "", i)
            for k in kids:
                if _fixed & set(tbl.item(k)["tags"] or []):
                    tbl.move(k, "", "end")
        self.tbl_rpt_mdo.heading("p_total", text="P.Total ↕", command=_sort_mdo)

    def _cargar_rpt_mdo(self):
        for item in self.tbl_rpt_mdo.get_children():
            self.tbl_rpt_mdo.delete(item)
        insumos_raw = self.obra.calcular_insumos(self.maestro["incidencias"])
        if not insumos_raw:
            self.tbl_rpt_mdo.insert("", "end",
                values=("", "Sin tareas o cantidades cargadas.", "", "", "", ""))
            self.lbl_rpt_mdo.config(text="")
            return
        cat = self.maestro["insumos"]
        i = 0
        suma_total  = 0.0
        hs_oficial  = 0.0
        hs_ayudante = 0.0
        for cod_ins, datos in sorted(insumos_raw.items()):
            nombre = cat.get(cod_ins, {}).get("nombre", cod_ins)
            if self._tipo_insumo(nombre) != "mdo":
                continue
            unidad  = datos.get("unidad") or cat.get(cod_ins, {}).get("unidad", "")
            cant    = datos["cantidad_total"]
            p_unit  = self._precios.get(cod_ins)
            p_total = p_unit * cant if p_unit is not None else None
            if p_total is not None:
                suma_total += p_total
            if nombre.strip().startswith("Oficial"):
                hs_oficial  += cant
            elif nombre.strip().startswith("Ayudante"):
                hs_ayudante += cant
            p_u_str = self._fmt_pu(p_unit)  if p_unit  is not None else ""
            p_t_str = self._fmt_pt(p_total) if p_total is not None else ""
            tag     = "par" if i % 2 == 0 else "impar"
            self.tbl_rpt_mdo.insert("", "end", tags=(tag,),
                values=(cod_ins, nombre, unidad, self._fmt_q(cant, 2), p_u_str, p_t_str))
            i += 1
        self.tbl_rpt_mdo.tag_configure("jornal_row", background="#c8e6c9",
                                        foreground="#1b5e20",
                                        font=("Segoe UI", 10, "bold"))
        self.tbl_rpt_mdo.insert("", "end", iid="mdo_total_row", tags=("total_row",),
            values=("", "TOTAL", "", "", "", self._fmt_pt(suma_total)))
        jof  = hs_oficial  / 8
        jay  = hs_ayudante / 8
        jtot = jof + jay
        _jf  = lambda v: f"{v:,.1f}" if v else ""
        self.tbl_rpt_mdo.insert("", "end", iid="mdo_jornal_of", tags=("jornal_row",),
            values=("", "", "", "", "Jornales Oficial",  _jf(jof)))
        self.tbl_rpt_mdo.insert("", "end", iid="mdo_jornal_ay", tags=("jornal_row",),
            values=("", "", "", "", "Jornales Ayudante", _jf(jay)))
        self.tbl_rpt_mdo.insert("", "end", iid="mdo_jornal_tot", tags=("jornal_row",),
            values=("", "", "", "", "Total Jornales",    _jf(jtot)))
        self.lbl_rpt_mdo.config(text=f"Categorias M. de Obra: {i}")

    # ── Detalle de Tareas ───────────────────────────────────────────
    def _build_rpt_detalle(self):
        cols   = ("rubro", "item", "descripcion", "unidad", "cantidad",
                  "p_unitario", "p_total")
        anchos = {"rubro": 42, "item": 42, "descripcion": 260,
                  "unidad": 60, "cantidad": 90, "p_unitario": 100, "p_total": 100}
        textos = {"rubro": "Rubro", "item": "Item", "descripcion": "Descripcion",
                  "unidad": "Unidad", "cantidad": "Cantidad",
                  "p_unitario": "P.Unitario", "p_total": "P.Total"}
        anclas = {"rubro": "center", "item": "center", "descripcion": "w",
                  "unidad": "center", "cantidad": "e",
                  "p_unitario": "e", "p_total": "e"}
        self.tbl_rpt_det, self.lbl_rpt_det = self._make_rpt_tabla(
            self.tab_rpt_det, "Detalle de Tareas",
            cols, anchos, textos, anclas, self._cargar_rpt_detalle,
            export_fn=self._exportar_rpt_detalle)
        self._det_children = {}   # tarea_iid → [child_iids]
        self._det_open     = set()  # iids actualmente abiertos
        def _toggle_det(event):
            iid = self.tbl_rpt_det.identify_row(event.y)
            if not iid.startswith("dtar_"):
                return
            children = self._det_children.get(iid, [])
            if not children:
                return
            vals = list(self.tbl_rpt_det.item(iid, "values"))
            if iid in self._det_open:
                for c in children:
                    self.tbl_rpt_det.detach(c)
                vals[2] = "▶" + vals[2][1:]
                self._det_open.discard(iid)
            else:
                all_top = list(self.tbl_rpt_det.get_children(""))
                pos = all_top.index(iid) + 1
                for j, c in enumerate(children):
                    self.tbl_rpt_det.move(c, "", pos + j)
                vals[2] = "▼" + vals[2][1:]
                self._det_open.add(iid)
            self.tbl_rpt_det.item(iid, values=vals)
        self.tbl_rpt_det.bind("<Button-1>", _toggle_det)

    def _cargar_rpt_detalle(self):
        # Eliminar filas adjuntas
        for item in self.tbl_rpt_det.get_children():
            self.tbl_rpt_det.delete(item)
        # Eliminar también los hijos detacheados de la carga anterior
        for children in getattr(self, "_det_children", {}).values():
            for c in children:
                try:
                    self.tbl_rpt_det.delete(c)
                except Exception:
                    pass
        items_ppto  = getattr(self.obra, "items_presupuesto", [])
        incidencias = self.maestro["incidencias"]
        cat         = self.maestro["insumos"]
        if not items_ppto:
            self.tbl_rpt_det.insert("", "end",
                values=("", "", "Sin items de presupuesto.", "", "", "", ""))
            self.lbl_rpt_det.config(text="")
            return
        self._det_children = {}
        self._det_open     = set()
        i_tar = 0
        n_tar = 0
        sin_vnc = 0
        suma_total    = 0.0
        cur_rubro_idx = None
        rubro_counts  = {}
        for idx, it in enumerate(items_ppto):
            if it.get("es_rubro"):
                cur_rubro_idx = idx
                rubro_counts[cur_rubro_idx] = 0
                self.tbl_rpt_det.insert("", "end", tags=("rub_hdr",),
                    values=(it.get("rubro", ""), "",
                            it.get("descripcion", ""), "", "", "", ""))
                continue
            cod_tar = it.get("cod_tar", "")
            subcont = (it.get("subcontrato") or "").strip().upper()
            cant    = it.get("cantidad") or 0.0
            desc    = it.get("descripcion", "")
            unidad  = it.get("unidad", "")
            rub     = it.get("rubro", "")
            rubro_counts[cur_rubro_idx] = rubro_counts.get(cur_rubro_idx, 0) + 1
            item_num = f"{rubro_counts[cur_rubro_idx]:02d}"
            if not cod_tar:
                sin_vnc += 1
                self.tbl_rpt_det.insert("", "end", tags=("sin_vnc",),
                    values=(rub, item_num, f"  [sin vincular]  {desc}", unidad,
                            self._fmt_q(cant, 2) if cant else "", "", ""))
                continue
            n_tar += 1
            cod_buscar = cod_tar + subcont if (cod_tar and subcont) else cod_tar
            lista_inc  = incidencias.get(cod_buscar) or incidencias.get(cod_tar, [])
            tag_tar    = "par" if i_tar % 2 == 0 else "impar"
            cod_label  = cod_tar + subcont if subcont else cod_tar
            cant_str   = self._fmt_q(cant, 2) if cant else ""
            p_unit_tar = self._precios_tarea.get(idx)
            if p_unit_tar is None:
                p_unit_tar = sum(
                    (self._precios.get(inc["cod_ins"], 0.0) or 0.0) * inc.get("cantidad", 0.0)
                    for inc in lista_inc
                ) or None
            p_total_tar = p_unit_tar * cant if (p_unit_tar and cant) else None
            if p_total_tar is not None:
                suma_total += p_total_tar
            pu_str = self._fmt_pu(p_unit_tar)  if p_unit_tar  is not None else ""
            pt_str = self._fmt_pt(p_total_tar) if p_total_tar is not None else ""
            tar_iid = f"dtar_{idx}"
            flecha  = "▶ " if lista_inc else "  "
            self.tbl_rpt_det.insert("", "end", iid=tar_iid, tags=(tag_tar,),
                values=(rub, item_num, f"{flecha}{desc}  [{cod_label}]",
                        unidad, cant_str, pu_str, pt_str))
            child_iids = []
            for j, inc in enumerate(lista_inc):
                cod_ins    = inc["cod_ins"]
                nombre_ins = cat.get(cod_ins, {}).get("nombre", cod_ins)
                unidad_ins = inc.get("unidad") or cat.get(cod_ins, {}).get("unidad", "")
                inc_cant   = inc.get("cantidad", 0)
                total_ins  = inc_cant * cant
                p_ins_u    = self._precios.get(cod_ins)
                p_ins_t    = p_ins_u * total_ins if p_ins_u is not None else None
                p_iu_str   = self._fmt_pu(p_ins_u) if p_ins_u is not None else ""
                p_it_str   = self._fmt_pt(p_ins_t) if p_ins_t is not None else ""
                tag_ins    = "ins_a" if j % 2 == 0 else "ins_b"
                ins_iid    = f"dins_{idx}_{j}"
                self.tbl_rpt_det.insert("", "end", iid=ins_iid, tags=(tag_ins,),
                    values=("", "", f"    {nombre_ins}",
                            unidad_ins, self._fmt_q(total_ins, 2), p_iu_str, p_it_str))
                child_iids.append(ins_iid)
            if child_iids:
                self._det_children[tar_iid] = child_iids
                # empieza colapsado: desconectar hijos inmediatamente
                for c in child_iids:
                    self.tbl_rpt_det.detach(c)
            i_tar += 1
        self.tbl_rpt_det.insert("", "end", iid="det_total_row", tags=("total_row",),
            values=("", "TOTAL", "", "", "", "", self._fmt_pt(suma_total)))
        self.lbl_rpt_det.config(
            text=f"Tareas vinculadas: {n_tar}  |  Sin vincular: {sin_vnc}")


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


class _DlgGuardarVersion(tk.Toplevel):
    def __init__(self, parent, nombre_actual: str):
        super().__init__(parent)
        self.title("Guardar obra")
        self.resizable(False, False)
        self.grab_set()
        self.accion = None
        self.nota   = ""
        hdr = tk.Frame(self, bg=COLOR_HDR, height=40)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="  ¿Cómo querés guardar?",
                 bg=COLOR_HDR, fg="white", font=FUENTE_B).pack(side="left", padx=12)
        frm = tk.Frame(self, padx=20, pady=14)
        frm.pack(fill="both", expand=True)

        # ── Opción 1: Actualizar ──────────────────────────────────
        tk.Button(frm, text=f"Actualizar  {nombre_actual}",
                  bg=COLOR_VERDE, fg="white", font=FUENTE_B,
                  relief="flat", padx=12, pady=8, cursor="hand2", anchor="w",
                  command=lambda: self._elegir("pisar")
                  ).pack(fill="x", pady=(0, 10))

        ttk.Separator(frm, orient="horizontal").pack(fill="x", pady=(0, 10))

        # ── Opción 2: Nueva versión ───────────────────────────────
        tk.Button(frm, text="Guardar como nueva versión...",
                  bg=COLOR_SEC, fg="white", font=FUENTE_B,
                  relief="flat", padx=12, pady=8, cursor="hand2",
                  command=lambda: self._elegir("nueva")
                  ).pack(fill="x", pady=(0, 8))

        tk.Label(frm, text="Nombre de la versión:",
                 font=FUENTE_S, fg="#555", anchor="w").pack(fill="x", pady=(4, 0))
        self.var_nombre = tk.StringVar()
        ttk.Entry(frm, textvariable=self.var_nombre, font=FUENTE, width=38
                  ).pack(fill="x", pady=(2, 8))

        tk.Label(frm, text="Descripción de cambios (opcional):",
                 font=FUENTE_S, fg="#555", anchor="w").pack(fill="x")
        self.var_nota = tk.StringVar()
        ttk.Entry(frm, textvariable=self.var_nota, font=FUENTE, width=38
                  ).pack(fill="x", pady=(2, 10))

        tk.Button(frm, text="Cancelar", bg="#888", fg="white", font=FUENTE,
                  relief="flat", padx=12, pady=6, cursor="hand2",
                  command=self.destroy).pack(fill="x")
        self.bind("<Escape>", lambda _: self.destroy())
        self.update_idletasks()
        self.geometry(
            f"+{parent.winfo_x()+(parent.winfo_width()-self.winfo_width())//2}"
            f"+{parent.winfo_y()+(parent.winfo_height()-self.winfo_height())//2}")

    def _elegir(self, accion: str):
        self.accion = accion
        nombre = self.var_nombre.get().strip()
        desc   = self.var_nota.get().strip()
        if nombre and desc:
            self.nota = f"{nombre} — {desc}"
        elif nombre:
            self.nota = nombre
        else:
            self.nota = desc
        self.destroy()


class _DlgEditarFila(tk.Toplevel):
    def __init__(self, parent, it: dict, es_rubro=False, cod_tar_label=None):
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
            next_row = [0]
            def next_r():
                r = next_row[0]; next_row[0] += 1; return r
            v_rub,  e_rub = fila("Rubro:",      it.get("rubro", ""),      next_r())
            v_item, _     = fila("Ítem:",        it.get("item", ""),       next_r())
            v_desc, _     = fila("Descripción:", it.get("descripcion", ""),next_r())
            v_un,   _     = fila("Unidad:",      it.get("unidad", ""),     next_r())
            v_cant, _     = fila("Cantidad:",    it.get("cantidad", ""),   next_r())
            v_sub = None
            if it.get("cod_tar"):
                v_sub, _ = fila("Subcontrato:", it.get("subcontrato", ""), next_r())
                # Tarea vinculada — solo lectura + botón Desvincular
                row_tar = next_r()
                tk.Label(frm, text="Tarea std:", font=FUENTE_S, anchor="e", width=12
                         ).grid(row=row_tar, column=0, sticky="e", pady=(6, 2))
                frm_tar = tk.Frame(frm)
                frm_tar.grid(row=row_tar, column=1, sticky="ew", padx=(8, 0), pady=(6, 2))
                lbl_cod = cod_tar_label or it.get("cod_tar", "")
                tk.Label(frm_tar, text=lbl_cod[:55], font=FUENTE_S,
                         fg="#1a3a5c", anchor="w").pack(side="left", fill="x", expand=True)
                def _desvincular():
                    self.resultado = {
                        "es_rubro":    False,
                        "rubro":       v_rub.get().strip(),
                        "item":        v_item.get().strip(),
                        "descripcion": v_desc.get().strip(),
                        "unidad":      v_un.get().strip(),
                        "cantidad":    (float(v_cant.get().replace(",", "."))
                                        if v_cant.get().strip() else 0.0),
                        "cod_tar":     "",
                        "subcontrato": "",
                    }
                    self.destroy()
                tk.Button(frm_tar, text="Desvincular", bg=COLOR_ROJO, fg="white",
                          font=FUENTE_S, relief="flat", padx=6, pady=1,
                          cursor="hand2", command=_desvincular
                          ).pack(side="right")
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
                if it.get("cod_tar") and v_sub is not None:
                    res["subcontrato"] = v_sub.get().strip().upper()[:1]
            self.resultado = res
            self.destroy()
        tk.Button(frm_btn, text="Aceptar", bg=COLOR_VERDE, fg="white",
                  font=FUENTE_B, relief="flat", padx=12, pady=5,
                  command=_ok).pack(side="left", padx=4)
        tk.Button(frm_btn, text="Cancelar", bg="#888", fg="white", font=FUENTE,
                  relief="flat", padx=12, pady=5,
                  command=self.destroy).pack(side="left")
        self.bind("<Return>", lambda _: _ok())
        self.bind("<Escape>", lambda _: self.destroy())
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(
            f"+{parent.winfo_x()+(parent.winfo_width()-w)//2}"
            f"+{parent.winfo_y()+(parent.winfo_height()-h)//2}")


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
        tk.Button(frm_btn, text="Cancelar", bg="#888", fg="white", font=FUENTE,
                  relief="flat", padx=12, pady=5,
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
            tk.Button(frm, text=f"Actualizar  {nombre_actual}",
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


