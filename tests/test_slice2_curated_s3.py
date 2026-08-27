"""
Project : S3 Data Lake + Parquet Platform
Project ID : 022

Slice 2 - Curated S3 Integration Test
"""

from __future__ import annotations

from pathlib import Path

from src.config import get_config
from src.core.curated_pipeline import CuratedPipeline


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_DIRECTORY = PROJECT_ROOT / "data" / "input"

EXPECTED_S3_FILE_COUNTS = {
    "customers": 1,
    "transactions": 5,
}


def process_dataset(
    pipeline: CuratedPipeline,
    dataset_name: str,
) -> dict[str, object]:
    """
    Process one input dataset through the complete
    curated pipeline and return the execution result.
    """

    source_file = (
        INPUT_DIRECTORY
        / f"{dataset_name}.csv"
    )

    print()
    print(f"PROCESSING: {dataset_name}")
    print("-" * 55)

    result = pipeline.process_dataset(
        source_file=source_file,
        dataset_name=dataset_name,
    )

    print(
        f"Rows processed   : "
        f"{result['row_count']}"
    )

    print(
        f"Columns processed: "
        f"{result['column_count']}"
    )

    print(
        f"Partitioned      : "
        f"{result['partitioned']}"
    )

    print(
        f"Parquet output   : "
        f"{result['output_directory']}"
    )

    print(
        f"Uploaded files   : "
        f"{len(result['uploaded_files'])}"
    )

    print(
        f"S3 URI           : "
        f"{result['s3_uri']}"
    )

    print(
        f"S3 verification  : "
        f"{result['s3_verified']}"
    )

    if not result["schema_validated"]:
        raise RuntimeError(
            f"Schema validation failed: "
            f"{dataset_name}"
        )

    if not result["s3_verified"]["verified"]:
        raise RuntimeError(
            f"S3 verification failed: "
            f"{dataset_name}"
        )

    print("RESULT           : PASS")

    return result


def assert_s3_file_count(
    pipeline: CuratedPipeline,
    dataset_name: str,
) -> None:
    """
    Confirm that the dataset prefix contains only
    the newly uploaded Parquet files.
    """
    objects = (
        pipeline.curated_manager
        .list_s3_dataset_objects(
            dataset_name
        )
    )

    expected_count = EXPECTED_S3_FILE_COUNTS[
        dataset_name
    ]

    if len(objects) != expected_count:
        raise RuntimeError(
            "Unexpected S3 object count for "
            f"'{dataset_name}': expected "
            f"{expected_count}, found "
            f"{len(objects)}."
        )


def main() -> None:
    """
    Execute the Slice 2 curated S3 integration test.
    """

    print()
    print(
        "PROJECT 022 - SLICE 2 "
        "CURATED S3 INTEGRATION TEST"
    )
    print("=" * 60)

    config = get_config()

    print()
    print(f"S3 Bucket : {config.s3_bucket_name}")
    print(f"AWS Region: {config.aws_region}")
    print(
        f"Curated Prefix: "
        f"{config.s3_curated_prefix}"
    )

    if not INPUT_DIRECTORY.exists():
        raise FileNotFoundError(
            "Input directory does not exist: "
            f"{INPUT_DIRECTORY}"
        )

    pipeline = CuratedPipeline(
        config=config,
    )

    results: list[dict[str, object]] = []

    for run_number in range(1, 3):
        print()
        print(f"PIPELINE RUN: {run_number}")
        print("-" * 60)

        results = []

        for dataset_name in (
            "customers",
            "transactions",
        ):
            results.append(
                process_dataset(
                    pipeline=pipeline,
                    dataset_name=dataset_name,
                )
            )

            assert_s3_file_count(
                pipeline,
                dataset_name,
            )

    print()
    print("=" * 60)
    print(
        "SLICE 2 CURATED S3 "
        "INTEGRATION TEST SUCCESSFUL"
    )
    print("=" * 60)

    print()
    print("DATASETS PROCESSED")
    print("-" * 60)

    for result in results:
        print(
            f"{result['dataset_name']}: "
            f"{result['row_count']} rows | "
            f"{len(result['uploaded_files'])} "
            f"files uploaded | "
            f"S3 verification PASS"
        )

    print()
    print("S3 CURATED LOCATION")
    print("-" * 60)

    for result in results:
        print(result["s3_uri"])


if __name__ == "__main__":
    main()
