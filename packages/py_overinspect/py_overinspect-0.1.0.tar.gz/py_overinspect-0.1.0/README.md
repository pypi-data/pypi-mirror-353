# py_overinspect

A Python library to provide some functions over standard "`inspect`" module

## Installation

```bash
poetry add py_overinspect
# or
pip install py_overinspect
# or
pipenv install py_overinspect
```

## Functions

```python
def get_fct_name(fct: Callable, full_qual: bool = NOT_FULL_QUAL) -> str
def get_fct_filename(fct: Callable) -> str
def get_full_fct_path_and_name(fct: Callable, full_qual: bool = NOT_FULL_QUAL, sep=DEFAULT_PATH_AND_NAME_SEP) -> str
def get_fct_parameter_names(fct: Callable) -> List[str]
def get_current_fct_filename(level: int = 1) -> str
def get_current_fct_line(level: int = 1) -> int
def get_current_fct_name(level: int = 1) -> str
```
