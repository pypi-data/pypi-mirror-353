import pytest
from pytest import MonkeyPatch
import os
import shutil
from pathlib import Path
from typing import Generator, Literal
from pytest_mock import MockerFixture
from datasets import Dataset, DatasetDict  # type: ignore
import csv

from artifex import Artifex
from artifex.config import config


@pytest.fixture(autouse=True)
def isolate_env(tmp_path: Path = Path(".pytest_env_backup")) -> Generator[None, None, None]:
    """
    A pytest fixture that backs up the .env file before each test and restores it afterward.
    It uses a local temporary path to store the backup and ensures the directory is cleaned up after the test.
    Args:
        tmp_path (Path): Path used to temporarily store the .env backup.
    Yields:
        None
    """
    
    backup_file = tmp_path / ".env.bak"
    tmp_path.mkdir(parents=True, exist_ok=True)

    if os.path.exists(".env"):
        shutil.copy(".env", backup_file)

    yield  # Run the test

    if backup_file.exists():
        shutil.copy(backup_file, ".env")

    # Clean up backup directory
    shutil.rmtree(tmp_path, ignore_errors=True)
    
    
@pytest.fixture(scope="function")
def artifex() -> Artifex:
    """
    Creates and returns an instance of the Artifex class using the API key 
    from the environment variables.
    Returns:
        Artifex: An instance of the Artifex class initialized with the API key.
    """
    
    api_key = config.API_KEY
    if not api_key:
        pytest.fail("API_KEY not found in environment variables")
    return Artifex(api_key)


@pytest.fixture
def mock_generate_synthetic_data(mocker: MockerFixture) -> MockerFixture:
    """
    Mocks the `generate_data` method of the `JobsAPI` class in the `synthex.jobs_api` module.
    Args:
        mocker (MockerFixture): The pytest-mock fixture used to patch objects.
    Returns:
        MockerFixture: The mock object for the 'generate_data' method.
    """
    
    return mocker.patch("synthex.jobs_api.JobsAPI.generate_data")


@pytest.fixture
def temp_synthetic_csv_file(tmp_path: Path) -> Path:
    """
    Creates a temporary CSV file with mock data for testing purposes.
    Args:
        tmp_path (Path): A temporary directory path provided by pytest's tmp_path fixture.
    Returns:
        Path: The path to the created mock CSV file containing sample data.
    """
    
    # Define some mock CSV data
    data: list[dict[str, str | Literal[0, 1]]] = [
        {"llm_output": "The sky is blue.", "labels": 1} for _ in range(10)
    ]

    # Create the CSV file in the temporary directory
    csv_path = tmp_path / config.DEFAULT_SYNTHEX_DATASET_NAME
    with open(csv_path, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["llm_output", "labels"])
        writer.writeheader()
        writer.writerows(data)

    return csv_path


@pytest.fixture
def temp_env_file(tmp_path: Path, monkeypatch: MonkeyPatch) -> Path:
    env_path = tmp_path / ".env"
    env_path.write_text("API_KEY=patched_key\nFAKE_ENV=123\n")

    # Temporarily patch the env_file path
    monkeypatch.setenv("PYDANTIC_SETTINGS_PATH", str(env_path))
    monkeypatch.chdir(tmp_path)  # make it the current dir

    return env_path


@pytest.fixture
def mock_datasetdict() -> DatasetDict:
    """
    Creates a mock `datasets.DatasetDict object` for testing purposes.
    Returns:
        DatasetDict: A dictionary-like object containing two splits:
            - "train": A Dataset with two examples, each having an "llm_output" (str) and a "labels" (int, 0 or 1).
            - "test": A Dataset with two examples, each having an "llm_output" (str) and a "labels" (int, 0 or 1).
    """
    
    train_data: dict[str, list[str] | list[Literal[0, 1]]] = {
        "llm_output": [
            "The capital of France is Paris.",
            "Water boils at 100 degrees Celsius.",
        ],
        "labels": [1, 0],
    }

    test_data: dict[str, list[str] | list[Literal[0, 1]]] = {
        "llm_output": [
            "Cats are animals.",
            "The Moon orbits the Earth.",
        ],
        "labels": [0, 1],
    }

    # Create DatasetDict
    return DatasetDict({
        "train": Dataset.from_dict(train_data), # type: ignore
        "test": Dataset.from_dict(test_data), # type: ignore
    })


@pytest.fixture
def mock_await_data_generation(mocker: MockerFixture) -> MockerFixture:
    """
    Mocks the `_await_data_generation` method of the `Guardrail` class in the `artifex.guardrail` module.
    Args:
        mocker (MockerFixture): The pytest-mock fixture used to patch objects.
    Returns:
        MockerFixture: The mock object for the '_await_data_generation' method.
    """
    
    return mocker.patch("artifex.guardrail.Guardrail._await_data_generation")