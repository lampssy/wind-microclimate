import pytest
from PACKAGE_NAME.PACKAGE_NAME import func


@pytest.mark.parametrize("test_input,expected", [
    ('test', 0)
])
def test_func(test_input, expected):
    f = func(test_input)
    assert f == expected


@pytest.mark.skip(reason="feature not supported yet")
def test_future():
    f = func_2('test')
    assert f == 1


@pytest.mark.xfail
def test_divide_by_zero():
    assert 1 / 0 == 1


@pytest.mark.xfail
def test_db_slap(pytest_fixture):
    assert ...
