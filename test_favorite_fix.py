"""Script para verificar que el fix de favoritos funciona"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.config_manager import ConfigManager

print("=" * 80)
print("TEST: Verificar que is_favorite se carga correctamente")
print("=" * 80)

config_mgr = ConfigManager()
category = config_mgr.get_category(17)  # Git

if category:
    print(f"\nCategoría: {category.name}")
    print(f"Total items: {len(category.items)}")

    favoritos = [item for item in category.items if item.is_favorite]
    no_favoritos = [item for item in category.items if not item.is_favorite]

    print(f"\n[OK] Items favoritos: {len(favoritos)}")
    for item in favoritos:
        print(f"  - {item.label} (is_favorite={item.is_favorite})")

    print(f"\n[--] Items NO favoritos: {len(no_favoritos)}")
    for item in no_favoritos[:3]:
        print(f"  - {item.label} (is_favorite={item.is_favorite})")

    print("\n" + "=" * 80)
    print("TEST: Aplicar filtro de favoritos")
    print("=" * 80)

    from core.advanced_filter_engine import AdvancedFilterEngine

    filter_engine = AdvancedFilterEngine()

    # Test filtro de favoritos
    filters = {'is_favorite': True}
    filtered = filter_engine.apply_filters(category.items, filters)

    print(f"\nFiltro aplicado: is_favorite=True")
    print(f"Resultados: {len(filtered)} items")
    for item in filtered:
        print(f"  - {item.label}")

    if len(filtered) == len(favoritos):
        print("\n[OK] EL FIX FUNCIONA! El filtro de favoritos esta devolviendo los resultados correctos")
    else:
        print(f"\n[ERROR] Se esperaban {len(favoritos)} items pero se obtuvieron {len(filtered)}")

print("\n" + "=" * 80)
