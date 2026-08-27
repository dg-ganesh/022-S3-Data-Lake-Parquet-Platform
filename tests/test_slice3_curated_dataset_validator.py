import pandas as pd

from src.core.curated_dataset_validator import CuratedDatasetValidator


def main() -> int:
    validator = CuratedDatasetValidator()

    # ---------------------------------------------------------
    # TEST 1 — Valid dataset
    # ---------------------------------------------------------

    dataframe = pd.DataFrame(
        {
            "customer_id": [1, 2, 3],
            "customer_name": ["A", "B", "C"],
            "country": ["IN", "US", "UK"],
        }
    )

    result = validator.validate(
        dataframe=dataframe,
        required_columns=[
            "customer_id",
            "customer_name",
            "country",
        ],
        dataset_name="customers",
    )

    assert result["valid"] is True
    assert result["dataset_name"] == "customers"
    assert result["row_count"] == 3
    assert result["column_count"] == 3
    assert result["missing_columns"] == []
    assert result["null_columns"] == []
    assert result["errors"] == []

    # ---------------------------------------------------------
    # TEST 2 — Missing required column
    # ---------------------------------------------------------

    dataframe = pd.DataFrame(
        {
            "customer_id": [1, 2],
            "customer_name": ["A", "B"],
        }
    )

    result = validator.validate(
        dataframe=dataframe,
        required_columns=[
            "customer_id",
            "customer_name",
            "country",
        ],
        dataset_name="customers",
    )

    assert result["valid"] is False
    assert "country" in result["missing_columns"]

    # ---------------------------------------------------------
    # TEST 3 — Required column contains NULL
    # ---------------------------------------------------------

    dataframe = pd.DataFrame(
        {
            "customer_id": [1, None, 3],
            "customer_name": ["A", "B", "C"],
        }
    )

    result = validator.validate(
        dataframe=dataframe,
        required_columns=[
            "customer_id",
            "customer_name",
        ],
        dataset_name="customers",
    )

    assert result["valid"] is False
    assert "customer_id" in result["null_columns"]

    # ---------------------------------------------------------
    # TEST 4 — Empty dataset
    # ---------------------------------------------------------

    dataframe = pd.DataFrame(
        columns=[
            "customer_id",
            "customer_name",
        ]
    )

    result = validator.validate(
        dataframe=dataframe,
        required_columns=[
            "customer_id",
            "customer_name",
        ],
        dataset_name="customers",
    )

    assert result["valid"] is False
    assert "Dataset is empty" in result["errors"]

    # ---------------------------------------------------------
    # TEST 5 — Empty dataset explicitly allowed
    # ---------------------------------------------------------

    result = validator.validate(
        dataframe=dataframe,
        required_columns=[
            "customer_id",
            "customer_name",
        ],
        dataset_name="customers",
        allow_empty=True,
    )

    assert result["valid"] is True

    # ---------------------------------------------------------
    # TEST 6 — Input DataFrame must not be modified
    # ---------------------------------------------------------

    dataframe = pd.DataFrame(
        {
            "customer_id": [1, 2],
            "customer_name": ["A", "B"],
        }
    )

    original_columns = list(dataframe.columns)
    original_values = dataframe.copy()

    validator.validate(
        dataframe=dataframe,
        required_columns=[
            "customer_id",
            "customer_name",
        ],
        dataset_name="customers",
    )

    assert list(dataframe.columns) == original_columns
    assert dataframe.equals(original_values)

    print("CuratedDatasetValidator: PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
