"""
Pinned Panels Manager
Manages the business logic for pinned panel persistence and management
"""

from typing import List, Dict, Optional
import logging
import json

logger = logging.getLogger(__name__)


class PinnedPanelsManager:
    """Manager for pinned panel persistence and management"""

    def __init__(self, db_manager):
        """
        Initialize the pinned panels manager

        Args:
            db_manager: DBManager instance for database operations
        """
        self.db = db_manager
        logger.info("PinnedPanelsManager initialized")

    def _serialize_filter_config(self, panel_widget) -> Optional[str]:
        """
        Serialize panel's filter configuration to JSON string

        Args:
            panel_widget: FloatingPanel widget instance

        Returns:
            str: JSON string of filter configuration, or None if no filters
        """
        try:
            filter_config = {
                "advanced_filters": getattr(panel_widget, 'current_filters', {}),
                "state_filter": getattr(panel_widget, 'current_state_filter', 'normal'),
                "search_text": getattr(panel_widget, 'search_bar', None).text() if hasattr(panel_widget, 'search_bar') else ""
            }

            # Only save if there's actual filter data
            if filter_config["advanced_filters"] or filter_config["state_filter"] != "normal" or filter_config["search_text"]:
                return json.dumps(filter_config)

            return None
        except Exception as e:
            logger.warning(f"Could not serialize filter config: {e}")
            return None

    def _deserialize_filter_config(self, filter_config_json: Optional[str]) -> Optional[Dict]:
        """
        Deserialize filter configuration from JSON string

        Args:
            filter_config_json: JSON string from database

        Returns:
            dict: Filter configuration dict, or None if no filters saved
        """
        if not filter_config_json:
            return None

        try:
            filter_config = json.loads(filter_config_json)
            logger.debug(f"Deserialized filter config: {filter_config}")
            return filter_config
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse filter config JSON: {e}")
            return None

    def save_panel_state(self, panel_widget, category_id: int,
                        custom_name: str = None, custom_color: str = None) -> int:
        """
        Save current state of a FloatingPanel to database

        Args:
            panel_widget: FloatingPanel widget instance
            category_id: ID of the category this panel displays
            custom_name: Custom name for the panel (optional)
            custom_color: Custom color for panel header (optional, hex format)

        Returns:
            int: Panel ID in database
        """
        try:
            # Serialize filter configuration
            filter_config = self._serialize_filter_config(panel_widget)

            panel_id = self.db.save_pinned_panel(
                category_id=category_id,
                x_pos=panel_widget.x(),
                y_pos=panel_widget.y(),
                width=panel_widget.width(),
                height=panel_widget.height(),
                is_minimized=getattr(panel_widget, 'is_minimized', False),
                custom_name=custom_name,
                custom_color=custom_color,
                filter_config=filter_config
            )
            logger.info(f"Panel state saved for category {category_id} (Panel ID: {panel_id})")
            return panel_id
        except Exception as e:
            logger.error(f"Failed to save panel state: {e}")
            raise

    def update_panel_state(self, panel_id: int, panel_widget, include_filters: bool = True):
        """
        Update panel position/size/filters in database

        Args:
            panel_id: Panel ID in database
            panel_widget: FloatingPanel widget instance
            include_filters: Whether to also update filter configuration (default True)
        """
        try:
            update_data = {
                'x_position': panel_widget.x(),
                'y_position': panel_widget.y(),
                'width': panel_widget.width(),
                'height': panel_widget.height(),
                'is_minimized': getattr(panel_widget, 'is_minimized', False)
            }

            # Include filter configuration if requested
            if include_filters:
                filter_config = self._serialize_filter_config(panel_widget)
                update_data['filter_config'] = filter_config

            self.db.update_pinned_panel(panel_id=panel_id, **update_data)
            logger.debug(f"Panel {panel_id} state updated (filters: {include_filters})")
        except Exception as e:
            logger.error(f"Failed to update panel state: {e}")
            raise

    def restore_panels_on_startup(self) -> List[Dict]:
        """
        Get all active panels to restore on application startup

        Returns:
            List[Dict]: List of panel dictionaries with configuration
        """
        try:
            panels = self.db.get_pinned_panels(active_only=True)
            logger.info(f"Retrieved {len(panels)} active panels for restoration")
            return panels
        except Exception as e:
            logger.error(f"Failed to retrieve panels for restoration: {e}")
            return []

    def mark_panel_opened(self, panel_id: int):
        """
        Update statistics when panel is opened

        Args:
            panel_id: Panel ID in database
        """
        try:
            self.db.update_panel_last_opened(panel_id)
            logger.debug(f"Panel {panel_id} marked as opened")
        except Exception as e:
            logger.error(f"Failed to mark panel as opened: {e}")

    def get_recent_history(self, limit: int = 10) -> List[Dict]:
        """
        Get recently used panels for history dropdown

        Args:
            limit: Maximum number of panels to return (default: 10)

        Returns:
            List[Dict]: List of panel dictionaries ordered by last_opened
        """
        try:
            panels = self.db.get_recent_panels(limit=limit)
            logger.debug(f"Retrieved {len(panels)} recent panels")
            return panels
        except Exception as e:
            logger.error(f"Failed to retrieve recent panels: {e}")
            return []

    def delete_panel(self, panel_id: int):
        """
        Remove panel from database

        Args:
            panel_id: Panel ID to delete
        """
        try:
            self.db.delete_pinned_panel(panel_id)
            logger.info(f"Panel {panel_id} deleted from database")
        except Exception as e:
            logger.error(f"Failed to delete panel: {e}")
            raise

    def cleanup_on_exit(self):
        """
        Mark all panels as inactive when app closes
        This allows us to know which panels were active in the last session
        """
        try:
            self.db.deactivate_all_panels()
            logger.info("All panels marked as inactive on application exit")
        except Exception as e:
            logger.error(f"Failed to cleanup panels on exit: {e}")

    def update_panel_customization(self, panel_id: int, custom_name: str = None,
                                   custom_color: str = None):
        """
        Update panel's custom name and/or color

        Args:
            panel_id: Panel ID to update
            custom_name: New custom name (None to keep unchanged)
            custom_color: New custom color in hex format (None to keep unchanged)
        """
        try:
            kwargs = {}
            if custom_name is not None:
                kwargs['custom_name'] = custom_name
            if custom_color is not None:
                kwargs['custom_color'] = custom_color

            if kwargs:
                self.db.update_pinned_panel(panel_id, **kwargs)
                logger.info(f"Panel {panel_id} customization updated")
        except Exception as e:
            logger.error(f"Failed to update panel customization: {e}")
            raise

    def get_panel_by_category(self, category_id: int) -> Optional[Dict]:
        """
        Check if an active panel for this category already exists

        Args:
            category_id: Category ID to check

        Returns:
            Optional[Dict]: Panel data if exists, None otherwise
        """
        try:
            panel = self.db.get_panel_by_category(category_id)
            if panel:
                logger.debug(f"Found existing panel for category {category_id}")
            return panel
        except Exception as e:
            logger.error(f"Failed to check panel by category: {e}")
            return None

    def get_all_panels(self, active_only: bool = False) -> List[Dict]:
        """
        Get all pinned panels

        Args:
            active_only: If True, only return active panels

        Returns:
            List[Dict]: List of all panel dictionaries
        """
        try:
            panels = self.db.get_pinned_panels(active_only=active_only)
            logger.debug(f"Retrieved {len(panels)} panels (active_only={active_only})")
            return panels
        except Exception as e:
            logger.error(f"Failed to retrieve all panels: {e}")
            return []

    def get_panel_by_id(self, panel_id: int) -> Optional[Dict]:
        """
        Get specific panel by ID

        Args:
            panel_id: Panel ID to retrieve

        Returns:
            Optional[Dict]: Panel data if found, None otherwise
        """
        try:
            panel = self.db.get_panel_by_id(panel_id)
            if panel:
                logger.debug(f"Retrieved panel {panel_id}")
            else:
                logger.warning(f"Panel {panel_id} not found")
            return panel
        except Exception as e:
            logger.error(f"Failed to retrieve panel by ID: {e}")
            return None

    def has_panels(self) -> bool:
        """
        Check if there are any saved panels

        Returns:
            bool: True if at least one panel exists
        """
        try:
            panels = self.db.get_pinned_panels(active_only=False)
            return len(panels) > 0
        except Exception as e:
            logger.error(f"Failed to check if panels exist: {e}")
            return False
