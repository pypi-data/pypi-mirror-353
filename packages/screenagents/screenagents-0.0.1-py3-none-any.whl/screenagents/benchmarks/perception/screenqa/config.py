from enum import Enum
from typing import Literal

from screensuite.benchmarks.hubbasebenchmark import HubBaseBenchmarkConfig
from screensuite.benchmarks.perception.screenqa.prompt import ScreenQaPrompt


class ScreenQaDatasetVersion(str, Enum):
    """Dataset version"""

    SHORT = "short"
    COMPLEX = "complex"


class ScreenQAHFRepo(str, Enum):
    """HF repo name"""

    SHORT = "rootsautomation/RICO-ScreenQA-Short"
    COMPLEX = "rootsautomation/RICO-ScreenQA-Complex"


class ScreenQaConfig(HubBaseBenchmarkConfig):
    dataset_version: str
    """Dataset version"""

    hf_repo: str
    """HF repo name"""

    revision: str = "main"

    split: Literal["test"] = "test"
    """HF split name"""

    system_prompt: ScreenQaPrompt
    """System prompt"""

    max_tokens: int = 1024
    """Maximum number of tokens in the completion."""

    temperature: float = 0.0
    """Sampling temperature."""

    @classmethod
    def short(cls) -> "ScreenQaConfig":
        """Create a config for ScreenSpot v1 training dataset"""
        return cls(
            hf_repo=ScreenQAHFRepo.SHORT,
            dataset_version=ScreenQaDatasetVersion.SHORT,
            system_prompt=ScreenQaPrompt.SHORT_PROMPT,
        )

    @classmethod
    def complex(cls) -> "ScreenQaConfig":
        """Create a config for ScreenSpot v1 training dataset"""
        return cls(
            hf_repo=ScreenQAHFRepo.COMPLEX,
            dataset_version=ScreenQaDatasetVersion.COMPLEX,
            system_prompt=ScreenQaPrompt.SHORT_PROMPT,
        )
