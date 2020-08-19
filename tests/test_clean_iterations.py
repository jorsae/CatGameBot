import pytest
import sys
sys.path.append('.')
from settings import Settings
import event

settings = Settings('test_settings.json')
settings.parse_settings()

def test_clean_iterations():
    ret = event.clean_iterations(1)
    assert(ret) == 1

def test_clean_iterations_large_number():
    ret = event.clean_iterations(1000)
    assert(ret) == 10

def test_clean_iterations_negative_number():
    ret = event.clean_iterations(-4)
    assert(ret) == 1

def test_clean_iterations_no_number():
    ret = event.clean_iterations(None)
    assert(ret) == 1

def test_clean_iterations_string():
    ret = event.clean_iterations("2")
    assert(ret) == 1

def test_clean_iterations_boolean():
    ret = event.clean_iterations(False)
    assert(ret) == 1