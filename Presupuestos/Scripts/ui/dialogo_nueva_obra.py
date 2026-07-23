"""
dialogo_nueva_obra.py  —  Formulario para crear una obra nueva.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.obra import Obra

COLOR_HEADER = "#1a3a5c"


class DialogoNuevaObra(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Nueva obra")
        self.resizable(False, False)
        self.grab_set()
        self.obra_creada: Obra | None = None
        self._build_ui()
        self.update_idletasks()          # calcular tamaño real
        self._centrar(parent)

    def _centrar(self, parent):
        w = self.winfo_width()
        h = self.winfo_height()
        px = parent.winfo_x() + (parent.winfo_width()  - w) // 2
        py = parent.winfo_y() + (parent.winfo_height() - h) // 2
        self.geometry(f"{w}x{h}+{px}+{py}")

    def _build_ui(self):
        # ── Cabecera ──────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=COLOR_HEADER, height=46)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="  Nueva obra", bg=COLOR_HEADER, fg="white",
                 font=("Segoe UI", 13, "bold")).pack(side="left", padx=12, pady=8)

        # ── Botones — pack ANTES del form para que siempre sean visibles ──
        frm_btn = tk.Frame(self, pady=12, padx=24)
        frm_btn.pack(side="bottom", fill="x")
        tk.Button(frm_btn, text="Crear obra", bg="#1d7a4a", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat",
                  padx=16, pady=7, cursor="hand2",
                  command=self._confirmar).pack(side="right", padx=(6, 0))
        tk.Button(frm_btn, text="Cancelar", bg="#888", fg="white",
                  font=("Segoe UI", 10), relief="flat",
                  padx=16, pady=7, cursor="hand2",
                  command=self.destroy).pack(side="right")

        ttk.Separator(self, orient="horizontal").pack(side="bottom", fill="x")

        # ── Campos ────────────────────────────────────────────────────────
        frm = tk.Frame(self, padx=28, pady=16)
        frm.pack(fill="both", expand=True)
        frm.columnconfigure(1, weight=1)

        campos = [
            ("Número de obra",       "var_num"),
            ("Nombre / descripción", "var_nom"),
            ("Ubicación",            "var_ubi"),
            ("Comitente",            "var_com"),
        ]
        self.entries = {}
        for i, (label, var_name) in enumerate(campos):
            tk.Label(frm, text=label, font=("Segoe UI", 10),
                     anchor="w").grid(row=i, column=0, sticky="w",
                                      padx=(0, 14), pady=9)
            var = tk.StringVar()
            setattr(self, var_name, var)
            ent = ttk.Entry(frm, textvariable=var, font=("Segoe UI", 10),
                            width=32)
            ent.grid(row=i, column=1, sticky="ew", pady=9)
            self.entries[var_name] = ent

        self.entries["var_num"].focus_set()
        self.bind("<Return>", lambda _: self._confirmar())
        self.bind("<Escape>", lambda _: self.destroy())

    def _confirmar(self):
        num = self.var_num.get().strip()
        nom = self.var_nom.get().strip()
        ubi = self.var_ubi.get().strip()

        if not num:
            messagebox.showwarning("Falta dato", "Ingresá el número de obra.",
                                   parent=self)
            return
        if not nom:
            messagebox.showwarning("Falta dato", "Ingresá el nombre de la obra.",
                                   parent=self)
            return
        if not num.isdigit():
            messagebox.showwarning("Dato inválido", "El número debe ser numérico.",
                                   parent=self)
            return
        if Obra.existe(num):
            ok = messagebox.askyesno(
                "Obra existente",
                f"Ya existe la Obra {num.zfill(3)}.\n¿Querés sobreescribirla?",
                parent=self)
            if not ok:
                return

        com = self.var_com.get().strip()
        obra = Obra(num, nom, ubi)
        obra.comitente = com
        try:
            obra.inicializar()
        except Exception as e:
            messagebox.showerror("Error al guardar", str(e), parent=self)
            return

        self.obra_creada = obra
        self.destroy()
