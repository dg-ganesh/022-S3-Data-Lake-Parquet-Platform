import pandas as pd

from src.core.curated_dataset_service import CuratedDatasetService


class FakeReader:
    def __init__(self, dataframe):
        self.dataframe = dataframe
        self.calls = []

    def read_dataset(self, dataset_name):
        self.calls.append(dataset_name)
        return self.dataframe


class FakeValidator:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def validate(
        self,
        dataframe,
        required_columns,
        dataset_name,
        allow_empty=False,
    ):
        self.calls.append(
            {
                "dataset_name": dataset_name,
                "required_columns": required_columns,
                "allow_empty": allow_empty,
            }
        )

        return self.result


def main() -> int:

    # ---------------------------------------------------------
    # TEST 1 — Successful load
    # ---------------------------------------------------------

    dataframe = pd.DataFrame(
        {
            "customer_id": [1, 2, 3],
            "customer_name": ["A", "B", "C"],
        }
    )

    reader = FakeReader(dataframe)

    validator = FakeValidator(
        {
            "valid": True,
            "dataset_name": "customers",
            "row_count": 3,
            "column_count": 2,
            "missing_columns": [],
            "null_columns": [],
            "errors": [],
        }
    )

    service = CuratedDatasetService(
        config=None,
        reader=reader,
        validator=validator,
    )

    result = service.load_dataset(
        dataset_name="customers",
        required_columns=[
            "customer_id",
            "customer_name",
        ],
    )

    assert result.equals(dataframe)

    assert reader.calls == ["customers"]

    assert len(validator.calls) == 1
    assert validator.calls[0]["dataset_name"] == "customers"
    assert validator.calls[0]["required_columns"] == [
        "customer_id",
        "customer_name",
    ]
    assert validator.calls[0]["allow_empty"] is False

    # ---------------------------------------------------------
    # TEST 2 — Validation failure
    # ---------------------------------------------------------

    reader = FakeReader(dataframe)

    validator = FakeValidator(
        {
            "valid": False,
            "dataset_name": "customers",
            "row_count": 3,
            "column_count": 2,
            "missing_columns": ["country"],
            "null_columns": [],
            "errors": [
                "Missing required columns: ['country']"
            ],
        }
    )

    service = CuratedDatasetService(
        config=None,
        reader=reader,
        validator=validator,
    )

    try:
        service.load_dataset(
            dataset_name="customers",
            required_columns=[
                "customer_id",
                "customer_name",
                "country",
            ],
        )
    except ValueError as exc:
        assert "customers" in str(exc)
        assert "Missing required columns" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError for validation failure"
        )

    # ---------------------------------------------------------
    # TEST 3 — Allow empty passed through
    # ---------------------------------------------------------

    empty_dataframe = pd.DataFrame(
        columns=["customer_id"]
    )

    reader = FakeReader(empty_dataframe)

    validator = FakeValidator(
        {
            "valid": True,
            "dataset_name": "customers",
            "row_count": 0,
            "column_count": 1,
            "missing_columns": [],
            "null_columns": [],
            "errors": [],
        }
    )

    service = CuratedDatasetService(
        config=None,
        reader=reader,
        validator=validator,
    )

    result = service.load_dataset(
        dataset_name="customers",
        required_columns=["customer_id"],
        allow_empty=True,
    )

    assert result.empty
    assert validator.calls[0]["allow_empty"] is True

    print("CuratedDatasetService: PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())