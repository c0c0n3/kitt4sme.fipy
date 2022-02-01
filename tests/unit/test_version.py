from fipy import __version__, pyproject_file, pyproject_version


def test_version():
    project_version = pyproject_version(pyproject_file())
    assert __version__ == project_version
