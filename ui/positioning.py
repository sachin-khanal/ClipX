"""
Popup positioning calculations for multi-monitor support.
"""

from AppKit import NSScreen
from accessibility import ElementRect


def calculate_popup_position(element_rect: ElementRect, popup_height: float) -> tuple:
    """
    Calculate where to show the popup based on the focused element.
    
    The popup should appear directly below the input field unless there's 
    not enough space, in which case it appears directly above.
    
    Args:
        element_rect: The screen coordinates of the focused element (Y from User Top-Left)
        popup_height: The height of the popup window
        
    Returns:
        (x, y, show_above) where x,y is the BOTTOM-LEFT corner of popup in Cocoa coords.
    """
    screens = NSScreen.screens()
    if not screens:
        return (100, 100, False)
        
    # 1. Coordinate System Conversion
    # Cocoa uses a coordinate system where (0,0) is the BOTTOM-LEFT of the PRIMARY screen.
    # Accessibility API (AX) uses (0,0) as the TOP-LEFT of the PRIMARY screen.
    # To convert AX Y to Cocoa Y: CocoaY = PrimaryScreenHeight - AXY
    
    primary_screen = screens[0]
    primary_height = primary_screen.frame().size.height
    
    # Calculate element bounds in Cocoa coordinates
    elem_top_cocoa = primary_height - element_rect.y
    elem_bottom_cocoa = primary_height - (element_rect.y + element_rect.height)
    
    elem_x_cocoa = element_rect.x  # X is same
    elem_center_x = element_rect.center_x
    
    print(f"[Pos] Element (AX): y={element_rect.y}, h={element_rect.height} -> Cocoa: top={elem_top_cocoa}, bottom={elem_bottom_cocoa}", flush=True)

    # 2. Find which screen the element is on
    target_screen = primary_screen
    
    for screen in screens:
        frame = screen.visibleFrame()
        if (frame.origin.x <= elem_center_x <= frame.origin.x + frame.size.width) and \
           (frame.origin.y <= elem_bottom_cocoa <= frame.origin.y + frame.size.height):
            target_screen = screen
            break
            
    screen_frame = target_screen.visibleFrame()
    screen_min_y = screen_frame.origin.y
    screen_max_y = screen_frame.origin.y + screen_frame.size.height
    print(f"[Pos] Target Screen Frame (Visible): {screen_frame}", flush=True)

    # 3. Determine Position
    gap = 6
    
    # Proposal 1: Below the element
    y_below = (elem_bottom_cocoa - gap) - popup_height
    
    # Proposal 2: Above the element
    y_above = elem_top_cocoa + gap
    
    # 4. Constraints
    fits_below = y_below >= screen_min_y
    fits_above = (y_above + popup_height) <= screen_max_y
    
    show_above = False
    final_y = y_below
    
    if fits_below:
        final_y = y_below
        show_above = False
        print("[Pos] Fits below.", flush=True)
    elif fits_above:
        final_y = y_above
        show_above = True
        print("[Pos] Fits above (below blocked).", flush=True)
    else:
        # Fits neither? Pick whichever has more space or clamp to screen
        space_below = elem_bottom_cocoa - screen_min_y
        space_above = screen_max_y - elem_top_cocoa
        
        if space_above > space_below:
             final_y = y_above
             show_above = True
             if final_y + popup_height > screen_max_y:
                 final_y = screen_max_y - popup_height
        else:
             final_y = y_below
             show_above = False
             if final_y < screen_min_y:
                 final_y = screen_min_y

    print(f"[Pos] Result: y={final_y}, above={show_above}", flush=True)
    return (elem_center_x, final_y, show_above)
