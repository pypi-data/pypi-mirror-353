import os
from .colors import ToolsCordColors

def generate_ascii_art(text):
    """
    Generate ASCII art for the given text.
    This is a simple implementation - each character is represented by a block of ASCII art.
    
    Args:
        text: The text to convert to ASCII art
    
    Returns:
        A list of strings representing the ASCII art banner
    """
    # Dictionary mapping characters to their ASCII art representation
    ascii_chars = {
        'A': [
            "   █████╗   ",
            "  ██╔══██╗  ",
            "  ███████║  ",
            "  ██╔══██║  ",
            "  ██║  ██║  ",
            "  ╚═╝  ╚═╝  "
        ],
        'B': [
            "  ██████╗   ",
            "  ██╔══██╗  ",
            "  ██████╔╝  ",
            "  ██╔══██╗  ",
            "  ██████╔╝  ",
            "  ╚═════╝   "
        ],
        'C': [
            "  ██████╗   ",
            "  ██╔══██╗  ",
            "  ██║  ╚═╝  ",
            "  ██║  ██╗  ",
            "  ██████╔╝  ",
            "  ╚═════╝   "
        ],
        'D': [
            "  ██████╗   ",
            "  ██╔══██╗  ",
            "  ██║  ██║  ",
            "  ██║  ██║  ",
            "  ██████╔╝  ",
            "  ╚═════╝   "
        ],
        'E': [
            "  ███████╗  ",
            "  ██╔════╝  ",
            "  █████╗    ",
            "  ██╔══╝    ",
            "  ███████╗  ",
            "  ╚══════╝  "
        ],
        'F': [
            "  ███████╗  ",
            "  ██╔════╝  ",
            "  █████╗    ",
            "  ██╔══╝    ",
            "  ██║       ",
            "  ╚═╝       "
        ],
        'G': [
            "  ██████╗   ",
            "  ██╔══██╗  ",
            "  ██║  ╚═╝  ",
            "  ██║ ████╗ ",
            "  ██████╔╝  ",
            "  ╚═════╝   "
        ],
        'H': [
            "  ██╗  ██╗  ",
            "  ██║  ██║  ",
            "  ███████║  ",
            "  ██╔══██║  ",
            "  ██║  ██║  ",
            "  ╚═╝  ╚═╝  "
        ],
        'I': [
            "  ██████╗   ",
            "  ╚════██╗  ",
            "   █████╔╝  ",
            "   ╚═══██╗  ",
            "  ██████╔╝  ",
            "  ╚═════╝   "
        ],
        'J': [
            "     ██╗    ",
            "     ██║    ",
            "     ██║    ",
            "██   ██║    ",
            "╚█████╔╝    ",
            " ╚════╝     "
        ],
        'K': [
            "  ██╗  ██╗  ",
            "  ██║ ██╔╝  ",
            "  █████╔╝   ",
            "  ██╔═██╗   ",
            "  ██║  ██╗  ",
            "  ╚═╝  ╚═╝  "
        ],
        'L': [
            "  ██╗       ",
            "  ██║       ",
            "  ██║       ",
            "  ██║       ",
            "  ███████╗  ",
            "  ╚══════╝  "
        ],
        'M': [
            "  ███╗ ███╗ ",
            "  ████╗████║ ",
            "  ██╔████╔██║ ",
            "  ██║╚██╔╝██║ ",
            "  ██║ ╚═╝ ██║ ",
            "  ╚═╝     ╚═╝ "
        ],
        'N': [
            "  ███╗  ██╗ ",
            "  ████╗ ██║ ",
            "  ██╔██╗██║ ",
            "  ██║╚████║ ",
            "  ██║ ╚███║ ",
            "  ╚═╝  ╚══╝ "
        ],
        'O': [
            "  ██████╗   ",
            "  ██╔══██╗  ",
            "  ██║  ██║  ",
            "  ██║  ██║  ",
            "  ██████╔╝  ",
            "  ╚═════╝   "
        ],
        'P': [
            "  ██████╗   ",
            "  ██╔══██╗  ",
            "  ██████╔╝  ",
            "  ██╔═══╝   ",
            "  ██║       ",
            "  ╚═╝       "
        ],
        'Q': [
            "  ██████╗   ",
            "  ██╔══██╗  ",
            "  ██║  ██║  ",
            "  ██║ ██╔╝  ",
            "  ████╔╝██╗ ",
            "  ╚═══╝ ╚═╝ "
        ],
        'R': [
            "  ██████╗   ",
            "  ██╔══██╗  ",
            "  ██████╔╝  ",
            "  ██╔══██╗  ",
            "  ██║  ██║  ",
            "  ╚═╝  ╚═╝  "
        ],
        'S': [
            "  ███████╗  ",
            "  ██╔════╝  ",
            "  ███████╗  ",
            "  ╚════██║  ",
            "  ███████║  ",
            "  ╚══════╝  "
        ],
        'T': [
            "  ████████╗ ",
            "  ╚══██╔══╝ ",
            "     ██║    ",
            "     ██║    ",
            "     ██║    ",
            "     ╚═╝    "
        ],
        'U': [
            "  ██╗  ██╗  ",
            "  ██║  ██║  ",
            "  ██║  ██║  ",
            "  ██║  ██║  ",
            "  ██████╔╝  ",
            "  ╚═════╝   "
        ],
        'V': [
            "  ██╗  ██╗  ",
            "  ██║  ██║  ",
            "  ██║  ██║  ",
            "  ╚██╗██╔╝  ",
            "   ╚███╔╝   ",
            "    ╚══╝    "
        ],
        'W': [
            "  ██╗    ██╗ ",
            "  ██║    ██║ ",
            "  ██║ █╗ ██║ ",
            "  ██║███╗██║ ",
            "  ╚███╔███╔╝ ",
            "   ╚══╝╚══╝  "
        ],
        'X': [
            "  ██╗  ██╗  ",
            "  ╚██╗██╔╝  ",
            "   ╚███╔╝   ",
            "   ██╔██╗   ",
            "  ██╔╝ ██╗  ",
            "  ╚═╝  ╚═╝  "
        ],
        'Y': [
            "  ██╗  ██╗  ",
            "  ╚██╗██╔╝  ",
            "   ╚███╔╝   ",
            "    ██╔╝    ",
            "    ██║     ",
            "    ╚═╝     "
        ],
        'Z': [
            "  ███████╗  ",
            "  ╚══███╔╝  ",
            "    ███╔╝   ",
            "   ███╔╝    ",
            "  ███████╗  ",
            "  ╚══════╝  "
        ],
        '0': [
            "   ██████╗  ",
            "  ██╔═████╗ ",
            "  ██║██╔██║ ",
            "  ████╔╝██║ ",
            "  ╚██████╔╝ ",
            "   ╚═════╝  "
        ],
        '1': [
            "    ██╗    ",
            "  ████║    ",
            "    ██║    ",
            "    ██║    ",
            "  ██████╗  ",
            "  ╚═════╝  "
        ],
        '2': [
            "  ██████╗   ",
            "  ╚════██╗  ",
            "   █████╔╝  ",
            "  ██╔═══╝   ",
            "  ███████╗  ",
            "  ╚══════╝  "
        ],
        '3': [
            "  ██████╗   ",
            "  ╚════██╗  ",
            "   █████╔╝  ",
            "   ╚═══██╗  ",
            "  ██████╔╝  ",
            "  ╚═════╝   "
        ],
        '4': [
            "  ██╗  ██╗  ",
            "  ██║  ██║  ",
            "  ███████║  ",
            "  ╚════██║  ",
            "       ██║  ",
            "       ╚═╝  "
        ],
        '5': [
            "  ███████╗  ",
            "  ██╔════╝  ",
            "  ███████╗  ",
            "  ╚════██║  ",
            "  ███████║  ",
            "  ╚══════╝  "
        ],
        '6': [
            "   ██████╗  ",
            "  ██╔════╝  ",
            "  ███████╗  ",
            "  ██╔═══██╗ ",
            "  ╚██████╔╝ ",
            "   ╚═════╝  "
        ],
        '7': [
            "  ███████╗  ",
            "  ╚════██║  ",
            "      ██╔╝  ",
            "     ██╔╝   ",
            "     ██║    ",
            "     ╚═╝    "
        ],
        '8': [
            "   █████╗   ",
            "  ██╔══██╗  ",
            "  ╚█████╔╝  ",
            "  ██╔══██╗  ",
            "  ╚█████╔╝  ",
            "   ╚════╝   "
        ],
        '9': [
            "   █████╗   ",
            "  ██╔══██╗  ",
            "  ╚██████║  ",
            "   ╚═══██║  ",
            "   █████╔╝  ",
            "   ╚════╝   "
        ],
        '-': [
            "           ",
            "           ",
            "  ███████╗ ",
            "  ╚══════╝ ",
            "           ",
            "           "
        ],
        '_': [
            "           ",
            "           ",
            "           ",
            "           ",
            "  ███████╗ ",
            "  ╚══════╝ "
        ],
        '.': [
            "           ",
            "           ",
            "           ",
            "           ",
            "    ██╗    ",
            "    ╚═╝    "
        ],
        ' ': [
            "           ",
            "           ",
            "           ",
            "           ",
            "           ",
            "           "
        ],
        '!': [
            "    ██╗    ",
            "    ██║    ",
            "    ██║    ",
            "    ╚═╝    ",
            "    ██╗    ",
            "    ╚═╝    "
        ],
        '@': [
            "   ██████╗  ",
            "  ██╔══██╗  ",
            "  ██║██╔██║ ",
            "  ██║██║██║ ",
            "  ╚█████╔═╝ ",
            "   ╚════╝   "
        ],
        '#': [
            "  ██╗ ██╗  ",
            "  ████████╗ ",
            "  ╚██╔═██╔╝ ",
            "  ████████╗ ",
            "  ╚██╔═██╔╝ ",
            "   ╚═╝ ╚═╝  "
        ]
    }
    
    # Convert text to uppercase since our ASCII art is for uppercase letters
    text = text.upper()
    
    # Initialize the banner with empty lines
    banner = ["", "", "", "", "", ""]
    
    # Build the banner by concatenating the ASCII art for each character
    for char in text:
        if char in ascii_chars:
            for i in range(6):
                banner[i] += ascii_chars[char][i]
        else:
            # For unsupported characters, use spaces
            for i in range(6):
                banner[i] += "           "
    
    return banner

def display_banner(text="TOOLS CORD", base_color=ToolsCordColors.CYAN, style=ToolsCordColors.BOLD):
    """
    Display a centered banner in the terminal with gradient colors.
    
    Args:
        text: The text to display in the banner (default: "TOOLS CORD")
        base_color: Base color from ToolsCordColors (default: CYAN)
        style: Style from ToolsCordColors (default: BOLD)
    """
    # Generate ASCII art for the text
    banner = generate_ascii_art(text)
    
    terminal_width = os.get_terminal_size().columns
    
    # Gradient colors - from cyan to blue
    gradient_colors = [
        ToolsCordColors.CYAN, 
        "\033[38;5;51m",  # Light cyan
        "\033[38;5;45m",  # Light cyan/blue
        "\033[38;5;39m",  # Blue-ish
        "\033[38;5;33m",  # More blue
        ToolsCordColors.DEEPBLUE
    ]
    
    print("\n")
    for i, line in enumerate(banner):
        # Center the line in the terminal
        padding = (terminal_width - len(line)) // 2
        
        # Get the gradient color for this line
        color = gradient_colors[i % len(gradient_colors)]
        
        print(" " * padding + color + style + line + ToolsCordColors.ENDC)
    print("\n")

def display_toolscord_banner(base_color=ToolsCordColors.CYAN, style=ToolsCordColors.BOLD):
    """
    Display the original TOOLSCORD banner (for backward compatibility)
    
    Args:
        base_color: Base color from ToolsCordColors (default: CYAN)
        style: Style from ToolsCordColors (default: BOLD)
    """
    banner = [
        "████████╗ ██████╗  ██████╗ ██╗     ███████╗     ██████╗ ██████╗ ██████╗ ██████╗ ",
        "╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝    ██╔════╝██╔═══██╗██╔══██╗██╔══██╗",
        "   ██║   ██║   ██║██║   ██║██║     ███████╗    ██║     ██║   ██║██████╔╝██║  ██║",
        "   ██║   ██║   ██║██║   ██║██║     ╚════██║    ██║     ██║   ██║██╔══██╗██║  ██║",
        "   ██║   ╚██████╔╝╚██████╔╝███████╗███████║    ╚██████╗╚██████╔╝██║  ██║██████╔╝",
        "   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝     ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═════╝ "
    ]
    
    terminal_width = os.get_terminal_size().columns
    
    # Gradient colors - from cyan to blue
    gradient_colors = [
        ToolsCordColors.CYAN, 
        "\033[38;5;51m",  # Light cyan
        "\033[38;5;45m",  # Light cyan/blue
        "\033[38;5;39m",  # Blue-ish
        "\033[38;5;33m",  # More blue
        ToolsCordColors.DEEPBLUE
    ]
    
    print("\n")
    for i, line in enumerate(banner):
        # Center the line in the terminal
        padding = (terminal_width - len(line)) // 2
        
        # Get the gradient color for this line
        color = gradient_colors[i % len(gradient_colors)]
        
        print(" " * padding + color + style + line + ToolsCordColors.ENDC)
    print("\n") 