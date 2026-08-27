from __future__ import annotations

import pandas as pd


class CuratedDatasetStatisticsService:
    """
    Provides read-only profiling and statistics for curated datasets.

    This class does not:
    - Read from S3.
    - Write to S3.
    - Modify the input DataFrame.
    - Perform dataset validation.
    """

    def row_count(self, dataframe: pd.DataFrame) -> int:
        self._validate_dataframe(dataframe)
        return len(dataframe)

    def column_count(self, dataframe: pd.DataFrame) -> int:
        self._validate_dataframe(dataframe)
        return len(dataframe.columns)

    def null_counts(self, dataframe: pd.DataFrame) -> dict[str, int]:
        self._validate_dataframe(dataframe)

        return {
            column: int(dataframe[column].isnull().sum())
            for column in dataframe.columns
        }

    def unique_counts(self, dataframe: pd.DataFrame) -> dict[str, int]:
        self._validate_dataframe(dataframe)

        return {
            column: int(dataframe[column].nunique(dropna=True))
            for column in dataframe.columns
        }

    def numeric_statistics(
        self,
        dataframe: pd.DataFrame,
    ) -> dict[str, dict[str, float]]:
        self._validate_dataframe(dataframe)

        numeric_columns = dataframe.select_dtypes(
            include="number"
        ).columns

        statistics: dict[str, dict[str, float]] = {}

        for column in numeric_columns:
            series = dataframe[column]

            statistics[column] = {
                "min": float(series.min()),
                "max": float(series.max()),
                "mean": float(series.mean()),
                "sum": float(series.sum()),
            }

        return statistics

    def profile(self, dataframe: pd.DataFrame) -> dict:
        """
        Return a complete lightweight dataset profile.
        """

        self._validate_dataframe(dataframe)

        return {
            "row_count": self.row_count(dataframe),
            "column_count": self.column_count(dataframe),
            "null_counts": self.null_counts(dataframe),
            "unique_counts": self.unique_counts(dataframe),
            "numeric_statistics": self.numeric_statistics(dataframe),
        }

    @staticmethod
    def _validate_dataframe(dataframe: pd.DataFrame) -> None:
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError(
                "dataframe must be a pandas DataFrame"
            )