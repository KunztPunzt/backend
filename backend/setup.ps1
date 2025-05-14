<#
.SYNOPSIS
   Crea o activa un virtualenv en .\venv y, si corresponde, instala dependencias.
.PARAMETER Path
   Ruta al proyecto.
.PARAMETER EnvName
   Nombre de la carpeta para el entorno.
#>
param(
  [string]$Path    = "D:\Code Snippets\Python\FastAPI\2025\Yavanna\backend",
  [string]$EnvName = "venv"
)



Push-Location $Path
$YavannaDir = Split-Path -Path $Path -Parent
Write-Host "📂 Proyecto en: $Path"
Write-Host "📂 Carpeta Yavanna en: $YavannaDir"



if (Test-Path -Path "$Path\$EnvName") {
    Write-Host "✅ venv ya existe. Activando..."
} else {
    Write-Host "🛠️ Creando venv en '$EnvName'..."
    python -m venv $EnvName
}



Write-Host "🔑 Activando entorno virtual..."
. "$Path\$EnvName\Scripts\Activate.ps1"



if ( (Test-Path -Path "$Path\$EnvName") -and (Test-Path -Path $YavannaDir) ) {
    Write-Host "📦 venv y Yavanna detectados. Instalando dependencias..."


    Set-Location $YavannaDir


    Write-Host "⬆️  Actualizando pip..."
    python -m pip install --upgrade pip


    Write-Host "🔍 Leyendo lista de paquetes instalados..."
    $installedPackages    = python -m pip list --format=json | ConvertFrom-Json
    $installedNames       = $installedPackages | Select-Object -ExpandProperty name

    $normalizedInstalled  = $installedNames |
        ForEach-Object { $_.ToLower().Replace('_','-') }
    $packages = @(
        "fastapi",
        "uvicorn[standard]",
        "python-dotenv",
        "pydantic",
        "email-validator",
        "sqlalchemy",
        "pyodbc",
        "python-jose",
        "passlib[bcrypt]"
    )

    foreach ($pkg in $packages) {
        $baseName        = $pkg.Split('[')[0]
        $normalizedBase  = $baseName.ToLower()

        if ($normalizedInstalled -contains $normalizedBase) {
            Write-Host "   ✅ $baseName ya instalado; omitiendo."
        } else {
            Write-Host "   ➕ Instalando $pkg..."
            python -m pip install $pkg
        }
    }

    Write-Host "🎉 ¡Todo listo! Entorno y dependencias configurados."
    Set-Location $Path
} else {
    Write-Host "⏭️ Saltando instalación de dependencias (no se detecta venv o carpeta Yavanna)."
}

Pop-Location

Write-Host "📂 Volviendo al directorio Yavanna..."
Set-Location $YavannaDir
