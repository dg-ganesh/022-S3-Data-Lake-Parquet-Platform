"""
Project : S3 Data Lake + Parquet Platform
Project ID : 022

Curated Dataset Manager
"""

from __future__ import annotations

from pathlib import Path

from src.services.s3_service import S3Service


class CuratedDatasetManager:
    """
    Manages curated dataset locations and uploads
    partitioned Parquet datasets to Amazon S3.
    """

    def __init__(
        self,
        s3_service: S3Service | None = None,
        bucket_name: str | None = None,
        curated_prefix: str = "curated",
    ) -> None:
        """
        Initialize the curated dataset manager.

        Args:
            s3_service: Existing S3 service from Slice 1.
            bucket_name: Target S3 bucket.
            curated_prefix: Root prefix for curated datasets.
        """
        self.s3_service = (
            s3_service or S3Service()
        )

        self.bucket_name = bucket_name
        self.curated_prefix = (
            curated_prefix.strip("/")
        )

    def build_dataset_prefix(
        self,
        dataset_name: str,
    ) -> str:
        """
        Build the S3 prefix for a curated dataset.

        Args:
            dataset_name: Name of the dataset.

        Returns:
            Curated S3 prefix.

        Raises:
            ValueError: If dataset name is invalid.
        """
        normalized_name = dataset_name.strip("/")

        if not normalized_name:
            raise ValueError(
                "Dataset name cannot be empty."
            )

        return (
            f"{self.curated_prefix}/"
            f"{normalized_name}/"
        )

    def build_s3_uri(
        self,
        dataset_name: str,
    ) -> str:
        """
        Build the S3 URI for a curated dataset.

        Args:
            dataset_name: Name of the dataset.

        Returns:
            S3 URI.

        Raises:
            ValueError: If bucket name is unavailable.
        """
        if not self.bucket_name:
            raise ValueError(
                "S3 bucket name is required."
            )

        prefix = self.build_dataset_prefix(
            dataset_name
        )

        return (
            f"s3://{self.bucket_name}/"
            f"{prefix}"
        )

    def upload_dataset(
        self,
        local_dataset_directory: Path,
        dataset_name: str,
    ) -> int:
        """
        Upload a local partitioned Parquet dataset
        to the curated S3 prefix.

        Args:
            local_dataset_directory:
                Local partitioned dataset directory.
            dataset_name:
                Curated dataset name.

        Returns:
            Number of uploaded files.

        Raises:
            FileNotFoundError: If local dataset does not exist.
            ValueError: If bucket or dataset is invalid.
        """
        if not self.bucket_name:
            raise ValueError(
                "S3 bucket name is required."
            )

        if not local_dataset_directory.exists():
            raise FileNotFoundError(
                "Curated dataset directory does not exist: "
                f"{local_dataset_directory}"
            )

        if not local_dataset_directory.is_dir():
            raise ValueError(
                "Curated dataset path is not a directory: "
                f"{local_dataset_directory}"
            )

        parquet_files = sorted(
            local_dataset_directory.rglob(
                "*.parquet"
            )
        )

        if not parquet_files:
            raise ValueError(
                "No Parquet files found in curated "
                f"dataset: {local_dataset_directory}"
            )

        dataset_prefix = self.build_dataset_prefix(
            dataset_name
        )

        uploaded_count = 0

        for parquet_file in parquet_files:
            relative_path = (
                parquet_file.relative_to(
                    local_dataset_directory
                )
            )

            s3_key = (
                f"{dataset_prefix}"
                f"{relative_path.as_posix()}"
            )

            self.s3_service.upload_file(
                local_file=parquet_file,
                bucket_name=self.bucket_name,
                object_key=s3_key,
            )

            uploaded_count += 1

        return uploaded_count

    def list_curated_objects(
        self,
        dataset_name: str,
    ) -> list[str]:
        """
        List objects belonging to a curated dataset.

        Args:
            dataset_name: Curated dataset name.

        Returns:
            List of S3 object keys.
        """
        if not self.bucket_name:
            raise ValueError(
                "S3 bucket name is required."
            )

        prefix = self.build_dataset_prefix(
            dataset_name
        )

        return self.s3_service.list_objects(
            bucket_name=self.bucket_name,
            prefix=prefix,
        )

    def verify_dataset(
        self,
        dataset_name: str,
    ) -> bool:
        """
        Verify that the curated dataset exists in S3.

        Args:
            dataset_name: Curated dataset name.

        Returns:
            True when at least one object exists.
        """
        objects = self.list_curated_objects(
            dataset_name
        )

        parquet_objects = [
            key
            for key in objects
            if key.lower().endswith(".parquet")
        ]

        return bool(parquet_objects)

    def get_dataset_summary(
        self,
        dataset_name: str,
    ) -> dict[str, object]:
        """
        Return basic information about a curated
        S3 dataset.

        Args:
            dataset_name: Curated dataset name.

        Returns:
            Curated dataset summary.
        """
        objects = self.list_curated_objects(
            dataset_name
        )

        parquet_objects = [
            key
            for key in objects
            if key.lower().endswith(".parquet")
        ]

        return {
            "dataset_name": dataset_name,
            "s3_uri": self.build_s3_uri(
                dataset_name
            ),
            "object_count": len(objects),
            "parquet_file_count": len(
                parquet_objects
            ),
            "objects": objects,
        }


__all__ = [
    "CuratedDatasetManager",
]
