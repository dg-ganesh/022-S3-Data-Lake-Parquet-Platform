"""
Project : S3 Data Lake + Parquet Platform
Project ID : 022

Data Lake Structure Manager
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.config import AppConfig
from src.services.s3_service import S3Service


@dataclass(frozen=True)
class DataLakeStructure:
    """Defines the standard S3 structure for Project 022."""

    raw_prefix: str
    curated_prefix: str
    rejected_prefix: str
    metadata_prefix: str


class DataLakeManager:
    """Manages the foundational S3 data-lake structure."""

    def __init__(
        self,
        config: AppConfig,
        s3_service: S3Service,
    ) -> None:
        """
        Initialize the data-lake manager.

        Args:
            config: Application configuration.
            s3_service: Configured S3 service.
        """
        self._config = config
        self._s3_service = s3_service

        self._structure = DataLakeStructure(
            raw_prefix=config.s3_raw_prefix,
            curated_prefix=config.s3_curated_prefix,
            rejected_prefix=config.s3_rejected_prefix,
            metadata_prefix=config.s3_metadata_prefix,
        )

    @property
    def structure(self) -> DataLakeStructure:
        """Return the configured data-lake structure."""
        return self._structure

    @property
    def bucket_name(self) -> str:
        """Return the data-lake S3 bucket name."""
        return self._config.s3_bucket_name

    def initialize(self) -> dict[str, Any]:
        """
        Initialize the S3 data-lake structure.

        The operation ensures that the configured bucket is
        available and creates the standard data-lake prefixes.

        Returns:
            Initialization result containing bucket and prefix details.

        Raises:
            RuntimeError: If the bucket cannot be initialized.
        """
        bucket_ready = self._s3_service.ensure_bucket()

        if not bucket_ready:
            raise RuntimeError(
                f"Unable to initialize S3 bucket "
                f"'{self.bucket_name}'."
            )

        prefixes = self._get_prefixes()

        created_prefixes: list[str] = []

        for prefix in prefixes:
            s3_uri = self._s3_service.create_prefix(prefix)
            created_prefixes.append(s3_uri)

        return {
            "bucket": self.bucket_name,
            "bucket_ready": True,
            "prefixes": created_prefixes,
            "prefix_count": len(created_prefixes),
        }

    def verify_structure(self) -> dict[str, Any]:
        """
        Verify that the configured data-lake prefixes exist.

        Returns:
            Verification result containing the status of each prefix.
        """
        prefix_status: dict[str, bool] = {}

        for prefix in self._get_prefixes():
            objects = self._s3_service.list_objects(prefix)
            prefix_status[prefix] = bool(objects)

        return {
            "bucket": self.bucket_name,
            "bucket_accessible": self._s3_service.bucket_exists(),
            "prefixes": prefix_status,
            "all_prefixes_available": all(prefix_status.values()),
        }

    def get_s3_uri(self, prefix: str) -> str:
        """
        Build an S3 URI for a configured data-lake prefix.

        Args:
            prefix: Data-lake prefix.

        Returns:
            Complete S3 URI.

        Raises:
            ValueError: If the supplied prefix is not part of
                the configured data-lake structure.
        """
        normalized_prefix = prefix.strip().strip("/")

        configured_prefixes = {
            self._structure.raw_prefix.strip("/"),
            self._structure.curated_prefix.strip("/"),
            self._structure.rejected_prefix.strip("/"),
            self._structure.metadata_prefix.strip("/"),
        }

        if normalized_prefix not in configured_prefixes:
            raise ValueError(
                f"Unknown data-lake prefix: {prefix}"
            )

        return (
            f"s3://{self.bucket_name}/"
            f"{normalized_prefix}/"
        )

    def get_zone_prefixes(self) -> dict[str, str]:
        """
        Return the configured data-lake zones.

        Returns:
            Dictionary mapping zone names to S3 prefixes.
        """
        return {
            "raw": self._structure.raw_prefix,
            "curated": self._structure.curated_prefix,
            "rejected": self._structure.rejected_prefix,
            "metadata": self._structure.metadata_prefix,
        }

    def _get_prefixes(self) -> tuple[str, ...]:
        """
        Return all configured data-lake prefixes.

        Returns:
            Tuple containing the four standard prefixes.
        """
        return (
            self._structure.raw_prefix,
            self._structure.curated_prefix,
            self._structure.rejected_prefix,
            self._structure.metadata_prefix,
        )


__all__ = [
    "DataLakeManager",
    "DataLakeStructure",
]
