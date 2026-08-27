from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from src.services.dataset_definition_service import DatasetDefinitionService


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    dataset_name: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class CuratedDatasetValidationService:
    """
    Read-only validation service for curated dataset DataFrames.

    This service validates a DataFrame against the configured
    dataset definition. It does not read or write S3, Parquet,
    or local files.
    """

    def __init__(
        self,
        dataset_definition_service: DatasetDefinitionService,
    ) -> None:
        self.dataset_definition_service = dataset_definition_service

    def validate(
        self,
        dataset_name: str,
        dataframe: pd.DataFrame,
    ) -> ValidationResult:

        errors: list[str] = []
        warnings: list[str] = []

        # ---------------------------------------------------------
        # Dataset definition
        # ---------------------------------------------------------
        try:
            definition = (
                self.dataset_definition_service.get_definition(
                    dataset_name
                )
            )
        except ValueError as exc:
            return ValidationResult(
                valid=False,
                dataset_name=dataset_name,
                errors=[str(exc)],
            )

        # ---------------------------------------------------------
        # DataFrame existence
        # ---------------------------------------------------------
        if dataframe is None:
            return ValidationResult(
                valid=False,
                dataset_name=definition.name,
                errors=["DataFrame cannot be None."],
            )

        # ---------------------------------------------------------
        # Empty dataset
        # ---------------------------------------------------------
        if dataframe.empty:
            errors.append("Dataset contains no rows.")

        # ---------------------------------------------------------
        # Expected schema
        # ---------------------------------------------------------
        expected_schema = (
            self.dataset_definition_service.get_expected_schema(
                dataset_name
            )
        )

        expected_columns = list(expected_schema.keys())
        actual_columns = list(dataframe.columns)

        missing_columns = [
            column
            for column in expected_columns
            if column not in actual_columns
        ]

        unexpected_columns = [
            column
            for column in actual_columns
            if column not in expected_columns
        ]

        if missing_columns:
            errors.append(
                "Missing required columns: "
                + ", ".join(missing_columns)
            )

        if unexpected_columns:
            errors.append(
                "Unexpected columns: "
                + ", ".join(unexpected_columns)
            )

        # ---------------------------------------------------------
        # Data types
        # ---------------------------------------------------------
        for column, expected_dtype in expected_schema.items():
            if column not in dataframe.columns:
                continue

            actual_dtype = str(dataframe[column].dtype)

            if actual_dtype != expected_dtype:
                errors.append(
                    f"Invalid datatype for column '{column}': "
                    f"expected {expected_dtype}, "
                    f"found {actual_dtype}"
                )

        # ---------------------------------------------------------
        # Partition columns
        # ---------------------------------------------------------
        partition_columns = (
            self.dataset_definition_service.get_partition_columns(
                dataset_name
            )
        )

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
            valid=not errors,
            dataset_name=definition.name,
            errors=errors,
            warnings=warnings,
        )


__all__ = [
    "CuratedDatasetValidationService",
    "ValidationResult",
]