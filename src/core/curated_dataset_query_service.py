from __future__ import annotations

from collections.abc import Iterable

import pandas as pd


class CuratedDatasetQueryService:
    """
    Provides simple read-only query operations on a curated DataFrame.

    Responsibilities:
    - Filter rows using a boolean condition.
    - Select requested columns.
    - Return a new DataFrame.

    This class does not:
    - Read from S3.
    - Write to S3.
    - Validate dataset schemas.
    - Modify the supplied DataFrame.
    """

    def filter_rows(
        self,
        dataframe: pd.DataFrame,
        condition: pd.Series,
    ) -> pd.DataFrame:
        """
        Return rows matching the supplied boolean condition.
        """

        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("dataframe must be a pandas DataFrame")

        if not isinstance(condition, pd.Series):
            raise TypeError("condition must be a pandas Series")

        if len(condition) != len(dataframe):
            raise ValueError(
                "condition length must match dataframe length"
            )

        return dataframe.loc[condition].copy()

    def select_columns(
        self,
        dataframe: pd.DataFrame,
        columns: Iterable[str],
    ) -> pd.DataFrame:
        """
        Return only the requested columns.
        """

        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("dataframe must be a pandas DataFrame")

        columns = list(columns)

        missing_columns = [
            column
            for column in columns
            if column not in dataframe.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Requested columns do not exist: {missing_columns}"
            )

        return dataframe.loc[:, columns].copy()

    def filter_and_select(
        self,
        dataframe: pd.DataFrame,
        condition: pd.Series,
        columns: Iterable[str],
    ) -> pd.DataFrame:
        """
        Filter rows and then select columns.
        """

        filtered = self.filter_rows(
            dataframe=dataframe,
            condition=condition,
        )

        return self.select_columns(
            dataframe=filtered,
            columns=columns,
        )
    