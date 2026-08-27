"""
Project : S3 Data Lake + Parquet Platform
Project ID : 022

Execution Report Service
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from time import perf_counter


class ExecutionReportService:
    """Creates and manages the runtime execution report."""

    def __init__(
        self,
        log_directory: Path,
        application_version: str,
    ) -> None:
        """
        Initialize the execution report service.

        Args:
            log_directory: Directory where runtime reports are stored.
            application_version: Current application version.
        """
        self._log_directory = log_directory
        self._application_version = application_version
        self._report_path = (
            log_directory / "execution_report.txt"
        )

        self._start_time: datetime | None = None
        self._start_counter: float | None = None
        self._last_successful_checkpoint: str | None = None

    @property
    def report_path(self) -> Path:
        """Return the path of the execution report."""
        return self._report_path

    def start_execution(self) -> None:
        """
        Start a new execution report.

        Creates the logs directory when necessary and initializes
        the execution report with application information.
        """
        self._log_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._start_time = datetime.now()
        self._start_counter = perf_counter()
        self._last_successful_checkpoint = None

        self._write_report(
            [
                "PROJECT 022 - EXECUTION REPORT",
                "=" * 50,
                f"Application Version : {self._application_version}",
                f"Execution Start     : "
                f"{self._format_datetime(self._start_time)}",
                "Status              : RUNNING",
                "",
                "CHECKPOINTS",
                "-" * 50,
            ]
        )

    def record_checkpoint(
        self,
        checkpoint: str,
    ) -> None:
        """
        Record a successfully completed execution checkpoint.

        Args:
            checkpoint: Description of the completed checkpoint.

        Raises:
            ValueError: If checkpoint is empty.
            RuntimeError: If execution has not been started.
        """
        self._ensure_execution_started()

        normalized_checkpoint = checkpoint.strip()

        if not normalized_checkpoint:
            raise ValueError(
                "Execution checkpoint cannot be empty."
            )

        self._last_successful_checkpoint = normalized_checkpoint

        self._append_report_line(
            f"PASS | {normalized_checkpoint}"
        )

    def record_failure(
        self,
        checkpoint: str,
        error: Exception | str,
    ) -> None:
        """
        Record a failed execution checkpoint.

        Args:
            checkpoint: Description of the failed checkpoint.
            error: Error information.
        """
        self._ensure_execution_started()

        normalized_checkpoint = checkpoint.strip()

        if not normalized_checkpoint:
            normalized_checkpoint = "Unknown checkpoint"

        error_message = str(error).strip()

        if not error_message:
            error_message = "Unknown error"

        self._append_report_line(
            f"FAIL | {normalized_checkpoint}"
        )
        self._append_report_line(
            f"ERROR | {error_message}"
        )

    def complete_execution(
        self,
        status: str = "PASS",
    ) -> Path:
        """
        Complete the execution report.

        Args:
            status: Final execution status.

        Returns:
            Path to the completed execution report.

        Raises:
            ValueError: If status is invalid.
            RuntimeError: If execution has not been started.
        """
        self._ensure_execution_started()

        normalized_status = status.strip().upper()

        if normalized_status not in {"PASS", "FAIL"}:
            raise ValueError(
                "Execution status must be PASS or FAIL."
            )

        end_time = datetime.now()

        duration_seconds = self._calculate_duration()

        self._append_report_line("")
        self._append_report_line("EXECUTION SUMMARY")
        self._append_report_line("-" * 50)
        self._append_report_line(
            f"Execution End       : "
            f"{self._format_datetime(end_time)}"
        )
        self._append_report_line(
            f"Status              : {normalized_status}"
        )
        self._append_report_line(
            f"Last Successful     : "
            f"{self._last_successful_checkpoint or 'None'}"
        )
        self._append_report_line(
            f"Execution Duration  : "
            f"{duration_seconds:.3f} seconds"
        )

        return self._report_path

    def get_report_contents(self) -> str:
        """
        Read the current execution report.

        Returns:
            Report contents.

        Raises:
            FileNotFoundError: If the report does not exist.
        """
        if not self._report_path.exists():
            raise FileNotFoundError(
                f"Execution report does not exist: "
                f"{self._report_path}"
            )

        return self._report_path.read_text(
            encoding="utf-8"
        )

    def _write_report(
        self,
        lines: list[str],
    ) -> None:
        """
        Write the initial report contents.

        Args:
            lines: Report lines to write.
        """
        self._report_path.write_text(
            "\n".join(lines) + "\n",
            encoding="utf-8",
        )

    def _append_report_line(
        self,
        line: str,
    ) -> None:
        """
        Append a single line to the execution report.

        Args:
            line: Text to append.
        """
        with self._report_path.open(
            "a",
            encoding="utf-8",
        ) as report_file:
            report_file.write(f"{line}\n")

    def _calculate_duration(self) -> float:
        """
        Calculate execution duration.

        Returns:
            Duration in seconds.

        Raises:
            RuntimeError: If execution timing was not initialized.
        """
        if self._start_counter is None:
            raise RuntimeError(
                "Execution timer has not been initialized."
            )

        return perf_counter() - self._start_counter

    def _ensure_execution_started(self) -> None:
        """Ensure an execution session has been started."""
        if self._start_time is None:
            raise RuntimeError(
                "Execution has not been started. "
                "Call start_execution() first."
            )

    @staticmethod
    def _format_datetime(
        timestamp: datetime,
    ) -> str:
        """
        Format an execution timestamp.

        Args:
            timestamp: Datetime to format.

        Returns:
            Human-readable timestamp.
        """
        return timestamp.strftime(
            "%Y-%m-%d %H:%M:%S"
        )


__all__ = [
    "ExecutionReportService",
]