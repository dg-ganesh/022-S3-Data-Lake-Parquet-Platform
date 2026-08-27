"""
Project : S3 Data Lake + Parquet Platform
Project ID : 022

Partition Service
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import pandas as pd


class PartitionService:
    """
    Service responsible for partitioned Parquet datasets.

    Responsibilities:

        DataFrame
            ↓
        Validate partition columns
            ↓
        Create partitioned directory structure
            ↓
        Write Parquet files
            ↓
        Inspect partitioned dataset
    """

    def validate_partition_columns(
        self,
        dataframe: pd.DataFrame,
        partition_columns: Iterable[str],
    ) -> list[str]:
        """
        Validate partition columns against a DataFrame.

        Args:
            dataframe:
                Source DataFrame.

            partition_columns:
                Columns that will be used for partitioning.

        Returns:
            Normalized list of partition columns.

        Raises:
            ValueError:
                If partition configuration is invalid.
        """

        if not isinstance(
            dataframe,
            pd.DataFrame,
        ):
            raise TypeError(
                "dataframe must be a pandas DataFrame."
            )

        columns = [
            str(column).strip()
            for column in partition_columns
        ]

        columns = [
            column
            for column in columns
            if column
        ]

        if not columns:
            raise ValueError(
                "At least one partition column "
                "must be provided."
            )

        duplicates = [
            column
            for column in columns
            if columns.count(column) > 1
        ]

        if duplicates:
            raise ValueError(
                "Duplicate partition columns: "
                f"{sorted(set(duplicates))}"
            )

        missing_columns = [
            column
            for column in columns
            if column not in dataframe.columns
        ]

        if missing_columns:
            raise ValueError(
                "Partition columns do not exist "
                "in the DataFrame: "
                f"{missing_columns}"
            )

        for column in columns:
            if dataframe[column].isna().any():
                raise ValueError(
                    "Partition column contains "
                    f"null values: {column}"
                )

        return columns

    def write_partitioned_dataset(
        self,
        dataframe: pd.DataFrame,
        output_directory: Path,
        partition_columns: Iterable[str],
        compression: str = "snappy",
    ) -> list[Path]:
        """
        Write a DataFrame as a partitioned Parquet dataset.

        Args:
            dataframe:
                DataFrame to write.

            output_directory:
                Root directory for the dataset.

            partition_columns:
                Columns used for partitioning.

            compression:
                Parquet compression codec.

        Returns:
            List of generated Parquet files.
        """

        if not isinstance(
            dataframe,
            pd.DataFrame,
        ):
            raise TypeError(
                "dataframe must be a pandas DataFrame."
            )

        output_directory = Path(
            output_directory
        )

        columns = (
            self.validate_partition_columns(
                dataframe,
                partition_columns,
            )
        )

        if output_directory.exists():
            if not output_directory.is_dir():
                raise ValueError(
                    "Output path is not a directory: "
                    f"{output_directory}"
                )
        else:
            output_directory.mkdir(
                parents=True,
                exist_ok=True,
            )

        self._validate_compression(
            compression
        )

        dataframe.to_parquet(
            output_directory,
            engine="pyarrow",
            compression=(
                None
                if compression.lower() == "none"
                else compression.lower()
            ),
            partition_cols=columns,
            index=False,
        )

        parquet_files = (
            self.list_parquet_files(
                output_directory
            )
        )

        if not parquet_files:
            raise RuntimeError(
                "Partitioned Parquet dataset "
                "was not created: "
                f"{output_directory}"
            )

        return parquet_files

    def list_parquet_files(
        self,
        dataset_directory: Path,
    ) -> list[Path]:
        """
        Recursively list Parquet files in a dataset.

        Args:
            dataset_directory:
                Dataset root directory.

        Returns:
            Sorted list of Parquet files.
        """

        dataset_directory = Path(
            dataset_directory
        )

        if not dataset_directory.exists():
            return []

        if not dataset_directory.is_dir():
            raise ValueError(
                "Dataset path is not a directory: "
                f"{dataset_directory}"
            )

        return sorted(
            [
                path
                for path in dataset_directory.rglob(
                    "*.parquet"
                )
                if path.is_file()
            ],
            key=lambda path: str(path).lower(),
        )

    def get_partition_summary(
        self,
        dataset_directory: Path,
    ) -> dict[str, Any]:
        """
        Inspect a partitioned Parquet dataset.

        Args:
            dataset_directory:
                Dataset root directory.

        Returns:
            Partition summary.
        """

        dataset_directory = Path(
            dataset_directory
        )

        parquet_files = (
            self.list_parquet_files(
                dataset_directory
            )
        )

        partition_directories: set[str] = set()

        for parquet_file in parquet_files:
            relative_parent = (
                parquet_file.parent.relative_to(
                    dataset_directory
                )
            )

            if str(relative_parent) != ".":
                partition_directories.add(
                    str(relative_parent)
                )

        return {
            "dataset_directory": str(
                dataset_directory
            ),
            "parquet_file_count": len(
                parquet_files
            ),
            "partition_directory_count": len(
                partition_directories
            ),
            "partition_directories": sorted(
                partition_directories
            ),
            "files": [
                str(path)
                for path in parquet_files
            ],
        }

    def validate_partitioned_dataset(
        self,
        dataset_directory: Path,
    ) -> dict[str, Any]:
        """
        Validate that a partitioned dataset exists
        and contains readable Parquet files.

        Args:
            dataset_directory:
                Dataset root directory.

        Returns:
            Validation summary.
        """

        dataset_directory = Path(
            dataset_directory
        )

        if not dataset_directory.exists():
            raise FileNotFoundError(
                "Partitioned dataset does not exist: "
                f"{dataset_directory}"
            )

        if not dataset_directory.is_dir():
            raise ValueError(
                "Partitioned dataset path is not "
                "a directory: "
                f"{dataset_directory}"
            )

        parquet_files = (
            self.list_parquet_files(
                dataset_directory
            )
        )

        if not parquet_files:
            raise RuntimeError(
                "No Parquet files found in "
                "partitioned dataset: "
                f"{dataset_directory}"
            )

        invalid_files: list[str] = []

        for parquet_file in parquet_files:
            try:
                pd.read_parquet(
                    parquet_file,
                    engine="pyarrow",
                )
            except Exception:
                invalid_files.append(
                    str(parquet_file)
                )

        if invalid_files:
            raise RuntimeError(
                "Invalid Parquet files detected: "
                f"{invalid_files}"
            )

        summary = (
            self.get_partition_summary(
                dataset_directory
            )
        )

        return {
            "valid": True,
            **summary,
        }

    @staticmethod
    def _validate_compression(
        compression: str,
    ) -> None:
        """
        Validate the Parquet compression codec.
        """

        supported = {
            "snappy",
            "gzip",
            "brotli",
            "zstd",
            "lz4",
            "none",
        }

        if not isinstance(
            compression,
            str,
        ):
            raise ValueError(
                "Compression must be a string."
            )

        normalized = (
            compression.strip().lower()
        )

        if normalized not in supported:
            raise ValueError(
                "Unsupported Parquet compression: "
                f"{compression}"
            )


__all__ = [
    "PartitionService",
]