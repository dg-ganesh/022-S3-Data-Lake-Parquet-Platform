from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class QualityResult:
    dataset_name: str
    rule: str
    passed: bool
    details: str


class DatasetQualityService:
    """
    Executes reusable data-quality rules against a DataFrame.

    This service does not:
    - read from S3
    - write to S3
    - modify the source DataFrame
    - perform dataset transformations
    """

    def __init__(self) -> None:
        self._results: list[QualityResult] = []

    def check_not_empty(
        self,
        dataset_name: str,
        dataframe: pd.DataFrame,
    ) -> QualityResult:

        passed = not dataframe.empty

        result = QualityResult(
            dataset_name=dataset_name,
            rule="not_empty",
            passed=passed,
            details=(
                f"Dataset contains {len(dataframe)} rows"
                if passed
                else "Dataset contains no rows"
            ),
        )

        self._results.append(result)
        return result

    def check_required_columns(
        self,
        dataset_name: str,
        dataframe: pd.DataFrame,
        required_columns: list[str],
    ) -> QualityResult:

        missing = [
            column
            for column in required_columns
            if column not in dataframe.columns
        ]

        passed = not missing

        result = QualityResult(
            dataset_name=dataset_name,
            rule="required_columns",
            passed=passed,
            details=(
                "All required columns are present"
                if passed
                else f"Missing columns: {missing}"
            ),
        )

        self._results.append(result)
        return result

    def check_not_null(
        self,
        dataset_name: str,
        dataframe: pd.DataFrame,
        column: str,
    ) -> QualityResult:

        if column not in dataframe.columns:
            result = QualityResult(
                dataset_name=dataset_name,
                rule=f"not_null:{column}",
                passed=False,
                details=f"Column not found: {column}",
            )
        else:
            null_count = int(dataframe[column].isna().sum())
            passed = null_count == 0

            result = QualityResult(
                dataset_name=dataset_name,
                rule=f"not_null:{column}",
                passed=passed,
                details=(
                    f"No null values in {column}"
                    if passed
                    else f"{null_count} null values found in {column}"
                ),
            )

        self._results.append(result)
        return result

    def check_unique(
        self,
        dataset_name: str,
        dataframe: pd.DataFrame,
        column: str,
    ) -> QualityResult:

        if column not in dataframe.columns:
            result = QualityResult(
                dataset_name=dataset_name,
                rule=f"unique:{column}",
                passed=False,
                details=f"Column not found: {column}",
            )
        else:
            duplicate_count = int(
                dataframe[column].duplicated().sum()
            )

            passed = duplicate_count == 0

            result = QualityResult(
                dataset_name=dataset_name,
                rule=f"unique:{column}",
                passed=passed,
                details=(
                    f"All values in {column} are unique"
                    if passed
                    else (
                        f"{duplicate_count} duplicate values "
                        f"found in {column}"
                    )
                ),
            )

        self._results.append(result)
        return result

    def get_results(self) -> list[QualityResult]:
        return list(self._results)

    def all_passed(self) -> bool:
        return all(
            result.passed
            for result in self._results
        )

    def as_dict(self) -> list[dict[str, Any]]:
        return [
            {
                "dataset_name": result.dataset_name,
                "rule": result.rule,
                "passed": result.passed,
                "details": result.details,
            }
            for result in self._results
        ]