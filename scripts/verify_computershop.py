"""
Script de verificación de la integración de ComputerShop
Verifica que todos los componentes estén correctamente instalados
"""
import os
import sys
from pathlib import Path

def check_file(path, description):
    """Verifica si un archivo existe"""
    exists = os.path.exists(path)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {path}")
    return exists

def check_import(module_name, class_name=None):
    """Verifica si un módulo se puede importar"""
    try:
        if class_name:
            exec(f"from {module_name} import {class_name}")
            print(f"✅ Import OK: from {module_name} import {class_name}")
        else:
            exec(f"import {module_name}")
            print(f"✅ Import OK: import {module_name}")
        return True
    except Exception as e:
        print(f"❌ Import FAILED: {module_name} - {e}")
        return False

def main():
    """Ejecuta todas las verificaciones"""
    
    print("\n" + "="*80)
    print("🔍 VERIFICACIÓN DE INTEGRACIÓN - COMPUTERSHOP")
    print("="*80)
    
    # Get base path
    base_path = Path(__file__).parent.parent
    os.chdir(base_path)
    
    all_checks = []
    
    # 1. Verificar archivos del scraper
    print("\n📁 Verificando archivos del scraper...")
    scraper_files = [
        ("scrapers/computershop/__init__.py", "Módulo init"),
        ("scrapers/computershop/scraper.py", "Scraper principal"),
        ("scrapers/computershop/run.py", "Script de ejecución"),
        ("scrapers/computershop/load_to_db.py", "Loader a BD"),
        ("scrapers/computershop/README.md", "Documentación"),
    ]
    
    for path, desc in scraper_files:
        all_checks.append(check_file(path, desc))
    
    # 2. Verificar wrapper
    print("\n📁 Verificando wrapper...")
    all_checks.append(check_file("scrapers/computershop_scraper.py", "Wrapper"))
    
    # 3. Verificar tests
    print("\n📁 Verificando tests...")
    all_checks.append(check_file("tests/test_computershop.py", "Test de integración"))
    
    # 4. Verificar documentación
    print("\n📁 Verificando documentación...")
    doc_files = [
        ("docs/COMPUTERSHOP_INTEGRATION.md", "Guía de integración"),
        ("docs/COMPUTERSHOP_SUMMARY.md", "Resumen ejecutivo"),
    ]
    
    for path, desc in doc_files:
        all_checks.append(check_file(path, desc))
    
    # 5. Verificar scripts
    print("\n📁 Verificando scripts...")
    all_checks.append(check_file("scripts/run_all_scrapers_complete.py", "Script completo"))
    
    # 6. Verificar imports
    print("\n📦 Verificando imports...")
    
    # Add paths
    sys.path.insert(0, str(base_path))
    sys.path.insert(0, str(base_path / "scrapers"))
    
    import_checks = [
        ("scrapers.computershop_scraper", "ComputerShopScraper"),
        ("scrapers", "ComputerShopScraper"),
    ]
    
    for module, class_name in import_checks:
        all_checks.append(check_import(module, class_name))
    
    # 7. Verificar integración en main.py
    print("\n📝 Verificando integración en main.py...")
    
    try:
        with open("main.py", 'r', encoding='utf-8') as f:
            main_content = f.read()
        
        checks = [
            ("ComputerShopScraper" in main_content, "ComputerShopScraper importado"),
            ("'ComputerShop':" in main_content, "ComputerShop en dict de scrapers"),
            ("computershop/products" in main_content, "Endpoint de ComputerShop"),
            ("computershop" in main_content.lower(), "Referencia a computershop"),
        ]
        
        for condition, desc in checks:
            status = "✅" if condition else "❌"
            print(f"{status} {desc}")
            all_checks.append(condition)
    
    except Exception as e:
        print(f"❌ Error leyendo main.py: {e}")
        all_checks.append(False)
    
    # 8. Verificar integración en __init__.py
    print("\n📝 Verificando scrapers/__init__.py...")
    
    try:
        with open("scrapers/__init__.py", 'r', encoding='utf-8') as f:
            init_content = f.read()
        
        checks = [
            ("ComputerShopScraper" in init_content, "ComputerShopScraper importado"),
            ("computershop_scraper" in init_content, "Módulo importado"),
            ("ComputerShopScraper" in init_content.split("__all__")[1], "En __all__"),
        ]
        
        for condition, desc in checks:
            status = "✅" if condition else "❌"
            print(f"{status} {desc}")
            all_checks.append(condition)
    
    except Exception as e:
        print(f"❌ Error leyendo __init__.py: {e}")
        all_checks.append(False)
    
    # 9. Verificar README.md
    print("\n📝 Verificando README.md...")
    
    try:
        with open("README.md", 'r', encoding='utf-8') as f:
            readme_content = f.read()
        
        checks = [
            ("ComputerShop" in readme_content, "ComputerShop mencionado"),
            ("computershopperu.com" in readme_content, "URL incluida"),
        ]
        
        for condition, desc in checks:
            status = "✅" if condition else "❌"
            print(f"{status} {desc}")
            all_checks.append(condition)
    
    except Exception as e:
        print(f"❌ Error leyendo README.md: {e}")
        all_checks.append(False)
    
    # 10. Verificar dependencias
    print("\n📦 Verificando dependencias...")
    
    dependencies = [
        ("selenium", "Selenium"),
        ("bs4", "BeautifulSoup4"),
        ("requests", "Requests"),
    ]
    
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"✅ {name} instalado")
            all_checks.append(True)
        except ImportError:
            print(f"❌ {name} NO instalado")
            all_checks.append(False)
    
    # Resumen final
    print("\n" + "="*80)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("="*80)
    
    total_checks = len(all_checks)
    passed_checks = sum(all_checks)
    failed_checks = total_checks - passed_checks
    
    print(f"\nTotal de verificaciones: {total_checks}")
    print(f"✅ Exitosas: {passed_checks}")
    print(f"❌ Fallidas: {failed_checks}")
    
    success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
    print(f"\n📈 Tasa de éxito: {success_rate:.1f}%")
    
    print("\n" + "="*80)
    
    if success_rate >= 90:
        print("✅ INTEGRACIÓN COMPLETA Y VERIFICADA")
        print("   ComputerShop está listo para usar")
        print("\n🚀 Siguiente paso:")
        print("   cd scrapers/computershop")
        print("   python run.py")
    elif success_rate >= 70:
        print("⚠️ INTEGRACIÓN PARCIAL")
        print(f"   {failed_checks} verificaciones fallidas")
        print("   Revisar los items marcados con ❌")
    else:
        print("❌ INTEGRACIÓN INCOMPLETA")
        print(f"   {failed_checks} verificaciones fallidas")
        print("   Revisar la instalación")
    
    print("="*80 + "\n")
    
    return success_rate >= 90


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
