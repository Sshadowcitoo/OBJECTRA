param(
    [string]$ModelsSource,
    [switch]$NoStart
)

$ErrorActionPreference = 'Stop'
if ($ModelsSource) { $ModelsSource = (Resolve-Path -LiteralPath $ModelsSource).Path }

# The same script can also be run from Downloads on a clean PC.
if (-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'manage.py'))) {
    $destination = Join-Path $env:LOCALAPPDATA 'OBJECTRA'
    if (-not (Test-Path -LiteralPath (Join-Path $destination 'manage.py'))) {
        if (Test-Path -LiteralPath $destination) { throw "La carpeta ya existe: $destination" }
        $temp = Join-Path ([IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString())
        New-Item -ItemType Directory -Path $temp | Out-Null
        try {
            $archive = Join-Path $temp 'objectra.zip'
            $source = 'https://github.com/Sshadowcitoo/OBJECTRA/archive/refs/heads/feature/instalador-windows.zip'
            Invoke-WebRequest -UseBasicParsing -Uri $source -OutFile $archive
            Expand-Archive -LiteralPath $archive -DestinationPath $temp
            $project = Get-ChildItem -LiteralPath $temp -Directory | Select-Object -First 1
            if (-not $project -or -not (Test-Path (Join-Path $project.FullName 'manage.py'))) {
                throw 'El archivo descargado no contiene OBJECTRA.'
            }
            Move-Item -LiteralPath $project.FullName -Destination $destination
        } finally {
            Remove-Item -LiteralPath $temp -Recurse -Force
        }
    }
    & (Join-Path $destination 'setup-local.ps1') -ModelsSource $ModelsSource -NoStart:$NoStart
    return
}

function Install-Package([string]$Id, [string[]]$Options) {
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        throw 'Windows necesita App Installer (winget) para instalar los componentes automaticamente.'
    }
    & winget install --id $Id --exact --source winget --silent --no-upgrade --accept-package-agreements --accept-source-agreements @Options
    # WinGet reports this code when the installed package already meets the request.
    if ($LASTEXITCODE -ne 0 -and $LASTEXITCODE -ne -1978335189) {
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
