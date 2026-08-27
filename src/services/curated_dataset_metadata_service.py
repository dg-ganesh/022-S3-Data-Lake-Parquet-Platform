from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class DatasetMetadata:
    dataset_name: str
    description: str
    format: str
    location: str
    partitioned: bool
    partition_columns: tuple[str, ...]
    columns: tuple[str, ...]


class CuratedDatasetMetadataService:
    """
    Provides metadata for curated datasets.

    This service is intentionally read-only. It does not:
    - read or write S3 objects
    - modify Parquet files
    - modify datasets
    - perform queries or aggregations
    """

    def __init__(self, metadata: dict[str, DatasetMetadata] | None = None):
        self._metadata = metadata or {}

    def register_dataset(
        self,
        *,
        dataset_name: str,
        description: str,
        format: str,
        location: str,
        partitioned: bool,
        partition_columns: list[str] | tuple[str, ...],
        columns: list[str] | tuple[str, ...],
    ) -> DatasetMetadata:
        if not dataset_name:
            raise ValueError("dataset_name must not be empty")

        if dataset_name in self._metadata:
            raise ValueError(
                f"Dataset metadata already exists: {dataset_name}"
            )

        metadata = DatasetMetadata(
            dataset_name=dataset_name,
            description=description,
            format=format,
            location=location,
            partitioned=partitioned,
            partition_columns=tuple(partition_columns),
            columns=tuple(columns),
        )

        self._metadata[dataset_name] = metadata
        return metadata

    def get_metadata(self, dataset_name: str) -> DatasetMetadata:
        if dataset_name not in self._metadata:
            raise KeyError(
                f"Dataset metadata not found: {dataset_name}"
            )

        return self._metadata[dataset_name]

    def list_datasets(self) -> list[str]:
        return sorted(self._metadata.keys())

    def get_metadata_dict(self, dataset_name: str) -> dict[str, Any]:
        return asdict(self.get_metadata(dataset_name))
    