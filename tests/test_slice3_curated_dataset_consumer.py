from __future__ import annotations

import pandas as pd

from src.core.curated_dataset_consumer import (
    CuratedDatasetConsumer,
)
from src.services.curated_dataset_validation_service import (
    CuratedDatasetValidationService,
)
from src.services.dataset_definition_service import (
    DatasetDefinitionService,
)


class FakeReader:
    """
    Test double for CuratedDatasetReader.

    Keeps this unit test independent of S3.
    """

    def __init__(self) -> None:
        self.datasets = {
            "customers": pd.DataFrame(
                {
                    "customer_id": pd.Series(
                        [1, 2],
                        dtype="int64",
                    ),
                    "name": pd.Series(
                        ["Alice", "Bob"],
                        dtype="string",
                    ),
                    "city": pd.Series(
                        ["Chennai", "Mumbai"],
                        dtype="string",
                    ),
                    "registration_date": pd.Series(
                        ["2026-08-20", "2026-08-21"],
                        dtype="string",
                    ),
                }
            ),
            "transactions": pd.DataFrame(
                {
                    "transaction_id": pd.Series(
                        ["T001", "T002"],
                        dtype="string",
                    ),
                    "customer_id": pd.Series(
                        [1, 2],
                        dtype="int64",
                    ),
                    "amount": pd.Series(
                        [100.50, 200.00],
                        dtype="float64",
                    ),
                    "transaction_date": pd.Series(
                        ["2026-08-20", "2026-08-21"],
                        dtype="string",
                    ),
                }
            ),
        }

    def read_dataset(
        self,
        dataset_name: str,
    ) -> pd.DataFrame:

        if dataset_name not in self.datasets:
            raise ValueError(
                f"Dataset not available: {dataset_name}"
            )

        return self.datasets[dataset_name].copy()


def main() -> int:

    reader = FakeReader()

    validator = CuratedDatasetValidationService(
        DatasetDefinitionService()
    )

    consumer = CuratedDatasetConsumer(
        reader,
        validator,
    )

    # ---------------------------------------------------------
    # Customers
    # ---------------------------------------------------------
    customers = consumer.load_dataset(
        "customers"
    )

    assert len(customers) == 2
    assert list(customers.columns) == [
        "customer_id",
        "name",
        "city",
        "registration_date",
    ]

    # ---------------------------------------------------------
    # Transactions
    # ---------------------------------------------------------
    transactions = consumer.load_dataset(
        "transactions"
    )

    assert len(transactions) == 2
    assert list(transactions.columns) == [
        "transaction_id",
        "customer_id",
        "amount",
        "transaction_date",
    ]

    # ---------------------------------------------------------
    # Invalid dataset
    # ---------------------------------------------------------
    try:
        consumer.load_dataset(
            "unknown_dataset"
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected invalid dataset to raise ValueError"
        )

    print("CuratedDatasetConsumer: PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())