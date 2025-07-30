from .logger import Logger
from .banner import display_banner
from .colors import ToolsCordColors

# Create convenience functions for direct import
colorize = ToolsCordColors.colorize
red = ToolsCordColors.red
green = ToolsCordColors.green
yellow = ToolsCordColors.yellow
blue = ToolsCordColors.blue
magenta = ToolsCordColors.magenta
cyan = ToolsCordColors.cyan
white = ToolsCordColors.white
bold = ToolsCordColors.bold
underline = ToolsCordColors.underline
italic = ToolsCordColors.italic
success = ToolsCordColors.success
warning = ToolsCordColors.warning
error = ToolsCordColors.error
info = ToolsCordColors.info
header = ToolsCordColors.header
rainbow = ToolsCordColors.rainbow
gradient = ToolsCordColors.gradient
github = ToolsCordColors.github

# Convenience print functions
print_red = ToolsCordColors.print_red
print_green = ToolsCordColors.print_green
print_yellow = ToolsCordColors.print_yellow
print_blue = ToolsCordColors.print_blue
print_success = ToolsCordColors.print_success
print_error = ToolsCordColors.print_error
print_warning = ToolsCordColors.print_warning
print_info = ToolsCordColors.print_info
print_rainbow = ToolsCordColors.print_rainbow
print_github = ToolsCordColors.print_github

__all__ = [
    "Logger", "display_banner", "ToolsCordColors",
    "colorize", "red", "green", "yellow", "blue", "magenta", "cyan", "white",
    "bold", "underline", "italic", "success", "warning", "error", "info", "header",
    "rainbow", "gradient", "github",
    "print_red", "print_green", "print_yellow", "print_blue",
    "print_success", "print_error", "print_warning", "print_info",
    "print_rainbow", "print_github"
]