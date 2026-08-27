from __future__ import annotations

from typing import Iterable

import pandas as pd


class CuratedDatasetValidator:
    """
    Validates curated datasets after they have been read from S3.

    Responsibilities:
    - Validate that the dataset is a pandas DataFrame.
    - Validate that required columns exist.
    - Validate that the dataset is not unexpectedly empty.
    - Validate that required columns do not contain null values.
    - Return a simple validation result.

    This class does not:
    - Read from S3.
    - Write to S3.
    - Modify the input DataFrame.
    - Perform business transformations.
    """


    def validate(
        self,
        dataframe: pd.DataFrame,
        required_columns: Iterable[str],
        dataset_name: str,
        allow_empty: bool = False,
    ) -> dict:
        """
        Validate a curated dataset.

        Returns:
            {
                "valid": bool,
                "dataset_name": str,
                "row_count": int,
                "column_count": int,
                "missing_columns": list[str],
                "null_columns": list[str],
                "errors": list[str],
            }
        """

        errors: list[str] = []

        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("dataframe must be a pandas DataFrame")

        required_columns = list(required_columns)

        missing_columns = [
            column
            for column in required_columns
            if column not in dataframe.columns
        ]

        if missing_columns:
            errors.append(
                f"Missing required columns: {missing_columns}"
            )

        if dataframe.empty and not allow_empty:
            errors.append("Dataset is empty")

        null_columns = [
            column
            for column in required_columns
            if column in dataframe.columns
            and dataframe[column].isnull().any()
        ]

        if null_columns:
            errors.append(
                f"Required columns contain null values: {null_columns}"
            )

        return {
            "valid": len(errors) == 0,
            "dataset_name": dataset_name,
            "row_count": len(dataframe),
            "column_count": len(dataframe.columns),
            "missing_columns": missing_columns,
            "null_columns": null_columns,
            "errors": errors,
        }