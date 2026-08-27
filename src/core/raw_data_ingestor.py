"""
Project : S3 Data Lake + Parquet Platform
Project ID : 022

Raw Data Ingestion
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.config import AppConfig
from src.services.s3_service import S3Service


SUPPORTED_INPUT_EXTENSIONS = {
    ".csv",
    ".json",
    ".jsonl",
    ".txt",
}


@dataclass(frozen=True)
class IngestionResult:
    """Represents the result of a raw-data ingestion operation."""

    source_file: str
    s3_uri: str
    s3_key: str
    file_size_bytes: int
    status: str
    skipped: bool


class RawDataIngestor:
    """Uploads supported source files into the S3 raw-data zone."""

    def __init__(
        self,
        config: AppConfig,
        s3_service: S3Service,
    ) -> None:
        """
        Initialize the raw-data ingestor.

        Args:
            config: Application configuration.
            s3_service: Configured S3 service.
        """
        self._config = config
        self._s3_service = s3_service

    def discover_input_files(self) -> list[Path]:
        """
        Discover supported files in the configured input directory.

        Returns:
            Sorted list of supported input files.

        Raises:
            FileNotFoundError: If the input directory does not exist.
        """
        input_directory = self._config.input_directory

        if not input_directory.exists():
            raise FileNotFoundError(
                f"Input directory does not exist: {input_directory}"
            )

        if not input_directory.is_dir():
            raise NotADirectoryError(
                f"Input path is not a directory: {input_directory}"
            )

        files = [
            path
            for path in input_directory.iterdir()
            if path.is_file()
            and path.suffix.lower() in SUPPORTED_INPUT_EXTENSIONS
        ]

        return sorted(files, key=lambda path: path.name.lower())

    def validate_input_file(self, source_file: Path) -> None:
        """
        Validate a source file before ingestion.

        Args:
            source_file: Source file to validate.

        Raises:
            FileNotFoundError: If the source file does not exist.
            ValueError: If the file format is unsupported.
        """
        if not source_file.exists():
            raise FileNotFoundError(
                f"Source file does not exist: {source_file}"
            )

        if not source_file.is_file():
            raise ValueError(
                f"Source path is not a file: {source_file}"
            )

        if source_file.suffix.lower() not in SUPPORTED_INPUT_EXTENSIONS:
            raise ValueError(
                f"Unsupported input file format: "
                f"{source_file.suffix}"
            )

    def build_s3_key(self, source_file: Path) -> str:
        """
        Build the S3 object key for a source file.

        Args:
            source_file: Source file to be ingested.

        Returns:
            S3 object key within the raw-data zone.
        """
        self.validate_input_file(source_file)

        filename = source_file.name

        return (
            f"{self._config.s3_raw_prefix}"
            f"{filename}"
        )

    def is_already_ingested(self, source_file: Path) -> bool:
        """
        Determine whether the source file already exists in S3.

        Args:
            source_file: Source file to check.

        Returns:
            True when an object with the same raw-data key exists.
        """
        s3_key = self.build_s3_key(source_file)

        return self._s3_service.object_exists(s3_key)

    def ingest_file(
        self,
        source_file: Path,
        skip_existing: bool = True,
    ) -> IngestionResult:
        """
        Ingest one source file into the S3 raw-data zone.

        Args:
            source_file: Source file to upload.
            skip_existing: Skip upload when the destination object exists.

        Returns:
            IngestionResult describing the operation.

        Raises:
            FileNotFoundError: If the source file does not exist.
            ValueError: If the source file is unsupported.
        """
        self.validate_input_file(source_file)

        s3_key = self.build_s3_key(source_file)
        file_size = source_file.stat().st_size

        if skip_existing and self._s3_service.object_exists(s3_key):
            s3_uri = (
                f"s3://{self._config.s3_bucket_name}/"
                f"{s3_key}"
            )

            return IngestionResult(
                source_file=str(source_file),
                s3_uri=s3_uri,
                s3_key=s3_key,
                file_size_bytes=file_size,
                status="SKIPPED",
                skipped=True,
            )

        s3_uri = self._s3_service.upload_file(
            local_file=source_file,
            s3_key=s3_key,
        )

        return IngestionResult(
            source_file=str(source_file),
            s3_uri=s3_uri,
            s3_key=s3_key,
            file_size_bytes=file_size,
            status="UPLOADED",
            skipped=False,
        )

    def ingest_all(
        self,
        skip_existing: bool = True,
    ) -> list[IngestionResult]:
        """
        Ingest all supported files from the input directory.

        Args:
            skip_existing: Skip files already present in S3.

        Returns:
            List of ingestion results.
        """
        input_files = self.discover_input_files()

        results: list[IngestionResult] = []

        for source_file in input_files:
            result = self.ingest_file(
                source_file=source_file,
                skip_existing=skip_existing,
            )
            results.append(result)

        return results

    def get_ingestion_summary(
        self,
        results: list[IngestionResult],
    ) -> dict[str, int]:
        """
        Generate a summary from ingestion results.

        Args:
            results: Completed ingestion results.

        Returns:
            Summary containing upload and skip counts.
        """
        uploaded_count = sum(
            result.status == "UPLOADED"
            for result in results
        )

        skipped_count = sum(
            result.status == "SKIPPED"
            for result in results
        )

        total_bytes = sum(
            result.file_size_bytes
            for result in results
        )

        return {
            "total_files": len(results),
            "uploaded_files": uploaded_count,
            "skipped_files": skipped_count,
            "total_bytes": total_bytes,
        }


__all__ = [
    "IngestionResult",
    "RawDataIngestor",
    "SUPPORTED_INPUT_EXTENSIONS",
]
