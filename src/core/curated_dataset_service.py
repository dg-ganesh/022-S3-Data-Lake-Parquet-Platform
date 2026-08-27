from __future__ import annotations

import pandas as pd

from src.config import AppConfig
from src.core.curated_dataset_reader import CuratedDatasetReader
from src.core.curated_dataset_validator import CuratedDatasetValidator


class CuratedDatasetService:
    """
    Orchestrates reading and validating a curated dataset.

    Responsibilities:
    - Read the curated dataset through CuratedDatasetReader.
    - Validate it through CuratedDatasetValidator.
    - Return the validated DataFrame.

    This class does not:
    - Access S3 directly.
    - Implement Parquet reading.
    - Implement validation rules.
    - Modify the dataset.
    """

    def __init__(
        self,
        config: AppConfig,
        reader: CuratedDatasetReader | None = None,
        validator: CuratedDatasetValidator | None = None,
    ) -> None:
        self.config = config
        self.reader = reader or CuratedDatasetReader(config)
        self.validator = validator or CuratedDatasetValidator()

    def load_dataset(
        self,
        dataset_name: str,
        required_columns: list[str],
        allow_empty: bool = False,
    ) -> pd.DataFrame:
        """
        Read and validate a curated dataset.

        Raises:
            ValueError: if validation fails.
        """

        dataframe = self.reader.read_dataset(dataset_name)

        validation_result = self.validator.validate(
            dataframe=dataframe,
            required_columns=required_columns,
            dataset_name=dataset_name,
            allow_empty=allow_empty,
        )

        if not validation_result["valid"]:
            errors = "; ".join(validation_result["errors"])

            raise ValueError(
                f"Curated dataset validation failed for "
                f"'{dataset_name}': {errors}"
            )

        return dataframe