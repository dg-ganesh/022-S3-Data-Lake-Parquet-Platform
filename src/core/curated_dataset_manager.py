"""
Project : S3 Data Lake + Parquet Platform
Project ID : 022

Curated Dataset Manager
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.config import AppConfig
from src.services.s3_service import S3Service


class CuratedDatasetManager:
    """
    Manage upload and verification of curated datasets
    in Amazon S3.

    Responsibilities:

        Local curated dataset
                ↓
        Build S3 object keys
                ↓
        Remove existing dataset objects
                ↓
        Upload Parquet files
                ↓
        Verify uploaded objects

    This class deliberately delegates all AWS/S3 operations
    to the existing S3Service.
    """

    def __init__(
        self,
        config: AppConfig,
        s3_service: S3Service,
    ) -> None:
        """
        Initialize the curated dataset manager.

        Args:
            config:
                Application configuration.

            s3_service:
                Existing Project 022 S3 service.
        """

        self.config = config
        self.s3_service = s3_service

    def upload_dataset(
        self,
        dataset_directory: Path,
        dataset_name: str,
    ) -> list[str]:
        """
        Upload a local curated Parquet dataset to S3.

        Existing S3 objects belonging to the same dataset
        are removed before the new files are uploaded.

        This makes the dataset upload idempotent.

        Args:
            dataset_directory:
                Local root directory containing Parquet files.

            dataset_name:
                Logical dataset name.

        Returns:
            List of uploaded S3 object keys.
        """

        dataset_directory = Path(
            dataset_directory
        )

        normalized_dataset_name = (
            self._normalize_dataset_name(
                dataset_name
            )
        )

        if not dataset_directory.exists():
            raise FileNotFoundError(
                "Curated dataset directory does not exist: "
                f"{dataset_directory}"
            )

        if not dataset_directory.is_dir():
            raise ValueError(
                "Curated dataset path is not a directory: "
                f"{dataset_directory}"
            )

        parquet_files = self._list_parquet_files(
            dataset_directory
        )

        if not parquet_files:
            raise RuntimeError(
                "No Parquet files found in curated "
                f"dataset: {dataset_directory}"
            )

        # --------------------------------------------------
        # Remove existing S3 objects only for this dataset,
        # then upload the current local Parquet dataset.
        # --------------------------------------------------
        self.s3_service.delete_prefix(
            self._get_dataset_s3_prefix(
                normalized_dataset_name
            )
        )

        uploaded_keys: list[str] = []

        for parquet_file in parquet_files:

            relative_path = (
                parquet_file.relative_to(
                    dataset_directory
                )
            )

            s3_key = self.build_s3_key(
                dataset_name=(
                    normalized_dataset_name
                ),
                relative_path=relative_path,
            )

            self.s3_service.upload_file(
                local_file=parquet_file,
                s3_key=s3_key,
            )

            uploaded_keys.append(
                s3_key
            )

        return uploaded_keys

    def verify_dataset(
        self,
        dataset_directory: Path,
        dataset_name: str,
    ) -> dict[str, Any]:
        """
        Verify that all local Parquet files exist in S3.

        Args:
            dataset_directory:
                Local curated dataset directory.

            dataset_name:
                Logical dataset name.

        Returns:
            Verification summary.
        """

        dataset_directory = Path(
            dataset_directory
        )

        normalized_dataset_name = (
            self._normalize_dataset_name(
                dataset_name
            )
        )

        parquet_files = self._list_parquet_files(
            dataset_directory
        )

        if not parquet_files:
            raise RuntimeError(
                "No Parquet files found for "
                "verification: "
                f"{dataset_directory}"
            )

        verified_keys: list[str] = []
        missing_keys: list[str] = []

        for parquet_file in parquet_files:

            relative_path = (
                parquet_file.relative_to(
                    dataset_directory
                )
            )

            s3_key = self.build_s3_key(
                dataset_name=(
                    normalized_dataset_name
                ),
                relative_path=relative_path,
            )

            if self.s3_service.object_exists(
                s3_key
            ):
                verified_keys.append(
                    s3_key
                )
            else:
                missing_keys.append(
                    s3_key
                )

        if missing_keys:
            raise RuntimeError(
                "Curated dataset S3 verification "
                "failed. Missing objects: "
                f"{missing_keys}"
            )

        return {
            "verified": True,
            "dataset_name": (
                normalized_dataset_name
            ),
            "verified_file_count": len(
                verified_keys
            ),
            "verified_keys": verified_keys,
            "missing_keys": missing_keys,
        }

    def build_s3_key(
        self,
        dataset_name: str,
        relative_path: Path,
    ) -> str:
        """
        Build the S3 key for a curated dataset file.

        Example:

            dataset_name:
                customers

            relative_path:
                part-0.parquet

            result:
                curated/customers/part-0.parquet
        """

        normalized_dataset_name = (
            self._normalize_dataset_name(
                dataset_name
            )
        )

        normalized_relative_path = (
            relative_path.as_posix()
            .lstrip("/")
        )

        if not normalized_relative_path:
            raise ValueError(
                "Relative Parquet path cannot be empty."
            )

        prefix = (
            self.config.s3_curated_prefix
            .strip("/")
        )

        return (
            f"{prefix}/"
            f"{normalized_dataset_name}/"
            f"{normalized_relative_path}"
        )

    def build_s3_uri(
        self,
        dataset_name: str,
        relative_path: Path,
    ) -> str:
        """
        Build a complete S3 URI.

        Example:

            s3://bucket/curated/customers/part-0.parquet
        """

        s3_key = self.build_s3_key(
            dataset_name=dataset_name,
            relative_path=relative_path,
        )

        return (
            f"s3://"
            f"{self.config.s3_bucket_name}/"
            f"{s3_key}"
        )

    def list_s3_dataset_objects(
        self,
        dataset_name: str,
    ) -> list[dict[str, Any]]:
        """
        List objects belonging to a curated dataset.

        Args:
            dataset_name:
                Logical dataset name.

        Returns:
            S3 object metadata.
        """

        return self.s3_service.list_objects(
            prefix=self._get_dataset_s3_prefix(
                dataset_name
            )
        )

    def _get_dataset_s3_prefix(
        self,
        dataset_name: str,
    ) -> str:
        """Return the S3 prefix scoped to one dataset."""
        normalized_dataset_name = (
            self._normalize_dataset_name(
                dataset_name
            )
        )

        curated_prefix = (
            self.config.s3_curated_prefix
            .strip("/")
        )

        return (
            f"{curated_prefix}/"
            f"{normalized_dataset_name}/"
        )

    def _list_parquet_files(
        self,
        dataset_directory: Path,
    ) -> list[Path]:
        """
        Recursively locate Parquet files.
        """

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

    @staticmethod
    def _normalize_dataset_name(
        dataset_name: str,
    ) -> str:
        """
        Normalize and validate a dataset name.
        """

        if not isinstance(
            dataset_name,
            str,
        ):
            raise TypeError(
                "dataset_name must be a string."
            )

        normalized = (
            dataset_name.strip().lower()
        )

        if not normalized:
            raise ValueError(
                "dataset_name cannot be empty."
            )

        if "/" in normalized or "\\" in normalized:
            raise ValueError(
                "dataset_name cannot contain "
                "path separators."
            )

        return normalized


__all__ = [
    "CuratedDatasetManager",
]
