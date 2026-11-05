from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.utils import Error


class Command(BaseCommand):
    help = "Comprueba la conexión real y el motor de la base de datos sin modificar datos."

    def add_arguments(self, parser):
        parser.add_argument("--require-postgresql", action="store_true")

    def handle(self, *args, **options):
        if options["require_postgresql"] and connection.vendor != "postgresql":
            raise CommandError("OBJECTRA está usando SQLite. Desactiva LOCAL_SQLITE para comprobar PostgreSQL.")
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                if cursor.fetchone()[0] != 1:
                    raise CommandError("La base no respondió correctamente.")
        except Error as exc:
            raise CommandError(
                "No se pudo conectar a la base. Revisa que el servicio esté activo y las variables DB_NAME, DB_USER, DB_PASSWORD, DB_HOST y DB_PORT."
            ) from exc
        self.stdout.write(self.style.SUCCESS(f"Conexión comprobada. Motor: {connection.vendor}."))
