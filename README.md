# ELT Orchestration with Apache Airflow, dbt & Great Expectations

End-to-end ELT workflow: **Airflow** orchestrates extraction into a warehouse (Snowflake / PostgreSQL), **dbt** builds modular, version-controlled transformations into a **star schema**, and **Great Expectations** + custom checks gate each run on data quality.

## DAG: `retail_elt_daily`
```
extract_orders ─┐
extract_customers ─┼─► dq_raw_checks ─► dbt_run_staging ─► dbt_run_marts ─► dbt_test ─► dq_marts_checks ─► notify
extract_products ─┘
```
- Task-level retries, SLAs, and failure callbacks
- `dbt` invoked through `BashOperator` with `--select tag:<layer>`
- Data-quality failures fail the DAG before bad data reaches dashboards

## Dimensional model (dbt)
| Model | Type | Grain |
|-------|------|-------|
| `stg_orders`, `stg_customers`, `stg_products` | staging views | 1 row per source record |
| `dim_customer` | dimension (SCD1) | 1 row per customer |
| `dim_product` | dimension | 1 row per product |
| `fct_sales` | **incremental** fact | 1 row per order line |

## Data quality
- `data_quality/expectations.py` — Great Expectations suite (nulls, uniqueness, ranges, accepted values)
- `data_quality/checks.py` — lightweight custom checks (row-count drift, freshness, completeness) with unit tests

## Run
```bash
pip install -r requirements.txt
pytest -q
cd dbt && dbt deps && dbt build --profiles-dir .
```

## Tech
Apache Airflow · dbt · Great Expectations · Snowflake / PostgreSQL · SQL · Python
