# kitt4sme.fipy
Python utils for a little sweeter FIWARE experience.


### Importing in your project

We ship no PyPi packages. Install directly from GitHub. FiPy adopts
semantic versioning and each version gets tagged in this repo with
a tag in the format `vM.m.p` where `M`, `m` and `p` are the major,
minor and patch numbers. For example, if you'd like to import FiPy
version `0.1.0`, use the tag `v0.1.0`. Poetry users can do that just
by adding a line like the following to the `[tool.poetry.dependencies]`
table in their `pyproject.toml`

```toml
fipy = { git = "https://github.com/c0c0n3/kitt4sme.fipy.git", tag = "v0.1.0" }
```

Other dependency management tools work similarly---e.g. with Pipenv
it's also a no-brainer.


### Hacking

Install Python (`>= 3.8`), Poetry (`>=1.1`) and the usual Docker
stack (Engine `>= 20.10`, Compose `>= 2.1`). If you've got Nix, you
get a dev shell with the right Python and Poetry versions simply by
running

```console
$ nix shell github:c0c0n3/kitt4sme.fipy?dir=nix
```

Otherwise, install the usual way you do on your platform. Then clone
this repo, `cd` into its root dir and install the Python dependencies

```console
$ git clone https://github.com/c0c0n3/kitt4sme.fipy.git
$ cd kitt4sme.fipy
$ poetry install
```

Finally drop into a virtual env shell to hack away

```bash
$ poetry shell
$ charm .
# ^ Pycharm or whatever floats your boat
```

Run all the test suites:

```console
$ pytest tests
```

or just the unit tests

```console
$ pytest tests/unit
```

Measure global test coverage and generate an HTML report

```console
$ coverage run -m pytest -v tests
$ coverage html
```
