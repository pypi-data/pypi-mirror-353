import pytest
from datasets import DatasetDict # type: ignore
from pathlib import Path

from artifex import Artifex
from artifex.exceptions import ValidationError


@pytest.mark.unit
@pytest.mark.parametrize(
    "synthetic_dataset_path",
    [ (1,) ] # wrong type, should be a string
)
def test_synthetic_to_training_dataset_validation_failure(
    artifex: Artifex, synthetic_dataset_path: str
):
    """
    Test that the `_synthetic_to_training_dataset` method of the `Guardrail` class raises a ValidationError when 
    provided with invalid arguments.
    Args:
        artifex (Artifex): The Artifex instance under test.
        mock_generate_synthetic_data (MockerFixture): Mock for the `generate_data` method of the `JobsAPI` class.
        synthetic_dataset_path (str): Path to the synthetic dataset file.
    """

    with pytest.raises(ValidationError):
        artifex.guardrail._synthetic_to_training_dataset(synthetic_dataset_path) # type: ignore
    
    
@pytest.mark.unit
def test_synthetic_to_training_dataset_success(
    artifex: Artifex, temp_synthetic_csv_file: Path
):
    """
    Test the successful conversion of a synthetic CSV dataset to a training DatasetDict.
    This test verifies that the `_synthetic_to_training_dataset` method of the `guardrail` component:
    1. Correctly reads a CSV file with 'llm_output' and 'labels' columns.
    2. Returns a `DatasetDict` object with 'train' and 'test' splits.
    3. Splits the data such that 90% of the samples are in the 'train' set and 10% in the 'test' set.
    4. Ensures that the 'labels' field in the resulting dataset is of type `int`.
    Args:
        artifex (Artifex): The Artifex instance under test.
        temp_synthetic_csv_file (Path): Path to a temporary CSV file containing synthetic data.
    """

    # Call the method under test
    result = artifex.guardrail._synthetic_to_training_dataset(str(temp_synthetic_csv_file)) # type: ignore

    # Assert that:
    # 1. the output is a DatasetDict 
    # 2. the train/test split is correct
    # 3. the labels are of type int
    assert isinstance(result, DatasetDict)
    assert result["train"].num_rows == 9  # 90% of 10 samples
    assert result["test"].num_rows == 1
    assert type(result["train"][0]["labels"]) == int # type: ignore