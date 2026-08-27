from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass
class ValidationResult:
    valid: bool
    dataset_name: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "dataset_name": self.dataset_name,
            "errors": self.errors,
            "warnings": self.warnings,
        }


class CuratedDatasetValidationService:
    """
    Read-only validation service for curated dataset DataFrames.

    Responsibilities:
    - Validate dataset existence.
    - Validate required columns.
    - Validate partition columns.
    - Validate non-empty datasets.
    
    This service does not:
    - read from S3
    - write to S3
    - write Parquet
    - modify the supplied DataFrame
    """

    def __init__(self, dataset_definition_service):
        self.dataset_definition_service = dataset_definition_service

    def validate(
        self,
        dataset_name: str,
        dataframe: pd.DataFrame,
    ) -> ValidationResult:

        errors: list[str] = []
        warnings: list[str] = []

        # ---------------------------------------------------------
        # 1. Dataset definition
        # ---------------------------------------------------------
        try:
            definition = self.dataset_definition_service.get_definition(
                dataset_name
            )
        except Exception as exc:
            return ValidationResult(
                valid=False,
                dataset_name=dataset_name,
                errors=[f"Unknown dataset '{dataset_name}': {exc}"],
            )

        if definition is None:
            return ValidationResult(
                valid=False,
                dataset_name=dataset_name,
                errors=[f"Unknown dataset '{dataset_name}'"],
            )

        # ---------------------------------------------------------
        # 2. Empty dataset validation
        # ---------------------------------------------------------
        if dataframe is None:
            errors.append("DataFrame is None.")
            return ValidationResult(
                valid=False,
                dataset_name=dataset_name,
                errors=errors,
                warnings=warnings,
            )

        if dataframe.empty:
            errors.append("Dataset contains no rows.")

        # ---------------------------------------------------------
        # 3. Required columns
        # ---------------------------------------------------------
        required_columns = self._get_required_columns(definition)

        missing_columns = [
            column
            for column in required_columns
            if column not in dataframe.columns
        ]

        if missing_columns:
            errors.append(
                "Missing required columns: "
                + ", ".join(missing_columns)
            )

        # ---------------------------------------------------------
        # 4. Partition column
        # ---------------------------------------------------------
        partition_columns = self._get_partition_columns(definition)

        missing_partition_columns = [
            column
            for column in partition_columns
            if column not in dataframe.columns
        ]

        if missing_partition_columns:
            errors.append(
                "Missing partition columns: "
                + ", ".join(missing_partition_columns)
            )

        return ValidationResult(
            valid=len(errors) == 0,
            dataset_name=dataset_name,
            errors=errors,
            warnings=warnings,
        )

    @staticmethod
    def _get_required_columns(definition) -> list[str]:
        """
        Extract required columns from the existing dataset definition.
        Supports the existing dictionary/dataclass style definitions.
        """

        if isinstance(definition, dict):
            columns = definition.get("columns", [])
        else:
            columns = getattr(definition, "columns", [])

        if isinstance(columns, dict):
            return list(columns.keys())

        return list(columns or [])

    @staticmethod
    def _get_partition_columns(definition) -> list[str]:
        """
        Extract partition columns from the existing dataset definition.
        """

        if isinstance(definition, dict):
            partition_columns = definition.get("partition_columns", [])
        else:
            partition_columns = getattr(
                definition,
                "partition_columns",
                [],
            )

        if partition_columns is None:
            return []

        if isinstance(partition_columns, str):
            return [partition_columns]

        return list(partition_columns)