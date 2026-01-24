INSIDE = "INSIDE"
OUTSIDE = "OUTSIDE"

def apply_status(current_status, new_event):
    if new_event == "MARK_PRESENT":
        if current_status == INSIDE:
            return None  # no change
        return INSIDE

    if new_event == "MARK_ABSENT":
        if current_status == OUTSIDE:
            return None
        return OUTSIDE

    return None