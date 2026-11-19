param([string]$Python = "$PSScriptRoot/.venv/Scripts/python.exe")
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $Python)) { throw 'Prepara .venv según README.md.' }
Remove-Item Env:LOCAL_SQLITE -ErrorAction SilentlyContinue
$startedPostgres = $false
Push-Location $PSScriptRoot
try {
    if (Test-Path -LiteralPath '.local/postgresql-data/PG_VERSION') {
        & $Python scripts/portable_postgres.py start
        if ($LASTEXITCODE -notin @(0, 3)) { throw 'No se pudo arrancar PostgreSQL local.' }
        $startedPostgres = $LASTEXITCODE -eq 0
    }
    & $Python manage.py check_database --require-postgresql
    if ($LASTEXITCODE -ne 0) { throw 'Revisa PostgreSQL y .local/database.json.' }
    & $Python manage.py migrate
    if ($LASTEXITCODE -ne 0) { throw 'No se pudieron aplicar las migraciones.' }
    & $Python manage.py runserver 127.0.0.1:8000 --noreload
    if ($LASTEXITCODE -ne 0) { throw 'Django se cerro con un error.' }
} finally {
    try {
        if ($startedPostgres) { & $Python scripts/portable_postgres.py stop }
    } finally {
        Pop-Location
    }
}
