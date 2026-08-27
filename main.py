"""
Project : S3 Data Lake + Parquet Platform
Project ID : 022

Application Entry Point
"""

from __future__ import annotations

from pathlib import Path

from src.config import AppConfig, get_config
from src.core.curated_pipeline_runner import (
    CuratedPipelineRunner,
)
from src.core.data_lake_manager import (
    DataLakeManager,
)
from src.core.raw_data_ingestor import (
    RawDataIngestor,
)
from src.services.execution_report_service import (
    ExecutionReportService,
)
from src.services.s3_service import S3Service


def main() -> int:
    """
    Execute Project 022 end-to-end.

    Flow:

        Configuration
             ↓
        S3 connectivity
             ↓
        Data Lake initialization
             ↓
        Raw data ingestion
             ↓
        Curated processing
             ↓
        Parquet generation
             ↓
        Curated S3 upload
             ↓
        Verification
             ↓
        Execution report
    """

    config: AppConfig | None = None
    report_service: (
        ExecutionReportService | None
    ) = None

    try:

        # ===============================================================
        # 1. Load configuration
        # ===============================================================

        config = get_config()

        report_service = ExecutionReportService(
            log_directory=config.log_directory,
            application_version=(
                config.application_version
            ),
        )

        report_service.start_execution()

        report_service.record_checkpoint(
            "Application configuration loaded"
        )

        # ===============================================================
        # 2. Initialize S3
        # ===============================================================

        s3_service = S3Service(
            bucket_name=config.s3_bucket_name,
            region_name=config.aws_region,
        )

        s3_service.check_connection()

        report_service.record_checkpoint(
            "S3 connectivity verified"
        )

        # ===============================================================
        # 3. Initialize Data Lake
        # ===============================================================

        data_lake_manager = DataLakeManager(
            config=config,
            s3_service=s3_service,
        )

        initialization_result = (
            data_lake_manager.initialize()
        )

        report_service.record_checkpoint(
            "Data lake structure initialized"
        )

        # Verify actual structure status.
        structure_status = (
            data_lake_manager.verify_structure()
        )

        if not structure_status[
            "all_prefixes_available"
        ]:
            raise RuntimeError(
                "Data lake structure verification failed."
            )

        report_service.record_checkpoint(
            "Data lake structure verified"
        )

        # ===============================================================
        # 4. Raw Data Ingestion
        # ===============================================================

        raw_ingestor = RawDataIngestor(
            config=config,
            s3_service=s3_service,
        )

        input_files = (
            raw_ingestor.discover_input_files()
        )

        report_service.record_checkpoint(
            "Input discovery completed: "
            f"{len(input_files)} file(s) found"
        )

        ingestion_results = (
            raw_ingestor.ingest_all(
                skip_existing=True,
            )
        )

        ingestion_summary = (
            raw_ingestor.get_ingestion_summary(
                ingestion_results
            )
        )

        report_service.record_checkpoint(
            "Raw data ingestion completed"
        )

        # ===============================================================
        # 5. Discover Curated Datasets
        # ===============================================================

        curated_datasets = (
            _discover_curated_datasets(
                config
            )
        )

        report_service.record_checkpoint(
            "Curated dataset discovery completed: "
            f"{len(curated_datasets)} dataset(s) found"
        )

        # ===============================================================
        # 6. Curated Processing
        # ===============================================================

        curated_summary = {
            "successful": True,
            "dataset_count": 0,
            "successful_count": 0,
            "failed_count": 0,
            "results": {},
            "failures": {},
        }

        if curated_datasets:

            curated_runner = (
                CuratedPipelineRunner(
                    config=config
                )
            )

            curated_summary = (
                curated_runner.run(
                    curated_datasets
                )
            )

            if not curated_summary[
                "successful"
            ]:
                raise RuntimeError(
                    "Curated pipeline execution failed."
                )

            report_service.record_checkpoint(
                "Curated Parquet processing completed"
            )

        else:

            report_service.record_checkpoint(
                "No curated datasets discovered"
            )

        # ===============================================================
        # 7. Complete Execution
        # ===============================================================

        report_service.complete_execution(
            status="PASS"
        )

        _print_execution_summary(
            config=config,
            initialization_result=(
                initialization_result
            ),
            ingestion_summary=(
                ingestion_summary
            ),
            curated_summary=(
                curated_summary
            ),
        )

        return 0

    except Exception as exc:

        if report_service is not None:

            try:

                report_service.record_failure(
                    checkpoint="Application execution",
                    error=exc,
                )

                report_service.complete_execution(
                    status="FAIL"
                )

            except Exception:
                pass

        print()
        print(
            "PROJECT 022 EXECUTION FAILED"
        )
        print(
            "========================================"
        )
        print(
            f"Error: {exc}"
        )

        if report_service is not None:

            print(
                "Execution report: "
                f"{report_service.report_path}"
            )

        return 1


def _discover_curated_datasets(
    config: AppConfig,
) -> dict[str, Path]:
    """
    Discover supported source files that correspond
    to configured dataset definitions.
    """

    input_directory = Path(
        config.input_directory
    )

    if not input_directory.exists():
        raise FileNotFoundError(
            "Input directory does not exist: "
            f"{input_directory}"
        )

    if not input_directory.is_dir():
        raise NotADirectoryError(
            "Input path is not a directory: "
            f"{input_directory}"
        )

    supported_extensions = {
        ".csv",
        ".json",
        ".jsonl",
    }

    datasets: dict[str, Path] = {}

    for file_path in sorted(
        input_directory.iterdir(),
        key=lambda path: path.name.lower(),
    ):

        if not file_path.is_file():
            continue

        if (
            file_path.suffix.lower()
            not in supported_extensions
        ):
            continue

        dataset_name = (
            file_path.stem.strip().lower()
        )

        if not dataset_name:
            continue

        datasets[dataset_name] = file_path

    return datasets


def _print_execution_summary(
    config: AppConfig,
    initialization_result: dict,
    ingestion_summary: dict[str, int],
    curated_summary: dict,
) -> None:
    """
    Display the final application execution summary.
    """

    print()
    print(
        "PROJECT 022 EXECUTION SUCCESSFUL"
    )
    print(
        "========================================"
    )

    print(
        f"Project     : {config.project_name}"
    )

    print(
        f"Project ID  : {config.project_id}"
    )

    print(
        f"Version     : "
        f"{config.application_version}"
    )

    print(
        f"Environment : "
        f"{config.environment}"
    )

    print(
        f"AWS Region  : "
        f"{config.aws_region}"
    )

    print(
        f"S3 Bucket   : "
        f"{config.s3_bucket_name}"
    )

    print()
    print(
        "DATA LAKE INITIALIZATION"
    )
    print(
        "----------------------------------------"
    )

    print(
        f"Bucket ready    : "
        f"{initialization_result['bucket_ready']}"
    )

    print(
        f"Prefixes created: "
        f"{initialization_result['prefix_count']}"
    )

    print()
    print(
        "RAW INGESTION SUMMARY"
    )
    print(
        "----------------------------------------"
    )

    print(
        f"Files found     : "
        f"{ingestion_summary['total_files']}"
    )

    print(
        f"Files uploaded  : "
        f"{ingestion_summary['uploaded_files']}"
    )

    print(
        f"Files skipped    : "
        f"{ingestion_summary['skipped_files']}"
    )

    print(
        f"Bytes processed : "
        f"{ingestion_summary['total_bytes']}"
    )

    print()
    print(
        "CURATED SUMMARY"
    )
    print(
        "----------------------------------------"
    )

    print(
        f"Datasets found  : "
        f"{curated_summary['dataset_count']}"
    )

    print(
        f"Datasets passed : "
        f"{curated_summary['successful_count']}"
    )

    print(
        f"Datasets failed : "
        f"{curated_summary['failed_count']}"
    )

    print()
    print(
        "Execution report: "
        f"{config.log_directory / 'execution_report.txt'}"
    )


if __name__ == "__main__":
    raise SystemExit(
        main()
    )