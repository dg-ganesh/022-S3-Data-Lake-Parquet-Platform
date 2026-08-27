"""
Project : S3 Data Lake + Parquet Platform
Project ID : 022

Curated Pipeline Report Service
"""

from __future__ import annotations

from typing import Any

from src.services.execution_report_service import (
    ExecutionReportService,
)


class CuratedPipelineReportService:
    """
    Converts curated-pipeline processing events into
    standardized execution-report checkpoints.
    """

    def __init__(
        self,
        execution_report_service: (
            ExecutionReportService | None
        ) = None,
    ) -> None:
        """
        Initialize the reporting adapter.

        Args:
            execution_report_service:
                Existing generic execution report service.
        """
        self.execution_report_service = (
            execution_report_service
            or ExecutionReportService()
        )

    def record_dataset_started(
        self,
        dataset_name: str,
    ) -> None:
        """
        Record the beginning of dataset processing.
        """
        self.execution_report_service.record_checkpoint(
            f"Dataset processing started: {dataset_name}"
        )

    def record_dataset_definition_loaded(
        self,
        dataset_name: str,
    ) -> None:
        """
        Record successful dataset-definition loading.
        """
        self.execution_report_service.record_checkpoint(
            f"Dataset definition loaded: {dataset_name}"
        )

    def record_source_loaded(
        self,
        dataset_name: str,
        row_count: int,
    ) -> None:
        """
        Record successful source loading.
        """
        self.execution_report_service.record_checkpoint(
            f"Source dataset loaded: "
            f"{dataset_name} "
            f"({row_count} rows)"
        )

    def record_schema_validated(
        self,
        dataset_name: str,
    ) -> None:
        """
        Record successful schema validation.
        """
        self.execution_report_service.record_checkpoint(
            f"Schema validated: {dataset_name}"
        )

    def record_parquet_generated(
        self,
        dataset_name: str,
        parquet_file_count: int,
    ) -> None:
        """
        Record successful Parquet generation.
        """
        self.execution_report_service.record_checkpoint(
            f"Parquet dataset generated: "
            f"{dataset_name} "
            f"({parquet_file_count} files)"
        )

    def record_parquet_verified(
        self,
        dataset_name: str,
    ) -> None:
        """
        Record successful Parquet validation.
        """
        self.execution_report_service.record_checkpoint(
            f"Parquet dataset verified: {dataset_name}"
        )

    def record_curated_upload(
        self,
        dataset_name: str,
        uploaded_file_count: int,
    ) -> None:
        """
        Record successful S3 curated upload.
        """
        self.execution_report_service.record_checkpoint(
            f"Curated dataset uploaded: "
            f"{dataset_name} "
            f"({uploaded_file_count} files)"
        )

    def record_curated_verification(
        self,
        dataset_name: str,
    ) -> None:
        """
        Record successful S3 curated verification.
        """
        self.execution_report_service.record_checkpoint(
            f"Curated dataset verified: {dataset_name}"
        )

    def record_dataset_completed(
        self,
        dataset_name: str,
    ) -> None:
        """
        Record successful completion of one dataset.
        """
        self.execution_report_service.record_checkpoint(
            f"Dataset processing completed: "
            f"{dataset_name}"
        )

    def record_failure(
        self,
        stage: str,
        error: Exception,
    ) -> None:
        """
        Record a controlled pipeline failure.
        """
        self.execution_report_service.record_failure(
            stage,
            error,
        )

    def get_report_contents(self) -> str:
        """
        Return the current execution report.
        """
        return (
            self.execution_report_service
            .get_report_contents()
        )


__all__ = [
    "CuratedPipelineReportService",
]
