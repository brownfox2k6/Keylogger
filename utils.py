from datetime import datetime

def get_time(day=False) -> str:
    """
    Get local time on computer
    """
    format_ = "%d %b %H:%M:%S" if day else "%H:%M:%S"
    return datetime.now().strftime(format_)
