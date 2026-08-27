"""
Project : S3 Data Lake + Parquet Platform
Project ID : 022

Application Configuration
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_NAME = "S3 Data Lake + Parquet Platform"
PROJECT_ID = "022"
APPLICATION_VERSION = "0.1.0"


@dataclass(frozen=True)
class AppConfig:
    """Central application configuration for Project 022."""

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------

    project_name: str
    project_id: str
    application_version: str
    environment: str

    # ------------------------------------------------------------------
    # AWS / S3
    # ------------------------------------------------------------------

    aws_region: str
    s3_bucket_name: str

    s3_raw_prefix: str
    s3_curated_prefix: str
    s3_rejected_prefix: str
    s3_metadata_prefix: str

    # ------------------------------------------------------------------
    # Local directories
    # ------------------------------------------------------------------

    project_root: Path
    input_directory: Path
    output_directory: Path
    curated_output_directory: Path
    sample_data_directory: Path
    log_directory: Path

    # ------------------------------------------------------------------
    # Parquet
    # ------------------------------------------------------------------

    parquet_compression: str


def _get_environment_value(
    name: str,
    default: str | None = None,
) -> str:
    """
    Retrieve a configuration value from an environment variable.

    Args:
        name:
            Environment variable name.

        default:
            Optional default value.

    Returns:
        Configured value.

    Raises:
        ValueError:
            If the value is missing or blank.
    """

    value = os.getenv(name, default)

    if value is None or not value.strip():
        raise ValueError(
            "Required configuration environment variable "
            f"is missing: {name}"
        )

    return value.strip()


def _get_project_root() -> Path:
    """
    Resolve the project root directory from this source file.
    """

    return Path(__file__).resolve().parent.parent


def _normalize_s3_prefix(prefix: str) -> str:
    """
    Normalize an S3 prefix so that it has a trailing slash.
    """

    normalized_prefix = prefix.strip().strip("/")

    if not normalized_prefix:
        raise ValueError(
            "S3 prefix cannot be empty."
        )

    return f"{normalized_prefix}/"


def get_config() -> AppConfig:
    """
    Build the complete Project 022 application configuration.
    """

    project_root = _get_project_root()

    curated_output_directory = (
        project_root / "data" / "curated"
    )

    config = AppConfig(
        # --------------------------------------------------------------
        # Application
        # --------------------------------------------------------------

        project_name=PROJECT_NAME,

        project_id=PROJECT_ID,

        application_version=APPLICATION_VERSION,

        environment=os.getenv(
            "PROJECT022_ENVIRONMENT",
            "development",
        ).strip(),

        # --------------------------------------------------------------
        # AWS / S3
        # --------------------------------------------------------------

        aws_region=os.getenv(
            "AWS_REGION",
            "ap-south-1",
        ).strip(),

        s3_bucket_name=_get_environment_value(
            "PROJECT022_S3_BUCKET"
        ),

        s3_raw_prefix=_normalize_s3_prefix(
            os.getenv(
                "PROJECT022_S3_RAW_PREFIX",
                "raw",
            )
        ),

        s3_curated_prefix=_normalize_s3_prefix(
            os.getenv(
                "PROJECT022_S3_CURATED_PREFIX",
                "curated",
            )
        ),

        s3_rejected_prefix=_normalize_s3_prefix(
            os.getenv(
                "PROJECT022_S3_REJECTED_PREFIX",
                "rejected",
            )
        ),

        s3_metadata_prefix=_normalize_s3_prefix(
            os.getenv(
                "PROJECT022_S3_METADATA_PREFIX",
                "metadata",
            )
        ),

        # --------------------------------------------------------------
        # Local directories
        # --------------------------------------------------------------

        project_root=project_root,

        input_directory=(
            project_root / "data" / "input"
        ),

        output_directory=(
            project_root / "data" / "output"
        ),

        curated_output_directory=(
            curated_output_directory
        ),

        sample_data_directory=(
            project_root / "data" / "samples"
        ),

        log_directory=(
            project_root / "logs"
        ),

        # --------------------------------------------------------------
        # Parquet
        # --------------------------------------------------------------

        parquet_compression=os.getenv(
            "PROJECT022_PARQUET_COMPRESSION",
            "snappy",
        ).strip(),
    )

    validate_config(config)

    return config


def validate_config(
    config: AppConfig,
) -> None:
    """
    Validate Project 022 application configuration.
    """

    if not config.project_name:
        raise ValueError(
            "Project name cannot be empty."
        )

    if not config.project_id:
        raise ValueError(
            "Project ID cannot be empty."
        )

    if not config.application_version:
        raise ValueError(
            "Application version cannot be empty."
        )

    if not config.environment:
        raise ValueError(
            "Environment cannot be empty."
        )

    if not config.aws_region:
        raise ValueError(
            "AWS region cannot be empty."
        )

    if not config.s3_bucket_name:
        raise ValueError(
            "S3 bucket name cannot be empty."
        )

    s3_prefixes = {
        "raw": config.s3_raw_prefix,
        "curated": config.s3_curated_prefix,
        "rejected": config.s3_rejected_prefix,
        "metadata": config.s3_metadata_prefix,
    }

    for prefix_name, prefix_value in (
        s3_prefixes.items()
    ):

        if not prefix_value.endswith("/"):
            raise ValueError(
                f"S3 {prefix_name} prefix must "
                f"end with '/': {prefix_value}"
            )

    if config.project_root == Path():
        raise ValueError(
            "Project root directory is invalid."
        )

    if not config.input_directory.exists():
        raise ValueError(
            "Input directory does not exist: "
            f"{config.input_directory}"
        )

    if not config.curated_output_directory.exists():
        config.curated_output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    if not config.log_directory.exists():
        config.log_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    if not config.parquet_compression:
        raise ValueError(
            "Parquet compression cannot be empty."
        )


def get_s3_raw_prefix(
    config: AppConfig | None = None,
) -> str:
    """Return the configured raw-data S3 prefix."""

    active_config = config or get_config()

    return active_config.s3_raw_prefix


def get_s3_curated_prefix(
    config: AppConfig | None = None,
) -> str:
    """Return the configured curated-data S3 prefix."""

    active_config = config or get_config()

    return active_config.s3_curated_prefix


def get_s3_rejected_prefix(
    config: AppConfig | None = None,
) -> str:
    """Return the configured rejected-data S3 prefix."""

    active_config = config or get_config()

    return active_config.s3_rejected_prefix


def get_s3_metadata_prefix(
    config: AppConfig | None = None,
) -> str:
    """Return the configured metadata S3 prefix."""

    active_config = config or get_config()

    return active_config.s3_metadata_prefix


__all__ = [
    "APPLICATION_VERSION",
    "AppConfig",
    "PROJECT_ID",
    "PROJECT_NAME",
    "get_config",
    "get_s3_curated_prefix",
    "get_s3_metadata_prefix",
    "get_s3_raw_prefix",
    "get_s3_rejected_prefix",
    "validate_config",
]