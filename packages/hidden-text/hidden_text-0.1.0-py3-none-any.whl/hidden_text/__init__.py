import os

if os.name == 'nt':
    try:
        from .windows_impl import hidden_text
    except ImportError:
        raise ImportError("Failed to import hidden_text for Windows. Ensure you have the required dependencies installed.")
else:
    try:
        from .unix_impl import hidden_text
    except ImportError:
        raise ImportError("Failed to import hidden_text for Unix-like systems. Ensure you have the required dependencies installed.")
    
