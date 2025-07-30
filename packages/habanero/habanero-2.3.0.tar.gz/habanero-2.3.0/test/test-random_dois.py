import pytest

from habanero import Crossref

cr = Crossref()


@pytest.mark.vcr
def test_random_dois():
    """random dois"""
    res = cr.random_dois()
    assert isinstance(res, list)
    assert isinstance(res[0], str)
    assert 10 == len(res)


@pytest.mark.vcr
def test_random_dois_sample_param():
    """random dois - sample parameter"""
    res = cr.random_dois(3)
    assert 3 == len(res)

    res = cr.random_dois(5)
    assert 5 == len(res)
