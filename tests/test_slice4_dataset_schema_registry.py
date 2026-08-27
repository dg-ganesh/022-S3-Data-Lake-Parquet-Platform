from src.services.dataset_schema_registry import (
    DatasetSchemaRegistry,
)


def main() -> None:

    registry = DatasetSchemaRegistry()

    # ---------------------------------------------------------
    # Register customers schema
    # ---------------------------------------------------------

    customers = registry.register_schema(
        dataset_name="customers",
        columns=[
            "customer_id",
            "customer_name",
            "email",
            "country",
        ],
        column_types={
            "customer_id": "int64",
            "customer_name": "string",
            "email": "string",
            "country": "string",
        },
    )

    assert customers.dataset_name == "customers"

    assert customers.columns == (
        "customer_id",
        "customer_name",
        "email",
        "country",
    )

    assert dict(customers.column_types) == {
        "customer_id": "int64",
        "customer_name": "string",
        "email": "string",
        "country": "string",
    }

    # ---------------------------------------------------------
    # Register transactions schema
    # ---------------------------------------------------------

    transactions = registry.register_schema(
        dataset_name="transactions",
        columns=[
            "transaction_id",
            "customer_id",
            "amount",
            "transaction_date",
        ],
        column_types={
            "transaction_id": "int64",
            "customer_id": "int64",
            "amount": "float64",
            "transaction_date": "date",
        },
    )

    assert transactions.dataset_name == "transactions"

    # ---------------------------------------------------------
    # Retrieve schema
    # ---------------------------------------------------------

    schema = registry.get_schema("transactions")

    assert schema.columns == (
        "transaction_id",
        "customer_id",
        "amount",
        "transaction_date",
    )

    # ---------------------------------------------------------
    # Retrieve individual column type
    # ---------------------------------------------------------

    assert (
        registry.get_column_type(
            "transactions",
            "amount",
        )
        == "float64"
    )

    assert (
        registry.get_column_type(
            "transactions",
            "transaction_date",
        )
        == "date"
    )

    # ---------------------------------------------------------
    # List registered datasets
    # ---------------------------------------------------------

    datasets = registry.list_datasets()

    assert datasets == [
        "customers",
        "transactions",
    ]

    # ---------------------------------------------------------
    # Dictionary representation
    # ---------------------------------------------------------

    schema_dict = registry.as_dict("customers")

    assert schema_dict["dataset_name"] == "customers"

    assert schema_dict["columns"] == [
        "customer_id",
        "customer_name",
        "email",
        "country",
    ]

    assert schema_dict["column_types"]["customer_id"] == "int64"

    # ---------------------------------------------------------
    # Unknown dataset
    # ---------------------------------------------------------

    try:
        registry.get_schema("unknown_dataset")
        raise AssertionError(
            "Expected KeyError for unknown dataset"
        )
    except KeyError:
        pass

    # ---------------------------------------------------------
    # Unknown column
    # ---------------------------------------------------------

    try:
        registry.get_column_type(
            "customers",
            "unknown_column",
        )
        raise AssertionError(
            "Expected KeyError for unknown column"
        )
    except KeyError:
        pass

    # ---------------------------------------------------------
    # Duplicate schema
    # ---------------------------------------------------------

    try:
        registry.register_schema(
            dataset_name="customers",
            columns=["id"],
            column_types={"id": "int64"},
        )
        raise AssertionError(
            "Expected ValueError for duplicate schema"
        )
    except ValueError:
        pass

    # ---------------------------------------------------------
    # Missing column type
    # ---------------------------------------------------------

    try:
        registry.register_schema(
            dataset_name="invalid_dataset",
            columns=["id", "name"],
            column_types={"id": "int64"},
        )
        raise AssertionError(
            "Expected ValueError for missing type"
        )
    except ValueError:
        pass

    # ---------------------------------------------------------
    # Extra column type
    # ---------------------------------------------------------

    try:
        registry.register_schema(
            dataset_name="invalid_dataset_2",
            columns=["id"],
            column_types={
                "id": "int64",
                "unexpected": "string",
            },
        )
        raise AssertionError(
            "Expected ValueError for extra type"
        )
    except ValueError:
        pass

    print("DatasetSchemaRegistry: PASS")


if __name__ == "__main__":
    main()