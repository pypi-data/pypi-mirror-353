from pydantic import BaseModel
from typing import Literal, Protocol


GuardrailExamplesModel = list[tuple[str, Literal[0, 1]]]

class HasProgress(Protocol):
    progress: float
    
class TextClassificationResponse(BaseModel):
    label: str
    score: float