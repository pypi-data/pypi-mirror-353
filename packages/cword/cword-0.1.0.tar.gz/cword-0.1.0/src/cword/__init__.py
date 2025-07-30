"""
cword - A CLI spelling assistant powered by Google Gemini AI

A powerful command-line tool for checking and correcting spelling, grammar, and text quality
using Google's Gemini AI model.
"""

__version__ = "0.1.0"
__author__ = "Baraa"
__email__ = "baraa0email@gmail.com"

from .cli import main as run

__all__ = ['run']
