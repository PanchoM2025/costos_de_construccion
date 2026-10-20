"""
main.pyw  —  Pantalla principal · Análisis de Costos y Presupuestación
Ejecutar: python main.pyw  (desde la carpeta Scripts)
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import subprocess
import threading
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.obra import listar_obras, Obra, CARPETA_DATA
from ui.dialogo_nueva_obra import DialogoNuevaObra
from ui.ventana_obra import VentanaObra
from cierre_de_dia import cierre as _cierre_de_dia

# ── Rutas de integración con el módulo Costos ─────────────────────────────────
RAIZ            = Path(__file__).resolve().parent.parent.parent  # Analisis_de_costos_y_Presupuestacion
APP_TAREAS      = RAIZ / "Costos" / "Scripts" / "app_tareas.py"
CATALOGO_DB     = RAIZ / "Costos" / "Data" / "Master_FINAL.db"   # Master único (se copia a cada obra nueva)

TITULO_APP      = "Análisis de Costos y Presupuestación"
COLOR_HEADER    = "#1a3a5c"
COLOR_BTN_NUEVO = "#1d7a4a"
COLOR_BTN_ABRIR = "#1a5c9e"
COLOR_BTN_ELIM  = "#b03030"
COLOR_BTN_DB    = "#7b1fa2"
COLOR_BTN_TEXTO = "white"
PYTHON          = sys.executable


def _lanzar_app_tareas(db_path: Path, titulo: str, copiar_a: Path = None):
    proc = subprocess.Popen(
        [PYTHON, str(APP_TAREAS), "--db", str(db_path), "--title", titulo],
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
    )
    if copiar_a:
        def _esperar_y_copiar():
            proc.wait()
            try:
                shutil.copy2(str(db_path), str(copiar_a))
            except Exception:
                pass
        threading.Thread(target=_esperar_y_copiar, daemon=True).start()


# ═══════════════════════════════════════════════════════════
class AlertaBaseDatosDialog(tk.Toplevel):
    def __init__(self, parent, mensaje: str, on_confirmar):
        super().__init__(parent)
        self.on_confirmar = on_confirmar
        self.title("⚠  ATENCIÓN — Base de Datos")
        self.resizable(False, False)
        self.grab_set()
        self.configure(bg="#C0392B")
        hdr = tk.Frame(self, bg="#922B21", pady=14); hdr.pack(fill="x")
        tk.Label(hdr, text="⚠  ATENCIÓN", bg="#922B21", fg="white",
                 font=("Segoe UI", 15, "bold")).pack()
        frm = tk.Frame(self, bg="#C0392B", padx=24, pady=16); frm.pack(fill="both")
        tk.Label(frm, text=mensaje, bg="#C0392B", fg="white",
                 font=("Segoe UI", 11), wraplength=440, justify="center").pack()
        bf = tk.Frame(self, bg="#C0392B", pady=14); bf.pack()
        tk.Button(bf, text="  Cancelar  ", bg="#7B241C", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", padx=16, pady=8,
                  cursor="hand2", activebackground="#641E16", activeforeground="white",
                  command=self.destroy).pack(side="left", padx=8)
        tk.Button(bf, text="  Entendido, continuar  ", bg="#FDFEFE", fg="#C0392B",
                  font=("Segoe UI", 10, "bold"), relief="flat", padx=16, pady=8,
                  cursor="hand2", activebackground="#EAEDED", activeforeground="#C0392B",
                  command=self._confirmar).pack(side="left", padx=8)
        self.bind("<Escape>", lambda _: self.destroy())
        self.update_idletasks()
        px = parent.winfo_x() + (parent.winfo_width()  - self.winfo_width())  // 2
        py = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{px}+{py}")

    def _confirmar(self):
        cb = self.on_confirmar
        self.grab_release(); self.destroy(); cb()


# ═══════════════════════════════════════════════════════════
class AppPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(TITULO_APP)
        self.geometry("920x520"); self.minsize(720, 400)
        self.configure(bg="#f0f0f0")
        self._build_menu(); self._build_ui(); self.actualizar_lista()

    def _build_menu(self):
        menubar = tk.Menu(self); self.config(menu=menubar)
        men_her = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Herramientas", menu=men_her)
        men_her.add_command(label="Cierre de día  (backup + GitHub)",
                            command=lambda: _cierre_de_dia(parent_window=self))

    def _build_ui(self):
        header = tk.Frame(self, bg=COLOR_HEADER, height=56)
        header.pack(fill="x"); header.pack_propagate(False)
        tk.Label(header, text=f"  {TITULO_APP}", bg=COLOR_HEADER, fg="white",
                 font=("Segoe UI", 14, "bold")).pack(side="left", padx=12, pady=10)

        barra = tk.Frame(self, bg="#e0e0e0", pady=8); barra.pack(fill="x")
        self._btn(barra, "Nueva obra",    COLOR_BTN_NUEVO, self.nueva_obra   ).pack(side="left", padx=(12,4))
        self._btn(barra, "Abrir obra",    COLOR_BTN_ABRIR, self.abrir_obra   ).pack(side="left", padx=4)
        self._btn(barra, "Eliminar obra", COLOR_BTN_ELIM,  self.eliminar_obra).pack(side="left", padx=4)
        self._btn(barra, "↑ BackUp",      "#555555",       self.hacer_backup ).pack(side="left", padx=(16,4))

        self._btn(barra, "🗄 Base de datos Costos",
                  COLOR_BTN_DB, self._abrir_db_catalogo).pack(side="right", padx=(4,12))
        self.btn_db_obra = self._btn(barra, "🗄 Base de datos Costos Obra ---",
                                     COLOR_BTN_DB, self._abrir_db_obra)
        self.btn_db_obra.pack(side="right", padx=4)
        self.btn_db_obra.config(state="disabled")

        frame_tabla = tk.Frame(self, bg="#f0f0f0")
        frame_tabla.pack(fill="both", expand=True, padx=16, pady=(12,16))
        cols = ("numero","nombre","ubicacion","comitente","fecha")
        self.tabla = ttk.Treeview(frame_tabla, columns=cols, show="headings", selectmode="browse")
        for col,(txt,ancho) in {"numero":("Nro",60),"nombre":("Nombre",240),"ubicacion":("Ubicación",180),"comitente":("Comitente",160),"fecha":("Creación",90)}.items():
            self.tabla.heading(col, text=txt); self.tabla.column(col, width=ancho, minwidth=40)
        scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll_y.set)
        self.tabla.pack(side="left", fill="both", expand=True); scroll_y.pack(side="right", fill="y")
        self.tabla.bind("<Double-1>", lambda e: self.abrir_obra())
        self.tabla.bind("<<TreeviewSelect>>", self._on_obra_select)
        self.tabla.tag_configure("par",   background="#ffffff")
        self.tabla.tag_configure("impar", background="#eaf2fb")

        self.lbl_estado = tk.Label(self, text="", bg="#e0e0e0", fg="#444",
                                   font=("Segoe UI",9), anchor="w", padx=12, pady=4)
        self.lbl_estado.pack(fill="x", side="bottom")

    def _btn(self, parent, texto, color, comando):
        return tk.Button(parent, text=texto, bg=color, fg=COLOR_BTN_TEXTO,
                         font=("Segoe UI",10,"bold"), relief="flat", padx=14, pady=6,
                         cursor="hand2", activebackground=color, activeforeground="white",
                         command=comando)

    def _on_obra_select(self, _=None):
        num = self._obra_seleccionada()
        if num:
            self.btn_db_obra.config(text=f"🗄 Base de datos Costos Obra {num}", state="normal")
        else:
            self.btn_db_obra.config(text="🗄 Base de datos Costos Obra ---", state="disabled")

    def _abrir_db_catalogo(self):
        if not APP_TAREAS.exists():
            messagebox.showerror("Error", f"No se encontró app_tareas.py en:\n{APP_TAREAS}", parent=self); return
        AlertaBaseDatosDialog(self,
            mensaje=("Está por hacer modificaciones a la Base de Datos\n"
                     "de las Tareas, Insumos e Incidencias MASTER.\n\n"
                     "Cualquier cambio modificará las incidencias\n"
                     "en FUTURAS OBRAS."),
            on_confirmar=self._confirmar_db_catalogo)

    def _confirmar_db_catalogo(self):
        _lanzar_app_tareas(db_path=CATALOGO_DB,
                           titulo="Base de Datos Costos — CATÁLOGO MAESTRO")

    def _abrir_db_obra(self):
        num = self._obra_seleccionada()
        if not num: return
        from core.obra import CARPETA_OBRAS
        db_obra = CARPETA_OBRAS / f"Obra{num}" / "data" / "BaseParticular.db"
        if not db_obra.exists():
            messagebox.showerror("Error", f"No se encontró BaseParticular.db para la Obra {num}.", parent=self); return
        AlertaBaseDatosDialog(self,
            mensaje=(f"Está por hacer modificaciones a la Base de Datos\n"
                     f"de las Tareas, Insumos e Incidencias de la\n\n"
                     f"OBRA  {num}\n\n"
                     f"Podés hacer cualquier cambio.\n"
                     f"Solo modificará las incidencias de esta obra."),
            on_confirmar=lambda: _lanzar_app_tareas(
                db_path=db_obra,
                titulo=f"Base de Datos Costos — Obra {num}",
                copiar_a=None))

    def actualizar_lista(self):
        for item in self.tabla.get_children(): self.tabla.delete(item)
        try:
            obras = listar_obras()
        except RuntimeError as e:
            messagebox.showerror("Índice de obras", str(e), parent=self)
            obras = []
        for i,o in enumerate(obras):
            tag = "par" if i%2==0 else "impar"
            self.tabla.insert("","end",iid=o["numero"],tags=(tag,),
                              values=(o["numero"],o["nombre"],o.get("ubicacion",""),o.get("comitente",""),o.get("fecha_creacion","")))
        n = len(obras)
        self.lbl_estado.config(text=f"  {n} obra{'s' if n!=1 else ''} registrada{'s' if n!=1 else ''}")

    def _obra_seleccionada(self) -> str | None:
        sel = self.tabla.selection()
        return sel[0] if sel else None

    def nueva_obra(self):
        dlg = DialogoNuevaObra(self); self.wait_window(dlg)
        if dlg.obra_creada:
            self.actualizar_lista()
            num = dlg.obra_creada.numero
            if self.tabla.exists(num): self.tabla.selection_set(num); self.tabla.see(num)
            self.abrir_obra(obra=dlg.obra_creada)

    def abrir_obra(self, obra: Obra = None):
        if obra is None:
            num = self._obra_seleccionada()
            if not num: messagebox.showinfo("Sin selección","Seleccioná una obra de la lista.",parent=self); return
            try:
                from core.obra import CARPETA_OBRAS
                carpeta_data = CARPETA_OBRAS / f"Obra{num}" / "data"
                jsons = sorted(carpeta_data.glob("obra???.json"))
                if len(jsons) > 1:
                    dlg = _DlgVersiones(self, num, jsons); self.wait_window(dlg)
                    if not dlg.seleccionados: return
                    if len(dlg.seleccionados) == 1:
                        obra = Obra.cargar_version(dlg.seleccionados[0]); VentanaObra(self, obra)
                    else:
                        obra = self._combinar_versiones(dlg.seleccionados)
                        if obra: VentanaObra(self, obra)
                    return
                else:
                    obra = Obra.cargar(num)
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=self); return
        VentanaObra(self, obra)

    def _combinar_versiones(self, rutas: list) -> Obra | None:
        from collections import defaultdict
        try:
            rubro_headers={}; task_dict={}; rubro_for_task={}; base_obra=None
            for ruta in rutas:
                version_obra=Obra.cargar_version(ruta)
                if base_obra is None: base_obra=version_obra
                cur_rub_key=("","")
                for it in version_obra.items_presupuesto:
                    if it.get("es_rubro"):
                        key=(it.get("rubro",""),it.get("descripcion",""))
                        cur_rub_key=key
                        if key not in rubro_headers: rubro_headers[key]=dict(it)
                    else:
                        cod_tar=it.get("cod_tar",""); subcont=(it.get("subcontrato") or "").strip()
                        task_key=(cod_tar,subcont)
                        if task_key in task_dict:
                            task_dict[task_key]["cantidad"]=(task_dict[task_key].get("cantidad") or 0.0)+(it.get("cantidad") or 0.0)
                        else:
                            task_dict[task_key]=dict(it); rubro_for_task[task_key]=cur_rub_key
            rubro_tasks=defaultdict(list)
            for task_key,item in task_dict.items(): rubro_tasks[rubro_for_task.get(task_key,("",""))].append(item)
            result=[]
            for rub_key,rub_item in rubro_headers.items():
                result.append(rub_item); result.extend(rubro_tasks[rub_key])
            if rubro_tasks[("","")] and ("","") not in rubro_headers:
                result.append({"es_rubro":True,"rubro":"","descripcion":"Sin rubro"}); result.extend(rubro_tasks[("","")])
            base_obra.items_presupuesto=result
            nombres=", ".join(r.name for r in rutas)
            base_obra.guardar(nueva_version=True,nota=f"Combinación de: {nombres}")
            return base_obra
        except Exception as e:
            messagebox.showerror("Error al combinar versiones",str(e),parent=self); return None

    def eliminar_obra(self):
        num=self._obra_seleccionada()
        if not num: messagebox.showinfo("Sin selección","Seleccioná una obra para eliminar.",parent=self); return
        try: obra=Obra.cargar(num)
        except Exception as e: messagebox.showerror("Error",str(e),parent=self); return
        ok=messagebox.askyesno("Confirmar eliminación",
            f"¿Eliminás la obra {obra.titulo}?\n\nSe borrará la carpeta completa y todos sus datos.\nEsta acción no se puede deshacer.",
            icon="warning",parent=self)
        if ok: obra.eliminar(); self.actualizar_lista()

    def hacer_backup(self):
        from core.obra import CARPETA_DATA as CD, CARPETA_OBRAS
        errores = []

        # 1. Datos_Obras.db
        try:
            shutil.copy2(str(CD / "Datos_Obras.db"), str(CD / "Datos_Obras_BUP.db"))
        except Exception as e:
            errores.append(f"Datos_Obras.db: {e}")

        # 2. Master_FINAL.db (Master único, en Costos/Data)
        try:
            shutil.copy2(str(CATALOGO_DB), str(CATALOGO_DB.with_name("Master_FINAL_BUP.db")))
        except Exception as e:
            errores.append(f"Master_FINAL.db: {e}")

        # 3. BaseParticular.db de cada obra → BaseParticular_BUP.db en su misma carpeta
        for carpeta_obra in sorted(CARPETA_OBRAS.glob("Obra*")):
            db = carpeta_obra / "data" / "BaseParticular.db"
            if db.exists():
                bup = carpeta_obra / "data" / "BaseParticular_BUP.db"
                try:
                    shutil.copy2(str(db), str(bup))
                except Exception as e:
                    errores.append(f"{carpeta_obra.name}/BaseParticular.db: {e}")

        if errores:
            messagebox.showwarning("Backup parcial",
                "Algunos backups fallaron:\n" + "\n".join(errores), parent=self)

        _cierre_de_dia(parent_window=self)


# ═══════════════════════════════════════════════════════════
class _DlgVersiones(tk.Toplevel):
    def __init__(self,parent,numero,jsons):
        super().__init__(parent); self.title(f"Versiones — Obra {numero}")
        self.geometry("520x340"); self.minsize(420,240); self.resizable(True,True)
        self.grab_set(); self.seleccionados=[]
        hdr=tk.Frame(self,bg=COLOR_HEADER,height=40); hdr.pack(fill="x"); hdr.pack_propagate(False)
        tk.Label(hdr,text=f"  Versiones de la Obra {numero}",bg=COLOR_HEADER,fg="white",
                 font=("Segoe UI",11,"bold")).pack(side="left",padx=12)
        tk.Label(self,text="Seleccioná una o más versiones (Shift/Ctrl) y hacé clic en Abrir:",
                 font=("Segoe UI",9),fg="#555",bg="#f5f5f5",anchor="w",padx=12,pady=6).pack(fill="x")
        frame=tk.Frame(self); frame.pack(fill="both",expand=True,padx=12,pady=(0,6))
        cols=("archivo","version","fecha","nota")
        self.tbl=ttk.Treeview(frame,columns=cols,show="headings",selectmode="extended")
        for col,txt,w in [("archivo","Archivo",120),("version","Versión",60),("fecha","Fecha",100),("nota","Nota",200)]:
            self.tbl.heading(col,text=txt)
            self.tbl.column(col,width=w,minwidth=40,anchor="w" if col in ("archivo","nota") else "center")
        scr=ttk.Scrollbar(frame,orient="vertical",command=self.tbl.yview)
        self.tbl.configure(yscrollcommand=scr.set); scr.pack(side="right",fill="y")
        self.tbl.pack(side="left",fill="both",expand=True)
        self.tbl.tag_configure("par",background="#ffffff")
        self.tbl.tag_configure("impar",background="#eaf2fb")
        self.tbl.tag_configure("last",background="#d4edda")
        import json as _json
        notas=self._leer_notas(jsons[0].parent)
        for i,j in enumerate(jsons):
            try:
                with open(j,encoding="utf-8") as f: d=_json.load(f)
                ver=d.get("version",i); fecha=d.get("fecha_creacion","")
            except: ver,fecha=i,""
            nota=notas.get(j.name,"")
            tag="last" if i==len(jsons)-1 else ("par" if i%2==0 else "impar")
            self.tbl.insert("","end",iid=str(j),tags=(tag,),values=(j.name,ver,fecha,nota))
        if jsons: self.tbl.selection_set(str(jsons[-1])); self.tbl.see(str(jsons[-1]))
        self.tbl.bind("<Double-1>",lambda _: self._abrir())
        self.tbl.bind("<<TreeviewSelect>>",self._actualizar_btn)
        frm_btn=tk.Frame(self,pady=8); frm_btn.pack(fill="x",padx=12)
        self.btn_abrir=tk.Button(frm_btn,text="Abrir seleccionada",bg=COLOR_BTN_ABRIR,fg="white",
                                 font=("Segoe UI",10,"bold"),relief="flat",padx=14,pady=6,
                                 cursor="hand2",command=self._abrir)
        self.btn_abrir.pack(side="right",padx=(4,0))
        tk.Button(frm_btn,text="Cancelar",bg="#888",fg="white",font=("Segoe UI",10),
                  relief="flat",padx=14,pady=6,cursor="hand2",command=self.destroy).pack(side="right")
        self.bind("<Return>",lambda _: self._abrir()); self.bind("<Escape>",lambda _: self.destroy())
        self.update_idletasks()
        px=parent.winfo_x()+(parent.winfo_width()-self.winfo_width())//2
        py=parent.winfo_y()+(parent.winfo_height()-self.winfo_height())//2
        self.geometry(f"+{px}+{py}")

    def _actualizar_btn(self,_=None):
        n=len(self.tbl.selection())
        self.btn_abrir.config(text=f"Combinar {n} versiones →" if n>=2 else "Abrir seleccionada")

    def _leer_notas(self,carpeta):
        notas={}; ruta=carpeta/"variaciones.txt"
        if not ruta.exists(): return notas
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            partes=linea.split("  —  ")
            if partes: notas[partes[0].strip()]=partes[-1].strip() if len(partes)>=3 else ""
        return notas

    def _abrir(self):
        sel=self.tbl.selection()
        if not sel: return
        self.seleccionados=[Path(s) for s in sel]; self.destroy()


if __name__ == "__main__":
    app = AppPrincipal()
    app.mainloop()
