from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DatasetSchema:
    dataset_name: str
    columns: tuple[str, ...]
    column_types: tuple[tuple[str, str], ...]


class DatasetSchemaRegistry:
    """
    Read/write in-memory registry for curated dataset schemas.

    This module owns schema definitions only.
    It does not:
    - read or write Parquet files
    - access S3
    - transform DataFrames
    - execute queries
    """

    def __init__(
        self,
        schemas: dict[str, DatasetSchema] | None = None,
    ) -> None:
        self._schemas = schemas or {}

    def register_schema(
        self,
        *,
        dataset_name: str,
        columns: list[str] | tuple[str, ...],
        column_types: dict[str, str],
    ) -> DatasetSchema:

        if not dataset_name:
            raise ValueError("dataset_name must not be empty")

        if dataset_name in self._schemas:
            raise ValueError(
                f"Schema already exists: {dataset_name}"
            )

        column_names = tuple(columns)

        if not column_names:
            raise ValueError(
                "columns must contain at least one column"
            )

        missing_types = [
            column
            for column in column_names
            if column not in column_types
        ]

        if missing_types:
            raise ValueError(
                f"Missing types for columns: {missing_types}"
            )

        extra_types = [
            column
            for column in column_types
            if column not in column_names
        ]

        if extra_types:
            raise ValueError(
                f"Types supplied for unknown columns: {extra_types}"
            )

        schema = DatasetSchema(
            dataset_name=dataset_name,
            columns=column_names,
            column_types=tuple(
                (column, column_types[column])
                for column in column_names
            ),
        )

        self._schemas[dataset_name] = schema

        return schema

    def get_schema(
        self,
        dataset_name: str,
    ) -> DatasetSchema:

        if dataset_name not in self._schemas:
            raise KeyError(
                f"Schema not found: {dataset_name}"
            )

        return self._schemas[dataset_name]

    def list_datasets(self) -> list[str]:
        return sorted(self._schemas.keys())

    def get_column_type(
        self,
        dataset_name: str,
        column_name: str,
    ) -> str:

        schema = self.get_schema(dataset_name)

        for column, column_type in schema.column_types:
            if column == column_name:
                return column_type

        raise KeyError(
            f"Column not found: {dataset_name}.{column_name}"
        )

    def as_dict(
        self,
        dataset_name: str,
    ) -> dict[str, Any]:

        schema = self.get_schema(dataset_name)

        return {
            "dataset_name": schema.dataset_name,
            "columns": list(schema.columns),
            "column_types": dict(schema.column_types),
        }