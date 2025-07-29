#!/usr/bin/env python
"""
Example script demonstrating how to use the benchmark registry.
"""

from screensuite import registry
from screensuite.basebenchmark import InferenceConfig
from smolagents import Model


def main():
    # Get all registered benchmarks
    all_benchmarks = registry.list_all()
    print(f"Found {len(all_benchmarks)} benchmarks:")
    for benchmark in all_benchmarks:
        print(f"- {benchmark.name}")

    # Get benchmarks by tags
    tags = ["demo"]
    demo_benchmarks = registry.get_by_tags(tags)
    print(f"\nFound {len(demo_benchmarks)} benchmarks with tag {tags}:")
    for benchmark in demo_benchmarks:
        print(f"- {benchmark.name}")

    # Get a specific benchmark by name
    example_benchmark = registry.get("example")
    if example_benchmark:
        print(f"\nRunning example benchmark: {example_benchmark.name}")

        # Create a model (this is just a placeholder)
        # In a real scenario, you would use a proper model
        class DummyModel(Model):
            model_id = "qwen_futuristic"

            def __call__(self, messages: list[dict[str, str]]) -> str:
                if "2+2" in messages:
                    return "4"
                elif "capital of France" in messages:
                    return "Paris"
                return "I don't know"

        model = DummyModel()

        # Run the benchmark
        results = example_benchmark.evaluate(model, InferenceConfig())
        print(f"Results: {results}")


if __name__ == "__main__":
    main()
