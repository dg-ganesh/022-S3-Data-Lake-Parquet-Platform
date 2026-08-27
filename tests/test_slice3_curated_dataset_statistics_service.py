import pandas as pd

from src.core.curated_dataset_statistics_service import (
    CuratedDatasetStatisticsService,
)


def main() -> int:

    service = CuratedDatasetStatisticsService()

    dataframe = pd.DataFrame(
        {
            "customer_id": [101, 102, 101, 103],
            "amount": [100.0, 200.0, 300.0, 400.0],
            "status": [
                "COMPLETED",
                "PENDING",
                "COMPLETED",
                None,
            ],
        }
    )

    original = dataframe.copy()

    # ---------------------------------------------------------
    # TEST 1 — Row count
    # ---------------------------------------------------------

    assert service.row_count(dataframe) == 4

    # ---------------------------------------------------------
    # TEST 2 — Column count
    # ---------------------------------------------------------

    assert service.column_count(dataframe) == 3

    # ---------------------------------------------------------
    # TEST 3 — Null counts
    # ---------------------------------------------------------

    null_counts = service.null_counts(dataframe)

    assert null_counts == {
        "customer_id": 0,
        "amount": 0,
        "status": 1,
    }

    # ---------------------------------------------------------
    # TEST 4 — Unique counts
    # ---------------------------------------------------------

    unique_counts = service.unique_counts(dataframe)

    assert unique_counts == {
        "customer_id": 3,
        "amount": 4,
        "status": 2,
    }

    # ---------------------------------------------------------
    # TEST 5 — Numeric statistics
    # ---------------------------------------------------------

    statistics = service.numeric_statistics(dataframe)

    assert statistics["amount"]["min"] == 100.0
    assert statistics["amount"]["max"] == 400.0
    assert statistics["amount"]["mean"] == 250.0
    assert statistics["amount"]["sum"] == 1000.0

    # ---------------------------------------------------------
    # TEST 6 — Complete profile
    # ---------------------------------------------------------

    profile = service.profile(dataframe)

    assert profile["row_count"] == 4
    assert profile["column_count"] == 3

    assert profile["null_counts"]["status"] == 1
    assert profile["unique_counts"]["customer_id"] == 3
    assert profile["numeric_statistics"]["amount"]["sum"] == 1000.0

    # ---------------------------------------------------------
    # TEST 7 — Input remains unchanged
    # ---------------------------------------------------------

    assert dataframe.equals(original)

    # ---------------------------------------------------------
    # TEST 8 — Invalid input
    # ---------------------------------------------------------

    try:
        service.row_count("not a dataframe")
    except TypeError as exc:
        assert "pandas DataFrame" in str(exc)
    else:
        raise AssertionError(
            "Expected TypeError for invalid dataframe"
        )

    print("CuratedDatasetStatisticsService: PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())