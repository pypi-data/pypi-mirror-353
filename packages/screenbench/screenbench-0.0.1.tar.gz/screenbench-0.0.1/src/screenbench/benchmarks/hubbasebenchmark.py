import os
from typing import Any, Generic, Sequence, TypeVar

from datasets import (
    Dataset,
    DatasetDict,
    IterableDataset,
    IterableDatasetDict,
    load_dataset,
)
from huggingface_hub import login
from pydantic import BaseModel

from screensuite.basebenchmark import BaseBenchmark, BaseBenchmarkEnvironmentConfigType
from screensuite.benchmarks.multistep.config import AgentRunResult
from screensuite.response_generation import AnnotatedOutput


class HubBaseBenchmarkConfig(BaseModel):
    hf_repo: str
    """HF repo name"""

    split: str | list[str]
    """HF split name"""

    revision: str = "main"
    """HF branch repo name"""

    data_dir: str | list[str] | None = None
    """HF data directory"""


T_HubBaseBenchmarkConfig = TypeVar("T_HubBaseBenchmarkConfig", bound=HubBaseBenchmarkConfig)


class HubBaseBenchmark(
    Generic[T_HubBaseBenchmarkConfig, BaseBenchmarkEnvironmentConfigType],
    BaseBenchmark[T_HubBaseBenchmarkConfig, BaseBenchmarkEnvironmentConfigType],
):
    def __init__(self, name: str, config: T_HubBaseBenchmarkConfig, tags: list[str]):
        """
        Initialize the HubBaseBenchmark

        Args:
            name: Name of the benchmark.
            config: Configuration for the benchmark.
            tags: Tags for the benchmark.
        """

        super().__init__(
            name=name,
            config=config,
            tags=tags,
        )
        self.dataset: Dataset | None = None
        self.datasets: dict[str, DatasetDict | Dataset | IterableDatasetDict | IterableDataset] = {}

    def _calculate_proportion_missing(self, responses: Sequence[AnnotatedOutput[Any] | None | AgentRunResult]) -> float:
        """
        Calculate the proportion of missing (None) responses in the evaluation results.

        Args:
            responses: A list of responses

        Returns:
            The proportion of missing responses (between 0 and 1)
        """

        missing = sum(
            1
            for r in responses
            if r is None
            or (hasattr(r, "output") and getattr(r, "output") is None)
            or (hasattr(r, "answer") and getattr(r, "answer") is None)
        )
        return missing / len(responses) if responses else 0.0

    def load(self, streaming: bool = False) -> None:
        """
        Load the dataset from the Hugging Face Hub
        """
        if self.dataset is None and not self.datasets:
            hf_token = os.environ.get("HF_TOKEN")
            if hf_token:
                login(token=hf_token)
            else:
                print(
                    "Warning: HF_TOKEN environment variable not set. Attempting to load dataset without authentication."
                )

            # Normalize data_dir and split to lists for consistent handling
            data_dirs = [self.config.data_dir] if not isinstance(self.config.data_dir, list) else self.config.data_dir
            splits = [self.config.split] if not isinstance(self.config.split, list) else self.config.split

            # Handle the case where we have a single data_dir and single split
            if len(data_dirs) == 1 and len(splits) == 1:
                self.dataset = load_dataset(
                    self.config.hf_repo,
                    split=splits[0],
                    revision=self.config.revision,
                    data_dir=data_dirs[0],
                    streaming=streaming,
                )  # type: ignore
            else:
                # Handle multiple data_dirs and/or splits
                for data_dir in data_dirs:
                    for split in splits:
                        if len(splits) == 1:
                            key = data_dir
                        elif len(data_dirs) == 1:
                            key = split
                        else:
                            key = f"{split}_{data_dir}"

                        assert key is not None

                        self.datasets[key] = load_dataset(
                            self.config.hf_repo,
                            split=split,
                            revision=self.config.revision,
                            data_dir=data_dir,
                        )
