"""
Item Model
"""
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum


class ItemType(Enum):
    """Enum for different types of items"""
    TEXT = "text"
    URL = "url"
    CODE = "code"
    PATH = "path"


class Item:
    """Model representing a clipboard item"""

    def __init__(
        self,
        item_id: str,
        label: str,
        content: str,
        item_type: ItemType = ItemType.TEXT,
        icon: Optional[str] = None,
        is_sensitive: bool = False,
        is_favorite: bool = False,
        tags: Optional[list] = None,
        description: Optional[str] = None,
        working_dir: Optional[str] = None,
        color: Optional[str] = None,
        is_active: bool = True,
        is_archived: bool = False,
        # Nuevos campos para listas avanzadas
        is_list: bool = False,
        list_group: Optional[str] = None,
        orden_lista: int = 0
    ):
        self.id = item_id
        self.label = label
        self.content = content
        self.type = item_type if isinstance(item_type, ItemType) else ItemType(item_type)
        self.icon = icon
        self.is_sensitive = is_sensitive
        self.is_favorite = is_favorite
        self.tags = tags or []
        self.description = description
        self.working_dir = working_dir  # Directorio de trabajo para ejecutar comandos CODE
        self.color = color  # Color para identificación visual
        self.is_active = is_active  # Si el item está activo (puede usarse)
        self.is_archived = is_archived  # Si el item está archivado (oculto por defecto)
        # Campos de listas avanzadas
        self.is_list = is_list  # Indica si este item es parte de una lista
        self.list_group = list_group  # Nombre/identificador del grupo de lista
        self.orden_lista = orden_lista  # Posición del item dentro de la lista
        self.created_at = datetime.now()
        self.last_used = datetime.now()

    def update_last_used(self) -> None:
        """Update the last used timestamp"""
        self.last_used = datetime.now()

    def validate_content(self) -> bool:
        """Validate content based on type"""
        if not self.content:
            return False

        if self.type == ItemType.URL:
            return self.content.startswith(('http://', 'https://', 'www.'))

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert item to dictionary"""
        return {
            "id": self.id,
            "label": self.label,
            "content": self.content,
            "type": self.type.value if isinstance(self.type, ItemType) else self.type,
            "icon": self.icon,
            "is_sensitive": self.is_sensitive,
            "is_favorite": self.is_favorite,
            "tags": self.tags,
            "description": self.description,
            "working_dir": self.working_dir,
            "color": self.color,
            "is_active": self.is_active,
            "is_archived": self.is_archived,
            # Campos de listas avanzadas
            "is_list": self.is_list,
            "list_group": self.list_group,
            "orden_lista": self.orden_lista
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Item':
        """Create an Item from a dictionary"""
        # Generate ID from label if not provided
        item_id = data.get("id", data.get("label", "").lower().replace(" ", "_"))

        item_type_str = data.get("type", "text")
        item_type = ItemType(item_type_str) if item_type_str in [t.value for t in ItemType] else ItemType.TEXT

        return cls(
            item_id=item_id,
            label=data.get("label", ""),
            content=data.get("content", ""),
            item_type=item_type,
            icon=data.get("icon"),
            is_sensitive=data.get("is_sensitive", False),
            is_favorite=data.get("is_favorite", False),
            tags=data.get("tags", []),
            description=data.get("description"),
            working_dir=data.get("working_dir"),
            color=data.get("color"),
            is_active=data.get("is_active", True),
            is_archived=data.get("is_archived", False),
            # Campos de listas avanzadas
            is_list=data.get("is_list", False),
            list_group=data.get("list_group"),
            orden_lista=data.get("orden_lista", 0)
        )

    # Estado y visibilidad
    def is_visible(self) -> bool:
        """Retorna True si el item está activo y NO archivado (visible por defecto)"""
        return self.is_active and not self.is_archived

    def can_use(self) -> bool:
        """Retorna True si el item puede ser usado (activo, independiente de si está archivado)"""
        return self.is_active

    def archive(self) -> None:
        """Archivar el item (ocultar de vista por defecto)"""
        self.is_archived = True

    def unarchive(self) -> None:
        """Desarchivar el item (volver a vista por defecto)"""
        self.is_archived = False

    def activate(self) -> None:
        """Activar el item (puede ser usado)"""
        self.is_active = True

    def deactivate(self) -> None:
        """Desactivar el item (no puede ser usado)"""
        self.is_active = False

    # Métodos para listas avanzadas
    def is_list_item(self) -> bool:
        """Retorna True si este item es parte de una lista"""
        return self.is_list == True or self.is_list == 1

    def get_list_group(self) -> Optional[str]:
        """Retorna el nombre del grupo de lista al que pertenece este item (o None)"""
        return self.list_group if self.is_list_item() else None

    def get_orden_lista(self) -> int:
        """Retorna la posición de este item dentro de su lista"""
        return self.orden_lista if self.is_list_item() else 0

    def set_as_list_item(self, list_group: str, orden: int) -> None:
        """
        Configura este item como parte de una lista

        Args:
            list_group: Nombre/identificador del grupo de lista
            orden: Posición del item dentro de la lista (1, 2, 3...)
        """
        self.is_list = True
        self.list_group = list_group
        self.orden_lista = orden

    def remove_from_list(self) -> None:
        """Remueve este item de cualquier lista (lo convierte en item normal)"""
        self.is_list = False
        self.list_group = None
        self.orden_lista = 0

    def __repr__(self) -> str:
        list_info = f", list={self.list_group}[{self.orden_lista}]" if self.is_list_item() else ""
        return f"Item(id={self.id}, label={self.label}, type={self.type.value}{list_info})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Item):
            return False
        return self.id == other.id
