"""
Color utilities for the RAG application.

This module provides ANSI color codes and utility functions for colorizing terminal output.
"""

import sys
from typing import Optional


class Colors:
    """ANSI color codes for terminal output."""
    
    # Reset
    RESET = '\033[0m'
    
    # Regular colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # Text styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    STRIKETHROUGH = '\033[9m'


class ColorPrinter:
    """Utility class for printing colored text."""
    
    def __init__(self, enable_colors: bool = None):
        """
        Initialize ColorPrinter.
        
        Args:
            enable_colors (bool): Whether to enable colors. If None, auto-detect based on terminal support.
        """
        if enable_colors is None:
            # Auto-detect color support
            self.colors_enabled = self._supports_color()
        else:
            self.colors_enabled = enable_colors
    
    def _supports_color(self) -> bool:
        """
        Check if the terminal supports colors.
        
        Returns:
            bool: True if colors are supported, False otherwise
        """
        # Check if stdout is a TTY and not redirected
        if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
            return False
        
        # Check environment variables
        import os
        term = os.environ.get('TERM', '')
        if 'color' in term.lower() or term in ['xterm', 'xterm-256color', 'screen', 'screen-256color']:
            return True
        
        # Check for Windows terminal
        if sys.platform == 'win32':
            try:
                import colorama
                colorama.init()
                return True
            except ImportError:
                return False
        
        return True
    
    def colorize(self, text: str, color: str, style: Optional[str] = None) -> str:
        """
        Colorize text with the given color and optional style.
        
        Args:
            text (str): Text to colorize
            color (str): Color code
            style (str, optional): Style code
            
        Returns:
            str: Colorized text if colors are enabled, otherwise plain text
        """
        if not self.colors_enabled:
            return text
        
        result = color + text + Colors.RESET
        if style:
            result = style + result
        
        return result
    
    def print_colored(self, text: str, color: str, style: Optional[str] = None, **kwargs):
        """
        Print colored text.
        
        Args:
            text (str): Text to print
            color (str): Color code
            style (str, optional): Style code
            **kwargs: Additional arguments for print()
        """
        colored_text = self.colorize(text, color, style)
        print(colored_text, **kwargs)
    
    def success(self, text: str, **kwargs):
        """Print success message in green."""
        self.print_colored(f"✓ {text}", Colors.BRIGHT_GREEN, **kwargs)
    
    def error(self, text: str, **kwargs):
        """Print error message in red."""
        self.print_colored(f"✗ {text}", Colors.BRIGHT_RED, **kwargs)
    
    def warning(self, text: str, **kwargs):
        """Print warning message in yellow."""
        self.print_colored(f"⚠️  {text}", Colors.BRIGHT_YELLOW, **kwargs)
    
    def info(self, text: str, **kwargs):
        """Print info message in blue."""
        self.print_colored(f"ℹ️  {text}", Colors.BRIGHT_BLUE, **kwargs)
    
    def header(self, text: str, **kwargs):
        """Print header text in bold cyan."""
        self.print_colored(text, Colors.BRIGHT_CYAN, Colors.BOLD, **kwargs)
    
    def subheader(self, text: str, **kwargs):
        """Print subheader text in cyan."""
        self.print_colored(text, Colors.CYAN, **kwargs)
    
    def command(self, text: str, **kwargs):
        """Print command text in magenta."""
        self.print_colored(text, Colors.BRIGHT_MAGENTA, **kwargs)
    
    def prompt(self, text: str, **kwargs):
        """Print prompt text in bright white."""
        self.print_colored(text, Colors.BRIGHT_WHITE, Colors.BOLD, **kwargs)
    
    def dim(self, text: str, **kwargs):
        """Print dimmed text."""
        self.print_colored(text, Colors.BRIGHT_BLACK, **kwargs)


# Global color printer instance
color_printer = ColorPrinter()


# Convenience functions
def colorize(text: str, color: str, style: Optional[str] = None) -> str:
    """Colorize text using the global color printer."""
    return color_printer.colorize(text, color, style)


def print_success(text: str, **kwargs):
    """Print success message."""
    color_printer.success(text, **kwargs)


def print_error(text: str, **kwargs):
    """Print error message."""
    color_printer.error(text, **kwargs)


def print_warning(text: str, **kwargs):
    """Print warning message."""
    color_printer.warning(text, **kwargs)


def print_info(text: str, **kwargs):
    """Print info message."""
    color_printer.info(text, **kwargs)


def print_header(text: str, **kwargs):
    """Print header text."""
    color_printer.header(text, **kwargs)


def print_subheader(text: str, **kwargs):
    """Print subheader text."""
    color_printer.subheader(text, **kwargs)


def print_command(text: str, **kwargs):
    """Print command text."""
    color_printer.command(text, **kwargs)


def print_prompt(text: str, **kwargs):
    """Print prompt text."""
    color_printer.prompt(text, **kwargs)


def print_dim(text: str, **kwargs):
    """Print dimmed text."""
    color_printer.dim(text, **kwargs)
