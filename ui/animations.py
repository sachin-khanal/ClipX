from AppKit import (
    NSAnimationContext,
    NSTimer,
    NSMakePoint,
    NSMakeRect,
    NSEvent,
    CAMediaTimingFunction,
    kCAMediaTimingFunctionEaseOut,
    NSView,
    NSColor
)
import traceback
from typing import List, Optional

from .constants import (
    PADDING, 
    ITEM_HEIGHT, 
    EDIT_BUTTON_HEIGHT, 
    POPUP_MAX_HEIGHT,
    POPUP_WIDTH
)

class PopupAnimationMixin:
    """
    Mixin for ClipboardPopup to handle animations.
    Expected to be mixed into a class that inherits from NSPanel/NSWindow and has specific attributes.
    """
    
    def _animate_hide(self):
        """Animate the popup hiding using timer."""
        if not self._is_visible:
            return
        self._is_visible = False
        
        # Remove click monitor if exists
        if hasattr(self, '_click_monitor') and self._click_monitor:
            NSEvent.removeMonitor_(self._click_monitor)
            self._click_monitor = None
        
        self._hide_step = 0
        self._hide_steps = 8
        self._hide_start_y = self.frame().origin.y
        self._hide_start_alpha = self.alphaValue()
        
        def step_animation(timer):
            self._hide_step += 1
            progress = self._hide_step / self._hide_steps
            ease = progress * progress
            
            alpha = self._hide_start_alpha * (1 - ease)
            y = self._hide_start_y - (10 * ease)
            
            self.setAlphaValue_(alpha)
            self.setFrameOrigin_(NSMakePoint(self.frame().origin.x, y))
            
            if self._hide_step >= self._hide_steps:
                timer.invalidate()
                self.orderOut_(None)
        
        NSTimer.scheduledTimerWithTimeInterval_repeats_block_(
            0.015, True, step_animation
        )

    def _animate_selection_change(self):
        """Animate the selection view to the current selected index."""
        target_frame = None
        
        # Determine target frame
        if self._selected_index == 0:
            if self._edit_button_view:
                target_frame = self._edit_button_view.frame()
        elif 1 <= self._selected_index <= len(self._item_views):
            view = self._item_views[self._selected_index - 1]
            target_frame = view.frame()
            
        if target_frame is None:
            self._selection_view.setHidden_(True)
            return
            
        self._selection_view.setHidden_(False)
        
        # Use NSAnimationContext for fluid frame animation (position + size)
        NSAnimationContext.beginGrouping()
        NSAnimationContext.currentContext().setDuration_(0.15)
        # Use easeOut for gliding effect
        NSAnimationContext.currentContext().setTimingFunction_(
            CAMediaTimingFunction.functionWithName_(kCAMediaTimingFunctionEaseOut)
        )
        
        self._selection_view.animator().setFrame_(target_frame)
        
        NSAnimationContext.endGrouping()

    def _animate_item_removal(self, removed_index: int):
        """Animate removal of an item and repositioning of remaining items."""
        
        print(f"[Popup] _animate_item_removal called, removed_index={removed_index}, item_views={len(self._item_views)}", flush=True)
        
        if removed_index >= len(self._item_views):
            print(f"[Popup] removed_index out of bounds, skipping animation", flush=True)
            return
        
        try:
            removed_view = self._item_views[removed_index]
            
            # Calculate new dimensions (for after the animation)
            num_items = len(self._items)
            edit_button_space = EDIT_BUTTON_HEIGHT + PADDING
            items_height = ITEM_HEIGHT * num_items
            new_total_content_height = items_height + edit_button_space + (PADDING * 3)
            new_visible_height = min(new_total_content_height, POPUP_MAX_HEIGHT)
            
            # Store current values for the closure
            blur_width = self.contentView().bounds().size.width
            old_selected_index = self._selected_index
            
            # Figure out new selection - stay at same position if possible
            if num_items == 0:
                new_selected_index = 0  # Edit button only
            elif old_selected_index - 1 >= num_items:
                new_selected_index = num_items  # Last remaining item (1-indexed)
            else:
                new_selected_index = old_selected_index
            
            # Animation parameters
            duration = 0.2
            
            # Calculate window height change (delta)
            # This is positive if window shrinks (bottom moves up)
            frame = self.frame()
            old_height = frame.size.height
            height_delta = old_height - new_visible_height
            
            # If we are deleting the LAST item (num_items == 0), just fade out the whole window
            if num_items == 0:
                print(f"[Popup] Deleting last item, dismissing window", flush=True)
                self.hide(animate=True)
                
                # Cleanup state in background after window fades
                def cleanup_last_item(timer):
                    removed_view.removeFromSuperview()
                    if removed_index < len(self._item_views):
                        self._item_views.pop(removed_index)
                    self._items_container.setFrame_(NSMakeRect(0, 0, blur_width, 0))
                    self._selected_index = 0
                    if self._edit_button_view:
                        self._edit_button_view.set_selected(True) # Reset to edit button
                        
                NSTimer.scheduledTimerWithTimeInterval_repeats_block_(
                    0.25, False, cleanup_last_item
                )
                return

            # Generalized Animation Logic:
            NSAnimationContext.beginGrouping()
            NSAnimationContext.currentContext().setDuration_(duration)
            
            # 1. Fade out the removed item
            removed_view.animator().setAlphaValue_(0.0)
            
            # 2. Animate items ABOVE (index < removed_index) -> Move Down by delta
            for i in range(removed_index):
                view = self._item_views[i]
                current_frame = view.frame()
                new_y = current_frame.origin.y - height_delta
                view.animator().setFrameOrigin_(NSMakePoint(current_frame.origin.x, new_y))
            
            # 3. Animate Edit Button -> Move Down by delta
            if self._edit_button_view:
                current_frame = self._edit_button_view.frame()
                new_y = current_frame.origin.y - height_delta
                self._edit_button_view.animator().setFrameOrigin_(NSMakePoint(current_frame.origin.x, new_y))

            # 4. Animate items BELOW (index > removed_index) -> Move Up by (ITEM_HEIGHT - delta)
            offset_below = ITEM_HEIGHT - height_delta
            for i in range(removed_index + 1, len(self._item_views)):
                view = self._item_views[i]
                current_frame = view.frame()
                new_y = current_frame.origin.y + offset_below
                view.animator().setFrameOrigin_(NSMakePoint(current_frame.origin.x, new_y))
            
            # 5. Animate Selection View
            if new_selected_index > 0 and new_selected_index - 1 < len(self._item_views):
                target_index = new_selected_index - 1
                
                if target_index < removed_index:
                    target_view = self._item_views[target_index]
                    current_frame = target_view.frame()
                    new_y = current_frame.origin.y - height_delta
                    
                elif target_index > removed_index:
                    target_view = self._item_views[target_index]
                    current_frame = target_view.frame()
                    offset_below = ITEM_HEIGHT - height_delta
                    new_y = current_frame.origin.y + offset_below
                    
                else: 
                    current_frame = removed_view.frame()
                    new_y = current_frame.origin.y - height_delta
                
                sel_frame = NSMakeRect(PADDING, new_y, blur_width - (PADDING * 2), ITEM_HEIGHT)
                self._selection_view.animator().setFrame_(sel_frame)
                
            elif new_selected_index == 0 and self._edit_button_view:
                current_frame = self._edit_button_view.frame()
                new_y = current_frame.origin.y - height_delta
                new_edit_frame = NSMakeRect(current_frame.origin.x, new_y, current_frame.size.width, current_frame.size.height)
                self._selection_view.animator().setFrame_(new_edit_frame)
            
            # 6. Animate Window Resize
            if height_delta != 0:
                frame.size.height = new_visible_height
                frame.origin.y += height_delta
                self.animator().setFrame_display_(frame, True)
            
            NSAnimationContext.endGrouping()
            
            # Capture values for the closure
            popup = self
            
            # After animation completes, update container and window size
            def cleanup_after_animation(timer):
                try:
                    print(f"[Popup] cleanup_after_animation running", flush=True)
                    
                    # Remove the deleted view
                    removed_view.removeFromSuperview()
                    if removed_index < len(popup._item_views):
                        popup._item_views.pop(removed_index)
                    
                    # Update indices for remaining views
                    for i, view in enumerate(popup._item_views):
                        view._index = i + 1  # 1-based index
                    
                    # Resize container and edit button to match new content
                    popup._items_container.setFrame_(NSMakeRect(0, 0, blur_width, new_total_content_height))
                    
                    # Reposition edit button
                    if popup._edit_button_view:
                        edit_btn_x = blur_width - PADDING - 64
                        edit_btn_y = new_total_content_height - PADDING - EDIT_BUTTON_HEIGHT
                        popup._edit_button_view.setFrameOrigin_(NSMakePoint(edit_btn_x, edit_btn_y))
                    
                    # Reposition all items to their final correct positions
                    for i, view in enumerate(popup._item_views):
                        y = new_total_content_height - PADDING - edit_button_space - ((i + 1) * ITEM_HEIGHT)
                        view.setFrameOrigin_(NSMakePoint(PADDING, y))
                    
                    # Update selection
                    popup._selected_index = new_selected_index
                    
                    # Deselect all first
                    for view in popup._item_views:
                        view.set_selected(False)
                    if popup._edit_button_view:
                        popup._edit_button_view.set_selected(False)
                    
                    # Select the new item
                    if new_selected_index == 0:
                        if popup._edit_button_view:
                            popup._edit_button_view.set_selected(True)
                        popup._selection_view.setHidden_(True)
                    elif new_selected_index - 1 < len(popup._item_views):
                        popup._item_views[new_selected_index - 1].set_selected(True)
                        popup._selection_view.setHidden_(False)
                        # Update selection view to correct position
                        target_view = popup._item_views[new_selected_index - 1]
                        popup._selection_view.setFrame_(target_view.frame())
                    
                    print(f"[Popup] cleanup_after_animation completed, new_selected={new_selected_index}", flush=True)
                except Exception as e:
                    print(f"[Popup] Error in cleanup_after_animation: {e}", flush=True)
                    traceback.print_exc()
            
            NSTimer.scheduledTimerWithTimeInterval_repeats_block_(
                duration + 0.05, False, cleanup_after_animation
            )
        except Exception as e:
            print(f"[Popup] Error in _animate_item_removal: {e}", flush=True)
            traceback.print_exc()
