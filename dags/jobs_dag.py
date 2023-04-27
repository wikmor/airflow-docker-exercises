import logging
from uuid import uuid4
from datetime import datetime

from airflow import DAG
from airflow.models import Variable
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.utils.trigger_rule import TriggerRule

from extensions.count_rows_postgres import PostgresCountRowsOperator

config = {
    "update_table_dag_1": {
        "schedule": None,
        "start_date": datetime(2022, 1, 1),
        "table_name": "table_dag_1",
    },
    "update_table_dag_2": {
        "schedule": None,
        "start_date": datetime(2022, 1, 1),
        "table_name": "table_dag_2",
    },
    "update_table_dag_3": {
        "schedule": None,
        "start_date": datetime(2022, 1, 1),
        "table_name": "table_dag_3",
    },
}


def _check_table_exists(sql_to_check_table_exist: str, table_name: str) -> str:
    hook = PostgresHook(postgres_conn_id="postgres_localhost")
    query = hook.get_first(sql=sql_to_check_table_exist.format(table_name))
    print('query:', query)
    if query:
        return 'insert_row'
    else:
        logging.info(f"table {table_name} does not exists, creating one...")
        return 'create_table'


def log_process_start(dag_id: str, table: str) -> None:
    logging.info(f"{dag_id} start processing rows in table: {table}")


for dict in config:
    with DAG(dag_id=dict, schedule=config[dict]["schedule"], start_date=config[dict]["start_date"],
             catchup=False) as dag:
        print_process_start = PythonOperator(
            task_id="print_process_start",
            python_callable=log_process_start,
            op_args=[dict, config[dict]["table_name"]],
            queue='jobs_queue'
        )
        get_current_user = BashOperator(
            task_id="get_current_user",
            bash_command='whoami',
            queue='jobs_queue'
        )
        check_table_exists = BranchPythonOperator(
            task_id="check_table_exists",
            python_callable=_check_table_exists,
            op_args=["SELECT * FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '{}';",
                     config[dict]['table_name']],
            queue='jobs_queue'
        )

        # You can simply type CREATE TABLE IF NOT EXISTS, but for this
        # demo we use BranchPythonOperator to check if table exists.
        create_table = PostgresOperator(
            task_id="create_table",
            postgres_conn_id="postgres_localhost",
            sql=f"""
                CREATE TABLE {config[dict]["table_name"]} (
                custom_id integer NOT NULL,
                user_name VARCHAR(50) NOT NULL, 
                timestamp TIMESTAMP NOT NULL);
                """,
            queue='jobs_queue'
        )

        insert_row = PostgresOperator(
            task_id="insert_row",
            postgres_conn_id="postgres_localhost",
            sql="sql/insert.sql",
            trigger_rule=TriggerRule.NONE_FAILED,
            params={
                "table_name": config[dict]["table_name"],
                "custom_id": uuid4().int % 123456789,
                "timestamp": datetime.now()
            },
            queue='jobs_queue'
        )

        query_table = PostgresCountRowsOperator(
            task_id="query_table",
            table=config[dict]['table_name'],
            postgres_conn_id="postgres_localhost",
            database="test",
            queue='jobs_queue'
        )

        print_process_start >> get_current_user >> check_table_exists >> create_table >> insert_row >> query_table
        check_table_exists >> insert_row
