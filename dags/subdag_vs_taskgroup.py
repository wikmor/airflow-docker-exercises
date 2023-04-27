import datetime

from airflow import DAG
from airflow.example_dags.subdags.subdag import subdag
from airflow.operators.empty import EmptyOperator
from airflow.operators.subdag import SubDagOperator
from airflow.utils.task_group import TaskGroup

DAG_NAME = 'example_subdag_operator'

with DAG(
    dag_id=DAG_NAME,
    default_args={"retries": 2},
    start_date=datetime.datetime(2022, 1, 1),
    schedule="@once",
    tags=['example'],
) as dag:

    start = EmptyOperator(
        task_id='start',
    )

    with TaskGroup("section_1", tooltip="Tasks for Section 1") as section_1:
        _ = [EmptyOperator(task_id=f'task-{i + 1}') for i in range(5)]

    some_other_task = EmptyOperator(
        task_id='some-other-task',
    )

    section_2 = SubDagOperator(
        task_id='section-2',
        subdag=subdag(DAG_NAME, 'section-2', dag.default_args),
    )

    end = EmptyOperator(
        task_id='end',
    )

    start >> section_1 >> some_other_task >> section_2 >> end
