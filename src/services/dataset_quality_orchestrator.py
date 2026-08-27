from __future__ import annotations

from typing import Any

import pandas as pd

from src.services.dataset_quality_report_service import (
    DatasetQualityReportService,
)
from src.services.dataset_quality_service import (
    DatasetQualityService,
)


class DatasetQualityOrchestrator:
    """
    Coordinates dataset quality checks and report generation.

    The orchestrator contains no individual quality-rule logic.
    It delegates rule execution to DatasetQualityService and
    report construction to DatasetQualityReportService.
    """

    def __init__(
        self,
        quality_service: DatasetQualityService | None = None,
        report_service: DatasetQualityReportService | None = None,
    ) -> None:

        self.quality_service = (
            quality_service
            if quality_service is not None
            else DatasetQualityService()
        )

        self.report_service = (
            report_service
            if report_service is not None
            else DatasetQualityReportService()
        )

    def validate_dataset(
        self,
        dataset_name: str,
        dataframe: pd.DataFrame,
        required_columns: list[str] | None = None,
        not_null_columns: list[str] | None = None,
        unique_columns: list[str] | None = None,
    ) -> dict[str, Any]:

        self.quality_service = DatasetQualityService()

        self.quality_service.check_not_empty(
            dataset_name,
            dataframe,
        )

        if required_columns:
            self.quality_service.check_required_columns(
                dataset_name,
                dataframe,
                required_columns,
            )

        if not_null_columns:
            for column in not_null_columns:
                self.quality_service.check_not_null(
                    dataset_name,
                    dataframe,
                    column,
                )

        if unique_columns:
            for column in unique_columns:
                self.quality_service.check_unique(
                    dataset_name,
                    dataframe,
                    column,
                )

        results = self.quality_service.get_results()

        return self.report_service.build_report(
            dataset_name,
            results,
        )