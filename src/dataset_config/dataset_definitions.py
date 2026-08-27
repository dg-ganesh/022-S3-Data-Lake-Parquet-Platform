"""
Project : S3 Data Lake + Parquet Platform
Project ID : 022

Dataset Definitions
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DatasetDefinition:
    """
    Defines the processing rules for one dataset.
    """

    name: str
    source_formats: tuple[str, ...]
    expected_schema: dict[str, str]
    partition_columns: tuple[str, ...]


DATASET_DEFINITIONS: dict[str, DatasetDefinition] = {
    "customers": DatasetDefinition(
        name="customers",
        source_formats=(
            ".csv",
            ".json",
            ".jsonl",
        ),
        expected_schema={
            "customer_id": "int64",
            "name": "string",
            "city": "string",
            "registration_date": "string",
        },
        partition_columns=(),
    ),

    "transactions": DatasetDefinition(
        name="transactions",
        source_formats=(
            ".csv",
            ".json",
            ".jsonl",
        ),
        expected_schema={
            "transaction_id": "string",
            "customer_id": "int64",
            "amount": "float64",
            "transaction_date": "string",
        },
        partition_columns=(
            "transaction_date",
        ),
    ),

    "olist_order_items_dataset": DatasetDefinition(
        name="olist_order_items_dataset",
        source_formats=(
            ".csv",
        ),
        expected_schema={
            "order_id": "string",
            "order_item_id": "int64",
            "product_id": "string",
            "seller_id": "string",
            "shipping_limit_date": "string",
            "price": "float64",
            "freight_value": "float64",
        },
        partition_columns=(),
    ),
}


def get_dataset_definition(
    dataset_name: str,
) -> DatasetDefinition:
    """
    Retrieve the definition for a dataset.

    Args:
        dataset_name:
            Dataset name.

    Returns:
        DatasetDefinition.

    Raises:
        ValueError:
            If the dataset is not configured.
    """

    normalized_name = (
        dataset_name.strip().lower()
    )

    if not normalized_name:
        raise ValueError(
            "Dataset name cannot be empty."
        )

    try:
        return DATASET_DEFINITIONS[
            normalized_name
        ]
    except KeyError as exc:
        raise ValueError(
            f"Dataset is not configured: "
            f"{normalized_name}"
        ) from exc


def get_expected_schema(
    dataset_name: str,
) -> dict[str, str]:
    """
    Return the expected schema for a dataset.
    """

    definition = get_dataset_definition(
        dataset_name
    )

    return dict(
        definition.expected_schema
    )


def get_partition_columns(
    dataset_name: str,
) -> list[str]:
    """
    Return the configured partition columns
    for a dataset.
    """

    definition = get_dataset_definition(
        dataset_name
    )

    return list(
        definition.partition_columns
    )


def is_supported_source_format(
    dataset_name: str,
    file_extension: str,
) -> bool:
    """
    Determine whether a source file format is
    supported for the dataset.
    """

    definition = get_dataset_definition(
        dataset_name
    )

    normalized_extension = (
        file_extension.strip().lower()
    )

    return (
        normalized_extension
        in definition.source_formats
    )


__all__ = [
    "DATASET_DEFINITIONS",
    "DatasetDefinition",
    "get_dataset_definition",
    "get_expected_schema",
    "get_partition_columns",
    "is_supported_source_format",
]