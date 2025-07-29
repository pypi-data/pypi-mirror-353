from synthex import Synthex
from synthex.models import JobOutputSchemaDefinition
from typing import Optional, cast, Sequence, TypeVar, Callable
import os
import time
from datasets import Dataset, DatasetDict, ClassLabel # type: ignore
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments, BatchEncoding # type: ignore
from transformers.models.bert.modeling_bert import BertForSequenceClassification
from transformers.trainer_utils import TrainOutput
from tqdm import tqdm

from artifex.config import config
from artifex.decorators import auto_validate_methods

from .models import GuardrailExamplesModel, HasProgress, TextClassificationResponse


T = TypeVar("T", bound=HasProgress)


@auto_validate_methods
class Guardrail:
    """
    A class to represent a Guardrail Model for LLMs.
    """

    def __init__(self, synthex: Synthex):
        """
        Initializes the Guardrail class with a Synthex instance.
        Args:
            synthex (Synthex): An instance of the Synthex class to generate the synthetic data used to train the model.
        """
        
        self._synthex: Synthex = synthex
        self._synthetic_data_schema: JobOutputSchemaDefinition = {
            "llm_output": {"type": "string"},
            "labels": {"type": "integer"},
        }
        self._model: BertForSequenceClassification = AutoModelForSequenceClassification.from_pretrained( # type: ignore
            config.DEFAULT_HUGGINGFACE_BASE_MODEL, num_labels=2
        )
        self._tokenizer = AutoTokenizer.from_pretrained(config.DEFAULT_HUGGINGFACE_BASE_MODEL) # type: ignore


    @staticmethod
    def _sanitize_output_path(output_path: str) -> str:
        """
        Ensure that the output path is valid; if it is not, sanitize it.
        Args:
            output_path (str): The output path to sanitize.
        Returns:
            str: The sanitized output path.
        """
                
        # If output_path is not an empty string, use a default directory
        directory = config.DEFAULT_OUTPUT_PATH
        
        if output_path != "":
            output_path = output_path.strip()
            # Extract the directory and file name from the output path, use only the directory
            directory, filename = os.path.split(output_path)
            # If the filename does not have an extension, use it as a directory
            if "." not in filename:
                directory = os.path.join(directory, filename).rstrip("/")
            # Strip whitespaces
            directory += "/"
        
        return directory
    
    
    def _generate_synthetic_data(
        self, requirements: list[str], examples: GuardrailExamplesModel, output_path: str
    ) -> None:
        """
        Use Synthex to generate synthetic data based on the provided requirements and examples.
        
        Args:
            requirements (list[str]): A list of requirements for the synthetic data generation.
            examples (GuardrailExamplesModel): A model containing examples to be used for generating synthetic data.
            output_path (str): The path where the generated synthetic data will be saved.
        """
        
        # Turn examples into a format that Synthex can use.
        formatted_examples: list[dict[str, int | str]] = [
            {"llm_output": example[0], "labels": example[1]} for example in examples
        ]
        
        # Trigger the data generation job in Synthex.
        self._synthex.jobs.generate_data(
            schema_definition=self._synthetic_data_schema,
            examples=formatted_examples,
            requirements=requirements,
            output_path=output_path,
            number_of_samples=config.DEFAULT_SYNTHEX_DATAPOINT_NUM,
            output_type="csv"
        )


    def _await_data_generation(
        self,
        get_status_fn: Callable[[], T],
        check_interval: float = 5.0,
        timeout: float = 300.0
    ) -> T:
        """
        Polls the synthetic data generation job status until progress reaches 1.0, or a timeout is reached.
        Use a progress bar to visualize the progress of the data generation.
        Args:
            get_status_fn (Callable[[], T]): A function that returns a job status object with a `progress` attribute.
            check_interval (float): Time to wait between checks (in seconds).
            timeout (float): Maximum time to wait for completion (in seconds).
        Returns:
            T: The final job status object with progress >= 1.0.
        """
        
        start_time = time.time()
        
        # Initialize a progress bar using tqdm to visualize the progress of the data generation.
        with tqdm(
            total=100, desc="Generating synthetic data", 
            bar_format="{l_bar}{bar} | ETA: {remaining}"
        ) as pbar:
            
            status = get_status_fn()

            while status.progress < 1:
                if time.time() - start_time > timeout:
                    raise TimeoutError("Job did not complete within the timeout period.")
                time.sleep(check_interval)
                new_status = get_status_fn()

                # Update the progress bar if the new status has a higher progress value.
                if new_status.progress > status.progress:
                    pbar.update(new_status.progress - status.progress)

                status = new_status

        return status
        
    
    def _synthetic_to_training_dataset(self, synthetic_dataset_path: str) -> DatasetDict:
        """
        Load the generated synthetic dataset from the specified path into a `datasets.Dataset` and prepare it for training.
        Args:
            synthetic_dataset_path (str): The path to the synthetic dataset file.
        Returns:
            Dataset: A `datasets.DatasetDict` object containing the synthetic data, split into training and validation sets.
        """
        
        # Load the generated data into a datasets.Dataset
        dataset = cast(Dataset, Dataset.from_csv(synthetic_dataset_path)) # type: ignore
        # Ensure labels are int64
        dataset = dataset.cast_column("labels", ClassLabel(num_classes=2)) # type: ignore
        # Automatically split into train/validation (90%/10%)
        dataset = dataset.train_test_split(test_size=0.1)
        
        return dataset
    
    
    def _tokenize_dataset(self, dataset: DatasetDict) -> DatasetDict:
        """
        Tokenize the dataset using a pre-trained tokenizer.
        Args:
            dataset (DatasetDict): The dataset to be tokenized.
        Returns:
            DatasetDict: The tokenized dataset.
        """

        def tokenize(example: dict[str, Sequence[str]]) -> BatchEncoding:
            return self._tokenizer(example["llm_output"], truncation=True, padding="max_length", max_length=128) # type: ignore

        return dataset.map(tokenize, batched=True) # type: ignore
    

    def train(
        self, requirements: list[str], examples: GuardrailExamplesModel, output_path: Optional[str] = None, num_epochs: int = 3
    ) -> TrainOutput:
        """
        Train the Guardrail model using synthetic data generated by Synthex.
        Args:
            requirements (list[str]): A list of requirements for the synthetic data generation.
            examples (GuardrailExamplesModel): A model containing examples to be used for generating synthetic data.
            output_path (Optional[str]): The path where the generated synthetic data will be saved.
            num_epochs (int): The number of epochs for training the model. Default is 3.
        """

        output_path = output_path or config.DEFAULT_OUTPUT_PATH
        # Sanitize the output path and append the filename.
        output_path = self._sanitize_output_path(output_path)
        output_dataset_path = os.path.join(output_path, config.DEFAULT_SYNTHEX_DATASET_NAME)
        
        # Generate synthetic data.
        self._generate_synthetic_data(
            requirements=requirements,
            examples=examples,
            output_path=output_dataset_path
        )
        
        # Await the completion of the synthetic data generation job.
        self._await_data_generation(self._synthex.jobs.status)
        
        # Turn synthetic data into a training dataset with train/test split.
        dataset = self._synthetic_to_training_dataset(output_dataset_path)
        
        # Tokenize the dataset.
        tokenized_dataset = self._tokenize_dataset(dataset)

        training_args = TrainingArguments(
            output_dir=output_path,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=16,
            per_device_eval_batch_size=16,
            save_strategy="epoch",
            logging_strategy="epoch",
            report_to=[]
        )

        trainer = Trainer(
            model=self._model,
            args=training_args,
            train_dataset=tokenized_dataset["train"],
            eval_dataset=tokenized_dataset["test"],
        )

        train_output: TrainOutput = trainer.train() # type: ignore
        
        return train_output # type: ignore
        
        
    def __call__(self, text: str | list[str]) -> list[TextClassificationResponse]:
        """
        Classifies the input text using a pre-defined text classification pipeline.
        Args:
            text (str): The input text to be classified.
        Returns:
            Any: The classification result produced by the pipeline.
        """
        
        classifier = pipeline("text-classification", model=self._model, tokenizer=self._tokenizer) # type: ignore
        classifications = classifier(text) # type: ignore
        
        if not classifications:
            return []
        
        return [ TextClassificationResponse(
            label=classification["label"], # type: ignore
            score=classification["score"] # type: ignore
        ) for classification in classifications ] # type: ignore