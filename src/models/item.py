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
        is_archived: bool = False
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
            "is_archived": self.is_archived
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
            is_archived=data.get("is_archived", False)
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

    def __repr__(self) -> str:
        return f"Item(id={self.id}, label={self.label}, type={self.type.value})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Item):
            return False
        return self.id == other.id
