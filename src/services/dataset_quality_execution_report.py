from __future__ import annotations

from typing import Any


class DatasetQualityExecutionReport:
    """
    Converts a dataset quality report into an execution-level result.

    This class does not execute quality rules.
    It only interprets an already generated quality report.
    """

    def build_execution_result(
        self,
        quality_report: dict[str, Any],
    ) -> dict[str, Any]:

        dataset_name = quality_report["dataset_name"]
        total_rules = quality_report["total_rules"]
        passed_rules = quality_report["passed_rules"]
        failed_rules = quality_report["failed_rules"]
        overall_passed = quality_report["overall_passed"]

        status = "PASS" if overall_passed else "FAIL"

        return {
            "dataset_name": dataset_name,
            "status": status,
            "success": overall_passed,
            "total_rules": total_rules,
            "passed_rules": passed_rules,
            "failed_rules": failed_rules,
        }

    def build_execution_summary(
        self,
        quality_report: dict[str, Any],
    ) -> str:

        result = self.build_execution_result(
            quality_report
        )

        return (
            f"Dataset: {result['dataset_name']} | "
            f"Status: {result['status']} | "
            f"Rules: {result['total_rules']} | "
            f"Passed: {result['passed_rules']} | "
            f"Failed: {result['failed_rules']}"
        )