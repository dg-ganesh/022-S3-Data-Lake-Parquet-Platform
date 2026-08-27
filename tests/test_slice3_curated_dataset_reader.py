"""
Project : S3 Data Lake + Parquet Platform
Project ID : 022

Slice 3 - Curated Dataset Reader Integration Test
"""

from __future__ import annotations

import pandas as pd

from src.config import get_config
from src.core.curated_dataset_reader import (
    CuratedDatasetReader,
)


EXPECTED_ROW_COUNTS = {
    "customers": 5,
    "transactions": 5,
}

EXPECTED_TRANSACTION_DATES = {
    "2026-08-20",
    "2026-08-21",
    "2026-08-22",
    "2026-08-23",
    "2026-08-24",
}


def main() -> int:
    """Verify read-only access to curated S3 datasets."""
    config = get_config()
    reader = CuratedDatasetReader(config=config)

    customers = reader.read_dataset("customers")
    transactions = reader.read_dataset("transactions")

    assert isinstance(customers, pd.DataFrame)
    assert isinstance(transactions, pd.DataFrame)
    assert len(customers) == EXPECTED_ROW_COUNTS["customers"]
    assert len(transactions) == EXPECTED_ROW_COUNTS["transactions"]
    assert set(transactions["transaction_date"].astype(str)) == (
        EXPECTED_TRANSACTION_DATES
    )

    repeated_transactions = reader.read_dataset("transactions")
    pd.testing.assert_frame_equal(
        transactions,
        repeated_transactions,
    )

    try:
        reader.read_dataset("missing_dataset")
    except FileNotFoundError as exc:
        assert "Curated dataset does not exist" in str(exc)
    else:
        raise AssertionError(
            "Missing dataset did not raise FileNotFoundError."
        )

    print("CuratedDatasetReader: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
