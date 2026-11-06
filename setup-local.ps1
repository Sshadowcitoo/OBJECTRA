param(
    [string]$ModelsSource,
    [switch]$NoStart
)

$ErrorActionPreference = 'Stop'
$python = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if ($ModelsSource) { $ModelsSource = (Resolve-Path -LiteralPath $ModelsSource).Path }

Push-Location $PSScriptRoot
try {
    if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
        if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
            throw 'Instala Python 3.13 con el lanzador py y vuelve a ejecutar este script.'
        }
        & py -3.13 -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw 'No se pudo crear .venv con Python 3.13.' }
    }

    & $python -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw 'No se pudieron instalar las dependencias.' }

    $setupArgs = @('scripts/setup_local.py')
    if ($ModelsSource) { $setupArgs += @('--models-source', $ModelsSource) }
    & $python @setupArgs
    if ($LASTEXITCODE -ne 0) { throw 'La preparacion de OBJECTRA quedo incompleta. Revisa el mensaje anterior.' }

    if (-not $NoStart) {
        & "$PSScriptRoot/start-local.ps1" -Python $python
        if ($LASTEXITCODE -ne 0) { throw 'OBJECTRA se cerro con un error.' }
    }
} finally {
    Pop-Location
}
