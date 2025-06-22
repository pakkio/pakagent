import pytest

import send
import modify
import show_answer
import apply
import revert

def test_import_modules():
    # Ensure that core modules import without errors and have main functions
    for module in (send, modify, show_answer, apply, revert):
        assert hasattr(module, "main"), f"Module {module.__name__} missing main()"
