
# shubham_test_library/utils.py
"""
Utility functions for shubham_test_library.

This module contains helper functions and utilities that support
the main functionality of the library.
"""

import re
import json
from typing import Any, Dict, List, Optional, Union
from datetime import datetime


def helper_function(text: str) -> str:
    """
    A simple helper function that capitalizes each word in a string.
    
    Args:
        text (str): The input text to process
        
    Returns:
        str: Text with each word capitalized
        
    Example:
        >>> helper_function("hello world")
        'Hello World'
    """
    return text.title()
