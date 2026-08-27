from src.services.dataset_quality_execution_report import (
    DatasetQualityExecutionReport,
)


def main() -> None:

    service = DatasetQualityExecutionReport()

    # ---------------------------------------------------------
    # Successful quality report
    # ---------------------------------------------------------

    passing_report = {
        "dataset_name": "customers",
        "total_rules": 4,
        "passed_rules": 4,
        "failed_rules": 0,
        "overall_passed": True,
        "results": [],
    }

    result = service.build_execution_result(
        passing_report
    )

    assert result["dataset_name"] == "customers"
    assert result["status"] == "PASS"
    assert result["success"] is True
    assert result["total_rules"] == 4
    assert result["passed_rules"] == 4
    assert result["failed_rules"] == 0

    summary = service.build_execution_summary(
        passing_report
    )

    assert "Dataset: customers" in summary
    assert "Status: PASS" in summary
    assert "Rules: 4" in summary
    assert "Passed: 4" in summary
    assert "Failed: 0" in summary

    # ---------------------------------------------------------
    # Failed quality report
    # ---------------------------------------------------------

    failing_report = {
        "dataset_name": "transactions",
        "total_rules": 5,
        "passed_rules": 3,
        "failed_rules": 2,
        "overall_passed": False,
        "results": [],
    }

    result = service.build_execution_result(
        failing_report
    )

    assert result["dataset_name"] == "transactions"
    assert result["status"] == "FAIL"
    assert result["success"] is False
    assert result["total_rules"] == 5
    assert result["passed_rules"] == 3
    assert result["failed_rules"] == 2

    summary = service.build_execution_summary(
        failing_report
    )

    assert "Dataset: transactions" in summary
    assert "Status: FAIL" in summary
    assert "Rules: 5" in summary
    assert "Passed: 3" in summary
    assert "Failed: 2" in summary

    # ---------------------------------------------------------
    # Original quality report must remain unchanged
    # ---------------------------------------------------------

    assert failing_report["overall_passed"] is False
    assert failing_report["failed_rules"] == 2

    print("DatasetQualityExecutionReport: PASS")


if __name__ == "__main__":
    main()