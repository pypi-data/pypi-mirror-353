"""Tests for ScreenQA benchmark."""

from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from screensuite.basebenchmark import EvaluationConfig
from screensuite.benchmark_result import BenchmarkResult
from screensuite.benchmarks.perception.screenqa.benchmark import ScreenQABenchmark
from screensuite.benchmarks.perception.screenqa.config import (
    ScreenQaConfig,
    ScreenQaDatasetVersion,
    ScreenQAHFRepo,
)
from screensuite.benchmarks.perception.screenqa.prompt import ScreenQaPrompt


class MockModel:
    def __init__(self, responses):
        self.responses = responses
        self.current_index = 0

    def generate(self, messages, max_tokens, temperature):
        response = MagicMock()
        response.content = self.responses[self.current_index]
        self.current_index += 1
        return response


@pytest.fixture
def mock_dataset():
    return [
        {
            "question": "What is the color of the button?",
            "image": Image.new("RGB", (1, 1), color=(255, 255, 255)),
            "ground_truth": ["blue", "navy"],
        },
        {
            "question": "What is the text on the screen?",
            "image": Image.new("RGB", (1, 1), color=(255, 255, 255)),
            "ground_truth": ["Hello World"],
        },
    ]


@pytest.fixture
def screenqa_benchmark():
    config = ScreenQaConfig(
        hf_repo=ScreenQAHFRepo.SHORT,
        dataset_version=ScreenQaDatasetVersion.SHORT,
        system_prompt=ScreenQaPrompt.SHORT_PROMPT,
        max_tokens=100,
        temperature=0.0,
    )
    return ScreenQABenchmark(name="test_screenqa", config=config, tags=["test"])


def test_screenqa_benchmark_initialization(screenqa_benchmark):
    assert screenqa_benchmark.name == "test_screenqa"
    assert "test" in screenqa_benchmark.tags
    assert screenqa_benchmark.config.max_tokens == 100
    assert screenqa_benchmark.config.temperature == 0.0


@patch("screensuite.benchmarks.perception.screenqa.benchmark.HubBaseBenchmark.load")
def test_screenqa_benchmark_evaluate(mock_load, screenqa_benchmark, mock_dataset):
    # Setup
    screenqa_benchmark.dataset = mock_dataset
    model = MockModel(responses=["blue", "Hello World"])

    # Execute
    results = screenqa_benchmark.evaluate(
        model=model, evaluation_config=EvaluationConfig(timeout=10, parallel_workers=1, run_name=None)
    )

    # Assert
    assert isinstance(results, BenchmarkResult)
    assert "exact_match" in results.get_fields()
    assert "f1" in results.get_fields()
    assert isinstance(results["exact_match"], float)
    assert isinstance(results["f1"], float)
    assert 0 <= results["exact_match"] <= 1
    assert 0 <= results["f1"] <= 1


@patch("screensuite.benchmarks.perception.screenqa.benchmark.HubBaseBenchmark.load")
def test_screenqa_benchmark_evaluate_no_answer(mock_load, screenqa_benchmark, mock_dataset):
    screenqa_benchmark.dataset = mock_dataset
    model = MockModel(responses=["<no answer>", "Hello World"])

    results = screenqa_benchmark.evaluate(
        model=model, evaluation_config=EvaluationConfig(timeout=10, parallel_workers=1, run_name=None)
    )

    # First answer should be marked as incorrect since ground truth doesn't contain NO_ANSWER
    assert results["exact_match"] < 1.0


@patch("screensuite.benchmarks.perception.screenqa.benchmark.HubBaseBenchmark.load")
def test_screenqa_benchmark_evaluate_empty_response(mock_load, screenqa_benchmark, mock_dataset):
    # Setup
    screenqa_benchmark.dataset = mock_dataset
    model = MockModel(responses=["", "Hello World"])

    results = screenqa_benchmark.evaluate(
        model=model, evaluation_config=EvaluationConfig(timeout=10, parallel_workers=1, run_name=None)
    )

    # Empty response should be treated as incorrect
    assert results["exact_match"] < 1.0
