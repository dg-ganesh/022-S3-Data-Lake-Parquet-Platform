from __future__ import annotations

from typing import Any

import pandas as pd

from src.services.dataset_quality_execution_report import (
    DatasetQualityExecutionReport,
)
from src.services.dataset_quality_orchestrator import (
    DatasetQualityOrchestrator,
)


class DatasetQualityRunner:
    """
    End-to-end runner for dataset quality validation.

    The runner coordinates the quality orchestrator and the
    execution-report service. It does not implement individual
    quality rules.
    """

    def __init__(
        self,
        orchestrator: DatasetQualityOrchestrator | None = None,
        execution_report: DatasetQualityExecutionReport | None = None,
    ) -> None:

        self.orchestrator = (
            orchestrator
            if orchestrator is not None
            else DatasetQualityOrchestrator()
        )

        self.execution_report = (
            execution_report
            if execution_report is not None
            else DatasetQualityExecutionReport()
        )

    def run(
        self,
        dataset_name: str,
        dataframe: pd.DataFrame,
        required_columns: list[str] | None = None,
        not_null_columns: list[str] | None = None,
        unique_columns: list[str] | None = None,
    ) -> dict[str, Any]:

        quality_report = self.orchestrator.validate_dataset(
            dataset_name=dataset_name,
            dataframe=dataframe,
            required_columns=required_columns,
            not_null_columns=not_null_columns,
            unique_columns=unique_columns,
        )

        return self.execution_report.build_execution_result(
            quality_report
        )