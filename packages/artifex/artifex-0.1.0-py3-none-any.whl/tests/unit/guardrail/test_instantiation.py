import pytest
from transformers.models.bert.modeling_bert import BertForSequenceClassification

from artifex import Artifex


@pytest.mark.unit
def test_instantiation_success(artifex: Artifex):
    """
    Test the successful instantiation of the Guardrail class: it should contain a `_model` attribute of 
    type BertForSequenceClassification.
    Args:
        artifex (Artifex): An instance of the Artifex class.
    """
    
    guardrail = artifex.guardrail 
    assert isinstance(guardrail._model, BertForSequenceClassification) # type: ignore