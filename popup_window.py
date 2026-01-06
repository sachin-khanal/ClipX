"""
Clipboard Popup Window - Backward compatibility re-export module.

This module re-exports all components from the ui package for backward
compatibility with existing imports. New code should import directly from ui/.
"""

from ui import (
    # Constants
    POPUP_WIDTH,
    POPUP_MAX_HEIGHT,
    ITEM_HEIGHT,
    PADDING,
    CORNER_RADIUS,
    ANIMATION_DURATION,
    # Classes
    ClipboardItemView,
    ClipboardPopup,
    # Functions
    calculate_popup_position,
)

__all__ = [
    'POPUP_WIDTH',
    'POPUP_MAX_HEIGHT',
    'ITEM_HEIGHT',
    'PADDING',
    'CORNER_RADIUS',
    'ANIMATION_DURATION',
    'ClipboardItemView',
    'ClipboardPopup',
    'calculate_popup_position',
]
