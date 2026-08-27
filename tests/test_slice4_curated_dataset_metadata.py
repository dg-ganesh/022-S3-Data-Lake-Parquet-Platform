from src.services.curated_dataset_metadata_service import (
    CuratedDatasetMetadataService,
)


def main() -> None:
    service = CuratedDatasetMetadataService()

    # ---------------------------------------------------------
    # Register customers
    # ---------------------------------------------------------
    customers = service.register_dataset(
        dataset_name="customers",
        description="Curated customer dataset",
        format="parquet",
        location="curated/customers/",
        partitioned=False,
        partition_columns=[],
        columns=[
            "customer_id",
            "customer_name",
            "email",
            "country",
        ],
    )

    assert customers.dataset_name == "customers"
    assert customers.format == "parquet"
    assert customers.partitioned is False
    assert customers.partition_columns == ()

    # ---------------------------------------------------------
    # Register transactions
    # ---------------------------------------------------------
    transactions = service.register_dataset(
        dataset_name="transactions",
        description="Curated transaction dataset",
        format="parquet",
        location="curated/transactions/",
        partitioned=True,
        partition_columns=["transaction_date"],
        columns=[
            "transaction_id",
            "customer_id",
            "amount",
            "transaction_date",
        ],
    )

    assert transactions.dataset_name == "transactions"
    assert transactions.format == "parquet"
    assert transactions.partitioned is True
    assert transactions.partition_columns == ("transaction_date",)

    # ---------------------------------------------------------
    # Retrieve metadata
    # ---------------------------------------------------------
    result = service.get_metadata("customers")

    assert result.dataset_name == "customers"
    assert result.location == "curated/customers/"
    assert result.columns == (
        "customer_id",
        "customer_name",
        "email",
        "country",
    )

    # ---------------------------------------------------------
    # List datasets
    # ---------------------------------------------------------
    datasets = service.list_datasets()

    assert datasets == [
        "customers",
        "transactions",
    ]

    # ---------------------------------------------------------
    # Dictionary representation
    # ---------------------------------------------------------
    metadata_dict = service.get_metadata_dict("transactions")

    assert metadata_dict["dataset_name"] == "transactions"
    assert metadata_dict["format"] == "parquet"
    assert metadata_dict["partitioned"] is True

    # ---------------------------------------------------------
    # Unknown dataset must fail
    # ---------------------------------------------------------
    try:
        service.get_metadata("unknown_dataset")
        raise AssertionError(
            "Expected KeyError for unknown dataset"
        )
    except KeyError:
        pass

    # ---------------------------------------------------------
    # Duplicate registration must fail
    # ---------------------------------------------------------
    try:
        service.register_dataset(
            dataset_name="customers",
            description="Duplicate",
            format="parquet",
            location="curated/customers/",
            partitioned=False,
            partition_columns=[],
            columns=[],
        )
        raise AssertionError(
            "Expected ValueError for duplicate dataset"
        )
    except ValueError:
        pass

    print("CuratedDatasetMetadataService: PASS")


if __name__ == "__main__":
    main()