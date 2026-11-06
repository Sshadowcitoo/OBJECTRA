"""Prepare the local PostgreSQL configuration and validate model exports."""

import argparse
import getpass
import json
import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

import psycopg
from psycopg import sql

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
    missing = []
    for name in MODELS:
        destination = ROOT / "models" / name
        if not destination.exists() and source and model_ready(source / name):
            with TemporaryDirectory(dir=destination.parent) as temporary:
                staged = Path(temporary) / name
                shutil.copytree(source / name, staged)
                staged.rename(destination)
        if not model_ready(destination):
            missing.append(name)
    if missing:
        raise SystemExit(
            "Faltan exportaciones completas (.xml, .bin y metadata.yaml) en models/:\n"
            + "\n".join(f"  {name}" for name in missing)
            + "\nCópialas ahí o vuelve a ejecutar con -ModelsSource."
        )


def database_options(config):
    return {
        key.lower(): os.environ.get(f"DB_{key}", config[f"DB_{key}"])
        for key in ("HOST", "PORT", "USER", "PASSWORD")
    }


def check_databases(options, names):
    for name in names:
        with psycopg.connect(dbname=name, connect_timeout=5, **options) as connection:
            connection.execute("SELECT 1").fetchone()


def provision_databases(options, names):
    user = options["user"]
    admin = input("Usuario administrador de PostgreSQL [postgres]: ").strip() or "postgres"
    password = getpass.getpass(f"Contraseña de {admin}: ")
    with psycopg.connect(
        dbname="postgres", host=options["host"], port=options["port"],
        user=admin, password=password, connect_timeout=5, autocommit=True,
    ) as connection:
        if not connection.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (user,)).fetchone():
            connection.execute(
                sql.SQL("CREATE ROLE {} LOGIN PASSWORD {}").format(
                    sql.Identifier(user), sql.Literal(options["password"]),
                )
            )
        for name in names:
            if not connection.execute("SELECT 1 FROM pg_database WHERE datname = %s", (name,)).fetchone():
                connection.execute(
                    sql.SQL("CREATE DATABASE {} OWNER {}").format(
                        sql.Identifier(name), sql.Identifier(user),
                    )
                )


def prepare_database():
    existing_config = CONFIG.exists()
    path = CONFIG if existing_config else ROOT / ".local.example" / "database.json"
    config = json.loads(path.read_text(encoding="utf-8-sig"))
    if not existing_config and "DB_PASSWORD" not in os.environ:
        config["DB_PASSWORD"] = getpass.getpass(
            "Contraseña del rol de OBJECTRA (elige una si es nuevo): "
        )
        if not config["DB_PASSWORD"]:
            raise SystemExit("La contraseña del rol de OBJECTRA no puede quedar vacía.")

    options = database_options(config)
    name = os.environ.get("DB_NAME", config["DB_NAME"])
    names = (name, f"test_{name}")
    try:
        check_databases(options, names)
    except psycopg.OperationalError as error:
        print(f"No se pudo conectar como {options['user']} a las dos bases.\n{error}")
        answer = input("¿Crear el rol y las bases que falten con un administrador local? [s/N]: ")
        if answer.strip().lower() != "s":
            raise SystemExit("Revisa la conexión de PostgreSQL y vuelve a ejecutar el instalador.")
        try:
            provision_databases(options, names)
        except psycopg.Error:
            raise SystemExit(
                "No se pudieron crear el rol y las bases. Revisa el servicio, "
                "las credenciales y los permisos del administrador de PostgreSQL."
            ) from None
        check_databases(options, names)

    if not existing_config:
        config.update({f"DB_{key.upper()}": value for key, value in options.items()})
        config["DB_NAME"] = name
        CONFIG.parent.mkdir(exist_ok=True)
        with CONFIG.open("x", encoding="utf-8") as file:
            json.dump(config, file, ensure_ascii=False, indent=2)
            file.write("\n")
    print("Conexión PostgreSQL comprobada para la aplicación y las pruebas.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models-source", type=Path)
    args = parser.parse_args()
    try:
        prepare_models(args.models_source)
        prepare_database()
    except (OSError, ValueError, KeyError, psycopg.Error) as error:
        raise SystemExit(f"No se pudo completar la instalación: {error}") from None
