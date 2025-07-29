import pytest
from pytest_mock import MockerFixture
from pathlib import Path
from transformers.models.bert.modeling_bert import BertForSequenceClassification
from transformers.trainer_utils import TrainOutput

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
def test_train_argument_validation_failure(
    mock_generate_synthetic_data: MockerFixture,
    artifex: Artifex,
    requirements: list[str],
    examples: GuardrailExamplesModel,
    output_path: str
):
    """
    Test that the `train` method of the guardrail raises a ValidationError when provided with invalid arguments.
    Args:
        mock_generate_synthetic_data (MockerFixture): Mock for the `generate_data` method of the JobsAPI.
        artifex (Artifex): The Artifex instance under test.
        requirements (list[str]): List of requirements to be validated.
        examples (GuardrailExamplesModel): Example data for training.
        output_path (str): Path where output should be saved.
    """

    with pytest.raises(ValidationError):
        artifex.guardrail.train(
            requirements=requirements,
            examples=examples,
            output_path=output_path
        )


@pytest.mark.unit
def test_train_success(
    mock_generate_synthetic_data: MockerFixture,
    mock_await_data_generation: MockerFixture,
    temp_synthetic_csv_file: Path,
    artifex: Artifex
):
    """
    Test the successful execution of the `train` method of the guardrail:
    1. Prior to calling the `train` method, the class should contain a `_model` 
        attribute of type `BertForSequenceClassification`.
    2. The `train` method should return a TrainOutput object with the expected attributes.
    Args:
        mock_generate_synthetic_data (MockerFixture): Mock for the `generate_data` method of the JobsAPI.
        mock_await_data_generation (MockerFixture): Mock for the `_await_data_generation` method of the Guardrail class.
        temp_synthetic_csv_file (Path): Temporary file path for the mocked synthetic training data.
        artifex (Artifex): The Artifex instance under test.
    """
    
    output_path = str(temp_synthetic_csv_file.parent)
    
    guardrail = artifex.guardrail
    untrained_model = guardrail._model # type: ignore
    assert isinstance(untrained_model, BertForSequenceClassification) # type: ignore
    
    out = guardrail.train(
        requirements=["requirement1", "requirement2"],
        examples=[("test", 0)],
        output_path=output_path,
        num_epochs=1
    )
    assert isinstance(out, TrainOutput)
    assert out.metrics["train_runtime"] > 0.5 # Ensure the training took some time