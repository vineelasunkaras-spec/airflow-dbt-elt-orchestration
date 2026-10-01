"""Great Expectations suites for the raw and marts layers."""
import great_expectations as gx

SUITES = {
    "raw": {
        "table": "RAW.ORDERS",
        "expectations": [
            ("expect_column_values_to_not_be_null", {"column": "ORDER_ID"}),
            ("expect_column_values_to_be_between", {"column": "QUANTITY", "min_value": 1, "max_value": 10000}),
            ("expect_column_values_to_be_between", {"column": "UNIT_PRICE", "min_value": 0}),
        ],
    },
    "marts": {
        "table": "ANALYTICS.FCT_SALES",
        "expectations": [
            ("expect_column_values_to_be_unique", {"column": "ORDER_LINE_ID"}),
            ("expect_column_values_to_not_be_null", {"column": "CUSTOMER_KEY", "mostly": 0.995}),
            ("expect_table_row_count_to_be_between", {"min_value": 1}),
        ],
    },
}


def run_suite(layer: str, connection_string: str | None = None) -> None:
    import os

    cfg = SUITES[layer]
    ctx = gx.get_context()
    ds = ctx.sources.add_or_update_sql("warehouse", connection_string=connection_string or os.environ["DW_CONN"])
    asset = ds.add_table_asset(cfg["table"].split(".")[-1], table_name=cfg["table"])
    validator = ctx.get_validator(batch_request=asset.build_batch_request())
    for name, kwargs in cfg["expectations"]:
        getattr(validator, name)(**kwargs)
    result = validator.validate()
    if not result.success:
        failed = [r.expectation_config.expectation_type for r in result.results if not r.success]
        raise ValueError(f"Data quality failed for {layer}: {failed}")
