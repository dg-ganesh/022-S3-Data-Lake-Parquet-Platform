"""
Project : S3 Data Lake + Parquet Platform
Project ID : 022

Curated Dataset Reader
"""

from __future__ import annotations

from io import BytesIO
from urllib.parse import unquote

import pandas as pd

from src.config import AppConfig
from src.services.s3_service import S3Service


class CuratedDatasetReader:
    """Read curated Parquet datasets from the S3 data lake."""

    def __init__(
        self,
        config: AppConfig,
        s3_service: S3Service | None = None,
    ) -> None:
        """Initialize the reader with project S3 configuration."""
        self.config = config
        self.s3_service = (
            s3_service
            or S3Service(
                bucket_name=config.s3_bucket_name,
                region_name=config.aws_region,
            )
        )

    def read_dataset(
        self,
        dataset_name: str,
    ) -> pd.DataFrame:
        """Return all curated Parquet data for one dataset."""
        normalized_dataset_name = (
            self._normalize_dataset_name(dataset_name)
        )
        dataset_prefix = self._get_dataset_prefix(
            normalized_dataset_name
        )

        parquet_keys = sorted(
            str(object_metadata["Key"])
            for object_metadata in self.s3_service.list_objects(
                prefix=dataset_prefix
            )
            if (
                object_metadata.get("Key")
                and str(object_metadata["Key"]).lower().endswith(
                    ".parquet"
                )
            )
        )

        if not parquet_keys:
            raise FileNotFoundError(
                "Curated dataset does not exist in S3: "
                f"{normalized_dataset_name}"
            )

        dataframes = [
            self._read_parquet_object(
                s3_key,
                dataset_prefix,
            )
            for s3_key in parquet_keys
        ]

        return pd.concat(
            dataframes,
            ignore_index=True,
        )

    def _read_parquet_object(
        self,
        s3_key: str,
        dataset_prefix: str,
    ) -> pd.DataFrame:
        """Read one Parquet object and restore path partitions."""
        dataframe = pd.read_parquet(
            BytesIO(
                self.s3_service.get_object_bytes(s3_key)
            )
        )

        relative_key = s3_key.removeprefix(
            dataset_prefix
        )

        for path_component in relative_key.split("/")[:-1]:
            if "=" not in path_component:
                continue

            column_name, value = path_component.split(
                "=",
                maxsplit=1,
            )

            if column_name not in dataframe.columns:
                dataframe[unquote(column_name)] = unquote(value)

        return dataframe

    def _get_dataset_prefix(
        self,
        dataset_name: str,
    ) -> str:
        """Return the curated S3 prefix for one dataset."""
        curated_prefix = self.config.s3_curated_prefix.strip(
            "/"
        )

        return f"{curated_prefix}/{dataset_name}/"

    @staticmethod
    def _normalize_dataset_name(
        dataset_name: str,
    ) -> str:
        """Normalize and validate a logical dataset name."""
        if not isinstance(dataset_name, str):
            raise TypeError("dataset_name must be a string.")

        normalized_dataset_name = dataset_name.strip().lower()

        if not normalized_dataset_name:
            raise ValueError("dataset_name cannot be empty.")

        if "/" in normalized_dataset_name or "\\" in normalized_dataset_name:
            raise ValueError(
                "dataset_name cannot contain path separators."
            )

        return normalized_dataset_name


__all__ = [
    "CuratedDatasetReader",
]
