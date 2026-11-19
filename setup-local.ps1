param(
    [string]$ModelsSource,
    [switch]$NoStart
)

$ErrorActionPreference = 'Stop'
if ($ModelsSource) { $ModelsSource = (Resolve-Path -LiteralPath $ModelsSource).Path }

if (-not [Environment]::Is64BitOperatingSystem) {
    throw 'OBJECTRA requiere Windows de 64 bits.'
}
if (-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'manage.py'))) {
    throw 'Extrae el proyecto completo y ejecuta setup-local.ps1 desde su carpeta raiz.'
}

function Install-Package([string]$Id, [string[]]$Options) {
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        throw 'Windows necesita App Installer (winget) para instalar los componentes automaticamente.'
    }
    & winget install --id $Id --exact --source winget --silent --no-upgrade --accept-package-agreements --accept-source-agreements @Options
    # WinGet reports this code when the installed package already meets the request.
    if ($LASTEXITCODE -ne 0 -and $LASTEXITCODE -ne -1978335135) {
        throw "No se pudo instalar $Id (codigo $LASTEXITCODE)."
    }
}

$python = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
Push-Location $PSScriptRoot
try {
    if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
        Install-Package -Id 'Microsoft.VCRedist.2015+.x64'
        $installedPython = Join-Path $env:LOCALAPPDATA 'Programs/Python/Python313/python.exe'
        $launcher = Get-Command py -ErrorAction SilentlyContinue
        if ($launcher) {
            & py -3.13 -c 'import sys; print(sys.executable)'
        }
        if (-not $launcher -or $LASTEXITCODE -ne 0) {
            if (-not (Test-Path -LiteralPath $installedPython)) {
                Install-Package -Id 'Python.Python.3.13' -Options @('--scope', 'user')
            }
            & $installedPython -m venv .venv
        } else {
            & py -3.13 -m venv .venv
        }
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
