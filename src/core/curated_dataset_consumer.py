from __future__ import annotations

import pandas as pd

from src.core.curated_dataset_reader import CuratedDatasetReader
from src.services.curated_dataset_validation_service import (
    CuratedDatasetValidationService,
)


class CuratedDatasetConsumer:
    """
    Coordinates reading and validation of curated datasets.

    This class does not perform S3 operations directly and does not
    modify or persist the dataset.
    """

    def __init__(
        self,
        reader: CuratedDatasetReader,
        validator: CuratedDatasetValidationService,
    ) -> None:
        self.reader = reader
        self.validator = validator

    def load_dataset(
        self,
        dataset_name: str,
    ) -> pd.DataFrame:
        """
        Read and validate a curated dataset.

        Raises:
            ValueError: If validation fails.
        """

        dataframe = self.reader.read_dataset(
            dataset_name
        )

        validation_result = self.validator.validate(
            dataset_name,
            dataframe,
        )

        if not validation_result.valid:
            raise ValueError(
                f"Curated dataset validation failed for "
                f"'{dataset_name}': "
                + "; ".join(validation_result.errors)
            )

        return dataframe


__all__ = [
    "CuratedDatasetConsumer",
]