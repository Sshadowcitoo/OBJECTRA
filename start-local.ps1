param([string]$Python = "$PSScriptRoot/.venv/Scripts/python.exe")
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $Python)) { throw 'Prepara .venv según README.md.' }
Remove-Item Env:LOCAL_SQLITE -ErrorAction SilentlyContinue
Push-Location $PSScriptRoot
try {
    & $Python manage.py check_database --require-postgresql
    if ($LASTEXITCODE -ne 0) { throw 'Revisa PostgreSQL y .local/database.json.' }
    & $Python manage.py migrate
    if ($LASTEXITCODE -ne 0) { throw 'No se pudieron aplicar las migraciones.' }
    & $Python manage.py runserver 127.0.0.1:8000 --noreload
} finally { Pop-Location }
