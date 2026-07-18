"""
main.py  —  Pantalla principal del sistema de Costos de Construcción.
Ejecutar: python main.py  (desde la carpeta Scripts)
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path

# Agregar carpeta raíz al path para imports
sys.path.insert(0, str(Path(__file__).parent))

from core.obra import listar_obras, Obra
from ui.dialogo_nueva_obra import DialogoNuevaObra
from ui.ventana_obra import VentanaObra
from cierre_de_dia import cierre as _cierre_de_dia


TITULO_APP = "Costos de Construcción"
COLOR_HEADER = "#1a3a5c"
COLOR_BTN_NUEVO = "#1d7a4a"
COLOR_BTN_ABRIR = "#1a5c9e"
COLOR_BTN_ELIM  = "#b03030"
COLOR_BTN_TEXTO = "white"


class AppPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(TITULO_APP)
        self.geometry("780x520")
        self.minsize(640, 400)
        self.configure(bg="#f0f0f0")
        self._build_menu()
        self._build_ui()
        self.actualizar_lista()

    # ── Menú principal ────────────────────────────────────────────────────
    def _build_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        men_her = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Herramientas", menu=men_her)
        men_her.add_command(
            label="Cierre de día  (backup + GitHub)",
            command=lambda: _cierre_de_dia(parent_window=self)
        )

    # ── Construcción de la UI ──────────────────────────────────────────────
    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg=COLOR_HEADER, height=56)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="  Costos de Construcción",
                 bg=COLOR_HEADER, fg="white",
                 font=("Segoe UI", 16, "bold")).pack(side="left", padx=12, pady=10)

        # Barra de botones
        barra = tk.Frame(self, bg="#e0e0e0", pady=8)
        barra.pack(fill="x", padx=0)

        self._btn(barra, "Nueva obra", COLOR_BTN_NUEVO, self.nueva_obra).pack(side="left", padx=(12, 4))
        self._btn(barra, "Abrir obra", COLOR_BTN_ABRIR, self.abrir_obra).pack(side="left", padx=4)
        self._btn(barra, "Eliminar obra", COLOR_BTN_ELIM, self.eliminar_obra).pack(side="left", padx=4)
        self._btn(barra, "↑ BackUp", "#555555", self.hacer_backup).pack(side="left", padx=(16, 4))

        # Tabla de obras
        frame_tabla = tk.Frame(self, bg="#f0f0f0")
        frame_tabla.pack(fill="both", expand=True, padx=16, pady=(12, 16))

        cols = ("numero", "nombre", "ubicacion", "comitente", "fecha")
        self.tabla = ttk.Treeview(frame_tabla, columns=cols, show="headings",
                                  selectmode="browse")

        encabezados = {
            "numero":    ("Nro",       60),
            "nombre":    ("Nombre",   240),
            "ubicacion": ("Ubicación",180),
            "comitente": ("Comitente",160),
            "fecha":     ("Creación",  90),
        }
        for col, (texto, ancho) in encabezados.items():
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=ancho, minwidth=40)

        scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical",
                                 command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll_y.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        # Doble clic = abrir
        self.tabla.bind("<Double-1>", lambda e: self.abrir_obra())

        # Estilo de filas alternas
        self.tabla.tag_configure("par",   background="#ffffff")
        self.tabla.tag_configure("impar", background="#eaf2fb")

        # Barra de estado
        self.lbl_estado = tk.Label(self, text="", bg="#e0e0e0",
                                   fg="#444", font=("Segoe UI", 9),
                                   anchor="w", padx=12, pady=4)
        self.lbl_estado.pack(fill="x", side="bottom")

    def _btn(self, parent, texto, color, comando):
        return tk.Button(parent, text=texto, bg=color, fg=COLOR_BTN_TEXTO,
                         font=("Segoe UI", 10, "bold"),
                         relief="flat", padx=14, pady=6,
                         cursor="hand2", activebackground=color,
                         activeforeground="white", command=comando)

    # ── Datos ──────────────────────────────────────────────────────────────
    def actualizar_lista(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        obras = listar_obras()
        for i, o in enumerate(obras):
            tag = "par" if i % 2 == 0 else "impar"
            self.tabla.insert("", "end", iid=o["numero"], tags=(tag,),
                              values=(
                                  o["numero"],
                                  o["nombre"],
                                  o.get("ubicacion", ""),
                                  o.get("comitente", ""),
                                  o.get("fecha_creacion", ""),
                              ))
        n = len(obras)
        self.lbl_estado.config(
            text=f"  {n} obra{'s' if n != 1 else ''} registrada{'s' if n != 1 else ''}"
        )

    def _obra_seleccionada(self) -> str | None:
        sel = self.tabla.selection()
        return sel[0] if sel else None

    # ── Acciones ───────────────────────────────────────────────────────────
    def nueva_obra(self):
        dlg = DialogoNuevaObra(self)
        self.wait_window(dlg)
        if dlg.obra_creada:
            self.actualizar_lista()
            num = dlg.obra_creada.numero
            if self.tabla.exists(num):
                self.tabla.selection_set(num)
                self.tabla.see(num)
            self.abrir_obra(obra=dlg.obra_creada)

    def abrir_obra(self, obra: Obra = None):
        if obra is None:
            num = self._obra_seleccionada()
            if not num:
                messagebox.showinfo("Sin selección",
                                    "Seleccioná una obra de la lista.",
                                    parent=self)
                return
            try:
                from pathlib import Path
                from core.obra import CARPETA_OBRAS
                carpeta_data = CARPETA_OBRAS / f"Obra{num}" / "data"
                jsons = sorted(carpeta_data.glob("obra???.json"))
                if len(jsons) > 1:
                    dlg = _DlgVersiones(self, num, jsons)
                    self.wait_window(dlg)
                    if not dlg.seleccionados:
                        return
                    for ruta in dlg.seleccionados:
                        obra = Obra.cargar_version(ruta)
                        VentanaObra(self, obra)
                    return
                else:
                    obra = Obra.cargar(num)
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=self)
                return
        VentanaObra(self, obra)

    def eliminar_obra(self):
        num = self._obra_seleccionada()
        if not num:
            messagebox.showinfo("Sin selección",
                                "Seleccioná una obra para eliminar.",
                                parent=self)
            return
        try:
            obra = Obra.cargar(num)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)
            return

        ok = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Eliminás la obra {obra.titulo}?\n\n"
            "Se borrará la carpeta completa y todos sus datos.\n"
            "Esta acción no se puede deshacer.",
            icon="warning", parent=self
        )
        if ok:
            obra.eliminar()
            self.actualizar_lista()

    def hacer_backup(self):
        """Copia Datos_Obras.db y hace commit+push a GitHub."""
        import shutil
        from core.obra import CARPETA_DATA

        # Copia local de seguridad de Datos_Obras.db
        origen  = CARPETA_DATA / "Datos_Obras.db"
        destino = CARPETA_DATA / "Datos_Obras_BUP.db"
        try:
            shutil.copy2(str(origen), str(destino))
        except Exception as e:
            messagebox.showerror("Error en backup", f"No se pudo copiar la DB:\n{e}", parent=self)
            return

        # Commit + push
        _cierre_de_dia(parent_window=self)


class _DlgVersiones(tk.Toplevel):
    """Diálogo para elegir una o varias versiones de una obra."""
    def __init__(self, parent, numero: str, jsons: list):
        super().__init__(parent)
        self.title(f"Versiones — Obra {numero}")
        self.geometry("520x340")
        self.minsize(420, 240)
        self.resizable(True, True)
        self.grab_set()
        self.seleccionados = []

        hdr = tk.Frame(self, bg=COLOR_HEADER, height=40)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text=f"  Versiones de la Obra {numero}",
                 bg=COLOR_HEADER, fg="white",
                 font=("Segoe UI", 11, "bold")).pack(side="left", padx=12)

        tk.Label(self,
                 text="Seleccioná una o más versiones (Shift / Ctrl) y hacé clic en Abrir:",
                 font=("Segoe UI", 9), fg="#555", bg="#f5f5f5",
                 anchor="w", padx=12, pady=6).pack(fill="x")

        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True, padx=12, pady=(0, 6))

        cols = ("archivo", "version", "fecha", "nota")
        self.tbl = ttk.Treeview(frame, columns=cols, show="headings",
                                selectmode="extended")
        self.tbl.heading("archivo", text="Archivo")
        self.tbl.heading("version", text="Versión")
        self.tbl.heading("fecha",   text="Fecha creación")
        self.tbl.heading("nota",    text="Nota")
        self.tbl.column("archivo",  width=120, minwidth=80)
        self.tbl.column("version",  width=60,  minwidth=40, anchor="center")
        self.tbl.column("fecha",    width=100, minwidth=80, anchor="center")
        self.tbl.column("nota",     width=200, minwidth=80)

        scr = ttk.Scrollbar(frame, orient="vertical", command=self.tbl.yview)
        self.tbl.configure(yscrollcommand=scr.set)
        scr.pack(side="right", fill="y")
        self.tbl.pack(side="left", fill="both", expand=True)

        self.tbl.tag_configure("par",   background="#ffffff")
        self.tbl.tag_configure("impar", background="#eaf2fb")
        self.tbl.tag_configure("last",  background="#d4edda")

        import json as _json
        notas = self._leer_notas(jsons[0].parent)

        for i, j in enumerate(jsons):
            try:
                with open(j, encoding="utf-8") as f:
                    d = _json.load(f)
                ver   = d.get("version", i)
                fecha = d.get("fecha_creacion", "")
            except Exception:
                ver, fecha = i, ""
            nota = notas.get(j.name, "")
            es_ultima = (i == len(jsons) - 1)
            tag = "last" if es_ultima else ("par" if i % 2 == 0 else "impar")
            self.tbl.insert("", "end", iid=str(j), tags=(tag,),
                            values=(j.name, ver, fecha, nota))

        if jsons:
            self.tbl.selection_set(str(jsons[-1]))
            self.tbl.see(str(jsons[-1]))

        self.tbl.bind("<Double-1>", lambda _: self._abrir())

        frm_btn = tk.Frame(self, pady=8)
        frm_btn.pack(fill="x", padx=12)
        tk.Button(frm_btn, text="Abrir seleccionadas",
                  bg=COLOR_BTN_ABRIR, fg="white",
                  font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=14, pady=6, cursor="hand2",
                  command=self._abrir).pack(side="right", padx=(4, 0))
        tk.Button(frm_btn, text="Cancelar",
                  bg="#888", fg="white",
                  font=("Segoe UI", 10),
                  relief="flat", padx=14, pady=6, cursor="hand2",
                  command=self.destroy).pack(side="right")

        self.bind("<Return>", lambda _: self._abrir())
        self.bind("<Escape>", lambda _: self.destroy())
        self.update_idletasks()
        px = parent.winfo_x() + (parent.winfo_width()  - self.winfo_width())  // 2
        py = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{px}+{py}")

    def _leer_notas(self, carpeta) -> dict:
        notas = {}
        ruta = carpeta / "variaciones.txt"
        if not ruta.exists():
            return notas
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            partes = linea.split("  —  ")
            if partes:
                archivo = partes[0].strip()
                nota = partes[-1].strip() if len(partes) >= 3 else ""
                notas[archivo] = nota
        return notas

    def _abrir(self):
        sel = self.tbl.selection()
        if not sel:
            return
        self.seleccionados = [Path(s) for s in sel]
        self.destroy()


if __name__ == "__main__":
    app = AppPrincipal()
    app.mainloop()
