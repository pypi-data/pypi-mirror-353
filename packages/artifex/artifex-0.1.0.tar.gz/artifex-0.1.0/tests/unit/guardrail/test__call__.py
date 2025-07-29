import pytest

from artifex import Artifex
from artifex.exceptions import ValidationError
from artifex.guardrail.models import TextClassificationResponse


@pytest.mark.unit
def test__call__validation_failure(artifex: Artifex):
    """
    Test that calling the `__call__` method of the `Guardrail` class with an invalid input raises a ValidationError.
    Args:
        artifex (Artifex): An instance of the Artifex class.
    """
    
    with pytest.raises(ValidationError):
        artifex.guardrail(True) # type: ignore


@pytest.mark.unit
def test__call__success(artifex: Artifex):
    """
    Test that calling the `__call__` method of the `Guardrail` class returns a list[TextClassificationResponse].
    Args:
        artifex (Artifex): An instance of the Artifex class.
    """
    
    out = artifex.guardrail("A sample sentence")
    assert isinstance(out[0], TextClassificationResponse)