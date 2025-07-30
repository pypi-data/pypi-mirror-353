class ToolsCordColors:
    # Basic colors
    BLACK        = '\033[30m'
    RED          = '\033[31m'
    GREEN        = '\033[32m'
    YELLOW       = '\033[33m'
    BLUE         = '\033[34m'
    MAGENTA      = '\033[35m'
    CYAN         = '\033[36m'
    WHITE        = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK   = '\033[90m'
    BRIGHT_RED     = '\033[91m'
    BRIGHT_GREEN   = '\033[92m'
    BRIGHT_YELLOW  = '\033[93m'
    BRIGHT_BLUE    = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN    = '\033[96m'
    BRIGHT_WHITE   = '\033[97m'
    
    # Semantic colors
    TIME         = '\033[90m'
    OKBLUE       = '\033[94m'
    DEEPBLUE     = '\033[34m'
    PURPLE       = '\033[95m'
    FAIL         = '\033[91m'
    SUCCESS      = '\033[92m'
    HEADER       = '\033[95m'
    OKGREEN      = '\033[92m'
    WARNING      = '\033[93m'
    DARKGREEN    = '\033[32m'
    
    # Text styles
    BOLD         = '\033[1m'
    FAINT        = '\033[2m'
    ITALIC       = '\033[3m'
    UNDERLINE    = '\033[4m'
    BLINK        = '\033[5m'
    REVERSE      = '\033[7m'
    STRIKE       = '\033[9m'
    
    # Reset
    ENDC         = '\033[0m'
    
    # Brand colors
    PINK         = '\033[38;5;13m'
    TWITTERBLUE  = '\033[38;2;29;161;242m'
    CLOUDFLARE_ORANGE = '\033[38;2;243;128;32m'
    GITHUB_PURPLE = '\033[38;2;111;66;193m'
    INSTAGRAM_PURPLE = '\033[38;2;138;58;185m'
    FACEBOOK_BLUE = '\033[38;2;59;89;152m'
    YOUTUBE_RED = '\033[38;2;255;0;0m'
    LINKEDIN_BLUE = '\033[38;2;0;119;181m'
    DISCORD_BLURPLE = '\033[38;2;114;137;218m'
    SPOTIFY_GREEN = '\033[38;2;30;215;96m'
    TWITCH_PURPLE = '\033[38;2;100;65;165m'
    SLACK_RED = '\033[38;2;221;22;27m'
    
    # 256 color palette examples
    ORANGE       = '\033[38;5;208m'
    LIME         = '\033[38;5;118m'
    GOLD         = '\033[38;5;220m'
    TEAL         = '\033[38;5;30m'
    LAVENDER     = '\033[38;5;183m'
    MAROON       = '\033[38;5;88m'
    NAVY         = '\033[38;5;17m'
    OLIVE        = '\033[38;5;100m'
    MINT         = '\033[38;5;121m'
    CORAL        = '\033[38;5;209m'
    SALMON       = '\033[38;5;209m'
    VIOLET       = '\033[38;5;93m'
    TURQUOISE    = '\033[38;5;45m'
    CHOCOLATE    = '\033[38;5;94m'
    CRIMSON      = '\033[38;5;160m'
    STEEL_BLUE   = '\033[38;5;67m'
    FOREST_GREEN = '\033[38;5;22m'
    ROYAL_BLUE   = '\033[38;5;20m'
    
    # Background colors
    BG_BLACK     = '\033[40m'
    BG_RED       = '\033[41m'
    BG_GREEN     = '\033[42m'
    BG_YELLOW    = '\033[43m'
    BG_BLUE      = '\033[44m'
    BG_MAGENTA   = '\033[45m'
    BG_CYAN      = '\033[46m'
    BG_WHITE     = '\033[47m'
    
    # GitHub branding
    GITHUB_BHASKAR = '\033[38;2;111;66;193m' # github.com/bhaskarsaikia-17
    
    @staticmethod
    def colorize(text, color):
        """Apply a color to text and reset after"""
        return f"{color}{text}{ToolsCordColors.ENDC}"
    
    @staticmethod
    def red(text):
        """Print text in red"""
        return ToolsCordColors.colorize(text, ToolsCordColors.RED)
    
    @staticmethod
    def green(text):
        """Print text in green"""
        return ToolsCordColors.colorize(text, ToolsCordColors.GREEN)
    
    @staticmethod
    def yellow(text):
        """Print text in yellow"""
        return ToolsCordColors.colorize(text, ToolsCordColors.YELLOW)
    
    @staticmethod
    def blue(text):
        """Print text in blue"""
        return ToolsCordColors.colorize(text, ToolsCordColors.BLUE)
    
    @staticmethod
    def magenta(text):
        """Print text in magenta"""
        return ToolsCordColors.colorize(text, ToolsCordColors.MAGENTA)
    
    @staticmethod
    def cyan(text):
        """Print text in cyan"""
        return ToolsCordColors.colorize(text, ToolsCordColors.CYAN)
    
    @staticmethod
    def white(text):
        """Print text in white"""
        return ToolsCordColors.colorize(text, ToolsCordColors.WHITE)
    
    @staticmethod
    def bold(text):
        """Make text bold"""
        return ToolsCordColors.colorize(text, ToolsCordColors.BOLD)
    
    @staticmethod
    def underline(text):
        """Underline text"""
        return ToolsCordColors.colorize(text, ToolsCordColors.UNDERLINE)
    
    @staticmethod
    def italic(text):
        """Italicize text"""
        return ToolsCordColors.colorize(text, ToolsCordColors.ITALIC)
    
    @staticmethod
    def success(text):
        """Format text as success message"""
        return ToolsCordColors.colorize(text, ToolsCordColors.SUCCESS)
    
    @staticmethod
    def warning(text):
        """Format text as warning message"""
        return ToolsCordColors.colorize(text, ToolsCordColors.WARNING)
    
    @staticmethod
    def error(text):
        """Format text as error message"""
        return ToolsCordColors.colorize(text, ToolsCordColors.FAIL)
    
    @staticmethod
    def info(text):
        """Format text as info message"""
        return ToolsCordColors.colorize(text, ToolsCordColors.OKBLUE)
    
    @staticmethod
    def header(text):
        """Format text as header"""
        return ToolsCordColors.colorize(text, ToolsCordColors.HEADER)
    
    @staticmethod
    def github(text):
        """Format text with GitHub branding"""
        return ToolsCordColors.colorize(text, ToolsCordColors.GITHUB_BHASKAR)
    
    @staticmethod
    def rainbow(text):
        """Format text with rainbow colors"""
        colors = [
            ToolsCordColors.RED,
            ToolsCordColors.ORANGE,
            ToolsCordColors.YELLOW,
            ToolsCordColors.GREEN,
            ToolsCordColors.BLUE,
            ToolsCordColors.PURPLE
        ]
        result = ""
        for i, char in enumerate(text):
            if char.strip():  # Only colorize non-whitespace
                color = colors[i % len(colors)]
                result += f"{color}{char}{ToolsCordColors.ENDC}"
            else:
                result += char
        return result
    
    @staticmethod
    def gradient(text, start_color, end_color):
        """
        Create a gradient effect between two RGB colors
        start_color and end_color should be tuples of (r,g,b)
        """
        if not text:
            return ""
            
        result = ""
        for i, char in enumerate(text):
            if char.strip():  # Only colorize non-whitespace
                # Calculate the gradient color for this position
                progress = i / (len(text) - 1) if len(text) > 1 else 0
                r = int(start_color[0] + (end_color[0] - start_color[0]) * progress)
                g = int(start_color[1] + (end_color[1] - start_color[1]) * progress)
                b = int(start_color[2] + (end_color[2] - start_color[2]) * progress)
                
                # Apply the color
                result += f"\033[38;2;{r};{g};{b}m{char}{ToolsCordColors.ENDC}"
            else:
                result += char
        return result
    
    @staticmethod
    def print_red(text):
        """Print text in red"""
        print(ToolsCordColors.red(text))
    
    @staticmethod
    def print_green(text):
        """Print text in green"""
        print(ToolsCordColors.green(text))
    
    @staticmethod
    def print_yellow(text):
        """Print text in yellow"""
        print(ToolsCordColors.yellow(text))
    
    @staticmethod
    def print_blue(text):
        """Print text in blue"""
        print(ToolsCordColors.blue(text))
    
    @staticmethod
    def print_success(text):
        """Print success message"""
        print(ToolsCordColors.success(text))
    
    @staticmethod
    def print_error(text):
        """Print error message"""
        print(ToolsCordColors.error(text))
    
    @staticmethod
    def print_warning(text):
        """Print warning message"""
        print(ToolsCordColors.warning(text))
    
    @staticmethod
    def print_info(text):
        """Print info message"""
        print(ToolsCordColors.info(text))
    
    @staticmethod
    def print_rainbow(text):
        """Print text with rainbow colors"""
        print(ToolsCordColors.rainbow(text))
    
    @staticmethod
    def print_github(text):
        """Print text with GitHub branding"""
        print(ToolsCordColors.github(text)) 