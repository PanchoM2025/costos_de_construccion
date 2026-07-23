"""
cierre_de_dia.py
Backup del proyecto: git add -A + commit con timestamp + push a GitHub.
Llamado desde el menú de la app o directamente: python cierre_de_dia.py
"""
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

# Raíz del proyecto (un nivel arriba de Scripts/)
RAIZ = Path(__file__).resolve().parent.parent


def _encontrar_git() -> str:
    """Devuelve la ruta completa a git.exe, o None si no se encuentra."""
    # 1. Buscar en el PATH del sistema
    git = shutil.which("git")
    if git:
        return git
    # 2. Ubicaciones típicas en Windows
    candidatos = [
        r"C:\Program Files\Git\cmd\git.exe",
        r"C:\Program Files\Git\bin\git.exe",
        r"C:\Program Files (x86)\Git\cmd\git.exe",
        r"C:\Users\{}\AppData\Local\Programs\Git\cmd\git.exe".format(
            __import__("os").environ.get("USERNAME", "")
        ),
    ]
    for c in candidatos:
        if Path(c).exists():
            return c
    return None


def _run(git_exe: str, *args):
    """Ejecuta un comando git usando la ruta completa al ejecutable."""
    try:
        return subprocess.run(
            [git_exe] + list(args),
            cwd=str(RAIZ),
            capture_output=True,
            text=True,
            encoding="utf-8",
            creationflags=0x08000000,  # CREATE_NO_WINDOW
        )
    except Exception as e:
        class _Falso:
            returncode = -1
            stdout = ""
            stderr = str(e)
        return _Falso()


def cierre(parent_window=None):
    """
    Hace git add -A, commit con timestamp y push.
    parent_window: ventana Tkinter padre para messageboxes (None si se corre solo).
    """
    import tkinter as tk
    from tkinter import messagebox

    timestamp  = datetime.now().strftime("%Y-%m-%d %H:%M")
    msg_commit = f"Cierre {timestamp}"

    _root_temporal = None
    if parent_window is None:
        _root_temporal = tk.Tk()
        _root_temporal.withdraw()
        parent = _root_temporal
    else:
        parent = parent_window

    try:
        # 0. Encontrar git
        git = _encontrar_git()
        if not git:
            messagebox.showerror(
                "Git no encontrado",
                "No se encontró git.exe en el sistema.\n\n"
                "Instalá Git para Windows desde:\n"
                "  https://git-scm.com/download/win",
                parent=parent)
            return

        # 1. Verificar que hay repo git
        r = _run(git, "status")
        if r.returncode != 0:
            messagebox.showerror(
                "Repositorio no inicializado",
                f"La carpeta no es un repositorio git:\n{RAIZ}\n\n"
                f"Detalle: {r.stderr or r.stdout}",
                parent=parent)
            return

        # 2. git add -A
        r = _run(git, "add", "-A")
        if r.returncode != 0:
            messagebox.showerror("Error — git add",
                                 r.stderr or r.stdout, parent=parent)
            return

        # 3. Verificar si hay cambios para commitear
        status = _run(git, "status", "--short")
        if not status.stdout.strip():
            messagebox.showinfo(
                "Sin cambios",
                "No hay cambios nuevos para commitear.\nEl proyecto ya está al día.",
                parent=parent)
            return

        lineas  = status.stdout.strip().splitlines()
        resumen = "\n".join(lineas[:12])
        if len(lineas) > 12:
            resumen += f"\n... y {len(lineas)-12} archivos más"

        # 4. git commit
        r = _run(git, "commit", "-m", msg_commit)
        if r.returncode != 0:
            messagebox.showerror("Error — git commit",
                                 r.stderr or r.stdout, parent=parent)
            return

        # 5. git push
        r        = _run(git, "push")
        push_ok  = r.returncode == 0
        push_msg = r.stdout.strip() or r.stderr.strip()

        if push_ok:
            messagebox.showinfo(
                "Cierre de día — OK",
                f"✓ Commit: {msg_commit}\n\n"
                f"Archivos guardados:\n{resumen}\n\n"
                f"✓ Push a GitHub exitoso.",
                parent=parent)
        else:
            messagebox.showwarning(
                "Cierre de día — Push falló",
                f"✓ Commit realizado: {msg_commit}\n\n"
                f"✗ Push falló. Podés subirlo manualmente con:\n"
                f"   git push\n\n{push_msg}",
                parent=parent)

    except Exception as e:
        messagebox.showerror(
            "Error inesperado — Cierre de día",
            f"Ocurrió un error:\n{e}",
            parent=parent)
    finally:
        if _root_temporal:
            _root_temporal.destroy()


if __name__ == "__main__":
    cierre()
