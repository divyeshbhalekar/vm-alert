# import os
# from google.oauth2 import service_account
# from googleapiclient import discovery
# from slack_sdk import WebClient
# from slack_sdk.errors import SlackApiError
# from dotenv import load_dotenv

# def run_gcp_test_vm_main():
#     load_dotenv()
#     # Use environment variables for credentials
#     private_key = os.environ.get("PRIVATE_KEY_TEST")
#     if private_key:
#         private_key = private_key.replace("\\n", "\n")

#     # Use environment variables for credentials
#     credentials = service_account.Credentials.from_service_account_info({
#         "type": os.environ.get("TYPE_TEST"),
#         "project_id": os.environ.get("PROJECT_ID_TEST"),
#         "private_key_id": os.environ.get("PRIVATE_KEY_ID_TEST"),
#         "private_key": private_key,
#         "client_email": os.environ.get("CLIENT_EMAIL_TEST"),
#         "client_id": os.environ.get("CLIENT_ID_TEST"),
#         "auth_uri": os.environ.get("AUTH_URI_TEST"),
#         "token_uri": os.environ.get("TOKEN_URI_TEST"),
#         "auth_provider_x509_cert_url": os.environ.get("AUTH_PROVIDER_X509_CERT_URL_TEST"),
#         "client_x509_cert_url": os.environ.get("CLIENT_X509_CERT_URL_TEST"),
#         "universe_domain": os.environ.get("UNIVERSE_DOMAIN_TEST")
#     })


#     slack_token = os.environ.get('SLACK_TOKEN')
#     slack_channel = os.environ.get('SLACK_CHANNEL')

    
#     compute = discovery.build('compute', 'v1', credentials=credentials)

#     def get_running_instances_count(project, region):
#     # def get_terminated_instances_count(project):
#         request = compute.instances().aggregatedList(project=project)
#         response = request.execute()
        
#         running_count = 0
#         for zone, instances in response.get('items', {}).items():
#             if 'instances' in instances:
#                 running_count += len([instance for instance in instances['instances'] if instance['status'] == 'RUNNING'])
#                 # print(running_count)

#         return running_count

#     def send_slack_alert(message):
#         client = WebClient(token=slack_token)
#         try:
#             response = client.chat_postMessage(
#                 channel=slack_channel,
#                 text=message
#             )
#             print("Slack alert sent successfully!")
#         except SlackApiError as e:
#             print(f"Error sending Slack alert: {e.response['error']}")


#     def main():
#         project = 'msec-test'  # Replace with your GCP project ID
        
#         running_count = get_running_instances_count(project,'all')  # 'all' is not a valid region but used to indicate all regions
        
#         if running_count >= 1:
#             print(f"Alert! There are {running_count} instances running in gcp msec-001 project.")
#             # You can add additional alerting mechanisms or actions here.
#             send_slack_alert(f"Alert! There are {running_count} instances running \ncloud = gcp, project = 'msec-test' please check @divyesh @rizwan ")

# if __name__ == "__main__":
#     run_gcp_test_vm_main

import os
from google.oauth2 import service_account
from googleapiclient import discovery
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

def should_ignore_instance(instance_name):
    # Add conditions to ignore specific instances if needed
    return False

def get_running_instances_count(compute, project, region):
    request = compute.instances().aggregatedList(project=project)
    response = request.execute()

    running_count = 0
    for zone, instances in response.get('items', {}).items():
        if 'instances' in instances:
            running_count += len([instance for instance in instances['instances'] if instance['status'] == 'RUNNING' and not should_ignore_instance(instance['name'])])

    return running_count

def send_slack_alert(slack_client, slack_channel, message):
    try:
        response = slack_client.chat_postMessage(
            channel=slack_channel,
            text=message
        )
        print("Slack alert sent successfully!")
    except SlackApiError as e:
        print(f"Error sending Slack alert: {e.response['error']}")

# def run_gcp_test_vm():
def run_gcp_test_vm_main():
    # Load environment variables from .env
    load_dotenv()
    # Use environment variables for credentials
    private_key = os.environ.get("PRIVATE_KEY_TEST")
    if private_key:
        private_key = private_key.replace("\\n", "\n")

    # Use environment variables for credentials
    credentials = service_account.Credentials.from_service_account_info({
        "type": os.environ.get("TYPE_TEST"),
        "project_id": os.environ.get("PROJECT_ID_TEST"),
        "private_key_id": os.environ.get("PRIVATE_KEY_ID_TEST"),
        "private_key": private_key,
        "client_email": os.environ.get("CLIENT_EMAIL_TEST"),
        "client_id": os.environ.get("CLIENT_ID_TEST"),
        "auth_uri": os.environ.get("AUTH_URI_TEST"),
        "token_uri": os.environ.get("TOKEN_URI_TEST"),
        "auth_provider_x509_cert_url": os.environ.get("AUTH_PROVIDER_X509_CERT_URL_TEST"),
        "client_x509_cert_url": os.environ.get("CLIENT_X509_CERT_URL_TEST"),
        "universe_domain": os.environ.get("UNIVERSE_DOMAIN_TEST")
    })

    slack_token = os.environ.get('SLACK_TOKEN')
    slack_channel = os.environ.get('SLACK_CHANNEL')

    compute = discovery.build('compute', 'v1', credentials=credentials)

    running_count = get_running_instances_count(compute, 'msec-test', 'all')  # 'all' is not a valid region but used to indicate all regions

    if running_count >= 1:
        print(f"Alert! There are {running_count} instances running in gcp msec-test project.")
        # You can add additional alerting mechanisms or actions here.
        send_slack_alert(WebClient(token=slack_token), slack_channel, f"Alert! There are {running_count} instances running \ncloud = gcp, project = 'msec-test' please check")
    else:
        print("No action required. Number of running VMs is within the limit.cloud = gcp, project = 'msec-test'")

if __name__ == "__main__":
    run_gcp_test_vm_main()
