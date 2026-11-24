"""tab_ejecucion.py — Pestaña '5. Ejecución': estados de tareas, Etapas XX
y cierre comparativo contra el Original. La lógica está en core/etapas.py."""
import json
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox, filedialog, simpledialog

from core import etapas as E
from core.maestro import cargar_precios

COLOR_HDR   = "#1a3a5c"
COLOR_SEC   = "#2a6099"
COLOR_VERDE = "#1d7a4a"
COLOR_ROJO  = "#b03030"
COLOR_BG    = "#f5f5f5"
FUENTE      = ("Segoe UI", 10)
FUENTE_B    = ("Segoe UI", 10, "bold")
FUENTE_S    = ("Segoe UI", 9)

COLOR_ESTADO = {"a_realizar": "#ffffff", "en_curso": "#fff3cd", "realizada": "#d4edda"}
COLOR_ADIC   = "#6a3d9a"   # texto de las tareas adicionales
COLOR_SEC_AD = "#5b2c83"   # encabezado de la sección Adicionales


def _fmt(v, dec=2):
    s = f"{v:,.{dec}f}"
    return s.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def _fmt_pt(v):
    return f"{round(v):,}".replace(",", ".")


def _parse_num(s: str):
    s = (s or "").strip().replace("$", "").replace(" ", "")
    if not s:
        return None
    if "," in s:                                   # 1.234,56 → 1234.56
        s = s.replace(".", "").replace(",", ".")
    elif s.count(".") > 1 or (s.count(".") == 1 and len(s.split(".")[1]) == 3
                              and s.split(".")[0].lstrip("-") not in ("", "0")):
        s = s.replace(".", "")                     # 850.000 / 1.250.000 → miles (0.125 no)
    return float(s)


def _btn(parent, texto, color, cmd, bold=False):
    return tk.Button(parent, text=texto, bg=color, fg="white",
                     font=FUENTE_B if bold else FUENTE_S, relief="flat",
                     padx=8, pady=3, cursor="hand2", command=cmd)


def _centrar(win, parent):
    win.update_idletasks()
    win.geometry(f"+{parent.winfo_rootx() + max((parent.winfo_width() - win.winfo_width()) // 2, 0)}"
                 f"+{parent.winfo_rooty() + max((parent.winfo_height() - win.winfo_height()) // 3, 0)}")


class TabEjecucion:
    """Se arma dentro de `frame`; `ventana` es la VentanaObra (obra, maestro, precios)."""

    def __init__(self, frame: tk.Frame, ventana):
        self.f = frame
        self.v = ventana
        self.obra = ventana.obra
        self.data = self.obra.carpeta_data
        self.ejec = None
        self.var_filtro = tk.StringVar(value="todas")
        self._abiertos = set()                       # tareas desplegadas
        self._build()

    # ── Armado ───────────────────────────────────────────────────
    def _build(self):
        f = self.f
        hdr = tk.Frame(f, bg=COLOR_HDR, height=36)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="  Ejecución por etapas", bg=COLOR_HDR, fg="white",
                 font=FUENTE_B).pack(side="left", padx=8)
        _btn(hdr, "Cierre / Comparación", COLOR_VERDE, self._cierre, True
             ).pack(side="right", padx=(4, 8), pady=4)
        _btn(hdr, "+ Nueva Etapa", COLOR_SEC, self._nueva_version, True
             ).pack(side="right", padx=4, pady=4)
        _btn(hdr, "Definir Original…", "#555", self._definir_original
             ).pack(side="right", padx=4, pady=4)
        _btn(hdr, "Actualizar precios del Original…", "#555", self._actualizar_precios_orig
             ).pack(side="right", padx=4, pady=4)

        self.lbl_orig = tk.Label(f, text="", bg="#e8f0f8", fg=COLOR_HDR,
                                 font=FUENTE_S, anchor="w", padx=10, pady=3)
        self.lbl_orig.pack(fill="x", padx=8, pady=(4, 0))

        fil = tk.Frame(f, bg=COLOR_BG)
        fil.pack(fill="x", padx=8, pady=(4, 2))
        tk.Label(fil, text="Ver:", bg=COLOR_BG, font=FUENTE_S).pack(side="left")
        for val, txt in (("todas", "Todas"), ("a_realizar", "A realizar"),
                         ("en_curso", "En curso"), ("realizada", "Realizadas"),
                         ("pendientes", "Pendientes (lo que falta)")):
            tk.Radiobutton(fil, text=txt, value=val, variable=self.var_filtro,
                           bg=COLOR_BG, font=FUENTE_S, command=self.refrescar
                           ).pack(side="left", padx=2)
        tk.Label(fil, text="   Marcar selección como:", bg=COLOR_BG,
                 font=FUENTE_S).pack(side="left", padx=(12, 4))
        for est, col in (("a_realizar", "#777"), ("en_curso", "#b8860b"),
                         ("realizada", COLOR_VERDE)):
            _btn(fil, E.ESTADO_TXT[est], col,
                 lambda e=est: self._marcar(e)).pack(side="left", padx=2)

        # Panel dividido: tareas arriba, etapas abajo
        pan = tk.PanedWindow(f, orient="vertical", bg=COLOR_BG, sashwidth=6)
        pan.pack(fill="both", expand=True, padx=8, pady=(2, 4))

        fr_t = tk.Frame(pan, bg=COLOR_BG)
        cols = ("rubro", "item", "desc", "unidad", "cant", "pu", "total",
                "pu_act", "tot_act", "ejec", "ejec_p", "saldo", "estado")
        txt = {"rubro": "Rubro", "item": "Ítem", "desc": "Descripción", "unidad": "Unidad",
               "cant": "Cant. Orig.", "pu": "PU Orig.", "total": "Total Orig.",
               "pu_act": "PU actual", "tot_act": "Total actual", "ejec": "Ejecutado", "ejec_p": "$ Ejecutado", "saldo": "Saldo",
               "estado": "Estado"}
        anch = {"rubro": 42, "item": 40, "desc": 260, "unidad": 50, "cant": 80,
                "pu": 95, "total": 105, "pu_act": 95, "tot_act": 105, "ejec": 80, "ejec_p": 105, "saldo": 80,
                "estado": 80}
        self.tbl = ttk.Treeview(fr_t, columns=cols, show="tree headings",
                                selectmode="extended")
        self.tbl.column("#0", width=22, minwidth=22, stretch=False)
        for c in cols:
            self.tbl.heading(c, text=txt[c])
            self.tbl.column(c, width=anch[c], minwidth=24,
                            anchor="w" if c == "desc" else ("center" if c in
                            ("rubro", "item", "unidad", "estado") else "e"))
        scr = ttk.Scrollbar(fr_t, orient="vertical", command=self.tbl.yview)
        self.tbl.configure(yscrollcommand=scr.set)
        scr.pack(side="right", fill="y")
        self.tbl.pack(fill="both", expand=True)
        self.tbl.tag_configure("tot", background="#d0dcea", foreground=COLOR_HDR,
                               font=FUENTE_B)
        self.tbl.tag_configure("rub", background=COLOR_HDR, foreground="white",
                               font=FUENTE_B)
        for est, col in COLOR_ESTADO.items():
            self.tbl.tag_configure(est, background=col)
        self.tbl.tag_configure("adic", foreground=COLOR_ADIC)
        self.tbl.tag_configure("sec_adic", background=COLOR_SEC_AD, foreground="white",
                               font=FUENTE_B)
        self.tbl.tag_configure("ins", background="#f7f7f7", foreground="#444",
                               font=FUENTE_S)
        self.tbl.tag_configure("ins_falta", background="#fff8e1", foreground="#8a5a00",
                               font=FUENTE_S)
        self.tbl.tag_configure("ins_exceso", background="#f7f7f7", foreground=COLOR_ROJO,
                               font=FUENTE_S)
        self.tbl.bind("<Button-3>", self._menu_tarea)
        self.tbl.bind("<ButtonRelease-1>", self._clic_tarea)
        self.tbl.bind("<<TreeviewOpen>>", lambda _: self._abiertos.add(self.tbl.focus()))
        self.tbl.bind("<<TreeviewClose>>",
                      lambda _: self._abiertos.discard(self.tbl.focus()))
        pan.add(fr_t, minsize=150, stretch="always")

        fr_v = tk.Frame(pan, bg=COLOR_BG)
        top_v = tk.Frame(fr_v, bg=COLOR_BG)
        top_v.pack(fill="x")
        tk.Label(top_v, text="Etapas", bg=COLOR_BG, fg=COLOR_HDR,
                 font=FUENTE_B).pack(side="left")
        _btn(top_v, "Eliminar", COLOR_ROJO, self._eliminar_version).pack(side="right", padx=2)
        _btn(top_v, "Exportar Excel", COLOR_VERDE, self._exportar_version).pack(side="right", padx=2)
        _btn(top_v, "Abrir / Editar", COLOR_SEC, self._abrir_version).pack(side="right", padx=2)
        vcols = ("ver", "nombre", "fecha", "precios", "n", "total")
        vtxt = {"ver": "Etapa", "nombre": "Nombre", "fecha": "Fecha",
                "precios": "Archivo de precios", "n": "Tareas", "total": "Total"}
        vanch = {"ver": 150, "nombre": 220, "fecha": 90, "precios": 200, "n": 60, "total": 120}
        self.tbl_v = ttk.Treeview(fr_v, columns=vcols, show="headings",
                                  selectmode="browse", height=5)
        for c in vcols:
            self.tbl_v.heading(c, text=vtxt[c])
            self.tbl_v.column(c, width=vanch[c], minwidth=30,
                              anchor="e" if c in ("total", "n") else
                              ("w" if c in ("nombre", "precios") else "center"))
        self.tbl_v.tag_configure("variante", background="#eef3fb", foreground="#1f5fbf")
        self.tbl_v.pack(fill="both", expand=True, pady=(2, 0))
        self.tbl_v.bind("<Double-1>", lambda _: self._abrir_version())
        pan.add(fr_v, minsize=90)

        self.lbl_tot = tk.Label(f, text="", bg="#e8f0f8", font=FUENTE_B, anchor="e",
                                fg=COLOR_HDR, pady=4, padx=12)
        self.lbl_tot.pack(side="bottom", fill="x", padx=8, pady=(0, 4))

    # ── Carga ────────────────────────────────────────────────────
    def refrescar(self):
        self.ejec = E.cargar_ejecucion(self.data)
        for t in (self.tbl, self.tbl_v):
            t.delete(*t.get_children())
        if not self.ejec:
            self.lbl_orig.config(text="  Todavía no hay Original definido. Usá «Definir Original…» "
                                      "para elegir la versión contratada (obraNNN.json).")
            self.lbl_tot.config(text="")
            return
        o = self.ejec["original"]
        self.lbl_orig.config(
            text=f"  Original: {o['archivo']}   |   precios: {o.get('archivo_precios') or '-'}"
                 f"   |   definido {o['fecha']}"
                 + (f"   |   precios actualizados {o['precios_actualizados']}"
                    if o.get("precios_actualizados") else ""))
        acc = E.acumulado(self.data)
        filtro = self.var_filtro.get()
        rubros = o.get("rubros", {})
        rub_act, n_est = None, {k: 0 for k in E.ESTADOS}
        t_orig = 0.0
        rub_tot = {}                                  # rubro: [$ orig, $ actual, $ ejecutado]
        inc = self.v.maestro["incidencias"]
        cat = self.v.maestro.get("insumos")
        consumo = E.consumo_insumos(self.data, inc)
        t_pend = 0.0                                  # insumos que faltan, a precio actual
        # Precios actuales de la obra (pestaña 3); si un insumo no tiene, el del Original.
        prec_act = {c: p for c, p in (self.v._precios or {}).items() if p}
        pend = filtro == "pendientes"
        _m = lambda v: f"$ {_fmt_pt(v)}" if v else ""
        for it in o["items"]:
            est = E.estado(self.ejec, it["clave"])
            n_est[est] += 1
            t_orig += it["cantidad"] * it["pu"]
            filas = E.saldo_insumos(self.ejec, it, inc, consumo, cat)
            q_ej = acc.get(it["clave"], {}).get("cantidad", 0.0)
            falta = est != "realizada" and (it["cantidad"] - q_ej > 1e-6 or
                                            any(f["saldo"] > 1e-6 for f in filas))
            if est != "realizada":
                t_pend += sum(f["saldo"] * (prec_act.get(f["cod_ins"]) or f["precio"])
                              for f in filas if f["saldo"] > 0)
            if pend:
                if not falta:
                    continue
            elif filtro != "todas" and est != filtro:
                continue
            if it["rubro"] != rub_act:
                rub_act = it["rubro"]
                if rub_act not in rub_tot:
                    rub_tot[rub_act] = [0.0, 0.0, 0.0]
                    self.tbl.insert("", "end", iid=f"rub|{rub_act}", tags=("rub",),
                                    values=(rub_act, "", rubros.get(rub_act, "")))
            p_ej = acc.get(it["clave"], {}).get("total", 0.0)
            n_falta = sum(1 for f in filas if f["saldo"] > 1e-6)
            desc = it["descripcion"] + (f"   [faltan {n_falta} insumo(s)]"
                                        if est != "realizada" and n_falta and q_ej else "")
            pu = it["pu"]
            pu_act = pu                               # PU con los precios actuales de la obra
            if not it.get("precio_manual") and it["cantidad"] and \
                    any(f["previsto"] for f in filas):
                pu_act = sum(f["q_orig"] * (prec_act.get(f["cod_ins"]) or f["precio"])
                             for f in filas if f["previsto"]) / it["cantidad"]
            r = rub_tot[rub_act]
            r[0] += it["cantidad"] * pu
            r[1] += it["cantidad"] * pu_act
            r[2] += p_ej
            self.tbl.insert("", "end", iid=it["clave"], tags=(est,),
                            open=it["clave"] in self._abiertos,
                            values=(
                it["rubro"], it["item"], desc, it["unidad"],
                _fmt(it["cantidad"]),
                f"$ {_fmt(pu)}" if pu else "-", _m(it["cantidad"] * pu) or "-",
                f"$ {_fmt(pu_act)}" if pu_act else "-", _m(it["cantidad"] * pu_act) or "-",
                _fmt(q_ej) if q_ej else "", _m(p_ej),
                _fmt(it["cantidad"] - q_ej), E.ESTADO_TXT[est]))
            self._insertar_insumos(it["clave"], filas, prec_act, solo_faltantes=pend)
        for r, (t_o, t_a, ej) in rub_tot.items():        # montos de cada rubro
            for col, v in (("total", t_o), ("tot_act", t_a), ("ejec_p", ej)):
                self.tbl.set(f"rub|{r}", col, _m(v))
        adic = sorted(E.adicionales(self.ejec), key=lambda a: (a["rubro"], a["clave"]))
        visibles = [a for a in adic if not pend and
                    (filtro == "todas" or E.estado(self.ejec, a["clave"]) == filtro)]
        for a in adic:
            n_est[E.estado(self.ejec, a["clave"])] += 1
        t_ad = sum(acc.get(a["clave"], {}).get("total", 0.0) for a in visibles)
        if visibles:
            self.tbl.insert("", "end", iid="rub|ADIC", tags=("sec_adic",), values=(
                "", "", "ADICIONALES (no previstas en el Original)",
                "", "", "", "", "", "", "", _m(t_ad), "", ""))
        for a in visibles:
            est = E.estado(self.ejec, a["clave"])
            q_ej = acc.get(a["clave"], {}).get("cantidad", 0.0)
            p_ej = acc.get(a["clave"], {}).get("total", 0.0)
            self.tbl.insert("", "end", iid=a["clave"], tags=(est, "adic"), values=(
                a["rubro"], a["item"], a["descripcion"], a["unidad"], "—", "—", "—", "—", "—",
                _fmt(q_ej) if q_ej else "", _m(p_ej), "", E.ESTADO_TXT[est]))
            self._insertar_insumos(a["clave"], E.saldo_insumos(self.ejec, a, inc, consumo, cat),
                                   prec_act)
        # Fila de totales de lo listado (solo montos: las cantidades tienen distintas unidades)
        if rub_tot or visibles:
            g = [sum(v[k] for v in rub_tot.values()) for k in range(3)]
            self.tbl.insert("", "end", iid="tot|", tags=("tot",), values=(
                "", "", "TOTAL" + (" (lo listado)" if filtro != "todas" else ""),
                "", "", "", _m(g[0]), "", _m(g[1]), "", _m(g[2] + t_ad), "", ""))
        t_ejec = 0.0
        for e in E.listar_etapas(self.data):
            tot = sum(i["cantidad"] * i["pu"] for i in e.get("items", []))
            t_ejec += tot
            self.tbl_v.insert("", "end", iid=str(e["numero"]), values=(
                f"Etapa {e['numero']:02d}", e.get("nombre", ""), e.get("fecha", ""),
                e.get("archivo_precios", ""), len(e.get("items", [])),
                f"$ {_fmt_pt(tot)}"))
            for v in E.listar_variantes(self.data, e["numero"]):   # no suman al ejecutado
                self.tbl_v.insert("", "end", iid=f"{e['numero']}v{v['variante']}",
                                  tags=("variante",), values=(
                    E.nombre_etapa(v), v.get("nombre", ""), v.get("fecha", ""),
                    v.get("archivo_precios", ""), len(v.get("items", [])),
                    f"$ {_fmt_pt(sum(i['cantidad'] * i['pu'] for i in v.get('items', [])))}"))
        self.lbl_tot.config(
            text=f"A realizar: {n_est['a_realizar']}   En curso: {n_est['en_curso']}   "
                 f"Realizadas: {n_est['realizada']}      |      "
                 f"Original: $ {_fmt_pt(t_orig)}     Ejecutado: $ {_fmt_pt(t_ejec)}"
                 + (f"  (adicionales: {len(adic)})" if adic else "")
                 + f"     Falta (insumos a precio actual): $ {_fmt_pt(t_pend)}")

    def _insertar_insumos(self, clave, filas, precios, solo_faltantes=False):
        """Filas hijas de una tarea: por insumo, previsto / ejecutado / saldo, con el precio
        del Original y el actual de la obra (« *» = cambió respecto del Original)."""
        for n, f in enumerate(filas):
            if solo_faltantes and f["saldo"] <= 1e-6:
                continue
            p_act = precios.get(f["cod_ins"]) or f["precio"]
            marca = " *" if f["precio"] and abs(p_act - f["precio"]) > 1e-9 else ""
            tag = ("ins_falta" if f["saldo"] > 1e-6 else
                   "ins_exceso" if f["saldo"] < -1e-6 else "ins")
            extra = "" if f["previsto"] else "   (no previsto)"
            self.tbl.insert(clave, "end", iid=f"{clave}|{n}", tags=(tag,), values=(
                "", f["cod_ins"], f"    {f['nombre'] or f['cod_ins']}{extra}", f["unidad"],
                _fmt(f["q_orig"]) if f["q_orig"] else "—",
                f"$ {_fmt(f['precio'])}" if f["precio"] else "",
                f"$ {_fmt_pt(f['q_orig'] * f['precio'])}" if f["q_orig"] * f["precio"] else "",
                f"$ {_fmt(p_act)}{marca}" if p_act else "",
                f"$ {_fmt_pt(f['q_orig'] * p_act)}" if f["q_orig"] * p_act else "",
                _fmt(f["q_ejec"]) if f["q_ejec"] else "",
                f"$ {_fmt_pt(f['pesos_ejec'])}" if f["pesos_ejec"] else "",
                _fmt(f["saldo"]) if abs(f["saldo"]) > 1e-6 else "0", ""))

    def _clic_tarea(self, event):
        """Clic en rubro / ítem / descripción de una tarea: despliega sus insumos."""
        if self.tbl.identify_region(event.x, event.y) != "cell":
            return
        iid = self.tbl.identify_row(event.y)
        if (not iid or "|" in iid
                or self.tbl.identify_column(event.x) not in ("#1", "#2", "#3")
                or not self.tbl.get_children(iid)):
            return
        abrir = not self.tbl.item(iid, "open")
        self.tbl.item(iid, open=abrir)
        if abrir:
            self._abiertos.add(iid)
        else:
            self._abiertos.discard(iid)

    # ── Acciones ─────────────────────────────────────────────────
    def _requiere_original(self) -> bool:
        if not self.ejec:
            messagebox.showinfo("Sin Original",
                "Primero definí el Original con «Definir Original…».", parent=self.v)
            return False
        return True

    def _definir_original(self):
        jsons = sorted(self.data.glob("obra???.json"))
        if not jsons:
            messagebox.showwarning("Sin versiones",
                "Guardá la obra al menos una vez antes de definir el Original.", parent=self.v)
            return
        if self.ejec:
            n = len(E.listar_etapas(self.data))
            msg = (f"Ya hay un Original definido ({self.ejec['original']['archivo']})"
                   + (f" y {n} etapa(s) cargadas" if n else "") + ".\n\n"
                   "Si lo redefinís se reinician los estados de todas las tareas"
                   + (" y las etapas existentes pueden dejar de coincidir con las tareas"
                      if n else "") + ".\n\n¿Continuar?")
            if not messagebox.askyesno("Redefinir Original", msg, icon="warning", parent=self.v):
                return
        dlg = _DlgElegirVersion(self.v, jsons, self.obra.version)
        self.v.wait_window(dlg)
        if not dlg.ruta:
            return
        self.ejec = E.definir_original(self.data, dlg.ruta, self.v.maestro["incidencias"],
                                       self.v.maestro.get("insumos"))
        falt = sum(1 for i in self.ejec["original"]["items"] if i["sin_precio"])
        self.refrescar()
        messagebox.showinfo("Original definido",
            f"Original: {dlg.ruta.name}\n{len(self.ejec['original']['items'])} tareas, "
            "todas en «A realizar»."
            + (f"\n\n⚠ {falt} tareas tienen insumos sin precio en esa versión." if falt else ""),
            parent=self.v)

    def _actualizar_precios_orig(self):
        """Pasa al Original los precios actuales de la obra (pestaña 3) sin tocar
        estados ni etapas: completa los que no tenían precio y, si se elige, cambia el resto."""
        if not self._requiere_original():
            return
        cambios = E.cambios_precios_original(self.ejec, self.v._precios or {},
                                             self.v.maestro["incidencias"],
                                             self.v.maestro.get("insumos"))
        if not cambios:
            messagebox.showinfo("Precios del Original",
                "Los precios del Original ya coinciden con los de la obra (pestaña 3).",
                parent=self.v)
            return
        falt = [c for c in cambios if not c["antes"]]
        dif = [c for c in cambios if c["antes"]]

        def lineas(lst, n=18):
            r = [f"  {c['cod_ins']:7} {c['nombre'][:34]:34} "
                 + (f"$ {_fmt(c['antes'])} → " if c["antes"] else "")
                 + f"$ {_fmt(c['nuevo'])}" for c in lst[:n]]
            return r + ([f"  … y {len(lst) - n} más"] if len(lst) > n else [])

        msg = ""
        if falt:
            msg += f"Sin precio en el Original ({len(falt)}):\n" + "\n".join(lineas(falt)) + "\n\n"
        if dif:
            msg += f"Con otro precio en el Original ({len(dif)}):\n" + "\n".join(lineas(dif)) + "\n\n"
        msg += ("Sí = actualizar todos\n"
                + ("No = solo completar los que no tenían precio\n" if falt else "")
                + "Cancelar = no cambiar nada\n\n"
                "No se tocan estados ni etapas. Las tareas con precio manual quedan igual.")
        if falt and dif:
            r = messagebox.askyesnocancel("Actualizar precios del Original", msg, parent=self.v)
            if r is None:
                return
            elegidos = cambios if r else falt
        else:
            msg = msg.replace("Sí = actualizar todos\n", "").replace("Cancelar = no cambiar nada\n\n", "")
            if not messagebox.askokcancel("Actualizar precios del Original", msg, parent=self.v):
                return
            elegidos = cambios
        t_antes = sum(i["cantidad"] * i["pu"] for i in self.ejec["original"]["items"])
        bak = E.actualizar_precios_original(self.data, self.ejec,
                                            {c["cod_ins"]: c["nuevo"] for c in elegidos},
                                            self.v.maestro["incidencias"],
                                            self.v.maestro.get("insumos"))
        t_desp = sum(i["cantidad"] * i["pu"] for i in self.ejec["original"]["items"])
        self.refrescar()
        messagebox.showinfo("Precios del Original",
            f"{len(elegidos)} precios actualizados.\n\n"
            f"Total Original: $ {_fmt_pt(t_antes)} → $ {_fmt_pt(t_desp)}\n\n"
            f"Copia previa: {bak.name}", parent=self.v)

    def _seleccion_claves(self):
        return [i for i in self.tbl.selection() if not i.startswith("rub|") and "|" not in i]

    def _marcar(self, est):
        if not self._requiere_original():
            return
        cl = self._seleccion_claves()
        if not cl:
            messagebox.showinfo("Sin selección",
                "Seleccioná una o más tareas (Ctrl/Shift + clic).", parent=self.v)
            return
        E.cambiar_estado(self.data, self.ejec, cl, est)
        self.refrescar()
        for c in cl:
            if self.tbl.exists(c):
                self.tbl.selection_add(c)

    def _menu_tarea(self, event):
        iid = self.tbl.identify_row(event.y)
        if not iid or iid.startswith("rub|") or "|" in iid:
            return
        if iid not in self.tbl.selection():
            self.tbl.selection_set(iid)
        m = tk.Menu(self.v, tearoff=0)
        for est in E.ESTADOS:
            m.add_command(label=f"Marcar como {E.ESTADO_TXT[est]}",
                          command=lambda e=est: self._marcar(e))
        m.tk_popup(event.x_root, event.y_root)

    def _precios_iniciales(self):
        """Precios del Original + precios actuales de la obra (pestaña 3)."""
        return {**(self.ejec["original"].get("precios") or {}), **(self.v._precios or {})}

    def _nueva_version(self):
        if not self._requiere_original():
            return
        precios = self._precios_iniciales()
        etapa = E.nueva_etapa(self.data, self.ejec, self.v.maestro["incidencias"],
                              precios, self.v._nombre_precios or "",
                              catalogo=self.v.maestro.get("insumos"))
        if not etapa["items"]:
            if not messagebox.askyesno("Sin tareas en curso",
                    "No hay tareas «En curso». ¿Abrir la etapa vacía igual y agregar "
                    "tareas a mano?", parent=self.v):
                return
        _DlgVersion(self, etapa, precios, nueva=True)

    def _version_sel(self):
        sel = self.tbl_v.selection()
        if not sel:
            messagebox.showinfo("Sin selección", "Seleccioná una etapa de la lista.",
                                parent=self.v)
            return None
        if "v" in sel[0]:                            # fila de una variante: "2v1"
            num, var = sel[0].split("v")
            ruta = E.ruta_variante(self.data, int(num), int(var))
        else:
            ruta = E.ruta_etapa(self.data, int(sel[0]))
        with open(ruta, encoding="utf-8") as f:
            return json.load(f)

    def _abrir_version(self):
        if not self._requiere_original():
            return
        et = self._version_sel()
        if et:
            # Los precios guardados en la etapa mandan; el resto (insumos de tareas
            # que se agreguen ahora) sale del Original y de la obra.
            precios = {**self._precios_iniciales(), **(et.get("precios") or {})}
            _DlgVersion(self, et, precios, nueva=False)

    def _exportar_version(self):
        et = self._version_sel()
        if not et:
            return
        ruta = filedialog.asksaveasfilename(
            parent=self.v, title="Exportar etapa",
            initialdir=str(self.obra.carpeta),
            initialfile=f"Obra{self.obra.numero}_{E.nombre_etapa(et).replace(' ', '_')}.xlsx",
            defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if ruta:
            try:
                E.exportar_etapa(Path(ruta), self.obra.titulo, et, self.ejec)
            except PermissionError:
                messagebox.showerror("Archivo en uso", "Cerralo en Excel y volvé a intentar.",
                                     parent=self.v)
                return
            messagebox.showinfo("Exportado", ruta, parent=self.v)

    def _eliminar_version(self):
        et = self._version_sel()
        if not et:
            return
        if et.get("variante"):
            if messagebox.askyesno("Eliminar variante",
                    f"¿Eliminar {E.nombre_etapa(et)}?\n\nLa etapa real no cambia. "
                    "No se puede deshacer.", icon="warning", parent=self.v):
                E.eliminar_variante(self.data, et["numero"], et["variante"])
                self.refrescar()
            return
        if E.listar_variantes(self.data, et["numero"]):
            messagebox.showinfo("Etapa con variantes",
                f"La Etapa {et['numero']:02d} tiene variantes. Eliminalas primero.",
                parent=self.v)
            return
        if not messagebox.askyesno("Eliminar etapa",
                f"¿Eliminar la Etapa {et['numero']:02d}?\n\nLas tareas que esa etapa "
                "daba por finalizadas vuelven a «En curso». No se puede deshacer.",
                icon="warning", parent=self.v):
            return
        E.eliminar_etapa(self.data, self.ejec, et["numero"])
        self.refrescar()

    def _cierre(self):
        if not self._requiere_original():
            return
        _DlgCierre(self)


# ═════════════════════════════════════════════════════════════════
class _DlgElegirVersion(tk.Toplevel):
    def __init__(self, parent, jsons, version_actual):
        super().__init__(parent)
        self.title("Definir Original")
        self.geometry("560x340")
        self.grab_set()
        self.ruta = None
        tk.Label(self, text="  Elegí la versión contratada (queda como Original de la obra)",
                 bg=COLOR_HDR, fg="white", font=FUENTE_B, anchor="w", pady=8).pack(fill="x")
        tk.Label(self, text="  Se toma lo guardado en el archivo: si hiciste cambios, primero "
                            "«Guardar obra».", bg=COLOR_BG, fg="#555", font=FUENTE_S,
                 anchor="w").pack(fill="x")
        notas = {}
        var = parent.obra.carpeta_data / "variaciones.txt"
        if var.exists():
            for l in var.read_text(encoding="utf-8").splitlines():
                p = l.split("  —  ")
                if len(p) >= 3:
                    notas[p[0].strip()] = p[-1].strip()
        cols = ("archivo", "fecha", "nota")
        self.tbl = ttk.Treeview(self, columns=cols, show="headings", selectmode="browse")
        for c, t, w in (("archivo", "Archivo", 110), ("fecha", "Fecha", 110), ("nota", "Nota", 300)):
            self.tbl.heading(c, text=t)
            self.tbl.column(c, width=w)
        for j in jsons:
            try:
                d = json.loads(j.read_text(encoding="utf-8"))
            except Exception:
                d = {}
            self.tbl.insert("", "end", iid=str(j),
                            values=(j.name, d.get("fecha_creacion", ""), notas.get(j.name, "")))
            if d.get("version") == version_actual:
                self.tbl.selection_set(str(j))
        self.tbl.pack(fill="both", expand=True, padx=8, pady=6)
        self.tbl.bind("<Double-1>", lambda _: self._ok())
        bot = tk.Frame(self, bg=COLOR_BG, pady=6)
        bot.pack(fill="x")
        _btn(bot, "Cancelar", "#888", self.destroy).pack(side="right", padx=8)
        _btn(bot, "Usar como Original", COLOR_VERDE, self._ok, True).pack(side="right")
        _centrar(self, parent)

    def _ok(self):
        sel = self.tbl.selection()
        if sel:
            self.ruta = Path(sel[0])
            self.destroy()


# ═════════════════════════════════════════════════════════════════
class _DlgVersion(tk.Toplevel):
    """Crear o editar una Etapa XX."""

    def __init__(self, tab: TabEjecucion, etapa: dict, precios: dict, nueva: bool):
        super().__init__(tab.v)
        self.tab, self.v = tab, tab.v
        self.etapa, self.precios, self.nueva = etapa, precios, nueva
        self.inc = self.v.maestro["incidencias"]
        self.orig = E.registro(tab.ejec)   # Original + adicionales ya registradas
        for i in etapa["items"]:            # adicionales nuevas de esta etapa
            if i.get("adicional") and i["clave"] not in self.orig:
                self.orig[i["clave"]] = E.nuevo_adicional(
                    i["clave"], i["descripcion"], i["unidad"], i["rubro"], i["cod_tar"],
                    i.get("pu_manual"))
        self.cat = self.v.maestro.get("insumos") or {}
        for i in etapa["items"]:            # etapas guardadas sin lista de insumos
            E.asegurar_insumos(i, self.orig.get(i["clave"], i), self.inc, self.precios,
                               self.cat)
        self._abiertos = set()              # tareas desplegadas
        self.acc_prev = E.acumulado(tab.data, excluir=etapa["numero"])
        self.title(E.nombre_etapa(etapa))
        self.geometry("1150x620")
        self.minsize(900, 420)
        self.grab_set()
        self._build()
        self._poblar()
        _centrar(self, self.v)

    def _build(self):
        hdr = tk.Frame(self, bg=COLOR_HDR)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"  {E.nombre_etapa(self.etapa)}"
                           + ("  (nueva)" if self.nueva else "")
                           + ("  (alternativa: no suma al ejecutado)"
                              if self.etapa.get("variante") else ""),
                 bg=COLOR_HDR, fg="white", font=("Segoe UI", 12, "bold"), pady=6
                 ).pack(side="left", padx=6)

        top = tk.Frame(self, bg=COLOR_BG, pady=4)
        top.pack(fill="x", padx=8)
        tk.Label(top, text="Nombre:", bg=COLOR_BG, font=FUENTE_S).pack(side="left")
        self.var_nom = tk.StringVar(value=self.etapa.get("nombre", ""))
        ttk.Entry(top, textvariable=self.var_nom, width=30).pack(side="left", padx=(2, 10))
        tk.Label(top, text="Fecha:", bg=COLOR_BG, font=FUENTE_S).pack(side="left")
        self.var_fecha = tk.StringVar(value=self.etapa.get("fecha", ""))
        ttk.Entry(top, textvariable=self.var_fecha, width=11).pack(side="left", padx=(2, 10))
        tk.Label(top, text="Precios:", bg=COLOR_BG, font=FUENTE_S).pack(side="left")
        self.var_prc = tk.StringVar(value=self.etapa.get("archivo_precios") or "(los de la obra)")
        tk.Label(top, textvariable=self.var_prc, bg=COLOR_BG, fg=COLOR_HDR,
                 font=FUENTE_B).pack(side="left", padx=2)
        _btn(top, "Cargar archivo de precios…", COLOR_SEC, self._elegir_precios
             ).pack(side="left", padx=6)
        _btn(top, "Exportar Excel", COLOR_VERDE, self._exportar, True
             ).pack(side="right", padx=4)

        ayuda = ("Tareas: doble clic en «Cantidad» o «P. Unit.» para editar  ·  clic en «Finaliza» "
                 "para darla por terminada  ·  P. Unit. vacío = se calcula con los insumos\n"
                 "Insumos: clic en la descripción (o en ▸) para desplegarlos  ·  doble clic en "
                 "«Incid.» (por unidad de tarea), «Cantidad» (total de la etapa) o «P. Unit.» "
                 "para cambiarlos  ·  clic derecho = agregar / quitar / restaurar  ·  "
                 "en azul = modificado")
        tk.Label(self, text=ayuda, bg=COLOR_BG, fg="#555", font=FUENTE_S, anchor="w",
                 justify="left").pack(fill="x", padx=10)

        bot = tk.Frame(self, bg="#e0e0e0", pady=6)
        bot.pack(side="bottom", fill="x")
        _btn(bot, "Cancelar", "#888", self.destroy).pack(side="right", padx=(4, 10))
        _btn(bot, f"Guardar {E.nombre_etapa(self.etapa)}", COLOR_VERDE, self._guardar,
             True).pack(side="right", padx=4)
        if not self.nueva:
            _btn(bot, "Guardar como nueva Variante", "#1f5fbf", self._guardar_como_variante,
                 True).pack(side="right", padx=4)
        _btn(bot, "+ Agregar tarea", COLOR_SEC, self._agregar).pack(side="left", padx=(10, 4))
        _btn(bot, "+ Adicional (no prevista)", COLOR_SEC_AD, self._adicional
             ).pack(side="left", padx=4)
        _btn(bot, "Quitar tarea", COLOR_ROJO, self._quitar).pack(side="left", padx=4)
        _btn(bot, "+ Insumo a la tarea", "#1f5fbf", self._agregar_insumo
             ).pack(side="left", padx=(16, 4))
        self.lbl_tot = tk.Label(bot, text="", bg="#e0e0e0", fg=COLOR_HDR, font=FUENTE_B)
        self.lbl_tot.pack(side="right", padx=16)

        cols = ("rubro", "item", "desc", "unidad", "orig", "previo", "cant", "pu", "total", "fin")
        txt = {"rubro": "Rubro", "item": "Ítem", "desc": "Descripción", "unidad": "Unidad",
               "orig": "Cant. Orig. / Incid.", "previo": "Ejec. otras etapas",
               "cant": "Cantidad", "pu": "P. Unit.", "total": "Total", "fin": "Finaliza"}
        anch = {"rubro": 42, "item": 40, "desc": 300, "unidad": 50, "orig": 110,
                "previo": 90, "cant": 85, "pu": 110, "total": 115, "fin": 60}
        fr = tk.Frame(self, bg=COLOR_BG)
        fr.pack(fill="both", expand=True, padx=8, pady=4)
        self.tbl = ttk.Treeview(fr, columns=cols, show="tree headings", selectmode="extended")
        self.tbl.column("#0", width=22, minwidth=22, stretch=False)
        for c in cols:
            self.tbl.heading(c, text=txt[c])
            self.tbl.column(c, width=anch[c], minwidth=24,
                            anchor="w" if c == "desc" else
                            ("center" if c in ("rubro", "item", "unidad", "fin") else "e"))
        scr = ttk.Scrollbar(fr, orient="vertical", command=self.tbl.yview)
        self.tbl.configure(yscrollcommand=scr.set)
        scr.pack(side="right", fill="y")
        self.tbl.pack(fill="both", expand=True)
        self.tbl.tag_configure("ok", background="#ffffff")
        self.tbl.tag_configure("sinprecio", background="#fff3cd")
        self.tbl.tag_configure("manual", background="#e8f0f8")
        self.tbl.tag_configure("adic", foreground=COLOR_ADIC)
        self.tbl.tag_configure("sec_adic", background=COLOR_SEC_AD, foreground="white",
                               font=FUENTE_B)
        self.tbl.tag_configure("ins", background="#f7f7f7", foreground="#444",
                               font=FUENTE_S)
        self.tbl.tag_configure("ins_sinp", background="#fff3cd", foreground="#444",
                               font=FUENTE_S)
        self.tbl.tag_configure("ins_mod", foreground="#1f5fbf",
                               font=("Segoe UI", 9, "bold"))
        self.tbl.tag_configure("ins_off", foreground="#aaaaaa")
        self.tbl.bind("<Double-1>", self._doble_clic)
        self.tbl.bind("<ButtonRelease-1>", self._clic)
        self.tbl.bind("<Button-3>", self._menu)
        self.tbl.bind("<<TreeviewOpen>>", lambda _: self._abiertos.add(self.tbl.focus()))
        self.tbl.bind("<<TreeviewClose>>",
                      lambda _: self._abiertos.discard(self.tbl.focus()))

    def _poblar(self):
        self.tbl.delete(*self.tbl.get_children())
        orden = {c: n for n, c in enumerate(self.orig)}
        self.etapa["items"].sort(key=lambda i: (
            E.es_adicional(i["clave"]),
            i["rubro"] if E.es_adicional(i["clave"]) else "",
            orden.get(i["clave"], 1e9), i["clave"]))
        total = 0.0
        hay_sec = False
        for i in self.etapa["items"]:
            if E.es_adicional(i["clave"]) and not hay_sec:
                hay_sec = True
                self.tbl.insert("", "end", iid="sec|ADIC", tags=("sec_adic",), values=(
                    "", "", "ADICIONALES (no previstas en el Original)", "", "", "", "", "",
                    "", ""))
            t = i["cantidad"] * i["pu"]
            total += t
            o = self.orig.get(i["clave"], {})
            prev = self.acc_prev.get(i["clave"], {}).get("cantidad", 0.0)
            tag = "manual" if i.get("pu_manual") else ("sinprecio" if i.get("sin_precio") or
                                                        not i["pu"] else "ok")
            tags = (tag, "adic") if E.es_adicional(i["clave"]) else (tag,)
            n_mod = sum(1 for x in i.get("insumos") or []
                        if x.get("mod_incid") or x.get("mod_precio") or x.get("agregado"))
            desc = i["descripcion"] + (f"   [{n_mod} insumo(s) modificado(s)]" if n_mod else "")
            if E.variante_cambiada(i, o or i):
                sub = i.get("subcontrato") or ""
                desc += f"   [{sub or 'Propio'}: {E.VARIANTE_TXT.get(sub, '')}]"
            if i.get("solo_insumos"):
                desc = (i["descripcion"] + f"   [solo insumos pendientes · no suma "
                        f"{i['unidad']}]")
            self.tbl.insert("", "end", iid=i["clave"], tags=tags,
                            open=i["clave"] in self._abiertos, values=(
                i["rubro"], i["item"], desc, i["unidad"],
                "—" if E.es_adicional(i["clave"]) else _fmt(o.get("cantidad", 0.0)),
                _fmt(prev) if prev else "",
                _fmt(i["cantidad"]) + (" ref." if i.get("solo_insumos") else ""),
                f"$ {_fmt(i['pu'])}" if i["pu"] else "sin precio",
                f"$ {_fmt_pt(t)}", "✔" if i.get("finaliza") else ""))
            for n, x in enumerate(i.get("insumos") or []):
                q = x["incid"] * i["cantidad"]
                tg = ["ins_sinp" if not x["precio"] else "ins"]
                if x.get("mod_incid") or x.get("mod_precio") or x.get("agregado"):
                    tg.append("ins_mod")
                if i.get("pu_manual"):
                    tg.append("ins_off")          # con PU manual los insumos no cuentan
                precio = (f"$ {_fmt(x['precio'])}" + (" *" if x.get("mod_precio") else "")
                          if x["precio"] else "sin precio")
                self.tbl.insert(i["clave"], "end", iid=f"{i['clave']}|{n}", tags=tuple(tg),
                                values=(
                    "", x["cod_ins"], ("  + " if x.get("agregado") else "    ")
                    + (x.get("nombre") or x["cod_ins"])
                    + ("   (agregado en la etapa)" if x.get("agregado") else ""), x["unidad"],
                    _fmt(x["incid"], 4) + (" *" if x.get("mod_incid") else ""), "",
                    _fmt(q), precio, f"$ {_fmt_pt(q * x['precio'])}", ""))
        falt = sum(1 for i in self.etapa["items"] if i.get("sin_precio"))
        t_ad = sum(i["cantidad"] * i["pu"] for i in self.etapa["items"]
                   if E.es_adicional(i["clave"]))
        self.lbl_tot.config(text=(f"⚠ {falt} con insumos sin precio    " if falt else "")
                                 + (f"Adicionales: $ {_fmt_pt(t_ad)}    " if t_ad else "")
                                 + f"Total etapa: $ {_fmt_pt(total)}")

    def _item(self, clave):
        return next((i for i in self.etapa["items"] if i["clave"] == clave), None)

    def _insumo(self, iid):
        """iid de una fila de insumo ('clave|n') → (tarea, insumo), o (None, None)."""
        if not iid or "|" not in iid or iid.startswith("sec|"):
            return None, None
        clave, n = iid.rsplit("|", 1)
        i = self._item(clave)
        if i is None or not n.isdigit() or int(n) >= len(i.get("insumos") or []):
            return None, None
        return i, i["insumos"][int(n)]

    def _recalcular(self, i):
        E.recalcular_item(i, self.orig.get(i["clave"], i))

    def _refrescar(self, iid):
        self._poblar()
        if self.tbl.exists(iid):
            self.tbl.selection_set(iid)
            self.tbl.see(iid)

    def _pedir_num(self, titulo, texto, valor, dec=2):
        s = simpledialog.askstring(titulo, texto, parent=self,
                                   initialvalue=_fmt(valor, dec).replace(".", "")
                                   if valor is not None else "")
        if s is None:
            return None
        try:
            return _parse_num(s) or 0.0
        except ValueError:
            messagebox.showerror("Valor inválido", s, parent=self)
            return None

    def _clic(self, event):
        if self.tbl.identify_region(event.x, event.y) != "cell":
            return                                  # la flecha ▸ la maneja el Treeview
        iid = self.tbl.identify_row(event.y)
        col = self.tbl.identify_column(event.x)
        i = self._item(iid)
        if not i:
            return
        if col == "#10":
            i["finaliza"] = not i.get("finaliza")
            self._refrescar(iid)
        elif col in ("#1", "#2", "#3") and i.get("insumos"):
            abrir = not self.tbl.item(iid, "open")
            self.tbl.item(iid, open=abrir)
            if abrir:
                self._abiertos.add(iid)
            else:
                self._abiertos.discard(iid)

    def _doble_clic(self, event):
        iid = self.tbl.identify_row(event.y)
        col = self.tbl.identify_column(event.x)
        ti, x = self._insumo(iid)
        if x is not None:
            self._editar_insumo(iid, col, ti, x)
            return
        i = self._item(iid)
        if not i:
            return
        if col == "#7" and i.get("solo_insumos"):
            messagebox.showinfo(
                "Solo insumos", "Esta fila completa los insumos que faltaban y no suma "
                f"{i['unidad']} a la tarea ({_fmt(i['cantidad'])} es solo la referencia).\n\n"
                "Desplegala y cambiá la cantidad de cada insumo. Con clic derecho sobre la "
                "tarea podés hacer que sume cantidad.", parent=self)
            return
        if col == "#7":
            q = self._pedir_num("Cantidad", f"{i['descripcion']}\n\nCantidad en esta "
                                f"etapa ({i['unidad']}):", i["cantidad"])
            if q is None:
                return
            i["cantidad"] = q
        elif col == "#8":
            s = simpledialog.askstring("Precio unitario",
                                       f"{i['descripcion']}\n\nPrecio unitario manual "
                                       "(vacío = calcular con los insumos):",
                                       initialvalue=_fmt(i["pu_manual"]).replace(".", "")
                                       if i.get("pu_manual") else "", parent=self)
            if s is None:
                return
            try:
                p = _parse_num(s)
            except ValueError:
                messagebox.showerror("Valor inválido", s, parent=self)
                return
            i["pu_manual"] = p if p else None
            self._recalcular(i)
        else:
            return
        self._refrescar(iid)

    def _editar_insumo(self, iid, col, i, x):
        nom = f"{i['descripcion']}\n\nInsumo {x['cod_ins']}  {x.get('nombre', '')}"
        if col == "#5":                                    # incidencia por unidad
            v = self._pedir_num("Incidencia", f"{nom}\n\nCantidad de {x['unidad']} por "
                                f"{i['unidad']} de tarea (análisis: "
                                f"{_fmt(x['incid_base'], 4)}):", x["incid"], 4)
            if v is None:
                return
            x["incid"] = v
        elif col == "#7":                                  # cantidad total de la etapa
            if not i["cantidad"]:
                messagebox.showinfo("Sin cantidad", "La tarea tiene cantidad 0 en esta etapa: "
                                    "cargá primero la cantidad de la tarea, o cambiá la "
                                    "incidencia por unidad.", parent=self)
                return
            v = self._pedir_num("Cantidad del insumo", f"{nom}\n\nCantidad total en esta "
                                f"etapa ({x['unidad']}), para {_fmt(i['cantidad'])} "
                                f"{i['unidad']} de tarea:", x["incid"] * i["cantidad"])
            if v is None:
                return
            x["incid"] = v / i["cantidad"]
        elif col == "#8":                                  # precio del insumo
            v = self._pedir_num("Precio del insumo", f"{nom}\n\nPrecio por {x['unidad']} "
                                f"(archivo de precios: $ {_fmt(x['precio_base'])}):",
                                x["precio"])
            if v is None:
                return
            otras = [(t, y) for t in self.etapa["items"] if t is not i
                     for y in t.get("insumos") or [] if y["cod_ins"] == x["cod_ins"]]
            if otras and messagebox.askyesno(
                    "Precio del insumo",
                    f"Hay {len(otras)} tarea(s) más en esta etapa que usan este insumo.\n\n"
                    "¿Aplicar el mismo precio a todas?\n(No = solo a esta tarea)", parent=self):
                for t, y in otras:
                    y["precio"] = v
                    y["mod_precio"] = abs(v - y["precio_base"]) > 1e-9
                    self._recalcular(t)
            x["precio"] = v
        else:
            return
        x["mod_incid"] = abs(x["incid"] - x["incid_base"]) > 1e-9
        x["mod_precio"] = abs(x["precio"] - x["precio_base"]) > 1e-9
        if i.get("pu_manual"):
            i["pu_manual"] = None          # al tocar insumos, el PU vuelve a salir de ellos
        self._recalcular(i)
        self._refrescar(iid)

    def _menu(self, event):
        iid = self.tbl.identify_row(event.y)
        if not iid:
            return
        self.tbl.selection_set(iid)
        i, x = self._insumo(iid)
        m = tk.Menu(self, tearoff=0)
        if x is not None:
            clave = iid.rsplit("|", 1)[0]
            m.add_command(label="Agregar insumo a esta tarea…",
                          command=lambda: self._agregar_insumo(i))
            m.add_separator()
            if x.get("agregado"):
                m.add_command(label="Quitar este insumo (agregado en la etapa)",
                              command=lambda: self._quitar_insumo(i, x, clave))
            else:
                m.add_command(label="Quitar este insumo (incidencia 0)",
                              command=lambda: self._quitar_insumo(i, x, clave))

                def rest():
                    E.restaurar_insumo(x)
                    self._recalcular(i)
                    self._refrescar(iid)
                m.add_command(label="Restaurar valores del análisis y del archivo de precios",
                              command=rest)
        else:
            i = self._item(iid)
            if not i:
                return
            m.add_command(label="Agregar insumo a esta tarea…",
                          command=lambda: self._agregar_insumo(i))

            def alternar_solo():
                i["solo_insumos"] = not i.get("solo_insumos")
                self._refrescar(iid)
            m.add_command(label=("Que sume cantidad a la tarea" if i.get("solo_insumos")
                                 else "Solo insumos (que no sume cantidad a la tarea)"),
                          command=alternar_solo)
            if i.get("insumos"):
                def rest_todo():
                    i["insumos"] = [y for y in i["insumos"] if not y.get("agregado")]
                    for y in i["insumos"]:
                        E.restaurar_insumo(y)
                    self._recalcular(i)
                    self._refrescar(iid)
                m.add_command(label="Restaurar todos los insumos de la tarea "
                                    "(saca los agregados)", command=rest_todo)
            if not self.nueva and not i.get("solo_insumos") and i.get("cod_tar"):
                actual = (i.get("subcontrato") or "").strip().upper()
                opciones = [v for v in E.variantes_tarea(i["cod_tar"], self.inc) if v != actual]
                if opciones:
                    m.add_separator()
                for v in opciones:
                    m.add_command(label=f"Cambiar a {v or 'Propio'}  ({E.VARIANTE_TXT[v]})",
                                  command=lambda var=v: self._cambiar_variante(i, var))
        m.tk_popup(event.x_root, event.y_root)

    def _cambiar_variante(self, i, variante):
        """Reemplaza los insumos de la tarea por los de la variante elegida."""
        if (i.get("pu_manual") or any(x.get("mod_incid") or x.get("agregado")
                                      for x in i.get("insumos") or [])) and \
                not messagebox.askokcancel("Cambiar variante",
                    "Esta tarea tiene un PU manual, incidencias modificadas o insumos "
                    "agregados, que se pierden al cambiar de variante.\n\n"
                    "Los precios cambiados a mano se conservan en los insumos que sigan.",
                    parent=self):
            return
        E.cambiar_variante(i, self.orig.get(i["clave"], i), variante, self.inc, self.precios,
                           self.cat)
        self._abiertos.add(i["clave"])
        self._refrescar(i["clave"])

    def _tarea_seleccionada(self):
        for iid in self.tbl.selection():
            i, x = self._insumo(iid)
            if i is None:
                i = self._item(iid)
            if i is not None:
                return i
        return None

    def _agregar_insumo(self, i=None):
        i = i or self._tarea_seleccionada()
        if i is None:
            messagebox.showinfo("Agregar insumo", "Seleccioná primero la tarea (o uno de sus "
                                "insumos).", parent=self)
            return
        dlg = _DlgInsumo(self, i, self.cat, self.precios,
                         {x["cod_ins"] for x in i.get("insumos") or []})
        self.wait_window(dlg)
        r = dlg.resultado
        if not r:
            return
        if i.get("pu_manual"):
            i["pu_manual"] = None          # el PU vuelve a salir de los insumos
        i.setdefault("insumos", []).append(
            E.nuevo_insumo(r["cod_ins"], self.cat, self.precios, r["incid"], r["precio"]))
        self._recalcular(i)
        self._abiertos.add(i["clave"])
        self._refrescar(f"{i['clave']}|{len(i['insumos']) - 1}")

    def _quitar_insumo(self, i, x, clave):
        if x.get("agregado"):
            i["insumos"].remove(x)
        else:                              # del análisis: queda con incidencia 0 (restaurable)
            x["incid"] = 0.0
            x["mod_incid"] = abs(x["incid_base"]) > 1e-9
        self._recalcular(i)
        self._refrescar(clave)

    def _elegir_precios(self):
        ini = self.v.obra.carpeta_precios
        ruta = filedialog.askopenfilename(parent=self, title="Archivo de precios de esta etapa",
                                          initialdir=str(ini) if ini.exists() else None,
                                          filetypes=[("Excel", "*.xlsx *.XLSX")])
        if not ruta:
            return
        try:
            nuevos = cargar_precios(ruta)
        except Exception as e:
            messagebox.showerror("Error al leer precios", str(e), parent=self)
            return
        # Los insumos que no están en el archivo nuevo conservan el precio anterior.
        # Los precios cambiados a mano en la etapa se respetan.
        self.precios = {**self.precios, **nuevos}
        self.etapa["archivo_precios"] = Path(ruta).name
        self.var_prc.set(Path(ruta).name)
        for i in self.etapa["items"]:
            E.aplicar_precios(i, self.precios)
            self._recalcular(i)
        self._poblar()

    def _agregar(self):
        presentes = {i["clave"] for i in self.etapa["items"]}
        cand = [o for c, o in self.orig.items() if c not in presentes]
        if not cand:
            messagebox.showinfo("Agregar tarea", "Ya están todas las tareas.", parent=self)
            return
        dlg = _DlgAgregar(self, cand, self.tab.ejec)
        self.wait_window(dlg)
        for c in dlg.claves:
            # Cantidad propuesta = saldo de la tarea (Original − otras etapas), como en
            # «+ Nueva Etapa». Las adicionales (sin cantidad en el Original) quedan en 0.
            o = self.orig[c]
            saldo = max((o.get("cantidad") or 0.0)
                        - self.acc_prev.get(c, {}).get("cantidad", 0.0), 0.0)
            self.etapa["items"].append(
                E.item_etapa(o, saldo, self.inc, self.precios, catalogo=self.cat))
        if dlg.claves:
            self._poblar()

    def _adicional(self):
        claves = [i["clave"] for i in self.etapa["items"]] + list(self.orig)
        rubros = self.tab.ejec["original"].get("rubros", {})
        dlg = _DlgAdicional(self, self.v.maestro, rubros,
                            E.nueva_clave_adicional(self.tab.ejec, claves))
        self.wait_window(dlg)
        a = dlg.resultado
        if not a:
            return
        ficha = E.nuevo_adicional(a["clave"], a["descripcion"], a["unidad"], a["rubro"],
                                  a["cod_tar"], a["pu_manual"])
        self.orig[a["clave"]] = ficha
        it = E.item_etapa(ficha, a["cantidad"], self.inc, self.precios,
                          pu_manual=a["pu_manual"], catalogo=self.cat)
        self.etapa["items"].append(it)
        self._poblar()
        self.tbl.selection_set(a["clave"])
        self.tbl.see(a["clave"])

    def _quitar(self):
        sel = {x for x in self.tbl.selection() if not x.startswith("sec|") and "|" not in x}
        if sel:
            self.etapa["items"] = [i for i in self.etapa["items"] if i["clave"] not in sel]
            self._poblar()

    def _exportar(self):
        """Exporta la etapa tal como está en pantalla (aunque no esté guardada)."""
        obra = self.v.obra
        et = {**self.etapa, "nombre": self.var_nom.get().strip(),
              "fecha": self.var_fecha.get().strip()}
        nom = f"_{et['nombre']}" if et["nombre"] else ""
        nom = "".join(c for c in nom if c not in '\\/:*?"<>|')
        ruta = filedialog.asksaveasfilename(
            parent=self, title="Exportar etapa", initialdir=str(obra.carpeta),
            initialfile=f"Obra{obra.numero}_{E.nombre_etapa(et).replace(' ', '_')}{nom}.xlsx",
            defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if not ruta:
            return
        try:
            E.exportar_etapa(Path(ruta), obra.titulo, et, self.tab.ejec)
        except PermissionError:
            messagebox.showerror("Archivo en uso", "Cerralo en Excel y volvé a intentar.",
                                 parent=self)
            return
        if messagebox.askyesno("Exportado", f"{ruta}\n\n¿Abrirlo ahora?", parent=self):
            import os
            os.startfile(ruta)

    def _preparar_guardado(self) -> bool:
        self.etapa["nombre"] = self.var_nom.get().strip()
        self.etapa["fecha"] = self.var_fecha.get().strip()
        if self.etapa.get("archivo_precios") == "(los de la obra)":
            self.etapa["archivo_precios"] = ""
        self.etapa["precios"] = E.precios_usados(self.etapa["items"], self.inc, self.precios)
        falt = sum(1 for i in self.etapa["items"] if i.get("sin_precio"))
        return not falt or messagebox.askyesno("Insumos sin precio",
                f"{falt} tareas tienen insumos sin precio (fila amarilla). ¿Guardar igual?",
                parent=self)

    def _guardar_como_variante(self):
        if not self._preparar_guardado():
            return
        n = E.guardar_variante(self.tab.data, self.etapa)
        self.tab.refrescar()
        messagebox.showinfo("Variante guardada",
            f"{E.nombre_etapa({**self.etapa, 'variante': n})}\n"
            f"Total: $ {_fmt_pt(sum(i['cantidad'] * i['pu'] for i in self.etapa['items']))}\n\n"
            "No suma al ejecutado ni cambia la etapa real.", parent=self.v)
        self.destroy()

    def _guardar(self):
        if self.etapa.get("variante"):
            if self._preparar_guardado():
                E.guardar_variante(self.tab.data, self.etapa, self.etapa["variante"])
                self.tab.refrescar()
                self.destroy()
            return
        if any(E.variante_cambiada(i, self.orig.get(i["clave"], i)) for i in self.etapa["items"]):
            messagebox.showinfo("Etapa con variantes",
                "Hay tareas cambiadas a otra variante. Usá «Guardar como nueva Variante» "
                "para no modificar la etapa real.", parent=self)
            return
        if not self._preparar_guardado():
            return
        ejec = self.tab.ejec
        # Las tareas agregadas a mano que estaban 'a realizar' pasan a 'en curso'.
        for i in self.etapa["items"]:
            if E.estado(ejec, i["clave"]) == "a_realizar":
                ejec["estados"][i["clave"]] = "en_curso"
        E.guardar_etapa(self.tab.data, ejec, self.etapa)
        self.tab.refrescar()
        self.destroy()


class _DlgInsumo(tk.Toplevel):
    """Elegir un insumo del catálogo de la obra para agregarlo a una tarea de la etapa."""

    def __init__(self, parent, tarea: dict, catalogo: dict, precios: dict, ya: set):
        super().__init__(parent)
        self.title("Agregar insumo a la tarea")
        self.geometry("820x560")
        self.minsize(700, 440)
        self.grab_set()
        self.resultado = None
        self.tarea, self.precios = tarea, precios
        self.items = sorted((c for c in catalogo.values() if c["cod"] not in ya),
                            key=lambda c: c["nombre"].lower())
        self.cod_sel = ""

        tk.Label(self, text=f"  {tarea['item']}  {tarea['descripcion']}  —  "
                            f"{_fmt(tarea['cantidad'])} {tarea['unidad']} en esta etapa",
                 bg="#1f5fbf", fg="white", font=FUENTE_B, anchor="w", pady=8).pack(fill="x")
        bus = tk.Frame(self, bg=COLOR_BG, pady=4)
        bus.pack(fill="x", padx=8)
        tk.Label(bus, text="Buscar insumo (código o nombre):", bg=COLOR_BG,
                 font=FUENTE_S).pack(side="left")
        self.var_bus = tk.StringVar()
        e = ttk.Entry(bus, textvariable=self.var_bus, width=40)
        e.pack(side="left", padx=4)
        e.focus_set()
        self.var_bus.trace_add("write", lambda *_: self._filtrar())

        fr = tk.Frame(self)
        fr.pack(fill="both", expand=True, padx=8)
        self.tbl = ttk.Treeview(fr, columns=("cod", "nombre", "unidad", "precio"),
                                show="headings", selectmode="browse", height=12)
        for c, t, w, a in (("cod", "Código", 80, "center"), ("nombre", "Insumo", 450, "w"),
                           ("unidad", "Unidad", 60, "center"), ("precio", "Precio", 110, "e")):
            self.tbl.heading(c, text=t)
            self.tbl.column(c, width=w, anchor=a)
        scr = ttk.Scrollbar(fr, orient="vertical", command=self.tbl.yview)
        self.tbl.configure(yscrollcommand=scr.set)
        scr.pack(side="right", fill="y")
        self.tbl.pack(fill="both", expand=True)
        self.tbl.bind("<<TreeviewSelect>>", self._elegir)

        frm = tk.Frame(self, bg=COLOR_BG, pady=6)
        frm.pack(fill="x", padx=8)
        self.var_sel = tk.StringVar(value="(elegí un insumo de la lista)")
        self.var_inc = tk.StringVar()
        self.var_tot = tk.StringVar()
        self.var_pre = tk.StringVar()
        filas = (("Insumo:", tk.Label(frm, textvariable=self.var_sel, bg=COLOR_BG,
                                      fg="#1f5fbf", font=FUENTE_B, anchor="w")),
                 (f"Incidencia (por {tarea['unidad']} de tarea):",
                  ttk.Entry(frm, textvariable=self.var_inc, width=14)),
                 ("  o Cantidad total en la etapa:",
                  ttk.Entry(frm, textvariable=self.var_tot, width=14)),
                 ("Precio:", ttk.Entry(frm, textvariable=self.var_pre, width=14)))
        for r, (lbl, w) in enumerate(filas):
            tk.Label(frm, text=lbl, bg=COLOR_BG, font=FUENTE_S, anchor="e"
                     ).grid(row=r, column=0, sticky="e", padx=(0, 6), pady=1)
            w.grid(row=r, column=1, sticky="w", pady=1)
        tk.Label(frm, text="(completá la incidencia o la cantidad total; el precio sale del "
                           "archivo y se puede cambiar)", bg=COLOR_BG, fg="#666",
                 font=FUENTE_S).grid(row=2, column=2, sticky="w", padx=6)

        bot = tk.Frame(self, bg="#e0e0e0", pady=6)
        bot.pack(side="bottom", fill="x")
        _btn(bot, "Cancelar", "#888", self.destroy).pack(side="right", padx=(4, 10))
        _btn(bot, "Agregar insumo", "#1f5fbf", self._ok, True).pack(side="right")
        self._filtrar()
        _centrar(self, parent)

    def _filtrar(self):
        txt = self.var_bus.get().strip().lower()
        self.tbl.delete(*self.tbl.get_children())
        n = 0
        for c in self.items:
            if txt and txt not in c["cod"].lower() and txt not in c["nombre"].lower():
                continue
            p = self.precios.get(c["cod"])
            self.tbl.insert("", "end", iid=c["cod"], values=(
                c["cod"], c["nombre"], c["unidad"], f"$ {_fmt(p)}" if p else "sin precio"))
            n += 1
            if n >= 500:                   # con la búsqueda se acota
                break

    def _elegir(self, _=None):
        sel = self.tbl.selection()
        if not sel:
            return
        c = next(x for x in self.items if x["cod"] == sel[0])
        self.cod_sel = c["cod"]
        self.var_sel.set(f"{c['cod']}  {c['nombre']}  ({c['unidad']})")
        p = self.precios.get(c["cod"])
        self.var_pre.set(_fmt(p).replace(".", "") if p else "")

    def _ok(self):
        if not self.cod_sel:
            messagebox.showwarning("Falta insumo", "Elegí un insumo de la lista.", parent=self)
            return
        try:
            inc = _parse_num(self.var_inc.get())
            tot = _parse_num(self.var_tot.get())
            pre = _parse_num(self.var_pre.get())
        except ValueError:
            messagebox.showerror("Valor inválido", "Revisá los números.", parent=self)
            return
        if inc is None and tot is not None:
            if not self.tarea["cantidad"]:
                messagebox.showwarning("Sin cantidad", "La tarea tiene cantidad 0: cargá la "
                                       "incidencia por unidad.", parent=self)
                return
            inc = tot / self.tarea["cantidad"]
        if not inc:
            messagebox.showwarning("Falta cantidad",
                                   "Completá la incidencia o la cantidad total.", parent=self)
            return
        self.resultado = {"cod_ins": self.cod_sel, "incid": inc,
                          "precio": pre if pre is not None else None}
        self.destroy()


class _DlgAgregar(tk.Toplevel):
    def __init__(self, parent, candidatos, ejec):
        super().__init__(parent)
        self.title("Agregar tareas a la etapa")
        self.geometry("760x460")
        self.grab_set()
        self.claves = []
        cols = ("rubro", "item", "desc", "unidad", "estado")
        self.tbl = ttk.Treeview(self, columns=cols, show="headings", selectmode="extended")
        for c, t, w in (("rubro", "Rubro", 50), ("item", "Ítem", 45), ("desc", "Descripción", 400),
                        ("unidad", "Unidad", 60), ("estado", "Estado", 90)):
            self.tbl.heading(c, text=t)
            self.tbl.column(c, width=w, anchor="w" if c == "desc" else "center")
        for o in candidatos:
            est = E.estado(ejec, o["clave"])
            ad = E.es_adicional(o["clave"])
            self.tbl.insert("", "end", iid=o["clave"], tags=(est, "adic") if ad else (est,),
                            values=(o["rubro"], o["item"],
                                    o["descripcion"] + ("  (adicional)" if ad else ""),
                                    o["unidad"], E.ESTADO_TXT[est]))
        self.tbl.tag_configure("adic", foreground=COLOR_ADIC)
        for est, col in COLOR_ESTADO.items():
            self.tbl.tag_configure(est, background=col)
        self.tbl.pack(fill="both", expand=True, padx=8, pady=8)
        bot = tk.Frame(self, bg=COLOR_BG, pady=6)
        bot.pack(fill="x")
        _btn(bot, "Cancelar", "#888", self.destroy).pack(side="right", padx=8)
        _btn(bot, "Agregar seleccionadas", COLOR_VERDE, self._ok, True).pack(side="right")
        _centrar(self, parent)

    def _ok(self):
        self.claves = list(self.tbl.selection())
        self.destroy()


# ═════════════════════════════════════════════════════════════════
class _DlgAdicional(tk.Toplevel):
    """Carga una tarea adicional: del catálogo de la obra (precio por insumos) o
    libre (descripción, unidad y precio unitario a mano)."""

    def __init__(self, parent, maestro, rubros: dict, clave: str):
        super().__init__(parent)
        self.title(f"Tarea adicional {clave}")
        self.geometry("820x560")
        self.minsize(700, 460)
        self.grab_set()
        self.resultado = None
        self.clave = clave
        self.tareas = sorted(maestro["tareas_por_cod"].values(), key=lambda t: t["cod"])
        self.cod_sel = ""

        tk.Label(self, text=f"  Tarea adicional {clave} — no prevista en el Original",
                 bg=COLOR_SEC_AD, fg="white", font=FUENTE_B, anchor="w", pady=8
                 ).pack(fill="x")

        bus = tk.Frame(self, bg=COLOR_BG, pady=4)
        bus.pack(fill="x", padx=8)
        tk.Label(bus, text="Buscar en el catálogo de la obra:", bg=COLOR_BG,
                 font=FUENTE_S).pack(side="left")
        self.var_bus = tk.StringVar()
        e = ttk.Entry(bus, textvariable=self.var_bus, width=40)
        e.pack(side="left", padx=4)
        e.focus_set()
        self.var_bus.trace_add("write", lambda *_: self._filtrar())
        _btn(bus, "Sin tarea del catálogo (precio a mano)", "#777", self._libre
             ).pack(side="right")

        fr = tk.Frame(self)
        fr.pack(fill="both", expand=True, padx=8)
        self.tbl = ttk.Treeview(fr, columns=("cod", "nombre", "unidad"), show="headings",
                                selectmode="browse", height=10)
        for c, t, w in (("cod", "Código", 80), ("nombre", "Tarea", 520), ("unidad", "Unidad", 60)):
            self.tbl.heading(c, text=t)
            self.tbl.column(c, width=w, anchor="w" if c == "nombre" else "center")
        scr = ttk.Scrollbar(fr, orient="vertical", command=self.tbl.yview)
        self.tbl.configure(yscrollcommand=scr.set)
        scr.pack(side="right", fill="y")
        self.tbl.pack(fill="both", expand=True)
        self.tbl.bind("<<TreeviewSelect>>", self._elegir)

        frm = tk.Frame(self, bg=COLOR_BG, pady=6)
        frm.pack(fill="x", padx=8)
        self.var_cod = tk.StringVar(value="(ninguna: precio a mano)")
        self.var_desc = tk.StringVar()
        self.var_uni = tk.StringVar()
        self.var_cant = tk.StringVar(value="0")
        self.var_pu = tk.StringVar()
        opciones = [f"{k} - {v}" for k, v in rubros.items()] + ["AD - Adicionales varios"]
        self.var_rub = tk.StringVar(value=opciones[-1])
        filas = (("Tarea del catálogo:", tk.Label(frm, textvariable=self.var_cod, bg=COLOR_BG,
                                                   fg=COLOR_ADIC, font=FUENTE_B, anchor="w")),
                 ("Descripción:", ttk.Entry(frm, textvariable=self.var_desc, width=70)),
                 ("Unidad:", ttk.Entry(frm, textvariable=self.var_uni, width=10)),
                 ("Rubro:", ttk.Combobox(frm, textvariable=self.var_rub, values=opciones,
                                         width=50, state="readonly")),
                 ("Cantidad:", ttk.Entry(frm, textvariable=self.var_cant, width=14)),
                 ("P. Unit. a mano:", ttk.Entry(frm, textvariable=self.var_pu, width=14)))
        for r, (lbl, w) in enumerate(filas):
            tk.Label(frm, text=lbl, bg=COLOR_BG, font=FUENTE_S, anchor="e"
                     ).grid(row=r, column=0, sticky="e", padx=(0, 6), pady=1)
            w.grid(row=r, column=1, sticky="w", pady=1)
        tk.Label(frm, text="(vacío = se calcula con los precios de la etapa; obligatorio si "
                           "no hay tarea del catálogo)", bg=COLOR_BG, fg="#666", font=FUENTE_S
                 ).grid(row=5, column=2, sticky="w", padx=6)

        bot = tk.Frame(self, bg="#e0e0e0", pady=6)
        bot.pack(side="bottom", fill="x")
        _btn(bot, "Cancelar", "#888", self.destroy).pack(side="right", padx=(4, 10))
        _btn(bot, "Agregar adicional", COLOR_SEC_AD, self._ok, True).pack(side="right")
        self._filtrar()
        _centrar(self, parent)

    def _filtrar(self):
        txt = self.var_bus.get().strip().lower()
        self.tbl.delete(*self.tbl.get_children())
        for t in self.tareas:
            if txt and txt not in t["cod"].lower() and txt not in t["nombre"].lower():
                continue
            self.tbl.insert("", "end", iid=t["cod"], values=(t["cod"], t["nombre"], t["unidad"]))

    def _elegir(self, _=None):
        sel = self.tbl.selection()
        if not sel:
            return
        t = next(x for x in self.tareas if x["cod"] == sel[0])
        self.cod_sel = t["cod"]
        self.var_cod.set(f"{t['cod']}  {t['nombre']}")
        self.var_desc.set(t["nombre"])
        self.var_uni.set(t["unidad"])

    def _libre(self):
        self.tbl.selection_remove(*self.tbl.selection())
        self.cod_sel = ""
        self.var_cod.set("(ninguna: precio a mano)")

    def _ok(self):
        desc = self.var_desc.get().strip()
        if not desc:
            messagebox.showwarning("Falta descripción", "Escribí la descripción.", parent=self)
            return
        try:
            cant = _parse_num(self.var_cant.get()) or 0.0
            pu = _parse_num(self.var_pu.get())
        except ValueError:
            messagebox.showerror("Valor inválido", "Revisá cantidad y precio.", parent=self)
            return
        if not self.cod_sel and not pu:
            messagebox.showwarning("Falta precio",
                "Sin tarea del catálogo hay que poner el precio unitario a mano.", parent=self)
            return
        self.resultado = {
            "clave": self.clave, "descripcion": desc, "unidad": self.var_uni.get().strip(),
            "rubro": self.var_rub.get().split(" - ")[0], "cod_tar": self.cod_sel,
            "cantidad": cant, "pu_manual": pu or None,
        }
        self.destroy()


# ═════════════════════════════════════════════════════════════════
class _DlgCierre(tk.Toplevel):
    def __init__(self, tab: TabEjecucion):
        super().__init__(tab.v)
        self.tab = tab
        quedan = any(E.estado(tab.ejec, i["clave"]) == "a_realizar"
                     for i in tab.ejec["original"]["items"])
        self.var_avance = tk.BooleanVar(value=quedan)
        self.title("Cierre — Etapas vs Original")
        self.geometry("1250x640")
        self.minsize(900, 400)
        hdr = tk.Frame(self, bg=COLOR_VERDE)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"  Cierre de obra — {self.tab.obra.titulo}", bg=COLOR_VERDE,
                 fg="white", font=("Segoe UI", 12, "bold"), pady=6).pack(side="left", padx=6)
        _btn(hdr, "Exportar Excel", "#155c38", self._exportar, True).pack(side="right", padx=8)
        _btn(hdr, "Incidencias reales → BaseParticular…", "#155c38",
             lambda: _DlgIncidencias(self, self.tab)).pack(side="right", padx=4)
        tk.Checkbutton(hdr, text="Solo tareas con avance (sin las «A realizar»)",
                       variable=self.var_avance, command=self._build, bg=COLOR_VERDE,
                       fg="white", selectcolor="#155c38", activebackground=COLOR_VERDE,
                       activeforeground="white", font=FUENTE_S).pack(side="right", padx=8)
        self.cuerpo = None
        self._build()
        _centrar(self, tab.v)

    def _build(self):
        if self.cuerpo is not None:
            self.cuerpo.destroy()
        self.comp = E.comparar(self.tab.data, self.tab.ejec, self.var_avance.get())
        self.cuerpo = tk.Frame(self)
        self.cuerpo.pack(fill="both", expand=True)
        c, t, g = self.comp, self.comp["total"], self.comp["total_general"]
        res = tk.Frame(self.cuerpo, bg="#e8f0f8", padx=12, pady=6)
        res.pack(fill="x", padx=8, pady=(6, 2))
        vers = "   ".join(f"E{e['numero']:02d}: $ {_fmt_pt(e['total'])}"
                           + (f" (adic. $ {_fmt_pt(e['total_adic'])})" if e["total_adic"] else "")
                           for e in c["etapas"])
        pct = f"{t['dif'] / t['orig'] * 100:+.1f} %" if t["orig"] else "-"
        pct_g = f"{g['dif'] / g['orig'] * 100:+.1f} %" if g["orig"] else "-"
        tk.Label(res, bg="#e8f0f8", fg=COLOR_HDR, font=FUENTE_S, anchor="w", justify="left",
                 text=f"Etapas:  {vers or '(ninguna)'}").pack(fill="x")
        tk.Label(res, bg="#e8f0f8", fg=COLOR_HDR, font=FUENTE_S, anchor="w", justify="left",
                 text=f"Tareas del Original:   Original $ {_fmt_pt(t['orig'])}   ·   "
                      f"Ejecutado $ {_fmt_pt(t['ejec'])}   ·   Diferencia $ {_fmt_pt(t['dif'])}"
                      f" ({pct}):  por cantidades $ {_fmt_pt(t['ef_cant'])},  "
                      f"por precios $ {_fmt_pt(t['ef_prec'])}").pack(fill="x")
        tk.Label(res, bg="#e8f0f8", fg=COLOR_ADIC, font=FUENTE_S, anchor="w", justify="left",
                 text=f"Adicionales (no previstas):   $ {_fmt_pt(g['adic'])}   "
                      f"({len(c['filas_adic'])} tareas)").pack(fill="x")
        tk.Label(res, bg="#e8f0f8", fg=COLOR_HDR, font=FUENTE_B, anchor="w", justify="left",
                 text=f"TOTAL:   Original $ {_fmt_pt(g['orig'])}      Ejecutado $ "
                      f"{_fmt_pt(g['ejec'])}      Diferencia $ {_fmt_pt(g['dif'])} ({pct_g})"
                 ).pack(fill="x")

        cols = ("rubro", "item", "desc", "estado", "q_o", "t_o", "q_e", "t_e",
                "dif", "ef_q", "ef_p", "pct")
        txt = {"rubro": "Rubro", "item": "Ítem", "desc": "Descripción", "estado": "Estado",
               "q_o": "Cant. Orig.", "t_o": "Total Orig.", "q_e": "Cant. Ejec.",
               "t_e": "Total Ejec.", "dif": "Diferencia", "ef_q": "Por cantidad",
               "ef_p": "Por precio", "pct": "Var. %"}
        anch = {"rubro": 42, "item": 40, "desc": 260, "estado": 75, "q_o": 75, "t_o": 105,
                "q_e": 75, "t_e": 105, "dif": 105, "ef_q": 100, "ef_p": 100, "pct": 60}
        fr = tk.Frame(self.cuerpo)
        fr.pack(fill="both", expand=True, padx=8, pady=6)
        tbl = ttk.Treeview(fr, columns=cols, show="headings")
        for k in cols:
            tbl.heading(k, text=txt[k])
            tbl.column(k, width=anch[k], minwidth=24,
                       anchor="w" if k == "desc" else
                       ("center" if k in ("rubro", "item", "estado") else "e"))
        scr = ttk.Scrollbar(fr, orient="vertical", command=tbl.yview)
        tbl.configure(yscrollcommand=scr.set)
        scr.pack(side="right", fill="y")
        tbl.pack(fill="both", expand=True)
        tbl.tag_configure("rub", background="#d4edda", font=FUENTE_B)
        tbl.tag_configure("mas", foreground=COLOR_ROJO)
        tbl.tag_configure("menos", foreground=COLOR_VERDE)
        tbl.tag_configure("tot", background="#1d5a2a", foreground="white", font=FUENTE_B)
        tbl.tag_configure("sub", background=COLOR_HDR, foreground="white", font=FUENTE_B)
        tbl.tag_configure("sec", background=COLOR_SEC, foreground="white", font=FUENTE_B)
        tbl.tag_configure("sec_adic", background=COLOR_SEC_AD, foreground="white",
                          font=FUENTE_B)
        tbl.tag_configure("adic", foreground=COLOR_ADIC, background="#f3edf8")

        def p(v):
            return f"$ {_fmt_pt(v)}" if v else ""

        vacia = ("",) * 12
        tbl.insert("", "end", tags=("sec",), values=(
            "", "", "TAREAS DEL ORIGINAL", "", "", "", "", "", "", "", "", ""))
        rub = None
        for f in c["filas"]:
            if f["rubro"] != rub:
                rub = f["rubro"]
                r = c["rubros"][rub]
                tbl.insert("", "end", tags=("rub",), values=(
                    rub, "", c["rubros_desc"].get(rub, ""), "", "", p(r["orig"]), "",
                    p(r["ejec"]), p(r["dif"]), p(r["ef_cant"]), p(r["ef_prec"]),
                    f"{r['dif'] / r['orig'] * 100:+.1f}" if r["orig"] else ""))
            tag = "mas" if f["dif"] > 0.5 else ("menos" if f["dif"] < -0.5 else "")
            tbl.insert("", "end", tags=(tag,), values=(
                f["rubro"], f["item"], f["descripcion"], E.ESTADO_TXT[f["estado"]],
                _fmt(f["cant_orig"]), p(f["total_orig"]),
                _fmt(f["cant_ejec"]) if f["cant_ejec"] else "", p(f["total_ejec"]),
                p(f["dif"]), p(f["ef_cant"]), p(f["ef_prec"]),
                f"{f['dif'] / f['total_orig'] * 100:+.1f}" if f["total_orig"] else ""))
        tbl.insert("", "end", tags=("sub",), values=(
            "", "", "SUBTOTAL TAREAS DEL ORIGINAL", "", "", p(t["orig"]), "", p(t["ejec"]),
            p(t["dif"]), p(t["ef_cant"]), p(t["ef_prec"]),
            f"{t['dif'] / t['orig'] * 100:+.1f}" if t["orig"] else ""))
        if c["filas_adic"]:
            tbl.insert("", "end", values=vacia)
            tbl.insert("", "end", tags=("sec_adic",), values=(
                "", "", "ADICIONALES (no previstas en el Original)", "", "", "", "", "", "",
                "", "", ""))
            for f in c["filas_adic"]:
                tbl.insert("", "end", tags=("adic",), values=(
                    f["rubro"], f["item"], f["descripcion"], E.ESTADO_TXT[f["estado"]],
                    "—", "—", _fmt(f["cant_ejec"]) if f["cant_ejec"] else "",
                    p(f["total_ejec"]), p(f["dif"]), "", "", ""))
            tbl.insert("", "end", tags=("sub",), values=(
                "", "", "SUBTOTAL ADICIONALES", "", "", "", "", p(c["total_adic"]),
                p(c["total_adic"]), "", "", ""))
        tbl.insert("", "end", values=vacia)
        tbl.insert("", "end", tags=("tot",), values=(
            "", "", "TOTAL GENERAL (Original + adicionales)", "", "", p(g["orig"]), "",
            p(g["ejec"]), p(g["dif"]), p(g["ef_cant"]), p(g["ef_prec"]),
            f"{g['dif'] / g['orig'] * 100:+.1f}" if g["orig"] else ""))

    def _exportar(self):
        obra = self.tab.obra
        ruta = filedialog.asksaveasfilename(
            parent=self, title="Exportar cierre", initialdir=str(obra.carpeta),
            initialfile=f"Obra{obra.numero}_Cierre_Etapas_vs_Original.xlsx",
            defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if not ruta:
            return
        try:
            E.exportar_comparacion(Path(ruta), obra.titulo, self.tab.ejec, self.comp)
        except PermissionError:
            messagebox.showerror("Archivo en uso", "Cerralo en Excel y volvé a intentar.",
                                 parent=self)
            return
        messagebox.showinfo("Exportado", ruta, parent=self)


# ═════════════════════════════════════════════════════════════════
class _DlgIncidencias(tk.Toplevel):
    """Vista previa y carga de las incidencias reales (tareas Realizadas) en la
    BaseParticular.db de la obra."""

    def __init__(self, parent, tab: TabEjecucion):
        super().__init__(parent)
        self.tab = tab
        self.title("Incidencias reales → BaseParticular.db")
        self.geometry("1100x600")
        self.minsize(850, 400)
        self.grupos = E.incidencias_reales(tab.data, tab.ejec, tab.v.maestro["incidencias"],
                                           tab.v.maestro.get("insumos"), solo_realizadas=True)
        if not self.grupos:
            self.destroy()
            messagebox.showinfo("Sin tareas realizadas",
                                "No hay tareas «Realizadas» con cantidad ejecutada en las etapas.",
                                parent=parent)
            return
        self.aplicar = {g["cod"] for g in self.grupos if g["cambios"]}
        self.grab_set()

        tk.Label(self, text="  Incidencias reales de las tareas Realizadas  —  consumo de todas "
                            "las etapas ÷ cantidad ejecutada", bg=COLOR_VERDE, fg="white",
                 font=FUENTE_B, anchor="w", pady=8).pack(fill="x")
        tk.Label(self, text="  Clic en ✔ para incluir o excluir una tarea.  Las tareas que "
                            "comparten código (ej. 1250E) se suman y quedan con una sola "
                            "incidencia.  Antes de escribir se hace un backup de la base.",
                 bg=COLOR_BG, fg="#555", font=FUENTE_S, anchor="w").pack(fill="x")

        bot = tk.Frame(self, bg="#e0e0e0", pady=6)
        bot.pack(side="bottom", fill="x")
        _btn(bot, "Cancelar", "#888", self.destroy).pack(side="right", padx=(4, 10))
        _btn(bot, "Aplicar a la BaseParticular", COLOR_ROJO, self._aplicar, True
             ).pack(side="right", padx=4)
        self.lbl = tk.Label(bot, text="", bg="#e0e0e0", fg=COLOR_HDR, font=FUENTE_B)
        self.lbl.pack(side="left", padx=10)

        cols = ("ap", "cod", "desc", "unidad", "base", "real", "dif", "acc")
        txt = {"ap": "Aplicar", "cod": "Código", "desc": "Tarea / Insumo", "unidad": "Unidad",
               "base": "Incid. análisis", "real": "Incid. real", "dif": "Dif. %",
               "acc": "Acción"}
        anch = {"ap": 55, "cod": 70, "desc": 430, "unidad": 55, "base": 105, "real": 105,
                "dif": 65, "acc": 110}
        fr = tk.Frame(self)
        fr.pack(fill="both", expand=True, padx=8, pady=6)
        self.tbl = ttk.Treeview(fr, columns=cols, show="tree headings", selectmode="browse")
        self.tbl.column("#0", width=22, minwidth=22, stretch=False)
        for c in cols:
            self.tbl.heading(c, text=txt[c])
            self.tbl.column(c, width=anch[c], minwidth=30,
                            anchor="w" if c == "desc" else
                            ("e" if c in ("base", "real", "dif") else "center"))
        scr = ttk.Scrollbar(fr, orient="vertical", command=self.tbl.yview)
        self.tbl.configure(yscrollcommand=scr.set)
        scr.pack(side="right", fill="y")
        self.tbl.pack(fill="both", expand=True)
        self.tbl.tag_configure("tarea", background="#d4edda", font=FUENTE_B)
        self.tbl.tag_configure("tarea_no", background="#eeeeee", foreground="#888",
                               font=FUENTE_B)
        self.tbl.tag_configure("igual", foreground="#999")
        self.tbl.tag_configure("actualizar", foreground="#1f5fbf")
        self.tbl.tag_configure("nuevo", foreground=COLOR_VERDE)
        self.tbl.tag_configure("quitar", foreground=COLOR_ROJO)
        self.tbl.bind("<ButtonRelease-1>", self._clic)
        self._poblar()
        _centrar(self, parent)

    def _poblar(self):
        abiertos = {g for g in self.tbl.get_children() if self.tbl.item(g, "open")}
        primera = not self.tbl.get_children()
        self.tbl.delete(*self.tbl.get_children())
        for g in self.grupos:
            ap = g["cod"] in self.aplicar
            self.tbl.insert("", "end", iid=g["cod"], tags=("tarea" if ap else "tarea_no",),
                            open=(g["cambios"] > 0) if primera else g["cod"] in abiertos,
                            values=(
                "✔" if ap else "", g["cod"],
                "  ·  ".join(g["tareas"].values()) + f"   —  {_fmt(g['cantidad'])} ejecutado",
                "", "", "", "", f"{g['cambios']} cambio(s)" if g["cambios"] else "sin cambios"))
            for n, f in enumerate(g["insumos"]):
                b, r = f["base"], f["real"]
                dif = (f"{(r - b) / b * 100:+.1f}" if b else "") if b is not None else ""
                tag = "igual" if f["accion"] == "sin cambio" else f["accion"]
                self.tbl.insert(g["cod"], "end", iid=f"{g['cod']}|{n}", tags=(tag,), values=(
                    "", f["cod_ins"], f"    {f['nombre']}", f["unidad"],
                    _fmt(b, 4) if b is not None else "—", _fmt(r, 4), dif, f["accion"]))
        n_t = sum(1 for g in self.grupos if g["cod"] in self.aplicar)
        n_f = sum(g["cambios"] for g in self.grupos if g["cod"] in self.aplicar)
        self.lbl.config(text=f"Se aplican {n_f} cambio(s) en {n_t} tarea(s)")

    def _clic(self, event):
        if self.tbl.identify_region(event.x, event.y) != "cell":
            return
        iid = self.tbl.identify_row(event.y)
        if not iid or "|" in iid or self.tbl.identify_column(event.x) != "#1":
            return
        g = next(x for x in self.grupos if x["cod"] == iid)
        if not g["cambios"]:
            return
        if iid in self.aplicar:
            self.aplicar.discard(iid)
        else:
            self.aplicar.add(iid)
        self._poblar()

    def _aplicar(self):
        sel = [g for g in self.grupos if g["cod"] in self.aplicar and g["cambios"]]
        if not sel:
            messagebox.showinfo("Nada para aplicar", "No hay tareas marcadas con cambios.",
                                parent=self)
            return
        n = sum(g["cambios"] for g in sel)
        if not messagebox.askyesno(
                "Aplicar incidencias reales",
                f"Se van a modificar {n} incidencia(s) de {len(sel)} tarea(s) en la "
                "BaseParticular.db de esta obra:\n\n"
                + "\n".join(f"  {g['cod']}: {g['cambios']} cambio(s)" for g in sel[:15])
                + ("\n  …" if len(sel) > 15 else "")
                + "\n\nAntes se guarda un backup de la base. El presupuesto de la obra va a "
                  "usar las incidencias nuevas; el Original de la pestaña Ejecución no "
                  "cambia.\n\n¿Continuar?", icon="warning", parent=self):
            return
        try:
            bak = E.aplicar_incidencias(self.tab.data, sel)
        except Exception as e:
            messagebox.showerror("Error al escribir la base", str(e), parent=self)
            return
        from core.obra import cargar_maestro_desde_db
        self.tab.v.maestro.update(cargar_maestro_desde_db(self.tab.data))
        messagebox.showinfo("Incidencias cargadas",
                            f"Se cargaron {n} incidencia(s) en BaseParticular.db.\n\n"
                            f"Backup: {bak.name}", parent=self)
        self.destroy()
