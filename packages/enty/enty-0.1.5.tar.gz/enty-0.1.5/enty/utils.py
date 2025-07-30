import re
from typing import Union
from collections.abc import Iterable


def is_scalar_type(value, allow_tuple=True):
    # allow all scalar types -- this includes all non-Iterables as well as str and byte objects
    if not isinstance(value, (Iterable,)) or isinstance(value, (str, bytes)):
        return True
    # also allow tuple objects as long as they are composed of scalar objects
    # note: in the recursion step, set allow_tuple=False so that we don't allow nested tuples.
    if allow_tuple and isinstance(value, (tuple,)):
        return all(is_scalar_type(entry, allow_tuple=False) for entry in value)
    return False


def camel_to_snake(camel: Union[str, None]) -> str:
    """
    Converts a CamelCase or PascalCase string to snake_case, handling acronyms properly.
    
    Specifically, it ensures a single underscore is added between the last letter of an
    acronym and the next word (e.g., 'LBMScan' -> 'lbm_scan').
    
    Args:
        camel (str | None): The CamelCase or PascalCase string to convert.
        
    Returns:
        str: The converted snake_case string.
        
    Example:
        >>> camel_to_snake("CamelCaseExample")
        'camel_case_example'
        >>> camel_to_snake("LBMScan")
        'lbm_scan'
        >>> camel_to_snake("HTTPResponseCode")
        'http_response_code'
    """
    if camel is None:
        return ""
    
    # Step 1: Handle transitions from acronyms to regular words (e.g., LBMScan -> lbm_scan)
    snake = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', camel)

    # Step 2: Handle remaining transitions from lowercase to uppercase
    snake = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', snake)

    # Step 3: Convert to lowercase
    return snake.lower()