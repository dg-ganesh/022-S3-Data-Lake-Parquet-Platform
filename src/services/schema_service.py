"""
Project : S3 Data Lake + Parquet Platform
Project ID : 022

Schema Service
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class SchemaField:
    """Represents a single dataset field."""

    name: str
    data_type: str


@dataclass(frozen=True)
class SchemaValidationResult:
    """Represents the result of schema validation."""

    is_valid: bool
    missing_columns: list[str]
    unexpected_columns: list[str]
    type_mismatches: dict[str, dict[str, str]]


class SchemaService:
    """Provides schema inspection and validation."""

    @staticmethod
    def _is_type_compatible(
        expected_type: str,
        actual_type: str,
    ) -> bool:
        """
        Determine whether a Pandas dtype satisfies
        the configured logical schema type.
        """
        normalized_expected = (
            expected_type.strip().lower()
        )

        normalized_actual = (
            actual_type.strip().lower()
        )

        if normalized_expected == "string":
            return normalized_actual in {
                "string",
                "object",
            }

        return (
            normalized_expected
            == normalized_actual
        )

    def infer_schema(
        self,
        dataframe: pd.DataFrame,
    ) -> list[SchemaField]:
        """
        Infer a schema from a DataFrame.

        Args:
            dataframe: DataFrame to inspect.

        Returns:
            List of schema fields.
        """
        return [
            SchemaField(
                name=str(column),
                data_type=str(dataframe[column].dtype),
            )
            for column in dataframe.columns
        ]

    def get_schema_dict(
        self,
        dataframe: pd.DataFrame,
    ) -> dict[str, str]:
        """
        Return the inferred schema as a dictionary.

        Args:
            dataframe: DataFrame to inspect.

        Returns:
            Mapping of column name to pandas datatype.
        """
        return {
            field.name: field.data_type
            for field in self.infer_schema(dataframe)
        }

    def validate_schema(
        self,
        dataframe: pd.DataFrame,
        expected_schema: dict[str, str],
    ) -> SchemaValidationResult:
        """
        Validate a DataFrame against an expected schema.

        Args:
            dataframe: DataFrame to validate.
            expected_schema: Expected column/type mapping.

        Returns:
            SchemaValidationResult containing validation details.
        """
        actual_schema = self.get_schema_dict(dataframe)

        expected_columns = set(expected_schema)
        actual_columns = set(actual_schema)

        missing_columns = sorted(
            expected_columns - actual_columns
        )

        unexpected_columns = sorted(
            actual_columns - expected_columns
        )

        type_mismatches: dict[str, dict[str, str]] = {}

        for column in sorted(expected_columns & actual_columns):
            expected_type = expected_schema[column]
            actual_type = actual_schema[column]

            if not self._is_type_compatible(
                expected_type,
                actual_type,
            ):
                type_mismatches[column] = {
                    "expected": expected_type,
                    "actual": actual_type,
                }

        is_valid = not (
            missing_columns
            or unexpected_columns
            or type_mismatches
        )

        return SchemaValidationResult(
            is_valid=is_valid,
            missing_columns=missing_columns,
            unexpected_columns=unexpected_columns,
            type_mismatches=type_mismatches,
        )

    def validate_required_columns(
        self,
        dataframe: pd.DataFrame,
        required_columns: list[str],
    ) -> list[str]:
        """
        Return required columns that are missing.

        Args:
            dataframe: DataFrame to inspect.
            required_columns: Columns that must exist.

        Returns:
            Sorted list of missing columns.
        """
        actual_columns = set(
            str(column)
            for column in dataframe.columns
        )

        return sorted(
            set(required_columns) - actual_columns
        )

    def has_required_columns(
        self,
        dataframe: pd.DataFrame,
        required_columns: list[str],
    ) -> bool:
        """
        Check whether all required columns exist.

        Args:
            dataframe: DataFrame to inspect.
            required_columns: Required column names.

        Returns:
            True when all required columns exist.
        """
        return not self.validate_required_columns(
            dataframe,
            required_columns,
        )


__all__ = [
    "SchemaField",
    "SchemaValidationResult",
    "SchemaService",
]
