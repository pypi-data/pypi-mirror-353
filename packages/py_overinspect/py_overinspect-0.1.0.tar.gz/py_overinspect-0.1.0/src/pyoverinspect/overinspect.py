import inspect
from typing import Callable, Final, List, Union

FULL_QUAL:                 Final[bool] = True
NOT_FULL_QUAL:             Final[bool] = False

DEFAULT_PATH_AND_NAME_SEP: Final[str] = '.'

UNKNOWN_FUNCTION: Final[str] = 'unknown'
BUILTIN_FUNCTION: Final[str] = 'built-in'

__INSPECT_FCT_FIELNAME_INDEX: Final[int] = 1
__INSPECT_FCT_LINE_INDEX:     Final[int] = 2
__INSPECT_FCT_NAME_INDEX:     Final[int] = 3


def get_fct_name(fct: Callable, full_qual: bool = NOT_FULL_QUAL) -> str:
    if full_qual:
        return fct.__qualname__
    else:
        return fct.__name__


def get_fct_filename(fct: Callable) -> str:
    try:
        src_filename: Union[str, None] = inspect.getsourcefile(fct)
        if src_filename is None:
            return UNKNOWN_FUNCTION
        return src_filename
    except TypeError:
        return BUILTIN_FUNCTION


def get_full_fct_path_and_name(fct: Callable, full_qual: bool = NOT_FULL_QUAL, sep=DEFAULT_PATH_AND_NAME_SEP) -> str:
    return '%s%s%s' % (get_fct_filename(fct), sep, get_fct_name(fct, full_qual))


def get_fct_parameter_names(fct: Callable) -> List[str]:
    """
    Returns the list of parameter names from the given function.

    Args:
        fct (Callable): The function to extract parameters from.

    Returns:
        List[str]: The list of parameter names.
    """
    return list(inspect.signature(fct).parameters.keys())


def get_current_fct_filename(level: int = 1) -> str:
    """Return the caller function or method filename

    Args:
        level (int, optional): Index of previous caller. Defaults to 1.

    Returns:
        str: Caller function or method filename
    """
    return inspect.stack()[level][__INSPECT_FCT_FIELNAME_INDEX]


def get_current_fct_line(level: int = 1) -> int:
    """Return the caller function or method line

    Args:
        level (int, optional): Index of previous caller. Defaults to 1.

    Returns:
        str: Caller function or method line
    """
    return inspect.stack()[level][__INSPECT_FCT_LINE_INDEX]


def get_current_fct_name(level: int = 1) -> str:
    """Return the caller function or method name

    Args:
        level (int, optional): Index of previous caller. Defaults to 1.

    Returns:
        str: Caller function or method name
    """
    return inspect.stack()[level][__INSPECT_FCT_NAME_INDEX]
