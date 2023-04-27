INSERT INTO {{ params.table_name }}
VALUES ( {{ params.custom_id }}, '{{ ti.xcom_pull(key="return_value", task_ids="get_current_user") }}', '{{ params.timestamp }}' )