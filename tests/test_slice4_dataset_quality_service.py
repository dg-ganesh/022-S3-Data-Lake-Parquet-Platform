import pandas as pd

from src.services.dataset_quality_service import (
    DatasetQualityService,
)


def main() -> None:

    service = DatasetQualityService()

    dataframe = pd.DataFrame(
        {
            "customer_id": [1, 2, 3],
            "customer_name": ["A", "B", "C"],
            "country": ["IN", "US", "UK"],
        }
    )

    # ---------------------------------------------------------
    # 1. Not empty
    # ---------------------------------------------------------

    result = service.check_not_empty(
        "customers",
        dataframe,
    )

    assert result.passed is True

    # ---------------------------------------------------------
    # 2. Required columns - PASS
    # ---------------------------------------------------------

    result = service.check_required_columns(
        "customers",
        dataframe,
        [
            "customer_id",
            "customer_name",
            "country",
        ],
    )

    assert result.passed is True

    # ---------------------------------------------------------
    # 3. Required columns - FAIL
    # ---------------------------------------------------------

    result = service.check_required_columns(
        "customers",
        dataframe,
        [
            "customer_id",
            "email",
        ],
    )

    assert result.passed is False

    # ---------------------------------------------------------
    # 4. Not-null - PASS
    # ---------------------------------------------------------

    result = service.check_not_null(
        "customers",
        dataframe,
        "customer_id",
    )

    assert result.passed is True

    # ---------------------------------------------------------
    # 5. Not-null - FAIL
    # ---------------------------------------------------------

    dataframe_with_null = pd.DataFrame(
        {
            "customer_id": [1, None, 3],
        }
    )

    result = service.check_not_null(
        "customers",
        dataframe_with_null,
        "customer_id",
    )

    assert result.passed is False

    # ---------------------------------------------------------
    # 6. Unique - PASS
    # ---------------------------------------------------------

    result = service.check_unique(
        "customers",
        dataframe,
        "customer_id",
    )

    assert result.passed is True

    # ---------------------------------------------------------
    # 7. Unique - FAIL
    # ---------------------------------------------------------

    dataframe_with_duplicates = pd.DataFrame(
        {
            "customer_id": [1, 2, 2],
        }
    )

    result = service.check_unique(
        "customers",
        dataframe_with_duplicates,
        "customer_id",
    )

    assert result.passed is False

    # ---------------------------------------------------------
    # 8. Not-null - UNKNOWN COLUMN
    # ---------------------------------------------------------

    result = service.check_not_null(
        "customers",
        dataframe,
        "unknown_column",
    )

    assert result.passed is False

    # ---------------------------------------------------------
    # 9. Unique - UNKNOWN COLUMN
    # ---------------------------------------------------------

    result = service.check_unique(
        "customers",
        dataframe,
        "unknown_column",
    )

    assert result.passed is False

    # ---------------------------------------------------------
    # 10. Empty dataset
    # ---------------------------------------------------------

    empty_dataframe = pd.DataFrame(
        columns=["customer_id"]
    )

    result = service.check_not_empty(
        "empty_dataset",
        empty_dataframe,
    )

    assert result.passed is False

    # ---------------------------------------------------------
    # Verify result collection
    # ---------------------------------------------------------

    results = service.get_results()

    assert len(results) == 10

    # At least one rule failed, so overall result must be False.
    assert service.all_passed() is False

    # ---------------------------------------------------------
    # Verify dictionary representation
    # ---------------------------------------------------------

    dictionary_results = service.as_dict()

    assert len(dictionary_results) == 10

    assert dictionary_results[0]["dataset_name"] == "customers"
    assert dictionary_results[0]["rule"] == "not_empty"
    assert dictionary_results[0]["passed"] is True

    print("DatasetQualityService: PASS")


if __name__ == "__main__":
    main()