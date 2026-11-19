"""Extract only the PostgreSQL server runtime, excluding pgAdmin and tools."""
import shutil
from pathlib import Path, PurePosixPath


def extract_runtime(package, destination):
    destination = Path(destination)
    roots = []
    for entry in package.infolist():
        parts = PurePosixPath(entry.filename).parts
        if len(parts) >= 2 and parts[-2:] == ("bin", "pg_ctl.exe"):
            roots.append(parts[:-2])
    if len(roots) != 1:
        raise OSError("El paquete debe contener una sola instalacion PostgreSQL con bin/pg_ctl.exe.")
    prefix = roots[0]
    selected = []
    for entry in package.infolist():
        parts = PurePosixPath(entry.filename).parts
        if parts[:len(prefix)] != prefix:
            continue
        relative = parts[len(prefix):]
        if not relative or relative[0] not in ("bin", "lib", "share"):
            continue
        if any(part in ("..", ".") or ":" in part or "\\" in part for part in relative):
            raise OSError("Ruta invalida dentro del paquete PostgreSQL.")
        target = destination.joinpath(*relative)
        if not target.resolve().is_relative_to(destination.resolve()):
            raise OSError("La ruta del paquete sale del directorio de instalacion.")
        selected.append((entry, target))
    for entry, target in selected:
        if entry.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            with package.open(entry) as source, target.open("wb") as output:
                shutil.copyfileobj(source, output)
    for executable in ("pg_ctl.exe", "initdb.exe", "postgres.exe"):
        if not (destination / "bin" / executable).is_file():
            raise OSError(f"El paquete PostgreSQL no contiene {executable}.")
    for folder in ("lib", "share"):
        if not (destination / folder).is_dir():
            raise OSError(f"El paquete PostgreSQL no contiene {folder}.")
