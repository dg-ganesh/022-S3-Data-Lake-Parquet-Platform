"""
Project : S3 Data Lake + Parquet Platform
Project ID : 022

Parquet Dataset Processor
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd

from src.services.parquet_service import (
    ParquetService,
)
from src.services.partition_service import (
    PartitionService,
)


class ParquetDatasetProcessor:
    """
    Coordinates generation and validation of a
    Parquet dataset.

    Supports both partitioned and non-partitioned
    datasets.
    """

    def __init__(
        self,
        parquet_service: ParquetService | None = None,
        partition_service: PartitionService | None = None,
    ) -> None:
        """
        Initialize the Parquet dataset processor.
        """

        self.parquet_service = (
            parquet_service
            or ParquetService()
        )

        self.partition_service = (
            partition_service
            or PartitionService()
        )

    def generate_dataset(
        self,
        dataframe: pd.DataFrame,
        output_directory: Path,
        partition_columns: list[str] | None = None,
        compression: str = "snappy",
    ) -> dict[str, object]:
        """
        Generate a Parquet dataset.

        Partitioned datasets are generated when
        partition_columns are supplied.
        """

        if dataframe.empty:
            raise ValueError(
                "Cannot generate Parquet dataset from "
                "an empty DataFrame."
            )

        active_partition_columns = list(
            partition_columns or []
        )

        normalized_compression = (
            self.parquet_service.validate_compression(
                compression
            )
        )

        output_directory = Path(
            output_directory
        )

        if output_directory.is_symlink():
            raise ValueError(
                "Output directory cannot be a symbolic link: "
                f"{output_directory}"
            )

        if output_directory.exists():
            if not output_directory.is_dir():
                raise ValueError(
                    "Output path is not a directory: "
                    f"{output_directory}"
                )

            shutil.rmtree(output_directory)

        output_directory.mkdir(
            parents=True,
            exist_ok=False,
        )

        if active_partition_columns:

            self.partition_service.validate_partition_columns(
                dataframe,
                active_partition_columns,
            )

            self.partition_service.write_partitioned_dataset(
                dataframe=dataframe,
                output_directory=output_directory,
                partition_columns=(
                    active_partition_columns
                ),
                compression=normalized_compression,
            )

            dataset_type = "partitioned"

        else:

            output_file = (
                output_directory
                / "part-00000.parquet"
            )

            self.parquet_service.write_parquet(
                dataframe=dataframe,
                output_file=output_file,
                compression=normalized_compression,
            )

            dataset_type = "non-partitioned"

        parquet_files = (
            self.partition_service.list_parquet_files(
                output_directory
            )
        )

        if not parquet_files:
            raise RuntimeError(
                "Parquet dataset generation produced "
                "no Parquet files: "
                f"{output_directory}"
            )

        return {
            "output_directory": str(
                output_directory
            ),
            "row_count": len(dataframe),
            "column_count": len(
                dataframe.columns
            ),
            "partition_columns": (
                active_partition_columns
            ),
            "compression": normalized_compression,
            "dataset_type": dataset_type,
            "parquet_file_count": len(
                parquet_files
            ),
        }

    def validate_dataset(
        self,
        dataset_directory: Path,
    ) -> dict[str, object]:
        """
        Validate a generated Parquet dataset.
        """

        dataset_directory = Path(
            dataset_directory
        )

        if not dataset_directory.exists():
            raise FileNotFoundError(
                "Parquet dataset directory does not "
                "exist: "
                f"{dataset_directory}"
            )

        parquet_files = (
            self.partition_service.list_parquet_files(
                dataset_directory
            )
        )

        if not parquet_files:
            raise ValueError(
                "No Parquet files found in dataset: "
                f"{dataset_directory}"
            )

        total_rows = 0
        schemas: list[str] = []

        for parquet_file in parquet_files:

            validation = (
                self.parquet_service.validate_parquet(
                    parquet_file
                )
            )

            if not validation.get(
                "valid",
                False,
            ):
                raise RuntimeError(
                    "Parquet validation failed: "
                    f"{parquet_file}"
                )

            metadata = (
                self.parquet_service.get_metadata(
                    parquet_file
                )
            )

            total_rows += int(
                metadata["row_count"]
            )

            schema = (
                self.parquet_service.get_schema(
                    parquet_file
                )
            )

            schemas.append(
                str(schema)
            )

        partition_summary = (
            self.partition_service
            .get_partition_summary(
                dataset_directory
            )
        )

        return {
            "valid": True,
            "dataset_directory": str(
                dataset_directory
            ),
            "parquet_file_count": len(
                parquet_files
            ),
            "row_count": total_rows,
            "partition_count": (
                partition_summary[
                    "partition_directory_count"
                ]
            ),
            "partition_directories": (
                partition_summary[
                    "partition_directories"
                ]
            ),
            "schemas": schemas,
        }

    def process(
        self,
        dataframe: pd.DataFrame,
        output_directory: Path,
        partition_columns: list[str] | None = None,
        compression: str = "snappy",
    ) -> dict[str, object]:
        """
        Generate and validate a Parquet dataset.
        """

        generation_summary = (
            self.generate_dataset(
                dataframe=dataframe,
                output_directory=output_directory,
                partition_columns=partition_columns,
                compression=compression,
            )
        )

        validation_summary = (
            self.validate_dataset(
                output_directory
            )
        )

        return {
            "generation": generation_summary,
            "validation": validation_summary,
        }


__all__ = [
    "ParquetDatasetProcessor",
]
