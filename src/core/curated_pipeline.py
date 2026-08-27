"""
Project : S3 Data Lake + Parquet Platform
Project ID : 022

Curated Data Pipeline
"""

from __future__ import annotations

from pathlib import Path

from src.config import AppConfig
from src.core.curated_dataset_manager import (
    CuratedDatasetManager,
)
from src.core.parquet_dataset_processor import (
    ParquetDatasetProcessor,
)
from src.services.dataframe_service import (
    DataFrameService,
)
from src.services.curated_pipeline_report_service import (
    CuratedPipelineReportService,
)
from src.services.dataset_definition_service import (
    DatasetDefinitionService,
)
from src.services.s3_service import S3Service
from src.services.schema_service import (
    SchemaService,
)


class CuratedPipeline:
    """
    Execute the complete curated-data processing flow.

    Flow:

        Source Dataset
             ↓
        Dataset Definition
             ↓
        DataFrame Loading
             ↓
        Schema Validation
             ↓
        Parquet Generation
             ↓
        Parquet Validation
             ↓
        S3 Curated Upload
             ↓
        S3 Verification
    """

    def __init__(
        self,
        config: AppConfig,
        dataframe_service: DataFrameService | None = None,
        schema_service: SchemaService | None = None,
        dataset_definition_service: (
            DatasetDefinitionService | None
        ) = None,
        parquet_processor: (
            ParquetDatasetProcessor | None
        ) = None,
        s3_service: S3Service | None = None,
        curated_manager: (
            CuratedDatasetManager | None
        ) = None,
        report_service: (
            CuratedPipelineReportService | None
        ) = None,
    ) -> None:
        """
        Initialize the curated pipeline.
        """

        self.config = config
        self.report_service = report_service

        self.dataframe_service = (
            dataframe_service
            or DataFrameService()
        )

        self.schema_service = (
            schema_service
            or SchemaService()
        )

        self.dataset_definition_service = (
            dataset_definition_service
            or DatasetDefinitionService()
        )

        self.parquet_processor = (
            parquet_processor
            or ParquetDatasetProcessor()
        )

        self.s3_service = (
            s3_service
            or S3Service(
                bucket_name=config.s3_bucket_name,
                region_name=config.aws_region,
            )
        )

        self.curated_manager = (
            curated_manager
            or CuratedDatasetManager(
                config=config,
                s3_service=self.s3_service,
            )
        )

    def process_dataset(
        self,
        source_file: Path,
        dataset_name: str,
    ) -> dict[str, object]:
        """
        Process one configured dataset through
        the complete curated pipeline.
        """

        source_file = Path(source_file)

        normalized_dataset_name = (
            dataset_name.strip().lower()
        )

        if not normalized_dataset_name:
            raise ValueError(
                "Dataset name cannot be empty."
            )

        if self.report_service is not None:
            self.report_service.record_dataset_started(
                normalized_dataset_name
            )

        try:

            self._validate_source_path(
                source_file
            )

        # ---------------------------------------------------------------
        # 1. Retrieve dataset definition
        # ---------------------------------------------------------------

            definition = (
                self.dataset_definition_service
                .get_definition(
                    normalized_dataset_name
                )
            )

            if self.report_service is not None:
                self.report_service.record_dataset_definition_loaded(
                    normalized_dataset_name
                )

        # ---------------------------------------------------------------
        # 2. Validate source file format
        # ---------------------------------------------------------------

            self.dataset_definition_service.validate_source_file(
                normalized_dataset_name,
                source_file,
            )

        # ---------------------------------------------------------------
        # 3. Load source dataset
        # ---------------------------------------------------------------

            dataframe = (
                self.dataframe_service.load_file(
                    source_file
                )
            )

            if self.report_service is not None:
                self.report_service.record_source_loaded(
                    normalized_dataset_name,
                    len(dataframe),
                )

        # ---------------------------------------------------------------
        # 4. Validate schema
        # ---------------------------------------------------------------

            expected_schema = (
                self.dataset_definition_service
                .get_expected_schema(
                    normalized_dataset_name
                )
            )

            schema_result = (
                self.schema_service.validate_schema(
                    dataframe,
                    expected_schema,
                )
            )

            if not schema_result.is_valid:
                raise ValueError(
                    self._format_schema_error(
                        schema_result
                    )
                )

            if self.report_service is not None:
                self.report_service.record_schema_validated(
                    normalized_dataset_name
                )

        # ---------------------------------------------------------------
        # 5. Determine partition strategy
        # ---------------------------------------------------------------

            partition_columns = (
                self.dataset_definition_service
                .get_partition_columns(
                    normalized_dataset_name
                )
            )

        # ---------------------------------------------------------------
        # 6. Generate and validate Parquet dataset
        # ---------------------------------------------------------------

            output_directory = (
                self.config.curated_output_directory
                / normalized_dataset_name
            )

            parquet_result = (
                self.parquet_processor.process(
                    dataframe=dataframe,
                    output_directory=output_directory,
                    partition_columns=partition_columns,
                    compression=(
                        self.config.parquet_compression
                    ),
                )
            )

            if self.report_service is not None:
                self.report_service.record_parquet_generated(
                    normalized_dataset_name,
                    parquet_result["generation"][
                        "parquet_file_count"
                    ],
                )
                self.report_service.record_parquet_verified(
                    normalized_dataset_name
                )

        # ---------------------------------------------------------------
        # 7. Upload curated dataset to S3
        # ---------------------------------------------------------------

            uploaded_files = (
                self.curated_manager.upload_dataset(
                    dataset_directory=output_directory,
                    dataset_name=normalized_dataset_name,
                )
            )

            if self.report_service is not None:
                self.report_service.record_curated_upload(
                    normalized_dataset_name,
                    len(uploaded_files),
                )

        # ---------------------------------------------------------------
        # 8. Verify S3 dataset
        # ---------------------------------------------------------------

            verification_result = (
                self.curated_manager.verify_dataset(
                    dataset_directory=output_directory,
                    dataset_name=normalized_dataset_name,
                )
            )

            if not verification_result["verified"]:
                raise RuntimeError(
                    "Curated dataset upload could not "
                    "be verified in S3: "
                    f"{normalized_dataset_name}"
                )

            if self.report_service is not None:
                self.report_service.record_curated_verification(
                    normalized_dataset_name
                )
                self.report_service.record_dataset_completed(
                    normalized_dataset_name
                )

        # ---------------------------------------------------------------
        # 9. Return execution summary
        # ---------------------------------------------------------------

            return {
                "dataset_name": (
                    normalized_dataset_name
                ),
                "source_file": str(
                    source_file
                ),
                "source_format": (
                    source_file.suffix.lower()
                ),
                "output_directory": str(
                    output_directory
                ),
                "s3_uri": (
                    self.curated_manager.build_s3_uri(
                        dataset_name=normalized_dataset_name,
                        relative_path=Path("."),
                    )
                    if False
                    else (
                        f"s3://"
                        f"{self.config.s3_bucket_name}/"
                        f"{self.config.s3_curated_prefix.strip('/')}/"
                        f"{normalized_dataset_name}/"
                    )
                ),
                "row_count": len(dataframe),
                "column_count": len(
                    dataframe.columns
                ),
                "columns": [
                    str(column)
                    for column in dataframe.columns
                ],
                "schema_validated": True,
                "partitioned": bool(
                    partition_columns
                ),
                "partition_columns": (
                    partition_columns
                ),
                "parquet": parquet_result,
                "uploaded_files": uploaded_files,
                "s3_verified": verification_result,
            }

        except Exception as exc:
            if self.report_service is not None:
                try:
                    self.report_service.record_failure(
                        "Curated dataset processing: "
                        f"{normalized_dataset_name}",
                        exc,
                    )
                except Exception:
                    pass

            raise

    @staticmethod
    def _validate_source_path(
        source_file: Path,
    ) -> None:
        """
        Validate the source dataset path.
        """

        if not source_file.exists():
            raise FileNotFoundError(
                "Source dataset does not exist: "
                f"{source_file}"
            )

        if not source_file.is_file():
            raise ValueError(
                "Source dataset is not a file: "
                f"{source_file}"
            )

    @staticmethod
    def _format_schema_error(
        result,
    ) -> str:
        """
        Format schema validation failures.
        """

        errors: list[str] = []

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
            mismatch_details = []

            for column, details in (
                result.type_mismatches.items()
            ):
                mismatch_details.append(
                    f"{column} "
                    f"(expected={details['expected']}, "
                    f"actual={details['actual']})"
                )

            errors.append(
                "Type mismatches: "
                + "; ".join(
                    mismatch_details
                )
            )

        return (
            "Schema validation failed. "
            + " | ".join(errors)
        )


__all__ = [
    "CuratedPipeline",
]
