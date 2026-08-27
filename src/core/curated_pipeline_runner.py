"""
Project : S3 Data Lake + Parquet Platform
Project ID : 022

Curated Pipeline Runner
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.config import AppConfig, get_config
from src.core.curated_pipeline import CuratedPipeline
from src.services.curated_pipeline_report_service import (
    CuratedPipelineReportService,
)
from src.services.execution_report_service import (
    ExecutionReportService,
)


class CuratedPipelineRunner:
    """
    Orchestrate curated pipeline execution across datasets.

    The runner is responsible for orchestration across
    multiple datasets. Individual dataset processing
    remains the responsibility of CuratedPipeline.
    """

    def __init__(
        self,
        config: AppConfig | None = None,
        pipeline: CuratedPipeline | None = None,
        report_service: (
            CuratedPipelineReportService | None
        ) = None,
    ) -> None:
        """
        Initialize the runner.

        Args:
            config:
                Optional application configuration.

            pipeline:
                Optional preconfigured curated pipeline.

            report_service:
                Optional curated pipeline reporting adapter.
        """

        self.config = config or get_config()

        self.report_service = report_service

        if self.report_service is None and pipeline is None:
            execution_report_service = (
                ExecutionReportService(
                    log_directory=self.config.log_directory,
                    application_version=(
                        self.config.application_version
                    ),
                )
            )

            self.report_service = (
                CuratedPipelineReportService(
                    execution_report_service
                )
            )

        self.pipeline = (
            pipeline
            or CuratedPipeline(
                config=self.config,
                report_service=self.report_service,
            )
        )

        if (
            pipeline is not None
            and self.report_service is not None
            and isinstance(
                self.pipeline,
                CuratedPipeline,
            )
        ):
            self.pipeline.report_service = self.report_service

    def run_dataset(
        self,
        source_file: Path,
        dataset_name: str,
    ) -> dict[str, Any]:
        """
        Process one dataset.

        Args:
            source_file:
                Source dataset file.

            dataset_name:
                Dataset definition name.

        Returns:
            Dataset processing result.
        """

        return self.pipeline.process_dataset(
            source_file=Path(source_file),
            dataset_name=dataset_name,
        )

    def run(
        self,
        dataset_names: list[str] | dict[str, Path],
    ) -> dict[str, Any]:
        """
        Process multiple datasets.

        Args:
            dataset_names:
                Dataset names to process. A mapping of dataset name
                to source file is also accepted for compatibility
                with the application entry point.

        Returns:
            Overall execution summary.

        """
        if self.report_service is not None:
            self.report_service.execution_report_service.start_execution()

        try:
            dataset_sources = self._resolve_dataset_sources(
                dataset_names
            )

            results: dict[str, Any] = {}
            failures: dict[str, str] = {}

            for dataset_name, source_file in dataset_sources:
                try:
                    results[dataset_name] = self.run_dataset(
                        source_file=source_file,
                        dataset_name=dataset_name,
                    )
                except Exception as exc:
                    failures[dataset_name] = str(exc)

            summary = {
                "successful": not failures,
                "dataset_count": len(dataset_sources),
                "successful_count": len(results),
                "failed_count": len(failures),
                "results": results,
                "failures": failures,
            }

            if self.report_service is not None:
                self.report_service.execution_report_service.complete_execution(
                    "PASS" if summary["successful"] else "FAIL"
                )

            return summary

        except Exception as exc:
            if self.report_service is not None:
                self.report_service.record_failure(
                    "Curated pipeline runner",
                    exc,
                )
                self.report_service.execution_report_service.complete_execution(
                    "FAIL"
                )

            raise

    def _resolve_dataset_sources(
        self,
        dataset_names: list[str] | dict[str, Path],
    ) -> list[tuple[str, Path]]:
        """Resolve names to the configured CSV source paths."""
        if isinstance(dataset_names, dict):
            return [
                (dataset_name, Path(source_file))
                for dataset_name, source_file
                in dataset_names.items()
            ]

        return [
            (
                dataset_name,
                Path(self.config.input_directory)
                / f"{dataset_name}.csv",
            )
            for dataset_name in dataset_names
        ]


__all__ = [
    "CuratedPipelineRunner",
]
