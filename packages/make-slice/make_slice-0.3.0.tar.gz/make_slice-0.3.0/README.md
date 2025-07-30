# make-slice

Creates slice objects with clean syntax.

![](https://img.shields.io/github/license/0x00-pl/make_slice.svg)
[![PyPI](https://img.shields.io/pypi/v/make-slice?logo=pypi&label=PyPI%20package)](https://pypi.org/project/make-slice/)
![](https://img.shields.io/github/release/0x00-pl/make_slice)
![cov](https://0x00-pl.github.io/make_slice/badges/coverage.svg)
![](https://img.shields.io/github/issues/0x00-pl/make_slice)
![](https://img.shields.io/github/stars/0x00-pl/make_slice)

## Install

```bash
pip install make-slice
```

## Usage

```python
from make_slice import make_slice

my_list = list(range(5))  # list: [0, 1, 2, 3, 4]
# Create a slice object
rev_slice = make_slice[::-1]  # Equivalent to slice(None, None, -1)
# Use the slice object
print(my_list[rev_slice])  # Output: [4, 3, 2, 1, 0]
```

## Development

use `poetry` to manage dependencies and virtual environments:

```bash
pip install poetry
poetry install
```

use `pre-commit` to run reformatting and linting:

```bash
pre-commit install
pre-commit autoupdate
pre-commit run --all-files
```

## License

MIT License - See [LICENSE](LICENSE) for details.
