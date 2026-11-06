"""Private PostgreSQL instance for the Windows installer."""

import json
import secrets
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import urlretrieve
from zipfile import ZipFile

import psycopg
from psycopg import sql

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / ".local"
BIN = LOCAL / "postgresql" / "bin"
DATA = LOCAL / "postgresql-data"
ADMIN = LOCAL / "postgresql-admin.json"
PG_URL = "https://get.enterprisedb.com/postgresql/postgresql-17.11-3-windows-x64-binaries.zip"
HOST = "127.0.0.1"
PORT = "55432"


def pg(command, *args, check=True):
    return subprocess.run([str(BIN / f"{command}.exe"), *map(str, args)], check=check)


def start():
    if pg("pg_ctl", "status", "-D", DATA, check=False).returncode == 0:
        return False
    pg("pg_ctl", "start", "-D", DATA, "-l", LOCAL / "postgresql.log", "-w",
       "-o", f"-h {HOST} -p {PORT}")
    return True


def stop():
    pg("pg_ctl", "stop", "-D", DATA, "-m", "fast", "-w")


def prepare():
    LOCAL.mkdir(exist_ok=True)
    if not (BIN / "pg_ctl.exe").is_file():
        print("Descargando PostgreSQL para OBJECTRA…", flush=True)
        with TemporaryDirectory(dir=LOCAL) as directory:
            stage = Path(directory)
            archive = stage / "postgres.zip"
            urlretrieve(PG_URL, archive)
            with ZipFile(archive) as package:
                package.extractall(stage)
            executable = next(stage.glob("**/bin/pg_ctl.exe"), None)
            if executable is None:
                raise OSError("El archivo de PostgreSQL no contiene pg_ctl.exe.")
            executable.parent.parent.rename(BIN.parent)

    if not ADMIN.exists():
        ADMIN.write_text(json.dumps({"admin": secrets.token_urlsafe(32),
                                     "app": secrets.token_urlsafe(32)}), encoding="utf-8")
    passwords = json.loads(ADMIN.read_text(encoding="utf-8"))
    if not (DATA / "PG_VERSION").is_file():
        with TemporaryDirectory(dir=LOCAL) as directory:
            pwfile = Path(directory) / "password"
            pwfile.write_text(passwords["admin"] + "\n", encoding="ascii")
            staged_data = Path(directory) / "data"
            pg("initdb", "-D", staged_data, "-U", "postgres", "--pwfile", pwfile,
               "-A", "scram-sha-256", "-E", "UTF8", "--locale=C")
            staged_data.rename(DATA)

    started = start()
    try:
        with psycopg.connect(dbname="postgres", host=HOST, port=PORT, user="postgres",
                             password=passwords["admin"], connect_timeout=5, autocommit=True) as conn:
            if not conn.execute("SELECT 1 FROM pg_roles WHERE rolname = 'objectra'").fetchone():
                conn.execute(sql.SQL("CREATE ROLE objectra LOGIN PASSWORD {}").format(
                    sql.Literal(passwords["app"])
                ))
            for name in ("objectra", "test_objectra"):
                if not conn.execute("SELECT 1 FROM pg_database WHERE datname = %s", (name,)).fetchone():
                    conn.execute(sql.SQL("CREATE DATABASE {} OWNER objectra").format(sql.Identifier(name)))
                with psycopg.connect(dbname=name, host=HOST, port=PORT, user="objectra",
                                     password=passwords["app"], connect_timeout=5) as app:
                    app.execute("SELECT 1").fetchone()
    finally:
        if started:
            stop()

    return {"DB_NAME": "objectra", "DB_USER": "objectra", "DB_PASSWORD": passwords["app"],
            "DB_HOST": HOST, "DB_PORT": PORT}


if __name__ == "__main__":
    import sys

    if sys.argv[1] == "start":
        sys.exit(0 if start() else 3)
    stop()
