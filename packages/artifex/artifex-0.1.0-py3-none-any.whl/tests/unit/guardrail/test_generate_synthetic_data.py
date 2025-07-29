import pytest
from pytest_mock import MockerFixture

from artifex import Artifex
from artifex.guardrail.models import GuardrailExamplesModel
from artifex.exceptions import ValidationError


@pytest.mark.unit
@pytest.mark.parametrize(
    "requirements, examples, output_path",
    [
        ([1, 2, 3], [("some text", 1)], "results/output/"), # wrong requirements, not a list of strings
        (["requirement1", "requirement2"], ("some text", 1), ""), # wrong examples, not a list of tuples
        (["requirement1", "requirement2"], [("some text", "1")], "results/output.json"), # wrong examples, label is not an integer
        (["requirement1", "requirement2"], [("some text", 1)], 1), # wrong output_path, not a string
    ]
)
def test_generate_synthetic_data_argument_validation_failure(
    mock_generate_synthetic_data: MockerFixture, 
    artifex: Artifex, 
    requirements: list[str], 
    examples: GuardrailExamplesModel, 
    output_path: str
):
    """
    Test that the `_generate_synthetic_data` method raises a `ValidationError` when provided with invalid arguments.
    Args:
        mock_generate_synthetic_data (MockerFixture): Mocked version of the generate_synthetic_data function.
        artifex (Artifex): Instance of the Artifex class under test.
        requirements (list[str]): List of requirement strings to be validated.
        examples (GuardrailExamplesModel): Example data for guardrail validation.
        output_path (str): Path where the synthetic data should be output.
    """
    
    with pytest.raises(ValidationError):
        artifex.guardrail._generate_synthetic_data( # type: ignore
            requirements=requirements,
            examples=examples,
            output_path=output_path
        )