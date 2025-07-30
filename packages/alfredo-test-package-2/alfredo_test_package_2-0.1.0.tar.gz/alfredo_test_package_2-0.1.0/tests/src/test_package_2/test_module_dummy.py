# Test dummy function

from src.test_package_2.module_dummy import dummy_func # full explicit import (could also be from src.test_package_2 import dummy func)

def test_dummy_func():
    assert dummy_func("Alfredo") == "This is Alfredo world 2"