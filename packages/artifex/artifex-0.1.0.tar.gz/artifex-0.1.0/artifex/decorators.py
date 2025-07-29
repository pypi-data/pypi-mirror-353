from pydantic import validate_call, ValidationError
from typing import Any, Callable, TypeVar
from functools import wraps
import inspect

from artifex.exceptions import ValidationError as ArtifexValidationError


T = TypeVar("T", bound=type)


def auto_validate_methods(cls: T) -> T:
    """
    A class decorator that combines Pydantic's `validate_call` for input validation
    and automatic handling of validation errors, raising a custom `ArtifexValidationError`.
    This decorator applies to methods that have parameters beyond 'self'.
    """
    
    for attr_name in dir(cls):
        # Skip dunder methods, except the __call__ method
        if attr_name.startswith("__") and attr_name != "__call__":
            continue

        attr = getattr(cls, attr_name)
        if not callable(attr):
            continue

        # Get method signature and skip methods that only have 'self' as parameter
        sig = inspect.signature(attr)
        params = list(sig.parameters.values())
        if len(params) <= 1:
            continue

        # Apply validate_call to the method
        validated = validate_call(attr, config={"arbitrary_types_allowed": True}) # type: ignore

        # Wrap the method with both validation and error handling
        @wraps(attr)
        def wrapper(*args: Any, __f: Callable[..., Any] = validated, **kwargs: Any) -> Any:
            try:
                return __f(*args, **kwargs)
            except ValidationError as e:
                raise ArtifexValidationError(f"Invalid input: {e}")

        setattr(cls, attr_name, wrapper)

    return cls
