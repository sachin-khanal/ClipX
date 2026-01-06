"""
EditButtonView - A toggle button for edit mode in the popup.
"""

from typing import Callable, Optional

from AppKit import (
    NSView,
    NSTextField,
    NSColor,
    NSFont,
    NSCursor,
    NSTrackingArea,
    NSTrackingMouseEnteredAndExited,
    NSTrackingMouseMoved,
    NSTrackingActiveAlways,
    NSTrackingInVisibleRect,
    NSMakeRect,
    NSImageView,
    NSImage,
    NSTextAlignmentLeft,
)

from .constants import EDIT_BUTTON_HEIGHT, PADDING


class EditButtonView(NSView):
    """A toggle button for edit mode with pencil icon and Edit/Done text."""
    
    @classmethod
    def alloc_with_callbacks(cls, width: float,
                              on_click: Optional[Callable[[], None]] = None,
                              on_hover: Optional[Callable[[int], None]] = None,
                              index: int = 0):
        view = cls.alloc().initWithFrame_(NSMakeRect(0, 0, width, EDIT_BUTTON_HEIGHT))
        view._is_edit_mode = False
        view._is_selected = False
        view._on_click = on_click
        view._on_hover = on_hover
        view._index = index
        view._setup_content()
        view._setup_tracking()
        return view
    
    def _setup_content(self):
        """Create separate icon and label pairs for Edit and Done states to allow cross-fading."""
        # Common layout
        icon_size = 12
        label_width = 34
        spacing = 4
        total_content_width = icon_size + spacing + label_width
        
        start_x = (self.frame().size.width - total_content_width) / 2 + 2  # +2 nudge right for visual center
        
        icon_x = start_x
        icon_y = (EDIT_BUTTON_HEIGHT - icon_size) / 2 + 0.5
        
        label_x = icon_x + icon_size + spacing + 2
        # Move text down slightly (from 5.0 to 4.0) for better optical centering
        label_y = (EDIT_BUTTON_HEIGHT - 16) / 2 - 1
        
        # --- Edit State Views ---
        self._edit_icon = NSImageView.alloc().initWithFrame_(
            NSMakeRect(icon_x + 2, icon_y, icon_size, icon_size)
        )
        self._edit_icon.setWantsLayer_(True)
        edit_img = NSImage.imageWithSystemSymbolName_accessibilityDescription_("pencil", None)
        if edit_img:
            self._edit_icon.setImage_(edit_img)
            self._edit_icon.setContentTintColor_(NSColor.colorWithWhite_alpha_(0.7, 1.0))
        self.addSubview_(self._edit_icon)
        
        self._edit_label = NSTextField.alloc().initWithFrame_(
            NSMakeRect(label_x, label_y, label_width, 16)
        )
        self._edit_label.setWantsLayer_(True)
        self._edit_label.setStringValue_("Edit")
        self._edit_label.setAlignment_(NSTextAlignmentLeft)
        self._edit_label.setBezeled_(False)
        self._edit_label.setDrawsBackground_(False)
        self._edit_label.setEditable_(False)
        self._edit_label.setSelectable_(False)
        self._edit_label.setTextColor_(NSColor.colorWithWhite_alpha_(0.7, 1.0))
        self._edit_label.setFont_(NSFont.systemFontOfSize_weight_(11, 0.0))
        self.addSubview_(self._edit_label)
        
        # --- Done State Views (Hidden initially) ---
        self._done_icon = NSImageView.alloc().initWithFrame_(
            NSMakeRect(icon_x, icon_y, icon_size, icon_size)
        )
        self._done_icon.setWantsLayer_(True)
        self._done_icon.setAlphaValue_(0.0)
        done_img = NSImage.imageWithSystemSymbolName_accessibilityDescription_("checkmark", None)
        if done_img:
            self._done_icon.setImage_(done_img)
            self._done_icon.setContentTintColor_(NSColor.colorWithWhite_alpha_(0.7, 1.0))
        self.addSubview_(self._done_icon)
        
        self._done_label = NSTextField.alloc().initWithFrame_(
            NSMakeRect(label_x, label_y, label_width, 16)
        )
        self._done_label.setWantsLayer_(True)
        self._done_label.setAlphaValue_(0.0)
        self._done_label.setStringValue_("Done")
        self._done_label.setAlignment_(NSTextAlignmentLeft)
        self._done_label.setBezeled_(False)
        self._done_label.setDrawsBackground_(False)
        self._done_label.setEditable_(False)
        self._done_label.setSelectable_(False)
        self._done_label.setTextColor_(NSColor.colorWithWhite_alpha_(0.7, 1.0))
        self._done_label.setFont_(NSFont.systemFontOfSize_weight_(11, 0.0))
        self.addSubview_(self._done_label)
    
    def _setup_tracking(self):
        """Set up mouse tracking for hover effects."""
        options = (
            NSTrackingMouseEnteredAndExited |
            NSTrackingMouseMoved |
            NSTrackingActiveAlways |
            NSTrackingInVisibleRect
        )
        tracking = NSTrackingArea.alloc().initWithRect_options_owner_userInfo_(
            self.bounds(), options, self, None
        )
        self.addTrackingArea_(tracking)
    
    def set_edit_mode(self, enabled: bool):
        """Animate between Edit and Done states."""
        self._is_edit_mode = enabled
        
        from AppKit import NSAnimationContext
        NSAnimationContext.beginGrouping()
        NSAnimationContext.currentContext().setDuration_(0.2)
        
        if enabled:
            # Show Done, Hide Edit
            self._edit_icon.animator().setAlphaValue_(0.0)
            self._edit_label.animator().setAlphaValue_(0.0)
            self._done_icon.animator().setAlphaValue_(1.0)
            self._done_label.animator().setAlphaValue_(1.0)
        else:
            # Show Edit, Hide Done
            self._edit_icon.animator().setAlphaValue_(1.0)
            self._edit_label.animator().setAlphaValue_(1.0)
            self._done_icon.animator().setAlphaValue_(0.0)
            self._done_label.animator().setAlphaValue_(0.0)
            
        NSAnimationContext.endGrouping()
    
    def set_selected(self, selected: bool):
        """Update selection state colors."""
        self._is_selected = selected
        
        if selected:
            color = NSColor.colorWithWhite_alpha_(1.0, 1.0)
        else:
            color = NSColor.colorWithWhite_alpha_(0.7, 1.0)
            
        self._edit_label.setTextColor_(color)
        self._edit_icon.setContentTintColor_(color)
        self._done_label.setTextColor_(color)
        self._done_icon.setContentTintColor_(color)
        
        self.setNeedsDisplay_(True)
    
    def mouseEntered_(self, event):
        """Update selection when mouse enters."""
        if self._on_hover:
            self._on_hover(self._index)
    
    def mouseMoved_(self, event):
        """Update selection when mouse moves within the button."""
        if self._on_hover:
            self._on_hover(self._index)
    
    def mouseExited_(self, event):
        pass
    
    def mouseDown_(self, event):
        """Handle click on the button."""
        if self._on_click:
            self._on_click()
    
    def resetCursorRects(self):
        """Set the cursor to a pointing hand when hovering."""
        self.addCursorRect_cursor_(self.bounds(), NSCursor.pointingHandCursor())
    
    def drawRect_(self, rect):
        """Draw background - handled by floating selection view."""
        pass

