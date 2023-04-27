from airflow.models.baseoperator import BaseOperator
from airflow.utils.context import Context
from airflow.providers.postgres.hooks.postgres import PostgresHook


class PostgresCountRowsOperator(BaseOperator):
    def __init__(self, table: str, postgres_conn_id: str, database: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.table = table
        self.postgres_conn_id = postgres_conn_id
        self.database = database

    def execute(self, context: Context) -> int:
        hook = PostgresHook(postgres_conn_id=self.postgres_conn_id, schema=self.database)
        sql = f"SELECT COUNT(*) FROM {self.table};"
        query = hook.get_first(sql)
        return query
