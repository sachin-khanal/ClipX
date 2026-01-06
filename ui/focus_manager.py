from typing import Optional, Any
from AppKit import NSApplication
from Quartz import (
    CGEventCreateKeyboardEvent,
    CGEventSetFlags,
    CGEventPost,
    kCGHIDEventTap,
    kCGEventFlagMaskCommand,
)
import traceback

class FocusManager:
    """
    Manages focus storage, restoration, and paste simulation for the ClipboardPopup.
    """
    def __init__(self):
        self._original_focused_element = None
        self._original_frontmost_app = None

    def store_focused_element(self, element: Any):
        """Store the currently focused element to restore later."""
        self._original_focused_element = element

    def store_frontmost_app(self, app: Any):
        """Store the frontmost application to reactivate later."""
        self._original_frontmost_app = app

    def refocus_original_app(self):
        """Refocus the original application."""
        if self._original_frontmost_app is not None:
            try:
                self._original_frontmost_app.activateWithOptions_(0)
                print(f"[FocusManager] Activated app: {self._original_frontmost_app.localizedName()}", flush=True)
            except Exception as e:
                print(f"[FocusManager] Could not activate app: {e}", flush=True)
        self._original_frontmost_app = None

    def refocus_original_element(self):
        """Refocus the original input element."""
        if self._original_focused_element is None:
            return
        
        try:
            from ApplicationServices import AXUIElementPerformAction
            AXUIElementPerformAction(self._original_focused_element, "AXFocus")
            print("[FocusManager] Refocused original element", flush=True)
        except Exception as e:
            print(f"[FocusManager] Could not refocus original element: {e}", flush=True)
        finally:
            self._original_focused_element = None

    def simulate_paste(self):
        """Simulate Cmd+V keystroke to paste."""
        print("[FocusManager] Executing paste...", flush=True)
        
        KEY_V = 9
        
        # Press Cmd+V
        event = CGEventCreateKeyboardEvent(None, KEY_V, True)
        CGEventSetFlags(event, kCGEventFlagMaskCommand)
        CGEventPost(kCGHIDEventTap, event)
        
        # Release Cmd+V
        event = CGEventCreateKeyboardEvent(None, KEY_V, False)
        CGEventSetFlags(event, kCGEventFlagMaskCommand)
        CGEventPost(kCGHIDEventTap, event)

    def perform_paste_sequence(self):
        """Refocus original app/element and simulate paste with a delay."""
        from Foundation import NSTimer
        
        # 1. Activate App and Focus Element
        self.refocus_original_app()
        self.refocus_original_element()
        
        # 2. Schedule Paste
        def do_paste(timer):
             self.simulate_paste()
             
        NSTimer.scheduledTimerWithTimeInterval_repeats_block_(
             0.1, False, do_paste
        )
