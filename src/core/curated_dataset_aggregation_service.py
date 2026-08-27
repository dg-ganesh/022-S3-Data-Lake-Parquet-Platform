from __future__ import annotations

from typing import Iterable

import pandas as pd


class CuratedDatasetAggregationService:
    """
    Provides simple read-only aggregation operations on curated data.

    Responsibilities:
    - Count rows.
    - Calculate sum.
    - Calculate average.
    - Calculate minimum.
    - Calculate maximum.
    - Group and aggregate.

    This class does not:
    - Read from S3.
    - Write to S3.
    - Validate schemas.
    - Modify the input DataFrame.
    """

    def count(self, dataframe: pd.DataFrame) -> int:
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("dataframe must be a pandas DataFrame")

        return len(dataframe)

    def sum(
        self,
        dataframe: pd.DataFrame,
        column: str,
    ):
        self._validate_column(dataframe, column)
        return dataframe[column].sum()

    def average(
        self,
        dataframe: pd.DataFrame,
        column: str,
    ):
        self._validate_column(dataframe, column)
        return dataframe[column].mean()

    def minimum(
        self,
        dataframe: pd.DataFrame,
        column: str,
    ):
        self._validate_column(dataframe, column)
        return dataframe[column].min()

    def maximum(
        self,
        dataframe: pd.DataFrame,
        column: str,
    ):
        self._validate_column(dataframe, column)
        return dataframe[column].max()

    def group_and_aggregate(
        self,
        dataframe: pd.DataFrame,
        group_by: Iterable[str],
        aggregate_column: str,
        operation: str = "sum",
    ) -> pd.DataFrame:

        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("dataframe must be a pandas DataFrame")

        group_by = list(group_by)

        for column in group_by:
            self._validate_column(dataframe, column)

        self._validate_column(dataframe, aggregate_column)

        supported_operations = {
            "sum",
            "mean",
            "min",
            "max",
            "count",
        }

        if operation not in supported_operations:
            raise ValueError(
                f"Unsupported aggregation operation: {operation}"
            )

        result = (
            dataframe
            .groupby(group_by, dropna=False)[aggregate_column]
            .agg(operation)
            .reset_index()
        )

        return result

    @staticmethod
    def _validate_column(
        dataframe: pd.DataFrame,
        column: str,
    ) -> None:

        if column not in dataframe.columns:
            raise ValueError(
                f"Column does not exist: {column}"
            )