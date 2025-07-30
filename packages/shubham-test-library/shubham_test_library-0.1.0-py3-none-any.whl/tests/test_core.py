# tests/test_core.py
import pytest
from shubham_test_library.core import main_function

def test_main_function():
    result = main_function(5)
    assert result == 10

def test_main_function_with_zero():
    result = main_function(0)
    assert result == 0