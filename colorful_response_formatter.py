"""
Colorful Response Formatter Module

This module provides enhanced colorful formatting for AI responses,
making them more visually appealing and easier to read.
"""

import re
from typing import List, Tuple
from colors import Colors, ColorPrinter, colorize


class ColorfulResponseFormatter:
    """Formats AI responses with beautiful colors and styling."""
    
    def __init__(self, enable_colors: bool = None):
        """
        Initialize the colorful response formatter.
        
        Args:
            enable_colors (bool): Whether to enable colors. Auto-detect if None.
        """
        self.color_printer = ColorPrinter(enable_colors)
    
    def format_response(self, response: str, query: str = None) -> str:
        """
        Format an AI response with beautiful colors and styling.
        
        Args:
            response (str): The AI response to format
            query (str): The original query (optional, for context)
            
        Returns:
            str: Beautifully formatted response
        """
        if not response.strip():
            return colorize("No response generated.", Colors.BRIGHT_BLACK)
        
        # Split response into paragraphs
        paragraphs = [p.strip() for p in response.split('\n\n') if p.strip()]
        formatted_paragraphs = []
        
        for i, paragraph in enumerate(paragraphs):
            formatted_paragraph = self._format_paragraph(paragraph, i == 0)
            formatted_paragraphs.append(formatted_paragraph)
        
        return '\n\n'.join(formatted_paragraphs)
    
    def _format_paragraph(self, paragraph: str, is_first: bool = False) -> str:
        """
        Format a single paragraph with colors.
        
        Args:
            paragraph (str): Paragraph to format
            is_first (bool): Whether this is the first paragraph
            
        Returns:
            str: Formatted paragraph
        """
        # Handle different types of content
        if self._is_list_item(paragraph):
            return self._format_list_item(paragraph)
        elif self._is_code_block(paragraph):
            return self._format_code_block(paragraph)
        elif self._is_heading(paragraph):
            return self._format_heading(paragraph)
        elif self._contains_emphasis(paragraph):
            return self._format_emphasized_text(paragraph)
        else:
            return self._format_regular_paragraph(paragraph, is_first)
    
    def _is_list_item(self, text: str) -> bool:
        """Check if text is a list item."""
        return text.strip().startswith(('•', '-', '*', '1.', '2.', '3.', '4.', '5.'))
    
    def _is_code_block(self, text: str) -> bool:
        """Check if text is a code block."""
        return '```' in text or text.strip().startswith('    ')
    
    def _is_heading(self, text: str) -> bool:
        """Check if text is a heading."""
        return text.strip().startswith('#') or (len(text) < 100 and text.isupper())
    
    def _contains_emphasis(self, text: str) -> bool:
        """Check if text contains emphasis markers."""
        return any(marker in text for marker in ['**', '*', '__', '_', '`'])
    
    def _format_list_item(self, text: str) -> str:
        """Format list items with colors."""
        # Color the bullet point
        if text.strip().startswith('•'):
            return colorize('•', Colors.BRIGHT_CYAN) + ' ' + colorize(text.strip()[1:].strip(), Colors.WHITE)
        elif text.strip().startswith(('-', '*')):
            return colorize('▸', Colors.BRIGHT_MAGENTA) + ' ' + colorize(text.strip()[1:].strip(), Colors.WHITE)
        elif re.match(r'^\d+\.', text.strip()):
            number_part = re.match(r'^(\d+\.)', text.strip()).group(1)
            rest = text.strip()[len(number_part):].strip()
            return colorize(number_part, Colors.BRIGHT_YELLOW) + ' ' + colorize(rest, Colors.WHITE)
        else:
            return colorize(text, Colors.WHITE)
    
    def _format_code_block(self, text: str) -> str:
        """Format code blocks with colors."""
        if '```' in text:
            # Handle markdown code blocks
            parts = text.split('```')
            formatted_parts = []
            for i, part in enumerate(parts):
                if i % 2 == 1:  # Code part
                    formatted_parts.append(colorize(f"```{part}```", Colors.BRIGHT_GREEN, Colors.DIM))
                else:  # Regular text
                    formatted_parts.append(colorize(part, Colors.WHITE))
            return ''.join(formatted_parts)
        else:
            # Handle indented code
            return colorize(text, Colors.BRIGHT_GREEN, Colors.DIM)
    
    def _format_heading(self, text: str) -> str:
        """Format headings with colors."""
        if text.strip().startswith('#'):
            # Markdown heading
            level = len(text) - len(text.lstrip('#'))
            heading_text = text.strip('#').strip()
            if level == 1:
                return colorize(f"{'#' * level} {heading_text}", Colors.BRIGHT_CYAN, Colors.BOLD)
            elif level == 2:
                return colorize(f"{'#' * level} {heading_text}", Colors.CYAN, Colors.BOLD)
            else:
                return colorize(f"{'#' * level} {heading_text}", Colors.BLUE, Colors.BOLD)
        else:
            # All caps heading
            return colorize(text, Colors.BRIGHT_CYAN, Colors.BOLD)
    
    def _format_emphasized_text(self, text: str) -> str:
        """Format text with enhanced emphasis markers."""
        # Handle triple emphasis (***text***) - bold + italic combined
        text = re.sub(r'\*\*\*(.*?)\*\*\*', 
                     lambda m: colorize(m.group(1), Colors.BRIGHT_YELLOW + Colors.BOLD + Colors.ITALIC), text)
        
        # Handle bold text (**text**) - make it more prominent
        text = re.sub(r'\*\*(.*?)\*\*', 
                     lambda m: colorize(m.group(1), Colors.BRIGHT_WHITE, Colors.BOLD), text)
        
        # Handle italic text (*text*) - make it more elegant
        text = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', 
                     lambda m: colorize(m.group(1), Colors.BRIGHT_CYAN, Colors.ITALIC), text)
        
        # Handle underlined bold (__text__)
        text = re.sub(r'__(.*?)__', 
                     lambda m: colorize(m.group(1), Colors.BRIGHT_MAGENTA + Colors.BOLD + Colors.UNDERLINE), text)
        
        # Handle underlined italic (_text_)
        text = re.sub(r'(?<!_)_([^_]+?)_(?!_)', 
                     lambda m: colorize(m.group(1), Colors.CYAN + Colors.ITALIC + Colors.UNDERLINE), text)
        
        # Handle strikethrough (~~text~~)
        text = re.sub(r'~~(.*?)~~', 
                     lambda m: colorize(m.group(1), Colors.BRIGHT_BLACK, Colors.STRIKETHROUGH), text)
        
        # Handle inline code with better visibility (`code`)
        text = re.sub(r'`([^`]+?)`', 
                     lambda m: colorize(f" {m.group(1)} ", Colors.BRIGHT_GREEN, Colors.BOLD), text)
        
        # Handle highlighted text (==text==) - simulate highlight with bright background
        text = re.sub(r'==(.*?)==', 
                     lambda m: colorize(m.group(1), Colors.BLACK + Colors.BG_YELLOW, Colors.BOLD), text)
        
        # Color the remaining text
        return colorize(text, Colors.WHITE)
    
    def _format_regular_paragraph(self, text: str, is_first: bool = False) -> str:
        """Format regular paragraphs."""
        # Highlight important words and phrases
        highlighted_text = self._highlight_keywords(text)
        
        if is_first:
            # Make first paragraph slightly brighter
            return colorize(highlighted_text, Colors.BRIGHT_WHITE)
        else:
            return colorize(highlighted_text, Colors.WHITE)
    
    def _highlight_keywords(self, text: str) -> str:
        """Highlight important keywords in the text."""
        # Define keywords to highlight
        keywords = [
            # Technical terms
            'API', 'database', 'server', 'client', 'HTTP', 'HTTPS', 'JSON', 'XML',
            'Python', 'JavaScript', 'SQL', 'HTML', 'CSS', 'React', 'Node.js',
            
            # Important concepts
            'important', 'note', 'warning', 'error', 'success', 'failed', 'completed',
            'required', 'optional', 'recommended', 'deprecated',
            
            # Action words
            'install', 'configure', 'setup', 'deploy', 'build', 'test', 'debug',
            'create', 'update', 'delete', 'modify', 'execute', 'run',
            
            # Status words
            'active', 'inactive', 'enabled', 'disabled', 'online', 'offline'
        ]
        
        # Highlight keywords (case-insensitive)
        for keyword in keywords:
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            text = pattern.sub(lambda m: colorize(m.group(0), Colors.BRIGHT_YELLOW), text)
        
        # Highlight numbers
        text = re.sub(r'\b\d+\b', lambda m: colorize(m.group(0), Colors.BRIGHT_CYAN), text)
        
        # Highlight URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        text = re.sub(url_pattern, lambda m: colorize(m.group(0), Colors.BRIGHT_BLUE, Colors.UNDERLINE), text)
        
        # Highlight file paths
        path_pattern = r'[/\\][\w\-_./\\]+'
        text = re.sub(path_pattern, lambda m: colorize(m.group(0), Colors.BRIGHT_MAGENTA), text)
        
        return text
    
    def print_formatted_response(self, response: str, query: str = None):
        """
        Print a beautifully formatted response.
        
        Args:
            response (str): The AI response to format and print
            query (str): The original query (optional)
        """
        # Print header
        print(colorize("\n" + "═" * 60, Colors.BRIGHT_CYAN))
        print(colorize("🤖 AI RESPONSE", Colors.BRIGHT_CYAN, Colors.BOLD))
        print(colorize("═" * 60, Colors.BRIGHT_CYAN))
        
        # Print query context if provided
        if query:
            print(colorize(f"📝 Query: {query}", Colors.BRIGHT_BLACK))
            print(colorize("─" * 60, Colors.BRIGHT_BLACK))
        
        # Print formatted response
        formatted_response = self.format_response(response, query)
        print(f"\n{formatted_response}\n")
        
        # Print footer
        print(colorize("═" * 60, Colors.BRIGHT_CYAN))
    
    def create_response_box(self, response: str, title: str = "AI Response") -> str:
        """
        Create a boxed response with borders.
        
        Args:
            response (str): Response text
            title (str): Box title
            
        Returns:
            str: Boxed response
        """
        lines = response.split('\n')
        max_width = max(len(line) for line in lines) if lines else 0
        max_width = max(max_width, len(title) + 4)
        
        # Create box
        top_border = colorize("┌" + "─" * (max_width + 2) + "┐", Colors.BRIGHT_CYAN)
        title_line = colorize(f"│ {title.center(max_width)} │", Colors.BRIGHT_CYAN, Colors.BOLD)
        separator = colorize("├" + "─" * (max_width + 2) + "┤", Colors.BRIGHT_CYAN)
        bottom_border = colorize("└" + "─" * (max_width + 2) + "┘", Colors.BRIGHT_CYAN)
        
        # Format content lines
        content_lines = []
        for line in lines:
            padded_line = line.ljust(max_width)
            content_lines.append(colorize(f"│ {padded_line} │", Colors.CYAN))
        
        # Combine all parts
        box_parts = [top_border, title_line, separator] + content_lines + [bottom_border]
        return '\n'.join(box_parts)


# Global formatter instance
response_formatter = ColorfulResponseFormatter()


# Convenience functions
def format_response(response: str, query: str = None) -> str:
    """Format response using the global formatter."""
    return response_formatter.format_response(response, query)


def print_colorful_response(response: str, query: str = None):
    """Print colorful response using the global formatter."""
    response_formatter.print_formatted_response(response, query)


def create_response_box(response: str, title: str = "AI Response") -> str:
    """Create response box using the global formatter."""
    return response_formatter.create_response_box(response, title)
