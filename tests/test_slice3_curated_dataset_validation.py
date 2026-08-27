from __future__ import annotations

import pandas as pd

from src.services.curated_dataset_validation_service import (
    CuratedDatasetValidationService,
)
from src.services.dataset_definition_service import (
    DatasetDefinitionService,
)


def customers_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "customer_id": pd.Series(
                [1, 2, 3],
                dtype="int64",
            ),
            "name": pd.Series(
                ["Alice", "Bob", "Charlie"],
                dtype="string",
            ),
            "city": pd.Series(
                ["Chennai", "Mumbai", "Delhi"],
                dtype="string",
            ),
            "registration_date": pd.Series(
                ["2026-08-20", "2026-08-21", "2026-08-22"],
                dtype="string",
            ),
        }
    )


def transactions_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "transaction_id": pd.Series(
                ["T001", "T002", "T003"],
                dtype="string",
            ),
            "customer_id": pd.Series(
                [1, 2, 3],
                dtype="int64",
            ),
            "amount": pd.Series(
                [100.50, 250.00, 75.25],
                dtype="float64",
            ),
            "transaction_date": pd.Series(
                ["2026-08-20", "2026-08-21", "2026-08-22"],
                dtype="string",
            ),
        }
    )


def main() -> int:

    service = CuratedDatasetValidationService(
        DatasetDefinitionService()
    )

    # ---------------------------------------------------------
    # 1. Customers PASS
    # ---------------------------------------------------------
    result = service.validate(
        "customers",
        customers_dataframe(),
    )

    assert result.valid
    assert result.errors == []

    # ---------------------------------------------------------
    # 2. Transactions PASS
    # ---------------------------------------------------------
    result = service.validate(
        "transactions",
        transactions_dataframe(),
    )

    assert result.valid
    assert result.errors == []

    # ---------------------------------------------------------
    # 3. Missing required column FAIL
    # ---------------------------------------------------------
    dataframe = customers_dataframe().drop(
        columns=["city"]
    )

    result = service.validate(
        "customers",
        dataframe,
    )

    assert not result.valid
    assert any(
        "Missing required columns" in error
        for error in result.errors
    )

    # ---------------------------------------------------------
    # 4. Empty DataFrame FAIL
    # ---------------------------------------------------------
    dataframe = customers_dataframe().iloc[0:0]

    result = service.validate(
        "customers",
        dataframe,
    )

    assert not result.valid
    assert "Dataset contains no rows." in result.errors

    # ---------------------------------------------------------
    # 5. Unknown dataset FAIL
    # ---------------------------------------------------------
    result = service.validate(
        "unknown_dataset",
        customers_dataframe(),
    )

    assert not result.valid
    assert any(
        "not configured" in error.lower()
        for error in result.errors
    )

    # ---------------------------------------------------------
    # 6. Missing partition column FAIL
    # ---------------------------------------------------------
    dataframe = transactions_dataframe().drop(
        columns=["transaction_date"]
    )

    result = service.validate(
        "transactions",
        dataframe,
    )

    assert not result.valid
    assert any(
        "Missing required columns" in error
        for error in result.errors
    )

    print("CuratedDatasetValidationService: PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())