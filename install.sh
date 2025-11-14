#!/bin/bash
# Setup con Entorno Virtual - Linux/macOS
# Ejecuta este script para configurar el proyecto completo

echo "========================================"
echo "  PC Price Scraper - Setup Completo"
echo "========================================"
echo ""

# Verificar Python
echo "1. Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✓ Python encontrado: $PYTHON_VERSION"
else
    echo "   ✗ Python no encontrado. Por favor instala Python 3.8+"
    exit 1
fi

# Crear entorno virtual
echo ""
echo "2. Creando entorno virtual..."
if [ -d "venv" ]; then
    echo "   ⚠ Entorno virtual ya existe"
    read -p "   ¿Deseas recrearlo? (s/n): " response
    if [ "$response" = "s" ] || [ "$response" = "S" ]; then
        rm -rf venv
        python3 -m venv venv
        echo "   ✓ Entorno virtual recreado"
    fi
else
    python3 -m venv venv
    echo "   ✓ Entorno virtual creado"
fi

# Activar entorno virtual
echo ""
echo "3. Activando entorno virtual..."
source venv/bin/activate
echo "   ✓ Entorno virtual activado"

# Actualizar pip
echo ""
echo "4. Actualizando pip..."
python -m pip install --upgrade pip > /dev/null 2>&1
echo "   ✓ pip actualizado"

# Instalar dependencias
echo ""
echo "5. Instalando dependencias..."
echo "   (Esto puede tomar un momento...)"
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "   ✓ Dependencias instaladas"
else
    echo "   ✗ Error instalando dependencias"
    exit 1
fi

# Crear archivo .env
echo ""
echo "6. Configurando environment..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "   ✓ Archivo .env creado"
else
    echo "   ⚠ Archivo .env ya existe"
fi

# Crear directorio de logs
echo ""
echo "7. Creando directorios..."
if [ ! -d "logs" ]; then
    mkdir logs
    echo "   ✓ Directorio logs creado"
else
    echo "   ⚠ Directorio logs ya existe"
fi

# Inicializar base de datos
echo ""
echo "8. Inicializando base de datos..."
read -p "   ¿Deseas inicializar la base de datos ahora? (s/n): " response
if [ "$response" = "s" ] || [ "$response" = "S" ]; then
    python setup.py
else
    echo "   ⏩ Inicialización omitida"
    echo "   Ejecuta 'python setup.py' cuando estés listo"
fi

# Resumen final
echo ""
echo "========================================"
echo "  ✓ Setup Completado"
echo "========================================"
echo ""
echo "Próximos pasos:"
echo ""
echo "1. Para activar el entorno virtual:"
echo "   source venv/bin/activate"
echo ""
echo "2. Para iniciar el servidor:"
echo "   python main.py"
echo ""
echo "3. Para ejecutar tests:"
echo "   python test_scrapers.py"
echo ""
echo "4. Documentación:"
echo "   - START_HERE.md - Guía de inicio"
echo "   - MOBILE_API_GUIDE.md - Para iOS"
echo "   - http://localhost:8000/docs - API Docs"
echo ""
echo "¡Feliz scraping! 🎉"
echo ""
