"""
Project : S3 Data Lake + Parquet Platform
Project ID : 022

Parquet Service
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


class ParquetService:
    """
    Low-level service for Parquet dataset operations.

    Responsibilities:

        DataFrame
            ↓
        Parquet writing
            ↓
        Parquet validation
            ↓
        Parquet metadata/schema inspection
    """

    SUPPORTED_COMPRESSION = {
        "snappy",
        "gzip",
        "brotli",
        "zstd",
        "lz4",
        "none",
    }

    def validate_compression(
        self,
        compression: str,
    ) -> str:
        """
        Validate and normalize the requested compression codec.

        Args:
            compression:
                Parquet compression codec.

        Returns:
            Normalized compression codec.

        Raises:
            ValueError:
                If compression is unsupported.
        """

        if not isinstance(
            compression,
            str,
        ):
            raise ValueError(
                "Parquet compression must be a string."
            )

        normalized = (
            compression.strip().lower()
        )

        if normalized not in (
            self.SUPPORTED_COMPRESSION
        ):
            raise ValueError(
                "Unsupported Parquet compression: "
                f"{compression}. "
                "Supported values: "
                f"{', '.join(sorted(self.SUPPORTED_COMPRESSION))}"
            )

        return normalized

    def write_parquet(
        self,
        dataframe: pd.DataFrame,
        output_file: Path,
        compression: str = "snappy",
    ) -> Path:
        """
        Write a DataFrame to a Parquet file.

        Args:
            dataframe:
                DataFrame to write.

            output_file:
                Destination Parquet file.

            compression:
                Parquet compression codec.

        Returns:
            Path to the generated Parquet file.
        """

        if not isinstance(
            dataframe,
            pd.DataFrame,
        ):
            raise TypeError(
                "dataframe must be a pandas DataFrame."
            )

        if not isinstance(
            output_file,
            Path,
        ):
            output_file = Path(
                output_file
            )

        normalized_compression = (
            self.validate_compression(
                compression
            )
        )

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        table = pa.Table.from_pandas(
            dataframe,
            preserve_index=False,
        )

        parquet_compression = (
            None
            if normalized_compression == "none"
            else normalized_compression
        )

        pq.write_table(
            table,
            output_file,
            compression=parquet_compression,
        )

        if not output_file.exists():
            raise RuntimeError(
                "Parquet file was not created: "
                f"{output_file}"
            )

        if output_file.stat().st_size == 0:
            raise RuntimeError(
                "Generated Parquet file is empty: "
                f"{output_file}"
            )

        return output_file

    def validate_parquet(
        self,
        parquet_file: Path,
    ) -> dict[str, Any]:
        """
        Validate a Parquet file and return basic metadata.

        Args:
            parquet_file:
                Parquet file to validate.

        Returns:
            Validation and metadata information.

        Raises:
            FileNotFoundError:
                If the file does not exist.

            ValueError:
                If the file is not a Parquet file.

            RuntimeError:
                If the Parquet file cannot be read.
        """

        parquet_file = Path(
            parquet_file
        )

        if not parquet_file.exists():
            raise FileNotFoundError(
                "Parquet file does not exist: "
                f"{parquet_file}"
            )

        if not parquet_file.is_file():
            raise ValueError(
                "Parquet path is not a file: "
                f"{parquet_file}"
            )

        if parquet_file.suffix.lower() != ".parquet":
            raise ValueError(
                "Expected a .parquet file: "
                f"{parquet_file}"
            )

        if parquet_file.stat().st_size == 0:
            raise RuntimeError(
                "Parquet file is empty: "
                f"{parquet_file}"
            )

        try:
            parquet_file_metadata = (
                pq.ParquetFile(
                    parquet_file
                )
            )

            metadata = (
                parquet_file_metadata.metadata
            )

            schema = (
                parquet_file_metadata.schema_arrow
            )

            return {
                "valid": True,
                "file": str(parquet_file),
                "row_count": (
                    metadata.num_rows
                ),
                "column_count": (
                    metadata.num_columns
                ),
                "row_group_count": (
                    metadata.num_row_groups
                ),
                "schema": schema,
            }

        except Exception as exc:
            raise RuntimeError(
                "Unable to validate Parquet file: "
                f"{parquet_file}"
            ) from exc

    def get_metadata(
        self,
        parquet_file: Path,
    ) -> dict[str, Any]:
        """
        Retrieve Parquet metadata.

        Args:
            parquet_file:
                Parquet file.

        Returns:
            Metadata dictionary.
        """

        validation = (
            self.validate_parquet(
                parquet_file
            )
        )

        return {
            "file": validation["file"],
            "row_count": validation[
                "row_count"
            ],
            "column_count": validation[
                "column_count"
            ],
            "row_group_count": validation[
                "row_group_count"
            ],
        }

    def get_schema(
        self,
        parquet_file: Path,
    ) -> pa.Schema:
        """
        Retrieve the Arrow schema from a Parquet file.

        Args:
            parquet_file:
                Parquet file.

        Returns:
            PyArrow schema.
        """

        parquet_file = Path(
            parquet_file
        )

        if not parquet_file.exists():
            raise FileNotFoundError(
                "Parquet file does not exist: "
                f"{parquet_file}"
            )

        try:
            parquet_file_reader = (
                pq.ParquetFile(
                    parquet_file
                )
            )

            return (
                parquet_file_reader
                .schema_arrow
            )

        except Exception as exc:
            raise RuntimeError(
                "Unable to read Parquet schema: "
                f"{parquet_file}"
            ) from exc

    def read_parquet(
        self,
        parquet_file: Path,
    ) -> pd.DataFrame:
        """
        Read a Parquet file into a pandas DataFrame.

        Args:
            parquet_file:
                Parquet file.

        Returns:
            DataFrame containing Parquet data.
        """

        parquet_file = Path(
            parquet_file
        )

        if not parquet_file.exists():
            raise FileNotFoundError(
                "Parquet file does not exist: "
                f"{parquet_file}"
            )

        try:
            return pd.read_parquet(
                parquet_file
            )

        except Exception as exc:
            raise RuntimeError(
                "Unable to read Parquet dataset: "
                f"{parquet_file}"
            ) from exc

    def get_row_count(
        self,
        parquet_file: Path,
    ) -> int:
        """
        Return the number of rows in a Parquet file.
        """

        metadata = self.get_metadata(
            parquet_file
        )

        return int(
            metadata["row_count"]
        )

    def get_column_count(
        self,
        parquet_file: Path,
    ) -> int:
        """
        Return the number of columns in a Parquet file.
        """

        metadata = self.get_metadata(
            parquet_file
        )

        return int(
            metadata["column_count"]
        )


__all__ = [
    "ParquetService",
]