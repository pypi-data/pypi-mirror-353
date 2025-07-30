# make-slice

Creates slice objects with clean syntax.

## Install

```bash
pip install make-slice
```

## Usage

```python
from make_slice import make_slice
# Create a slice object
s = make_slice[1:10:2]  # Equivalent to slice(1, 10, 2)
# Use the slice object
my_list = list(range(20))
print(my_list[s])  # Output: [1, 3, 5, 7, 9]
```


## License

MIT License - See [LICENSE](LICENSE) for details.
