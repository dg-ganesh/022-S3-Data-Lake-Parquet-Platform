import pandas as pd

from src.core.curated_dataset_aggregation_service import (
    CuratedDatasetAggregationService,
)


def main() -> int:

    service = CuratedDatasetAggregationService()

    dataframe = pd.DataFrame(
        {
            "transaction_id": [1, 2, 3, 4, 5],
            "customer_id": [101, 101, 102, 102, 103],
            "amount": [100.0, 200.0, 50.0, 150.0, 500.0],
        }
    )

    original = dataframe.copy()

    # ---------------------------------------------------------
    # TEST 1 — Count
    # ---------------------------------------------------------

    assert service.count(dataframe) == 5

    # ---------------------------------------------------------
    # TEST 2 — Sum
    # ---------------------------------------------------------

    assert service.sum(dataframe, "amount") == 1000.0

    # ---------------------------------------------------------
    # TEST 3 — Average
    # ---------------------------------------------------------

    assert service.average(dataframe, "amount") == 200.0

    # ---------------------------------------------------------
    # TEST 4 — Minimum
    # ---------------------------------------------------------

    assert service.minimum(dataframe, "amount") == 50.0

    # ---------------------------------------------------------
    # TEST 5 — Maximum
    # ---------------------------------------------------------

    assert service.maximum(dataframe, "amount") == 500.0

    # ---------------------------------------------------------
    # TEST 6 — Group + Sum
    # ---------------------------------------------------------

    result = service.group_and_aggregate(
        dataframe=dataframe,
        group_by=["customer_id"],
        aggregate_column="amount",
        operation="sum",
    )

    assert list(result.columns) == [
        "customer_id",
        "amount",
    ]

    result = result.sort_values("customer_id")

    assert result["customer_id"].tolist() == [
        101,
        102,
        103,
    ]

    assert result["amount"].tolist() == [
        300.0,
        200.0,
        500.0,
    ]

    # ---------------------------------------------------------
    # TEST 7 — Group + Average
    # ---------------------------------------------------------

    result = service.group_and_aggregate(
        dataframe=dataframe,
        group_by=["customer_id"],
        aggregate_column="amount",
        operation="mean",
    )

    result = result.sort_values("customer_id")

    assert result["amount"].tolist() == [
        150.0,
        100.0,
        500.0,
    ]

    # ---------------------------------------------------------
    # TEST 8 — Unsupported operation
    # ---------------------------------------------------------

    try:
        service.group_and_aggregate(
            dataframe=dataframe,
            group_by=["customer_id"],
            aggregate_column="amount",
            operation="median",
        )
    except ValueError as exc:
        assert "Unsupported aggregation operation" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError for unsupported operation"
        )

    # ---------------------------------------------------------
    # TEST 9 — Missing column
    # ---------------------------------------------------------

    try:
        service.sum(dataframe, "does_not_exist")
    except ValueError as exc:
        assert "does_not_exist" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError for missing column"
        )

    # ---------------------------------------------------------
    # TEST 10 — Input remains unchanged
    # ---------------------------------------------------------

    assert dataframe.equals(original)

    print("CuratedDatasetAggregationService: PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
