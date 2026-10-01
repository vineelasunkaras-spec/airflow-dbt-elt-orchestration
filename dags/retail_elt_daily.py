"""Daily ELT: extract -> raw DQ -> dbt staging -> dbt marts -> dbt test -> marts DQ."""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

DBT_DIR = "/opt/airflow/dbt"
DBT = f"cd {DBT_DIR} && dbt"

default_args = {
    "owner": "data-engineering",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "sla": timedelta(hours=2),
    "email_on_failure": True,
}


def extract_table(table: str, **ctx):
    """Incremental extract from the OLTP source into the RAW schema for the run's interval."""
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook

    start, end = ctx["data_interval_start"], ctx["data_interval_end"]
    df = PostgresHook("oltp_postgres").get_pandas_df(
        f"SELECT * FROM public.{table} WHERE updated_at >= %(s)s AND updated_at < %(e)s",
        parameters={"s": start, "e": end},
    )
    if not df.empty:
        from snowflake.connector.pandas_tools import write_pandas

        with SnowflakeHook("snowflake_dw").get_conn() as conn:
            write_pandas(conn, df, table.upper(), schema="RAW", auto_create_table=True)
    return len(df)


def run_dq(layer: str, **_):
    from data_quality.expectations import run_suite

    run_suite(layer)


with DAG(
    dag_id="retail_elt_daily",
    start_date=datetime(2025, 1, 1),
    schedule="0 4 * * *",
    catchup=False,
    max_active_runs=1,
    default_args=default_args,
    tags=["elt", "dbt", "snowflake"],
) as dag:
    extracts = [
        PythonOperator(task_id=f"extract_{t}", python_callable=extract_table, op_kwargs={"table": t})
        for t in ("orders", "customers", "products")
    ]
    dq_raw = PythonOperator(task_id="dq_raw_checks", python_callable=run_dq, op_kwargs={"layer": "raw"})
    stg = BashOperator(task_id="dbt_run_staging", bash_command=f"{DBT} run --select tag:staging")
    marts = BashOperator(task_id="dbt_run_marts", bash_command=f"{DBT} run --select tag:marts")
    tests = BashOperator(task_id="dbt_test", bash_command=f"{DBT} test")
    dq_marts = PythonOperator(task_id="dq_marts_checks", python_callable=run_dq, op_kwargs={"layer": "marts"})
    done = EmptyOperator(task_id="notify")

    extracts >> dq_raw >> stg >> marts >> tests >> dq_marts >> done
