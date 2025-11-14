@echo off
REM Setup con Entorno Virtual - Windows CMD
REM Ejecuta este script para configurar el proyecto completo

echo ========================================
echo   PC Price Scraper - Setup Completo
echo ========================================
echo.

REM Verificar Python
echo 1. Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo    X Python no encontrado. Por favor instala Python 3.8+
    pause
    exit /b 1
)
echo    √ Python encontrado

REM Crear entorno virtual
echo.
echo 2. Creando entorno virtual...
if exist venv (
    echo    ! Entorno virtual ya existe
    set /p response="   ¿Deseas recrearlo? (s/n): "
    if /i "%response%"=="s" (
        rmdir /s /q venv
        python -m venv venv
        echo    √ Entorno virtual recreado
    )
) else (
    python -m venv venv
    echo    √ Entorno virtual creado
)

REM Activar entorno virtual
echo.
echo 3. Activando entorno virtual...
call venv\Scripts\activate.bat
echo    √ Entorno virtual activado

REM Actualizar pip
echo.
echo 4. Actualizando pip...
python -m pip install --upgrade pip >nul 2>&1
echo    √ pip actualizado

REM Instalar dependencias
echo.
echo 5. Instalando dependencias...
echo    (Esto puede tomar un momento...)
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo    X Error instalando dependencias
    pause
    exit /b 1
)
echo    √ Dependencias instaladas

REM Crear archivo .env
echo.
echo 6. Configurando environment...
if not exist .env (
    copy .env.example .env >nul
    echo    √ Archivo .env creado
) else (
    echo    ! Archivo .env ya existe
)

REM Crear directorio de logs
echo.
echo 7. Creando directorios...
if not exist logs mkdir logs
echo    √ Directorio logs creado

REM Inicializar base de datos
echo.
echo 8. Inicializando base de datos...
set /p response="   ¿Deseas inicializar la base de datos ahora? (s/n): "
if /i "%response%"=="s" (
    python setup.py
) else (
    echo    ⏩ Inicialización omitida
    echo    Ejecuta 'python setup.py' cuando estés listo
)

REM Resumen final
echo.
echo ========================================
echo   √ Setup Completado
echo ========================================
echo.
echo Próximos pasos:
echo.
echo 1. Para activar el entorno virtual:
echo    venv\Scripts\activate.bat
echo.
echo 2. Para iniciar el servidor:
echo    python main.py
echo.
echo 3. Para ejecutar tests:
echo    python test_scrapers.py
echo.
echo 4. Documentación:
echo    - START_HERE.md - Guía de inicio
echo    - MOBILE_API_GUIDE.md - Para iOS
echo    - http://localhost:8000/docs - API Docs
echo.
echo ¡Feliz scraping! 🎉
echo.
pause
