import pandas as pd

from src.services.dataset_quality_orchestrator import (
    DatasetQualityOrchestrator,
)


def main() -> None:

    orchestrator = DatasetQualityOrchestrator()

    dataframe = pd.DataFrame(
        {
            "customer_id": [1, 2, 3],
            "customer_name": ["A", "B", "C"],
            "country": ["IN", "US", "UK"],
        }
    )

    # ---------------------------------------------------------
    # Successful validation
    # ---------------------------------------------------------

    report = orchestrator.validate_dataset(
        dataset_name="customers",
        dataframe=dataframe,
        required_columns=[
            "customer_id",
            "customer_name",
            "country",
        ],
        not_null_columns=[
            "customer_id",
        ],
        unique_columns=[
            "customer_id",
        ],
    )

    assert report["dataset_name"] == "customers"
    assert report["total_rules"] == 4
    assert report["passed_rules"] == 4
    assert report["failed_rules"] == 0
    assert report["overall_passed"] is True

    # ---------------------------------------------------------
    # Validation with failure
    # ---------------------------------------------------------

    dataframe_with_duplicate = pd.DataFrame(
        {
            "customer_id": [1, 2, 2],
            "customer_name": ["A", "B", "C"],
            "country": ["IN", "US", "UK"],
        }
    )

    failed_report = orchestrator.validate_dataset(
        dataset_name="customers",
        dataframe=dataframe_with_duplicate,
        required_columns=[
            "customer_id",
            "customer_name",
            "country",
        ],
        not_null_columns=[
            "customer_id",
        ],
        unique_columns=[
            "customer_id",
        ],
    )

    assert failed_report["dataset_name"] == "customers"
    assert failed_report["total_rules"] == 4
    assert failed_report["passed_rules"] == 3
    assert failed_report["failed_rules"] == 1
    assert failed_report["overall_passed"] is False

    # ---------------------------------------------------------
    # Missing column
    # ---------------------------------------------------------

    missing_column_report = orchestrator.validate_dataset(
        dataset_name="customers",
        dataframe=dataframe,
        required_columns=[
            "customer_id",
            "email",
        ],
    )

    assert missing_column_report["total_rules"] == 2
    assert missing_column_report["passed_rules"] == 1
    assert missing_column_report["failed_rules"] == 1
    assert missing_column_report["overall_passed"] is False

    print("DatasetQualityOrchestrator: PASS")


if __name__ == "__main__":
    main()