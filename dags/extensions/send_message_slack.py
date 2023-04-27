from airflow.models import Variable
from airflow.models.connection import Connection
from slack import WebClient
from slack.errors import SlackApiError


def send_message_to_slack_channel():
    # c = Connection.get_connection_from_secrets(conn_id="slack_conn")
    # extra = c.extra_dejson
    # slack_token = extra.get("token")
    slack_token = Variable.get_variable_from_secrets("slack_token")
    print("Your slack token is:", slack_token)
    client = WebClient(token=slack_token)

    try:
        response = client.chat_postMessage(channel="apache-airflow-connecting-to-slacks-api",
                                           text="Hello from your app! :tada:")
    except SlackApiError as e:
        assert e.response["error"]
