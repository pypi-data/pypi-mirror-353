# Test dummy function

from src.alfredo_test_package.module_dummy import dummy_func # full explicit import (could also be from src.test_package_1 import dummy func)

def test_dummy_func():
    assert dummy_func("Alfredo") == "This is Alfredo world"