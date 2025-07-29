import pytest
import random

from artifex import Artifex


class Status:
    """
    Represents the status of a process with a progress indicator.
    Attributes:
        progress (float): The current progress of the process as a value between 0.0 and 1.0.
    """
    
    def __init__(self, progress: float):
        self.progress = progress
        
def job_status_func_success() -> Status:
    """
    Simulates a job status function that returns a Status object with either full (1.0) or half (0.5) progress.
    Returns:
        Status: An instance of Status with the progress attribute set to 1.0 or 0.5, chosen randomly.
    """
    
    return Status(progress=1.0) if random.random() < 0.5 else Status(progress=0.5)

def job_status_func_timeout() -> Status:
    """
    Simulates a job status function that returns a Status object with progress set to 0.5.
    Returns:
        Status: An instance of Status with progress initialized to 0.5.
    """
    
    return Status(progress=0.5)


@pytest.mark.unit
def test_await_data_generation_success(
    artifex: Artifex
):
    """
    Test that the `_await_data_generation` method successfully waits for data generation to complete.
    Args:
        artifex (Artifex): An instance of the Artifex class.
    """
    
    result = artifex.guardrail._await_data_generation( # type: ignore
        get_status_fn=job_status_func_success,
        check_interval=1.0,
        timeout=10.0
    )
    
    assert result.progress == 1.0
    
    
@pytest.mark.unit
def test_await_data_generation_timeout_failure(
    artifex: Artifex
):
    """
    Test that the _await_data_generation method raises a TimeoutError when the data generation process does not 
    complete within the specified timeout.
    Args:
        artifex (Artifex): An instance of the Artifex class.
    """
    
    with pytest.raises(TimeoutError):
        artifex.guardrail._await_data_generation( # type: ignore
            get_status_fn=job_status_func_timeout,
            check_interval=1.0,
            timeout=3.0
        )