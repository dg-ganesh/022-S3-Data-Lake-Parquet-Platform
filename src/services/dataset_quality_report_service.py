from __future__ import annotations

from typing import Any

from src.services.dataset_quality_service import QualityResult


class DatasetQualityReportService:
    """
    Builds summary reports from DatasetQualityService results.

    This service is read-only with respect to the supplied results.
    It does not execute quality rules or access S3/local files.
    """

    def build_report(
        self,
        dataset_name: str,
        results: list[QualityResult],
    ) -> dict[str, Any]:

        total_rules = len(results)
        passed_rules = sum(1 for result in results if result.passed)
        failed_rules = total_rules - passed_rules

        overall_passed = (
            total_rules > 0 and failed_rules == 0
        )

        return {
            "dataset_name": dataset_name,
            "total_rules": total_rules,
            "passed_rules": passed_rules,
            "failed_rules": failed_rules,
            "overall_passed": overall_passed,
            "results": [
                {
                    "rule": result.rule,
                    "passed": result.passed,
                    "details": result.details,
                }
                for result in results
            ],
        }

    def build_summary(
        self,
        dataset_name: str,
        results: list[QualityResult],
    ) -> str:

        total_rules = len(results)
        passed_rules = sum(
            1 for result in results if result.passed
        )
        failed_rules = total_rules - passed_rules

        status = "PASS" if (
            total_rules > 0 and failed_rules == 0
        ) else "FAIL"

        return (
            f"Dataset: {dataset_name} | "
            f"Status: {status} | "
            f"Rules: {total_rules} | "
            f"Passed: {passed_rules} | "
            f"Failed: {failed_rules}"
        )