"""
Test rapido para verificar que el widget puede iniciarse
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_can_initialize():
    """Test que todos los componentes pueden inicializarse"""
    print("=== VERIFICACION DE INICIO ===\n")

    try:
        # 1. Verificar base de datos
        print("[1/4] Verificando base de datos...")
        db_path = Path("widget_sidebar.db")
        if not db_path.exists():
            print("  [ERROR] Base de datos no existe")
            return False
        print("  [OK] Base de datos existe")

        # 2. Verificar MainController puede inicializarse
        print("\n[2/4] Inicializando MainController...")
        from controllers.main_controller import MainController
        controller = MainController()
        print("  [OK] MainController inicializado")

        # 3. Verificar categorias cargadas
        print("\n[3/4] Verificando categorias...")
        categories = controller.get_categories()
        print(f"  [OK] {len(categories)} categorias cargadas")

        # 4. Verificar que PyQt6 puede importarse
        print("\n[4/4] Verificando PyQt6...")
        from PyQt6.QtWidgets import QApplication
        print("  [OK] PyQt6 disponible")

        # Cleanup
        del controller

        print("\n" + "="*50)
        print("RESULTADO: EL WIDGET ESTA LISTO PARA EJECUTARSE")
        print("="*50)
        print("\nPuedes ejecutar:")
        print("  python main.py")
        print("\nO compilar el ejecutable:")
        print("  build.bat")
        print()

        return True

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_can_initialize()
    sys.exit(0 if success else 1)
