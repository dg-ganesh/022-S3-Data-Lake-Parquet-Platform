"""
Project : S3 Data Lake + Parquet Platform
Project ID : 022

Slice 2 - Curated Pipeline Runner Test
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from src.core.curated_pipeline_runner import (
    CuratedPipelineRunner,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_DIRECTORY = PROJECT_ROOT / "data" / "input"

EXPECTED_ROW_COUNTS = {
    "customers": 5,
    "transactions": 5,
}


class StubCuratedPipeline:
    """Provide deterministic outcomes for runner orchestration."""

    def process_dataset(
        self,
        source_file: Path,
        dataset_name: str,
    ) -> dict[str, object]:
        if dataset_name not in EXPECTED_ROW_COUNTS:
            raise ValueError(
                f"Unknown dataset: {dataset_name}"
            )

        return {
            "dataset_name": dataset_name,
            "row_count": EXPECTED_ROW_COUNTS[dataset_name],
            "schema_validated": True,
        }


def main() -> int:
    """Verify successful and failed runner outcomes."""
    runner = CuratedPipelineRunner(
        config=SimpleNamespace(
            input_directory=INPUT_DIRECTORY,
        ),
        pipeline=StubCuratedPipeline(),
    )

    success_summary = runner.run(
        ["customers", "transactions"]
    )

    assert success_summary["successful"]
    assert success_summary["successful_count"] == 2
    assert success_summary["failed_count"] == 0
    assert (
        success_summary["results"]["customers"]["row_count"]
        == 5
    )
    assert (
        success_summary["results"]["transactions"]["row_count"]
        == 5
    )

    failure_summary = runner.run(
        ["customers", "invalid_dataset"]
    )

    assert not failure_summary["successful"]
    assert failure_summary["successful_count"] == 1
    assert failure_summary["failed_count"] == 1
    assert "invalid_dataset" in failure_summary["failures"]
    assert "Unknown dataset" in (
        failure_summary["failures"]["invalid_dataset"]
    )

    print("CuratedPipelineRunner: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
