# Setup con Entorno Virtual - Windows PowerShell
# Ejecuta este script para configurar el proyecto completo

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PC Price Scraper - Setup Completo" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Python
Write-Host "1. Verificando Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Python encontrado: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "   ✗ Python no encontrado. Por favor instala Python 3.8+" -ForegroundColor Red
    exit 1
}

# Crear entorno virtual
Write-Host ""
Write-Host "2. Creando entorno virtual..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "   ⚠ Entorno virtual ya existe" -ForegroundColor Yellow
    $response = Read-Host "   ¿Deseas recrearlo? (s/n)"
    if ($response -eq "s" -or $response -eq "S") {
        Remove-Item -Recurse -Force venv
        python -m venv venv
        Write-Host "   ✓ Entorno virtual recreado" -ForegroundColor Green
    }
} else {
    python -m venv venv
    Write-Host "   ✓ Entorno virtual creado" -ForegroundColor Green
}

# Activar entorno virtual
Write-Host ""
Write-Host "3. Activando entorno virtual..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

if ($LASTEXITCODE -ne 0) {
    Write-Host "   ⚠ Error activando entorno virtual" -ForegroundColor Yellow
    Write-Host "   Si ves error de ejecución de scripts, ejecuta:" -ForegroundColor Yellow
    Write-Host "   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   Luego vuelve a ejecutar este script." -ForegroundColor Yellow
    exit 1
}

Write-Host "   ✓ Entorno virtual activado" -ForegroundColor Green

# Actualizar pip
Write-Host ""
Write-Host "4. Actualizando pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip | Out-Null
Write-Host "   ✓ pip actualizado" -ForegroundColor Green

# Instalar dependencias
Write-Host ""
Write-Host "5. Instalando dependencias..." -ForegroundColor Yellow
Write-Host "   (Esto puede tomar un momento...)" -ForegroundColor Gray
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Dependencias instaladas" -ForegroundColor Green
} else {
    Write-Host "   ✗ Error instalando dependencias" -ForegroundColor Red
    exit 1
}

# Crear archivo .env si no existe
Write-Host ""
Write-Host "6. Configurando environment..." -ForegroundColor Yellow
if (!(Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "   ✓ Archivo .env creado" -ForegroundColor Green
} else {
    Write-Host "   ⚠ Archivo .env ya existe" -ForegroundColor Yellow
}

# Crear directorio de logs
Write-Host ""
Write-Host "7. Creando directorios..." -ForegroundColor Yellow
if (!(Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
    Write-Host "   ✓ Directorio logs creado" -ForegroundColor Green
} else {
    Write-Host "   ⚠ Directorio logs ya existe" -ForegroundColor Yellow
}

# Inicializar base de datos
Write-Host ""
Write-Host "8. Inicializando base de datos..." -ForegroundColor Yellow
$response = Read-Host "   ¿Deseas inicializar la base de datos ahora? (s/n)"
if ($response -eq "s" -or $response -eq "S") {
    python setup.py
} else {
    Write-Host "   ⏩ Inicialización omitida" -ForegroundColor Yellow
    Write-Host "   Ejecuta 'python setup.py' cuando estés listo" -ForegroundColor Gray
}

# Resumen final
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ✓ Setup Completado" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Próximos pasos:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Para activar el entorno virtual:" -ForegroundColor White
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Para iniciar el servidor:" -ForegroundColor White
Write-Host "   python main.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Para ejecutar tests:" -ForegroundColor White
Write-Host "   python test_scrapers.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Documentación:" -ForegroundColor White
Write-Host "   - START_HERE.md - Guía de inicio" -ForegroundColor Gray
Write-Host "   - MOBILE_API_GUIDE.md - Para iOS" -ForegroundColor Gray
Write-Host "   - http://localhost:8000/docs - API Docs" -ForegroundColor Gray
Write-Host ""
Write-Host "¡Feliz scraping! 🎉" -ForegroundColor Green
Write-Host ""
