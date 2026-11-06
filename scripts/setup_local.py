"""Prepare the local PostgreSQL configuration and validate model exports."""

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

import psycopg

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / ".local" / "database.json"
MODELS = (
    "yolo11s-seg-eva-320_openvino_model",
    "yolo11s-seg-eva-480_openvino_model",
    "yolo11s-seg_openvino_model",
)


def model_ready(folder):
    return (folder / "metadata.yaml").is_file() and any(
        xml.is_file() and xml.with_suffix(".bin").is_file()
        for xml in folder.glob("*.xml")
    )


def prepare_models(source):
    pending = []
    for name in MODELS:
        destination = ROOT / "models" / name
        if model_ready(destination):
            continue
        if destination.exists():
            raise SystemExit(f"Exportación incompleta en {destination}. Corrígela o muévela para continuar.")
        if source is None or not model_ready(source / name):
            raise SystemExit(f"Falta la exportación de EVA {name}. Usa -ModelsSource con la carpeta de modelos del paquete.")
        pending.append(name)

    if not pending:
        return

    with TemporaryDirectory(dir=ROOT / "models") as temporary:
        stage = Path(temporary)
        for name in pending:
            shutil.copytree(source / name, stage / name)
            if not model_ready(stage / name):
                raise SystemExit(f"La copia de {name} quedó incompleta.")
        for name in pending:
            (stage / name).rename(ROOT / "models" / name)


def database_options(config):
    return {
        key.lower(): os.environ.get(f"DB_{key}", config.get(f"DB_{key}", ""))
        for key in ("HOST", "PORT", "USER", "PASSWORD")
    }


def check_databases(options, names):
    for name in names:
        with psycopg.connect(dbname=name, connect_timeout=5, **options) as connection:
            connection.execute("SELECT 1").fetchone()


def prepare_database():
    existing_config = CONFIG.exists()
    if not existing_config and not any(key in os.environ for key in ("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD")):
        from portable_postgres import prepare

        config = prepare()
        with CONFIG.open("x", encoding="utf-8") as file:
            json.dump(config, file, ensure_ascii=False, indent=2)
            file.write("\n")
        print("PostgreSQL local preparado para OBJECTRA.")
        return

    path = CONFIG if existing_config else ROOT / ".local.example" / "database.json"
    config = json.loads(path.read_text(encoding="utf-8-sig"))
    options = database_options(config)
    name = os.environ.get("DB_NAME", config["DB_NAME"])
    names = (name, f"test_{name}")
    portable_started = False
    if options["port"] == "55432" and (ROOT / ".local/postgresql-data/PG_VERSION").is_file():
        from portable_postgres import start, stop

        portable_started = start()
    try:
        check_databases(options, names)
    finally:
        if portable_started:
            stop()

    print("Conexión PostgreSQL comprobada para la aplicación y las pruebas.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models-source", type=Path)
    args = parser.parse_args()
    try:
        prepare_models(args.models_source)
        prepare_database()
    except (OSError, ValueError, KeyError, psycopg.Error, subprocess.CalledProcessError) as error:
        raise SystemExit(f"No se pudo completar la instalación: {error}") from None
