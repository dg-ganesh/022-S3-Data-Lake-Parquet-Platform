"""
Project : S3 Data Lake + Parquet Platform
Project ID : 022

Slice 2 - Local Parquet Integration Test
"""

from __future__ import annotations

import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from src.core.parquet_dataset_processor import (
    ParquetDatasetProcessor,
)
from src.services.dataframe_service import (
    DataFrameService,
)
from src.services.dataset_definition_service import (
    DatasetDefinitionService,
)
from src.services.schema_service import (
    SchemaService,
)


PROJECT_ROOT = (
    Path(__file__).resolve().parents[1]
)

INPUT_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "input"
)

TEST_OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "curated_test"
)


def main() -> int:

    print()
    print(
        "PROJECT 022 - SLICE 2 "
        "LOCAL PARQUET TEST"
    )
    print(
        "=" * 55
    )

    dataframe_service = (
        DataFrameService()
    )

    schema_service = (
        SchemaService()
    )

    dataset_definition_service = (
        DatasetDefinitionService()
    )

    parquet_processor = (
        ParquetDatasetProcessor()
    )

    _verify_output_directory_is_replaced(
        parquet_processor
    )

    if TEST_OUTPUT_DIRECTORY.exists():
        shutil.rmtree(
            TEST_OUTPUT_DIRECTORY
        )

    TEST_OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    datasets = [
        "customers",
        "transactions",
    ]

    for dataset_name in datasets:

        print()
        print(
            f"PROCESSING: {dataset_name}"
        )
        print(
            "-" * 55
        )

        source_file = (
            INPUT_DIRECTORY
            / f"{dataset_name}.csv"
        )

        if not source_file.exists():
            raise FileNotFoundError(
                f"Source file not found: "
                f"{source_file}"
            )

        dataframe = (
            dataframe_service.load_file(
                source_file
            )
        )

        print(
            f"Rows loaded     : "
            f"{len(dataframe)}"
        )

        print(
            f"Columns loaded  : "
            f"{len(dataframe.columns)}"
        )

        expected_schema = (
            dataset_definition_service
            .get_expected_schema(
                dataset_name
            )
        )

        schema_result = (
            schema_service.validate_schema(
                dataframe,
                expected_schema,
            )
        )

        if not schema_result.is_valid:
            raise RuntimeError(
                _format_schema_failure(
                    dataset_name,
                    schema_result,
                )
            )

        print(
            "Schema validation: PASS"
        )

        partition_columns = (
            dataset_definition_service
            .get_partition_columns(
                dataset_name
            )
        )

        print(
            "Partition columns: "
            + (
                ", ".join(
                    partition_columns
                )
                if partition_columns
                else "None"
            )
        )

        output_directory = (
            TEST_OUTPUT_DIRECTORY
            / dataset_name
        )

        result = (
            parquet_processor.process(
                dataframe=dataframe,
                output_directory=(
                    output_directory
                ),
                partition_columns=(
                    partition_columns
                ),
                compression="snappy",
            )
        )

        validation = result[
            "validation"
        ]

        print(
            f"Parquet files    : "
            f"{validation['parquet_file_count']}"
        )

        print(
            f"Rows in Parquet  : "
            f"{validation['row_count']}"
        )

        print(
            f"Partitions       : "
            f"{validation['partition_count']}"
        )

        print(
            "Parquet validation: PASS"
        )

        _print_output_tree(
            output_directory
        )

    print()
    print(
        "=" * 55
    )
    print(
        "LOCAL PARQUET TEST SUCCESSFUL"
    )
    print(
        f"Output directory: "
        f"{TEST_OUTPUT_DIRECTORY}"
    )
    print()

    return 0


def _format_schema_failure(
    dataset_name: str,
    result,
) -> str:

    errors = []

    if result.missing_columns:
        errors.append(
            "Missing columns: "
            + ", ".join(
                result.missing_columns
            )
        )

    if result.unexpected_columns:
        errors.append(
            "Unexpected columns: "
            + ", ".join(
                result.unexpected_columns
            )
        )

    if result.type_mismatches:

        mismatches = []

        for column, details in (
            result.type_mismatches.items()
        ):
            mismatches.append(
                f"{column} "
                f"(expected="
                f"{details['expected']}, "
                f"actual="
                f"{details['actual']})"
            )

        errors.append(
            "Type mismatches: "
            + "; ".join(
                mismatches
            )
        )

    return (
        f"Schema validation failed "
        f"for '{dataset_name}': "
        + " | ".join(errors)
    )


def _print_output_tree(
    directory: Path,
) -> None:

    print()
    print(
        f"Output: {directory}"
    )

    for path in sorted(
        directory.rglob("*")
    ):

        relative = path.relative_to(
            directory
        )

        if path.is_dir():
            print(
                f"  [DIR]  {relative}"
            )
        else:
            print(
                f"  [FILE] {relative}"
            )


def _verify_output_directory_is_replaced(
    parquet_processor: ParquetDatasetProcessor,
) -> None:
    """
    Verify that a prior partitioned output is removed
    before new Parquet files are generated.
    """
    with TemporaryDirectory() as temporary_directory:
        output_directory = (
            Path(temporary_directory)
            / "transactions"
        )
        partition_directory = (
            output_directory
            / "transaction_date=old"
        )
        partition_directory.mkdir(parents=True)
        old_file = partition_directory / "old.parquet"
        old_file.write_bytes(b"old parquet data")

        dataframe = pd.DataFrame(
            {
                "transaction_id": ["T-1", "T-2"],
                "transaction_date": [
                    "2026-08-20",
                    "2026-08-21",
                ],
            }
        )

        result = parquet_processor.process(
            dataframe=dataframe,
            output_directory=output_directory,
            partition_columns=["transaction_date"],
            compression="snappy",
        )

        assert not old_file.exists()
        assert result["validation"]["parquet_file_count"] == 2


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
