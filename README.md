# AIRFLOW-Wiktor-Morski
Apache Airflow is a workflow system for managing and scheduling data pipelines.

## Installation:
**Requirements:** Docker, Docker Compose, PostgreSQL, Git

1. **Setup development environment.**
    
    Open your terminal and run the following commands:
    - `git clone git@github.com:gridu/AIRFLOW-Wiktor-Morski.git`
    - `cd AIRFLOW-Wiktor-Morski`
    - `python3 -m venv venv`
    - `source venv/bin/activate`
    - `python -m pip install "apache-airflow[celery, postgres]==2.5.0" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.5.0/constraints-3.7.txt"`
  
    you can now open the `AIRFLOW-Wiktor-Morski` directory with your desired code editor in the virtual environment we've created and start developing.
    
2. **Run Airflow services in Docker.**

    Open your terminal and run the following commands:
    - Initialize the database: `docker compose up airflow-init`
    - Run Airflow services in the background: `docker compose up -d`
    - Get Postgres container id and check if services are already healthy: `docker ps`
    - Open Postgres: `docker exec -it POSTGRES_CONTAINER_ID psql -U airflow`
    - Create database: `CREATE DATABASE test;`
    - Run `\l` command to see, if created correctly and `\q` to quit
  
    In the Airflow's webserver UI:
    - When all services are healty, navigate to `localhost:8080` in your web browser
    - Authenticate using login: `airflow` and password: `airflow`

    - Create new connections (Admin -> Connections):
  
        1. For FileSensor task:
            * Connection Id: `fs_default`
            * Connection Type: `File (path)`
      
        2. For Postgres tasks:
            * Connection Id: `postgres_localhost`
            * Host: `host.docker.internal`
            * Schema: `test`
            * Login: `airflow`
            * Password: `airflow`
            * Port: `5432`
      
    - Create new variables (Admin -> Variables):
        
        2. (Optional) For FileSensor task:
            * Key: `path_to_run_file`
            * Value: `path/to/run` (must include run at the end, since you specify the path and the file itself)

## Running dags:
All dags you can run from web UI. Firstly you have to Unpause a dag and then Trigger it.

1. update_table_dag_1, update_table_dag_2, update_table_dag_3 (jobs_dag.py):
    - after the dag finishes its tasks, you can check if the table was correctly inserted to the `test` database using dbeaver or by typing the following commands:
        -  `docker exec -it POSTGRES_CONTAINER_ID psql -U airflow`
        -  `\c test`
        -  `SELECT * FROM table_dag_[number here];` [number here] means 1, 2 or 3 depending on the dag you've run
        - you should see the content of the table
2. trigger_dag (trigger_dag.py) - **needs extra setup steps decribed below**:
    - to run this dag you have to put `run` file in the `AIRFLOW-Wiktor-Morski/dags` folder or in `path/to/` which you specified in 2. **Run Airflow services in Docker** -> Create new variables (Admin -> Variables) -> 2. (Optional) For FileSensor task
    - this dag will trigger update_table_dag_1 (so make sure in Airflow web UI that it's Unpaused)
    - (optional) this dag will send alert to your Slack workspace, to configure this you have to:
        1. Create your workspace - https://slack.com/get-started#/
        2. Create an application. Name it as you want - https://api.slack.com/
        3. After creation you will see basic information about your application. In the ‘Add features and functionality’ section click on ‘Permissions’ then in ‘Scopes’ under ‘Bot’ section add an OAuth scope called ‘chat:write:public’. After installation you will see a generated token that you need to save to Vault.
        4. Create a channel: `apache-airflow-connecting-to-slacks-api`
        5. Add variable to HashiCorp Vault:
            - `docker exec -it VAULT_CONTAINER_ID sh`
            - `vault login ZyrP7NtNw0hbLUqu7N3IlTdO`
            - `vault secrets enable -path=airflow -version=2 kv`
            - `vault kv put airflow/variables/slack_token value=YOUR_SLACK_TOKEN`
3. simple_etl (simple_etl_dag.py) and example_subdag_operator (subdag_vs_taskgroup.py):
    - you can simply check what these dags do and how they work in the web UI

## Cleaning-up the environment:
1. Run `docker-compose down --volumes --remove-orphans` command in the `AIRFLOW-Wiktor-Morski` directory
2. Remove the entire directory `rm -rf AIRFLOW-Wiktor-Morski`
