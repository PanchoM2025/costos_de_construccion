"""
cierre_de_dia.py
Backup del proyecto: git add -A + commit con timestamp + push a GitHub.
Llamado desde el menú de la app o directamente: python cierre_de_dia.py
"""
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Raíz del proyecto (un nivel arriba de Scripts/)
RAIZ = Path(__file__).resolve().parent.parent


def _run(*cmd):
    return subprocess.run(
        list(cmd), cwd=str(RAIZ),
        capture_output=True, text=True, encoding="utf-8"
    )


def cierre(parent_window=None):
    """
    Hace git add -A, commit con timestamp y push.
    parent_window: ventana Tkinter padre para messageboxes (None si se corre solo).
    """
    import tkinter as tk
    from tkinter import messagebox

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    msg_commit = f"Cierre {timestamp}"

    # Si no hay ventana padre, crear una raíz oculta
    _root_temporal = None
    if parent_window is None:
        _root_temporal = tk.Tk()
        _root_temporal.withdraw()
        parent = _root_temporal
    else:
        parent = parent_window

    try:
        # 1. Verificar que hay repo git
        r = _run("git", "status")
        if r.returncode != 0:
            messagebox.showerror(
                "Git no iniciado",
                "No hay repositorio git en la carpeta del proyecto.\n\n"
                "Ejecutá primero el script de setup:\n"
                "  Scripts\\setup_git.bat",
                parent=parent)
            return

        # 2. git add -A
        r = _run("git", "add", "-A")
        if r.returncode != 0:
            messagebox.showerror("Error — git add", r.stderr or r.stdout, parent=parent)
            return

        # 3. Verificar si hay cambios reales
        status = _run("git", "status", "--short")
        if not status.stdout.strip():
            messagebox.showinfo(
                "Sin cambios",
                "No hay cambios nuevos para commitear.\nEl proyecto ya está al día.",
                parent=parent)
            return

        # Mostrar resumen de archivos modificados
        lineas = status.stdout.strip().splitlines()
        resumen = "\n".join(lineas[:12])
        if len(lineas) > 12:
            resumen += f"\n... y {len(lineas)-12} archivos más"

        # 4. git commit
        r = _run("git", "commit", "-m", msg_commit)
        if r.returncode != 0:
            messagebox.showerror("Error — git commit", r.stderr or r.stdout, parent=parent)
            return

        # 5. git push
        r = _run("git", "push")
        push_ok = r.returncode == 0
        push_msg = r.stdout.strip() or r.stderr.strip()

        if push_ok:
            messagebox.showinfo(
                "Cierre de día — OK",
                f"✓ Commit realizado: {msg_commit}\n\n"
                f"Archivos guardados:\n{resumen}\n\n"
                f"✓ Push a GitHub exitoso.",
                parent=parent)
        else:
            messagebox.showwarning(
                "Cierre de día — Push falló",
                f"✓ Commit realizado: {msg_commit}\n\n"
                f"✗ Push falló. Podés subirlo manualmente.\n\n{push_msg}",
                parent=parent)

    finally:
        if _root_temporal:
            _root_temporal.destroy()


if __name__ == "__main__":
    cierre()
