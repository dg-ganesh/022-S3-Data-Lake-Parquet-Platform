"""
Project : S3 Data Lake + Parquet Platform
Project ID : 022

Dataset Definition Service
"""

from __future__ import annotations

from pathlib import Path

from src.dataset_config.dataset_definitions import (
    DatasetDefinition,
    get_dataset_definition,
)


class DatasetDefinitionService:
    """
    Provides controlled access to dataset definitions.
    """

    def get_definition(
        self,
        dataset_name: str,
    ) -> DatasetDefinition:
        """
        Retrieve a dataset definition.

        Args:
            dataset_name:
                Dataset name.

        Returns:
            DatasetDefinition.

        Raises:
            ValueError:
                If the dataset is not configured.
        """
        return get_dataset_definition(
            dataset_name
        )

    def validate_source_file(
        self,
        dataset_name: str,
        source_file: Path,
    ) -> None:
        """
        Validate that a source file is supported
        for the specified dataset.

        Args:
            dataset_name:
                Dataset name.

            source_file:
                Source file.

        Raises:
            ValueError:
                If the file format is unsupported.
        """
        definition = self.get_definition(
            dataset_name
        )

        extension = (
            source_file.suffix.lower()
        )

        if extension not in definition.source_formats:
            raise ValueError(
                "Unsupported source format for "
                f"dataset '{definition.name}': "
                f"{extension}. "
                "Supported formats: "
                f"{', '.join(definition.source_formats)}"
            )

    def get_expected_schema(
        self,
        dataset_name: str,
    ) -> dict[str, str]:
        """
        Return the expected schema.

        Args:
            dataset_name:
                Dataset name.

        Returns:
            Expected schema.
        """
        definition = self.get_definition(
            dataset_name
        )

        return dict(
            definition.expected_schema
        )

    def get_partition_columns(
        self,
        dataset_name: str,
    ) -> list[str]:
        """
        Return configured partition columns.

        Args:
            dataset_name:
                Dataset name.

        Returns:
            Partition column list.
        """
        definition = self.get_definition(
            dataset_name
        )

        return list(
            definition.partition_columns
        )

    def is_partitioned(
        self,
        dataset_name: str,
    ) -> bool:
        """
        Determine whether a dataset is configured
        for partitioned storage.

        Args:
            dataset_name:
                Dataset name.

        Returns:
            True when partition columns exist.
        """
        return bool(
            self.get_partition_columns(
                dataset_name
            )
        )


__all__ = [
    "DatasetDefinitionService",
]