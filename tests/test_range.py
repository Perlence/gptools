from gptools.cli import Range


def test_range():
    r = Range()
    assert r.convert('', None, None) == []
    assert r.convert('1', None, None) == [1]
    assert r.convert('1,2', None, None) == [1, 2]
    assert r.convert('1,2-3', None, None) == [1, 2, 3]
    assert r.convert('1,2-4', None, None) == [1, 2, 3, 4]
