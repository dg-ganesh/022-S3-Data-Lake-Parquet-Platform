from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class LineageRecord:
    dataset_name: str
    source: str
    processing_step: str
    output_location: str


class DatasetLineageService:
    """
    In-memory registry for dataset lineage.

    This service records where a dataset came from and
    which processing step produced it.

    It does not:
    - access S3
    - read/write Parquet
    - execute pipeline processing
    - modify datasets
    """

    def __init__(
        self,
        records: dict[str, LineageRecord] | None = None,
    ) -> None:
        self._records = records or {}

    def register_lineage(
        self,
        *,
        dataset_name: str,
        source: str,
        processing_step: str,
        output_location: str,
    ) -> LineageRecord:

        if not dataset_name:
            raise ValueError(
                "dataset_name must not be empty"
            )

        if dataset_name in self._records:
            raise ValueError(
                f"Lineage already exists: {dataset_name}"
            )

        if not source:
            raise ValueError("source must not be empty")

        if not processing_step:
            raise ValueError(
                "processing_step must not be empty"
            )

        if not output_location:
            raise ValueError(
                "output_location must not be empty"
            )

        record = LineageRecord(
            dataset_name=dataset_name,
            source=source,
            processing_step=processing_step,
            output_location=output_location,
        )

        self._records[dataset_name] = record

        return record

    def get_lineage(
        self,
        dataset_name: str,
    ) -> LineageRecord:

        if dataset_name not in self._records:
            raise KeyError(
                f"Lineage not found: {dataset_name}"
            )

        return self._records[dataset_name]

    def list_datasets(self) -> list[str]:
        return sorted(self._records.keys())

    def as_dict(
        self,
        dataset_name: str,
    ) -> dict[str, Any]:

        return asdict(
            self.get_lineage(dataset_name)
        )