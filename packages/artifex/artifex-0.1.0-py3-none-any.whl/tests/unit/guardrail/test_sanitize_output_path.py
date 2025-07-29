import pytest
from pytest_mock import MockerFixture

from artifex.config import config
from artifex.guardrail import Guardrail


@pytest.mark.unit
@pytest.mark.parametrize(
    "output_path, expected_path",
    [
        ("results/output", "results/output/"),
        ("results/output.json", "results/"),
        ("results/output/", "results/output/"),
        ("   results/output", "results/output/"),
        ("   results/output   ", "results/output/"),
        ("", config.DEFAULT_OUTPUT_PATH),
    ]
)
def test_sanitize_output_path_success(
    mocker: MockerFixture,
    output_path: str,
    expected_path: str
):
    """
    Test the `_sanitize_output_path` method of the `Guardrail` class.
    This test verifies that the `_sanitize_output_path` method correctly processes
    the given output path, returning the expected sanitized path.
    Args:
        output_path (str): The output path to be sanitized.
        expected_path (str): The expected sanitized output path.
    """
    
    mocker.patch("os.getcwd", return_value="")
    sanitized = Guardrail._sanitize_output_path(output_path) # type: ignore
    assert sanitized == expected_path