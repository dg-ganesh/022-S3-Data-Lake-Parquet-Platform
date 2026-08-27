import pandas as pd

from src.core.curated_dataset_query_service import (
    CuratedDatasetQueryService,
)


def main() -> int:

    service = CuratedDatasetQueryService()

    dataframe = pd.DataFrame(
        {
            "transaction_id": [1, 2, 3, 4],
            "customer_id": [101, 102, 101, 103],
            "amount": [100.0, 250.0, 75.0, 500.0],
            "status": [
                "COMPLETED",
                "PENDING",
                "COMPLETED",
                "COMPLETED",
            ],
        }
    )

    original = dataframe.copy()

    # ---------------------------------------------------------
    # TEST 1 — Filter rows
    # ---------------------------------------------------------

    result = service.filter_rows(
        dataframe=dataframe,
        condition=dataframe["status"] == "COMPLETED",
    )

    assert len(result) == 3
    assert result["transaction_id"].tolist() == [1, 3, 4]

    # ---------------------------------------------------------
    # TEST 2 — Select columns
    # ---------------------------------------------------------

    result = service.select_columns(
        dataframe=dataframe,
        columns=[
            "transaction_id",
            "amount",
        ],
    )

    assert list(result.columns) == [
        "transaction_id",
        "amount",
    ]

    assert len(result) == 4

    # ---------------------------------------------------------
    # TEST 3 — Filter + select
    # ---------------------------------------------------------

    result = service.filter_and_select(
        dataframe=dataframe,
        condition=dataframe["amount"] >= 100,
        columns=[
            "transaction_id",
            "customer_id",
            "amount",
        ],
    )

    assert len(result) == 3
    assert list(result.columns) == [
        "transaction_id",
        "customer_id",
        "amount",
    ]

    assert result["transaction_id"].tolist() == [1, 2, 4]

    # ---------------------------------------------------------
    # TEST 4 — Missing column
    # ---------------------------------------------------------

    try:
        service.select_columns(
            dataframe=dataframe,
            columns=[
                "transaction_id",
                "does_not_exist",
            ],
        )
    except ValueError as exc:
        assert "does_not_exist" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError for missing column"
        )

    # ---------------------------------------------------------
    # TEST 5 — Invalid condition length
    # ---------------------------------------------------------

    invalid_condition = pd.Series([True, False])

    try:
        service.filter_rows(
            dataframe=dataframe,
            condition=invalid_condition,
        )
    except ValueError as exc:
        assert "condition length" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError for invalid condition length"
        )

    # ---------------------------------------------------------
    # TEST 6 — Original DataFrame is unchanged
    # ---------------------------------------------------------

    assert dataframe.equals(original)

    print("CuratedDatasetQueryService: PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
