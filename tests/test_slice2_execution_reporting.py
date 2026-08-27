"""
Project : S3 Data Lake + Parquet Platform
Project ID : 022

Slice 2 - Execution Reporting Test
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from src.config import AppConfig
from src.core.curated_pipeline import CuratedPipeline
from src.core.curated_pipeline_runner import (
    CuratedPipelineRunner,
)
from src.services.curated_pipeline_report_service import (
    CuratedPipelineReportService,
)
from src.services.execution_report_service import (
    ExecutionReportService,
)


class StubCuratedDatasetManager:
    """Avoid real S3 while preserving pipeline behavior."""

    def upload_dataset(
        self,
        dataset_directory: Path,
        dataset_name: str,
    ) -> list[str]:
        return [
            f"curated/{dataset_name}/"
            f"{path.relative_to(dataset_directory).as_posix()}"
            for path in dataset_directory.rglob("*.parquet")
        ]

    def verify_dataset(
        self,
        dataset_directory: Path,
        dataset_name: str,
    ) -> dict[str, object]:
        return {
            "verified": True,
            "dataset_name": dataset_name,
        }


def _build_config(
    project_root: Path,
) -> AppConfig:
    """Build isolated configuration for the reporting test."""
    return AppConfig(
        project_name="S3 Data Lake + Parquet Platform",
        project_id="022",
        application_version="test",
        environment="test",
        aws_region="ap-south-1",
        s3_bucket_name="test-bucket",
        s3_raw_prefix="raw/",
        s3_curated_prefix="curated/",
        s3_rejected_prefix="rejected/",
        s3_metadata_prefix="metadata/",
        parquet_compression="snappy",
        supported_source_formats=(".csv",),
        default_partition_columns={"customers": []},
        project_root=project_root,
        input_directory=project_root / "input",
        output_directory=project_root / "output",
        sample_data_directory=project_root / "samples",
        curated_output_directory=project_root / "curated",
        log_directory=project_root / "logs",
    )


def main() -> int:
    """Verify generic, adapter, and pipeline reporting behavior."""
    with TemporaryDirectory() as temporary_directory:
        project_root = Path(temporary_directory)

        _test_execution_report_service(project_root)
        _test_report_adapter(project_root)
        _test_runner_pipeline_reporting(project_root)

    print("Execution reporting: PASS")
    return 0


def _test_execution_report_service(
    project_root: Path,
) -> None:
    """Verify generic report lifecycle and failure reporting."""
    service = ExecutionReportService(
        log_directory=project_root / "generic_logs",
        application_version="test",
    )

    service.start_execution()
    service.record_checkpoint("Generic checkpoint")
    service.record_failure("Generic failure", "Expected error")
    service.complete_execution("FAIL")

    contents = service.get_report_contents()

    assert "PASS | Generic checkpoint" in contents
    assert "FAIL | Generic failure" in contents
    assert "ERROR | Expected error" in contents
    assert "EXECUTION SUMMARY" in contents
    assert "Status              : FAIL" in contents


def _test_report_adapter(
    project_root: Path,
) -> None:
    """Verify the curated adapter delegates pipeline events."""
    execution_service = ExecutionReportService(
        log_directory=project_root / "adapter_logs",
        application_version="test",
    )
    report_service = CuratedPipelineReportService(
        execution_service
    )

    execution_service.start_execution()
    report_service.record_dataset_started("customers")
    report_service.record_source_loaded("customers", 5)
    report_service.record_failure(
        "Curated adapter failure",
        ValueError("Expected adapter error"),
    )
    execution_service.complete_execution("FAIL")

    contents = report_service.get_report_contents()

    assert "Dataset processing started: customers" in contents
    assert "Source dataset loaded: customers (5 rows)" in contents
    assert "FAIL | Curated adapter failure" in contents
    assert "ERROR | Expected adapter error" in contents


def _test_runner_pipeline_reporting(
    project_root: Path,
) -> None:
    """Verify runner lifecycle and pipeline checkpoints."""
    config = _build_config(project_root)
    config.input_directory.mkdir(parents=True)
    (config.input_directory / "customers.csv").write_text(
        "customer_id,name,city,registration_date\n"
        "1001,Alice,Bengaluru,2026-08-20\n",
        encoding="utf-8",
    )

    execution_service = ExecutionReportService(
        log_directory=config.log_directory,
        application_version=config.application_version,
    )
    report_service = CuratedPipelineReportService(
        execution_service
    )

    pipeline = CuratedPipeline(
        config=config,
        s3_service=object(),
        curated_manager=StubCuratedDatasetManager(),
        report_service=report_service,
    )
    runner = CuratedPipelineRunner(
        config=config,
        pipeline=pipeline,
        report_service=report_service,
    )

    summary = runner.run(["customers"])
    contents = execution_service.get_report_contents()

    assert summary["successful"]
    assert summary["successful_count"] == 1
    assert summary["results"]["customers"]["row_count"] == 1
    assert "Dataset processing started: customers" in contents
    assert "Dataset definition loaded: customers" in contents
    assert "Source dataset loaded: customers (1 rows)" in contents
    assert "Schema validated: customers" in contents
    assert "Parquet dataset generated: customers (1 files)" in contents
    assert "Parquet dataset verified: customers" in contents
    assert "Curated dataset uploaded: customers (1 files)" in contents
    assert "Curated dataset verified: customers" in contents
    assert "Dataset processing completed: customers" in contents
    assert "Status              : PASS" in contents


if __name__ == "__main__":
    raise SystemExit(main())
