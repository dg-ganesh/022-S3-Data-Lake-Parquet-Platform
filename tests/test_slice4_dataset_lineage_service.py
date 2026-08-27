from src.services.dataset_lineage_service import (
    DatasetLineageService,
)


def main() -> None:

    service = DatasetLineageService()

    # ---------------------------------------------------------
    # Register customers lineage
    # ---------------------------------------------------------

    customers = service.register_lineage(
        dataset_name="customers",
        source="data/input/customers.csv",
        processing_step="curated_pipeline",
        output_location="curated/customers/",
    )

    assert customers.dataset_name == "customers"
    assert customers.source == (
        "data/input/customers.csv"
    )
    assert customers.processing_step == (
        "curated_pipeline"
    )
    assert customers.output_location == (
        "curated/customers/"
    )

    # ---------------------------------------------------------
    # Register transactions lineage
    # ---------------------------------------------------------

    transactions = service.register_lineage(
        dataset_name="transactions",
        source="data/input/transactions.csv",
        processing_step="curated_pipeline",
        output_location="curated/transactions/",
    )

    assert transactions.dataset_name == "transactions"
    assert transactions.source == (
        "data/input/transactions.csv"
    )

    # ---------------------------------------------------------
    # Retrieve lineage
    # ---------------------------------------------------------

    record = service.get_lineage("customers")

    assert record.dataset_name == "customers"
    assert record.source == (
        "data/input/customers.csv"
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

    lineage_dict = service.as_dict("transactions")

    assert lineage_dict["dataset_name"] == "transactions"
    assert lineage_dict["source"] == (
        "data/input/transactions.csv"
    )
    assert lineage_dict["processing_step"] == (
        "curated_pipeline"
    )
    assert lineage_dict["output_location"] == (
        "curated/transactions/"
    )

    # ---------------------------------------------------------
    # Unknown dataset
    # ---------------------------------------------------------

    try:
        service.get_lineage("unknown_dataset")
        raise AssertionError(
            "Expected KeyError for unknown dataset"
        )
    except KeyError:
        pass

    # ---------------------------------------------------------
    # Duplicate lineage
    # ---------------------------------------------------------

    try:
        service.register_lineage(
            dataset_name="customers",
            source="another.csv",
            processing_step="another_step",
            output_location="another/",
        )
        raise AssertionError(
            "Expected ValueError for duplicate lineage"
        )
    except ValueError:
        pass

    # ---------------------------------------------------------
    # Empty source
    # ---------------------------------------------------------

    try:
        service.register_lineage(
            dataset_name="invalid_source",
            source="",
            processing_step="curated_pipeline",
            output_location="curated/",
        )
        raise AssertionError(
            "Expected ValueError for empty source"
        )
    except ValueError:
        pass

    # ---------------------------------------------------------
    # Empty processing step
    # ---------------------------------------------------------

    try:
        service.register_lineage(
            dataset_name="invalid_step",
            source="input.csv",
            processing_step="",
            output_location="curated/",
        )
        raise AssertionError(
            "Expected ValueError for empty processing step"
        )
    except ValueError:
        pass

    # ---------------------------------------------------------
    # Empty output location
    # ---------------------------------------------------------

    try:
        service.register_lineage(
            dataset_name="invalid_output",
            source="input.csv",
            processing_step="curated_pipeline",
            output_location="",
        )
        raise AssertionError(
            "Expected ValueError for empty output location"
        )
    except ValueError:
        pass

    print("DatasetLineageService: PASS")


if __name__ == "__main__":
    main()