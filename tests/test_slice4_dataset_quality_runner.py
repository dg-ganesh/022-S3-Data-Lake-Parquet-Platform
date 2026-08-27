import pandas as pd

from src.core.dataset_quality_runner import (
    DatasetQualityRunner,
)


def main() -> None:

    runner = DatasetQualityRunner()

    # ---------------------------------------------------------
    # Customers - successful execution
    # ---------------------------------------------------------

    customers = pd.DataFrame(
        {
            "customer_id": [1, 2, 3],
            "customer_name": ["Alice", "Bob", "Charlie"],
            "country": ["IN", "US", "UK"],
        }
    )

    result = runner.run(
        dataset_name="customers",
        dataframe=customers,
        required_columns=[
            "customer_id",
            "customer_name",
            "country",
        ],
        not_null_columns=[
            "customer_id",
            "customer_name",
        ],
        unique_columns=[
            "customer_id",
        ],
    )

    assert result["dataset_name"] == "customers"
    assert result["status"] == "PASS"
    assert result["success"] is True
    assert result["failed_rules"] == 0

    # ---------------------------------------------------------
    # Transactions - successful execution
    # ---------------------------------------------------------

    transactions = pd.DataFrame(
        {
            "transaction_id": [101, 102, 103],
            "customer_id": [1, 2, 3],
            "amount": [100.0, 250.0, 75.0],
        }
    )

    result = runner.run(
        dataset_name="transactions",
        dataframe=transactions,
        required_columns=[
            "transaction_id",
            "customer_id",
            "amount",
        ],
        not_null_columns=[
            "transaction_id",
            "customer_id",
        ],
        unique_columns=[
            "transaction_id",
        ],
    )

    assert result["dataset_name"] == "transactions"
    assert result["status"] == "PASS"
    assert result["success"] is True
    assert result["failed_rules"] == 0

    # ---------------------------------------------------------
    # Dataset with duplicate key - expected failure
    # ---------------------------------------------------------

    invalid_transactions = pd.DataFrame(
        {
            "transaction_id": [101, 102, 102],
            "customer_id": [1, 2, 3],
            "amount": [100.0, 250.0, 75.0],
        }
    )

    result = runner.run(
        dataset_name="invalid_transactions",
        dataframe=invalid_transactions,
        required_columns=[
            "transaction_id",
            "customer_id",
            "amount",
        ],
        not_null_columns=[
            "transaction_id",
        ],
        unique_columns=[
            "transaction_id",
        ],
    )

    assert result["dataset_name"] == "invalid_transactions"
    assert result["status"] == "FAIL"
    assert result["success"] is False
    assert result["failed_rules"] == 1

    # ---------------------------------------------------------
    # Dataset with missing required column - expected failure
    # ---------------------------------------------------------

    incomplete = pd.DataFrame(
        {
            "customer_id": [1, 2, 3],
        }
    )

    result = runner.run(
        dataset_name="incomplete_customers",
        dataframe=incomplete,
        required_columns=[
            "customer_id",
            "customer_name",
        ],
    )

    assert result["dataset_name"] == "incomplete_customers"
    assert result["status"] == "FAIL"
    assert result["success"] is False
    assert result["failed_rules"] == 1

    # ---------------------------------------------------------
    # Verify independent executions
    # ---------------------------------------------------------

    result = runner.run(
        dataset_name="customers_again",
        dataframe=customers,
        required_columns=[
            "customer_id",
        ],
    )

    assert result["dataset_name"] == "customers_again"
    assert result["status"] == "PASS"
    assert result["success"] is True

    print("DatasetQualityRunner: PASS")


if __name__ == "__main__":
    main()