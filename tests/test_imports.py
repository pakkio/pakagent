import pytest

import prepare
import pakmod
import pakdiff
import pakapply
import pakrestore
import pakview

def test_import_modules():
    # Ensure that core modules import without errors and have main functions
    for module in (prepare, pakmod, pakdiff, pakapply, pakrestore, pakview):
        assert hasattr(module, "main"), f"Module {module.__name__} missing main()"
