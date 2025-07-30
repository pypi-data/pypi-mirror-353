# ToolsCord

A customizable terminal UI library with a centered banner and advanced logging features. ToolsCord provides colorful, styled terminal output with different log types, custom styling, and formatting options.

## Features

- Single-line "TOOLS CORD" banner display with gradient colors
- Personal logger style with "{time} • {type} > message" format
- Various log types with appropriate styling: info, success, warning, error, debug, etc.
- Custom color palette including special colors like Twitter Blue and Cloudflare Orange
- Customizable text formatting: colors, bold text, underlines
- Customizable bullet styles between time and type
- Timestamps on log messages
- Divider lines

## Installation

You can install ToolsCord directly from GitHub:

```bash
pip install toolscord
```

## Usage

### Basic Usage

```python
from toolscord import Logger, display_banner, ToolsCordColors

# Display the TOOLSCORD banner
display_banner()

# Create a logger instance
logger = Logger()

# Use different log types
logger.info("This is an information message")
logger.success("Operation completed successfully")
logger.warning("This is a warning message")
logger.error("An error occurred")
```

### Customizing the Output

```python
# Create a logger without timestamps
logger = Logger(show_time=False)

# Use formatting options
logger.log("Bold text", bold=True)
logger.log("Underlined text", underline=True)
logger.log("Custom color", color=ToolsCordColors.PINK)
logger.log("Twitter Blue color", color=ToolsCordColors.TWITTERBLUE)

# Print a divider
logger.divider("=", 60, ToolsCordColors.CYAN)
```

### Customizing the Banner

```python
from toolscord import display_banner, ToolsCordColors

# Display the banner with different base colors
display_banner(base_color=ToolsCordColors.TWITTERBLUE)
```

### Logger Usage

```python
from toolscord import Logger, ToolsCordColors

# Create a logger with default settings
logger = Logger()

# Basic log types
logger.info("This is an information message")     # {time} • INFO > This is an information message
logger.warning("This is a warning message")       # {time} • WARN > This is a warning message
logger.error("An error occurred")                 # {time} • ERROR > An error occurred
logger.success("Operation completed")             # {time} • SUCCESS > Operation completed

# Custom bullet style
logger = Logger(bullet_style="→")
logger.info("Using arrow bullet style")           # {time} → INFO > Using arrow bullet style

# Try other bullet styles
logger = Logger(bullet_style="⌁")                 # Zigzag
logger = Logger(bullet_style="⨠")                 # Square donut
logger = Logger(bullet_style="‣")                 # Triangle 
logger = Logger(bullet_style="⁕")                 # Flower
logger = Logger(bullet_style="⁙")                 # Dot pattern

# Without timestamp
logger = Logger(show_time=False)
logger.info("No timestamp shown")                 # INFO > No timestamp shown
```

### Available Colors

ToolsCord provides a range of predefined colors that you can use:

```python
from toolscord import ToolsCordColors

# Basic colors
ToolsCordColors.CYAN        # Cyan color
ToolsCordColors.SUCCESS     # Green color for success
ToolsCordColors.WARNING     # Yellow color for warnings
ToolsCordColors.FAIL        # Red color for errors
ToolsCordColors.PURPLE      # Purple color
ToolsCordColors.DEEPBLUE    # Deep blue color

# Special colors
ToolsCordColors.PINK              # Pink color
ToolsCordColors.TWITTERBLUE       # Twitter blue brand color
ToolsCordColors.CLOUDFLARE_ORANGE # Cloudflare orange brand color
```

## Example

See `example.py` and `color_demo.py` for a complete demonstration of ToolsCord's features.

## Requirements

- Python 3.6+

## License

MIT