from fipy import __version__, project_version


def test_version():
    assert __version__ == project_version
