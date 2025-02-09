import os
import platform

def clear_screen():
    """Clear the console screen based on the operating system."""
    if platform.system().lower() == "windows":
        os.system('cls')
    else:
        os.system('clear')

def format_eth(amount):
    """Format ETH amount with symbol."""
    return f"Ξ{amount:.3f}"
