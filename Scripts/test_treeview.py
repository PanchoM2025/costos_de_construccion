"""
test_treeview.py - test minimo para verificar que Treeview funciona
Correr: C:\Python313\python.exe test_treeview.py
"""
import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Test Treeview")
root.geometry("800x500")

nb = ttk.Notebook(root)
nb.pack(fill="both", expand=True, padx=8, pady=8)

tab1 = tk.Frame(nb)
tab2 = tk.Frame(nb)
nb.add(tab1, text="  Tab 1  ")
nb.add(tab2, text="  Tab 2  ")

# Tab 1: boton que carga datos en tab2
datos = [("0110", "Limpieza superficial", "m2"),
         ("0121", "Casilla Obrador", "m2"),
         ("0130", "Cartel de Obra", "gl"),
         ("0140", "Replanteo", "m2")]

def cargar():
    for item in tbl.get_children():
        tbl.delete(item)
    for i, (cod, nom, uni) in enumerate(datos):
        bg = "#d4edda" if i % 2 == 0 else "#f0f4fa"
        tbl.insert("", "end", iid=cod, values=(cod, nom, uni))
    lbl_info.config(text=f"Cargadas {len(datos)} filas")
    nb.select(1)

tk.Button(tab1, text="Cargar tareas en Tab 2",
          font=("Segoe UI", 11, "bold"),
          bg="#1a5c9e", fg="white", relief="flat",
          padx=14, pady=8, command=cargar).pack(pady=30)

# Tab 2: treeview
cols = ("cod", "nombre", "unidad")
tbl = ttk.Treeview(tab2, columns=cols, show="headings", height=15)
tbl.heading("cod",    text="Codigo")
tbl.heading("nombre", text="Nombre")
tbl.heading("unidad", text="Unidad")
tbl.column("cod",    width=80)
tbl.column("nombre", width=400)
tbl.column("unidad", width=80)

scr = ttk.Scrollbar(tab2, orient="vertical", command=tbl.yview)
tbl.configure(yscrollcommand=scr.set)
scr.pack(side="right", fill="y")
tbl.pack(side="left", fill="both", expand=True)

lbl_info = tk.Label(tab2, text="Sin datos", font=("Segoe UI", 10), fg="#555")
lbl_info.pack(anchor="w", padx=8, pady=4)

root.mainloop()
