"""
Enhanced Formatting Module

This module provides enhanced bold and italic formatting for AI responses,
building upon the existing colorful response formatter with improved emphasis.
"""

import re
from typing import List, Tuple
from colors import Colors, ColorPrinter, colorize


class EnhancedFormatter:
    """Enhanced formatter with improved bold and italic support."""
    
    def __init__(self, enable_colors: bool = None):
        """
        Initialize the enhanced formatter.
        
        Args:
            enable_colors (bool): Whether to enable colors. Auto-detect if None.
        """
        self.color_printer = ColorPrinter(enable_colors)
    
    def format_with_enhanced_emphasis(self, text: str) -> str:
        """
        Format text with enhanced bold and italic emphasis.
        
        Args:
            text (str): Text to format
            
        Returns:
            str: Text with enhanced formatting
        """
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
        
        return text
    
    def format_response_with_enhanced_emphasis(self, response: str) -> str:
        """
        Format entire response with enhanced emphasis and structure.
        
        Args:
            response (str): Response to format
            
        Returns:
            str: Formatted response
        """
        if not response.strip():
            return colorize("No response generated.", Colors.BRIGHT_BLACK)
        
        # Split into paragraphs and process each
        paragraphs = [p.strip() for p in response.split('\n\n') if p.strip()]
        formatted_paragraphs = []
        
        for i, paragraph in enumerate(paragraphs):
            # Apply enhanced emphasis formatting
            formatted_paragraph = self.format_with_enhanced_emphasis(paragraph)
            
            # Apply additional paragraph-level formatting
            formatted_paragraph = self._apply_paragraph_formatting(formatted_paragraph, i == 0)
            
            formatted_paragraphs.append(formatted_paragraph)
        
        return '\n\n'.join(formatted_paragraphs)
    
    def _apply_paragraph_formatting(self, paragraph: str, is_first: bool = False) -> str:
        """Apply paragraph-level formatting."""
        # Handle headings
        if paragraph.strip().startswith('#'):
            return self._format_heading(paragraph)
        
        # Handle lists
        if self._is_list_item(paragraph):
            return self._format_list_item(paragraph)
        
        # Handle code blocks
        if '```' in paragraph:
            return self._format_code_block(paragraph)
        
        # Handle quotes
        if paragraph.strip().startswith('>'):
            return self._format_quote(paragraph)
        
        # Regular paragraph
        if is_first:
            return colorize(paragraph, Colors.BRIGHT_WHITE)
        else:
            return colorize(paragraph, Colors.WHITE)
    
    def _format_heading(self, text: str) -> str:
        """Format headings with enhanced colors."""
        level = len(text) - len(text.lstrip('#'))
        heading_text = text.strip('#').strip()
        
        # Apply emphasis formatting to heading text
        heading_text = self.format_with_enhanced_emphasis(heading_text)
        
        if level == 1:
            return colorize(f"{'#' * level} {heading_text}", Colors.BRIGHT_CYAN, Colors.BOLD)
        elif level == 2:
            return colorize(f"{'#' * level} {heading_text}", Colors.CYAN, Colors.BOLD)
        elif level == 3:
            return colorize(f"{'#' * level} {heading_text}", Colors.BLUE, Colors.BOLD)
        else:
            return colorize(f"{'#' * level} {heading_text}", Colors.BRIGHT_BLUE)
    
    def _is_list_item(self, text: str) -> bool:
        """Check if text is a list item."""
        return text.strip().startswith(('•', '-', '*', '1.', '2.', '3.', '4.', '5.'))
    
    def _format_list_item(self, text: str) -> str:
        """Format list items with enhanced emphasis."""
        # Apply emphasis formatting first
        formatted_text = self.format_with_enhanced_emphasis(text)
        
        # Then apply list formatting
        if formatted_text.strip().startswith('•'):
            return colorize('•', Colors.BRIGHT_CYAN) + ' ' + formatted_text.strip()[1:].strip()
        elif formatted_text.strip().startswith(('-', '*')):
            return colorize('▸', Colors.BRIGHT_MAGENTA) + ' ' + formatted_text.strip()[1:].strip()
        elif re.match(r'^\d+\.', formatted_text.strip()):
            number_part = re.match(r'^(\d+\.)', formatted_text.strip()).group(1)
            rest = formatted_text.strip()[len(number_part):].strip()
            return colorize(number_part, Colors.BRIGHT_YELLOW) + ' ' + rest
        else:
            return formatted_text
    
    def _format_code_block(self, text: str) -> str:
        """Format code blocks."""
        if '```' in text:
            parts = text.split('```')
            formatted_parts = []
            for i, part in enumerate(parts):
                if i % 2 == 1:  # Code part
                    # Apply syntax highlighting to code
                    highlighted_code = self._apply_syntax_highlighting(part)
                    formatted_parts.append(colorize(f"```{highlighted_code}```", Colors.BRIGHT_GREEN, background=Colors.DIM))
                else:  # Regular text with emphasis
                    formatted_parts.append(self.format_with_enhanced_emphasis(part))
            return ''.join(formatted_parts)
        else:
            return colorize(text, Colors.BRIGHT_GREEN, Colors.DIM)
    
    def _format_quote(self, text: str) -> str:
        """Format quoted text."""
        quote_text = text.strip('> ').strip()
        formatted_quote = self.format_with_enhanced_emphasis(quote_text)
        return colorize(f"▌ {formatted_quote}", Colors.BRIGHT_BLACK, Colors.ITALIC)
    
    def _apply_syntax_highlighting(self, code: str) -> str:
        """Apply basic syntax highlighting to code."""
        # Keywords
        keywords = ['def', 'class', 'import', 'from', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'return']
        for keyword in keywords:
            code = re.sub(rf'\b{keyword}\b', colorize(keyword, Colors.BRIGHT_MAGENTA, Colors.BOLD), code)
        
        # Strings
        code = re.sub(r'"([^"]*)"', lambda m: colorize(f'"{m.group(1)}"', Colors.BRIGHT_GREEN), code)
        code = re.sub(r"'([^']*)'", lambda m: colorize(f"'{m.group(1)}'", Colors.BRIGHT_GREEN), code)
        
        # Comments
        code = re.sub(r'#.*$', lambda m: colorize(m.group(0), Colors.BRIGHT_BLACK, Colors.ITALIC), code, flags=re.MULTILINE)
        
        return code
    
    def create_enhanced_response_display(self, response: str, query: str = None, title: str = "AI Response") -> str:
        """
        Create an enhanced display for responses with better formatting.
        
        Args:
            response (str): Response text
            query (str): Original query
            title (str): Display title
            
        Returns:
            str: Enhanced formatted display
        """
        # Format the response with enhanced emphasis
        formatted_response = self.format_response_with_enhanced_emphasis(response)
        
        # Create header
        header_line = "═" * 70
        header = colorize(header_line, Colors.BRIGHT_CYAN)
        title_line = colorize(f"🤖 {title}", Colors.BRIGHT_CYAN, Colors.BOLD)
        
        # Create query context if provided
        query_section = ""
        if query:
            query_section = f"\n{colorize('📝 Query:', Colors.BRIGHT_YELLOW, Colors.BOLD)} {colorize(query, Colors.YELLOW)}\n{colorize('─' * 70, Colors.BRIGHT_BLACK)}"
        
        # Create footer
        footer = colorize(header_line, Colors.BRIGHT_CYAN)
        
        # Combine all parts
        return f"\n{header}\n{title_line}{query_section}\n\n{formatted_response}\n\n{footer}"
    
    def print_enhanced_response(self, response: str, query: str = None, title: str = "AI Response"):
        """Print response with enhanced formatting."""
        enhanced_display = self.create_enhanced_response_display(response, query, title)
        print(enhanced_display)


# Global enhanced formatter instance
enhanced_formatter = EnhancedFormatter()


# Convenience functions
def format_with_enhanced_emphasis(text: str) -> str:
    """Format text with enhanced emphasis using global formatter."""
    return enhanced_formatter.format_with_enhanced_emphasis(text)


def format_response_with_enhanced_emphasis(response: str) -> str:
    """Format response with enhanced emphasis using global formatter."""
    return enhanced_formatter.format_response_with_enhanced_emphasis(response)


def print_enhanced_response(response: str, query: str = None, title: str = "AI Response"):
    """Print enhanced response using global formatter."""
    enhanced_formatter.print_enhanced_response(response, query, title)


def create_enhanced_response_display(response: str, query: str = None, title: str = "AI Response") -> str:
    """Create enhanced response display using global formatter."""
    return enhanced_formatter.create_enhanced_response_display(response, query, title)
