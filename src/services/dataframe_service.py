"""
Project : S3 Data Lake + Parquet Platform
Project ID : 022

DataFrame Service
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


SUPPORTED_FORMATS = {
    ".csv",
    ".json",
    ".jsonl",
}


class DataFrameService:
    """Loads supported datasets into pandas DataFrames."""

    def load_file(
        self,
        source_file: Path,
    ) -> pd.DataFrame:
        """
        Load a supported source file into a DataFrame.

        Args:
            source_file: Path to the source dataset.

        Returns:
            Loaded pandas DataFrame.

        Raises:
            FileNotFoundError: If the source file does not exist.
            ValueError: If the file format is unsupported.
        """
        self.validate_file(source_file)

        suffix = source_file.suffix.lower()

        if suffix == ".csv":
            return self._load_csv(source_file)

        if suffix in {".json", ".jsonl"}:
            return self._load_json(source_file)

        raise ValueError(
            f"Unsupported file format: {suffix}"
        )

    def validate_file(
        self,
        source_file: Path,
    ) -> None:
        """
        Validate a source dataset before loading.

        Args:
            source_file: Dataset to validate.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file format is unsupported.
        """
        if not source_file.exists():
            raise FileNotFoundError(
                f"Source file does not exist: {source_file}"
            )

        if not source_file.is_file():
            raise ValueError(
                f"Source path is not a file: {source_file}"
            )

        if source_file.suffix.lower() not in SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported file format: "
                f"{source_file.suffix}"
            )

    def get_row_count(
        self,
        dataframe: pd.DataFrame,
    ) -> int:
        """
        Return the number of rows in a DataFrame.

        Args:
            dataframe: DataFrame to inspect.

        Returns:
            Number of rows.
        """
        return len(dataframe)

    def get_column_names(
        self,
        dataframe: pd.DataFrame,
    ) -> list[str]:
        """
        Return DataFrame column names.

        Args:
            dataframe: DataFrame to inspect.

        Returns:
            List of column names.
        """
        return [
            str(column)
            for column in dataframe.columns
        ]

    def get_column_count(
        self,
        dataframe: pd.DataFrame,
    ) -> int:
        """
        Return the number of columns.

        Args:
            dataframe: DataFrame to inspect.

        Returns:
            Number of columns.
        """
        return len(dataframe.columns)

    def get_dataset_summary(
        self,
        dataframe: pd.DataFrame,
    ) -> dict[str, object]:
        """
        Generate basic metadata for a DataFrame.

        Args:
            dataframe: DataFrame to inspect.

        Returns:
            Dictionary containing dataset metadata.
        """
        return {
            "row_count": self.get_row_count(dataframe),
            "column_count": self.get_column_count(dataframe),
            "columns": self.get_column_names(dataframe),
        }

    def _load_csv(
        self,
        source_file: Path,
    ) -> pd.DataFrame:
        """
        Load a CSV dataset.

        Args:
            source_file: CSV file path.

        Returns:
            Loaded DataFrame.
        """
        return pd.read_csv(source_file)

    def _load_json(
        self,
        source_file: Path,
    ) -> pd.DataFrame:
        """
        Load a JSON or JSON Lines dataset.

        Args:
            source_file: JSON file path.

        Returns:
            Loaded DataFrame.
        """
        try:
            return pd.read_json(
                source_file,
                lines=source_file.suffix.lower() == ".jsonl",
            )
        except ValueError as exc:
            raise ValueError(
                f"Unable to parse JSON dataset: "
                f"{source_file}"
            ) from exc


__all__ = [
    "DataFrameService",
    "SUPPORTED_FORMATS",
]