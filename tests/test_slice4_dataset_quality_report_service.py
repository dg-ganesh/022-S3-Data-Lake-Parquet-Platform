import pandas as pd

from src.services.dataset_quality_service import (
    DatasetQualityService,
)
from src.services.dataset_quality_report_service import (
    DatasetQualityReportService,
)


def main() -> None:

    quality_service = DatasetQualityService()

    dataframe = pd.DataFrame(
        {
            "customer_id": [1, 2, 3],
            "customer_name": ["A", "B", "C"],
        }
    )

    # Generate quality results.
    quality_service.check_not_empty(
        "customers",
        dataframe,
    )

    quality_service.check_required_columns(
        "customers",
        dataframe,
        ["customer_id", "customer_name"],
    )

    quality_service.check_not_null(
        "customers",
        dataframe,
        "customer_id",
    )

    results = quality_service.get_results()

    report_service = DatasetQualityReportService()

    # ---------------------------------------------------------
    # Report with all rules passing
    # ---------------------------------------------------------

    report = report_service.build_report(
        "customers",
        results,
    )

    assert report["dataset_name"] == "customers"
    assert report["total_rules"] == 3
    assert report["passed_rules"] == 3
    assert report["failed_rules"] == 0
    assert report["overall_passed"] is True
    assert len(report["results"]) == 3

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    summary = report_service.build_summary(
        "customers",
        results,
    )

    assert "Dataset: customers" in summary
    assert "Status: PASS" in summary
    assert "Rules: 3" in summary
    assert "Passed: 3" in summary
    assert "Failed: 0" in summary

    # ---------------------------------------------------------
    # Report containing a failure
    # ---------------------------------------------------------

    quality_service.check_not_null(
        "customers",
        dataframe,
        "missing_column",
    )

    failed_results = quality_service.get_results()

    failed_report = report_service.build_report(
        "customers",
        failed_results,
    )

    assert failed_report["total_rules"] == 4
    assert failed_report["passed_rules"] == 3
    assert failed_report["failed_rules"] == 1
    assert failed_report["overall_passed"] is False

    failed_summary = report_service.build_summary(
        "customers",
        failed_results,
    )

    assert "Status: FAIL" in failed_summary
    assert "Failed: 1" in failed_summary

    # ---------------------------------------------------------
    # Empty result set
    # ---------------------------------------------------------

    empty_report = report_service.build_report(
        "empty_dataset",
        [],
    )

    assert empty_report["total_rules"] == 0
    assert empty_report["passed_rules"] == 0
    assert empty_report["failed_rules"] == 0
    assert empty_report["overall_passed"] is False

    print("DatasetQualityReportService: PASS")


if __name__ == "__main__":
    main()