import pytest

import send
import modify
import pakdiff
import apply
import revert

def test_import_modules():
    # Ensure that core modules import without errors and have main functions
    for module in (send, modify, pakdiff, apply, revert):
        assert hasattr(module, "main"), f"Module {module.__name__} missing main()"
