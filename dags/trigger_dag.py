from airflow import DAG
from airflow.decorators import task
from airflow.models import Variable
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.subdag import SubDagOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sensors.filesystem import FileSensor

from datetime import datetime

from extensions.send_message_slack import send_message_to_slack_channel


def _pull_row_count(ti):
    row_count = ti.xcom_pull(dag_id="update_table_dag_1", task_ids="query_table")
    print(row_count)


with DAG("trigger_dag", schedule=None, start_date=datetime(2022, 1, 1), catchup=False):
    wait_for_run_file = FileSensor(
        task_id="wait_for_run_file",
        filepath=Variable.get("path_to_run_file", default_var="/opt/airflow/dags/run"),
        poke_interval=10,
        timeout=60 * 5,
    )

    trigger_update_table_dag_1 = TriggerDagRunOperator(
        task_id="trigger_update_table_dag_1",
        trigger_dag_id="update_table_dag_1",
        wait_for_completion=True,
        poke_interval=10,
    )

    with DAG(
            "trigger_dag.process_results_subdag", schedule=None, start_date=datetime(2022, 1, 1), catchup=False
    ) as subdag:
        print_result = PythonOperator(task_id="print_result", python_callable=_pull_row_count)

        remove_run_file = BashOperator(task_id="remove_run_file", bash_command=f'rm {Variable.get("path_to_run_file", default_var="/opt/airflow/dags/run")}')

        create_file_with_timestamp = BashOperator(
            task_id="create_finished_timestamp",
            bash_command="touch /opt/airflow/dags/finished_{{ ts_nodash }}",
        )

        print_result >> remove_run_file >> create_file_with_timestamp

    process_results_subdag = SubDagOperator(task_id="process_results_subdag", subdag=subdag)

    @task
    def alert_to_slack():
        return send_message_to_slack_channel()
    # alert_to_slack = PythonOperator(task_id="alert_to_slack", python_callable=send_message_to_slack_channel)

    wait_for_run_file >> trigger_update_table_dag_1 >> process_results_subdag >> alert_to_slack()
