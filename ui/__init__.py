"""
UI Package for ClipX popup components.
"""

from .constants import (
    POPUP_WIDTH,
    POPUP_MAX_HEIGHT,
    ITEM_HEIGHT,
    PADDING,
    CORNER_RADIUS,
    ANIMATION_DURATION,
    EDIT_BUTTON_HEIGHT,
    DELETE_BUTTON_SIZE,
)
from .item_view import ClipboardItemView
from .edit_button_view import EditButtonView
from .popup import ClipboardPopup
from .positioning import calculate_popup_position

__all__ = [
    'POPUP_WIDTH',
    'POPUP_MAX_HEIGHT',
    'ITEM_HEIGHT',
    'PADDING',
    'CORNER_RADIUS',
    'ANIMATION_DURATION',
    'EDIT_BUTTON_HEIGHT',
    'DELETE_BUTTON_SIZE',
    'ClipboardItemView',
    'EditButtonView',
    'ClipboardPopup',
    'calculate_popup_position',
]

