
from purealgebra import add, subtract, multiply, divide

def test_add():
    assert add(2, 3) == 5

def test_subtract():
    assert subtract(5, 3) == 2

def test_multiply():
    assert multiply(2, 4) == 8

def test_divide():
    assert divide(8, 2) == 4
