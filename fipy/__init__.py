from pathlib import Path
from typing import Optional, Tuple

__version__ = '0.1.0'


def pyproject_file() -> Path:
    this_file = Path(__file__)
    root_dir = this_file.parent.parent
    return root_dir / 'pyproject.toml'

def parse_key(line: str) -> Tuple[str, str]:
    key, value = line.strip().partition('=')[::2]  # (*)
    return key.strip(), value.strip().strip('"').strip("'")
# NOTE. [::2] won't bomb out if there's no key-value pair. E.g.
# >>> k, v = "v  1".partition('=')[::2]
# >>> k, v
# ('v 1', '')

def pyproject_version(pyproject_pathname: Path) -> Optional[str]:
    with open(pyproject_pathname) as f:
        for line in f:
            key, value = parse_key(line)
            if key == 'version':
                return value
        return None
